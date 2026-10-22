-- Baseline: how far off is "same hour last week"?


SELECT
    ts_utc,                         -- the timestamp
    price,                         -- the real price
    price_lag_168h,                         -- the guess
    price - price_lag_168h AS error_168h      -- real minus guess
FROM energy_lakehouse.gold.price_features_hourly
WHERE ts_utc >= '2025-09-30 22:00:00'                  -- only the test period
ORDER BY ts_utc
LIMIT 5;


-- Baseline MAE on the test period

SELECT
    ROUND(AVG(ABS(price - price_lag_168h)), 2) AS mae_lag_168h,
    ROUND(AVG(ABS(price - price_lag_24h)), 2) AS mae_lag_24h
FROM energy_lakehouse.gold.price_features_hourly
WHERE ts_utc >= '2025-09-30 22:00:00'                  -- only the test period
