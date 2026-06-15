"""Prometheus metrics for the server.

Each server owns its own registry so several apps (including in tests) can be
created without colliding on the global default registry.
"""

from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest


class Metrics:
    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        self.registry = registry or CollectorRegistry()
        self.requests = Counter(
            "servectl_requests_total",
            "Total requests by endpoint and outcome.",
            ["endpoint", "outcome"],
            registry=self.registry,
        )
        self.predictions = Counter(
            "servectl_predictions_total",
            "Total prediction instances served.",
            registry=self.registry,
        )
        self.latency = Histogram(
            "servectl_predict_seconds",
            "Prediction request latency in seconds.",
            registry=self.registry,
        )

    def render(self) -> bytes:
        return generate_latest(self.registry)
