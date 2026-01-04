-- Databricks notebook source
GRANT ALL PRIVILEGES ON SCHEMA main_nyctaxi.raw TO `enter_your_email_address_here`;
-- change the email to your own databricks account email

-- COMMAND ----------

-- Batch medallion pipeline for Databricks Free Edition (no DLT/streaming features).
-- Run these statements from a SQL Warehouse or notebook after Bronze ingestion completes.
-- Each step recreates the downstream Delta tables so rerunning the script keeps them in sync with the latest source files.

USE CATALOG main_nyctaxi;

-- BRONZE ------------------------------------------------------------------
-- Build the Bronze Delta table from the batch-ingested raw landing table.
-- If you skipped the ingestion notebook, you can swap the SELECT to read
-- from samples.nyctaxi.trips for a fully self-contained demo.
CREATE OR REPLACE TABLE raw.taxi_bronze AS
SELECT * FROM raw.taxi_raw;
-- Alternative sample path:
-- CREATE OR REPLACE TABLE raw.taxi_bronze AS SELECT * FROM samples.nyctaxi.trips;

-- SILVER -----------------------------------------------------------------
-- Cast raw strings into strongly typed columns and remove obviously bad rows.
CREATE OR REPLACE TABLE ref.trips_clean AS
SELECT
  CAST(tpep_pickup_datetime  AS TIMESTAMP) AS pickup_ts,
  CAST(tpep_dropoff_datetime AS TIMESTAMP) AS dropoff_ts,
  DATE(CAST(tpep_pickup_datetime AS TIMESTAMP)) AS pickup_date,
  CAST(passenger_count AS INT)    AS passenger_count,
  CAST(trip_distance  AS DOUBLE)  AS trip_distance,
  CAST(fare_amount    AS DOUBLE)  AS fare_amount,
  VendorID,
  pickup_zip,
  dropoff_zip
FROM raw.taxi_bronze
WHERE trip_distance IS NOT NULL
  AND fare_amount IS NOT NULL;

-- Apply data quality checks with standard WHERE clauses so the Free Edition
-- drops bad rows even without DLT expectations.
CREATE OR REPLACE TABLE ref.trips_valid AS
SELECT *
FROM ref.trips_clean
WHERE VendorID IS NOT NULL
  AND fare_amount >= 0;

-- GOLD -------------------------------------------------------------------
-- Produce a Gold Delta table for BI consumption (materialized views are not
-- available in the Free Edition).
CREATE OR REPLACE TABLE mart.daily_kpis AS
SELECT
  pickup_date,
  COUNT(*)                     AS trip_count,
  ROUND(AVG(fare_amount), 2)   AS avg_fare,
  ROUND(AVG(trip_distance), 3) AS avg_trip_miles,
  ROUND(SUM(fare_amount), 2)   AS total_revenue,
  ROUND(SUM(fare_amount) / NULLIF(SUM(trip_distance), 0), 3) AS revenue_per_mile
FROM ref.trips_valid
GROUP BY pickup_date;

SELECT * FROM mart.daily_kpis;

-- COMMAND ----------

-- MAGIC %python
-- MAGIC display(_sqldf)