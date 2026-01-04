# Unity Catalog Setup Guide

## Overview

Run the assets in this directory first. They create the governed namespaces that every notebook, SQL script, and monitoring asset in the NYC Taxi Lakehouse demo relies on. Databricks Unity Catalog defines catalogs, schemas, tables, volumes, and experiments for the entire workspace, so provisioning these objects upfront guarantees a consistent security and naming model. All instructions in this guide are written for Databricks Community (Free) Edition—you can execute the setup notebook from either an all-purpose cluster or a SQL Warehouse.

## Key Unity Catalog concepts

* **Catalog** – The top-level namespace. A catalog gathers related schemas, tables, views, volumes, and experiments under a single governance boundary (for example, `main_nyctaxi`).
* **Schema** – A logical container inside a catalog. Schemas organize objects by purpose, such as Bronze/Silver/Gold layers, and are referenced with two-part names like `main_nyctaxi.raw`.
* **Table** – A managed dataset stored in a schema. Tables hold rows produced or consumed by pipelines and are addressed with a three-part name (`catalog.schema.table`).

**How they relate:** Grants cascade downward. Granting `USE CATALOG` lets a principal see schemas; `USE SCHEMA` plus object-level permissions control table access. Keeping the hierarchy consistent is what makes the rest of the repository predictable.

## Primary asset: `00_main_nyctaxi_catalogue_creator.ipynb`

This SQL notebook bootstraps the governance layer with a short, repeatable sequence:

1. **Create the catalog** – Defines `main_nyctaxi` (or a name you choose) as the top-level container for all demo assets. Production teams typically create one catalog per domain or environment.
2. **Create schemas for each medallion layer** – Builds `raw`, `ref`, and `mart`, mirroring the Bronze/Silver/Gold pattern referenced throughout the repository. `raw` stores ingested landings, `ref` curates cleaned datasets, and `mart` exposes analytics-ready tables.
3. **Grant access** – Applies ownership and usage permissions so jobs, warehouses, and analysts can read and write to the appropriate schemas. Replace the demo principals with Unity Catalog groups or service principals in your workspace.
4. **Prepare for external data** – Includes templates for `CREATE EXTERNAL LOCATION` statements and optional `CREATE VOLUME` commands so you can register object storage paths under Unity Catalog governance when ingesting from the cloud.

Because the notebook uses idempotent `CREATE ... IF NOT EXISTS` and `GRANT` statements, you can re-run it safely whenever you need to verify or repair governance.

## Customize for your environment

* Swap `main_nyctaxi` with a catalog name that matches your domain (for example, `prod_finance`).
* Update each `GRANT` clause to point at the Unity Catalog groups, users, or service principals that own ingestion, transformation, and analytics tasks.
* Uncomment and populate the external location templates when your raw data resides in Amazon S3, Azure Data Lake Storage, or Google Cloud Storage.
* Add `CREATE VOLUME` statements in the relevant schemas if you plan to read from or write to managed Volumes.

## Where this step fits in the overall flow

1. **Provision governance (this folder).** Run the setup notebook from a SQL Warehouse or all-purpose cluster so the catalog, schemas, external locations, and optional experiments exist.
2. **Ingest Bronze data.** Move to `/notebooks/README.md` and execute `01_copy_into_bronze.sql.ipynb` to populate the `raw` schema once governance is in place.
3. **Transform Silver and Gold tables.** Use `/dlt/README.md` to rebuild the curated layers on top of the governed catalog.
4. **Serve analytics and monitor health.** The `/sql` and `/monitoring` folders depend on the permissions and namespaces created here.

## Next steps

After the catalog and schemas exist, proceed to the ingestion notebook guide so you can load raw taxi trips into `main_nyctaxi.raw.taxi_raw`. Keeping the Unity Catalog objects version-controlled alongside your notebooks ensures everyone shares the same governed foundation before any pipelines run.
