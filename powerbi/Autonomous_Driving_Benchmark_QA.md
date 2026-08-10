# Autonomous Driving Benchmark - Power BI QA Summary

Date: 2026-08-10
Status: PASS

## Deliverables verified

- `Autonomous_Driving_Benchmark.pbip` opens successfully in Power BI Desktop.
- `Autonomous_Driving_Benchmark.pbix` was refreshed and saved from Power BI Desktop.
- `Executive_Benchmark.png` is a 1280 x 720 export of the Executive Benchmark canvas.
- `Autonomous_Driving_Benchmark.pdf` contains four visible report pages at 1280 x 720 points per page.
- `build_powerbi_project.py` reproducibly generates the PBIP semantic model and PBIR report definition from `powerbi_ready_data.xlsx`.

## Semantic model

- 18 model tables.
- 20 single-direction relationships.
- 53 explicit DAX measures organized into display folders.
- 4 canonical companies: Mobileye, NVIDIA, Tesla, and Waymo.
- 35 sources, including 33 primary sources.
- Historical evidence cutoff enforced at 2025-06-30.
- The candidate direct GPU-price-to-cost-scenario relationship was intentionally omitted because it created an ambiguous path to `dim_source`; scenario rows retain provider, instance, and GPU attributes directly.
- No disengagement fact was invented because no separate disengagement fact table was delivered.

## Report definition

| Page | Visibility | Visuals | Result |
|---|---:|---:|---:|
| Executive Benchmark | Visible | 18 | PASS |
| Technology & Workflow | Visible | 13 | PASS |
| Safety & Deployment | Visible | 12 | PASS |
| GPU Cost & Scalability | Visible | 19 | PASS |
| Evidence & Source Detail | Hidden in view mode | 2 | PASS |

All 64 visuals opened in Power BI Desktop without missing-custom-visual placeholders. KPI cards, native charts, slicers, matrices, tables, warnings, titles, and page navigation were visually checked at normal zoom.

## Data QA

The supplied validation suite reports 20 of 20 checks as PASS:

- Source cutoff, uniqueness, URL completeness, and referential integrity.
- Company key uniqueness and canonical-name standardization.
- Incident duplicate, date, cutoff, state, mileage, and record-count checks.
- Deployment nonnegative and cutoff checks.
- GPU price positivity and scenario-utilization range checks.
- Training-cost reconciliation to component totals.
- Scalability weighting totals, 1-to-5 score bounds, and referential integrity.

Dashboard checks also confirmed:

- QA pass rate: 100.0%.
- Model health: PASS.
- Waymo rider-only miles: 56.7 million.
- Waymo paid trips per week: 250,000.
- Raw incident rows remain an evidence extract and are not presented as population safety rates.
- Cost outputs remain standardized analytical scenarios and are not described as company expenditures.
- Scalability scores remain explicitly ordinal and weighting-lens dependent.

## Export QA

- PDF: four pages, 1280 x 720 points, rendered back to PNG with Poppler and visually inspected.
- Executive PNG: 1280 x 720, legible title, labels, KPI values, tables, and warnings.
- No remaining manual completion step is required.
