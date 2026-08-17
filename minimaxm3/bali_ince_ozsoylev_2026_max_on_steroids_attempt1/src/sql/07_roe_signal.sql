-- 07_roe_signal.sql
-- Purpose: ROE = ibq / one-quarter-lagged book equity per (gvkey, quarter_end_date).
--          Book equity per quarter uses same formula as annual:
--            BE_q = seqq + coalesce(txdbq,0) + coalesce(itcbq,0) - pstkq (fallback)
--          One-quarter lag uses previous row of (gvkey, datadate).
-- Tables: comp_202601.fundq
-- Output columns: gvkey, datadate, roe
-- Depends on: (none)
-- Notes:
--   - Standard Compustat quality filter applied.
--   - We sort by gvkey + datadate ascending; the lagged row is the previous datadate.
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
WITH base AS (
    SELECT
        gvkey,
        toDate32(datadate)                                                AS qe,
        ibq,
        -- Quarterly book equity approximation: seqq + txdbq + itcbq - pstkq
        coalesce(seqq, 0)
            + coalesce(txdbq, 0)
            + coalesce(itcbq, 0)
            - if(isFinite(pstkrq), pstkrq,
                if(isFinite(pstkq), pstkq, 0))                            AS be_q
    FROM comp_202601.fundq
    WHERE indfmt = 'INDL'
      AND datafmt IN ('STD', 'SUMM')
      AND consol = 'C'
      AND popsrc IN ('D', 'I')
      AND ibq IS NOT NULL
      AND seqq IS NOT NULL
      AND toDate32(datadate) BETWEEN toDate32('1968-01-01') AND toDate32('2022-12-31')
),
lagged AS (
    SELECT
        gvkey,
        qe,
        ibq,
        be_q,
        lagInFrame(be_q, 1) OVER w                                         AS be_q_lag1
    FROM base
    WINDOW w AS (PARTITION BY gvkey ORDER BY qe
                 ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
)
SELECT
    gvkey,
    qe                                                                   AS datadate,
    ibq / nullIf(be_q_lag1, 0)                                            AS roe
FROM lagged
WHERE be_q_lag1 IS NOT NULL
  AND be_q_lag1 > 0
