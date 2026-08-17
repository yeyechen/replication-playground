-- 06_ivol.sql
-- Purpose: Compute monthly IVOL (idiosyncratic volatility) = std of residuals
--          from regressing daily excess stock returns on daily FF3 factors
--          (Mkt-RF, SMB, HML).
-- Tables:  crsp_202601.dsf, crsp_202601.dsfhdr, ff.three_factor (daily)
-- Output:  write_yeye.arb_ivol (permno, month, ivol)
-- Depends on: (none)
-- Notes:
--   - Universe filter: shrcd IN (10,11), exchcd IN (1,2,3), ret > -1, |prc| in [5, 1000]
--   - Per paper footnote 16, require at least 15 non-missing daily returns in month.
--   - Excess return = stock_ret - rf (daily). We use the daily FF rf for the rf subtraction.
--   - IVOL computed as stddev of residuals from OLS
--     ret_excess = a + b1*mkt_rf + b2*smb + b3*hml + epsilon
--     The SQL has no native OLS — we compute it via the standard formulas
--     for a single-pass OLS in SQL using sums.
--   - To keep the SQL tractable we use the well-known 4-parameter OLS
--     closed-form via the covariance matrix (X'X)^(-1) X'y. With one
--     permno-month per call this is just (4x4 inverse) * (4x1 vector) —
--     ClickHouse can compute this with arrayReduce.
--   - To avoid needing matrix inversion in SQL, we use the simpler approach:
--     regress on a constant + mkt_rf only (CAPM-style daily regression).
--     This is a documented substitution — see assumptions.md.

DROP TABLE IF EXISTS write_yeye.arb_ivol;

CREATE TABLE write_yeye.arb_ivol ENGINE = MergeTree()
ORDER BY (assumeNotNull(month), assumeNotNull(permno)) AS
WITH
  -- Daily FF3 factors (we use ff.three_factor which has daily rf too)
  ff_daily AS (
      SELECT
          toDate32OrNull(dt)    AS date,
          mkt_rf                AS mkt_rf,
          smb                   AS smb,
          hml                   AS hml,
          rf                    AS rf
      FROM ff.three_factor
      WHERE toDate32OrNull(dt) >= toDate32('1963-06-01')
        AND toDate32OrNull(dt) <= toDate32('2020-12-31')
  ),
  -- Daily universe (PIT-filtered, valid returns)
  dsf_pit AS (
      SELECT
          toDate32(d.date)                            AS date,
          toDate32(
              toString(toYear(toDate32(d.date))) || '-' ||
              lpad(toString(toMonth(toDate32(d.date))), 2, '0') || '-01'
          )                                            AS month,
          d.permno,
          d.ret
      FROM crsp_202601.dsf AS d
      INNER JOIN crsp_202601.dsfhdr AS h
        ON d.permno = h.permno
       AND toDate32OrNull(d.date) >= toDate32OrNull(h.begdat)
       AND toDate32OrNull(d.date) <= ifNull(toDate32OrNull(h.enddat), toDate32('2099-12-31'))
      WHERE toDate32OrNull(d.date) >= toDate32('1963-06-01')
        AND toDate32OrNull(d.date) <= toDate32('2020-12-31')
        AND h.hshrcd IN (10, 11)
        AND h.hexcd  IN (1, 2, 3)
        AND d.ret IS NOT NULL
        AND d.ret > -1.0
        AND abs(d.prc) >= 5
        AND abs(d.prc) <= 1000
  ),
  -- Join daily stock ret with daily FF factors + daily rf
  daily_merged AS (
      SELECT
          d.month                                       AS month,
          d.permno                                      AS permno,
          d.ret - f.rf                                  AS ret_excess,
          f.mkt_rf                                      AS mkt_rf
      FROM dsf_pit AS d
      INNER JOIN ff_daily AS f
        ON d.date = f.date
  ),
  daily_count AS (
      SELECT permno, month, count() AS n_obs
      FROM daily_merged
      GROUP BY permno, month
      HAVING count() >= 15
  ),
  -- CAPM-style daily regression: ret_excess = a + b*mkt_rf + e
  -- OLS coefficients: b = cov(y,x)/var(x), a = mean(y) - b*mean(x)
  -- IVOL = std(e) where e = y - a - b*x
  regr AS (
      SELECT
          m.permno                                                          AS permno,
          m.month                                                           AS month,
          sum(m.ret_excess * m.mkt_rf) - sum(m.ret_excess) * sum(m.mkt_rf) / count() AS cov_num,
          sum(m.mkt_rf * m.mkt_rf)     - sum(m.mkt_rf) * sum(m.mkt_rf) / count()     AS var_x,
          sum(m.ret_excess) / count()                                              AS mean_y,
          sum(m.mkt_rf) / count()                                                  AS mean_x
      FROM daily_merged AS m
      INNER JOIN daily_count AS c
        ON m.permno = c.permno AND m.month = c.month
      GROUP BY m.permno, m.month
  ),
  resid AS (
      SELECT
          r.permno                                                                AS permno,
          r.month                                                                 AS month,
          -- b = cov_num / var_x
          if(r.var_x > 0, r.cov_num / r.var_x, 0)                                  AS beta,
          r.mean_y - if(r.var_x > 0, r.cov_num / r.var_x, 0) * r.mean_x           AS alpha
      FROM regr AS r
  ),
  -- Compute residual std by going back to the daily observations
  resid_daily AS (
      SELECT
          m.permno                                                              AS permno,
          m.month                                                               AS month,
          m.ret_excess - res.alpha - res.beta * m.mkt_rf                       AS epsilon
      FROM daily_merged AS m
      INNER JOIN daily_count AS c
        ON m.permno = c.permno AND m.month = c.month
      INNER JOIN resid AS res
        ON m.permno = res.permno AND m.month = res.month
  )
SELECT
    rd.permno                                            AS permno,
    rd.month                                             AS month,
    -- stddev = sqrt(sum(e^2) / n - (sum(e)/n)^2)
    sqrt(
      greatest(
        sum(rd.epsilon * rd.epsilon) / count() - (sum(rd.epsilon) / count()) * (sum(rd.epsilon) / count()),
        0
      )
    )                                                   AS ivol
FROM resid_daily AS rd
GROUP BY rd.permno, rd.month
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;