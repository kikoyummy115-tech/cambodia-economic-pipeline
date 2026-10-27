# Cambodia Economic Development Analytics

An end-to-end data engineering and analytics project that collects Cambodia's macroeconomic indicators from the World Bank API, validates and stores the data in DuckDB, and presents historical trends through an interactive Streamlit dashboard.

## Project Features

- **API ingestion:** Fetch economic indicators from the World Bank API.
- **Raw-data preservation:** Keep original API responses for traceability.
- **Data transformation:** Normalize observations into a consistent schema.
- **Data quality:** Validate records, database integrity, and annual data completeness.
- **Analytical warehouse:** Store observations in DuckDB.
- **Idempotent loading:** Repeated pipeline runs do not create duplicate observations.
- **Automated testing:** Test pipeline behavior, analytics, and data-quality rules.
- **Interactive dashboard:** Explore economic indicators, filter years, inspect records, and download CSV files.

## Dashboard

The Streamlit dashboard provides:

- KPI cards for GDP growth, inflation, GDP per capita, and population.
- Interactive historical trend charts.
- A year-range slider.
- A historical data table.
- CSV downloads for filtered observations.
- A data-quality summary and completeness warning.

## Economic Indicators

| Indicator                             | World Bank Code     | Unit               |
| ------------------------------------- | ------------------- | ------------------ |
| GDP growth (annual %)                 | `NY.GDP.MKTP.KD.ZG` | Percent            |
| GDP per capita (current US$)          | `NY.GDP.PCAP.CD`    | Current US dollars |
| Inflation, consumer prices (annual %) | `FP.CPI.TOTL.ZG`    | Percent            |
| Population, total                     | `SP.POP.TOTL`       | People             |

**Country:** Cambodia (`KHM`)

**Default period:** 2000–2024

Data availability varies by indicator and year. Missing observations are not fabricated.

## Technology Stack

- Python
- World Bank API
- pandas
- DuckDB
- Streamlit
- pytest
- SQL

## Getting Started

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Run the data pipeline

```powershell
python -m src.pipeline
```

The pipeline:

1. Requests World Bank data for Cambodia.
2. Saves raw API responses under `data/raw/world_bank/`.
3. Normalizes observations.
4. Validates the processed records.
5. Saves normalized CSV output under `data/processed/`.
6. Loads observations into `data/warehouse/economic.duckdb`.
7. Runs database and completeness checks.
8. Prints a summary of the results.

The default year range is configured in `src/common/config.py`.

### 3. Launch the dashboard

Run the pipeline first so the DuckDB database exists, then execute:

```powershell
python -m streamlit run dashboard.py
```

Streamlit will provide a local URL in your terminal. Open that URL in your browser.

Choose an indicator, adjust the year range, inspect the historical data table, and download the filtered observations as CSV.

### 4. Run the analytics module

```powershell
python -m src.analytics
```

This prints the latest available observation for each indicator, observation counts, and a GDP growth summary.

### 5. Inspect the database

```powershell
python -c "import duckdb; c=duckdb.connect('data/warehouse/economic.duckdb', read_only=True); print(c.sql('SELECT year, indicator_name, value, unit FROM economic_observations ORDER BY year, indicator_code').df().to_string(index=False)); c.close()"
```

### 6. Run automated tests

```powershell
pytest -q
```

## Project Structure

```text
.
├── data/
│   ├── raw/world_bank/       # Original API responses
│   ├── processed/            # Normalized CSV output
│   └── warehouse/            # DuckDB database
├── src/
│   ├── common/               # Shared configuration
│   ├── ingestion/            # World Bank API ingestion
│   ├── transformations/      # Data normalization
│   ├── validation/           # Data-quality checks
│   ├── economics/            # Economic analysis
│   ├── pipeline.py           # Pipeline entry point
│   └── analytics.py          # Analytical queries
├── tests/                    # Automated tests
├── sql/
│   ├── ddl/
│   └── analytics/
├── dags/                     # Reserved for orchestration
├── flaskapi/                 # Reserved for a future API
├── soda/checks/              # Reserved for future Soda checks
├── dashboard.py              # Streamlit dashboard
├── requirements.txt
├── Dockerfile
├── Makefile
└── README.md
```

## Reliability and Design Decisions

- **Preserve raw data:** Original API responses remain available for reprocessing.
- **Use an explicit schema:** Observations include country, year, indicator, value, unit, and source.
- **Do not invent missing values:** Missing observations remain missing.
- **Make loading idempotent:** The natural key is `(country_code, indicator_code, year)`.
- **Validate data:** Invalid records and completeness problems can be detected before or after loading.
- **Automate verification:** Tests help protect data transformations, database behavior, and analytical logic.

## Limitations

This is a learning and portfolio project, not a production national statistics platform.

- Historical World Bank values may be revised.
- The warehouse stores the latest loaded value for each natural key rather than a full revision history.
- The dashboard presents national indicators, not province-level statistics.
- The current dashboard provides basic data-quality checks, not a complete statistical audit.

## Future Improvements

Potential extensions include:

- Automated scheduled ingestion with Apache Airflow.
- Retry policies and API freshness monitoring.
- Ingestion-run metadata and historical revision tracking.
- Advanced data-quality checks with Soda.
- A Flask REST API for serving economic data.
- Docker-based deployment and CI/CD.
- Additional indicators and analytical visualizations.

## Learning Objectives

This project demonstrates practical experience with API ingestion, data transformation, validation, analytical storage, SQL, automated testing, and interactive data visualization.

It provides a foundation for expanding into more advanced data engineering systems.
