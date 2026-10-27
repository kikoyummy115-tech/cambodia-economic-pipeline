import duckdb

from src.common.config import DB_PATH


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit("Database not found. Run `python -m src.pipeline` first.")

    with duckdb.connect(str(DB_PATH), read_only=True) as connection:
        print("\nLatest available observation for each indicator:")
        result = connection.execute("""
            SELECT indicator_name, year, value, unit
            FROM economic_observations AS e
            WHERE year = (
                SELECT MAX(e2.year)
                FROM economic_observations AS e2
                WHERE e2.indicator_code = e.indicator_code
            )
            ORDER BY indicator_code
        """).df()
        print(result.to_string(index=False))

        print("\nObservation counts by indicator:")
        counts = connection.execute("""
            SELECT indicator_code, indicator_name, COUNT(*) AS observations,
                   MIN(year) AS first_year, MAX(year) AS last_year
            FROM economic_observations
            GROUP BY indicator_code, indicator_name
            ORDER BY indicator_code
        """).df()
        print(counts.to_string(index=False))


if __name__ == "__main__":
    main()
