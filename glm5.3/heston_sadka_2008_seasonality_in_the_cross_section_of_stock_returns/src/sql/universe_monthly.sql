-- universe_monthly.sql
-- Purpose: Raw monthly CRSP pull for the Heston-Sadka (2008) panel.
--          Returns data back to 1945-01 (formation windows need up to 240
--          lagged months before the first holding month 1965-01). The PIT
--          universe filter (dsfhdr shrcd 10/11, exchcd 1/2) is applied in
--          Python via utils.apply_universe_filter.
-- Tables: crsp_202601.msf
-- Output columns: permno, date, ret, prc, shrout, hexcd, hsiccd
-- Depends on: (none)
-- Notes: msf.date is Nullable(String) in this vintage -> cast with
--        toDate32OrNull. Keep rows with missing ret (needed for formation-
--        month availability logic downstream).
SELECT
    permno,
    toDate32OrNull(date)    AS date,
    ret,
    prc,
    shrout,
    hexcd,
    hsiccd
FROM crsp_202601.msf
WHERE date >= '1945-01-01'
  AND date <= '2002-12-31'
  AND permno IS NOT NULL
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;
