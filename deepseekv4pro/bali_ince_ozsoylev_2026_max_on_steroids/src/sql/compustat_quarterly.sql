-- compustat_quarterly.sql
-- Purpose: Pull quarterly Compustat fundamentals + CCM link for ROE, ROA, and
--   the Campbell-Hilscher-Szilagyi (CHS 2008) distress inputs. Quarter-end rows
--   only (standard WRDS filter, fiscal-quarter view datafqtr IS NOT NULL).
-- Tables: comp_202601.fundq, crsp_202601.ccmxpf_linktable
-- Output columns: permno, gvkey, datadate, fyearq, fqtr, atq, ltq, seqq, ceqq,
--   ibq, niq, cheq, cshoq, prccq, txdbq, pstkq, pstkrq
-- Depends on: (none)
-- Produces: feeds Section 3 merge for ROE (ibq / lagged BE_q), ROA
--   (ibq / atq at prior quarter), and CHS distress (NIMTA/TLMTA/CASHMTA inputs).
--
-- Quarterly book equity (be_q) is computed in Python from seqq + txdbq + itcb
--   (annual fallback) - preferred, because fundq LACKS itcbq: use the annual
--   itcb (compustat_annual.sql) at the same fiscal year, else 0. Logged in
--   Assumption 19/13. Preferred = pstkq, else pstkrq, else 0.
-- Settings: join_algorithm=partial_merge, max_execution_time=600
WITH ccm AS (
    SELECT
        gvkey      AS gvkey,
        lpermno    AS permno,
        linkdt     AS linkdt,
        linkenddt  AS linkenddt
    FROM crsp_202601.ccmxpf_linktable
    WHERE linktype IN ('LC', 'LU')
      AND linkprim IN ('P', 'C')
      AND usedflag = 1
)
SELECT
    c.permno   AS permno,
    f.gvkey    AS gvkey,
    toDate32OrNull(f.datadate) AS datadate,
    f.fyearq   AS fyearq,
    f.fqtr     AS fqtr,
    f.atq      AS atq,
    f.ltq      AS ltq,
    f.seqq     AS seqq,
    f.ceqq     AS ceqq,
    f.ibq      AS ibq,
    f.niq      AS niq,
    f.cheq     AS cheq,
    f.cshoq    AS cshoq,
    f.prccq    AS prccq,
    f.txdbq    AS txdbq,
    f.pstkq    AS pstkq,
    f.pstkrq   AS pstkrq
FROM comp_202601.fundq AS f
INNER JOIN ccm AS c
        ON f.gvkey = c.gvkey
       AND toDate32OrNull(f.datadate) >= toDate32OrNull(c.linkdt)
       AND (c.linkenddt IS NULL OR toDate32OrNull(f.datadate) <= toDate32OrNull(c.linkenddt))
WHERE f.indfmt  = 'INDL'
  AND f.consol  = 'C'
  AND f.popsrc  = 'D'
  AND f.datafmt = 'STD'
  AND f.datafqtr IS NOT NULL
  AND f.datadate IS NOT NULL
  AND f.datadate >= '1962-01-01'
  AND f.datadate <= '2022-12-31'
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 20000000000,
         timeout_before_checking_execution_speed = 0
