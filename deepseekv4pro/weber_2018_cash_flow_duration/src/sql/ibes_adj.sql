-- ibes_adj.sql
-- Purpose: I/B/E/S split-adjustment discovery. `adj` lists each US firm's cumulative
--          split-adjustment factor per split DATE; `adjsum` lists the same cumulative
--          factor keyed by statistical period (statpers).
--          Key finding (audit-2 [M3], Task 1): act_epsus.value is ALREADY split-adjusted
--          to a common share basis — the `adj` factor documents the transition, and the
--          actuals file carries post-adjustment values (verified on AAPL: FY2012 raw
--          EPS ~44.15 -> act_epsus 1.5768 = 44.15/28).
-- Tables: ibes_202601.adj, ibes_202601.adjsum
-- Output columns: ticker, cusip, spdates, adj, usfirm
-- Depends on: none
-- Settings: max_execution_time=120
--
-- adj semantics: `adj` = cumulative split factor in effect AFTER the split on `spdates`
--   (the terminal factor is 1.0). Historically this is expressed relative to the current
--   share base. AAPL: 224 -> 112 -> 56 -> 28 -> 4 -> 1 (the 2014 7:1 is 28->4; the 2020
--   4:1 is 4->1). To split-adjust a raw as-then-reported EPS to the current basis,
--   multiply by adj(spdates <= t). Note act_epsus actuals are already on this basis.

SELECT
    ticker,
    cusip,
    spdates,
    adj,
    usfirm
FROM ibes_202601.adj
WHERE usfirm = 1
ORDER BY cusip, toDate32(spdates)
SETTINGS max_execution_time = 120,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
