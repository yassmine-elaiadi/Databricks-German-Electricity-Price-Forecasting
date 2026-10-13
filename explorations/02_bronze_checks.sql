-- Overview per series: rows, nulls, first and last hour (UTC)

SELECT
  filter_id,
  COUNT(*)                                   AS rows,
  COUNT_IF(value IS NULL)                    AS nulls,
  timestamp_millis(MIN(ts_ms))               AS first_hour_utc,
  timestamp_millis(MAX(ts_ms))               AS last_hour_utc
FROM energy_lakehouse.bronze.smard_raw
GROUP BY filter_id
ORDER BY filter_id;


-- Missing values per series and day (German time)


SELECT
  filter_id,
  to_date(from_utc_timestamp(timestamp_millis(ts_ms), 'Europe/Berlin')) AS day_german,
  COUNT(*) AS null_hours
FROM energy_lakehouse.bronze.smard_raw
WHERE value IS NULL
GROUP BY filter_id, day_german
ORDER BY filter_id, day_german;