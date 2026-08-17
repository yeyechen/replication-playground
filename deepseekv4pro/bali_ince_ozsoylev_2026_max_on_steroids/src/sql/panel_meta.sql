-- panel_meta.sql
-- Purpose: Exchange code (exchcd -> Nasdaq dummy) and historical SIC
--   (hsiccd -> FF-17 industry) per (permno, month), point-in-time via
--   dsfhdr validity windows, so the E(ISKEW) predictor set can build the
--   Nasdaq indicator and 16 of 17 industry fixed effects.
-- Tables: crsp_202601.msf, crsp_202601.dsfhdr
-- Output columns: permno, date (month-end), hexcd, hsiccd
-- Depends on: (none)
-- Notes: same universe filters as monthly_universe.sql, so the resulting
--   (permno, month) keys are a superset of the panel's existing keys.
SELECT
    m.permno AS permno,
    m.date   AS date,
    h.hexcd  AS hexcd,
    h.hsiccd AS hsiccd
FROM crsp_202601.msf AS m
INNER JOIN crsp_202601.dsfhdr AS h
        ON m.permno = h.permno
       AND m.date >= h.begdat
       AND m.date <= h.enddat
WHERE m.date >= '1968-01-01'
  AND m.date <= '2022-12-31'
  AND h.hshrcd IN (10, 11)
  AND h.hexcd  IN (1, 2, 3)
  AND m.ret IS NOT NULL
  AND m.ret > -50
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 20000000000,
         timeout_before_checking_execution_speed = 0
