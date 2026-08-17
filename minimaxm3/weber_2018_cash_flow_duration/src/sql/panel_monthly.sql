-- panel_monthly.sql
-- Purpose: Build the monthly returns panel with sort_year assignment:
--          For each (permno, month) row in the universe, compute the
--          sort_year for the June sort that governs that month's return.
--
-- Convention (paper §3.1 L339): sort at end of June each year t for fiscal
-- year t-1; returns measured July t - June t+1.
--
-- So:
--   - Calendar month July Y - June Y+1 carry sort_year = Y
--   - Calendar month July Y-1 - June Y carry sort_year = Y-1
--   - January Y - June Y carry sort_year = Y-1
--
-- The "sort_year" label of a calendar row m is:
--   if month >= 7:  sort_year = year
--   else:           sort_year = year - 1
--
-- Tables:  crsp_202601.msf, crsp_202601.msenames, crsp_202601.ccmxpf_linktable,
--          comp_202601.names
-- Output columns: permno, gvkey, sort_year, month_date, year, month,
--                  hexcd, shrcd, exchcd, sic, ret, retx, prc, shrout,
--                  me_dollars
-- Depends on: universe_pit.sql shape

WITH
  base_universe AS (
    SELECT permno, month_date, year, month, hexcd, shrcd, exchcd, gvkey, sic, ret, retx, prc, shrout, me_dollars
    FROM (
      SELECT
        msf.permno                                                   AS permno,
        toDate32(msf.date)                                           AS month_date,
        toUInt16(toYear(toDate32(msf.date)))                         AS year,
        toUInt8(toMonth(toDate32(msf.date)))                         AS month,
        msf.hexcd                                                    AS hexcd,
        msen.shrcd                                                   AS shrcd,
        msen.exchcd                                                  AS exchcd,
        ccm.gvkey                                                    AS gvkey,
        cs.sic                                                       AS sic,
        msf.ret                                                      AS ret,
        msf.retx                                                     AS retx,
        msf.prc                                                      AS prc,
        msf.shrout                                                   AS shrout,
        abs(toFloat64(msf.prc)) * toFloat64(msf.shrout) * 1000.0     AS me_dollars
      FROM crsp_202601.msf AS msf
      INNER JOIN crsp_202601.msenames AS msen
        ON msf.permno = msen.permno
       AND toDate32(msf.date) >= toDate32(msen.namedt)
       AND toDate32(msf.date) <= toDate32(msen.nameendt)
      INNER JOIN (
        SELECT
          gvkey,
          toUInt32OrNull(toString(lpermno)) AS lpermno,
          toDate32OrNull(linkdt) AS linkdt,
          toDate32OrNull(coalesce(nullIf(linkenddt, ''), '2099-12-31')) AS linkenddt
        FROM crsp_202601.ccmxpf_linktable
        WHERE linktype IN ('LC','LU') AND linkprim IN ('P','C') AND usedflag = 1
          AND lpermno IS NOT NULL
      ) AS ccm
        ON msf.permno = ccm.lpermno
       AND toDate32(msf.date) >= ccm.linkdt
       AND toDate32(msf.date) <= ccm.linkenddt
      INNER JOIN (
        SELECT
          gvkey,
          toInt32OrZero(toString(sic)) AS sic,
          toInt32OrZero(coalesce(nullIf(toString(year1), ''), '0')) AS year1,
          toInt32OrZero(coalesce(nullIf(toString(year2), ''), '9999')) AS year2
        FROM comp_202601.names
        WHERE sic IS NOT NULL AND length(toString(sic)) > 0
      ) AS cs
        ON ccm.gvkey = cs.gvkey
       AND toUInt16(toYear(toDate32(msf.date))) >= cs.year1
       AND toUInt16(toYear(toDate32(msf.date))) <= cs.year2
      WHERE msf.permno IS NOT NULL
        AND msf.date >= '1963-01-01'
        AND msf.date <= '2014-12-31'
        AND msen.shrcd IN (10, 11)
        AND msen.exchcd IN (1, 2, 3)
        AND NOT (cs.sic >= 6000 AND cs.sic < 7000)
        AND NOT (cs.sic >= 4900 AND cs.sic < 5000)
        AND msf.prc IS NOT NULL
        AND abs(toFloat64(msf.prc)) > 0
        AND msf.shrout IS NOT NULL
        AND msf.shrout > 0
        AND msf.ret IS NOT NULL
        AND msf.ret > -0.50
    ) t
  )
SELECT
  permno,
  gvkey,
  if(month >= 7, year, year - 1) AS sort_year,
  month_date,
  year,
  month,
  hexcd,
  shrcd,
  exchcd,
  sic,
  ret,
  retx,
  prc,
  shrout,
  me_dollars
FROM base_universe
