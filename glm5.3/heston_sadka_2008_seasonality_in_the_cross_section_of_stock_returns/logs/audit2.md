---
iteration: 2
verdict: REPLICATED
blocker_count: 0
actionable_major_count: 0
requires_iteration: false
---

# Audit Report 2 — heston_sadka_2008_seasonality_in_the_cross_section_of_stock_returns

**Verdict:** REPLICATED
**Date:** 2026-09-08
**Auditor notes:** Audit-1 [M1] fixed exactly as specified (T4 t-unit; zero collateral metric changes), [m1]/[m2] REPORT staleness resolved; loss 0.1242 → 0.1220; remaining 160 FAILs are the same evidenced non-actionable residue accepted in audit 1. Loop closes under criterion B.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 5 | All 8 sub-checks pass; the audit-1 sub-check-8 failure (T4 t = 362.2) is fixed — t's now -0.25/-0.62/3.62 vs paper -0.26/-0.65/3.57 with a units assert in code (`src/table4.py:69-72`). |
| Headline matching | 3 | C1/C2 sign, shape, and pulse pattern all correct; annual spreads within ~15%; y1 drift remains 25–50%+ (unchanged, documented [STRUCTURAL-SAMPLE-VARIANCE]). |
| Data coverage | 5 | Period exact; universe validated against paper Fig-1 diagnostics; CRSP/Compustat/FF sources; 0 (permno,month) duplicates; prep_validation verdict ready (7/0/0). |
| Concrete result matching | 5 | 1,152 / 1,312 committed = 87.8% Match (auditor re-ran `scripts/score_replication.py --iteration 2`; aggregates identical to REPORT) — band ≥85%. |
| Signal strength | 2 | Worst headline cell still y1 Nonannual EW spread r = 0.455/1.17 = 0.39 (sign correct, six-variant evidence trail) — band 2 under the worst-case rule. |
| Corollary | 5 | Corollary cells (T3–T8): 723 Match / 865 match-or-FAIL = 83.6% — band ≥80%; every paper corollary computed (FF3, sigma^2_mu, size/industry/calendar/event independence). |

Overall = (5+3+5+5+2+5)/6 = **4.17**. Bright line: overall ≥ 3.0 AND no dimension = 1 → REPLICATED.

## 2. Issues by severity

### Blockers (must fix)

None.

### Major (should fix)

None. The audit-1 actionable major [M1] is resolved and verified:

- [M1-audit1] RESOLVED — T4 t-statistic x100 unit error. `src/table4.py:69-72` now computes `t = v.mean() / se_dec` with both terms in decimal^2 and an inline assert `abs(t - mean/(se_dec*100)) < 1e-12`. Verified: `eval/metrics.json` carries t4_mean_all_t = -0.2515, t4_mean_nonannual_t = -0.6239, t4_mean_annual_t = 3.6220 (paper -0.26/-0.65/3.57) — all three Match in `eval/scoring.json`; `results/table_4.md` prints -0.25/-0.62/3.62; T4 is 4 Match / 0 FAIL / 2 no_effect. Full-metrics diff claim ("exactly 3 keys") is consistent with every other spot-checked cell (T1 gammas, T3 alphas, T8 event spreads) being unchanged from audit 1.

### Minor (cleanup)

None new. Audit-1 [m1]/[m2] resolved and verified: `REPORT.md:28` now quotes the reversal trio -1.02/-0.41/-0.03 (All) and -1.20/-0.69/-0.23/-0.38 (nonannual) matching `results/table_2.md`, and "all 12 VW spread cells Match" matching the scored grid (t2_vw_* cells in `eval/scoring.json`).

### Documented non-actionable residue (criterion B evidence trail)

All 160 FAIL cells fall under the three evidenced clusters in `preparations/assumptions.md`, each carrying the closed-vocabulary marker `[STRUCTURAL-SAMPLE-VARIANCE]`:

1. **y1 January cluster (~25 cells across T2/T5/T6/T7/T8)** — verified: the 5 T2 FAILs are exactly `t2_y1_all_d1_t, t2_y1_all_spread_t, t2_y1_nonannual_d1, t2_y1_nonannual_spread, t2_y1_nonannual_spread_t`. Evidence: gamma_1 = -4.99 vs paper -5.03 (r = 0.99) regression counterpart; six tested variants; 38 January observations.
2. **T1 short-lag t-cells (13 FAIL, lags 2–8)** — delisting sensitivity tested (post-merge closer in 15/16); anchored coefficients match.
3. **Small-magnitude inference cells of null results (~120 across T3/T7/T8)** — paired estimate cells are no_effect or Match; paper itself reports no effect on these cells.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim | ✓ | As audit 1 (unchanged T2 grid): y1 All decile profile 1.06→1.85; annual rows monotone increasing; long-horizon reversal shapes match. |
| 2 | Headline-magnitude claim | ✓ | gamma_1 = -4.99 vs -5.03; gamma_12 = 2.79 vs 2.61; annual EW spreads r = 0.94–1.15. |
| 3 | Sample coverage ≥ 60% | ✓ | panel.parquet 1,367,649 rows, 1945-01..2002-12; 98.4% non-missing ret (audit-1 values, panel untouched this iteration). |
| 4 | Data-source choice justified | ✓ | Unchanged from audit 1; data_verification 7 full / 0 partial. |
| 5 | prep_validation.py exit 0 | ✓ | Re-run this audit: all prep artifacts pass, verdict ready. |
| 6 | All committed tables have results files | ✓ | 8/8 (results/table_1..8.md present). |
| 7 | REPORT.md matches results | ✓ | Headline tally 1,152/160/0/306, L = 0.1220 matches scoring.json; reversal trio and VW count refreshed ([m1]/[m2] fixed). |
| 8 | No orphan folders | ✓ | Slug root clean. |
| 9 | Diagnoses paired with fix attempts | ✓ | Iteration-11 entry has all five fields, Before (T4 1/3/2; L = 0.1242) and After (T4 4/0/2; three FAIL→Match) metrics, Status: resolved. |
| 10 | Cell status verification | ✓ | Re-ran `scripts/score_replication.py --iteration 2`: loss 0.12195, n_committed 1,312, 1,152/160/0/306 — identical to the replicator's reported tally; T4 cells re-read individually (all Match/no_effect as claimed). |
| 11 | Corollary coverage | ✓ | C3–C5 all computed (T3–T8); no silently skipped corollary. |
| 12 | Claim coverage of committed selection | ✓ | Same 1:1 C1–C5 ↔ T1–T8 mapping re-verified; budget_flag honest. |
| 13 | Sign conventions re-derived from paper | ✓ | Unchanged; no absolute-value comparisons or tolerance inflation introduced by the fix (t sign/magnitude both unit-consistent now). |
| 14 | Reporting discipline | ✓ | Claims cite t's; T4 significance categories now correct (all/nonannual n.s., annual significant — matching the paper). |
| 15 | REPORT.md headline freshness (DEV-010) | ✓ | Headline table matches eval/scoring.json on all five tallies. |

### Harness change review (item 3 of the audit brief)

The orchestrator's `scripts/prep_validation.py` DEV-034 change was reviewed from the working diff: (a) band table now >=0.85/0.60/0.40/0.25, matching `audit/RUBRIC.md` § 4 verbatim (the old >=0.90/0.70/... contradicted the rubric); (b) the denominator now subtracts `no_effect_count` alongside `skip_count`, matching the canonical scorer's n_committed (1,312) and `rep/LOSS_FUNCTION.md`'s exclusion of no_effect from both numerator and denominator. Both changes are cross-check infrastructure only — no cell status, tolerance, or scored value is touched — and are transparently documented in `preparations/assumptions.md:507-508` ("Harness note (outer 2, orchestrator)"). I judge the fix sound: the old validator would have contradicted both the rubric and the canonical scorer on this very slug. No flag.

## 4. Issues the agent should have caught (didn't)

1. Nothing new. The iteration did exactly what the audit-1 prompt specified, verified no collateral changes, and refreshed the REPORT prose. The one-cell canonical-vs-diagnostic divergence (1,152 vs 1,151) remains correctly documented with the canonical winning.

## 5. Continuation decision

- Loss: iteration 1 = 0.1242 → iteration 2 = 0.1220 (|Δ| = 0.0023 < 0.01; the entire delta is the three mandated T4 cells).
- Every one of the 160 FAIL cells carries an evidenced closed-vocabulary marker (`[STRUCTURAL-SAMPLE-VARIANCE]`) in `preparations/assumptions.md` (clusters verified against the per-cell FAIL list in `eval/scoring.json`).
- No blockers, no actionable majors, caps not reached.

→ **requires_iteration: false** (criterion B: documented-residue exit). The loop is closed.

## 6. Auditor's notes (free-form)

This is a model closing iteration: one surgical fix (three cells, zero collateral, asserted in code), two prose refreshes, an honest iteration-log entry with before/after metrics, and a transparent harness-note for an infrastructure alignment the auditor independently confirms was correct against the rubric. The replication ends at 87.8% Match with 0 MISSING across 1,312 committed cells, 306 no_effect cells on results the paper itself reports as null, and a 160-cell residue that is vintage-structural small-magnitude inference noise with six-variant evidence on the only cluster (y1 January) that materially touches headline magnitude. The Signal Strength dimension stays at 2 purely because of the worst-case-band rule on that one documented y1 cell; every other headline quantity is within ±25% of the paper. Nothing actionable remains.

(No next-iteration prompt: `requires_iteration: false`. The loop exits under criterion B.)
