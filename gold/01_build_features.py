import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # repo root

from databricks.connect import DatabricksSession
from features.feature_logic import FEATURES, build_features

SOURCE_TABLE = "energy_lakehouse.silver.smard_hourly"
OUTPUT_TABLE = "energy_lakehouse.gold.price_features_hourly"

spark = DatabricksSession.builder.serverless().getOrCreate()

df = spark.table(SOURCE_TABLE)                            # Silver
df = build_features(df)                                   # + 11 features (shared logic)
df = df.select(["ts_utc", "ts_berlin", "price"] + FEATURES)
df = df.dropna(subset=FEATURES)                           # drops the first 168 h (+ tail if any)

df.write.mode("overwrite").saveAsTable(OUTPUT_TABLE)