# Monitoring and Observability Guide

This directory contains lightweight observability assets that help you track the health of the NYC Taxi Lakehouse demo after the Delta Live Tables pipeline runs. Use the resources here to instrument key metrics and keep stakeholders informed about pipeline performance.

## Files in this folder

### `mlflow_demo.py`
* **Purpose:** Logs basic operational metrics about the Silver layer to MLflow so you can trend row counts and contextual data over time.
* **When to run it:** Trigger the script after successful DLT refreshes—either manually from a Databricks job or as a downstream task in a workflow.
* **Prerequisites to configure:**
  * Set the MLflow experiment path to a workspace location your team can access.
  * Ensure the script references the same catalog and schema names created during Unity setup (defaults assume `main_nyctaxi.ref`).
  * Provide the correct Delta table names or extend the script to pull additional metrics relevant to your governance policies.

## How monitoring fits the overall flow

1. **Unity Catalog first:** Run `/unity/00_uc_setup.sql` so the catalog and schemas exist—MLflow runs will reference these governed table names.
2. **Ingest Bronze data:** Use the notebooks in `/notebooks` to populate the Bronze table that the DLT pipeline consumes.
3. **Build Silver/Gold with DLT:** Execute the pipeline in `/dlt` to materialize curated datasets that monitoring will observe.
4. **Log metrics with MLflow:** Run `mlflow_demo.py` to capture row counts, pipeline metadata, or event log statistics after each refresh. These runs give you visibility into data quality and pipeline stability.
5. **Iterate:** Expand the script with additional metrics, alerts, or integrations with Databricks Lakehouse Monitoring as your project matures.

By operationalizing monitoring through MLflow (or your chosen observability tooling), you close the loop on the Lakehouse lifecycle—governed ingestion, reliable transformations, and measurable outcomes.
