
import duckdb

from src.common.config import DB_PATH


def validate_database(db_path=DB_PATH) -> None:
    """Raise an error if essential database quality checks fail."""

    connection = duckdb.connect(str(db_path), read_only=True)

    try:
        row_count = connection.execute("""
            SELECT COUNT(*)
            FROM economic_observations
        """).fetchone()[0]

        if row_count == 0:
            raise ValueError(
                "Database quality check failed: no observations."
            )

        null_count = connection.execute("""
            SELECT COUNT(*)
            FROM economic_observations
            WHERE country_code IS NULL
               OR indicator_code IS NULL
               OR year IS NULL
               OR value IS NULL
        """).fetchone()[0]

        if null_count:
            raise ValueError(
                f"Database quality check failed: {null_count} rows "
                "contain NULL required fields."
            )

        duplicate_count = connection.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT country_code, indicator_code, year
                FROM economic_observations
                GROUP BY country_code, indicator_code, year
                HAVING COUNT(*) > 1
            ) AS duplicates
        """).fetchone()[0]

        if duplicate_count:
            raise ValueError(
                f"Database quality check failed: "
                f"{duplicate_count} duplicate key groups."
            )

        print(
            f"Database quality checks passed: "
            f"{row_count} observations checked."
        )

    finally:
        connection.close()
