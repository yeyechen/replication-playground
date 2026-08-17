-- t9_crsp_mcap.sql
-- Purpose: June-end CRSP market capitalization (abs(prc)*shrout*1000, in dollars) and
--          June-end split-adjusted close (abs(prc)) per (permno, June year) for the
--          Table 9 PTB denominator. PTB must be split-INVARIANT: the IBES consensus
--          target `meanptg` is split-adjusted, and `shout` from actpsum_epsus is NOT on
--          a consistent split basis (see reversed-split microcap artifacts). We therefore
--          compute PTB = (meanptg/price) * (mcap / BE), where (meanptg/price) is a
--          split-invariant ratio and (mcap/BE) uses raw (split-invariant) dollar totals.
-- Tables: crsp_202601.msf, crsp_202601.msfhdr
-- Output columns: permno (Int32), june_year (Int16), prc (Float64), mcap (Float64)
-- Depends on: none
-- Settings: join_algorithm=partial_merge, max_execution_time=600
--
-- Same PIT universe filter as panel.sql (common stocks shrcd 10/11, exchcd 1/2/3,
-- ex-financials/utilities, valid return), restricted to June 2001..2013.

SELECT
    m.permno AS permno,
    toYear(toDate32(m.date)) AS june_year,
    abs(m.prc) AS prc,
    abs(m.prc) * m.shrout * 1000 AS mcap
FROM crsp_202601.msf AS m
INNER JOIN crsp_202601.msfhdr AS h
    ON m.permno = h.permno
   AND toDate32(m.date) >= toDate32(h.begdat)
   AND toDate32(m.date) <= toDate32(h.enddat)
WHERE toDate32(m.date) >= toDate32('2001-06-01')
  AND toDate32(m.date) <= toDate32('2013-07-31')
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
