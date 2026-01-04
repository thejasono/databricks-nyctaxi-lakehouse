-- Databricks notebook source
CREATE VOLUME IF NOT EXISTS main_nyctaxi.raw.nyctaxi_landing_staged;

-- COMMAND ----------

-- MAGIC %python
-- MAGIC # Read Parquet files and align schema
-- MAGIC df = (
-- MAGIC   spark.read.parquet('/Volumes/main_nyctaxi/raw/nyctaxi_landing/')
-- MAGIC )
-- MAGIC
-- MAGIC # Cast datetime columns to match the Delta table schema
-- MAGIC df_aligned = (
-- MAGIC   df.withColumn('tpep_pickup_datetime', df['tpep_pickup_datetime'].cast('timestamp'))
-- MAGIC     .withColumn('tpep_dropoff_datetime', df['tpep_dropoff_datetime'].cast('timestamp'))
-- MAGIC )
-- MAGIC
-- MAGIC # Write to a staging location in Parquet format
-- MAGIC df_aligned.write.mode('overwrite').parquet('/Volumes/main_nyctaxi/raw/nyctaxi_landing_staged/')
-- MAGIC display(df_aligned)

-- COMMAND ----------

USE CATALOG main_nyctaxi;
USE SCHEMA raw;

CREATE TABLE IF NOT EXISTS taxi_raw
LIKE samples.nyctaxi.trips;

INSERT OVERWRITE taxi_raw SELECT * FROM samples.nyctaxi.trips;

COPY INTO taxi_raw
  FROM '/Volumes/main_nyctaxi/raw/nyctaxi_landing_staged/'
  FILEFORMAT = PARQUET
  FORMAT_OPTIONS ('mergeSchema' = 'true')
  COPY_OPTIONS  ('mergeSchema' = 'true');