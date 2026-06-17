from __future__ import annotations

import joblib
from tests.conftest import SumModel
from typer.testing import CliRunner

from servectl import __version__
from servectl import cli as cli_module

runner = CliRunner()


def test_version():
    result = runner.invoke(cli_module.app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_info(tmp_path):
    path = tmp_path / "model.joblib"
    joblib.dump(SumModel(), path)
    result = runner.invoke(cli_module.app, ["info", str(path)])
    assert result.exit_code == 0
    assert "n_features: 3" in result.stdout
    assert "predict_proba: True" in result.stdout


def test_info_missing_model(tmp_path):
    result = runner.invoke(cli_module.app, ["info", str(tmp_path / "nope.joblib")])
    assert result.exit_code == cli_module.EXIT_BAD_INPUT


def test_serve_missing_model_fails_fast(tmp_path):
    result = runner.invoke(cli_module.app, ["serve", str(tmp_path / "nope.joblib")])
    assert result.exit_code == cli_module.EXIT_BAD_INPUT
