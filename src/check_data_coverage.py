
import duckdb

from src.common.config import DB_PATH


def main():
    connection = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        query = """
            WITH year_range AS (
                SELECT
                    indicator_code,
                    indicator_name,
                    MIN(year) AS first_year,
                    MAX(year) AS last_year
                FROM economic_observations
                GROUP BY indicator_code, indicator_name
            ),
            expected_years AS (
                SELECT
                    r.indicator_code,
                    r.indicator_name,
                    UNNEST(generate_series(
                        r.first_year,
                        r.last_year
                    )) AS year
                FROM year_range r
            )
            SELECT
                e.indicator_code,
                e.indicator_name,
                e.year AS missing_year
            FROM expected_years e
            LEFT JOIN economic_observations o
                ON o.indicator_code = e.indicator_code
                AND o.year = e.year
            WHERE o.year IS NULL
            ORDER BY e.indicator_code, e.year
        """

        missing = connection.execute(query).fetchall()

        if missing:
            print("Missing years found:")
            for row in missing:
                print(row)
        else:
            print("No missing years found within each indicator's range.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
