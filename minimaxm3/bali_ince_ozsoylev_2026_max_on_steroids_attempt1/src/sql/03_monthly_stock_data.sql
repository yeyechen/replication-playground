-- 03_monthly_stock_data.sql
-- Purpose: Per (permno, month) CRSP stock-level data after PIT universe filter
--          - ret, retx, prc, shrout, vol
--          - me = abs(prc) * shrout / 1000  (in $millions; shrout is in thousands)
--          - Includes only stocks with >=15 daily observations in month
-- Tables: crsp_202601.dsf, crsp_202601.dsenames
-- Output columns: permno, month, ret, retx, prc, shrout, vol, me
-- Depends on: (none — built independently)
-- Notes:
--   - Uses dsf (daily) aggregated to month-end for sample-period consistency.
--     msf is the pre-aggregated monthly file but its date is already
--     month-end and matches the LAST trading day of the month.
--   - Apply 15-day-obs count filter via the daily_obs_count computed here.
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
WITH daily AS (
    SELECT
        d.permno                          AS permno,
        toDate32(d.date)                  AS date,
        d.ret                             AS ret,
        d.retx                            AS retx,
        d.prc                             AS prc,
        d.shrout                          AS shrout,
        d.vol                             AS vol,
        n.siccd                           AS siccd
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
),
agg AS (
    SELECT
        permno,
        toLastDayOfMonth(date)            AS month,
        count(ret)                        AS daily_obs_count,
        -- Use last available prc/shrout/vol/retx/ret in month (last trading day)
        argMax(ret, date)                AS ret,
        argMax(retx, date)               AS retx,
        argMax(prc, date)                AS prc,
        argMax(shrout, date)             AS shrout,
        sum(vol)                         AS vol
    FROM daily
    GROUP BY permno, toLastDayOfMonth(date)
)
SELECT
    permno,
    month,
    ret,
    retx,
    prc,
    shrout,
    vol,
    if(daily_obs_count >= 15,
       abs(prc) * shrout / 1000.0,
       NULL)                             AS me
FROM agg
WHERE daily_obs_count >= 15
