# 02. Architecture, data contracts, ER model, grains and lineage

## Architecture and orchestration

Entry point: python/run_pipeline.py. It runs (in order): acquire_data.py --skip-downloads; clean_data.py; analyze_incidents.py; analyze_deployment.py; gpu_cost_model.py; scalability_model.py; export_powerbi_tables.py; build_database.py; validate_data.py. It launches each child process with sys.executable and subprocess.run, stops at first nonzero exit, and uses repository-root cwd. This is sequential batch orchestration, not Airflow, dbt, streaming or cloud orchestration.

Data layers:
- data/raw: original-format input and three-row ADS schema excerpt; acquisition log.
- data/manually_compiled: source register, company/criterion/scenario assumptions and dictionaries.
- data/staging: standardized incident records before latest-version and cutoff filtering.
- data/cleaned: canonical dimension/fact/bridge CSVs.
- data/reporting: analysis-specific, denormalized output for dashboards and charts.
- data/data_quality: validity reports, missingness and reconciliation artifacts.
- sql/autonomous_driving.db: delivered SQLite relational database.
- powerbi/csv plus powerbi_ready_data.xlsx: reporting and semantic-model inputs.
- notebooks/: descriptive/safety, cost, scalability analyses.
- outputs/: charts, tables, workbook-based QA.

## Core SQLite schema (15 named physical tables)

Dimensions (five):
1. dim_company: one row/company; PK company_id, unique company_name, role/business/sensor summaries.
2. dim_date: one row/day; PK date_key, unique full_date.
3. dim_geography: one row/geographic record; PK geography_id.
4. dim_source: one row/source; PK source_id, date/URL/primary flag/reliability.
5. dim_technology: one row/technology; PK technology_id, unique technology_name.

Fact/analytical tables (eight):
6. fact_av_incident: one latest retained version/report_id; PK report_id; company_id/source_id foreign keys.
7. fact_deployment_mileage: one sourced observation for metric, company or program, unit, date/period; PK deployment_metric_id.
8. fact_disengagement: one reported disengagement period/party; PK disengagement_id; can be blank/limited in delivered Power BI workflow. Do not imply comprehensive data.
9. fact_company_capability: one company/category evidence item; PK capability_id; company_id, source_id.
10. fact_partnership: one sourced partnership scope/event; PK partnership_id.
11. fact_gpu_pricing: one cloud provider/instance reference and price snapshot; PK gpu_price_id.
12. fact_training_cost_scenario: one workload scenario × GPU configuration × pricing treatment; PK cost_scenario_id; FK gpu_price_id plus source_id.
13. fact_scalability_score: one company × criterion scored evidence record; PK score_id; criterion_id is interpreted by separate CSV criteria metadata.
14. bridge_company_technology: M:N associative table keyed (company_id,technology_id), with relationship_type.
15. qa_validation_result: one QA outcome, PK validation_id.

This is five dimensions, eight fact/analytical tables, one bridge, one QA table. Do not label the entire implementation “a simple five-dimension, eight-fact star”; it is a normalized relational model with some snowflaked analytical relationships and multiple fact grains.

## Key join paths

dim_company.company_id -> fact_av_incident / fact_deployment_mileage / fact_company_capability / fact_partnership / fact_disengagement / fact_scalability_score.
dim_source.source_id -> source-bearing facts.
dim_technology.technology_id -> bridge_company_technology.technology_id; dim_company.company_id -> bridge_company_technology.company_id.
fact_gpu_pricing.gpu_price_id -> fact_training_cost_scenario.gpu_price_id (SQLite).
dim_date.full_date -> applicable dated facts in Power BI.
scalability_criteria.criterion_id -> fact_scalability_score.criterion_id in the Power BI semantic model (criteria stored in manually compiled CSV).
No relationship between company incidents and cloud-price records. Do not join two facts by arbitrary row order.

## ER diagram (conceptual)

~~~mermaid
erDiagram
  dim_company ||--o{ fact_av_incident : has
  dim_company ||--o{ fact_deployment_mileage : measures
  dim_company ||--o{ fact_company_capability : documents
  dim_company ||--o{ fact_partnership : joins
  dim_company ||--o{ fact_scalability_score : scored
  dim_company ||--o{ bridge_company_technology : uses
  dim_technology ||--o{ bridge_company_technology : mapped
  dim_source ||--o{ fact_av_incident : evidences
  dim_source ||--o{ fact_deployment_mileage : evidences
  dim_source ||--o{ fact_company_capability : evidences
  dim_source ||--o{ fact_training_cost_scenario : prices
  dim_source ||--o{ fact_scalability_score : evidences
  fact_gpu_pricing ||--o{ fact_training_cost_scenario : configured
~~~

The diagram is conceptual and omits several source-key links for readability. Use sql/01_create_schema.sql and relationships.tmdl as exact implementation authority. SQLite and Power BI intentionally have different relationship arrangements.

## Power BI model distinction

The completed Power BI model has 18 model tables and 20 declared relationships. It also contains analytical reporting tables not represented by one-to-one copies of every physical SQLite table, e.g., fact_safety_indicator, fact_cost_sensitivity, scalability_criteria and weighting_scheme. The Power BI model has one inactive date-to-incident-month relationship. All declared relationships use single-direction filtering. The GPU price -> cost scenario candidate relationship was not used in Power BI because it would give an ambiguous filter route through dim_source. Scenario rows therefore retain price-provider attributes.

Do not claim that fact_disengagement is an independently populated Power BI fact. The existing README and QA explicitly say none was invented.

## Data cleaning lineage

1. load_source() checks for ADS and Level 2 archives. When either archive is present, available archives are concatenated; otherwise 3-row excerpt is loaded. The OTHER archive is acquisition-only.
2. snake_case() maps raw NHTSA headers to lowercase underscored fields.
3. Trim text and normalize "nan"/blank-like object values to null.
4. standardize_entity() handles WAYMO/TESLA/NVIDIA/MOBILEYE prefixes; unknown entities title-cased.
5. pd.to_datetime(..., format="%b-%Y", errors="coerce") creates incident_month/submission_month; state/model uppercased.
6. pd.to_numeric(errors="coerce") converts version/year/mileage/speed.
7. SHA-256 hash of normalized staging row provides a change fingerprint.
8. Map normalized company name to company_id using dim_company CSV.
9. severity_category() groups descriptive injury labels.
10. Sort report_id/report_version and drop_duplicates(report_id, keep="last").
11. Retain rows with incident_month <= historical cutoff or missing month; write canonical columns.
12. CSV -> pandas.to_sql append in FK-safe table order -> SQLite constraints/indexes -> SQL views.

**Caveat:** NULL incident months are retained, so “all incident dates are valid” must be evaluated on each actual dataset; the delivered three-row example happened to parse.

## Grains and measures

Distinct reports, not rows in arbitrary joined tables, are the incident-count grain. The three bundled incident rows must not be treated as representative outcomes. Deployment uses metric_name+unit+date+company/program; avoid summing across heterogeneous units. Cost uses cost_scenario_id per three-dimensional Cartesian product. Scalability uses score_id per company/criterion, with one weight row per criterion per lens.

Program-total California testing mileage has NULL company_id by design. Its geography is a program-level total, not a fifth company.

## Where data models are defined

- SQLite DDL: sql/01_create_schema.sql.
- SQL Server-equivalent DDL: sql/07_sqlserver_compatible_schema.sql (not a verified live SQL Server deployment).
- CSV columns and definitions: data/manually_compiled/data_dictionary.csv, data_dictionary.xlsx.
- Power BI semantic model: powerbi/Autonomous_Driving_Benchmark.SemanticModel/definition/.
- Exact active/inactive links: .../definition/relationships.tmdl.
- Relationship design narrative: powerbi/data_model_specification.md.
- ER graphic: outputs/charts/11_entity_relationship_diagram.png.
