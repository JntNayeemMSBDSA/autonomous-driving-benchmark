"""Clean and harmonize NHTSA ADS and Level 2 ADAS incident files.

The raw layer preserves official field names. This script standardizes names,
parses dates, deduplicates report versions, enforces the historical cutoff,
and writes the canonical incident fact used by SQLite and Power BI.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pandas as pd

from config import CLEAN_DIR, HISTORICAL_CUTOFF, RAW_DIR, STAGING_DIR


def snake_case(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").lower()


def _read_with_source(path: Path, source_id: str, reporting_class: str) -> pd.DataFrame:
    frame = pd.read_csv(path, low_memory=False)
    if "Source ID" not in frame.columns:
        frame["Source ID"] = source_id
    frame["Project Reporting Class"] = reporting_class
    return frame


def load_source() -> pd.DataFrame:
    """Load downloaded official archives when available, otherwise the excerpt."""
    candidates = [
        (RAW_DIR / "nhtsa_sgo_ads_archive_through_2025-06-15.csv", "SRC002", "ADS"),
        (RAW_DIR / "nhtsa_sgo_adas_archive_through_2025-06-15.csv", "SRC003", "Level 2 ADAS"),
    ]
    available = [
        _read_with_source(path, source_id, reporting_class)
        for path, source_id, reporting_class in candidates
        if path.exists()
    ]
    if available:
        return pd.concat(available, ignore_index=True, sort=False)

    excerpt = RAW_DIR / "nhtsa_ads_curated_schema_excerpt.csv"
    if not excerpt.exists():
        raise FileNotFoundError("Run acquire_data.py or restore the bundled schema excerpt.")
    return _read_with_source(excerpt, "SRC002", "ADS")


def standardize_entity(value: object) -> object:
    if not isinstance(value, str):
        return value
    normalized = value.strip()
    upper = normalized.upper()
    if upper.startswith("WAYMO"):
        return "Waymo"
    if upper.startswith("TESLA"):
        return "Tesla"
    if upper.startswith("NVIDIA"):
        return "NVIDIA"
    if upper.startswith("MOBILEYE"):
        return "Mobileye"
    return normalized.title()


def severity_category(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        return "Unknown or not reported"
    upper = value.upper()
    if "NO INJUR" in upper:
        return "No injury reported"
    if "FATAL" in upper:
        return "Fatality alleged"
    if "SERIOUS" in upper:
        return "Serious injury alleged"
    if "MINOR" in upper or "MODERATE" in upper or "INJUR" in upper:
        return "Injury alleged"
    return value.strip().title()


def clean_incidents(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    staging = raw.copy()
    staging.columns = [snake_case(c) for c in staging.columns]

    for col in staging.select_dtypes(include="object").columns:
        staging[col] = staging[col].map(lambda x: x.strip() if isinstance(x, str) else x)
        staging[col] = staging[col].replace({"": pd.NA, "nan": pd.NA, "NaN": pd.NA})

    if "reporting_entity" not in staging.columns:
        staging["reporting_entity"] = pd.NA
    staging["reporting_entity_standardized"] = staging["reporting_entity"].map(standardize_entity)

    for raw_field, clean_field in [
        ("incident_date", "incident_month"),
        ("report_submission_date", "submission_month"),
    ]:
        staging[clean_field] = pd.to_datetime(
            staging.get(raw_field), format="%b-%Y", errors="coerce"
        )

    if "state" in staging.columns:
        staging["state"] = staging["state"].str.upper().str.strip()
    if "model" in staging.columns:
        staging["model"] = staging["model"].str.upper().str.strip()

    for field in ["report_version", "model_year", "mileage", "sv_precrash_speed_mph"]:
        if field in staging.columns:
            staging[field] = pd.to_numeric(staging[field], errors="coerce")

    hash_columns = sorted(staging.columns.tolist())
    staging["record_hash"] = (
        staging[hash_columns]
        .fillna("<NA>")
        .astype(str)
        .agg("|".join, axis=1)
        .map(lambda text: hashlib.sha256(text.encode("utf-8")).hexdigest())
    )

    companies = pd.read_csv(CLEAN_DIR / "dim_company.csv", usecols=["company_id", "company_name"])
    company_map = dict(zip(companies["company_name"], companies["company_id"]))
    staging["company_id"] = staging["reporting_entity_standardized"].map(company_map)
    staging["severity_category"] = staging.get(
        "highest_injury_severity_alleged", pd.Series(index=staging.index, dtype="object")
    ).map(severity_category)

    clean = staging.copy()
    if {"report_id", "report_version"}.issubset(clean.columns):
        clean = clean.sort_values(["report_id", "report_version"], na_position="first")
        clean = clean.drop_duplicates("report_id", keep="last")

    cutoff = pd.Timestamp(HISTORICAL_CUTOFF)
    clean = clean[clean["incident_month"].le(cutoff) | clean["incident_month"].isna()].copy()

    required = [
        "report_id", "report_version", "company_id", "reporting_entity_standardized",
        "report_type", "incident_month", "submission_month", "city", "state", "make",
        "model", "model_year", "mileage", "roadway_type", "roadway_surface", "lighting",
        "crash_with", "highest_injury_severity_alleged", "severity_category",
        "property_damage", "sv_pre_crash_movement", "sv_precrash_speed_mph", "within_odd",
        "source_id", "record_hash",
    ]
    for field in required:
        if field not in clean.columns:
            clean[field] = pd.NA
    clean = clean[required]

    clean["report_version"] = clean["report_version"].fillna(1).astype(int)
    for field in ["company_id", "model_year"]:
        clean[field] = clean[field].astype("Int64")
    for field in ["incident_month", "submission_month"]:
        clean[field] = pd.to_datetime(clean[field], errors="coerce").dt.strftime("%Y-%m-%d")

    return staging, clean


def main() -> None:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    staging, clean = clean_incidents(load_source())
    staging.to_csv(STAGING_DIR / "nhtsa_incidents_standardized.csv", index=False)
    clean.to_csv(CLEAN_DIR / "fact_av_incident.csv", index=False)
    print({"staging_rows": len(staging), "clean_rows": len(clean)})


if __name__ == "__main__":
    main()
