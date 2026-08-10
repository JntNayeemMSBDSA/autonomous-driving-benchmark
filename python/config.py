"""Project configuration with reproducible relative paths."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
MANUAL_DIR = DATA_DIR / "manually_compiled"
STAGING_DIR = DATA_DIR / "staging"
CLEAN_DIR = DATA_DIR / "cleaned"
REPORTING_DIR = DATA_DIR / "reporting"
QUALITY_DIR = DATA_DIR / "data_quality"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
SQL_DIR = PROJECT_ROOT / "sql"
POWERBI_DIR = PROJECT_ROOT / "powerbi"

HISTORICAL_CUTOFF = "2025-06-30"
NHTSA_ARCHIVE_URLS = {
    "ads": "https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/Archive-2021-2025/SGO-2021-01_Incident_Reports_ADS.csv",
    "adas": "https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/Archive-2021-2025/SGO-2021-01_Incident_Reports_ADAS.csv",
    "other": "https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/Archive-2021-2025/SGO-2021-01_Incident_Reports_OTHER.csv",
}
