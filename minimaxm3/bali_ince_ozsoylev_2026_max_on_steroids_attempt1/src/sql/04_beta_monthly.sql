-- 04_beta_monthly.sql
-- Purpose: Monthly average of daily beta from ea_oneoff.dsf_beta_252.
-- Tables: ea_oneoff.dsf_beta_252
-- Output columns: permno, month, beta_m
-- Depends on: (none)
-- Notes:
--   - security_id == permno in this table.
--   - Aggregate daily beta to monthly MEAN (more robust than last-day
--     argMax which is noisy for illiquid stocks).
--   - Filter to plausible beta range [-5, 10] inside SQL to drop outliers.
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
SELECT
    security_id                                     AS permno,
    toLastDayOfMonth(toDate32(dt))                  AS month,
    avg(if(beta_mktrf BETWEEN -5 AND 10, beta_mktrf, NULL)) AS beta_m
FROM ea_oneoff.dsf_beta_252
WHERE toDate32(dt) BETWEEN toDate32('2002-01-01') AND toDate32('2022-12-31')
GROUP BY security_id, toLastDayOfMonth(toDate32(dt))
