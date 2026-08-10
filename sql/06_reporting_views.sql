
DROP VIEW IF EXISTS vw_company_capability_scorecard;
CREATE VIEW vw_company_capability_scorecard AS
SELECT
    c.company_id,
    c.company_name,
    c.ecosystem_role,
    fc.capability_category,
    fc.evidence_summary,
    fc.evidence_status,
    fc.evidence_strength_1_5,
    fc.source_id,
    fc.limitation
FROM dim_company c
JOIN fact_company_capability fc ON fc.company_id = c.company_id;

DROP VIEW IF EXISTS vw_gpu_cost_composition;
CREATE VIEW vw_gpu_cost_composition AS
SELECT
    scenario_name,
    cloud_provider,
    instance_type,
    gpu_model,
    discount_model,
    training_compute_cost_usd,
    simulation_compute_cost_usd,
    base_storage_cost_usd,
    checkpoint_storage_cost_usd,
    egress_cost_usd,
    total_cost_usd,
    ROUND(training_compute_cost_usd / NULLIF(total_cost_usd, 0), 4) AS training_share,
    ROUND(simulation_compute_cost_usd / NULLIF(total_cost_usd, 0), 4) AS simulation_share
FROM fact_training_cost_scenario;

DROP VIEW IF EXISTS vw_latest_deployment_metric;
CREATE VIEW vw_latest_deployment_metric AS
WITH ranked AS (
    SELECT
        d.*,
        ROW_NUMBER() OVER (
            PARTITION BY company_id, metric_name, unit
            ORDER BY date(metric_date) DESC
        ) AS rn
    FROM fact_deployment_mileage d
)
SELECT
    r.*,
    c.company_name,
    c.ecosystem_role
FROM ranked r
LEFT JOIN dim_company c ON c.company_id = r.company_id
WHERE r.rn = 1;

DROP VIEW IF EXISTS vw_source_traceability;
CREATE VIEW vw_source_traceability AS
SELECT
    fc.capability_id AS record_id,
    'fact_company_capability' AS fact_table,
    c.company_name,
    fc.capability_category AS metric_or_category,
    fc.source_id,
    s.organization,
    s.title,
    s.publication_date,
    s.source_url,
    s.reliability_classification
FROM fact_company_capability fc
JOIN dim_company c ON c.company_id = fc.company_id
JOIN dim_source s ON s.source_id = fc.source_id;
