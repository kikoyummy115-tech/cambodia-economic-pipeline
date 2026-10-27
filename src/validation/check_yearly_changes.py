
import duckdb
from src.common.config import DB_PATH


def main():
    connection = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        query = """
            WITH yearly_changes AS (
                SELECT
                    indicator_code,
                    indicator_name,
                    year,
                    value,
                    LAG(year) OVER (
                        PARTITION BY indicator_code
                        ORDER BY year
                    ) AS previous_year,
                    LAG(value) OVER (
                        PARTITION BY indicator_code
                        ORDER BY year
                    ) AS previous_value
                FROM economic_observations
            )
            SELECT
                indicator_code,
                indicator_name,
                previous_year,
                year,
                previous_value,
                value,
                ROUND(
                    100.0 * (value - previous_value)
                    / NULLIF(ABS(previous_value), 0),
                    2
                ) AS percent_change
            FROM yearly_changes
            WHERE
                previous_value IS NOT NULL
                AND previous_value != 0
                AND ABS(
                    100.0 * (value - previous_value)
                    / ABS(previous_value)
                ) > 50
                AND year = previous_year + 1
            ORDER BY indicator_code, year
        """

        results = connection.execute(query).fetchall()

        if results:
            print("Large year-to-year changes to review:")
            for row in results:
                print(row)
        else:
            print("PASS: No consecutive-year changes above 50%.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
