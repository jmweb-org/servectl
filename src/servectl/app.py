"""The FastAPI application that serves a model.

``create_app`` takes an already-loaded :class:`~servectl.model.ModelHandle`, so
the whole HTTP surface can be exercised with a fake model and a test client
without reading a file or starting a server.
"""

from __future__ import annotations

import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from servectl import __version__
from servectl.metrics import Metrics
from servectl.model import ModelError, ModelHandle

CONTENT_TYPE_PROMETHEUS = "text/plain; version=0.0.4; charset=utf-8"


class PredictRequest(BaseModel):
    instances: list[list[float]] = Field(..., min_length=1)


class PredictResponse(BaseModel):
    predictions: list


def create_app(handle: ModelHandle, *, metrics: Metrics | None = None) -> FastAPI:
    metrics = metrics or Metrics()
    app = FastAPI(title="servectl", version=__version__)

    @app.get("/health")
    def health() -> dict:
        metrics.requests.labels("health", "ok").inc()
        return {
            "status": "ok",
            "model": handle.name,
            "n_features": handle.n_features,
            "version": __version__,
        }

    @app.get("/metrics")
    def metrics_endpoint() -> Response:
        return Response(content=metrics.render(), media_type=CONTENT_TYPE_PROMETHEUS)

    @app.post("/predict", response_model=PredictResponse)
    def predict(request: PredictRequest) -> PredictResponse:
        start = time.perf_counter()
        try:
            preds = handle.predict(request.instances)
        except ModelError as exc:
            metrics.requests.labels("predict", "error").inc()
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        finally:
            metrics.latency.observe(time.perf_counter() - start)
        metrics.requests.labels("predict", "ok").inc()
        metrics.predictions.inc(len(request.instances))
        return PredictResponse(predictions=preds)

    @app.post("/predict_proba")
    def predict_proba(request: PredictRequest) -> dict:
        if not handle.has_proba:
            metrics.requests.labels("predict_proba", "error").inc()
            raise HTTPException(status_code=400, detail="model has no predict_proba")
        try:
            proba = handle.predict_proba(request.instances)
        except ModelError as exc:
            metrics.requests.labels("predict_proba", "error").inc()
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        metrics.requests.labels("predict_proba", "ok").inc()
        return {"probabilities": proba}

    return app
