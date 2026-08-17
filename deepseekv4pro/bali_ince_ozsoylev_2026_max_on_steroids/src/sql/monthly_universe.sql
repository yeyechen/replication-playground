-- monthly_universe.sql
-- Purpose: PIT-filtered monthly stock data + market equity (1966-01 .. 2022-12).
--   Same universe filters as daily_universe.sql (hshrcd/hexcd/hsiccd PIT via
--   dsfhdr validity windows). Month-end price screen abs(prc) >= 5.
--   me = abs(prc) * shrout * 1000  (dollars; shrout in thousands, prc signed).
-- Tables: crsp_202601.msf, crsp_202601.dsfhdr
-- Output columns: permno, date, ret, prc, shrout, me
-- Depends on: (none)
-- Produces: feeds panel assembly (data/panel.parquet) for ret, me, me growth
-- Settings: join_algorithm=partial_merge, max_execution_time=600
SELECT
    m.permno  AS permno,
    m.date    AS date,
    m.ret     AS ret,
    m.prc     AS prc,
    m.shrout  AS shrout,
    abs(m.prc) * m.shrout * 1000 AS me
FROM crsp_202601.msf AS m
INNER JOIN crsp_202601.dsfhdr AS h
        ON m.permno = h.permno
       AND m.date >= h.begdat
       AND m.date <= h.enddat
WHERE m.date >= '1966-01-01'
  AND m.date <= '2022-12-31'
  AND h.hshrcd IN (10, 11)
  AND h.hexcd  IN (1, 2, 3)
  AND NOT (h.hsiccd >= 4900 AND h.hsiccd <= 4949)
  AND NOT (h.hsiccd >= 6000 AND h.hsiccd <= 6999)
  AND m.ret IS NOT NULL
  AND m.ret > -50
  AND abs(m.prc) >= 5
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 20000000000,
         timeout_before_checking_execution_speed = 0
