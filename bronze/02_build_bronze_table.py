"""Bronze: read all raw SMARD JSON files and save them as one Delta table."""
import inspect
import os
import sys

THIS_FILE = os.path.abspath(inspect.currentframe().f_code.co_filename)   # works on laptop AND as a job
sys.path.append(os.path.dirname(os.path.dirname(THIS_FILE)))             # repo root

from common.env import get_spark

from pyspark.sql import functions as F

spark = get_spark()
RAW_PATH = "/Volumes/energy_lakehouse/bronze/raw_files/smard/*.json"
TABLE = "energy_lakehouse.bronze.smard_raw"
SCHEMA = "meta_data STRUCT<version: INT, created: BIGINT>, series ARRAY<ARRAY<DOUBLE>>"

# 1. Read all files: one row per file
files = (
    spark.read
    .schema(SCHEMA)
    .option("multiLine", True)
    .json(RAW_PATH)
    .select("series", F.col("_metadata.file_path").alias("source_file"))
)

# 2. Unpack: one row per hour
rows = (
    files
    .select("source_file", F.explode("series").alias("point"))
    .select(
        F.regexp_extract("source_file", r"/(\d+)_DE-LU", 1).cast("int").alias("filter_id"),
        F.col("point")[0].cast("long").alias("ts_ms"),
        F.col("point")[1].alias("value"),
        "source_file",
    )
    .withColumn("ingested_at", F.current_timestamp())
)

# 3. Save as a Delta table
rows.write.mode("overwrite").saveAsTable(TABLE)

# 4. Check
spark.table(TABLE).groupBy("filter_id").count().orderBy("filter_id").show()