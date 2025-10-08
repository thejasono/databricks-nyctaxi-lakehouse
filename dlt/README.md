# Delta Live Tables Pipeline Guide

This directory contains the assets that operationalize the Silver and Gold transformation layers for the NYC Taxi Lakehouse demo. After the Bronze ingestion notebooks populate `main_nyctaxi.raw`, these resources let you declaratively define expectations, manage incremental processing, and publish curated tables for downstream analytics without hand-building orchestration.

At this point in the end-to-end flow, the Unity Catalog objects are already provisioned and the Auto Loader notebook has delivered a continuously updating Bronze table. **Delta Live Tables (DLT)** is a Databricks-managed service that lets you declare data pipelines as code; DLT continuously reads the raw Delta tables, applies your logic, and materializes new Delta outputs while managing infrastructure for you. DLT runs on Databricks-managed compute so you can focus on **declarative transformations**—describing *what* you want to happen instead of writing step-by-step execution code—and on business **service-level agreements (SLAs)**—the contractual targets for refresh cadence, latency, and data quality—rather than on cluster plumbing. Because the output tables are **Delta tables** (the open data format that combines Apache Parquet storage with Delta Lake transaction logs), you retain:

* **ACID transactions:** Atomic, Consistent, Isolated, Durable writes that protect readers from partial updates.
* **Time travel:** The ability to query older table versions for auditing or rollbacks.
* **Schema enforcement and evolution:** Automatic checks that block unexpected columns or let you explicitly evolve schemas.

These guarantees are crucial because they keep data trustworthy across the Bronze → Silver → Gold medallion layers (a layered design that progressively refines raw data into curated, analytics-ready datasets), even as upstream data streams in continuously.

## Assets in this folder

### `02_dlt_pipeline.sql.ipynb`
* **Purpose:** Defines the entire DLT pipeline, including expectations, table dependencies, and materialized views that move data from `raw` to curated `ref` and `mart` schemas.
* **When to use it:** Attach this notebook to a DLT pipeline (Workflows → Pipelines) or a Lakeflow project whenever you want an automated, continuously updating transformation layer fed by the Bronze ingestion job. It works for both triggered (batch-style) and continuous (always-on) pipelines.
* **Inputs to configure:**
  * Pipeline storage location (for checkpoints and system tables).
  * Target catalog/schema names that match the Unity setup (`main_nyctaxi.ref` and `main_nyctaxi.mart`).
  * Optional configuration for refresh schedules, expectations severity, and change data capture (CDC) options.

### How the DLT notebook works end to end

The notebook declares a Bronze streaming table sourced from the Auto Loader output, applies expectations to filter or quarantine bad records, and produces clean Silver tables (`trips_valid`, reference dimensions) plus Gold materialized views for daily KPIs. Because DLT manages **lineage**—the complete record of which upstream tables and transformations produced a dataset—each table’s definition references upstream datasets with simple `CREATE OR REFRESH STREAMING TABLE` statements. Expectations such as `EXPECT trip_distance > 0` enforce quality and populate SLA dashboards automatically.

When the pipeline runs, Databricks provisions a managed **cluster**—a set of compute resources managed by Databricks that execute the transformations—that ingests new Bronze data, writes change data to Silver, and refreshes the Gold aggregates. DLT’s built-in monitoring captures event logs, expectation metrics, and throughput so you can validate every batch or micro-batch without additional instrumentation.

> **Why the notebook is “run by the pipeline”:** DLT interprets the notebook as pipeline code. You do not execute this notebook directly in a SQL warehouse or interactively like a standard notebook run. Instead, you create a DLT pipeline in Workflows (or Lakeflow), attach this notebook as the pipeline’s sole notebook task, and DLT orchestrates the execution whenever the pipeline runs. Think of a DLT pipeline as a managed DAG (directed acyclic graph) where each table/view definition is a node; the notebook defines the DAG, and the DLT service schedules and manages it automatically. Once configured, the pipeline can run on a schedule, in response to data arrivals, or on demand without manual intervention.

### `pipeline_settings.json`
* **Purpose:** Provides a template configuration for the pipeline, covering cluster settings, continuous mode, target catalog, storage locations, and notebook libraries.
* **How to use it:** Copy the JSON when creating or updating the pipeline, replacing the `library` path with the workspace location of this repo (swap `.sql` for `.sql.ipynb` if you keep the notebook). Update the storage/base paths so checkpoints and system tables land in governed volumes or external locations appropriate for your workspace.

### Databricks concepts reinforced here

* **Delta Live Tables expectations** for declarative data quality and SLA tracking.
* **Streaming tables and materialized views** that keep Silver and Gold layers current for near-real-time analytics.
* **Managed orchestration** via Workflows → Pipelines or Lakeflow, including automated scaling and recovery.
* **Change data capture** options that let you enable schema evolution, apply CDC rules, or reuse existing checkpoints through `pipeline_settings.json`.

## How this pipeline fits the overall flow

1. **Foundation in Unity Catalog:** Run `/unity/00_main_nyctaxi_catalogue_creator.ipynb` first so the catalog and schemas referenced here exist with the right permissions.
2. **Bronze data availability:** Execute `/notebooks/01_auto_loader_bronze.sql.ipynb` to populate `main_nyctaxi.raw.taxi_raw`, which the DLT pipeline reads as its streaming source.
3. **Pipeline deployment:** Create or update a DLT pipeline using the SQL notebook and the JSON settings, pointing the storage location to your workspace path and targeting `main_nyctaxi`.
4. **Downstream consumption:** The resulting Silver and Gold tables power `/sql` queries, dashboards, and any ML/monitoring workloads that expect curated taxi data.
5. **Ongoing monitoring:** Use the DLT event log UI, `/monitoring/mlflow_demo.py`, or Lakehouse Monitoring to inspect throughput, expectation failures, and refresh cadence after each run.

## Operational tips

* Keep the pipeline compute policy aligned with your workspace governance (serverless or specific cluster policies) so access controls match production expectations.
* Store pipeline checkpoints and system tables in Unity Catalog Volumes or secured object storage paths to simplify cleanup between demos and prevent stale metadata.
* Review expectation metrics after each run to decide whether you need additional cleansing rules before promoting data to Gold consumers.
* Schedule the DLT pipeline alongside the ingestion notebook in Workflows if you want fully automated Bronze→Gold refreshes.

## Additional context you might find useful

* **Naming conventions simplify automation.** Stick with `catalog.schema.table` patterns (for example, `main_nyctaxi.mart.daily_kpis`) so SQL dashboards and monitoring scripts can reference tables without brittle rewrites.
* **Incremental logic benefits from small, frequent runs.** Continuous or hourly schedules keep Silver and Gold tables near real time while minimizing backfill effort.
* **System tables capture operational history.** Enable the DLT event log and quality dashboards to audit data freshness, failure rates, and expectation violations over time.
* **Testing in development workspaces pays dividends.** Clone this pipeline to a sandbox catalog before promoting changes so you can validate schema updates and expectation tweaks without affecting consumers.

By operationalizing these DLT assets, you extend the medallion architecture beyond ingestion and deliver trustworthy, production-ready datasets that feed analytics, dashboards, and monitoring workflows across the Lakehouse.
