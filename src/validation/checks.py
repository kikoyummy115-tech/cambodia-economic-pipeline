from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = [
    "country_code", "country_name", "year", "indicator_code",
    "indicator_name", "value", "unit", "source", "retrieved_at",
]


def validate_observations(frame: pd.DataFrame) -> None:
    """Raise ValueError if a batch violates basic data-contract rules."""
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    if frame.empty:
        raise ValueError("No observations received; refusing to load an empty batch")

    if frame[REQUIRED_COLUMNS].isna().any().any():
        bad_columns = frame[REQUIRED_COLUMNS].columns[
            frame[REQUIRED_COLUMNS].isna().any()
        ].tolist()
        raise ValueError(f"Null values in required columns: {bad_columns}")

    if not pd.api.types.is_numeric_dtype(frame["value"]):
        raise ValueError("'value' must be numeric")

    if not frame["value"].map(lambda x: pd.notna(x) and abs(float(x)) != float("inf")).all():
        raise ValueError("'value' contains non-finite values")

    if not frame["year"].between(1800, 2200).all():
        raise ValueError("Year outside the accepted range 1800–2200")

    key = ["country_code", "indicator_code", "year"]
    if frame.duplicated(key).any():
        duplicates = frame.loc[frame.duplicated(key, keep=False), key]
        raise ValueError(f"Duplicate natural keys found: {duplicates.to_dict('records')}")
    
    non_negative_indicators = {
        "SP.POP.TOTL": "Population",
        "NY.GDP.PCAP.CD": "GDP per capita",
    }

    for indicator_code, indicator_name in non_negative_indicators.items():
        invalid = (
            (frame["indicator_code"] == indicator_code)
            & (frame["value"] < 0)
        )

        if invalid.any():
            raise ValueError(
                f"{indicator_name} cannot be negative. "
                f"Found {int(invalid.sum())} invalid observations."
            )
