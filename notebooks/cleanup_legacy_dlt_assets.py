# Databricks notebook source
"""Utility notebook to reset the NYCTaxi Delta Live Tables pipeline before enabling Unity Catalog."""

# COMMAND ----------
# MAGIC -- Clean up the legacy objects that live in hive_metastore
# MAGIC USE CATALOG hive_metastore;
# MAGIC 
# MAGIC -- Optional: inspect the existing tables to understand what will be dropped
# MAGIC SHOW TABLES IN raw;
# MAGIC SHOW TABLES IN ref;
# MAGIC SHOW TABLES IN mart;

# COMMAND ----------
# MAGIC -- Drop the managed tables and views left by the earlier pipeline runs
# MAGIC DROP TABLE IF EXISTS raw.taxi_bronze;
# MAGIC DROP TABLE IF EXISTS ref.trips_clean;
# MAGIC DROP TABLE IF EXISTS ref.trips_valid;
# MAGIC DROP MATERIALIZED VIEW IF EXISTS mart.daily_kpis;

# COMMAND ----------
# MAGIC -- Remove any ad hoc raw tables that may reference the same storage
# MAGIC DROP TABLE IF EXISTS raw.taxi_raw;
# MAGIC DROP TABLE IF EXISTS raw.trips_sample;

# COMMAND ----------
# MAGIC -- Confirm that the schemas no longer contain pipeline artifacts
# MAGIC SHOW TABLES IN raw;
# MAGIC SHOW TABLES IN ref;
# MAGIC SHOW TABLES IN mart;

# COMMAND ----------
# Clean up the Delta Live Tables storage path that preserves pipeline metadata.
# Change the path if you configured a different storage location.
dbutils.fs.rm("dbfs:/pipelines/nyctaxi", recurse=True)

# COMMAND ----------
# MAGIC -- The pipeline is now ready to be recreated with Unity Catalog enabled.
# MAGIC -- After the first successful run you can validate the new assets with:
# MAGIC -- DESCRIBE HISTORY main_nyctaxi.ref.trips_clean;
