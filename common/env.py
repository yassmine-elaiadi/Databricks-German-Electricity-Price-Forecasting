import os

PROFILE = "elaiadi_personal"      # my laptop login (only used locally)


def on_databricks():
    """True when the code runs on Databricks (job / notebook), False on my laptop."""
    return "DATABRICKS_RUNTIME_VERSION" in os.environ


def get_spark():
    if on_databricks():
        from pyspark.sql import SparkSession                  # Spark already runs there
        return SparkSession.builder.getOrCreate()
    from databricks.connect import DatabricksSession          # laptop -> remote control
    return DatabricksSession.builder.serverless().getOrCreate()


def setup_mlflow():
    import mlflow
    if on_databricks():
        mlflow.set_tracking_uri("databricks")                 # job is already logged in
        mlflow.set_registry_uri("databricks-uc")
    else:
        mlflow.set_tracking_uri(f"databricks://{PROFILE}")    # laptop profile
        mlflow.set_registry_uri(f"databricks-uc://{PROFILE}")