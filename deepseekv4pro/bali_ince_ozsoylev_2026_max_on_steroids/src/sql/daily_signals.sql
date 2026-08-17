-- daily_signals.sql
-- Purpose: aggregate daily PIT-filtered data to monthly signal components in SQL.
--   * MAX: mean of the 5 highest daily returns in the month (paper L173)
--   * illiq_num: sum over month of |ret| / (abs(prc) * vol)  [dollar volume]
--       (the Amihud numerator, before scaling by 1e6 and averaging; vol in
--       shares — see CRSP.md)
--   * turnover: sum over month of vol / shrout  (for E(ISKEW) later)
--   * nobs: count of non-missing daily returns (for the >=15-obs rule)
--   * prc_end: last (month-end) abs(prc)
-- Monthly bucket = toStartOfMonth(date).
-- Tables: (none — operates on the daily PIT-filtered relation built in
--   daily_universe.sql; the daily relation is pulled once into
--   data/daily_universe.parquet and these aggregations run in ClickHouse here.)
-- Output columns: permno, month, max, illiq_num, turnover, nobs, prc_end
-- Depends on: daily_universe.sql (same PIT filter applied inline)
-- Settings: join_algorithm=partial_merge, max_execution_time=600
WITH daily AS (
    SELECT
        d.permno  AS permno,
        d.date    AS date,
        d.ret     AS ret,
        d.prc     AS prc,
        d.vol     AS vol,
        d.shrout  AS shrout
    FROM crsp_202601.dsf AS d
    INNER JOIN crsp_202601.dsfhdr AS h
            ON d.permno = h.permno
           AND d.date >= h.begdat
           AND d.date <= h.enddat
    WHERE d.date >= '1966-11-01'
      AND d.date <= '2022-12-31'
      AND h.hshrcd IN (10, 11)
      AND h.hexcd  IN (1, 2, 3)
      AND NOT (h.hsiccd >= 4900 AND h.hsiccd <= 4949)
      AND NOT (h.hsiccd >= 6000 AND h.hsiccd <= 6999)
      AND d.ret IS NOT NULL
      AND d.ret > -50
)
SELECT
    permno,
    toStartOfMonth(toDate32(date)) AS month,
    -- MAX: mean of the 5 highest daily returns (paper's definition)
    arrayReduce('avg', arraySlice(arrayReverseSort(groupArray(ret)), 1, 5)) AS max,
    -- Amihud numerator before scaling: sum |ret|/dollar_volume over days
    -- with positive volume (vol > 0, shrout > 0, prc > 0)
    sumIf(abs(ret) / (abs(prc) * vol), vol > 0 AND shrout > 0 AND abs(prc) > 0) AS illiq_num,
    countIf(vol > 0 AND shrout > 0 AND abs(prc) > 0) AS nvol_obs,
    -- turnover: sum vol/shrout over month t (shrout > 0 guard)
    sumIf(vol / shrout, shrout > 0) AS turnover,
    count() AS nobs,
    argMax(abs(prc), date) AS prc_end
FROM daily
GROUP BY permno, toStartOfMonth(toDate32(date))
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 20000000000,
         timeout_before_checking_execution_speed = 0
