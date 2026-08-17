-- inst_13f.sql
-- Purpose: Quarterly 13F institutional holdings aggregated to
--   (cusip, fdate), mapped cusip -> permno point-in-time via dsenames
--   (8-char ncusip, name window containing fdate), and normalized to an
--   institutional-ownership fraction using Thomson's 12-month-adjusted
--   shares outstanding (shrout1, fallback shrout2).
-- Tables: instown_202601.s34 (13F holdings), crsp_202601.dsenames
-- Output columns: permno, fquarter (Date32 quarter-end), inst_shares,
--   shrout (denominator used), shrout_src ('shrout1'|'shrout2'),
--   n_managers (reporting managers aggregated)
-- Depends on: (none)
-- Produces: quarterly INST series merged onto the monthly panel in main.py
-- Notes:
--   * s34.shares is held shares per (manager, cusip, fdate); shrout1/shrout2
--     are repeated on every row but are consistent within (cusip, fdate),
--     so any() picks the canonical denominator.
--   * cusip -> permno: one 13F cusip can map to several dsenames permnos over
--     time; the PIT window (namedt <= fdate <= nameendt) selects the right
--     record. When a cusip hits multiple live permnos at fdate we prefer the
--     ordinary-common-share record (shrcd IN 10,11) and the most-recently
--     started name window; otherwise pick the latest name window.
--   * INST = min(sum_shares / shrout, 1.0); shrout1 missing/zero -> shrout2.
-- Settings: join_algorithm=partial_merge, max_execution_time=600
WITH
-- (1) Aggregate 13F holdings to (cusip, fdate), carrying the canonical
--     shares-outstanding denominator from the first (lowest) shrout value.
hold AS (
    SELECT
        cusip,
        toDate32(fdate) AS fq,
        sum(shares)     AS inst_shares,
        count()         AS n_managers,
        any(shrout1)    AS shrout1,
        any(shrout2)    AS shrout2
    FROM instown_202601.s34
    WHERE fdate >= '1980-01-01'
      AND fdate <= '2022-12-31'
      AND cusip IS NOT NULL
      AND shares IS NOT NULL
      AND shares > 0
    GROUP BY cusip, fq
),
-- (2) PIT cusip -> permno via dsenames. ncusip is 8-char; s34.cusip is 8-char.
mapped AS (
    SELECT
        h.cusip,
        h.fq   AS fdate,
        h.inst_shares,
        h.n_managers,
        h.shrout1,
        h.shrout2,
        n.permno,
        n.shrcd,
        n.namedt,
        row_number() OVER (
            PARTITION BY h.cusip, h.fq
            ORDER BY
                (n.shrcd IN (10, 11)) DESC,
                n.namedt DESC
        ) AS rn
    FROM hold AS h
    INNER JOIN crsp_202601.dsenames AS n
            ON n.ncusip = h.cusip
           AND h.fq >= toDate32(n.namedt)
           AND h.fq <= toDate32(n.nameendt)
),
picked AS (
    SELECT * FROM mapped WHERE rn = 1
)
SELECT
    permno,
    fdate       AS fquarter,
    inst_shares,
    -- Denominator in RAW shares (same units as `shares`):
    --   shrout1 is Thomson's 12-month-adjusted shr, stored here in MILLIONS
    --   (round shrout to nearest 1e6) -> x1e6.
    --   shrout2 is stored in THOUSANDS (matches CRSP msf.shrout) -> x1e3.
    --   shrout1 preferred (paper convention); shrout2 fallback where
    --   shrout1 missing/0.
    multiIf(shrout1 IS NOT NULL AND shrout1 > 0, shrout1 * 1000000.0,
            shrout2 IS NOT NULL AND shrout2 > 0, shrout2 * 1000.0,
            NULL) AS shrout,
    if(shrout1 IS NOT NULL AND shrout1 > 0, 'shrout1(millions)',
       'shrout2(thousands)') AS shrout_src,
    n_managers
FROM picked
WHERE shrout1 IS NOT NULL OR shrout2 IS NOT NULL
ORDER BY permno, fquarter
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 20000000000,
         timeout_before_checking_execution_speed = 0
