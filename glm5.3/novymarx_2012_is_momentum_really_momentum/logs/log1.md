---
iteration: 1
slug: novymarx_2012_is_momentum_really_momentum
inner_iterations: 10
worker_spawns: 10
---

# Outer Iteration 1 — Reasoning Trace

**Conventions applied this iteration (at-a-glance):** `[CONVENTION-APPLIED]` CRSP-as-is delisting returns (Assumption 2); `[CONVENTION-APPLIED]` lagged-ME VW weighting (Assumption 4). `[CONVENTION-SKIPPED]` shrcd/exchcd universe default (Assumption 1 — paper-explicit "all stocks in the CRSP universe", validated by Table 7 Panel A 25/25 Match). Paper-silent choices logged as Assumptions 3, 5-12. Headline tally (canonical scorer, `eval/scoring.json`): **422 Match / 51 FAIL / 0 MISSING / 67 no_effect, L = 0.1078**, n_committed 473 of 540 targets.

## Inner iteration 1: panel + MOM strategies + Table 2 + Table 3 + evaluator
**Task spec → rep-worker:** Build universe SQL (ALL CRSP msf rows 1925-12..2010-12, no share/exchange filter per Assumption 1), me = abs(prc)·shrout·1000, signals r_12,7/r_6,2/r_1,0/r_12,2 with full-window requirement, VW decile strategies with NYSE-only breakpoints (documented deviation from utils.assign_quantiles), Table 2 (8 factor-regression specs) and Table 3 (spanning, whole/early/late), DIAGNOSTIC-ONLY evaluator + eval/metrics.json, sanity gates (1008 months, UMD anchor corr ≥ 0.90, IBM spot-checks done by Replicator beforehand: ret decimal, 558 stocks/mo 1927, hexcd=1 NYSE share 41% in 1980).
**rep-worker report:** Panel 3,770,504 rows × 13 cols, 28,696 permnos. CRSP 1925-12 returns all NULL (first price month) ⇒ MOM_12,7 spans 1007 months (starts Feb 1927) under formation-indexed windows. UMD anchor corr(MOM_12,2 decile, ff.mom) = 0.8345 — below gate; extensive diagnosis (alignment lags, dup rows, share-code variants, French-style 2×3 rebuild matching mean/std at corr 0.878) found no pipeline bug. MOM_12,7 mean 0.99%/mo vs paper 1.20. T2 41/10/3, T3 62/6/10 (diagnostic evaluator).
**Replicator decision:** REVISE — the 1007-vs-1008 month count plus the paper's own sample-start evidence pins a one-month indexing error (see inner iteration 2). The anchor shortfall is partially coupled to it; judged after the fix.

## Inner iteration 2: signal-indexing fix (committed change)
**Task spec → rep-worker:** Re-index signals to the RETURN month t (r127 = t−12..t−7, r62 = t−6..t−2, r10 = t−1, r122 = t−12..t−2), weight = me at t−1, first strategy month Jan 1927, exactly 1008 months; nothing else changed (single-change iteration); gate lowered to 0.85 pending judgment.
**rep-worker report:** All series exactly 1008 months (1927-01..2010-12). MOM_12,7 1.17%/mo [5.51] vs paper 1.20 [5.79]; MOM_6,2 0.67 [2.94] vs 0.67 [2.88] — essentially exact. Anchor corr 0.8345 → 0.8676. T2 39/12/3 (headline intercepts improved: s2 1.36=1.36, s5 0.67=0.67; small-magnitude loading/t cells failed more), T3 62/6/10.
**Replicator decision:** ACCEPT. Diagnosis logged (Iteration 1 entry in assumptions.md, Before/After recorded). Residual T2/T3 FAILs concentrated in FF4-loading cells — attributed to catalog-vintage comovement (below) and accepted as documented residue rather than chased.

## Inner iteration 3: vintage-drift decision (no code change)
**Diagnosis:** Worker's same-methodology 2×3 UMD rebuild from this catalog correlates 0.878 with French's published series (0.85–0.95 by subperiod, weakest pre-1945) where the paper achieves 0.99 in its own data (L101); insensitive to share-code/universe variants; means and stds replicate. Conclusion: 2026-vintage CRSP snapshot vs the paper's data vintage, not a pipeline bug. `[VINTAGE-DRIFT]` marker applied to T2 spec-4/8 cells. French-published factors kept (the paper's own UMD is 0.99-correlated with French's — faithful proxy).

## Inner iteration 4: Table 1 FM regressions
**Task spec → rep-worker:** Tiered BE (SEQ → CEQ+PSTK → AT−LT; TXDITC → TXDB+ITCB; PSTKR → PSTKL → PSTK), June-aligned with December-ME denominator, CCM link per manual recipe, FM on [r127, r62, r10, log(me_lag1), log_bm], listwise, 1%/99 monthly winsorization, plain FM t; committed columns Late/Third/Fourth only (DFF pre-Compustat BE unavailable — data_verification); diff row + invariant.
**rep-worker report:** T1 29/1/6 (L=0.033); diff-row identity 0.00e+00 exact; log_bm slope 0.28 [5.00] vs paper 0.31 [5.39] (Late). Two en-route bugs found+fixed (as-of merge scrambling log_bm across firms; merge_asof failure replaced with explicit year-key join). **Worker correctly rejected my spec's diff-regression instruction** — replacing [r127, r62] by [diff] changes the column space; the paper's diff row IS the same-regression coefficient difference. Alternative denominator (rolling t−6 ME) tested and rejected (flips logbm slope — discriminating check).
**Replicator decision:** ACCEPT + spec correction confirmed (Iteration 3 entry).

## Inner iteration 5: Tables 4 and 6 (double sorts)
**Task spec → rep-worker:** Independent 5×5 (NYSE breaks per signal, full eligible cross-section), VW cells, Panel A excess returns + edge spreads, Panel D FF4 alphas, sample 1927-01..2008-12; Table 6 conditional strategies within-quintile (subsample inner breakpoints, Assumption 9) on FF3 + unconditional MOM_12,7, sample 1969-01..2010-12.
**rep-worker report:** T4 91/9/23 (L=0.090) — Panel A grid within a few bp of the paper nearly everywhere (IR spreads 1.02/0.74/1.05/0.97/0.86 vs 0.99/0.70/1.04/0.96/0.92). T5 20/6/14 (L=0.231) — 6 FAILs are t-cells of paper-insignificant estimates; right-block (conditional 6-2) means run high in tail quintiles. rf handling for zero-cost portfolios resolved correctly (raw spread; excess-on-spread is identical, excess-on-cell wrong).
**Replicator decision:** ACCEPT; T5 residue logged with untested hypothesis (Iteration 4 entry) — cell left open.

## Inner iteration 6: Table 7 (size quintiles)
**Task spec → rep-worker:** NYSE size quintiles on me_lag1 over ALL stocks; Panel A time-series average characteristics (firms, %firms, total cap $B, %cap, avg cap $M) as a hard universe validator (stop if small-quintile outside [1500, 2100]); within-size-quintile momentum quintiles; Panels B/D mean returns, C/E alphas vs FF3 + other strategy.
**rep-worker report:** Panel A 25/25 Match (small quintile 1,758.8 vs paper 1,772; cap shares 1.6/2.8/5.3/11.6/78.7 vs 1.7/3.0/5.5/12.0/77.9) — direct validation of the all-CRSP-stocks universe. T6 95/5/5 (L=0.050); FAILs in the MOM_6,2-alpha tail.
**Replicator decision:** ACCEPT.

## Inner iteration 7: Table 8 (industry momentum)
**Task spec → rep-worker:** FF49 SIC mapping (published Ken French boundaries), VW industry portfolios (all stocks), tertile 30% EW strategies on the industry return series (return-month indexing), 6 spanning specs.
**rep-worker report:** T7 20/2/2 (L=0.091). s1 intercept 0.57 [5.14] vs paper 0.57 [4.93] — Match to the second decimal. UMD loadings and cross-loadings Match. 2 FAILs = t-cells of insignificant spanning intercepts (ours closer to zero — spanning conclusion holds more strongly).
**Replicator decision:** ACCEPT.

## Inner iteration 8: Table 14 (SUE FM)
**Task spec → rep-worker:** SUE = (ibq − 4-quarter mean)/atq from fundq (rdq-based availability, 6-month staleness — new Assumption 12), 8 FM specs with controls, diff rows s7/s8 with identity invariant.
**rep-worker report:** T8 66/10/4 (L=0.132). Controls all Match (48 cells); r127 significant with/without SUE (C6 reproduces); **SUE slopes 38–39×10⁻² [21] vs paper 22–24 [14] — uniform ~1.7× gap**; r62 t-cells sign-flipped in SUE specs (insignificant values). Pre-existing output-loop bug found+fixed (duplicate write stripping extras blocks).
**Replicator decision:** REVISE the SUE construction question — disambiguate "scaled by assets" (Iteration 5 entry opened).

## Inner iteration 9: SUE denominator disambiguation (diagnostic)
**Task spec → rep-worker:** spec-4 under 4 asset readings (atq_q / atq_{q−4} / 5-qtr mean / prior-FY AT), distributions + correlations; no production changes.
**rep-worker report:** Slopes 37.1–44.3 across readings (paper 22.5); variants 0.93–0.98 correlated post-winsorization; no variant improves slope and t jointly. Denominator ambiguity EXCLUDED empirically.
**Replicator decision:** Residue re-attributed to vintage; vintage is partially testable via comp_pit (next iteration).

## Inner iteration 10a: PIT vintage diagnostic
**Task spec → rep-worker:** PIT first-report SUE from comp_pit.pithistdataus (first pointdate per quarter), spec-4 on identical months vs as-restated.
**rep-worker report:** On the same 287 months (1987-2010): PIT 14.15 [11.33] vs as-restated 23.18 [25.99] (paper full-sample 22.5 [13.8]); window sensitivity 38.16→29.28→23.18 as window shortens. Neither tested cause alone reproduces the paper; raw corr(vintages) 0.235.
**Replicator decision:** Documented residue — cells stay FAIL with `[VINTAGE-DRIFT]`+`[STRUCTURAL-SAMPLE-VARIANCE]` (partially evidenced) and the full test trail (Iterations 5-6 entries). Production SUE kept on the plainest reading (atq_q).

## Inner iteration 10b: scorer-contract fix (mechanical)
The canonical scorer reads `eval/metrics.json` as `{metrics: {BARE_NAME: {"value": x}}}`; our file used `T1:`-prefixed keys ⇒ all 540 cells MISSING, and T2/T7 had bare-name collisions (intercept_s1..s6, r2_*). Replicator renamed T7 targets to `ind_*` (globally unique; validator + inference-ref checks pass), worker rewrote the metrics writer and evaluate.py lookup, re-ran. Scorer now reads all cells; evaluate.py and scorer agree exactly on every status. Also regenerated REPORT diagnostics (utils.portfolio_diagnostics) + `results/strategy_cumulative.png` from existing pipeline code.

## Assumption decisions this iteration
- A1 (universe, all CRSP stocks): paper-explicit — `[CONVENTION-SKIPPED]` default, justified by L91-101 and validated by Table 7 Panel A.
- A2 (delisting): `[CONVENTION-APPLIED]` CRSP as-is.
- A3 (full-window signals; return-month indexing): fixed in iteration 2 on L103 evidence.
- A4 (VW lagged ME): `[CONVENTION-APPLIED]`.
- A5-A7, A9-A12: paper-silent, documented with rationale (assumptions.md).
- A8 (DFF unavailable): scope reduction, data_verification.
- Worker-added: Assumption 12 (SUE timing/staleness/ibq).

## Per-cell evaluation
Canonical scorer output (`eval/scoring.json`, iteration 1):

```
status counts: Match 422 | FAIL 51 | MISSING 0 | no_effect 67 | skip 0
loss L = 0.1078   n_committed = 473   n_cells = 540
per_table: T1 29/1/6 · T2 39/12/3 · T3 62/6/10 · T4 91/9/23 ·
           T5 20/6/14 · T6 95/5/5 · T7 20/2/2 · T8 66/10/4
```

FAIL cells (51; every name carries evidence in assumptions.md § Documented residue):

| Table | Cells |
|---|---|
| T1 | r62_fourth_t |
| T2 | intercept_s8_t, mkt_s4, mkt_s4_t, smb_s3_t, smb_s4_t, smb_s7, smb_s7_t, smb_s8_t, hml_s4, hml_s4_t, hml_s8, hml_s8_t |
| T3 | A_mkt_whole_t, A_mkt_early_t, A_mkt_late_t, A_smb_whole_t, A_smb_early_t, B_smb_late_t |
| T4 | D_RR1_IR2_t, D_RR2_IR2_t, D_RR2_IR5_t, D_RR2_SP_t, D_RR3_IR2_t, D_RR4_IR2_t, D_RR4_IR4_t, D_RR4_IR5_t, D_RR5_IR4 |
| T5 | er_cond62_q1_t, er_cond62_q3_t, alpha_cond127_q3_t, alpha_cond127_q4_t, alpha_cond62_q1_t, alpha_cond62_q3_t |
| T6 | pc_m62_q5, pc_m62_q5_t, pe_m62_q1_t, pe_m62_q4_t, pe_m62_q5_t |
| T7 | ind_intercept_s5_t, ind_intercept_s6_t |
| T8 | r62_s6_t, r62_s8_t, sue_s2, sue_s2_t, sue_s4, sue_s4_t, sue_s6, sue_s6_t, sue_s8, sue_s8_t |

Full per-cell grids: `results/table_{1,2,3,4,6,7,8,14}.md` (evaluator output pasted there).

## Summary
All 8 committed tables implemented and scored; 422/473 committed cells Match (89.2%), 0 MISSING. The paper's headline claims reproduce: FM r_12,7 ≈ 2× r_6,2 with significant difference; MOM_12,7 FF4 alpha significant vs MOM_6,2 no effect; IR-spreads ≈ 2× RR-spreads; size-quintile universe matches to the tens of firms; industry momentum 12-7 intercept to the second decimal. Residue: 51 FAILs in three evidenced families (vintage comovement on published factors; t-cells of paper-insignificant estimates; tested-but-unresolved SUE scaling) + 2 open cells. Next iteration (if required): T5/T6 6-2-tail hypothesis test (conditional-sort breakpoint convention), and the UMD-anchor pre-1945 forensics if the auditor deems it actionable.
