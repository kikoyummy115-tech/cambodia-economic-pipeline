
import duckdb
import math
import pytest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.common.config import DB_PATH
@pytest.fixture
def connection():
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    yield conn
    conn.close()


def test_database_contains_observations(connection):
    count = connection.execute(
        "SELECT COUNT(*) FROM economic_observations"
    ).fetchone()[0]

    assert count > 0, "Database contains no observations"


def test_no_null_values(connection):
    count = connection.execute("""
        SELECT COUNT(*)
        FROM economic_observations
        WHERE country_code IS NULL
           OR indicator_code IS NULL
           OR year IS NULL
           OR value IS NULL
    """).fetchone()[0]

    assert count == 0, f"Found {count} rows with null required fields"


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

    assert duplicates == 0, f"Found {duplicates} duplicate groups"


def test_all_values_are_finite(connection):
    values = connection.execute("""
        SELECT value
        FROM economic_observations
    """).fetchall()

    invalid_count = sum(
        1 for (value,) in values
        if value is None or not math.isfinite(value)
    )

    assert invalid_count == 0, f"Found {invalid_count} invalid values"
