# SQL Consumption Guide

The SQL assets in this directory show how to consume the curated Gold layer that the Delta Live Tables pipeline produces. Run them from a Databricks SQL Warehouse (Serverless recommended) after the Unity Catalog and pipeline steps finish.

## Files in this folder

### `03_gold_queries.sql`
* **Purpose:** Provides a starting set of BI queries (KPI rollups, top trips, data validation) that analysts can run or turn into dashboard tiles.
* **How to use it:**
  * Open the file in Databricks SQL or the notebook editor and execute each statement against the `main_nyctaxi` catalog.
  * Swap `main_nyctaxi` with the catalog/schema names you created in `/unity` if you rebranded the deployment.
  * Use the query snippets as building blocks for dashboards, alerts, or data sharing products.

## How SQL consumption fits the project

1. **Governance first:** Ensure `/unity/00_main_nyctaxi_catalogue_creator.ipynb` has provisioned the catalog and schemas.
2. **Ingest and transform:** Run the Auto Loader notebook (optional) and the DLT pipeline (`/dlt/02_dlt_pipeline.sql.ipynb`) to populate the Gold materialized views.
3. **Query and visualize:** Use this SQL file to explore `mart.daily_kpis`, create visualizations, and share insights.
4. **Iterate:** Extend the queries with additional aggregations, joins to external reference data, or data sharing (Delta Sharing) endpoints to round out your Databricks analytics story.

By practicing with these SQL assets you complete the Lakehouse loop—governed data ingestion, reliable transformations, observability, and analytical consumption.
