# NYCTaxi Lakehouse (Free Edition Batch SQL)

This repository delivers an end-to-end lakehouse walkthrough that fits entirely inside the Databricks **Community (Free) Edition**. Every asset assumes you only have access to the baseline batch toolset (all-purpose clusters, SQL Warehouses, Unity Catalog, MLflow) so you can practice the medallion architecture without paid features. The demo intentionally avoids premium services such as Auto Loader in SQL, Delta Live Tables expectations, or materialized views while still showing how a governed lakehouse operates.

The high-level flow mirrors a production deployment even within the Free Edition limits:

* **Ingestion:** A batch `COPY INTO` notebook seeds the Bronze landing table from a Unity Catalog Volume or the built-in Databricks sample dataset.
* **Transformation & Quality:** Plain SQL scripts recreate the Silver and Gold Delta tables with explicit `WHERE` filters and assertions—no managed pipeline frameworks required.
* **Governance:** Unity Catalog catalogs, schemas, volumes, and grants keep every table and experiment in a single controlled namespace.
* **Consumption:** Databricks SQL Warehouses query the curated Gold layer for dashboards, ad-hoc analysis, and validation.
* **Observability:** A lightweight MLflow script logs row counts, null ratios, and freshness metrics immediately after each batch run.

---

## Repository layout

```
/unity
  00_main_nyctaxi_catalogue_creator.ipynb  # Catalog + schemas + grants (one-time platform setup)
/notebooks
  01_copy_into_bronze.sql.ipynb          # Batch COPY INTO Bronze from files or samples
/dlt
  02_dlt_pipeline.sql.ipynb                # Bronze→Silver→Gold batch tables (no managed pipeline dependencies)
  02_dlt_pipeline_sql_version.sql          # Plain SQL export of the same batch logic
  pipeline_settings.json                   # Optional template if you later upgrade to managed pipeline services
/sql
  03_gold_queries.sql                      # Ad-hoc BI queries & helper views
/monitoring
  mlflow_demo.py                           # MLflow logging of simple pipeline metrics
README.md                                  # This document
```

### What each folder is for

* **/unity** — *Governance setup.* Creates the Unity Catalog catalog `main_nyctaxi` and schemas `raw`, `ref`, `mart`; applies basic grants so jobs and SQL Warehouses can create/read objects.
* **/notebooks** — *Ingestion.* Batch notebook that issues `COPY INTO` against a governed landing path to backfill or refresh the Bronze table.
* **/dlt** — *Transform + Data Quality.* Despite the legacy folder name, the assets inside are plain SQL notebooks and scripts that rebuild the medallion layers on Databricks Community (Free) Edition compute. The JSON settings remain for teams that later graduate to paid tiers.
* **/sql** — *Consumption.* Saved queries and helper views you run from a SQL Warehouse to validate or visualize the Gold layer.
* **/monitoring** — *Observability.* Small MLflow script to log counts/quality metrics after the batch transformations complete.
* **README.md** — *Runbook & orientation.* How to operate the project end-to-end on the Free Edition.

### Recommended walkthrough order

1. Start in **`/unity/README.md`** to provision the catalog, schemas, and grants that every downstream asset expects.
2. Move to **`/notebooks/README.md`** to configure and run the Bronze ingestion once the governance layer exists.
3. Review **`/dlt/README.md`** to understand how the batch medallion SQL recreates the Silver and Gold tables.
4. Dive into **`/monitoring/README.md`** so you know how to track metrics and health after you load the curated tables.
5. Finish in **`/sql/README.md`** to see how analysts consume the Gold layer once the engineering pieces are in place.

### Databricks concepts you will practice

* **Workspace organization:** Import this repo into Databricks Repos so notebooks, SQL files, and scripts stay versioned together.
* **Unity Catalog governance:** Build catalogs, schemas, tables, and permissions that isolate domains and enable fine-grained access.
* **Batch ingestion with COPY INTO:** Land raw files in governed Volumes or external locations and load them into Delta tables using only batch operations.
* **Medallion modeling with SQL:** Recreate Bronze, Silver, and Gold Delta tables via repeatable SQL scripts.
* **Serverless SQL consumption:** Query Delta tables, publish dashboards, and materialize BI datasets with managed compute.
* **Observability & MLflow:** Capture operational metrics, build health dashboards, and reason about data quality impacts.
* **Workflows & Jobs:** Chain ingestion, transformation, and monitoring assets into an automated schedule to mimic production operations.

---

## Execution surfaces (who runs what)

| Asset | Typical compute surface |
| --- | --- |
| `/unity/*.sql` | SQL Warehouse or all-purpose cluster |
| `/notebooks/01_copy_into_bronze.sql.ipynb` | Interactive (all-purpose) cluster or Jobs task |
| `/dlt/02_dlt_pipeline.sql.ipynb` and `.sql` export | SQL Warehouse or all-purpose cluster |
| `/sql/*.sql` | SQL Warehouse |
| `/monitoring/mlflow_demo.py` | Notebook or Jobs task on an all-purpose cluster |

---

## Quick start

### Code validation checklist

Before chaining the assets into a production-style workflow, run these quick checks to confirm everything compiles in your workspace:

1. **Open each notebook** – Import `/unity/00_main_nyctaxi_catalogue_creator.ipynb`, `/notebooks/01_copy_into_bronze.sql.ipynb`, and `/dlt/02_dlt_pipeline.sql.ipynb` into Databricks Repos. Use the **Format** button, then run **Run All** in a scratch workspace to surface syntax issues early.
2. **Verify landing storage** – Upload a few taxi Parquet files (or plan to rely on the sample dataset) and confirm `LIST '/Volumes/main_nyctaxi/raw/nyctaxi_landing/'` succeeds from a cluster.
3. **Compile SQL artifacts** – Open `/sql/03_gold_queries.sql` in a SQL Warehouse, prepend `USE CATALOG main_nyctaxi;`, and run the statements to validate schema references.
4. **Check monitoring dependencies** – Run `python monitoring/mlflow_demo.py --dry-run` (or execute the script from a Databricks notebook) to ensure `mlflow` is available and the logging flow works.
5. **Confirm Unity permissions** – After running the governance notebook, execute `DESCRIBE CATALOG EXTENDED main_nyctaxi;` and `SHOW GRANTS ON CATALOG main_nyctaxi;` to verify catalog, schema, and grant setup.

### Run sequence (minimal happy path)

Once the validation checklist passes, follow this sequence to run the full demo:

1. **Create catalog & schemas** – In a SQL Warehouse, run `/unity/00_main_nyctaxi_catalogue_creator.ipynb` end to end.
2. **Load Bronze data (batch)** – Configure the landing path inside `/notebooks/01_copy_into_bronze.sql.ipynb`, run the notebook to execute `COPY INTO`, and optionally seed with the provided sample insert.
3. **Build Silver and Gold tables** – Execute `/dlt/02_dlt_pipeline.sql.ipynb` (or the `.sql` export) to recreate `raw.taxi_bronze`, `ref.trips_clean`, `ref.trips_valid`, and `mart.daily_kpis`. Re-run after each Bronze refresh.
4. **Query Gold & build a dashboard** – From a SQL Warehouse, run `/sql/03_gold_queries.sql` to explore `mart.daily_kpis` and derive dashboard-ready visuals.
5. **(Optional) Log metrics** – Trigger `/monitoring/mlflow_demo.py` as a Jobs task or notebook to capture row counts and quality signals in MLflow.

> **Upgrading later?** The SQL patterns here mirror what you would run in paid tiers. When you adopt premium ingestion services or declarative pipelines, swap them in incrementally without rewriting downstream consumption assets.

---

## End-to-end flow

```
Files (Volume/External) --(COPY INTO)--> raw.taxi_raw (Bronze landing table)
                                      │
                                      ▼
Batch SQL: raw.taxi_bronze  (Bronze cleanup, optional sample seed)
                                      │
                                      ▼
Batch SQL: ref.trips_clean   (typed/pruned Silver)
                                      │  + WHERE-based quality filters
                                      ▼
Batch SQL: ref.trips_valid   (validated Silver)
                                      │
                                      ▼
Batch SQL: mart.daily_kpis   (Gold Delta table for BI)
                                      │
                                      ▼
SQL queries / Dashboards / MLflow metrics
```

**Key idea:** The medallion layers remain the same even within the baseline batch toolset—rerun the SQL after new files arrive.

---

## File responsibilities (at a glance)

* **/unity/00_main_nyctaxi_catalogue_creator.ipynb**
  Creates `main_nyctaxi` and `raw/ref/mart` with basic grants. Run once per workspace or when reprovisioning.

* **/notebooks/01_copy_into_bronze.sql.ipynb**
  Issues `COPY INTO` (and optional sample inserts) to populate `main_nyctaxi.raw.taxi_raw` on demand.

* **/dlt/02_dlt_pipeline.sql.ipynb**
  Rebuilds the medallion tables with standard SQL. The `.sql` export provides the same logic for Jobs or git-driven deployments.

* **/dlt/pipeline_settings.json**
  Template configuration for teams that may eventually adopt managed pipeline services—safe to ignore on Free Edition.

* **/sql/03_gold_queries.sql**
  Quick BI/QA queries (time series, top expensive short rides) to validate the Gold layer and drive a dashboard.

* **/monitoring/mlflow_demo.py**
  Logs `silver_rows` (and optionally drop counts) to an MLflow experiment for simple health tracking across runs.

---

## Paths & storage (notes)

* **If using a Unity Catalog Volume** you created (e.g., `raw.nyctaxi_landing`), the canonical path is:
  * Spark/DBUtils: `/Volumes/main_nyctaxi/raw/nyctaxi_landing/...`
  * Databricks CLI: `dbfs:/Volumes/main_nyctaxi/raw/nyctaxi_landing/...`
* **If seeding from samples**, leave the landing folder empty and uncomment the sample insert in the ingestion notebook.

---

## Batch data quality (Free Edition pattern)

Without managed expectations frameworks, rely on explicit `WHERE` clauses and assertions in SQL notebooks:

* `ref.trips_clean` removes rows with missing trip distance or fare amounts.
* `ref.trips_valid` filters out null `vendor_id` values and negative fares.
* MLflow logging captures row counts so you can detect anomalies across runs.

Add additional validation rules directly to the SQL as your requirements evolve.

---
