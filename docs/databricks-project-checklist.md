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
  - Mount cloud storage (`/mnt/<source>`) or configure **Auto Loader** (`cloudFiles`) with `INFER_SCHEMA = true`.
- [ ] **Define Bronze table**
  - Use `CREATE OR REFRESH STREAMING TABLE bronze_<entity>` or a Delta Live Tables (DLT) pipeline cell.
  - Add `EXPECT` clauses to enforce minimal data quality (for example, `EXPECT country IS NOT NULL ON VIOLATION DROP ROW`).
- [ ] **Checkpointing**
  - Set checkpoint locations within the Delta directory, or rely on DLT to manage them automatically.
- [ ] **Validate ingestion**
  - Run `DESCRIBE HISTORY bronze_<entity>` to confirm writes.
  - Confirm schema inference and record counts meet expectations.

---

## 2. Cleansing & Transformation — Silver

- [ ] **Create Silver streaming table**
  - `CREATE OR REFRESH STREAMING TABLE silver_<entity> AS SELECT ... FROM STREAMING bronze_<entity> WHERE _is_valid;`
- [ ] Apply deduplication, joins, and column renaming as required.
- [ ] Validate business keys and handle nulls explicitly.
- [ ] Add stricter `EXPECT` rules (uniqueness, referential integrity, and so on).
- [ ] Manage schema evolution with `ALTER TABLE` statements when new upstream fields arrive.

---

## 3. Aggregation & Business Logic — Gold

- [ ] **Create materialized or streaming Gold tables** for aggregations, dimensional models, or KPIs.
  ```sql
  CREATE OR REFRESH MATERIALIZED VIEW gold_sales_summary AS
  SELECT region, SUM(amount) AS total_sales
  FROM silver_sales
  GROUP BY region;
  ```
- [ ] Configure incremental refresh policies or triggers as needed.
- [ ] Register Gold tables in Unity Catalog for downstream BI tools and Databricks SQL dashboards.

---

## 4. Pipeline Orchestration — Lakeflow / Delta Live Tables

- [ ] Open the **Lakeflow / DLT** UI and create a pipeline that references your notebooks or SQL definitions.
- [ ] Choose `Triggered` or `Continuous` mode based on freshness requirements.
- [ ] Set the target catalog and schema.
- [ ] Enable **expectations**, **schema evolution**, and **data quality metrics**.
- [ ] Start a run and monitor the event logs.

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

- [ ] Publish Gold tables as **Databricks SQL endpoints** or **materialized views**.
- [ ] Connect Power BI, Tableau, or other BI tools to the catalog.
- [ ] Build dashboards and schedule refreshes.

---

## 8. Validation & Monitoring

- [ ] Integrate **data quality reports** via DLT expectations or tools such as **Great Expectations**.
- [ ] Track job metrics in the **MLflow** or **Lakeflow metrics** tabs.
- [ ] Configure alerts for failed expectations, missing data, or pipeline errors.

---

## 9. Documentation & Versioning

- [ ] Document each layer (Bronze, Silver, Gold) and their schemas.
- [ ] Store notebooks and pipelines in Git (enable **Repo Sync** in Databricks).
- [ ] Maintain a pipeline README with dataset sources, quality expectations, refresh cadence, and ownership.

---

## 10. Optional Enhancements

- [ ] Add **MLflow model training** or feature engineering using Gold tables.
- [ ] Implement **Change Data Capture (CDC)** with Auto Loader incremental reads.
- [ ] Promote assets across environments (dev/staging/prod) using workspace folders or CI/CD workflows.

---

Keep this checklist nearby when kicking off new workstreams to ensure each project hits the critical Databricks milestones.
