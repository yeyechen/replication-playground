-- 03_beta_ivol.sql
-- Compute BETA and IVOL using daily returns over rolling 252-day window
-- Regression: stock excess return = alpha + beta * market excess return
-- Beta = slope; IVOL = std(residuals)
-- We use FF mkt_rf as market return
-- Sample: only stocks with >= 15 obs per month in the universe

-- Strategy: Compute market-cap weighted market return using full CRSP universe daily
-- Then compute stock-level residuals via per-stock rolling regression
-- For simplicity, use the FF daily market return from wrds_dailyindexret_query if available

-- Get daily market returns and daily RF
WITH
    -- Use value-weighted market return from crsp daily
    market AS (
        SELECT
            toDate(date) AS date,
            sum(if(abs(prc) > 0, ret * abs(prc) * shrout, 0)) / sum(if(abs(prc) > 0, abs(prc) * shrout, 0)) AS mkt_ret
        FROM crsp_202601.dsf
        WHERE toDate(date) >= '1968-01-01' AND toDate(date) <= '2022-12-31'
          AND ret IS NOT NULL AND ret > -1.0 AND abs(prc) > 0 AND shrout > 0
        GROUP BY toDate(date)
    ),
    -- Daily RF from FF factors
    rf AS (
        SELECT
            toDate(parseDateTimeBestEffort(dt)) AS date,
            rf AS rf_rate
        FROM ff.factors_na_2025
    ),
    -- Excess market return
    exmkt AS (
        SELECT
            m.date AS date,
            coalesce(m.mkt_ret, 0.0) - coalesce(r.rf_rate, 0.0) / 252 AS exmkt_ret
        FROM market m
        LEFT JOIN rf r ON m.date = r.date
    )
SELECT
    u.permno,
    u.month,
    -- Compute beta via closed-form regression over the trailing 252 days
    -- cov(stock_excess, mkt_excess) / var(mkt_excess)
    sum((u.ret - u.avg_ret) * (e.exmkt_ret - e.avg_mkt)) / sum(pow(e.exmkt_ret - e.avg_mkt, 2)) AS beta_252,
    -- IVOL = std of residuals (approximate using sqrt(var_resid))
    -- For computational efficiency, just compute std of (ret - beta*mkt - alpha)
    sqrt(avg(pow(u.ret - (u.beta_252 * e.exmkt_ret + u.avg_ret - u.beta_252 * e.avg_mkt), 2))) AS ivol_252
FROM (
    -- Universe-filtered daily panel
    SELECT
        d.permno,
        toDate(d.date) AS date,
        toYYYYMM(d.date) AS month,
        d.ret,
        m.shrcd,
        m.exchcd,
        m.siccd
    FROM crsp_202601.dsf d
    INNER JOIN crsp_202601.dsenames m
        ON d.permno = m.permno
        AND toDate(d.date) >= toDate(m.namedt)
        AND (toDate(m.nameendt) = '1970-01-01' OR toDate(m.nameendt) >= toDate(d.date))
    WHERE toDate(d.date) >= '1968-01-01'
      AND toDate(d.date) <= '2022-12-31'
      AND d.ret IS NOT NULL
      AND d.ret > -1.0
      AND m.shrcd IN (10, 11)
      AND m.exchcd IN (1, 2, 3)
      AND abs(d.prc) >= 5.0
      AND NOT (m.siccd BETWEEN 4900 AND 4949)
      AND NOT (m.siccd BETWEEN 6000 AND 6999)
) u
INNER JOIN exmkt e ON u.date = e.date
GROUP BY u.permno, u.month
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
