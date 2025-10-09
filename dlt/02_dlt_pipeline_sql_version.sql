-- Databricks Delta Live Tables pipeline: Bronze → Silver → Gold
-- This SQL file is attached to the pipeline configuration and defines
-- the full lineage graph. Each `CREATE OR REFRESH ... LIVE TABLE` block
-- materializes a managed table inside the Unity Catalog catalog declared
-- in `pipeline_settings.json` (set `"catalog": "main_nyctaxi"`). The
-- statements below specify schemas (`raw`, `ref`, `mart`) explicitly so
-- each medallion layer lands in the expected namespace while still letting
-- DLT infer lineage via the `LIVE.<schema>.<table>` references.
--
-- BRONZE ------------------------------------------------------------------
-- Option A: Auto Loader ingested `main_nyctaxi.raw.taxi_raw` (see 01_auto_loader_bronze).
--          Uncomment the statement below if that table exists.
--
-- CREATE OR REFRESH STREAMING LIVE TABLE main_nyctaxi.raw.taxi_bronze
-- AS SELECT * FROM STREAM(main_nyctaxi.raw.taxi_raw);
--
-- Leave the statement below uncommented if you want to build from the
-- shared sample dataset that Databricks hosts.
CREATE OR REFRESH STREAMING LIVE TABLE raw.taxi_bronze
COMMENT 'Raw taxi trips landing zone populated from the Databricks sample dataset.'
AS SELECT * FROM STREAM(samples.nyctaxi.trips);

-- SILVER -----------------------------------------------------------------
-- Cast raw string columns into strongly typed fields and filter out
-- clearly invalid records. The `LIVE` prefix ensures DLT reads the
-- managed Bronze table that this pipeline owns.
CREATE OR REFRESH STREAMING LIVE TABLE ref.trips_clean
COMMENT 'Curated taxi trips with typed columns and basic quality pruning.'
AS
SELECT
  CAST(tpep_pickup_datetime  AS TIMESTAMP) AS pickup_ts,
  CAST(tpep_dropoff_datetime AS TIMESTAMP) AS dropoff_ts,
  DATE(CAST(tpep_pickup_datetime AS TIMESTAMP)) AS pickup_date,
  CAST(passenger_count AS INT)    AS passenger_count,
  CAST(trip_distance  AS DOUBLE)  AS trip_distance,
  CAST(fare_amount    AS DOUBLE)  AS fare_amount,
  vendor_id,
  pickup_zip,
  dropoff_zip
FROM LIVE.raw.taxi_bronze
WHERE trip_distance IS NOT NULL AND fare_amount IS NOT NULL;

-- Apply data-quality expectations in a separate streaming layer.
CREATE OR REFRESH STREAMING LIVE TABLE ref.trips_valid
(
  CONSTRAINT vendor_not_null EXPECT (vendor_id IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT nonnegative_fare EXPECT (fare_amount >= 0)     ON VIOLATION DROP ROW
)
COMMENT 'Validated taxi trips with declarative expectations enforced.'
AS
SELECT * FROM LIVE.ref.trips_clean;

-- GOLD -------------------------------------------------------------------
-- Summarize Silver data for BI consumption. LIVE TABLE objects in this
-- layer become managed Delta tables (or materialized views when
-- configured with expectations) within the configured catalog/schema.
CREATE OR REFRESH LIVE TABLE mart.daily_kpis
COMMENT 'Daily KPIs derived from validated taxi trips.'
AS
SELECT
  pickup_date,
  COUNT(*)                     AS trip_count,
  ROUND(AVG(fare_amount), 2)   AS avg_fare,
  ROUND(AVG(trip_distance), 3) AS avg_trip_miles,
  ROUND(SUM(fare_amount), 2)   AS total_revenue,
  ROUND(SUM(fare_amount) / NULLIF(SUM(trip_distance), 0), 3) AS revenue_per_mile
FROM LIVE.ref.trips_valid
GROUP BY pickup_date;
