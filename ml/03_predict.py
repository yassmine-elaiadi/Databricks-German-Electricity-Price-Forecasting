import inspect
import os
import sys

THIS_FILE = os.path.abspath(inspect.currentframe().f_code.co_filename)   # works on laptop AND as a job (no __file__ there)
sys.path.append(os.path.dirname(os.path.dirname(THIS_FILE)))             # repo root

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from pyspark.sql import functions as F

from features.feature_logic import FEATURES, build_features
import mlflow
from mlflow import MlflowClient
from common.env import get_spark, setup_mlflow

SILVER_TABLE = "energy_lakehouse.silver.smard_hourly"
MODEL_NAME = "energy_lakehouse.gold.price_forecaster"
MODEL_URI = f"models:/{MODEL_NAME}@champion"
OUTPUT_TABLE = "energy_lakehouse.gold.price_predictions"
BERLIN = ZoneInfo("Europe/Berlin")

spark = get_spark()                                  # laptop or Databricks, decided by common/env.py


# --- 1. Tomorrow's hours (D+1) in UTC -----------------------------------------
today = datetime.now(BERLIN).date()
tomorrow = today + timedelta(days=1)                 # D+1
day_after = tomorrow + timedelta(days=1)             # D+2

start = datetime(tomorrow.year, tomorrow.month, tomorrow.day, tzinfo=BERLIN).astimezone(timezone.utc)
end   = datetime(day_after.year, day_after.month, day_after.day, tzinfo=BERLIN).astimezone(timezone.utc)

hours = []
t = start
while t < end:                                       # "<": end already belongs to D+2
    hours.append(t)
    t = t + timedelta(hours=1)

future = spark.createDataFrame([(t,) for t in hours], "ts_utc timestamp")
future = future.withColumn("ts_berlin", F.from_utc_timestamp("ts_utc", "Europe/Berlin"))

# --- 2. Silver + tomorrow's rows -> features ----------------------------------
silver = spark.table(SILVER_TABLE).filter(F.col("ts_utc") < start)   # only hours before D+1
df = silver.unionByName(future, allowMissingColumns=True)              # D+1 rows: price etc. = NULL

df = build_features(df)                                              # SAME logic as Gold
pred_rows = df.filter(F.col("ts_utc") >= start)                      # keep only D+1



# --- Guards: fail loudly instead of predicting with wrong clues ----------------
last_hour = start - timedelta(hours=1)                       # D 23:00 Berlin, in UTC
if silver.filter(F.col("ts_utc") == F.lit(last_hour)).count() != 1:
    raise ValueError(f"Silver doesn't reach {last_hour} UTC -> gap before D+1, lags would shift")

n = pred_rows.count()
if n != len(hours):
    raise ValueError(f"Expected {len(hours)} rows for D+1, got {n}")

null_counts = pred_rows.select(
    [F.sum(F.col(c).isNull().cast("int")).alias(c) for c in FEATURES]
).collect()[0].asDict()
missing = {c: k for c, k in null_counts.items() if k > 0}
if missing:
    raise ValueError(f"NULL features for D+1: {missing}")    # e.g. solar not published yet






# --- 3. Predict with @champion -------------------------------------------------
setup_mlflow()                                       # laptop profile or job login

pdf = pred_rows.select(["ts_utc", "ts_berlin"] + FEATURES).toPandas()   # 24 rows -> pandas
model = mlflow.sklearn.load_model(MODEL_URI)
pdf["pred"] = model.predict(pdf[FEATURES])

# --- 4. Write with MERGE (re-run = overwrite, never duplicate) -----------------
version = MlflowClient().get_model_version_by_alias(MODEL_NAME, "champion").version   # e.g. "1"

out = spark.createDataFrame(pdf[["ts_utc", "ts_berlin", "pred"]])
out = out.withColumn("model_version", F.lit(int(version)))
out = out.withColumn("created_at", F.current_timestamp())

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {OUTPUT_TABLE} (
        ts_utc TIMESTAMP, ts_berlin TIMESTAMP, pred DOUBLE,
        model_version INT, created_at TIMESTAMP
    )
""")

out.createOrReplaceTempView("new_preds")
spark.sql(f"""
    MERGE INTO {OUTPUT_TABLE} AS t
    USING new_preds AS s
    ON t.ts_utc = s.ts_utc
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""")


