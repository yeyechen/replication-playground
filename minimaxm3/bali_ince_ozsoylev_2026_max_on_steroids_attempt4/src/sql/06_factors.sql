-- 06_factors.sql
-- Purpose: Monthly Fama-French factor returns (CAPM, FF3, FFC4, FF5).
-- Tables:  ff.four_factor_monthly, ff.five_factor_monthly
-- Output columns: month (Date32), mkt_rf, smb, hml, rf, mom, rmw, cma
-- Notes:
--   * ff.four_factor_monthly.dt is calendar month-end string.
--   * Use ff.four_factor_monthly for CAPM/FF3/FFC4 (mkt_rf, smb, hml, mom, rf).
--   * Use ff.five_factor_monthly for FF5/FF6 (rmw, cma).
--   * FFCPS and FF6PS columns are dropped per Assumption 3 (LIQ missing).
-- Depends on: (none)

SELECT
    toDate32(f4.dt)                              AS month,
    f4.mkt_rf                                    AS mkt_rf,
    f4.smb                                       AS smb,
    f4.hml                                       AS hml,
    f4.rf                                        AS rf,
    f4.mom                                       AS mom,
    f5.rmw                                       AS rmw,
    f5.cma                                       AS cma
FROM ff.four_factor_monthly AS f4
LEFT JOIN ff.five_factor_monthly AS f5
    ON toDate32(f4.dt) = toDate32(f5.dt)
WHERE toDate32OrNull(f4.dt) >= toDate32('1968-01-01')
  AND toDate32OrNull(f4.dt) <= toDate32('2022-12-31')
SETTINGS max_execution_time = 60,
         max_rows_to_read = 1000000,
         timeout_before_checking_execution_speed = 0
