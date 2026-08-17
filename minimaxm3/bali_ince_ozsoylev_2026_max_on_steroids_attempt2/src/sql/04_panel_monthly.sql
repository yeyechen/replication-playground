-- 04_panel_monthly.sql
-- Compute the analysis-ready monthly panel with:
--   - MAX signal (avg of top-5 daily returns per stock-month)
--   - BETA (252-day rolling, regressed on equal-weighted daily market return)
--   - IVOL (252-day rolling std of residuals)
--   - RET (monthly return) + market cap
-- Universe: shrcd 10/11, exchcd 1/2/3, price >= $5, SIC exclusions, 15 daily obs

-- Step 1: build the universe-filtered daily panel with stock & market returns
WITH
    daily_universe AS (
        SELECT
            d.permno,
            toDate(d.date) AS date,
            toYYYYMM(toDate(d.date)) AS month,
            d.ret,
            m.shrcd,
            m.exchcd,
            m.siccd
        FROM crsp_202601.dsf d
        INNER JOIN crsp_202601.dsenames m
            ON d.permno = m.permno
            AND toDate(d.date) >= toDate(m.namedt)
            AND (toDate(m.nameendt) = '1970-01-01' OR toDate(m.nameendt) >= toDate(d.date))
        WHERE toDate(d.date) >= '1967-01-01'
          AND toDate(d.date) <= '2022-12-31'
          AND d.ret IS NOT NULL AND d.ret > -1.0
          AND m.shrcd IN (10, 11)
          AND m.exchcd IN (1, 2, 3)
          AND abs(d.prc) >= 5.0
          AND NOT (m.siccd BETWEEN 4900 AND 4949)
          AND NOT (m.siccd BETWEEN 6000 AND 6999)
    ),
    -- Daily equal-weighted market return (EW index of all stocks in universe)
    daily_mkt AS (
        SELECT
            date,
            avg(ret) AS mkt_ret
        FROM daily_universe
        GROUP BY date
    ),
    -- Combine stock and market returns
    stock_and_mkt AS (
        SELECT
            u.permno,
            u.date,
            u.month,
            u.ret AS stock_ret,
            m.mkt_ret
        FROM daily_universe u
        INNER JOIN daily_mkt m ON u.date = m.date
    ),
    -- Per-stock rolling sums (for beta & IVOL computation)
    rolling_stats AS (
        SELECT
            permno,
            date,
            month,
            stock_ret,
            mkt_ret,
            -- 252-day rolling sum of mkt_ret, sum of mkt_ret^2, etc.
            sum(mkt_ret) OVER w AS sx,
            sum(mkt_ret * mkt_ret) OVER w AS sxx,
            sum(stock_ret) OVER w AS sy,
            sum(stock_ret * stock_ret) OVER w AS syy,
            sum(stock_ret * mkt_ret) OVER w AS sxy,
            count(*) OVER w AS nw
        FROM stock_and_mkt
        WINDOW w AS (PARTITION BY permno ORDER BY date ROWS BETWEEN 251 PRECEDING AND CURRENT ROW)
    )
SELECT
    permno,
    month,
    -- Beta = cov / var_mkt
    (sxy / nw - (sx / nw) * (sy / nw)) / (sxx / nw - (sx / nw) * (sx / nw)) AS beta_252,
    -- IVOL = sqrt(var_resid)
    sqrt(max(0, (syy / nw - (sy / nw) * (sy / nw)) -
              pow((sxy / nw - (sx / nw) * (sy / nw)), 2) /
              (sxx / nw - (sx / nw) * (sx / nw)))) AS ivol_252,
    stock_ret
FROM rolling_stats
WHERE nw >= 200
SETTINGS max_execution_time = 1800,
         max_rows_to_read = 50000000000,
         max_memory_usage = 50000000000,
         timeout_before_checking_execution_speed = 0
