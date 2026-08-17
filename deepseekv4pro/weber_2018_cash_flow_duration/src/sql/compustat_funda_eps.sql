-- compustat_funda_eps.sql
-- Purpose: Compustat annual EPS (split-adjusted, per share) linked to CRSP permnos for
--          the realized five-year annualized EPS growth (EG, Table 8 Panel B).
-- Tables: comp_202601.funda, crsp_202601.ccmxpf_linktable
-- Output columns: permno, gvkey, datadate, fyear, epspx, epspi
-- Depends on: none
-- Settings: join_algorithm=partial_merge, max_execution_time=600
--
-- Iteration-10 rationale: the paper says EG comes from IBES (act_epsus, pdicity='ANN').
--   But act_epsus is the *unadjusted-for-splits* file: as-reported EPS five years apart
--   sits on different share bases after any split, biasing (EPS_t / EPS_{t-5}) downward
--   and producing spurious negative/compressed growth (e.g. ours D1 = -1.6% vs paper
--   6.95%). Compustat `epspx` (EPS excluding extraordinary items) is split-adjusted and
--   is the standard realized-EPS-growth input. Documented as a data-availability-driven
--   substitution of IBES unadjusted with Compustat split-adjusted EPS.

WITH funda AS (
    SELECT gvkey, datadate, fyear, epspx, epspi
    FROM comp_202601.funda
    WHERE indfmt = 'INDL'
      AND consol = 'C'
      AND popsrc = 'D'
      AND datafmt = 'STD'
      AND fyear >= 1976
      AND fyear <= 2014
),
link AS (
    SELECT gvkey, lpermno, linkdt, linkenddt
    FROM crsp_202601.ccmxpf_linktable
    WHERE linktype IN ('LC', 'LU')
      AND linkprim IN ('P', 'C')
      AND usedflag = 1
)
SELECT
    toUInt32(l.lpermno) AS permno,
    f.gvkey AS gvkey,
    toDate32(f.datadate) AS datadate,
    f.fyear AS fyear,
    f.epspx AS eps,
    f.epspi AS eps_pi
FROM funda AS f
INNER JOIN link AS l
    ON f.gvkey = l.gvkey
   AND toDate32(f.datadate) >= toDate32(l.linkdt)
   AND toDate32(f.datadate) <= toDate32(coalesce(l.linkenddt, '2100-01-01'))
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
