SELECT

    COUNT(*) as n_rows,
    MIN(ts_utc) as first_hour,
    MAX(ts_utc) as last_hour,
    timestampdiff(HOUR, first_hour,last_hour ) + 1  as expected_rows
FROM energy_lakehouse.silver.smard_hourly



-- Find holes: hours where the previous row is more than 1 hour earlier
SELECT
    prev_hour,
    ts_utc,
    timestampdiff(HOUR, prev_hour, ts_utc) - 1 AS missing_hours
FROM (
    SELECT
        ts_utc,
        LAG(ts_utc) OVER (ORDER BY ts_utc) AS prev_hour
    FROM energy_lakehouse.silver.smard_hourly
)
WHERE timestampdiff(HOUR, prev_hour, ts_utc) > 1


-- Count the NULLs per column


SELECT
    COUNT_IF(price IS NULL) AS price_nulls,
    COUNT_IF(load IS NULL) AS load_nulls,
    COUNT_IF(wind_onshore IS NULL) AS wind_onshore_nulls,
    COUNT_IF(wind_offshore IS NULL) AS wind_offshore_nulls,
    COUNT_IF(solar IS NULL) AS solar_nulls
FROM energy_lakehouse.silver.smard_hourly

--Find where the NULLs are 
-- What are the first and last hours where load is NULL?


SELECT 
    MIN(ts_utc) as first_null,
    MAX(ts_utc) as last_null,
    COUNT(*) as n_rows
FROM energy_lakehouse.silver.smard_hourly
WHERE load IS NULL