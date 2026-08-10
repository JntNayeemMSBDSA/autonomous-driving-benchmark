# Reproducibility Guide

## Environment

Use Python 3.10 or later. Install the packages in `requirements.txt`.

## Full local run

From the project root:

```bash
python python/run_pipeline.py
```

The default command uses the bundled cutoff-safe evidence, regenerates canonical incident, deployment, cost, scalability, Power BI CSV, and validation outputs, rebuilds SQLite, and validates the result without requiring internet access.

## Acquire full NHTSA data

```bash
python python/acquire_data.py
python python/run_pipeline.py
```

The acquisition script downloads the official archived ADS, Level 2 ADAS, and OTHER files through June 15, 2025, writes SHA 256 checksums, and logs failures without silently substituting data.

## Database

The delivered SQLite database is already populated and validated. The recommended rebuild method is:

```bash
python python/build_database.py
```

This method works even when the SQLite command line client is unavailable. The alternative CLI load sequence is documented in `sql/02_load_data.sql`.

Run checks:

```bash
sqlite3 sql/autonomous_driving.db < sql/04_validation_checks.sql
```

## Notebooks

Execute notebooks from the project root so relative paths resolve.

## Verification

Successful reproduction should show:

* all source dates at or before 2025-06-30
* zero duplicate source IDs
* zero SQLite foreign key violations
* scenario cost component difference below 0.01 USD
* scalability scores between 1 and 5
* each weight set totaling 100
