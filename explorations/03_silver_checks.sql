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