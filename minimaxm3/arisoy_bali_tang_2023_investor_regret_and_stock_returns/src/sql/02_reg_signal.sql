-- 02_reg_signal.sql
-- Purpose: Compute REG signal per (permno, month).
--          REG_{i,t} = -(R_{i,t} - max_j[R_{j,t}]) where j ranges over all OTHER
--          stocks sharing the same 3-digit SIC code with stock i in month t.
-- Tables:  write_yeye.arb_universe (output of 01_universe.sql)
-- Output:  write_yeye.arb_reg (permno, month, ret, ret_max_industry, reg_raw, reg)
-- Depends on: 01_universe.sql
-- Notes:
--   - reg_raw = -(ret - ret_max_industry) is always <= 0 (per §3, L148-152).
--   - reg = -reg_raw is the sign-flipped value; >= 0 by construction.
--   - For stocks where sic3 <= 0 (no industry code), reg is set to NULL
--     (industry-relative signal is undefined).
--   - reg == 0  -> stock was the industry leader (R_i = max_j R_j)
--   - reg > 0   -> stock lagged the industry leader
--   - max value of reg in (permno, month) within an industry = industry's
--     worst-vs-best gap (loss extent).

DROP TABLE IF EXISTS write_yeye.arb_reg;

CREATE TABLE write_yeye.arb_reg ENGINE = MergeTree()
ORDER BY (assumeNotNull(month), assumeNotNull(permno)) AS
WITH
  base AS (
      -- For each (permno, month, ret), the 3-digit SIC industry code.
      -- Exclude rows with missing/zero SIC so we don't compute reg against an
      -- "industry" that is actually every-sic3=0 stock.
      SELECT permno, month, ret, sic3
      FROM write_yeye.arb_universe
      WHERE sic3 > 0
        AND ret IS NOT NULL
  ),
  industry_max AS (
      -- Max return per (month, 3-digit SIC).
      SELECT month, sic3, max(ret) AS ret_max_industry
      FROM base
      GROUP BY month, sic3
  )
SELECT
    b.permno,
    b.month,
    b.ret,
    im.ret_max_industry,
    b.ret - im.ret_max_industry            AS reg_raw,   -- always <= 0 (per paper Eq. 5)
    im.ret_max_industry - b.ret            AS reg         -- always >= 0 (sign-flipped per L166)
FROM base AS b
INNER JOIN industry_max AS im
  ON b.month = im.month
 AND b.sic3  = im.sic3
SETTINGS max_execution_time = 300,
         max_rows_to_read = 10000000000,
         timeout_before_checking_execution_speed = 0;
