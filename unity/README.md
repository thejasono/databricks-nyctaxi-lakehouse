# Unity Catalog Setup Guide

This directory contains assets that provision the Unity Catalog objects used by the NYC Taxi Lakehouse demo. The catalog provides the governance foundation for every downstream notebook, Delta Live Tables pipeline, and SQL dashboard. Use the notebook in this folder at the beginning of a new deployment so that all data engineering and analytics teams share the same controlled namespace.

## What the setup notebook does

The notebook `00_main_nyctaxi_catalogue_creator.ipynb` runs a short sequence of SQL commands that mirror best practices in a typical Databricks project:

1. **Create a dedicated catalog** – Defines `main_nyctaxi` (or a name you choose) as the top-level container for all demo objects. In production, you would create one catalog per domain or environment to isolate data products and apply consistent governance.
2. **Establish schemas for each layer** – Builds the `raw`, `ref`, and `mart` schemas. These map to the Bronze/Silver/Gold layers that the rest of the repo references. Separating schemas by layer keeps ingestion, curated reference data, and serving tables organized and easy to secure.
3. **Grant access to principals** – Applies ownership and usage grants so pipelines, warehouses, and analysts can read and write to the appropriate schemas. In a real project you would tailor these grants to service principals, groups, or Unity Catalog roles aligned to your organization’s governance model.
4. **Register storage locations (if needed)** – The notebook is structured to let you add `CREATE EXTERNAL LOCATION` statements when your data lands in cloud object storage. This is how Unity Catalog tracks and secures access to external data volumes in enterprise deployments.

## How this fits into the broader project flow

1. Run the Unity Catalog setup notebook first from a SQL warehouse or Databricks notebook to ensure the catalog and schemas exist.
2. Once the catalog is in place, the ingestion notebooks (`/notebooks`) and Delta Live Tables pipeline (`/dlt`) can target the `raw`, `ref`, and `mart` schemas without additional manual configuration.
3. BI and analytics consumers (e.g., `/sql/03_gold_queries.sql`) rely on the permissions established here to query materialized views and dashboards securely.
4. Optional monitoring workflows (such as `/monitoring/mlflow_demo.py`) can also reference the same catalog, ensuring observability data stays in the governed Lakehouse environment.

By capturing these steps in Unity Catalog, you establish the consistent, governed foundation that every mature Databricks project requires before ingestion, transformation, and analytics layers are deployed.

