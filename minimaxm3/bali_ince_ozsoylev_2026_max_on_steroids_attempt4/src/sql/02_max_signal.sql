-- 02_max_signal.sql
-- Purpose: Monthly MAX signal — average of the five highest daily returns
--          in a calendar month for each (permno, month).
-- Tables:  crsp_202601.dsf, crsp_202601.dsenames (CTE inlined)
-- Output columns: permno, month (Date32), MAX (Float64, decimal), ndays (UInt32)
-- Filter rules applied here:
--   * ndays_in_month >= 15 (paper Section 3.1)
--   * month-end prc >= $5 (paper Section 3.1)
-- Notes:
--   * ret is decimal; MAX is decimal. Reporters multiply by 100 to get %.
--   * arrayReverseSort then arraySlice grabs the top 5 values.
--   * If fewer than 5 valid daily returns exist, MAX is NULL.
-- Depends on: 01_universe_daily.sql
-- IMPORTANT: ClickHouse's `toStartOfMonth` does NOT accept Date32. We use
-- `toDate32(substring(toString(trade_date), 1, 7) || '-01')` to compute
-- month-start without Date clamping (Date32 dates from 1926+ are preserved).

WITH
universe AS (
    -- mirror of 01_universe_daily.sql
    SELECT
        d.permno                                        AS permno,
        toDate32OrNull(d.date)                          AS trade_date,
        d.ret                                           AS ret,
        d.prc                                           AS prc
    FROM crsp_202601.dsf AS d
    INNER JOIN crsp_202601.dsenames AS n
        ON d.permno = n.permno
       AND toDate32OrNull(d.date) >= toDate32OrNull(n.namedt)
       AND toDate32OrNull(d.date) <= ifNull(toDate32OrNull(n.nameendt),
                                           toDate32('2099-12-31'))
    WHERE toDate32OrNull(d.date) >= toDate32('1968-01-01')
      AND toDate32OrNull(d.date) <= toDate32('2022-12-31')
      AND n.shrcd  IN (10, 11)
      AND n.exchcd IN (1, 2, 3)
      AND d.ret IS NOT NULL
      AND d.ret > -0.5
      AND (n.siccd < 4900 OR n.siccd > 4949)
      AND (n.siccd < 6000 OR n.siccd > 6999)
),
monthly AS (
    SELECT
        permno,
        toDate32(substring(toString(trade_date), 1, 7) || '-01') AS month,
        arrayReduce('avg',
                    arraySlice(arrayReverseSort(groupArray(ret)), 1, 5)) AS max_raw,
        count()                                        AS ndays,
        arrayReduce('any',
                    arrayReverseSort(groupArray(prc)))  AS month_end_prc
    FROM universe
    GROUP BY permno, toDate32(substring(toString(trade_date), 1, 7) || '-01') AS month
)
SELECT
    permno,
    month,
    if(ndays >= 5, max_raw, NULL)                     AS MAX,
    ndays,
    month_end_prc
FROM monthly
WHERE ndays >= 15
  AND abs(toFloat64(month_end_prc)) >= 5
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
