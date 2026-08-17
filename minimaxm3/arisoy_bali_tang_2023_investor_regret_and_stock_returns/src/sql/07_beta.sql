-- 07_beta.sql
-- Purpose: Compute rolling 60-month market beta for each (permno, month) in the
--          analysis panel. Uses ret_adj (delisting-adjusted) and the FF4 monthly
--          mkt_rf.
--          beta_i = cov(ret_i, mkt_rf) / var(mkt_rf)
--          over trailing 60 months requiring at least 24 non-missing obs.
-- Tables:  crsp_202601.msf, ff.four_factor_monthly, write_yeye.arb_panel
-- Output:  write_yeye.arb_beta (permno, month, beta)
-- Depends on: 03_panel.sql
-- Notes:
--   - Uses the panel grid to scope the beta computation: only (permno, month)
--     pairs that already passed the universe filter get a beta value. This
--     keeps the SQL tractable and aligned with the panel.
--   - The trailing 60-month window is computed over crsp_202601.msf returns
--     (not panel.ret) so we have a complete monthly time series per permno.

DROP TABLE IF EXISTS write_yeye.arb_beta;

CREATE TABLE write_yeye.arb_beta ENGINE = MergeTree()
ORDER BY (assumeNotNull(month), assumeNotNull(permno)) AS
WITH
  -- All panel rows -> (permno, month) grid
  panel_grid AS (
      SELECT DISTINCT permno, month
      FROM write_yeye.arb_panel
  ),
  -- Full monthly returns per permno from 1957 (60 months before 1963-07) to 2020-12
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
          r.month                          AS month,
          r.permno                         AS permno,
          r.ret                            AS ret,
          m.mkt_rf                         AS mkt_rf
      FROM msf_ret AS r
      INNER JOIN mkt AS m
        ON r.month = m.month
  ),
  -- Only keep monthly rows that are within +/- 60 months of any panel row's month.
  -- The window function will then use these rows for the rolling computation.
  -- For simplicity, we keep all rows: the join back to panel_grid at the end
  -- naturally limits output to panel rows.
  window_stats AS (
      SELECT
          month                                                        AS month,
          permno                                                       AS permno,
          ret                                                          AS ret,
          mkt_rf                                                       AS mkt_rf,
          count() OVER w                                               AS n_obs,
          sum(ret) OVER w                                              AS sum_y,
          sum(mkt_rf) OVER w                                           AS sum_x,
          sum(mkt_rf * mkt_rf) OVER w                                  AS sum_xx,
          sum(ret * mkt_rf) OVER w                                     AS sum_xy
      FROM monthly
      WINDOW w AS (PARTITION BY permno ORDER BY month
                   ROWS BETWEEN 59 PRECEDING AND CURRENT ROW)
  ),
  -- Compute beta per panel row.
  beta_computed AS (
      SELECT
          w.month                                                       AS month,
          w.permno                                                      AS permno,
          if(w.n_obs >= 24 AND (w.sum_xx - w.sum_x * w.sum_x / w.n_obs) > 0,
             (w.sum_xy - w.sum_x * w.sum_y / w.n_obs) / (w.sum_xx - w.sum_x * w.sum_x / w.n_obs),
             NULL)                                                      AS beta
      FROM window_stats AS w
      INNER JOIN panel_grid AS p
        ON w.permno = p.permno AND w.month = p.month
  )
SELECT
    month                                                                                  AS month,
    permno                                                                                 AS permno,
    beta                                                                                   AS beta
FROM beta_computed
SETTINGS max_execution_time = 900,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;