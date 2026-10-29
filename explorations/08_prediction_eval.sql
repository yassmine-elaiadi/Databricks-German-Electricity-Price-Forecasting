-- Evaluation view: forecast vs real price vs naive baseline, per hour.
-- A view = a saved query -> always up to date, no job task needed.
CREATE OR REPLACE VIEW energy_lakehouse.gold.prediction_eval AS
SELECT
    p.ts_utc,
    p.ts_berlin,
    DATE(p.ts_berlin)                           AS day,
    HOUR(p.ts_berlin)                           AS hour,
    ROUND(p.pred, 2)                            AS pred,
    g.price,
    g.price_lag_24h                             AS baseline,          -- naive guess: copy yesterday
    ROUND(g.price - p.pred, 2)                  AS error,             -- + = model too low
    ROUND(ABS(g.price - p.pred), 2)             AS abs_error,
    ROUND(ABS(g.price - g.price_lag_24h), 2)    AS baseline_abs_error,
    p.model_version
FROM energy_lakehouse.gold.price_predictions AS p
JOIN energy_lakehouse.gold.price_features_hourly AS g
  ON p.ts_utc = g.ts_utc;



