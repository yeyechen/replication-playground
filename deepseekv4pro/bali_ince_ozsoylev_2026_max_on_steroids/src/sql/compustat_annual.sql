-- compustat_annual.sql
-- Purpose: Pull annual Compustat fundamentals + CRSP-Compustat (CCM) link,
--   with book equity (BE) and all annual items needed for the mispricing
--   anomalies and O-score. Fiscal year-end rows only (standard WRDS filter).
-- Tables: comp_202601.funda, crsp_202601.ccmxpf_linktable
-- Output columns: permno, gvkey, datadate, fyear, be, at, lt, act, che, lct,
--   dlc, dltt, ppent, invt, ib, ni, revt, cogs, dp, oancf, txt
-- Depends on: (none)
-- Produces: feeds Section 3 merge (data/panel.parquet) for BE/BM, ROE lag,
--   accruals, NOA, asset growth, investment-to-assets, gross profitability,
--   Ohlson O-score.
--
-- BE (paper L189): seq + txdb + itcb - preferred,
--   preferred = pstkrv, else pstkl, else pstk, else 0.
-- Standard quality filter (WRDS-official): indfmt='INDL', consol='C',
--   popsrc='D', datafmt='STD'.
-- CCM link filter (FF standard): linktype IN ('LC','LU'), linkprim IN ('P','C'),
--   usedflag=1; temporal validity linkdt<=datadate<=linkenddt. Primary link
--   chosen by linkprim='P' tie-break (dedup in Python on (permno, datadate)).
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
    f.fyear    AS fyear,
    -- Book equity: seq + txdb + itcb - preferred (paper L189)
    ( f.seq
      + coalesce(f.txdb, 0)
      + coalesce(f.itcb, 0)
      - coalesce(f.pstkrv, coalesce(f.pstkl, coalesce(f.pstk, 0)))
    ) AS be,
    f.at       AS at,
    f.lt       AS lt,
    f.act      AS act,
    f.che      AS che,
    f.lct      AS lct,
    f.dlc      AS dlc,
    f.dltt     AS dltt,
    f.ppent    AS ppent,
    f.invt     AS invt,
    f.itcb     AS itcb,
    f.ib       AS ib,
    f.ni       AS ni,
    f.revt     AS revt,
    f.cogs     AS cogs,
    f.dp       AS dp,
    f.oancf    AS oancf,
    f.txt      AS txt
FROM comp_202601.funda AS f
INNER JOIN ccm AS c
        ON f.gvkey = c.gvkey
       AND toDate32OrNull(f.datadate) >= toDate32OrNull(c.linkdt)
       AND (c.linkenddt IS NULL OR toDate32OrNull(f.datadate) <= toDate32OrNull(c.linkenddt))
WHERE f.indfmt  = 'INDL'
  AND f.consol  = 'C'
  AND f.popsrc  = 'D'
  AND f.datafmt = 'STD'
  AND f.datadate IS NOT NULL
  AND f.datadate >= '1962-01-01'
  AND f.datadate <= '2022-12-31'
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 20000000000,
         timeout_before_checking_execution_speed = 0
