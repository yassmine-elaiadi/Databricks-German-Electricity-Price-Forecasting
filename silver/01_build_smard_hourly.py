"""Silver: Bronze (long, one row per series and hour) -> one clean row per hour."""
import inspect
import os
import sys

THIS_FILE = os.path.abspath(inspect.currentframe().f_code.co_filename)   # works on laptop AND as a job
sys.path.append(os.path.dirname(os.path.dirname(THIS_FILE)))             # repo root

from pyspark.sql import functions as F
from pyspark.sql import Window

from common.env import get_spark

spark = get_spark()

df = spark.table("energy_lakehouse.bronze.smard_raw")

df = df.withColumn("ts_utc", F.timestamp_millis(F.col("ts_ms")))      # ms → timestamp
df = df.withColumn("ts_berlin", F.from_utc_timestamp(F.col("ts_utc"), "Europe/Berlin"))   # ts_utc → German time

df = df.select("filter_id", "value", "ts_utc", "ts_berlin")

df = df.groupBy("ts_utc", "ts_berlin").pivot("filter_id").agg(F.first("value"))

df = df.withColumnsRenamed({"410": "load", "1225": "wind_offshore", "4067": "wind_onshore", "4068": "solar", "4169": "price"})
df = df.filter(F.col("ts_utc") >= "2018-09-30 22:00:00")
df = df.filter(F.col("price").isNotNull())

# --- Fill single load gaps from the neighbouring hours ---
w = Window.orderBy("ts_utc")

df = df.withColumn("load_prev", F.lag("load", 1).over(w))    # load of the hour before
df = df.withColumn("load_next", F.lead("load", 1).over(w))   # load of the hour after

df = df.withColumn("load", F.coalesce(
    F.col("load"),                                   # plan 1: keep the real value
    (F.col("load_prev") + F.col("load_next")) / 2,   # plan 2: average of the neighbours
    F.col("load_next")                               # plan 3: only the hour after
))

df = df.drop("load_prev", "load_next")

# --- Save as a Delta table ---
df.write.mode("overwrite").saveAsTable("energy_lakehouse.silver.smard_hourly")