-- ibes_ptg.sql
-- Purpose: June statistical-period consensus 12-month-ahead price target per
--          firm-year from I/B/E/S ptgsum (unadjusted summary). Consensus mean is
--          `meanptg` (median `medptg`, coverage `numest`). Joins to the summary/
--          actual table actpsum_epsus for the split-adjusted `price` (PTP and SUE
--          denominator) and to act_epsus ANNUAL actuals for realized growth.
-- Tables: ibes_202601.ptgsum, ibes_202601.actpsum_epsus
-- Output columns: cusip, ticker, statpers (Date32), meanptg, medptg, numest,
--                 price, prdays, shout, fvyrgro
-- Depends on: none
-- Settings: max_execution_time=300
--
-- Discovery note: ptgsum.statpers is a String (third-Thursday of month). meanptg
-- is the split-adjusted 12-month-forward consensus target ($ per share). The
-- matching current (split-adjusted) price comes from actpsum_epsus.price keyed on
-- the same (cusip, statpers). Sample window 2001..2014 (price-target availability).

WITH ptg AS (
    SELECT
        cusip,
        ticker,
        toDate32(statpers) AS statpers,
        meanptg,
        medptg,
        numest
    FROM ibes_202601.ptgsum
    WHERE measure = 'PTG'
      AND usfirm = 1
      AND toDate32(statpers) BETWEEN toDate32('2001-01-01') AND toDate32('2014-12-31')
      AND toMonth(toDate32(statpers)) = 6
      AND meanptg IS NOT NULL
),
px AS (
    SELECT
        cusip,
        toDate32(statpers) AS statpers,
        price,
        toDate32(prdays) AS prdays,
        shout,
        fvyrgro
    FROM ibes_202601.actpsum_epsus
    WHERE usfirm = 1
      AND toDate32(statpers) BETWEEN toDate32('2001-01-01') AND toDate32('2014-12-31')
      AND toMonth(toDate32(statpers)) = 6
)
SELECT
    p.cusip,
    p.ticker,
    p.statpers,
    p.meanptg,
    p.medptg,
    p.numest,
    x.price,
    x.shout,
    x.fvyrgro
FROM ptg AS p
LEFT JOIN px AS x
    ON p.cusip = x.cusip
   AND p.statpers = x.statpers
SETTINGS max_execution_time = 300,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
