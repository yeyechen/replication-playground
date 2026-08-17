-- 01_universe_daily.sql
-- Purpose: PIT-filtered daily returns for the MAX-on-Steroids universe.
-- Tables:  crsp_202601.dsf, crsp_202601.dsenames
-- Output columns: permno, trade_date (Date32), ret, prc, vol, shrout, siccd
-- Filter rules (paper Section 3.1, preprocessing_rules.json):
--   * shrcd IN (10, 11)
--   * exchcd IN (1, 2, 3)
--   * SIC not in 4900-4949 (utilities), not in 6000-6999 (financials)
--   * ret IS NOT NULL AND ret > -0.5 (drop CRSP sentinels)
-- Period: 1968-01-01 .. 2022-12-31.
-- Notes:
--   * dsf.date and dsenames.namedt/nameendt are Nullable(String).
--     Cast both sides to Date32 via toDate32OrNull for safe PIT join.
--   * dsfhdr lacks hexcd in this vintage (see Assumption 4); fall back to
--     dsenames for both shrcd and exchcd.
--   * CRSP columns ret/prc/vol/shrout are Nullable(Float64); use them
--     directly (NULL flows through naturally).
--   * Column name is renamed to trade_date (not date) to avoid ClickHouse
--     join-clause type-coercion issues when the same name is reused across
--     CTEs.

SELECT
    d.permno                                        AS permno,
    toDate32OrNull(d.date)                          AS trade_date,
    d.ret                                           AS ret,
    d.prc                                           AS prc,
    d.vol                                           AS vol,
    d.shrout                                        AS shrout,
    coalesce(d.hsiccd, n.siccd)                     AS siccd
FROM crsp_202601.dsf AS d
INNER JOIN crsp_202601.dsenames AS n
    ON d.permno = n.permno
   AND toDate32OrNull(d.date) >= toDate32OrNull(n.namedt)
   AND toDate32OrNull(d.date) <= ifNull(toDate32OrNull(n.nameendt),
                                       toDate32('2099-12-31'))
WHERE toDate32OrNull(d.date) >= toDate32('1968-01-01')
  AND toDate32OrNull(d.date) <= toDate32('2022-12-31')
  AND n.shrcd  IN (10, 11)
  AND n.exchcd IN (1, 2, 3)
  AND d.ret IS NOT NULL
  AND d.ret > -0.5
  AND (n.siccd < 4900 OR n.siccd > 4949)
  AND (n.siccd < 6000 OR n.siccd > 6999)
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
