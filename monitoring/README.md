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

### Databricks concepts reinforced here

* **MLflow tracking** for non-ML workloads (data pipelines, data quality metrics).
* **Unity Catalog integration** by writing metrics to governed experiments and Delta tables.
* **Jobs orchestration** by chaining monitoring tasks after DLT completes.
* **Cross-team observability** when you publish the metrics into dashboards or alerting systems.

### Extending observability for production

* **Event logs:** Query the DLT pipeline event log to capture expectation pass/fail counts or schema evolution warnings.
* **Lakehouse Monitoring:** Pair this script with native monitoring dashboards to visualize refresh latency and anomaly scores.
* **Alerting:** Configure Databricks Jobs notifications or external alerting (PagerDuty, Teams, Slack) when metrics deviate from thresholds you define in MLflow.
* **Data quality integration:** Persist the MLflow metrics back into a governed Delta table to join with product usage analytics or SLA dashboards.

## How monitoring fits the overall flow

1. **Unity Catalog first:** Run `/unity/00_main_nyctaxi_catalogue_creator.ipynb` so the catalog and schemas exist—MLflow runs will reference these governed table names.
2. **Ingest Bronze data:** Use `/notebooks/01_auto_loader_bronze.sql.ipynb` (or the sample stream) to populate the Bronze table that the DLT pipeline consumes.
3. **Build Silver/Gold with DLT:** Execute `/dlt/02_dlt_pipeline.sql.ipynb` (via a DLT pipeline) to materialize curated datasets that monitoring will observe.
4. **Log metrics with MLflow:** Run `mlflow_demo.py` to capture row counts, pipeline metadata, or event log statistics after each refresh. These runs give you visibility into data quality and pipeline stability.
5. **Iterate:** Expand the script with additional metrics, alerts, or integrations with Databricks Lakehouse Monitoring as your project matures.

By operationalizing monitoring through MLflow (or your chosen observability tooling), you close the loop on the Lakehouse lifecycle—governed ingestion, reliable transformations, and measurable outcomes.
