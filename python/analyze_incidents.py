"""Incident analysis that preserves reporting-class and denominator warnings."""
from __future__ import annotations
import pandas as pd
from config import CLEAN_DIR, REPORTING_DIR

def main() -> None:
    incidents = pd.read_csv(CLEAN_DIR / "fact_av_incident.csv")
    output = (incidents.groupby(["reporting_entity_standardized","state","severity_category"],dropna=False)
              .agg(report_count=("report_id","nunique"),
                   median_reported_vehicle_mileage=("mileage","median"))
              .reset_index())
    output["comparison_warning"] = (
        "Counts are schema-validation outputs only and must not be interpreted as safety rates."
    )
    REPORTING_DIR.mkdir(parents=True,exist_ok=True)
    output.to_csv(REPORTING_DIR/"incident_summary.csv",index=False)
    print(output.to_string(index=False))

if __name__ == "__main__":
    main()
