-- 08_coskew.sql
-- Purpose: Compute Harvey-Siddique (2000) co-skewness for each (permno, month)
--          in the analysis panel, rolling over trailing 60 months.
--          coskew_i = E[(R_i - μ_i)(R_m - μ_m)^2] / (σ_i * σ_m^2)
-- Tables:  crsp_202601.msf, ff.four_factor_monthly, write_yeye.arb_panel
-- Output:  write_yeye.arb_coskew (permno, month, coskew)
-- Depends on: 03_panel.sql
-- Notes:
--   - coskew measures the asymmetry of a stock's co-movement with the
--     market; lower coskew = stock returns are more left-skewed with the market.

DROP TABLE IF EXISTS write_yeye.arb_coskew;

CREATE TABLE write_yeye.arb_coskew ENGINE = MergeTree()
ORDER BY (assumeNotNull(month), assumeNotNull(permno)) AS
WITH
  panel_grid AS (
      SELECT DISTINCT permno, month
      FROM write_yeye.arb_panel
  ),
  msf_ret AS (
      SELECT
          toDate32(
              toString(toYear(toDate32(date))) || '-' ||
              lpad(toString(toMonth(toDate32(date))), 2, '0') || '-01'
          )                                          AS month,
          permno,
          ret                                        AS ret
      FROM crsp_202601.msf
      WHERE toDate32(date) >= toDate32('1957-01-01')
        AND toDate32(date) <= toDate32('2020-12-31')
        AND ret IS NOT NULL
        AND ret > -1.0
  ),
  mkt AS (
      SELECT
          toDate32(
              toString(toYear(toDate32OrNull(dt))) || '-' ||
              lpad(toString(toMonth(toDate32OrNull(dt))), 2, '0') || '-01'
          )                                          AS month,
          mkt_rf                                     AS mkt_rf
      FROM ff.four_factor_monthly
      WHERE toDate32OrNull(dt) >= toDate32('1957-01-01')
        AND toDate32OrNull(dt) <= toDate32('2020-12-31')
  ),
  monthly AS (
      SELECT
          r.month                AS month,
          r.permno               AS permno,
          r.ret                  AS ret,
          m.mkt_rf               AS mkt_rf
      FROM msf_ret AS r
      INNER JOIN mkt AS m
        ON r.month = m.month
  ),
  -- Rolling window over trailing 60 months
  rolling AS (
      SELECT
          month                                                        AS month,
          permno                                                       AS permno,
          ret                                                          AS ret,
          mkt_rf                                                       AS mkt_rf,
          count() OVER w                                               AS n_obs,
          sum(ret) OVER w                                              AS sum_y,
          sum(mkt_rf) OVER w                                           AS sum_x,
          sum(ret * ret) OVER w                                        AS sum_yy,
          sum(mkt_rf * mkt_rf) OVER w                                  AS sum_xx,
          sum(ret * mkt_rf) OVER w                                     AS sum_xy,
          sum(ret * mkt_rf * mkt_rf) OVER w                            AS sum_yxx
      FROM monthly
      WINDOW w AS (PARTITION BY permno ORDER BY month
                   ROWS BETWEEN 59 PRECEDING AND CURRENT ROW)
  )
SELECT
    month                                                                                  AS month,
    permno                                                                                 AS permno,
    if(n_obs >= 24,
       -- numerator: centered third cross moment E[(y - μ_y)(x - μ_x)^2]
       -- = (sum_yxx - mean_y*sum_xx - 2*mean_x*sum_xy + n*mean_x^2*mean_y) / n
       -- Denominator: σ_i * σ_m^2
       -- σ_i = sqrt((sum_yy - n * mean_y^2) / (n-1))
       -- σ_m^2 = (sum_xx - n * mean_x^2) / (n-1)
       -- coskew = num / (σ_i * σ_m^2)  = n * num_unscaled / (σ_i_unscaled * σ_m^2_unscaled)
       ((sum_yxx - (sum_y / n_obs) * sum_xx - 2 * (sum_x / n_obs) * sum_xy
         + n_obs * (sum_x / n_obs) * (sum_x / n_obs) * (sum_y / n_obs))
        / n_obs)
       / (sqrt(greatest(sum_yy - (sum_y * sum_y) / n_obs, 0) / (n_obs - 1))
          * greatest(sum_xx - (sum_x * sum_x) / n_obs, 0) / (n_obs - 1)
       ),
       NULL)                                                                               AS coskew
FROM rolling
INNER JOIN panel_grid AS p
  ON rolling.permno = p.permno AND rolling.month = p.month
SETTINGS max_execution_time = 900,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;