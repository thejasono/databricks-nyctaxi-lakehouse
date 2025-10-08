# Ingestion Notebooks Guide

This directory holds the interactive notebooks that seed the Bronze layer of the NYC Taxi Lakehouse demo. They are designed to be run after the Unity Catalog objects exist so that every Delta table lands in the governed `main_nyctaxi` catalog.

## Notebooks in this folder

### `01_auto_loader_bronze.sql.ipynb`
* **Purpose:** Streams raw NYC Taxi trip files into the Bronze Delta table that the Delta Live Tables pipeline consumes.
* **When to use it:** Choose this path when you want to demonstrate Auto Loader’s incremental ingestion from cloud object storage. The notebook can run on an interactive or job cluster with a DBR that supports Auto Loader (11.3+ recommended).
* **Inputs to configure:**
  * `source_url` (cloud storage path or volume) pointing at the raw taxi files.
  * `checkpoint_location` unique to your workspace so Auto Loader can track progress.
  * Target catalog/schema names that match the Unity setup (defaults use `main_nyctaxi.raw`).

## How these notebooks fit the overall flow

1. **After Unity setup:** Run the notebook once Unity Catalog has the `main_nyctaxi` catalog and the `raw` schema. This guarantees writes succeed and respect governance controls.
2. **Before DLT:** Successful Bronze ingestion provides the source table that `/dlt/02_dlt_pipeline.sql` expects for building Silver and Gold layers.
3. **Re-running:** Because Auto Loader is incremental, subsequent runs pick up only new files. Resetting requires clearing the checkpoint and table manually—useful for demos that need a clean slate.

## Operational tips

* Use a cluster with the same access mode (single user or shared) as your production setup to mirror permissions.
* When ingesting from external storage, make sure the Unity Catalog external locations referenced in the Unity README are created so Auto Loader can read the files.
* Monitor the notebook run from the Jobs UI if you schedule it; long-running streams can continue appending data for real-time demos.

By working through these notebooks, you establish the Bronze ingestion layer that powers the downstream Delta Live Tables transformations, SQL queries, and monitoring workflows in the rest of the repository.
