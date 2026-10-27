
import duckdb
import pytest

from src.validation.database_checks import validate_database


def create_test_database(path, rows):
    connection = duckdb.connect(str(path))

    try:
        # No primary key here: this allows us to test duplicate detection.
        connection.execute("""
            CREATE TABLE economic_observations (
                country_code VARCHAR,
                indicator_code VARCHAR,
                year INTEGER,
                value DOUBLE
            )
        """)

        if rows:
            connection.executemany("""
                INSERT INTO economic_observations
                VALUES (?, ?, ?, ?)
            """, rows)
    finally:
        connection.close()


def test_valid_database_passes(tmp_path):
    db_path = tmp_path / "valid.duckdb"

    create_test_database(db_path, [
        ("KHM", "GDP_GROWTH", 2023, 5.0),
        ("KHM", "GDP_GROWTH", 2024, 6.0),
    ])

    validate_database(db_path)


def test_empty_database_fails(tmp_path):
    db_path = tmp_path / "empty.duckdb"
    create_test_database(db_path, [])

    with pytest.raises(ValueError, match="no observations"):
        validate_database(db_path)


def test_duplicate_observations_fail(tmp_path):
    db_path = tmp_path / "duplicates.duckdb"

    create_test_database(db_path, [
        ("KHM", "GDP_GROWTH", 2024, 5.0),
        ("KHM", "GDP_GROWTH", 2024, 5.0),
    ])

    with pytest.raises(ValueError, match="duplicate key groups"):
        validate_database(db_path)

