"""Load a model artifact and wrap it behind a small predict interface.

The artifact is anything joblib can load that exposes a scikit-learn-style
``predict`` (and optionally ``predict_proba``). Loading is isolated here so the
HTTP layer can be tested with a fake model and no file on disk.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class Predictor(Protocol):
    def predict(self, x: Any) -> Any: ...


class ModelError(RuntimeError):
    """Raised when a model cannot be loaded or used."""


class ModelHandle:
    """A loaded model plus the metadata the server reports."""

    def __init__(self, model: Predictor, *, name: str = "model") -> None:
        if not isinstance(model, Predictor):
            raise ModelError("loaded object has no predict() method")
        self._model = model
        self.name = name

    @property
    def n_features(self) -> int | None:
        value = getattr(self._model, "n_features_in_", None)
        return int(value) if value is not None else None

    @property
    def has_proba(self) -> bool:
        return hasattr(self._model, "predict_proba")

    def predict(self, instances: list[list[float]]) -> list:
        x = np.asarray(instances, dtype=float)
        if x.ndim != 2:
            raise ModelError("instances must be a 2-D array")
        return np.asarray(self._model.predict(x)).tolist()

    def predict_proba(self, instances: list[list[float]]) -> list:
        if not self.has_proba:
            raise ModelError("model does not support predict_proba")
        x = np.asarray(instances, dtype=float)
        return np.asarray(self._model.predict_proba(x)).tolist()


def load_model(path: str | Path) -> ModelHandle:
    path = Path(path)
    if not path.exists():
        raise ModelError(f"model file not found: {path}")
    try:
        import joblib
    except ImportError as exc:  # pragma: no cover - import guard
        raise ModelError("joblib is not installed") from exc
    try:
        model = joblib.load(path)
    except Exception as exc:
        raise ModelError(f"could not load model: {exc}") from exc
    return ModelHandle(model, name=path.stem)
