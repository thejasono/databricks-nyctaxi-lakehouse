# Databricks Project Checklist

Use this checklist as a repeatable guide for building end-to-end Databricks data engineering projects. It follows the medallion architecture and highlights the key Databricks features to configure at each stage. Copy it into new projects and check each item as you go.

---

## 0. Workspace Setup

- [ ] Identify or provision a **Unity Catalog metastore**.
- [ ] Create the target **catalog** (for example, `project_catalog`) and **schema** (for example, `bronze_silver_gold`).
- [ ] Assign the necessary permissions to your user, group, or service principal.
- [ ] Confirm you have access to an interactive cluster or enable **Serverless SQL** for ad hoc queries.

---

## 1. Ingestion Layer — Bronze

- [ ] **Configure storage access**
  - Create a Unity Catalog **Volume** or register an **external location** that points at the raw files.
  - Grant the ingestion cluster or SQL warehouse permission to read from that storage path.
- [ ] **Define Bronze table**
  - Create a managed Delta table with `CREATE TABLE IF NOT EXISTS bronze_<entity> LIKE samples.<reference_table>;`.
  - Use `COPY INTO bronze_<entity> FROM '/Volumes/<catalog>/<schema>/<volume>/' FILEFORMAT = PARQUET;` for batch ingestion.
- [ ] **Reset / reload strategy**
  - Use `COPY_OPTIONS ('force'='true')` or `TRUNCATE TABLE bronze_<entity>;` before a rerun when you need a full refresh.
- [ ] **Validate ingestion**
  - Run `DESCRIBE HISTORY bronze_<entity>;` to confirm writes.
  - Check row counts and min/max timestamps to ensure the landing data matches expectations.

---

## 2. Cleansing & Transformation — Silver

- [ ] **Create Silver table**
  - `CREATE OR REPLACE TABLE silver_<entity> AS SELECT ... FROM bronze_<entity> WHERE quality_filters;`
- [ ] Apply deduplication, joins, and column renaming as required.
- [ ] Handle nulls explicitly with `WHERE` clauses so bad rows do not flow downstream.
- [ ] Manage schema evolution with `ALTER TABLE` statements when new upstream fields arrive.

---

## 3. Aggregation & Business Logic — Gold

- [ ] **Create Gold Delta tables** for aggregations, dimensional models, or KPIs.
  ```sql
  CREATE OR REPLACE TABLE gold_sales_summary AS
  SELECT region, SUM(amount) AS total_sales
  FROM silver_sales
  GROUP BY region;
  ```
- [ ] Document refresh cadence (for example, nightly batch) so consumers know when data changes.
- [ ] Register Gold tables in Unity Catalog for downstream BI tools and Databricks SQL dashboards.

---

## 4. Pipeline Orchestration — Jobs & Tasks

- [ ] Create a **Databricks Job** that chains the ingestion notebook and transformation SQL.
- [ ] Configure the job to run on an all-purpose cluster or SQL warehouse with catalog access.
- [ ] Set a schedule (manual, cron, or continuous trigger) that aligns to your freshness goals.
- [ ] Capture run outputs (row counts, audit logs) for troubleshooting.

---

## 5. Compute & Performance

- [ ] Use **Serverless** or **Job Compute** to reduce cluster management overhead.
- [ ] Enable **Photon** for faster Delta query execution where available.
- [ ] Optimize Delta tables on a schedule:
  - `OPTIMIZE table_name ZORDER BY (column);`
  - `VACUUM table_name RETAIN 168 HOURS;` (weekly cleanup).

---

## 6. Data Governance & Lineage

- [ ] Confirm the **Unity Catalog lineage** graph captures flows from Bronze → Silver → Gold.
- [ ] Tag assets with owners, business context, and descriptions.
- [ ] Verify access controls and audit logs.

---

## 7. BI & Consumption

- [ ] Publish Gold tables through **Databricks SQL Warehouses**.
- [ ] Connect Power BI, Tableau, or other BI tools to the catalog.
- [ ] Build dashboards and schedule refreshes.

---

## 8. Validation & Monitoring

- [ ] Encode data quality rules with SQL `WHERE` filters or post-load validation queries.
- [ ] Track job metrics in **MLflow** or by writing results to monitoring tables.
- [ ] Configure alerts for failed jobs, missing data, or anomalous row counts.

---

## 9. Documentation & Versioning

- [ ] Document each layer (Bronze, Silver, Gold) and their schemas.
- [ ] Store notebooks and pipelines in Git (enable **Repo Sync** in Databricks).
- [ ] Maintain a pipeline README with dataset sources, quality expectations, refresh cadence, and ownership.

---

## 10. Optional Enhancements

- [ ] Add **MLflow model training** or feature engineering using Gold tables.
- [ ] Introduce **Auto Loader** / **Delta Live Tables** once you upgrade to a paid tier that supports streaming features.
- [ ] Promote assets across environments (dev/staging/prod) using workspace folders or CI/CD workflows.

---

Keep this checklist nearby when kicking off new workstreams to ensure each project hits the critical Databricks milestones.
