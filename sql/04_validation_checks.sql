
-- Data-quality and reconciliation queries.

-- 1. Duplicate incident report IDs after deduplication.
SELECT report_id, COUNT(*) AS record_count
FROM fact_av_incident
GROUP BY report_id
HAVING COUNT(*) > 1;

-- 2. Orphan source keys across fact tables.
WITH used_sources AS (
    SELECT source_id, 'fact_av_incident' AS table_name FROM fact_av_incident
    UNION ALL SELECT source_id, 'fact_deployment_mileage' FROM fact_deployment_mileage
    UNION ALL SELECT source_id, 'fact_company_capability' FROM fact_company_capability
    UNION ALL SELECT source_id, 'fact_partnership' FROM fact_partnership
    UNION ALL SELECT source_id, 'fact_gpu_pricing' FROM fact_gpu_pricing
    UNION ALL SELECT source_id, 'fact_training_cost_scenario' FROM fact_training_cost_scenario
    UNION ALL SELECT source_id, 'fact_scalability_score' FROM fact_scalability_score
)
SELECT u.table_name, u.source_id, COUNT(*) AS rows_affected
FROM used_sources u
LEFT JOIN dim_source s ON s.source_id = u.source_id
WHERE s.source_id IS NULL
GROUP BY u.table_name, u.source_id;

-- 3. Historical cutoff violations.
SELECT source_id, publication_date, title
FROM dim_source
WHERE date(publication_date) > date('2025-06-30') OR cutoff_valid <> 1;

-- 4. Scenario component reconciliation.
SELECT
    cost_scenario_id,
    total_cost_usd,
    training_compute_cost_usd + simulation_compute_cost_usd +
    base_storage_cost_usd + checkpoint_storage_cost_usd + egress_cost_usd AS recomputed_total,
    ABS(total_cost_usd - (
        training_compute_cost_usd + simulation_compute_cost_usd +
        base_storage_cost_usd + checkpoint_storage_cost_usd + egress_cost_usd
    )) AS absolute_difference
FROM fact_training_cost_scenario
WHERE ABS(total_cost_usd - (
    training_compute_cost_usd + simulation_compute_cost_usd +
    base_storage_cost_usd + checkpoint_storage_cost_usd + egress_cost_usd
)) > 0.01;

-- 5. Foreign-key validation.
PRAGMA foreign_key_check;

-- 6. Summary of automated QA results.
SELECT severity, status, COUNT(*) AS checks
FROM qa_validation_result
GROUP BY severity, status
ORDER BY severity, status;
