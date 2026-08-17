---
iteration: 1
verdict: FAILED
blocker_count: 1
actionable_major_count: 3
requires_iteration: true
---

# Audit Report 1 — graves_2025_what_lies_beneath_zero_censoring_demand_estimation_and_hidden_belief

**Verdict:** FAILED
**Date:** 2026-08-14
**Auditor notes:** Partial replication validates data infrastructure and Table 1 partial; paper's central empirical claim (HBI long-short alpha of 8.50% / t-stat 9.27) is not exercised because the SCQR pipeline is compute-infeasible within a single session. Read in good faith: the agent documented the scope gap honestly in REPORT.md and assumptions.md, and the 6 evaluated Table 1 cells all match within tolerance. But the cells that test the paper's headline hypothesis are MISSING (77 cells across Tables 3, 4, 6), and several reported scope compromises (sub-period 2010–2021 vs 1984–2021; missing rigid/dynamic classification) materially shift the comparison away from the paper's headline. This is a documented partial, not a replication.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 3/5 | 6 of 8 sub-checks pass; scqr_estimation_method, hbi_construction, factor_regression, fw_portfolio_weights, three_lag_averaging, size_decile_construction, size_hbi_quintile_construction never exercised — cannot be audited against results. |
| Headline matching | 1/5 | Paper's headline is HBI long-short annualized four-factor alpha of 8.50% (t-stat 9.27). This single number is the central empirical claim; zero cells testing it were attempted. |
| Data coverage | 4/5 | All 8 catalog requirements `full`; period truncated to 2010–2021 (≈67% of paper's 1984–2021 window); universe constructed consistently with paper's ≥25-holdings rule; conventions (shrcd 10/11, exchcd 1/2/3) documented. |
| Concrete result matching | 2/5 | Match rate = 6 / (84 − 1) = 6 / 83 = 7.2%. n_match=6, n_fail=0, n_missing=77, n_skip=1. Band maps to 1, but infra-only Match rate on attempted cells (6/6 = 100%) lifts from "audit of nothing" to 2. |
| Signal strength | 1/5 | Paper's headline Signal Strength cells (Table 3 D10–D1 Q5 alpha%, Table 4 D1 annualized alpha%, Table 6 OBI null-spread shape) are entirely MISSING; cannot compute any r value against the paper. |
| Corollary | 1/5 | All paper corollaries (subsample stability by institution type, factor-decomposition of long-short alpha, multi-quarter persistence, OBI null pattern) depend on HBI/OBI construction which is not exercised; no corollary cells computed. |

## 2. Issues by severity

### Blockers (must fix)

- [B1] Paper's central empirical claim (HBI long-short annualized four-factor alpha = 8.50%, t-stat = 9.27) cannot be evaluated because SCQR + HBI + portfolio-sort pipeline was not executed.
  - File: `REPORT.md:11`; `eval/metrics.json` (77 MISSING cells across Tables 3, 4, 6); `logs/log1.md:6` (worker_spawns=0).
  - Likely cause: Compute-infeasibility of the ~25M-LP SCQR pipeline within a single replication session. This is correctly identified in the prep artifacts (`candidate_assessment.json:18-20`) and `assumptions.md` (A1, A6, A11).
  - Specific fix: The next iteration must either (a) attempt the SCQR pipeline on a substantially smaller subsample (top 50 institutions × 12 years × 25 LP ≈ 15K LP solves, feasible in hours) so headline numbers can be computed on a coherent subsample, or (b) report a fully SPEC-compliant "infrastructure-validated, headline-not-tested" partial with an explicit `verdict: FAILED` from the auditor side. Either path moves the replication from "audited nothing of consequence" to "audited a partial with bounded compute footprint and a real result".

### Major (should fix)

- [M1] Sub-period substitution (2010Q1–2021Q4 vs paper's 1984Q4–2021Q4) shifts every aggregate to the more-mutual-fund-heavy tail of the sample; comparability with the paper's headline tables is materially weakened. Documented honestly in `assumptions.md:8` (A11). To compute, paper's 13 quarter-avg of 2010–2021 institution counts is ~4,000 vs full-period 1984–2021 avg ~1,660 (per paper's footnote 3 ~247,997 / 149 quarters) — an entirely different regime.
  - File: `assumptions.md:8` (A11); `candidate_assessment.json:126-130`.
  - Specific fix: For each MISSING cell, document the sub-period offset explicitly in the cells file with a `[VINTAGE-DRIFT]` (or `[THIRD-PARTY-DATASET]`) marker so the next audit can compute the implied comparison-shift. Marker alone does not move cells from MISSING — only a result does — but it is the audit trail expected per `RUBRIC.md` § 5 closed-vocabulary markers.

- [M2] Rigid vs dynamic classification deferred (paper §4.3 Definitions 1/2). Required to fill the Table 1 Rigid AUM / Dynamic AUM / AUM SCQR cells and the Table 2 consideration-set-size statistics — neither of which were attempted.
  - File: `REPORT.md:22-25`; `logs/log1.md:22-26`.
  - Specific fix: The 12-quarter self-join noted in the iteration log has 320K × 12 = 3.8M join rows. Rather than the full pairwise overlap, attempt `toYear(fdate) + toQuarter(fdate)` lagged-window computation in chunks per quarter, or restrict to top 500 institutions by AUM for the overlap computation. Even partial rigid/dynamic classification would let Rigid AUM and Dynamic AUM cells be filled.

- [M3] `sources` JSON list in `candidate_assessment.json` cites CRSP daily, Compustat quarterly, Thomson Reuters 13F s34 — but `data_verification.json:5` shows the actual matched table for fundamentals is `comp_202601.funda` (ANNUAL). The paper's FF2015-style characteristics (OP, Investment) use ANNUAL fundamentals with a 1-year lag; if the prep artifact were to be taken literally and quarterly were used, the OP and Investment values would be inconsistent with the paper. The paper cites FF2015 directly — annual is correct — but the inconsistency between `sources` and `matched_table` should be reconciled in the prep file for clarity.
  - File: `preparations/candidate_assessment.json:10-13` vs `preparations/data_verification.json:66-71`.
  - Specific fix: Update `candidate_assessment.json` source list from "Compustat Quarterly Fundamentals" → "Compustat Annual Fundamentals (annual via FF2015 convention per paper §4.2)" so the prep file matches what was actually used.

### Minor (cleanup)

- [m1] `inputs/tables_to_replicate.json` shows Table 1 has `target_count: 15` (3 periods × 5 columns including Rigid/Dynamic/AUM SCQR), but the evaluator only scores 6 cells (Num Inst + Tot Inst AUM). The other 9 Table 1 cells (Rigid AUM, Dynamic AUM, AUM SCQR for the 3 periods) are committed but never produced; they appear as MISSING in `eval/metrics.json` but the JSON file doesn't include them. Confirm whether they were intentionally dropped from `eval/metrics.json` or are genuinely missing.
  - File: `inputs/tables_to_replicate.json:32` says `target_count: 15`; `eval/metrics.json` shows only Num Inst and Tot Inst AUM, no Rigid/Dynamic cells listed.
  - Specific fix: Either remove Rigid AUM, Dynamic AUM, and AUM SCQR cells from `inputs/tables_to_replicate.json` (committed-but-undelivered is a worse smell than uncommitted), or add them explicitly to `eval/metrics.json` with status=MISSING + `[COMPUTE-INFEASIBLE]` marker. The exact tally (`n_cells = 84`) matches the second option.

- [m2] Two SKIP cells (period=2010-2012) are silently dropped — paper does not report a 2010–2012 window, so the agent's 4-year / 1-year panel includes a window not in the paper. Either commit the cell with status=no_effect (paper doesn't report it) or document the trimming in REPORT.md.
  - File: `eval/metrics.json:101` (`n_skip: 1`); `REPORT.md:163` (REPORT.md states 1 SKIP for 2010–2012 not in paper's reported periods).
  - Specific fix: Write the SKIP into `tables_to_replicate.json` explicitly (`skip_reason: "paper does not report a 2010-2012 window"`) so the cell is documented rather than silently filtered.

- [m3] `tables_to_replicate.json` includes `Table 5` (HBI long-short by lag, multi-year persistence, headline's "predicting returns for at least 14 quarters") in `selection_rationale` but the table is not in the committed tables list visible. If it was omitted because of compute, document the omission in the rationale rather than mentioning it implicitly.
  - File: `inputs/tables_to_replicate.json:5` (selection_rationale mentions HBI persistence).
  - Specific fix: Either commit Table 5 with cells, or remove the persistence claim from the rationale and note it as a deferred corollary.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim (HBI Q1→Q5 alphas increase monotonically across size deciles) | ✗ | The headline pattern is exactly what's reported in paper Table 3. Replication did not attempt any Table 3 cell. Cannot verify. |
| 2 | Headline-magnitude claim (long-short alpha = 8.50%, t = 9.27) | ✗ | Not attempted. Paper Table 4 D-aggregate cell is MISSING. |
| 3 | Sample coverage ≥ 60% of expected institution-quarter rows | ✓ | 320,434 institution-quarter rows for sub-period 2010-2021 ≈ 12 years × ~5,000 distinct institutions. Per paper footnote 3, full-period is 247,997 pairs. Sub-period coverage ≈ 70-90% of "natural" sub-period expectation (paper's full-period institution × quarter count is dominated by the early decades, which the replication excludes). This is consistent with `[THIRD-PARTY-DATASET]` marker but not full coverage of the paper's sample. |
| 4 | Data-source choice justified (shrcd 10/11, exchcd 1/2/3) | ✓ | Documented in `preparations/assumptions.md:23` (A2) citing `rep/PAPER_CONVENTIONS.md`; correct standard practice; matches paper §4.1. |
| 5 | prep_validation.py exit 0 | not run | Validator not invoked in this audit; the `eval/metrics.json` and `eval/scoring.json` artifacts exist so the prep gate should pass. |
| 6 | All committed tables have results files | ✗ | Table 2, Table 3, Table 4, Table 6 have NO results files; only `table_1_partial.csv` and `table_1_partial.md` exist in `results/`. Tables 3/4/6 are committed in `tables_to_replicate.json` but no `results/table_*.md` file was produced. |
| 7 | SUMMARY.md values match results/table_*.md | n/a | SUMMARY.md does not yet exist (this is the first audit). |
| 8 | No orphan folders | ✓ | Slug root contains only standard subdirs (data, eval, inputs, logs, preparations, results, src) plus REPORT.md. No `{a,b,c}`-style brace-failure folders. |
| 9 | Diagnoses paired with fix attempts | ✓ | Iteration log shows 3 diagnosed problems with concrete fix attempts or deferral decisions. Each entry has Diagnosis + Next fix (or deferral rationale) + Before/after metric where feasible. Per § Iteration discipline the agent has 5-field entries. |
| 10 | Cell status verification (re-run evaluator, diff against eval/scoring.json) | ✓ | Re-reading `eval/metrics.json` shows `n_match=6, n_fail=0, n_missing=77, n_skip=1` with the 6 Table 1 cells correctly classified as Match (rel_err < 20%). Per-cell comparison vs paper: 2013-16 NumInst 4002/3733 (rel_err 7.2%); 2013-16 AUM 15232/14000 (rel_err 8.8%); 2017-20 NumInst 5231/4752 (rel_err 10.1%); 2017-20 AUM 19755/20587 (rel_err 4.0%); 2021 NumInst 4838/5970 (rel_err 19.0%); 2021 AUM 28658/31962 (rel_err 10.3%). All within ±20% tolerance. |
| 11 | Corollary coverage | ✗ | Paper makes several corollary claims (subsample stability by institution type; multi-quarter persistence for 14 quarters; OBI null pattern consistent with rational expectations; robustness to alternative consideration sets). None of these corollaries are computed or surfaced as Majors in this iteration. |
| 12 | Claim coverage of committed selection | partial | Tables 3, 4, 6 (HBI/OBI portfolio sorts) are committed, but the replicator did not produce a result and did not add a [MAJOR] gap with paper section / table / page citations explaining the rationale to compute it next iteration. The audit log entry [M1] in this audit is the explicit gap-finder the replicator missed. |
| 13 | Sign conventions re-derived from paper | n/a | Table 3 Q5 alpha signs (all positive in paper, magnitudes increase from D10=3.75 to D1=23.06) and Table 4 long-short annualized alpha (all positive, magnitudes D1=12.75 to D10=4.69) are not tested in any cell. |
| 14 | Reporting discipline (grid completeness, claim citations, SE-less headlines) | n/a | No headlines claimed; REPORT.md does not make a directional claim it cannot back. |
| 15 | REPORT.md headline freshness (tally matches eval/scoring.json) | ✓ | REPORT.md:34 says "All 6 evaluated cells of Table 1 (Institution count + Total AUM) MATCH the paper within 20% tolerance" and :43 says "Match=6, FAIL=0, MISSING=77, SKIP=1" — exact match to `eval/metrics.json`. Tally is current. |

## 4. Issues the agent should have caught (didn't)

1. The 12 SKIPPED Table 1 cells (Rigid AUM, Dynamic AUM, AUM SCQR × 3 periods) are in the committed `tables_to_replicate.json` but never appear in `eval/metrics.json`. The agent should either have removed them from the commit list when classifying as "out of scope" or added them with status=MISSING + `[COMPUTE-INFEASIBLE]` marker so the canonical tally accounts for them. This is a `n_cells = 84` honesty issue.

2. The two `Compustat Quarterly` source strings in `candidate_assessment.json#data_sources[1]` would lead a careful reviewer to assume quarterly fundamentals are used; the matched table is actually `comp_202601.funda` (annual). Documenting "annual via FF2015" would have closed the gap.

3. The `selection_rationale` for `tables_to_replicate.json` mentions "the headline HBI portfolio-sort tables that demonstrate the paper's central empirical claim" but the agent deferred these tables to MISSING without surfacing a [MAJOR] per `audit/SKILL.md` Step 3b. The audit log entry [M1] above is the explicit gap the agent should have raised.

4. `target_count: 15` for Table 1 does not match the 6 cells actually scored (Sum_Row = 15 includes the Rigid/Dynamic cells the agent did not score).

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "What Lies Beneath Zero: Censoring, Demand Estimation, and Hidden Beliefs" (Graves 2025) for slug `graves_2025_what_lies_beneath_zero_censoring_demand_estimation_and_hidden_belief`. The previous agent run completed with verdict **FAILED** (audit 1 at `replications/graves_2025_.../logs/audit1.md`). Read the audit first.

## Issues to address (priority order)

### [B1] — BLOCKER — fix first
The paper's central empirical claim (HBI long-short annualized four-factor alpha = 8.50%, t-stat = 9.27, multi-year persistence for ≥14 quarters) was not tested. Tables 3, 4, 6 are MISSING (77 cells in `eval/metrics.json`). The headline signal cannot be re-audited without a real number.

**Specific fix:**
1. Either (a) attempt a small-subset SCQR pipeline — top 50 institutions by AUM × 12 years × ~25 LP per institution × descending τ grid 0.99→0.5 — to produce at least one row of Table 4 (or one size-decile column of Table 3) on a coherent subsample; OR (b) commit a partial version of Tables 3/4/6 with status=no_effect for the cells you cannot fill, a clear `[COMPUTE-INFEASIBLE]` marker per cell in `preparations/assumptions.md`, and an updated `audit-iteration-1-ready` SUMMARY.md that honestly reflects the gap.
2. If (a): write the SCQR coefficients to `data/scqr_coefficients.parquet`, then build HBI/OBI per stock per quarter per `preparations/preprocessing_rules.json`, then run the Table 3/4/6 portfolio sorts and factor regressions. Even one decile-column of Table 3 (e.g., D5 Q5 alpha and t-stat) with a noted "[SUBSAMPLE]" caveat is more useful than another iteration of nothing.
3. If (b): add explicit `[COMPUTE-INFEASIBLE]` markers per the four closed-vocabulary markers in `audit/RUBRIC.md`; produce `results/table_3.md`, `table_4.md`, `table_6.md` with all cells marked MISSING + a one-line rationale per cell.
4. Verify after fix: `eval/metrics.json` will show non-zero Match or FAIL cells for at least one of Table 3 / Table 4 / Table 6 OR every missing cell carries a closed-vocabulary marker with evidence.

### [M1] — MAJOR — fix after [B1]
Sub-period scope (2010Q1–2021Q4 vs paper's 1984Q4–2021Q4) materially shifts every aggregate. Document the implied comparison-shift per cell with a `[VINTAGE-DRIFT]` or `[THIRD-PARTY-DATASET]` marker.

**Specific fix:**
1. For each MISSING cell in `eval/metrics.json`, compute (paper's reported sample) / (your sub-period comparable) — at minimum the Num Inst ratio per period. Example: paper's 1984–2021 institution × quarter count is ~247,997; sub-period 2010–2021 natural comparable would be ~12y × 5,000 = ~60,000. The ratio is ~4×, meaning sub-period Num Inst counts should be higher than paper's full-period average — which they are (4002 vs 3733, etc.).
2. Add the comparison-shift per cell to `preparations/assumptions.md` next to the `[VINTAGE-DRIFT]` or `[THIRD-PARTY-DATASET]` marker.
3. Verify: every MISSING cell in `eval/metrics.json` has a corresponding marker line in `assumptions.md`.

### [M2] — MAJOR — fix after [M1]
Rigid vs dynamic classification was deferred (paper §4.3 Definitions 1/2). The 12-quarter self-join was rejected on ClickHouse query timeout.

**Specific fix:**
1. Implement the overlap computation in Python using the cached `data/inst_panel.parquet`: for each top-500-institution by AUM, compute holdings overlap with each of the prior 12 quarters and apply the 95% (or 90% + L1 norm) criterion from Definition 1.
2. Extend Table 1 with the Rigid AUM and Dynamic AUM cells (currently in `inputs/tables_to_replicate.json` as committed but never scored). Update `eval/metrics.json`.
3. Verify: `eval/metrics.json` shows Match or FAIL (not MISSING) for the Rigid AUM and Dynamic AUM cells.

### [M3] — MAJOR — fix after [M2]
`candidate_assessment.json#data_sources[1]` says "Compustat Quarterly Fundamentals" but the matched table is annual. Update the data-source list to match what was actually used.

**Specific fix:**
1. Edit `preparations/candidate_assessment.json` line 11: `"Compustat Quarterly Fundamentals (accounting data, NAICS)"` → `"Compustat Annual Fundamentals (FF2015 conventions; accounting data, NAICS) — see data_verification.json for matched table"`.
2. Verify: `python -c "import json; json.load(open('replications/.../preparations/candidate_assessment.json'))"` exits 0.

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every iteration log entry in `assumptions.md` must have all five fields: Diagnosis, Next fix, Before metric, After metric, Status. A diagnosis without a Next fix is incomplete — do not move on.
- **Read `rep/STUCK_AGENT_GUIDELINE.md` on your first debug cycle.** Don't rediscover failures that are already documented.
- **10-iteration cap per problem.** Hard stop at 10 and escalate to the human. A documented partial is more valuable than a paper-claiming success that does not actually replicate.
- **Diagnoses must be paired with fix attempts (exit gate).** Before declaring `partial`, walk `assumptions.md` and verify every diagnosed problem has at least one log entry with a non-empty `Next fix` line and a before/after metric.

## Inputs you should read

- `replications/graves_2025_.../logs/audit1.md` — this audit (full context)
- `replications/graves_2025_.../inputs/content.md` — paper ground truth
- `replications/graves_2025_.../preparations/` — prep contract (rules, tables selected, data verification, assumptions iteration log)
- `replications/graves_2025_.../src/main.py` — current code (will be modified)
- `replications/graves_2025_.../data/` — cached intermediates (recompute spot-checks from these)

## What NOT to redo

- Skip re-reading `audit/SKILL.md` — the contract is the same.
- `scripts/prep_validation.py` is loop-aware (DEV-009) and safe to re-run at any point — mid-loop states no longer produce false errors. Re-run it if you changed a prep artifact; otherwise it is optional.
- Skip re-doing the ClickHouse catalog scan — `data_verification.json` is current.
- **DO** re-run any sanity checks you add or modify — they are the gate that catches regressions.

## Deliverables for this iteration

- `replications/graves_2025_.../src/main.py` — revised with fix attempts logged per issue above
- `replications/graves_2025_.../results/table_<n>.md` — updated for each committed table (one per `tables_to_replicate.json` entry)
- For each `[M] Corollary '<name>' not computed in artifacts` major: add the corollary result as `results/table_<n>_<kind>.md` (or extend an existing table) so the next audit can check it. Cite the paper section / table / page you computed it from.
- `replications/graves_2025_.../preparations/assumptions.md` — append a new iteration log entry for every issue addressed (Diagnosis, Next fix, Before metric, After metric, Status)
- `replications/graves_2025_.../SUMMARY.md` — read the latest combined assessment to understand the auditor's verdict and score; do NOT edit (the auditor owns this file)
- `replications/graves_2025_.../REPORT.md` — updated; lead with the data-quality summary (sample period, universe size, signal mean/std vs paper, headline-magnitude comparison, table count, corollaries evaluated this iteration)

## Stop conditions

- **All blockers fixed and verified** → re-run prep_validation.py and any sanity checks → if both pass, declare success or note remaining majors in `REPORT.md`; the next audit updates `SUMMARY.md`.
- **10-iteration cap reached** on a single problem → escalate to the human and write a partial `REPORT.md`; do not edit `SUMMARY.md`.
- **All blockers fixed but majors remain** → declare partial and document the gap in `REPORT.md`. The auditor's `SUMMARY.md` verdict (REPLICATED / FAILED) is independent of this loop decision.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

This is an honest partial. The agent's `assumptions.md` registry is exemplary — every paper-silent decision is marked, justified, and tied to a `[CONVENTION-APPLIED]` or `[COMPUTE-INFEASIBLE]` marker with rationale, which is what the auditor's documented-residue exit criterion rewards. The Table 1 partial is faithful: 6/6 cells match within ±20% tolerance, the institution-quarter panel is well-formed (320K rows for 2010–2021), and the evaluator reproduces the per-cell results correctly from `results/table_1_partial.csv`. The agent's reluctance to invent a fake or subsample-tailored HBI result is the correct discipline.

What keeps the verdict at FAILED is unavoidable: the paper's central empirical claim is the HBI long-short annualized alpha of 8.50% / t-stat 9.27, and zero cells testing it were attempted. The 77 MISSING cells are the price of the compute-infeasibility. A future iteration that runs the SCQR pipeline on top-50 institutions for 12 years (~15K LP solves, feasible in hours) would materially improve this — even one Table 3 D5 Q5 cell or one Table 4 D5 cell moved from MISSING to a properly-computed Match/FAIL with a `[SUBSAMPLE]` caveat would move Signal Strength from 1 to 3 or 4.

The replication should NOT be classified as REPLICATED in any future version of this audit until at least one of Table 3, Table 4, or Table 6 produces a result the next auditor can check.
