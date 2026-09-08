-- compustat_sue_variants.sql
-- Purpose: DIAGNOSTIC ONLY (Iteration 5, SUE denominator disambiguation).
--   Same construction as compustat_sue.sql, but outputs the SUE NUMERATOR
--   and the three quarterly denominator candidates per announcement
--   (atq_q = BASE, atq_{q-4} = YEARGO, mean(atq_{q-4..q}) = AVG5). The
--   ANNUAL variant (previous completed fiscal year's funda AT) is merged
--   in pandas from a separate funda pull (see diag_sue_variants.py).
--   This file is NOT part of the committed pipeline; compustat_sue.sql
--   remains the production SUE query.
-- Tables: comp_202601.fundq, crsp_202601.ccmxpf_linktable
-- Output columns: permno (Int32), month ('YYYY-MM' availability month),
--   num, den_base, den_yeargo, den_avg5 (Float64)
-- Depends on: (none; diagnostic sibling of compustat_sue.sql)
WITH qtr AS (
    SELECT
        gvkey,
        toDate32OrNull(datadate) AS dd,
        toDate32OrNull(rdq) AS rdq_d,
        ibq,
        atq
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
-- trailing 5-quarter mean of atq needs all 5 atq lags (consecutive)
seq2 AS (
    SELECT
        gvkey, dd, rdq_d, ibq,
        lagInFrame(ibq, 1) OVER w AS ib1, lagInFrame(qi, 1) OVER w AS q1,
        lagInFrame(ibq, 2) OVER w AS ib2, lagInFrame(qi, 2) OVER w AS q2,
        lagInFrame(ibq, 3) OVER w AS ib3, lagInFrame(qi, 3) OVER w AS q3,
        lagInFrame(ibq, 4) OVER w AS ib4, lagInFrame(qi, 4) OVER w AS q4,
        atq,
        lagInFrame(atq, 1) OVER w AS at1, lagInFrame(qi, 1) OVER w AS aq1,
        lagInFrame(atq, 2) OVER w AS at2, lagInFrame(qi, 2) OVER w AS aq2,
        lagInFrame(atq, 3) OVER w AS at3, lagInFrame(qi, 3) OVER w AS aq3,
        lagInFrame(atq, 4) OVER w AS at4, lagInFrame(qi, 4) OVER w AS aq4,
        toYear(dd) * 4 + ceil(toMonth(dd) / 3) AS qi
    FROM dedup
    WINDOW w AS (PARTITION BY gvkey ORDER BY dd
                 ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),
sue_full AS (
    -- production eligibility exactly as compustat_sue.sql (atq>0 + 4
    -- consecutive ibq lags); YEARGO/AVG5 denominators as NULLABLE
    -- per-row variants so BASE's sample is IDENTICAL to production.
    SELECT
        gvkey,
        dd,
        if(rdq_d IS NOT NULL, rdq_d, dd + INTERVAL 1 MONTH) AS avail_date,
        (ibq - (ib1 + ib2 + ib3 + ib4) / 4) / atq AS sue_base,
        if(at4 > 0 AND aq4 = qi - 4,
           (ibq - (ib1 + ib2 + ib3 + ib4) / 4) / at4, NULL) AS sue_yeargo,
        if(at1 > 0 AND at2 > 0 AND at3 > 0 AND at4 > 0
             AND aq1 = qi - 1 AND aq2 = qi - 2 AND aq3 = qi - 3
             AND aq4 = qi - 4,
           (ibq - (ib1 + ib2 + ib3 + ib4) / 4)
             / ((atq + at1 + at2 + at3 + at4) / 5), NULL) AS sue_avg5
    FROM seq2
    WHERE atq > 0
      AND ibq IS NOT NULL AND ib1 IS NOT NULL AND ib2 IS NOT NULL
      AND ib3 IS NOT NULL AND ib4 IS NOT NULL
      AND q1 = qi - 1 AND q2 = qi - 2 AND q3 = qi - 3 AND q4 = qi - 4
),
linked AS (
    SELECT
        CAST(ccm.lpermno AS Int32) AS permno,
        s.avail_date,
        s.sue_base, s.sue_yeargo, s.sue_avg5
    FROM sue_full AS s
    INNER JOIN crsp_202601.ccmxpf_linktable AS ccm
        ON ccm.gvkey = s.gvkey
        AND ccm.linktype IN ('LC', 'LU')
        AND ccm.linkprim IN ('P', 'C')
        AND ccm.usedflag = 1
        AND ccm.linkdt IS NOT NULL
        AND ccm.linkdt <= toString(s.avail_date + INTERVAL 6 MONTH)
        AND (ccm.linkenddt IS NULL OR ccm.linkenddt = ''
             OR ccm.linkenddt >= toString(toStartOfMonth(s.avail_date)))
)
SELECT
    permno,
    substring(toString(toStartOfMonth(avail_date)), 1, 7) AS month,
    avg(sue_base) AS sue_base,
    avg(sue_yeargo) AS sue_yeargo,
    avg(sue_avg5) AS sue_avg5
FROM linked
GROUP BY permno, month
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;
