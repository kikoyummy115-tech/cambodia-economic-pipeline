
import duckdb
import pytest


EXPECTED_INDICATORS = {
    "FP.CPI.TOTL.ZG",
    "NY.GDP.MKTP.KD.ZG",
    "NY.GDP.PCAP.CD",
    "SP.POP.TOTL",
}


@pytest.fixture
def connection(tmp_path):
    db_path = tmp_path / "economic.duckdb"
    conn = duckdb.connect(str(db_path))

    conn.execute("""
        CREATE TABLE economic_observations (
            country_code VARCHAR,
            indicator_code VARCHAR,
            year INTEGER,
            value DOUBLE
        )
    """)

    rows = [
        ("KHM", indicator, year, 1.0)
        for indicator in EXPECTED_INDICATORS
        for year in range(2000, 2025)
    ]

    conn.executemany(
        "INSERT INTO economic_observations VALUES (?, ?, ?, ?)",
        rows,
    )

    yield conn
    conn.close()


def test_expected_indicators_are_present(connection):
    actual = {
        row[0]
        for row in connection.execute("""
            SELECT DISTINCT indicator_code
            FROM economic_observations
        """).fetchall()
    }

    assert actual == EXPECTED_INDICATORS


def test_each_indicator_covers_expected_years(connection):
    results = connection.execute("""
        SELECT indicator_code, COUNT(*), MIN(year), MAX(year)
        FROM economic_observations
        GROUP BY indicator_code
    """).fetchall()

    assert len(results) == len(EXPECTED_INDICATORS)

    for indicator, count, first_year, last_year in results:
        assert count == 25, f"{indicator} should have 25 records"
        assert first_year == 2000
        assert last_year == 2024
