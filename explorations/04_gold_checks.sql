--How many rows, and which time range?

SELECT 
    COUNT(*) AS n_rows,
    MIN(ts_utc) AS first_hour,
    MAX(ts_utc) AS last_hour,
    timestampdiff(HOUR, first_hour,last_hour ) + 1  as expected_rows

FROM energy_lakehouse.gold.price_features_hourly;


---How many NULLs does each column have?

SELECT
   COUNT_IF(price IS NULL) AS price_nulls,
    COUNT_IF(price_lag_24h IS NULL) AS price_lag_24h_nulls,
    COUNT_IF(price_lag_48h IS NULL) AS price_lag_48h_nulls,
    COUNT_IF(price_lag_168h IS NULL) AS price_lag_168h_nulls,
    COUNT_IF(load_lag_48h IS NULL) AS load_lag_nulls,
    COUNT_IF(wind_onshore_lag_48h IS NULL) AS wind_onshore_lag_nulls,
    COUNT_IF(wind_offshore_lag_48h IS NULL) AS wind_offshore_lag_nulls,
    COUNT_IF(solar_lag_48h IS NULL) AS solar_lag_nulls
FROM energy_lakehouse.gold.price_features_hourly
