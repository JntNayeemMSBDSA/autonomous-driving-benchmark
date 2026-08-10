
-- Portable transformation patterns used by the Python pipeline.
-- This script demonstrates professional deduplication and harmonization logic.

DROP TABLE IF EXISTS staging_incident_ranked;
CREATE TEMP TABLE staging_incident_ranked AS
WITH standardized AS (
    SELECT
        TRIM(report_id) AS report_id,
        CAST(report_version AS INTEGER) AS report_version,
        CASE
            WHEN UPPER(TRIM(reporting_entity_standardized)) LIKE 'WAYMO%' THEN 'Waymo'
            WHEN UPPER(TRIM(reporting_entity_standardized)) LIKE 'TESLA%' THEN 'Tesla'
            ELSE TRIM(reporting_entity_standardized)
        END AS reporting_entity_standardized,
        UPPER(TRIM(state)) AS state,
        UPPER(TRIM(model)) AS model,
        incident_month,
        submission_month,
        source_id,
        record_hash
    FROM fact_av_incident
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY report_id
            ORDER BY report_version DESC, submission_month DESC
        ) AS version_rank
    FROM standardized
)
SELECT * FROM ranked;

-- Latest-version view of incident reports.
DROP VIEW IF EXISTS vw_incident_latest_version;
CREATE VIEW vw_incident_latest_version AS
SELECT i.*
FROM fact_av_incident i
JOIN (
    SELECT report_id, MAX(report_version) AS max_version
    FROM fact_av_incident
    GROUP BY report_id
) latest
  ON i.report_id = latest.report_id
 AND i.report_version = latest.max_version;
