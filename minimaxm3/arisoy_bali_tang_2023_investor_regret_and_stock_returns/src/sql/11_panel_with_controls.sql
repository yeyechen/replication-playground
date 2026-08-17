-- 11_panel_with_controls.sql
-- Purpose: Combine the panel with all 12 control variables into a single
--          enriched panel. This is the analysis-ready dataset for Table 3.
-- Tables:  write_yeye.arb_panel, write_yeye.arb_beta, write_yeye.arb_coskew,
--          write_yeye.arb_daily_controls, write_yeye.arb_ivol, write_yeye.arb_op_ia,
--          write_yeye.arb_sue
-- Output:  write_yeye.arb_panel_full
-- Depends on: 03_panel.sql, 05_daily_controls.sql, 06_ivol.sql,
--             07_beta.sql, 08_coskew.sql, 09_op_ia.sql, 10_sue.sql

DROP TABLE IF EXISTS write_yeye.arb_panel_full;

CREATE TABLE write_yeye.arb_panel_full ENGINE = MergeTree()
ORDER BY (assumeNotNull(month), assumeNotNull(permno)) AS
SELECT
    p.permno                                          AS permno,
    p.month                                           AS month,
    p.hexcd                                           AS hexcd,
    p.ret                                             AS ret,
    p.ret_excess_lead1                                AS ret_excess_lead1,
    p.me_lag1                                         AS me_lag1,
    p.reg                                             AS reg,
    -- The 12 control variables
    p.log_me                                          AS log_me,    -- SIZE
    p.bm                                              AS bm,        -- BM
    p.mom                                             AS mom,       -- MOM
    p.str                                             AS str,       -- STR
    b.beta                                            AS beta,      -- BETA
    cs.coskew                                         AS coskew,    -- COSKEW
    iv.ivol                                           AS ivol,      -- IVOL
    dc.max5                                           AS max5,      -- MAX
    dc.illiq                                          AS illiq,     -- ILLIQ
    op.op                                             AS op,        -- OP
    op.ia                                             AS ia,        -- IA
    sue.sue                                           AS sue        -- SUE
FROM write_yeye.arb_panel AS p
LEFT JOIN write_yeye.arb_beta AS b
  ON p.permno = b.permno AND p.month = b.month
LEFT JOIN write_yeye.arb_coskew AS cs
  ON p.permno = cs.permno AND p.month = cs.month
LEFT JOIN write_yeye.arb_daily_controls AS dc
  ON p.permno = dc.permno AND p.month = dc.month
LEFT JOIN write_yeye.arb_ivol AS iv
  ON p.permno = iv.permno AND p.month = iv.month
LEFT JOIN write_yeye.arb_op_ia AS op
  ON p.permno = op.permno AND p.month = op.month
LEFT JOIN write_yeye.arb_sue AS sue
  ON p.permno = sue.permno AND p.month = sue.month
SETTINGS max_execution_time = 600,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;