from __future__ import annotations

import joblib
import pytest
from tests.conftest import PredictOnlyModel, SumModel

from servectl.model import ModelError, ModelHandle, load_model


def test_handle_predicts():
    handle = ModelHandle(SumModel())
    assert handle.predict([[1, 2, 3], [0, 0, 0]]) == [6, 0]


def test_handle_reports_metadata():
    handle = ModelHandle(SumModel(), name="m")
    assert handle.name == "m"
    assert handle.n_features == 3
    assert handle.has_proba is True


def test_handle_without_proba():
    handle = ModelHandle(PredictOnlyModel())
    assert handle.has_proba is False
    with pytest.raises(ModelError):
        handle.predict_proba([[1, 2]])


def test_handle_rejects_object_without_predict():
    with pytest.raises(ModelError):
        ModelHandle(object())


def test_predict_requires_2d():
    handle = ModelHandle(SumModel())
    with pytest.raises(ModelError):
        handle.predict([1, 2, 3])  # 1-D


def test_load_model_round_trip(tmp_path):
    path = tmp_path / "model.joblib"
    joblib.dump(SumModel(), path)
    handle = load_model(path)
    assert handle.name == "model"
    assert handle.predict([[1, 1, 1]]) == [3]


def test_load_missing_file(tmp_path):
    with pytest.raises(ModelError):
        load_model(tmp_path / "nope.joblib")
