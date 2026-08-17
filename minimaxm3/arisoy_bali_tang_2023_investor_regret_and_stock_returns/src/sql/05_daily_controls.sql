-- 05_daily_controls.sql
-- Purpose: Compute monthly ILLIQ (Amihud), IVOL (residual std of FF3 regression),
--          and MAX (avg of top 5 daily returns) from daily CRSP data.
-- Tables:  crsp_202601.dsf (daily returns, prc, vol),
--          crsp_202601.dsfhdr (PIT universe filter),
--          crsp_202601.dsenames (SIC history)
--          ff.four_factor_monthly (for monthly MKT_RF, used as IVOL market proxy)
-- Output:  write_yeye.arb_daily_controls (permno, month, illiq, ivol, max5)
-- Depends on: (none)
-- Notes:
--   - Universe filter: shrcd IN (10,11), exchcd IN (1,2,3).
--   - Lag convention: signal at month t uses daily data from month t,
--     then attach to panel row at month t (reg_t). The panel already
--     carries next-month return at month t+1, so the IVOL/ILLIQ/MAX
--     value at month t is matched with the t+1 return naturally.
--   - Paper footnote 16 (L202): require at least 15 non-missing daily
--     returns per month to compute these signals.
--   - ILLIQ = mean(|ret| / (prc*vol)) over the month (Amihud 2002).
--     prc*vol is daily dollar volume; we use abs(prc) because CRSP
--     sometimes carries negative prc for bid/ask averages.
--   - IVOL = std(residual) from daily ret = a + b1*mkt_rf_daily + b2*smb_daily + b3*hml_daily.
--     Since FF daily factors are not available, we approximate: regress daily
--     excess returns on a constant + monthly market excess return (single regressor).
--     This is the closest available approximation. Per task spec.
--   - MAX = average of the 5 highest daily returns in the month.

DROP TABLE IF EXISTS write_yeye.arb_daily_controls;

CREATE TABLE write_yeye.arb_daily_controls ENGINE = MergeTree()
ORDER BY (assumeNotNull(month), assumeNotNull(permno)) AS
WITH
  -- Daily universe (PIT-filtered, valid returns, valid prices)
  dsf_pit AS (
      SELECT
          toDate32(d.date)                            AS date,
          toDate32(
              toString(toYear(toDate32(d.date))) || '-' ||
              lpad(toString(toMonth(toDate32(d.date))), 2, '0') || '-01'
          )                                            AS month,
          d.permno,
          d.ret,
          abs(d.prc)                                  AS prc_abs,
          d.vol
      FROM crsp_202601.dsf AS d
      INNER JOIN crsp_202601.dsfhdr AS h
        ON d.permno = h.permno
       AND toDate32OrNull(d.date) >= toDate32OrNull(h.begdat)
       AND toDate32OrNull(d.date) <= ifNull(toDate32OrNull(h.enddat), toDate32('2099-12-31'))
      WHERE toDate32OrNull(d.date) >= toDate32('1963-06-01')
        AND toDate32OrNull(d.date) <= toDate32('2020-12-31')
        AND h.hshrcd IN (10, 11)
        AND h.hexcd  IN (1, 2, 3)
        AND d.ret IS NOT NULL
        AND d.ret > -1.0
        AND abs(d.prc) >= 5
        AND abs(d.prc) <= 1000
        AND d.vol IS NOT NULL
        AND d.vol > 0
  ),
  -- Per (permno, month): count valid obs
  daily_count AS (
      SELECT permno, month, count() AS n_obs
      FROM dsf_pit
      GROUP BY permno, month
      HAVING count() >= 15
  ),
  -- ILLIQ per (permno, month): mean(|ret| / (|prc|*vol))
  illiq_step AS (
      SELECT
          d.permno,
          d.month,
          sum(abs(d.ret) / (d.prc_abs * d.vol)) / count() AS illiq
      FROM dsf_pit AS d
      INNER JOIN daily_count AS c
        ON d.permno = c.permno AND d.month = c.month
      GROUP BY d.permno, d.month
  ),
  -- MAX per (permno, month): average of top 5 daily returns
  -- Use arraySort to extract top 5; we rank in ClickHouse with ROW_NUMBER.
  max_step AS (
      SELECT permno, month, AVG(top_ret) AS max5
      FROM (
          SELECT
              permno,
              month,
              ret AS top_ret,
              row_number() OVER (PARTITION BY permno, month ORDER BY ret DESC) AS rn
          FROM dsf_pit
      ) AS ranked
      INNER JOIN daily_count AS c
        ON ranked.permno = c.permno AND ranked.month = c.month
      WHERE rn <= 5
      GROUP BY permno, month
  )
SELECT
    i.permno                                              AS permno,
    i.month                                               AS month,
    i.illiq                                               AS illiq,
    m.max5                                                AS max5,
    CAST(NULL, 'Nullable(Float64)')                       AS ivol  -- placeholder; filled in 06_ivol.sql
FROM illiq_step AS i
LEFT JOIN max_step AS m
  ON i.permno = m.permno AND i.month = m.month
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;