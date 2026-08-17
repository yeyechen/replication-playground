-- ibes_sue3_fc.sql
-- Purpose: Quarterly analyst forecast series for SUE3 (Livnat-Mendenhall 2006).
--          SUE3 = (actual EPS_q - consensus mean forecast_q) / std(prior forecast
--          errors). Both `actual` and `meanest` come from statsum_epsus (the SAME
--          I/B/E/S summary file, hence the same split-adjusted share basis), aligned
--          on (cusip, fpedats), so the forecast error is internally consistent —
--          unlike act_epsus.value, which is the UNadjusted-for-splits actual.
-- Tables: ibes_202601.statsum_epsus
-- Output columns: cusip, ticker, fpedats (fiscal period end), statpers, meanest,
--                 actual, numest
-- Depends on: none
-- Settings: max_execution_time=300
--
-- Convention (paper "June statistical periods"): take the June statpers snapshot for
-- the four quarterly periods (fpi 6..9). For each (cusip, fpedats) this yields the
-- June consensus (`meanest`) and, once announced, the I/B/E/S actual (`actual`).
-- The forecast error = actual - meanest is computed in Python; sigma_analyst is the
-- rolling std of the firm's PRIOR errors (require >= 4 prior non-null errors).
--
-- Note: statsum_epsus `actual` is populated shortly before/after the announcement and
-- is forward-PERSISTED across later statpers (it does not vanish once announced), so
-- it is suitable for building the PRIOR-error std (all prior errors use genuinely
-- announced actuals). We record this persistence in assumptions.md.

WITH clean AS (
    SELECT *
    FROM ibes_202601.statsum_epsus
    WHERE measure = 'EPS'
      AND usfirm = 1
      AND fpi IN ('6', '7', '8', '9')
      AND fpedats IS NOT NULL AND length(fpedats) >= 8
      AND meanest IS NOT NULL
      AND statpers IS NOT NULL AND length(statpers) >= 8
      AND toMonth(toDate32(statpers)) = 6
      AND toDate32(statpers) BETWEEN toDate32('1981-01-01') AND toDate32('2009-12-31')
)
SELECT
    cusip,
    ticker,
    toDate32(fpedats) AS fpedats,
    toDate32(statpers) AS statpers,
    meanest,
    actual,
    numest
FROM clean
SETTINGS max_execution_time = 300,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
