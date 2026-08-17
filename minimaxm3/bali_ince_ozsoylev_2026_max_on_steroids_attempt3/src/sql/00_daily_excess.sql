-- 00_daily_excess.sql
-- Purpose: Universe-filtered daily excess returns for CRSP sample
-- Tables: crsp_202601.dsf, crsp_202601.dsfhdr, ff.four_factor, crsp_202601.dsi
-- Output columns: permno, date, ret, stk_excess, mkt_excess, prc, vol, shrout, hexcd, hsiccd, shrcd
-- Depends on: (none) — first step in pipeline
-- Notes:
--   - Universe filter via dsfhdr PIT (Assumption 2): shrcd IN (10,11) AND exchcd IN (1,2,3).
--   - rf_daily from ff.four_factor (CRSP dsi/msf do not carry rf in this instance).
--   - dsf.ret is decimal (0.02 = 2%); no conversion needed.
--   - All dates stored as Nullable(String) in CRSP/FF; cast to Date32 consistently.
--   - This is an intermediate step; consumed by 02_max_signal.sql and 03_beta_ivol.sql.
--     Daily frequency cannot be merged into the monthly panel — saved as
--     data/daily_excess.parquet (justified per SKILL.md §data/).

SELECT
  toUInt32(d.permno) AS permno,
  toDate32OrNull(d.date) AS date,
  if(d.ret > -1.0, toFloat64(d.ret), NULL) AS ret,
  toFloat64(d.prc) AS prc,
  toFloat64(d.vol) AS vol,
  toFloat64(d.shrout) AS shrout,
  toUInt32(d.hexcd) AS hexcd,
  toUInt32(d.hsiccd) AS hsiccd,
  toUInt32(h.hshrcd) AS shrcd,
  if(d.ret > -1.0, toFloat64(d.ret), NULL) - toFloat64(rf.rf) AS stk_excess,
  toFloat64(mkt.vwretd) - toFloat64(rf.rf) AS mkt_excess,
  toFloat64(rf.rf) AS rf_daily,
  toFloat64(mkt.vwretd) AS mkt_ret
FROM crsp_202601.dsf AS d
INNER JOIN crsp_202601.dsfhdr AS h
  ON toUInt32(d.permno) = toUInt32(h.permno)
 AND toDate32OrNull(d.date) >= toDate32OrNull(h.begdat)
 AND toDate32OrNull(d.date) <= ifNull(toDate32OrNull(h.enddat), toDate32('2099-12-31'))
LEFT JOIN ff.four_factor AS rf
  ON toDate32OrNull(rf.dt) = toDate32OrNull(d.date)
LEFT JOIN crsp_202601.dsi AS mkt
  ON toDate32OrNull(mkt.date) = toDate32OrNull(d.date)
WHERE toUInt32(h.hshrcd) IN (10, 11) AND toUInt32(h.hexcd) IN (1, 2, 3)
  AND toDate32OrNull(d.date) >= toDate32('1968-01-01')
  AND toDate32OrNull(d.date) <= toDate32('2022-12-31')
  AND d.ret > -1.0
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
