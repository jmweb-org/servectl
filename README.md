# servectl

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
$ pip install servectl
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

## Scope

`servectl` is for trying a model, demos, and internal services. It does no
authentication, batching, or autoscaling. For a hardened deployment, put it
behind a reverse proxy or use a full serving stack; for a quick, observable
endpoint from a model file, this is one command.

## License

MIT. See [LICENSE](LICENSE).
