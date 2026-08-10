
-- SQLite CLI data-loading script.
-- Run from the project root after 01_create_schema.sql:
-- sqlite3 sql/autonomous_driving.db < sql/01_create_schema.sql
-- sqlite3 sql/autonomous_driving.db < sql/02_load_data.sql

.mode csv
.headers on

.import --skip 1 data/cleaned/dim_company.csv dim_company
.import --skip 1 data/cleaned/dim_date.csv dim_date
.import --skip 1 data/cleaned/dim_geography.csv dim_geography
.import --skip 1 data/cleaned/dim_source.csv dim_source
.import --skip 1 data/cleaned/dim_technology.csv dim_technology
.import --skip 1 data/cleaned/fact_av_incident.csv fact_av_incident
.import --skip 1 data/cleaned/fact_deployment_mileage.csv fact_deployment_mileage
.import --skip 1 data/cleaned/fact_disengagement.csv fact_disengagement
.import --skip 1 data/cleaned/fact_company_capability.csv fact_company_capability
.import --skip 1 data/cleaned/fact_partnership.csv fact_partnership
.import --skip 1 data/cleaned/fact_gpu_pricing.csv fact_gpu_pricing
.import --skip 1 data/cleaned/fact_training_cost_scenario.csv fact_training_cost_scenario
.import --skip 1 data/cleaned/fact_scalability_score.csv fact_scalability_score
.import --skip 1 data/cleaned/bridge_company_technology.csv bridge_company_technology
.import --skip 1 data/data_quality/qa_validation_result.csv qa_validation_result

PRAGMA foreign_key_check;
