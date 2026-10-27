
import pandas as pd
import pytest
from src.validation.checks import validate_observations
import math


def test_value_is_not_null():
    value = 125.5
    assert value is not None


def test_value_is_finite():
    value = 125.5
    assert math.isfinite(value)


def test_population_cannot_be_negative():
    value = 17_000_000
    assert value >= 0


def test_gdp_per_capita_cannot_be_negative():
    value = 1_500
    assert value >= 0
    


def make_valid_row(indicator_code, value):
    return pd.DataFrame([{
        "country_code": "KHM",
        "country_name": "Cambodia",
        "year": 2024,
        "indicator_code": indicator_code,
        "indicator_name": "Test indicator",
        "value": value,
        "unit": "test",
        "source": "World Bank",
        "retrieved_at": "2026-10-26T00:00:00+00:00",
    }])


def test_negative_population_is_rejected():
    frame = make_valid_row("SP.POP.TOTL", -100)

    with pytest.raises(ValueError, match="cannot be negative"):
        validate_observations(frame)


def test_negative_gdp_per_capita_is_rejected():
    frame = make_valid_row("NY.GDP.PCAP.CD", -50)

    with pytest.raises(ValueError, match="cannot be negative"):
        validate_observations(frame)

