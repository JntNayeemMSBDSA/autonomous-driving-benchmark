# Instructions for AI assistants working with this repository

Purpose: answer questions about this project accurately, including end-to-end implementation, data engineering, SQL, Python, Power BI, research design, metrics, limitations, and interview explanations. This file is a retrieval policy, not evidence by itself.

## Read in this order
1. ai_knowledge/README.md for the question-to-file index.
2. ai_knowledge/01_PROJECT_STORY.md for business context and an accurate narrative.
3. ai_knowledge/02_PIPELINE_AND_DATA_MODEL.md for data flow, table grains, keys, and relationships.
4. ai_knowledge/03_CODE_AND_DESIGN_DECISIONS.md for actual script/function/SQL mechanics.
5. ai_knowledge/04_METRICS_PROVENANCE.md for quantities, sources, assumptions, and claims.
6. ai_knowledge/05_POWER_BI_AND_OPERATIONS.md for reporting, QA, reproducibility, and conflicts.
7. ai_knowledge/06_INTERVIEW_QA.md for question patterns; verify against implementation before using.
8. The original source files under python/, sql/, data/, powerbi/, notebooks/, methodology.md, and the source register for final verification.

## Evidence precedence
Actual executable code and artifact contents > dated QA artifacts and concrete outputs > methodology and project report > narrative explanatory files > unsupported retrospective recollections. A clean README does not establish that a step ran; distinguish code capability, demonstrated run, and deployment.

When a fact is time-sensitive, note the historical evidence cutoff of 2025-06-30. Later project construction and QA dates are not company-evidence dates. Do not substitute present-day company facts for cutoff-era facts.

Every numeric answer must identify the measure, denominator, unit, period, business meaning, and supporting file/source_id. If no appropriate denominator exists, never derive a rate. Ask for missing source evidence only if the question cannot be answered accurately.

## Mandatory provenance boundary
This is an INDEPENDENT PUBLIC IMPLEMENTATION and substantial extension of an earlier Microsoft client-based global internship project facilitated through MSU's Russell Palmer Career Management Center. The author was NOT employed by Microsoft. The repo is not the exact historical client deliverable, does not establish production access or client deployment, and contains no Microsoft-internal data. Do not describe public scenario outputs as measured Microsoft operational results.

Do not attribute unrelated retrospective claims of 9.6 TB processed, 2.2x throughput, 28% cost/epoch improvement, 35% latency reduction, S3, Snowflake, Kubernetes/EKS, or 3 production flows to this repository without independent primary supporting artifacts. They are not established by the inspected public code and outputs.

## Interpretation rules
- Tesla: supervised Level 2 consumer ADAS; Waymo: geofenced Level 4 operator; NVIDIA: compute/software platform supplier; Mobileye: OEM technology supplier.
- Never put raw NHTSA incident counts into an unqualified four-company safety leaderboard. Bundled incident data are only THREE schema/logic test records, not a population.
- Never add vehicles, systems shipped, miles, rides, deliveries, and fleet size as a unified scale measure.
- Cloud costs are explicit standardized workloads with historical price snapshots and assumed discounts, not company spending or contractual quotes.
- Scalability scores are ordinal analyst judgments with changeable weighting lenses, not objective safety or market rankings.
- The original 20/20 QA artifact and the 7-check runtime validator are distinct. Do not claim the latter runs twenty checks.
- The README and dated Power BI QA show a refreshed PBIX and four-page export; one old limitation entry L014 incorrectly says PBIX cannot be produced.
- The Power BI TMDL contains a machine-specific Excel File.Contents path; changing machine may require updating the source and refreshing.

## Response pattern
For technical questions answer: business issue -> data sources and grain -> precise implementation (file/function/SQL/DAX) -> why it fits -> validation -> output -> limitation. For behavioral questions use supported examples only, and label an illustrative hypothetical if it is not documented as an actual incident. For a challenge or design-tradeoff, state alternative methods and why the chosen one is defensible WITHOUT claiming undocumented benchmarking of the alternatives.

Always name file paths and source IDs where useful. If code, docs and reports disagree, state the conflict and privilege the more concrete, later verified artifact. Never fabricate unseen deployment, RLS, refresh schedules, data sizes, cloud orchestration, production SLAs or team ownership.
