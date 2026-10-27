from __future__ import annotations

import logging
from typing import Any

import requests

from src.common.config import API_BASE_URL, COUNTRY_CODE, END_YEAR, INDICATORS, START_YEAR

logger = logging.getLogger(__name__)


def fetch_indicator(indicator_code: str, session: requests.Session | None = None) -> list[dict[str, Any]]:
    """Fetch one World Bank indicator for Cambodia.

    Returns the decoded API payload as a list. The caller is responsible for
    saving the raw response before transforming it.
    """
    if indicator_code not in INDICATORS:
        raise ValueError(f"Indicator is not configured: {indicator_code}")

    client = session or requests.Session()
    url = f"{API_BASE_URL}/country/{COUNTRY_CODE}/indicator/{indicator_code}"
    params = {
        "date": f"{START_YEAR}:{END_YEAR}",
        "format": "json",
        "per_page": 2000,
    }
    response = client.get(url, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError(f"Unexpected World Bank response for {indicator_code}: {payload!r}")

    records = payload[1] or []
    if not isinstance(records, list):
        raise ValueError(f"Unexpected observations payload for {indicator_code}")

    logger.info("Fetched %s source records for %s", len(records), indicator_code)
    return records
