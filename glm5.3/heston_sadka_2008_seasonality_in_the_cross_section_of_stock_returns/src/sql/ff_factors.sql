-- ff_factors.sql
-- Purpose: Fama-French 3-factor monthly series + risk-free rate for
--   Table 3 FF3 alpha regressions, 1965-01..2002-12 (456 months).
-- Tables: ff.four_factor_monthly
-- Output columns: month (Date32, calendar month start), mkt_rf, smb, hml, rf
-- Depends on: (none)
-- Note: dt is a Nullable(String) calendar month-end date (YYYY-MM-DD).
--   Month start is built from the string prefix (not toStartOfMonth,
--   which clamps pre-1970 Date32 values to 1970-01-01 in this build).
SELECT toDate32(concat(substring(assumeNotNull(dt), 1, 7), '-01')) AS month,
       mkt_rf, smb, hml, rf
FROM ff.four_factor_monthly
WHERE dt >= '1965-01-01' AND dt <= '2002-12-31'
  AND dt IS NOT NULL AND length(dt) = 10
ORDER BY month
SETTINGS max_execution_time = 300, max_rows_to_read = 100000000
