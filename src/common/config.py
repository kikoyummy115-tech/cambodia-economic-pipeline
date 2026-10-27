from pathlib import Path

# Project root is the directory containing ReadMe.md.
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw" / "world_bank"
PROCESSED_DIR = DATA_DIR / "processed"
WAREHOUSE_DIR = DATA_DIR / "warehouse"
DB_PATH = WAREHOUSE_DIR / "economic.duckdb"

COUNTRY_CODE = "KHM"
START_YEAR = 2000
END_YEAR = 2024
API_BASE_URL = "https://api.worldbank.org/v2"
SOURCE_NAME = "World Bank API"

INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": {
        "name": "GDP growth (annual %)",
        "unit": "percent",
    },
    "NY.GDP.PCAP.CD": {
        "name": "GDP per capita (current US$)",
        "unit": "current US dollars",
    },
    "FP.CPI.TOTL.ZG": {
        "name": "Inflation, consumer prices (annual %)",
        "unit": "percent",
    },
    "SP.POP.TOTL": {
        "name": "Population, total",
        "unit": "people",
    },
}
