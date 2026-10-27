from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

import duckdb
import pandas as pd

from src.common.config import (
    DB_PATH, INDICATORS, PROCESSED_DIR, RAW_DIR, WAREHOUSE_DIR,
)
from src.ingestion.world_bank import fetch_indicator
from src.transformations.normalize import normalize_indicator_records
from src.validation.checks import validate_observations
from src.validation.database_checks import validate_database


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

def ensure_directories() -> None:
    for path in (RAW_DIR, PROCESSED_DIR, WAREHOUSE_DIR):
        path.mkdir(parents=True, exist_ok=True)


def load_idempotently(frame: pd.DataFrame) -> int:
    """Upsert a batch using (country_code, indicator_code, year) as natural key.

    Existing observations for keys in this batch are deleted and replaced inside
    a transaction. A failed insert rolls the transaction back.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(DB_PATH))
    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS economic_observations (
                country_code VARCHAR NOT NULL,
                country_name VARCHAR NOT NULL,
                year INTEGER NOT NULL,
                indicator_code VARCHAR NOT NULL,
                indicator_name VARCHAR NOT NULL,
                value DOUBLE NOT NULL,
                unit VARCHAR NOT NULL,
                source VARCHAR NOT NULL,
                retrieved_at TIMESTAMP NOT NULL,
                PRIMARY KEY (country_code, indicator_code, year)
            )
        """)
        connection.register("incoming_batch", frame)
        connection.execute("BEGIN TRANSACTION")
        connection.execute("""
            DELETE FROM economic_observations
            WHERE (country_code, indicator_code, year) IN (
                SELECT country_code, indicator_code, year FROM incoming_batch
            )
        """)

        connection.execute("""
            INSERT INTO economic_observations
            SELECT country_code, country_name, year, indicator_code,
                   indicator_name, value, unit, source, CAST(retrieved_at AS TIMESTAMP)
            FROM incoming_batch
        """)

        # Verify the database before committing the transaction.
        row_count = connection.execute("""
            SELECT COUNT(*)
            FROM economic_observations
        """).fetchone()[0]

        if row_count == 0:
            raise ValueError("Database check failed: no observations.")

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
                f"Database check failed: {null_count} rows contain NULLs."
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
                f"Database check failed: {duplicate_count} duplicate groups."
            )

        connection.execute("COMMIT")

        return len(frame)
    except Exception:
        try:
            connection.execute("ROLLBACK")
        except Exception:
            pass
        raise
    finally:
        connection.close()



def run_pipeline() -> None:
    ensure_directories()
    run_started = datetime.now(timezone.utc)
    all_observations = []

    for indicator_code in INDICATORS:
        logger.info("Ingesting %s", indicator_code)
        source_records = fetch_indicator(indicator_code)
        retrieved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        raw_path = RAW_DIR / f"{indicator_code.replace('.', '_')}_{run_started:%Y%m%dT%H%M%SZ}.json"
        raw_document = {
            "source": "World Bank API",
            "country_code": "KHM",
            "indicator_code": indicator_code,
            "retrieved_at": retrieved_at,
            "records": source_records,
        }
        raw_path.write_text(json.dumps(raw_document, ensure_ascii=False, indent=2), encoding="utf-8")
        all_observations.extend(
            normalize_indicator_records(indicator_code, source_records, retrieved_at)
        )

    frame = pd.DataFrame(all_observations)
    validate_observations(frame)

    # Stable column order makes the processed CSV easier to inspect.
    columns = [
        "country_code", "country_name", "year", "indicator_code",
        "indicator_name", "value", "unit", "source", "retrieved_at",
    ]
    frame = frame[columns].sort_values(["indicator_code", "year"]).reset_index(drop=True)
    csv_path = PROCESSED_DIR / f"cambodia_economic_observations_{run_started:%Y%m%dT%H%M%SZ}.csv"
    frame.to_csv(csv_path, index=False)
    
    
    loaded = load_idempotently(frame)

    # Verify the actual database after loading.
    validate_database()

    logger.info(
        "Pipeline complete: %d observations loaded; CSV=%s",
        loaded,
        csv_path,
    )
    print(f"Success: loaded {loaded} observations into {DB_PATH}")
    print(f"Processed file: {csv_path}")


if __name__ == "__main__":
    run_pipeline()
