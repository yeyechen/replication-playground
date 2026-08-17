-- ibes_coverage.sql
-- Purpose: I/B/E/S coverage screen for Table 8's universe (footnote 15). A firm is
--          "IBES-covered at June t" if it appears in any of the three US I/B/E/S
--          files with a June-t statistical-period observation. Emits distinct
--          (cusip, june_year) covered pairs, usfirm=1.
-- Tables: ibes_202601.statsum_epsus, ibes_202601.act_epsus, ibes_202601.det_epsus
-- Output columns: cusip (String), june_year (Int16)
-- Depends on: none
-- Settings: max_execution_time=600
--
-- Operationalization (per Replicator spec):
--   - statsum_epsus: summary consensus file. Coverage date = statpers (the monthly
--     statistical period, third-Thursday string). Covered at June year t =
--     toMonth(statpers)=6 AND toYear(statpers)=t. require usfirm=1.
--   - act_epsus: actuals. Coverage date = anndats (announcement date). Covered at
--     June year t = toMonth(anndats)=6 AND toYear(anndats)=t. require usfirm=1.
--     (pends is the fiscal period end, often mid-quarter; anndats is when the actual
--     was recorded and observed in June — the period that "overlaps the June staper".)
--   - det_epsus: detail/analyst-level estimates. Coverage date = anndats (the estimate
--     announcement). Covered at June year t = toMonth(anndats)=6. require usfirm=1.
-- Union of the three, distinct on (cusip, june_year). The cusip -> permno mapping is
-- applied in Python (PIT via cusip_map.sql) so downstream can intersect with the
-- duration panel's (permno, sort_year).

WITH
statsym AS (
    SELECT DISTINCT cusip, toYear(toDate32(statpers)) AS june_year
    FROM ibes_202601.statsum_epsus
    WHERE usfirm = 1
      AND statpers IS NOT NULL AND statpers != ''
      AND toMonth(toDate32(statpers)) = 6
      AND toYear(toDate32(statpers)) BETWEEN 1982 AND 2009
),
actav AS (
    SELECT DISTINCT cusip, toYear(toDate32(anndats)) AS june_year
    FROM ibes_202601.act_epsus
    WHERE usfirm = 1
      AND anndats IS NOT NULL AND anndats != ''
      AND toMonth(toDate32(anndats)) = 6
      AND toYear(toDate32(anndats)) BETWEEN 1982 AND 2009
),
detav AS (
    SELECT DISTINCT cusip, toYear(toDate32(anndats)) AS june_year
    FROM ibes_202601.det_epsus
    WHERE usfirm = 1
      AND anndats IS NOT NULL AND anndats != ''
      AND toMonth(toDate32(anndats)) = 6
      AND toYear(toDate32(anndats)) BETWEEN 1982 AND 2009
)
SELECT DISTINCT cusip, june_year
FROM (
    SELECT cusip, june_year FROM statsym
    UNION ALL
    SELECT cusip, june_year FROM actav
    UNION ALL
    SELECT cusip, june_year FROM detav
)
WHERE cusip IS NOT NULL AND cusip != ''
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
