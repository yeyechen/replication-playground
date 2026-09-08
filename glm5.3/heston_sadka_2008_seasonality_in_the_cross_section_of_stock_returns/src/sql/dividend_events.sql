-- dividend_events.sql
-- Purpose: Table 8 CRSP distribution event months.
--   Panel B (pb): dividend-announcement months = calendar month of
--                 msedist.dclrdt, cash dividends (distcd 1200-1299).
--   Panel C (pc): ex-dividend months = calendar month of msedist.exdt
--                 (same distcd filter).
-- Tables: crsp_202601.msedist
-- Output columns: panel ('pb'|'pc'), permno, event_month (Date32, month start)
-- Depends on: (none)
-- Settings: max_execution_time=600
SELECT DISTINCT 'pb' AS panel, permno,
               toStartOfMonth(toDate32(dclrdt)) AS event_month
FROM crsp_202601.msedist
WHERE distcd BETWEEN 1200 AND 1299
  AND dclrdt IS NOT NULL
  AND toDate32(dclrdt) <= toDate32('2002-12-31')
UNION ALL
SELECT DISTINCT 'pc' AS panel, permno,
               toStartOfMonth(toDate32(exdt)) AS event_month
FROM crsp_202601.msedist
WHERE distcd BETWEEN 1200 AND 1299
  AND exdt IS NOT NULL
  AND toDate32(exdt) <= toDate32('2002-12-31')
SETTINGS max_execution_time = 600, max_rows_to_read = 10000000000
