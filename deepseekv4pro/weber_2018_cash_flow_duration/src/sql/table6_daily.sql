-- table6_daily.sql
-- Purpose: Daily equal-weighted portfolio returns for the 10 duration-decile
--          portfolios (D1..D10), ONE row per (date, bin). The D1-D10 long-short
--          daily series is formed in Python as (daily D1 - daily D10).
--          Portfolio membership is fixed within a sort year: a member (permno)
--          enters the portfolio bin for every trading day in its July-t..June-(t+1)
--          cohort. Daily EW = mean of constituent daily returns on that day,
--          skipping missing/sentinel returns.
-- Tables: crsp_202601.dsf, temp table t6_members
-- Output columns: date (Date32), bin (UInt8), ew_ret (Float64)
-- Depends on: t6_members temp table (permno, sort_year, bin) inserted by table6.py
-- Settings: join_algorithm=partial_merge, max_execution_time=600
--
-- Formation labeling (FF-style, matches panel.sql): a calendar trading day belongs
-- to sort_year = if(month>=7, year, year-1). Joining dsf to membership on
-- (permno, sort_year label) places each day's return in exactly one cohort.

SELECT
    toDate32(d.date) AS date,
    m.bin AS bin,
    avg(d.ret) AS ew_ret
FROM crsp_202601.dsf AS d
INNER JOIN t6_members AS m
    ON d.permno = m.permno
   AND if(toMonth(toDate32(d.date)) >= 7,
          toYear(toDate32(d.date)),
          toYear(toDate32(d.date)) - 1) = m.sort_year
WHERE toDate32(d.date) >= toDate32('1962-07-01')
  AND toDate32(d.date) <= toDate32('2014-06-30')
  AND d.ret IS NOT NULL
  AND d.ret > -1.0
GROUP BY date, bin
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
