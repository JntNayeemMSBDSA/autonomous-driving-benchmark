
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS qa_validation_result;
DROP TABLE IF EXISTS bridge_company_technology;
DROP TABLE IF EXISTS fact_scalability_score;
DROP TABLE IF EXISTS fact_training_cost_scenario;
DROP TABLE IF EXISTS fact_gpu_pricing;
DROP TABLE IF EXISTS fact_partnership;
DROP TABLE IF EXISTS fact_company_capability;
DROP TABLE IF EXISTS fact_disengagement;
DROP TABLE IF EXISTS fact_deployment_mileage;
DROP TABLE IF EXISTS fact_av_incident;
DROP TABLE IF EXISTS dim_technology;
DROP TABLE IF EXISTS dim_source;
DROP TABLE IF EXISTS dim_geography;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_company;

CREATE TABLE dim_company (
    company_id INTEGER PRIMARY KEY,
    company_name TEXT NOT NULL UNIQUE,
    ecosystem_role TEXT NOT NULL,
    business_model_classification TEXT NOT NULL,
    automation_exposure TEXT,
    sensor_strategy_summary TEXT,
    in_vehicle_compute_summary TEXT,
    commercial_model TEXT,
    comparability_boundary TEXT,
    geographic_reach_summary TEXT,
    primary_source_id TEXT
);

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date TEXT NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter TEXT NOT NULL,
    month_number INTEGER NOT NULL CHECK (month_number BETWEEN 1 AND 12),
    month_name TEXT NOT NULL,
    year_month TEXT NOT NULL,
    cutoff_valid INTEGER NOT NULL CHECK (cutoff_valid IN (0,1))
);

CREATE TABLE dim_geography (
    geography_id INTEGER PRIMARY KEY,
    geography_name TEXT NOT NULL,
    state_code TEXT,
    country TEXT NOT NULL,
    geography_level TEXT NOT NULL,
    note TEXT
);

CREATE TABLE dim_source (
    source_id TEXT PRIMARY KEY,
    organization TEXT NOT NULL,
    title TEXT NOT NULL,
    source_type TEXT NOT NULL,
    publication_date TEXT NOT NULL,
    historical_period_covered TEXT,
    access_date TEXT NOT NULL,
    source_url TEXT NOT NULL,
    variables_or_claims_supported TEXT,
    reliability_classification TEXT NOT NULL,
    relevant_limitations TEXT,
    source_class TEXT NOT NULL,
    cutoff_valid INTEGER NOT NULL CHECK (cutoff_valid IN (0,1)),
    is_primary INTEGER NOT NULL CHECK (is_primary IN (0,1))
);

CREATE TABLE dim_technology (
    technology_id INTEGER PRIMARY KEY,
    technology_name TEXT NOT NULL UNIQUE,
    technology_category TEXT NOT NULL,
    description TEXT NOT NULL,
    input_or_unit TEXT,
    comparability_warning TEXT
);

CREATE TABLE fact_av_incident (
    report_id TEXT PRIMARY KEY,
    report_version INTEGER NOT NULL,
    company_id INTEGER,
    reporting_entity_standardized TEXT NOT NULL,
    report_type TEXT,
    incident_month TEXT,
    submission_month TEXT,
    city TEXT,
    state TEXT,
    make TEXT,
    model TEXT,
    model_year INTEGER,
    mileage REAL,
    roadway_type TEXT,
    roadway_surface TEXT,
    lighting TEXT,
    crash_with TEXT,
    highest_injury_severity_alleged TEXT,
    severity_category TEXT,
    property_damage TEXT,
    sv_pre_crash_movement TEXT,
    sv_precrash_speed_mph REAL,
    within_odd TEXT,
    source_id TEXT NOT NULL,
    record_hash TEXT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES dim_company(company_id),
    FOREIGN KEY (source_id) REFERENCES dim_source(source_id)
);

CREATE TABLE fact_deployment_mileage (
    deployment_metric_id INTEGER PRIMARY KEY,
    company_id INTEGER,
    metric_date TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    unit TEXT NOT NULL,
    metric_value REAL NOT NULL CHECK (metric_value >= 0),
    period_type TEXT,
    geography TEXT,
    reporting_method TEXT,
    source_id TEXT NOT NULL,
    historical_cutoff_valid INTEGER NOT NULL CHECK (historical_cutoff_valid IN (0,1)),
    limitation TEXT,
    FOREIGN KEY (company_id) REFERENCES dim_company(company_id),
    FOREIGN KEY (source_id) REFERENCES dim_source(source_id)
);

CREATE TABLE fact_disengagement (
    disengagement_id INTEGER PRIMARY KEY,
    company_id INTEGER,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    total_autonomous_miles REAL,
    safety_driver_miles REAL,
    driverless_miles REAL,
    disengagement_count REAL,
    geography TEXT,
    source_id TEXT NOT NULL,
    limitation TEXT,
    FOREIGN KEY (company_id) REFERENCES dim_company(company_id),
    FOREIGN KEY (source_id) REFERENCES dim_source(source_id)
);

CREATE TABLE fact_company_capability (
    capability_id INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL,
    capability_category TEXT NOT NULL,
    evidence_summary TEXT NOT NULL,
    evidence_status TEXT NOT NULL,
    source_id TEXT NOT NULL,
    evidence_strength_1_5 INTEGER NOT NULL CHECK (evidence_strength_1_5 BETWEEN 1 AND 5),
    limitation TEXT,
    FOREIGN KEY (company_id) REFERENCES dim_company(company_id),
    FOREIGN KEY (source_id) REFERENCES dim_source(source_id)
);

CREATE TABLE fact_partnership (
    partnership_id INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL,
    partner_name TEXT NOT NULL,
    partnership_type TEXT,
    geography TEXT,
    announcement_date TEXT,
    end_date TEXT,
    scope TEXT,
    source_id TEXT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES dim_company(company_id),
    FOREIGN KEY (source_id) REFERENCES dim_source(source_id)
);

CREATE TABLE fact_gpu_pricing (
    gpu_price_id INTEGER PRIMARY KEY,
    cloud_provider TEXT NOT NULL,
    instance_family TEXT,
    gpu_model TEXT NOT NULL,
    instance_type TEXT NOT NULL,
    gpus_per_instance INTEGER NOT NULL CHECK (gpus_per_instance > 0),
    hourly_price_usd REAL NOT NULL CHECK (hourly_price_usd > 0),
    price_per_gpu_hour_usd REAL NOT NULL CHECK (price_per_gpu_hour_usd > 0),
    region_reference TEXT,
    pricing_model TEXT,
    price_snapshot_date TEXT NOT NULL,
    price_unit TEXT NOT NULL,
    source_id TEXT NOT NULL,
    limitation TEXT,
    FOREIGN KEY (source_id) REFERENCES dim_source(source_id)
);

CREATE TABLE fact_training_cost_scenario (
    cost_scenario_id INTEGER PRIMARY KEY,
    scenario_id INTEGER NOT NULL,
    scenario_name TEXT NOT NULL,
    gpu_price_id INTEGER NOT NULL,
    cloud_provider TEXT NOT NULL,
    instance_type TEXT NOT NULL,
    gpu_model TEXT NOT NULL,
    required_gpus INTEGER NOT NULL,
    instances_required INTEGER NOT NULL,
    provisioned_gpus INTEGER NOT NULL,
    training_hours_per_run REAL NOT NULL,
    number_of_runs INTEGER NOT NULL,
    utilization_rate REAL NOT NULL CHECK (utilization_rate > 0 AND utilization_rate <= 1),
    discount_model TEXT NOT NULL,
    price_factor REAL NOT NULL,
    training_compute_cost_usd REAL NOT NULL,
    simulation_compute_cost_usd REAL NOT NULL,
    base_storage_cost_usd REAL NOT NULL,
    checkpoint_storage_cost_usd REAL NOT NULL,
    egress_cost_usd REAL NOT NULL,
    total_cost_usd REAL NOT NULL,
    source_id TEXT NOT NULL,
    interpretation_note TEXT,
    FOREIGN KEY (gpu_price_id) REFERENCES fact_gpu_pricing(gpu_price_id),
    FOREIGN KEY (source_id) REFERENCES dim_source(source_id)
);

CREATE TABLE fact_scalability_score (
    score_id INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL,
    criterion_id INTEGER NOT NULL,
    score_1_5 INTEGER NOT NULL CHECK (score_1_5 BETWEEN 1 AND 5),
    source_id TEXT NOT NULL,
    evidence_note TEXT,
    missing_data_treatment TEXT,
    FOREIGN KEY (company_id) REFERENCES dim_company(company_id),
    FOREIGN KEY (source_id) REFERENCES dim_source(source_id)
);

CREATE TABLE bridge_company_technology (
    company_id INTEGER NOT NULL,
    technology_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL,
    PRIMARY KEY (company_id, technology_id),
    FOREIGN KEY (company_id) REFERENCES dim_company(company_id),
    FOREIGN KEY (technology_id) REFERENCES dim_technology(technology_id)
);

CREATE TABLE qa_validation_result (
    validation_id INTEGER PRIMARY KEY,
    check_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PASS','FAIL')),
    expected TEXT,
    actual TEXT,
    details TEXT,
    run_date TEXT NOT NULL
);

CREATE INDEX idx_incident_company_month ON fact_av_incident(company_id, incident_month);
CREATE INDEX idx_deployment_company_date ON fact_deployment_mileage(company_id, metric_date);
CREATE INDEX idx_capability_company_category ON fact_company_capability(company_id, capability_category);
CREATE INDEX idx_cost_scenario_provider ON fact_training_cost_scenario(scenario_name, cloud_provider, discount_model);
CREATE INDEX idx_score_company_criterion ON fact_scalability_score(company_id, criterion_id);
