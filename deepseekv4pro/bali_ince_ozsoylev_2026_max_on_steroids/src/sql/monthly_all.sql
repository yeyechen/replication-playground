-- monthly_all.sql
-- Purpose: UNFILTERED monthly returns for ALL CRSP stocks (no universe filters:
--   no PIT shrcd/exchcd/SIC screen, no price screen). This is the denominator
--   universe for one-month-ahead returns: the paper's price/universe filters
--   apply only at formation month t, so the t+1 return must come from the
--   unfiltered msf file (crashes below $5 keep their negative t+1 returns;
--   delisting returns included). Columns: permno, date (month-end), ret.
--   ret here is the delisting-adjusted monthly return computed exactly as the
--   panel's `ret_adj` (delisting.sql): substitute dsedelist.dlret on the
--   delisting month when a valid dlret exists, else -0.30 for performance
--   delistings (dlstcd >= 500).
-- Tables: crsp_202601.msf, crsp_202601.dsedelist
-- Output columns: permno, date, ret
-- Depends on: delisting.sql (same delisting-adjustment convention)
-- Produces: monthly_all.parquet (Section 2b) — merged with rf -> ret_excess,
--   and month-shifted to supply the panel's ret_fwd column (T1-T9 consumers).
-- Settings: join_algorithm=partial_merge, max_execution_time=600
SELECT
    m.permno AS permno,
    m.date   AS date,
    CASE
        WHEN dl.dlret IS NOT NULL AND dl.dlret > -0.40 THEN dl.dlret
        WHEN dl.dlstcd >= 500 THEN -0.30
        ELSE m.ret
    END AS ret
FROM crsp_202601.msf AS m
LEFT JOIN (
    -- collapse dsedelist to one row per (permno, dlstdt); keep the last dlret
    -- and max dlstcd for the (rare) repeated-delisting case.
    SELECT
        permno,
        dlstdt,
        dlret,
        dlstcd
    FROM (
        SELECT
            permno,
            dlstdt,
            dlret,
            dlstcd,
            row_number() OVER (
                PARTITION BY permno, dlstdt
                ORDER BY dlret DESC, dlstcd DESC
            ) AS rn
        FROM crsp_202601.dsedelist
    )
    WHERE rn = 1
) AS dl
       ON m.permno = dl.permno
      AND m.date = dl.dlstdt
WHERE m.date >= '1968-01-01'
  AND m.date <= '2023-01-31'
  AND m.ret IS NOT NULL
  AND m.ret > -50
SETTINGS join_algorithm = 'partial_merge',
         max_execution_time = 600,
         max_rows_to_read = 20000000000,
         timeout_before_checking_execution_speed = 0
