
from pathlib import Path
import duckdb
from src.common.config import DB_PATH, INDICATORS, START_YEAR, END_YEAR


def validate_completeness(db_path: Path | None = None) -> None:
    """Ensure every expected indicator has one record per year."""
    if db_path is None:
        db_path = DB_PATH

    expected_years = set(range(START_YEAR, END_YEAR + 1))
    expected_indicators = set(INDICATORS)

    connection = duckdb.connect(str(db_path), read_only=True)

    try:
        rows = connection.execute("""
            SELECT indicator_code, year, COUNT(*) AS record_count
            FROM economic_observations
            GROUP BY indicator_code, year
        """).fetchall()
    finally:
        connection.close()

    actual = {}

    for indicator_code, year, record_count in rows:
        actual.setdefault(indicator_code, {})
        actual[indicator_code][year] = record_count

    errors = []

    missing_indicators = expected_indicators - set(actual)
    unexpected_indicators = set(actual) - expected_indicators

    if missing_indicators:
        errors.append(f"Missing indicators: {sorted(missing_indicators)}")

    if unexpected_indicators:
        errors.append(f"Unexpected indicators: {sorted(unexpected_indicators)}")

    for indicator in sorted(expected_indicators):
        years_found = set(actual.get(indicator, {}))

        missing_years = expected_years - years_found
        unexpected_years = years_found - expected_years

        if missing_years:
            errors.append(
                f"{indicator}: missing years {sorted(missing_years)}"
            )

        if unexpected_years:
            errors.append(
                f"{indicator}: unexpected years {sorted(unexpected_years)}"
            )

        duplicate_years = [
            year
            for year, count in actual.get(indicator, {}).items()
            if count != 1
        ]

        if duplicate_years:
            errors.append(
                f"{indicator}: invalid record counts for years "
                f"{sorted(duplicate_years)}"
            )

    if errors:
        raise ValueError(
            "Data completeness validation failed:\n- "
            + "\n- ".join(errors)
        )

    print(
        f"Completeness validation passed: "
        f"{len(expected_indicators)} indicators, "
        f"{len(expected_years)} years each."
    )
