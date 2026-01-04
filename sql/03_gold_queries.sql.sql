-- Databricks notebook source
-- Ad-hoc queries against GOLD.
USE CATALOG main_nyctaxi;
USE SCHEMA mart;

-- COMMAND ----------

-- Time series for dashboarding.
SELECT pickup_date, trip_count, avg_fare, avg_trip_miles, total_revenue, revenue_per_mile
FROM daily_kpis
ORDER BY pickup_date;

-- COMMAND ----------

-- QA: most expensive sub-5 mile trips.
SELECT pickup_date, VendorID, trip_distance, fare_amount, pickup_zip, dropoff_zip
FROM main_nyctaxi.ref.trips_valid
WHERE trip_distance < 5 AND fare_amount > 50
ORDER BY fare_amount DESC
LIMIT 50;