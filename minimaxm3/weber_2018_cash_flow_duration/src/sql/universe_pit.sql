-- universe_pit.sql
-- Purpose: Build the PIT-filtered CRSP universe, restricted to common stocks
--          on NYSE/AMEX/NASDAQ, excluding financials (SIC 6000-6999) and
--          utilities (SIC 4900-4999). SIC comes from comp_202601.names
--          (historical sic) joined via crsp_202601.ccmxpf_linktable.
-- Tables:  crsp_202601.msf, crsp_202601.msenames,
--          crsp_202601.ccmxpf_linktable, comp_202601.names
-- Output columns: permno, gvkey, year, month, sic, shrcd, exchcd, hexcd,
--                  ret, retx, prc, shrout, me_dollars, linkdt, linkenddt, month_date
-- Depends on: (none)
-- Notes:
--   - Permno may map to multiple gvkeys over time; we resolve PIT using linkdt/linkenddt.
--   - shrcd/exchcd come from msenames PIT (namedt/nameendt validity windows).
--   - SIC is from comp_202601.names (historical sic with year1/year2 windows).
SELECT
  permno, month_date, year, month, hexcd, shrcd, exchcd, gvkey, sic,
  ret, retx, prc, shrout, me_dollars, linkdt, linkenddt
FROM (
  WITH
    ccm AS (
      SELECT
        gvkey,
        toUInt32OrNull(toString(lpermno)) AS lpermno,
        toDate32OrNull(linkdt) AS linkdt,
        toDate32OrNull(coalesce(nullIf(linkenddt, ''), '2099-12-31')) AS linkenddt
      FROM crsp_202601.ccmxpf_linktable
      WHERE linktype IN ('LC', 'LU')
        AND linkprim IN ('P', 'C')
        AND usedflag = 1
        AND lpermno IS NOT NULL
    ),
    comp_sic AS (
      SELECT
        gvkey,
        toInt32OrZero(toString(sic)) AS sic,
        toInt32OrZero(coalesce(nullIf(toString(year1), ''), '0')) AS year1,
        toInt32OrZero(coalesce(nullIf(toString(year2), ''), '9999')) AS year2
      FROM comp_202601.names
      WHERE sic IS NOT NULL AND length(toString(sic)) > 0
    )
  SELECT
    m.permno                          AS permno,
    toDate32(m.date)                  AS month_date,
    toUInt16(toYear(toDate32(m.date))) AS year,
    toUInt8(toMonth(toDate32(m.date))) AS month,
    m.hexcd                           AS hexcd,
    n.shrcd                           AS shrcd,
    n.exchcd                          AS exchcd,
    ccm.gvkey                         AS gvkey,
    cs.sic                            AS sic,
    m.ret                             AS ret,
    m.retx                            AS retx,
    m.prc                             AS prc,
    m.shrout                          AS shrout,
    abs(toFloat64(m.prc)) * toFloat64(m.shrout) * 1000.0 AS me_dollars,
    ccm.linkdt                        AS linkdt,
    ccm.linkenddt                     AS linkenddt
  FROM crsp_202601.msf AS m
  INNER JOIN crsp_202601.msenames AS n
    ON m.permno = n.permno
   AND toDate32(m.date) >= toDate32(n.namedt)
   AND toDate32(m.date) <= toDate32(n.nameendt)
  INNER JOIN ccm
    ON m.permno = ccm.lpermno
   AND toDate32(m.date) >= ccm.linkdt
   AND toDate32(m.date) <= ccm.linkenddt
  INNER JOIN comp_sic AS cs
    ON ccm.gvkey = cs.gvkey
   AND toUInt16(toYear(toDate32(m.date))) >= cs.year1
   AND toUInt16(toYear(toDate32(m.date))) <= cs.year2
  WHERE m.permno IS NOT NULL
    AND m.date >= '1963-01-01'
    AND m.date <= '2014-12-31'
    AND n.shrcd IN (10, 11)
    AND n.exchcd IN (1, 2, 3)
    AND NOT (cs.sic >= 6000 AND cs.sic < 7000)
    AND NOT (cs.sic >= 4900 AND cs.sic < 5000)
    AND m.prc IS NOT NULL
    AND abs(toFloat64(m.prc)) > 0
    AND m.shrout IS NOT NULL
    AND m.shrout > 0
    AND m.ret IS NOT NULL
    AND m.ret > -0.50
) t
