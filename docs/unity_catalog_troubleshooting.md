# Unity Catalog Migration Troubleshooting

## Symptom
Delta Live Tables pipeline fails during deployment with the error:

```
PERMISSION_DENIED: Can not move tables across arclight catalogs
```

## Diagnosis
The SQL in `dlt/02_dlt_pipeline.sql.ipynb` and `dlt/02_dlt_pipeline_sql_version.sql` now fully qualifies every table with the `main_nyctaxi` catalog (for example `CREATE OR REFRESH STREAMING TABLE main_nyctaxi.raw.taxi_bronze`). When the pipeline previously ran without Unity Catalog configured, it created the managed tables in the default `hive_metastore` catalog.

As soon as the pipeline is redeployed with the catalog property set to `main_nyctaxi` in `dlt/pipeline_settings.json`, Delta Live Tables attempts to update the pipeline state so the managed tables live inside the new catalog. Internally this is treated as a metadata move from `hive_metastore.<schema>.<table>` to `main_nyctaxi.<schema>.<table>`. Unity Catalog forbids cross-catalog moves, which surfaces as the `PERMISSION_DENIED` error before the pipeline is even able to start its first task.

## Resolution
Because Unity Catalog cannot move existing Delta Live Tables assets between catalogs, the pipeline (and the managed tables it created) must be reset before enabling the catalog:

1. **Clean up the old managed tables** – In Databricks SQL or a notebook, drop the previous pipeline tables and views in the old catalog (for example `DROP TABLE IF EXISTS hive_metastore.raw.taxi_bronze;`, `DROP TABLE IF EXISTS hive_metastore.ref.trips_clean;`, etc.). To run the end-to-end SQL reset workflow (including dropping Unity Catalog objects and clearing storage paths), open [`notebooks/hard_reset_automation.sql`](../notebooks/hard_reset_automation.sql) and execute each cell in order after updating the parameters.
2. **Reset or recreate the pipeline** – Either delete and recreate the pipeline in the UI or run it with a new pipeline ID/storage path so it does not reuse the metadata stored for the original run.
3. **Re-run after cleanup** – Once the old tables are gone, the Unity Catalog-qualified statements can create fresh managed objects directly in `main_nyctaxi`, and the deployment will succeed.

If dropping the old tables is not possible, create a brand-new pipeline that writes to a different `storage` location and produces uniquely named tables inside the `main_nyctaxi` catalog. This avoids the prohibited cross-catalog move while preserving the historical objects.

### SQL cleanup checklist

Run the statements below in a Databricks SQL warehouse (or from the linked notebook) **before** re-enabling Unity Catalog on the pipeline. They ensure no managed objects remain in `hive_metastore` that would trigger the cross-catalog migration.

```sql
-- Work in the legacy catalog that still holds the managed tables
USE CATALOG hive_metastore;

-- Inspect what the old pipeline left behind
SHOW TABLES IN raw;
SHOW TABLES IN ref;
SHOW TABLES IN mart;

-- Drop Bronze/Silver managed tables and materialized views created by the pipeline
DROP TABLE IF EXISTS raw.taxi_bronze;
DROP TABLE IF EXISTS ref.trips_clean;
DROP TABLE IF EXISTS ref.trips_valid;
DROP MATERIALIZED VIEW IF EXISTS mart.daily_kpis;

-- (Optional) Remove any ad hoc development copies that mirror the pipeline objects
DROP TABLE IF EXISTS raw.taxi_raw;
DROP TABLE IF EXISTS raw.trips_sample;

-- Confirm the schemas are empty before redeploying
SHOW TABLES IN raw;
SHOW TABLES IN ref;
SHOW TABLES IN mart;
```

In addition to the SQL cleanup, remove the Delta Live Tables storage directory (`dbfs:/pipelines/nyctaxi` by default) or set a brand-new storage path when you recreate the pipeline. This prevents the new deployment from reusing metadata that still references the `hive_metastore` catalog.
