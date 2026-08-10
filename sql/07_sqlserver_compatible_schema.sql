/*
Complete SQL Server-compatible analytical schema.
The executed source of truth is the portable SQLite database. This script
mirrors the delivered tables, keys, checks, and indexes for SQL Server 2019+.
*/

IF OBJECT_ID('dbo.qa_validation_result', 'U') IS NOT NULL DROP TABLE dbo.qa_validation_result;
IF OBJECT_ID('dbo.bridge_company_technology', 'U') IS NOT NULL DROP TABLE dbo.bridge_company_technology;
IF OBJECT_ID('dbo.fact_scalability_score', 'U') IS NOT NULL DROP TABLE dbo.fact_scalability_score;
IF OBJECT_ID('dbo.fact_training_cost_scenario', 'U') IS NOT NULL DROP TABLE dbo.fact_training_cost_scenario;
IF OBJECT_ID('dbo.fact_gpu_pricing', 'U') IS NOT NULL DROP TABLE dbo.fact_gpu_pricing;
IF OBJECT_ID('dbo.fact_partnership', 'U') IS NOT NULL DROP TABLE dbo.fact_partnership;
IF OBJECT_ID('dbo.fact_company_capability', 'U') IS NOT NULL DROP TABLE dbo.fact_company_capability;
IF OBJECT_ID('dbo.fact_disengagement', 'U') IS NOT NULL DROP TABLE dbo.fact_disengagement;
IF OBJECT_ID('dbo.fact_deployment_mileage', 'U') IS NOT NULL DROP TABLE dbo.fact_deployment_mileage;
IF OBJECT_ID('dbo.fact_av_incident', 'U') IS NOT NULL DROP TABLE dbo.fact_av_incident;
IF OBJECT_ID('dbo.dim_technology', 'U') IS NOT NULL DROP TABLE dbo.dim_technology;
IF OBJECT_ID('dbo.dim_source', 'U') IS NOT NULL DROP TABLE dbo.dim_source;
IF OBJECT_ID('dbo.dim_geography', 'U') IS NOT NULL DROP TABLE dbo.dim_geography;
IF OBJECT_ID('dbo.dim_date', 'U') IS NOT NULL DROP TABLE dbo.dim_date;
IF OBJECT_ID('dbo.dim_company', 'U') IS NOT NULL DROP TABLE dbo.dim_company;
GO

CREATE TABLE dbo.dim_company (
    company_id int NOT NULL CONSTRAINT PK_dim_company PRIMARY KEY,
    company_name nvarchar(100) NOT NULL CONSTRAINT UQ_dim_company_name UNIQUE,
    ecosystem_role nvarchar(250) NOT NULL,
    business_model_classification nvarchar(500) NOT NULL,
    automation_exposure nvarchar(250) NULL,
    sensor_strategy_summary nvarchar(500) NULL,
    in_vehicle_compute_summary nvarchar(500) NULL,
    commercial_model nvarchar(500) NULL,
    comparability_boundary nvarchar(1000) NULL,
    geographic_reach_summary nvarchar(500) NULL,
    primary_source_id varchar(20) NULL
);
GO

CREATE TABLE dbo.dim_date (
    date_key int NOT NULL CONSTRAINT PK_dim_date PRIMARY KEY,
    full_date date NOT NULL CONSTRAINT UQ_dim_date_full_date UNIQUE,
    [year] int NOT NULL,
    [quarter] varchar(10) NOT NULL,
    month_number tinyint NOT NULL CONSTRAINT CK_dim_date_month CHECK (month_number BETWEEN 1 AND 12),
    month_name nvarchar(20) NOT NULL,
    year_month char(7) NOT NULL,
    cutoff_valid bit NOT NULL
);
GO

CREATE TABLE dbo.dim_geography (
    geography_id int NOT NULL CONSTRAINT PK_dim_geography PRIMARY KEY,
    geography_name nvarchar(250) NOT NULL,
    state_code char(2) NULL,
    country nvarchar(100) NOT NULL,
    geography_level nvarchar(100) NOT NULL,
    note nvarchar(1000) NULL
);
GO

CREATE TABLE dbo.dim_source (
    source_id varchar(20) NOT NULL CONSTRAINT PK_dim_source PRIMARY KEY,
    organization nvarchar(200) NOT NULL,
    title nvarchar(1000) NOT NULL,
    source_type nvarchar(200) NOT NULL,
    publication_date date NOT NULL,
    historical_period_covered nvarchar(250) NULL,
    access_date date NOT NULL,
    source_url nvarchar(2000) NOT NULL,
    variables_or_claims_supported nvarchar(max) NULL,
    reliability_classification nvarchar(200) NOT NULL,
    relevant_limitations nvarchar(max) NULL,
    source_class nvarchar(50) NOT NULL,
    cutoff_valid bit NOT NULL,
    is_primary bit NOT NULL
);
GO

CREATE TABLE dbo.dim_technology (
    technology_id int NOT NULL CONSTRAINT PK_dim_technology PRIMARY KEY,
    technology_name nvarchar(200) NOT NULL CONSTRAINT UQ_dim_technology_name UNIQUE,
    technology_category nvarchar(150) NOT NULL,
    description nvarchar(max) NOT NULL,
    input_or_unit nvarchar(250) NULL,
    comparability_warning nvarchar(max) NULL
);
GO

CREATE TABLE dbo.fact_av_incident (
    report_id varchar(50) NOT NULL CONSTRAINT PK_fact_av_incident PRIMARY KEY,
    report_version int NOT NULL,
    company_id int NULL,
    reporting_entity_standardized nvarchar(250) NOT NULL,
    report_type nvarchar(100) NULL,
    incident_month date NULL,
    submission_month date NULL,
    city nvarchar(200) NULL,
    state varchar(20) NULL,
    make nvarchar(100) NULL,
    model nvarchar(100) NULL,
    model_year int NULL,
    mileage decimal(20,2) NULL,
    roadway_type nvarchar(200) NULL,
    roadway_surface nvarchar(200) NULL,
    lighting nvarchar(200) NULL,
    crash_with nvarchar(250) NULL,
    highest_injury_severity_alleged nvarchar(250) NULL,
    severity_category nvarchar(100) NULL,
    property_damage nvarchar(100) NULL,
    sv_pre_crash_movement nvarchar(250) NULL,
    sv_precrash_speed_mph decimal(10,2) NULL,
    within_odd nvarchar(100) NULL,
    source_id varchar(20) NOT NULL,
    record_hash char(64) NOT NULL,
    CONSTRAINT FK_fact_av_incident_company FOREIGN KEY (company_id) REFERENCES dbo.dim_company(company_id),
    CONSTRAINT FK_fact_av_incident_source FOREIGN KEY (source_id) REFERENCES dbo.dim_source(source_id)
);
GO

CREATE TABLE dbo.fact_deployment_mileage (
    deployment_metric_id int NOT NULL CONSTRAINT PK_fact_deployment_mileage PRIMARY KEY,
    company_id int NULL,
    metric_date date NOT NULL,
    metric_name nvarchar(250) NOT NULL,
    unit nvarchar(100) NOT NULL,
    metric_value decimal(24,4) NOT NULL CONSTRAINT CK_deployment_metric_value CHECK (metric_value >= 0),
    period_type nvarchar(100) NULL,
    geography nvarchar(500) NULL,
    reporting_method nvarchar(500) NULL,
    source_id varchar(20) NOT NULL,
    historical_cutoff_valid bit NOT NULL,
    limitation nvarchar(max) NULL,
    CONSTRAINT FK_deployment_company FOREIGN KEY (company_id) REFERENCES dbo.dim_company(company_id),
    CONSTRAINT FK_deployment_source FOREIGN KEY (source_id) REFERENCES dbo.dim_source(source_id)
);
GO

CREATE TABLE dbo.fact_disengagement (
    disengagement_id int NOT NULL CONSTRAINT PK_fact_disengagement PRIMARY KEY,
    company_id int NULL,
    period_start date NOT NULL,
    period_end date NOT NULL,
    total_autonomous_miles decimal(24,4) NULL,
    safety_driver_miles decimal(24,4) NULL,
    driverless_miles decimal(24,4) NULL,
    disengagement_count decimal(24,4) NULL,
    geography nvarchar(500) NULL,
    source_id varchar(20) NOT NULL,
    limitation nvarchar(max) NULL,
    CONSTRAINT FK_disengagement_company FOREIGN KEY (company_id) REFERENCES dbo.dim_company(company_id),
    CONSTRAINT FK_disengagement_source FOREIGN KEY (source_id) REFERENCES dbo.dim_source(source_id)
);
GO

CREATE TABLE dbo.fact_company_capability (
    capability_id int NOT NULL CONSTRAINT PK_fact_company_capability PRIMARY KEY,
    company_id int NOT NULL,
    capability_category nvarchar(200) NOT NULL,
    evidence_summary nvarchar(max) NOT NULL,
    evidence_status nvarchar(100) NOT NULL,
    source_id varchar(20) NOT NULL,
    evidence_strength_1_5 tinyint NOT NULL CONSTRAINT CK_capability_strength CHECK (evidence_strength_1_5 BETWEEN 1 AND 5),
    limitation nvarchar(max) NULL,
    CONSTRAINT FK_capability_company FOREIGN KEY (company_id) REFERENCES dbo.dim_company(company_id),
    CONSTRAINT FK_capability_source FOREIGN KEY (source_id) REFERENCES dbo.dim_source(source_id)
);
GO

CREATE TABLE dbo.fact_partnership (
    partnership_id int NOT NULL CONSTRAINT PK_fact_partnership PRIMARY KEY,
    company_id int NOT NULL,
    partner_name nvarchar(250) NOT NULL,
    partnership_type nvarchar(250) NULL,
    geography nvarchar(500) NULL,
    announcement_date date NULL,
    end_date date NULL,
    scope nvarchar(max) NULL,
    source_id varchar(20) NOT NULL,
    CONSTRAINT FK_partnership_company FOREIGN KEY (company_id) REFERENCES dbo.dim_company(company_id),
    CONSTRAINT FK_partnership_source FOREIGN KEY (source_id) REFERENCES dbo.dim_source(source_id)
);
GO

CREATE TABLE dbo.fact_gpu_pricing (
    gpu_price_id int NOT NULL CONSTRAINT PK_fact_gpu_pricing PRIMARY KEY,
    cloud_provider nvarchar(100) NOT NULL,
    instance_family nvarchar(100) NULL,
    gpu_model nvarchar(100) NOT NULL,
    instance_type nvarchar(200) NOT NULL,
    gpus_per_instance int NOT NULL CONSTRAINT CK_gpu_count CHECK (gpus_per_instance > 0),
    hourly_price_usd decimal(18,6) NOT NULL CONSTRAINT CK_gpu_hourly_price CHECK (hourly_price_usd > 0),
    price_per_gpu_hour_usd decimal(18,6) NOT NULL CONSTRAINT CK_gpu_unit_price CHECK (price_per_gpu_hour_usd > 0),
    region_reference nvarchar(200) NULL,
    pricing_model nvarchar(100) NULL,
    price_snapshot_date date NOT NULL,
    price_unit nvarchar(50) NOT NULL,
    source_id varchar(20) NOT NULL,
    limitation nvarchar(max) NULL,
    CONSTRAINT FK_gpu_pricing_source FOREIGN KEY (source_id) REFERENCES dbo.dim_source(source_id)
);
GO

CREATE TABLE dbo.fact_training_cost_scenario (
    cost_scenario_id int NOT NULL CONSTRAINT PK_fact_training_cost_scenario PRIMARY KEY,
    scenario_id int NOT NULL,
    scenario_name nvarchar(200) NOT NULL,
    gpu_price_id int NOT NULL,
    cloud_provider nvarchar(100) NOT NULL,
    instance_type nvarchar(200) NOT NULL,
    gpu_model nvarchar(100) NOT NULL,
    required_gpus int NOT NULL,
    instances_required int NOT NULL,
    provisioned_gpus int NOT NULL,
    training_hours_per_run decimal(18,4) NOT NULL,
    number_of_runs int NOT NULL,
    utilization_rate decimal(10,6) NOT NULL CONSTRAINT CK_scenario_utilization CHECK (utilization_rate > 0 AND utilization_rate <= 1),
    discount_model nvarchar(100) NOT NULL,
    price_factor decimal(10,6) NOT NULL,
    training_compute_cost_usd decimal(24,6) NOT NULL,
    simulation_compute_cost_usd decimal(24,6) NOT NULL,
    base_storage_cost_usd decimal(24,6) NOT NULL,
    checkpoint_storage_cost_usd decimal(24,6) NOT NULL,
    egress_cost_usd decimal(24,6) NOT NULL,
    total_cost_usd decimal(24,6) NOT NULL,
    source_id varchar(20) NOT NULL,
    interpretation_note nvarchar(max) NULL,
    CONSTRAINT FK_training_gpu_price FOREIGN KEY (gpu_price_id) REFERENCES dbo.fact_gpu_pricing(gpu_price_id),
    CONSTRAINT FK_training_source FOREIGN KEY (source_id) REFERENCES dbo.dim_source(source_id)
);
GO

CREATE TABLE dbo.fact_scalability_score (
    score_id int NOT NULL CONSTRAINT PK_fact_scalability_score PRIMARY KEY,
    company_id int NOT NULL,
    criterion_id int NOT NULL,
    score_1_5 tinyint NOT NULL CONSTRAINT CK_scalability_score CHECK (score_1_5 BETWEEN 1 AND 5),
    source_id varchar(20) NOT NULL,
    evidence_note nvarchar(max) NULL,
    missing_data_treatment nvarchar(max) NULL,
    CONSTRAINT FK_scalability_company FOREIGN KEY (company_id) REFERENCES dbo.dim_company(company_id),
    CONSTRAINT FK_scalability_source FOREIGN KEY (source_id) REFERENCES dbo.dim_source(source_id)
);
GO

CREATE TABLE dbo.bridge_company_technology (
    company_id int NOT NULL,
    technology_id int NOT NULL,
    relationship_type nvarchar(200) NOT NULL,
    CONSTRAINT PK_bridge_company_technology PRIMARY KEY (company_id, technology_id),
    CONSTRAINT FK_bridge_company FOREIGN KEY (company_id) REFERENCES dbo.dim_company(company_id),
    CONSTRAINT FK_bridge_technology FOREIGN KEY (technology_id) REFERENCES dbo.dim_technology(technology_id)
);
GO

CREATE TABLE dbo.qa_validation_result (
    validation_id int NOT NULL CONSTRAINT PK_qa_validation_result PRIMARY KEY,
    check_name nvarchar(250) NOT NULL,
    table_name nvarchar(250) NOT NULL,
    severity nvarchar(50) NOT NULL,
    status varchar(10) NOT NULL CONSTRAINT CK_validation_status CHECK (status IN ('PASS', 'FAIL')),
    expected nvarchar(max) NULL,
    actual nvarchar(max) NULL,
    details nvarchar(max) NULL,
    run_date date NOT NULL
);
GO

CREATE INDEX IX_incident_company_month ON dbo.fact_av_incident(company_id, incident_month);
CREATE INDEX IX_deployment_company_date ON dbo.fact_deployment_mileage(company_id, metric_date);
CREATE INDEX IX_capability_company_category ON dbo.fact_company_capability(company_id, capability_category);
CREATE INDEX IX_cost_scenario_provider ON dbo.fact_training_cost_scenario(scenario_name, cloud_provider, discount_model);
CREATE INDEX IX_score_company_criterion ON dbo.fact_scalability_score(company_id, criterion_id);
GO

/*
Loading guidance:
Use BULK INSERT, OPENROWSET, Azure Data Factory, SSIS, or a Python loader for
the delivered cleaned CSV files. Load dimensions first, then facts and bridges
in the same order used by python/build_database.py.
*/
