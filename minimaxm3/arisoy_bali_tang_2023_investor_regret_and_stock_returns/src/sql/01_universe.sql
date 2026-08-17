-- 01_universe.sql
-- Purpose: Build PIT-filtered monthly universe for REG panel (1963-06 to 2020-12).
--          Extends one month earlier than the sort period (1963-07) so that
--          me_lag1 (size snapshot at end of June 1963) is available for the
--          first sort month.
-- Tables:  crsp_202601.msf, crsp_202601.dsfhdr, crsp_202601.dsedelist
-- Filters: shrcd IN (10,11), exchcd IN (1,2,3), $5 <= |prc| <= $1000
-- Output:  write_yeye.arb_universe (date, month, permno, hexcd, hsiccd, sic3,
--                                   ret, ret_adj, prc_abs, me, me_lag1)
-- Depends on: (none)
-- Notes:
--   - Uses dsfhdr PIT (hshrcd/hexcd + begdat/enddat) per Assumption 2.
--   - hsiccd is the historical SIC at month-end (used for 3-digit industry).
--   - sic3 = floor(hsiccd / 10) gives 3-digit SIC code.
--   - For each stock-month, substitute ret with dlret when the stock delisted in
--     that month (Shumway-style: -0.30 fallback when dlret missing & dlstcd in 500-598).
--   - me_lag1 = me from t-1 (lagged one month within permno).
--   - msf.date and dsfhdr.begdat/enddat are stored as String; parse to Date32.

DROP TABLE IF EXISTS write_yeye.arb_universe;

CREATE TABLE write_yeye.arb_universe ENGINE = MergeTree()
ORDER BY (assumeNotNull(month), assumeNotNull(permno)) AS
WITH
  msf_with_pit AS (
      SELECT
          toDate32(m.date)                       AS date,
          toDate32(
              toString(toYear(toDate32(m.date))) || '-' ||
              lpad(toString(toMonth(toDate32(m.date))), 2, '0') || '-01'
          )                                       AS month,
          m.permno,
          m.hexcd,
          m.hsiccd,
          intDiv(m.hsiccd, 10)                   AS sic3,
          m.ret                                  AS ret,
          abs(m.prc)                             AS prc_abs,
          abs(m.prc) * m.shrout                  AS me
      FROM crsp_202601.msf AS m
      INNER JOIN crsp_202601.dsfhdr AS h
        ON m.permno = h.permno
       AND toDate32OrNull(m.date) >= toDate32OrNull(h.begdat)
       AND toDate32OrNull(m.date) <= ifNull(toDate32OrNull(h.enddat), toDate32('2099-12-31'))
      WHERE toDate32(m.date) >= toDate32('1963-06-01')
        AND toDate32(m.date) <= toDate32('2020-12-31')
        AND h.hshrcd IN (10, 11)
        AND h.hexcd  IN (1, 2, 3)
        AND abs(m.prc) >= 5
        AND abs(m.prc) <= 1000
        AND m.ret > -1.0
        AND m.ret IS NOT NULL
  ),
  dlret_lookup AS (
      SELECT
          toDate32(
              toString(toYear(toDate32OrNull(dlstdt))) || '-' ||
              lpad(toString(toMonth(toDate32OrNull(dlstdt))), 2, '0') || '-01'
          )                                       AS dl_month,
          permno,
          if(
              dlret > -0.40,
              dlret,
              if(dlstcd BETWEEN 500 AND 598, -0.30, -0.30)
          )                                       AS dlret_adj
      FROM crsp_202601.dsedelist
      WHERE toDate32OrNull(dlstdt) >= toDate32('1963-06-01')
        AND toDate32OrNull(dlstdt) <= toDate32('2021-06-30')
  ),
  universe AS (
      SELECT
          u.date,
          u.month,
          u.permno,
          u.hexcd,
          u.hsiccd,
          u.sic3,
          u.ret,
          if(d.permno IS NOT NULL, d.dlret_adj, u.ret) AS ret_adj,
          u.prc_abs,
          u.me
      FROM msf_with_pit AS u
      LEFT JOIN dlret_lookup AS d
        ON u.permno = d.permno
       AND u.month = d.dl_month
  )
SELECT
    date,
    month,
    permno,
    hexcd,
    hsiccd,
    sic3,
    ret,
    ret_adj,
    prc_abs,
    me,
    lagInFrame(me, 1) OVER w AS me_lag1
FROM universe
WINDOW w AS (PARTITION BY permno ORDER BY month
             ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
SETTINGS max_execution_time = 300,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;
