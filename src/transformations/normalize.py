from __future__ import annotations

from datetime import datetime
from typing import Any

from src.common.config import COUNTRY_CODE, INDICATORS, SOURCE_NAME


def normalize_indicator_records(
    indicator_code: str,
    source_records: list[dict[str, Any]],
    retrieved_at: str | None = None,
) -> list[dict[str, Any]]:
    """Convert World Bank records to our stable observation schema."""
    if indicator_code not in INDICATORS:
        raise ValueError(f"Indicator is not configured: {indicator_code}")

    metadata = INDICATORS[indicator_code]
    timestamp = retrieved_at or datetime.now().astimezone().isoformat(timespec="seconds")
    normalized = []

    for item in source_records:
        year_text = item.get("date")
        value = item.get("value")

        # The API can return years with null values. Missing values stay missing.
        if value is None or year_text is None:
            continue

        try:
            year = int(year_text)
            numeric_value = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid year/value for {indicator_code}: {item!r}") from exc

        country = item.get("country") or {}
        country_code = country.get("id") or COUNTRY_CODE

        normalized.append({
            "country_code": country_code,
            "country_name": country.get("value") or "Cambodia",
            "year": year,
            "indicator_code": indicator_code,
            "indicator_name": metadata["name"],
            "value": numeric_value,
            "unit": metadata["unit"],
            "source": SOURCE_NAME,
            "retrieved_at": timestamp,
        })

    return normalized
