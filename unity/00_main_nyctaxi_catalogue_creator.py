# Databricks notebook source
# MAGIC %sql
# MAGIC -- 00_uc_setup.sql
# MAGIC CREATE CATALOG IF NOT EXISTS main_nyctaxi COMMENT 'NYC Taxi demo';
# MAGIC
# MAGIC USE CATALOG main_nyctaxi;
# MAGIC
# MAGIC CREATE SCHEMA IF NOT EXISTS raw  COMMENT 'Bronze/Raw';
# MAGIC CREATE SCHEMA IF NOT EXISTS ref  COMMENT 'Silver/Refined';
# MAGIC CREATE SCHEMA IF NOT EXISTS mart COMMENT 'Gold/Marts';
# MAGIC
# MAGIC USE SCHEMA raw;
# MAGIC
# MAGIC CREATE VOLUME IF NOT EXISTS nyctaxi_landing
# MAGIC COMMENT 'Landing area for uploaded NYC taxi files';
# MAGIC
# MAGIC -- Optional: verify the volume exists
# MAGIC SHOW VOLUMES IN raw;
# MAGIC