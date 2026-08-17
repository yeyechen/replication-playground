-- 04_beta_ivol.sql
-- Purpose: Per-stock daily BETA and IVOL via 252-day rolling regression of
--          stock excess return on market excess return.
-- Tables:  crsp_202601.dsf, crsp_202601.dsenames, crsp_202601.dsi,
--          ff.four_factor_monthly
-- Output columns: permno, trade_date, BETA, IVOL
-- Notes:
--   * BETA = covarPop(stock_excess, market_excess) / varPop(market_excess)
--             over a 252-day rolling window (paper Section 3.3).
--   * IVOL = stddevPop of regression residuals over the same window
--             (paper Section 3.3).
--   * The paper uses daily excess returns; we replicate with
--             stock_excess = dsf.ret - rf_daily
--             market_excess = dsi.vwretd - rf_daily
--     Since rf_daily is the same for stock and market on the same day,
--     the slope coefficient is identical to regressing raw ret on raw
--     vwretd (the constant cancels).
-- Depends on: 01_universe_daily.sql, 03_market_index.sql

WITH
universe AS (
    SELECT
        d.permno                                AS permno,
        toDate32OrNull(d.date)                  AS trade_date,
        d.ret                                   AS ret
    FROM crsp_202601.dsf AS d
    INNER JOIN crsp_202601.dsenames AS n
        ON d.permno = n.permno
       AND toDate32OrNull(d.date) >= toDate32OrNull(n.namedt)
       AND toDate32OrNull(d.date) <= ifNull(toDate32OrNull(n.nameendt),
                                           toDate32('2099-12-31'))
    WHERE toDate32OrNull(d.date) >= toDate32('1968-01-01')
      AND toDate32OrNull(d.date) <= toDate32('2022-12-31')
      AND n.shrcd  IN (10, 11)
      AND n.exchcd IN (1, 2, 3)
      AND d.ret IS NOT NULL
      AND d.ret > -0.5
      AND (n.siccd < 4900 OR n.siccd > 4949)
      AND (n.siccd < 6000 OR n.siccd > 6999)
),
rf_m AS (
    SELECT
        toDate32(dt)                            AS month_end,
        rf / 21.0                               AS rf_daily
    FROM ff.four_factor_monthly
    WHERE toDate32OrNull(dt) >= toDate32('1967-01-01')
      AND toDate32OrNull(dt) <= toDate32('2023-12-31')
),
mkt AS (
    SELECT
        toDate32OrNull(date)                    AS mkt_date,
        vwretd                                  AS vwretd
    FROM crsp_202601.dsi
    WHERE toDate32OrNull(date) >= toDate32('1968-01-01')
      AND toDate32OrNull(date) <= toDate32('2022-12-31')
),
excess AS (
    SELECT
        u.permno                                       AS permno,
        u.trade_date                                   AS trade_date,
        u.ret - r.rf_daily                             AS stock_excess,
        m.vwretd - r.rf_daily                          AS market_excess
    FROM universe AS u
    INNER JOIN mkt AS m  ON u.trade_date = m.mkt_date
    INNER JOIN rf_m AS r
        ON toDate32(substring(toString(u.trade_date), 1, 7) || '-01')
         = toDate32(substring(toString(r.month_end), 1, 7) || '-01')
),
rolled AS (
    SELECT
        permno, trade_date,
        covarPop(stock_excess, market_excess) OVER w AS cov_xy,
        varPop(market_excess)              OVER w     AS var_x,
        stddevPop(stock_excess)            OVER w     AS sd_y
    FROM excess
    WINDOW w AS (PARTITION BY permno ORDER BY trade_date
                 ROWS BETWEEN 251 PRECEDING AND CURRENT ROW)
)
SELECT
    permno,
    trade_date,
    if(var_x > 0, cov_xy / var_x, NULL)              AS BETA,
    if(var_x > 0,
       sqrt(greatest(
           sd_y * sd_y - (cov_xy * cov_xy) / var_x,
           0.0)),
       NULL)                                         AS IVOL
FROM rolled
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
