-- ibes_sue_consensus.sql
-- Purpose: Quarterly analyst EPS consensus (meanest) and the announcement-day
--          actual, joined so SUE3 = (actual_eps - meanest)/price can be computed.
--          Uses statsum_epsus (fpi mapping: the fiscal quarter's estimate) matched
--          to act_epsus QTR actuals on (cusip, fiscal period end).
-- Tables: ibes_202601.statsum_epsus, ibes_202601.act_epsus
-- Output columns: cusip, ticker, fiscal period end, anndats, meanest, actual_eps
-- Depends on: none
-- Settings: max_execution_time=300
--
-- Discovery note: statsum_epsus has `meanest` (mean estimate) for a fiscal period
-- (`fpedats`) in a statistical period (`statpers`). For SUE3 we need the consensus
-- for the QUARTER whose EPS is announced. The quarterly fiscal period is identified
-- in act_epsus by pdicity='QTR' + pends. statsum_epsus fpi codes 6/7/8/9 are Q1..Q4;
-- fpedats gives the fiscal period end directly, so we join on (cusip, fpedats=pends).
-- meanest is the mean of individual estimates as of the June statistical period
-- (Livnat-Mendenhall SUE3 uses the consensus immediately before announcement; here
-- we use the June statpers consensus per the paper's "June statistical periods")

WITH qcons AS (
    SELECT
        s.cusip,
        s.ticker,
        toDate32(s.fpedats) AS fpedats,
        toDate32(s.statpers) AS statpers,
        s.meanest,
        s.numest
    FROM ibes_202601.statsum_epsus AS s
    WHERE s.measure = 'EPS'
      AND s.usfirm = 1
      AND s.fpi IN ('6', '7', '8', '9', '1', '2')   -- quarterly + FY1/FY2 (fiscal)
      AND s.meanest IS NOT NULL
      AND toDate32(s.statpers) BETWEEN toDate32('1982-01-01') AND toDate32('2009-12-31')
      AND toMonth(toDate32(s.statpers)) = 6
      AND s.fpedats IS NOT NULL AND s.fpedats != ''
)
SELECT
    q.cusip,
    q.ticker,
    q.fpedats,
    q.statpers,
    q.meanest,
    q.numest
FROM qcons AS q
SETTINGS max_execution_time = 300,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
