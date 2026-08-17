-- 05_book_equity.sql
-- Purpose: Book equity per (gvkey, fiscal_year) from comp_202601.funda
--          BE = SEQ + TXDB + ITCB - PSTKRV (fallback -PSTKL or -PSTK in that order)
--          Apply standard Compustat quality filter.
-- Tables: comp_202601.funda
-- Output columns: gvkey, fyear, be
-- Depends on: (none)
-- Notes:
--   - indfmt='INDL' consolidates the older 'FS'/'IN' convention.
--   - datafmt IN ('STD','SUMM') excludes pre-1987 raw.
--   - consol='C' for consolidated.
--   - popsrc IN ('D','I') for domestic firms.
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
SELECT
    gvkey,
    toYear(datadate)                                          AS fyear,
    -- BE per paper formula. coalesce to 0 for missing addends;
    -- subtract preferred stock using the priority -pstkrv, -pstkl, -pstk.
    coalesce(seq, 0)
        + coalesce(txdb, 0)
        + coalesce(itcb, 0)
        - if(isFinite(pstkrv), pstkrv,
            if(isFinite(pstkl), pstkl,
                if(isFinite(pstk), pstk, 0)))
                                                            AS be
FROM comp_202601.funda
WHERE indfmt = 'INDL'
  AND datafmt IN ('STD', 'SUMM')
  AND consol = 'C'
  AND popsrc IN ('D', 'I')
  AND seq IS NOT NULL
