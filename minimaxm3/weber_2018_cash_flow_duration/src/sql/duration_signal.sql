-- duration_signal.sql
-- Purpose: Assemble the seeds required for the duration computation:
--          - P_t = book equity at time t (in dollars)
--          - ROE_seed = ib / lagged book equity (initial ROE for the AR(1) recursion)
--          - sales_g_seed = 5-year (preferred) or 3-year sales growth
--          The actual 15-step AR(1) recursion is implemented in Python
--          (see src/main.py: compute_duration) — it operates on the
--          seeds produced here and outputs a `dur` column. This split keeps
--          SQL auditable (one place for the seed formulas) and Python small
--          (a 30-line numerical loop).
-- Tables: comp_202601.funda  (joined via same dedup chain as compustat_funda.sql)
-- Output columns: gvkey, fyear, datadate, be_dollars, bv_lag1_dollars,
--                 ib_dollars, roe_seed, sales_g_seed, sales_g_5y, sales_g_3y
-- Depends on: compustat_funda.sql (same dedup chain — see note)
--
-- Notes:
--   - All Compustat aggregates (at, be, ib, sale) are in millions USD; we
--     multiply by 1e6 here to convert to dollars, matching CRSP market equity.
--   - We require fyear >= 1962 to ensure at least 5 years of Compustat history
--     exists for the 5-year sales-growth lag (paper §2: "require at least two
--     years of Compustat" — we further require 5y lag availability for the
--     primary seed).
--   - sales_g_seed now uses a 5-year (preferred) or 3-year (fallback) AVERAGE
--     growth rate, annualized: (sale_t - sale_{t-k}) / sale_{t-k} / k.
--     A multi-year average is more stable than a 1-year rate and matches the
--     Dechow et al. (2004) "past sales growth" convention (see also Weber §2
--     L108).
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
      ) AS be_millions
    FROM comp_202601.funda
    WHERE gvkey IS NOT NULL
      AND fyear IS NOT NULL
      AND datadate IS NOT NULL
      AND indfmt = 'INDL'
      AND consol = 'C'
      AND popsrc = 'D'
      AND datafmt IN ('STD', 'SUMM_STD')
  ),
  dedup AS (
    SELECT *,
      row_number() OVER (
        PARTITION BY gvkey, fyear
        ORDER BY (datafmt = 'STD') DESC, datadate DESC
      ) AS rn
    FROM raw
  ),
  with_lags AS (
    SELECT
      gvkey,
      fyear,
      toDate32OrNull(datadate) AS datadate,
      be_millions,
      ib,
      sale,
      lagInFrame(sale, 5) OVER w AS sale_5y_ago,
      lagInFrame(sale, 3) OVER w AS sale_3y_ago,
      lagInFrame(sale, 1) OVER w AS sale_1y_ago,
      lagInFrame(be_millions, 1) OVER w AS be_lag1_millions
    FROM dedup
    WHERE rn = 1
    WINDOW w AS (PARTITION BY gvkey ORDER BY fyear)
  )
SELECT
  gvkey,
  fyear,
  datadate,
  -- Convert to dollars (matches CRSP market equity units)
  toFloat64(be_millions) * 1e6                  AS be_dollars,
  toFloat64(be_lag1_millions) * 1e6             AS bv_lag1_dollars,
  toFloat64(ib) * 1e6                           AS ib_dollars,
  -- ROE seed: ib / lagged book equity (both in dollars; ratio is unit-free)
  if(be_lag1_millions IS NOT NULL AND be_lag1_millions > 0,
     toFloat64(ib) / toFloat64(be_lag1_millions), NULL) AS roe_seed,
  -- 5-year COMPOUND annual growth rate (CAGR) (preferred seed).
  -- Computed as: (sale_t / sale_{t-5})^(1/5) - 1
  -- This is the standard "compound annual growth rate" convention and
  -- matches the paper's "past sales growth" wording more faithfully than
  -- simple annualization. Simple annualization (sale_t - sale_{t-5}) /
  -- sale_{t-5} / 5 over-states growth when sale_t / sale_{t-5} is large
  -- (e.g., a 3x increase over 5 years is 40% CAGR but 200% / 5 = 40% under
  -- simple annualization — equal in this case; but for 10x over 5 years
  -- CAGR = 58% vs simple = 180%, a 3x gap that compounds through the
  -- AR(1) recursion).
  if(
    sale_5y_ago IS NOT NULL AND sale_5y_ago > 0 AND sale IS NOT NULL AND sale > 0,
    pow(toFloat64(sale) / toFloat64(sale_5y_ago), 1.0 / 5.0) - 1.0,
    NULL
  ) AS sales_g_5y,
  -- 3-year COMPOUND annual growth rate (CAGR) (fallback if 5y missing).
  if(
    sale_3y_ago IS NOT NULL AND sale_3y_ago > 0 AND sale IS NOT NULL AND sale > 0,
    pow(toFloat64(sale) / toFloat64(sale_3y_ago), 1.0 / 3.0) - 1.0,
    NULL
  ) AS sales_g_3y,
  -- Selected seed: 5y preferred, 3y fallback. The 15-step AR(1) recursion
  -- amplifies any extreme seed into a wild duration value, so the seed is
  -- also winsorized per-fyear and hard-clipped in main.py. The hard clip
  -- range here is wider than the previous 1-year implementation:
  --   roe_seed:        [-1.0, 1.0]
  --   sales_g_seed:    [-1.0, 5.0]
  -- allowing explosive-growth firms (e.g., tech startups in the 1990s) to
  -- produce realistic extreme-duration values rather than a hard cap.
  -- Both sales_g_5y and sales_g_3y use CAGR (compound) — see comment above.
  coalesce(
    if(
      sale_5y_ago IS NOT NULL AND sale_5y_ago > 0 AND sale IS NOT NULL AND sale > 0,
      pow(toFloat64(sale) / toFloat64(sale_5y_ago), 1.0 / 5.0) - 1.0,
      NULL
    ),
    if(
      sale_3y_ago IS NOT NULL AND sale_3y_ago > 0 AND sale IS NOT NULL AND sale > 0,
      pow(toFloat64(sale) / toFloat64(sale_3y_ago), 1.0 / 3.0) - 1.0,
      NULL
    )
  ) AS sales_g_seed
FROM with_lags
WHERE be_millions IS NOT NULL AND be_millions > 0
