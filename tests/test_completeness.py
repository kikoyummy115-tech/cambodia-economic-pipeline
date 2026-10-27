
import duckdb
import pytest

from src.validation.completeness import validate_completeness


def test_missing_year_raises_error(tmp_path, monkeypatch):
    db_path = tmp_path / "incomplete.duckdb"
    connection = duckdb.connect(str(db_path))

    connection.execute("""
        CREATE TABLE economic_observations (
            indicator_code VARCHAR,
            year INTEGER
        )
    """)

    # Missing 2001 for this indicator.
    connection.executemany(
        "INSERT INTO economic_observations VALUES (?, ?)",
        [
            ("FP.CPI.TOTL.ZG", 2000),
            ("FP.CPI.TOTL.ZG", 2002),
        ],
    )
    connection.close()

    monkeypatch.setattr(
        "src.validation.completeness.DB_PATH",
        db_path,
    )

    with pytest.raises(ValueError, match="missing years"):
        validate_completeness()
