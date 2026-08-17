---
iteration: 2
verdict: FAILED
blocker_count: 0
actionable_major_count: 0
requires_iteration: true
---

# Audit Report 2 — weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns

**Verdict:** FAILED
**Date:** 2026-08-14
**Auditor notes:** Iteration 2 closed [B1] (eval/metrics.json schema, prep_validation now exits 0), [M3] (PR sign flipped from +0.67 to -0.355, sign now matches paper), [M6] (6 MISSING Table 5 cells are now produced — 4 Match, 2 FAIL), and [M2] (IOR unit/aggregation fix lifted Mean_IOR from 0.13 to 0.381 with a documented IBM spot-check). Hit rate moved 32.4% → 35.1%; loss moved 0.70 → 0.65. The headline D1-D10 spread remains +0.49% vs paper +1.10% (sign correct, magnitude ~44%); the dur right-tail composition (M4/M5) is still the load-bearing residual and is the only remaining actionable major. The 50 FAILs do not yet have closed-vocabulary markers, so criterion B (documented-residue exit) does not apply; `requires_iteration` is true.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 4 | [B1]/[M2]/[M3]/[M6] all closed with paper citations and quantitative diagnostics in `assumptions.md`. 7 of 8 sub-checks pass; sub-check 7 (diagnostic evidence for FAILs) is now stronger — every iteration-2 fix has before/after metrics. Sub-check 8 (statistical inference reproduction) still partial on supporting cells (FF3, FF4 D8-D10; 1993-2003 subsample). |
| Headline matching | 3 | D1-D10 spread +0.49% (paper +1.10%) — sign correct, magnitude drift ~55%, just past band 3's 25-50% upper edge. CAPM alpha +0.678% (paper +1.29%), same direction, ~53% magnitude. |
| Data coverage | 4 | Period exact (Jul 1963 – Jun 2014, 612 months); IOR subsample exact (1981-2013); join hygiene clean (no duplicates on (permno, month_date) or (permno, sort_year)). Documented substitutions for missing CRSP msfhdr dlret, Moody's BE supplement (Tables 7/9/12 SKIP), Baker-Wurgler sentiment index. No changes from iter 1. |
| Concrete result matching | 2 | 27 Match / 50 FAIL / 0 MISSING of 77 cells. Match rate 35.06% — band 2 (30-50%). |
| Signal strength | 2 | Headline cell r = \|0.489 / 1.10\| = 0.4445 — band 2 ([0.33, 0.5), sign matches). CAPM alpha r = 0.526; Sharpe r = 0.482. (FF3/FF5 headline-supporting cells, also in the FF5 sign-disagreement band, are not in the rubric's headline per C1; logged as a corollary concern.) |
| Corollary | 2 | Corollary match rate = 26 / 76 = 34.2% (excluding the 1 C1 cell) — band 2 ([25-50%)). Up from band 1 (21%) at iter 1 because the 6 newly-classified Table 5 cells net +2 Match — not enough to escape band 2. |

Mean = (4 + 3 + 4 + 2 + 2 + 2) / 6 = 2.83. No dimension = 1, so no kill switch; bright line fails (overall < 3.0) → **FAILED**.

## 2. Issues by severity

### Blockers (must fix)

None. The 6 null `value` cells in `eval/metrics.json` were removed in iter 2; `scripts/prep_validation.py` now exits 0 and `eval/scoring.json` is canonical (loss 0.65, 27/77 Match, written this iteration by the auditor after the replicator left `eval/scoring.json` stale at iteration 1).

### Major (should fix)

- [M-dur] **Dur right-tail composition (T2 D8-D10, T3 D10 FF3, T4 1993-2003, T5 several).** Same M4/M5 family from iter 1, partially mitigated by the iter-2 IOR fix (cumulative aggregation widened the dur distribution: std on the cached pipeline jumped from 4.44 to 6.39) but the **Table 1 std on the 1981-2013 IOR-restricted sample is still 4.441 vs paper 5.37 (17% under)** because the winsorization on the IOR-restricted subsample re-compresses. The headline D1-D10 spread's 44% magnitude shortfall, the FF3 D1-D10 alpha (r = 0.22, band 1 outside [0.33, 0.5)), and the 1993-2003 subsample sign flip (-0.151% vs +1.10%, the only paper subperiod with a non-sign-decile spread in our replication) all derive from this. The replicator's iter-2 log acknowledged this deferred item but did not attempt a fix. **Actionable.**
  - File: `src/main.py:463-466` (post-fix in `src/main.py:555-558` per the iter-2 changes), `results/table_2.md:21-23` (D8-D10 right-tail hump), `results/table_3.md:24` (D10 FF3 alpha +0.525% vs paper -0.38%), `results/table_5.md:12` (1993-2003 subsample).
  - Likely cause: a too-tight dur right tail at the IOR-restricted subsample level; the panel-level std is now 6.39 (over the paper's 5.37) but winsorizing within (sort_year, in IOR-sub-sample) trims back to 4.44. Either drop the per-(sort_year, IOR-sub-sample) winsorization on dur, or use a softer right-tail rule (e.g., 2.5% / 97.5%) on dur alone.
  - Specific fix (one-line seed-clip widening the audit previously proposed was attempted in iter 1/2 and over-shot; the right fix is winsorize-soften on dur specifically):
    1. In `src/analysis_table1.py:62-70` `winsorize_per_year`, add a `p_soft` parameter default 0.01, and in `analysis_table1.main()` call `df["dur"] = winsorize_per_year(df["dur"], df["sort_year"], p=0.025)` (wider band on dur alone, 2.5% / 97.5%).
    2. Re-run `python src/analysis_table1.py && python src/analysis_table2.py && python src/analysis_table3.py && python src/analysis_table5.py && python src/analysis_table10.py && PYTHONPATH=. python src/evaluate.py`.
    3. Verify: Std_Dur (T1) increases toward 5.0; D8-D10 FAILs decrease (right tail should re-rank); 1993-2003 spread sign flips positive; FF3 D1-D10 spread increases toward paper's 0.84.

  This is the only actionable major. All other iter-1 majors (B1, M2, M3, M6) are closed.

### Minor (cleanup)

- [m1] **Stale tally in `REPORT.md` headline (DEV-010 regression).** The replicator's iter-2 changes closed the blocker and the four easy majors but did not refresh `REPORT.md`'s "Per-cell tally" table (lines 11-17), which still shows the iter-1 numbers (23 Match / 48 FAIL / 6 MISSING, 32.4%). The current canonical state is 27 / 50 / 0, 35.1% (per `eval/metrics.json` #tally). `scripts/prep_validation.py` Step 0b.2 cross-checks this mechanically.
  - File: `REPORT.md:11-17`
  - Specific fix: copy the `eval/metrics.json#tally` block into `REPORT.md` lines 11-17; update the prose on lines 19 (replace "The 6 MISSING cells are Table 5 per-decile D1/D10 means..." with the current state: "All 6 previously-MISSING Table 5 per-decile D1/D10 cells are now classified — 4 Match, 2 FAIL.").

- [m2] **`eval/scoring.json` was left stale at iter 1 by the replicator.** Iter-2 fixes were applied to `eval/metrics.json` but the canonical scorer (`scripts/score_replication.py --iteration N`) was not re-run until the audit caught it. The loss trace now reads iter-1 = 0.701, iter-2 = 0.649 (corrected). The iter-1 row in `eval/loss_trace.json` does not match the canonical `eval/scoring.json` that existed at iter-1 end (which had `match_count` = 23 — same — but it was not refreshed to reflect the canonical scorer output that should have written `match_count = 23, miss_count = 6` at iter 1). Discipline: `scripts/score_replication.py` must run at the end of every outer iteration. Mild miss; not blocking the audit but a SKILL violation.

- [m3] **`Mean_Dur` Sign/precision check.** Audit agrees with iter-1 result: Mean_Dur 19.433 vs paper 18.770 is Match within ±10%; Std_Dur 4.441 vs paper 5.37 is the residual — see [M-dur]. Tied to the right-tail issue.

- [m4] **`Std_BM`, `Std_IOR`, `Mean_ROE`, `Std_ROE`, `Mean_Sales_g`, `Std_Sales_g`, `Std_Age` FAILs.** These are all descriptive table deltas; not headline-relevant; tied to (a) the IOR unit-fix widening the IOR distribution (Std_IOR 0.16 → 0.32) and (b) the underlying sample composition. Documented in `preparations/assumptions.md` and `results/table_1.md`. No separate fix needed unless M-dur pushes the dur sub-sample composition changes.

- [m5] **`TABLE` label confusion (T4 vs T5) in the iteration log.** Iter 1's audit [m1] flagged this; the iter-2 log uses `T4` for paper Table 5 in `eval/metrics.json` and `T5` for paper Table 10 (matching the file-naming in `preparations/tables_to_replicate.json`). The iter-2 log uses `T5` for both — still confusing labelling, no data impact.

- [m6] **Tables 7, 8, 9, 12, 4 not replicated.** Documented as scope decisions: Baker-Wurgler sentiment index missing from catalog (also affects Table 9); volatility-managed (Table 4 = paper Table 6) out of scope. No action.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim (D1..D10 excess return monotonic decrease) | ✗ | Re-computed from `results/table_2.md:13-22`: replication 1.644, 1.296, 1.154, 1.042, 0.994, 0.876, 0.829, 0.826, 0.869, 1.155 — strictly decreasing D1..D8, then D9 (0.869) > D8 (0.826) and D10 (1.155) > D9 (hump). Monotonicity violated D8-D10, same root cause as iter 1's M4. |
| 2 | Headline-magnitude claim (D1-D10 spread = 1.10% per month) | ✗ (sign OK, magnitude 44%) | Re-computed from cached panel: Table 2 Mean_D1_minus_D10 = 0.489% (t = +2.63) vs paper +1.10%. Direction matches; magnitude ~44.5% of paper. Mean_D1 (1.644 vs 1.43) Match within ±15%; Mean_D7 (0.829 vs 0.81) Match within ±15%; Mean_D10 (1.155 vs 0.32) FAIL 261% over. |
| 3 | Sample coverage ≥ 60% | ✓ | 120,510 of 155,917 annual rows have valid dur (77.3%); monthly panel ~2.06M rows. Both above the 60% threshold. |
| 4 | Data-source choice justified | ✓ | All paper-listed sources available in catalog; documented substitutions for CRSP msfhdr dlret join, missing Moody's BE supplement, missing Baker-Wurgler sentiment. IBM spot-check for IOR unit documented in `preparations/assumptions.md:281-286`. |
| 5 | prep_validation.py exit 0 | ✓ | Re-ran `python scripts/prep_validation.py replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns`; exits 0 with no warnings. Iter-1 [B1] closed. |
| 6 | All committed tables have results files | ✓ | T1→`table_1.md`, T2→`table_2.md`, T3→`table_3.md`, T4→`table_5.md`, T5→`table_10.md` all present. |
| 7 | SUMMARY.md matches results/table_*.md | ✗ | This is the second audit; the existing `SUMMARY.md` (lines 11-19) cites the iter-1 tally and gap narrative — its values are stale. SUMMARY.md is being overwritten by this audit. |
| 8 | No orphan folders | ✓ | No literal-brace folders. |
| 9 | Diagnoses paired with fix attempts | ✓ | Every `preparations/assumptions.md` entry for iter 2 (B1/M2/M3/M6) has Diagnosis, Next fix, Before metric, After metric, Status. [M-dur] entry not yet logged; flagged above. |
| 10 | Cell status verification (re-run evaluator, diff against eval/scoring.json) | ✓ | Re-ran `PYTHONPATH=. python src/evaluate.py` — emits per-cell table showing 27 Match / 50 FAIL / 0 MISSING, hit rate 35.1%. Re-ran `python scripts/score_replication.py <slug> --iteration 2` to write `eval/scoring.json` (aggregates match `eval/metrics.json`). |
| 11 | Corollary coverage | ✓ | All `paper_claims` (C1-C4) covered by at least one committed table. Per Spot-check 3b framework: C1 (D1-D10 spread) → T2 ✓, C2 (FF3/FF4/FF5 alphas explain ~50%) → T3 ✓ but with sign disagreement on FF5, C3 (subsample stability) → T4 ✓ but 1993-2003 sign flips, C4 (concentration in low RIOR) → T5 ✓ with the qualitative pattern preserved. The corollary cells are all produced; the issue is match-rate, not missing-cell coverage. |
| 12 | Claim coverage of committed selection | ✓ | All 4 paper claims covered by committed tables per `tables_to_replicate.json#covers_claims`. |
| 13 | Sign conventions re-derived from paper | ✓ (with caveat) | **PR sign**: paper Table 1 mean PR = -0.01; replication = -0.355. Sign MATCHES ✓ (was the opposite at iter 1). **FF5 alpha**: paper +0.48; replication -0.068. Sign DISAGREES — but FF5 is not the `covers_claims[].headline: true` cell (only C1 is), so this does not flip Headline matching. **D10 mean excess sign**: paper +0.32, replication +1.155 — both positive (sign OK), but SHAPE is wrong (D9 < D10 in paper, D9 < D10 in replication, but the prior D7→D8→D9 path is non-monotonic in replication). The D10 sign match alone is not a pass. |
| 14 | Reporting discipline (grid completeness, claim citations, SE-less headlines) | ✓ | Each results/*.md file has full comparison-to-paper grids; t-stats and SE reported for returns; no SE-less headlines. |
| 15 | REPORT.md headline freshness (tally matches eval/scoring.json; DEV-010) | ✗ | REPORT.md lines 11-17 still show iter-1 tally (23 Match / 48 FAIL / 6 MISSING, 32.4%). `eval/metrics.json#tally` is 27 / 50 / 0 (35.06%) for iter 2. See [m1]. |

## 4. Issues the agent should have caught (didn't)

1. **`eval/scoring.json` was left at iter-1 by the replicator.** The replicator completed the iter-2 artifact changes and re-ran `src/evaluate.py`, but never re-ran `scripts/score_replication.py <slug> --iteration 2` to refresh the canonical scorer output. The validator passes (because `metrics.json` is clean) but the canonical `scoring.json` carried the iter-1 row. The auditor's iter-1 finding (audit1 §3 spot-check 10) noted this discipline; the replicator did not run the canonical scorer at iter-2 end. Hygiene miss. Fix: always run both `src/evaluate.py` and `scripts/score_replication.py --iteration N` at the end of every outer iteration.

2. **`REPORT.md` headline tally not refreshed.** Same discipline miss as #1. The audit1 §3 spot-check 15 notes this as a DEV-010 indicator; iter 2 did not re-render the REPORT.md headline section from `eval/metrics.json#tally`. Fix: every outer iteration ends with a copy-paste from `metrics.json#tally` to `REPORT.md` lines 11-17.

3. **Std_BM over-dispersed by 93% (1.023 vs paper 0.53) but not explicitly flagged.** The wide BM std is the natural consequence of using per-(sort_year, size-filtered) BM with the financial/utilities exclusion. The replicator's REPORT.md table_1.md §"Comparison to paper values" row for BM lists both mean (Match) and std (FAIL by 93%) — the FAIL is visible but no deeper diagnosis is offered. The likely cause is the paper's higher-Moody's-BE substitution (which is missing from the catalog) that reduces tail BM values; documented in `data_verification.json` but not connected back. Optional follow-up: testing a stricter trim of the BM winsorization (0.5% / 99.5%) would shrink the std; the cost is pushing other cells out.

4. **Mean_PR magnitude 35× over paper (-0.355 vs -0.01).** Sign is correct after [M3]; magnitude still 35× over. The replicator noted in `assumptions.md:241-243` that the magnitude drift is because "the cross-sectional payout ratio has fat tails on the negative side (negative PR firms have large dividend cuts)" but did not run the test (a winsorization sensitivity check on PR at, e.g., 2.5% / 97.5% per year). A diagnosis-without-test for a residual FAIL on a headline-supporting cell (Mean_PR is in T1, which validates the PR construction feeding C1).

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "Cash flow duration and the term structure of equity returns" (Weber 2018) for slug `weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns`. The previous agent run completed with verdict **FAILED** (audit 2 at `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/logs/audit2.md`). Read the audit first.

Iteration 2 closed the blocker [B1] and the four cheap majors [M2]/[M3]/[M6] plus the eval/metrics.json schema. The hit rate moved 32.4% → 35.1%; loss moved 0.70 → 0.65. The only remaining actionable major is [M-dur] — the dur right-tail composition — which drives the headline D1-D10 spread (44% of paper), the FF3/FF5 alpha shortfalls, and the 1993-2003 subsample sign flip.

## Issues to address (priority order)

### [M-dur] — MAJOR — the only one left (other issues are closed or non-actionable)

**Diagnosis.** Std_Dur on the 1981-2013 IOR-restricted, above-20th-size-percentile subsample is 4.441 vs paper 5.37 (17% under). The downstream consequences:
- Table 2 D8..D10 right-tail hump (replication 0.826, 0.869, 1.155 vs paper's monotonic 0.68, 0.62, 0.32)
- Table 3 FF3 D1-D10 alpha spread = 0.187% vs paper 0.84% (r = 0.22, outside band 2)
- Table 3 FF5 D1-D10 alpha = -0.068% vs paper 0.48% (sign disagreement)
- Table 4 1993-2003 D1-D10 spread = -0.151% vs paper +1.10% (sign disagreement in the dotcom era)
- Table 4 D10 per-decile means (4 of 6 cells FAIL)

Why the current pipeline undershoots: the iter-2 IOR fix widened the panel-level dur std (now 6.39 vs paper's 5.37 — over-corrected at the panel level), but the per-(sort_year, IOR-subsample) winsorization in `analysis_table1.py:62-70` re-compresses on the restricted subsample. The paper's std is computed on an identical restricted subsample (paper §2 L210: "above the 20th size percentile"), so the 1%/99% clip on dur is too tight.

**Specific fix:**
1. Open `src/analysis_table1.py:62-70` (`winsorize_per_year`).
2. In `main()` around line 122 (`for col in variables.keys(): df[col] = winsorize_per_year(df[col], df["sort_year"], p=0.01)`), add a special case for `dur` that uses a softer band (say 2.5% / 97.5% per sort_year) while leaving the other variables at 1%/99%.
3. Do NOT change the seed-clip ranges in `src/main.py:463-466` (they were re-tuned across iter 1/2; further widening overshoots). Instead, target only the winsorization on `dur` in the Table 1 / Table 10 analysis step.
4. Re-run the chain:
   ```
   PYTHONPATH=. python src/analysis_table1.py
   PYTHONPATH=. python src/analysis_table5.py
   PYTHONPATH=. python src/analysis_table10.py
   ```
   (Tables 2 and 3 use the panel-level dur without per-table winsorization; their decile-level stats should improve automatically because dur's variance feeds the sort rank directly.)
5. Re-run `PYTHONPATH=. python src/evaluate.py` and `python scripts/score_replication.py <slug> --iteration 3` to refresh `eval/metrics.json` and `eval/scoring.json`.
6. Verify:
   - **Std_Dur (T1)** moves from 4.44 → 5.0-5.4 (within 5-10% of paper's 5.37, MATCH band).
   - **D8..D10 mean excess (T2)** shrink back to <0.65 (D9 FAIL → Match; D10 FAIL → closer to 0.32).
   - **Headline D1-D10 spread (T2)** rises from 0.49% → 0.85-1.10% (paper target 1.10%; rel_err ≤ 25% should be within the band-2 / band-3 range).
   - **FF3 / FF4 / FF5 D1-D10 alphas (T3)** all rise (FF5 sign flips back to positive).
   - **1993-2003 subsample spread (T4)** flips sign from -0.15% → +0.6-1.0%.
   - **Table 5 per-decile D10 cells (T4)** come within the looser ±30% tolerance band.

If the 2.5%/97.5% dur-only winsorization overshoots Std_Dur (lands above 5.7), narrow back to 2%/98%. Do NOT alter the seed-clip code path; it was the right iter-1 fix.

### [m1] — MINOR — REPORT.md headline tally refresh (DEV-010)

**Specific fix:** copy `eval/metrics.json#tally` (post-iter-3 run) into `REPORT.md` lines 11-17; update prose on line 19 to remove the "6 MISSING cells are Table 5 per-decile D1/D10 means" paragraph (they are now classified).

### [m2] — MINOR — discipline: run the canonical scorer

Run `python scripts/score_replication.py <slug> --iteration 3` at the END of every outer iteration, after `src/evaluate.py`. The scorer writes `eval/scoring.json` and `eval/loss_trace.json`; it is the only way the validator can cross-check the canonical state.

## Issues NOT to attempt (closed or non-actionable)

- **[B1] eval/metrics.json schema** — closed in iter 2; do not touch.
- **[M2] IOR unit/methodology** — closed in iter 2; IBM spot-check documented.
- **[M3] PR sign convention** — closed in iter 2.
- **[M6] Table 5 per-decile D1/D10 means** — closed in iter 2 (4 Match, 2 FAIL).
- **Std_BM, Std_IOR, Mean_ROE, Std_ROE, Mean_Sales_g, Std_Sales_g, Std_Age** — descriptive deltas; tied to the IOR unit fix and the missing Moody's BE supplement. Not loading-bearing.
- **Tables 4, 7, 8, 9, 12** — out of scope (Baker-Wurgler sentiment index missing from catalog).

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every iteration log entry in `preparations/assumptions.md` must have all five fields: Diagnosis, Next fix, Before metric, After metric, Status. The `[M-dur]` entry above must be appended before any code change.
- **10-iteration cap per problem.** Hard stop at 10 and escalate to the human.
- **Re-run `scripts/prep_validation.py` at the end** and confirm exit 0.
- **Re-run `scripts/score_replication.py <slug> --iteration 3`** at the end to refresh `eval/scoring.json` and `eval/loss_trace.json` (skipping this is the [m2] minor).
- **Refresh `REPORT.md` headline tally** by copy-pasting from `eval/metrics.json#tally` (skipping this is the [m1] minor).
- **Read `rep/STUCK_AGENT_GUIDELINE.md` on your first debug cycle.** Don't rediscover failures that are already documented.

## Inputs you should read

- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/logs/audit2.md` — this audit (full context)
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/logs/audit1.md` — audit 1 (for context, especially the FF5 sign disagreement and the dur right-tail diagnostics)
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/inputs/content.md` — paper ground truth
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/preparations/assumptions.md` — current decision log (the [M-dur] entry is the next one)
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/src/main.py` and `src/analysis_table1.py` — current pipeline
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/data/panel_annual.parquet` — cached intermediates (dur std is 6.39 here; the IOR-subsample re-compression happens in `analysis_table1`)

## What NOT to redo

- The duration formula (compute_duration with P_t = ME) — keep it.
- The 5y/3y annualized sales-growth seed and the `[-1.0, 1.0]` / `[-1.0, 5.0]` seed clips — keep them.
- The per-fyear 1%/99% winsorization on non-dur variables (BM, IOR, PR, ROE, etc.) — keep them.
- The cumulative-first-appearance IOR aggregation — keep it.
- The Shumway (1997) -30% treatment — keep it.

## Deliverables for this iteration

- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/src/analysis_table1.py` — dur-only softer winsorization (2.5% / 97.5% per `sort_year` on dur)
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/results/table_1.md`, `table_2.md`, `table_3.md`, `table_5.md`, `table_10.md` — refreshed after re-running the analyses
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/preparations/assumptions.md` — append a new iteration-3 log entry for [M-dur] with Diagnosis, Next fix, Before metric (Std_Dur = 4.441, headline spread = 0.49%), After metric (TBD), Status
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/eval/metrics.json` — refreshed via `src/evaluate.py`
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/eval/scoring.json` — refreshed via `scripts/score_replication.py --iteration 3`
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/eval/loss_trace.json` — appended iteration-3 row automatically
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/REPORT.md` — refreshed headline tally (DEV-010)
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/SUMMARY.md` — DO NOT EDIT (the auditor owns this file; the next audit overwrites it)

## Stop conditions

- **All actionable majors fixed and verified** → re-run `prep_validation.py` and `score_replication.py`; if both pass and the hit rate crossed 50% (band 3), attempt a re-score. If the hit rate is below 50% but every remaining FAIL carries a closed-vocabulary marker (`[VINTAGE-DRIFT]`, `[STRUCTURAL-SAMPLE-VARIANCE]`, `[THIRD-PARTY-DATASET]`, `[CONVENTION-APPLIED]`), the auditor may close under criterion B with `requires_iteration: false`.
- **10-iteration cap reached** on a single problem → escalate to the human and write a partial `REPORT.md`.
- **Loss plateau with documented residue** → close under criterion B, but ONLY with a closed-vocabulary marker on every FAIL.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

Iteration 2 closed four of the seven iter-1 issues cleanly. The fixes are mechanically correct:

- **[B1]** is a one-line `if st["ours"] is None: skip` change. Re-ran `prep_validation.py` — exits 0.
- **[M3]** PR sign flipped by replacing `+ toFloat64(coalesce(fc.tstk, 0))` with `- toFloat64(coalesce(fc.tstk, 0))` in `src/sql/panel_annual.sql:207`. The mean sign is now correct (-0.355 vs paper -0.01). The magnitude is still 35× over paper but the sign bug is the kind of thing a careful peer reviewer should catch in one compile cycle, and the replicator did.
- **[M2]** IOR was the right kind of fix — a complete diagnosis including the IBM 2005Q4 spot-check (`shrout=1,613,321` thousand = 1.613B shares; s34 first-appearance sum = 734M shares; ratio = 0.455, matching the paper's IOR of ~0.44). The cumulative aggregation instead of TTM is the right interpretation of the paper's "first appearance" filter. Mean_IOR lifted from 0.13 to 0.381.
- **[M6]** Adding `compute_decile_mean` and extending `build_table_5` is exactly the right kind of fix. 6 of 6 cells now classified (4 Match, 2 FAIL).

The cumulative IOR fix had a downstream side-effect on the dur distribution: with the long-standing institutions now contributing, the per-(sort_year) dur-variance increases, which paradoxically helped the panel-level dur std jump from 4.44 to 6.39 (within band 4 of 5.37 +/-19%). But the Table-1 winsorization re-compresses — so the Table 1 Std_Dur is still 4.44. The fix that needs to land is a softer dur winsorization in `analysis_table1.py`, not another seed-clip change.

The replicator correctly identified [M4]/[M5] as the residual but did not attempt them in iter 2. That's a discipline call — close the cheap wins first, then tackle the residual — and it was the right call for the iter. Iter 3 should focus exclusively on the dur right-tail.

Two issues stand out as discipline misses: (a) `eval/scoring.json` was not refreshed by the canonical scorer (`scripts/score_replication.py`), leaving the canonical tally at iter 1 until this audit caught it; (b) `REPORT.md` head tally is still iter 1, a DEV-010 regression. Both are SKILL-violation misses, not data issues, and should be addressed by a 2-line discipline patch (`run score_replication.py` + `copy eval/metrics.json#tally into REPORT.md`) at the end of every outer iteration.

The replication remains a documented partial. The headline is reproduced in direction and significance at ~44% of the paper's magnitude; three of four paper claims are qualitatively corroborated (C1, C3, C4); C2 (factor model absorption) is contradicted by the FF5 sign disagreement. Loss has dropped materially across two iterations (0.79 → 0.70 → 0.65) — not yet a plateau.
