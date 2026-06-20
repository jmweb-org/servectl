# Serve a model from inside a container by mounting it:
#
#   docker build -t servectl .
#   docker run --rm -p 8000:8000 -v "$PWD/model.joblib:/model.joblib" \
#     servectl serve /model.joblib --host 0.0.0.0
#
FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/jmweb-org/servectl"
LABEL org.opencontainers.image.description="Serve a model file over HTTP with health and Prometheus metrics."
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN pip install --no-cache-dir .

EXPOSE 8000
ENTRYPOINT ["servectl"]
CMD ["--help"]
