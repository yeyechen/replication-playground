---
iteration: 2
slug: heston_sadka_2008_seasonality_in_the_cross_section_of_stock_returns
inner_iterations: 1
worker_spawns: 1
---

# Outer Iteration 2 — Reasoning Trace

Audit 1 verdict: REPLICATED (overall 4.00), `requires_iteration: true` with 1 actionable major ([M1] T4 t-unit error) and 2 minors ([m1]/[m2] REPORT staleness). This iteration applies exactly the audit's next-iteration prompt.

## Inner iteration 1: [M1] T4 t-unit fix
**Task spec → rep-worker:** In src/table4.py compute mean and SE in the SAME units for the t calculation (keep the reported mean in table units); add a units assert; regenerate metrics + table_4.md; verify the 3 cells flip and that NO other metric changes.
**rep-worker report:** t now computed as v.mean()/(v.std(ddof=0)/sqrt(500)) in decimal^2 with an inline assert; reported mean stays x100. Corrected t's: t4_mean_all_t = -0.2515 (paper -0.26), t4_mean_nonannual_t = -0.6239 (paper -0.65), t4_mean_annual_t = 3.6220 (paper 3.57) — all three FAIL→Match. Full metrics.json diff: exactly 3 changed keys, all t4_mean_*_t; spot-checks of T1/T3/T8 cells identical.
**Replicator decision:** ACCEPT — the fix moved exactly the predicted cells and nothing else.

## [m1]/[m2] REPORT refresh (orchestrator, prose-only)
- Reversal-spread trio updated from results/table_2.md (post-Rule-B regeneration): All -1.02/-0.41/-0.03; nonannual -1.20/-0.69/-0.23/-0.38.
- VW count corrected to the scored grid: 12 VW spread cells, 12/12 Match (was "7 of 8").
- Known-open-items ledger: item 1 marked RESOLVED with the corrected values; canonical-vs-diagnostic divergence updated (1,151 vs 1,152).

## Assumption decisions this iteration
- No new assumptions; Assumption 4/5 unchanged. Iteration-11 entry in assumptions.md completed (After metric filled, Status: resolved).

## Per-cell evaluation
Canonical scorer (`scripts/score_replication.py --iteration 2`), written to `eval/scoring.json`:

```
loss            = 0.1220
n_committed     = 1312
match_count     = 1152   (rate 0.8780)
fail_count      = 160
missing_count   = 0
no_effect_count = 306
```

Per table (Match/FAIL/no_effect): T1 160/13/21 · T2 269/5/3 · T3 158/32/77 · T4 4/0/2 · T5 66/9/15 · T6 45/6/9 · T7 283/58/143 · T8 167/37/36. T4 is now a clean sweep (4 Match / 0 FAIL / 2 no_effect).

## Summary
Audit-1 [M1] applied and verified (3 cells FAIL→Match, zero collateral changes); [m1]/[m2] prose staleness fixed. Loss improved 0.1242 → 0.1220. Remaining 160 FAILs are the documented non-actionable residue (y1 January cluster, T1 short-lag t-cells, small-magnitude inference cells of null results), each with an evidenced closed-vocabulary marker in assumptions.md and accepted by audit 1 as non-actionable. No new methodology surfaces. Recommend closing under criterion B unless the audit finds a new actionable issue.
