-- compustat_sue_pit.sql
-- Purpose: DIAGNOSTIC (Iteration 6) — point-in-time (as-first-reported) SUE.
--   SUE_pit_q = (ibqh_q - mean(ibqh over the 4 preceding consecutive
--   quarters)) / atqh_q, where EVERY quarter's ibqh/atqh is taken as of its
--   OWN first report: for each (gvkey, datadate) we keep the row with the
--   earliest pointdate (argMin). This avoids look-ahead within the PIT data
--   itself (no restated values).
--   Table structure verified by inspection: one row per
--   (gvkey, pointdate, datadate); qtr0date = quarter being reported in that
--   vintage; qtrsback = quarters between datadate and qtr0date. A quarter's
--   first report is therefore its earliest pointdate, which may carry
--   qtrsback > 0 (backfill), so we key on datadate, not qtrsback.
--   Availability month = month(first pointdate of quarter q).
--   _dc data-coverage flag columns are not documented in references/
--   COMPUSTAT.md; plain ibqh/atqh with IS NOT NULL is used (NULL = missing).
--   NOTE: comp_pit coverage starts pointdate 1987-02-28 (manual confirms PIT
--   POINTDATE starts 1987), so PIT SUE announcements begin ~1987 even though
--   datadate >= 1980 is requested.
-- Tables: comp_pit.pithistdataus, crsp_202601.ccmxpf_linktable
-- Output columns: permno (Int32), month ('YYYY-MM' availability month),
--   sue_pit (Float64)
-- Depends on: (none; diagnostic twin of compustat_sue.sql)
WITH firstrep AS (
    -- first-report values per (gvkey, quarter end): value at earliest pointdate
    SELECT
        gvkey,
        datadate AS dd,
        min(pointdate) AS first_pointdate,
        argMin(ibqh, pointdate) AS ibq,
        argMin(atqh, pointdate) AS atq
    FROM comp_pit.pithistdataus
    WHERE datadate >= toDate32('1980-01-01')
      AND datadate <= toDate32('2010-12-31')
    GROUP BY gvkey, datadate
),
seq AS (
    -- quarter index from datadate; lagInFrame with consecutiveness check
    -- (identical logic to compustat_sue.sql)
    SELECT
        gvkey,
        dd,
        first_pointdate,
        ibq,
        atq,
        toYear(dd) * 4 + ceil(toMonth(dd) / 3) AS qi,
        lagInFrame(ibq, 1) OVER w AS ib1, lagInFrame(qi, 1) OVER w AS q1,
        lagInFrame(ibq, 2) OVER w AS ib2, lagInFrame(qi, 2) OVER w AS q2,
        lagInFrame(ibq, 3) OVER w AS ib3, lagInFrame(qi, 3) OVER w AS q3,
        lagInFrame(ibq, 4) OVER w AS ib4, lagInFrame(qi, 4) OVER w AS q4
    FROM firstrep
    WINDOW w AS (PARTITION BY gvkey ORDER BY dd
                 ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),
sue_q AS (
    SELECT
        gvkey,
        first_pointdate AS avail_date,
        (ibq - (ib1 + ib2 + ib3 + ib4) / 4) / atq AS sue_pit
    FROM seq
    WHERE atq > 0
      AND ibq IS NOT NULL AND ib1 IS NOT NULL AND ib2 IS NOT NULL
      AND ib3 IS NOT NULL AND ib4 IS NOT NULL
      AND q1 = qi - 1 AND q2 = qi - 2 AND q3 = qi - 3 AND q4 = qi - 4
),
linked AS (
    -- CCM link as in compustat_be.sql / compustat_sue.sql
    SELECT
        CAST(ccm.lpermno AS Int32) AS permno,
        s.avail_date,
        s.sue_pit
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
    avg(sue_pit) AS sue_pit
FROM linked
GROUP BY permno, month
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;
