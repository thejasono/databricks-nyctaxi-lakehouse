%python
import os
import mlflow
from pyspark.sql import functions as F
from datetime import datetime

PIPELINE_EVENT_LOG_TABLE = os.environ.get("PIPELINE_EVENT_LOG_TABLE", "pipelines.NYCTaxi-Lakeflow")

mlflow.set_registry_uri("databricks")
mlflow.set_experiment("/Shared/nyctaxi-pipeline")

with mlflow.start_run(run_name="dlt_kpis"):
    df = spark.table("main_nyctaxi.ref.trips_valid")
    
    # Log row count
    row_count = df.count()
    mlflow.log_metric("silver_rows", row_count)
    print(f"Logged silver_rows: {row_count}")
    
    # Log average fare
    avg_fare = df.agg(F.avg("fare_amount")).first()[0]
    mlflow.log_metric("avg_fare_amount", avg_fare)
    print(f"Logged avg_fare_amount: {avg_fare}")
    
    # Log null count for pickup_zip
    null_pickup_zip = df.filter(F.col("pickup_zip").isNull()).count()
    mlflow.log_metric("null_pickup_zip", null_pickup_zip)
    print(f"Logged null_pickup_zip: {null_pickup_zip}")
    
    # Log data-quality drop metrics from the pipeline event log
    dq_drop_events = (
        spark.read.table(PIPELINE_EVENT_LOG_TABLE)
        .filter(
            (F.col("event_type") == "data_quality")
            & (F.col("details.data_quality.action") == "drop")
        )
    )
    dq_dropped_rows = (
        dq_drop_events.agg(
            F.sum("details.data_quality.dropped_records").alias("total_dropped_rows")
        ).first()[0]
        or 0
    )
    mlflow.log_metric("dq_dropped_rows", dq_dropped_rows)
    print(f"Logged dq_dropped_rows: {dq_dropped_rows}")

    if row_count > 0:
        dq_drop_rate = dq_dropped_rows / row_count
        mlflow.log_metric("dq_drop_rate", dq_drop_rate)
        print(f"Logged dq_drop_rate: {dq_drop_rate}")
    
    # Log pipeline context parameters
    mlflow.log_param("pipeline_name", "NYCTaxi-Lakeflow")
    mlflow.log_param("pipeline_event_log_table", PIPELINE_EVENT_LOG_TABLE)
    mlflow.log_param("run_date", datetime.now().isoformat())
    
    # Log a sample artifact
    sample_path = "/tmp/trips_valid_sample.csv"
    df.limit(10).toPandas().to_csv(sample_path, index=False)
    mlflow.log_artifact(sample_path)
    print("Logged a sample of the data as an artifact.")
    
    print("View this run in the MLflow UI under /Shared/nyctaxi-pipeline.")
