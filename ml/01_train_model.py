from databricks.connect import DatabricksSession
import pandas as pd
import mlflow
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import HistGradientBoostingRegressor

EXPERIMENT = "/Users/yassminelaiadi@gmail.com/german_electricity_price_forecasting"
SOURCE_TABLE = "energy_lakehouse.gold.price_features_hourly"
CUTOFF = "2025-09-30 22:00:00"              # 1 Oct 2025 00:00 Berlin = first test hour (UTC)
TARGET = "price"
FEATURES = [
    "hour", "day_of_week", "month", "is_weekend",
    "price_lag_24h", "price_lag_48h", "price_lag_168h",
    "load_lag_48h", "wind_onshore_lag_48h", "wind_offshore_lag_48h", "solar_lag_48h",
    ]

spark = DatabricksSession.builder.serverless().getOrCreate()
mlflow.set_tracking_uri("databricks://elaiadi_personal")
mlflow.set_experiment(EXPERIMENT)
df = spark.table(SOURCE_TABLE).toPandas()
#print(df.shape)    #(70440, 14)

mask = df["ts_utc"] < CUTOFF
train = df[mask]
test = df[~mask]

#print(len(train) + len(test))    # expect 70440
#print(len(test))                 # expect 9240
#print(test["ts_utc"].min())      # expect 2025-09-30 22:00:00
#print(train["ts_utc"].max())     # expect 2025-09-30 21:00:00



X_train = train[FEATURES]
y_train = train[TARGET]
X_test  = test[FEATURES]
y_test  = test[TARGET]

#print(X_train.shape, y_train.shape)   # expect (61200, 11) (61200,)

#############################################################################


#print(mae)
# with mlflow.start_run(run_name="linear_regression"):
#     model = LinearRegression()                  # create an empty model
#     model.fit(X_train, y_train)                 # learn from the TRAIN data
#     pred = model.predict(X_test)                # guess prices for the TEST hours
#     mae = mean_absolute_error(y_test, pred)     # compare real vs guess

#     mlflow.log_param("model_type", "LinearRegression")   # which model
#     mlflow.log_param("cutoff", CUTOFF)                   # which test period
#     mlflow.log_metric("mae_test", mae)                   # the score
#     mlflow.sklearn.log_model(model, name="model")        # the trained model

# print(f"MAE: {mae:.2f}")

#############################################################################

with mlflow.start_run(run_name="hist_gradient_boosting"):
    model = HistGradientBoostingRegressor(random_state=42)                  # create an empty model
    model.fit(X_train, y_train)                 # learn from the TRAIN data
    pred = model.predict(X_test)                # guess prices for the TEST hours
    mae = mean_absolute_error(y_test, pred)     # compare real vs guess

    mlflow.log_param("model_type", "HistGradientBoostingRegressor")   # which model
    mlflow.log_param("cutoff", CUTOFF)                   # which test period
    mlflow.log_metric("mae_test", mae)                   # the score
    mlflow.sklearn.log_model(model, name="model")        # the trained model

print(f"HGB MAE: {mae:.2f}")

