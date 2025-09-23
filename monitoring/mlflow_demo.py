import mlflow
from pyspark.sql import functions as F

# Create/use an experiment in the workspace
mlflow.set_experiment("/Shared/nyctaxi-pipeline")

with mlflow.start_run(run_name="dlt_kpis"):
    df = spark.table("main_nyctaxi.ref.trips_valid")
    mlflow.log_metric("silver_rows", df.count())

    # Example: read pipeline event log (configure your event log table if enabled)
    # See Lakeflow event log docs for schema/availability.
    # drops = spark.table("main_nyctaxi.system.event_log").where("event_type = 'data_quality' and action = 'drop'").count()
    # mlflow.log_metric("dq_dropped_rows", drops)

    mlflow.log_param("pipeline_name", "NYCTaxi-Lakeflow")
