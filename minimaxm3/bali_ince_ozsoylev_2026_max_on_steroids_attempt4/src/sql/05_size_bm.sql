-- 05_size_bm.sql
-- Purpose: Monthly market equity (ME) and book-to-market (BM) signal.
-- Tables:  crsp_202601.msf (monthly ME), comp_202601.funda (annual book equity),
--          crsp_202601.ccmxpf_linktable (gvkey -> permno link)
-- Output columns: permno, month, ME (dollars), BM (Float64, log of book/me)
-- Notes:
--   * ME = abs(prc) * shrout * 1000 (CRSP prc in $/share, shrout in thousands).
--   * Book equity (per Assumption 6):
--       be = ceq + txdb + itcb - pstkrv
--       if be <= 0, fall back to: be = at - dlc - dltt - pstkrv
--       if pstkrv is NULL, try pstkl, then pstk.
--   * Fiscal-year t -> monthly returns July (t+1) through June (t+2).
--     Implementation: for each stock-month, attach the most-recent
--     Compustat fyear whose fiscal-year-end + 6 months <= month-end.
--   * Link: ccmxpf_linktable with linktype IN ('LU','LC'), linkprim IN ('P','C'),
--           linkdt <= month-end <= ifNull(linkenddt, '2099-12-31').
-- Depends on: (none)

WITH
comp AS (
    SELECT
        gvkey,
        toDate32OrNull(datadate)                AS datadate,
        toUInt16(fyear)                         AS fyear,
        at                                       AS at,
        dlc                                      AS dlc,
        dltt                                     AS dltt,
        ceq                                      AS ceq,
        txdb                                     AS txdb,
        itcb                                     AS itcb,
        coalesce(pstkrv, pstkl, pstk)           AS pstk
    FROM comp_202601.funda
    WHERE indfmt = 'INDL'
      AND datafmt = 'STD'
      AND consol = 'C'
      AND popsrc = 'D'
      AND toUInt16(fyear) BETWEEN 1965 AND 2022
),
book_eq AS (
    SELECT
        gvkey, datadate, fyear,
        -- primary: ceq + txdb + itcb - pstk
        if(ceq + txdb + itcb - pstk > 0,
           ceq + txdb + itcb - pstk,
           if(at - dlc - dltt - pstk > 0,
              at - dlc - dltt - pstk,
              NULL))                            AS be
    FROM comp
),
link AS (
    SELECT
        toString(gvkey)                         AS gvkey,
        toInt32(lpermno)                        AS permno,
        toDate32OrNull(linkdt)                  AS linkdt,
        ifNull(toDate32OrNull(linkenddt),
               toDate32('2099-12-31'))          AS linkenddt
    FROM crsp_202601.ccmxpf_linktable
    WHERE linktype IN ('LU', 'LC')
      AND linkprim IN ('P', 'C')
      AND usedflag = 1
      AND lpermno IS NOT NULL
),
msf AS (
    SELECT
        permno,
        toDate32OrNull(date)                    AS month,
        prc                                      AS prc,
        shrout                                   AS shrout
    FROM crsp_202601.msf
    WHERE toDate32OrNull(date) >= toDate32('1968-01-01')
      AND toDate32OrNull(date) <= toDate32('2022-12-31')
),
msf_me AS (
    SELECT
        permno, month,
        abs(prc) * shrout * 1000.0              AS me_dollars
    FROM msf
),
msf_with_link AS (
    SELECT
        m.permno,
        m.month,
        m.me_dollars,
        l.gvkey
    FROM msf_me AS m
    INNER JOIN link AS l
        ON m.permno = l.permno
       AND m.month >= l.linkdt
       AND m.month <= l.linkenddt
),
-- For each (permno, month), find the most recent book_eq observation whose
-- fyear-end + 6 months <= month.  This is the FF (1992) lag convention.
be_lagged AS (
    SELECT
        m.permno, m.month, m.me_dollars,
        b.be,
        b.datadate,
        -- Pick the row with the largest datadate still satisfying the lag
        row_number() OVER (PARTITION BY m.permno, m.month
                           ORDER BY b.datadate DESC) AS rn
    FROM msf_with_link AS m
    INNER JOIN book_eq AS b
        ON m.gvkey = b.gvkey
       AND addMonths(b.datadate, 6) <= m.month
)
SELECT
    permno,
    month,
    me_dollars                                  AS ME,
    if(be > 0 AND me_dollars > 0,
       log(be / (me_dollars / 1000000.0)),
       NULL)                                    AS BM
FROM be_lagged
WHERE rn = 1
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
