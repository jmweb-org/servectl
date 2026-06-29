# servectl

[![CI](https://github.com/jmweb-org/servectl/actions/workflows/ci.yml/badge.svg)](https://github.com/jmweb-org/servectl/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/servectl.svg)](https://pypi.org/project/servectl/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Serve a model file over HTTP in one command, with health and Prometheus metrics
built in.

You have a trained model on disk and you want it behind an HTTP endpoint to try
it, wire it into a demo, or scrape its metrics, without writing a FastAPI app
each time. `servectl` loads the artifact and serves it: a typed `/predict`, a
`/health` check, and a Prometheus `/metrics` endpoint, ready to scrape.

```console
$ servectl serve model.joblib --port 8000
servectl: serving 'model' on http://127.0.0.1:8000

$ curl -s localhost:8000/predict -d '{"instances": [[5.1, 3.5, 1.4, 0.2]]}'
{"predictions": [0]}
```

## Install

```console
$ pip install servectl                 # from PyPI, once released
$ pip install git+https://github.com/jmweb-org/servectl   # latest, available now
```

Loads any joblib/pickle artifact that exposes a scikit-learn-style `predict`
(and optionally `predict_proba`).

## Usage

```console
$ servectl serve model.joblib                 # serve on 127.0.0.1:8000
$ servectl serve model.joblib --host 0.0.0.0 --port 9000
$ servectl info model.joblib                  # inspect without serving
```

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/predict` | `{"instances": [[...], ...]}` to `{"predictions": [...]}` |
| POST | `/predict_proba` | Class probabilities, if the model supports it |
| GET | `/health` | Model name, feature count and version |
| GET | `/metrics` | Prometheus exposition format |

The request body is validated: `instances` must be a non-empty list of equal-
length numeric rows. A bad request returns 400 with a message, not a stack
trace.

## Metrics

The `/metrics` endpoint exposes:

- `servectl_requests_total{endpoint, outcome}` — request count per endpoint and ok/error.
- `servectl_predictions_total` — total prediction instances served.
- `servectl_predict_seconds` — prediction latency histogram.

Each server uses its own registry, so the counters reflect only that process.

### Prometheus scrape example

If `servectl` is running on port 8000, add a scrape job like this to
`prometheus.yml`:

```yaml
scrape_configs:
  - job_name: "servectl"
    metrics_path: "/metrics"
    static_configs:
      - targets: ["localhost:8000"]
```

For multiple model servers, give each target a stable label so dashboards can
separate them:

```yaml
scrape_configs:
  - job_name: "servectl"
    metrics_path: "/metrics"
    static_configs:
      - targets: ["iris-api:8000"]
        labels:
          model: "iris"
      - targets: ["churn-api:8000"]
        labels:
          model: "churn"
```

### Grafana panel queries

Use these PromQL queries for a basic dashboard:

| Panel | PromQL |
| --- | --- |
| Request rate | `sum by (endpoint, outcome) (rate(servectl_requests_total[5m]))` |
| Prediction throughput | `rate(servectl_predictions_total[5m])` |
| p95 prediction latency | `histogram_quantile(0.95, sum by (le) (rate(servectl_predict_seconds_bucket[5m])))` |

For per-model latency when you added a `model` scrape label, group the histogram
by both `model` and `le`:

```promql
histogram_quantile(
  0.95,
  sum by (model, le) (rate(servectl_predict_seconds_bucket[5m]))
)
```

## Scope

`servectl` is for trying a model, demos, and internal services. It does no
authentication, batching, or autoscaling. For a hardened deployment, put it
behind a reverse proxy or use a full serving stack; for a quick, observable
endpoint from a model file, this is one command.

## License

MIT. See [LICENSE](LICENSE).
