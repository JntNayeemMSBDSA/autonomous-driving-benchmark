"""Export Power BI-ready CSV tables from the cleaned relational layer."""
from __future__ import annotations
import shutil
from pathlib import Path
from config import CLEAN_DIR, REPORTING_DIR, POWERBI_DIR

TABLES=[
    "dim_company.csv","dim_date.csv","dim_geography.csv","dim_source.csv","dim_technology.csv",
    "fact_av_incident.csv","fact_deployment_mileage.csv","fact_disengagement.csv",
    "fact_company_capability.csv","fact_partnership.csv","fact_gpu_pricing.csv",
    "fact_training_cost_scenario.csv","fact_scalability_score.csv","bridge_company_technology.csv"
]
def main() -> None:
    target=POWERBI_DIR/"csv"
    target.mkdir(parents=True,exist_ok=True)
    copied=0
    for name in TABLES:
        src=CLEAN_DIR/name
        if src.exists():
            shutil.copy2(src,target/name)
            copied+=1
    for src in REPORTING_DIR.glob("*.csv"):
        shutil.copy2(src,target/src.name)
    print({"clean_tables_copied":copied,"target":str(target)})

if __name__ == "__main__":
    main()
