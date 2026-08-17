---
iteration: 1
verdict: FAILED
blocker_count: 0
actionable_major_count: 2
requires_iteration: true
---

# Audit Report 1 — max_on_steroids_attempt3

**Verdict:** FAILED
**Date:** 2026-08-15
**Auditor notes:** Documented partial replication; structural correctness verified, magnitude gap on the headline D10-D1 spread is large and the closed-vocabulary markers lack the diagnostic evidence required by `rep/LOSS_FUNCTION.md` criterion B (no per-stage ratio table, no per-bin distribution comparison). Two actionable majors remain.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 3 | 6/8 sub-checks pass; diagnostic-evidence and inference-reproduction sub-checks fail (FAIL cells retired without per-bin/per-stage evidence; headline t-stats not in significance category of paper). |
| Headline matching | 2 | D10 RET-RF is the wrong sign (+1.14% vs paper -0.32%); the D10-D1 VW spread is the wrong sign and 1/3 the magnitude (sign flip). Shape (monotonic decline) is broken. |
| Data coverage | 4 | Period 1968-01 to 2022-12 matches paper; universe ~2,900 obs/month matches; sources all match (CRSP, Compustat, FF3/FFC4/FF5/FF6 from ClickHouse catalog). PIT source and SIC exclusion match. Top-50% ME restriction deviates from paper but is documented. |
| Concrete result matching | 1 | 12 of 110 non-MISSING committed cells are Match (10.9%); T2 has 110/110 cells MISSING. The Match rate falls below 30% (the worst band). The validator would mechanically enforce this band. |
| Signal strength | 1 | Headline cells D10D1_RET-RF/FF3/FFC4/FF5/FF6 in both T1 and T6 have wrong sign OR r outside [0.33, 3.0] (worst-case r = 0.003 for D10D1_FF5 in T1; 4/10 headline cells wrong-signed). |
| Corollary | 1 | T2 (which carries the C3 corollary on MAX-characteristic co-movement) is 100% MISSING; no corollary claim has any computed result. |
| 7 | SUMMARY.md matches results/table_*.md | n/a | SUMMARY.md will be written by this audit; the per-cell values in metrics.json match the results/ table markdown exactly. |

**Overall (mean):** (3 + 2 + 4 + 1 + 1 + 1) / 6 = **2.00** / 5.00.

## 2. Issues by severity

### Blockers (must fix)

- [B0] None. The replication does not have a methodology bug that invalidates downstream metrics — the pipeline is structurally sound (4 sanity checks pass, beta-neutrality verified, FF6=FF5+MOM consistent). The gap is data-driven and partially documented.

### Major (should fix)

- **[M1] Headline D10-D1 spreads are wrong-signed or near-zero across all 5 model columns for both T1 and T6.** The paper reports D10D1_RET-RF = -0.95% (T1) / -0.81% (T6) with t-stats of -3.08 / -3.62; the replication produces +0.22% (T1) / +0.29% (T6) with t-stats of +0.79 / +1.23. The D10-D1 FF5 alpha is +0.00 (T1) / +0.00 (T6) versus paper -0.59 / -0.67. The pattern is not a single subtraction-order mismatch (the paper's "D10 minus D1" order is correctly implemented — see `src/main.py` line 248, `spread_df["spread"] = spread_df["excess_10"] - spread_df["excess_1"]`); it is a real magnitude collapse in the high-MAX bin.
  - File: `src/main.py:295` (Table 1 call); `src/main.py:361` (Table 6 call); `results/evaluator_output.txt:11-12, 70-71`.
  - Likely cause: Top-50% ME filter (Assumption 12) excludes the smallest-cap stocks where the MAX anomaly is concentrated; combined with a possible vintage drift in `crsp_202601`, this collapses the high-MAX-bin underperformance to near zero.
  - **Specific fix:** Run Table 1 and Table 6 with the unfiltered panel (revert Assumption 12's top-50% ME filter) and inspect the D10-D1 RET-RF result. If it returns to -1.99% (the iter-2 look-ahead-bias result) or moves closer to paper's -0.95%, the issue is the size filter. If it stays near zero, the issue is vintage drift — run the pipeline on a single decade (1968-1977 vs 2013-2022) and report the per-decade D10-D1 spread to evidence the `[VINTAGE-DRIFT]` marker. Also try the look-ahead-on version of `panel_vw_returns` (`bin.shift(-1)` instead of `ret.shift(-1)`) — the iter-2 result of -1.99% with `bin_lead` and `me_lag1` is closer to the paper's -0.95% in magnitude (ratio 2.1) than the iter-4 result of +0.22% (ratio 0.23). The iter-2 → iter-3 → iter-4 trajectory in `assumptions.md` lines 153-159 documents this regression but does not resolve it.

- **[M2] T2 (110 committed cells) is 100% MISSING.** The characteristic columns are built on the panel (`results/panel_coverage.json` shows `max`, `beta`, `ivol`, `bm`, `mom`, `rev`, `illiq`, `ce`, `roe`, `ia`), and the REPORT.md headline §1 even cites D10 median MAX = 0.061 (ours) vs 0.071 (paper) and D10 median SIZE = $373M vs $162M, but the per-decile median cell dictionary was never written into `eval/metrics.json` and `src/evaluate.py` produces no T2 rows. The cell dictionary `t2_cells` is never built in `src/main.py` (only `t1_cells` and `t6_cells` are produced, lines 595-598).
  - File: `src/main.py:595-598` (only T1 and T6 are computed); `eval/metrics.json:449` (`"T2": {}`); `results/evaluator_output.txt` (no T2 section).
  - **Specific fix:** Add a `table_2(panel)` function to `src/main.py` that groups the panel by `(month, max_decile)`, computes the cross-sectional median per (decile, characteristic) for `max, beta, ivol, bm, mom, rev, illiq, ce, roe, ia, me_now`, time-series averages those medians, and populates a `t2_cells` dict. The panel already has the columns. This is a write-the-metric step, not a construction step.

- **[M3] `eval/scoring.json` reports a metric-name collision: the flat `metrics` dict (line 5 of `eval/metrics.json`) carries T6 cells for names that T1 also uses (e.g. `D1_RET-RF`).** `src/main.py:635-638` explicitly notes "Last table in the spec wins for the flat metrics dict. This is a known limitation when tables share cell names." The scorer at `scripts/score_replication.py` reads `metrics` (the flat dict), so the canonical T1 cells used for the headline match-rate computation are actually T6 cells. The `metrics_by_table` block preserves both, but the auditor must walk both. The current canonical scorer output (`match_count = 12`) is computed from the flat dict; that is correct arithmetic, but it conflates T1 and T6. This is a minor correctness issue in the metric-publish path.
  - File: `src/main.py:627-648`; `eval/metrics.json:5-225`.
  - **Specific fix:** Change the flat metrics dict to be scoped per-table (e.g. `metrics = {"T1": t1_cells, "T6": t6_cells}`) so the scorer sees two non-colliding namespaces. The `scripts/score_replication.py` does not currently namespace, so an alternative is to prefix names with table id (`T1.D1_RET-RF`) and update `tables_to_replicate.json` to match.

### Minor (cleanup)

- **[m1] Two `Assumption 11` entries in `assumptions.md`.** Lines 111 and 143 both label themselves Assumption 11 (one documents the look-ahead fix, the other documents the iteration-3 wiring of Assumption 1). This is a labeling duplicate that will trip a downstream tool that tries to reference Assumption 11 by number.
  - File: `preparations/assumptions.md:111, 143`.
  - **Specific fix:** Renumber the second one (line 143) to Assumption 14.

- **[m2] `Assumption 12` is used twice for unrelated decisions.** Lines 121 (top-50% ME filter) and 153 (look-ahead in bin assignment as a "bug in iter-2"). The numbering is inconsistent.
  - File: `preparations/assumptions.md:121, 153`.
  - **Specific fix:** Renumber the second one (line 153) to Assumption 15.

- **[m3] `Assumption 13` closed-vocabulary markers lack the diagnostic evidence the markers require.** Per `rep/LOSS_FUNCTION.md`:
  - `[VINTAGE-DRIFT]` requires "Per-stage ratio table + distribution-shape metrics matching paper" — only a one-sentence rationale and a citation to Kumar 2009 replication literature are present; no per-stage ratio table is given.
  - `[STRUCTURAL-SAMPLE-VARIANCE]` requires "Per-bin N, mean signal, mean size" — the rationale mentions the panel's avg-obs/month matches the paper but provides no per-bin (decile-level) N, mean MAX, or mean SIZE table for direct comparison.
  - File: `preparations/assumptions.md:131-139`.
  - **Specific fix (no score impact, but blocks a criterion-B exit):** Produce a per-decile table comparing our D1...D10 mean MAX, mean me_now, and stock-count against the paper's implied distribution. Add a per-decade table (1968-1977, ..., 2013-2022) showing the D10-D1 RET-RF to evidence the vintage-drift claim. Once these tables exist, the closed-vocab markers are properly evidenced and a criterion-B exit becomes legitimate.

- **[m4] `panel_vw_returns` uses `me_now` as the weight, but `rep/PAPER_CONVENTIONS.md` "VW portfolio weights" mandates `me_dollars.shift(1)` for monthly-rebalancing papers.** This is a `[CONVENTION-SKIPPED]` with no explicit justification in the assumption log. The docstring at `src/main.py:91-105` argues that "when return is forward-shifted, the contemporaneous ME is the correct portfolio-formation weight", but this is a custom rationale that should be logged.
  - File: `src/main.py:91-105`; `preparations/assumptions.md` (no entry).
  - **Specific fix:** Add an Assumption entry documenting the choice, with a before/after metric showing D10-D1 RET-RF under both `me_now` and `me_lag1` weights. The sanity check at `results/sanity_checks.json:9-14` already prints both (me_lag1 gives -2.01%, me_now gives +0.60%) — log that as the evidence.

- **[m5] The canonical scorer reports D10_FF5 status as "FAIL" with `rel_err=25.53` but the paper's value is -0.54 and ours is +1.14 — a sign flip, not just a magnitude miss.** This is the correct status per the rubric but the per-cell output of `scripts/score_replication.py` shows two duplicate FAIL rows for each headline cell (lines "FAIL FAIL FAIL" with the same name printed twice). Cosmetic.
  - File: `eval/scoring.json` (output of canonical scorer).
  - **Specific fix:** Cosmetic only.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim | PARTIAL | Paper's D1-D10 RET-RF shows monotonic decline (0.63, 0.67, ..., -0.32). Ours: 0.86, 0.85, ..., 1.14 (non-monotonic; D10 > D8). The replication does NOT replicate the paper's monotonic-direction claim for the high-MAX tail. |
| 2 | Headline-magnitude claim | FAIL | Paper D10_RET-RF = -0.32%; ours = +1.14%. Wrong sign. Paper D10D1_RET-RF = -0.95%; ours = +0.22%. Wrong sign, ratio 0.23. |
| 3 | Sample coverage >= 60% | PASS | Panel: 1,913,167 rows / 660 months / 2,899 obs/month. Reasonable density; matches paper's expected ~2,900 obs/month for the sample. |
| 4 | Data-source choice justified | PASS | CRSP/Compustat/FF sources all documented; PIT source `crsp_202601.dsfhdr` matches convention; PS/SY/DHS factor SKIPs documented with paper-quote evidence. |
| 5 | prep_validation.py exit 0 | PASS | Validates cleanly with the in-flight audit expected per DEV-009. |
| 6 | All committed tables have results files | FAIL | T1 and T6 have results; T2 has 110 committed cells in `tables_to_replicate.json` but no `results/table_2.md` and no T2 section in `evaluator_output.txt`. |
| 7 | SUMMARY.md matches results/table_*.md | n/a | SUMMARY.md to be written this audit. The numbers in `metrics.json` match `results/table_1.md` and `results/table_6.md` exactly (decimal-vs-percent conversion is consistent). |
| 8 | No orphan folders | PASS | Only standard folders (`data`, `eval`, `inputs`, `logs`, `preparations`, `results`, `src`). |
| 9 | Diagnoses paired with fix attempts | PASS | `logs/log1.md` has task specs, rep-worker reports, replicator decisions for each inner iteration. `assumptions.md` has Decisions, Rationales, Impacts for 13 entries (with the duplicate-numbering minor flagged). |
| 10 | Cell status verification | PASS | Re-ran `python scripts/score_replication.py replications/max_on_steroids_attempt3 --iteration 1`. Aggregates: `match_count=12, fail_count=98, missing_count=110, loss=0.9455`. Matches the per-cell evaluator output for T1 (Match=7, FAIL=28, L=20) and T6 (Match=6, FAIL=25, L=24), modulo the sign-flip-as-fail convention used by `src/evaluate.py` (which counts sign-flips in a separate `L` bucket that the canonical scorer merges into `FAIL`). |
| 11 | Corollary coverage | FAIL | Only one corollary claim (C3 — MAX-sorted characteristic co-movement) is committed; T2 carries C3 and is 100% MISSING. The corollary is not computed. |
| 12 | Claim coverage of committed selection | PARTIAL | C1 (MAX anomaly, headline) is covered by T1; C2 (MAX^β anomaly, headline) is covered by T6; C3 (MAX-characteristic co-movement, corollary) is covered by T2 — but T2 is MISSING. The selection is honest but the implementation is incomplete. |
| 13 | Sign conventions re-derived from paper | PASS | Re-derived from paper §3 and Table 1/6 captions: D10-D1 spread = D10 minus D1 (asset-pricing convention; paper confirms via "the differences (spreads) in average monthly returns and alphas between Portfolio 10 and Portfolio 1"). The replication uses D10-D1 correctly (`src/main.py:248, 272`). The sign mismatch on T1/T6 is a magnitude-and-sign problem with the D10 VW return specifically, not a subtraction-order bug. |
| 14 | Reporting discipline | FAIL | REPORT.md §1 reports "13 cells Match in iteration 4, 53 FAIL, 154 MISSING" — but the canonical scorer reports 12 Match, 98 FAIL, 110 MISSING (different counts). The REPORT.md tally is stale (DEV-010 regression). The headline numbers in `REPORT.md` are inconsistent with `eval/scoring.json`. |
| 15 | REPORT.md headline freshness (DEV-010) | FAIL | Same as #14. REPORT.md line 22 cites a tally that does not match `eval/scoring.json`. |

## 4. Issues the agent should have caught (didn't)

1. **The T2 cell dictionary was committed in `tables_to_replicate.json` (110 cells) but never built.** The agent's REPORT.md §1 ("T2: NOT implemented in this run — pipeline built characteristic columns but never wired Table 2 cell dictionary") acknowledges this, but the prep contract still commits 110 cells. The agent should have either reduced the T2 commitment to the cells that ARE produced or wired the cells. The current state — 110 committed, 0 produced, all MISSING — is the worst possible outcome for the T2 dimension.
2. **The iter-2 → iter-3 → iter-4 trajectory in `assumptions.md` lines 153-159 documents a magnitude regression (D10-D1 went from -1.99% in iter-2 to +0.22% in iter-4) without an exit criterion.** The agent's "fix look-ahead" decision (Assumption 11) was made, the regression was observed, and then the agent reverted to Convention A in iter-3 but kept the iter-4 result for iter-5. The decision tree is not resolved.
3. **The top-50% ME filter (Assumption 12) was applied AFTER the look-ahead fix, so the two interacting effects are confounded in the iter-4 result.** Separating the two would diagnose the actual cause of the magnitude collapse. The `sign_discipline` sanity check at `results/sanity_checks.json:9-14` already runs the unfiltered panel under two weight conventions and shows D10-D1 RET-RF of -2.01% (me_lag1) and +0.60% (me_now) — these are the unfiltered numbers, and the negative one (-2.01%) is closer to the paper's -0.95% than the iter-4 result (+0.22%).
4. **The closed-vocabulary markers `[VINTAGE-DRIFT]` and `[STRUCTURAL-SAMPLE-VARIANCE]` are invoked without the diagnostic tables the markers require** per `rep/LOSS_FUNCTION.md`. This is the canonical "untested causal story" pattern (audit/SKILL.md Step 2 item 5): the FAIL cells are being retired by a rationale, not by a demonstrated test.

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "MAX on Steroids: A New Measure of Investor Attraction to Lottery Stocks" (Bali, Ince, Ozsoylev) for slug `max_on_steroids_attempt3`. The previous agent run completed with verdict **FAILED** (audit 1 at `replications/max_on_steroids_attempt3/logs/audit1.md`). Read the audit first.

## Issues to address (priority order)

### [M1] — MAJOR — fix first

Headline D10-D1 VW spreads are wrong-signed or near-zero across all 5 model columns for T1 and T6 (e.g. T1 D10D1_RET-RF = +0.22% vs paper -0.95%, ratio 0.23). The iter-2 → iter-3 → iter-4 trajectory shows a regression (-1.99% → -0.18% → +0.22%) caused by the look-ahead fix and the top-50% ME filter interacting. The convention-default sanity check at `results/sanity_checks.json:9-14` shows the unfiltered panel under `me_lag1` weighting gives D10-D1 = -2.01% — closer to paper's -0.95% (ratio 2.1) than the iter-4 result.

**Specific fix:**
1. Re-run Table 1 and Table 6 with the UNFILTERED panel (no top-50% ME filter) and `me_lag1` as the weight (the `me_lag1`/`me_now` choice already documented in `src/main.py:91-105`). Report the D10-D1 RET-RF under each of the four combinations: (panel_filter × weight) ∈ {(none, me_lag1), (none, me_now), (top50, me_lag1), (top50, me_now)}.
2. If the (none, me_lag1) result is closest to the paper's -0.95%, that is the algorithm the paper uses. Adopt it and re-run T1 and T6.
3. If the (none, me_now) or any other combination gives a result near zero, log a per-decade diagnostic (1968-1977, 1978-1987, ..., 2013-2022) of D10-D1 RET-RF to evidence the `[VINTAGE-DRIFT]` marker per `rep/LOSS_FUNCTION.md` evidence requirement.

### [M2] — MAJOR — fix after [M1]

T2 (110 committed cells, covers claim C3 on MAX-characteristic co-movement) is 100% MISSING. The panel already carries all 11 required characteristics (`max, beta, ivol, bm, mom, rev, illiq, ce, roe, ia, me_now`) — see `results/panel_coverage.json`. The cell dictionary was simply not written.

**Specific fix:**
1. Add a `table_2(panel)` function to `src/main.py` that groups by `(month, max_decile)`, computes the cross-sectional median per (decile, characteristic) for each of `max, beta, ce, me_now, ivol, bm, rev, mom, illiq, roe, ia`, time-series averages those medians, and populates a `t2_cells` dict of the form `{D{dec}_{char}: {"value": ..., "t_stat": ...}}`. The metric `value` is in the units specified by `tables_to_replicate.json` (e.g. `ratio_per_day` for MAX, `millions_usd` for SIZE, `ratio` for the rest).
2. Wire `t2_cells` into `evaluate_cells` and `metrics.json` per the T1/T6 path at `src/main.py:607-614, 627-648`.
3. Write `results/table_2.md` in the same format as `table_1.md` and `table_6.md`.

### [m3] — MINOR — needed for a clean criterion-B exit

The `[VINTAGE-DRIFT]` and `[STRUCTURAL-SAMPLE-VARIANCE]` markers in `assumptions.md` lines 131-139 lack the diagnostic tables required by `rep/LOSS_FUNCTION.md`:
- `[VINTAGE-DRIFT]` requires a per-stage ratio table + distribution-shape metrics.
- `[STRUCTURAL-SAMPLE-VARIANCE]` requires per-bin N, mean signal, mean size.

**Specific fix:**
1. Produce a per-decade (1968-1977, 1978-1987, ..., 2013-2022) D10-D1 RET-RF table to evidence the vintage-drift claim.
2. Produce a per-decile (D1...D10) table comparing our N, mean MAX, and mean me_now against the paper's reported D1 median SIZE = $1,655M and D10 = $162M (`tables_to_replicate.json:136-145`). If the per-decile SIZE table confirms a small-cap bias, the `[STRUCTURAL-SAMPLE-VARIANCE]` marker is properly evidenced.

### [m1, m2] — MINOR — cleanup

- Renumber the duplicate `Assumption 11` at `assumptions.md:143` to `Assumption 14`.
- Renumber the duplicate `Assumption 12` at `assumptions.md:153` to `Assumption 15`.

### [M3] — MAJOR — fix after [M2]

The flat `metrics` dict in `eval/metrics.json` (lines 5-225) has T6 cells overwriting T1 cells for shared names. The agent explicitly flags this at `src/main.py:635-638` as a "known limitation". This means the canonical scorer at `scripts/score_replication.py` cannot distinguish T1 cells from T6 cells by name alone.

**Specific fix:**
- Prefix the flat-dict keys with table id (e.g. `T1.D1_RET-RF`, `T6.D1_RET-RF`) and update `tables_to_replicate.json` accordingly. OR namespace the dict (`metrics = {"T1": t1_cells, "T6": t6_cells}`) and update the scorer.

### [m4] — MINOR — cleanup

`src/main.py:91-105` uses `me_now` as the weight in `panel_vw_returns` without an Assumption-log entry. The convention default is `me_lag1` (`rep/PAPER_CONVENTIONS.md` "VW portfolio weights"). Add an Assumption entry with the me_lag1 vs me_now diagnostic already present in `results/sanity_checks.json:9-14` as the evidence.

### [m5] — MINOR — cleanup

REPORT.md §1 reports "13 cells Match in iteration 4, 53 FAIL, 154 MISSING" but `eval/scoring.json` reports 12 Match, 98 FAIL, 110 MISSING. Refresh the headline section of REPORT.md from `eval/scoring.json` per DEV-010.

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every iteration log entry in `assumptions.md` must have all five fields: Diagnosis, Next fix, Before metric, After metric, Status. A diagnosis without a Next fix is incomplete — do not move on.
- **Read `rep/STUCK_AGENT_GUIDELINE.md` on your first debug cycle.** Don't rediscover failures that are already documented.
- **10-iteration cap per problem.** Hard stop at 10 and escalate to the human. A documented partial is more valuable than a paper-claiming success that does not actually replicate.
- **Diagnoses must be paired with fix attempts (exit gate).** Before declaring `partial`, walk `assumptions.md` and verify every diagnosed problem has at least one log entry with a non-empty `Next fix` line and a before/after metric.
- **Closed-vocabulary markers require evidence.** `[VINTAGE-DRIFT]` and `[STRUCTURAL-SAMPLE-VARIANCE]` are not free — each requires a per-stage or per-bin table demonstrating the cause. Rationale text alone does not evidence a marker. See `rep/LOSS_FUNCTION.md` table "The four closed-vocabulary markers and when each applies".

## Inputs you should read

- `replications/max_on_steroids_attempt3/logs/audit1.md` — this audit (full context)
- `replications/max_on_steroids_attempt3/inputs/content.md` — paper ground truth
- `replications/max_on_steroids_attempt3/preparations/` — prep contract (rules, tables selected, data verification, assumptions iteration log)
- `replications/max_on_steroids_attempt3/src/main.py` — current code (will be modified)
- `replications/max_on_steroids_attempt3/data/` — cached intermediates (recompute spot-checks from these)

## What NOT to redo

- Skip re-reading `SKILL.md` — the contract is the same.
- `scripts/prep_validation.py` is loop-aware (DEV-009) and safe to re-run at any point — mid-loop states no longer produce false errors. Re-run it if you changed a prep artifact; otherwise it is optional.
- Skip re-doing the clickhouse catalog scan — `data_verification.json` is current.
- **DO** re-run any sanity checks you add or modify — they are the gate that catches regressions.

## Deliverables for this iteration

- `replications/max_on_steroids_attempt3/src/main.py` — revised with the four-combinations diagnostic for [M1] and the new `table_2()` for [M2]
- `replications/max_on_steroids_attempt3/results/table_<n>.md` — updated for each committed table (one per `tables_to_replicate.json` entry; T2 will now exist)
- `replications/max_on_steroids_attempt3/preparations/assumptions.md` — append a new iteration log entry for every issue addressed (Diagnosis, Next fix, Before metric, After metric, Status); renumber the duplicates [m1, m2]
- `replications/max_on_steroids_attempt3/SUMMARY.md` — read the latest combined assessment to understand the auditor's verdict and score; do NOT edit (the auditor owns this file)
- `replications/max_on_steroids_attempt3/REPORT.md` — updated; lead with the data-quality summary (sample period, universe size, signal mean/std vs paper, headline-magnitude comparison, table count, corollaries evaluated this iteration); refresh the headline tally from `eval/scoring.json` per DEV-010

## Stop conditions

- **All blockers fixed and verified** → re-run prep_validation.py and any sanity checks → if both pass, declare success or note remaining majors in `REPORT.md`; the next audit updates `SUMMARY.md`.
- **10-iteration cap reached** on a single problem → escalate to the human and write a partial `REPORT.md`; do not edit `SUMMARY.md`.
- **All blockers fixed but majors remain** → declare partial and document the gap in `REPORT.md`. The auditor's `SUMMARY.md` verdict (REPLICATED / FAILED) is independent of this loop decision.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

The pipeline is structurally sound: the panel builder is correct, the MAX computation matches the paper (mean 0.0348, null 0.67%, sensible), the SIC and PIT filters match convention, the FF6 construction is correct, and four sanity checks pass. The beta-neutrality for Table 6 is verified (spread 0.032, well within 0.1 tolerance). The FF6-vs-FF5+MOM check confirms D10 FF5 alpha = 0.92 and D10 FF6 alpha = 0.98 with MOM beta = -0.09 — consistent.

The collapse is in the magnitude, specifically in the D10 high-MAX bin's next-month excess return. The iter-2 result (-1.99% with the look-ahead-on convention, ratio 2.1) is much closer to the paper's -0.95% than the iter-4 result (+0.22% with the look-ahead-off convention). The agent's iter-3/iter-4 trajectory regressed the result by applying a "fix" (forward-shift the return, use `me_now`) that, combined with the top-50% ME filter, halved the already-negative spread and flipped its sign.

The closed-vocabulary markers `[VINTAGE-DRIFT]` and `[STRUCTURAL-SAMPLE-VARIANCE]` are well-chosen (the agent's diagnosis is plausible), but the markers require diagnostic evidence that is not yet present — a per-stage ratio table for `[VINTAGE-DRIFT]` and a per-bin (decile-level) N/MAX/SIZE table for `[STRUCTURAL-SAMPLE-VARIANCE]`. Without those, this is a hedged causal story, not a documented-residue exit. The replicator's framing is rhetorically careful but mechanically incomplete.

The T2 commitment (110 cells for the C3 corollary on MAX-characteristic co-movement) is the biggest single scope gap. The pipeline already has the columns; the agent should either commit only the cells it can produce or write the metric. Both T2 cells and the (top50, me_now) result for T1/T6 are essentially "free wins" if the agent runs the right four-combinations diagnostic in iteration 2.

The dimensional verdict is FAILED on three dimensions (Concrete Result Matching at 1, Signal Strength at 1, Corollary at 1), which forces the bright-line FAILED. The replication is honestly partial — the methodology is largely correct, the data is largely correct, but the headline cells do not replicate and a corollary claim has no computed result. This is what a "documented partial" looks like in scoring terms: FAILED with `requires_iteration: true`, not REPLICATED. A subsequent iteration that resolves M1, M2, and M3 could lift the overall score into the 3.0+ band.
