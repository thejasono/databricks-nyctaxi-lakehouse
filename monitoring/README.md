# Monitoring and Observability Guide

## Overview

Use the assets in this directory after the batch medallion SQL publishes the Silver and Gold layers. They provide a lightweight way to log operational metrics so you can confirm the NYC Taxi Lakehouse demo is healthy. By running entirely on Databricks Community (Free) Edition—using MLflow and standard clusters—you can close the feedback loop without paid services. At this stage Unity Catalog governance is in place, `main_nyctaxi.raw.taxi_raw` has been ingested, and the curated tables in `main_nyctaxi.ref` and `main_nyctaxi.mart` exist.

## File in this folder

### `mlflow_demo.py`
* **Purpose** – Logs row counts, latency indicators, and contextual metadata from the Silver layer into an MLflow experiment each time the batch pipeline finishes.
* **When to run** – Trigger it as a downstream task after `/dlt/02_dlt_pipeline.sql.ipynb` (or the `.sql` export) completes. Run it manually, from a Databricks Job, or inside a Lakehouse Monitoring project.
* **Inputs to configure** – Set `MLFLOW_EXPERIMENT_PATH`, confirm catalog/schema names align with your Unity setup, and extend the script if you want to track additional tables or metrics.

## How the script works

1. Initializes Spark, switches to the governed catalog and schema (`main_nyctaxi.ref` by default), and sets the MLflow experiment path.
2. Starts an MLflow run that acts as an auditable record of a pipeline execution.
3. Reads the curated Silver table (for example, `main_nyctaxi.ref.trips_valid`) to gather counts, min/max dates, and quality indicators.
4. Logs metrics, parameters, and tags—including freshness timestamps, null ratios, pipeline metadata, and warnings when thresholds are exceeded.
5. Captures a CSV sample artifact and prints run details so notebook logs mirror what is stored in MLflow.
6. Ends the MLflow run, leaving an immutable history you can analyze from the Experiments UI or via system tables.

## Databricks concepts reinforced

* **MLflow tracking** for non-ML workloads, treating pipeline refreshes as first-class runs that can be audited.
* **Unity Catalog governance** for experiments, Delta tables, and checkpoints within the same namespace.
* **Jobs orchestration and Lakehouse Monitoring** to chain monitoring tasks immediately after transformations.
* **Batch quality validation** with SQL-derived metrics in lieu of managed expectations.

## How monitoring fits the project

1. **Provision governance** – `/unity/README.md` creates the catalog, schemas, external locations, and experiments.
2. **Ingest Bronze data** – `/notebooks/README.md` loads raw taxi trips.
3. **Transform with SQL** – `/dlt/README.md` materializes Silver and Gold tables.
4. **Capture metrics (this folder)** – Run `mlflow_demo.py` to log row counts, null ratios, and context immediately after each refresh.
5. **Operationalize** – Query MLflow experiments or Lakehouse Monitoring dashboards to confirm SLAs, send alerts, and iterate on metrics.

## Operational tips

* Schedule the script alongside the transformation job so metrics align with the latest data.
* Combine MLflow metrics with Databricks notifications or external tools (PagerDuty, Slack, Teams) to alert when thresholds are breached.
* Store any downstream Delta outputs (for example, MLflow metrics tables) in governed Unity Catalog locations.
* Enable Lakehouse Monitoring dashboards to visualize row-count trends and anomaly scores; they complement the MLflow runs logged here.
* Tag runs with owners or environments so responders know who maintains the pipeline.

## Next steps

Extend the script with additional metrics—schema drift checks, cost estimates, or quality thresholds—and feed those results into dashboards or alerts so stakeholders can trust every refresh of the NYC Taxi datasets.
