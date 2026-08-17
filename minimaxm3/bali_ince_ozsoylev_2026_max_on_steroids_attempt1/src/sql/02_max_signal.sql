-- 02_max_signal.sql
-- Purpose: MAX(5) signal = average of 5 highest daily returns in month t
--          + daily_obs_count (>=15 required)
-- Tables: depends on 01_universe_filtered_daily
-- Output columns: permno, month (last trading day), max_5, daily_obs_count
-- Depends on: 01_universe_filtered_daily.sql (built inline)
-- Notes:
--   - MAX = avg of top-5 daily returns; less than 5 daily obs => NULL
--   - Month label = last trading day of the month (matching CRSP dsf.date convention)
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
WITH daily AS (
    SELECT
        d.permno                                 AS permno,
        toDate32(d.date)                         AS date,
        d.ret                                    AS ret
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
ranked AS (
    SELECT
        permno,
        date,
        toLastDayOfMonth(date)              AS month_eom,
        ret,
        row_number() OVER (
            PARTITION BY permno, toLastDayOfMonth(date)
            ORDER BY ret DESC, date ASC
        )                                    AS rn
    FROM daily
)
SELECT
    permno,
    max(month_eom)                          AS month,
    if(countIf(rn <= 5, ret, NULL) = 5,
       sumIf(ret, rn <= 5) / 5.0,
       NULL)                                AS max_5,
    count(ret)                              AS daily_obs_count
FROM ranked
GROUP BY permno, month_eom
