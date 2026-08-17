-- 05_panel_base.sql
-- Purpose: PIT-filtered monthly CRSP panel (one row per permno-month)
-- Tables: crsp_202601.msf, crsp_202601.dsfhdr, crsp_202601.ccmxpf_linktable
-- Output columns: permno, month, date, ret, prc, shrout, hexcd, hsiccd, shrcd, gvkey
-- Depends on: (none)
-- Notes:
--   - Universe filter: shrcd IN (10,11) AND exchcd IN (1,2,3) AND abs(prc) >= 5
--   - month = YYYYMM (UInt32), last-trading-day-of-month convention
--   - gvkey attached via ccmxpf_linktable (linktype IN ('LC','LU'), linkprim IN ('P','C'),
--     usedflag=1) — most recent active link per permno (argMax).
--   - SIC attached in Python (panel_base_assembly) from comp_202601.co_industry,
--     keyed by (gvkey, calendar_year of month_end_date). Co_industry is yearly,
--     and the SIC lookup is cheap relative to the main panel pull.

WITH
  hdr AS (
    SELECT
      toUInt32(permno) AS permno,
      toUInt32(hshrcd) AS shrcd,
      toUInt32(hexcd) AS exchcd,
      toDate32OrNull(begdat) AS begdat,
      ifNull(toDate32OrNull(enddat), toDate32('2099-12-31')) AS enddat
    FROM crsp_202601.dsfhdr
    WHERE toUInt32(hshrcd) IN (10, 11) AND toUInt32(hexcd) IN (1, 2, 3)
  ),
  msf_filt AS (
    SELECT
      toUInt32(m.permno) AS permno,
      toDate32OrNull(m.date) AS date,
      -- Compute YYYYMM directly (avoids ClickHouse's toLastDayOfMonth
      -- pre-1970 clamp bug).
      toUInt32(toYear(toDate32OrNull(m.date)) * 100 + toMonth(toDate32OrNull(m.date))) AS month,
      toFloat64(m.ret) AS ret,
      toFloat64(m.prc) AS prc,
      toFloat64(m.shrout) AS shrout,
      toFloat64(m.vol) AS vol,
      toUInt32(m.hexcd) AS hexcd,
      toUInt32(m.hsiccd) AS hsiccd,
      h.shrcd AS shrcd_pit
    FROM crsp_202601.msf AS m
    INNER JOIN hdr AS h
      ON toUInt32(m.permno) = h.permno
     AND toDate32OrNull(m.date) >= h.begdat
     AND toDate32OrNull(m.date) <= h.enddat
    WHERE toDate32OrNull(m.date) >= toDate32('1968-01-01')
      AND toDate32OrNull(m.date) <= toDate32('2022-12-31')
      AND abs(toFloat64(m.prc)) >= 5.0
  ),
  link AS (
    SELECT permno, gvkey FROM (
      SELECT
        toUInt32OrZero(toString(lpermno)) AS permno,
        gvkey,
        row_number() OVER (PARTITION BY lpermno ORDER BY linkdt DESC) AS rnk
      FROM crsp_202601.ccmxpf_linktable
      WHERE linktype IN ('LC', 'LU')
        AND linkprim IN ('P', 'C')
        AND usedflag = 1
    )
    WHERE rnk = 1
  )
SELECT
  m.permno,
  m.month,
  m.date AS month_end_date,
  m.ret,
  m.prc,
  m.shrout,
  m.vol,
  m.hexcd,
  m.hsiccd,
  l.gvkey AS gvkey
FROM msf_filt AS m
LEFT JOIN link AS l
  ON m.permno = l.permno
WHERE m.shrcd_pit IN (10, 11)
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
