# Power BI Data Model Specification

## Recommended model

Use a star schema with dimensions filtering facts in a single direction.

### Dimensions

* `dim_company`
* `dim_date`
* `dim_geography`
* `dim_source`
* `dim_technology`
* `scalability_criteria`

### Facts and bridges

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

## Relationships

| From | Column | To | Column | Cardinality | Direction |
|---|---|---|---|---|---|
| dim_company | company_id | fact_av_incident | company_id | One to many | Single |
| dim_company | company_id | fact_deployment_mileage | company_id | One to many | Single |
| dim_company | company_id | fact_company_capability | company_id | One to many | Single |
| dim_company | company_id | fact_partnership | company_id | One to many | Single |
| dim_company | company_id | fact_scalability_score | company_id | One to many | Single |
| dim_source | source_id | all source linked facts | source_id | One to many | Single |
| dim_technology | technology_id | bridge_company_technology | technology_id | One to many | Single |
| dim_company | company_id | bridge_company_technology | company_id | One to many | Single |
| fact_gpu_pricing | gpu_price_id | fact_training_cost_scenario | gpu_price_id | One to many | Single |
| scalability_criteria | criterion_id | fact_scalability_score | criterion_id | One to many | Single |
| dim_date | full_date | fact_deployment_mileage | metric_date | One to many | Single |
| dim_date | full_date | fact_av_incident | incident_month | One to many | Single, inactive if month grain conflicts |

Program level California totals have a blank company key. Keep them visible through a separate “Program total” label in the reporting table or use `COALESCE` in Power Query.

## Grain

* `fact_av_incident`: latest NHTSA report version per report ID
* `fact_deployment_mileage`: one sourced metric by company, date, unit, and reporting method
* `fact_company_capability`: one sourced evidence item by company and category
* `fact_gpu_pricing`: one provider, instance, snapshot, and pricing model
* `fact_training_cost_scenario`: one workload, instance, and discount model
* `fact_scalability_score`: one company and criterion
* `fact_partnership`: one announced partnership scope

## Power Query guidance

1. Import from `powerbi_ready_data.xlsx` or the CSV folder.
2. Set IDs to whole number or text exactly as defined in the data dictionary.
3. Set metric, incident, price snapshot, and publication fields to Date.
4. Keep `metric_value` as decimal number because units vary.
5. Do not aggregate `metric_value` across different units.
6. Create a display column for program totals:
   `if [company_id] = null then "California program total" else [company_name]`.
7. Preserve the source ID in all fact tables for tooltip traceability.
8. Disable automatic date tables and use `dim_date`.
9. Hide surrogate keys from report view.
10. Mark `dim_date` as the date table.
11. Keep relationships single direction.
12. Do not create a relationship from incident records to GPU prices or scalability scores.

## Report page 1: Executive Benchmark

### Visuals

* KPI cards: source count, cutoff violations, Waymo rider only miles, latest paid trips, QA pass rate
* Role matrix: company, ecosystem role, automation exposure, business model
* Capability heatmap: company by capability category using evidence strength
* Deployment snapshot: separate visuals by unit
* Strength and limitation narrative cards
* Baseline and alternative weight score chart

### Slicers

Company, ecosystem role, capability category, evidence status, period.

### Warning

Display `Comparability Banner` at the top of the page.

## Report page 2: ADAS Workflow and Technology

### Visuals

* Process flow: collect, select, label, train, simulate, validate, deploy, monitor
* Sensor matrix
* In vehicle compute comparison
* Technology bridge table
* Evidence status and source tooltip
* Company workflow narrative

### Slicers

Company, technology category, relationship type, evidence status.

## Report page 3: Safety, Incidents, and Deployment

### Visuals

* Incident trend by reporting class and month
* Incident categories by state, lighting, roadway, crash counterpart, and severity
* California program mileage by reporting period
* Waymo matched benchmark card and chart
* Deployment metrics by unit
* Source and limitation tooltip

### Warning

Do not place Tesla Level 2 raw incident counts and Waymo ADS incident counts in a shared unqualified bar chart. Use reporting class small multiples and a permanent warning banner.

## Report page 4: GPU Cost and Scalability

### Visuals

* Scenario cost by provider, instance, and discount model
* Cost composition waterfall or stacked bar
* Sensitivity range chart
* Scenario input table
* Criterion score profile
* Alternative weight comparison

### Slicers

Scenario, provider, GPU model, instance, pricing model, company, criterion.

## Tooltip fields

Every evidence visual should expose source ID, source title, publication date, reliability classification, and limitation.
