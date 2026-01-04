# SQL Consumption Guide

## Overview

This folder packages the SQL workflows that showcase the Gold layer of the NYC Taxi Lakehouse demo once governance, ingestion, and batch transformations have finished running. At this point the curated tables in `main_nyctaxi.mart` (or your renamed catalog/schema) are populated with clean, reliable taxi metrics. Analysts run the statements from a Databricks SQL Warehouse—Serverless if available—to explore the data, validate quality, and build dashboards. Everything here works on Databricks Community (Free) Edition.

The Gold layer itself is materialized inside `/dlt/02_dlt_pipeline.sql.ipynb` (and the `.sql` export). When that pipeline completes, the following SQL definition exists:

```sql
CREATE OR REPLACE TABLE mart.daily_kpis AS
SELECT
  pickup_date,
  COUNT(*)                           AS trip_count,
  ROUND(AVG(fare_amount), 2)         AS avg_fare,
  ROUND(AVG(trip_distance), 3)       AS avg_trip_miles,
  ROUND(SUM(fare_amount), 2)         AS total_revenue,
  ROUND(SUM(fare_amount) / NULLIF(SUM(trip_distance), 0), 3) AS revenue_per_mile
FROM ref.trips_valid
GROUP BY pickup_date;
```

Because the table is Delta-backed, every query benefits from ACID guarantees, schema enforcement, and time travel.

## File in this folder

### `03_gold_queries.sql`
* **Purpose** – A collection of reusable SQL statements that highlight business questions on top of the Gold layer—daily KPI rollups, revenue leaders, trip outliers, and validation checks.
* **When to run** – After the batch pipeline has produced `main_nyctaxi.mart.daily_kpis` and companion tables. The statements form the backbone of demo dashboards or ad-hoc exploration sessions.
* **Inputs to adjust** – Update catalog and schema names to match your Unity Catalog deployment, and optionally parameterize date ranges or vendor filters when embedding in dashboards.

Example snippets illustrate both ad-hoc consumption and validation workflows:

```sql
%sql
-- Set context
USE CATALOG main_nyctaxi;
USE SCHEMA mart;

-- Dashboard-ready metrics
SELECT pickup_date, trip_count, avg_fare, avg_trip_miles, total_revenue, revenue_per_mile
FROM daily_kpis
ORDER BY pickup_date;

-- QA: most expensive sub-5 mile trips
SELECT pickup_date, vendor_id, trip_distance, fare_amount, pickup_zip, dropoff_zip
FROM main_nyctaxi.ref.trips_valid
WHERE trip_distance < 5 AND fare_amount > 50
ORDER BY fare_amount DESC
LIMIT 50;
```

## Databricks concepts reinforced

* **SQL Warehouses** as the managed compute endpoint for BI workloads with auto-scaling and governed access.
* **Unity Catalog governance** that keeps catalog/schema/table naming consistent across ingestion, transformation, and consumption layers.
* **Delta tables** that retain time travel and optimization benefits even when queried solely from SQL.
* **Dashboards and alerts** that turn curated tables into stakeholder-facing insights without exposing engineering complexity.

## Where this step fits in the project

1. **Governance** – `/unity/README.md` provisions the catalog and schemas.
2. **Bronze ingestion** – `/notebooks/README.md` loads `main_nyctaxi.raw.taxi_raw`.
3. **Silver & Gold transformation** – `/dlt/README.md` recreates the curated tables.
4. **SQL consumption (this folder)** – Run `03_gold_queries.sql` to analyze `mart.daily_kpis` and supporting tables.
5. **Feedback loop** – Insights or anomalies discovered here inform upstream filters, transformations, or monitoring rules.

## Operational tips

* Parameterize dashboard widgets or SQL variables (for example, `{{dashboard.start_date}}`) when embedding the queries into dashboards so presenters can filter by date, borough, or vendor.
* Monitor execution history in the SQL Warehouse UI; adjust cluster size or ask engineering teams to run `OPTIMIZE`/`VACUUM` on the tables if hotspots appear.
* Ensure Unity Catalog permissions align with the audiences who will view dashboards or Delta Sharing tables.
* Schedule SQL alerts or dashboard refreshes to match the cadence of the batch pipeline so consumers see fresh metrics.

## Next steps

Once analysts are comfortable with the Gold queries, leverage `/monitoring/README.md` to capture row counts and freshness metrics that protect downstream consumers.
