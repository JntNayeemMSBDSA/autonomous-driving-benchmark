"""Analyze deployment indicators without combining incompatible units."""
from __future__ import annotations
import pandas as pd
from config import CLEAN_DIR, REPORTING_DIR

def main() -> None:
    metrics=pd.read_csv(CLEAN_DIR/"fact_deployment_mileage.csv",parse_dates=["metric_date"])
    companies=pd.read_csv(CLEAN_DIR/"dim_company.csv")[["company_id","company_name","ecosystem_role"]]
    output=metrics.merge(companies,on="company_id",how="left")
    output["company_name"]=output.company_name.fillna("California program total")
    output["latest_within_metric"]=(
        output.groupby(["company_name","metric_name","unit"])["metric_date"].rank(method="first",ascending=False).eq(1)
    )
    REPORTING_DIR.mkdir(parents=True,exist_ok=True)
    output.to_csv(REPORTING_DIR/"deployment_metrics.csv",index=False)
    print(output[output.latest_within_metric][["company_name","metric_name","metric_value","unit"]].to_string(index=False))

if __name__ == "__main__":
    main()
