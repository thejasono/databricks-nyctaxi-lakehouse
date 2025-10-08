# Ingestion Notebooks Guide

This directory holds the interactive notebooks that seed the Bronze layer of the NYC Taxi Lakehouse demo. They are designed to be run after the Unity Catalog objects exist so that every Delta table lands in the governed `main_nyctaxi` catalog.

At this stage of the deployment, the catalog defined in the `unity` folder is already in place, so these notebooks focus on creating the Bronze layer inside that governed namespace. In Databricks, the Bronze layer represents the raw-but-persisted landing zone that captures ingested files with minimal transformation so you can audit and replay source data. Spark acts as the distributed processing engine that reads batches or streams of source files, applies light normalization, and writes the results as Delta Lake tables. For this project, the Bronze layer gives the Delta Live Tables pipeline a reliable, replayable source of taxi trips while letting you track data quality issues before promoting records downstream. Delta tables provide ACID transactions, schema evolution, and time travel so the raw history remains queryable and consistent even as sources evolve.

## Notebooks in this folder

### `01_auto_loader_bronze.sql.ipynb`
* **Purpose:** Streams raw NYC Taxi trip files into the Bronze Delta table that the Delta Live Tables pipeline consumes. In this context, a Delta table is a transactional storage layer on top of cloud object storage that combines the reliability of data warehouses with the scalability of data lakes.
* **When to use it:** Choose this path when you want to demonstrate Auto Loader’s incremental ingestion from cloud object storage. Auto Loader is Databricks’ optimized file ingestion service that automatically detects new files, infers schema changes, and continuously processes data as it arrives from a bucket or container in services such as AWS S3, Azure Data Lake Storage, or Google Cloud Storage. The notebook can run on an interactive or job cluster with a DBR that supports Auto Loader (11.3+ recommended).
* **Inputs to configure:**
  * `source_url` (cloud storage path or volume) pointing at the raw taxi files.
  * `checkpoint_location` unique to your workspace so Auto Loader can track progress.
  * Target catalog/schema names that match the Unity setup (defaults use `main_nyctaxi.raw`).

### How the Bronze notebook works end to end

After the Unity setup provisions the `main_nyctaxi` catalog, this notebook immediately switches to that catalog and its empty `raw` schema before creating a streaming Delta table named `taxi_raw`. That table is backed by Auto Loader, so Spark Structured Streaming jobs continuously ingest newly arrived files from the configured object storage path (for example, an S3 bucket) and append them to the Bronze table without manual intervention. Because the table is declared as streaming, Spark keeps it synchronized with the landing zone, ensuring the Bronze layer stays current for downstream transformations.

The `TBLPROPERTIES` block mirrors the recommended configuration for Delta Live Tables pipelines. Settings such as `pipelines.autoOptimize.managed = true` instruct Databricks to automatically compact small files and optimize storage layout over time. These options do not change the schema or the storage location, but they do keep the ingestion layer efficient even as data volumes grow.

Conceptually, `main_nyctaxi.raw.taxi_raw` is the Bronze landing zone for this project. It preserves raw, unmodeled taxi trip data as Delta files so that later Silver and Gold pipelines can cleanse, enrich, and publish curated datasets for analytics, dashboards, and monitoring workloads. The Unity Catalog provides the governance boundary, the `raw` schema acts as the staging area, and the Auto Loader–driven streaming table delivers the continuously updating foundation that powers the rest of the Lakehouse demo.

### Databricks concepts reinforced here

* **Auto Loader** for incrementally streaming new files with schema inference and evolution.
* **Volumes and external locations** for governed access to object storage.
* **Streaming tables** that persist state so DLT can subscribe without additional orchestration.
* **Job scheduling** when you wire the notebook into Workflows alongside the pipeline and monitoring steps.

## How these notebooks fit the overall flow

1. **After Unity setup:** Run the notebook once Unity Catalog has the `main_nyctaxi` catalog and the `raw` schema. This guarantees writes succeed and respect governance controls.
2. **Before DLT:** Successful Bronze ingestion provides the source table that `/dlt/02_dlt_pipeline.sql.ipynb` expects for building Silver and Gold layers.
3. **Re-running:** Because Auto Loader is incremental, subsequent runs pick up only new files. Resetting requires clearing the checkpoint and table manually—useful for demos that need a clean slate.

## Operational tips

* Use a cluster with the same access mode (single user or shared) as your production setup to mirror permissions.
* When ingesting from external storage, make sure the Unity Catalog external locations referenced in the Unity README are created so Auto Loader can read the files.
* Monitor the notebook run from the Jobs UI if you schedule it; long-running streams can continue appending data for real-time demos.

By working through these notebooks, you establish the Bronze ingestion layer that powers the downstream Delta Live Tables transformations, SQL queries, and monitoring workflows in the rest of the repository.

## Additional context you might find useful

* **Naming conventions help downstream automation.** Keeping table names aligned to the pattern `catalog.schema.table` (for example, `main_nyctaxi.raw.taxi_autoloader_bronze`) makes it easier to parameterize the DLT pipeline and SQL dashboards without brittle string substitutions.
* **Expect schema drift and late-arriving files.** Auto Loader automatically tracks new columns and backfilled data, but you should still review the schema evolution metrics after each run to confirm that unexpected attributes don’t require remediation before Silver processing.
* **Checkpoint hygiene matters.** Store checkpoints in Unity Catalog Volumes or secure object storage paths with lifecycle policies so that repeated demo runs don’t accumulate stale metadata or leak into production environments.
* **Validate Bronze outputs with sample queries.** Running quick aggregate checks (row counts by date, min/max timestamps) from a SQL Warehouse ensures the ingested data matches expectations before you trigger Silver/Gold transformations.
* **Document data quality contracts early.** If the downstream teams expect specific columns or SLAs, capture them now in the Bronze layer notebook markdown so future contributors know what guarantees the ingestion job is responsible for.
