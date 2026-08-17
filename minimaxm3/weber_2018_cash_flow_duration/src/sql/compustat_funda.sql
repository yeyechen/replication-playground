-- compustat_funda.sql
-- Purpose: Extract Compustat annual fundamentals with computed book equity,
--          lagged book equity for ROE, lagged sales for sales-growth seed.
--          One row per (gvkey, fyear), preferring datafmt='STD' over 'SUMM_STD'
--          when both exist.
-- Tables:  comp_202601.funda
-- Output columns: gvkey, fyear, datadate, at, be, ceq, seq, ib, sale, sale_5y_ago,
--                 sale_1y_ago, be_lag1, net_payout, dvc, tstk, csho, prcc_f, sich, datafmt
-- Depends on: (none)
--
-- Notes:
--   - Filter: indfmt='INDL', consol='C', popsrc='D', datafmt IN ('STD','SUMM_STD')
--   - Book equity (paper §2 L106): BE = ceq + txditc - pstkrv (preferred),
--     fallback chain: ceq -> ceqt -> seq.
--   - In SUMM_STD rows, ceq/ceqt are NULL so the fallback to seq - pstkrv applies.
--   - At: total assets (in millions of USD).
--   - ROE and other ratios will be computed in Python (post-aggregation) since
--     they require a proper lagged denominator.
WITH
  raw AS (
    SELECT
      gvkey,
      fyear,
      datadate,
      at,
      ceq,
      ceqt,
      seq,
      pstk,
      pstkrv,
      pstkl,
      txditc,
      ib,
      sale,
      dvc,
      tstk,
      csho,
      prcc_f,
      sich,
      datafmt,
      -- BE construction (per paper §2 L106)
      -- Preferred: ceq + txditc - pstkrv (fallback chain)
      COALESCE(
        if(ceq IS NOT NULL AND pstkrv IS NOT NULL AND txditc IS NOT NULL,
           ceq + txditc - pstkrv, NULL),
        if(ceq IS NOT NULL AND pstkl IS NOT NULL AND txditc IS NOT NULL,
           ceq + txditc - pstkl, NULL),
        if(ceq IS NOT NULL AND pstk IS NOT NULL AND txditc IS NOT NULL,
           ceq + txditc - pstk, NULL),
        if(ceq IS NOT NULL AND txditc IS NOT NULL,
           ceq + txditc, NULL),
        if(ceqt IS NOT NULL AND pstkrv IS NOT NULL AND txditc IS NOT NULL,
           ceqt + txditc - pstkrv, NULL),
        if(ceqt IS NOT NULL AND txditc IS NOT NULL,
           ceqt + txditc, NULL),
        if(ceqt IS NOT NULL AND pstkrv IS NOT NULL,
           ceqt - pstkrv, NULL),
        if(ceqt IS NOT NULL, ceqt, NULL),
        if(seq IS NOT NULL AND pstkrv IS NOT NULL, seq - pstkrv, NULL),
        if(seq IS NOT NULL AND pstkl IS NOT NULL, seq - pstkl, NULL),
        if(seq IS NOT NULL AND pstk IS NOT NULL, seq - pstk, NULL),
        seq
      ) AS be_millions,
      COALESCE(dvc, 0) + COALESCE(tstk, 0) AS net_payout
    FROM comp_202601.funda
    WHERE gvkey IS NOT NULL
      AND fyear IS NOT NULL
      AND datadate IS NOT NULL
      AND indfmt = 'INDL'
      AND consol = 'C'
      AND popsrc = 'D'
      AND datafmt IN ('STD', 'SUMM_STD')
  ),
  -- Dedupe (gvkey, fyear): prefer STD over SUMM_STD, then latest datadate
  dedup AS (
    SELECT *,
      row_number() OVER (
        PARTITION BY gvkey, fyear
        ORDER BY (datafmt = 'STD') DESC, datadate DESC
      ) AS rn
    FROM raw
  )
SELECT
  gvkey,
  fyear,
  toDate32OrNull(datadate) AS datadate,
  at,
  be_millions               AS be,
  ceq,
  seq,
  ib,
  sale,
  dvc,
  tstk,
  net_payout,
  csho,
  prcc_f,
  sich,
  datafmt,
  -- Per-(gvkey, fyear) lagged values:
  lagInFrame(sale, 5) OVER w AS sale_5y_ago,
  lagInFrame(sale, 1) OVER w AS sale_1y_ago,
  lagInFrame(be_millions, 1) OVER w AS be_lag1,
  lagInFrame(at, 1) OVER w AS at_lag1
FROM dedup
WHERE rn = 1
WINDOW w AS (PARTITION BY gvkey ORDER BY fyear)
