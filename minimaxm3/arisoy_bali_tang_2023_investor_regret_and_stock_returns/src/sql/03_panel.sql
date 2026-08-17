-- 03_panel.sql
-- Purpose: Assemble the final monthly panel — one row per (permno, month) with
--          REG, next-month excess return, ME_lag1, and the control variables
--          used in Tables 3 and 4.
-- Tables:  write_yeye.arb_universe, write_yeye.arb_reg, ff.four_factor_monthly,
--          ff.five_factor_monthly, comp_202601.funda, crsp_202601.ccmxpf_linktable
-- Output:  write_yeye.arb_panel
--          (permno, month, date, ret, ret_adj, ret_lead1, ret_excess_lead1,
--           reg, reg_raw, ret_max_industry,
--           me, me_lag1, log_me,
--           str, mom,
--           be, dec_me, bm,
--           ff_mkt_rf, ff_smb, ff_hml, ff_rf, ff_mom, ff_rmw, ff_cma,
--           ff_rf_lead, hexcd, hsiccd, sic3)
-- Depends on: 01_universe.sql, 02_reg_signal.sql
-- Notes:
--   - Period filter: month in [1963-07-01, 2020-11-01] (so ret_{t+1} is observable
--     in [1963-08, 2020-12]).
--   - ret_excess_lead1 = ret_lead1 - ff_rf_{t+1}.
--   - BM uses Compustat book equity from fiscal year ending in calendar year t-1,
--     paired with December ME from year t-1 (FF-style accounting lag, §4.1, L174).

DROP TABLE IF EXISTS write_yeye.arb_panel;

CREATE TABLE write_yeye.arb_panel ENGINE = MergeTree()
ORDER BY (assumeNotNull(month), assumeNotNull(permno)) AS
WITH
  -- Restrict universe to the analysis period.
  uni AS (
      SELECT
          toDate32(month) AS month_d32,
          permno,
          hexcd,
          hsiccd,
          intDiv(hsiccd, 10) AS sic3,
          ret,
          ret_adj,
          prc_abs,
          me,
          me_lag1,
          date AS raw_date
      FROM write_yeye.arb_universe
      WHERE toDate32(month) >= toDate32('1963-07-01')
        AND toDate32(month) <= toDate32('2020-11-01')
  ),
  reg_t AS (
      SELECT
          month AS month_d32,
          permno,
          ret_max_industry,
          reg_raw,
          reg
      FROM write_yeye.arb_reg
  ),
  -- Per-permno lead-1 return, lagged-1 return, and 12-2 momentum.
  next_ret AS (
      SELECT
          u.month_d32,
          u.permno,
          leadInFrame(u.ret_adj, 1) OVER w   AS ret_lead1,
          lagInFrame(u.ret_adj, 1)  OVER w   AS str,
          exp(sum(log(1 + greatest(u.ret_adj, -0.999))) OVER (
              PARTITION BY u.permno ORDER BY u.month_d32
              ROWS BETWEEN 12 PRECEDING AND 2 PRECEDING
          ) - 1)                             AS mom
      FROM uni AS u
      WINDOW w AS (PARTITION BY u.permno ORDER BY u.month_d32
                   ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
  ),
  -- FF factors monthly aligned on calendar month.
  -- We project dt (String, calendar month-end) to the 1st-of-month Date32 to
  -- match the universe's month column (which is the 1st of the month).
  ff_t AS (
      SELECT
          toDate32(
              toString(toYear(toDate32OrNull(dt))) || '-' ||
              lpad(toString(toMonth(toDate32OrNull(dt))), 2, '0') || '-01'
          ) AS month_d32,
          mkt_rf, smb, hml, rf, mom AS ff_mom
      FROM ff.four_factor_monthly
      WHERE toDate32OrNull(dt) >= toDate32('1963-07-01')
        AND toDate32OrNull(dt) <= toDate32('2021-12-31')
  ),
  ff5_t AS (
      SELECT
          toDate32(
              toString(toYear(toDate32OrNull(dt))) || '-' ||
              lpad(toString(toMonth(toDate32OrNull(dt))), 2, '0') || '-01'
          ) AS month_d32,
          rmw, cma
      FROM ff.five_factor_monthly
      WHERE toDate32OrNull(dt) >= toDate32('1963-07-01')
        AND toDate32OrNull(dt) <= toDate32('2021-12-31')
  ),
  -- Book equity (Compustat FF-style).
  be_raw AS (
      SELECT
          gvkey,
          fyear,
          coalesce(ceq, seq - coalesce(pstk, 0), at - lt) + coalesce(txdb, 0) AS be_value
      FROM comp_202601.funda
      WHERE indfmt = 'INDL'
        AND datafmt = 'STD'
        AND consol  = 'C'
        AND popsrc  = 'D'
        AND fyear BETWEEN 1962 AND 2020
  ),
  link_t AS (
      SELECT gvkey, toInt32(lpermno) AS permno, linkdt, linkenddt
      FROM crsp_202601.ccmxpf_linktable
      WHERE linktype IN ('LU', 'LC')
        AND linkprim IN ('P', 'C')
        AND usedflag = 1
  ),
  dec_me_t AS (
      SELECT permno, toYear(month) AS cyear, me AS dec_me
      FROM write_yeye.arb_universe
      WHERE toMonth(month) = 12
  ),
  bm_step AS (
      SELECT
          u.permno,
          u.month_d32,
          if(toMonth(u.month_d32) >= 7, toYear(u.month_d32), toYear(u.month_d32) - 1) AS holding_year
      FROM uni AS u
  ),
  bm_joined AS (
      SELECT
          s.permno        AS permno,
          s.month_d32     AS month_d32,
          s.holding_year  AS holding_year,
          sum(if(b.be_value > 0, b.be_value, NULL)) AS be
      FROM bm_step AS s
      LEFT JOIN link_t AS l
        ON s.permno = l.permno
       AND s.month_d32 >= toDate32OrNull(l.linkdt)
       AND s.month_d32 <= ifNull(toDate32OrNull(l.linkenddt), toDate32('2099-12-31'))
      LEFT JOIN be_raw AS b
        ON l.gvkey = b.gvkey
       AND b.fyear = s.holding_year - 1
      GROUP BY s.permno, s.month_d32, s.holding_year
  ),
  bm_full AS (
      SELECT
          bj.permno,
          bj.month_d32,
          bj.holding_year,
          bj.be,
          dm.dec_me
      FROM bm_joined AS bj
      LEFT JOIN dec_me_t AS dm
        ON bj.permno = dm.permno
       AND dm.cyear = bj.holding_year - 1
  )
SELECT
    u.permno                                                    AS permno,
    u.month_d32                                                 AS month,
    u.raw_date                                                  AS date,
    u.ret                                                       AS ret,
    u.ret_adj                                                   AS ret_adj,
    nr.ret_lead1                                                AS ret_lead1,
    if(nr.ret_lead1 IS NOT NULL AND ff_l.rf IS NOT NULL,
       nr.ret_lead1 - ff_l.rf,
       NULL)                                                    AS ret_excess_lead1,
    r.reg                                                       AS reg,
    r.reg_raw                                                   AS reg_raw,
    r.ret_max_industry                                          AS ret_max_industry,
    u.me                                                        AS me,
    u.me_lag1                                                   AS me_lag1,
    if(u.me_lag1 > 0, ln(u.me_lag1), NULL)                      AS log_me,
    nr.str                                                      AS str,
    nr.mom                                                      AS mom,
    bf.be                                                       AS be,
    bf.dec_me                                                   AS dec_me,
    if(bf.be > 0 AND bf.dec_me > 0,
       bf.be / (bf.dec_me / 1000.0),
       NULL)                                                    AS bm,
    ff_s.ff_mom                                                 AS ff_mom,
    ff_s.mkt_rf                                                 AS ff_mkt_rf,
    ff_s.smb                                                    AS ff_smb,
    ff_s.hml                                                    AS ff_hml,
    ff_s.rf                                                     AS ff_rf_sortmonth,
    ff5.rmw                                                     AS ff_rmw,
    ff5.cma                                                     AS ff_cma,
    u.hexcd                                                     AS hexcd,
    u.hsiccd                                                    AS hsiccd,
    u.sic3                                                      AS sic3,
    ff_l.rf                                                     AS ff_rf_lead
FROM uni AS u
INNER JOIN reg_t AS r
  ON u.permno = r.permno AND u.month_d32 = r.month_d32
LEFT JOIN next_ret AS nr
  ON u.permno = nr.permno AND u.month_d32 = nr.month_d32
LEFT JOIN ff_t AS ff_s
  ON u.month_d32 = ff_s.month_d32
LEFT JOIN ff5_t AS ff5
  ON u.month_d32 = ff5.month_d32
LEFT JOIN bm_full AS bf
  ON u.permno = bf.permno AND u.month_d32 = bf.month_d32
LEFT JOIN ff_t AS ff_l
  ON addMonths(u.month_d32, 1) = ff_l.month_d32
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;
