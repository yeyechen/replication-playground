-- ff_factors.sql
-- Purpose: Pull Fama-French monthly factors (Mkt-RF, SMB, HML, MOM, RF, RMW, CMA)
--          aligned to the sample period July 1963 - June 2014.
-- Tables:  ff.four_factor_monthly, ff.five_factor_monthly
-- Output columns: dt, year, month, mkt_rf, smb, hml, rf, mom, rmw, cma
-- Depends on: (none)
--
-- Notes:
--   - We use FF-monthly tables, which carry calendar month-end dates.
--   - ff.four_factor_monthly has dt, mkt_rf, smb, hml, rf, mom
--   - ff.five_factor_monthly has dt, mkt_rf, smb, hml, rmw, cma, rf
--     (no mom). We LEFT JOIN five_factor onto four_factor on dt to keep all
--     six factors in one row.
SELECT
  f4.dt                                                       AS dt,
  toUInt16(toYear(toDate32OrNull(f4.dt)))                     AS year,
  toUInt8(toMonth(toDate32OrNull(f4.dt)))                     AS month,
  toFloat64(f4.mkt_rf)                                        AS mkt_rf,
  toFloat64(f4.smb)                                           AS smb,
  toFloat64(f4.hml)                                           AS hml,
  toFloat64(f4.rf)                                            AS rf,
  toFloat64(f4.mom)                                           AS mom,
  toFloat64(f5.rmw)                                           AS rmw,
  toFloat64(f5.cma)                                           AS cma
FROM ff.four_factor_monthly AS f4
LEFT JOIN ff.five_factor_monthly AS f5
  ON f4.dt = f5.dt
WHERE f4.dt >= '1963-07-01'
  AND f4.dt <= '2014-12-31'
