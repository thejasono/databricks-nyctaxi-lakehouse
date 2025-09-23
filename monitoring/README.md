# NYCTaxi Lakehouse (Auto Loader → DLT → Delta → UC → Databricks SQL)

## Prereqs
- Unity Catalog-enabled workspace; Pro/Serverless SQL warehouse for MVs.
- Repo imported into Databricks **Repos**.

## Setup
1. Run `/unity/00_uc_setup.sql` in a SQL warehouse.
2. If using file ingest, put data under `dbfs:/mnt/nyctaxi/input` (or S3/ADLS) and run `/notebooks/01_auto_loader_bronze.sql`.
3. Create a **Pipeline** with `dlt/pipeline_settings.json` and notebook `dlt/02_dlt_pipeline.sql`. Target: `main_nyctaxi`.

## Runbook
- Trigger the pipeline (Triggered mode). Inspect DQ tab for expectation metrics.
- Query `mart.daily_kpis` from your Serverless/Pro SQL warehouse; build a dashboard.

## Costs/SLA
- Serverless warehouse for MVs; pipeline storage at `dbfs:/pipelines/nyctaxi`.
