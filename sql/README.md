# SQL Consumption Guide

This folder packages the SQL workflows that showcase the **Gold** layer of the NYC Taxi Lakehouse demo once the upstream Unity Catalog, ingestion notebook, and Delta Live Tables (DLT) pipeline have finished running. At this stage of the implementation, the curated tables in `main_nyctaxi.mart` (or whatever catalog/schema names you created) are already populated with clean, reliable taxi metrics. The statements here let data analysts and dashboard builders explore those assets directly from a Databricks SQL Warehouse—ideally Serverless for the fastest cold-starts—without needing to manage clusters or write ad-hoc data engineering code.

The Gold layer itself is defined inside the DLT SQL notebook (`/dlt/02_dlt_pipeline.sql.ipynb`). There, the pipeline creates a Delta materialized view that sits on top of the validated Silver table so it can refresh incrementally as new taxi trips land:

```sql
-- GOLD: BI aggregates as MVs (eligible on Pro/Serverless SQL or inside the pipeline).
-- Gold tables summarize Silver data for business intelligence. Here we build
-- a materialized view so DLT (or Databricks SQL) maintains the aggregation incrementally
-- each time new trips arrive. Materialized views persist their results in Delta storage
-- refresh automatically, and expose history/time travel like any Delta table—
-- they are more than a one-time snapshot.
-- `LIVE.ref.trips_valid` keeps dependency tracking intact so the pipeline refresh order
-- and lineage graphs show Bronze → Silver → Gold relationships.
CREATE OR REPLACE MATERIALIZED VIEW mart.daily_kpis AS
SELECT
  pickup_date,
  COUNT(*)                           AS trip_count,
  ROUND(AVG(fare_amount), 2)         AS avg_fare,
  ROUND(AVG(trip_distance), 3)       AS avg_trip_miles,
  ROUND(SUM(fare_amount), 2)         AS total_revenue,
  ROUND(SUM(fare_amount) / NULLIF(SUM(trip_distance), 0), 3) AS revenue_per_mile
FROM LIVE.ref.trips_valid
GROUP BY pickup_date;
```

When that DLT pipeline run completes, you can switch to Databricks SQL and execute the curated queries in this folder to consume the same Gold layer objects that power the demo dashboards.

Because the tables remain Delta-backed, every query benefits from the same **ACID guarantees**, **schema enforcement**, and **time travel** features that protected data quality through the Bronze → Silver → Gold medallion journey. The SQL assets simply surface those curated results through business-friendly aggregations and drill-downs so you can convert them into dashboards, alerts, or downstream data sharing products.

## Files in this folder

### `03_gold_queries.sql`
* **Purpose:** A collection of reusable SQL statements that highlight common business questions on top of the Gold layer—daily KPI rollups, revenue leaders, trip outliers, and validation queries that confirm pipeline health.
* **When to use it:** Run these statements from Databricks SQL after the DLT pipeline has produced `main_nyctaxi.mart.daily_kpis` and other curated tables. They form the backbone of the demo dashboard or any BI exploration you present to stakeholders.
* **Inputs to configure:**
  * Catalog and schema names that match your Unity Catalog deployment (defaults assume `main_nyctaxi.mart`).
  * Optional dashboard parameters (date ranges, vendor filters) if you wire the statements into visualizations.

Key snippets inside the notebook illustrate both the ad-hoc consumption pattern and deeper validation workflows. For example:

```sql
%sql
-- Ad-hoc queries against GOLD.
USE CATALOG main_nyctaxi;
USE SCHEMA mart;

-- Time series for dashboarding.
SELECT pickup_date, trip_count, avg_fare, avg_trip_miles, total_revenue, revenue_per_mile
FROM daily_kpis
ORDER BY pickup_date;

-- QA: most expensive sub-5 mile trips.
SELECT pickup_date, vendor_id, trip_distance, fare_amount, pickup_zip, dropoff_zip
FROM main_nyctaxi.ref.trips_valid
WHERE trip_distance < 5 AND fare_amount > 50
ORDER BY fare_amount DESC
LIMIT 50;
```

These commands reinforce the practice of setting the correct catalog/schema, querying the Gold materialized view for BI-friendly KPIs, and then diving back to Silver tables when deeper anomaly investigations are required.

## How the SQL workflow plays out end to end

1. **Select the right compute:** Launch a Databricks SQL Warehouse (Serverless or a governed cluster) with access to the Unity Catalog catalog where the Gold tables live.
2. **Establish context:** Run `USE CATALOG main_nyctaxi;` and `USE SCHEMA mart;` (or their equivalents) so every subsequent query hits the curated objects published by DLT.
3. **Explore KPIs first:** Execute the daily metrics query to confirm the pipeline populated `daily_kpis`. Validate row counts, min/max dates, and revenue totals to build confidence in freshness.
4. **Drill into business slices:** Leverage the top trips, geography breakdowns, or vendor-level aggregations in the file to tell a story about ridership patterns. These statements are designed to power dashboard tiles or ad-hoc analysis.
5. **Validate quality contracts:** Use the included sanity checks (null counts, negative fares, schema inspection) to demonstrate how downstream consumers can monitor quality even after data leaves DLT.
6. **Publish visuals:** Save the most compelling queries as dashboard widgets, alerts, or Databricks Explorer assets so business users can consume the Gold layer without touching SQL.

Throughout this flow, remember that the Gold tables are **materialized views** created by DLT. They refresh incrementally as new Bronze data arrives, so every time you rerun the SQL you should see up-to-date metrics without reprocessing raw files.

## Databricks concepts reinforced here

* **SQL Warehouses** as the serverless compute endpoint for BI workloads with auto-scaling and governed data access.
* **Unity Catalog governance** for row-level permissions, lineage tracking, and consistent catalog/schema/table naming conventions (`catalog.schema.table`).
* **Delta tables and materialized views** that retain time travel and optimization features even when consumed from pure SQL.
* **Dashboards and alerts** that operationalize curated tables for stakeholders without exposing engineering complexity.

## How SQL consumption fits the overall Lakehouse journey

1. **Foundation in Unity Catalog:** `/unity/00_main_nyctaxi_catalogue_creator.ipynb` creates the governed namespaces and external locations.
2. **Bronze ingestion:** `/notebooks/01_auto_loader_bronze.sql.ipynb` (or an equivalent job) streams raw taxi files into `main_nyctaxi.raw`.
3. **Silver and Gold transformation:** `/dlt/02_dlt_pipeline.sql.ipynb` materializes the refined `ref` and `mart` layers with expectations and incremental refresh.
4. **SQL consumption (this folder):** Use `03_gold_queries.sql` to analyze `mart.daily_kpis` and companion tables, turning them into dashboards, alerts, or Delta Sharing feeds.
5. **Feedback loop:** Insights or quality issues discovered here inform updates to expectations, transformations, or ingestion logic upstream.

## Operational tips

* **Parameterize for demos:** Add widget parameters or SQL variables (for example, `{{dashboard.start_date}}`) when embedding the queries into dashboards so presenters can filter by date, borough, or vendor on the fly.
* **Leverage query history:** Monitor execution costs and performance in the SQL Warehouse history view; adjust compute size or apply `OPTIMIZE` and `VACUUM` commands (via engineering teams) if hotspots appear.
* **Secure sharing:** When publishing dashboards or Delta Sharing tables, ensure workspace access mode and Unity Catalog permissions mirror the governance story you want to demonstrate.
* **Schedule refreshes:** If you pin dashboards for stakeholders, schedule alerts or e-mail snapshots aligned with the DLT pipeline cadence so consumers always see fresh numbers.

## Additional context you might find useful

* **Naming consistency accelerates automation.** Stick with the same catalog and schema conventions (`main_nyctaxi.mart`) referenced throughout the repo so SQL snippets plug into pipelines, dashboards, and Lakehouse Monitoring notebooks without edits.
* **Time travel aids audits.** Use `SELECT * FROM mart.daily_kpis VERSION AS OF ...` to demonstrate how historical comparisons or regulatory audits can be satisfied instantly.
* **Integration-ready outputs.** Gold tables are ready for downstream tools—connect them to Databricks Partner Connect BI integrations (Tableau, Power BI, ThoughtSpot) or expose them through Delta Sharing for external partners once governance approves.
* **Iterate collaboratively.** Encourage analysts to fork `03_gold_queries.sql`, commit enhancements, and raise pull requests so business logic stays version-controlled alongside the rest of the Lakehouse assets.

By executing the SQL assets in this directory, you close the loop on the Lakehouse lifecycle—turning governed, reliable Delta tables into insights, visualizations, and data products that stakeholders can trust.
