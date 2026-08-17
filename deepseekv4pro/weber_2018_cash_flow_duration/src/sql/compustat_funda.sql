-- compustat_funda.sql
-- Purpose: Compustat annual fundamentals linked to CRSP permnos via CCM link,
--          filtered to the standard WRDS quality screen and firms with >= 2
--          funda years in window. Produces the raw item columns used by main.py
--          for the book-equity cascade and duration inputs.
-- Tables: comp_202601.funda, crsp_202601.ccmxpf_linktable
-- Output columns: gvkey, lpermno, datadate, fyear, fyr, seq, ceq, pstk,
--                 pstkrv, pstkl, txdb, itcb, at, lt, ib, sale, ni, dv, prstkc, sstk
-- Depends on: (none)
-- Settings: join_algorithm=partial_merge, max_execution_time=600
--
-- Quality screen (references/COMPUSTAT.md, WRDS-official):
--   indfmt='INDL', consol='C', popsrc='D', datafmt='STD'.
-- CCM link (assumption A12): linktype IN ('LC','LU'), linkprim IN ('P','C'),
--   usedflag=1, PIT linkdt <= datadate <= coalesce(linkenddt,'2100-01-01').
-- Two-year availability (avail_compustat_two_years): keep gvkeys with >= 2 distinct
--   funda fyear observations in the 1960..2014 window (computed via window count).
--
-- datadate is a String in this extract -> toDate32.

WITH funda AS (
    SELECT
        gvkey, datadate, fyear, fyr,
        seq, ceq, pstk, pstkrv, pstkl, txdb, itcb,
        at, lt, ib, sale, ni, dv, prstkc, sstk
    FROM comp_202601.funda
    WHERE indfmt = 'INDL'
      AND consol = 'C'
      AND popsrc = 'D'
      AND datafmt = 'STD'
      AND fyear >= 1960
      AND fyear <= 2014
),
link AS (
    SELECT
        gvkey, lpermno, linkdt, linkenddt
    FROM crsp_202601.ccmxpf_linktable
    WHERE linktype IN ('LC', 'LU')
      AND linkprim IN ('P', 'C')
      AND usedflag = 1
),
two_year AS (
    SELECT gvkey
    FROM funda
    GROUP BY gvkey
    HAVING count(DISTINCT fyear) >= 2
)
SELECT
    f.gvkey AS gvkey,
    toUInt32(l.lpermno) AS lpermno,
    toDate32(f.datadate) AS datadate,
    f.fyear,
    f.fyr,
    f.seq, f.ceq, f.pstk, f.pstkrv, f.pstkl, f.txdb, f.itcb,
    f.at, f.lt, f.ib, f.sale, f.ni, f.dv, f.prstkc, f.sstk
FROM funda AS f
INNER JOIN link AS l
    ON f.gvkey = l.gvkey
   AND toDate32(f.datadate) >= toDate32(l.linkdt)
   AND toDate32(f.datadate) <= toDate32(coalesce(l.linkenddt, '2100-01-01'))
INNER JOIN two_year AS ty ON f.gvkey = ty.gvkey
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
