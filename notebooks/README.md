# Ingestion Notebook Guide

## Overview

The notebook in this directory seeds the Bronze layer of the NYC Taxi Lakehouse demo after Unity Catalog governance is in place. It targets Databricks Community (Free) Edition and should be run on an all-purpose cluster. By loading data into a governed Bronze Delta table, you create the durable landing zone that downstream SQL transformations and dashboards depend on.

## Notebook: `01_copy_into_bronze.sql.ipynb`

* **Purpose** – Executes a batch `COPY INTO` command that loads raw NYC Taxi trip files into the Bronze Delta table consumed by later stages. It also contains an optional sample insert so you can run the demo without external files.
* **When to run** – After the Unity Catalog setup notebook creates the `main_nyctaxi` catalog and schemas. Use it to backfill or refresh Bronze data on demand.
* **Inputs to configure** – Provide the governed landing path (`landing_path`), optional sample insert toggle, and (if changed) the catalog/schema names that match your Unity setup.

## How the notebook works

1. Switches to the governed catalog and `raw` schema created during the Unity setup.
2. Creates the `taxi_raw` table with `CREATE TABLE IF NOT EXISTS ... LIKE samples.nyctaxi.trips` to mirror the expected schema.
3. Runs `COPY INTO` against your Unity Catalog Volume or external location so only new files are ingested on subsequent runs.
4. Offers an optional `INSERT OVERWRITE` command that seeds the table from `samples.nyctaxi.trips` when you need a lightweight demo without uploading data.

Because `COPY INTO` tracks ingestion history, re-running the notebook is idempotent: new files append automatically, and you can force a reload by truncating the table or passing `FORCE = true` if you need a clean reset.

## Databricks concepts reinforced

* **COPY INTO** for incremental batch ingestion with schema inference and evolution support.
* **Volumes and external locations** for governed access to cloud object storage through Unity Catalog.
* **Delta Lake fundamentals** that preserve ACID guarantees even in a purely batch design.
* **Jobs scheduling** when you wire the notebook into a Databricks Workflow alongside transformation and monitoring tasks.

## Where this step fits in the project

1. **After governance** – Run the notebook once `/unity/00_main_nyctaxi_catalogue_creator.ipynb` has provisioned the catalog and schemas.
2. **Before transformations** – Successful Bronze ingestion supplies the source table that `/dlt/02_dlt_pipeline.sql.ipynb` expects for Silver and Gold processing.
3. **During refreshes** – Because `COPY INTO` remembers processed files, subsequent runs pick up only new data. Use `FORCE = true` or truncate the table when you need to replay everything for a demo.

## Operational tips

* Use a cluster with the same access mode (single user or shared) as your production setup so permissions mirror reality.
* Confirm the Unity Catalog external locations referenced in the Unity guide exist before running against cloud storage.
* Monitor scheduled runs from the Jobs UI if you automate the notebook; batch refreshes can be on-demand without keeping long-lived clusters alive.

## Next steps

After the Bronze table is populated, move to `/dlt/README.md` to rebuild the Silver and Gold layers that drive analytics and monitoring.
