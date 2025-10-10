-- Databricks notebook source
-- MAGIC %md
-- MAGIC # NYC Taxi Lakehouse Hard Reset
-- MAGIC 
-- MAGIC Use the SQL commands below to remove pipeline artifacts after you manually stop any related jobs or Delta Live Tables pipelines. Update the parameters in the first cell, then run the remaining cells in order.
-- MAGIC 
-- MAGIC ## Parameters
-- MAGIC * `pipeline_catalog` – Unity Catalog catalog that should own the NYC Taxi objects (for example `main_nyctaxi`).
-- MAGIC * `legacy_catalog` – Catalog that contains the legacy managed tables (typically `hive_metastore`).
-- MAGIC * `storage_path` – DBFS or cloud storage path backing the pipeline (`dbfs:/pipelines/nyctaxi` by default).
-- MAGIC * `volume_name` – Optional fully qualified Unity Catalog volume name that stores pipeline artifacts.

-- COMMAND ----------
-- MAGIC %sql
-- MAGIC -- Update the parameter values to match your workspace.
-- MAGIC SET pipeline_catalog = 'main_nyctaxi';
-- MAGIC SET legacy_catalog = 'hive_metastore';
-- MAGIC SET bronze_schema = 'raw';
-- MAGIC SET silver_schema = 'ref';
-- MAGIC SET gold_schema = 'mart';
-- MAGIC SET storage_path = 'dbfs:/pipelines/nyctaxi';
-- MAGIC SET volume_name = 'main_nyctaxi.workspace.nyctaxi_pipeline_volume';

-- COMMAND ----------
-- MAGIC %sql
-- MAGIC -- Inspect existing tables and views in the legacy catalog before dropping them.
-- MAGIC USE CATALOG ${legacy_catalog};
-- MAGIC SHOW TABLES IN ${bronze_schema};
-- MAGIC SHOW TABLES IN ${silver_schema};
-- MAGIC SHOW TABLES IN ${gold_schema};

-- COMMAND ----------
-- MAGIC %sql
-- MAGIC -- Drop the managed tables and views created by the legacy pipeline runs.
-- MAGIC USE CATALOG ${legacy_catalog};
-- MAGIC DROP TABLE IF EXISTS ${bronze_schema}.taxi_bronze;
-- MAGIC DROP TABLE IF EXISTS ${silver_schema}.trips_clean;
-- MAGIC DROP TABLE IF EXISTS ${silver_schema}.trips_valid;
-- MAGIC DROP MATERIALIZED VIEW IF EXISTS ${gold_schema}.daily_kpis;
-- MAGIC DROP TABLE IF EXISTS ${bronze_schema}.taxi_raw;
-- MAGIC DROP TABLE IF EXISTS ${bronze_schema}.trips_sample;

-- COMMAND ----------
-- MAGIC %sql
-- MAGIC -- Confirm the schemas are empty after cleanup.
-- MAGIC USE CATALOG ${legacy_catalog};
-- MAGIC SHOW TABLES IN ${bronze_schema};
-- MAGIC SHOW TABLES IN ${silver_schema};
-- MAGIC SHOW TABLES IN ${gold_schema};

-- COMMAND ----------
-- MAGIC %sql
-- MAGIC -- Drop Unity Catalog objects associated with the refreshed deployment.
-- MAGIC USE CATALOG ${pipeline_catalog};
-- MAGIC SHOW TABLES IN ${bronze_schema};
-- MAGIC SHOW TABLES IN ${silver_schema};
-- MAGIC SHOW TABLES IN ${gold_schema};
-- MAGIC DROP TABLE IF EXISTS ${bronze_schema}.taxi_bronze;
-- MAGIC DROP TABLE IF EXISTS ${silver_schema}.trips_clean;
-- MAGIC DROP TABLE IF EXISTS ${silver_schema}.trips_valid;
-- MAGIC DROP MATERIALIZED VIEW IF EXISTS ${gold_schema}.daily_kpis;
-- MAGIC DROP TABLE IF EXISTS ${bronze_schema}.taxi_raw;
-- MAGIC DROP TABLE IF EXISTS ${bronze_schema}.trips_sample;

-- COMMAND ----------
-- MAGIC %sql
-- MAGIC -- Drop entire schemas if they should be recreated during the next deployment.
-- MAGIC USE CATALOG ${pipeline_catalog};
-- MAGIC DROP SCHEMA IF EXISTS ${bronze_schema} CASCADE;
-- MAGIC DROP SCHEMA IF EXISTS ${silver_schema} CASCADE;
-- MAGIC DROP SCHEMA IF EXISTS ${gold_schema} CASCADE;

-- COMMAND ----------
-- MAGIC %sql
-- MAGIC -- Optionally drop the Unity Catalog catalog if the pipeline should re-create it.
-- MAGIC DROP CATALOG IF EXISTS ${pipeline_catalog} CASCADE;

-- COMMAND ----------
-- MAGIC %sql
-- MAGIC -- Remove Unity Catalog volume artifacts if the pipeline uses a UC volume for storage.
-- MAGIC DROP VOLUME IF EXISTS ${volume_name};

-- COMMAND ----------
-- MAGIC %sql
-- MAGIC -- Clear the pipeline storage location so the next run starts with a fresh checkpoint directory.
-- MAGIC REMOVE '${storage_path}';
