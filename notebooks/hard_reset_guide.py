# Databricks notebook source
# MAGIC %md
# MAGIC # Hard Reset Guide
# MAGIC 
# MAGIC Use this notebook to remove lingering artifacts from previous pipeline runs.
# MAGIC 
# COMMAND ----------
# MAGIC %md
# MAGIC ## Reset Steps
# MAGIC 1. Stop all running jobs that depend on the NYC Taxi Lakehouse assets.
# MAGIC 2. Use the Data Explorer UI to delete any managed tables or views that should be recreated.
# MAGIC 3. Drop the associated schemas if they are no longer required.
# MAGIC 4. Remove the workspace objects (catalogs, schemas, and volumes) related to the pipeline.
# MAGIC 5. Clear any remaining files from the configured storage locations (DBFS, external volumes, or cloud storage buckets).
# MAGIC 6. Re-run the setup notebooks to bootstrap the project again.
# MAGIC 
# COMMAND ----------
# MAGIC %md
# MAGIC ## Notes
# MAGIC * This notebook is intentionally lightweight so you can execute the cleanup manually.
# MAGIC * Review each step and adapt the commands to your workspace security model before executing destructive operations.
# MAGIC * Consider taking a backup or snapshot of important data before performing the reset.
