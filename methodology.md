# Methodology

## 1. Research design

The project uses a role aware comparative case study and analytical benchmarking design. The unit of comparison changes by question:

* Vehicle and mobility operations: Tesla and Waymo
* Consumer ADAS development: Tesla and Mobileye product tiers where applicable
* Compute and software platforms: NVIDIA, Mobileye, Tesla, and Waymo where public evidence exists
* OEM technology supply: NVIDIA and Mobileye
* Standardized cloud cost: provider instances under identical analytical workloads
* Scalability: all four companies under transparent role aware criteria

No metric is combined across companies unless the unit, exposure basis, reporting threshold, and interpretation are reasonably aligned.

## 2. Evidence hierarchy

Reliability classes are:

* A: government source, regulatory filing, official technical documentation, or dated primary research
* B: company primary page, mutable official page, or academic analysis requiring a specific caveat
* C: dated secondary corroboration used only when a historical primary price archive is unavailable

Important quantitative claims require a source ID. Source IDs join facts to `dim_source`.

## 3. Historical cutoff control

The cutoff is June 30, 2025. Each source has a publication date and `cutoff_valid` flag. Each dated fact also has an as of date or metric date. Automated tests fail if a source or fact exceeds the cutoff.

Pages that now show later information are not treated as historical evidence unless the relevant item itself is dated on or before the cutoff.

## 4. Data layers

### Raw

Preserves original field names and source structure. The bundled NHTSA file is a verified schema excerpt only.

### Manually compiled

Contains source controlled facts extracted from filings, government releases, technical documentation, and dated company releases. Every row contains a source ID where appropriate.

### Staging

Applies whitespace trimming, snake case names, date parsing, company name standardization, state standardization, and row hashing.

### Cleaned

Applies latest version deduplication, keys, normalized dates, role fields, units, and category harmonization.

### Reporting

Creates denormalized tables for charts, Power BI, written findings, sensitivity analysis, and scorecards.

### Data quality

Stores validation results, missing value profiles, and record count reconciliation.

## 5. Incident methodology

NHTSA reports are deduplicated by `report_id`. The highest `report_version` is retained. A record hash is generated after standardization.

Incident reports are not converted into cross company safety rates unless a valid exposure denominator is available for the same system, period, geography, and reporting definition.

The delivered excerpt is used to verify ingestion, field mapping, date parsing, state standardization, and deduplication code. It is explicitly excluded from substantive rate estimates.

## 6. Deployment methodology

Deployment indicators retain their original unit and period type. Miles, trips, vehicles, annual systems shipped, and cumulative installed vehicles remain separate.

Lower bound language such as “more than 1,500” is stored as 1,500 with a note that it is a minimum. It is not treated as an exact count.

California DMV mileage is stored as a program level aggregate with a NULL company key.

## 7. Safety methodology

Waymo’s 56.7 million rider only mile research is treated as exposure aligned evidence because it publishes a denominator and matched human benchmarks. It is still company authored and limited to Waymo operating domains.

Tesla vehicle safety reports are not merged with Waymo’s matched analysis because crash definitions, exposure, road mix, driver behavior, and benchmark construction differ.

NVIDIA and Mobileye do not receive fleet crash rates because they are platform and component suppliers whose customers determine vehicles, sensors, software integration, operating domains, and fleet operations.

## 8. Cloud cost methodology

For scenario `s` and price configuration `p`:

```text
instances = ceiling(required GPUs / GPUs per instance)

training compute =
instances x hourly instance price x hours per run x number of runs
divided by utilization
x price factor

simulation compute =
simulation GPU hours x price per GPU hour
divided by utilization
x price factor

storage =
(storage TB + checkpoint TB) x storage months x storage price per TB month

egress =
egress TB x egress price per TB

total =
training compute + simulation compute + storage + egress
```

Storage is standardized at 23 USD per TB month and egress at 90 USD per TB. Ingress is assumed zero. These are scenario inputs, not universal provider prices.

The model deliberately avoids claiming company expenditure.

## 9. Sensitivity analysis

One way sensitivity varies:

* GPU hours
* experiment count
* storage volume
* utilization
* price factor
* data egress price

Each variable changes while other inputs remain at the baseline. The effect is measured as percentage change from baseline total cost.

## 10. Scalability methodology

Scores range from 1 to 5. Criteria are selected to cover data, compute, simulation, vehicle architecture, integration, deployment, regulation, commercial model, and cost.

The weighted score is:

```text
sum(score x weight) / sum(weight)
```

Three weight sets are included. Missing private metrics are not imputed as leading performance. Scores are conservative judgments grounded in public evidence.

The model is not a safety ranking and should not be used as one.

## 11. Evidence strength labels

* Verified: directly supported by a primary source
* Moderately supported: supported at a high level but missing comparable quantitative detail
* Inference: reasoned interpretation from multiple verified facts
* Scenario: output of explicit analytical assumptions
* Unsupported: public information cannot answer the question responsibly

## 12. Reconciliation

The pipeline reconciles:

* raw to staging to cleaned incident rows
* source IDs across facts
* cost totals to cost components
* scalability weights to 100
* foreign keys in SQLite
* record counts by analytical layer
* all dates against the historical cutoff
