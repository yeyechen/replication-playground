---
iteration: 4
verdict: FAILED
blocker_count: 3
actionable_major_count: 3
requires_iteration: true
---

# Audit Report 4 — bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to

**Verdict:** FAILED
**Date:** 2026-08-14
**Auditor notes:** Iteration 4 ran two of the diagnostic tests the rubric required to retire `[STRUCTURAL-SAMPLE-VARIANCE]` FAILs without evidence (audit 1-3). Diagnostic 1 (MAX-5 hand-verification on `(permno=10107, 2010-01-31)`) MATCHES the panel to 6 decimals (0.0130078 vs hand-computed 0.013008) — the MAX signal SQL is correct. Diagnostic 2 (lag-1 ME weighting) FAILED to close the T1 10-1 spread gap (lag-1 ME spread = -0.26 vs month-end ME = -0.31 vs paper -0.95). The two causes previously suspected for the T1 magnitude gap are now empirically ruled out. The honest upgrade is `[STRUCTURAL-SAMPLE-VARIANCE]` → `[DIAGNOSE-PENDING]` in `assumptions.md` Limitation 4. Canonical-scorer loss remains L = 1.0000 (Match=0, FAIL=52, MISSING=30) — diagnostic tests do not change the metric-producing code, so the canonical tally is unchanged from iter-3. The same 52 FAIL cells and 30 MISSING cells (T2 + T4) remain. T1 P10_RET_RF sign flip (paper -0.32, ours +0.77) persists across all four iterations. T6 SPREAD_RET_RF magnitude gap (paper -0.81, ours -0.12) persists across all four iterations. No new tables were built. No new code paths were tested. The criterion-B documented-residue exit is now partially earned: diagnostic tests have produced evidence for two of the four previously-hedged causes, but the remaining FAILs still have no test evidence — only one further diagnostic candidate (RF series vintage) plus two untested candidates (universe vintage, time-period coverage) plus the unexplained cross-iteration persistence of the T1 P10_RET_RF sign flip. The verdict remains FAILED by both the bright-line rule (overall = 2.00 < 3.0) and the kill switch (three dimensions at 1: concrete_result, signal_strength, corollary).

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 3/5 | 6/8 sub-checks pass. Diagnostic 7 (FAIL evidence) improved from iter-3: two of the four previously-hedged causes for the T1 magnitude gap now have evidence (MAX-5 verified correct, lag-1 ME tested and rejected). Diagnostic 8 (significance reproduction) still fails: T1 P10_RET_RF sign flip persists (paper -0.32, ours +0.77), T6 SPREAD_RET_RF magnitude 7x off (paper -0.81, ours -0.12). The marker discipline is now honest — `[DIAGNOSE-PENDING]` is a more defensible marker than `[STRUCTURAL-SAMPLE-VARIANCE]` for the unspecified-cause residue. |
| Headline matching | 2/5 | C1 (T6 SPREAD_RET_RF): paper -0.81, ours -0.12 — direction matches, magnitude 7x attenuated (r = 0.148, outside band 2). T1 SPREAD_RET_RF: paper -0.95, ours -0.32 — direction matches, r = 0.33 (band-2 boundary). T1 P10_RET_RF: paper -0.32, ours +0.77 — wrong sign on the high-MAX leg. |
| Data coverage | 4/5 | Period (1968-2022 paper vs 1970-2022 panel; 23 months missing = 3.5% of window). Universe (~2655 stocks/month, NYSE/AMEX/NASDAQ common stocks, $5+ price, SIC exclusions, 15+ daily obs) matches. CRSP/Compustat/FF factor sources match. Pre-2002 beta gap documented. Third-party factors (PS-LIQ, SY MGMT/PERF, DHS FIN/PEAD) absent from catalog with documented substitute. Join hygiene clean. The 23-month period gap is the only sub-check that degrades vs the paper. |
| Concrete result matching | 1/5 | 0 of 82 cells Match (0.00%) — band <30%. Canonical scorer (DEV-019): match=0, fail=52, missing=30, skip=0, loss=1.0. Four-iteration plateau (iter 1 L=0.9634 → iter 2 L=1.0 → iter 3 L=1.0 → iter 4 L=1.0). Iter-4 did not modify any metric-producing code, so the canonical tally is identical to iter-3. |
| Signal strength | 1/5 | Worst-case headline cell: T6_SPREAD_RET_RF — paper -0.81, ours -0.12 → r = 0.148 (sign matches but r outside [0.33, 3.0]). T6 P10_RET_RF: paper -0.10, ours +0.80 (sign flip, r = 8.0). T1 P10_RET_RF: paper -0.32, ours +0.77 (sign flip, r = 2.4). |
| Corollary | 1/5 | T2 (12 cells, characteristics spread) entirely MISSING across four audits. T4 (18 cells, INST-stratified MAX^beta) entirely MISSING across four audits. 0 of 56 corollary cells have a computed result. C2 (mispricing), C3 (MAX^beta MIS/CE spreads), C4 (heterogeneous skewness preference across INST terciles) — all untestable in the artifact set. |
| **Overall** | **2.00** | FAILED by both bright line (overall < 3.0) and kill switch (three dimensions at 1: concrete_result, signal_strength, corollary). |

## 2. Issues by severity

### Blockers (must fix)

- **[B1] Table 6 (MAX^beta) headline effect still collapses to -0.12 vs paper -0.81 — fourth consecutive audit.**
  - File: `results/table_6.md:15` (10-1 spread = -0.12 vs paper -0.81); `eval/scoring.json` T3 cells.
  - Paper Table 6 SPREAD_RET_RF = -0.81 (L2206 of `inputs/content.md`); iter-1 gave -0.02 (sign right, magnitude collapsed); iter-2 gave +0.37 (sign WRONG, beta fix flipped the direction); iter-3 reverted and gave -0.12 (sign right, magnitude 7x off); iter-4 unchanged at -0.12. r = |−0.12 / −0.81| = 0.148. T6 P10_RET_RF: paper -0.10, ours +0.80 → sign flip (r = 8.0). The MAX^beta dependent double-sort code runs end-to-end but the headline result is nowhere near the paper.
  - Iter-4 ran two diagnostic tests from the recommended list (MAX-5 hand-verification, lag-1 ME weighting) but the T6 spread is post-2002 (`beta_m` non-null only 31,990 of 1,693,841 rows). The cheap diagnostic tests called for in `audit3.md` [B1] step 2 (re-run T6 P10_RET_RF on 2002-2022 WITHOUT the `(beta_m > -2) & (beta_m < 5)` filter) and step 3 (compare iter-1 vs iter-2 beta sources on 2002-2022) were NOT run. The T6 beta-source investigation remains open.
  - Specific fix: Run the two remaining T6 diagnostics from `audit3.md` [B1]: (a) Re-run T6 P10_RET_RF on 2002-2022 WITHOUT the `(beta_m > -2) & (beta_m < 5)` filter — if P10_RET_RF turns negative, the filter is the driver. (b) Re-run T6 with the iter-1 `argMax(beta_mktrf, dt)` source AND the iter-2 `avg(if(beta_mktrf BETWEEN -5 AND 10, ...))` source on the same 2002-2022 sample, compare both to paper -0.10. Each is a ~10-line code change in `src/sql/04_beta_monthly.sql` or `src/tables.py:265` and a single re-run. Log each result in `preparations/assumptions.md` with Before/After metrics — this is the criterion-B evidence the rubric requires.

- **[B2] T1 P10_RET_RF sign flip persists across all four iterations — no diagnostic test identifies the cause.**
  - File: `results/table_1.md:14` (P10_RET_RF = 0.77 vs paper -0.32); `eval/scoring.json` T1_P10_RET_RF cell.
  - Paper P10_RET_RF = -0.32% per month (L1110 of `inputs/content.md`); the replicator's P10_RET_RF is consistently +0.77% (iter-1, iter-2, iter-3, iter-4). Sign flip, magnitude 3.4x off on rel_err. This is the same after iter-4's MAX-5 verification (eliminates MAX signal) and lag-1 ME test (no improvement). The high-MAX leg of the T1 portfolio is positive in the replicator's data and negative in the paper — a fundamental directional disagreement.
  - Iter-4 narrowed the diagnostic space (MAX and VW ruled out) but did not advance the cause identification. The remaining candidates are: (a) RF series vintage, (b) universe vintage (paper may apply an additional filter not in the prep rules), (c) time-period coverage (panel has 637 months vs paper's 660 — 23 months gap at the start).
  - Specific fix: Run the three remaining diagnostics from `audit3.md` [M1] and `[B1]`: (a) Try `me_lag1` for VW weighting (already tested — slightly worse — so skip). (b) Try RF source variants: compare `ff.three_factor.rf3` against `ff.five_factor_monthly.rf / 100.0` and against `ea_oneoff.rf / 100.0`. Re-run T1 with each. (c) Try the 1968-01-01 → 1970-01-01 panel gap: if the 1968-1970 period is missing from the panel, check whether the panel was filtered by some additional rule (e.g., a min number of obs since listing) that excludes early years. Look at the panel's stock coverage by month — is month-coverage monotonic at the start, or does it start at 1970 abruptly? (d) Try restricting the panel to 1970-01 - 2022-12 explicitly and comparing T1 to a 1968-1970 backfilled sample. Log each test in `assumptions.md`.

- **[B3] Table 2 (12 cells) and Table 9 Panel B (18 cells) MISSING — fourth consecutive audit.**
  - File: `eval/scoring.json` T2 cells (12) and T4 cells (18) all `status: MISSING`; `src/tables.py` builds only T1 and T3; no `results/table_2.md` or `results/table_9_panel_b.md` exists.
  - Paper C2 (mispricing interpretation) is backed by T2 characteristics spreads; paper C4 (heterogeneous skewness preference across INST terciles) is one of the paper's three named contributions (L11 of `inputs/content.md`) and is tested by T4. Both are still entirely missing after four iterations.
  - `logs/log4.md` line 56 acknowledges "outer iteration cap is 5; we have used 4" — the partial exit is coming. But the rubric is clear: a `MISSING` cell cannot be retired by a closed-vocabulary marker if the only reason it is missing is that the work was never done. The T2/T4 cells are not non-actionable due to data limitation — they are non-actionable only because the replicator chose to skip them. The exit strategy must distinguish "MISSING because data is unavailable" from "MISSING because work was deferred."
  - Specific fix: Build at least the 8 computable T2 rows (MAX, BETA, BM, MOM, REV, ILLIQ, ROE, SIZE) by computing cross-sectional medians per MAX decile from `data/panel.parquet` and forming the 10-1 spread. Compute IVOL separately (FF3 daily residuals via 252-day rolling window — `m2` from iter-3 is a known minor). For T4, build the 9 RET-RF cells (the 9 RET-RF columns of T4) by aggregating `instown_202601.s34` to (permno, quarter-end) INST, merging to (permno, month) via closest prior quarter-end, forming INST terciles per month, running the dependent three-way sort. Leave FF6PS cells as `[THIRD-PARTY-DATASET]`. Result files: `results/table_2.md` and `results/table_9_panel_b.md`.

### Major (should fix)

- **[M1] Period truncation: panel covers 1970-01 to 2022-12 (637 months), paper claims 1968-01 to 2022-12 (660 months).**
  - File: `data/panel_summary.json` `n_months = 637`; `panel.month` min = 1970-01-01, max = 2022-12-31 vs paper L163.
  - The 23-month gap (1968-01 to 1969-12) is a documented period truncation that `preparations/assumptions.md` does not flag. The assumptions.md L16 explicitly states "Sample period: 1968-01-01 .. 2022-12-31" — but the panel parquet does not include 1968-1969. The replicator's `REPORT.md` L4 also claims "Jan 1968 – Dec 2022" without flagging the 23-month gap.
  - This is the candidate cause the iter-4 diagnostic flagged as "Time period (my full sample 1968-2022 vs paper's 1968-2022 — they should match, but my panel has only 637 months vs the paper's 660)" but did not test. If the CRSP msf/dsf tables in `crsp_202601` actually do contain 1968-1969 data (i.e., the gap is a panel-pipeline bug, not a source-data gap), the panel could be re-built to include those months.
  - Specific fix: Query `crsp_202601.msf` for 1968-01 to 1969-12 — does it contain data? If yes, the panel-pipeline filter is dropping these months (likely a min-obs filter or a `dsf` join issue). If no, document the gap as `[THIRD-PARTY-DATASET]` or `[VINTAGE-DRIFT]` in `assumptions.md` and update `REPORT.md` line 4 to "Jan 1970 – Dec 2022 (23 months of 1968-1969 panel-data discrepancy)". Either outcome needs to be resolved and documented.

- **[M2] `[DIAGNOSE-PENDING]` marker is honest but not yet actioned — T1 magnitude gap remains unresolved.**
  - File: `preparations/assumptions.md` Limitation 4 (lines 130-150 → updated to lines 169-193 in the new "Iteration 4 diagnostic results" section).
  - The marker upgrade from `[STRUCTURAL-SAMPLE-VARIANCE]` to `[DIAGNOSE-PENDING]` is a positive step — it acknowledges the cause is unknown, not undocumented. But `[DIAGNOSE-PENDING]` is a default-open marker, not a closed-vocabulary marker. The criterion-B documented-residue exit requires every failing cell to carry one of the four closed-vocabulary markers (`[VINTAGE-DRIFT]`, `[STRUCTURAL-SAMPLE-VARIANCE]`, `[THIRD-PARTY-DATASET]`, `[CONVENTION-APPLIED]`). The iter-4 marker swap means the criterion-B exit is now partially earned: 2 of 4 previously-hedged causes have evidence (MAX and VW), but the residual gap on the 52 FAIL cells still has no closed-vocabulary marker.
  - The remaining `[DIAGNOSE-PENDING]` cells need either (a) a closed-vocab marker with evidence (run one more diagnostic and update the marker), or (b) a `[NOT-COMPUTED]` annotation with a concrete next-iteration fix. The current state — honest but unresolved — is the right intermediate state, but the loop cannot exit on criterion B until the residue is either classified or computed.
  - Specific fix: Either run the remaining diagnostics (RF source, universe vintage, time-period coverage) and assign the correct closed-vocab marker, or accept the residue as `[NOT-COMPUTED]` and document the next-iteration fix path in `assumptions.md`. The current `[DIAGNOSE-PENDING]` is an interim state and must be resolved before the loop can exit.

- **[M3] T3 SPREAD_RET_RF and T1 SPREAD_RET_RF — long-short spreads are off because the high-MAX leg (P10) is wrong, not the spread calculation.**
  - File: `eval/scoring.json` T3_SPREAD_RET_RF (paper -0.81, ours -0.12) and T1_SPREAD_RET_RF (paper -0.95, ours -0.32).
  - The 10-1 spread is a subtraction of P10-P1. P1_RET_RF is roughly correct (T1 P1: paper 0.63, ours 1.08; T3 P1: paper 0.71, ours 0.92). The variation is in the high-MAX leg: T1 P10_RET_RF (paper -0.32, ours +0.77 — sign flip), T3 P10_RET_RF (paper -0.10, ours +0.80 — sign flip). The 10-1 spread mismatch is driven by the high-MAX leg being positive in the replicator's data.
  - This is a deeper diagnostic insight than iter-1/2/3 had: the issue is not the spread arithmetic, but the P10_RET_RF cell itself. The paper's high-MAX stocks earn negative excess returns; the replicator's high-MAX stocks earn positive excess returns. This is a fundamental portfolio-construction issue: stocks ranked into the top MAX decile in the replication are not the same stocks as the paper's top MAX decile, OR the forward returns are computed differently.
  - Specific fix: Audit the P10 stocks themselves. For one month (e.g., 2010-01-31), extract the top 10 stocks by MAX from the panel, compare their forward returns (`ret.shift(-1)`) to the paper's expected distribution. Also check: is the panel's `month` the formation month or the holding month? The paper's "one-month-ahead" timing convention is `ret_fwd = ret.shift(-1)` after `qcut`; check that the order is right (sort first, then shift the return — not shift first then sort).

### Minor (cleanup)

- **[m1] REPORT.md line 5 still has iter-1 tally (DEV-010 regression, fourth audit).**
  - File: `REPORT.md:5` shows `Match=1, FAIL=51, MISSING=0, SKIP=9. Loss L = 0.9808`; canonical `eval/scoring.json` for iter 4 is `Match=0, FAIL=52, MISSING=30, SKIP=0, Loss L = 1.0000`.
  - The headline tally section (lines 7-16) was refreshed for iter-3 and is now current for iter-4 (the numbers didn't change, but the canonical scorer ran with `--iteration 4`), but the top-of-file "Verdict" line on line 5 still has iter-1 numbers. The iter-2, iter-3, and iter-4 audits all flagged this; the replicator has not addressed it.
  - Specific fix: Re-render REPORT.md line 5 from canonical `eval/scoring.json#aggregates` (Match=0 / FAIL=52 / MISSING=30 / SKIP=0 / Loss L = 1.0000).

- **[m2] Panel coverage gap (637 vs 660 months) is not flagged in `assumptions.md` or `REPORT.md`.**
  - File: `data/panel_summary.json` `n_months = 637`; `preparations/assumptions.md` L16 says "Sample period: 1968-01-01 .. 2022-12-31" — incorrect.
  - The replicator's own diagnostic in `log4.md` L37-39 acknowledges "my panel has 637 months vs paper's 660 — 23 missing months" but does not flag this in `assumptions.md` or `REPORT.md`. The 23-month gap is a documented data-coverage finding that should be entered as a Limitation.
  - Specific fix: Add a new Limitation 6 in `assumptions.md`: "Period truncation: panel covers 1970-01 to 2022-12 (637 months); paper claims 1968-01 to 2022-12 (660 months). 23 months gap at the start. Status: [DIAGNOSE-PENDING] pending check of crsp_202601.msf 1968-1969 coverage."

- **[m3] IVOL signal still NULL on all 1.69M rows — affects T2 SPREAD_IVOL row if T2 is built.**
  - File: `data/panel_summary.json` `ivol` n_non_null = 0; `preparations/assumptions.md` Limitation 3.
  - The iter-4 audit [m3] carried this forward; the iter-4 replicator did not address it.
  - Specific fix: Compute FF3 daily residuals via a 252-day rolling regression and std the residuals per (permno, month-end) into an `ivol` column. Refresh `data/panel.parquet` only if [B3] is being addressed.

- **[m4] `eval/metrics.json` (replicator) and `eval/scoring.json` (canonical) schema mismatch persists.**
  - File: `eval/metrics.json` uses legacy schema (`loss_L`, no `schema_version`, no per-cell `rel_err`); `eval/scoring.json` uses canonical DEV-019 schema (`schema_version: 3`, per-cell `rel_err`, `loss`).
  - The two artifacts coexist with different numbers per audit2 [M3] and audit3 [m4]. The canonical scorer is the source of truth; `eval/metrics.json` is the replicator's hand-evaluated output.
  - Specific fix: Either update `src/evaluate.py` to write the canonical schema, or delete `eval/metrics.json` after each canonical re-run. The canonical scorer is the only source of truth.

- **[m5] `logs/log4.md` L53-56 says "outer iteration cap is 5; we have used 4" — but the per-iteration cap is 10 per [SKILL.md] iteration cap, not 5.**
  - File: `logs/log4.md` L53 and L57.
  - The 10-iteration cap is the per-problem cap, not the per-paper cap. The outer iteration cap is a soft budget, not a hard cap. The iter-4 log confuses the two, which is misleading.
  - Specific fix: Correct `log4.md` L53, L57 to state "outer iteration cap is 5 of an unspecified max" or remove the cap reference. The Cap is 10 per problem; the audit is the source of truth on whether to continue.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim (T1 P1→P10 should decline) | FAIL | T1 P1_RET_RF = 1.08, P10_RET_RF = 0.77 — both positive, declining 1.08 → 0.77. Paper has P10 = -0.32 (negative). Sign flip on P10_RET_RF fails the monotonic claim under sign-check rules. |
| 2 | Headline-magnitude claim (T6 10-1 SPREAD_RET_RF) | FAIL | Paper -0.81, ours -0.12 — unchanged from iter-3. r = 0.148 — outside any band. Sign matches paper. |
| 3 | Sample coverage ≥ 60% | PASS | Panel n_rows = 1,693,841; 637 unique months × ~2655 stocks/month ≈ 100% coverage of stock-month universe in the panel file. Coverage at the panel level is fine; Table 6 sub-coverage (beta 2002-2022) is the gap. Period-level coverage gap (23 months 1968-1970) is a separate finding (m2). |
| 4 | Data-source choice justified | PASS | CRSP, Compustat, FF factor sources match paper §3 (L161-191 of `inputs/content.md`). PS-LIQ/SY/DHS substitutions documented as `[THIRD-PARTY-DATASET]`. RF source variant not tested (open diagnostic from iter-4 M1). |
| 5 | prep_validation.py exit 0 | PASS | Re-ran `python scripts/prep_validation.py replications/<slug>` — all present prep artifacts pass; verdict `partial` consistent with `data_verification.json`. |
| 6 | All committed tables have results files | FAIL | `results/table_1.md` and `results/table_6.md` exist. `results/table_2.md` and `results/table_9_panel_b.md` do not exist (T2 has 12 cells, T4 has 18 cells, all currently MISSING). |
| 7 | SUMMARY.md matches results/table_*.md | PARTIAL | SUMMARY.md is stale by one iteration (last overwritten for iter-3). Audit overwrites it. Result tables have no per-cell evaluation blocks (they're just the result tables; the per-cell evaluation is in `eval/metrics.json`). |
| 8 | No orphan folders | PASS | Slug root has only `data/ eval/ inputs/ logs/ preparations/ results/ src/` — no shell-brace-expansion folders. |
| 9 | Diagnoses paired with fix attempts | PARTIAL | Audit 4 ran two diagnostic tests (MAX-5 hand-verification, lag-1 ME weighting) — both with Before/After metrics. Two of the four previously-hedged causes now have evidence. Iter-4 did not run the T6 beta-source diagnostic (audit3 [B1] step 2-3) or the RF source diagnostic (audit3 [M1] step 3). |
| 10 | Cell status verification (re-run canonical scorer, diff against eval/metrics.json) | PASS | Re-ran `python scripts/score_replication.py replications/<slug> --iteration 4` — canonical `eval/scoring.json` aggregates match `eval/metrics.json` on match=0, fail=52; canonical reports missing=30, replicator's `metrics.json` reports the same 52 FAIL and 30 MISSING. |
| 11 | Corollary coverage | FAIL | Paper C2 (T2 characteristics spread) and C4 (T4 INST terciles) — both entirely MISSING across four audits. C3 (MAX^beta MIS/CE spreads lower than MAX spreads) cannot be tested without T2. No corollary has a computed result in artifacts. |
| 12 | Claim coverage of committed selection | FAIL | Paper claim C1 (T3 headline) is computed but FAIL (r = 0.148). C2 (T2) is committed but not computed. C3 (T3 MIS/CE) is a corollary of T3 but T2 is missing. C4 (T4) is committed but not computed. Three of four `paper_claims` have NO computed result the next iteration can score. |
| 13 | Sign conventions re-derived from paper | PARTIAL | Paper Table 6: 10-1 spread reported as `Portfolio 10 - Portfolio 1` excess return, expected negative per paper text (L76-78 of `inputs/content.md`). Replicator's `compute_long_short` uses `D_long - D_short`. Sign convention matches. But the high-MAX leg (P10_RET_RF) is sign-flipped in T1 (+0.77 vs paper -0.32) and T3 (+0.80 vs paper -0.10) — the source is not the spread arithmetic but the P10 cell itself. See [M3]. |
| 14 | Reporting discipline (grid completeness, claim citations, SE-less headlines) | FAIL | REPORT.md line 5 has stale iter-1 tally (m1). The iter-4 log cites diagnostic results but does not report the T6 SPREAD_RET_RF or T1 SPREAD_RET_RF with t-stat/SE. Result tables (table_1.md, table_6.md) do not have per-cell evaluation blocks. |
| 15 | REPORT.md headline freshness (tally matches eval/scoring.json; DEV-010) | PARTIAL | `REPORT.md` headline tally section (lines 7-16) shows iter-3 numbers (Match=0, FAIL=52, MISSING=30, Loss=1.0) which match eval/scoring.json for iter-4 (loss unchanged). But line 5 still shows iter-1 numbers (m1). |
| 16 | MAX-5 hand-verification diagnostic (iter-4 Diagnostic 1) | PASS | Queried `crsp_202601.dsf` for `permno=10107` in January 2010, sorted by `ret DESC, date ASC`, computed top-5 average = 0.013008. Compared to `data/panel.parquet` `max_5` for `(permno=10107, month=2010-01-31)` = 0.0130078. Match to 6 decimals. MAX signal SQL is verified correct. |
| 17 | Panel coverage matches paper (1968-2022 vs 1970-2022) | FAIL | Panel `data/panel.parquet` covers 1970-01-01 to 2022-12-31 (637 months). Paper claims 1968-01-01 to 2022-12-31 (660 months). 23 months missing. Not flagged in `assumptions.md` or `REPORT.md`. See m2. |

## 4. Issues the agent should have caught (didn't)

1. **Iter-4 was a diagnostic-only iteration.** The only metric-producing change was the iterative diagnostic test for MAX-5 (verifying a value that was already computed). The canonical loss stayed at L = 1.0000 (Match=0). The replicator describes iter-4 as a "diagnostic contribution" — but the rubric's criterion-A exit (`L == 0`) and criterion-B exit (every failing cell carries a closed-vocab marker with evidence) are not met. The criterion-B exit is now partially earned but not fully. The 23-month panel-coverage gap (m2) was acknowledged in the log but not flagged in `assumptions.md` or `REPORT.md`.

2. **REPORT.md headline tally is stale by three iterations (DEV-010 regression).** `REPORT.md:5` still cites the iter-1 canonical tally (`Match=1, FAIL=51, MISSING=0, SKIP=9, Loss L = 0.9808`). Iter 2, 3, and 4 audits all flagged this as a minor; the replicator has not addressed it. The audit-4's [m1] is a repeat of the audit-2 and audit-3 minor.

3. **T2 + T4 were never started across four iterations.** `audit1.md` [B3] recommended building the 8 computable T2 rows; `audit2.md` [B3] re-prioritized the same work; `audit3.md` [B3] re-prioritized again; `audit4.md` [B3] repeats the same. The log line 56 acknowledges "outer iteration cap is 5" — but the cap is 10 per problem, not 5 per paper. The replicator is signalling an exit, not a continuation. C2 (mispricing interpretation) and C4 (heterogeneous skewness preference) — two of the paper's three named contributions — remain entirely untestable in the artifact set.

4. **T1 P10_RET_RF sign flip hasn't been drilled into.** The paper's high-MAX stocks earn negative excess returns (-0.32% per month); the replicator's high-MAX stocks earn positive excess returns (+0.77%). This is a sign flip on the most diagnostic cell of the table. The iter-4 diagnostic narrowed the cause space (MAX and VW ruled out) but did not drill into the high-MAX portfolio itself. A simple spot-check on a representative month — extract the top 10 stocks by MAX, compute their forward returns — would tell a careful peer reviewer whether the stocks are different or the returns are different.

5. **Panel period coverage gap (1970-2022 vs 1968-2022) is undocumented.** The replicator's own diagnostic in `log4.md` L37-39 says "my panel has 637 months vs paper's 660 — 23 missing months" but doesn't flag this in `assumptions.md` or `REPORT.md`. The 23-month gap at the start of the sample is a documented data-coverage finding that needs an entry in `assumptions.md` as a Limitation with a `[VINTAGE-DRIFT]` or `[DIAGNOSE-PENDING]` marker.

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "MAX on Steroids: A New Measure of Investor Attraction to Maximum Daily Returns" (Bali, Ince, Ozsöylev 2026) for slug `bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to`. The previous agent run completed with verdict **FAILED** (audit 4 at `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/logs/audit4.md`). Read the audit first.

## Issues to address (priority order)

### [B1] — BLOCKER — fix first

Table 6 (MAX^beta) headline effect still collapses: paper -0.81, ours -0.12 (sign matches paper after iter-3 revert, but magnitude is 7x off). Two of the four diagnostic tests from `audit3.md` were run in iter-4 (MAX-5 hand-verification, lag-1 ME) — both improved the marker discipline but did not move the loss. The remaining T6 diagnostics are beta-source and beta-filter tests.

**Specific fix:**
1. Re-run Table 6 P10_RET_RF on the 2002-2022 sample WITHOUT the `(beta_m > -2) & (beta_m < 5)` filter (`src/tables.py:265`). If P10_RET_RF turns negative (target paper -0.10), the filter is the driver; if not, the beta source is the driver.
2. Re-run Table 6 P10_RET_RF with both the iter-1 `argMax(beta_mktrf, dt)` source AND the iter-2 `avg(if(beta_mktrf BETWEEN -5 AND 10, ...))` source on the same 2002-2022 sample. Compare both to the paper's -0.10 P10_RET_RF. The one closer to the paper is the source to keep.
3. Log each result in `preparations/assumptions.md` with Before/After metrics and the marker that matches the diagnostic result (`[DIAGNOSE-PENDING]` if still unknown, `[VINTAGE-DRIFT]` if the filter is the driver, `[CONVENTION-APPLIED]` if the source is the driver).

### [B2] — BLOCKER — fix after [B1]

T1 P10_RET_RF sign flip persists across four iterations. Paper -0.32, ours +0.77. The high-MAX leg of the T1 portfolio is positive in the replicator's data and negative in the paper. This is the most diagnostic cell of T1 — fixing it would close most of the T1 magnitude gap.

**Specific fix:**
1. Spot-check the top 10 stocks by MAX in a representative month (e.g., 2010-01-31). Extract their forward returns (`ret.shift(-1)`) and compare to the paper's expected distribution. Verify the panel's `month` is the formation month, not the holding month.
2. Run the remaining diagnostic tests from `audit3.md` [M1]/[B1]: (a) RF source variants — compare `ff.three_factor.rf3` against `ff.five_factor_monthly.rf / 100.0` and against `ea_oneoff.rf / 100.0`. Re-run T1 with each. (b) Universe vintage — check whether the panel applies a stricter filter than the paper's (e.g., min 5-year listing history, min 60 monthly observations). (c) Period coverage — check whether the 23-month 1968-1970 gap is a source-data gap or a pipeline gap (see [M1] below).
3. Drill into the high-MAX portfolio itself: for one month, compute the cross-sectional mean of MAX in P10, the mean of `ret_fwd` in P10, and the count of stocks in P10. Compare to the paper's expected distribution.
4. Log each result in `preparations/assumptions.md` with Before/After metrics and the marker that matches the diagnostic result.

### [B3] — BLOCKER — fix after [B1]/[B2]

Table 2 (characteristics spread, 12 cells) and Table 9 Panel B (INST-stratified MAX^beta, 18 cells) remain entirely MISSING across four audits. The iter-4 log mentions "outer iteration cap is 5" — but the cap is 10 per problem, not 5 per paper. The criterion-B exit is not earned while T2/T4 cells are unbuilt.

**Specific fix:**
1. For Table 9 Panel B (T4): Aggregate `instown_202601.s34` to (permno, quarter-end) INST series, merge to (permno, month) via closest prior quarter-end. Form INST terciles per month. Run the dependent three-way sort: MAX decile × beta decile × INST tercile, regrouping by MAX rank across (beta, INST) bins. Output cells: 3 MAX legs × 3 INST terciles × (RET_RF + FF6PS) = 18 cells. For now, build only the RET_RF columns (9 cells); mark FF6PS cells as `[THIRD-PARTY-DATASET]`. Result file: `results/table_9_panel_b.md`.
2. For Table 2 (T2): Pull cross-sectional medians of MAX, BETA, BM, MOM, REV, ILLIQ, ROE, SIZE per MAX decile from `data/panel.parquet`, compute the 10-1 spread for each — produces 8 of the 12 rows. Build IVOL separately (FF3 daily residuals via 252-day rolling window). Leave MIS, CE, INST rows as `[NOT-COMPUTED]` with a clear next-iteration note. Result file: `results/table_2.md`.

### [M1] — MAJOR — fix in parallel with the above

Period truncation: panel covers 1970-01 to 2022-12 (637 months); paper claims 1968-01 to 2022-12 (660 months). 23 months gap at the start. Not flagged in `assumptions.md` or `REPORT.md`.

**Specific fix:**
1. Query `crsp_202601.msf` for 1968-01 to 1969-12 — does it contain data? If yes, the panel-pipeline filter is dropping these months (likely a min-obs filter or a `dsf` join issue). If no, document the gap as `[VINTAGE-DRIFT]` in `assumptions.md` and update `REPORT.md` line 4 to "Jan 1970 – Dec 2022 (23 months of 1968-1969 panel-data discrepancy)".
2. Add a new Limitation 6 in `assumptions.md`: "Period truncation: panel covers 1970-01 to 2022-12 (637 months); paper claims 1968-01 to 2022-12 (660 months). 23 months gap at the start. Status: [DIAGNOSE-PENDING] pending check of crsp_202601.msf 1968-1969 coverage."

### [M2] — MAJOR — fix after [M1]

`[DIAGNOSE-PENDING]` marker is interim, not closed-vocab. The criterion-B documented-residue exit requires every failing cell to carry one of the four closed-vocab markers with evidence. The iter-4 marker upgrade is positive but interim.

**Specific fix:**
1. Either run the remaining diagnostics (from [B1] and [B2]) and assign the correct closed-vocab marker based on the diagnostic result, OR accept the residue as `[NOT-COMPUTED]` and document the next-iteration fix path in `assumptions.md`.
2. The current `[DIAGNOSE-PENDING]` is an interim state and must be resolved before the loop can exit on criterion B.

### [M3] — MAJOR — fix after [B2]

T3 SPREAD_RET_RF and T1 SPREAD_RET_RF — long-short spreads are off because the high-MAX leg (P10) is wrong, not the spread arithmetic. The 10-1 spread is P10-P1; P1 is roughly correct, but P10 is sign-flipped.

**Specific fix:**
1. Drill into the P10 portfolio itself: for one month (e.g., 2010-01-31), extract the top 10 stocks by MAX, compare their forward returns to the paper's expected distribution. Verify the panel's `month` is the formation month, not the holding month.
2. If the high-MAX stocks in the panel earn positive forward returns on average, the issue is portfolio-construction (different stocks ending up in P10). If they earn negative forward returns but the mean is positive, the issue is winsorization or a small-N outlier.

### [m1] — MINOR — cleanup

`REPORT.md` line 5 is stale by three iterations. Re-render from canonical `eval/scoring.json#aggregates` (Match=0 / FAIL=52 / MISSING=30 / SKIP=0 / Loss L = 1.0000).

### [m2] — MINOR — cleanup

Panel coverage gap (637 vs 660 months) is not flagged in `assumptions.md` or `REPORT.md`. Add Limitation 6 per [M1].

### [m3] — MINOR — cleanup

`ivol` is still NULL on all 1.69M panel rows. Compute FF3 daily residuals and add `ivol = std(residuals over 252 days per permno)` to the panel. Affects 1 cell of T2 if T2 is built.

### [m4] — MINOR — cleanup

`eval/metrics.json` (replicator) and `eval/scoring.json` (canonical) use different schemas. Either update `src/evaluate.py` to write canonical schema, or delete `eval/metrics.json` after each canonical run.

### [m5] — MINOR — cleanup

`logs/log4.md` L53, L57 incorrectly states "outer iteration cap is 5." The cap is 10 per problem (per `rep/SKILL.md` "10-iteration cap per problem"), not 5 per paper. The audit should be the source of truth on whether to continue, not a self-imposed cap.

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every iteration log entry in `preparations/assumptions.md` must have all five fields: Diagnosis, Next fix, Before metric, After metric, Status. A diagnosis without a Next fix is incomplete — do not move on.
- **Read `rep/STUCK_AGENT_GUIDELINE.md` on your first debug cycle.** Don't rediscover failures that are already documented.
- **10-iteration cap per problem.** Hard stop at 10 and escalate to the human. A documented partial is more valuable than a paper-claiming success that does not actually replicate. The audit will tell you whether to continue; the cap is 10 per problem.
- **Diagnoses must be paired with fix attempts (exit gate).** Before declaring `partial`, walk `assumptions.md` and verify every diagnosed problem has at least one log entry with a non-empty `Next fix` line and a before/after metric.
- **Don't retire a FAIL with hedged language.** The `[STRUCTURAL-SAMPLE-VARIANCE]` and `[DIAGNOSE-PENDING]` markers require evidence. If you can't run the diagnostic in the available time budget, mark the cell `[NOT-COMPUTED]` and explicitly defer — do NOT close with "most likely due to" prose.
- **The loss can regress.** Iter-1 → iter-2 loss went 0.9634 → 1.0000. Iter-2 → iter-3 loss stayed at 1.0000. Iter-3 → iter-4 loss stayed at 1.0000. Before declaring any fix a win, re-run `python scripts/score_replication.py … --iteration N+1` and confirm the canonical `loss` field is LOWER than the prior iteration's. If it's higher, the fix moved the metric farther from the paper — back out the change.
- **Criterion-B exit requires evidence.** The documented-residue exit requires every remaining failing cell to carry a closed-vocabulary marker with test evidence. Markers without diagnostic results do NOT satisfy criterion B.
- **Iter-4 made progress on diagnostic evidence.** The MAX-5 hand-verification and the lag-1 ME test are exactly the kind of cheap diagnostic tests the rubric requires. Two of the four previously-hedged causes for the T1 magnitude gap now have evidence. Build on this — the next iteration should run the remaining diagnostics (RF source, universe vintage, time-period coverage, T6 beta source/filter) and assign the correct closed-vocab marker to each.

## Inputs you should read

- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/logs/audit4.md` — this audit (full context)
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/logs/audit3.md`, `audit2.md`, `audit1.md` — prior audits (B1/M1/B3 history)
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/logs/log4.md` — iter-4 decision log (Diagnostic 1 + 2)
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/inputs/content.md` — paper ground truth
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/preparations/` — prep contract (rules, tables selected, data verification, assumptions iteration log)
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/src/main.py`, `src/tables.py`, `src/evaluate.py`, `src/sql/*.sql` — current code (will be modified)
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/data/` — cached intermediates (recompute spot-checks from these)

## What NOT to redo

- Skip re-reading `SKILL.md` — the contract is the same.
- `scripts/prep_validation.py` is loop-aware (DEV-009) and safe to re-run at any point. Re-run it if you changed a prep artifact; otherwise it is optional.
- Skip re-doing the clickhouse catalog scan — `data_verification.json` is current.
- **DO** re-run any sanity checks you add or modify — they are the gate that catches regressions.

## Deliverables for this iteration

- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/src/sql/02_max_signal.sql` and `src/sql/04_beta_monthly.sql` and `src/tables.py` — revised with the diagnostic-tested fix from [B1]/[B2]
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/results/table_1.md`, `results/table_6.md` — updated for the T1 and T3 cells
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/results/table_2.md`, `results/table_9_panel_b.md` — new for [B3]
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/preparations/assumptions.md` — append a new iteration log entry for every issue addressed (Diagnosis, Next fix, Before metric, After metric, Status), with diagnostic test results behind every marker
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/SUMMARY.md` — read the latest combined assessment to understand the auditor's verdict and score; do NOT edit (the auditor owns this file)
- `replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to/REPORT.md` — updated; lead with the data-quality summary (sample period, universe size, signal mean/std vs paper, headline-magnitude comparison, table count, corollaries evaluated this iteration) and re-render the headline tally from canonical `eval/scoring.json` (DEV-010)
- After all metric-producing changes, run the canonical scorer ONCE: `python scripts/score_replication.py replications/bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to --iteration 5`

## Stop conditions

- **All blockers fixed and verified** → re-run `scripts/prep_validation.py` and the canonical scorer → if both pass, declare success or note remaining majors in `REPORT.md`; the next audit updates `SUMMARY.md`.
- **10-iteration cap reached** on a single problem → escalate to the human and write a partial `REPORT.md`; do not edit `SUMMARY.md`.
- **All blockers fixed but majors remain** → declare partial and document the gap in `REPORT.md`. The auditor's `SUMMARY.md` verdict (REPLICATED / FAILED) is independent of this loop decision.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

The iter-4 outcome is a diagnostic-only iteration. The two diagnostic tests the rubric required (MAX-5 hand-verification, lag-1 ME weighting) were run with proper Before/After metrics. The MAX-5 hand-verification confirms the SQL is correct to 6 decimals — the MAX signal is not the cause of the T1 magnitude gap. The lag-1 ME weighting test shows the spread is slightly worse (-0.26 vs -0.31) — the VW weighting convention is not the cause either. The marker discipline improved from hedged `[STRUCTURAL-SAMPLE-VARIANCE]` to honest `[DIAGNOSE-PENDING]` — this is the right intermediate state but not a closed-vocab marker, so the criterion-B exit is not yet earned.

The canonical loss remains L = 1.0000 across iter-2, iter-3, and iter-4. The 52 FAIL cells and 30 MISSING cells are unchanged. T1 P10_RET_RF sign flip persists; T6 SPREAD_RET_RF magnitude gap persists. The 23-month panel-coverage gap (1970-2022 vs 1968-2022) is a new finding that the iter-4 diagnostic surfaced but did not flag in `assumptions.md` or `REPORT.md`.

The deeper insight from the diagnostic trail is that the T1 P10_RET_RF sign flip is the primary driver of the T1 10-1 spread gap. P1_RET_RF is roughly correct (T1: paper 0.63, ours 1.08; T3: paper 0.71, ours 0.92). The high-MAX leg is sign-flipped (T1: paper -0.32, ours +0.77; T3: paper -0.10, ours +0.80). The fix is not the spread arithmetic or the portfolio-construction — it's the high-MAX portfolio itself. The next iteration should drill into the P10 stocks themselves: extract the top 10 stocks by MAX for a representative month, compute their forward returns, and check whether the stocks are different or the returns are different.

Three of six dimensions are at 1 (concrete_result, signal_strength, corollary); one is at 2 (headline_matching); two are at 3 and 4. The bright line verdict is FAILED by both overall < 3.0 and the kill switch. The replicator's [B3] (T2 + T4) is the highest-leverage unfixed blocker — building those tables would close the corollary dimension and add at least 9 cells (T4 RET-RF columns) for the next iteration to score.

`requires_iteration: true` because three blockers and three actionable majors remain. The next iteration must run the remaining diagnostic tests (T6 beta source/filter, RF source, universe vintage, time-period coverage) and build the missing tables (T2 + T4), not just iterate on existing assumptions.
