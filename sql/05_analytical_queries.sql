
-- Analytical query 1: role-aware executive benchmark.
SELECT
    c.company_name,
    c.ecosystem_role,
    c.automation_exposure,
    ROUND(AVG(fc.evidence_strength_1_5), 2) AS average_public_evidence_strength,
    COUNT(fc.capability_id) AS capability_evidence_rows
FROM dim_company c
LEFT JOIN fact_company_capability fc ON fc.company_id = c.company_id
GROUP BY c.company_id, c.company_name, c.ecosystem_role, c.automation_exposure
ORDER BY average_public_evidence_strength DESC;

-- Analytical query 2: deployment metrics with explicit unit separation.
WITH latest_metric AS (
    SELECT
        d.*,
        ROW_NUMBER() OVER (
            PARTITION BY company_id, metric_name, unit
            ORDER BY date(metric_date) DESC
        ) AS recency_rank
    FROM fact_deployment_mileage d
)
SELECT
    COALESCE(c.company_name, 'California program total') AS company_name,
    l.metric_date,
    l.metric_name,
    l.metric_value,
    l.unit,
    l.period_type,
    l.limitation
FROM latest_metric l
LEFT JOIN dim_company c ON c.company_id = l.company_id
WHERE l.recency_rank = 1
ORDER BY company_name, metric_name;

-- Analytical query 3: lowest modeled cost by scenario and pricing model.
WITH ranked_cost AS (
    SELECT
        scenario_name,
        discount_model,
        cloud_provider,
        instance_type,
        total_cost_usd,
        ROW_NUMBER() OVER (
            PARTITION BY scenario_name, discount_model
            ORDER BY total_cost_usd
        ) AS cost_rank
    FROM fact_training_cost_scenario
)
SELECT
    scenario_name,
    discount_model,
    cloud_provider,
    instance_type,
    ROUND(total_cost_usd, 2) AS total_cost_usd
FROM ranked_cost
WHERE cost_rank = 1
ORDER BY scenario_name, discount_model;

-- Analytical query 4: conditional cost aggregation.
SELECT
    scenario_name,
    cloud_provider,
    ROUND(SUM(CASE WHEN discount_model = 'On-demand' THEN total_cost_usd ELSE 0 END), 2) AS on_demand_total,
    ROUND(SUM(CASE WHEN discount_model = 'Committed scenario' THEN total_cost_usd ELSE 0 END), 2) AS committed_total,
    ROUND(SUM(CASE WHEN discount_model = 'Interruptible scenario' THEN total_cost_usd ELSE 0 END), 2) AS interruptible_total
FROM fact_training_cost_scenario
GROUP BY scenario_name, cloud_provider
ORDER BY scenario_name, on_demand_total;

-- Analytical query 5: scoring profile by criterion.
SELECT
    c.company_name,
    s.criterion_id,
    s.score_1_5,
    s.source_id,
    s.missing_data_treatment
FROM fact_scalability_score s
JOIN dim_company c ON c.company_id = s.company_id
ORDER BY c.company_name, s.criterion_id;

-- Analytical query 6: data-quality failures, if any.
SELECT *
FROM qa_validation_result
WHERE status <> 'PASS'
ORDER BY severity, table_name, check_name;
