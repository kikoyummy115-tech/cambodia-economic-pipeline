
import duckdb
import math
import pytest


@pytest.fixture
def connection(tmp_path):
    db_path = tmp_path / "test_economic.duckdb"
    conn = duckdb.connect(str(db_path))

    conn.execute("""
        CREATE TABLE economic_observations (
            country_code VARCHAR,
            country_name VARCHAR,
            year INTEGER,
            indicator_code VARCHAR,
            indicator_name VARCHAR,
            value DOUBLE,
            unit VARCHAR,
            source VARCHAR,
            retrieved_at TIMESTAMP
        )
    """)

    conn.executemany("""
        INSERT INTO economic_observations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (
            "KHM", "Cambodia", 2023, "TEST.GDP", "Test GDP",
            5.0, "percent", "Test", "2026-01-01 00:00:00"
        ),
        (
            "KHM", "Cambodia", 2024, "TEST.GDP", "Test GDP",
            6.0, "percent", "Test", "2026-01-01 00:00:00"
        ),
    ])

    yield conn
    conn.close()


def test_database_contains_observations(connection):
    count = connection.execute("""
        SELECT COUNT(*) FROM economic_observations
    """).fetchone()[0]

    assert count > 0


def test_no_null_values(connection):
    count = connection.execute("""
        SELECT COUNT(*)
        FROM economic_observations
        WHERE country_code IS NULL
           OR indicator_code IS NULL
           OR year IS NULL
           OR value IS NULL
    """).fetchone()[0]

    assert count == 0


def test_no_duplicate_observations(connection):
    duplicates = connection.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT country_code, indicator_code, year
            FROM economic_observations
            GROUP BY country_code, indicator_code, year
            HAVING COUNT(*) > 1
        ) AS duplicate_groups
    """).fetchone()[0]

    assert duplicates == 0


def test_all_values_are_finite(connection):
    values = connection.execute("""
        SELECT value FROM economic_observations
    """).fetchall()

    assert all(
        value is not None and math.isfinite(value)
        for (value,) in values
    )
