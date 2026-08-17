-- market_max.sql
-- Purpose: Monthly market-level MAX — the mean of the 5 highest daily returns
--   of the CRSP value-weighted market index in each month. This is the
--   "MARKET MAX" used as the independent variable in the beta^MAX 12-month
--   rolling time-series regression (stock MAX on market MAX), NOT the VW
--   cross-sectional mean of individual-stock MAX (that was the pre-Iteration-9
--   approximation). Paper: beta^MAX = 12-month rolling slope of a stock's MAX
--   on the MARKET's MAX, where market MAX = mean of the 5 highest daily
--   market-index (dsi.vwretd) returns in month t.
-- Tables: crsp_202601.dsi
-- Output columns: month, mkt_max
-- Depends on: (none)
-- Settings: max_execution_time=300
SELECT
    toDate32(concat(toString(toYear(toDate32(date))), '-',
                    toString(toMonth(toDate32(date))), '-01')) AS month,
    arrayReduce('avg', arraySlice(arrayReverseSort(groupArray(vwretd)), 1, 5)) AS mkt_max
FROM (
    SELECT
        date AS date,
        vwretd AS vwretd
    FROM crsp_202601.dsi
    WHERE date >= '1967-01-01'
      AND date <= '2022-12-31'
      AND vwretd IS NOT NULL
)
GROUP BY month
SETTINGS max_execution_time = 300,
         max_rows_to_read = 10000000,
         timeout_before_checking_execution_speed = 0
