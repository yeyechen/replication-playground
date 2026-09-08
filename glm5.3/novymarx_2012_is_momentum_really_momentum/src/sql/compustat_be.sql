-- compustat_be.sql
-- Purpose: Book equity per (gvkey, fiscal year) with the paper's tiered
--   construction (footnote 1, L155; Assumption 7), linked to CRSP permnos
--   via the CCM link table, and June-aligned (a fiscal year with datadate
--   in calendar year y-1 is active from July of year y).
--   BE = SE + DT - PS where
--     SE = coalesce(seq, ceq + pstk, at - lt)   [PSTX -> PSTK substitution]
--     DT = coalesce(txditc, txdb + itcb, 0)
--     PS = coalesce(pstkrv, pstkl, pstk, 0)
--   BE kept only if > 0. Units: millions of USD (funda convention).
-- Tables: comp_202601.funda, crsp_202601.ccmxpf_linktable
-- Output columns: permno (Int32), active_year (Int32: BE active July
--   active_year .. June active_year+1), be (Float64, millions)
-- Depends on: (none; joined to the panel in pandas via merge_asof)
-- NOTE: datadate and linkdt/linkenddt are Strings in this extract —
--   datadate parsed with toDate32OrNull (Date-clamp trap), link dates
--   compared lexically ('YYYY-MM-DD' strings compare correctly).
WITH funda AS (
    SELECT
        gvkey,
        toDate32OrNull(datadate) AS dd,
        seq, ceq, pstk, pstkrv, pstkl, at, lt, txditc, txdb, itcb
    FROM comp_202601.funda
    WHERE indfmt = 'INDL'
      AND datafmt = 'STD'
      AND popsrc = 'D'
      AND consol = 'C'
      AND toDate32OrNull(datadate) IS NOT NULL
      AND toDate32OrNull(datadate) >= toDate32('1965-01-01')
      AND toDate32OrNull(datadate) <= toDate32('2010-12-31')
      AND coalesce(seq, ceq + pstk, at - lt) IS NOT NULL
),
dedup AS (
    -- funda is keyed on 6 fields; after the standard filter a few
    -- (gvkey, datadate) duplicates remain — keep one row arbitrarily.
    SELECT *
    FROM funda
    QUALIFY row_number() OVER (PARTITION BY gvkey, dd) = 1
),
be AS (
    SELECT
        gvkey,
        dd,
        toYear(dd) + 1 AS active_year,
        coalesce(seq, ceq + pstk, at - lt)
          + coalesce(txditc, txdb + itcb, 0)
          - coalesce(pstkrv, pstkl, pstk, 0) AS be
    FROM dedup
),
linked AS (
    SELECT
        CAST(ccm.lpermno AS Int32) AS permno,
        be.active_year,
        be.be
    FROM be
    INNER JOIN crsp_202601.ccmxpf_linktable AS ccm
        ON ccm.gvkey = be.gvkey
        AND ccm.linktype IN ('LC', 'LU')
        AND ccm.linkprim IN ('P', 'C')
        AND ccm.usedflag = 1
        AND ccm.linkdt IS NOT NULL
        -- link must overlap the active window [July y, June y+1]
        AND ccm.linkdt <= concat(toString(be.active_year + 1), '-06-30')
        AND (ccm.linkenddt IS NULL OR ccm.linkenddt = ''
             OR ccm.linkenddt >= concat(toString(be.active_year), '-07-01'))
    WHERE be.be > 0
)
SELECT permno, active_year, avg(be) AS be
FROM linked
GROUP BY permno, active_year
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;
