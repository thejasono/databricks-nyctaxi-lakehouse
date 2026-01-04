%python
import mlflow
from pyspark.sql import functions as F
from datetime import datetime

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
    
    # Log pipeline context parameters
    mlflow.log_param("pipeline_name", "NYCTaxi-Lakeflow")
    mlflow.log_param("run_date", datetime.now().isoformat())
    
    # Log a sample artifact
    sample_path = "/tmp/trips_valid_sample.csv"
    df.limit(10).toPandas().to_csv(sample_path, index=False)
    mlflow.log_artifact(sample_path)
    print("Logged a sample of the data as an artifact.")
    
    print("View this run in the MLflow UI under /Shared/nyctaxi-pipeline.")