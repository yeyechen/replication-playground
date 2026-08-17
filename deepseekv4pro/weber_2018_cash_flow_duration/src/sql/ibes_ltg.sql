-- ibes_ltg.sql
-- Purpose: June statistical-period consensus LTG (long-term earnings growth)
--          forecast per firm-year from I/B/E/S unadjusted summary file.
--          LTG lives in statsum_epsus with fpi='0' and fiscalp='LTG';
--          the consensus mean is `meanest` (median `medest`, coverage `numest`).
-- Tables: ibes_202601.statsum_epsus
-- Output columns: cusip, ticker, statpers (Date32), meanest, medest, numest
-- Depends on: none
-- Settings: max_execution_time=300
--
-- Discovery note: statpers is a String of the monthly statistical-period date
-- (third Thursday, e.g. '2005-06-16'). The June cross-section is
-- toMonth(statpers)=6. fpi='0' + fiscalp='LTG' identifies LTG forecasts
-- (verified: meanest=12.66 ... 6.0 are growth %, not EPS $).
--
-- We emit only June statistical periods within the sample window (1982..2009).

SELECT
    cusip,
    ticker,
    toDate32(statpers) AS statpers,
    meanest,
    medest,
    numest
FROM ibes_202601.statsum_epsus
WHERE fpi = '0'
  AND fiscalp = 'LTG'
  AND measure = 'EPS'
  AND usfirm = 1
  AND toDate32(statpers) BETWEEN toDate32('1982-01-01') AND toDate32('2009-12-31')
  AND toMonth(toDate32(statpers)) = 6
  AND meanest IS NOT NULL
SETTINGS max_execution_time = 300,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
