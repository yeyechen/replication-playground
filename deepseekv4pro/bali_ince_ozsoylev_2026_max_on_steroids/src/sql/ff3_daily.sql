-- ff3_daily.sql
-- Purpose: Daily Fama-French 3-factor set (mkt_rf, smb, hml) + risk-free rate
--   for the 60-month rolling ISKEW residual regressions (paper §3.3, L193).
--   Stock-level daily excess return is computed in Python as dsf.ret - rf.
-- Tables: ff.four_factor (daily)
-- Output columns: dt, mkt_rf, smb, hml, rf
-- Depends on: (none)
-- Notes: ff.four_factor.dt is a trading-day date (YYYY-MM-DD), strings.
--   Factors are decimals (e.g. 0.02 = 2%), NOT percent. Daily factor rows
--   begin 1926-07-01; null-free over the 1967-01..2022-12 ISKEW window.
SELECT
    toDate32(dt) AS dt,
    mkt_rf       AS mkt_rf,
    smb          AS smb,
    hml          AS hml,
    rf           AS rf
FROM ff.four_factor
WHERE dt >= '1967-01-01'
  AND dt <= '2022-12-31'
ORDER BY dt
SETTINGS max_execution_time = 300,
         max_rows_to_read = 10000000,
         timeout_before_checking_execution_speed = 0
