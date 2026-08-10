# Transformation Log

| Step | Input | Transformation | Output | Row effect |
|---|---|---|---|---|
| 1 | NHTSA source file or schema excerpt | Preserve original field names | `data/raw/nhtsa_ads_curated_schema_excerpt.csv` | 3 rows retained |
| 2 | Raw incident archives or bundled excerpt | Convert headers to snake case | `data/staging/nhtsa_incidents_standardized.csv` | No row removal |
| 3 | Raw text fields | Trim whitespace and standardize entity and state | `data/staging/nhtsa_incidents_standardized.csv` | No row removal |
| 4 | Month year fields | Parse incident and submission month | `data/staging/nhtsa_incidents_standardized.csv` | No row removal |
| 5 | Standardized row | Generate SHA 256 record hash | `data/staging/nhtsa_incidents_standardized.csv` | No row removal |
| 6 | Staging incidents | Sort by report ID and version; retain latest version | `fact_av_incident.csv` | 0 duplicates removed in excerpt |
| 7 | Source log | Parse dates and calculate cutoff flag | `dim_source.csv` | 35 of 35 valid |
| 8 | Deployment facts | Preserve unit and period; use NULL for program total company key | `fact_deployment_mileage.csv` | No row removal |
| 9 | Cloud prices and workloads | Calculate instances, compute, storage, transfer, and total | `fact_training_cost_scenario.csv` | 54 scenarios |
| 10 | Scalability evidence | Join score, criterion, company, source, and weights | reporting score tables | 48 score rows |
| 11 | All model tables | Enforce primary keys, foreign keys, checks, and indexes | SQLite database | No FK violations |
| 12 | Reporting tables | Export role aware denormalized tables | Power BI CSV and XLSX | No silent exclusions |

No record is silently removed. Exclusions, deduplication rules, and unavailable source files are documented.
