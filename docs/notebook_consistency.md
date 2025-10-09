# Notebook Consistency Review

## Scope
- `notebooks/01_auto_loader_bronze.sql.ipynb`
- `dlt/02_dlt_pipeline.sql.ipynb`

## Findings
- Both notebooks operate in the governed catalog `main_nyctaxi` and the `raw` schema, so the landing zone referenced in Notebook 02 matches the table created in Notebook 01.
- Notebook 01 defines `main_nyctaxi.raw.taxi_raw` as the streaming ingestion table via Auto Loader, and Notebook 02 reuses that table as the Bronze source when option (A) is selected.
- Notebook 02 also offers an alternative sample-based Bronze source (option B), but it is clearly marked as a mutually exclusive choice and does not conflict with the Auto Loader path.
- No contradictory statements were identified; the notebooks describe complementary steps in the ingestion → DLT pipeline lifecycle.

## Recommendation
No changes required for alignment between Notebook 01 and Notebook 02.

## How to run Notebook 02
- The `dlt/02_dlt_pipeline.sql.ipynb` file is authored as a Delta Live Tables
  pipeline script. You can open it interactively to review or test individual
  cells, but the intended execution path is to create a Delta Live Tables
  pipeline in the Databricks Jobs & Pipelines UI (or via the REST API/CLI) and
  attach this notebook as the pipeline notebook.
- Running the notebook directly from a SQL warehouse or the notebook editor
  will only execute the statements once. When the notebook is registered as the
  pipeline task, Delta Live Tables manages the continuous/triggered runs,
  handles dependency resolution, and enforces expectations automatically.
