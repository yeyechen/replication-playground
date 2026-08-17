-- compustat_fundq_sue.sql
-- Purpose: Compustat quarterly EPS (split-adjusted, per share) + quarter-end price
--          for the Livnat-Mendenhall seasonal-random-walk SUE (SUE1/SUE2).
--          Compustat EPS fields are split-adjusted (unlike IBES "unadjusted"
--          act_epsus, whose raw value carries reverse-split artifacts up to 7.6e11).
-- Tables: comp_202601.fundq, crsp_202601.ccmxpf_linktable
-- Output columns: permno, gvkey, datadate (qtr-end), rdq (report date), fyearq, fqtr,
--                 eps_piq, eps_pxq, exsp_eps (=(ibq-spiq)/cshfdq), prccq, cshfdq
-- Depends on: none
-- Settings: join_algorithm=partial_merge, max_execution_time=600
--
-- SUE definitions (paper L1929 / footnote 17):
--   SUE1 = seasonal random walk on REPORTED EPS            -> epspiq
--           (EPS incl. extraordinary + special items).
--   SUE2 = seasonal random walk on EX-SPECIAL-ITEMS EPS    -> (ibq - spiq) / cshfdq
--           (income before extraordinaries, less special items, diluted per share).
--           NOTE: spiq is pre-tax; subtracting it gross over-corrects. Documented
--           first-order proxy in the absence of an after-tax special-items field.
--   price = prccq (close at quarter end, split-adjusted) — the Livnat-Mendenhall
--           scaler at the surprise quarter (not the June IBES price).
--
-- Quality screen mirrors compustat_funda.sql: indfmt='INDL', consol='C',
-- popsrc='D', datafmt='STD'; CCM link linktype IN ('LC','LU'), linkprim IN ('P','C'),
-- usedflag=1, PIT linkdt <= datadate <= coalesce(linkenddt,'2100-01-01').

WITH fundq AS (
    SELECT
        gvkey, datadate, rdq, fyearq, fqtr,
        epspiq, epspxq, ibq, spiq, cshfdq, prccq, cusip
    FROM comp_202601.fundq
    WHERE indfmt = 'INDL'
      AND consol = 'C'
      AND popsrc = 'D'
      AND datafmt = 'STD'
      AND fyearq >= 1976
      AND fyearq <= 2009
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
    toDate32(f.rdq) AS rdq,
    f.fyearq,
    f.fqtr,
    f.epspiq AS eps_piq,
    f.epspxq AS eps_pxq,
    if(f.ibq IS NOT NULL AND f.spiq IS NOT NULL AND f.cshfdq IS NOT NULL AND f.cshfdq != 0,
       (f.ibq - f.spiq) / f.cshfdq, NULL) AS exsp_eps,
    f.prccq AS prccq,
    f.cshfdq AS cshfdq,
    f.cusip AS cusip
FROM fundq AS f
INNER JOIN link AS l
    ON f.gvkey = l.gvkey
   AND toDate32(f.datadate) >= toDate32(l.linkdt)
   AND toDate32(f.datadate) <= toDate32(coalesce(l.linkenddt, '2100-01-01'))
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
