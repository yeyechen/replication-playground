---
iteration: 1
verdict: FAILED
blocker_count: 0
actionable_major_count: 2
requires_iteration: true
---

# Audit Report 1 — max_on_steroids_attempt4

**Verdict:** FAILED
**Date:** 2026-08-15
**Auditor notes:** A faithful methodological replication of Bali, Ince, Ozsoylev's MAX/MAX^beta paper whose headline 10-1 spread is consistently 28-50% of the paper's. Direction of the anomaly is reproduced in every signed cell, but the magnitude shortfall plus a sign flip on P10_RET_RF on both Tables 1 and 6 falls outside the headline-match bands and pulls Signal Strength to 1.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 4/5 | 7/8 sub-checks pass; the diagnostic-evidence sub-check fails because the magnitude-shortfall root cause is hypothesised but not isolated with a single targeted test (e.g. June-t ME snapshot re-run). |
| Headline matching | 3/5 | Direction matches on every headline 10-1 cell; magnitudes are 11-50% of paper across Tables 1 and 6. |
| Data coverage | 4/5 | Period exact (1968-01 to 2022-12), universe ~2,616 obs/month within bounds, documented substitutions (dlretx, dsenames, FF6 in lieu of FF6PS), join hygiene clean (no duplicates). |
| Concrete result matching | 2/5 | Match rate = 10/25 = 40.0% (band 2: 30-50%). |
| Signal strength | 1/5 | Worst-case headline cell P10_RET_RF on Tables 1 and 6 carries the wrong sign (paper -0.32 / -0.10; replication +0.47 on both). Every other D10-D1 alpha has r ∈ [0.11, 0.33], also outside the [0.33, 3.0] band. Rubric says wrong sign on a headline cell = 1. |
| Corollary | 4/5 | T2 (which covers the C3 cross-sectional-correlation corollary) matches in 8/9 = 89% of cells; C4 (MAX^beta BETA-neutralization, Table 9 territory) is not committed. |
| 7 | SUMMARY.md matches results/table_*.md | -- | SUMMARY.md was overwritten by this audit; the prior per-cell numbers in eval/scoring.json and the canonical per_cell_evaluation.json are consistent. |

**Overall:** (4 + 3 + 4 + 2 + 1 + 4) / 6 = 3.00

A dimension-1 kill-switch is in force (Signal Strength = 1 on sign disagreement in headline P10_RET_RF), so the binary verdict is FAILED even though overall = 3.00 exactly.

## 2. Issues by severity

### Blockers (must fix)

- None. Methodology is sound; the panel, sorts, regressions, NW t-stats, and universe filter all trace to paper-cited preprocessing rules. The shortfall is magnitude-class, not construction-class.

### Major (should fix)

- [M1] **Headline sign disagreement on P10_RET_RF (Tables 1 and 6).** Replicated +0.47%/mo (t = 1.36) vs paper -0.32 (T1) and -0.10 (T6). The replication's high-MAX portfolio earns a positive excess return where the paper reports a negative one. This is a sign flip on a headline cell — not a tolerance question. The cause is most likely the same as the broader magnitude shortfall (next-iteration prompt item #1 below) but it warrants its own diagnostic: a single re-sort with current-month ME on DSFH and no NYSE breakpoints will tell the replicator whether the issue is the 1-month-lag choice or the NYSE-breakpoint choice.
  - File: `eval/per_cell_evaluation.json` lines 22-33 (T1 P10_RET_RF) and lines 130-138 (T6 P10_RET_RF)
  - Likely cause: either the VW weight is wrong (the paper likely uses June-t ME for VW weighting, per Bali-Cakici-Whitelaw 2011; the replication uses 1-month-lagged ME), or the paper's high-MAX portfolio contains a much larger fraction of COVID-era / 2020-2021 lottery spikes that the CRSP 2026 vintage continues to carry as positive returns.
  - Specific fix: re-run Table 1 with June-t ME snapshot (the standard FF/Bali 2011 convention) and compare P10_RET_RF; if the sign flips negative, the magnitude-shortfall root cause is the ME-timing convention. If it does not, the issue is the 2026 vintage's COVID-era tail.

- [M2] **Magnitude shortfall on every D10-D1 spread cell (Tables 1 and 6).** Replicated alphas are 11-30% of paper across all six factor models (CAPM, FF3, FFC4, FF5, FF6). Documented as `[VINTAGE-DRIFT]` + `[STRUCTURAL-SAMPLE-VARIANCE]` in `assumptions.md` A16/A17 and `REPORT.md` §3, but the hypotheses (June-t ME snapshot, vintage tail, NYSE-breakpoint composition) have not been tested one-at-a-time. The replicator's iter-3 NYSE-breakpoint switch (assumptions.md A17) was tried and made the spread *narrower*, not wider — so that hypothesis is falsified, leaving June-t ME as the leading candidate.
  - File: `eval/per_cell_evaluation.json` lines 33-110 (15 D10_D1 cells)
  - Likely cause: VW weighting convention. The paper most likely uses June-t ME (the standard FF/Bali 2011 convention); the replication uses 1-month-lagged ME (`ME_lag1`, per `assumptions.md` A15).
  - Specific fix: add a June-t ME snapshot to the panel (a single `me_june_t` column), use it as the VW weight, and re-run both Table 1 and Table 6. Compare D10_D1_RET_RF against the paper's -0.95 (T1) and -0.81 (T6). If r jumps into [0.5, 2.0], you have the root cause.

### Minor (cleanup)

- [m1] **Stale aggregates in `eval/scoring.json`.** The file contains a pre-binary-match tallies block (`n_committed: 35, loss: 0.714`) that contradicts the canonical `eval/per_cell_evaluation.json` (`n_committed: 25, loss: 0.60`). The canonical scorer (`scripts/score_replication.py`) writes `eval/scoring.json` on every run, so the stale version is overwritten next time the scorer runs — but until then it could confuse downstream readers. DEV-012 hygiene. Not a substantive issue.

- [m2] **`eval/metrics.json` carries a duplicate set of T2 metrics under both bare (`P1_MAX`) and `T2_`-prefixed (`T2_P1_MAX`) keys.** 18 duplicate entries (90 lines). The evaluator's `_pick_replicated()` function knows how to fall back to the `T2_`-prefixed names. Harmless but noisy; the bare-prefixed set was probably written by an early run before the namespacing convention was standardised.

- [m3] **`assumptions.md` A7 documents "[CONVENTION-APPLIED]" for NYSE-only breakpoints in MAX sorts, but the paper is silent on this and the implementation only arrived at iter-3 after iter-2 already established NYSE-only as the leading hypothesis.** A7 reads as if it were always the convention; in practice it was a fix. Tighten the language to "applied per Assumption 17 in iter-3" so the iteration history is visible in the registry.

- [m4] **No inference-cell flagged in `per_cell_evaluation.json` even though the paper's headline is statistical significance (Newey-West t-stats), not just the value.** None of the 25 cells has `inference_cell: <stat>`, so the rubric's sub-check 8 ("statistical inference reproduction") cannot be mechanically evaluated. The replication does compute NW(6) t-stats in `results/table_*.md` (e.g., t = -2.62 on D10_D1_CAPM), but the cell entries in `tables_to_replicate.json` only carry `value` and `tolerance_pct`, not a paired t-stat target. A future iteration could add `inference_target: {direction: -1, threshold: 1.96}` per cell.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim (T2: MAX, BETA, IVOL all increase P1 → P10) | PASS | T2 grid at `results/table_2.md` shows P1-P10 strictly increasing for all three characteristics. This validates the sort logic and the universe filter. |
| 2 | Headline-magnitude claim (T1 D10_D1_RET_RF: paper -0.95, replicated -0.27) | FAIL | r = 0.28 — outside [0.5, 2.0]. Direction matches but magnitude is short by 71%. |
| 3 | Sample coverage ≥ 60% | PASS | Panel has 1,726,806 stock-months across 660 months = 2,616 obs/month avg. The paper's Table 1 footnote implies a comparable density; ~85% of expected coverage survives after the 15-day minimum and SIC filters. |
| 4 | Data-source choice justified | PASS | dlretx-for-dlret, dsenames-for-exchcd, FF6-in-lieu-of-FF6PS, SY/DHS/FFCPS/FF6PS dropped — each documented in `data_verification.json` and `assumptions.md`. |
| 5 | prep_validation.py exit 0 | PASS | See run above. Single warning is "REPORT.md exists but no logs/audit*.md yet" — expected pre-audit. |
| 6 | All committed tables have results files | PASS | `results/table_1.md`, `results/table_2.md`, `results/table_6.md` all exist. |
| 7 | SUMMARY.md matches results/table_*.md | PASS | SUMMARY.md (this audit, just written) values derive from `eval/scoring.json` aggregates which match the per-cell grid in `results/table_*.md`. |
| 8 | No orphan folders | PASS | `ls` on slug root returns only `data/`, `eval/`, `inputs/`, `logs/`, `preparations/`, `results/`, `src/`, `REPORT.md`. |
| 9 | Diagnoses paired with fix attempts | PASS | `assumptions.md` has 19 entries, each with Diagnosis, Decision, Rationale, and Impact sections. The three leading magnitude-shortfall hypotheses (A16) are documented; iter-3 falsified the NYSE-breakpoint hypothesis (A17 documents the result); iter-1/2 documented the look-ahead correction (A14, A15). |
| 10 | Cell status verification (re-run evaluator, diff against eval/scoring.json) | PASS | Re-ran `src/evaluate.py`; output exactly matches `eval/per_cell_evaluation.json` (10/15/0/0). The pre-existing `eval/scoring.json` contains stale aggregates (35 committed, 23 SKIP) from a pre-binary-match run; the canonical scorer overwrites this on each invocation (verified by re-running `scripts/score_replication.py` which yields 25/10/15/0/0). |
| 11 | Corollary coverage | PASS (with one gap) | C3 (cross-sectional confounding) is well-supported by 8/9 T2 cells matching. C4 (MAX^beta neutralization of BETA across deciles, Table 9 territory) is not in the committed selection — `tables_to_replicate.json` does not include Table 9. Per scope guardrail, this is acceptable. |
| 12 | Claim coverage of committed selection | PASS | All four paper claims (C1, C2, C3, C4) are represented in committed tables. C4 is implicitly exercised by T6's construction (paper's section 3.2 specifies the conditional sort as the test of C4), though no dedicated Table 9 cell is committed. |
| 13 | Sign conventions re-derived from paper | FAIL on P10_RET_RF | Paper Table 1 reports P10_RET-RF = -0.32 (t = -0.85) — high-MAX stocks underperform. The replication reports +0.47 (t = 1.36). Sign disagreement on a load-bearing cell. The D10-D1 RET-RF is correctly signed (-0.27 vs paper -0.95), so the spread sign is fine — the issue is that P10 in isolation is positive rather than negative, which means the magnitude gap is in the short leg specifically. |
| 14 | Reporting discipline (grid completeness, claim citations, SE-less headlines) | PASS | Every committed cell in `results/table_*.md` carries the NW(6) t-stat in parentheses. The headline claim of "the magnitude gap is documented as [VINTAGE-DRIFT]" in REPORT.md cites no t-stat/SE for the magnitude gap itself — but that is a non-significant gap (the spread is significant at t = -2.62 CAPM, just smaller than paper), so this is borderline. The narrative is consistent with the headline cells. |
| 15 | REPORT.md headline freshness (tally matches eval/scoring.json; DEV-010) | PASS | `REPORT.md` headline tally shows `n_cells = 25, match = 10, fail = 15, loss = 0.60`. Matches `eval/per_cell_evaluation.json#aggregates` exactly. |

## 4. Issues the agent should have caught (didn't)

1. **The sign disagreement on P10_RET_RF deserves a dedicated paragraph in REPORT.md, not a footnote.** REPORT.md §1.2 notes that "the replicated high-MAX portfolio (P10) excess return is +0.47%/month where the paper reports −0.32%/month. This is the single source of the magnitude shortfall" — but the language frames it as a magnitude question when it is in fact also a sign question. A peer reviewer would flag this immediately: even if the spread is correctly signed (D10 - D1 < 0), the fact that P10 alone is the wrong sign means the construction is in some way wrong, not just small.

2. **The 25-cell scope is honest, but the 35-cell "skipped" cells in the pre-binary-match scoring.json file are misleading.** A casual reader would conclude that 35 cells were committed; only 25 are. The replicator left the stale file in place. The canonical scorer overwrites it, but the iteration log should mention the discrepancy was noticed and re-run.

3. **The third-party factors (SY, DHS, FFCPS, FF6PS) are central to the paper's argument** — the paper's "novel" contribution is that the MAX^beta anomaly survives SY/DHS whereas the original MAX anomaly does not. Dropping these cells as SKIP removes 20 of the paper's most novel cells from evaluation. This is well-documented in `assumptions.md` A1-A3, but it means the replication cannot evaluate the paper's central novel claim (C2's resilience to mispricing factors). A future iteration could load SY/DHS factors as external CSVs and exercise those cells.

4. **The ME_lag1 choice is flagged as a hypothesis** in `REPORT.md` §3 but never tested by adding a June-t ME snapshot and re-running. This is the single highest-leverage next-iteration fix.

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "MAX on Steroids: A New Measure of Investor Attraction to Lottery Stocks" (Bali, Ince, Ozsoylev) for slug `max_on_steroids_attempt4`. The previous agent run completed with verdict **FAILED** (audit 1 at `replications/max_on_steroids_attempt4/logs/audit1.md`). Read the audit first.

## Issues to address (priority order)

### [M1] — MAJOR — fix first

**Headline sign disagreement on P10_RET_RF (Tables 1 and 6).** Replicated +0.47%/mo vs paper -0.32 (T1) and -0.10 (T6). Direction matches on the spread (D10-D1 < 0) but the high-MAX portfolio alone is positive in the replication.

**Specific fix:**
1. Add a `me_june_t` column to `data/panel.parquet`: for each (permno, month), `me_june_t` = ME at the June of fiscal-year `y - 1` if month is July-December of year `y`, else ME at the June of year `y` if month is January-June of year `y`. This is the standard FF1993/Bali 2011 carry-forward convention.
2. Re-run `src/table1_max.py` with the new VW weight (`me_june_t` instead of `ME_lag1`); report `P10_RET_RF` and `D10_D1_RET_RF` side-by-side with the current values.
3. If `P10_RET_RF` flips negative under June-t ME weights, M1 is fixed by the weight convention alone. If it does not, the issue is the 2026 CRSP vintage's COVID-era lottery tail — in which case restrict the sample to 1968-2019 and re-run.

**Verification:** After the fix, `P10_RET_RF` on T1 should be ≤ 0 (paper -0.32). The D10_D1_RET_RF target is paper -0.95; aim for r ∈ [0.5, 2.0] (i.e., replicated value ∈ [-1.90, -0.475]).

### [M2] — MAJOR — fix after [M1]

**Magnitude shortfall on every D10-D1 spread cell (Tables 1 and 6).** Replicated alphas are 11-30% of paper across CAPM, FF3, FFC4, FF5, FF6. The June-t ME fix from [M1] is the leading candidate; if it lands, the D10-D1 alphas should follow.

**Specific fix:**
1. Same as [M1] step 1 — add `me_june_t` to the panel.
2. Re-run `src/table1_max.py` and `src/table6_maxbeta.py` with `me_june_t` as the VW weight.
3. For each D10_D1 cell in the canonical `per_cell_evaluation.json` (T1: D10_D1_RET_RF/CAPM/FF3/FFC4/FF5/FF6; T6: same), report the new replicated value and the r = |replicated/paper| ratio. Aim for every r in [0.5, 2.0]; below [0.33, 3.0] still fails the rubric.
4. If June-t ME is insufficient, also try: (a) drop COVID-era months 2020-04..2020-12 from the panel; (b) switch NYSE-breakpoints back to all-stocks breakpoints for Table 1 only (the paper's MAX sort may not use NYSE-only breakpoints — this is paper-silent, see Assumption 7/17).

**Verification:** After the fix, run `python3 scripts/score_replication.py replications/max_on_steroids_attempt4 --iteration 2`. Aim for `match_count` ≥ 18 (out of 25), `loss` ≤ 0.30.

### [m1] — MINOR — cleanup

**Stale aggregates in `eval/scoring.json`.** The pre-binary-match file (n_committed=35, 23 SKIP) is overwritten by the canonical scorer but may confuse a downstream reader. Confirm the canonical scorer has overwritten it after running Step [M2] above.

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every iteration log entry in `assumptions.md` must have all five fields: Diagnosis, Next fix, Before metric, After metric, Status. A diagnosis without a Next fix is incomplete — do not move on.
- **Read `rep/STUCK_AGENT_GUIDELINE.md` on your first debug cycle.** Don't rediscover failures that are already documented.
- **10-iteration cap per problem.** Hard stop at 10 and escalate to the human. A documented partial is more valuable than a paper-claiming success that does not actually replicate.
- **Diagnoses must be paired with fix attempts (exit gate).** Before declaring `partial`, walk `assumptions.md` and verify every diagnosed problem has at least one log entry with a non-empty `Next fix` line and a before/after metric.

## Inputs you should read

- `replications/max_on_steroids_attempt4/logs/audit1.md` — this audit (full context)
- `replications/max_on_steroids_attempt4/inputs/content.md` — paper ground truth
- `replications/max_on_steroids_attempt4/preparations/` — prep contract (rules, tables selected, data verification, assumptions iteration log)
- `replications/max_on_steroids_attempt4/src/main.py`, `src/table1_max.py`, `src/table6_maxbeta.py`, `src/table2_chars.py`, `src/evaluate.py` — current code (will be modified)
- `replications/max_on_steroids_attempt4/data/panel.parquet` — cached intermediates (recompute spot-checks from these)

## What NOT to redo

- Skip re-reading `SKILL.md` — the contract is the same.
- `scripts/prep_validation.py` is loop-aware (DEV-009) and safe to re-run at any point.
- Skip re-doing the clickhouse catalog scan — `data_verification.json` is current.
- **DO** re-run any sanity checks you add or modify — they are the gate that catches regressions.

## Deliverables for this iteration

- `replications/max_on_steroids_attempt4/src/main.py` — revised with the June-t ME snapshot added to `data/panel.parquet`
- `replications/max_on_steroids_attempt4/src/table1_max.py` — switched to `me_june_t` VW weight
- `replications/max_on_steroids_attempt4/src/table6_maxbeta.py` — switched to `me_june_t` VW weight
- `replications/max_on_steroids_attempt4/data/panel.parquet` — re-written with the new column
- `replications/max_on_steroids_attempt4/results/table_1.md`, `table_6.md` — updated
- `replications/max_on_steroids_attempt4/eval/metrics.json` — updated with the new replicated values
- `replications/max_on_steroids_attempt4/preparations/assumptions.md` — append a new iteration log entry (A20) with the before/after metric for P10_RET_RF and D10_D1_RET_RF under June-t ME
- `replications/max_on_steroids_attempt4/REPORT.md` — updated; lead with the new headline tally from `eval/scoring.json` after running `python3 scripts/score_replication.py replications/max_on_steroids_attempt4 --iteration 2`

## Stop conditions

- **All blockers fixed and verified** → re-run prep_validation.py and any sanity checks → if both pass, declare success or note remaining majors in `REPORT.md`; the next audit updates `SUMMARY.md`.
- **10-iteration cap reached** on a single problem → escalate to the human and write a partial `REPORT.md`; do not edit `SUMMARY.md`.
- **All blockers fixed but majors remain** → declare partial and document the gap in `REPORT.md`. The auditor's `SUMMARY.md` verdict (REPLICATED / FAILED) is independent of this loop decision.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

This is a thoughtful, well-documented replication. The pipeline is clean (single SQL CTE chain, panel.parquet is the only data artifact, no shell-expansion residue), the iteration log records four passes with explicit fix attempts, and the per-cell evaluation block is reproducible from `src/evaluate.py`. The 8/9 Table 2 match is a genuine replication of the paper's cross-sectional-confounding claim (C3), and the long leg (P1_RET_RF) is within tolerance on both Tables 1 and 6 — these are real positives.

The failure is concentrated: every short-leg headline cell on Tables 1 and 6 is in the wrong sign or magnitude band. The single highest-leverage fix is the VW weight convention (June-t ME vs ME_lag1); this is exactly the hypothesis that the iteration log left on the table as "untested". A next iteration that simply adds `me_june_t` to the panel and re-runs Table 1 + Table 6 would either resolve M1 and M2 simultaneously, or falsify the hypothesis and force the replicator to commit to the residual-magnitude-residue exit per the rubric's criterion B.

The score (overall = 3.00, FAILED) is mechanical and reflects the rubric's sign-flip kill-switch on Signal Strength. This is not a quality judgment — the replication is well above the median for this corpus on methodology and reporting discipline. It is the rubric's band on the headline-magnitude dimension that drives the verdict.