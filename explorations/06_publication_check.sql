-- When was each series last published? (run on fresh data, note the time)
SELECT
    MAX(CASE WHEN price IS NOT NULL THEN ts_berlin END) AS last_price,
    MAX(CASE WHEN load IS NOT NULL THEN ts_berlin END)AS last_load,
    MAX(CASE WHEN wind_onshore IS NOT NULL THEN ts_berlin END)AS last_wind_onshore,
    MAX(CASE WHEN wind_offshore IS NOT NULL THEN ts_berlin END)AS last_wind_offshore,
    MAX(CASE WHEN solar IS NOT NULL THEN ts_berlin END)AS last_solar
FROM energy_lakehouse.silver.smard_hourly;


-- Result, run Mon 26 Oct 2026 (ingest_smard 12:42–12:45 Berlin):
--   last_price         = 2026-10-26 23:00  -> today complete; tomorrow's prices not on SMARD yet (publishing delay)
--   last_load          = 2026-10-26 10:00  -> ~2-3 h delay
--   last_wind_onshore  = 2026-10-26 10:00  -> ~2-3 h delay
--   last_wind_offshore = 2026-10-26 11:00  -> ~2 h delay
--   last_solar         = 2026-10-25 23:00  -> stops at end of yesterday = bottleneck
--
-- Conclusion for the daily job (08:00 on D, predicts D+1):
--   price_lag_24h (needs all of D)          OK
--   load/wind lag_48h (need all of D-1)     OK
--   solar_lag_48h (needs all of D-1)        to verify: re-run this check tomorrow ~07:45
--   Fallback: move the job later (still before the 12:00 auction)