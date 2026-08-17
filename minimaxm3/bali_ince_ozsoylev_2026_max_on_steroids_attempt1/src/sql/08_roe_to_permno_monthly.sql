-- 08_roe_to_permno_monthly.sql
-- Purpose: Attach ROE to the stock-month panel via gvkey-PIT link.
--          For each (permno, month), pick the most recent quarterly ROE
--          where the report date (datadate) is <= month+1 (i.e., available
--          at formation time with a 1-quarter lag in mind).
-- Tables: comp_202601.fundq (07_roe_signal), crsp_202601.ccmxpf_linktable
-- Output columns: permno, month, roe
-- Depends on: 07_roe_signal.sql
-- Notes:
--   - IBQ / BE convention: the standard paper convention uses
--     IBQ(t) / BE(t-1) where BE(t-1) is the most recent available book
--     equity, which (per "one-quarter-lagged book equity") is the prior
--     quarter's BE. We pre-computed roe = ibq / lagged_be above, so
--     here we just attach the latest roe whose qe is within the prior
--     12 months of the formation month.
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
WITH
  link AS (
      SELECT
          gvkey,
          lpermno                                                       AS permno,
          toDate32OrNull(linkdt)                                        AS linkdt,
          toDate32OrNull(ifNull(linkenddt, '2099-12-31'))               AS linkenddt
      FROM crsp_202601.ccmxpf_linktable
      WHERE linktype IN ('LC', 'LU')
        AND linkprim IN ('P', 'C')
        AND usedflag = 1
  ),
  base AS (
      SELECT
          gvkey,
          toDate32(datadate)                                            AS qe,
          ibq,
          coalesce(seqq, 0)
              + coalesce(txdbq, 0)
              + coalesce(itcbq, 0)
              - if(isFinite(pstkrq), pstkrq,
                  if(isFinite(pstkq), pstkq, 0))                        AS be_q
      FROM comp_202601.fundq
      WHERE indfmt = 'INDL'
        AND datafmt IN ('STD', 'SUMM')
        AND consol = 'C'
        AND popsrc IN ('D', 'I')
        AND ibq IS NOT NULL
        AND seqq IS NOT NULL
        AND toDate32(datadate) BETWEEN toDate32('1968-01-01') AND toDate32('2022-12-31')
  ),
  roe_q AS (
      SELECT
          gvkey,
          qe,
          ibq / nullIf(lagInFrame(be_q, 1) OVER w, 0)                   AS roe
      FROM base
      WINDOW w AS (PARTITION BY gvkey ORDER BY qe
                   ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
  ),
  monthly AS (
      SELECT
          d.permno                                                       AS permno,
          toLastDayOfMonth(toDate32(d.date))                              AS month,
          argMax(d.prc, toDate32(d.date))                                AS prc,
          argMax(d.shrout, toDate32(d.date))                             AS shrout
      FROM crsp_202601.dsf AS d
      INNER JOIN crsp_202601.dsenames AS n
          ON d.permno = n.permno
         AND toDate32(d.date) >= toDate32(n.namedt)
         AND toDate32(d.date) <= ifNull(toDate32(n.nameendt), toDate32('2099-12-31'))
      WHERE d.ret > -1.0
        AND abs(d.prc) >= 5
        AND n.shrcd IN (10, 11)
        AND n.exchcd IN (1, 2, 3)
        AND (n.siccd < 4900 OR n.siccd > 4949)
        AND (n.siccd < 6000 OR n.siccd > 6999)
        AND toDate32(d.date) BETWEEN toDate32('1968-01-01') AND toDate32('2022-12-31')
      GROUP BY d.permno, toLastDayOfMonth(toDate32(d.date))
      HAVING count(d.ret) >= 15
  ),
  link_pit AS (
      SELECT
          m.permno,
          m.month,
          argMax(l.gvkey, l.linkdt)                                      AS gvkey
      FROM monthly AS m
      INNER JOIN link AS l
          ON m.permno = l.permno
         AND m.month >= l.linkdt
         AND m.month <= l.linkenddt
      GROUP BY m.permno, m.month
  ),
  roe_attached AS (
      SELECT
          lp.permno                                                       AS permno,
          lp.month                                                        AS month,
          r.roe                                                           AS roe
      FROM link_pit AS lp
      ASOF INNER JOIN roe_q AS r
          ON lp.gvkey = r.gvkey
         AND r.qe <= lp.month
  )
SELECT permno, month, roe FROM roe_attached WHERE roe IS NOT NULL
