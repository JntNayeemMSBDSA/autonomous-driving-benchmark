# 01. Project story: business problem to decision-ready analytics

## First explain the problem in simple words

Imagine leadership wants to understand which businesses and technologies can scale autonomous driving. A conventional comparison might rank Tesla, Waymo, NVIDIA, and Mobileye on incidents, vehicles, revenue, GPU capacity or a weighted score. That would be misleading: one company sells cars and supervised driving software, another operates driverless robotaxis in defined areas, another sells compute and development platforms, and another supplies technology to automakers.

The real business question was: **How do we compare autonomous-driving technologies, infrastructure economics and scale in a way that executives can trust, without confusing incompatible metrics or pretending to know private company information?**

The delivered work reframes the problem. Before building charts, it establishes separate company roles, comparable measures, source quality, reporting periods, metric grains and limitations.

## Relationship to original engagement

An earlier Microsoft client-based global internship facilitated through the Russell Palmer Career Management Center at Michigan State University explored autonomous driving, cloud computing, competitive positioning and scalability. The author later independently built and expanded the public analytical system in this repo. The project is not a Microsoft employee project, not a production Microsoft workload, and not a copy of confidential client deliverables.

The reproducible public implementation has: sources and assumptions, source acquisition logic, transformation scripts, a relational analytical database, standalone notebooks, role-aware cost and scalability models, a Power BI report, QA artifacts and executive reports.

## The workflow, in first-person story form

1. **Requirements and comparison contract.** I divided the leadership question into technology, safety evidence, real-world deployment, cloud development costs, partnership models and scalability. I explicitly defined what not to compare: Level 2 and Level 4 incidents without exposure alignment; vehicle deliveries with rider-only miles; customer outcomes with a chip/platform vendor's direct performance. See README.md and methodology.md.

2. **Feasibility and source audit.** I checked which data could actually be sourced through 2025-06-30. Sources included NHTSA Standing General Order reports, California DMV testing data, government and regulatory material, SEC filings, official company information, technical documentation and cloud price references. I created source IDs with date, reliability, claim support, URL and limitations. The delivered source register has 35 entries, of which 33 are tagged primary.

3. **Landing and organization.** Publicly obtainable company and technology facts were registered in data/manually_compiled. The NHTSA fetcher in python/acquire_data.py defines archive URLs, retry/error handling, SHA-256 checksums and acquisition logs. The default local pipeline intentionally does not fetch large external archives. The repository bundles a THREE-ROW official-format ADS excerpt for ingestion tests, not full incident data.

4. **Cleaning and standardization.** python/clean_data.py reads ADS/Level 2 archives when present, otherwise the excerpt; standardizes headings to snake_case, trims text, converts blank markers to null, maps company names, parses month-year dates, normalizes state/model text, casts numeric columns, hashes records, associates company keys, classifies alleged severity, keeps latest report version and filters incident months to the cutoff. It writes a staging CSV and the canonical incident fact.

5. **Model design.** I separated descriptive dimensions (company, date, source, technology, geography) from measurable facts (incidents, deployment, capabilities, partnerships, pricing, scenario costs, scores, disengagement) and a company-technology bridge. The main database is an executed SQLite artifact. Source IDs provide evidence traceability. A SQL Server-compatible DDL is provided as a portability example, but this repo does not prove a SQL Server runtime.

6. **Analytical workstreams.** Incident aggregation is explicitly non-population; deployment outputs retain measurement units. A GPU cost script crosses 3 workload sizes with 6 infrastructure price references and 3 assumed price treatments to create 54 modeled rows. A scalability script combines 4 companies and 12 criteria into 48 score rows, then calculates weighted views for three different decision lenses.

7. **SQL for interpretation and validation.** SQL views supply company capabilities, scenario cost breakdown, latest deployment measures and source traceability. Window functions select the latest metric by company/name/unit; joins resolve company names and source records; NULLIF protects denominator-sensitive shares; CASE aggregates price scenarios; validation queries catch duplicate reports, orphan source keys and cost mismatch.

8. **Power BI and user experience.** The delivered semantic model has 18 tables, 20 single-direction relationships, 53 explicit DAX measures and 64 visuals across five authored pages, of which four are visible. A disconnected weighting selector changes the displayed scalability lens. DAX avoids showing an unqualified deployment total across incompatible units, and warnings explain comparison boundaries. Power BI Desktop QA is documented separately.

9. **Validation.** The dated QA artifact records 20 PASS checks and the Power BI QA note records dashboard validation. The currently runnable python/validate_data.py executes seven grouped checks; they are not identical suites. Code also validates SQLite foreign keys and cost-component sums. A full archive rebuild must be revalidated separately from the included three-row excerpt run.

10. **Executive conclusions.** Waymo's published 56.7 million rider-only-mile matched analysis offers exposure-aligned safety evidence within its specific ODD; Tesla has a broad direct consumer distribution channel but not an equivalent public denominator; NVIDIA has broad train/simulate/deploy platform coverage; Mobileye provides extensive OEM system penetration. The point is different routes to scale, not a universal rank.

## What a nontechnical executive should hear

“We compared four companies that operate at different layers of autonomous driving. We separated verified public evidence from scenario assumptions, used a consistent historical cutoff, and tested what their technical and commercial models imply. The dashboard helps you choose the right comparison rather than combining unrelated metrics. Cloud-cost outputs estimate what a *standardized workload* would cost, not what these companies actually spend. The scalability framework exposes which conclusions change when decision priorities change.”

## Three genuine analytical tensions

**Incompatible safety denominators.** A count of Level 2 reports versus Level 4 reports is not a safety comparison. Solution: keep reporting classes and ODD/exposure context; reference matched safety research where available; suppress invalid rankings.

**Incomplete private infrastructure costs.** Exact training throughput and enterprise contract terms are proprietary. Solution: controlled workload scenarios with explicit utilization, prices, compute/storage/egress breakdown and one-variable sensitivity testing.

**A potentially arbitrary universal ranking.** A supplier and an operator have different scaling needs. Solution: company-role table, twelve transparent criteria, three weight sets and warnings against objective leader claims.

## Concrete scope boundaries

Included: public data collection and governance, reproducible local Python processing, SQLite database, SQL reporting logic, notebooks, cost scenarios, scalability model, Power BI report artifacts and QA.

Not established: confidential training data, 9.6 TB real cloud ingestion, real S3-to-Snowflake transfers, running GPU training jobs on Kubernetes/EKS, 2.2x achieved measured throughput, 28% measured cost-per-epoch decrease, 35% measured latency improvement, or live production operations. Those earlier retrospective items would need their own verified implementation artifacts and should not be merged into this repository narrative.

## Outcome language

Safe: “Produced 54 standardized cost scenarios, 48 role-aware criterion scores, 20 PASS results in the dated QA artifact, a populated relational model, a five-page Power BI report definition with four visible pages, and 64 visuals.”

Unsafe: “Improved Microsoft production throughput by 2.2x using this repository.” It is not supported by this code.
