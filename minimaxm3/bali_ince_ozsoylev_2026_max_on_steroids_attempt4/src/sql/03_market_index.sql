-- 03_market_index.sql
-- Purpose: Build the daily market excess return series used for BETA / IVOL.
-- Tables:  crsp_202601.dsi (daily VW market return)
--          ff.four_factor_monthly (calendar-month-end risk-free rate)
-- Output columns: date, vwretd, rf_daily
-- Notes:
--   * Subtract rf/21 (a per-trading-day split of the monthly rf) from the
--     CRSP VW return to form the market excess return. The exact same
--     subtraction is applied to the stock excess return (in 04_beta_ivol.sql)
--     so the resulting beta is identical to regressing raw returns on raw
--     returns with an intercept (the constant cancels in slope).
--   * ff.four_factor_monthly.dt is calendar month-end; CRSP dsi.date is
--     trading-day-end. Project both sides to year-month for the join.
-- Depends on: (none)

WITH
rf_m AS (
    SELECT
        toDate32(dt)                                  AS month_end,
        toFloat64OrZero(rf) / 21.0                    AS rf_daily
    FROM ff.four_factor_monthly
    WHERE toDate32OrNull(dt) >= toDate32('1967-01-01')
      AND toDate32OrNull(dt) <= toDate32('2023-12-31')
),
dsi AS (
    SELECT
        toDate32OrNull(date)                          AS date,
        toFloat64OrNull(vwretd)                       AS vwretd
    FROM crsp_202601.dsi
    WHERE toDate32OrNull(date) >= toDate32('1968-01-01')
      AND toDate32OrNull(date) <= toDate32('2022-12-31')
)
SELECT
    d.date                                            AS date,
    d.vwretd                                          AS vwretd,
    r.rf_daily                                        AS rf_daily,
    d.vwretd - r.rf_daily                             AS vwretd_excess
FROM dsi AS d
INNER JOIN rf_m AS r
    ON toStartOfMonth(d.date) = toStartOfMonth(r.month_end)
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
