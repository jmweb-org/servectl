from __future__ import annotations

from fastapi.testclient import TestClient

from servectl.app import create_app


def test_health(handle):
    client = TestClient(create_app(handle))
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model"] == "sum"
    assert body["n_features"] == 3


def test_predict(handle):
    client = TestClient(create_app(handle))
    response = client.post("/predict", json={"instances": [[1, 2, 3], [0, 0, 0]]})
    assert response.status_code == 200
    assert response.json()["predictions"] == [6, 0]


def test_predict_rejects_empty(handle):
    client = TestClient(create_app(handle))
    response = client.post("/predict", json={"instances": []})
    assert response.status_code == 422  # pydantic validation


def test_predict_proba(handle):
    client = TestClient(create_app(handle))
    response = client.post("/predict_proba", json={"instances": [[1, 1, 1]]})
    assert response.status_code == 200
    probs = response.json()["probabilities"][0]
    assert len(probs) == 2
    assert abs(sum(probs) - 1.0) < 1e-9


def test_predict_proba_unsupported(predict_only_handle):
    client = TestClient(create_app(predict_only_handle))
    response = client.post("/predict_proba", json={"instances": [[1, 1]]})
    assert response.status_code == 400


def test_metrics_endpoint_counts_predictions(handle):
    client = TestClient(create_app(handle))
    client.post("/predict", json={"instances": [[1, 2, 3], [1, 1, 1]]})
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    text = metrics.text
    assert "servectl_predictions_total" in text
    assert "servectl_requests_total" in text


def test_separate_apps_have_independent_metrics(handle):
    # Two apps must not collide on the global Prometheus registry.
    create_app(handle)
    create_app(handle)
