
import duckdb
import pytest

from src.common.config import DB_PATH
from src.analytics import main


def test_gdp_growth_summary_calculation(tmp_path, monkeypatch, capsys):
    db_path = tmp_path / "analytics.duckdb"
    connection = duckdb.connect(str(db_path))

    connection.execute("""
        CREATE TABLE economic_observations (
            indicator_code VARCHAR,
            indicator_name VARCHAR,
            year INTEGER,
            value DOUBLE,
            unit VARCHAR
        )
    """)

    connection.executemany("""
        INSERT INTO economic_observations VALUES (?, ?, ?, ?, ?)
    """, [
        ("NY.GDP.MKTP.KD.ZG", "GDP growth", 2020, -2.0, "percent"),
        ("NY.GDP.MKTP.KD.ZG", "GDP growth", 2021, 4.0, "percent"),
        ("NY.GDP.MKTP.KD.ZG", "GDP growth", 2022, 7.0, "percent"),
    ])

    connection.close()

    monkeypatch.setattr("src.analytics.DB_PATH", db_path)

    main()
    output = capsys.readouterr().out

    assert "GDP growth summary (2000–2024):" in output
    assert "3.0" in output
    assert "-2.0" in output
    assert "7.0" in output
