-- Are the predictions stored correctly? (re-run the script -> count must NOT grow)
SELECT
    COUNT(*)            AS n_rows,
    MIN(ts_utc)         AS first_hour,
    MAX(ts_utc)         AS last_hour,
    MAX(model_version)  AS model_version
FROM energy_lakehouse.gold.price_predictions;