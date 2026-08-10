# Raw Data Notes

The raw folder preserves source fields and acquisition records.

`nhtsa_ads_curated_schema_excerpt.csv` contains three verified pre cutoff ADS rows used only for pipeline execution and schema validation. It is not representative and must not be used for safety rates.

Run `python/acquire_data.py` in a normal networked environment to download the complete archived NHTSA files. The official files are not bundled because the execution runtime could not reliably transfer the large archives.
