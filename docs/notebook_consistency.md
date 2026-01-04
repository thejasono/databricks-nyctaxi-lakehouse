# Notebook Consistency Review

## Scope
- `notebooks/01_copy_into_bronze.sql.ipynb`
- `dlt/02_dlt_pipeline.sql.ipynb`

## Findings
- Both notebooks operate in the governed catalog `main_nyctaxi` and the `raw` schema, so the landing zone referenced in Notebook 02 matches the table created in Notebook 01.
- Notebook 01 defines `main_nyctaxi.raw.taxi_raw` as the batch ingestion table loaded via `COPY INTO`, and Notebook 02 reuses that table as the Bronze source when option (A) is selected.
- Notebook 02 also offers an alternative sample-based Bronze source (option B), but it is clearly marked as a mutually exclusive choice and does not conflict with the batch ingestion path.
- No contradictory statements were identified; the notebooks describe complementary steps in the ingestion → batch SQL pipeline lifecycle.

## Recommendation
No changes required for alignment between Notebook 01 and Notebook 02.

## How to run Notebook 02
- The `dlt/02_dlt_pipeline.sql.ipynb` file is authored as a SQL notebook that
  rebuilds the Bronze, Silver, and Gold tables in batch mode. Open it in a SQL
  Warehouse or on an all-purpose cluster and run the cells sequentially to
  refresh every layer.
- Because each statement uses `CREATE OR REPLACE TABLE`, rerunning the notebook
  is idempotent and keeps downstream tables synchronized with the latest Bronze
  load.
- To operationalize the workflow, add the notebook (or the exported
  `02_dlt_pipeline_sql_version.sql`) as a task in a Databricks Job immediately
  after the ingestion notebook so refreshes remain automated on the Free
  Edition.
