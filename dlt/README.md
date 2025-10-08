# Delta Live Tables Pipeline Guide

The assets in this directory define the streaming transformation layer that turns Bronze ingestion into curated Silver and Gold datasets. Use them to configure a Delta Live Tables (DLT) pipeline or Lakeflow project that automates quality checks, incremental processing, and downstream serving tables for the NYC Taxi demo.

## Files in this folder

### `02_dlt_pipeline.sql.ipynb`
* **Purpose:** Implements the DLT pipeline logic using SQL expectations and table definitions for the `raw`, `ref`, and `mart` schemas.
* **What it builds:**
  * Bronze streaming table sourced from the ingestion notebook output.
  * Silver table (`trips_valid`) with data quality rules applied.
  * Gold materialized view(s) that aggregate daily KPIs for analytics consumers.
* **How to run it:** Attach the notebook to a DLT pipeline (Workflows → Pipelines) or Lakeflow project, choose a cluster policy/serverless mode, and point the storage location to your workspace path.

### `pipeline_settings.json`
* **Purpose:** Provides a template for the pipeline configuration, including continuous mode, target catalog, storage, and libraries.
* **How to use it:** Copy the JSON when creating the pipeline, updating the `library` path to match your repo workspace location and customizing the storage/base paths for your environment.

## Where DLT fits in the overall flow

1. **Unity Catalog foundation:** Run the setup in `/unity` to create the catalog and schemas that the pipeline references.
2. **Feed Bronze data:** Execute the notebooks in `/notebooks` (Auto Loader or sample ingestion) so the Bronze Delta table exists.
3. **Deploy the pipeline:** Create or update the DLT pipeline using the SQL notebook and settings here, ensuring the target is `main_nyctaxi` (or your chosen catalog).
4. **Serve downstream consumers:** The Gold outputs power the SQL queries in `/sql` and any dashboards or BI tools you layer on top.
5. **Monitor and iterate:** After each run, use `/monitoring/mlflow_demo.py` or Lakehouse Monitoring to confirm row counts, data quality, and refresh cadences.

With these DLT assets, you operationalize the transformation layer of the Lakehouse, enforcing quality expectations and delivering trusted data products for analytics and reporting.
