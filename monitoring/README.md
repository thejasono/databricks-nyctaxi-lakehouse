# Monitoring and Observability Guide

This directory collects the lightweight observability assets that help you prove the NYC Taxi Lakehouse demo is behaving as expected after the Delta Live Tables (DLT) pipeline publishes the Silver and Gold layers. At this stage of the journey, Unity Catalog governance is in place, the Bronze ingestion notebook has landed raw taxi trips, and the DLT pipeline has already materialized curated Delta tables in `main_nyctaxi.ref` and `main_nyctaxi.mart`. The goal here is to close the feedback loop by tracking operational metrics, validating quality, and signaling when downstream consumers can trust the refreshed data. Databricks treats monitoring as a first-class citizen—services like MLflow, Lakehouse Monitoring, and the DLT event log all expose hooks so you can capture health indicators without bolting on external tooling.

Delta tables remain the backbone for every layer, so the observability workflow inherits **ACID transactions**, **time travel**, and **schema enforcement**. The script in this folder logs metrics to **MLflow**—the experiment tracking service native to Databricks that stores runs, parameters, metrics, and artifacts inside governed Unity Catalog experiments. Those runs become the operational ledger for your pipelines: they record refresh timestamps, row counts, and any contextual metadata you want to capture. Because MLflow experiments are governed objects, lineage and permissions stay consistent with the rest of the Lakehouse, and you can join run data back to Delta tables or dashboards for deeper analytics.

## Files in this folder

### `mlflow_demo.py`
* **Purpose:** Instruments the Silver layer by logging row counts, latency signals, and other contextual metrics to an MLflow experiment each time the DLT pipeline finishes. Treat it as a starting point for building a broader monitoring job that ties into alerts or dashboards.
* **When to use it:** Run the script as a downstream task after `/dlt/02_dlt_pipeline.sql.ipynb` completes—either manually, as part of a Databricks Job sequence, or within a Lakeflow project. Triggering it right after DLT ensures the captured metrics align with the latest pipeline run.
* **Inputs to configure:**
  * `MLFLOW_EXPERIMENT_PATH` pointing at a Unity Catalog experiment (for example, `main_nyctaxi/monitoring`).
  * Catalog and schema names that match your Unity setup (defaults assume `main_nyctaxi.ref`).
  * Target Delta table names if you extend the script to track additional assets beyond the provided Silver table.

Key snippets inside the script illustrate how to authenticate with MLflow from a Databricks job, fetch row counts from Delta tables via Spark, and log metrics with run-level tags that capture pipeline metadata (for example, pipeline run IDs, cluster policies, or DLT expectation summaries). Because MLflow tracks time-series metrics per run, you can trend row counts across refreshes, detect anomalies (such as a sudden drop in valid trips), and feed the data into dashboards or alerting rules.

## How the monitoring script works end to end

1. **Establish context:** The script initializes a Spark session and switches to the governed catalog and schema (`main_nyctaxi.ref`) created during the Unity setup.
2. **Open an MLflow run:** It sets the MLflow experiment path (Unity Catalog experiments support access control and lineage) and starts a new run, which is an auditable record of a pipeline execution.
3. **Query Delta tables:** Using Spark SQL, it reads the curated Silver table (for example, `main_nyctaxi.ref.trips_valid`) to gather counts, min/max dates, or expectation failure totals captured in DLT event logs.
4. **Log metrics and tags:** The script records row counts, freshness timestamps, and any contextual metadata (pipeline mode, workspace URL, commit SHA) as MLflow metrics and tags so analysts can trace runs back to code versions.
5. **Persist artifacts (optional):** Extend the script to store JSON summaries or rendered charts as run artifacts—MLflow will version them alongside the metrics.
6. **Close the run:** Once metrics are logged, MLflow seals the run with start/end timestamps so you can compute latency and reliability trends directly from the experiment UI or via API queries.

Because MLflow runs are immutable records, they create an operational audit trail parallel to the data stored in Delta tables. You can query the MLflow system tables, join them with DLT event logs, and build dashboards that highlight refresh cadence, row-count drift, or quality gate failures over time.

## Databricks concepts reinforced here

* **MLflow tracking** for non-ML workloads—treating pipeline refreshes as first-class runs that can be monitored, alerted on, and audited.
* **Unity Catalog governance** by storing experiments, Delta tables, and checkpoints inside the same governed namespace.
* **Jobs orchestration and Lakeflow** for chaining monitoring tasks immediately after ingestion and transformation complete.
* **Lakehouse Monitoring and DLT event logs** as complementary data sources for expectations, throughput, and anomaly detection.

## How monitoring fits the overall flow

1. **Provision governance:** Execute `/unity/00_main_nyctaxi_catalogue_creator.ipynb` so the catalog, schemas, external locations, and experiments exist with the right permissions.
2. **Ingest Bronze data:** Run `/notebooks/01_auto_loader_bronze.sql.ipynb` to stream raw taxi trips into the governed Bronze table.
3. **Transform with DLT:** Deploy `/dlt/02_dlt_pipeline.sql.ipynb` via a DLT pipeline to populate Silver and Gold Delta tables.
4. **Capture metrics:** Trigger `mlflow_demo.py` to log row counts, freshness indicators, and quality signals after each DLT refresh.
5. **Operationalize insights:** Query the MLflow experiment history, DLT event logs, or Lakehouse Monitoring dashboards to confirm SLAs, alert stakeholders, and feed dashboards.
6. **Iterate:** Extend the script with additional metrics (expectation failure counts, schema drift alerts, cost estimates) as your Lakehouse matures.

## Operational tips

* **Schedule alongside DLT:** Use Databricks Workflows to run the monitoring script immediately after the pipeline so metrics stay aligned with the latest data.
* **Surface alerts:** Combine MLflow metrics with Databricks notifications, SQL alerts, or external tools (PagerDuty, Slack, Microsoft Teams) to signal when thresholds are breached.
* **Store checkpoints in governed locations:** If you enrich the script with Delta outputs (for example, persisting MLflow metrics into a Delta table), keep those tables inside Unity Catalog volumes or external locations with proper lifecycle policies.
* **Leverage Lakehouse Monitoring:** Enable native dashboards to visualize expectation pass/fail rates, latency, and anomaly scores; they complement the MLflow runs logged here.
* **Document ownership:** Tag runs with responsible teams or service owners so on-call responders know who to contact when alerts fire.

## Additional context you might find useful

* **Treat metrics as data.** Consider landing MLflow run metrics into Delta tables (`main_nyctaxi.monitoring.pipeline_runs`) so you can join them with business KPIs and build holistic health dashboards.
* **Exploit time travel for audits.** Because Delta tables retain history, you can reconstruct the state of monitoring outputs at any point—useful for compliance reviews or demo resets.
* **Align naming conventions.** Keep experiment names, schema names, and table names consistent (`main_nyctaxi.ref`, `main_nyctaxi.mart`) to simplify parameterization across notebooks, pipelines, and monitoring scripts.
* **Iterate in lower environments.** Clone the script to a sandbox catalog before rolling changes into production demos to validate permissions and MLflow experiment access without affecting stakeholders.
* **Integrate with Unity Catalog lineage.** Linking MLflow runs to Delta tables enhances lineage graphs, making it easier to trace which pipeline run produced a given dashboard refresh.

By operationalizing the monitoring assets in this folder, you extend the Lakehouse lifecycle beyond ingestion and transformation—creating a measurable, auditable feedback loop that keeps stakeholders confident in the quality and freshness of the NYC Taxi datasets.
