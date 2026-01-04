# Batch Medallion Pipeline Guide

## Overview

The SQL assets in this directory rebuild the Silver and Gold layers of the NYC Taxi Lakehouse demo using only Databricks Community (Free) Edition capabilities. Run them on a SQL Warehouse or all-purpose job cluster after the Bronze ingestion notebook has populated `main_nyctaxi.raw.taxi_raw`. The approach stays firmly inside the batch SQL toolkit so you can rehearse medallion patterns without managed pipeline services.

## Assets in this folder

### `02_dlt_pipeline.sql.ipynb`
* **Purpose** – Recreates `raw.taxi_bronze`, `ref.trips_clean`, `ref.trips_valid`, and `mart.daily_kpis` via standard SQL so Free Edition workspaces can implement the medallion architecture without premium features.
* **When to run** – Execute after `/notebooks/01_copy_into_bronze.sql.ipynb` completes. Re-run end to end whenever new Bronze data lands to keep downstream tables current.
* **Inputs to review** – Update catalog/schema names if you customized the Unity setup, and optionally switch the Bronze source to `samples.nyctaxi.trips` for demos without external files.

### `02_dlt_pipeline_sql_version.sql`
* **Purpose** – Plain SQL export of the notebook so you can run the same logic from the SQL editor, Databricks Jobs, or CI/CD pipelines without notebook metadata.
* **How to use it** – Paste the statements into a SQL Warehouse query or reference the file as a multi-command Jobs task. The statements are idempotent and overwrite the target tables with fresh results each run.

### `pipeline_settings.json`
* **Purpose** – Legacy configuration template for teams that may later upgrade to managed pipeline services. Free Edition users can ignore it safely.

## How the pipeline works

1. **Bronze refresh** – `CREATE OR REPLACE TABLE raw.taxi_bronze AS SELECT * FROM raw.taxi_raw;` copies the landing table into a governed Bronze table. An optional commented statement swaps the source to the Databricks sample dataset.
2. **Silver typing and pruning** – `ref.trips_clean` casts strings to typed columns while dropping rows with null distances or fares.
3. **Silver validation** – `ref.trips_valid` applies `WHERE` filters to reject null vendors and negative fares—the Free Edition alternative to declarative expectations.
4. **Gold aggregation** – `mart.daily_kpis` computes daily metrics as a standard Delta table instead of relying on materialized views.

Each step uses `CREATE OR REPLACE TABLE`, so re-running the notebook produces deterministic outputs. Schedule it after the ingestion notebook if you want an automated refresh cadence.

## Databricks concepts reinforced

* **Batch medallion processing** orchestrated with SQL notebooks or Jobs tasks.
* **Delta Lake ACID guarantees** that ensure reliable table rewrites across repeatable batch refreshes.
* **Unity Catalog governance** enforced through fully qualified `catalog.schema.table` references.
* **Workflows automation** that chains ingestion → transformation → monitoring without premium services.

## Where this step fits in the project

1. **Foundation** – `/unity/README.md` provisions the catalog and schemas referenced in these scripts.
2. **Bronze data available** – `/notebooks/README.md` ensures `main_nyctaxi.raw.taxi_raw` exists.
3. **Transformation** – This folder rebuilds the Silver and Gold tables in batch mode.
4. **Consumption & monitoring** – `/sql/README.md` and `/monitoring/README.md` rely on the curated tables produced here.

## Operational tips

* Keep the notebook and SQL export in sync if you customize logic; commit changes to both files.
* Parameterize catalog and schema names with SQL variables when promoting across environments.
* Store landing files, checkpoints, and MLflow experiments in Unity Catalog Volumes or external locations that align with your governance policies.
* Use Databricks Workflows to schedule the notebook alongside ingestion so Free Edition Jobs orchestrate the full medallion refresh.

## Next steps

After Silver and Gold tables are rebuilt, proceed to `/sql/README.md` to explore the curated metrics or to `/monitoring/README.md` to log data quality signals.
