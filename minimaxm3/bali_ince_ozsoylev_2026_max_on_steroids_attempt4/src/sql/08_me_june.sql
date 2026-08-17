-- 08_me_june.sql
-- Purpose: Pull the June ME snapshot per permno for the "carry-forward" June-t
--          convention used by Fama-French (1993) and Bali-Cakici-Whitelaw (2011).
-- Tables:  crsp_202601.msf (month-end), crsp_202601.dsenames (PIT exchange/SIC filter)
-- Output columns: permno, june_month, ME_june
-- Depends on: (none — direct query)
--
-- Convention: Universe filter matches the panel: shrcd 10/11, exchcd 1/2/3,
-- SIC 4900-4949 and 6000-6999 excluded, prc and shrout > 0.
--
-- `june_month` is the calendar June that the snapshot ME belongs to.
-- For a (permno, any-month-t), the carry-forward convention applies:
--   if month is July-Dec of year Y: use the June of year Y (june_month = Y-06-01)
--   if month is Jan-June of year Y: use the June of year Y-1 (june_month = Y-1, 06-01)
-- This file only emits the (permno, june_month, ME_june) tuples; the assignment
-- to each (permno, month) is done in Python (rebuild_panel_june.py) using the
-- rule above.
--
-- Settings: max_execution_time = 300, max_rows_to_read = 10B.

SELECT
    m.permno                                          AS permno,
    toUInt16(toYear(toDate32OrNull(m.date))) * 100
        + toUInt8(6)                                  AS ym_key,
    toDate32(toString(toYear(toDate32OrNull(m.date)))
        || '-06-01')                                  AS june_month,
    abs(m.prc) * m.shrout * 1000.0                     AS ME_june
FROM crsp_202601.msf AS m
INNER JOIN crsp_202601.dsenames AS n
    ON m.permno = n.permno
   AND toDate32OrNull(m.date) >= toDate32OrNull(n.namedt)
   AND toDate32OrNull(m.date) <= ifNull(toDate32OrNull(n.nameendt),
                                       toDate32('2099-12-31'))
WHERE toUInt8(toMonth(toDate32OrNull(m.date))) = 6
  AND toDate32OrNull(m.date) >= toDate32('1967-06-01')
  AND toDate32OrNull(m.date) <= toDate32('2022-06-30')
  AND n.shrcd  IN (10, 11)
  AND n.exchcd IN (1, 2, 3)
  AND (n.siccd < 4900 OR n.siccd > 4949)
  AND (n.siccd < 6000 OR n.siccd > 6999)
  AND m.prc IS NOT NULL
  AND m.shrout IS NOT NULL
  AND abs(m.prc) > 0
  AND m.shrout > 0
SETTINGS max_execution_time = 300,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
