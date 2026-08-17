-- june_price_me.sql
-- Purpose: June-end CRSP price (abs(prc)) and market equity (abs(prc)*shrout*1000)
--          per (permno, June year) for the Table 8 composition report (median price,
--          median me, and coverage-share denominator across the full universe).
-- Tables: crsp_202601.msf, crsp_202601.msfhdr
-- Output columns: permno, june_year (Int16), prc (Float64), me (Float64)
-- Depends on: none
-- Settings: join_algorithm=partial_merge, max_execution_time=600
--
-- Same PIT universe filter as panel.sql (common stocks shrcd 10/11, exchcd 1/2/3,
-- ex-financials/utilities, valid returns, no price floor), restricted to June rows.

SELECT
    m.permno AS permno,
    toYear(toDate32(m.date)) AS june_year,
    abs(m.prc) AS prc,
    abs(m.prc) * m.shrout * 1000 AS me
FROM crsp_202601.msf AS m
INNER JOIN crsp_202601.msfhdr AS h
    ON m.permno = h.permno
   AND toDate32(m.date) >= toDate32(h.begdat)
   AND toDate32(m.date) <= toDate32(h.enddat)
WHERE toDate32(m.date) >= toDate32('1982-06-01')
  AND toDate32(m.date) <= toDate32('2009-07-31')
  AND toMonth(toDate32(m.date)) = 6
  AND h.hshrcd IN (10, 11)
  AND h.hexcd IN (1, 2, 3)
  AND (h.hsiccd < 4900 OR h.hsiccd >= 5000)
  AND (h.hsiccd < 6000 OR h.hsiccd >= 7000)
  AND m.ret IS NOT NULL
  AND m.ret > -1.0
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
