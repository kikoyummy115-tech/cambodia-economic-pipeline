
import duckdb
from src.common.config import DB_PATH


def main():
    connection = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        query = """
            SELECT
                indicator_code,
                indicator_name,
                year,
                value
            FROM economic_observations
            WHERE
                value IS NULL
                OR NOT isfinite(value)
                OR (
                    indicator_code IN (
                        'SP.POP.TOTL',
                        'NY.GDP.PCAP.CD'
                    )
                    AND value < 0
                )
            ORDER BY indicator_code, year
        """

        invalid_rows = connection.execute(query).fetchall()

        if invalid_rows:
            print("Data quality issues found:")
            for row in invalid_rows:
                print(row)
        else:
            print("PASS: No invalid values found.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
