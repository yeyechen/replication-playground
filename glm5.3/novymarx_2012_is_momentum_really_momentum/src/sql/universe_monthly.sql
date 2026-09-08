-- universe_monthly.sql
-- Purpose: Pull the full CRSP monthly universe (NO share-code or exchange
--   filter — Assumption 1: "all stocks in the CRSP universe") with returns,
--   prices, shares outstanding, exchange and SIC codes. Null return months
--   are KEPT (signal windows need them); only rows missing both prc and ret
--   are dropped. CRSP missing-return sentinels (-66/-77/-88/-99/-55) are
--   converted to NULL so they behave as missing months in signal windows.
-- Tables: crsp_202601.msf
-- Output columns: permno, month (calendar month-end Date32), ret, prc,
--   shrout, hexcd, hsiccd, me_dollars
-- Depends on: (none)
-- NOTE: month is returned as a 'YYYY-MM' string because every ClickHouse
-- month-end expression here (toLastDayOfMonth, Date32+INTERVAL) clamps
-- pre-1970 dates to 1970-01 (Date range limit); main.py converts the
-- string key to a calendar month-end timestamp in pandas.
SELECT
    permno,
    substring(date, 1, 7) AS month,
    if(ret IS NULL OR ret <= -50, NULL, ret) AS ret,
    prc,
    shrout,
    hexcd,
    hsiccd,
    abs(prc) * shrout * 1000 AS me_dollars
FROM crsp_202601.msf
WHERE toDate32(date) >= toDate32('1925-12-01')
  AND toDate32(date) <= toDate32('2010-12-31')
  AND NOT (prc IS NULL AND ret IS NULL)
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;
