
import duckdb
import pandas as pd

from src.pipeline import load_idempotently


def make_frame():
    return pd.DataFrame([
        {
            "country_code": "KHM",
            "country_name": "Cambodia",
            "year": 2024,
            "indicator_code": "TEST.GDP",
            "indicator_name": "Test GDP",
            "value": 100.0,
            "unit": "test units",
            "source": "Test",
            "retrieved_at": "2026-10-26T00:00:00+00:00",
        },
        {
            "country_code": "KHM",
            "country_name": "Cambodia",
            "year": 2025,
            "indicator_code": "TEST.GDP",
            "indicator_name": "Test GDP",
            "value": 110.0,
            "unit": "test units",
            "source": "Test",
            "retrieved_at": "2026-10-26T00:00:00+00:00",
        },
    ])


def test_loading_same_batch_twice_creates_no_duplicates(tmp_path, monkeypatch):
    db_path = tmp_path / "test.duckdb"

    monkeypatch.setattr("src.pipeline.DB_PATH", db_path)

    frame = make_frame()

    load_idempotently(frame)
    load_idempotently(frame)

    connection = duckdb.connect(str(db_path), read_only=True)

    try:
        count = connection.execute(
            "SELECT COUNT(*) FROM economic_observations"
        ).fetchone()[0]

        duplicates = connection.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT country_code, indicator_code, year
                FROM economic_observations
                GROUP BY country_code, indicator_code, year
                HAVING COUNT(*) > 1
            ) AS duplicate_groups
        """).fetchone()[0]
    finally:
        connection.close()

    assert count == 2
    assert duplicates == 0
