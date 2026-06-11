from __future__ import annotations

import numpy as np
import pytest

from servectl.model import ModelHandle


class SumModel:
    """A tiny model: predicts the rounded row sum, with a two-class proba."""

    n_features_in_ = 3

    def predict(self, x):
        arr = np.asarray(x, dtype=float)
        return np.round(arr.sum(axis=1)).astype(int)

    def predict_proba(self, x):
        arr = np.asarray(x, dtype=float)
        p1 = 1.0 / (1.0 + np.exp(-arr.sum(axis=1)))
        return np.stack([1.0 - p1, p1], axis=1)


class PredictOnlyModel:
    n_features_in_ = 2

    def predict(self, x):
        return np.asarray(x, dtype=float).sum(axis=1)


@pytest.fixture
def handle():
    return ModelHandle(SumModel(), name="sum")


@pytest.fixture
def predict_only_handle():
    return ModelHandle(PredictOnlyModel(), name="po")
