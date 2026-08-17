-- 02_max_signal.sql
-- Compute MAX = average of top-5 daily returns per (permno, month)
-- Filter: at least 15 daily observations per (permno, month)
-- Dedup in Python after loading

SELECT
    permno,
    month,
    count(ret) AS n_obs,
    -- MAX = average of 5 highest daily returns in this month
    arraySum(
        arraySlice(arraySort(x -> -x, groupArray(ret)), 1, 5)
    ) / 5.0 AS max_signal
FROM (
    SELECT
        d.permno,
        toDate(d.date) AS date,
        toYYYYMM(toDate(d.date)) AS month,
        d.ret
    FROM crsp_202601.dsf d
    INNER JOIN crsp_202601.dsenames m
        ON d.permno = m.permno
        AND toDate(d.date) >= toDate(m.namedt)
        AND (toDate(m.nameendt) = '1970-01-01' OR toDate(m.nameendt) >= toDate(d.date))
    WHERE toDate(d.date) >= '1968-01-01'
      AND toDate(d.date) <= '2022-12-31'
      AND d.ret IS NOT NULL
      AND d.ret > -1.0
      AND m.shrcd IN (10, 11)
      AND m.exchcd IN (1, 2, 3)
      AND abs(d.prc) >= 5.0
      AND NOT (m.siccd BETWEEN 4900 AND 4949)
      AND NOT (m.siccd BETWEEN 6000 AND 6999)
)
GROUP BY permno, month
HAVING count(ret) >= 15
SETTINGS max_execution_time = 600,
         max_rows_to_read = 5000000000,
         timeout_before_checking_execution_speed = 0
