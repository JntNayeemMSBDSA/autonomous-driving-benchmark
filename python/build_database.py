"""Build the portable SQLite analytical database from cleaned CSV files.

Why this exists:
    The delivered SQL DDL remains the source of truth, while this Python loader
    makes database creation reproducible even when the sqlite3 command-line
    client is not installed.

How it works:
    1. Recreates the schema from sql/01_create_schema.sql.
    2. Appends cleaned CSV rows in foreign-key-safe order.
    3. Creates transformation and reporting views.
    4. Runs integrity and row-count checks before committing.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Final

import pandas as pd

from config import CLEAN_DIR, QUALITY_DIR, SQL_DIR

DB_PATH: Final[Path] = SQL_DIR / "autonomous_driving.db"

TABLE_FILES: Final[list[tuple[str, Path]]] = [
    ("dim_company", CLEAN_DIR / "dim_company.csv"),
    ("dim_date", CLEAN_DIR / "dim_date.csv"),
    ("dim_geography", CLEAN_DIR / "dim_geography.csv"),
    ("dim_source", CLEAN_DIR / "dim_source.csv"),
    ("dim_technology", CLEAN_DIR / "dim_technology.csv"),
    ("fact_av_incident", CLEAN_DIR / "fact_av_incident.csv"),
    ("fact_deployment_mileage", CLEAN_DIR / "fact_deployment_mileage.csv"),
    ("fact_disengagement", CLEAN_DIR / "fact_disengagement.csv"),
    ("fact_company_capability", CLEAN_DIR / "fact_company_capability.csv"),
    ("fact_partnership", CLEAN_DIR / "fact_partnership.csv"),
    ("fact_gpu_pricing", CLEAN_DIR / "fact_gpu_pricing.csv"),
    ("fact_training_cost_scenario", CLEAN_DIR / "fact_training_cost_scenario.csv"),
    ("fact_scalability_score", CLEAN_DIR / "fact_scalability_score.csv"),
    ("bridge_company_technology", CLEAN_DIR / "bridge_company_technology.csv"),
    ("qa_validation_result", QUALITY_DIR / "qa_validation_result.csv"),
]


def read_sql(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Required SQL script not found: {path}")
    return path.read_text(encoding="utf-8")


def load_csv(con: sqlite3.Connection, table_name: str, csv_path: Path) -> int:
    if not csv_path.exists():
        raise FileNotFoundError(f"Required input not found: {csv_path}")

    frame = pd.read_csv(csv_path)
    frame = frame.where(pd.notna(frame), None)
    frame.to_sql(table_name, con, if_exists="append", index=False, method="multi")
    loaded = con.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
    if loaded != len(frame):
        raise RuntimeError(
            f"Row-count mismatch for {table_name}: CSV={len(frame)}, database={loaded}"
        )
    return loaded


def build_database() -> dict[str, int]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    row_counts: dict[str, int] = {}
    con = sqlite3.connect(DB_PATH)
    try:
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript(read_sql(SQL_DIR / "01_create_schema.sql"))

        for table_name, csv_path in TABLE_FILES:
            row_counts[table_name] = load_csv(con, table_name, csv_path)

        con.executescript(read_sql(SQL_DIR / "03_clean_transform.sql"))
        con.executescript(read_sql(SQL_DIR / "06_reporting_views.sql"))

        foreign_key_violations = con.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_key_violations:
            raise RuntimeError(f"Foreign-key violations: {foreign_key_violations[:10]}")

        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"SQLite integrity check failed: {integrity}")

        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

    return row_counts


def main() -> int:
    counts = build_database()
    print(f"Built {DB_PATH}")
    for table_name, count in counts.items():
        print(f"  {table_name}: {count:,} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
