"""Command-line interface for servectl."""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console

from servectl import __version__
from servectl.model import ModelError, load_model

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Serve a model file over HTTP with health and Prometheus metrics.",
)
_out = Console()
_err = Console(stderr=True)

EXIT_BAD_INPUT = 2


def _version_callback(value: bool) -> None:
    if value:
        _out.print(f"servectl {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    _version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    """servectl command-line interface."""


@app.command("serve")
def serve(
    model: Path = typer.Argument(..., help="Model artifact (joblib/pickle)."),
    host: str = typer.Option("127.0.0.1", "--host", help="Bind host."),
    port: int = typer.Option(8000, "--port", help="Bind port."),
) -> None:
    """Load a model and serve it on /predict, /health and /metrics."""

    try:
        handle = load_model(model)
    except ModelError as exc:
        _err.print(f"servectl: {exc}")
        raise typer.Exit(EXIT_BAD_INPUT) from exc

    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover - import guard
        _err.print("servectl: uvicorn is not installed")
        raise typer.Exit(EXIT_BAD_INPUT) from exc

    from servectl.app import create_app

    _err.print(f"servectl: serving '{handle.name}' on http://{host}:{port}")
    uvicorn.run(create_app(handle), host=host, port=port, log_level="info")


@app.command("info")
def info(
    model: Path = typer.Argument(..., help="Model artifact to inspect."),
) -> None:
    """Print what servectl can tell about a model without serving it."""

    try:
        handle = load_model(model)
    except ModelError as exc:
        _err.print(f"servectl: {exc}")
        raise typer.Exit(EXIT_BAD_INPUT) from exc
    _out.print(f"name: {handle.name}")
    _out.print(f"n_features: {handle.n_features}")
    _out.print(f"predict_proba: {handle.has_proba}")


def entrypoint() -> None:
    try:
        app()
    except KeyboardInterrupt:  # pragma: no cover - interactive only
        print("servectl: interrupted", file=sys.stderr)
        raise SystemExit(130) from None
