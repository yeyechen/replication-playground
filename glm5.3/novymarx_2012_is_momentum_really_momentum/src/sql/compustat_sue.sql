-- compustat_sue.sql
-- Purpose: Standardized unexpected earnings (SUE, Table 14 / T8; paper
--   L2587): SUE_q = (ibq_q - mean(ibq over the 4 PRECEDING consecutive
--   quarters of the same gvkey)) / atq_q. Requires all 5 quarters present
--   (non-missing ibq) and atq_q > 0. Quarterly earnings = ibq (income
--   before extraordinary items), the standard SUE earnings item; the
--   paper does not name the item.
--   Availability timing (paper silent, logged as an assumption): SUE
--   becomes usable at the earnings announcement month -- month(rdq) when
--   rdq is non-missing, else the month after datadate (quarter end + 1).
--   The output is one row per (permno, announcement month); carry-forward
--   and the 6-month staleness cap are applied downstream in pandas.
-- Tables: comp_202601.fundq, crsp_202601.ccmxpf_linktable
-- Output columns: permno (Int32), month ('YYYY-MM' string of the
--   availability month, matching universe_monthly.sql's convention),
--   sue (Float64)
-- Depends on: (none; merged onto the panel in pandas, as-of by month)
-- NOTE: datadate/rdq are Strings in this extract -> toDate32OrNull
--   (Date-clamp trap); CCM link dates compared lexically (see
--   compustat_be.sql).
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
    -- fundq is keyed on 6 fields; keep one row per (gvkey, quarter end)
    SELECT * EXCEPT(rn)
    FROM (
        SELECT *, row_number() OVER (PARTITION BY gvkey, dd) AS rn
        FROM qtr
    )
    WHERE rn = 1
),
seq AS (
    -- quarter index from datadate (calendar quarter); lagInFrame over the
    -- gvkey quarter series. A lag qualifies as "the previous quarter" only
    -- if its quarter index is exactly qi - k, which enforces consecutive
    -- datacqtr and catches gap quarters.
    SELECT
        gvkey,
        dd,
        rdq_d,
        ibq,
        atq,
        toYear(dd) * 4 + ceil(toMonth(dd) / 3) AS qi,
        lagInFrame(ibq, 1) OVER w AS ib1, lagInFrame(qi, 1) OVER w AS q1,
        lagInFrame(ibq, 2) OVER w AS ib2, lagInFrame(qi, 2) OVER w AS q2,
        lagInFrame(ibq, 3) OVER w AS ib3, lagInFrame(qi, 3) OVER w AS q3,
        lagInFrame(ibq, 4) OVER w AS ib4, lagInFrame(qi, 4) OVER w AS q4
    FROM dedup
    WINDOW w AS (PARTITION BY gvkey ORDER BY dd
                 ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),
sue_q AS (
    SELECT
        gvkey,
        dd,
        if(rdq_d IS NOT NULL, rdq_d, dd + INTERVAL 1 MONTH) AS avail_date,
        (ibq - (ib1 + ib2 + ib3 + ib4) / 4) / atq AS sue
    FROM seq
    WHERE atq > 0
      AND ibq IS NOT NULL AND ib1 IS NOT NULL AND ib2 IS NOT NULL
      AND ib3 IS NOT NULL AND ib4 IS NOT NULL
      AND q1 = qi - 1 AND q2 = qi - 2 AND q3 = qi - 3 AND q4 = qi - 4
),
linked AS (
    -- CCM link as in compustat_be.sql; the link must overlap the
    -- availability window [avail month, avail month + 6 months] (the
    -- maximum carry-forward window downstream).
    SELECT
        CAST(ccm.lpermno AS Int32) AS permno,
        s.avail_date,
        s.sue
    FROM sue_q AS s
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
    avg(sue) AS sue
FROM linked
GROUP BY permno, month
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;
