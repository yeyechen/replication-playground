-- daily_universe.sql
-- Purpose: PIT-filtered daily stock data for universe construction (1966-11 .. 2022-12).
--   Filters applied point-in-time via dsfhdr validity windows (begdat/enddat):
--     * hshrcd IN (10, 11)  — ordinary common shares
--     * hexcd  IN (1, 2, 3) — NYSE / AMEX(NYSE MKT) / NASDAQ
--     * hsiccd NOT IN util (4900-4949) and NOT IN financials (6000-6999)
--   (Universe per paper L163/L169; PIT source per PAPER_CONVENTIONS.md — never dsenames.)
--   Price filter (abs(prc) >= 5) is NOT applied here: the $5 filter is a
--   month-end screen (applied in monthly_universe.sql), while the daily pull
--   must retain all days for the >=15-obs rule, ILLIQ dollar volume, and the
--   252-day BETA/IVOL regressions.
-- Tables: crsp_202601.dsf, crsp_202601.dsfhdr
-- Output columns: permno, date, ret, prc, vol, shrout, cfacpr, cfacshr, hshrcd, hexcd, hsiccd
-- Depends on: (none)
-- Produces: data/daily_universe.parquet (Assumption 16 intermediate — feeds
--   BETA, IVOL, ILLIQ, MAX, turnover)
-- Settings: join_algorithm=partial_merge, max_execution_time=600
SELECT
    d.permno  AS permno,
    d.date    AS date,
    d.ret     AS ret,
    d.prc     AS prc,
    d.vol     AS vol,
    d.shrout  AS shrout,
    d.cfacpr  AS cfacpr,
    d.cfacshr AS cfacshr,
    h.hshrcd  AS hshrcd,
    h.hexcd   AS hexcd,
    h.hsiccd  AS hsiccd
FROM crsp_202601.dsf AS d
INNER JOIN crsp_202601.dsfhdr AS h
        ON d.permno = h.permno
       AND d.date >= h.begdat
       AND d.date <= h.enddat
WHERE d.date >= '1966-11-01'
  AND d.date <= '2022-12-31'
  AND h.hshrcd IN (10, 11)
  AND h.hexcd  IN (1, 2, 3)
  AND NOT (h.hsiccd >= 4900 AND h.hsiccd <= 4949)
  AND NOT (h.hsiccd >= 6000 AND h.hsiccd <= 6999)
  AND d.ret IS NOT NULL
  AND d.ret > -50
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 20000000000,
         timeout_before_checking_execution_speed = 0
