# 06. Interview question bank, supported responses and follow-up drilling

These are concise answer skeletons for an interview, not memorized scripts. For each question, give WHAT problem, HOW technically, WHY this design, validation and a limitation. Speak in first person about the independently delivered public implementation, without turning an earlier Microsoft client-based internship into Microsoft employment or confidential production work.

## Business and architecture

### 1. Walk me through the full project.
The question was how to benchmark four autonomous-driving businesses with very different business models. I separated comparisons by role and metric unit, registered 35 dated evidence sources, built raw/staging/clean/reporting layers with Python and a normalized SQLite analytical database, modeled 54 GPU costs and a 12-criterion scalability framework, then delivered a verified Power BI semantic model and four-page visible report. The main result was a transparent decision aid that preserves safety and deployment comparability, not a single winner. Proof: README.md, python/run_pipeline.py, sql/01_create_schema.sql.

### 2. How did you gather requirements?
I converted a broad company comparison into measurable questions about ecosystem role, technology, safety, deployment, cloud costs and scalability. Each metric needed an entity, unit, period, source ID and comparability rule; anything without an appropriate denominator would not be promoted to a rate. That rule materially changed the report design. Proof: methodology.md; powerbi/data_model_specification.md.

### 3. What was the biggest data feasibility challenge?
Different sources use incompatible reporting classes and denominators. Tesla consumer deliveries do not measure Level 2 safety exposure; Waymo matched research measures rider-only miles within defined ODDs; NVIDIA/Mobileye primarily sell platforms to customers. I kept those measures separate instead of manufacturing a shared rate. Proof: documentation/known_limitations.md; methodology.md.

### 4. Give the end-to-end ingestion/transformation path.
python/acquire_data.py defines official NHTSA archives, retry/download/checksum/logging; clean_data.py uses bundled test records by default, normalizes fields/companies/dates, fingerprints and deduplicates versions, applies cutoff and exports canonical facts. Python scripts create scenario/reporting tables; build_database.py loads them into SQLite and builds views; validate_data.py runs seven runtime checks. Proof: scripts in python/.

### 5. Why choose batch Python plus SQLite, not Snowflake or Spark?
The delivered reproducible public workload is small and requires auditable local execution. Pandas and SQLite minimize infrastructure needs, make transformations inspectable and support relational constraints. They are not evidence of performance benchmarking against Spark/Snowflake; a larger archive or production target could justify a warehouse, chunked loading and incremental merges. Proof: python/build_database.py and requirements.txt.

### 6. Explain the ER diagram and why not one flat table.
I kept company/source/technology/date/geography descriptions separate from distinct incident, deployment, cost and scored evidence grains. A single table would duplicate source/company fields, multiply rows across multiple fact types and create misleading aggregates. I used PK/FK relationships and a bridge for many-to-many company-technology. Proof: sql/01_create_schema.sql; ai_knowledge/02_PIPELINE_AND_DATA_MODEL.md.

### 7. How many facts and dimensions did you create?
SQLite defines five dimensions, eight analytical/fact tables, one company-technology bridge and one QA results table, 15 physical tables in total. Power BI has a separate 18-table semantic model. Do not conflate counts. Proof: sql/01_create_schema.sql and relationships.tmdl.

### 8. How did you handle nulls and duplicate incidents?
Strip/normalize string fields, map blanks to missing, coerce dates/numbers and standardize company names. Incident dedup uses report_id and highest report_version; SHA-256 is an audit fingerprint, not the business key. The delivered excerpt had three nonduplicate records. Proof: python/clean_data.py; documentation/transformation_log.md.

### 9. Why a source dimension?
Every material public claim must be traced to a URL, publication date, reliability classification, source ID and stated limitation. That supports historical cutoff checks and source-level tooltips, and prevents unknowingly blending post-cutoff updates with June 2025 facts. Proof: dim_source.csv; source_log.csv.

### 10. What SQL functions did you use and why?
ROW_NUMBER with PARTITION BY company/metric/unit isolates the latest observation per metric; CTEs keep ranking steps readable; LEFT JOIN retains NULL company program aggregates; CASE conditionally separates discount treatments; NULLIF prevents division by zero; CHECK/FK/PRAGMA validate constraints. Proof: sql/05_analytical_queries.sql; sql/06_reporting_views.sql; sql/01_create_schema.sql.

## Quantitative, Power BI and design questions

### 11. Explain your GPU cost formula in plain words.
I choose whole GPU instances based on requested GPU count, multiply the instance price by training time and experiment count, adjust for utilization and an assumed pricing treatment, then add simulation, storage, checkpoints and transfer. Three workloads, six configurations and three treatments create 54 what-if rows. I explicitly avoid calling this actual Tesla, Waymo or Microsoft spend. Proof: python/gpu_cost_model.py.

### 12. What drives cost most?
Within the modeled assumptions, GPU count/hours, number of runs, utilization and price factor affect compute strongly; storage and egress rise with TB retained/transferred. The sensitivity notebooks and reporting CSVs quantify changes; do not present the conclusion as a measured production cloud optimization. Proof: data/reporting/gpu_cost_sensitivity.csv; notebooks/03_gpu_cost_scenarios.ipynb.

### 13. How did you keep weighted scoring fair?
I defined 12 public-evidence criteria, exposed three weight sets for different operational priorities, and computed the 1–5 weighted score per company. The score is an analyst decision aid, not an objective technology or safety ranking. It's valid only within its stated rubric. Proof: python/scalability_model.py; scalability_criteria.csv.

### 14. Why is Mobileye top in the saved baseline score?
It receives the largest weighted score within this particular set of subjective criteria and weights (4.52). That does not mean Mobileye is objectively the safest or most advanced; I would drill into each score/weight and test how the result changes when decision priorities change. Proof: scalability_weighted_scores.csv; fact_scalability_score.csv.

### 15. Explain the Power BI data model.
The delivered model has 18 tables and 20 single-direction relationships, with one inactive incident-month link. Company, date, source and technology dimensions filter their relevant facts. I avoided a direct GPU-pricing-to-cost relationship in Power BI because a separate source path would make filtering ambiguous. Proof: relationships.tmdl; Power BI QA note.

### 16. Which DAX expressions mattered most?
DISTINCTCOUNT for unique sources/incidents, CALCULATE for company/metric filter context, DIVIDE for safe shares, SUMX and RELATED for criteria weights, SELECTEDVALUE and SWITCH for dynamic weighting, IF/HASONEVALUE to blank out mixed-unit aggregates, and a Model Health expression for QA guardrails. Proof: dim_company.tmdl.

### 17. What was your Power BI dashboard layout?
Executive Benchmark, Technology & Workflow, Safety & Deployment and GPU Cost & Scalability are visible; a source-detail page is hidden. The 64 authored visuals include 18+13+12+19 on visible pages and two on hidden page. Report export has four pages. Proof: powerbi/Autonomous_Driving_Benchmark_QA.md.

### 18. Did you use RLS or scheduled refresh?
Not established by the repository. The report is a Desktop PBIX/PBIP with a local Excel File.Contents path. I can explain how I'd add row-level security and service refresh, but I would not claim they are already implemented here. Proof: TMDL partitions and project files.

## Situational questions grounded in real design choices

### 19. Tell me about a time the data did not support what stakeholders wanted.
The central research design encountered a tempting but invalid universal safety comparison. I tested the meaning of each denominator, deployment unit and reporting class, and redesigned reporting around role-specific measures and warnings. The outcome was an analysis that made uncertainty visible rather than publishing an unsupported winner. This is a documented project-level analytic challenge, not a confirmed dialogue with a particular stakeholder.

### 20. Describe a data quality problem and how you solved it.
NHTSA incident reports can include revised report versions; raw counts would overstate incidents. I based the canonical grain on report_id, kept the last version with sorting/dedup, retained a record hash and created validations for uniqueness and source integrity. The included three-row excerpt had no duplicates, so I don't claim that these exact three rows demonstrated duplicate removal. Proof: python/clean_data.py; qa_validation_result.csv.

### 21. Describe a design tradeoff.
A universal cross-company KPI would be easy to visualize but misleading. I chose a role-aware data contract and dashboard, even though the result was less like a simple leaderboard. That prevented mixing Tesla vehicle deliveries with Waymo rider-only miles and Mobileye systems shipped. Proof: methodology.md; DAX Deployment Context Is Valid.

### 22. Describe a time you found an inconsistent result.
The cloud model requires total cost to equal compute, simulation, storage, checkpoint and egress components. I added a $0.01 reconciliation tolerance in validation to catch future errors. The committed runtime validation reports a difference near floating-point zero. Do not invent a production outage or a particular detected fault. Proof: python/validate_data.py.

### 23. What if the CEO asks “Which company wins?”
I'd first ask which decision they mean: driverless operations, consumer reach, platform supply or cloud economics. I would show the best comparable evidence and its limits, then demonstrate that weighted scores depend on selected criteria. The right answer is an explicit recommendation conditional on the decision, not a universal technology winner.

### 24. What if the source data changes tomorrow?
The historical report stays frozen at 2025-06-30. For a new edition I'd version the evidence cutoff, rerun acquisition with recorded URLs/checksums, audit schema/date changes, regenerate outputs and verify all QA before publishing. That's a proposed extension; the existing project is an as-of benchmark, not a live feed.

### 25. How would you productionize it?
I'd move ingestion to a scheduler with retries/checkpoints, use schema contracts, immutable raw storage and incremental dedup in a database/warehouse, record run IDs/lineage, add integration tests, use environment-specific Power BI parameters and set up controlled refresh/governance. Those are next steps, not work proved by this repo.

## Quick technical drill

**Why ROW_NUMBER?** It selects one record per business-key partition after sorting, while retaining other attributes for subsequent joins.

**Why LEFT JOIN?** It keeps all deployment metrics, including program totals with NULL company_id; an INNER JOIN would silently remove them.

**Why NULLIF?** It makes a zero cost denominator NULL, preventing divide-by-zero errors in SQL shares.

**Why DIVIDE in DAX?** It handles zero or blank denominators more safely than a bare slash.

**Why SHA-256?** Record-change fingerprint and auditability; not a replacement for report_id or a cryptographic claim about upstream authenticity.

**Why many-to-many bridge?** One technology can relate to several companies and one company can relate to multiple technologies without repeated comma-separated values.

**What is fact grain?** The unit represented by one fact row: report, deployment observation, GPU scenario/config/treatment, company/criterion score etc.

**What is the biggest limitation?** Lack of common safety exposure measures and confidential internal training costs. Honest limits are part of the product.

**What if asked about Snowflake/EKS and 2.2x throughput?** That is not established in this repository. Separate the earlier internship or other work from this independent public benchmark and provide only artifacts actually verified for the other effort.

## How to make any AI answer a new question

Find the relevant section in ai_knowledge/README.md, inspect original source file and exact function/SQL/DAX, retrieve source_id and underlying record if quantitative, explain the business-to-technical chain, and end with concrete outputs and boundaries. If implementation differs from prose, use the concrete implementation and flag the discrepancy.
