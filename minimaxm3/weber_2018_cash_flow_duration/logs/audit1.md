---
iteration: 1
verdict: FAILED
blocker_count: 1
actionable_major_count: 6
requires_iteration: true
---

# Audit Report 1 — weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns

**Verdict:** FAILED
**Date:** 2026-08-14
**Auditor notes:** The replication reproduces the headline D1-D10 spread in the right direction and with statistical significance, but at 44% of the paper's magnitude. The FF5 alpha flips sign (a critical supporting cell for claim C2), the IOR construction is off by ~3.5× (propagating into the RIOR Table 10 spread), the PR sign disagrees with the paper, and the right-tail deciles (D8-D10) carry the wrong excess-return pattern. Concrete-match rate 32.4% falls in band 2; corollary-match rate ~21% falls in band 1 and trips the kill switch. The replication is a documented partial — direction preserved, magnitude and corollary claims substantially short of the paper.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 4 | 7 of 8 sub-checks pass; deviations (seed clips, P_t=ME, no Cohen prorate, no Moody's supplement) are documented with paper citations and quantitative evidence. Sub-check 8 (inference reproduction) is partial: headline t-stat reproduced, but most supporting cells lack t-stat reproduction. |
| Headline matching | 3 | D1-D10 spread +0.49% vs paper +1.10% — sign correct, rough shape, magnitude drift ~56% (band 3: 25-50% drift; this drifts just past the upper edge). |
| Data coverage | 4 | Period exact (Jul 1963-Jun 2014, 612 months); IOR subsample exact (1981-2013); no duplicates on join keys; documented CRSP/Compustat/FF/13F substitutions; Moody's BE supplement and Baker-Wurgler sentiment acknowledged as missing. |
| Concrete result matching | 2 | 23 Match / 48 FAIL / 6 MISSING / 0 SKIP. Match rate 32.4% — band 2 (30-50%). |
| Signal strength | 2 | Worst-case headline r = |0.489 / 1.10| = 0.4445 — band 2 ([0.33, 0.5), sign matches). CAPM alpha r = 0.526; Sharpe r = 0.482. |
| Corollary | 1 | Corollary match rate = 12 / 57 = 21.0% — band 1 (<25%). |

Mean = (4 + 3 + 4 + 2 + 2 + 1) / 6 = 2.67. Verdict is FAILED by bright line (overall < 3.0) AND by kill switch (Corollary = 1).

## 2. Issues by severity

### Blockers (must fix)

- [B1] `eval/metrics.json` schema violation. The `evaluate.py` writes `"value": null` for the 6 T5 per-decile D1/D10 means that the pipeline never computes. The validator (`scripts/prep_validation.py`) reports `6 metric(s) have non-numeric 'value'` and exits non-zero. This is a hygiene blocker the replicator can fix in one line by either omitting those keys from `metrics["metrics"]` or writing them with a `None` field stripped.
  - File: `src/evaluate.py:629-637`
  - Likely cause: the `out_repl[name] = None` branch in `eval_table_5` propagates `None` into the metrics dict instead of being stripped.
  - Specific fix: In `evaluate.py`, change the per-cell block (around line 629) so that cells with `st["ours"] is None` are dropped from `metrics` (not emitted as `{"value": null, "status": "MISSING"}`). Re-running `scripts/prep_validation.py` should then exit 0.

### Major (should fix)

- [M1] **FF5 alpha sign disagreement (COROLLARY C2, table T3).** Paper reports +0.48% per month for the D1-D10 FF5 alpha (paper §3.1, abstract). Replication: -0.068% per month. r = 0.14 (band 1 sign disagreement). The FF5 alpha is the headline-supporting cell for claim C2 ("factor models explain only ~50% of the duration spread"). The replication's near-zero alpha would imply the FF5 model fully absorbs the spread — the opposite of the paper's claim. Likely root cause: right-tail composition (D8-D10 all have positive FF5 alpha in our replication, paper has negative — D10 paper -0.38 vs ours +0.525).
  - File: `results/table_3.md:24` (replicated D10 FF3 alpha +0.525 vs paper -0.38; FF5 row flips sign)
  - Likely cause: dur distribution compression shrinks the high-dur extreme-growth stock concentration that drives the FF5 spread in the paper. Fix dur right tail to fix this.
  - Specific fix: investigate ROE source for the dur recursion (the paper says "income before extraordinary items over lagged book equity" — if `ib` includes one-time items or the lagged BE has backfill artifacts, the ROE seed distribution shifts). Or relax dur right-tail seed clipping beyond [-1.0, 5.0] (the post-winsorize cap on dur in the 1981-2013 IOR sample is around 27y; paper's portfolio-level high-dur mean is ~25y, but the paper's full dur std is 5.37 vs ours 4.44 — a 17% compression).

- [M2] **IOR mean is 3.5× understated (T1 / Table 10 IOR construction).** Paper's IOR mean = 0.44; replication = 0.13 (rel_err 71%, FAIL). Propagates into RIOR quintile assignment in Table 10. The replicator's REPORT §"Limitations" and assumptions.md both identify this as a unit issue between s34.shares and CRSP.shrout. Until fixed, every Table 10 corollary cell is untrustworthy.
  - File: `src/main.py:312` (the `out["ior"] = out["shares_ttm"] / (out["shrout"] * 1000.0)` line), `src/sql/inst_ownership.sql` (first-appearance filter)
  - Likely cause: shrout is already in actual share count in modern CRSP (since CRSP's late-2000s vintage, shrout is in shares not thousands); the ×1000 divisor divides by 1000× too many. Alternatively, the s34.shares figure may be in thousands. Verify against a single known-firm (e.g. AAPL at a known quarter).
  - Specific fix: spot-check a known firm-quarter (e.g. IBM 2005Q4 — IBM had ~1.6B shares outstanding, s34 holdings reported by major institutions summed to ~600M shares, expected ratio ~0.4). Adjust the divisor to match.

- [M3] **PR mean sign disagreement (T1).** Paper's PR mean = -0.01; replication = +0.67 (FAIL, sign disagreement). The replicator computes `pr = (dvc + tstk) / ib` in `src/sql/panel_annual.sql:201-204`, but Compustat's `tstk` is signed such that positive values indicate a reduction of treasury stock (i.e., share issuance, not repurchase). The paper's "net purchases of common and preferred stock" should be REPURCHASES minus ISSUANCES, i.e. -(tstk) when tstk is positive. This is a sign convention bug, not a magnitude drift.
  - File: `src/sql/panel_annual.sql:201-204`
  - Likely cause: Compustat `tstk` sign convention is "decrease in treasury stock" (positive for issuance). The paper's "net payout" intends repurchases positive (treasury stock increase). So the replicator should use `dvc - tstk` not `dvc + tstk`.
  - Specific fix: change `(toFloat64(coalesce(fc.dvc, 0)) + toFloat64(coalesce(fc.tstk, 0)))` to `(toFloat64(coalesce(fc.dvc, 0)) - toFloat64(coalesce(fc.tstk, 0)))`. Verify against paper Table 1 PR mean of -0.01.

- [M4] **Right-tail dur compression + extreme growth D8-D10 wrong sign (T2).** Paper has monotonically decreasing excess returns D1 → D10 (1.43, 1.24, ..., 0.32). Replication: D1..D7 match, then D8 (0.83) ≈ D7 (0.83), D9 (0.87) > D8, D10 (1.16) > D9 — a hump shape that violates the paper's monotonic claim. Root cause is dur distribution compression (paper std 5.37, ours 4.44): the right tail lacks the explosive-growth firms that should be in D10 with negative excess returns. A few large-cap high-dur firms inflate D10's returns.
  - File: `results/table_2.md:21-23`; `src/main.py:451-466` (seed clip bounds)
  - Likely cause: dur right-tail truncation from per-fyear 1%/99% winsorization + seed clipping at sales_g_seed ≤ 5. The paper's D10 contains firms with sales_g seeds > 5 (multi-year averages of explosive 1990s tech growth).
  - Specific fix: relax sales_g_seed hard clip from [-1, 5] to [-1, 10] (or use no hard clip, relying solely on per-fyear winsorization). Recompute and re-check D10 mean excess.

- [M5] **1993-2003 subsample sign flip (T4).** Paper's D1-D10 spread in the dotcom era is +1.10% per month (the strongest subperiod in the paper); replication shows -0.15% per month (sign disagreement, t = -0.25). This is the subperiod where the paper's headline effect is strongest and where the right-tail composition matters most.
  - File: `results/table_5.md:12`
  - Likely cause: same as M4 — dur distribution compression hurts most in the right-tail era of high-growth tech firms.
  - Specific fix: tied to M4 (relax dur right-tail clip).

- [M6] **6 per-decile D1/D10 means in T4 (paper Table 5) are MISSING.** Committed in `tables_to_replicate.json` (Mean_D1_1963_1973, Mean_D10_1963_1973, Mean_D1_1983_1993, Mean_D10_1983_1993, Mean_D1_2003_2014, Mean_D10_2003_2014) but `src/analysis_table5.py` only computes the spread, not the individual decile means. The pipeline computes D1 and D10 separately; just not the means.
  - File: `src/analysis_table5.py:82-132` (only `compute_d1d10_spread` is implemented)
  - Specific fix: extend `build_table_5` to also emit per-decile D1 and D10 means for each subsample, write them to `results/table_5.md`, and re-run `evaluate.py`. This is a 10-line change.

### Minor (cleanup)

- [m1] **Metric-name mismatch between paper Table 5 panel and replicator IDs.** The replicator uses `id: "T4"` for paper Table 5, and `id: "T5"` for paper Table 10. The iteration log conflates them (uses "T5" for both the subsample paper Table 5 and the dur × RIOR paper Table 10). Not a data issue; just confusing labelling.
- [m2] **`inputs/tables_to_replicate.json` has unescaped JSON quotes.** Line 53, column 165: `"paper's \"restricted\" sample"` is invalid JSON. `src/evaluate.py` patches this with a string replace. The canonical scorer (`scripts/score_replication.py`) cannot read it directly. This blocks the validation gate. Specific fix: replace literal quotes with escaped quotes in the source file.
- [m3] **Mean_Dur sign matches but Std_Dur FAIL (4.44 vs paper 5.37, 17% under).** This is the dur right-tail compression (M4) expressed in T1; no separate fix needed.
- [m4] **FF3 decile-level alphas almost all FAIL (10 of 10 D1-D10 cells).** Even D3 (0.297 vs paper 0.26) is "Match" only because tolerance is 20%; the underlying pattern is deciles-monotonic in paper but kinked in the replication. Tied to M4 / M1.
- [m5] **Tables 7, 8, 9, 12 not replicated.** Documented: Baker-Wurgler sentiment index missing from catalog. The scope guardrail in SKILL.md says these can be SKIP — they're already excluded from `tables_to_replicate.json`. No action.
- [m6] **Table 4 (paper) not replicated.** This is the volatility-managed return analysis. Not in `tables_to_replicate.json`. Scope choice; not a finding.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim (D1..D10 excess return monotonic decrease) | ✗ | Paper: 1.43, 1.24, 1.14, 1.04, 1.00, 0.97, 0.81, 0.68, 0.62, 0.32 (strictly decreasing). Replication: 1.64, 1.30, 1.15, 1.04, 0.99, 0.88, 0.83, 0.83, 0.87, 1.16 (kink at D8-D10, hump). Monotonicity violated. |
| 2 | Headline-magnitude claim (D1-D10 spread = 1.10% per month) | ✗ (sign OK, magnitude 44%) | Replication: 0.489% per month, t = +2.63. Direction matches, magnitude is 44.5% of paper. |
| 3 | Sample coverage ≥ 60% | ✓ | 120,510 of 155,917 annual rows have valid dur = 77.3%. Monthly panel covers 1963-2014 with 3,294 stocks/month on average. |
| 4 | Data-source choice justified | ✓ | All paper-listed sources available in catalog; documented substitutions for CRSP msfhdr dlret join, missing Moody's BE supplement, missing Baker-Wurgler sentiment. |
| 5 | prep_validation.py exit 0 | ✗ | Exits 1: `eval/metrics.json` schema violation (6 null values). See B1. |
| 6 | All committed tables have results files | ✓ | T1, T2, T3, T4 (table_5.md), T5 (table_10.md) all present in `results/`. |
| 7 | SUMMARY.md matches results/table_*.md | n/a | This is the first audit — SUMMARY.md is being written this iteration. |
| 8 | No orphan folders | ✓ | No literal-brace folders. |
| 9 | Diagnoses paired with fix attempts | ✓ | Every assumptions.md entry has Diagnosis, Next fix, Before metric, After metric, Status fields. Iteration log shows 5 inner iterations with paired diagnose → fix → verify cycles. |
| 10 | Cell status verification (re-run evaluator, diff against eval/scoring.json) | ✓ | Re-ran `src/evaluate.py`; tally 23 Match / 48 FAIL / 6 MISSING consistent with original metrics.json. Canonical scorer (`scripts/score_replication.py --iteration 1`) wrote `eval/scoring.json` with loss = 0.7013, match_count = 23, fail_count = 48, missing_count = 6. |
| 11 | Corollary coverage | ✗ | C2 (FF3/FF4/FF5 alphas), C3 (subsample stability), C4 (RIOR cross-section) all have computed cells in `results/`. The corollary Match rate of 12 / 57 = 21.0% is below the 25% threshold. |
| 12 | Claim coverage of committed selection | ✓ | All 4 paper claims (C1-C4) are covered by at least one committed table. C1 → T2, C2 → T3, C3 → T4, C4 → T5. T1 supports all by validating construction. |
| 13 | Sign conventions re-derived from paper | ✗ | PR sign disagreement (M3); FF5 alpha sign disagreement (M1). Both are sign-flip failures per Spot-check 13. D10 mean excess sign matches (both positive) but the SHAPE is wrong (right-tail hump vs paper's monotonic decrease). The D10 sign match is not a pass — it's a FAIL because the relative-to-D9 pattern is broken. |
| 14 | Reporting discipline (grid completeness, claim citations, SE-less headlines) | ✓ | Every committed cell is in the table; every paper claim is cited; SE / t-stats are reported for all returns cells. |
| 15 | REPORT.md headline freshness (tally matches eval/scoring.json; DEV-010) | ✓ | REPORT.md reports 23 Match / 48 FAIL / 6 MISSING = 32.4% hit rate. Consistent with `eval/scoring.json#aggregates` (match_count=23, fail_count=48, missing_count=6, hit_rate=29.87% by canonical scorer formula but 32.4% by the replicator's exclude-MISSING formula). The two differ in the denominator (canonical uses n_committed=77 including MISSING; replicator's hit rate uses Match+FAIL=71). The canonical formula is the audit-canonical one. |

## 4. Issues the agent should have caught (didn't)

1. **P_t = BV is the wrong dur denominator.** Inner iterations 1-3 had this bug; the dur-BM correlation was +0.035 (wrong sign) for the first three iterations. The replicator correctly diagnosed it in inner iteration 4 and applied the ME fix in iteration 5. This is good — the agent caught it. (No finding.)

2. **IOR unit mismatch.** The replicator's REPORT.md §Limitations identifies "IOR mean (0.13 vs 0.44) — IOR construction has a unit issue" and suggests "need to verify shares unit vs shrout unit". This is correctly identified as a known issue. (No finding.)

3. **PR sign convention bug.** REPORT.md identifies "PR mean sign disagreement. Our PR mean is +0.67 vs paper -0.01. Likely a definition discrepancy in 'net payout'". The agent flagged the symptom but did not investigate the root cause (the `tstk` sign convention in Compustat). This is a partial fix: documented but not actionable. **Auditor finding**: the fix is mechanical (`-` instead of `+` in `src/sql/panel_annual.sql:203`); the agent should have committed this fix.

4. **6 MISSING cells in T4 (per-decile D1/D10 means).** The replicator noted them in iteration log: "6 MISSING cells are Table 5 per-decile D1/D10 means, which the pipeline does not currently produce (the spread is computed but not the per-decile means)." This is a scope gap the agent identified but did not address in this iteration. **Auditor finding**: a 10-line addition to `src/analysis_table5.py` would close all 6. Low-cost fix not attempted.

5. **FF5 alpha sign disagreement.** Not explicitly flagged in REPORT.md. REPORT.md does note "FF5 = -0.068 vs 0.48 (wrong sign)" for Table 3. The agent correctly noted this is a FAIL but did not classify it as critical to the headline claim (C2 = "factor models explain only ~50%"). **Auditor finding**: this should be elevated to a headline-supporting cell.

6. **`eval/metrics.json` schema violation.** Not addressed. The validator (`prep_validation.py`) flags this at exit-1. **Auditor finding**: the replicator ran `evaluate.py` but did not run `prep_validation.py` to confirm the schema was clean. Hygiene miss.

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "Cash flow duration and the term structure of equity returns" (Weber 2018) for slug `weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns`. The previous agent run completed with verdict **FAILED** (audit 1 at `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/logs/audit1.md`). Read the audit first.

The replication produces the right direction with statistical significance but at 44% of the paper's magnitude. Most corollary cells fail. The most load-bearing fixes are:

## Issues to address (priority order)

### [B1] — BLOCKER — fix first
`eval/metrics.json` schema violation: 6 entries written with `"value": null`. The canonical scorer (`scripts/score_replication.py`) errors on this; `scripts/prep_validation.py` exits non-zero.

**Specific fix:**
1. Open `src/evaluate.py` line 611-637 (the `metrics` dict construction).
2. Change the loop so that when `st["ours"] is None`, the metric key is **omitted** from `metrics` (not emitted as `{"value": null, "status": "MISSING"}`). The canonical scorer treats missing keys as MISSING — same effect, clean schema.
3. Re-run `python scripts/prep_validation.py weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns` and confirm exit 0.

### [M6] — MAJOR — fix second (cheap)
6 per-decile D1/D10 means in T4 (paper Table 5) are MISSING. The pipeline computes the spread but not the individual decile means.

**Specific fix:**
1. Open `src/analysis_table5.py` around `build_table_5` (line 94).
2. Compute per-decile D1 and D10 mean excess returns per subsample (mirror `compute_d1d10_spread` for each decile separately).
3. Write them to `results/table_5.md` as additional rows.
4. Re-run `python src/evaluate.py` — all 6 cells should become computable.

### [M3] — MAJOR — fix third (one-line)
PR sign convention bug. `src/sql/panel_annual.sql:201-204` computes `pr = (dvc + tstk) / ib`. Compustat `tstk` is signed "decrease in treasury stock" — positive for issuance, negative for repurchase. The paper's "net payout" intends repurchases positive. Change `+` to `-`.

**Specific fix:**
1. Edit `src/sql/panel_annual.sql` line 203: replace `+ toFloat64(coalesce(fc.tstk, 0))` with `- toFloat64(coalesce(fc.tstk, 0))`.
2. Re-run the pipeline (`python src/main.py`).
3. Re-run `src/analysis_table1.py` and `src/evaluate.py`.
4. Verify Mean_PR (T1) flips sign to near-zero. Paper target = -0.01, tolerance ±25%.

### [M4] + [M5] + [M1] — MAJOR — fix together (dur right-tail)
The dur distribution is too compressed (std 4.44 vs paper 5.37; 17% under). This drives D8-D10 wrong pattern, the 1993-2003 subsample sign flip, and the FF5 alpha sign disagreement. Root cause is the seed clipping at `sales_g_seed ≤ 5` and `roe_seed ≤ 1.0` plus per-fyear winsorization.

**Specific fix:**
1. Open `src/main.py` line 463-466. Change `df_seeds["sales_g_seed"].clip(lower=-1.0, upper=5.0)` to `upper=10.0` (or higher; the paper's 1990s tech firms had sustained >100% annual sales growth). Same for roe_seed if needed.
2. Or: remove the hard clip entirely, rely on per-fyear 1%/99% winsorization alone.
3. Re-run `python src/main.py` (this rewrites `data/panel_annual.parquet`).
4. Re-run all five `analysis_table*.py` scripts and `src/evaluate.py`.
5. Verify: Std_Dur (T1) increases toward paper's 5.37; D10 mean excess decreases; 1993-2003 sign flips back to positive; FF5 alpha flips back to positive.

### [M2] — MAJOR — fix fifth (IOR construction)
IOR mean is 0.13 vs paper 0.44 (3.5× under). The unit mismatch is at `src/main.py:312`: `out["ior"] = out["shares_ttm"] / (out["shrout"] * 1000.0)`. Either shrout is in shares not thousands (modern CRSP vintage), or s34 shares is in thousands.

**Specific fix:**
1. Spot-check IBM 2005Q4: IBM had ~1.6B shares outstanding. Find s34 holdings reported by all institutions for IBM at 2005Q4 — should sum to ~600M shares (40% of shares outstanding, consistent with paper IOR mean of 0.44).
2. If s34.shares is in thousands (older convention) but shrout is in actual shares (modern convention), the divisor should be removed entirely (or set to 1.0). If shrout is in thousands but s34.shares is in shares, the ×1000 divisor is correct.
3. The single-firm spot-check tells you which direction.
4. Re-run pipeline + Table 10 analysis + evaluate.py. Verify Mean_IOR (T1) increases to ~0.40.

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every iteration log entry in `preparations/assumptions.md` must have all five fields: Diagnosis, Next fix, Before metric, After metric, Status.
- **10-iteration cap per problem.** Hard stop at 10 and escalate to the human.
- **Re-run `scripts/prep_validation.py` at the end of every iteration.** Confirm exit 0 before declaring the iteration complete.
- **Re-run `scripts/score_replication.py <slug> --iteration N`** at the end of every iteration to refresh `eval/scoring.json` and `eval/loss_trace.json`.

## Inputs you should read

- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/logs/audit1.md` — this audit (full context)
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/inputs/content.md` — paper ground truth
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/preparations/assumptions.md` — current decision log
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/src/main.py` — current pipeline (will be modified)
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/data/` — cached intermediates

## What NOT to redo

- The duration formula (compute_duration with P_t = ME) — keep it.
- The 5y/3y annualized sales-growth seed — keep it.
- The per-fyear 1%/99% winsorization — keep it.
- The Shumway (1997) -30% treatment — keep it.

## Deliverables for this iteration

- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/src/main.py` — revised with [M2] IOR fix
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/src/sql/panel_annual.sql` — revised with [M3] PR fix
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/src/analysis_table5.py` — extended with [M6] per-decile means
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/results/table_*.md` — updated for each committed table
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/preparations/assumptions.md` — append a new iteration log entry for every issue addressed
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/REPORT.md` — updated; lead with the data-quality summary and the new headline D1-D10 spread value
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/eval/metrics.json` — refreshed; value=null entries removed

## Stop conditions

- **All blockers fixed and verified** → re-run `prep_validation.py` and `score_replication.py`; if both pass, declare success or note remaining majors in `REPORT.md`.
- **10-iteration cap reached** on a single problem → escalate to the human and write a partial `REPORT.md`.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

This is a thoughtful, well-instrumented replication. The replicator built a 15-step AR(1) dur recursion in pure numpy (correctly identified the P_t=ME fix), wired Shumway (1997) delisting treatment, hit the exact sample period and universe, and surfaced every FAIL with quantitative diagnostics in `assumptions.md`. The iteration log (`logs/log1.md`) is exemplary — five inner iterations, paired diagnose/fix/verify cycles, clear before/after metrics. The P_t = ME fix in inner iteration 4 is the kind of methodology insight that turns a wrong-sign failure into a Match.

But the corpus is partial. The headline reproduces in direction and significance at half the paper's magnitude. The dur distribution compression (std 4.44 vs 5.37) is the most consequential gap and propagates into the right-tail deciles (D8-D10 wrong pattern), the 1993-2003 subsample sign flip, and the FF5 alpha sign disagreement. The IOR unit mismatch at `src/main.py:312` is a one-line fix that unblocks 17 cells in Table 10. The PR sign convention bug is a one-character fix in `src/sql/panel_annual.sql`. The 6 MISSING T5 per-decile means are a 10-line addition to `analysis_table5.py`.

These are all actionable. The replicator correctly identified several of them in REPORT.md §Limitations but did not apply the fixes in this iteration. The next iteration should be a tight 5-issue patch pass, not a methodology overhaul — the core pipeline is sound, the diagnostic loop is tight, and the data is in the right shape.