-- 09_op_ia.sql
-- Purpose: Compute operating profitability (OP) and investment/asset growth (IA)
--          per stock-month from Compustat annual fundamentals.
--          OP = (sale - cogs - xsga - dp) / be, paired using FF-style lag:
--               fiscal year t-1 paired with calendar year t (Jul t to Jun t+1).
--          IA = at_t / at_t-1  using the same lag convention.
-- Tables:  comp_202601.funda, crsp_202601.ccmxpf_linktable,
--          write_yeye.arb_panel (for permno-month grid)
-- Output:  write_yeye.arb_op_ia (permno, month, op, ia)
-- Depends on: 03_panel.sql (for the permno-month grid)
-- Notes:
--   - The paper convention is to use fiscal-year t-1 fundamentals from
--     July of calendar year t to June of calendar year t+1 (FF-style lag).
--   - We compute OP using (sale - cogs - xsga - dp), the standard FF2015
--     recipe. When any of cogs/xsga/dp are missing we use 0 for that term.
--   - IA = at_t / at_t-1, where at_t is total assets at fiscal year t.
--     For the first year of a firm's history, IA is undefined (no at_t-1).

DROP TABLE IF EXISTS write_yeye.arb_op_ia;

CREATE TABLE write_yeye.arb_op_ia ENGINE = MergeTree()
ORDER BY (assumeNotNull(month), assumeNotNull(permno)) AS
WITH
  -- Annual fundamentals (already filtered in 03_panel.sql, replicate here)
  comp_raw AS (
      SELECT
          gvkey,
          fyear,
          -- BE = ceq + txdb (FF-style; txdb=0 if missing)
          coalesce(ceq, seq - coalesce(pstk, 0), at - lt) + coalesce(txdb, 0) AS be_value,
          at,
          sale,
          cogs,
          xsga,
          dp
      FROM comp_202601.funda
      WHERE indfmt = 'INDL'
        AND datafmt = 'STD'
        AND consol  = 'C'
        AND popsrc  = 'D'
        AND fyear BETWEEN 1962 AND 2020
  ),
  -- CRSP-Compustat link
  link_t AS (
      SELECT gvkey, toInt32(lpermno) AS permno, linkdt, linkenddt
      FROM crsp_202601.ccmxpf_linktable
      WHERE linktype IN ('LU', 'LC')
        AND linkprim IN ('P', 'C')
        AND usedflag = 1
  ),
  -- For each panel row, attach gvkey via PIT link
  panel_permno AS (
      SELECT DISTINCT permno, month
      FROM write_yeye.arb_panel
  ),
  panel_linked AS (
      SELECT
          p.permno                                            AS permno,
          p.month                                             AS month,
          l.gvkey                                             AS gvkey
      FROM panel_permno AS p
      LEFT JOIN link_t AS l
        ON p.permno = l.permno
       AND p.month >= toDate32OrNull(l.linkdt)
       AND p.month <= ifNull(toDate32OrNull(l.linkenddt), toDate32('2099-12-31'))
  ),
  -- For each (permno, month), compute the FF "holding_year" mapping and join
  -- Compustat fundamentals from fiscal year (holding_year - 1).
  panel_with_op AS (
      SELECT
          pl.permno                                          AS permno,
          pl.month                                           AS month,
          if(toMonth(pl.month) >= 7, toYear(pl.month), toYear(pl.month) - 1) AS holding_year,
          pl.gvkey                                           AS gvkey,
          -- OP = (sale - cogs - xsga - dp) / be, with null terms treated as 0
          (coalesce(c.sale, 0) - coalesce(c.cogs, 0) - coalesce(c.xsga, 0) - coalesce(c.dp, 0))
              / nullIf(c.be_value, 0)                        AS op,
          c.at                                               AS at_t
      FROM panel_linked AS pl
      LEFT JOIN comp_raw AS c
        ON pl.gvkey = c.gvkey
       AND c.fyear = if(toMonth(pl.month) >= 7, toYear(pl.month), toYear(pl.month) - 1) - 1
  ),
  panel_with_at_prev AS (
      SELECT
          po.permno                                          AS permno,
          po.month                                           AS month,
          po.op                                              AS op,
          po.at_t                                            AS at_t,
          c_prev.at                                          AS at_prev
      FROM panel_with_op AS po
      LEFT JOIN comp_raw AS c_prev
        ON po.gvkey = c_prev.gvkey
       AND c_prev.fyear = if(toMonth(po.month) >= 7, toYear(po.month), toYear(po.month) - 1) - 2
  )
SELECT
    permno                                                                                 AS permno,
    month                                                                                  AS month,
    op                                                                                     AS op,
    if(at_t > 0 AND at_prev > 0, at_t / at_prev, NULL)                                      AS ia
FROM panel_with_at_prev
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;