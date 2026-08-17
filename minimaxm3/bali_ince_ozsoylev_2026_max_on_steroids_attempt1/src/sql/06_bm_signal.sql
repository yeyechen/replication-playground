-- 06_bm_signal.sql
-- Purpose: BM signal = log(BE / ME) per (permno, month)
--          BE from comp_202601.funda (via 05_book_equity.sql) per fiscal year t-1
--          mapped to months Jul(t) to Jun(t+1).
--          ME per month from 03_monthly_stock_data.sql (in $millions).
--          BE is in $millions (Compustat convention). Units match.
-- Tables: crsp_202601.ccmxpf_linktable, comp_202601.funda, crsp_202601.dsf, crsp_202601.dsenames
-- Output columns: permno, month, bm
-- Depends on: 05_book_equity.sql (built inline as CTE)
-- Notes:
--   - For each calendar month m in calendar year y:
--       If m >= 7: lookup fyear = y - 1
--       Else:       lookup fyear = y - 2
--     (since July y starts a new "formation year" that uses prior FY data.)
--   - The CRSP-Compustat link is PIT: linkdt <= month and
--     (linkenddt >= month or linkenddt IS NULL).
--   - Standard FF link filter: linktype IN ('LC','LU'), linkprim IN ('P','C'),
--     usedflag = 1.
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
  be AS (
      SELECT
          gvkey,
          toYear(datadate)                                              AS fyear,
          (coalesce(seq, 0)
              + coalesce(txdb, 0)
              + coalesce(itcb, 0)
              - if(isFinite(pstkrv), pstkrv,
                  if(isFinite(pstkl), pstkl,
                      if(isFinite(pstk), pstk, 0)))
          )                                                              AS be
      FROM comp_202601.funda
      WHERE indfmt = 'INDL'
        AND datafmt IN ('STD', 'SUMM')
        AND consol = 'C'
        AND popsrc IN ('D', 'I')
        AND seq IS NOT NULL
  ),
  monthly AS (
      SELECT
          d.permno                                                       AS permno,
          toLastDayOfMonth(toDate32(d.date))                              AS month,
          count(d.ret)                                                   AS daily_obs_count,
          argMax(d.ret, toDate32(d.date))                                AS ret,
          argMax(d.retx, toDate32(d.date))                               AS retx,
          argMax(d.prc, toDate32(d.date))                                AS prc,
          argMax(d.shrout, toDate32(d.date))                             AS shrout,
          sum(d.vol)                                                    AS vol
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
          m.permno                                                       AS permno,
          m.month                                                        AS month,
          m.ret                                                          AS ret,
          m.retx                                                         AS retx,
          m.prc                                                          AS prc,
          m.shrout                                                       AS shrout,
          m.vol                                                          AS vol,
          argMax(l.gvkey, l.linkdt)                                      AS gvkey
      FROM monthly AS m
      INNER JOIN link AS l
          ON m.permno = l.permno
         AND m.month >= l.linkdt
         AND m.month <= l.linkenddt
      GROUP BY m.permno, m.month, m.ret, m.retx, m.prc, m.shrout, m.vol
  )
SELECT
    lp.permno                                                           AS permno,
    lp.month                                                            AS month,
    log(b.be / nullIf(abs(lp.prc) * lp.shrout / 1000.0, 0))             AS bm
FROM link_pit AS lp
INNER JOIN be AS b
    ON lp.gvkey = b.gvkey
   AND b.fyear = if(toMonth(lp.month) >= 7,
                    toYear(lp.month) - 1,
                    toYear(lp.month) - 2)
WHERE b.be > 0
