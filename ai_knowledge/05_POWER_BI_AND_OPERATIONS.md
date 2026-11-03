# 05. Power BI reporting, DAX, QA, reproducibility, and conflicting documentation

## Delivered artifacts (not just mockups)

The repository includes:
- powerbi/Autonomous_Driving_Benchmark.pbix: refreshed saved Desktop report.
- powerbi/Autonomous_Driving_Benchmark.pbip: source-controlled project.
- powerbi/Autonomous_Driving_Benchmark.Report/: PBIR JSON page and visual definitions.
- powerbi/Autonomous_Driving_Benchmark.SemanticModel/: TMDL measures, columns, relationships, Power Query M partitions.
- powerbi/Autonomous_Driving_Benchmark.pdf: four visible page exports.
- powerbi/Executive_Benchmark.png: executive screenshot.
- powerbi/Autonomous_Driving_Benchmark_QA.md: dashboard QA, dated 2026-08-10.
- powerbi/build_powerbi_project.py: generator for PBIP/PBIR/TMDL from workbook.
- powerbi/powerbi_ready_data.xlsx and powerbi/csv/: model-ready data.
- powerbi/data_model_specification.md and powerbi/dax_measures.txt: design companions.

The dated QA documents 18 model tables, 20 declared relationships, 53 explicit DAX measures, 64 visuals; 18 executive, 13 technology, 12 safety/deployment, 19 cost/scalability and 2 on hidden source-detail page.

## The five pages
1. Executive Benchmark (18): roles, source counts and evidence health, comparable deployment summary, capability/scalability context.
2. Technology & Workflow (13): sensors, in-vehicle compute, training/simulation/validation/deployment narrative and underlying evidence.
3. Safety & Deployment (12): exposure-aligned claims and distinct reporting class/period/unit comparisons with warnings.
4. GPU Cost & Scalability (19): standardized scenarios, components, sensitivities, role-aware scores with selectable weights.
5. Evidence & Source Detail (2, hidden): deeper audit/source information; not a fifth visible PDF export page.

## Relationships and filter discipline

The semantic model relationships.tmdl has 20 links. They are single direction; the dim_date -> fact_av_incident month link is explicitly inactive. Company and source dimensions filter relevant facts. Technology uses a company-technology bridge. Cost pricing was deliberately not directly related to the cost scenario fact within Power BI because the paths through dim_source would be ambiguous; scenario rows contain price/provider/instance attributes and retain their own source IDs.

Unlike the database, Power BI's extra reporting tables include fact_safety_indicator, fact_cost_sensitivity, scalability_criteria and disconnected weighting_scheme. The semantic-model table count is NOT the same as SQLite physical table count.

## Real DAX patterns: name the actual measure

Source Count = DISTINCTCOUNT(dim_source[source_id]).
Cutoff Violations = CALCULATE(COUNTROWS(dim_source), dim_source[cutoff_valid] = 0).
Waymo Rider Only Miles = CALCULATE(SUM(fact_deployment_mileage[metric_value]), dim_company[company_name] = "Waymo", fact_deployment_mileage[metric_name] = "Rider-only autonomous miles").
Incident Reports = DISTINCTCOUNT(fact_av_incident[report_id]).
Total Scenario Cost = SUM(fact_training_cost_scenario[total_cost_usd]).
Storage Cost = SUM(base_storage_cost_usd) + SUM(checkpoint_storage_cost_usd).
Compute Cost Share = DIVIDE([Training Compute Cost]+[Simulation Compute Cost],[Total Scenario Cost]).
Baseline Weighted Score = DIVIDE(SUMX(fact_scalability_score, fact_scalability_score[score_1_5] * RELATED(scalability_criteria[baseline_weight])), SUMX(fact_scalability_score, RELATED(scalability_criteria[baseline_weight]))).
Selected Weighting Scheme = SELECTEDVALUE(weighting_scheme[scheme], "Baseline").
Selected Weighted Score = SWITCH([Selected Weighting Scheme], "L4 operator lens", [L4 Operator Weighted Score], "Platform supplier lens", [Platform Supplier Weighted Score], [Baseline Weighted Score]).
QA Pass Rate = DIVIDE([QA Passed], [QA Checks]).
Model Health = IF([Critical QA Failures] = 0 && [Cutoff Violations] = 0 && ABS([Cost Component Reconciliation Delta]) < 0.01, "PASS", "REVIEW").

Source for actual TMDL measure definitions: powerbi/Autonomous_Driving_Benchmark.SemanticModel/definition/tables/dim_company.tmdl. Read all measures there; the companion dax_measures.txt does not contain all 53.

## Safe deployment metric

The measure Deployment Context Is Valid checks HASONEVALUE(metric_name) AND HASONEVALUE(unit). Deployment Display Value returns [Deployment Metric Value] only when context valid; otherwise BLANK(). Deployment Context Warning explains why. This prevents invalid aggregation of miles + vehicles + trips; it does not by itself guarantee all grain-level duplicate observations are filtered. When extracting KPIs, specify period and reporting definition.

## Changeable weights

weighting_scheme.tmdl defines a disconnected table with three text rows. A DAX SWITCH changes which weighted score to use based on user selection. This is not RLS or calculation groups. Underlying Python outputs are also saved for comparison/reconciliation.

## Actual Power Query M caveat

In dim_company.tmdl an import partition uses File.Contents with a local Windows absolute pathname under a developer Desktop folder pointing to powerbi_ready_data.xlsx. This is not portable without editing source parameters or file paths and refreshing. A committed PBIX/QA result does not prove scheduled Power BI Service refresh, gateway setup, published workspace permissions, RLS role definitions or tenant-wide usage monitoring.

## Validation source-of-truth table

| Evidence | Meaning |
| --- | --- |
| data/data_quality/qa_validation_result.csv | 20 dated PASS rows from 2026-07-21; source, incident, costing, weighting, reconciliation tests |
| python/validate_data.py | Seven currently coded runtime checks, writes pipeline_validation.csv/json |
| data/data_quality/pipeline_validation.json | Current committed seven-result sample |
| python/build_database.py | Physical FK check and integrity check as part of DB build |
| sql/04_validation_checks.sql | SQL diagnostic queries for duplication, cutoff, FK, cost components |
| powerbi/Autonomous_Driving_Benchmark_QA.md | 2026-08-10 manual Desktop, semantic model, export and visual QA report |

Do not say the default Python validator dynamically runs all 20 archived checks.

## Documentation conflicts detected

**L014 outdated:** documentation/known_limitations.md states that no tested PBIX can be produced because Desktop is unavailable. This describes an earlier environment/state. Later QA dated Aug 10 and actual committed PBIX, PBIP, PDF and PNG establish that a PBIX was subsequently delivered and tested. Treat L014 as historical, not current.

**DAX companion incomplete:** powerbi/dax_measures.txt only shows a subset. The canonical TMDL contains actual measures and the 53-measure count; prefer TMDL.

**SQLite vs Power BI model:** SQLite has a fact_disengagement table and direct price->cost FK; Power BI has no fabricated separate disengagement fact and omits direct price relationship intentionally. Neither means the other model is incorrect.

**Reproducibility nuance:** default pipeline will regenerate some clean/reporting/SQLite/QA artifacts, but does not automatically regenerate the finished PBIX, PDF, charts, PDFs, reports or historically archived 20-check QA result. Do not claim one Python command rebuilds every artifact from scratch or that the full public archives were bundled.

## Local execution and QA

Requirements: Python >=3.10, packages listed in requirements.txt; local sqlite3 command optional. Power BI Desktop needed to inspect/edit PBIX or PBIP.

Run from repository root:
  python -m pip install -r requirements.txt
  python python/run_pipeline.py

To fetch official historical ADS/ADAS/OTHER archives first:
  python python/acquire_data.py
  python python/run_pipeline.py

These archives can be large, network-dependent and may require a new field mapping if schemas drift. The OTHER archive is not loaded into fact_av_incident.

To rebuild database:
  python python/build_database.py

To inspect analytical queries with local sqlite3 CLI:
  sqlite3 sql/autonomous_driving.db
  .read sql/05_analytical_queries.sql

**Risk to mention in interviews:** full rebuild deletes and recreates the SQLite database; this is appropriate to a reproducible small portfolio batch, not an incremental warehouse. For a production adaptation propose staging isolation, idempotent MERGE/upserts, audit tables, partitioning, secrets/config handling, automated CI, observability and controlled release; describe these as improvements, not implemented features.

## What is not documented as implemented

No proven RLS policies, Power BI Service scheduled refresh, usage telemetry, gateway, data catalog service, S3/Snowflake/EKS operational deployment, 9.6 TB throughput run, model training cluster, or SLA. Use “I would extend the project by ...” for such designs, not “I implemented ...”.
