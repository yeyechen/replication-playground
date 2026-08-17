---
iteration: 5
verdict: FAILED
blocker_count: 0
actionable_major_count: 0
requires_iteration: false
---

# Audit Report 5 — bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to

**Verdict:** FAILED
**Date:** 2026-08-14
**Auditor notes:** FINAL iteration of the 5-iter cap. Iter-5 ran one diagnostic (panel period coverage gap, surfaced by audit4 [M1]): the source data exists for 1968-1969 in `crsp_202601.msf` (25,838 / 26,610 rows) and `dsf` (488,614 / 558,342 daily rows), but the `monthly_daily_count` CTE's `count(ret) >= 15` requirement drops early-year stocks with sparse daily observations, so the panel starts at 1970-01. This is now documented as Limitation 6 in `assumptions.md` with `[DIAGNOSE-PENDING]` marker. Canonical loss remains L = 1.0000 (Match=0, FAIL=52, MISSING=30) — identical to iter-4 because no metric-producing code changed. The 5-iter hard cap is now hit; the replicator exits under documented-residue criterion B. Verdict remains FAILED by both bright-line (overall < 3.0) and kill switch (three dimensions at 1: concrete_result, signal_strength, corollary). `requires_iteration: false` because (a) we are at the hard cap (per the SKILL.md hard cap rule), and (b) every remaining failing cell carries a closed-vocabulary marker with diagnostic evidence. The exit is final; no further iterations are possible.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 3/5 | 6/8 sub-checks pass. Iter-5 added one more diagnostic test (panel period coverage source-data check) and updated Limitation 6 in `assumptions.md`. The marker upgrade chain `[STRUCTURAL-SAMPLE-VARIANCE]` → `[DIAGNOSE-PENDING]` (iter-4) → documented Limitation 6 (iter-5) is the right discipline but does not close the magnitude gap. Diagnostic 8 (significance reproduction) still fails: T1 P10_RET_RF sign flip persists (paper -0.32, ours +0.77), T6 SPREAD_RET_RF magnitude 7x off (paper -0.81, ours -0.12). |
| Headline matching | 2/5 | C1 (T6 SPREAD_RET_RF): paper -0.81, ours -0.12 — direction matches, magnitude 7x attenuated (r = 0.148, outside any band). T1 SPREAD_RET_RF: paper -0.95, ours -0.32 — direction matches, r = 0.33 (band-2 boundary). T1 P10_RET_RF: paper -0.32, ours +0.77 — wrong sign on the high-MAX leg. |
| Data coverage | 4/5 | Period (paper 1968-2022; panel 1970-2022 — 23-month gap at the start). Iter-5 diagnostic confirmed the gap is a pipeline filter, not a source-data gap: `crsp_202601.msf` has 1968/1969 data but the `count(ret) >= 15` requirement drops them. Documented as Limitation 6 with `[DIAGNOSE-PENDING]` marker. Universe (~2655 stocks/month, NYSE/AMEX/NASDAQ common stocks, $5+ price, SIC exclusions, 15+ daily obs) matches paper. CRSP/Compustat/FF sources all match. Pre-2002 beta gap documented. Third-party factors (PS-LIQ, SY MGMT/PERF, DHS FIN/PEAD) absent from catalog. Join hygiene clean. |
| Concrete result matching | 1/5 | 0 of 82 cells Match (0.00%) — band <30%. Canonical scorer (DEV-019): match=0, fail=52, missing=30, skip=0, loss=1.0. Five-iteration plateau (iter 1 L=0.9634 → iter 2 L=1.0 → iter 3 L=1.0 → iter 4 L=1.0 → iter 5 L=1.0). Iter-5 did not modify any metric-producing code, so the canonical tally is identical to iter-4. |
| Signal strength | 1/5 | Worst-case headline cell: T6_SPREAD_RET_RF — paper -0.81, ours -0.12 → r = 0.148 (sign matches but r outside [0.33, 3.0]). T6 P10_RET_RF: paper -0.10, ours +0.80 (sign flip, r = 8.0). T1 P10_RET_RF: paper -0.32, ours +0.77 (sign flip, r = 2.4). |
| Corollary | 1/5 | T2 (12 cells, characteristics spread) entirely MISSING across five audits. T4 (18 cells, INST-stratified MAX^beta) entirely MISSING across five audits. 0 of 56 corollary cells have a computed result. C2 (mispricing), C3 (MAX^beta MIS/CE spreads), C4 (heterogeneous skewness preference across INST terciles) — all untestable in the artifact set. |
| **Overall** | **2.00** | FAILED by both bright line (overall < 3.0) and kill switch (three dimensions at 1: concrete_result, signal_strength, corollary). |

## 2. Issues by severity

### Blockers (must fix)

None. The audit-4 blockers ([B1] T6 spread collapse; [B2] T1 P10_RET_RF sign flip; [B3] T2/T4 not built) remain unresolved at the metric level but are now classified under documented-residue criterion B with closed-vocabulary markers. The 5-iter hard cap has been hit, so no further iterations are possible.

### Major (should fix)

All audit-4 majors and blockers have been retired under documented-residue criterion B with appropriate closed-vocabulary markers. Each carries diagnostic evidence in `assumptions.md`:

- **[M1]** Period truncation: panel 1970-01 to 2022-12 vs paper 1968-01 to 2022-12 (23-month gap at the start) — NOW documented as Limitation 6 in `assumptions.md` with `[DIAGNOSE-PENDING]` marker. Iter-5 diagnostic (`logs/log5.md` Diagnostic 3) confirmed the source data exists in `crsp_202601.msf` (1968: 25,838 rows; 1969: 26,610 rows) and `crsp_202601.dsf` (1968: 488,614 daily rows; 1969: 558,342 daily rows), but the panel pipeline's `count(ret) >= 15` requirement in the `monthly_daily_count` CTE drops these early-year stocks with sparse daily observations. The 23-month gap is a documented panel-coverage finding, not a source-data gap. **Status: documented; non-actionable within time budget.**

- **[M2]** T1 magnitude gap (~3x attenuation on 10-1 spread; P10_RET_RF sign flip) — documented as `[DIAGNOSE-PENDING]` in `assumptions.md`. Iter-4 diagnostic test (MAX-5 hand-verification, lag-1 ME weighting) ruled out two of four previously-hedged causes; iter-5 added the period-coverage diagnostic to the list of tested causes. The remaining candidate drivers (RF series vintage, universe vintage) are non-actionable within time budget. **Status: documented; non-actionable within time budget.**

- **[M3]** T6 spread collapse (paper -0.81, ours -0.12) — documented as `[STRUCTURAL-SAMPLE-VARIANCE]` in `assumptions.md`. The dependent MAX^beta double-sort runs on 2002-2022 only (38% of paper's window due to pre-2002 beta unavailability in `ea_oneoff.dsf_beta_252`). Combined with the T1 magnitude gap, the effect washes out. **Status: documented; non-actionable within time budget.**

- **[M4]** T2 (12 cells) and T4 (18 cells) MISSING — both unbuilt across five audits. Per the SKILL.md hard cap rule, the 5-iter cap has been hit. Building T2/T4 would require substantial additional work (13F INST construction, characteristic spreads across all deciles, IVOL signal computation) outside the time budget. **Status: documented; non-actionable within time budget.**

### Minor (cleanup)

- **[m1]** REPORT.md line 5 still cites iter-1 tally wording (DEV-010 regression; fourth audit).
  - File: `REPORT.md:5` describes "Match=0, FAIL=52, MISSING=30, SKIP=0. Loss `L = 1.0000`" — this matches canonical `eval/scoring.json` for iter-5 (loss=1.0, match=0, fail=52, missing=30, skip=0). Actually re-rendered correctly for iter-4/iter-5; iter-2 and iter-3 audits flagged this as stale. **Status: resolved as of iter-4/iter-5.**

- **[m2]** Panel coverage gap (637 vs 660 months) — NOW flagged in `assumptions.md` as Limitation 6 with `[DIAGNOSE-PENDING]` marker. **Status: resolved as of iter-5.**

- **[m3]** IVOL signal still NULL on all 1.69M rows — affects T2 SPREAD_IVOL row if T2 is built. **Status: documented in `assumptions.md` Limitation 3; non-actionable within time budget.**

- **[m4]** `eval/metrics.json` (replicator) and `eval/scoring.json` (canonical) schema mismatch — canonical scorer is the source of truth; `eval/metrics.json` is the replicator's hand-evaluated output. **Status: documented; non-actionable.**

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim (T1 P1→P10 should decline) | FAIL | T1 P1_RET_RF = 1.08, P10_RET_RF = 0.77 — both positive, declining 1.08 → 0.77. Paper has P10 = -0.32 (negative). Sign flip on P10_RET_RF fails the monotonic claim under sign-check rules. |
| 2 | Headline-magnitude claim (T6 10-1 SPREAD_RET_RF) | FAIL | Paper -0.81, ours -0.12 — unchanged from iter-3/iter-4. r = 0.148 — outside any band. Sign matches paper. |
| 3 | Sample coverage ≥ 60% | PASS | Panel n_rows = 1,693,841; 637 unique months × ~2655 stocks/month ≈ 100% coverage of stock-month universe in the panel file. Period-level coverage gap (23 months 1968-1970) is documented in `assumptions.md` Limitation 6. |
| 4 | Data-source choice justified | PASS | CRSP, Compustat, FF factor sources match paper §3 (L161-191 of `inputs/content.md`). PS-LIQ/SY/DHS substitutions documented as `[THIRD-PARTY-DATASET]`. RF source variant not tested (open diagnostic from iter-4/iter-5). |
| 5 | prep_validation.py exit 0 | PASS | Re-ran `python scripts/prep_validation.py replications/<slug>` — all present prep artifacts pass; verdict `partial` consistent with `data_verification.json`. |
| 6 | All committed tables have results files | FAIL | `results/table_1.md` and `results/table_6.md` exist. `results/table_2.md` and `results/table_9_panel_b.md` do not exist (T2 has 12 cells, T4 has 18 cells, all currently MISSING). |
| 7 | SUMMARY.md matches results/table_*.md | PARTIAL | SUMMARY.md is overwritten by this audit. Result tables have no per-cell evaluation blocks (they're just the result tables; the per-cell evaluation is in `eval/scoring.json`). |
| 8 | No orphan folders | PASS | Slug root has only `data/ eval/ inputs/ logs/ preparations/ results/ src/` — no shell-brace-expansion folders. |
| 9 | Diagnoses paired with fix attempts | PASS | Five iterations of diagnostics: iter-1 build pipeline; iter-2 beta source swap; iter-3 revert; iter-4 MAX-5 hand-verification + lag-1 ME test; iter-5 panel period coverage source-data check. All have Before/After metrics in `assumptions.md`. |
| 10 | Cell status verification (re-run canonical scorer, diff against eval/metrics.json) | PASS | Re-ran `python scripts/score_replication.py replications/<slug> --iteration 5` — canonical `eval/scoring.json` aggregates match: match=0, fail=52, missing=30, skip=0, loss=1.0. |
| 11 | Corollary coverage | FAIL | Paper C2 (T2 characteristics spread) and C4 (T4 INST terciles) — both entirely MISSING across five audits. C3 (MAX^beta MIS/CE spreads lower than MAX spreads) cannot be tested without T2. No corollary has a computed result in artifacts. |
| 12 | Claim coverage of committed selection | FAIL | Paper claim C1 (T3 headline) is computed but FAIL (r = 0.148). C2 (T2) is committed but not computed. C3 (T3 MIS/CE) is a corollary of T3 but T2 is missing. C4 (T4) is committed but not computed. Three of four `paper_claims` have NO computed result. |
| 13 | Sign conventions re-derived from paper | PARTIAL | Paper Table 6: 10-1 spread reported as `Portfolio 10 - Portfolio 1` excess return, expected negative per paper text (L76-78 of `inputs/content.md`). Replicator's `compute_long_short` uses `D_long - D_short`. Sign convention matches. But the high-MAX leg (P10_RET_RF) is sign-flipped in T1 (+0.77 vs paper -0.32) and T3 (+0.80 vs paper -0.10) — the source is not the spread arithmetic but the P10 cell itself. |
| 14 | Reporting discipline (grid completeness, claim citations, SE-less headlines) | PARTIAL | RESULT TABLES now show t-statistics in parentheses for each cell (`results/table_1.md`, `results/table_6.md`) — this is the paper's format and supports the SE-less headline concern. REPORT.md headline tally section (lines 7-16) shows current iter-5 numbers (Match=0, FAIL=52, MISSING=30, Loss=1.0) which match `eval/scoring.json`. REPORT.md line 5 verdict description is also current. |
| 15 | REPORT.md headline freshness (tally matches eval/scoring.json; DEV-010) | PASS | `REPORT.md` headline tally section (lines 7-16) shows iter-5 numbers (Match=0, FAIL=52, MISSING=30, Loss=1.0) which match `eval/scoring.json` for iter-5. Line 5 verdict description also current. DEV-010 resolved. |
| 16 | Panel period coverage source-data check (iter-5 Diagnostic 3) | PASS | Queried `crsp_202601.msf` and `crsp_202601.dsf` for 1968-1969. Source data exists (25,838/26,610 monthly rows; 488,614/558,342 daily rows). The 23-month panel gap is a pipeline filter (the `count(ret) >= 15` requirement in `monthly_daily_count` CTE drops sparse-daily-obs stocks in early years), not a source-data gap. Documented as Limitation 6 in `assumptions.md`. |

## 4. Issues the agent should have caught (didn't)

1. **The 23-month panel-coverage gap (1970-2022 vs 1968-2022) was acknowledged in `logs/log4.md` but not flagged in `assumptions.md` until iter-5.** Iter-4 surfaced the gap but did not run a source-data diagnostic until prompted by audit4 [M1]. Iter-5 ran the diagnostic (logs/log5.md L19-36) and confirmed the source data exists; the gap is a pipeline-filter artifact, not a source-data gap. This is documented as Limitation 6 with `[DIAGNOSE-PENDING]` marker.

2. **The T1 P10_RET_RF sign flip has persisted across all five iterations without being drilled into.** The paper's high-MAX stocks earn negative excess returns (-0.32% per month); the replicator's high-MAX stocks earn positive excess returns (+0.77%). The iter-4 diagnostic narrowed the cause space (MAX and VW ruled out) but did not drill into the P10 portfolio itself. The deeper insight from the diagnostic trail is that the T1 P10_RET_RF sign flip is the primary driver of the T1 10-1 spread gap — P1_RET_RF is roughly correct (T1: paper 0.63, ours 1.08; T3: paper 0.71, ours 0.92). The fix is not the spread arithmetic or the portfolio-construction; it's the high-MAX portfolio itself.

3. **Tables 2 and 9 Panel B were never built across all five iterations.** Audit1 [B3] recommended building the 8 computable T2 rows; audit2 [B3] re-prioritized the same work; audit3 [B3] re-prioritized again; audit4 [B3] repeats; audit5 confirms the cap is hit. C2 (mispricing interpretation) and C4 (heterogeneous skewness preference) — two of the paper's three named contributions — remain entirely untestable in the artifact set.

4. **REPORT.md line 5 was stale through iterations 2-3; the audit-4 finding flagged it as resolved.** Iter-5 confirmed the canonical tally in REPORT.md matches `eval/scoring.json`. DEV-010 hygiene is now maintained.

## 5. Final state (5-iter cap reached)

This is the FINAL iteration of the 5-iter hard cap. Per the SKILL.md hard cap rule, the replicator stops after this audit. The exit is under documented-residue criterion B (`rep/LOSS_FUNCTION.md`):

- **Loss has plateaued**: L = 1.0 across iter 2, 3, 4, 5.
- **Every failing cell carries a closed-vocabulary marker with diagnostic evidence**:
  - T1 magnitude gap: `[DIAGNOSE-PENDING]` (iter-4 MAX-5 verified correct; iter-4 lag-1 ME tested and rejected; iter-5 period-coverage source-data check ruled out).
  - T6 magnitude gap: `[STRUCTURAL-SAMPLE-VARIANCE]` (iter-1/iter-2 beta-source tested; iter-3 reverted).
  - FFCPS, FF6PS, SY, DHS columns: `[THIRD-PARTY-DATASET]` (factors not in catalog).
  - T2 (12 cells), T4 (18 cells): documented as `[NOT-COMPUTED]` rather than `[MISSING]` in `tables_to_replicate.json` notes — work was deferred, not unavailable.

## 6. Auditor's notes (free-form)

The iter-5 outcome is a single diagnostic contribution: confirming the 23-month panel-coverage gap is a pipeline-filter artifact, not a source-data gap. This is now documented as Limitation 6 in `assumptions.md`. The canonical loss remains L = 1.0000 across iter 2, 3, 4, and 5.

The five-iteration run reached a clear plateau: the data pipeline is structurally correct (MAX signal verified to 6 decimals, universe filters match paper §3.1, VW weighting convention matches, Newey-West t-stats implemented, MAX^beta dependent double-sort runs end-to-end) but the methodology calibration to the paper's exact conventions is the unresolved gap. The 52 FAIL cells (T1 and T3 magnitude/sign gaps) are attributable to (a) the T1 P10_RET_RF sign flip (paper -0.32, ours +0.77 — a fundamental directional disagreement on the high-MAX leg), and (b) the T6 MAX^beta sample truncation (2002-2022 vs paper's 1968-2022). The 30 MISSING cells (T2 + T4) are not built due to time budget — they require substantial additional work (13F INST construction, characteristic spreads, IVOL signal).

The 5-iter hard cap has been reached. The exit is final. Three of six dimensions are at 1 (concrete_result, signal_strength, corollary); one is at 2 (headline_matching); two are at 3 and 4. The bright-line verdict is FAILED by both overall < 3.0 and the kill switch. `requires_iteration: false` because we are at the hard cap and every remaining failing cell carries a closed-vocabulary marker with diagnostic evidence.

A future run with access to the third-party factor downloads (PS-LIQ, SY MGMT/PERF, DHS FIN/PEAD), a 13F-derived INST series for T4, a full panel rebuild to include 1968-1969, and a drill-into-P10 diagnostic for the T1 sign flip could close most of the gap. The current run exits with full diagnostic evidence for three of the previously-hedged causes (MAX signal, VW weighting, period-coverage source data) and a documented 23-month panel-coverage finding.
