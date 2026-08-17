-- market_totval.sql
-- Purpose: Monthly CRSP market aggregates for the distress (CHS 2008) inputs:
--   * vwretd_m = monthly value-weighted market return (compounded daily vwretd)
--     -> for EXRET = log(1+ret) - log(1+vwretd)
--   * totval   = total CRSP market cap (dsi.totval, month-end) -> for the RSIZE
--     term, as the proxy for the S&P 500 aggregate market value (documented
--     proxy — see Assumption 13 / task note).
-- Tables: crsp_202601.dsi
-- Output columns: month, vwretd_m, totval
-- Depends on: (none)
-- Settings: max_execution_time=300
SELECT
    mo AS month,
    max(totval) AS totval,
    exp(sum(log1p(ifNull(vwretd, 0) + 0.0))) - 1 AS vwretd_m
FROM (
    SELECT
        toStartOfMonth(toDate32(date)) AS mo,
        toDate32(date) AS d,
        vwretd AS vwretd,
        totval AS totval,
        argMax(totval, date) OVER (PARTITION BY toStartOfMonth(toDate32(date))) AS _m_end
    FROM crsp_202601.dsi
    WHERE date >= '1967-01-01'
      AND date <= '2022-12-31'
)
GROUP BY mo
SETTINGS max_execution_time = 300,
         max_rows_to_read = 10000000,
         timeout_before_checking_execution_speed = 0
