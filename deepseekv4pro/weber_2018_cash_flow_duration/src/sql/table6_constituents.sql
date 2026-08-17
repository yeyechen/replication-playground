-- table6_constituents.sql
-- Purpose: Raw daily constituent returns (permno-level, with formation-June ME weight)
--          for the 10 duration-decile portfolios, to support the Table 6 RV-series
--          sensitivity grid (T0..T5). Returns ONE row per (permno, date, bin), carrying
--          me_jun so that Python can form BOTH equal-weighted and value-weighted daily
--          portfolio returns, and screen membership on >=15 valid trading days/month.
--          (The production table6_daily.sql emits only the aggregated EW; this file is
--          the diagnostic superset used by src/table6_sensitivity.py.)
-- Tables: crsp_202601.dsf, temp table t6_members (permno, sort_year, bin, me_jun)
-- Output columns: date (Date32), bin (UInt8), permno (Int32), ret (Float64), me_jun (Float64)
-- Depends on: t6_members temp table (permno, sort_year, bin, me_jun) inserted by table6_sensitivity.py
-- Settings: join_algorithm=partial_merge, max_execution_time=600
--
-- Formation labeling (FF-style, matches panel.sql): a calendar trading day belongs
-- to sort_year = if(month>=7, year, year-1). Joining dsf to membership on
-- (permno, sort_year label) places each day's return in exactly one cohort.

SELECT
    toDate32(d.date) AS date,
    m.bin AS bin,
    d.permno AS permno,
    d.ret AS ret,
    m.me_jun AS me_jun
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
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
