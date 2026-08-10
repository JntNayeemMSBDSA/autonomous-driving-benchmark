# Autonomous Driving Technology, Cloud Computing, and Scalability Benchmark

## Project context

This project is an independent, publicly reproducible reconstruction and extension of an earlier Microsoft client based global internship facilitated through the Russell Palmer Career Management Center at Michigan State University. Jannatul Nayeem was not employed by Microsoft. The reconstructed outputs are not represented as the exact historical deliverables submitted to Microsoft.

The reconstruction uses public information and a historical cutoff of **June 30, 2025**. It is designed as a portfolio grade data analytics project with an executed relational database, Python pipeline, analytical notebooks, scenario models, Power BI ready data, visual mockups, a source register, automated quality checks, and written reporting.

![Executive Benchmark dashboard](powerbi/Executive_Benchmark.png)

## Business problem

Autonomous driving companies are often compared with a single leaderboard even though they perform different roles. Tesla develops consumer vehicles and supervised driver assistance. Waymo develops and operates a geofenced Level 4 mobility service. NVIDIA supplies computing, operating software, training, simulation, and reference architectures. Mobileye supplies purpose built chips, software, mapping, and multiple ADAS and autonomy product tiers to automakers.

A responsible benchmark must therefore answer two questions at the same time:

1. What is comparable across the four companies?
2. Which metrics should remain separate because business model, automation level, exposure, geography, reporting method, or data availability differ?

This project answers those questions with a role aware analytical framework.

## Historical cutoff

Only evidence publicly available on or before **June 30, 2025** supports historical findings. Publication dates are stored in `source_log.xlsx` and `data/cleaned/dim_source.csv`. The automated quality layer checks that every source date satisfies the cutoff.

Mutable pages are treated cautiously. Dated SEC filings, government releases, technical papers, archived regulatory datasets, and dated company releases are preferred. Current pages that now contain later information are not used as evidence for post cutoff developments.

## Main analytical questions

The project examines:

1. Ecosystem role and commercial model
2. Sensor and perception strategy
3. Data collection and model development workflow
4. In vehicle computing
5. Training and simulation infrastructure
6. Safety and incident indicators
7. Deployment scale and geography
8. Standardized GPU and cloud cost scenarios
9. Partnerships and integration routes
10. Technical, operational, regulatory, and cost scalability
11. Strategic advantages, constraints, and uncertainty

## Core findings

* **The companies are not four identical competitors.** Tesla and Waymo have direct vehicle or mobility exposure. NVIDIA and Mobileye mainly create platforms or components that are integrated by customers.
* **Waymo had the strongest public exposure aligned Level 4 safety evidence within the cutoff.** Its May 2025 research used 56.7 million rider only miles and matched human benchmarks. This does not create a universal four company safety ranking.
* **Tesla had the broadest direct consumer distribution channel in this group.** Its public filings described a primarily vision based supervised system, custom inference hardware, fleet learning, and Cortex infrastructure. Public system level mileage denominators by software version and operating domain were not available.
* **NVIDIA offered the broadest public train, simulate, and deploy platform.** Direct crash or deployment mileage should not be attributed to NVIDIA because customers determine vehicles, sensors, software, operating domains, and fleet operations.
* **Mobileye demonstrated very broad OEM scale.** It reported 29.0 million EyeQ and SuperVision systems shipped in 2024 and technology in more than 200 million vehicles. Those units span different generations, products, and automation levels.
* **Raw incident totals are inadequate for direct safety comparison.** NHTSA ADS and Level 2 reporting thresholds differ. Reporting entities have different telemetry, geography, exposure, vehicle types, software versions, and reporting practices.
* **Cloud cost is dominated by compute.** In the standardized scenarios, GPU hours, experiment count, utilization, and price model have the greatest effect. Storage and transfer matter more as retained datasets and checkpoints become large.
* **The scalability model is a decision aid, not a winner selection.** It exposes tradeoffs across data, infrastructure, sensors, geography, integration, deployment, regulation, commercial flexibility, and cost.

## Architecture

```text
Public and manual sources
        |
        v
data/raw and data/manually_compiled
        |
        v
data/staging
        |
        v
data/cleaned  ->  SQLite normalized model
        |
        +-------------------+
        |                   |
        v                   v
data/reporting         Power BI ready tables
        |                   |
        v                   v
reports, charts        four report page specifications
```

The normalized model includes:

* `dim_company`
* `dim_date`
* `dim_geography`
* `dim_source`
* `dim_technology`
* `fact_av_incident`
* `fact_deployment_mileage`
* `fact_disengagement`
* `fact_company_capability`
* `fact_partnership`
* `fact_gpu_pricing`
* `fact_training_cost_scenario`
* `fact_scalability_score`
* `bridge_company_technology`
* `qa_validation_result`

The executed database is `sql/autonomous_driving.db`. DDL, load scripts, transformations, validation queries, analytical queries, reporting views, and a complete SQL Server compatible schema are in `sql/`.

## Data sources

The source register contains 35 sources and records:

* organization
* title
* source type
* publication date
* historical period
* access date
* URL
* supported variables or claims
* reliability classification
* limitations
* primary or secondary status
* cutoff validation

Priority sources include NHTSA Standing General Order materials, California DMV reports, Waymo Safety Impact research, company filings and technical documentation, cloud provider documentation, and dated price corroboration.

The complete register is in `source_log.xlsx` and `data/manually_compiled/source_log.csv`.

## Raw data policy

Original field names are preserved in the raw layer. Standardized names, parsed dates, canonical company names, state codes, severity categories, and record hashes are created in staging and clean layers.

The execution environment could not reliably transfer the large NHTSA archive files. The package therefore contains:

1. official archive URLs
2. a retrying acquisition script
3. a verified schema excerpt used only to execute and validate the pipeline
4. staging and cleaning logic
5. duplicate and cutoff checks
6. processed project tables that do not fabricate unavailable records

The excerpt is **not** used to claim incident rates or representative distributions.

## Python work

The `python/` folder includes executed scripts for:

* acquisition and source logging
* incident cleaning and latest version deduplication
* validation and reconciliation
* incident and deployment analysis
* GPU cost modeling
* sensitivity analysis
* scalability scoring
* Power BI table export
* SQLite database recreation from canonical CSV tables
* full pipeline orchestration

All paths are relative to the project root.

## SQL work

The SQL package demonstrates:

* normalized schema creation
* primary and foreign keys
* joins
* common table expressions
* window functions
* latest version deduplication
* conditional aggregation
* date logic
* ranking
* reconciliation
* scenario calculations
* reporting views
* data quality and referential integrity checks

The SQLite database was rebuilt from the canonical cleaned CSV files and validated successfully. `PRAGMA foreign_key_check` returned no violations.

## GPU and cloud cost model

Three standardized workloads are included:

| Scenario | Required GPUs | Training hours per run | Runs | Storage | Simulation GPU hours |
|---|---:|---:|---:|---:|---:|
| Small experimentation | 1 | 24 | 5 | 1 TB | 100 |
| Medium development | 8 | 168 | 10 | 20 TB | 10,000 |
| Large AV training | 64 | 720 | 12 | 200 TB | 100,000 |

Cost components include training compute, simulation compute, persistent storage, checkpoint storage, and egress.

Three pricing treatments are shown:

* on demand at 1.00 times the price snapshot
* committed scenario at 0.70 times
* interruptible scenario at 0.45 times

The discount factors are explicit analytical assumptions, not provider quotes. The workbook `powerbi/powerbi_ready_data.xlsx` includes an editable formula driven scenario calculator.

## Scalability framework

Twelve criteria are scored on a 1 to 5 ordinal scale:

1. Data scale
2. Training infrastructure
3. Simulation capabilities
4. In vehicle compute
5. Sensor complexity
6. Geographic scalability
7. Hardware dependence
8. OEM or fleet integration
9. Deployment maturity
10. Regulatory exposure
11. Commercial flexibility
12. Cost scalability

Each criterion has a definition, measurement method, weight, evidence source, missing data treatment, and interpretation warning. Baseline, Level 4 operator, and platform supplier weight sets are included.

A high sensor complexity score means lower manufacturing and integration burden. It does not mean stronger perception redundancy.

## Power BI package

The Power BI folder contains:

* `Autonomous_Driving_Benchmark.pbix` - refreshed, portable Power BI report
* `Autonomous_Driving_Benchmark.pbip` - source-controlled Power BI project
* `Autonomous_Driving_Benchmark.Report/` - PBIR report definition
* `Autonomous_Driving_Benchmark.SemanticModel/` - TMDL semantic model
* `Autonomous_Driving_Benchmark.pdf` - four-page dashboard export
* `Executive_Benchmark.png` - dashboard preview
* `Autonomous_Driving_Benchmark_QA.md` - build and validation summary
* `build_powerbi_project.py` - reproducible PBIP/PBIR/TMDL generator
* `powerbi_ready_data.xlsx` and exported CSV tables

The report pages are:

1. Executive Benchmark
2. Technology & Workflow
3. Safety & Deployment
4. GPU Cost & Scalability
5. Evidence & Source Detail (hidden in view mode)

The report was opened, refreshed, and saved in Power BI Desktop. It contains 18 model tables, 20 single-direction relationships, 53 explicit DAX measures, and 64 visuals. All supplied QA checks pass.

## Data quality

The quality layer checks:

* duplicate keys
* missing values
* data types
* date parsing
* company name standardization
* state and geographic standardization
* units
* category harmonization
* numeric ranges
* foreign keys
* record counts
* source traceability
* historical cutoff
* reporting changes
* cost component reconciliation
* scalability weights and score ranges

All 20 project validation checks passed. The full results are in `outputs/quality_report.xlsx`.

## Reproduction

From the project root:

```bash
python -m pip install -r requirements.txt
python python/run_pipeline.py
```

To acquire the complete NHTSA archives in a normal networked environment and then rebuild every canonical output:

```bash
python python/acquire_data.py
python python/run_pipeline.py
```

The canonical incident fact ingests ADS and Level 2 ADAS archives when present. The OTHER archive is retained for source audit but is not loaded into the incident fact because its reporting scope differs.

To inspect the executed SQLite database:

```bash
sqlite3 sql/autonomous_driving.db
.read sql/05_analytical_queries.sql
```

The notebooks were executed with the project root as the working directory. `MANIFEST.csv` records the final package contents, file sizes, hashes, and descriptions.

## Ethical and comparability concerns

Safety evidence is sensitive to exposure, system definition, operating domain, geography, weather, road type, vehicle type, reporting threshold, software version, telemetry, and human intervention policy. The project avoids:

* dividing incident counts by unrelated denominators
* treating systems shipped as autonomous miles
* attributing OEM fleet outcomes directly to a component supplier
* treating TOPS as a universal measure of platform capability
* presenting scenario cost as company expenditure
* using post cutoff information to explain historical performance
* claiming a universal safety or autonomy winner

## Project limitations

The most important unresolved questions are exact company training spend, internal dataset size, model architecture, sensor bill of materials, enterprise cloud discounts, per vehicle operating cost, software version exposure, and matched fleet safety denominators. Public information cannot answer these responsibly.

See `documentation/known_limitations.md` and `assumptions_and_limitations.xlsx` for the full register.
