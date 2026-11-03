# 03. Exact functions, SQL choices, algorithms, and tradeoffs

This walkthrough distinguishes implemented code from plausible engineering improvements. Name functions accurately, do not claim unexecuted alternatives were tested.

## Pipeline entry and fault behavior
**python/run_pipeline.py:** STEPS list defines task order. subprocess.run([sys.executable, HERE/script, *args], cwd=HERE.parent, check=False) checks each returncode and aborts after first failure. This gives one repeatable local batch and consistent relative paths; unlike a workflow scheduler it has no automated cloud retries, DAG metadata, queueing or incremental-state management.

## Acquisition
**python/acquire_data.py:**
- NHTSA_ARCHIVE_URLS from python/config.py (ADS, Level 2 ADAS, OTHER).
- download() uses urllib.request.Request / urlopen, binary chunks of 1 MiB, 90-second timeout and up to 3 attempts, 2/4/6-second retry waits, deletes incomplete destination on failure.
- sha256() reads bytes in 1 MiB chunks for file checksum, useful for content integrity and audit.
- acquisition_log.json records source URL, path, status, bytes, hash/error.
- --skip-downloads logs "present" or "not_bundled" and intentionally avoids network work; it does not imply archives were ingested.
Reason: official files can be large, mutable and unavailable in a restricted environment; log failures rather than silently substitute. Limitation: no conditional GET, persistence checkpoint or backoff jitter.

## Cleaning
**python/clean_data.py:**
- load_source(): if archives exist, reads present ADS and/or ADAS CSVs with source IDs SRC002/SRC003; otherwise reads verified excerpt.
- snake_case(): regex substitutes nonalphanumeric separators and lowercases headers; predictable canonical schema.
- String trim and blank/NaN-like replacement; uppercase state/model; pd.to_numeric(errors="coerce").
- standardize_entity(): deterministic company canonicalization.
- pd.to_datetime(format="%b-%Y", errors="coerce"): explicit known date grammar, invalid formats become missing rather than crashing without context.
- staging record SHA-256 over sorted columns, null sentinel and joined string values; useful fingerprint, not a unique business key.
- company map created with zip(dim_company.company_name, dim_company.company_id).
- severity_category() bins reported alleged injury descriptions; not independently adjudicated outcomes.
- sort_values(["report_id","report_version"], na_position="first") then drop_duplicates("report_id", keep="last"): latest version in the implemented Python branch.
- Cutoff: month <= 2025-06-30 or month is NA. Do not imply all missing dates are rejected.
- Exports data/staging/nhtsa_incidents_standardized.csv and data/cleaned/fact_av_incident.csv.

**Design alternatives:** SQL ROW_NUMBER can deduplicate at scale and is shown in sql/03_clean_transform.sql; Pandas is used for the bundled local CSV build. The SQL demonstration also ranks on submission_month, while Python uses report_version sorting. They are not literally identical tie-breakers. Do not claim that full 2021–2025 archives were embedded.

## Incident and deployment analytics
**python/analyze_incidents.py:** groupby(reporting_entity_standardized,state,severity_category,dropna=False); COUNT DISTINCT report_id and median of reported mileage; saves incident_summary.csv with explicit "schema-validation outputs only" warning. No causal incident risk or exposure-normalized comparisons.

**python/analyze_deployment.py:** left-merge deployment facts to company dimension; missing company -> California program total. groupby(company_name,metric_name,unit) and date rank to mark latest within each measure. This preserves comparable reporting units and keeps program totals.

**SQL example**, sql/05_analytical_queries.sql: ROW_NUMBER() OVER (PARTITION BY company_id, metric_name, unit ORDER BY date(metric_date) DESC) as recency_rank; select rank=1. Why: latest per *metric and unit*, rather than selecting a single latest record for the company. A new metric does not suppress existing historical metric types. Equal-date ties require an additional deterministic tiebreaker if expanded.

## Cloud scenario engine
**python/gpu_cost_model.py** reads 3 scenarios, 6 GPU-price rows and 3 pricing treatments. Triple nested loop produces 3×6×3=54 rows. math.ceil(required_gpus / gpus_per_instance) chooses whole instances. Assumptions:
- On-demand factor 1.00; committed scenario 0.70; interruptible scenario 0.45. The latter two are modeled assumptions, NOT actual provider quotes or guaranteed savings.
- Storage $23/TB-month, egress $90/TB; ingress zero by assumption.
- Workload utilization 0.70, 0.80 or 0.85 as configured by scenario.
- Training cost = instance count × instance hourly price × hours/run × runs ÷ utilization × price factor.
- Simulation cost = simulation GPU-hours × per-GPU-hour price ÷ utilization × price factor.
- Storage = (base TB+checkpoint TB)×months×23.
- Egress = TB×90.
- total_cost_usd = training+simulation+base_storage+checkpoint_storage+egress.
- source_id comes from price record; workload assumptions come from gpu_scenarios.csv.
Why: standardized what-if experiment avoids pretending to know a company's confidential training bill. A potential refinement would distinguish interruption overhead, networking and cluster efficiency more explicitly, but it is not in current code.

**SQL queries:** sql/05_analytical_queries.sql ranks scenario-provider configurations with ROW_NUMBER; sums discounted and on-demand cases using CASE; sql/06_reporting_views.sql computes component shares with NULLIF(total_cost_usd,0); sql/04_validation_checks.sql flags totals off by >$0.01.

## Scalability engine
**python/scalability_model.py** joins fact_scalability_score to scalability_criteria and dim_company. Schemes map Baseline, L4 operator lens, Platform supplier lens to separate weight columns. Computes weighted = score_1_5 × selected criterion weight, groups by company, divides weighted_sum / weight_sum (100), and generates dense rank within each lens. Four companies × 12 criteria = 48 score rows; 4 companies × 3 lenses = 12 output scores. Scores are analyst ordinal judgments and cannot be treated as independently measured continuous performance.

Role-aware alternatives: a flat average ignores what decision is being made; three weight lenses expose dependency on priorities. Ranking numbers are internal modeling outputs, not objectively validated global winners.

## Database creation
**python/build_database.py:**
- Removes existing SQLite db, connects sqlite3, enables PRAGMA foreign_keys=ON.
- Runs SQL DDL via executescript("sql/01_create_schema.sql").
- Reads each canonical CSV with pd.read_csv, converts missing values to None, appends with DataFrame.to_sql(if_exists="append", index=False, method="multi").
- Checks CSV vs loaded row count per table, creates transformation and reporting views, runs PRAGMA foreign_key_check and PRAGMA integrity_check.
- Commits on success, rollback on exception, closes connection.
This is a full rebuild, not incremental load, CDC or SCD2. The schema includes CHECK constraints, PK/FK constraints and indexes for frequent company/date/metric filters.

**SQL surface:** sql/03_clean_transform.sql demonstrates standardization and a ROW_NUMBER window over reports; sql/04_validation_checks.sql is validation queries; sql/05_analytical_queries.sql covers joins, CTEs, window functions, conditional aggregation; sql/06_reporting_views.sql exposes reusable analytics.

## QA implementation differences
**python/validate_data.py** evaluates exactly SEVEN checks: source cutoff; unique source IDs; four canonical companies; positive hourly GPU prices; cost reconciliation; score range; SQLite FK integrity. It saves pipeline_validation.csv and pipeline_validation.json and returns nonzero on failure.

**data/data_quality/qa_validation_result.csv** is a separately dated, 20-row PASS dataset, not the dynamically computed seven-check suite. Both are useful, but must be described as separate results.

## Where to find formulas
For real source-of-truth implementations inspect python/gpu_cost_model.py, python/scalability_model.py, sql/05_analytical_queries.sql and TMDL measures in powerbi/Autonomous_Driving_Benchmark.SemanticModel/definition/tables/dim_company.tmdl. powerbi/dax_measures.txt is a shorter companion, not necessarily the full 53-measure deployed semantic model.

## Hard interview pitfalls
- No proof of real production GPU training, job scheduling on EKS, Snowflake ingestion, cloud storage transfer, or measured actual model latency in this repo.
- Do not call three schema excerpt incidents a meaningful safety sample.
- Do not infer superiority from 4.52 versus 4.21 scalability scoring; depends on subjective framework and weighting.
- A report/export passing QA does not imply automated service refresh, enterprise RLS, or operational SLA.
- Be clear when a feature is documented but not run on the full NHTSA archive.
