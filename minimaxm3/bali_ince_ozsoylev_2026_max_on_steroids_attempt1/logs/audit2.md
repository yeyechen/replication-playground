---
iteration: 2
verdict: FAILED
blocker_count: 3
actionable_major_count: 3
requires_iteration: true
---

# Audit Report 2 — bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to

**Verdict:** FAILED
**Date:** 2026-08-14
**Auditor notes:** The audit-1 [B1] beta-source fix was applied (`avg(if(beta_mktrf BETWEEN -5 AND 10, ...))` instead of `argMax`) and the panel-level beta distribution tightened (mean 1.13, std 0.98, min −4.94, max 9.98 — was min −29.7, max 12.5). However, the fix made Table 6 worse on the headline sign: the MAX^beta 10-1 spread flipped from −0.02 (iter 1) to +0.37 (iter 2) — paper is −0.81. The previous iter-1 zero-band matches (T3_P5_FF5/FF6, T3_P9_RET_RF) no longer fall within tolerance. Canonical scorer loss rose from 0.9634 → 1.0000 (3 Match → 0 Match). T2 and T4 still MISSING. No new tables were built; Table 9 Panel B (INST terciles) and Table 2 (characteristics spread) remain unbuilt. The replicator's exit strategy is the documented-residue exit (criterion B), but the failure-mode evidence (sign flips on headline C1) shows the gap is not residual — it is actionable.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 3/5 | Beta aggregation convention applied with documented justification (`assumptions.md` A8). Sub-checks 7 (diagnostic evidence for FAILs) and 8 (significance reproduction) still fail. The new beta convention flipped T6's headline sign — the fix changed the symptom but did not diagnose the cause. |
| Headline matching | 1/5 | T3 SPREAD_RET_RF: paper −0.81 vs ours +0.37 — wrong sign (r = 0.46, wrong direction). T1 SPREAD_RET_RF: paper −0.95 vs ours −0.32 — direction matches, magnitude 3x attenuated (r = 0.33, at band boundary). T1 P10_RET_RF: paper −0.32 vs ours +0.77 — wrong sign. |
| Data coverage | 3/5 | Period, universe, and CRSP sources unchanged (pass). Table 6 sample still truncated to 2002-2022 (pre-2002 betas unavailable — same as iter 1). Third-party factor data (PS-LIQ, SY MGMT/PERF, DHS FIN/PEAD) still absent (same as iter 1). |
| Concrete result matching | 1/5 | Canonical scorer iter 2: 0 Match / 52 FAIL / 30 MISSING / 82 committed — loss L = 1.0000. Iter 1 had 3 Match (T3_P5_FF5, T3_P5_FF6, T3_P9_RET_RF — zero-band cells); iter 2 has 0 because the beta fix changed those cells away from zero (T3_P5_FF5 went from 0.02 → 0.72; T3_P9_RET_RF went from 0.31 → 0.44). |
| Signal strength | 1/5 | Worst-case headline cell: T3_SPREAD_RET_RF — paper −0.81, ours +0.37 → r = 0.46 with sign flip (paper negative, ours positive). r outside [0.33, 3.0] with sign disagreement = band 1. All six T3 spread cells have wrong sign. |
| Corollary | 1/5 | T2 (12 cells, characteristics spread) entirely MISSING. T4 (18 cells, INST-stratified MAX^beta) entirely MISSING. No corollary claim has any computed result the next iteration can verify against the paper. |
| **Overall** | **1.67** | FAILED by both bright line (overall < 3.0) and kill switch (four dimensions at 1: headline_matching, concrete_result, signal_strength, corollary). |

## 2. Issues by severity

### Blockers (must fix)

- **[B1] Table 6 (MAX^beta) headline sign flipped negative-to-positive.**
  - File: `results/table_6.md:15` (10-1 spread = +0.37 vs paper −0.81); `eval/scoring.json` T3 cells.
  - Paper Table 6 SPREAD_RET_RF = −0.81 (L2206); iter-1 replication gave −0.02 (sign right, magnitude collapsed); iter-2 replication gives +0.37 (sign WRONG). All six T3 SPREAD cells (RET_RF, CAPM, FF3, FFC4, FF5, FF6) are wrong-sign. The beta-source fix from iter 1 (replacing `argMax(beta_mktrf, dt)` with `avg(if(beta_mktrf BETWEEN -5 AND 10, beta_mktrf, NULL))`) tightened the beta distribution (min moved from −29.7 to −4.94; max from 12.5 to 9.98), but the dependent double-sort now produces positive MAX^beta excess returns — the opposite of the paper's claim.
  - The diagnostic in `log2.md` lines 46-51 acknowledges three possible causes (MAX signal construction, universe vintage, return timing) and lists a cheap MAX-5 spot check that was NOT run within the available time budget. Hedged language ("most likely", "perhaps") in `log2.md` lines 65-69 is a diagnose-and-skip, not a diagnostic test.
  - Specific fix: Run the MAX-5 spot check from `log2.md` line 51 (compute `MAX-5 = sum(top_5) / 5` on a known sample month for permno 10107 in 2010-01-31 and hand-verify against the daily CRSP tape). Separately, recompute Table 6 P10 RET-RF on the 2002-2022 sample WITHOUT the beta filter (the filter may be hiding a sign-flipped subset). The goal is to isolate which of (a) MAX signal, (b) beta filter, (c) sample truncation drives the sign flip. Re-run Table 6 with the corrected identification.

- **[B2] Concrete result match rate dropped from 3.66% to 0% — net regression.**
  - File: `eval/scoring.json` (canonical DEV-019 scorer, written by `python scripts/score_replication.py … --iteration 2`): iter-2 aggregates are `match_count=0, fail_count=52, missing_count=30, skip_count=0, loss=1.0` vs iter-1's `match=3, fail=49, missing=30, loss=0.9634`. The loss INCREASED; the previous run was closer to a Match on three cells (T3_P5_FF5, T3_P5_FF6, T3_P9_RET_RF) and the new run moved them off zero (T3_P5_FF5 went 0.02 → 0.72; T3_P9_RET_RF went 0.31 → 0.44). These three cells flipped from Match to FAIL not because of tolerance change but because the iter-2 numbers fell outside the zero_band 0.10.
  - This is the iter-2 regression the rubric is built to detect: a fix that moves the metric farther from the paper while claiming partial success. The replicator's REPORT.md line 5 still cites the iter-1 canonical tally (`Match=1, FAIL=51, MISSING=0, SKIP=9, Loss L = 0.9808`) — the headline tally in REPORT.md is stale relative to `eval/scoring.json` (DEV-010).
  - Specific fix: Re-render REPORT.md headline tally from canonical `eval/scoring.json` (Match=0 / FAIL=52 / MISSING=30 / SKIP=0 / Loss L=1.0000). Document the loss-regression in `assumptions.md` as a new iteration log entry. Before declaring any further partial progress, run the MAX-5 spot check (B1) and confirm whether the sign flip is reversible.

- **[B3] Table 9 Panel B (INST-stratified MAX^beta) and Table 2 (characteristics spread) not built — second consecutive audit.**
  - File: `eval/scoring.json` T2 cells (12) and T4 cells (18) — all `status: MISSING` in canonical scorer; `src/tables.py:368-410` only builds T1 and T6.
  - Paper C4 (heterogeneous skewness preference across clienteles) is tested by Table 9 Panel B and is one of the paper's three named contributions (L11 of inputs/content.md). Paper C2 mispricing claim is backed by Table 2 characteristics spreads (MIS, CE, IVOL, INST). Both are still entirely missing.
  - The `log2.md` line 24 says these tables are "NOT FIXED. Skipped due to time budget." This is a second-iteration continuation of the iter-1 blocker [B3], which the rubric flags as not-progressing: the gap remains and the exit strategy is "time budget."
  - Specific fix: Build `instown_202601.s34` aggregation to (permno, month) institutional-ownership terciles and run the three-way MAX×beta×INST sort for Table 9 Panel B (9 cells: 3 INST × 3 MAX legs, RET-RF + 2 alpha columns). For Table 2, add the 12 characteristics-spread rows that can be computed from the existing panel (MAX, BETA, BM, MOM, REV, ILLIQ, ROE are already in `data/panel.parquet`); leave IVOL/E(ISKEW)/MIS/CE as documented MISSING with a `[THIRD-PARTY-DATASET]` or `[UNCOMPUTABLE]` marker. At minimum, the 8 computable rows would convert 8 of the 30 MISSING cells into testable FAIL/Partial cells.

### Major (should fix)

- **[M1] Magnitude gap on Table 1 (~3x attenuation) — closed with hedged causal story.**
  - File: `results/table_1.md:15` (10-1 spread = −0.32 vs paper −0.95); `eval/scoring.json` T1 cells (all 26 FAIL).
  - The T1 P10_RET_RF sign is still flipped (paper −0.32, ours +0.77) — same as iter 1. The replicator's `[STRUCTURAL-SAMPLE-VARIANCE]` marker in `preparations/assumptions.md` line 130-150 cites four possible causes (MAX signal definition, VW weighting convention, RF series, post-publication attenuation) without running the cheap diagnostic tests that would distinguish among them (`log2.md` line 28 confirms M1 was not pursued in this iteration).
  - Specific fix: Run the MAX-5 hand-verification spot check (same as B1 — the diagnostic covers both B1 and M1 simultaneously). Try lag-1 ME for VW weighting (replace `me` in `src/tables.py:138` with `me.shift(1)` per permno, then re-sort) and compare the P10_RET_RF sign. Compare `rf3` from `ff.three_factor` against an alternative rf source. Each is a ~10-line code change and re-run.

- **[M2] Pre-2002 market betas unavailable — Table 6 sample truncated to 38% of paper's window.**
  - File: `data/panel_summary.json` `beta_m` n_non_null = 31,950 of 1,693,841 (1.9%); `preparations/assumptions.md` Limitation 2.
  - The MAX^beta sample (2002-2022) is post-publication for Bali, Cakici, Whitelaw (2011), and the paper documents (footnote 1, L39 of inputs/content.md) that the MAX effect "remained economically large and statistically significant for the post-publication period of … March 2011-December 2022." With sample 2002-2022, the iter-2 MAX^beta effect is wrong-sign — the truncation to the post-publication period is a plausible driver, but the cheap test (compute MAX-only P10_RET_RF on the 2002-2022 subset alone and compare to the full-sample P10_RET_RF) was not run.
  - Specific fix: Compute MAX-only P10_RET_RF on the 2002-2022 subset of the panel and compare to P10_RET_RF on the full 1968-2022 sample. If the 2002-2022 subset matches the full-sample T1 P10_RET_RF, the truncation is not the cause of the Table 1 magnitude gap; if it differs, the truncation is a real driver. Either result is actionable. The diagnostic is in `src/tables.py:390` (one-line change to add a date filter before `build_decile_table`).

- **[M3] Cell status misassignment between `eval/metrics.json` (replicator) and `eval/scoring.json` (canonical scorer).**
  - File: `eval/metrics.json` shows `n_match=0, n_fail=52, n_skip=9, n_missing=0`; `eval/scoring.json` shows `match_count=0, fail_count=52, missing_count=30, skip_count=0`. The replicator's evaluator (`src/evaluate.py:134-140`) classifies T4 cells as `SKIP (T9 not built)`; the canonical DEV-019 scorer classifies all 30 T2+T4 cells as MISSING (no `ours` value produced).
  - The replicator's `eval/metrics.json` is in a legacy schema (no `schema_version`, key `loss_L` instead of `loss`, no per-cell `rel_err`). The canonical scorer overwrites `eval/scoring.json` on every run. The two artifacts disagree on whether 9 T4 RET_RF cells are SKIP or MISSING — both views are defensible but the disagreement is undocumented.
  - Specific fix: Decide on one convention. If the replicator intends SKIP for "tables we chose not to build because of time budget," document the choice in `assumptions.md` and add a `skip` block to `tables_to_replicate.json` for the 9 T4 cells. If the cells are genuinely MISSING because the table was never built, drop the SKIP classification from `src/evaluate.py`. Either way, the two artifacts must agree on the per-cell status.

### Minor (cleanup)

- **[m1] REPORT.md headline tally is stale (DEV-010).**
  - File: `REPORT.md` line 5 cites `Match=1, FAIL=51, MISSING=0, SKIP=9, Loss L = 0.9808`. Canonical `eval/scoring.json` is `Match=0, FAIL=52, MISSING=30, SKIP=0, Loss L=1.0000` after the iter-2 scorer run.
  - Specific fix: Re-render REPORT.md headline tally from canonical `eval/scoring.json`.

- **[m2] `assumptions.md` Limitation 4/5 (Table 1 magnitude, Table 6 spread) carry `[STRUCTURAL-SAMPLE-VARIANCE]` markers without test evidence.**
  - File: `preparations/assumptions.md` lines 130-160.
  - The Step-2 evidence-for-close-out check requires every closed FAIL to cite a test result. The `[STRUCTURAL-SAMPLE-VARIANCE]` marker on 51 of the 52 FAILs is not backed by a per-bin distribution check, an alternative-vintage spot check, or a filter re-run. The iter-2 log (`logs/log2.md` line 27-28) confirms the cheap diagnostic tests were not run within the time budget.
  - Specific fix: Either run one of the listed diagnostic tests (lag-1 ME weighting; MAX-5 spot check; rf source comparison) and log a Before/After metric, or change the marker to `[DIAGNOSE-PENDING]` and add a TODO with a concrete next-iteration fix.

- **[m3] IVOL signal is NULL on all 1.69M rows — affects Table 2 SPREAD_IVOL row.**
  - File: `data/panel_summary.json` `ivol` n_non_null = 0; `preparations/assumptions.md` Limitation 3.
  - Documented as TODO. Affects one row of Table 2 only.
  - Specific fix: Compute FF3 daily residuals via a 252-day rolling regression in ClickHouse (separate SQL or in pandas after loading daily returns) and std the residuals per (permno, month-end) into an `ivol` column. Refresh `data/panel.parquet` with the new column.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim (Table 1 P1→P10 should decline) | ✗ | T1 P1_RET_RF = 1.08, P10_RET_RF = 0.77 — directionally correct (declines), but P10 should be NEGATIVE per paper (−0.32). Sign flip on P10_RET_RF fails the monotonic claim under sign-check rules. |
| 2 | Headline-magnitude claim (Table 1 10-1 spread) | ✗ | Paper −0.95, ours −0.32. r = 0.33 — at the band-2 boundary. Combined with P10 sign flip, headline does not match. |
| 3 | Sample coverage ≥ 60% | ✓ | Panel n_rows = 1,693,841 over 637 months × 2655 stocks/month avg → ~100% coverage of stock-month universe in the panel file. Coverage at the panel level is fine; Table 6 sub-coverage (beta 2002-2022) is the gap. |
| 4 | Data-source choice justified | ✓ | CRSP, Compustat, FF factor sources match paper §3 (paper L161-191 of inputs/content.md). PS-LIQ/SY/DHS substitutions are documented as `[THIRD-PARTY-DATASET]`. Beta source change is documented in `assumptions.md` A8 with rationale. |
| 5 | prep_validation.py exit 0 | ✓ | Ran `python scripts/prep_validation.py replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to` — all present prep artifacts pass; verdict `partial` consistent with `data_verification.json`. |
| 6 | All committed tables have results files | ✗ | `results/table_1.md` and `results/table_6.md` exist. `results/table_2.md` and `results/table_9_panel_b.md` do not exist (T2 has 12 cells, T4 has 18 cells, all currently MISSING). |
| 7 | SUMMARY.md matches results/table_*.md | ✗ | SUMMARY.md (from iter 1) reports 3 of 82 Match cells; canonical scorer reports 0 of 82. Pre-existing SUMMARY.md is stale — this audit overwrites it. |
| 8 | No orphan folders | ✓ | Slug root has only `data/ eval/ inputs/ logs/ preparations/ results/ src/` — no shell-brace-expansion folders. |
| 9 | Diagnoses paired with fix attempts | ✗ | `log2.md` lines 27-29 list [M1]/[M2]/[M4] as "not pursued"; only [B1] received a fix attempt. Three diagnoses have no Before/After metric. |
| 10 | Cell status verification (re-run evaluator, diff against eval/scoring.json) | ✓ (after canonical re-run) | `python scripts/score_replication.py … --iteration 2` writes canonical `eval/scoring.json` with `match_count=0, fail_count=52, missing_count=30, skip_count=0, loss=1.0` — matches `eval/metrics.json` on `match=0, fail=52`; differs on `missing` vs `skip` (M3 above). |
| 11 | Corollary coverage | ✗ | Paper C2 (Table 2 characteristics spread) and C4 (Table 9 INST terciles) — both are entirely MISSING. C3 (MAX^beta MIS/CE spreads lower than MAX spreads) cannot be tested without T2. No corollary has a computed result in artifacts. |
| 12 | Claim coverage of committed selection | ✗ | Paper claim C1 (Table 6 headline) is covered by T3 — computed but FAIL (sign flip). C2 (Table 2) is in the table list but the table was never built — committed but not computed. C4 (Table 9) is in the table list (T4) but the table was never built — same situation. Three of four `paper_claims` have NO computed result the next iteration can score. |
| 13 | Sign conventions re-derived from paper | ✓ | Paper Table 6: 10-1 spread reported as `Portfolio 10 - Portfolio 1` excess return, expected negative per paper text (L76-78 of inputs/content.md). Replicator's `compute_long_short` uses `D_long - D_short` (src/tables.py:152-158). Sign convention matches. The sign flip is a magnitude/sign issue, not a subtraction-order bug. |
| 14 | Reporting discipline (grid completeness, claim citations, SE-less headlines) | ✗ | REPORT.md claims "directional pattern of the headline MAX effect is reproduced but magnitudes are ~3x smaller than the paper" without citing a t-stat or SE on the directional claim. The Table 6 headline in REPORT.md does not flag the sign flip (it says "T6 spread improved from −0.02 to +0.37 but sign and magnitude still disagree" — `log2.md` line 13 — but the canonical failure mode is that the spread went the wrong direction). |
| 15 | REPORT.md headline freshness (tally matches eval/scoring.json; DEV-010) | ✗ | REPORT.md line 5 cites iter-1 tally (`Match=1, FAIL=51, MISSING=0, SKIP=9, Loss L = 0.9808`). Canonical `eval/scoring.json` is iter-2 tally (`Match=0, FAIL=52, MISSING=30, SKIP=0, Loss L = 1.0000`). Stale by one iteration. [m1]. |

## 4. Issues the agent should have caught (didn't)

1. **Loss regression.** The beta aggregation fix moved Table 6 from −0.02 (sign correct, magnitude collapsed) to +0.37 (sign WRONG). The replicator's `log2.md` line 13 acknowledges "sign and magnitude still disagree" but the more precise statement is that the fix flipped the sign on the wrong side. A careful peer reviewer would run the cheap test on the same metric (compute MAX^beta P10_RET_RF with the OLD beta source vs the NEW beta source) and confirm which one matches the paper before keeping either. The iter-2 run kept the new (worse) source without a back-comparison.

2. **REPORT.md tally stale by one iteration.** DEV-010 hygiene: any change to `src/tables.py` or the panel requires re-running the canonical scorer and re-rendering REPORT.md's headline table. The iter-2 REPORT.md still has iter-1's tally line.

3. **`eval/metrics.json` legacy schema.** The replicator's evaluator (`src/evaluate.py`) writes `eval/metrics.json` in a legacy schema (key `loss_L`, no `schema_version`, no per-cell `rel_err`). The validator (`scripts/prep_validation.py`) requires the canonical `eval/scoring.json` written by `scripts/score_replication.py`. The two artifacts coexist with different numbers — the replicator could have noticed this and either updated `src/evaluate.py` to write the canonical schema, OR deleted `eval/metrics.json` entirely so the canonical scorer is the only writer.

4. **No `data/` parquet column refresh after the beta fix.** The beta fix landed in `src/sql/04_beta_monthly.sql` but `data/panel_summary.json` shows the NEW distribution (mean 1.13, std 0.98, min −4.94) — so the panel was rebuilt and the parquet was updated. But the `assumptions.md` log entry for A8 says "monthly MEAN of daily betas in [-5, 10] range" — there is no entry confirming the panel was rewritten. A careful peer reviewer would expect a `Before metric / After metric` line confirming the rebuild.

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "MAX on Steroids: A New Measure of Investor Attraction to Maximum Daily Returns" (Bali, Ince, Ozsöylev 2026) for slug `bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to`. The previous agent run completed with verdict **FAILED** (audit 2 at `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/logs/audit2.md`). Read the audit first.

## Issues to address (priority order)

### [B1] — BLOCKER — fix first

The iter-2 beta-source fix flipped Table 6's headline sign from −0.02 (iter 1, sign correct) to +0.37 (iter 2, sign WRONG; paper is −0.81). The fix changed the symptom but not the cause. Before any further changes, run a diagnostic to isolate the driver.

**Specific fix:**
1. Run a MAX-5 hand-verification spot check on a known sample month. Pick `(permno=10107, month=2010-01-31)`, query `crsp_202601.dsf` for the daily returns in January 2010, take the top-5 by `ret DESC, date ASC`, average them, and compare to `data/panel.parquet` `max_5` for the same `(permno, month)`. They should match exactly. If they don't, the MAX signal SQL is the bug. (See `src/sql/02_max_signal.sql` — the `row_number() OVER (PARTITION BY permno, month ORDER BY ret DESC, date ASC)` and `sumIf(ret, rn <= 5) / 5.0` should yield the same value as a hand-computed top-5 average.)
2. Re-run Table 6 P10_RET_RF on the 2002-2022 sample WITHOUT the `(beta_m > -2) & (beta_m < 5)` filter (`src/tables.py:265`). If removing the filter restores the negative sign, the filter is the driver; if not, the beta source is the driver.
3. Re-run Table 6 P10_RET_RF with the iter-1 beta source (`argMax(beta_mktrf, dt)`) on the same 2002-2022 sample. If the iter-1 source restores the negative sign, the iter-2 `avg(...)` aggregation convention is the driver.

Each of these is a ~10-line code change in `src/sql/04_beta_monthly.sql` or `src/tables.py:265` and a single re-run of `python src/tables.py` + `python src/evaluate.py`. Log each result in `preparations/assumptions.md` with Before/After metrics.

### [B2] — BLOCKER — fix after [B1]

The iter-2 canonical-scorer loss INCREASED from 0.9634 (iter 1) to 1.0000 (iter 2) — Match count dropped from 3 to 0 because the beta fix moved the previously-zero-band cells (T3_P5_FF5/FF6, T3_P9_RET_RF) off zero. REPORT.md still cites the iter-1 tally.

**Specific fix:**
1. After addressing [B1], re-run the canonical scorer: `python scripts/score_replication.py replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to --iteration 3`.
2. Re-render REPORT.md line 5 ("Verdict (from `eval/scoring.json`): …") and the headline tally table from canonical `eval/scoring.json` aggregates (DEV-010 hygiene). The line should reflect whatever the new iter-3 tally is, not the stale iter-1 or iter-2 numbers.
3. Add a new entry in `preparations/assumptions.md` (Diagnosis, Next fix, Before metric, After metric, Status) documenting the loss regression and the fix that addressed it.

### [B3] — BLOCKER — fix after [B1]/[B2]

Table 2 (characteristics spread, 12 cells) and Table 9 Panel B (INST-stratified MAX^beta, 18 cells) remain entirely MISSING in iter 2 — same as iter 1.

**Specific fix:**
1. For Table 9 Panel B (T4): Build institutional ownership from `instown_202601.s34` by aggregating to (permno, quarter-end) and merging to (permno, month) via the closest prior quarter-end. Form INST terciles per month, then run the three-way dependent sort: MAX decile × beta decile × INST tercile, regrouping by MAX rank across (beta, INST) bins. Output cells: 3 MAX legs × 3 INST terciles × (RET_RF + 2 alpha columns) = 27 cells; the committed scope is 18 (RET_RF + FF6PS per INST tercile). For now, build only the RET_RF columns; mark FF6PS cells as `[THIRD-PARTY-DATASET]`. The result file goes to `results/table_9_panel_b.md`.
2. For Table 2 (T2): The 12 characteristics-spread rows can be computed from the existing panel for 8 of them (MAX, BETA, BM, MOM, REV, ILLIQ, ROE — already in `data/panel.parquet`). The other 4 (IVOL, MIS, CE, INST) require additional computation; for the next iteration, at minimum compute the 8 that are already available and skip the 4 with a `[NOT-COMPUTED]` marker and a clear "next-iteration" note. Result file: `results/table_2.md`.

### [M1] — MAJOR — fix after [B1]

Table 1 magnitude gap (~3x attenuation) is still closed with a hedged causal story (`[STRUCTURAL-SAMPLE-VARIANCE]` in `preparations/assumptions.md`). The diagnostic tests listed in `assumptions.md` lines 130-150 were not run.

**Specific fix:**
1. The MAX-5 hand-verification from [B1] doubles as the T1 diagnostic. If the SQL MAX signal is wrong, fixing it will close the T1 gap simultaneously.
2. Additionally: try lag-1 ME for VW weighting. Replace `me` with `me.shift(1)` per permno in `src/tables.py:138` (or use a new column `me_lag1 = panel.groupby('permno')['me'].shift(1)`). Re-run T1 and compare P10_RET_RF. If sign flips to negative, the weighting convention is the driver.
3. Try comparing `rf3` from `ff.three_factor` against an alternative rf source — `ff.five_factor_monthly.rf` is already in the panel pipeline; re-run T1 with `ff.five_factor_monthly.rf / 100.0` and see if the spread tightens.
4. Log each variant in `assumptions.md` with Before/After metric. Replace `[STRUCTURAL-SAMPLE-VARIANCE]` with the marker that matches the actual diagnostic result (`[VINTAGE-DRIFT]`, `[CONVENTION-APPLIED]`, or open as a new [M]).

### [M2] — MAJOR — fix after [M1]

The MAX^beta sample is truncated to 2002-2022 (38% of paper's window) because `ea_oneoff.dsf_beta_252` only covers 2002-01-09 onward.

**Specific fix:**
1. Compute MAX-only P10_RET_RF on the 2002-2022 subset of the panel and compare to P10_RET_RF on the full 1968-2022 sample. This is a one-line change in `src/tables.py:390` to add `panel = panel[panel['month'] >= '2002-01-01'].copy()` before `build_decile_table`.
2. If the 2002-2022 subset has P10_RET_RF much closer to zero than the full sample, the truncation is a real driver of the T1 magnitude gap. Document in `assumptions.md` and adjust the marker on T1 cells.
3. Optionally backfill pre-2002 betas by running a daily CAPM regression on `crsp_202601.dsf` per (permno, month) and storing to a new parquet — but only if time permits; this is not required for the diagnostic.

### [M3] — MAJOR — fix in parallel with the above

The replicator's `eval/metrics.json` and canonical `eval/scoring.json` disagree on whether T4 cells are SKIP or MISSING (9 SKIP vs 30 MISSING).

**Specific fix:**
1. Pick one convention. Recommended: drop the `SKIP (T9 not built)` branch from `src/evaluate.py:134-140` and let the canonical scorer (which writes `eval/scoring.json`) be the only writer. Either delete `src/evaluate.py` or update it to write canonical `eval/scoring.json` schema (`schema_version: 3`, per-cell `rel_err`, `loss` instead of `loss_L`).
2. If T4 stays unbuilt, it is MISSING (canonical scorer convention). The `tables_to_replicate.json` `notes` field on T4 already explains why; the canonical scorer picks up `MISSING` automatically.

### [m1] — MINOR — cleanup

`REPORT.md` headline tally is stale (DEV-010). After addressing [B2], the tally will be fresh; until then, this audit's [B2] fix covers it.

### [m2] — MINOR — cleanup

`preparations/assumptions.md` lines 130-160 carry `[STRUCTURAL-SAMPLE-VARIANCE]` markers without test evidence. After [M1], replace with the marker that matches the diagnostic result.

### [m3] — MINOR — cleanup

`ivol` is NULL on all 1.69M panel rows. Compute FF3 daily residuals and add `ivol = std(residuals over 252 days per permno)` to the panel. Affects Table 2 SPREAD_IVOL row only.

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every iteration log entry in `assumptions.md` must have all five fields: Diagnosis, Next fix, Before metric, After metric, Status. A diagnosis without a Next fix is incomplete — do not move on.
- **Read `rep/STUCK_AGENT_GUIDELINE.md` on your first debug cycle.** Don't rediscover failures that are already documented.
- **10-iteration cap per problem.** Hard stop at 10 and escalate to the human. A documented partial is more valuable than a paper-claiming success that does not actually replicate.
- **Diagnoses must be paired with fix attempts (exit gate).** Before declaring `partial`, walk `assumptions.md` and verify every diagnosed problem has at least one log entry with a non-empty `Next fix` line and a before/after metric.
- **Don't retire a FAIL with hedged language.** The `[STRUCTURAL-SAMPLE-VARIANCE]` and `[VINTAGE-DRIFT]` markers require evidence. If you can't run the diagnostic in the available time budget, mark the cell `[DIAGNOSE-PENDING]` and explicitly defer — do NOT close with "most likely due to" prose.
- **The loss can regress.** The iter-1 → iter-2 loss went 0.9634 → 1.0000. Before declaring any fix a win, re-run `python scripts/score_replication.py … --iteration N+1` and confirm the canonical `loss` field is LOWER than the prior iteration's. If it's higher, the fix moved the metric farther from the paper — back out the change.

## Inputs you should read

- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/logs/audit2.md` — this audit (full context)
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/logs/audit1.md` — prior audit (B1 / M1 / M2 history)
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/inputs/content.md` — paper ground truth
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/preparations/` — prep contract (rules, tables selected, data verification, assumptions iteration log)
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/src/main.py`, `src/tables.py`, `src/evaluate.py`, `src/sql/*.sql` — current code (will be modified)
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/data/` — cached intermediates (recompute spot-checks from these)

## What NOT to redo

- Skip re-reading `SKILL.md` — the contract is the same.
- `scripts/prep_validation.py` is loop-aware (DEV-009) and safe to re-run at any point — mid-loop states no longer produce false errors. Re-run it if you changed a prep artifact; otherwise it is optional.
- Skip re-doing the clickhouse catalog scan — `data_verification.json` is current.
- **DO** re-run any sanity checks you add or modify — they are the gate that catches regressions.

## Deliverables for this iteration

- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/src/sql/04_beta_monthly.sql` and `src/tables.py` — revised with the diagnostic-tested fix from [B1]
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/results/table_1.md`, `results/table_6.md` — updated for the T1 and T6 cells
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/results/table_2.md`, `results/table_9_panel_b.md` — new for [B3]
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/preparations/assumptions.md` — append a new iteration log entry for every issue addressed (Diagnosis, Next fix, Before metric, After metric, Status)
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/SUMMARY.md` — read the latest combined assessment to understand the auditor's verdict and score; do NOT edit (the auditor owns this file)
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/REPORT.md` — updated; lead with the data-quality summary (sample period, universe size, signal mean/std vs paper, headline-magnitude comparison, table count, corollaries evaluated this iteration) and re-render the headline tally from canonical `eval/scoring.json` (DEV-010)
- After all metric-producing changes, run the canonical scorer ONCE: `python scripts/score_replication.py replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to --iteration 3`

## Stop conditions

- **All blockers fixed and verified** → re-run `scripts/prep_validation.py` and the canonical scorer → if both pass, declare success or note remaining majors in `REPORT.md`; the next audit updates `SUMMARY.md`.
- **10-iteration cap reached** on a single problem → escalate to the human and write a partial `REPORT.md`; do not edit `SUMMARY.md`.
- **All blockers fixed but majors remain** → declare partial and document the gap in `REPORT.md`. The auditor's `SUMMARY.md` verdict (REPLICATED / FAILED) is independent of this loop decision.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

The iter-2 outcome is a useful demonstration of a fix moving a metric away from the paper rather than toward it. The iter-1 Table 6 SPREAD_RET_RF of −0.02 was directionally correct (paper −0.81, sign matches) but magnitude-collapsed; the iter-2 fix pushed it to +0.37 with the wrong sign. A careful peer reviewer would have run a back-comparison before declaring the beta fix a win — the cheap test is a 5-line code change in `src/sql/04_beta_monthly.sql` (revert the aggregation to `argMax(beta_mktrf, dt)`), one re-run, and a comparison to the iter-2 numbers. The replicator did not do this back-comparison and shipped a worse result.

The 30 MISSING cells (T2 + T4) are not a fresh blocker — they were also MISSING in iter 1 — but the rubric and the bright line treat MISSING as a fail cell, so they continue to drive the concrete-result score down. The replicator's `[THIRD-PARTY-DATASET]` and `[STRUCTURAL-SAMPLE-VARIANCE]` markers are the closed-vocab mechanism for criterion-B exit, but the iter-2 log acknowledges the cheap diagnostic tests for these markers were not run within the time budget — which means the markers carry no evidence and the criterion-B exit is not earned. Documenting the gap is appropriate; exiting as partial on the basis of untested markers is not.

The pipeline engineering is sound — panel construction, universe filters, MAX signal SQL, VW sorting, Newey-West HAC, factor-model regressions all run without errors. The gap is in the methodology calibration (MAX signal vs paper's exact specification; beta source vs paper's "monthly beta over 252 days"; VW weighting convention vs paper's "lag-1 ME"). Each is a paper-silent choice where the replicator's default differs from the paper's intent. The fix is to run the cheap diagnostic tests the iter-2 log lists and let the diagnostic drive the convention, rather than guessing.
