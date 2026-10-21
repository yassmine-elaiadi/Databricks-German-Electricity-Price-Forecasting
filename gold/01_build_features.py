from databricks.connect import DatabricksSession
from pyspark.sql import functions as F
from pyspark.sql import Window             


spark = DatabricksSession.builder.serverless().getOrCreate()
SOURCE_TABLE = "energy_lakehouse.silver.smard_hourly"
OUTPUT_TABLE = "energy_lakehouse.gold.price_features_hourly"

df = spark.table(SOURCE_TABLE)
df.printSchema()
df.orderBy("ts_utc").show(5)

df = df.withColumn("hour", F.hour(F.col("ts_berlin")))





