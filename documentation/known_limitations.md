# Known Limitations

## L001: Exposure denominator

**Limitation:** Tesla public system-level miles by software version and ODD are unavailable

**Effect:** Prevents incident-rate normalization

**Treatment:** Do not divide Tesla SGO counts by total vehicle deliveries

## L002: Supplier attribution

**Limitation:** NVIDIA and Mobileye do not operate one homogeneous public fleet

**Effect:** Prevents direct crash-rate comparison

**Treatment:** Evaluate platform capability and integration instead

## L003: Reporting threshold

**Limitation:** NHTSA ADS and Level 2 ADAS reporting criteria differ

**Effect:** Raw incident totals are not comparable

**Treatment:** Analyze within reporting class and label threshold

## L004: Report revisions

**Limitation:** SGO reports can be updated, corrected, or duplicate earlier versions

**Effect:** Naive record counts overstate incidents

**Treatment:** Deduplicate by report ID and retain latest version

## L005: Geography and ODD

**Limitation:** Waymo operates in defined service areas while Tesla consumer exposure is geographically broader

**Effect:** Safety outcomes reflect different environments

**Treatment:** Use matched benchmarks only where supplied

## L006: California scope

**Limitation:** DMV disengagement data omit private roads, out-of-state testing, below L3, and simulation

**Effect:** Understates total development activity

**Treatment:** Use only as a California testing indicator

## L007: Disengagement definition

**Limitation:** Intervention practices and testing goals vary by company and period

**Effect:** Disengagement rates are not capability rankings

**Treatment:** Use trends within the same entity cautiously

## L008: Mutable web pages

**Limitation:** Some technical and price pages change after the cutoff

**Effect:** Risk of present-day contamination

**Treatment:** Retain publication/snapshot dates and use filings/releases

## L009: Cloud discounts

**Limitation:** Enterprise contracts and reserved capacity are confidential

**Effect:** Scenario cost may differ materially from actual spend

**Treatment:** Show on-demand and standardized discount sensitivities

## L010: Training workload

**Limitation:** Exact parameter counts, tokens/frames, epochs, and cluster utilization are confidential

**Effect:** Cannot estimate company expenditure responsibly

**Treatment:** Use standardized workloads only

## L011: TOPS comparability

**Limitation:** TOPS/TFLOPS vary by numeric precision and architecture

**Effect:** Compute specifications can mislead

**Treatment:** Avoid ranking platforms solely by TOPS

## L012: Fleet size definitions

**Limitation:** Vehicles, deployed vehicles, systems shipped, and installed base are different concepts

**Effect:** Cross-company scale metrics are not interchangeable

**Treatment:** Preserve metric name and unit; no combined total

## L013: Source transfer

**Limitation:** Large official NHTSA archive could not be redistributed in this runtime

**Effect:** Full incident-level execution is not embedded

**Treatment:** Include official URL, acquisition script, schema excerpt, and validation logic

## L014: Power BI runtime

**Limitation:** Power BI Desktop is unavailable in the execution environment

**Effect:** A tested PBIX cannot be produced

**Treatment:** Deliver star-schema workbook, DAX, layouts, guide, and mockups
