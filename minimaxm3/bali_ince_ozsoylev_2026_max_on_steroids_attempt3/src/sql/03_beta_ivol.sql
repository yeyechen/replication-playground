-- 03_beta_ivol.sql
-- Purpose: 252-trading-day rolling CAPM beta and idiosyncratic volatility at month-end
-- Tables: crsp_202601.dsf, crsp_202601.dsfhdr, ff.four_factor, crsp_202601.dsi
-- Output columns: permno, month (YYYYMM), month_end_date, beta, ivol, n_days
-- Depends on: 00_daily_excess.sql (daily excess returns)
-- Notes:
--   - beta = cov(mkt_excess, stk_excess) / var(mkt_excess) over 252 trading days
--   - ivol = sqrt(var_resid) where residuals = stk_excess - (alpha + beta*mkt_excess)
--   - Only kept at month-end (last trading day of month per permno).
--   - Requires exactly 252 daily obs in window; otherwise NULL.
--   - Date filter starts at 1970-01-01 to avoid ClickHouse's pre-1970
--     toLastDayOfMonth clamp (which would silently mis-label month-end dates
--     before 1970). After 252 days of warm-up (1968 + 252 ≈ 1969), beta/ivol
--     is naturally only available from ~1970 onwards anyway.

WITH
  daily_excess AS (
    SELECT
      toUInt32(d.permno) AS permno,
      toDate32OrNull(d.date) AS date,
      if(d.ret > -1.0, toFloat64(d.ret), NULL) - toFloat64(rf.rf) AS stk_excess,
      toFloat64(mkt.vwretd) - toFloat64(rf.rf) AS mkt_excess
    FROM crsp_202601.dsf AS d
    INNER JOIN crsp_202601.dsfhdr AS h
      ON toUInt32(d.permno) = toUInt32(h.permno)
     AND toDate32OrNull(d.date) >= toDate32OrNull(h.begdat)
     AND toDate32OrNull(d.date) <= ifNull(toDate32OrNull(h.enddat), toDate32('2099-12-31'))
    LEFT JOIN ff.four_factor AS rf
      ON toDate32OrNull(rf.dt) = toDate32OrNull(d.date)
    LEFT JOIN crsp_202601.dsi AS mkt
      ON toDate32OrNull(mkt.date) = toDate32OrNull(d.date)
    WHERE toUInt32(h.hshrcd) IN (10, 11) AND toUInt32(h.hexcd) IN (1, 2, 3)
      AND toDate32OrNull(d.date) >= toDate32('1970-01-01')
      AND toDate32OrNull(d.date) <= toDate32('2022-12-31')
      AND d.ret > -1.0
  ),
  with_arrays AS (
    SELECT
      permno,
      date,
      groupArray(252)(stk_excess) OVER (PARTITION BY permno ORDER BY date ASC ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS s_arr,
      groupArray(252)(mkt_excess) OVER (PARTITION BY permno ORDER BY date ASC ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS m_arr
    FROM daily_excess
  ),
  stats AS (
    SELECT
      permno,
      date,
      length(s_arr) AS n,
      arraySum(s_arr) / length(s_arr) AS mean_s,
      arraySum(m_arr) / length(m_arr) AS mean_m,
      arraySum(arrayMap(i -> s_arr[i] * m_arr[i], arrayEnumerate(s_arr))) / length(s_arr) - (arraySum(s_arr) / length(s_arr)) * (arraySum(m_arr) / length(m_arr)) AS cov,
      arraySum(arrayMap(i -> m_arr[i] * m_arr[i], arrayEnumerate(m_arr))) / length(m_arr) - pow(arraySum(m_arr) / length(m_arr), 2) AS var_m,
      arraySum(arrayMap(i -> s_arr[i] * s_arr[i], arrayEnumerate(s_arr))) / length(s_arr) - pow(arraySum(s_arr) / length(s_arr), 2) AS var_s
    FROM with_arrays
    WHERE length(s_arr) = 252
  )
SELECT
  permno,
  toUInt32(toYYYYMM(date)) AS month,
  date AS month_end_date,
  cov / var_m AS beta,
  sqrt(var_s - (cov * cov) / var_m) AS ivol,
  toUInt32(n) AS n_days
FROM stats
WHERE toDate(date) = toLastDayOfMonth(toDate(date))
SETTINGS max_execution_time = 1800,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
