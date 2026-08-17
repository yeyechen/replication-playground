-- 10_panel.sql
-- Final stock-month panel.
-- Uses crsp_202601.msf for monthly returns (pre-aggregated).
-- MAX(5) signal computed from crsp_202601.dsf (daily).
-- Output columns: permno, gvkey, month, ret, retx, prc, shrout, vol, me,
--                 max_5, beta_m, bm, mom, rev, illiq, roe, ivol
WITH
  monthly_base AS (
      SELECT
          m.permno                                       AS permno,
          toLastDayOfMonth(toDate32(m.date))             AS month,
          any(m.ret)                                     AS ret,
          any(m.retx)                                    AS retx,
          any(m.prc)                                     AS prc,
          any(m.shrout)                                  AS shrout,
          any(m.vol)                                     AS vol,
          any(n.siccd)                                   AS siccd
      FROM crsp_202601.msf AS m
      INNER JOIN crsp_202601.dsenames AS n
          ON m.permno = n.permno
         AND toDate32(m.date) >= toDate32(n.namedt)
         AND toDate32(m.date) <= ifNull(toDate32(n.nameendt), toDate32('2099-12-31'))
      WHERE m.ret > -1.0
        AND abs(m.prc) >= 5
        AND n.shrcd IN (10, 11)
        AND n.exchcd IN (1, 2, 3)
        AND (n.siccd < 4900 OR n.siccd > 4949)
        AND (n.siccd < 6000 OR n.siccd > 6999)
        AND toDate32(m.date) BETWEEN toDate32('1968-01-01') AND toDate32('2022-12-31')
      GROUP BY m.permno, toLastDayOfMonth(toDate32(m.date))
  ),
  daily_filt AS (
      SELECT
          d.permno                                       AS permno,
          toDate32(d.date)                               AS date,
          d.ret                                          AS ret,
          d.prc                                          AS prc,
          d.vol                                          AS vol
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
  ),
  monthly_daily_count AS (
      SELECT
          permno,
          toLastDayOfMonth(date)                         AS month,
          count(ret)                                     AS daily_obs_count
      FROM daily_filt
      GROUP BY permno, toLastDayOfMonth(date)
      HAVING count(ret) >= 15
  ),
  monthly AS (
      SELECT
          mb.permno                                      AS permno,
          mb.month                                       AS month,
          mb.ret                                         AS ret,
          mb.retx                                        AS retx,
          mb.prc                                         AS prc,
          mb.shrout                                      AS shrout,
          mb.vol                                         AS vol,
          mb.siccd                                       AS siccd
      FROM monthly_base AS mb
      INNER JOIN monthly_daily_count AS mc
          ON mb.permno = mc.permno AND mb.month = mc.month
  ),
  ranked AS (
      SELECT
          permno,
          date,
          toLastDayOfMonth(date)                         AS month_eom,
          ret,
          row_number() OVER (
              PARTITION BY permno, toLastDayOfMonth(date)
              ORDER BY ret DESC, date ASC
          )                                              AS rn
      FROM daily_filt
  ),
  max_signal AS (
      SELECT
          permno,
          month_eom                                      AS month,
          sumIf(ret, rn <= 5) / 5.0                      AS max_5
      FROM ranked
      WHERE rn <= 5
      GROUP BY permno, month_eom
      HAVING count(ret) = 5
  ),
  beta_monthly AS (
      SELECT
          security_id                                    AS permno,
          toLastDayOfMonth(toDate32(dt))                 AS month,
          argMax(beta_mktrf, toDate32(dt))               AS beta_m
      FROM ea_oneoff.dsf_beta_252
      WHERE toDate32(dt) BETWEEN toDate32('2002-01-01') AND toDate32('2022-12-31')
      GROUP BY security_id, toLastDayOfMonth(toDate32(dt))
  ),
  link AS (
      SELECT
          gvkey,
          lpermno                                        AS permno,
          toDate32OrNull(linkdt)                         AS linkdt,
          toDate32OrNull(ifNull(linkenddt, '2099-12-31')) AS linkenddt
      FROM crsp_202601.ccmxpf_linktable
      WHERE linktype IN ('LC', 'LU')
        AND linkprim IN ('P', 'C')
        AND usedflag = 1
  ),
  be AS (
      SELECT
          gvkey,
          toYear(toDate32(datadate))                    AS fyear,
          (coalesce(seq, 0)
              + coalesce(txdb, 0)
              + coalesce(itcb, 0)
              - if(isFinite(pstkrv), pstkrv,
                  if(isFinite(pstkl), pstkl,
                      if(isFinite(pstk), pstk, 0)))
          )                                              AS be
      FROM comp_202601.funda
      WHERE indfmt = 'INDL'
        AND datafmt IN ('STD', 'SUMM')
        AND consol = 'C'
        AND popsrc IN ('D', 'I')
        AND seq IS NOT NULL
  ),
  link_pit AS (
      SELECT
          m.permno                                        AS permno,
          m.month                                         AS month,
          argMax(l.gvkey, l.linkdt)                       AS gvkey
      FROM monthly AS m
      INNER JOIN link AS l
          ON m.permno = l.permno
         AND m.month >= l.linkdt
         AND m.month <= l.linkenddt
      GROUP BY m.permno, m.month
  ),
  bm AS (
      SELECT
          lp.permno                                       AS permno,
          lp.month                                        AS month,
          log(b.be / nullIf(abs(m.prc) * m.shrout / 1000.0, 0)) AS bm
      FROM link_pit AS lp
      INNER JOIN monthly AS m
          ON lp.permno = m.permno AND lp.month = m.month
      INNER JOIN be AS b
          ON lp.gvkey = b.gvkey
         AND b.fyear = if(toMonth(lp.month) >= 7,
                          toYear(lp.month) - 1,
                          toYear(lp.month) - 2)
      WHERE b.be > 0
  ),
  fundq_base AS (
      SELECT
          gvkey,
          toDate32(datadate)                             AS qe,
          ibq,
          coalesce(seqq, 0)
              + coalesce(txdbq, 0)
              - if(isFinite(pstkrq), pstkrq,
                  if(isFinite(pstkq), pstkq, 0))         AS be_q
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
          ibq / nullIf(lagInFrame(be_q, 1) OVER w, 0)    AS roe
      FROM fundq_base
      WINDOW w AS (PARTITION BY gvkey ORDER BY qe
                   ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
  ),
  roe AS (
      SELECT
          lp.permno                                       AS permno,
          lp.month                                        AS month,
          r.roe                                           AS roe
      FROM link_pit AS lp
      ASOF INNER JOIN roe_q AS r
          ON lp.gvkey = r.gvkey
         AND r.qe <= lp.month
      WHERE r.roe IS NOT NULL
  ),
  illiq AS (
      SELECT
          permno,
          toLastDayOfMonth(date)                         AS month,
          sum(abs(ret) / nullIf(abs(prc) * vol, 0)) / count(ret) * 1e6 AS illiq
      FROM daily_filt
      GROUP BY permno, toLastDayOfMonth(date)
      HAVING count(ret) >= 15
  ),
  panel_base AS (
      SELECT
          m.permno                                        AS permno,
          lp.gvkey                                        AS gvkey,
          m.month                                         AS month,
          m.ret                                           AS ret,
          m.retx                                          AS retx,
          m.prc                                           AS prc,
          m.shrout                                        AS shrout,
          m.vol                                           AS vol,
          if(abs(m.prc) * m.shrout > 0,
             abs(m.prc) * m.shrout / 1000.0,
             NULL)                                        AS me,
          ms.max_5                                        AS max_5,
          bm.bm                                           AS bm,
          roe.roe                                         AS roe,
          b.beta_m                                        AS beta_m,
          il.illiq                                        AS illiq
      FROM monthly AS m
      LEFT JOIN link_pit AS lp ON m.permno = lp.permno AND m.month = lp.month
      LEFT JOIN max_signal AS ms ON m.permno = ms.permno AND m.month = ms.month
      LEFT JOIN bm AS bm ON m.permno = bm.permno AND m.month = bm.month
      LEFT JOIN roe AS roe ON m.permno = roe.permno AND m.month = roe.month
      LEFT JOIN beta_monthly AS b ON m.permno = b.permno AND m.month = b.month
      LEFT JOIN illiq AS il ON m.permno = il.permno AND m.month = il.month
  )
SELECT
    permno,
    gvkey,
    month,
    ret,
    retx,
    prc,
    shrout,
    vol,
    me,
    max_5,
    beta_m,
    bm,
    ret                                                       AS rev,
    illiq,
    cast(NULL, 'Nullable(Float64)')                           AS ivol,
    roe
FROM panel_base
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0