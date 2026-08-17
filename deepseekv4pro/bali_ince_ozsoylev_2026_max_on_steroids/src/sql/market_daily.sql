-- market_daily.sql
-- Purpose: daily CRSP value-weighted market return (with dividends) — the market
--   proxy for the 252-day beta/IVOL regressions (Assumption 3).
-- Tables: crsp_202601.dsi
-- Output columns: date, vwretd
-- Depends on: (none)
-- Settings: (none)
SELECT
    date    AS date,
    vwretd  AS vwretd
FROM crsp_202601.dsi
WHERE date >= '1966-11-01'
  AND date <= '2022-12-31'
SETTINGS max_execution_time = 300,
         max_rows_to_read = 10000000,
         timeout_before_checking_execution_speed = 0
