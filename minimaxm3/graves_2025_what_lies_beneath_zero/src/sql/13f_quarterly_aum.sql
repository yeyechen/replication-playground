-- =====================================================================
-- 13F Quarterly AUM Summary — Sub-period 2010Q1 to 2021Q4
--
-- Purpose:
--   Compute institution count and aggregate AUM by quarter for
--   Graves (2025) Table 1 partial replication.
--
-- Filters:
--   - Sub-period: 2010-01-01 to 2021-12-31
--   - Common stocks: stkcd in (NULL, '', '0')  -- TR common-stock code
--   - Valid CUSIPs and positive shares
--   - Minimum 25 positive holdings per institution-quarter
--
-- Output:
--   One row per (year, quarter) with: num_inst, total_aum_B,
--   plus institution metadata.
-- =====================================================================

WITH
-- 1. Filter to common stocks
filtered_filings AS (
    SELECT
        mgrno,
        fdate,
        cusip,
        shares,
        prc
    FROM tr_13f_202401.s34
    WHERE fdate >= '2010-01-01'
      AND fdate <= '2021-12-31'
      AND shares IS NOT NULL
      AND shares > 0
      AND cusip IS NOT NULL
      AND cusip != ''
      AND (stkcd = '0' OR stkcd = '' OR stkcd IS NULL)
),

-- 2. Aggregate at institution-quarter level (apply 25-holdings minimum)
inst_q AS (
    SELECT
        mgrno,
        fdate,
        COUNT(DISTINCT cusip) AS num_holdings,
        SUM(shares * COALESCE(prc, 0)) AS holdings_value
    FROM filtered_filings
    GROUP BY mgrno, fdate
    HAVING num_holdings >= 25
),

-- 3. Join with manager metadata to get typecode
inst_with_type AS (
    SELECT
        iq.mgrno,
        iq.fdate,
        iq.num_holdings,
        iq.holdings_value,
        sn.typecode,
        sn.country
    FROM inst_q iq
    LEFT JOIN tr_13f_202401.s34names sn
        ON iq.mgrno = sn.mgrno
)

-- 4. Final: institution-quarter panel
SELECT
    mgrno,
    fdate,
    num_holdings,
    holdings_value,
    holdings_value / 1e9 AS holdings_value_B,
    typecode,
    country
FROM inst_with_type
ORDER BY fdate, mgrno