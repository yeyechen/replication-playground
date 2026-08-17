-- universe_monthly.sql
-- Purpose: PIT-filtered monthly CRSP universe (common stocks NYSE/AMEX/Nasdaq,
--          excludes financials/utilities, optional $5 price floor, valid returns,
--          firm-level market equity in dollars).
-- Tables: crsp_202601.msf, crsp_202601.msfhdr
-- Output columns: permno, date, ret, prc, shrout, hsiccd, me_dollars
-- Depends on: (none)
-- Settings: join_algorithm=partial_merge, max_execution_time=600
--
-- Paper (Weber 2018, L104): common stocks on NYSE/Amex/Nasdaq; exclude
-- financials (6000<=SIC<7000) and utilities (4900<=SIC<5000) [CONVENTION-APPLIED,
-- SIC = PIT header hsiccd]. Universe validity via msfhdr begdat/enddat windows.
--
-- Funnel stages (reported per decade by main.py):
--   S0 raw msf rows in window
--   S1 PIT share/exchange filter (hshrcd 10/11, hexcd 1/2/3)
--   S2 SIC exclusion (financials/utilities)
--   S3 price floor abs(prc) >= 5  [behind PRICE_FILTER flag in main.py]
--   S4 valid return (ret IS NOT NULL AND ret > -1.0)  [sentinels -44/-55/-66/-77/-88/-99]
--
-- me_dollars = abs(prc) * shrout * 1000  (shrout in thousands of shares).

SELECT
    m.permno,
    toDate32(m.date) AS date,
    m.ret,
    m.prc,
    m.shrout,
    h.hsiccd AS hsiccd,
    abs(m.prc) * m.shrout * 1000 AS me_dollars
FROM crsp_202601.msf AS m
INNER JOIN crsp_202601.msfhdr AS h
    ON m.permno = h.permno
   AND toDate32(m.date) >= toDate32(h.begdat)
   AND toDate32(m.date) <= toDate32(h.enddat)
WHERE toDate32(m.date) >= toDate32('1962-07-01')
  AND toDate32(m.date) <= toDate32('2014-06-30')
  AND h.hshrcd IN (10, 11)
  AND h.hexcd IN (1, 2, 3)
  AND (h.hsiccd < 4900 OR h.hsiccd >= 5000)   -- drop utilities 4900-4999
  AND (h.hsiccd < 6000 OR h.hsiccd >= 7000)   -- drop financials 6000-6999
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
