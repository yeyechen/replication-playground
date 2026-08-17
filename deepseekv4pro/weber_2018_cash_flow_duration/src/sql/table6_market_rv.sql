-- table6_market_rv.sql
-- Purpose: CRSP market daily returns (vwretd) for the T6 RV-sensitivity T3 variant
--          (RV from the CRSP value-weighted market, daily squared).
-- Tables: crsp_202601.dsi
-- Output columns: date (Date32), vwretd (Float64)
-- Depends on: (none)
-- Settings: max_execution_time=300
--
-- NOTE: dsi.date is a String 'YYYY-MM-DD'. Cast with toDate32.

SELECT
    toDate32(date) AS date,
    vwretd AS vwretd
FROM crsp_202601.dsi
WHERE toDate32(date) >= toDate32('1962-07-01')
  AND toDate32(date) <= toDate32('2014-06-30')
  AND vwretd IS NOT NULL
ORDER BY date
SETTINGS max_execution_time = 300,
         max_rows_to_read = 100000000
