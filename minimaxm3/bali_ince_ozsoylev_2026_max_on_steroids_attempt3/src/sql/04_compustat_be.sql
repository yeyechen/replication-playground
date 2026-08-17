-- 04_compustat_be.sql
-- Purpose: Compustat book equity per (gvkey, fiscal year) for BM/ROE/IA calculations
-- Tables: comp_202601.funda
-- Output columns: gvkey, datadate, fyear, be, at, ib, equity, sich
-- Depends on: (none)
-- Notes:
--   - Book equity (BE) = SEQ + TXDB + ITCB - PSTKRV with fallbacks (per Assumption 7).
--   - Standard Compustat quality filter: indfmt='INDL', consol='C', popsrc='D', datafmt='STD'.
--   - PSTKRV -> PSTKL -> PSTK fallback (use first non-NULL).
--   - If SEQ is NULL, fall back to CEQ.
--   - datadate stored as Nullable(String); cast via CAST(... AS Date32) to avoid
--     analyzer type-inference cache issues.

SELECT
  gvkey,
  CAST(datadate AS Date32) AS datadate,
  toUInt32(fyear) AS fyear,
  toFloat64(ifNull(seq, ceq)) + ifNull(txdb, 0.0) + ifNull(itcb, 0.0) -
    ifNull(pstkrv, ifNull(pstkl, ifNull(pstk, 0.0))) AS be,
  ifNull(at, NULL) AS at,
  ifNull(ib, NULL) AS ib,
  ifNull(seq, ceq) AS equity,
  toUInt32(ifNull(sich, 0)) AS sich
FROM comp_202601.funda
WHERE indfmt = 'INDL'
  AND consol = 'C'
  AND popsrc = 'D'
  AND datafmt = 'STD'
  AND fic = 'USA'
  AND CAST(datadate AS Date32) >= toDate32('1967-01-01')
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
