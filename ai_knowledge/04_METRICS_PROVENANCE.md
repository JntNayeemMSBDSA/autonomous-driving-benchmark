# 04. Numeric facts, source provenance, formulas, and limitations

## Rule: distinguish four categories

1. **Verified public-source claim:** company/regulator statement traceable to source_id, period, units and publication date. May be verified as a *statement published* by a company without independently confirming the physical fact.
2. **Delivered dataset metric:** calculated from a file in this repository, not automatically generalizable to a population.
3. **Scenario or judgment:** analytical assumptions, derived model output, ordinal scores.
4. **Unsupported:** not established by repo evidence; do not invent or estimate as fact.

## Actual project scope metrics

| Claim | Value | What it refers to | File |
| --- | ---: | --- | --- |
| Historical company evidence cutoff | 2025-06-30 | Source publication dates and observations, not build date | methodology.md; python/config.py |
| Company roles | 4 | Tesla, Waymo, NVIDIA, Mobileye | data/cleaned/dim_company.csv |
| Registered sources | 35 | Source register entries | data/manually_compiled/source_log.csv |
| Primary sources | 33 | Registered primary class | data/reporting/executive_kpis.csv |
| NHTSA incident excerpt | 3 records | Schema/transform test only; *NOT* crash incident population | data/raw/README.md; data/cleaned/fact_av_incident.csv |
| GPU price configurations | 6 | Two AWS, two Azure, two Google references | data/cleaned/fact_gpu_pricing.csv |
| GPU workload scenarios | 3 | Small, medium, large | data/manually_compiled/gpu_scenarios.csv |
| Discount treatments | 3 | On-demand, committed-assumption, interruptible-assumption | python/gpu_cost_model.py |
| Modeled GPU cost rows | 54 | 3 workload × 6 price × 3 treatments | data/cleaned/fact_training_cost_scenario.csv |
| Scalability criteria | 12 | 1–5 ordinal evidence scoring | data/manually_compiled/scalability_criteria.csv |
| Criterion score rows | 48 | 4 companies × 12 criteria | data/cleaned/fact_scalability_score.csv |
| Weighting schemes | 3 | Baseline, L4 operator, supplier | python/scalability_model.py |
| Weighted result rows | 12 | 4 companies × 3 schemes | data/reporting/scalability_weighted_scores.csv |
| Dated QA artifact | 20 PASS of 20 | July 21, 2026 QA result file | data/data_quality/qa_validation_result.csv |
| Python runtime validator | 7 distinct checks | Different, narrower suite | python/validate_data.py |
| Power BI model | 18 tables, 20 relationships, 53 explicit measures | Verified dashboard QA note dated Aug 10, 2026 | powerbi/Autonomous_Driving_Benchmark_QA.md |
| Power BI authored visuals | 64 | 62 visible-page visuals, 2 hidden-page visuals | powerbi/Autonomous_Driving_Benchmark_QA.md |

## Selected external facts frozen at cutoff

| Measure | Value | Period and meaning | Source |
| --- | --- | --- | --- |
| Waymo exposure-aligned rider-only miles in matched research | 56.7 million | Published 2025, through Jan 2025 research exposure; cannot extrapolate to all geographies | SRC009 |
| Waymo paid trips per week | 250,000 | Minimum reported May 2025; not lifetime trips | SRC010 |
| Waymo operating vehicles | 1,500 | Reported lower bound May 2025; not exact fleet count | SRC010 |
| Tesla deliveries | 1,789,226 | Global deliveries 2024; **not Level 2 miles** | SRC015 |
| Mobileye systems shipped | 29 million | 2024 EyeQ and SuperVision total; **not autonomous vehicles** | SRC023 |
| California 2024 test miles | 4,498,066 | All permit holders, reporting period and program scope only | SRC006 |

Find exact URLs, organizations, titles and publication dates by looking up source_id in data/manually_compiled/source_log.csv or dim_source.csv. Do not transform a lower bound into an exact count.

## Cloud-workload input contract

| Workload | GPUs | Hours/run | Runs | Storage TB | Months | Checkpoint TB | Egress TB | Simulation GPU hours | Utilization |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Small experimentation | 1 | 24 | 5 | 1 | 1 | 0.25 | 0.5 | 100 | 0.70 |
| Medium development | 8 | 168 | 10 | 20 | 3 | 5 | 5 | 10,000 | 0.80 |
| Large AV training | 64 | 720 | 12 | 200 | 6 | 50 | 50 | 100,000 | 0.85 |

Read exact values from data/manually_compiled/gpu_scenarios.csv.

Configurations in data/cleaned/fact_gpu_pricing.csv (historical scenario price snapshot dated 2024-09-20):
- AWS p5.48xlarge H100, 8 GPUs, $98.32 per instance hour, SRC030
- AWS p4d.24xlarge A100 40GB, 8 GPUs, $32.772/hour, SRC028
- Azure Standard_ND96isr_H100_v5 H100, 8 GPUs, $98.32/hour, SRC030
- Azure Standard_NC24ads_A100_v4 A100 80GB, 1 GPU, $3.67/hour, SRC030
- Google Cloud a3-highgpu-8g H100, 8 GPUs, $88.49/hour, SRC026
- Google Cloud a2-ultragpu-1g A100 80GB, 1 GPU, $5.0688/hour, SRC026

Snapshot prices are specific analytical inputs with stated limitations; they are not proof of quotes available at any present date or actual all-in cloud contracts.

Formulas (from python/gpu_cost_model.py):
- instances_required = ceil(required_gpus / gpus_per_instance).
- training = instances × hourly_price × training_hours_per_run × number_of_runs / utilization × factor.
- simulation = simulation_gpu_hours × hourly_price_per_gpu / utilization × factor.
- base storage = storage_tb × storage_months × 23 USD.
- checkpoints = checkpoint_tb × storage_months × 23 USD.
- egress = egress_tb × 90 USD.
- total = sum of five cost components.

Price factor: 1.00 on-demand, 0.70 committed hypothetical, 0.45 interruptible hypothetical. Model omits additional unquantified potential overhead and confidential contracting; cannot be used to infer company spending.

## Scalability output (ordinal, NOT an objective global ranking)

| Company | Baseline | L4 lens | Supplier lens |
| --- | ---: | ---: | ---: |
| Tesla | 3.77 | 3.61 | 3.62 |
| Waymo | 3.51 | 3.65 | 3.68 |
| NVIDIA | 4.21 | 4.35 | 4.38 |
| Mobileye | 4.52 | 4.51 | 4.50 |

Source: data/reporting/scalability_weighted_scores.csv. These outputs reflect selected analyst scores, weights and scoring definitions; counterintuitive rankings are a reason to examine the scoring rubric, NOT an independently corroborated claim that Mobileye is objectively safer or better than Waymo/Tesla/NVIDIA.

Weighted score = SUM(score_1_5 × weight) / SUM(weight), where each scheme's weights total 100. See data/manually_compiled/scalability_criteria.csv and data/cleaned/fact_scalability_score.csv.

## Role-aware research interpretation

Tesla: supervised Level 2 automotive/consumer ADAS distribution, vision-first strategy; no comparable public system-version-specific exposure denominator. Waymo: geofenced Level 4 service, matched company-authored safety research with limited ODD relevance. NVIDIA: training, simulation, in-vehicle and software platform supplier; do not attribute customer incidents to NVIDIA. Mobileye: OEM system, EyeQ, platform and mapping integration; systems shipped and installed base cover many automation tiers.

The five labels used in findings: Verified, Moderately supported, Inference, Scenario, Unsupported. Match each claim to findings_summary.csv and source log rather than trusting labels alone.

## Answer restrictions and common traps

Do not:
- compare raw ADS vs L2 SGO counts as risk rates.
- divide NHTSA report counts by unrelated vehicle deliveries.
- use the three-row excerpt to infer geographic trends or provider outcomes.
- compare California disengagements as an unconditional capability ranking.
- treat software levels and ODDs as equivalent.
- count NVIDIA/Mobileye customer fleets as provider-operated.
- present cloud costs as measured capital or operating expenses.
- state an independent “winner” based only on 1–5 subjective criteria.
- merge claims about real cloud ingestion throughput and latency from another project into this public repo.

## Sources and citations
Use code/data file path plus source_id to substantiate claims. Relevant native source index: data/manually_compiled/source_log.csv. Relevant conceptual risks: documentation/known_limitations.md, data/manually_compiled/limitations.csv, methodology.md. If a value is not listed or cannot be computed from delivered records, respond "not established by this repository" and say what data would be required.
