-- delist_diagnostic.sql
-- Purpose: Assumption-4 diagnostic. For performance-related delistings
--          (dlstcd >= 500) in 1980-1999, pull the msf return of the
--          delisting month (and the prior month) together with
--          msedelist.dlret, so we can test whether msf.ret in the
--          delisting month already embeds the delisting return or
--          excludes it.
-- Tables: crsp_202601.msedelist, crsp_202601.msf
-- Output columns: permno, dlstdt, dlstcd, dlret, msf_date, msf_ret, prior_ret
-- Depends on: (none)
-- Notes: msf.date is the last TRADING day of the month, so the join is on
--        the (year, month) tuple, not on calendar month-end. dlstdt is a
--        String; parse with toDate32OrNull (pre-1970 safety).
SELECT
    e.permno   AS permno,
    e.dlstdt,
    e.dlstcd,
    e.dlret,
    m.date     AS msf_date,
    m.ret      AS msf_ret,
    p.ret      AS prior_ret
FROM crsp_202601.msedelist AS e
LEFT JOIN crsp_202601.msf AS m
       ON m.permno = e.permno
      AND toYear(toDate32OrNull(m.date)) = toYear(toDate32OrNull(e.dlstdt))
      AND toMonth(toDate32OrNull(m.date)) = toMonth(toDate32OrNull(e.dlstdt))
LEFT JOIN crsp_202601.msf AS p
       ON p.permno = e.permno
      AND toInt64(toYear(toDate32OrNull(p.date))) * 12
          + toInt64(toMonth(toDate32OrNull(p.date)))
        = toInt64(toYear(toDate32OrNull(e.dlstdt))) * 12
          + toInt64(toMonth(toDate32OrNull(e.dlstdt))) - 1
WHERE e.dlstcd >= 500
  AND e.dlstdt >= '1980-01-01'
  AND e.dlstdt <= '1999-12-31'
  AND e.dlret IS NOT NULL
  AND abs(e.dlret) > 0.001          -- focus on nonzero delisting returns
LIMIT 20000
SETTINGS max_execution_time = 600,
         join_algorithm = 'partial_merge',
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;
