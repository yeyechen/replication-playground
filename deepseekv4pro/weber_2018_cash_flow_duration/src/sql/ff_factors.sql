-- ff_factors.sql
-- Purpose: Fama-French factor returns + risk-free rate for the main sample
--          period (July 1963 - June 2014), aligned on calendar month-end.
--          FF3 = Mkt-RF, SMB, HML (from four_factor_monthly); FF4 = + MOM;
--          FF5 = Mkt-RF, SMB, HML, RMW, CMA (from five_factor_monthly).
--          All factors are decimal units (per FAMA_FRENCH.md), matching CRSP ret.
-- Tables: ff.four_factor_monthly, ff.five_factor_monthly
-- Output columns: dt (month-end Date32), mkt_rf, smb, hml, mom, rmw, cma, rf
-- Depends on: (none)
-- Settings: max_execution_time=300
--
-- NOTE: dt is calendar month-end (String 'YYYY-MM-DD', e.g. '1977-07-31').
-- CRSP `date` is trading-day-end. Align in Python on year-month tuple, NOT on
-- exact date (see SKILL.md "FF factor date alignment gotcha").

SELECT
    toDate32(f4.dt) AS dt,
    f4.mkt_rf AS mkt_rf,
    f4.smb   AS smb,
    f4.hml   AS hml,
    f4.mom   AS mom,
    f5.rmw   AS rmw,
    f5.cma   AS cma,
    f4.rf    AS rf
FROM ff.four_factor_monthly AS f4
LEFT JOIN ff.five_factor_monthly AS f5
       ON f4.dt = f5.dt
WHERE toDate32(f4.dt) >= toDate32('1963-07-01')
  AND toDate32(f4.dt) <= toDate32('2014-06-30')
ORDER BY dt
SETTINGS max_execution_time = 300,
         max_rows_to_read = 100000000,
         timeout_before_checking_execution_speed = 0
