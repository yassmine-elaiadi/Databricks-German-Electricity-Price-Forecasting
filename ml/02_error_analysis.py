from databricks.connect import DatabricksSession
import pandas as pd
import mlflow
from sklearn.metrics import mean_absolute_error



SOURCE_TABLE = "energy_lakehouse.gold.price_features_hourly"
CUTOFF = "2025-09-30 22:00:00"              # 1 Oct 2025 00:00 Berlin = first test hour (UTC)
TARGET = "price"
FEATURES = [
    "hour", "day_of_week", "month", "is_weekend",
    "price_lag_24h", "price_lag_48h", "price_lag_168h",
    "load_lag_48h", "wind_onshore_lag_48h", "wind_offshore_lag_48h", "solar_lag_48h",
    ]

MODEL_URI = "models:/energy_lakehouse.gold.price_forecaster@champion"

spark = DatabricksSession.builder.serverless().getOrCreate()
mlflow.set_tracking_uri("databricks://elaiadi_personal")
mlflow.set_registry_uri("databricks-uc://elaiadi_personal")

df = spark.table(SOURCE_TABLE).toPandas()

mask = df["ts_utc"] < CUTOFF
test = df[~mask].copy()

X_test  = test[FEATURES]
y_test  = test[TARGET]


#############################################################################

model = mlflow.sklearn.load_model(MODEL_URI)

pred = model.predict(X_test)
mae = mean_absolute_error(y_test, pred)  
print(f"HGB MAE: {mae:.2f}")

#############################################################################

# --- Step 2: errors as columns ---------------------------------------------
test["pred"] = pred                                      # model's guess per hour
test["error"] = (test[TARGET] - test["pred"]).abs()      # |real - guess|

#print(test[["ts_berlin", TARGET, "pred", "error"]].head())   # first 5 rows
#print(f"Mean error: {test['error'].mean():.2f}")             # must be 27.01 again
#############################################################################

#print("Error by hour:", test.groupby("hour")["error"].mean().round(2))
#print("Error by day_of_week:", test.groupby("day_of_week")["error"].mean().round(2))
#print("Error by month:", test.groupby("month")["error"].mean().round(2))
test["date"] = test["ts_berlin"].dt.date
worst_days = test.groupby("date")["error"].mean().sort_values(ascending=False).head(10)
#print("10 worst days:\n", worst_days)

#############################################################################
day = test[test["date"] == pd.to_datetime("2025-11-25").date()]
print(day.sort_values("ts_utc")[["hour", TARGET, "pred", "error", "price_lag_24h"]].round(1).to_string())