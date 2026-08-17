-- panel.sql
-- Purpose: Build the analysis-ready monthly panel skeleton: universe_monthly
--          (PIT common-stock universe, ex-finl/utilities, NO price floor, valid returns,
--          me_dollars) -> monthly rows July t .. June t+1 per stock, with
--          sort_year / formation labels and lagged market equity (me_prev).
--          The cross-section of duration sorts (end-of-June sort on Dur of fiscal
--          year t-1) is assembled in Python on return-flat panel rows because it
--          requires the duration values computed in numpy in main.py (not a SQL
--          expression), and delisting-adjusted returns are merged in Python from
--          delisting.sql.
-- Tables: crsp_202601.msf, crsp_202601.msfhdr
-- Output columns: permno, date, month (month-start), sort_year, ret, prc, shrout,
--                 hsiccd, me_dollars, me_prev
-- Depends on: universe_monthly.sql (same PIT universe filter, re-expressed so the
--             price floor and return filter stay in SQL; see notes)
-- Settings: join_algorithm=partial_merge, max_execution_time=600
--
-- Formation labeling (FF-style, references/SKILL.md "FF-style panel formation_year"):
--   A calendar month row is in the July-t-through-June-(t+1) cohort opened by the
--   end-of-June-t sort. Label sort_year = if(month>=7, year, year-1): a July-Dec
--   row in calendar Y belongs to sort year Y; a Jan-Jun row in calendar Y belongs
--   to sort year Y-1 (the cohort that opened the prior July).
--
-- RETURN handling: SQL carries raw ret and drop sentinels; the delisting adjustment
--   runtime-merged in Python (see delisting.sql). The $5 price floor was REMOVED
--   (iteration 4, A2 reversed) — all common stocks with a valid return enter. Only
--   the missing-return sentinel filter is applied here so the pipeline does not
--   carry sentinel rows into Python.

SELECT
    permno,
    date,
    -- NOTE: do NOT use toStartOfMonth(date) here — it returns a 32-bit `Date`
    -- which silently clamps every pre-1970 row to 1970-01-01 (references/
    -- CLICKHOUSE.md § Date and time types). Use toDate32(formatDateTime(...))
    -- so month-starts are correct back to July 1963.
    toDate32(formatDateTime(toDate32(date), '%Y-%m-01')) AS month,
    if(toMonth(date) >= 7, toYear(date), toYear(date) - 1) AS sort_year,
    ret,
    prc,
    shrout,
    hsiccd,
    me_dollars,
    lagInFrame(me_dollars, 1) OVER w AS me_prev
FROM
(
    SELECT
        m.permno,
        toDate32(m.date) AS date,
        m.ret,
        m.prc,
        m.shrout,
        h.hsiccd AS hsiccd,
        abs(m.prc) * m.shrout * 1000 AS me_dollars
    FROM crsp_202601.msf AS m
    INNER JOIN crsp_202601.msfhdr AS h
        ON m.permno = h.permno
       AND toDate32(m.date) >= toDate32(h.begdat)
       AND toDate32(m.date) <= toDate32(h.enddat)
    WHERE toDate32(m.date) >= toDate32('1962-07-01')
      AND toDate32(m.date) <= toDate32('2014-06-30')
      AND h.hshrcd IN (10, 11)
      AND h.hexcd IN (1, 2, 3)
      AND (h.hsiccd < 4900 OR h.hsiccd >= 5000)
      AND (h.hsiccd < 6000 OR h.hsiccd >= 7000)
      -- A2 REVERSED (iteration 4): no $5 price floor — the floor inflates universe
      -- EW from 1.24% to 2.01%/mo by removing low-return penny stocks, incompatible
      -- with the paper's Table 2 means. All common stocks with a valid return enter.
      AND m.ret IS NOT NULL
      AND m.ret > -1.0               -- drop missing-return sentinels
)
WINDOW w AS (PARTITION BY permno ORDER BY date
             ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0
