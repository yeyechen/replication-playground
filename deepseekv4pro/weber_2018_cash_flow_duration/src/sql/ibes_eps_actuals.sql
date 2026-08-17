-- ibes_eps_actuals.sql
-- Purpose: Actual EPS from I/B/E/S unadjusted actuals — both ANNUAL (for realized
--          5-year EPS growth EG) and QUARTERLY (for SUE1/SUE2).
-- Tables: ibes_202601.act_epsus
-- Output columns: cusip, ticker, pends, fpedats, anndats, pdicity, value
-- Depends on: none
-- Settings: max_execution_time=300
--
-- Discovery note: act_epsus.pdicity in ('ANN','QTR','SAN'). `value` is the
-- split-adjusted actual EPS; `pends` is the fiscal period end date (String);
-- `anndats` is the announcement date; `actdats` is the actual-flag date.
-- We pull ANN and QTR rows only. usfirm=1 restricts to US firms (I/B/E/S flag).

SELECT
    cusip,
    ticker,
    toDate32(pends)  AS pends,
    toDate32(anndats) AS anndats,
    pdicity,
    value
FROM ibes_202601.act_epsus
WHERE pdicity IN ('ANN', 'QTR')
  AND usfirm = 1
  AND value IS NOT NULL
SETTINGS max_execution_time = 300,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
