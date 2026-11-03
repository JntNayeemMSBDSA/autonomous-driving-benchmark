# Autonomous Driving Benchmark: AI Knowledge Base

This directory is a structured retrieval layer over the existing complete public repository. It does not replace the actual scripts, data, database, reports, notebook outputs or semantic model.

**Project:** Autonomous Driving Technology, Cloud Computing & Scalability Benchmark
**Repository:** https://github.com/JntNayeemMSBDSA/autonomous-driving-benchmark
**Historical company-evidence cutoff:** 2025-06-30
**Implementation:** independent public analytics implementation extending an earlier Microsoft client-based global internship investigation
**Company set:** Tesla, Waymo, NVIDIA, Mobileye
**Primary tasks:** role-aware competitive benchmarking, evidence governance, incident/deployment analysis, GPU cost scenario modeling, scalability scoring, database design, Power BI reporting, QA
**Read AGENTS.md before synthesizing any answer.**

## Where to look

| User question | First read | Cross-check |
| --- | --- | --- |
| Tell the project story, business problem, end-to-end ownership | 01_PROJECT_STORY.md | README.md; methodology.md |
| Sources, raw/staging/clean/reporting layers | 02_PIPELINE_AND_DATA_MODEL.md | python/clean_data.py; documentation/transformation_log.md |
| ERD, schema, keys, foreign keys, fact/dim counts | 02_PIPELINE_AND_DATA_MODEL.md | sql/01_create_schema.sql; data/manually_compiled/data_dictionary.csv |
| Functions, algorithms, transformations, Python/SQL code | 03_CODE_AND_DESIGN_DECISIONS.md | python/; sql/ |
| KPI, results, sources, numeric evidence, scenario meaning | 04_METRICS_PROVENANCE.md | data/reporting/; data/manually_compiled/source_log.csv |
| Power Query, DAX, relationship design, dashboards | 05_POWER_BI_AND_OPERATIONS.md | powerbi/Autonomous_Driving_Benchmark.SemanticModel; powerbi/Autonomous_Driving_Benchmark_QA.md |
| QA, what actually ran, reproducibility, caveats | 05_POWER_BI_AND_OPERATIONS.md | python/validate_data.py; data/data_quality/ |
| Interview challenges, situational questions, trade-offs | 06_INTERVIEW_QA.md | each primary implementation file |
| Machine-readable facts and confidence | project_context.json | all source paths |
| Data limitations | 04_METRICS_PROVENANCE.md | documentation/known_limitations.md |

## Technical topology

    Official/public documentation, regulatory reports, SEC and company filings
                         |
              source_log / assumptions / input datasets
                         |
          raw excerpts or downloaded official archives
                         |
            clean_data.py -> staging -> incident facts
                         |
          canonical dimensions and manually compiled facts
                         |
       +-----------------+-------------------+
       |                 |                   |
    Python analyses   SQLite DB          reporting CSV
       |                 |                   |
    scenarios/scores  SQL views        Power BI import
       |                 |                   |
       +-----------------+---------+---------+
                                 |
                     Power BI / notebooks / QA / reports

Default orchestration is python/run_pipeline.py, which uses bundled evidence and skip-downloads. The archive acquisition is a separate explicit command.

## Existing primary assets
- README.md and methodology.md: intended project scope.
- python/: 11 separate Python scripts including orchestration, cleaning, analysis, modeling, DB load and QA.
- sql/: SQLite DDL, SQL loading and analytical queries, views, validation and SQL Server-compatible schema.
- data/: raw, manually_compiled, staging, cleaned, reporting, data_quality.
- notebooks/: four executed analyses.
- powerbi/: delivered PBIX, PBIP, PBIR/TMDL, ready-data workbook, DAX measures, PDF, PNG, quality notes.
- outputs/ and project_report.pdf: analysis and communication.
- source_log.xlsx and data/manually_compiled/source_log.csv: source IDs and citations.

## Core logic
The project prevents false comparison between a consumer ADAS provider, a robotaxi operator, a compute platform and an OEM technology supplier. It delivers a defensible comparison *within the appropriate unit of analysis*, not one universal winner.

## File freshness
These AI-specific docs were prepared from the repo state at commit 92ca645fe5741c10b3656fe52930369f264ee8f8 (main branch inspected 2026-11-03). When code changes, verify and update this documentation.
