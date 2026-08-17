-- delisting.sql
-- Purpose: Delisting-return adjustment factors.
--   (a) Shumway(1997) -30% substitution for "delisted for cause" (dlstcd 400-591)
--       with a missing dlret (paper preprocessing_rules.json delisting_for_cause_missing_ret).
--   (b) Cohen et al. (2009) proration: if CRSP reports dlret several months after
--       the security stopped trading, spread the delisting return geometrically over
--       the intervening months.
-- Tables: crsp_202601.dsedelist
-- Output columns: permno, dlstdt, dlstcd, dlret_raw, dlret_eff (after -30% fix),
--                 dlpdt, nextdt, dlpdt_month, last_trade_month, n_months
-- Depends on: (none)
-- Settings: max_execution_time=300
--
-- Month-assignment worked example (documented):
--   A stock last trades in 1983-06 (msf june row exists), delists.
--   dsedelist has dlstdt='1983-06-30', dlpdt='1983-09-15' (CRSP delayed reporting),
--   dlret=-0.25. last_trade_month = 1983-06 (dlstdt month, or the final msf month).
--   The delisting return "lands" in dlpdt_month = 1983-09.
--   n_months = months strictly between them, from the month AFTER last trade through
--   the month the delisting return lands = 1983-07, 1983-08, 1983-09 -> 3 months.
--   Cohen proration: each of those 3 months gets factor (1+dlret)^(1/n)-1
--     = (1-0.25)^(1/3)-1 = -0.0914.
--   The monthly panel applies (1 + factor) in each intervening month, so the
--   chain 0.9086^3 = 0.75 reproduces 1+dlret exactly.
--
-- Output is "last trade month" and "landing month" plus the per-month geometric
-- factor; main.py expands this into (permno, adj_month, adj_ret) rows. We compute
-- n_months = 1 + monthsBetween(last_trade_month, dlpdt_month) counting the landing
-- month inclusive (i.e. number of panel months to distribute across).

SELECT
    permno,
    dlstdt,
    dlstcd,
    dlret AS dlret_raw,
    -- Fix 1: missing/negative-sentinel delisting return for "for cause" delistings
    --   -> Shumway -30%. dlret missing sentinels (-44,-55,-66,-77,-88,-99) and NULL
    --   are replaced with -0.30 when dlstcd in [400,591].
    multiIf(
        dlstcd >= 400 AND dlstcd <= 591
          AND (dlret IS NULL OR dlret <= -0.40), -0.30,
        dlret
    ) AS dlret_eff,
    dlpdt,
    nextdt,
    toStartOfMonth(toDate32(dlpdt)) AS dlpdt_month,
    toStartOfMonth(toDate32(dlstdt)) AS last_trade_month,
    -- n_months = number of panel months to distribute across = (landing month -
    -- last-trade month) in months; since both are month-starts, monthsBetween gives
    -- the gap, and we add 1 to include the landing month itself (Cohen proration).
    GREATEST(1, dateDiff('month', toStartOfMonth(toDate32(dlstdt)),
                                  toStartOfMonth(toDate32(dlpdt))) + 1) AS n_months
FROM crsp_202601.dsedelist
WHERE toDate32(dlstdt) >= toDate32('1962-07-01')
  AND toDate32(dlstdt) <= toDate32('2014-06-30')
  AND dlret_eff IS NOT NULL
SETTINGS max_execution_time = 300,
         max_rows_to_read = 2000000000,
         timeout_before_checking_execution_speed = 0
