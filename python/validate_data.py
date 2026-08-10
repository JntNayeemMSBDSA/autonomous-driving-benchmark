"""Run automated validations and write a quality report."""
from __future__ import annotations
import json
import sqlite3
import pandas as pd
from config import CLEAN_DIR, MANUAL_DIR, QUALITY_DIR, SQL_DIR, HISTORICAL_CUTOFF

def check(name, passed, expected, actual, detail):
    return {"check_name": name, "status": "PASS" if bool(passed) else "FAIL",
            "expected": expected, "actual": actual, "details": detail}

def main() -> int:
    results = []
    sources = pd.read_csv(MANUAL_DIR / "source_log.csv", parse_dates=["publication_date"])
    companies = pd.read_csv(CLEAN_DIR / "dim_company.csv")
    prices = pd.read_csv(CLEAN_DIR / "fact_gpu_pricing.csv")
    costs = pd.read_csv(CLEAN_DIR / "fact_training_cost_scenario.csv")
    scores = pd.read_csv(CLEAN_DIR / "fact_scalability_score.csv")
    results.append(check("Historical cutoff", sources.publication_date.le(HISTORICAL_CUTOFF).all(),
                         "All source dates at or before cutoff", str(sources.publication_date.max().date()),
                         "Prevents post-cutoff evidence leakage"))
    results.append(check("Unique source IDs", sources.source_id.is_unique, "Unique", sources.source_id.nunique(),
                         "Source traceability key"))
    results.append(check("Four canonical companies", set(companies.company_name)=={"Tesla","Waymo","NVIDIA","Mobileye"},
                         "Four canonical names", sorted(companies.company_name.tolist()), "Company-name standardization"))
    results.append(check("Positive GPU prices", prices.hourly_price_usd.gt(0).all(), "All > 0",
                         prices.hourly_price_usd.min(), "Range check"))
    component_cols = ["training_compute_cost_usd","simulation_compute_cost_usd","base_storage_cost_usd",
                      "checkpoint_storage_cost_usd","egress_cost_usd"]
    diff=(costs.total_cost_usd-costs[component_cols].sum(axis=1)).abs().max()
    results.append(check("Cost reconciliation", diff < 0.01, "Max difference < 0.01", diff,
                         "Total equals cost components"))
    results.append(check("Score range", scores.score_1_5.between(1,5).all(), "1 to 5",
                         f"{scores.score_1_5.min()} to {scores.score_1_5.max()}", "Ordinal constraint"))
    con=sqlite3.connect(SQL_DIR/"autonomous_driving.db")
    fk=con.execute("PRAGMA foreign_key_check").fetchall()
    con.close()
    results.append(check("SQLite foreign keys", len(fk)==0, "No violations", len(fk),
                         "Executed database integrity"))
    report=pd.DataFrame(results)
    QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    report.to_csv(QUALITY_DIR/"pipeline_validation.csv",index=False)
    (QUALITY_DIR/"pipeline_validation.json").write_text(json.dumps(results,indent=2,default=str),encoding="utf-8")
    print(report.to_string(index=False))
    return 0 if report.status.eq("PASS").all() else 1

if __name__ == "__main__":
    raise SystemExit(main())
