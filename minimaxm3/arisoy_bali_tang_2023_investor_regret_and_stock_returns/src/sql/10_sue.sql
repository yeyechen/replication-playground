-- 10_sue.sql
-- Purpose: Compute standardized unexpected earnings surprise (SUE) per
--          (permno, month) from IBES, mapped to CRSP via ticker.
-- Tables:  ibes_202601.surpsumu (sue summary, has suescore column already),
--          crsp_202601.dsenames (ticker history),
--          write_yeye.arb_panel (for the permno-month grid)
-- Output:  write_yeye.arb_sue (permno, month, sue)
-- Depends on: 03_panel.sql (for the permno-month grid)
-- Notes:
--   - IBES' suescore column is exactly SUE = (actual - meanest) / surpstdev.
--   - We match IBES to CRSP via ticker + announcement date, using the
--     dsenames ticker history.
--   - We use argMax to pick the most recent SUE within a 12-month lag.

DROP TABLE IF EXISTS write_yeye.arb_sue;

CREATE TABLE write_yeye.arb_sue ENGINE = MergeTree()
ORDER BY (assumeNotNull(month), assumeNotNull(permno)) AS
WITH
  -- IBES SUE records (summary table)
  ibes_sue_raw AS (
      SELECT
          anndats                                AS anndats_str,
          oftic                                  AS oftic_str,
          suescore                               AS sue
      FROM ibes_202601.surpsumu
      WHERE anndats != ''
        AND measure = 'EPS'
        AND suescore IS NOT NULL
  ),
  ibes_sue AS (
      SELECT
          toDate32OrNull(anndats_str)            AS anndats,
          lower(oftic_str)                       AS ticker_lc,
          sue                                    AS sue
      FROM ibes_sue_raw
      WHERE toDate32OrNull(anndats_str) <= toDate32('2020-12-31')
        AND toDate32OrNull(anndats_str) >= toDate32('1965-01-01')
  ),
  -- CRSP ticker history (dsenames); we want (permno, ticker) with validity windows.
  crsp_tickers_raw AS (
      SELECT
          permno                                 AS permno_str,
          ticker                                 AS ticker_str,
          namedt                                 AS namedt_str,
          nameendt                               AS nameendt_str
      FROM crsp_202601.dsenames
      WHERE ticker != ''
  ),
  crsp_tickers AS (
      SELECT
          toInt32(permno_str)                    AS permno,
          lower(ticker_str)                      AS ticker_lc,
          toDate32OrNull(namedt_str)             AS namedt,
          ifNull(toDate32OrNull(nameendt_str), toDate32('2099-12-31')) AS nameendt
      FROM crsp_tickers_raw
      WHERE toDate32OrNull(namedt_str) <= toDate32('2020-12-31')
        AND ifNull(toDate32OrNull(nameendt_str), toDate32('2099-12-31')) >= toDate32('1965-01-01')
  ),
  -- For each IBES SUE record, attach all permnos matching the ticker at anndats.
  ibes_permno AS (
      SELECT
          ibes.anndats                           AS anndats,
          ibes.sue                               AS sue,
          crsp.permno                            AS permno
      FROM ibes_sue AS ibes
      INNER JOIN crsp_tickers AS crsp
        ON ibes.ticker_lc = crsp.ticker_lc
       AND ibes.anndats >= crsp.namedt
       AND ibes.anndats <= crsp.nameendt
  ),
  -- For each panel row, find the most recent SUE with anndats in (month-12, month].
  panel_grid AS (
      SELECT DISTINCT permno, month
      FROM write_yeye.arb_panel
  ),
  panel_with_sue AS (
      SELECT
          pg.permno                                          AS permno,
          pg.month                                           AS month,
          argMax(ip.sue, ip.anndats)                         AS sue
      FROM panel_grid AS pg
      LEFT JOIN ibes_permno AS ip
        ON pg.permno = ip.permno
       AND ip.anndats > addMonths(pg.month, -12)
       AND ip.anndats <= pg.month
      GROUP BY pg.permno, pg.month
  )
SELECT
    permno                                                                                 AS permno,
    month                                                                                  AS month,
    sue                                                                                    AS sue
FROM panel_with_sue
SETTINGS max_execution_time = 900,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;