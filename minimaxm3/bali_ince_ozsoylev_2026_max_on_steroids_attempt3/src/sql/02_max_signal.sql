-- 02_max_signal.sql
-- Purpose: MAX signal per (permno, month) — average of 5 highest daily returns
-- Tables: crsp_202601.dsf, crsp_202601.dsfhdr
-- Output columns: permno, month, max, n_obs
-- Depends on: 01_universe_daily.sql (the universe-filtered daily return set)
-- Notes:
--   - dsf.ret is decimal (0.02 = 2%); MAX = average of 5 highest values, no
--     conversion needed.
--   - Require n_obs >= 15 daily observations within the month for MAX to be
--     non-null (per preprocessing_rules.json#avail_min_15_obs_per_month).
--   - month is YYYYMM (UInt32) — last-trading-day-of-month convention. The CRSP
--     msf.date is the last trading day of each month. We use a pre-1970-safe
--     date computation that avoids ClickHouse's toLastDayOfMonth clamp on
--     pre-1970 dates (which returns 1970-01-01 instead of the actual month-end).

WITH
  universe_daily AS (
    SELECT
      toUInt32(d.permno) AS permno,
      toDate32OrNull(d.date) AS date,
      if(d.ret > -1.0, toFloat64(d.ret), NULL) AS ret
    FROM crsp_202601.dsf AS d
    INNER JOIN crsp_202601.dsfhdr AS h
      ON toUInt32(d.permno) = toUInt32(h.permno)
     AND toDate32OrNull(d.date) >= toDate32OrNull(h.begdat)
     AND toDate32OrNull(d.date) <= ifNull(toDate32OrNull(h.enddat), toDate32('2099-12-31'))
    WHERE toUInt32(h.hshrcd) IN (10, 11) AND toUInt32(h.hexcd) IN (1, 2, 3)
      AND d.ret > -1.0
      AND toDate32OrNull(d.date) >= toDate32('1968-01-01')
      AND toDate32OrNull(d.date) <= toDate32('2022-12-31')
  ),
  ranked AS (
    -- Compute YYYYMM directly from year/month components to avoid the
    -- toLastDayOfMonth pre-1970 clamp bug in ClickHouse.
    SELECT
      permno,
      toUInt32(toYear(date) * 100 + toMonth(date)) AS month,
      ret,
      row_number() OVER (PARTITION BY permno, toYear(date) * 100 + toMonth(date) ORDER BY ret DESC) AS rnk
    FROM universe_daily
  )
SELECT
  permno,
  month,
  avg(ret) FILTER (WHERE rnk <= 5) AS max,
  count(ret) AS n_obs
FROM ranked
GROUP BY permno, month
HAVING n_obs >= 15
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
