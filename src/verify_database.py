
import duckdb

from src.common.config import DB_PATH


def main():
    connection = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        # Check 1: How many records are stored?
        total = connection.execute("""
            SELECT COUNT(*)
            FROM economic_observations
        """).fetchone()[0]

        print(f"Total observations: {total}")

        # Check 2: How many records exist for each indicator?
        results = connection.execute("""
            SELECT
                indicator_code,
                indicator_name,
                COUNT(*) AS observation_count,
                MIN(year) AS first_year,
                MAX(year) AS last_year
            FROM economic_observations
            GROUP BY indicator_code, indicator_name
            ORDER BY indicator_code
        """).fetchall()

        print("\nObservations by indicator:")
        for row in results:
            print(row)

        # Check 3: Are there duplicate logical observations?
        duplicates = connection.execute("""
            SELECT
                country_code,
                indicator_code,
                year,
                COUNT(*) AS record_count
            FROM economic_observations
            GROUP BY country_code, indicator_code, year
            HAVING COUNT(*) > 1
        """).fetchall()

        print(f"\nDuplicate keys: {len(duplicates)}")

        if duplicates:
            for duplicate in duplicates:
                print(duplicate)
            raise RuntimeError("Database integrity check failed")

        print("\nPASS: No duplicate logical observations.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
