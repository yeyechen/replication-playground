-- table1_me.sql
-- Purpose: Firm-level month-end market equity (dollars) for the CRSP common-stock
--          universe (shares outstanding x price), one row per (permno, month).
--          Used by Table 1 for the June-t market equity (ME) and the December t-1
--          market equity (BM denominator). Also supplies the NYSE-only June size
--          breakpoints (exchcd=1) for the "above 20th size percentile" screen.
-- Tables: crsp_202601.msf, crsp_202601.msfhdr
-- Output columns: permno, month (Date32 month-start), exchcd, me_dollars, cfacshr, shrout
-- Depends on: none
-- Settings: join_algorithm=partial_merge, max_execution_time=600
--
-- me_dollars = abs(prc) * shrout * 1000 (shrout in thousands of shares).
-- exchcd from the header (hexcd) PIT window.

SELECT
    m.permno AS permno,
    toDate32(formatDateTime(toDate32(m.date), '%Y-%m-01')) AS month,
    toUInt16(h.hexcd) AS exchcd,
    abs(m.prc) * m.shrout * 1000 AS me_dollars,
    m.cfacshr AS cfacshr,
    m.shrout AS shrout
FROM crsp_202601.msf AS m
INNER JOIN crsp_202601.msfhdr AS h
    ON m.permno = h.permno
   AND toDate32(m.date) >= toDate32(h.begdat)
   AND toDate32(m.date) <= toDate32(h.enddat)
WHERE toDate32(m.date) >= toDate32('1978-01-01')
  AND toDate32(m.date) <= toDate32('2014-12-31')
  AND h.hshrcd IN (10, 11)
  AND h.hexcd IN (1, 2, 3)
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
