---
iteration: 1
slug: heston_sadka_2008_seasonality_in_the_cross_section_of_stock_returns
inner_iterations: 10
worker_spawns: 10
---

# Outer Iteration 1 — Reasoning Trace

Paper: Heston & Sadka (2008), JFE 87, 418-445. 1,618 target cells across 8 tables (budget_flag set — full-grid commitment). All 8 tables implemented; 0 MISSING.

## Inner iteration 1: Panel + universe diagnostics + Table 2
**Task spec → rep-worker:** Build monthly panel 1945-2002 (msf + dsfhdr PIT shrcd 10/11 + exchcd 1/2 paper-explicit; no $5 screen — skip justified by Fig-1 diagnostics; no delisting merge yet), formation lag sets for 15 strategies (Rule A complete-window eligibility), equal-count deciles, EW grid + VW spreads, evaluator + metrics plumbing.
**rep-worker report:** Panel 1,364,007 rows; Jan-1965 eligible 1,922 (<2,000 ✓); 240-month histories 678-928 (>500 ✓); 120-month at 1999 1,356 (>1,000 ✓); hexcd agreement 1.000. Delisting diagnostic: msf.ret EXCLUDES delret in this vintage (19/19 total-loss cases). T2 tally 265 Match / 9 FAIL / 3 no_effect; FAILs in y1 loser deciles (y1_all_d1 1.30 vs paper 0.64).
**Replicator decision:** ACCEPT panel (all guards pass); REVISE delisting treatment — diagnostic evidence overturns Assumption 4's initial reading (Shumway msf-only bias signature).

## Inner iteration 2: Delisting merge + Table 2 re-run
**Task spec → rep-worker:** Merge msedelist (combined (1+ret)(1+dlret)-1; dlret-alone insert; -0.30 for 500-599 missing dlret; same PIT filter on delisting month). One change only.
**rep-worker report:** 4,197 delisting rows merged (555 combined, 3,642 inserted). T2 268/6/3; 3 FAILs closed (y1_all_spread 0.59→0.83); no Match→FAIL flips. Residual: y1 All/Nonannual spreads still low (0.83/0.43 vs 1.46/1.17).
**Replicator decision:** ACCEPT (delisting evidence attached to Assumption 4). Diagnose residual y1 gap — hypothesis: formation eligibility (recent listings).

## Inner iteration 3: Eligibility A/B/C experiment
**Task spec → rep-worker:** Standalone experiment only — Rule B (≥1 available formation month, mean of available) and Rule C (≤2 missing) vs Rule A for y1 and y2_5.
**rep-worker report:** Rule B does NOT fix y1 (0.83→0.80, 0.43→0.45). Rule B materially closer for y2_5 (Annual 0.92→0.69 vs paper 0.67; RMSE 0.042 vs 0.173). Found my "before" snapshot was stale (post-merge Rule A: y2_5 All -0.90, y1 Annual 1.32).
**Replicator decision:** Eligibility hypothesis for y1 REJECTED. Rule B promising for longer windows — defer global switch until long intervals tested. Next: Table 1 as independent panel validator (gamma_1 = -5.03 is the reversal test).

## Inner iteration 4: Table 1 (FM return responses)
**Task spec → rep-worker:** Panel A simple regressions at 31 lags (pairwise availability), Panel B 3 multiple-regression specs (listwise), NW(12) t-stats, percent units.
**rep-worker report:** gamma_1 = -4.99 [-8.84] vs paper -5.03 [-9.03] — panel reversal validated. gamma_12 2.79 vs 2.61. T1 159/14/21; 14 FAILs at short lags (2-8). No rank deficiency in Panel B.
**Replicator decision:** ACCEPT. The y1 decile gap is NOT a weak-reversal artifact. Diagnose: (a) does the delisting merge inflate short-lag FM cells, (b) where in the calendar is the y1 spread lost, (c) Rule B on long intervals.

## Inner iteration 5: Three-part diagnostic
**Task spec → rep-worker:** (a) T1 short-lag cells pre-merge vs post-merge; (b) calendar-month decomposition of y1 spreads vs Table 7; (c) Rule A vs B for y6_10/y11_15/y16_20.
**rep-worker report:** (a) Post-merge closer in 15/16 cells — merge KEPT. (b) y1 gap concentrated in January (ours -7.14 vs paper -4.49) + Feb/Mar weak; May/Jun/Dec match. (c) Rule B matches or beats A on every long-interval paper cell (Annual: 0.71/0.71/0.49 vs paper 0.68/0.66/0.52); nothing breaks.
**Replicator decision:** COMMIT Rule B globally (Assumption 5 revised with correction note). y1 January residual to be bounded later.

## Inner iteration 6: Rule B commit + Table 3
**Task spec → rep-worker:** Commit Rule B; re-run T2; implement T3 FF3 alphas (deciles excess-of-rf; spreads; VW prose cells).
**rep-worker report:** T2 269/5/3 (annual spreads land on paper; y11_15 pair fixed). T3 first pass 141/49/77 — spread alphas uniformly ~0.47 (mean rf) BELOW paper; our raw spreads match.
**Replicator decision:** Zero-investment alpha convention bug (rf subtracted from L/S spreads — the documented utils trap). Fix committed next spawn.

## Inner iteration 7: T3 fix + Tables 5 and 7
**Task spec → rep-worker:** Spreads regress RAW spread on factors (rf cancels in the paper's difference-of-decile-alphas); implement T5 (30/40/30 size groups) and T7 (calendar-month decomposition + difference rows).
**rep-worker report:** T3 158/32/77 (y2_5 Annual alpha 0.64 [4.69] vs paper 0.65 [5.11]; VW y16_20 sign restored). T5 66/9/15 (group sizes within paper bands). T7 283/58/143 (y2_5 Annual Feb-Dec 0.38 vs 0.38 exact).
**Replicator decision:** ACCEPT all three. Remaining FAIL clusters: y1 January, small-t cells.

## Inner iteration 8: Tables 4 and 6
**Task spec → rep-worker:** T4 WRSS pi over all 480-month pairs (pair-common demeaning, pop-SD/√500 SE); T6 MG-20 industry decomposition (SIC mapping per Assumption 8).
**rep-worker report:** T6 45/6/9 (intra components match; paper prose-vs-table swap at L2386 identified — table wins). T4 0/4/2 — pi means ~10x too large, positive at ALL lags including k=1.
**Replicator decision:** T4 REJECT — pi(1) must be negative given our own gamma_1 = -4.99; suspect NaN zero-fill or wrong demeaning set. T6 ACCEPT.

## Inner iteration 9: T4 debug + Table 8
**Task spec → rep-worker:** Cross-validate T4 against table1 covariance internals; fix defect; implement T8 (event months via CCM/msedist/fundq/funda).
**rep-worker report:** T4 defect = NaN zero-fill (masked cells held -mA, injecting mA*mB per missing stock). Fixed; cross-validation agrees to floating point. T4 means: all -0.0010, nonannual -0.0023, annual 0.0147 vs paper -0.0006/-0.0019/0.0133 (annual Match; implied SD 1.21% vs 1.15%). T8 167/37/36 (pa_event 0.84 [3.55] vs 0.78 [3.30]).
**Replicator decision:** ACCEPT. T4 t-cells FAIL on magnitude — flagged for SE-construction test.

## Inner iteration 10: Final diagnostics + plots + regeneration
**Task spec → rep-worker:** y1-January variants (history screen, ME screen, pre-merge); T4 SE readings (3); Fig-2 plot + P&L plot; full regeneration.
**rep-worker report:** No decisive y1 fix (variants (i)/(iii) move ≤0.3pp; (ii) breaks annual cells). No alternative SE reading reproduces paper t's. Plots written. Final: 1,148 Match / 164 FAIL / 306 no_effect / 0 MISSING (diagnostic evaluator).
**Replicator decision:** DIAGNOSIS ON T4 UNITS: our t's ÷100 = 3.622/-0.252/-0.624 vs paper 3.57/-0.26/-0.65 (within 1.5-4% on all three) — a x100 unit error (mean in table units, SE in decimal^2). One-line fix SPECIFIED but DEFERRED: the 10-inner-iteration cap is reached; the fix goes to outer iteration 2. Documented in assumptions.md iteration 10 with the exact expected before/after.

## Assumption decisions this iteration
- A1 [CONVENTION-APPLIED] shrcd 10/11 via dsfhdr PIT.
- A2 (paper-explicit) exchcd 1/2 — NYSE/AMEX only, overrides harness default (1,2,3).
- A3 [CONVENTION-SKIPPED] $5 price screen — justified by paper's own Fig-1 universe diagnostics (Jan-1965 count <2,000 reproduced at 1,922).
- A4 [CONVENTION-APPLIED, evidence-revised] delisting merge after the iteration-1 diagnostic (msf.ret excludes delret in crsp_202601).
- A5 REVISED to Rule B eligibility after A/B/C + long-interval experiments (annual spreads within 0.03 of paper at every interval).
- A6 [CONVENTION-APPLIED] VW weights mcap_lag1.
- A7 [applied] listwise availability for Panel B specs.
- A8 [applied] MG-20 SIC mapping reconstructed (14 groups observed; 'other' 1.28%).
- A9 [applied] T4 unit conversion (decimal^2 x 100).
- A10 [applied] event-month fields (rdq/dclrdt/exdt/datadate+1; rdq effectively starts 1971).
- A11/A12 [applied] equal-count deciles; percent reporting.

## Per-cell evaluation
Canonical scorer (`scripts/score_replication.py`, iteration 1) — full per-cell table in `eval/scoring.json`; verbatim evaluator printout in `results/evaluation_summary.md`. Aggregate:

```
loss            = 0.1242   (0 = all Match, 1 = all non-Match)
n_cells         = 1618
n_committed     = 1312   (denominator)
match_count     = 1149   (rate 0.8758)
fail_count      = 163
missing_count   = 0
no_effect_count = 306    (excluded from loss)
```

Per table (Match/FAIL/no_effect): T1 160/13/21 · T2 269/5/3 · T3 158/32/77 · T4 1/3/2 · T5 66/9/15 · T6 45/6/9 · T7 283/58/143 · T8 167/37/36. Diagnostic evaluator prints 1,148/164 — 1-cell canonical divergence, canonical wins ([CANONICAL-DIVERGENCE] noted in REPORT.md).

## Summary
All 8 tables implemented, 0 MISSING, L = 0.1242 (87.6% Match). Both headline claims replicate (C1: full annual-lag pulse train incl. gamma_1 anchor; C2: annual decile spreads 1.32-0.49 vs paper 1.15-0.52 with reversal pattern). One actionable fix is specified and pending: the T4 t-stat x100 unit error (inner cap reached). The residual y1-January FAILs carry an evidenced [STRUCTURAL-SAMPLE-VARIANCE] classification (6 variants tested; regression counterpart matches exactly). Next iteration should: apply the T4 unit fix, re-run the canonical scorer, and address whatever the audit surfaces.
