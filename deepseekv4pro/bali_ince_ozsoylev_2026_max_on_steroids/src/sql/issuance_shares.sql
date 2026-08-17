-- issuance_shares.sql
-- Purpose: Monthly split-adjusted shares outstanding for net stock issuance
--   (NSI) and 5-year composite share issuance (CSI-5). Split adjustment via
--   CRSP cumulative share factor (cfacshr). Universe filters match the panel
--   (hshrcd/hexcd/hsiccd PIT via dsfhdr; month-end price screen abs(prc) >= 5).
-- Tables: crsp_202601.msf, crsp_202601.dsfhdr
-- Output columns: permno, month, adjshrout, prc
--   adjshrout = shrout * cfacshr (split-adjusted shares); prc = |prc| month-end
-- Depends on: (none)
-- Produces: Section 3 computes nsi = log(adjshrout_t / adjshrout_{t-12}) and
--   csi5 = log(adjshrout_t / adjshrout_{t-60}) in Python (per-permno shift).
--   prc feeds the CHS (2008) PRICE term.
-- Settings: join_algorithm=partial_merge, max_execution_time=600
SELECT
    m.permno          AS permno,
    toStartOfMonth(toDate32(m.date)) AS month,
    m.shrout * m.cfacshr AS adjshrout,
    abs(m.prc)        AS prc
FROM crsp_202601.msf AS m
INNER JOIN crsp_202601.dsfhdr AS h
        ON m.permno = h.permno
       AND m.date >= h.begdat
       AND m.date <= h.enddat
WHERE m.date >= '1966-01-01'
  AND m.date <= '2022-12-31'
  AND h.hshrcd IN (10, 11)
  AND h.hexcd  IN (1, 2, 3)
  AND NOT (h.hsiccd >= 4900 AND h.hsiccd <= 4949)
  AND NOT (h.hsiccd >= 6000 AND h.hsiccd <= 6999)
  AND m.shrout IS NOT NULL
  AND abs(m.prc) >= 5
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 20000000000,
         timeout_before_checking_execution_speed = 0
