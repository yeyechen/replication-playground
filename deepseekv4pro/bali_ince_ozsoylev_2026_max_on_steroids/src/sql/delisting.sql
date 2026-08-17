-- delisting.sql
-- Purpose: delisting events with delisting return + code (for delisting-adjusted
--   monthly returns; the paper is silent on delistings, so the standard
--   convention applies: substitute dsedelist.dlret on the delisting month when
--   available, else -0.30 for performance delistings dlstcd >= 500).
-- Tables: crsp_202601.dsedelist
-- Output columns: permno, dlstdt, dlstcd, dlret
-- Depends on: (none)
-- Settings: (none)
SELECT
    permno   AS permno,
    dlstdt   AS dlstdt,
    dlstcd   AS dlstcd,
    dlret    AS dlret
FROM crsp_202601.dsedelist
WHERE dlstdt >= '1966-01-01'
  AND dlstdt <= '2022-12-31'
SETTINGS max_execution_time = 300,
         max_rows_to_read = 10000000,
         timeout_before_checking_execution_speed = 0
