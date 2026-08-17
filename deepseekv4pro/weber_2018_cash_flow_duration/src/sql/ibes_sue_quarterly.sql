-- ibes_sue_quarterly.sql
-- Purpose: I/B/E/S quarterly realized EPS for the seasonal-random-walk SUE candidates
--          (SUE1/SUE2). This is the candidate source the audit-2 [M3] asked to test:
--          I/B/E/S quarterly actuals (act_epsus, measure='EPS', pdicity='QTR') with the
--          announcement date (anndats) for June-cadence alignment, in place of Compustat
--          fundq (which was switched to in outer-iteration 1 on split-adjustment grounds).
-- Tables: ibes_202601.act_epsus
-- Output columns: cusip, ticker, pends (fiscal period end), anndats (announcement date),
--                 value (split-adjusted actual EPS)
-- Depends on: none
-- Settings: max_execution_time=600
--
-- IMPORTANT (audit-2 M3 resolution): act_epsus.value is ALREADY split-adjusted to a
--   common share basis (verified via ibes_202601.adj; see ibes_adj.sql). The outer-1
--   switch to Compustat on "split adjustment" grounds was based on a false premise — the
--   act_epsus split-bias concern applied to the price-target file (ptgsum), NOT to the
--   EPS actuals. Both Compustat epspx and IBES act_epsus ARE split-adjusted; the SUE
--   numerator being "flat at ~0" is intrinsic to the seasonal-random-walk definition, not
--   a split-adjustment artifact (see results/table_8.md diagnostic section).

SELECT
    cusip,
    ticker,
    toDate32(pends)  AS pends,
    toDate32(anndats) AS anndats,
    value
FROM ibes_202601.act_epsus
WHERE pdicity = 'QTR'
  AND measure = 'EPS'
  AND usfirm = 1
  AND value IS NOT NULL
  AND pends IS NOT NULL AND pends != ''
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
