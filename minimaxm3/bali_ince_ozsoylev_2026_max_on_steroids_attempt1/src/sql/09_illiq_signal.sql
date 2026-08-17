-- 09_illiq_signal.sql
-- Purpose: Monthly Amihud illiquidity = avg of (|ret| / (prc*vol)) over the month,
--          scaled by 1e6. CRSP prc is signed (negative for bid/ask avg) so we
--          use abs(prc).
-- Tables: crsp_202601.dsf, crsp_202601.dsenames
-- Output columns: permno, month, illiq
-- Depends on: (none)
-- Notes:
--   - Per paper: illiq_t = (1/D_t) * sum_d (|ret_d| / (PRC_d * VOL_d)) * 1e6
--     where D_t is the number of valid (non-NULL, non-zero denom) days.
--   - Apply the 15-daily-obs minimum as a sanity filter on this aggregate too
--     (matches the universe filter applied elsewhere in the pipeline).
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
WITH daily AS (
    SELECT
        d.permno                                                          AS permno,
        toLastDayOfMonth(toDate32(d.date))                                 AS month,
        d.ret                                                             AS ret,
        d.prc                                                             AS prc,
        d.vol                                                             AS vol
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
)
SELECT
    permno,
    month,
    sum(abs(ret) / nullIf(abs(prc) * vol, 0)) / count(ret) * 1e6         AS illiq
FROM daily
GROUP BY permno, month
HAVING count(ret) >= 15
