-- 06_ff_factors.sql
-- Purpose: Outer-join FF4 + FF5 monthly to materialize the FF6 factor set
--          (mkt_rf, smb, hml, mom, rmw, cma, rf) on the standard calendar month-end.
-- Tables: ff.four_factor_monthly, ff.five_factor_monthly
-- Output columns: month (YYYYMM), date, mkt_rf, smb, hml, mom, rmw, cma, rf
-- Depends on: (none)
-- Notes:
--   - Inner join on dt is exact because both tables share the same Kenneth French
--     calendar (Assumption 6 in assumptions.md).
--   - dt is Nullable(String); cast to Date32 to align with panel months.
--   - month = YYYYMM (UInt32) to match the panel's month convention.

SELECT
  toUInt32(toYear(CAST(a.dt AS Date32)) * 100 + toMonth(CAST(a.dt AS Date32))) AS month,
  toDate32(CAST(a.dt AS Date32)) AS date,
  toFloat64(a.mkt_rf) AS mkt_rf,
  toFloat64(a.smb) AS smb,
  toFloat64(a.hml) AS hml,
  toFloat64(a.mom) AS mom,
  toFloat64(b.rmw) AS rmw,
  toFloat64(b.cma) AS cma,
  toFloat64(a.rf) AS rf
FROM ff.four_factor_monthly AS a
INNER JOIN ff.five_factor_monthly AS b
  ON CAST(a.dt AS Date32) = CAST(b.dt AS Date32)
WHERE toUInt32(toYear(CAST(a.dt AS Date32)) * 100 + toMonth(CAST(a.dt AS Date32))) >= 196802
  AND toUInt32(toYear(CAST(a.dt AS Date32)) * 100 + toMonth(CAST(a.dt AS Date32))) <= 202212
SETTINGS max_execution_time = 120,
         max_rows_to_read = 1000000,
         timeout_before_checking_execution_speed = 0
