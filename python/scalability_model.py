"""Role-aware weighted scalability decision model."""
from __future__ import annotations
import pandas as pd
from config import CLEAN_DIR, MANUAL_DIR, REPORTING_DIR

SCHEMES={
    "Baseline":"baseline_weight",
    "L4 operator lens":"l4_operator_weight",
    "Platform supplier lens":"platform_supplier_weight",
}
def main() -> None:
    scores=pd.read_csv(CLEAN_DIR/"fact_scalability_score.csv")
    criteria=pd.read_csv(MANUAL_DIR/"scalability_criteria.csv")
    companies=pd.read_csv(CLEAN_DIR/"dim_company.csv")[["company_id","company_name"]]
    detail=scores.merge(criteria,on="criterion_id").merge(companies,on="company_id")
    rows=[]
    for scheme,weight in SCHEMES.items():
        temp=detail.assign(weighted=detail.score_1_5*detail[weight])
        agg=temp.groupby(["company_id","company_name"],as_index=False).agg(
            weighted_sum=("weighted","sum"),weight_sum=(weight,"sum"))
        agg["weighted_score_1_5"]=agg.weighted_sum/agg.weight_sum
        agg["weighting_scheme"]=scheme
        rows.append(agg)
    output=pd.concat(rows,ignore_index=True)
    output["rank_within_scheme"]=output.groupby("weighting_scheme").weighted_score_1_5.rank(
        method="dense",ascending=False).astype(int)
    REPORTING_DIR.mkdir(parents=True,exist_ok=True)
    output.to_csv(REPORTING_DIR/"scalability_weighted_scores.csv",index=False)
    print(output.sort_values(["weighting_scheme","rank_within_scheme"]).to_string(index=False))

if __name__ == "__main__":
    main()
