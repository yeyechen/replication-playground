-- 07_panel.sql
-- Purpose: Master panel CTE chain — single ClickHouse query that produces
--          the analysis-ready panel used by Tables 1, 6, and 2.
-- Output columns: permno, month, MAX, BETA, ME, BM, MOM, REV, ILLIQ, IVOL,
--                 ret (current-month), ret_excess (formation-month excess),
--                 ret_next (next-month return), ret_excess_next (t+1 excess)
-- Tables:  crsp_202601.dsf, crsp_202601.msf, crsp_202601.dsenames,
--          crsp_202601.dsi, crsp_202601.ccmxpf_linktable,
--          comp_202601.funda, ff.four_factor_monthly, ff.five_factor_monthly
-- Depends on: 01-06 (inlined as CTEs)
-- Column-naming convention: the daily date column is `trade_date` (not
-- `date`) to avoid ClickHouse join-clause type-coercion issues when the
-- same name is reused across CTEs.
-- IMPORTANT: ClickHouse's `toStartOfMonth` does NOT accept Date32 — it
-- silently clamps pre-1970 dates to 1970-01-01. Use the manual calc
-- `month_start(d)` defined below for all date32->month operations.

WITH
-- Helper: month-start of a Date32 column (manual, to avoid Date clamp).
month_start AS (
    SELECT toDate32(substring(toString(d), 1, 7) || '-01') AS ms
    FROM (SELECT toDate32('1900-01-01') AS d)  -- dummy for type inference
    LIMIT 0
),

-- A. Universe: PIT-filtered daily returns
u AS (
    SELECT
        d.permno                                        AS permno,
        toDate32OrNull(d.date)                          AS trade_date,
        d.ret                                           AS ret,
        d.prc                                           AS prc,
        d.vol                                           AS vol,
        d.shrout                                        AS shrout
    FROM crsp_202601.dsf AS d
    INNER JOIN crsp_202601.dsenames AS n
        ON d.permno = n.permno
       AND toDate32OrNull(d.date) >= toDate32OrNull(n.namedt)
       AND toDate32OrNull(d.date) <= ifNull(toDate32OrNull(n.nameendt),
                                           toDate32('2099-12-31'))
    WHERE toDate32OrNull(d.date) >= toDate32('1968-01-01')
      AND toDate32OrNull(d.date) <= toDate32('2022-12-31')
      AND n.shrcd  IN (10, 11)
      AND n.exchcd IN (1, 2, 3)
      AND d.ret IS NOT NULL
      AND d.ret > -0.5
      AND (n.siccd < 4900 OR n.siccd > 4949)
      AND (n.siccd < 6000 OR n.siccd > 6999)
),

-- B. Daily market excess return (vwretd - rf_daily proxy)
rf_m AS (
    SELECT
        toDate32(dt)                                    AS month_end,
        rf / 21.0                                       AS rf_daily
    FROM ff.four_factor_monthly
    WHERE toDate32OrNull(dt) >= toDate32('1967-01-01')
      AND toDate32OrNull(dt) <= toDate32('2023-12-31')
),
mkt AS (
    SELECT
        toDate32OrNull(date)                            AS mkt_date,
        vwretd                                          AS vwretd
    FROM crsp_202601.dsi
    WHERE toDate32OrNull(date) >= toDate32('1968-01-01')
      AND toDate32OrNull(date) <= toDate32('2022-12-31')
),
ex AS (
    SELECT
        u.permno                                        AS permno,
        u.trade_date                                    AS trade_date,
        u.ret                                           AS ret,
        u.prc                                           AS prc,
        u.vol                                           AS vol,
        u.shrout                                        AS shrout,
        u.ret - r.rf_daily                              AS stock_excess,
        m.vwretd - r.rf_daily                           AS market_excess
    FROM u
    INNER JOIN mkt AS m ON u.trade_date = m.mkt_date
    INNER JOIN rf_m AS r
        ON toDate32(substring(toString(u.trade_date), 1, 7) || '-01')
         = toDate32(substring(toString(r.month_end), 1, 7) || '-01')
),

-- C. Rolling 252-day beta and ivol per (permno, trade_date)
rolled AS (
    SELECT
        permno, trade_date, ret, prc, vol, shrout, stock_excess, market_excess,
        covarPop(stock_excess, market_excess) OVER w AS cov_xy,
        varPop(market_excess)              OVER w    AS var_x,
        stddevPop(stock_excess)            OVER w    AS sd_y
    FROM ex
    WINDOW w AS (PARTITION BY permno ORDER BY trade_date
                 ROWS BETWEEN 251 PRECEDING AND CURRENT ROW)
),
beta_ivol AS (
    SELECT
        permno, trade_date,
        if(var_x > 0, cov_xy / var_x, NULL)             AS BETA,
        if(var_x > 0,
           sqrt(greatest(sd_y * sd_y - (cov_xy * cov_xy) / var_x, 0.0)),
           NULL)                                       AS IVOL
    FROM rolled
),

-- D. Monthly MAX signal with month-end prc filter and 15-day min
max_sig AS (
    SELECT
        permno,
        toDate32(substring(toString(trade_date), 1, 7) || '-01') AS month,
        arrayReduce('avg',
                    arraySlice(arrayReverseSort(groupArray(ret)), 1, 5)) AS max_raw,
        count()                                         AS ndays,
        arrayReduce('any',
                    arrayReverseSort(groupArray(prc)))  AS month_end_prc
    FROM ex
    GROUP BY permno, toDate32(substring(toString(trade_date), 1, 7) || '-01') AS month
    HAVING ndays >= 15
       AND abs(toFloat64(month_end_prc)) >= 5
),
max_clean AS (
    SELECT
        permno, month,
        if(ndays >= 5, max_raw, NULL)                   AS MAX
    FROM max_sig
),

-- E. Monthly ILLIQ = mean of |ret| / (prc * vol * 1000) over days in month, *1e6
illiq_monthly AS (
    SELECT
        permno,
        toDate32(substring(toString(trade_date), 1, 7) || '-01') AS month,
        avg(abs(ret) / nullIf(abs(prc) * vol * 1000.0, 0)) * 1000000.0 AS ILLIQ
    FROM ex
    WHERE prc IS NOT NULL AND vol IS NOT NULL
      AND abs(prc) > 0 AND vol > 0
    GROUP BY permno, toDate32(substring(toString(trade_date), 1, 7) || '-01') AS month
),

-- F. Monthly ME from msf (month-end), restricted to the universe
--    (shrcd 10/11, exchcd 1/2/3, SIC exclusion, ndays >= 15, month-end prc >= $5)
me_monthly AS (
    SELECT
        m.permno                                         AS permno,
        toDate32(substring(toString(toDate32OrNull(m.date)), 1, 7) || '-01')
                                                       AS month,
        abs(m.prc) * m.shrout * 1000.0                   AS ME,
        m.ret                                            AS ret
    FROM crsp_202601.msf AS m
    INNER JOIN crsp_202601.dsenames AS n
        ON m.permno = n.permno
       AND toDate32OrNull(m.date) >= toDate32OrNull(n.namedt)
       AND toDate32OrNull(m.date) <= ifNull(toDate32OrNull(n.nameendt),
                                           toDate32('2099-12-31'))
    -- Universe constraints
    INNER JOIN (
        SELECT permno,
               toDate32(substring(toString(trade_date), 1, 7) || '-01') AS month,
               count() AS ndays,
               arrayReduce('any', arrayReverseSort(groupArray(prc))) AS month_end_prc
        FROM ex
        GROUP BY permno,
                 toDate32(substring(toString(trade_date), 1, 7) || '-01') AS month
        HAVING ndays >= 15
    ) AS ud
        ON m.permno = ud.permno
       AND toDate32(substring(toString(toDate32OrNull(m.date)), 1, 7) || '-01') = ud.month
    WHERE toDate32OrNull(m.date) >= toDate32('1968-01-01')
      AND toDate32OrNull(m.date) <= toDate32('2022-12-31')
      AND n.shrcd  IN (10, 11)
      AND n.exchcd IN (1, 2, 3)
      AND (n.siccd < 4900 OR n.siccd > 4949)
      AND (n.siccd < 6000 OR n.siccd > 6999)
      AND m.prc IS NOT NULL
      AND m.shrout IS NOT NULL
      AND abs(m.prc) > 0
      AND m.shrout > 0
      AND abs(ud.month_end_prc) >= 5
),

-- G. Book equity from Compustat (annual)
comp AS (
    SELECT
        toString(gvkey)                                 AS gvkey,
        toDate32OrNull(datadate)                        AS datadate,
        toUInt16(fyear)                                 AS fyear,
        at                                               AS at,
        dlc                                              AS dlc,
        dltt                                             AS dltt,
        ceq                                              AS ceq,
        txdb                                             AS txdb,
        itcb                                             AS itcb,
        coalesce(pstkrv, pstkl, pstk)                   AS pstk
    FROM comp_202601.funda
    WHERE indfmt = 'INDL' AND datafmt = 'STD' AND consol = 'C' AND popsrc = 'D'
      AND toUInt16(fyear) BETWEEN 1965 AND 2022
),
book_eq AS (
    SELECT
        gvkey, datadate, fyear,
        if(ceq + txdb + itcb - pstk > 0,
           ceq + txdb + itcb - pstk,
           if(at - dlc - dltt - pstk > 0,
              at - dlc - dltt - pstk,
              NULL))                                    AS be
    FROM comp
),
link AS (
    SELECT
        toString(gvkey)                                 AS gvkey,
        toInt32(lpermno)                                AS permno,
        toDate32OrNull(linkdt)                          AS linkdt,
        ifNull(toDate32OrNull(linkenddt),
               toDate32('2099-12-31'))                  AS linkenddt
    FROM crsp_202601.ccmxpf_linktable
    WHERE linktype IN ('LU', 'LC')
      AND linkprim IN ('P', 'C')
      AND usedflag = 1
      AND lpermno IS NOT NULL
),
me_with_link AS (
    SELECT
        m.permno, m.month, m.ME, m.ret,
        l.gvkey
    FROM me_monthly AS m
    INNER JOIN link AS l
        ON m.permno = l.permno
       AND m.month >= l.linkdt
       AND m.month <= l.linkenddt
),
be_lagged AS (
    SELECT
        m.permno, m.month, m.ME, m.ret, m.gvkey,
        b.be, b.datadate,
        row_number() OVER (PARTITION BY m.permno, m.month
                           ORDER BY b.datadate DESC)    AS rn
    FROM me_with_link AS m
    INNER JOIN book_eq AS b
        ON m.gvkey = b.gvkey
       AND addMonths(b.datadate, 6) <= m.month
),
bm_monthly AS (
    SELECT
        permno, month, ME,
        if(be > 0 AND ME > 0,
           log(be / (ME / 1000000.0)),
           NULL)                                        AS BM,
        ret                                              AS mret
    FROM be_lagged
    WHERE rn = 1
),

-- H. MOM = cumulative return from t-12 to t-2 (skip the formation month t-1)
-- REV = ret in month t (the formation month itself)
mom_rev AS (
    SELECT
        permno, month, ME, BM,
        mret                                            AS REV,
        exp(sum(log(1 + mret)) OVER w) - 1              AS MOM
    FROM bm_monthly
    WINDOW w AS (PARTITION BY permno ORDER BY month
                 ROWS BETWEEN 12 PRECEDING AND 2 PRECEDING)
),

-- I. Monthly BETA / IVOL: take the last day-of-month value from beta_ivol
beta_ivol_monthly AS (
    SELECT
        permno,
        toDate32(substring(toString(trade_date), 1, 7) || '-01') AS month,
        argMax(BETA, trade_date)                        AS BETA,
        argMax(IVOL, trade_date)                        AS IVOL
    FROM beta_ivol
    GROUP BY permno,
             toDate32(substring(toString(trade_date), 1, 7) || '-01') AS month
),

-- J. Monthly Fama-French factors (calendar month-end)
factors AS (
    SELECT
        toDate32(dt)                                    AS month,
        mkt_rf                                          AS mkt_rf,
        rf                                              AS rf,
        mom                                             AS umd
    FROM ff.four_factor_monthly
    WHERE toDate32OrNull(dt) >= toDate32('1968-01-01')
      AND toDate32OrNull(dt) <= toDate32('2023-12-31')
),
panel_base AS (
    SELECT
        m.permno                                          AS permno,
        m.month                                           AS month,
        m.ME                                              AS ME,
        m.BM                                              AS BM,
        m.MOM                                             AS MOM,
        m.REV                                             AS REV,
        m.REV                                             AS ret,
        bi.BETA                                           AS BETA,
        bi.IVOL                                           AS IVOL,
        il.ILLIQ                                          AS ILLIQ,
        mx.MAX                                            AS MAX
    FROM mom_rev AS m
    LEFT JOIN max_clean         AS mx ON m.permno = mx.permno AND m.month = mx.month
    LEFT JOIN illiq_monthly     AS il ON m.permno = il.permno AND m.month = il.month
    LEFT JOIN beta_ivol_monthly AS bi ON m.permno = bi.permno AND m.month = bi.month
),
panel_with_fwd AS (
    SELECT
        pb.permno                                         AS permno,
        pb.month                                          AS month,
        pb.MAX                                            AS MAX,
        pb.BETA                                           AS BETA,
        pb.ME                                             AS ME,
        pb.BM                                             AS BM,
        pb.MOM                                            AS MOM,
        pb.REV                                            AS REV,
        pb.ILLIQ                                          AS ILLIQ,
        pb.IVOL                                           AS IVOL,
        pb.ret                                            AS ret,
        leadInFrame(pb.ret, 1) OVER w                    AS ret_next,
        f.rf                                              AS rf_cur,
        leadInFrame(f.rf, 1)  OVER w                     AS rf_next
    FROM panel_base AS pb
    LEFT JOIN factors AS f
        ON toDate32(substring(toString(pb.month), 1, 7) || '-01')
         = toDate32(substring(toString(f.month), 1, 7) || '-01')
    WINDOW w AS (PARTITION BY pb.permno ORDER BY pb.month
                 ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
)

SELECT
    permno,
    month,
    MAX,
    BETA,
    ME,
    BM,
    MOM,
    REV,
    ILLIQ,
    IVOL,
    ret                                                 AS ret,
    ret_next                                            AS ret_next,
    ret  - rf_cur                                       AS ret_excess,
    ret_next - rf_next                                  AS ret_excess_next
FROM panel_with_fwd
SETTINGS max_execution_time = 900,
         max_rows_to_read = 20000000000,
         timeout_before_checking_execution_speed = 0
