-- compustat_sue_annual.sql
-- Purpose: DIAGNOSTIC ONLY (Iteration 5). ANNUAL SUE variant: same SUE
--   numerator/availability as compustat_sue.sql, but the denominator is
--   total assets AT from compustat funda of the most recent fiscal year
--   with datadate STRICTLY BEFORE the quarter's datadate (the previous
--   completed FY). ASOF JOIN on (gvkey, quarter dd > funda dd).
-- Tables: comp_202601.fundq, comp_202601.funda, crsp_202601.ccmxpf_linktable
-- Output columns: permno (Int32), month ('YYYY-MM'), num, den_annual
-- Depends on: (none; diagnostic sibling of compustat_sue.sql)
WITH qtr AS (
    SELECT
        gvkey,
        toDate32OrNull(datadate) AS dd,
        toDate32OrNull(rdq) AS rdq_d,
        ibq
    FROM comp_202601.fundq
    WHERE indfmt = 'INDL'
      AND datafmt = 'STD'
      AND popsrc = 'D'
      AND consol = 'C'
      AND toDate32OrNull(datadate) IS NOT NULL
      AND toDate32OrNull(datadate) >= toDate32('1971-06-01')
      AND toDate32OrNull(datadate) <= toDate32('2010-12-31')
),
dedup AS (
    SELECT * EXCEPT(rn)
    FROM (
        SELECT *, row_number() OVER (PARTITION BY gvkey, dd) AS rn
        FROM qtr
    )
    WHERE rn = 1
),
seq2 AS (
    SELECT
        gvkey, dd, rdq_d, ibq,
        lagInFrame(ibq, 1) OVER w AS ib1, lagInFrame(qi, 1) OVER w AS q1,
        lagInFrame(ibq, 2) OVER w AS ib2, lagInFrame(qi, 2) OVER w AS q2,
        lagInFrame(ibq, 3) OVER w AS ib3, lagInFrame(qi, 3) OVER w AS q3,
        lagInFrame(ibq, 4) OVER w AS ib4, lagInFrame(qi, 4) OVER w AS q4,
        toYear(dd) * 4 + ceil(toMonth(dd) / 3) AS qi
    FROM dedup
    WINDOW w AS (PARTITION BY gvkey ORDER BY dd
                 ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),
sue_q AS (
    SELECT gvkey, dd,
           if(rdq_d IS NOT NULL, rdq_d, dd + INTERVAL 1 MONTH) AS avail_date,
           ibq - (ib1 + ib2 + ib3 + ib4) / 4 AS num
    FROM seq2
    WHERE ibq IS NOT NULL AND ib1 IS NOT NULL AND ib2 IS NOT NULL
      AND ib3 IS NOT NULL AND ib4 IS NOT NULL
      AND q1 = qi - 1 AND q2 = qi - 2 AND q3 = qi - 3 AND q4 = qi - 4
),
funda AS (
    SELECT gvkey, toDate32OrNull(datadate) AS fdd, at
    FROM comp_202601.funda
    WHERE indfmt = 'INDL' AND datafmt = 'STD' AND popsrc = 'D'
      AND consol = 'C'
      AND toDate32OrNull(datadate) IS NOT NULL
      AND toDate32OrNull(datadate) >= toDate32('1965-01-01')
      AND toDate32OrNull(datadate) <= toDate32('2010-12-31')
      AND at > 0
),
funda_dedup AS (
    SELECT * FROM (
        SELECT *, row_number() OVER (PARTITION BY gvkey, fdd) AS rn
        FROM funda
    ) WHERE rn = 1
),
asof AS (
    SELECT s.gvkey, s.dd, s.avail_date, s.num, f.at AS den_annual
    FROM sue_q AS s
    ASOF INNER JOIN funda_dedup AS f
        ON s.gvkey = f.gvkey AND s.dd > f.fdd
),
linked AS (
    SELECT
        CAST(ccm.lpermno AS Int32) AS permno,
        a.avail_date, a.num, a.den_annual
    FROM asof AS a
    INNER JOIN crsp_202601.ccmxpf_linktable AS ccm
        ON ccm.gvkey = a.gvkey
        AND ccm.linktype IN ('LC', 'LU')
        AND ccm.linkprim IN ('P', 'C')
        AND ccm.usedflag = 1
        AND ccm.linkdt IS NOT NULL
        AND ccm.linkdt <= toString(a.avail_date + INTERVAL 6 MONTH)
        AND (ccm.linkenddt IS NULL OR ccm.linkenddt = ''
             OR ccm.linkenddt >= toString(toStartOfMonth(a.avail_date)))
    WHERE a.den_annual > 0
)
SELECT
    permno,
    substring(toString(toStartOfMonth(avail_date)), 1, 7) AS month,
    avg(num) AS num,
    avg(den_annual) AS den_annual
FROM linked
GROUP BY permno, month
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;
