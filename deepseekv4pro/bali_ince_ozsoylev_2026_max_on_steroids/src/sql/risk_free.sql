-- risk_free.sql
-- Purpose: daily and monthly risk-free rate for beta/IVOL regressions and excess
--   returns. Daily rf from ff.four_factor (daily); monthly rf from
--   ff.four_factor_monthly. Daily rf aligned to CRSP trading-day `date`; monthly
--   rf aligned on calendar (year, month).
-- Tables: ff.four_factor, ff.four_factor_monthly
-- Output columns: dt_kind, dt, rf
-- Depends on: (none)
-- Settings: (none)
SELECT 'monthly' AS dt_kind, dt AS dt, rf AS rf
FROM ff.four_factor_monthly
WHERE dt >= '1966-01-01' AND dt <= '2022-12-31'
UNION ALL
SELECT 'daily' AS dt_kind, dt AS dt, rf AS rf
FROM ff.four_factor
WHERE dt >= '1966-11-01' AND dt <= '2022-12-31'
SETTINGS max_execution_time = 300,
         max_rows_to_read = 10000000,
         timeout_before_checking_execution_speed = 0
