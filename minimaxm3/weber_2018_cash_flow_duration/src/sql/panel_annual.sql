-- panel_annual.sql
-- Purpose: Build the per-(permno, sort_year) annual features panel.
--
-- For each sort_year t (calendar year of the June sort):
--   - fyear = t - 1 (the fiscal year used for the sort)
--   - me_jun_dollars  = |prc| * shrout * 1000  at June of sort_year t
--   - me_dec_prior_dollars = |prc| * shrout * 1000 at December of (t-1)
--   - be_t = book equity for fiscal year (t-1)        -- millions USD, converted to dollars
--   - bm_t = be_t / me_dec_prior_dollars              (paper §2 L106)
--
-- The 13F IOR (Table 10) is left as 0 here; the IOR column is populated in
-- main.py after running the inst_ownership.sql pull.
--
-- The duration (Dur) is also 0 here; it is computed in main.py via the
-- 15-step AR(1) recursion on the seeds pulled by duration_signal.sql.
--
-- Tables:  crsp_202601.msf, crsp_202601.msenames, crsp_202601.ccmxpf_linktable,
--          comp_202601.names, comp_202601.funda
-- Output columns: permno, gvkey, sort_year, fyear, sic, hexcd, shrcd, exchcd,
--                  me_jun_dollars, me_dec_prior_dollars, be_dollars,
--                  at_millions, bm, pr, roe, sales_g, sales_g_5y,
--                  age, dur, ior
-- Depends on: universe_pit.sql shape, compustat_funda.sql shape
--
-- Note: Each CTE wraps its source in `SELECT ... FROM (...) t` so that the
-- ClickHouse analyzer exposes plain column names (no qualifier syntax like
-- `m.gvkey`) for the next CTE to reference.

WITH
  -- ---- Per-(permno, year, month) universe rows with SIC and gvkey ----
  base_universe AS (
    SELECT permno, year, month, hexcd, shrcd, exchcd, gvkey, sic
    FROM (
      SELECT
        msf.permno                                                       AS permno,
        toUInt16(toYear(toDate32(msf.date)))                              AS year,
        toUInt8(toMonth(toDate32(msf.date)))                              AS month,
        msf.hexcd                                                        AS hexcd,
        msen.shrcd                                                       AS shrcd,
        msen.exchcd                                                      AS exchcd,
        ccm.gvkey                                                        AS gvkey,
        cs.sic                                                           AS sic
      FROM crsp_202601.msf AS msf
      INNER JOIN crsp_202601.msenames AS msen
        ON msf.permno = msen.permno
       AND toDate32(msf.date) >= toDate32(msen.namedt)
       AND toDate32(msf.date) <= toDate32(msen.nameendt)
      INNER JOIN (
        SELECT
          gvkey,
          toUInt32OrNull(toString(lpermno)) AS lpermno,
          toDate32OrNull(linkdt) AS linkdt,
          toDate32OrNull(coalesce(nullIf(linkenddt, ''), '2099-12-31')) AS linkenddt
        FROM crsp_202601.ccmxpf_linktable
        WHERE linktype IN ('LC','LU') AND linkprim IN ('P','C') AND usedflag = 1
          AND lpermno IS NOT NULL
      ) AS ccm
        ON msf.permno = ccm.lpermno
       AND toDate32(msf.date) >= ccm.linkdt
       AND toDate32(msf.date) <= ccm.linkenddt
      INNER JOIN (
        SELECT
          gvkey,
          toInt32OrZero(toString(sic)) AS sic,
          toInt32OrZero(coalesce(nullIf(toString(year1), ''), '0')) AS year1,
          toInt32OrZero(coalesce(nullIf(toString(year2), ''), '9999')) AS year2
        FROM comp_202601.names
        WHERE sic IS NOT NULL AND length(toString(sic)) > 0
      ) AS cs
        ON ccm.gvkey = cs.gvkey
       AND toUInt16(toYear(toDate32(msf.date))) >= cs.year1
       AND toUInt16(toYear(toDate32(msf.date))) <= cs.year2
      WHERE msf.permno IS NOT NULL
        AND msen.shrcd IN (10, 11)
        AND msen.exchcd IN (1, 2, 3)
        AND NOT (cs.sic >= 6000 AND cs.sic < 7000)
        AND NOT (cs.sic >= 4900 AND cs.sic < 5000)
    ) t
  ),
  -- ---- June-only rows (one per (permno, sort_year)) ----
  june_universe AS (
    SELECT permno, gvkey, sort_year, fyear, sic, hexcd, shrcd, exchcd
    FROM (
      SELECT
        permno,
        gvkey,
        year                            AS sort_year,
        year - 1                        AS fyear,
        sic,
        hexcd,
        shrcd,
        exchcd
      FROM base_universe
      WHERE month = 6
        AND year BETWEEN 1963 AND 2013
    ) t
  ),
  -- ---- June-end ME: |prc|*shrout*1000 at June of sort_year ----
  june_me AS (
    SELECT permno, sort_year, me_jun_dollars
    FROM (
      SELECT
        permno,
        toUInt16(toYear(toDate32(date))) AS sort_year,
        abs(toFloat64(prc)) * toFloat64(shrout) * 1000.0 AS me_jun_dollars
      FROM crsp_202601.msf
      WHERE permno IS NOT NULL
        AND prc IS NOT NULL AND abs(toFloat64(prc)) > 0
        AND shrout IS NOT NULL AND shrout > 0
        AND toMonth(toDate32(date)) = 6
        AND toYear(toDate32(date)) BETWEEN 1963 AND 2013
    ) t
  ),
  -- ---- December-end ME for prior year (for BM denominator) ----
  dec_me AS (
    SELECT permno, sort_year, me_dec_prior_dollars
    FROM (
      SELECT
        permno,
        toUInt16(toYear(toDate32(date))) - 1 AS sort_year,
        abs(toFloat64(prc)) * toFloat64(shrout) * 1000.0 AS me_dec_prior_dollars
      FROM crsp_202601.msf
      WHERE permno IS NOT NULL
        AND prc IS NOT NULL AND abs(toFloat64(prc)) > 0
        AND shrout IS NOT NULL AND shrout > 0
        AND toMonth(toDate32(date)) = 12
        AND toYear(toDate32(date)) BETWEEN 1962 AND 2014
    ) t
  ),
  -- ---- Per-(gvkey, fyear) Compustat fundamentals (deduped) ----
  raw_funda AS (
    SELECT gvkey, fyear, datadate, at, ceq, ceqt, seq, pstk, pstkrv, pstkl, txditc,
           ib, sale, dvc, tstk, datafmt, be_millions
    FROM (
      SELECT
        gvkey, fyear, datadate, at, ceq, ceqt, seq, pstk, pstkrv, pstkl, txditc,
        ib, sale, dvc, tstk, datafmt,
        COALESCE(
          if(ceq IS NOT NULL AND pstkrv IS NOT NULL AND txditc IS NOT NULL, ceq + txditc - pstkrv, NULL),
          if(ceq IS NOT NULL AND pstkl IS NOT NULL AND txditc IS NOT NULL, ceq + txditc - pstkl, NULL),
          if(ceq IS NOT NULL AND pstk IS NOT NULL  AND txditc IS NOT NULL, ceq + txditc - pstk,  NULL),
          if(ceq IS NOT NULL AND txditc IS NOT NULL, ceq + txditc, NULL),
          if(ceqt IS NOT NULL AND pstkrv IS NOT NULL AND txditc IS NOT NULL, ceqt + txditc - pstkrv, NULL),
          if(ceqt IS NOT NULL AND txditc IS NOT NULL, ceqt + txditc, NULL),
          if(ceqt IS NOT NULL AND pstkrv IS NOT NULL, ceqt - pstkrv, NULL),
          if(ceqt IS NOT NULL, ceqt, NULL),
          if(seq IS NOT NULL AND pstkrv IS NOT NULL, seq - pstkrv, NULL),
          if(seq IS NOT NULL AND pstkl IS NOT NULL, seq - pstkl, NULL),
          if(seq IS NOT NULL AND pstk IS NOT NULL, seq - pstk, NULL),
          seq
        ) AS be_millions
      FROM comp_202601.funda
      WHERE gvkey IS NOT NULL AND fyear IS NOT NULL
        AND indfmt = 'INDL' AND consol = 'C' AND popsrc = 'D'
        AND datafmt IN ('STD','SUMM_STD')
    ) t
  ),
  dedup_funda AS (
    SELECT gvkey, fyear, datadate, at, be_millions, ib, sale, dvc, tstk,
           sale_5y_ago, sale_1y_ago, be_lag1_millions
    FROM (
      SELECT
        gvkey, fyear, datadate, at, be_millions, ib, sale, dvc, tstk,
        lagInFrame(sale, 5) OVER w AS sale_5y_ago,
        lagInFrame(sale, 1) OVER w AS sale_1y_ago,
        lagInFrame(be_millions, 1) OVER w AS be_lag1_millions,
        row_number() OVER (
          PARTITION BY gvkey, fyear
          ORDER BY (datafmt = 'STD') DESC, datadate DESC
        ) AS rn
      FROM raw_funda
      WINDOW w AS (PARTITION BY gvkey ORDER BY fyear)
    ) t
    WHERE rn = 1
  ),
  first_fyear AS (
    SELECT gvkey, min_fyear
    FROM (
      SELECT gvkey, min(fyear) AS min_fyear
      FROM raw_funda
      GROUP BY gvkey
    ) t
  )
SELECT
  ju.permno,
  ju.gvkey,
  ju.sort_year,
  ju.fyear,
  ju.sic,
  ju.hexcd,
  ju.shrcd,
  ju.exchcd,
  toFloat64(jm.me_jun_dollars)                                       AS me_jun_dollars,
  toFloat64(dm.me_dec_prior_dollars)                                 AS me_dec_prior_dollars,
  toFloat64(fc.be_millions) * 1e6                                    AS be_dollars,
  toFloat64(fc.at)                                                   AS at_millions,
  -- B/M ratio: book equity in dollars / market equity in dollars
  if(toFloat64(dm.me_dec_prior_dollars) > 0,
     (toFloat64(fc.be_millions) * 1e6) / toFloat64(dm.me_dec_prior_dollars),
     NULL)                                                            AS bm,
  -- Payout ratio: (dvc - tstk) / ib
  -- Compustat's tstk is signed "decrease in treasury stock" — positive
  -- for ISSUANCE (treasury stock went down, so shares outstanding went
  -- up), negative for REPURCHASE. The paper's "net payout" treats
  -- repurchases as positive payouts, so we subtract tstk.
  if(fc.ib IS NOT NULL AND fc.ib != 0,
     (toFloat64(coalesce(fc.dvc, 0)) - toFloat64(coalesce(fc.tstk, 0))) / toFloat64(fc.ib),
     NULL)                                                            AS pr,
  -- ROE: ib / lagged book equity
  if(fc.be_lag1_millions IS NOT NULL AND fc.be_lag1_millions > 0,
     toFloat64(fc.ib) / toFloat64(fc.be_lag1_millions), NULL)        AS roe,
  -- 1-year sales growth (CAGR for k=1, equivalent to simple % change)
  if(fc.sale_1y_ago IS NOT NULL AND fc.sale_1y_ago > 0 AND fc.sale IS NOT NULL AND fc.sale > 0,
     (toFloat64(fc.sale) - toFloat64(fc.sale_1y_ago)) / toFloat64(fc.sale_1y_ago),
     NULL)                                                            AS sales_g,
  -- 5-year sales growth (CAGR): (sale_t / sale_{t-5})^(1/5) - 1
  if(fc.sale_5y_ago IS NOT NULL AND fc.sale_5y_ago > 0 AND fc.sale IS NOT NULL AND fc.sale > 0,
     pow(toFloat64(fc.sale) / toFloat64(fc.sale_5y_ago), 1.0 / 5.0) - 1.0,
     NULL)                                                            AS sales_g_5y,
  -- Age: years on Compustat (clipped at 2)
  toUInt16(greatest(ju.fyear - toInt32(ff.min_fyear) + 1, 2))         AS age,
  -- Dur and IOR placeholders (filled by main.py)
  toFloat64(0)                                                        AS dur,
  toFloat64(0)                                                        AS ior
FROM june_universe AS ju
INNER JOIN june_me AS jm
  ON ju.permno = jm.permno AND ju.sort_year = jm.sort_year
INNER JOIN dec_me AS dm
  ON ju.permno = dm.permno AND ju.sort_year = dm.sort_year
LEFT JOIN dedup_funda AS fc
  ON ju.gvkey = fc.gvkey AND ju.fyear = fc.fyear
LEFT JOIN first_fyear AS ff
  ON ju.gvkey = ff.gvkey
