import mlflow  # MLflow handles experiment tracking so we can log metrics and parameters for each run.
from pyspark.sql import functions as F  # Spark SQL helper functions available in the Databricks runtime (install pyspark locally if running off-cluster).

# Create/use an experiment in the workspace
mlflow.set_experiment("/Shared/nyctaxi-pipeline")  # Points the run at this experiment path, creating it if it does not already exist.

with mlflow.start_run(run_name="dlt_kpis"):
    df = spark.table("main_nyctaxi.ref.trips_valid")  # Reads the Delta table into a Spark DataFrame so we can compute KPIs.
    mlflow.log_metric("silver_rows", df.count())  # Logs the row count as a numeric MLflow metric for tracking over time.

    # Example: read pipeline event log (configure your event log table if enabled)
    # See Lakeflow event log docs for schema/availability.
    # drops = spark.table("main_nyctaxi.system.event_log").where("event_type = 'data_quality' and action = 'drop'").count()
    # mlflow.log_metric("dq_dropped_rows", drops)

    mlflow.log_param("pipeline_name", "NYCTaxi-Lakeflow")  # Records static run context alongside the metrics for filtering in MLflow UI.
