-- inst_ownership.sql
-- Purpose: Annual institutional ownership ratio (IOR) from Thomson Reuters 13F (s34).
--
-- IOR calculation (paper §2 L110):
--   IOR_t = sum(holdings_{i, q}) / CRSP_total_shares_at_quarter_t
--   where i indexes the reporting institutions, q is the 13F quarter,
--   and we sum the **first-appearance** holdings only (paper: "I only keep
--   the holding data as they first appear in the database" — TR carries
--   holdings forward up to 8 quarters; first appearance means the EARLIEST
--   fdate for each (mgrno, cusip) pair).
--
--   For each June t (sort_year), we use the most recent 4 quarters of 13F data
--   (a TTM aggregation of institutional holdings).
--
--   IOR_t = 0 if the security is in CRSP but not in the 13F database.
--
-- Tables:  instown_202601.s34  (holdings, 124M rows)
-- Output columns: fyear_qtr, mgrno, cusip, shares_first
-- Depends on: (none)
--
-- Implementation note: The full IOR computation (linking s34.cusip -> ncusip -> permno
-- -> CRSP shares outstanding per quarter) is multi-stage. We split it into:
--   (1) s34_first_appearance.sql (this file): per-(cusip, mgrno) first fdate and shares.
--   (2) main.py: merge s34_first_appearance into CRSP/CCM link table to obtain permno,
--       aggregate by (permno, year, quarter) sum of shares, divide by CRSP shrout.
--
-- For this pipeline, we keep s34 holdings at the (cusip, mgrno, fdate_first) grain
-- so the Python aggregation step is straightforward.

WITH
  -- Trim to the sample period + a few quarters margin
  s34_in AS (
    SELECT
      toUInt32(mgrno)        AS mgrno,
      cusip,
      toDate32OrNull(fdate)  AS fdate,
      shares,
      typecode
    FROM instown_202601.s34
    WHERE fdate IS NOT NULL
      AND fdate >= '1978-01-01'
      AND fdate <= '2015-06-30'
      AND shares IS NOT NULL
      AND shares > 0
      AND cusip IS NOT NULL
      AND length(cusip) >= 8
  ),
  -- Keep the earliest fdate for each (mgrno, cusip) pair
  first_app AS (
    SELECT
      mgrno,
      cusip,
      argMin(fdate, fdate)  AS fdate_first,
      argMin(shares, fdate) AS shares_first
    FROM s34_in
    GROUP BY mgrno, cusip
  )
SELECT
  fdate_first,
  toUInt16(toYear(fdate_first))  AS fyear,
  toUInt8(toQuarter(fdate_first)) AS fquarter,
  mgrno,
  cusip,
  shares_first
FROM first_app
