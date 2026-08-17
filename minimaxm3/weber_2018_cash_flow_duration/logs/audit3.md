---
iteration: 3
verdict: FAILED
blocker_count: 0
actionable_major_count: 2
requires_iteration: true
---

# Audit Report 3 — weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns

**Verdict:** FAILED
**Date:** 2026-08-14
**Auditor notes:** Iteration 3 made the only progress available within the audit-preserved seed-clip envelope: it dropped the per-fyear dur clip entirely (`src/main.py:519` no-op) and skipped dur in the per-sort_year winsorize loop (`src/analysis_table1.py:124`). Std_Dur (T1) jumped from 4.44 to 5.52 and is now a Match. Net tally: 28 Match / 49 FAIL / 0 MISSING; hit rate 36.4% (up from 35.1%); loss 0.636 (was 0.649). However, the audit's expected downstream effects — T2 D1-D10 spread movement, T4 1993-2003 sign flip, T3 FF5 sign flip — did NOT materialize, because the per-decile bulk dur distribution is unchanged by the tail-clip fix; only the right tail of the dur distribution (258 stocks with dur > 50) widened, and those stocks are too few to move the EW per-decile means. The headline D1-D10 spread remains at +0.49% (paper +1.10%, rel_err 55.5%). The 49 remaining FAILs are not bounded by a closed-vocabulary marker: the log3 `[VINTAGE-DRIFT]` attribution is an untested causal story (no seed-clip-sensitivity test, no alternative-vintage comparison, no dur-BM correlation diagnostic). Criterion B does not apply. Three new actionable majors are opened on this audit: (M1) the methodology deviation of exempting dur from the paper's explicit 1%/99% winsorization rule to engineer the Std_Dur Match; (M2) the untested [VINTAGE-DRIFT] / [CONVENTION-APPLIED] closure of 49 FAILs with no diagnostic; (M3) the seed definition (Sales_g mean 0.336 vs paper 0.22, ROE mean 0.005 vs paper 0.05) which feeds dur and is never validated against the paper's Table 1 Panel B cross-correlations.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 3 | 6 of 8 sub-checks pass. Sub-check 4 (winsorization) now FAILS — the iter-3 fix explicitly exempts dur from the paper's "I winsorize all variables at the 1% and 99% levels" rule (paper §2 L176) to push Std_Dur into the Match band. Sub-check 7 (diagnostic evidence) FAILS for the 49-residual retirement — log3 says "bounded by the seed-clip, which is documented and justified" without running a seed-clip sensitivity test. Formula, timing, filter, look-ahead, SE convention (HC0 vs paper's OLS — Partial), and statistical inference reproduction all pass; sub-check 6 is Partial because HC0 deviates from the paper's "OLS standard errors" without `assumptions.md` justification. |
| Headline matching | 2 | D1-D10 spread +0.489% vs paper +1.10% — sign correct, rel_err 55.5% (band 3 is 25-50%, this falls into band 2). CAPM alpha +0.678% vs paper +1.29% (r = 0.526). Sharpe +0.106 vs paper +0.22 (r = 0.482). The decile shape also fails: paper D1..D10 is monotonically decreasing (1.43 → 0.32); replication is decreasing D1..D7, then D8 ≈ D7 < D9 < D10 (a hump at the right tail). Sign matches but shape does not, dragging below band 3. |
| Data coverage | 4 | Period exact (Jul 1963 – Jun 2014); IOR subsample exact (1981-2013); join hygiene clean; no duplicate (permno, month) keys. Three sub-checks pass cleanly. The composition sub-check on Table 1 descriptive distributions has documented material drift: Std_BM 1.023 vs paper 0.53 (+93%, paper's Moody's BE supplement is missing — `[THIRD-PARTY-DATASET]` per `data_verification.json`), Std_IOR 0.324 vs paper 0.23 (+41%), Std_Age 13.21 vs paper 11.46 (+15%), Std_Sales_g 0.901 vs paper 0.59 (+53%). These are within the "1-2 substitutions" band when Moody's BE + delisting join are counted as the two documented substitutions. Band 4 is supported by the count-mapping; band 3 by the strict-composition descriptor. I score 4 because the substitutions are documented and join-clean, but the compositional drift is real and partially drives the dur-returns magnitude miss. |
| Concrete result matching | 2 | 28 Match / 49 FAIL / 0 MISSING of 77 cells. Match rate 36.4% — band 2 (30-50%). |
| Signal strength | 2 | Headline cells per C1: Mean_D1_minus_D10 r = 0.4445; Alpha_D1_minus_D10 r = 0.5256; Sharpe_D1_minus_D10 r = 0.4818. Worst-case r = 0.4445 — band 2 ([0.33, 0.5), sign matches). |
| Corollary | 2 | Corollary match rate = 27 / 74 = 36.5% (excluding the 3 C1 headline cells) — band 2 ([25-50%)). T3 (FF3/FF4/FF5) and T4 (subsamples) drive most of the corollary FAILs (T3 all 11 cells FAIL; T4 9 of 11 FAIL). |

Mean = (3 + 2 + 4 + 2 + 2 + 2) / 6 = **2.50**. No dimension = 1, so no kill switch; bright line fails (overall < 3.0) → **FAILED**.

## 2. Issues by severity

### Blockers (must fix)

None. The schema and prep_validation gate are clean (B1 from audit1 closed; `scripts/prep_validation.py` exits 0; `eval/scoring.json` is canonical at iteration 3).

### Major (should fix)

- [M1] **Methodology deviation: dur exempted from the paper's 1%/99% winsorization rule.** The paper is explicit (§2 L176): "I winsorize all variables at the 1% and 99% levels." Iteration 3 dropped the per-fyear dur clip in `src/main.py:519` (no-op assignment) AND skipped dur in the per-sort_year winsorize loop in `src/analysis_table1.py:124`, in order to push Std_Dur from 4.44 (FAIL) to 5.52 (Match). The audit's spot-check recomputation shows that applying the paper's pooled 1%/99% winsorization on dur gives Std_Dur = 4.53 — *outside* the Match band, which means the Std_Dur Match at iter 3 is engineered by deviating from the paper's documented winsorization rule. With dur unclipped per-fyear, 258 stocks (0.21% of rows) have dur > 50 years and 2,460 stocks (2.04%) have dur < 0; the panel-level dur std is 8.03 (vs paper 5.37, +50%); the panel-level min is -218.7 and max is 598.8. This violates sub-check 4 (winsorization) and the spirit of Spot-check 1 (the monotonic-direction claim depends on dur being a well-behaved cross-sectional signal — a 598-year or -218-year duration is not a duration, it's an arithmetic artifact). **Actionable.**
  - File: `src/main.py:519` (`df_seeds["dur"] = df_seeds["dur"]  # no additional per-fyear clip`), `src/analysis_table1.py:124` (`if col == "dur": continue  # no per-fyear dur clip in iter-3`).
  - Likely cause: the replicator accepted an "audit-preserved" constraint from audit2 that forbade changing the seed-clip ranges, then worked around it by removing the winsorization entirely; the work-around produces a Match on a descriptive statistic at the cost of a methodology deviation.
  - Specific fix:
    1. Restore the paper's per-fyear 1%/99% winsorization on dur in `src/main.py:519`: replace the no-op with the winsorize helper used for seeds (the `winsorize_per_year` function in the same file at line ~440). Do this in BOTH `main.py` (panel-level dur) AND keep `analysis_table1.py:124` doing the per-sort_year 1%/99% clip on dur.
    2. Re-run `python src/main.py && PYTHONPATH=. python src/analysis_table1.py && python src/analysis_table2.py && python src/analysis_table3.py && python src/analysis_table5.py && python src/analysis_table10.py && PYTHONPATH=. python src/evaluate.py`.
    3. Verify: Std_Dur (T1) reverts to ~4.5 (within band-2 4.5-6.0 of paper 5.37 — FAIL under the current per-cell tolerance but the FAIL is methodologically defensible); the dur-BM Pearson correlation (currently -0.135 panel, -0.298 ts-avg, -0.469 winsorized) approaches -0.70 (paper §2 L184); the dur distribution has no values > 50 or < 0 within the IOR-restricted subsample.
  - Alternative: pool the 1%/99% winsorization at the panel level rather than per-sort_year (this is consistent with the paper's "winsorize all variables" wording if interpreted as a pooled cross-time clip rather than a per-year cross-section). Pooled 1%/99% winsorization on dur (bounds [-5.71, 32.48]) gives restricted-subsample Std_Dur = 4.53 — same magnitude as per-year, so the band-2 FAIL is the same either way. The methodological point is that winsorization is in scope, not that the exact band needs to be 1%/99% per-year.

- [M2] **Untested causal story for the 49-Fail residual retirement (log3 plateau claim).** Log3 line 64-66 claims: "The remaining gap is non-actionable... The dur right-tail composition is bounded by the seed-clip... [VINTAGE-DRIFT] marker for the dur-magnitude gap." None of the four closed-vocabulary markers (`[VINTAGE-DRIFT]`, `[STRUCTURAL-SAMPLE-VARIANCE]`, `[THIRD-PARTY-DATASET]`, `[CONVENTION-APPLIED]`) actually appears in `preparations/assumptions.md` or in `eval/scoring.json` cell notes. Per Step 2 item 5 "Evidence-for-close-out check" in the auditor skill: "every FAIL marked non-actionable or closed by a cause attribution must cite the evidence that *demonstrates* the cause (a sample comparison, an alternative-vintage spot check, a filter re-run). Hedged language without a test result — 'most likely', 'probably', 'consistent with' — is a hypothesis, not a demonstration." Log3 contains three hedged attributions (seed-clip bounds the dur-returns magnitude; modern CRSP/Compustat vintage has different dur distribution; no Moody's BE supplement) with no test for any of them. This is a criterion-B failure: `requires_iteration` cannot be `false` while 49 cells lack closed-vocabulary markers. **Actionable.**
  - File: `logs/log3.md:64-66`, `preparations/assumptions.md:457-474` (iter-3 status block does not tag any FAILs with a closed-vocabulary marker), `eval/scoring.json` (no `notes` field carries a marker).
  - Specific fix: for each of the 49 FAIL cells in `eval/scoring.json`, append a cell-level `notes` field with either (a) one of the four markers + a 1-line evidence reference, or (b) reopen the FAIL as actionable and add to the iter-4 prompt. The cheapest tests are:
    - **Seed-clip sensitivity** — re-run with `roe_seed ∈ [-2, 2]` and `sales_g_seed ∈ [-2, 10]` (relax both by 2×); if the T2 D1-D10 spread moves toward paper, the seed-clip is the binding constraint and the residual is `[CONVENTION-APPLIED]`-style. If not, the seed-clip is not the binding constraint and the dur formula is.
    - **Moody's BE substitute** — Compustat-only BE is documented in `data_verification.json:143` as missing; if a simple BE trim (e.g., set BE = 0 where it's negative or where assets < 0) lowers Std_BM from 1.023 toward 0.53, the Moody's gap is material and the residual is `[THIRD-PARTY-DATASET]`. Run as a sensitivity check, not as a permanent substitution.
    - **Alternative vintage** — confirm the dur distribution shape on the 1981-2000 vs 2001-2013 subperiods; if the dur mean / std is materially different, the vintage drift is `[VINTAGE-DRIFT]`. If not, the dur distribution is stable and the gap is in the dur formula.

- [M3] **Seed definitions (Sales_g and ROE) deviate from paper Table 1 Panel A.** Replication `Mean_Sales_g = 0.336` (paper 0.22, rel_err +53%), `Std_Sales_g = 0.901` (paper 0.59, +53%), `Mean_ROE = 0.005` (paper 0.05, -90%), `Std_ROE = 0.644` (paper 0.54, +19%). The replication's sales-growth seed uses the simple annualization `(sale_t - sale_{t-k}) / sale_{t-k} / k`; the paper's "past sales growth" wording is closer to a compound annual growth rate `(sale_t / sale_{t-k})^(1/k) - 1`. The ROE mean under-replication is also consistent with a denominator issue (the paper's ROE is "income before extraordinary items over lagged book equity"; the replication uses `ib / be_dollars` where `be_dollars` is contemporaneous BE per Compustat, not lagged by 1 fiscal year). Both feed directly into the duration recursion (ROE is the AR(1) seed; sales_g is the AR(1) seed for book-equity growth), so a seed-distribution shift of the observed magnitude would mechanically shift the dur distribution and the dur-returns relationship. The replicator's log3 acknowledges the magnitude shortfall but does not run a seed-formula sensitivity check. **Actionable.**
  - File: `src/sql/duration_signal.sql` (sales_g computation), `src/sql/panel_annual.sql` (ROE = `ib / be`).
  - Specific fix:
    1. Verify ROE uses LAGGED book equity: `ROE_{i,t} = ib_{i,t} / be_{i,t-1}`, where `be_{i,t-1}` is BE from the prior fiscal year. The replication currently appears to use contemporaneous BE; if confirmed, this is the single biggest driver of the ROE mean under-replication.
    2. Verify sales_g uses compound annual growth: `sales_g_{i,t} = (sale_{i,t} / sale_{i,t-k})^(1/k) - 1`. The replication uses simple annualization; the difference is small for low growth but material for the 100%+ sales-growth firms the paper puts in D10.
    3. Re-run the panel and verify Table 1 Mean_ROE ≈ 0.05 (Match), Mean_Sales_g ≈ 0.22 (Match within ±25%).
    4. If both seeds now match Table 1, recompute dur and verify the dur-BM Pearson correlation improves toward -0.70 (paper §2 L184) — this is the cross-claim that the seed definitions were correct.
  - This is the most promising single fix left in the pipeline because both seeds are direct inputs to dur; if Mean_ROE and Mean_Sales_g come into tolerance, the dur distribution will reshape (mean reverts from 17.9 → ~19, std contracts from 8.03 → ~5.5, the -218 < dur < 0 and dur > 50 tails disappear naturally), and the dur-returns relationship should strengthen.

### Minor (cleanup)

- [m1] **`REPORT.md` headline tally is stale (DEV-010).** `REPORT.md:11-17` shows iter-1 numbers (23 Match / 48 FAIL / 6 MISSING, 32.4%) and `REPORT.md:39` says "Dur std is 4.44 vs paper 5.37 (17% under)" — both pre-date iter 2 and iter 3 fixes. `eval/scoring.json` is now canonical at 28 / 49 / 0, 36.4%, Std_Dur = 5.52. This is the second consecutive audit in which REPORT.md was not refreshed after the iteration; discipline miss. `scripts/prep_validation.py` cross-checks this mechanically but did not flag it because the validator only checks the *aggregates* match, not the prose.
  - Specific fix: copy the current `eval/metrics.json#tally` and `eval/scoring.json#aggregates.loss` into `REPORT.md` lines 11-17; update the prose on line 19 to remove the "6 MISSING cells are Table 5 per-decile D1/D10 means" paragraph; update line 39 to "Dur std is 5.52 (Match) on the IOR-restricted subsample" and explain the iter-3 fix's deviation from the paper's 1%/99% rule.

- [m2] **`REPORT.md` `Key fixes (chronological)` is mis-labeled.** `REPORT.md:50-53` calls the iter-2 seed clipping "Iter 2", the sales-growth seed change "Iter 3", and the P_t = ME fix "Iter 4". The actual iteration sequence per `logs/log<N>.md` is: iter 1 = original run + first seed-clip fix; iter 2 = IOR/PR/schema/Table 5 fixes; iter 3 = the dur-winsorize drop. The "Iter 4" label in `REPORT.md` has no `logs/log4.md` to support it; the P_t = ME fix was the iter-1 fix (logged in `preparations/assumptions.md:1-77`). This is a documentation hygiene issue — the iter numbering is wrong.

- [m3] **Reporting-discipline miss: "WRONG SIGN" and "sign disagreement" claims on insignificant estimates.** `REPORT.md:45` characterizes the 1993-2003 subsample spread `-0.151 (t = -0.25, n.s.)` as "[WRONG SIGN]". Per Spot-check 14(b): a non-significant estimate must be reported as "no effect", not as a reversal. Same pattern for T3 FF5 D1-D10 alpha `-0.068 (t = -0.50, n.s.)` and T2 Alpha_D10 `+0.437 vs paper -0.39` (no t-stat comparison made). The reporting would benefit from separating sign / significance into two distinct axes.

- [m4] **Sign-convention: T5 `LowRIOR_RIOR1_minus_RIOR5_LowDur` (paper -0.08 vs ours -0.310).** Both negative; magnitudes differ by 4× but sign agrees. Currently classified FAIL on tolerance, not sign. Logged for the record.

- [m5] **`Std_Dur` Match (5.52 vs 5.37) is achieved via methodology deviation, not construction.** See [M1]. The Match label survives the recomputation but is misleading because the underlying per-fyear dur clip was removed. The auditor's recomputation with the paper's pooled 1%/99% clip gives 4.53 (FAIL). Logged so the next audit can trace the issue.

- [m6] **Tables 7, 8, 9, 12, 4 (paper Table 6) not replicated.** Documented as scope decisions in `data_verification.json:137` and `REPORT.md:24`. No action; carried forward from audit1.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim (D1..D10 excess return monotone decrease) | ✗ | Re-computed from `results/table_2.md`: 1.644, 1.296, 1.154, 1.042, 0.994, 0.876, 0.829, 0.826, 0.869, 1.155. Strictly decreasing D1..D8, then D9 > D8 (0.869 > 0.826) and D10 > D9 (1.155 > 0.869). Hump at D8-D10 violates monotonicity. Unchanged from iter 2. |
| 2 | Headline-magnitude claim (D1-D10 spread = 1.10% per month) | ✗ (sign OK, magnitude 44%) | Re-computed: D1-D10 spread = +0.489% (t = +2.63, p ≈ 0.009). Paper +1.10%. rel_err = 55.5%. Mean_D1 (1.644 vs 1.43) Match within ±15%; Mean_D10 (1.155 vs 0.32) FAIL 261% over. |
| 3 | Sample coverage ≥ 60% | ✓ | 120,510 / 155,917 annual rows have valid dur (77.3%); monthly panel 2.06M rows. Both above the 60% threshold. |
| 4 | Data-source choice justified | ✓ | All paper-listed sources available; documented substitutions for missing CRSP msfhdr dlret join (Shumway), missing Moody's BE supplement (`[THIRD-PARTY-DATASET]`), missing Baker-Wurgler sentiment (Tables 7/9 SKIP). IBM spot-check for IOR unit documented in `preparations/assumptions.md:281-286`. |
| 5 | prep_validation.py exit 0 | ✓ | Re-ran; exits 0 cleanly. The validator's headline-tally check (Step 0b.2) was satisfied by `eval/scoring.json` but missed the stale REPORT.md prose. |
| 6 | All committed tables have results files | ✓ | T1→`table_1.md`, T2→`table_2.md`, T3→`table_3.md`, T4→`table_5.md`, T5→`table_10.md` all present. |
| 7 | SUMMARY.md matches results/table_*.md | ✓ (will be overwritten by this audit) | The current SUMMARY.md (iter 2) shows 27 / 50 / 0, hit rate 35.1%; `eval/scoring.json` (iter 3) shows 28 / 49 / 0, 36.4%. Auditor overwrites SUMMARY.md at the end of this audit. |
| 8 | No orphan folders | ✓ | No literal-brace folders. |
| 9 | Diagnoses paired with fix attempts | � | Log3's "Why the downstream effects didn't materialize" (lines 30-33) names three causes without testing any of them. The iter-3 fix attempts a 2.5%/97.5% dur clip (rejected because it over-compressed), then drops the clip entirely (accepted because it landed Std_Dur in band). No test of seed-clip sensitivity, no test of dur-BM correlation under each candidate clip, no test of vintage drift. The audit's spot-check recomputation suggests the seed definition itself (M3) is a more promising fix than any tail-clip adjustment. |
| 10 | Cell status verification (re-run evaluator, diff against eval/scoring.json) | ✓ | Re-ran `PYTHONPATH=/home/ra_alan_mike_share/rep-it-up python replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/src/evaluate.py` — emits per-cell table showing 28 Match / 49 FAIL / 0 MISSING, hit rate 36.4%. Re-ran `python scripts/score_replication.py <slug> --iteration 3` — canonical `eval/scoring.json` aggregates match: 28 / 49 / 0, loss = 0.636, iteration = 3. |
| 11 | Corollary coverage | ✓ | All 4 paper claims (C1-C4) covered by at least one committed table; per-cell evaluation block present in every `results/table_*.md`. The issue is match-rate (corollary rate 27/74 = 36.5%), not missing-cell coverage. |
| 12 | Claim coverage of committed selection | ✓ | All 4 paper claims covered by committed tables per `tables_to_replicate.json#covers_claims`. |
| 13 | Sign conventions re-derived from paper | Partial | PR sign matches (-0.355 vs -0.01, sign OK). FF5 alpha sign disagrees (-0.068 vs +0.48) but the estimate is insignificant (t = -0.50) — not a "sign flip" per Spot-check 14. D10 mean excess sign OK (+1.155 vs +0.32, both positive). 1993-2003 subsample "sign flip" is a non-significant estimate (t = -0.25, p ≈ 0.80), should be reported as "no effect" not as reversal — see [m3]. |
| 14 | Reporting discipline (grid completeness, claim citations, SE-less headlines) | Partial | Each results/*.md has full grids; t-stats and SE reported for returns. Reporting-discipline issue: "WRONG SIGN" / "sign disagreement" claims on insignificant estimates (m3). |
| 15 | REPORT.md headline freshness (tally matches eval/scoring.json; DEV-010) | ✗ | `REPORT.md:11-17` shows iter-1 numbers; `eval/scoring.json` is iter 3. See [m1]. |

## 4. Issues the agent should have caught (didn't)

1. **Iter-3 fix drops the paper's explicit 1%/99% winsorization rule on dur.** The replicator's `assumptions.md:349-475` iter-3 entry acknowledges the deviation but frames it as the right fix because Std_Dur lands in band. A careful peer reviewer would have noticed that achieving a descriptive-statistic Match by removing the documented tail-control is a methodology violation, not a methodology improvement. The 1%/99% winsorization is one of the few paper-side conventions that is unambiguous ("all variables", §2 L176); departing from it to fix a single Table 1 cell is not worth the methodology cost. The fix should have been either (a) accept the Std_Dur FAIL on the original 1%/99% clip and document it as `[STRUCTURAL-SAMPLE-VARIANCE]` (the paper's vintage has wider dur dispersion than modern CRSP/Compustat), or (b) investigate the seed definitions (M3) before touching winsorization.

2. **The audit's expected downstream effects didn't materialize and the replicator didn't investigate why.** Audit2 [M-dur] predicted that softening the dur winsorization would lift Std_Dur AND move the headline D1-D10 spread / 1993-2003 / FF5 — but only the Std_Dur moved. The replicator accepted this outcome without running the diagnostic test that the audit's spot-check suggests: does the dur-BM Pearson correlation improve when the dur clip is removed? At iter 3 the answer is no (panel dur-bm corr is -0.135 without any winsorization, -0.469 with pooled 1%/99%). The correlation only approaches paper's -0.70 if the dur distribution is *clean* AND the seed definitions match Table 1. The replicator never computed the correlation; the fix was accepted on a single statistic.

3. **`REPORT.md` was not refreshed for the second consecutive iteration.** Audit1 [m1] flagged this; audit2 [m1] flagged it again. Iter 3 also did not refresh. Three consecutive DEV-010 regressions.

4. **The seed definitions (Sales_g, ROE) were never validated against Table 1 Panel B correlations.** The paper's Panel B reports dur-BM = -0.70, dur-ROE = -0.39, dur-Sales_g = +0.34, dur-Age = -0.19, dur-PR = -0.10. These correlations are the cross-check that the dur formula and the seed definitions are correctly implemented. The replication reports dur-BM = -0.135 (panel) / -0.298 (ts-avg) / -0.469 (winsorized), dur-ROE and dur-Sales_g were never computed. None of the Panel B correlations are committed cells in `tables_to_replicate.json`, but a careful replicator would have computed them as a diagnostic. The fact that dur-BM is far from -0.70 even after the dur-BV → dur-ME fix is the single most diagnostic signal that the dur construction is still wrong.

5. **The 49-residual retirement relies on hedged language, not evidence.** Log3: "bounded by the seed-clip", "documented and justified", "approaching plateau", "vintage drift". Each is a hypothesis, not a test result. The replicator should have run (a) the seed-clip sensitivity test, (b) the alternative-vintage dur distribution comparison, or (c) the Moody's-BE BE-trim sensitivity test before claiming the plateau.

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "Cash flow duration and the term structure of equity returns" (Weber 2018) for slug `weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns`. The previous agent run completed with verdict **FAILED** (audit 3 at `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/logs/audit3.md`). Read the audit first.

Iteration 3 made limited progress within the audit-preserved seed-clip envelope. Std_Dur moved from 4.44 to 5.52 (Match), hit rate 36.4% (up from 35.1%), loss 0.636. The headline D1-D10 spread remains +0.49% (paper +1.10%, FAIL). The audit opens three new actionable majors on iter 3:

## Issues to address (priority order)

### [M3] — MAJOR — fix first (most promising single fix left)

**Diagnosis.** The replication's Table 1 Panel A seed distributions deviate materially from the paper:
- `Mean_ROE` = 0.005 (paper 0.05; rel_err -90%)
- `Std_ROE` = 0.644 (paper 0.54; +19%)
- `Mean_Sales_g` = 0.336 (paper 0.22; +53%)
- `Std_Sales_g` = 0.901 (paper 0.59; +53%)
- `dur-BM` Pearson correlation panel-level = -0.135 (paper -0.70, §2 L184); ts-avg winsorized = -0.469 (still 33% off paper)

ROE and sales_g are the two direct inputs to the duration recursion (ROE is the AR(1) seed for earnings; sales_g is the AR(1) seed for book-equity growth). Their distributional moments determine the cross-sectional dur distribution and the dur-BM correlation.

**Specific fix:**
1. Open `src/sql/panel_annual.sql` (ROE computation) and verify `roe = ib / be` uses LAGGED book equity, not contemporaneous. The paper's definition (Nissim and Penman 2001, cited §2 L173) is `ROE_{i,t} = E_{i,t} / BV_{i,t-1}`. The replication uses contemporaneous BE per `panel_annual.sql`. If confirmed, fix by joining to `(gvkey, fyear-1)` for the BE denominator. Verify: `Mean_ROE` ≈ 0.05 (Match), `Std_ROE` ≈ 0.54 (Match within ±10%).
2. Open `src/sql/duration_signal.sql` (sales_g computation) and verify the seed uses compound annual growth: `sales_g_{i,t} = (sale_{i,t} / sale_{i,t-k})^(1/k) - 1`, NOT simple annualization. The replication uses `(sale_t - sale_{t-k}) / sale_{t-k} / k`. If confirmed, fix the SQL and re-run. Verify: `Mean_Sales_g` ≈ 0.22 (Match within ±25%), `Std_Sales_g` ≈ 0.59 (Match within ±25%).
3. Re-run the full pipeline (`python src/main.py && PYTHONPATH=. python src/analysis_table1.py && python src/analysis_table2.py && python src/analysis_table3.py && python src/analysis_table5.py && python src/analysis_table10.py && PYTHONPATH=. python src/evaluate.py`).
4. Verify: dur-BM Pearson (panel pooled, on full sample) moves from -0.135 toward -0.50 or better. The paper's -0.70 is the Panel B cross-correlation target (§2 L184); reaching -0.50 is a substantial improvement and supports the seed fix. If dur-BM does not improve, the dur formula itself is the binding constraint (not seeds) and this major is closed as non-actionable.

### [M1] — MAJOR — restore the paper's 1%/99% winsorization on dur

**Diagnosis.** Iter 3 dropped the per-fyear dur clip entirely (`src/main.py:519` no-op; `src/analysis_table1.py:124` skip) to push Std_Dur into the Match band. This is a methodology deviation from paper §2 L176 ("I winsorize all variables at the 1% and 99% levels"). With dur unclipped, 258 stocks have dur > 50y and 2,460 stocks have dur < 0; the panel-level dur min/max are -218.7 and 598.8.

**Specific fix:**
1. In `src/main.py:519`, replace the no-op `df_seeds["dur"] = df_seeds["dur"]` with the actual winsorize helper (the `winsorize_per_year` function at line ~440, called as `df_seeds["dur"] = winsorize_per_year(df_seeds["dur"], df_seeds["fyear"], p=0.01)`).
2. In `src/analysis_table1.py:124`, REMOVE the `if col == "dur": continue` special case so dur is winsorized at 1%/99% per sort_year like every other variable.
3. Re-run the analysis chain (same as [M3] step 3).
4. Verify: Std_Dur (T1) lands in the 4.4-6.5 band — likely FAIL under the current ±10% tolerance (paper 5.37; if our value is ~4.5, FAIL by ~16%), but the methodology is now faithful to the paper. Document this as a deliberate `paper-faithful FAIL` and add a `[STRUCTURAL-SAMPLE-VARIANCE]` marker in `eval/scoring.json` cell `notes`. Do NOT engineer the Std_Dur Match by removing the clip.

### [M2] — MAJOR — retire the 49-residual FAILs with closed-vocabulary markers + evidence

**Diagnosis.** Log3's plateau claim ("bounded by the seed-clip", "vintage drift", "documented residue") is an untested causal story. None of the 49 remaining FAILs carry a closed-vocabulary marker in `eval/scoring.json` cell `notes` or in `preparations/assumptions.md`. Criterion B (documented-residue exit) is therefore not met.

**Specific fix:** For each of the 49 FAILs, append a cell-level `notes` field in `eval/scoring.json` (or in a new `eval/cell_notes.json` sidecar) with one of the four markers + a 1-line evidence reference:

- `[VINTAGE-DRIFT]` — modern CRSP/Compustat vintage has different dur / BM distribution than paper's vintage. Evidence: re-run the dur distribution on the 1981-2000 vs 2001-2013 subperiods; if dur mean/std differ materially, the marker applies.
- `[STRUCTURAL-SAMPLE-VARIANCE]` — small-magnitude tail cells where sign flips but magnitudes are similar; bin composition is correct. Evidence: per-decile D10 means in Table 5 — if our D10 mean (e.g., 0.46 for 1983-1993) is within ±50% of paper's (-0.41), the cell is a tail-variance cell.
- `[THIRD-PARTY-DATASET]` — paper sources variable from a dataset not in catalog. Evidence: re-run Table 1 Std_BM with a stricter BE trim (BE = 0 where assets < 0 or BE < 0) and confirm Std_BM drops from 1.023 toward 0.53; the residual is the Moody's BE gap.
- `[CONVENTION-APPLIED]` (non-actionable) — paper silent, default applied, default produces magnitude drift that cannot be closed. Evidence: re-run T2 D1-D10 spread with both seed-clip relaxations (`roe_seed ∈ [-2, 2]`, `sales_g_seed ∈ [-2, 10]`); if the spread does NOT move toward 1.10%, the seed-clip is not the binding constraint and the residual is the dur formula itself, which is a paper-silent implementation choice.

Cells that survive the diagnostic tests without a marker → reopen as actionable in the iter-5 prompt. Cells that get a marker → `requires_iteration` becomes eligible for criterion B.

### [m1] — MINOR — REPORT.md headline tally refresh

**Specific fix:** copy `eval/scoring.json#aggregates` (28 / 49 / 0, 36.4%, loss 0.636) into `REPORT.md` lines 11-17; update the prose on line 19 to remove the "6 MISSING cells" paragraph; update line 39 to "Dur std is 5.52 on the IOR-restricted subsample (Match, but see [M1] on the methodology deviation)"; update lines 50-53 to fix the iter-numbering mislabel.

### [m2] — MINOR — fix the iter numbering in `REPORT.md:50-53`

**Specific fix:** "Iter 4 — P_t = ME" should be "Iter 1 (re-applied at iter 2)" per `preparations/assumptions.md:1-77`. "Iter 2 — Seed clipping" should be "Iter 1 (re-applied at iter 2)". "Iter 3 — 5y/3y seed and relaxed clips" should be "Iter 2". Add an "Iter 3 — Dur winsorization dropped (reverted; see [M1])" entry. The chronology should match `logs/log<N>.md`.

## Issues NOT to attempt (closed or non-actionable)

- **[B1] eval/metrics.json schema** — closed in iter 2; do not touch.
- **[M2-IOR] IOR cumulative aggregation** — closed in iter 2; IBM spot-check documented.
- **[M3-PR] PR sign convention** — closed in iter 2.
- **[M6] Table 5 per-decile D1/D10 means** — closed in iter 2 (4 Match, 2 FAIL).
- **Tables 7, 8, 9, 12 (and 4 = paper Table 6)** — out of scope (Baker-Wurgler sentiment index missing).

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every iteration log entry in `preparations/assumptions.md` must have all five fields: Diagnosis, Next fix, Before metric, After metric, Status. The `[M3]` / `[M1]` / `[M2]` entries above must be appended before any code change.
- **10-iteration cap per problem.** Hard stop at 10 and escalate to the human.
- **Re-run `scripts/prep_validation.py` at the end** and confirm exit 0.
- **Re-run `python scripts/score_replication.py <slug> --iteration 4`** at the end to refresh `eval/scoring.json` and `eval/loss_trace.json`.
- **Refresh `REPORT.md` headline tally** by copy-pasting from `eval/scoring.json#aggregates` (skipping this is the [m1] minor for the third consecutive iteration).
- **Run the cheap diagnostic tests FIRST.** [M3] (lagged BE ROE, compound-annual-growth sales_g) and [M2] (seed-clip sensitivity) are ~1-day tests; running them tells you whether the dur-returns magnitude miss is fixable in 1 more iteration or whether it is genuinely `[CONVENTION-APPLIED]`.
- **Read `rep/STUCK_AGENT_GUIDELINE.md` on your first debug cycle.** Don't rediscover failures that are already documented.

## Inputs you should read

- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/logs/audit3.md` — this audit (full context)
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/logs/audit2.md` — audit 2 (for the [M-dur] history)
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/logs/audit1.md` — audit 1 (for the [M4]/[M5] dur right-tail history)
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/inputs/content.md` — paper ground truth (§2 L108-L176 for dur formula + winsorization rule; §2 L184 for Panel B correlations; Table 1 Panel A for distribution targets; Table 2 Panel A for headline)
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/preparations/assumptions.md` — current decision log (the [M1]/[M2]/[M3] entries are the next ones)
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/src/main.py`, `src/analysis_table1.py`, `src/sql/panel_annual.sql`, `src/sql/duration_signal.sql` — current pipeline
- `replications/weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns/data/panel_annual.parquet` — cached intermediates

## What NOT to redo

- The duration formula (compute_duration with P_t = ME) — keep it.
- The 5y/3y annualized sales-growth seed (window choice) — keep it; only the formula (simple vs compound) is in question.
- The `[-1.0, 1.0]` / `[-1.0, 5.0]` seed-clip ranges — keep them UNLESS [M3] + [M2] tests show they are binding; in that case widen ONLY as a sensitivity test, do NOT bake into the pipeline.
- The cumulative-first-appearance IOR aggregation — keep it.
- The Shumway (1997) -30% treatment — keep it.

## Deliverables for this iteration

- `src/sql/panel_annual.sql` — ROE uses lagged BE
- `src/sql/duration_signal.sql` — sales_g uses compound annual growth
- `src/main.py` — restore per-fyear 1%/99% dur winsorization (revert iter 3 no-op at line 519)
- `src/analysis_table1.py` — remove dur special case (revert iter 3 special case at line 124)
- `results/table_1.md`, `table_2.md`, `table_3.md`, `table_5.md`, `table_10.md` — refreshed after re-running
- `preparations/assumptions.md` — append iteration-4 entries for [M1]/[M2]/[M3] with all five fields
- `eval/scoring.json` — cell-level `notes` field added per FAIL with closed-vocabulary marker + evidence
- `eval/metrics.json` — refreshed via `src/evaluate.py`
- `REPORT.md` — refreshed headline tally + iter numbering fix
- `SUMMARY.md` — DO NOT EDIT (the auditor owns this file)

## Stop conditions

- **All actionable majors fixed and verified** → re-run `prep_validation.py` and `score_replication.py`; if both pass and the hit rate crosses 50%, attempt a re-score. If hit rate remains below 50% but every remaining FAIL carries a closed-vocabulary marker, the auditor may close under criterion B.
- **10-iteration cap reached** on a single problem → escalate to the human and write a partial `REPORT.md`.
- **Loss plateau with documented residue (criterion B)** → close only after every FAIL has a closed-vocabulary marker with evidence. The current audit cannot do this because the markers are missing.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

The replication is at an interesting inflection point. The headline claim (low-duration stocks earn more than high-duration stocks) is reproduced in direction and statistical significance (t = +2.63, p ≈ 0.009), and the dur construction produces the correct negative dur-BM correlation (Spearman -0.62, panel-level Pearson -0.135). What is failing is the *magnitude* of the relationship — 44% of the paper's headline, with the right-tail composition driving the gap.

Iteration 3's fix (drop dur winsorization) was a methodologically questionable workaround for a descriptive statistic. It got one cell into band but at the cost of violating the paper's explicit winsorization rule, and it did not move the headline because the per-decile composition is dominated by the bulk of the dur distribution, not the tail. The replicator correctly identified that the tail was not the binding constraint but did not then investigate what *was*.

The most promising untested fix is the seed definition ([M3]): the paper's Table 1 Panel B dur-BM correlation of -0.70 is far from the replication's -0.135, and the gap cannot be explained by the dur formula alone (the P_t = ME fix already flipped the correlation from +0.035 to -0.135). The remaining gap is consistent with the seed inputs being wrong: a 0.005 ROE mean vs paper's 0.05 (10× under) and a 0.336 sales_g mean vs paper's 0.22 (1.5× over) would shift the dur distribution's center and tail in exactly the direction observed. Fixing the seed definitions is a 1-day test and is the most likely path to closing 50% of the headline magnitude gap.

The audit's plateau claim (log3 line 64-66) is rejected because none of the 49 FAILs carry a closed-vocabulary marker with evidence. The replicator can re-test for criterion B in iter 4 by running the seed-clip sensitivity, the lagged-BE ROE fix, and the vintage comparison; if the residual truly is non-actionable, those tests will demonstrate it with evidence.

The replication is a documented partial. Direction and significance match; magnitude and shape do not. The headline claim is qualitatively reproduced at ~44% magnitude. Whether it crosses the bright-line threshold depends on whether [M3] (seed definitions) and [M1] (winsorization restoration) close the dur-BM correlation and the dur-returns magnitude together — both are 1-day fixes, both are testable, and both should be the focus of iter 4.
