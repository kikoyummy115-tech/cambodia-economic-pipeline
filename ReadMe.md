# Cambodia Economic Data Pipeline (Starter Project)

A small, reproducible data engineering project that collects Cambodia's macroeconomic indicators from the World Bank API, preserves the raw response, normalizes observations, validates them, and loads them idempotently into DuckDB.

## What this project teaches

- API ingestion and HTTP error handling
- Raw-data preservation
- Data normalization and validation
- Analytical storage with DuckDB
- Idempotent loads (running twice does not create duplicates)
- Automated tests
- Basic pipeline logging

## Indicators

| Code | Indicator | Unit |
|---|---|---|
| `NY.GDP.MKTP.KD.ZG` | GDP growth (annual %) | percent |
| `NY.GDP.PCAP.CD` | GDP per capita (current US$) | current US dollars |
| `FP.CPI.TOTL.ZG` | Inflation, consumer prices (annual %) | percent |
| `SP.POP.TOTL` | Population, total | people |

Data availability varies by indicator and year. Missing observations are skipped, not fabricated.

## 1. Create an environment

Python 3.10+ is recommended.

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Run the pipeline

```powershell
python -m src.pipeline
```

The pipeline will:
1. Request World Bank data for Cambodia.
2. Save the unmodified API response under `data/raw/world_bank/`.
3. Normalize records into a consistent observation schema.
4. Validate the normalized records.
5. Save a normalized CSV under `data/processed/`.
6. Load records into `data/warehouse/economic.duckdb`.
7. Print a summary.

The default period is 2000–2024. Change `START_YEAR` and `END_YEAR` in `src/common/config.py` if you want another period.

## 3. Inspect the database

```powershell
python -c "import duckdb; c=duckdb.connect('data/warehouse/economic.duckdb', read_only=True); print(c.sql('SELECT year, indicator_name, value, unit FROM economic_observations ORDER BY year, indicator_code').df().to_string(index=False)); c.close()"
```

Or run the included query:

```powershell
python -m src.analytics
```

## 4. Run tests

```powershell
pytest -q
```

## Folder map

```text
.
├── .devcontainer/
├── dags/
├── data/
│   ├── raw/world_bank/       # Original API responses; do not edit manually
│   ├── processed/            # Normalized CSV output
│   └── warehouse/            # DuckDB database
├── dummy/                    # Small synthetic fixture for tests
├── flaskapi/                 # Reserved for a later Flask API step
├── soda/checks/              # Reserved for a later Soda data-quality step
├── sql/
│   ├── ddl/
│   └── analytics/
├── src/
│   ├── common/
│   ├── ingestion/
│   ├── transformations/
│   ├── validation/
│   ├── indicators/
│   ├── economics/
│   ├── pipeline.py
│   └── analytics.py
├── tests/
├── Dockerfile
├── Makefile
├── requirements.txt
└── ReadMe.md
```

## Reliability decisions

- **Raw data is preserved:** transformation bugs can be fixed without losing the source response.
- **Explicit schema:** every observation has a country, year, indicator, value, unit, and source.
- **No invented values:** missing data stays missing.
- **Idempotent loading:** the natural key is `(country_code, indicator_code, year)`.
- **Validation before loading:** invalid rows fail early.
- **Tests:** normalization and data-quality rules can be checked automatically.

## Limitations and next improvements

This is a learning-grade, single-machine pipeline, not a production national statistics platform. The World Bank may revise historical values; this starter preserves each downloaded raw snapshot but stores the latest loaded value for each natural key. A more advanced version should add ingestion-run metadata, revision history, retry/backoff, freshness alerts, and scheduled orchestration with Airflow.

National indicators must not be presented as province-level statistics. The pipeline is designed for national time-series analysis.

## Suggested next challenge

Add one indicator, write a test for it, rerun the pipeline twice, and prove that the row count does not increase on the second run.
