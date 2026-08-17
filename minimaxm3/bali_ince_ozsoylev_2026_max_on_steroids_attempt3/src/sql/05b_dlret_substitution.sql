-- 05b_dlret_substitution.sql
-- Purpose: Produce delisting-month ret substitutions for permnos that have NULL ret
--          in the panel (per Shumway 1997 / BMP 2007 convention, Assumption 1).
-- Tables: crsp_202601.msf, crsp_202601.dsfhdr, crsp_202601.dsedelist
-- Output columns: permno, month, ret_substituted, source
-- Depends on: (none)
-- Notes:
--   - For each permno, find the last (calendar) month it appears in msf (with
--     shrcd IN 10/11 + exchcd IN 1/2/3 — the universe membership).
--   - In the last month, if ret is NULL (CRSP records the position but no
--     return), substitute dlret if available.
--   - For performance-related delistings (dlstcd first digit 4=liquidation,
--     5=delisted by exchange; BMP list 300/400/500/510/520/530/540/550/560/
--     570/580/590; SEC 700-714) where dlret is also missing, apply Shumway
--     imputation: -0.30 for NYSE/AMEX (exchcd IN 1,2), -0.55 for NASDAQ
--     (exchcd = 3).
--   - The substitution target is the last month the firm appears in msf.
--     Returns ALL firms that appear at least once in msf during 1968-2022,
--     regardless of whether they had prc >= $5 in the delisting month —
--     because if the firm was in the panel in t-1 (prc >= 5) but no row at t
--     (prc < 5), the dsedelist still records the delisting and we substitute.
--   - HOWEVER, the SQL still requires prc >= 5 for the last msf row because
--     the price floor only affects row inclusion. We union with: for permnos
--     whose last msf month is at prc < 5 (i.e., the row isn't in the panel),
--     we still record the substitution for the prior month's row.

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
  msf_univ AS (
    SELECT
      toUInt32(m.permno) AS permno,
      toDate32OrNull(m.date) AS date,
      toUInt32(toYear(toDate32OrNull(m.date)) * 100 + toMonth(toDate32OrNull(m.date))) AS month,
      toFloat64(m.ret) AS ret,
      toFloat64(m.prc) AS prc,
      toFloat64(m.shrout) AS shrout,
      toUInt32(m.hexcd) AS hexcd
    FROM crsp_202601.msf AS m
    INNER JOIN hdr AS h
      ON toUInt32(m.permno) = h.permno
     AND toDate32OrNull(m.date) >= h.begdat
     AND toDate32OrNull(m.date) <= h.enddat
    WHERE toDate32OrNull(m.date) >= toDate32('1968-01-01')
      AND toDate32OrNull(m.date) <= toDate32('2022-12-31')
  ),
  -- For each permno, find the LAST month it appears in msf_univ (no prc filter).
  last_trade AS (
    SELECT
      permno,
      max(date) AS last_date,
      max(month) AS last_month
    FROM msf_univ
    GROUP BY permno
  ),
  -- The ret in the last month (typically NULL for delistings).
  last_ret AS (
    SELECT
      lt.permno,
      lt.last_month AS month,
      m.ret,
      m.hexcd AS exchcd
    FROM last_trade AS lt
    INNER JOIN msf_univ AS m
      ON lt.permno = m.permno
     AND lt.last_date = m.date
  ),
  -- Join to dsedelist via the last_date.
  dljoin AS (
    SELECT
      lr.permno,
      lr.month,
      lr.ret,
      lr.exchcd,
      d.dlret,
      toUInt32OrZero(toString(d.dlstcd)) AS dlstcd
    FROM last_ret AS lr
    LEFT JOIN crsp_202601.dsedelist AS d
      ON lr.permno = toUInt32OrZero(toString(d.permno))
     AND toDate32OrNull(d.dlstdt) BETWEEN
         toDate32OrNull(concat(toString(intDiv(lr.month, 100)), '-', toString(lr.month % 100), '-01'))
         AND toLastDayOfMonth(toDate32OrNull(concat(toString(intDiv(lr.month, 100)), '-', toString(lr.month % 100), '-01')))
  ),
  classification AS (
    SELECT
      permno,
      month,
      ret,
      exchcd,
      dlret,
      dlstcd,
      -- ret needs substitution if NULL or a missing-return sentinel.
      (ret IS NULL
        OR ret IN (-55.0, -66.0, -77.0, -88.0, -99.0)
        OR ret < -1.0) AS needs_substitution,
      -- dlret is usable if not NULL and not a missing-return sentinel.
      (dlret IS NOT NULL
        AND dlret NOT IN (-55.0, -66.0, -77.0, -88.0, -99.0, -44.0)
        AND dlret > -2.0) AS dlret_usable,
      -- Performance-related delisting per BMP (first-digit 4/5 + BMP code list
      -- + SEC 700-714).
      intDiv(dlstcd, 100) AS dlstcd_first,
      (intDiv(dlstcd, 100) IN (4, 5)
        OR dlstcd BETWEEN 300 AND 399
        OR dlstcd BETWEEN 400 AND 499
        OR dlstcd BETWEEN 500 AND 599
        OR (dlstcd BETWEEN 700 AND 714)) AS performance_related
    FROM dljoin
  )
SELECT
  permno,
  month,
  -- Compute the substituted return.
  if(
    NOT needs_substitution, ret,
    if(
      dlret_usable, dlret,
      if(
        performance_related,
        if(exchcd IN (1, 2), -0.30, -0.55),
        NULL
      )
    )
  ) AS ret_substituted,
  needs_substitution,
  dlret_usable,
  performance_related,
  ret AS ret_original,
  dlret,
  dlstcd,
  exchcd,
  -- Tag the source for downstream diagnostics.
  if(
    NOT needs_substitution, 'kept_original',
    if(dlret_usable, 'dlret_used',
       if(performance_related, 'shumway_imputed', 'null_after'))
  ) AS source
FROM classification
WHERE needs_substitution
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
