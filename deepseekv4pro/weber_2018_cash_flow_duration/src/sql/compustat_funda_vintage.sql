-- compustat_funda_vintage.sql
-- Purpose: Scratch-probe ONLY (audit1 M1 diagnosis) — NOT part of the canonical
--          pipeline. Builds the Compustat annual fundamentals table from an older
--          data vintage ({funda_db}.funda) linked to CRSP via the matching vintage
--          link table ({link_db}.ccmxpf_linktable), using the IDENTICAL quality
--          screen and cascade as compustat_funda.sql. Used by src/vintage_probe.py
--          to test whether the D9/D10 tail drift is caused by Compustat vintage
--          backfills. {funda_db} / {link_db} are substituted at run time (a
--          placeholder DB is injected so this file stays version-controlled while
--          the probe iterates over vintages without touching canonical SQL).
-- Tables: {funda_db}.funda, {link_db}.ccmxpf_linktable
-- Output columns: gvkey, lpermno, datadate, fyear, fyr, seq, ceq, pstk,
--                 pstkrv, pstkl, txdb, itcb, at, lt, ib, sale, ni, dv, prstkc, sstk
-- Depends on: (none) — mirrors compustat_funda.sql filters exactly
-- Settings: join_algorithm=partial_merge, max_execution_time=600

WITH funda AS (
    SELECT
        gvkey, datadate, fyear, fyr,
        seq, ceq, pstk, pstkrv, pstkl, txdb, itcb,
        at, lt, ib, sale, ni, dv, prstkc, sstk
    FROM {funda_db}.funda
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
    FROM {link_db}.ccmxpf_linktable
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
