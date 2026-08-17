---
iteration: 1
verdict: REPLICATED
blocker_count: 0
actionable_major_count: 4
requires_iteration: true
---

# Audit Report 1 — max_on_steroids_attempt5_deepseek

**Verdict:** REPLICATED
**Date:** 2026-08-16
**Auditor notes:** Strong core replication — the paper's headline MAX and MAX^β spreads land within tolerance; remaining issues are FM coefficient unit corrections and a handful of characteristic/robustness cells, all actionable in iteration 2.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 4 | 8/8 sub-checks pass; deviations documented (SY 1968-2016, DHS missing); two look-ahead bugs diagnosed and fixed with before/after evidence |
| Headline matching | 5 | T1 spread −1.02 vs −0.95, T3 −0.87 vs −0.81; all headline spreads Match with correct sign and monotonic decile profile |
| Data coverage | 3 | Period exact 1968-2022, universe size close, join 0 dup; but SY truncated (2016-12), DHS absent, PS-LIQ/BW-sentiment external/missing |
| Concrete result matching | 3 | 439/701 committed cells Match (62.6%) — band 3 |
| Signal strength | 5 | Headline spread cells worst-case r = 1.10 (T1 CAPM −1.54 vs −1.41); all within [0.9, 1.1] |
| Corollary | 3 | 110/205 corollary cells Match (53.7%) — band 3; T8/T5 strong, T9 weak |
| 7 | SUMMARY.md matches results/table_*.md | ✗ | REPORT.md T7/T8 values don't reproduce from results/ (see m2/m3) | |

## 2. Issues by severity

### Blockers (must fix)

None.

### Major (should fix)

- [M1] FM control coefficient unit errors in T2/T4 (Table 4/8).
  - File: `results/table_4.md:18` (ivol −12.280 vs paper −0.217; roe 1.033 vs 0.414), `results/table_8.md:22,26`
  - Likely cause: IVOL was already percent-equivalent before the ×100 FIX-1 (over-converted ~55×); ROE annualization + scaling double-counts. Logged by worker ("ivol over-converted", "roe 2.5× high") but left for iteration 2.
  - Specific fix: remove the ×100 on IVOL only; scale ROE by a single factor; re-run `sections_678.py` and confirm t2_ivol_c2 ≈ −0.2 and t2_roe_c2 ≈ 0.4.

- [M2] Composite-equity-issuance (CE) residual outliers and BM sign.
  - File: `src/regen_ce_betamax.py`; `results/table_4.md:9` (ce −0.514 vs −0.017); `results/table_a5.md:18` (bm 10-1 −0.056 vs paper +0.052).
  - Likely cause: ~460 rows with |ce|>10 and one 4730 outlier (near-zero shrout at t−12) leak into the FM CE coefficient and the T9 state split; T6 raw-BM spread is a genuine sign disagreement (ours −0.056 vs paper +0.052) unresolved.
  - Specific fix: winsorize/flag CE at the rank boundary before FM (not just post-hoc); check whether bm_raw 10-1 order is inverted by MAX^β's beta-neutralization (a subtraction/decile-order check).

- [M3] E(ISKEW) and β^MAX magnitude residuals (T6).
  - File: `results/table_a5.md:8,18` (eiskew spread 0.302 vs 0.451; betamax spread 0.153 vs 0.036)
  - Likely cause: 60-month daily-residual skewness in our vintage is magnitude-lower than the BMV-fitted values; β^MAX is compressed by the market-MAX redefinition.
  - Specific fix: document the ISKEW window convention (1260 vs 252×5) against BMV (2010); leave as documented residue only if a 100-obs spot check confirms the convention is correct.

- [M4] Table 12 long-horizon legs and Table A7 MAX-state deciles.
  - File: `results/table_12.md:11-14` (K≥6 legs and CR24 sign-reverse), `results/table_a7.md:5-18` (MAX-state columns inverted vs paper)
  - Likely cause: overlapping-horizon noise at K≥6 and CR24; T9 MAX-state cells contaminated by residual CE outliers (documented).
  - Specific fix: for T5, confirm the calendar-time aggregation denominator (K-window mean) against footnote 12; for T9, re-split after the CE fix in M2.

- [M5] DHS columns scored MISSING but documented "SKIP" (label-vocabulary inconsistency).
  - File: `preparations/assumptions.md:99` (Assumption 8), `preparations/data_verification.json` (dhs_behavioral_factors), `eval/scoring.json` (24 MISSING).
  - Likely cause: the diagnostic evaluator's `skips` list labels DHS "SKIP", but the canonical scorer's `loss_form` has no SKIP slot, so the committed DHS cells land as MISSING (counted in the 701 denominator and numerator).
  - Specific fix: accept MISSING as canonical (loss already correct) and re-label Assumption 8 / data_verification to say "MISSING in the scorer (non-actionable via [THIRD-PARTY-DATASET])", not "SKIP".

### Minor (cleanup)

- [m1] REPORT.md T8 retrf spread mislabeled: reports INST1 Panel B "−1.51 (t=−4.05)" but the retrf spread is −1.77 (t=−4.18); −1.51 is the FF6PS *alpha* spread. Align the two columns with `results/table_9.md`.
  - File: `REPORT.md:109`
- [m2] REPORT.md T7 cites "ours −0.59 (t=−3.46) / −0.50 (t=−3.03)" but `results/table_7.md` shows 10-1 −0.44 (a_maxb) / −0.38 (b_maxb). Values must reproduce from results/.
  - File: `REPORT.md:105-106`
- [m3] Ensure REPORT.md headline tally is re-copied if any fix in iteration 2 moves cells (DEV-010 freshness).

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim | ✓ | T1/T3 decile RET-RF decline P1→P10; spreads negative (paper sign) |
| 2 | Headline-magnitude claim | ✓ | T1 spread −1.02 vs −0.95; T3 −0.87 vs −0.81 (r≈1.08) |
| 3 | Sample coverage ≥ 60% | ✓ | 1.74M stock-months, 17,856 permnos, BM 87.1%, full 660 months |
| 4 | Data-source choice justified | ✓ | dsfhdr PIT, delisting dsedelist, CRSP vwretd, PS-LIQ user file — all in assumptions.md |
| 5 | prep_validation.py exit 0 | ✓ | "All present prep artifacts pass validation" |
| 6 | All committed tables have results files | ✓ | 9 tables → 9 table_*.md present |
| 7 | SUMMARY.md matches results/table_*.md | ✗ | T7/T8 REPORT.md values don't reproduce (m1/m2) |
| 8 | No orphan folders | ✓ | No brace-name folders |
| 9 | Diagnoses paired with fix attempts | ✓ | Iterations 5-6 and FIX 1-4 all have Diagnosis/Before/After/Status |
| 10 | Cell status verification (scorer canonical) | ✓ | score_replication.py reproduces 439/238/24/7; evaluate.py matches |
| 11 | Corollary coverage | ✓ | C3(T8)/C4(T5)/C5(T9) each have computed results; T9 weak but computed |
| 12 | Claim coverage of committed selection | ✓ | C1-C5 each covered by ≥1 table; omitted tables are robustness/appendix (scope-guardrail OK) |
| 13 | Sign conventions re-derived from paper | ✓ | Spreads are defined 10-1 (low-minus-high); paper L285/L450 negative; sign matches |
| 14 | Reporting discipline (grids, citations, SE-less) | ✓ | Spreads carry t-stats; "significant" claims cite t; T6/9 grids complete |
| 15 | REPORT.md headline freshness (DEV-010) | ✓ | 439/238/24 tally matches eval/scoring.json |

## 4. Issues the agent should have caught (didn't)

1. The T7/T8 REPORT.md prose values (−0.59/−0.50; INST1 −1.51) do not reproduce from `results/`. The sign/status are consistent, but the cited magnitudes are rounded/fabricated figures that a careful re-read of the result tables would flag (m1/m2).
2. The DHS "SKIP" vs scorer "MISSING" vocabulary mismatch (M5) — the intent (non-actionable third-party gap) is clear, but the labels diverged between assumptions and the canonical tally without a note.

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "MAX on Steroids" (Bali, Ince & Ozsoylev) for slug `max_on_steroids_attempt5_deepseek`. The previous agent run completed with verdict **REPLICATED** (audit 1 at `replications/max_on_steroids_attempt5_deepseek/logs/audit1.md`). Read the audit first.

## Issues to address (priority order)

### [M1] — MAJOR — FM coefficient unit errors (Table 4 / Table 8)
IVOL was over-converted by the ×100 percent scaling (already percent-equivalent; t2_ivol_c2 = −12.28 vs paper −0.217, ~55× too large); ROE is ~2.5× high (1.03 vs 0.414) from double annualization/scaling.

**Specific fix:**
1. In `src/sections_678.py`, remove the `SCALE_PCT` ×100 for IVOL only (leave MIS/SIZE/BETA/BM/ILLIQ/ROE/I-A in percent).
2. Re-derive ROE scaling to a single factor so t2_roe_c2 ≈ 0.41.
3. Re-run `sections_678.py`, then `evaluate.py`, and confirm t2_ivol_c2 ≈ −0.2 and t2_roe_c2 ≈ 0.4 (paper −0.217 / 0.414).

### [M2] — MAJOR — CE outliers and T6 BM sign
CE has ~460 rows with |ce|>10 plus one 4730 outlier (near-zero shrout at t−12) leaking into t2_ce_c4 (−0.51 vs −0.017) and the T9 state split. T6 raw-BM 10-1 spread is sign-flipped (−0.056 vs paper +0.052).

**Specific fix:**
1. Mask/winsorize CE at the rank boundary BEFORE FM estimation (not just post-hoc), then re-run sections_678/9_11.
2. Trace whether bm_raw's 10-1 order is inverted by the beta-neutralization sort (check subtraction order); correct or document.

### [M3] — MAJOR — E(ISKEW) and β^MAX residuals (Table A5)
E(ISKEW) spread 0.302 vs 0.451; β^MAX spread 0.153 vs 0.036.

**Specific fix:**
1. Confirm ISKEW window (1260 trading days) against BMV (2010); run a ~100-obs spot check.
2. If the convention is correct, mark as `[STRUCTURAL-SAMPLE-VARIANCE]` residue with evidence; otherwise correct the window.

### [M4] — MAJOR — Table 12 long horizons and Table A7 MAX-state deciles
K≥18 legs and CR24 cells mostly FAIL/noisy; T9 MAX-state deciles inverted (residual CE outliers).

**Specific fix:**
1. Verify T5 calendar-time means against footnote 12 (K-window denominator).
2. Re-split T9 states after the CE fix in M2; report the new MAX-state spreads.

### [M5] — MAJOR — DHS "SKIP" vs "MISSING" label consistency
The DHS columns (24 cells) are documented "SKIP" in assumptions.md but scored MISSING by the canonical scorer (they count in the 701 denominator and loss numerator).

**Specific fix:**
1. Accept MISSING as canonical and re-label Assumption 8 (`assumptions.md`) and `data_verification.json` to "MISSING (non-actionable [THIRD-PARTY-DATASET])".

### [m1]/[m2] — MINOR — REPORT.md value fidelity
The T7 (−0.59/−0.50) and T8 INST1 (−1.51) prose values don't reproduce from `results/`. Re-copy the exact result-table values.

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every fix logged in `assumptions.md` with Diagnosis/Next fix/Before/After/Status.
- **Read `rep/STUCK_AGENT_GUIDELINE.md` on your first debug cycle.**
- **10-iteration cap per problem;** hard stop and escalate.
- **Confirm cell moves** re-copy the REPORT.md headline tally (and the evaluator output) after every fix; the scorer `--iteration 2` is the canonical tally.

## Inputs you should read

- `replications/max_on_steroids_attempt5_deepseek/logs/audit1.md` — this audit
- `replications/max_on_steroids_attempt5_deepseek/inputs/content.md` — paper ground truth
- `replications/max_on_steroids_attempt5_deepseek/preparations/` — prep contract
- `replications/max_on_steroids_attempt5_deepseek/src/sections_678.py`, `sections_9_11.py` — current code
- `replications/max_on_steroids_attempt5_deepseek/data/` — cached intermediates

## What NOT to redo

- Skip re-reading `SKILL.md`; the contract is unchanged.
- Skip the clickhouse catalog scan — `data_verification.json` is current.
- Do not regenerate the factor set or re-litigate the universe/filter choices — those are correct.
- DHS/SY/BW-sentiment gaps are documented [THIRD-PARTY-DATASET]; do not re-attempt unless new data is provided.

## Deliverables for this iteration

- `src/main.py` + `sections_678.py` / `sections_9_11.py` revised with fixes logged
- `results/table_*.md` updated for affected tables
- `preparations/assumptions.md` — append iteration-log entries per fix
- `REPORT.md` — refreshed headline tally and re-copied table values
- Do NOT edit `SUMMARY.md` (auditor-owned).

## Stop conditions

- All majors fixed and verified → re-run `prep_validation.py` and `make_plots.py` → declare success or note remaining residue.
- 10-iteration cap reached → escalate and write partial REPORT.md.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

This is a high-quality first iteration. The two forward-return bugs that initially inverted the T1 spread (+0.21 → −1.02) were diagnosed by characterizing the *contemporaneous* pattern and *then* fixing, which is exactly the "verify by characterization, not guessing" discipline the harness rewards. The assumptions registry is exemplary — every paper-silent decision carries a citation or a `[CONVENTION-APPLIED]`/`[THIRD-PARTY-DATASET]` marker. The remaining failures are almost entirely (a) unit-conversion bookkeeping on FM coefficient cells, (b) a documented third-party factor gap, and (c) tail-cell noise — none of which undermines the paper's two headline claims (C1: MAX explained by mispricing; C2: MAX^β robust). The main nitpick is prose fidelity: REPORT.md's Table 7/8 narrative cites magnitudes (−0.59, −0.50, −1.51) that don't reproduce from the result files, a symptom of composing the report from memory rather than re-reading the artifacts.
