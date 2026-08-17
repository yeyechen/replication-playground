-- ior_s34.sql
-- Purpose: Aggregate TR-13F institutional holdings to security-level, per quarter,
--          for the IOR ratio: sum over institutions of reported shares per (cusip,
--          quarter-end report date rdate).
-- Table: tr_13f_202401.s34
-- Output columns: cusip (String), rdate (Date32 quarter-end), shares (Float64),
--                 prdate (Date32) -- associated price date (used for split adjustment)
-- Depends on: none
-- Settings: max_execution_time=600
--
-- Carry-forward ("first appearance, up to 8 quarters") is applied at the point of
-- use (table1.py, June-t selection): the most recent report quarter-end <= June t is
-- used, and a security whose most recent report is more than 8 quarters stale is
-- treated as holding zero. This avoids the extreme "drop all re-filings" reading that
-- would erase genuine quarterly re-balancing and collapse IOR.

WITH raw AS (
    SELECT
        toUInt64(mgrno) AS mgrno,
        cusip,
        toDate32(rdate) AS rdate,
        toDate32(prdate) AS prdate,
        shares
    FROM tr_13f_202401.s34
    WHERE rdate >= '1980-06-30'
      AND rdate <= '2014-06-30'
      AND cusip IS NOT NULL
      AND cusip != ''
      AND shares IS NOT NULL
      AND shares > 0
)
SELECT
    cusip,
    rdate,
    SUM(shares) AS shares,
    min(prdate) AS prdate
FROM raw
GROUP BY cusip, rdate
SETTINGS max_execution_time = 600,
         max_rows_to_read = 300000000,
         timeout_before_checking_execution_speed = 0
