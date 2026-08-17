-- =====================================================================
-- Aggregate by period — for Table 1 reproduction
--
-- Aggregates institution-quarter data into paper's period windows:
--   2010-2012, 2013-2016, 2017-2020, 2021
--
-- Returns one row per period with Num Inst, Total AUM, AUM SCQR (approximated)
-- =====================================================================

WITH
inst_q AS (
    SELECT
        iq.mgrno,
        iq.fdate,
        iq.num_holdings,
        iq.holdings_value
    FROM (
        SELECT
            mgrno,
            fdate,
            COUNT(DISTINCT cusip) AS num_holdings,
            SUM(shares * COALESCE(prc, 0)) AS holdings_value
        FROM tr_13f_202401.s34
        WHERE fdate >= '2010-01-01'
          AND fdate <= '2021-12-31'
          AND shares IS NOT NULL AND shares > 0
          AND cusip IS NOT NULL AND cusip != ''
          AND (stkcd = '0' OR stkcd = '' OR stkcd IS NULL)
        GROUP BY mgrno, fdate
        HAVING num_holdings >= 25
    ) iq
)

SELECT
    CASE
        WHEN toYear(toDate(fdate)) BETWEEN 2010 AND 2012 THEN '2010-2012'
        WHEN toYear(toDate(fdate)) BETWEEN 2013 AND 2016 THEN '2013-2016'
        WHEN toYear(toDate(fdate)) BETWEEN 2017 AND 2020 THEN '2017-2020'
        ELSE '2021'
    END AS period,
    count(DISTINCT mgrno) AS num_inst,
    count(DISTINCT mgrno, fdate) AS inst_quarters,
    AVG(num_holdings) AS avg_pos_hold,
    SUM(holdings_value) / 1e9 AS total_aum_B,
    SUM(holdings_value) / count(DISTINCT fdate) / 1e9 AS avg_quarterly_aum_B
FROM inst_q
GROUP BY period
ORDER BY period