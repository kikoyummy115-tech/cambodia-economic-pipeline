import pandas as pd
import pytest

from src.transformations.normalize import normalize_indicator_records
from src.validation.checks import validate_observations


def sample_frame():
    rows = normalize_indicator_records(
        "NY.GDP.MKTP.KD.ZG",
        [
            {"date": "2020", "value": 2.5, "country": {"id": "KHM", "value": "Cambodia"}},
            {"date": "2021", "value": -3.1, "country": {"id": "KHM", "value": "Cambodia"}},
        ],
        "2026-01-01T00:00:00+00:00",
    )
    return pd.DataFrame(rows)


def test_valid_batch_passes():
    validate_observations(sample_frame())


def test_duplicate_natural_key_fails():
    frame = sample_frame()
    frame = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="Duplicate natural keys"):
        validate_observations(frame)


def test_empty_batch_fails():
    with pytest.raises(ValueError, match="No observations"):
        validate_observations(pd.DataFrame(columns=[
            "country_code", "country_name", "year", "indicator_code",
            "indicator_name", "value", "unit", "source", "retrieved_at",
        ]))
