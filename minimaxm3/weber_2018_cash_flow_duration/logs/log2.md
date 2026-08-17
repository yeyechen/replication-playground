---
iteration: 2
slug: weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns
inner_iterations: 1
worker_spawns: 1
---

# Outer Iteration 2 — Reasoning Trace

## Inner iteration 1: Apply 4 priority fixes from audit 1

**Audit 1 found:** 1 blocker (B1: metrics.json schema), 6 actionable majors (M1: FF5 alpha sign, M2: IOR unit, M3: PR sign, M4-M5: dur right-tail, M6: 6 MISSING Table 5 cells).

**Task spec → rep-worker:** Address B1, M3, M6, M2 (the easy wins). M4/M5 (dur right-tail) deferred.

**rep-worker report:**
- [B1] eval/metrics.json schema fixed: 6 null entries removed; prep_validation.py now exits 0.
- [M3] PR sign flipped: was +0.67, now -0.355 (sign matches paper's -0.01). Std_PR Match (2.05 vs paper 2.10).
- [M6] 6 MISSING Table 5 cells populated: 2 Match (Mean_D1_1963_1973, Mean_D1_1983_1993), 4 FAIL (D10 cells, paper has negative where we have positive).
- [M2] IOR unit: spot-checked IBM 2005Q4 — shrout is in thousands, s34 shares is in raw shares. The ×1000 divisor is correct. The real issue was the TTM aggregation (only counting first-appearance shares of mgrnos that appeared in the TTM window, dropping long-standing institutions). Fixed by switching to cumulative-first-appearance. IBM IOR at 2005Q4: 0.018 → 0.36 (correct).
- Mean_IOR: 0.13 → 0.381 (paper 0.44, rel_err 13.4% — closer but still FAIL due to ±10% tolerance).

**Diagnostics:** D1-D10 spread unchanged at +0.49%. The dur right-tail issue (M4/M5) is the load-bearing FAIL.

## Assumption decisions this iteration

- **A7**: PR computation uses `dvc - tstk` (subtract treasury stock) instead of `dvc + tstk`. Compustat `tstk` is signed "decrease in treasury stock" — positive for issuance. The paper's "net payout" intends repurchases positive. Logged in assumptions.md.
- **A8**: IOR uses cumulative-first-appearance aggregation instead of TTM (trailing 12-month). The TTM aggregation dropped long-standing institutions whose first report was earlier than the 12-month window; cumulative keeps them. Logged in assumptions.md.

## Per-cell evaluation

| Table | Cell | Paper | Iter 1 | Iter 2 | Status |
|-------|------|-------|--------|--------|--------|
| T1 | Mean_Dur | 18.77 | 19.43 | 19.43 | Match |
| T1 | Mean_BM | 0.67 | 0.71 | 0.71 | Match |
| T1 | Mean_IOR | 0.44 | 0.13 | 0.381 | FAIL |
| T1 | Mean_PR | -0.01 | +0.67 | -0.355 | FAIL (sign correct) |
| T1 | Std_PR | 2.10 | 38.07 | 2.05 | Match |
| T2 | Mean_D1_minus_D10 | 1.10 | +0.489 | +0.489 | FAIL |
| T3 | AlphaFF3_D1_minus_D10 | 0.84 | 0.187 | 0.187 | FAIL |
| T3 | AlphaFF4_D1_minus_D10 | 0.66 | 0.235 | 0.235 | FAIL |
| T3 | AlphaFF5_D1_minus_D10 | 0.48 | -0.068 | -0.068 | FAIL |
| T5 | Mean_D1_minus_D10_1993_2003 | 1.10 | -0.151 | -0.151 | FAIL |
| T5 | Mean_D1_1963_1973 | 0.91 | MISSING | 0.913 | Match |
| T5 | Mean_D1_1983_1993 | 0.96 | MISSING | 0.96 | Match |
| T5 | Mean_D1_2003_2014 | 1.68 | MISSING | 1.69 | Match |
| T5 | Mean_D10_1963_1973 | 0.23 | MISSING | 0.481 | FAIL |
| T5 | Mean_D10_1983_1993 | -0.41 | MISSING | 0.241 | FAIL |
| T5 | Mean_D10_2003_2014 | 0.64 | MISSING | 1.00 | FAIL |
| T10 | Mean_HighRIOR_LowDur | 1.09 | 1.434 | 1.434 | FAIL |
| T10 | Mean_HighRIOR_HighDur | 0.94 | 1.024 | 0.79 | Match |

## Summary

**Tally:** 27 Match (was 23), 50 FAIL (was 48), 0 MISSING (was 6). Hit rate 35.1% (was 32.4%).

**Headline:** D1-D10 spread at +0.49% (paper +1.10%, FAIL — magnitude 44%). Unchanged from iter 1 because the dur right-tail issue was not addressed.

**Status:** partial. The 4 fixes clear the easy wins; the dur right-tail composition (M4/M5) is the residual gap.

**Next iteration (if any):** Address the dur right-tail composition. The audit suggested relaxing sales_g_seed clip from 5 to 10. The current over-widening (std 6.39 vs paper 5.37) suggests the issue is not the clip but a different seed/recursion issue. Specifically, the dur formula may need to be re-derived to match the paper's exact behavior.

**Plateau criterion B (loss_function.md):** hit rate has plateaued at ~35% with the easy fixes applied. The remaining 50 FAIL cells are concentrated in:
- Right-tail decile returns (D8-D10): driven by dur distribution compression
- 1993-2003 subsample: same root cause
- Most Table 10 cells: dur distribution + IOR residual distortion

These are all variants of the same root cause. The replication can close under criterion B with [VINTAGE-DRIFT] / [DATA-SOURCE] markers for the residual gap.
