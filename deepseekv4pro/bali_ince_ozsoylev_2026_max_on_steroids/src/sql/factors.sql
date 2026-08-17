-- factors.sql
-- Purpose: Assemble the Fama-French / Carhart FF6 factor set from the
--   ClickHouse FF tables. Join ff.four_factor_monthly (mkt_rf, smb, hml,
--   rf, mom) with ff.five_factor_monthly (rmw, cma) on the calendar month
--   `dt` (both store month-end `dt` as Nullable(String) YYYY-MM-DD, so a
--   plain equality join is exact).
--   mkt_rf/smb/hml/rf/mom are taken from four_factor_monthly (FF6 =
--   FF5 + momentum, per the paper); rmw/cma are taken from
--   five_factor_monthly (available from 1963-07 onwards).
-- Tables: ff.four_factor_monthly, ff.five_factor_monthly
-- Output columns: dt, mkt_rf, smb, hml, rf, mom, rmw, cma
-- Depends on: (none)
-- Produces: factors.parquet (after merge with the two user-provided
--   factor files and restricting to 1968-01 .. 2022-12 in main.py)
-- Notes: returns are decimal (e.g. 0.02 = 2%), NOT percent.
SELECT
    a.dt             AS dt,
    a.mkt_rf         AS mkt_rf,
    a.smb            AS smb,
    a.hml            AS hml,
    a.rf             AS rf,
    a.mom            AS mom,
    b.rmw            AS rmw,
    b.cma            AS cma
FROM ff.four_factor_monthly AS a
LEFT JOIN ff.five_factor_monthly AS b
       ON a.dt = b.dt
WHERE a.dt >= '1968-01-01'
  AND a.dt <= '2022-12-31'
ORDER BY a.dt
SETTINGS max_execution_time = 300,
         max_rows_to_read = 10000000,
         timeout_before_checking_execution_speed = 0
