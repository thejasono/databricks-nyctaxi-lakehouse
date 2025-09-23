# NYCTaxi Lakehouse (Auto Loader → DLT → Delta → Unity Catalog → Databricks SQL)

End-to-end lakehouse demo on Databricks:

* **Ingestion:** Auto Loader (optional) into **Bronze** Delta.
* **Transform + Quality:** DLT/Lakeflow to **Silver** and **Gold** with `EXPECT`.
* **Governance:** Unity Catalog (catalog/schemas/grants).
* **Consumption:** Serverless SQL (queries, dashboards, materialized views).
* **Observability:** MLflow metrics.

---

## Repository layout

```
/unity
  00_uc_setup.sql              # Catalog + schemas + grants (one-time platform setup)
/notebooks
  01_auto_loader_bronze.sql    # OPTIONAL: Auto Loader into Bronze from files
/dlt
  pipeline_settings.json       # DLT/Lakeflow pipeline config
  02_dlt_pipeline.sql          # Bronze→Silver→Gold (streaming tables + EXPECT + MVs)
/sql
  03_gold_queries.sql          # Ad-hoc BI queries & helper views
/monitoring
  mlflow_demo.py               # MLflow logging of simple pipeline metrics
README.md                      # This document
```

### What each folder is for

* **/unity** — *Governance setup.* Creates the UC catalog `main_nyctaxi` and schemas `raw`, `ref`, `mart`; applies basic grants so pipelines and SQL can create/read objects.
* **/notebooks** — *Ingestion.* Optional Auto Loader notebook that incrementally ingests files (CSV/Parquet) into a Bronze **streaming table**.
* **/dlt** — *Transform + Data Quality.* DLT/Lakeflow files that define Bronze→Silver→Gold, `EXPECT` rules, and a Gold **materialized view** for BI.
* **/sql** — *Consumption.* Saved queries and small helper views you use from a Serverless SQL warehouse or dashboards.
* **/monitoring** — *Observability.* Small MLflow script to log basic counts/quality metrics after runs.
* **README.md** — *Runbook & orientation.* How to operate the project end-to-end.

---

## Execution surfaces (who runs what)

* **SQL Warehouse:** `/unity/*.sql`, `/sql/*.sql`
* **Interactive Cluster or Job:** `/notebooks/01_auto_loader_bronze.sql` (if you use file ingest)
* **DLT/Lakeflow Pipeline:** `/dlt/02_dlt_pipeline.sql` with `/dlt/pipeline_settings.json`
* **Job/Notebook:** `/monitoring/mlflow_demo.py`

---

## Quick start (minimal happy path)

1. **Create catalog & schemas**
   Open a **SQL Warehouse** and run: `/unity/00_uc_setup.sql`.

2. **Choose ONE Bronze source**

   * **Option A — Samples (lowest friction):**
     *Skip* `/notebooks/01_auto_loader_bronze.sql`. In `/dlt/02_dlt_pipeline.sql`, use the `STREAM(samples.nyctaxi.trips)` variant for `raw.taxi_bronze`.
   * **Option B — Auto Loader from files:**
     Edit and run `/notebooks/01_auto_loader_bronze.sql` to point `cloud_files(...)` at your input location (DBFS mount/S3/ADLS). This creates `main_nyctaxi.raw.taxi_raw`. The DLT Bronze step then reads from that.

3. **Create & run the pipeline**

   * In **Workflows → Pipelines**, create a pipeline.
   * Use `/dlt/02_dlt_pipeline.sql` as the notebook/script.
   * Set **Target** = `main_nyctaxi`.
   * Paste or attach `/dlt/pipeline_settings.json` (update the `"libraries"[0].notebook.path"` to your Repos path).
   * Use **Serverless** (Pro/Serverless required for Gold materialized views).
   * Run in **Triggered** mode (or switch to Continuous later).

4. **Query Gold & build a dashboard**

   * Use a **Serverless SQL Warehouse**.
   * Run `/sql/03_gold_queries.sql` to explore `mart.daily_kpis`.
   * Build a dashboard over `main_nyctaxi.mart.daily_kpis`.

5. **(Optional) Log metrics**

   * Run `/monitoring/mlflow_demo.py` as a Job task to log counts/drops to MLflow.

---

## End-to-end flow

```
Files (S3/ADLS/DBFS) --(Auto Loader)--> raw.taxi_raw (Bronze, Delta)   [OPTIONAL path]
                                        │
                                        ▼
                   DLT: LIVE.raw.taxi_bronze (streaming from raw.taxi_raw OR samples.nyctaxi.trips)
                                        │
                                        ▼
                   DLT: LIVE.ref.trips_clean (typed/pruned)
                                        │  + EXPECT constraints
                                        ▼
                   DLT: LIVE.ref.trips_valid (validated Silver)
                                        │
                                        ▼
                   mart.daily_kpis (Gold MATERIALIZED VIEW for BI)
                                        │
                                        ▼
                   SQL queries / Dashboards / MLflow metrics
```

**Key idea:** pick one Bronze source (Samples **or** Auto Loader). Everything downstream stays the same.

---

## File responsibilities (at a glance)

* **/unity/00\_uc\_setup.sql**
  Creates `main_nyctaxi` and `raw/ref/mart` with basic grants. Run once per workspace or when reprovisioning.

* **/notebooks/01\_auto\_loader\_bronze.sql** *(optional)*
  Uses `cloud_files(...)` to incrementally ingest files to `main_nyctaxi.raw.taxi_raw` (Bronze). Edit the input path before running.

* **/dlt/pipeline\_settings.json**
  Pipeline configuration (edition, channel, serverless, storage, target). Update the `"libraries".[0].notebook.path"` to your actual Repos path.

* **/dlt/02\_dlt\_pipeline.sql**
  Declares **STREAMING TABLES** for Bronze/Silver, applies `EXPECT` rules, and defines **Gold** `mart.daily_kpis` as a **materialized view**.

* **/sql/03\_gold\_queries.sql**
  Quick BI/QA queries (time series, top expensive short rides) to validate the Gold layer and drive a dashboard.

* **/monitoring/mlflow\_demo.py**
  Logs `silver_rows` (and optionally drop counts) to an MLflow experiment for simple health tracking across runs.

---

## Paths & storage (notes)

* **If using a Unity Catalog Volume** you created (e.g., `raw.nyctaxi_landing`), the canonical path is:

  * Spark/DBUtils: `/Volumes/main_nyctaxi/raw/nyctaxi_landing/...`
  * Databricks CLI: `dbfs:/Volumes/main_nyctaxi/raw/nyctaxi_landing/...`
* **If using `cloud_files(...)`** with a DBFS mount or external storage, update the path in `/notebooks/01_auto_loader_bronze.sql` accordingly.

---

## Common commands

**Upload a local file to a UC volume (Windows PowerShell example):**

```powershell
databricks fs cp "C:\path\to\file.parquet" "dbfs:/Volumes/main_nyctaxi/raw/nyctaxi_landing/file.parquet"
databricks fs ls "dbfs:/Volumes/main_nyctaxi/raw/nyctaxi_landing"
```

**Create an external table over a volume (optional sanity check):**

```sql
USE CATALOG main_nyctaxi; USE SCHEMA raw;
CREATE TABLE IF NOT EXISTS taxi_ext USING PARQUET
LOCATION '/Volumes/main_nyctaxi/raw/nyctaxi_landing/';
SELECT COUNT(*) FROM taxi_ext;
```

---

## Data quality (EXPECT)

`EXPECT` rules in DLT drop or warn on bad rows (e.g., `fare_amount >= 0`, `vendor_id IS NOT NULL`). Review the **Data quality** tab in the pipeline UI to confirm counts of passed/dropped rows and tweak rules as needed.

---

## Dashboards (BI)

* Use **Serverless** SQL.
* Primary dataset: `main_nyctaxi.mart.daily_kpis`.
* Start with a line chart of `trip_count` and `avg_fare` by `pickup_date`, plus filters (date range, `vendor_id`).

---

## Observability

Run `/monitoring/mlflow_demo.py` after a pipeline run to log:

* `silver_rows` — row count in `ref.trips_valid`.
* (Optional) dropped row counts from the pipeline event log, if you materialize it.

---

## Troubleshooting

* **“Both paths provided are local” when copying files:** ensure the destination starts with `dbfs:/...`.
* **Materialized view not supported:** use a **Pro/Serverless** SQL warehouse (or run the MV inside the pipeline). Otherwise, convert the Gold object to a standard table/view.
* **Permission errors (create/read):** re-run `/unity/00_uc_setup.sql` and verify grants to your principal (e.g., `account users`).
* **No Bronze data:** confirm you picked exactly one Bronze source (Samples *or* Auto Loader) and that the chosen path/table exists.

---

## Test checklist

* **Incrementality:** Add one new input file; verify only new rows appear (no reprocessing).
* **Schema evolution:** Add a new column; confirm it flows through with `schemaEvolutionMode='addNewColumns'` (if using Auto Loader).
* **DQ behavior:** Insert a row with `fare_amount < 0`; confirm it’s dropped in `ref.trips_valid`.
* **Gold refresh:** After a small update, check `mart.daily_kpis` on Serverless to confirm refresh.

---

## Glossary

* **Bronze / Silver / Gold:** Raw ingest → cleaned/typed → BI-ready aggregates.
* **DLT/Lakeflow:** Declarative pipeline engine for incremental tables, quality rules, lineage, retries.
* **Unity Catalog:** Governance layer (catalogs, schemas, tables, volumes, permissions).
* **Serverless SQL Warehouse:** Managed compute for low-latency SQL, supports materialized views.
* **MLflow:** Tracking runs/metrics for models or pipelines.

---

### Notes for reviewers

* Keep **one** Bronze source active at a time.
* Update `pipeline_settings.json` path to your actual Repos path.
* Use **Serverless** for the Gold MV and dashboards.
