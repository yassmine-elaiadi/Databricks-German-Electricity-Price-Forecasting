"""Gold: Silver -> 11 features per hour (shared logic in features/feature_logic.py)."""
import inspect
import os
import sys

THIS_FILE = os.path.abspath(inspect.currentframe().f_code.co_filename)   # works on laptop AND as a job
sys.path.append(os.path.dirname(os.path.dirname(THIS_FILE)))             # repo root

from features.feature_logic import FEATURES, build_features
from common.env import get_spark

SOURCE_TABLE = "energy_lakehouse.silver.smard_hourly"
OUTPUT_TABLE = "energy_lakehouse.gold.price_features_hourly"

spark = get_spark()

df = spark.table(SOURCE_TABLE)                            # Silver
df = build_features(df)                                   # + 11 features (shared logic)
df = df.select(["ts_utc", "ts_berlin", "price"] + FEATURES)
df = df.dropna(subset=FEATURES)                           # drops the first 168 h (+ tail if any)

df.write.mode("overwrite").saveAsTable(OUTPUT_TABLE)