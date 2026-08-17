-- 04_ff_factors.sql
-- Purpose: Pull Fama-French factor monthly time series used for portfolio
--          alpha regressions in Tables 1 and 3.
-- Tables:  ff.four_factor_monthly (FF3 + RF + MOM/UMD), ff.five_factor_monthly
--          (FF5: adds RMW and CMA).
-- Output:  write_yeye.arb_ff (calendar-month aligned)
-- Depends on: (none)
-- Notes:
--   - ff.four_factor_monthly has dt (calendar month-end) -> mkt_rf, smb, hml, rf, mom.
--   - ff.five_factor_monthly has dt -> mkt_rf, smb, hml, rmw, cma, rf.
--   - Note: LIQ (Pastor-Stambaugh) is NOT in the available ClickHouse ff tables
--     per data_verification.json — see Assumption 3.

DROP TABLE IF EXISTS write_yeye.arb_ff;

CREATE TABLE write_yeye.arb_ff ENGINE = MergeTree()
ORDER BY (assumeNotNull(month)) AS
SELECT
    f4.month                                                     AS month,
    f4.mkt_rf                                                    AS ff_mkt_rf,
    f4.smb                                                       AS ff_smb,
    f4.hml                                                       AS ff_hml,
    f4.rf                                                        AS ff_rf,
    f4.mom                                                       AS ff_mom,
    f5.rmw                                                       AS ff_rmw,
    f5.cma                                                       AS ff_cma
FROM (
    SELECT
        toDate32(
            toString(toYear(toDate32OrNull(dt))) || '-' ||
            lpad(toString(toMonth(toDate32OrNull(dt))), 2, '0') || '-01'
        ) AS month,
        mkt_rf, smb, hml, rf, mom
    FROM ff.four_factor_monthly
    WHERE toDate32OrNull(dt) >= toDate32('1963-07-01')
      AND toDate32OrNull(dt) <= toDate32('2021-12-31')
) AS f4
LEFT JOIN (
    SELECT
        toDate32(
            toString(toYear(toDate32OrNull(dt))) || '-' ||
            lpad(toString(toMonth(toDate32OrNull(dt))), 2, '0') || '-01'
        ) AS month,
        rmw, cma
    FROM ff.five_factor_monthly
    WHERE toDate32OrNull(dt) >= toDate32('1963-07-01')
      AND toDate32OrNull(dt) <= toDate32('2021-12-31')
) AS f5
  ON f4.month = f5.month
SETTINGS max_execution_time = 60,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;
