-- 01_universe_filtered_daily.sql
-- Purpose: PIT-filtered daily returns for MAX signal construction
-- Tables: crsp_202601.dsf, crsp_202601.dsenames
-- Output columns: permno, date, ret, prc, shrout, vol, siccd
-- Filters: shrcd IN (10,11), exchcd IN (1,2,3), prc >= 5 (abs),
--          SIC exclusion: not (4900-4949) and not (6000-6999),
--          sample period 1968-01-01 to 2022-12-31, ret > -1.0 (sentinel)
-- Depends on: (none)
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
SELECT
    d.permno                AS permno,
    toDate32(d.date)        AS date,
    d.ret                   AS ret,
    d.retx                  AS retx,
    d.prc                   AS prc,
    d.shrout                AS shrout,
    d.vol                   AS vol,
    n.siccd                 AS siccd
FROM crsp_202601.dsf AS d
INNER JOIN crsp_202601.dsenames AS n
    ON d.permno = n.permno
   AND toDate32(d.date) >= toDate32(n.namedt)
   AND toDate32(d.date) <= ifNull(toDate32(n.nameendt), toDate32('2099-12-31'))
WHERE d.ret > -1.0
  AND abs(d.prc) >= 5
  AND n.shrcd IN (10, 11)
  AND n.exchcd IN (1, 2, 3)
  AND (n.siccd < 4900 OR n.siccd > 4949)
  AND (n.siccd < 6000 OR n.siccd > 6999)
  AND toDate32(d.date) BETWEEN toDate32('1968-01-01') AND toDate32('2022-12-31')
