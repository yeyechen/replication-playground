-- ff_factors.sql
-- Purpose: Fama-French four-factor monthly series (Mkt-RF, SMB, HML, MOM, RF)
--   for the factor regressions of Tables 2 and 3 and the UMD sanity anchor.
--   ff.dt is calendar month-end, matching the panel's toLastDayOfMonth(month).
-- Tables: ff.four_factor_monthly
-- Output columns: dt, mkt_rf, smb, hml, mom, rf
-- Depends on: (none)
SELECT dt, mkt_rf, smb, hml, mom, rf
FROM ff.four_factor_monthly
WHERE dt >= '1927-01-01' AND dt <= '2010-12-31'
SETTINGS max_execution_time = 300;
