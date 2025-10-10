# Databricks notebook source
"""Utility notebook to reset the NYCTaxi Delta Live Tables pipeline before enabling Unity Catalog."""

# COMMAND ----------
# Clean up the legacy objects that live in catalogs that may hold pipeline state.
# The script now works whether the classic Hive Metastore is enabled or the
# workspace only uses Unity Catalog.  It attempts to clean both catalogs and
# skips any that are unavailable.

# COMMAND ----------
from pyspark.sql.utils import AnalysisException


def _clean_catalog(catalog: str) -> None:
    """Drop the Delta Live Tables artifacts inside ``catalog`` if it exists."""

    try:
        spark.sql(f"USE CATALOG {catalog}")
    except AnalysisException as exc:  # pragma: no cover - executed in Databricks
        message = getattr(exc, "desc", str(exc))
        if "UC_HIVE_METASTORE_DISABLED_EXCEPTION" in message or "Catalog does not exist" in message:
            print(f"Skipping catalog '{catalog}' because it is not available: {message}")
            return
        raise

    print(f"Cleaning catalog '{catalog}'...")

    print("Existing tables in raw/ref/mart before cleanup (if any):")
    spark.sql("SHOW TABLES IN raw").show(truncate=False)
    spark.sql("SHOW TABLES IN ref").show(truncate=False)
    spark.sql("SHOW TABLES IN mart").show(truncate=False)

    spark.sql("DROP TABLE IF EXISTS raw.taxi_bronze")
    spark.sql("DROP TABLE IF EXISTS ref.trips_clean")
    spark.sql("DROP TABLE IF EXISTS ref.trips_valid")
    spark.sql("DROP MATERIALIZED VIEW IF EXISTS mart.daily_kpis")

    spark.sql("DROP TABLE IF EXISTS raw.taxi_raw")
    spark.sql("DROP TABLE IF EXISTS raw.trips_sample")

    print("Remaining tables in raw/ref/mart after cleanup:")
    spark.sql("SHOW TABLES IN raw").show(truncate=False)
    spark.sql("SHOW TABLES IN ref").show(truncate=False)
    spark.sql("SHOW TABLES IN mart").show(truncate=False)


for catalog_name in ["hive_metastore", "main_nyctaxi"]:
    _clean_catalog(catalog_name)

# COMMAND ----------
# Clean up the Delta Live Tables storage path that preserves pipeline metadata.
# Change the path if you configured a different storage location.
dbutils.fs.rm("dbfs:/pipelines/nyctaxi", recurse=True)

# COMMAND ----------
# MAGIC -- The pipeline is now ready to be recreated with Unity Catalog enabled.
# MAGIC -- After the first successful run you can validate the new assets with:
# MAGIC -- DESCRIBE HISTORY main_nyctaxi.ref.trips_clean;
