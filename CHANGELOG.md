# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Documented Prometheus scrape configuration and starter Grafana panel queries.

## [0.2.0] - 2026-06-20

### Added
- Docker image and a published container entry point.
- Continuous integration across Python 3.10, 3.11 and 3.12.
- Expanded documentation, including endpoints, metrics and scope.

## [0.1.0] - 2026-06-17

### Added
- `serve` command: load a joblib/pickle model and serve `/predict`,
  `/predict_proba`, `/health` and Prometheus `/metrics`.
- `info` command: inspect a model artifact without serving it.
- Request validation and clean 400 responses on bad input.
- Per-server Prometheus registry with request, prediction and latency metrics.

[Unreleased]: https://github.com/jmweb-org/servectl/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/jmweb-org/servectl/releases/tag/v0.2.0
[0.1.0]: https://github.com/jmweb-org/servectl/releases/tag/v0.1.0
