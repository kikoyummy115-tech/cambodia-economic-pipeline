from src.transformations.normalize import normalize_indicator_records


def test_normalize_skips_missing_values():
    records = [
        {"date": "2020", "value": 2.5, "country": {"id": "KHM", "value": "Cambodia"}},
        {"date": "2021", "value": None, "country": {"id": "KHM", "value": "Cambodia"}},
    ]
    result = normalize_indicator_records(
        "NY.GDP.MKTP.KD.ZG", records, "2026-01-01T00:00:00+00:00"
    )
    assert len(result) == 1
    assert result[0]["year"] == 2020
    assert result[0]["value"] == 2.5
    assert result[0]["unit"] == "percent"


def test_normalize_uses_expected_country():
    result = normalize_indicator_records(
        "SP.POP.TOTL",
        [{"date": "2020", "value": 16000000, "country": {"id": "KHM", "value": "Cambodia"}}],
        "2026-01-01T00:00:00+00:00",
    )
    assert result[0]["country_code"] == "KHM"
