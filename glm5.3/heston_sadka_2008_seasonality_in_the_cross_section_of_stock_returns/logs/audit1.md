---
iteration: 1
verdict: REPLICATED
blocker_count: 0
actionable_major_count: 1
requires_iteration: true
---

# Audit Report 1 — heston_sadka_2008_seasonality_in_the_cross_section_of_stock_returns

**Verdict:** REPLICATED
**Date:** 2026-09-08
**Auditor notes:** Strong first-iteration replication (87.6% Match, 0 MISSING, all 8 tables); one diagnosed-but-deferred actionable major (Table 4 t-stat x100 unit error) and one minor REPORT staleness issue.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 4 | 7/8 sub-checks pass with substantive documentation; sub-check 8 (inference reproduction) fails on the T4 t-unit bug (t = 362.2 vs paper 3.57). |
| Headline matching | 3 | C1/C2 sign, shape, and pulse pattern all correct; annual spreads within ~15%, but y1 drift is 25–50%+ (y1 All spread 0.80 vs 1.46). |
| Data coverage | 5 | Period exact (1945–2002 panel; 1963–2002 WRSS; 1965–2002 strategies); universe validated against paper's own Fig-1 diagnostics (Jan-1965 N=1,922 < 2,000); CRSP/Compustat/FF sources; 0 (permno,month) duplicates. |
| Concrete result matching | 5 | 1,149 / 1,312 committed = 87.6% Match (canonical scorer re-run by auditor, identical) — band ≥85%. |
| Signal strength | 2 | Worst headline cell: y1 Nonannual EW spread r = 0.455/1.17 = 0.39 (sign matches, documented [STRUCTURAL-SAMPLE-VARIANCE]); also y11_15 VW annual r = 1.23. Band 2. |
| Corollary | 5 | Corollary tables T3–T8: 720 / 864 committed cells Match = 83.3% — band ≥80%; every paper corollary (FF3, sigma^2_mu, size/industry/calendar/event independence) computed. |

Overall = (4+3+5+5+2+5)/6 = **4.00**. Bright line: overall ≥ 3.0 AND no dimension = 1 → REPLICATED.

## 2. Issues by severity

### Blockers (must fix)

None.

### Major (should fix)

- [M1] Table 4 t-statistics inflated by exactly x100 — diagnosed, fix specified, deferred only because the 10-inner-iteration cap was reached. `src/table4.py:66-68`: `mean = v.mean() * 100.0` (table units) but `se = v.std(ddof=0) / sqrt(500)` (decimal^2), so `t = mean / se` carries a x100 unit mismatch. `results/table_4.md` prints t = 362.20 / -25.15 / -62.39 vs paper 3.57 / -0.26 / -0.65; dividing by 100 gives 3.62 / -0.25 / -0.62 (within 1.5–4% on all three). Two of three groups flip significance category (all/nonannual print as |t|>25 where the paper reports n.s.). Actionable: next outer iteration applies the one-line fix already specified in `preparations/assumptions.md` iteration 10.
  - File: `src/table4.py:66-68`; `results/table_4.md:7-9`; `preparations/assumptions.md` "Iteration 10 — … T4 t-unit bug DIAGNOSED".
  - Likely cause: unit asymmetry between mean (x100) and SE (decimal^2).
  - Specific fix: compute mean and SE in the same units (or `t = (mean/100) / se`); expected outcome t ≈ -0.25 / -0.62 / 3.62 → all three FAIL→Match.

### Minor (cleanup)

- [m1] REPORT.md reversal-spread values are stale relative to `results/table_2.md`: REPORT quotes "-0.86/-1.19/-0.50/-0.23/-0.38" but the final table/scoring carry -1.02 (y2_5 All), -1.20 (y2_5 Nonannual), -0.41/-0.69 (y6_10), -0.23, -0.38. The canonical cells all Match; the prose just predates the final Rule-B regeneration.
  - File: `REPORT.md:28` vs `results/table_2.md:10-21`.
  - Specific fix: re-copy the five reversal-spread values from `results/table_2.md` when refreshing REPORT.md next iteration.
- [m2] REPORT.md "VW spreads 7 of 8 Match" is inconsistent with the scored grid (9 VW spread cells in scoring.json, 9/9 Match). Same regeneration-hygiene bucket as [m1].
  - File: `REPORT.md:28` vs `eval/scoring.json` (t2_vw_* cells).
  - Specific fix: state the scored count, not a hand tally.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim | ✓ | y1 All decile profile increases 1.06→1.85; annual rows monotone increasing; long-horizon All/Nonannual reversed (winner decile low) — matches paper's shapes in `results/table_2.md`. |
| 2 | Headline-magnitude claim | ✓ | gamma_1 = -4.99 vs paper -5.03 (r=0.99); gamma_12 = 2.79 vs 2.61 (r=1.07); annual EW spreads r = 0.94–1.15 across all five intervals. |
| 3 | Sample coverage ≥ 60% | ✓ | panel.parquet 1,367,649 rows, 1945-01..2002-12, 98.4% non-missing ret; mean eligible 1,965/month in-strategy. |
| 4 | Data-source choice justified | ✓ | CRSP msf + dsfhdr PIT + msedelist merge; delisting treatment adopted only after an evidence-bearing diagnostic (19/19 total-loss cases show msf.ret excludes delret in this vintage); A2/A3 skips carry substantive Fig-1-based justification. |
| 5 | prep_validation.py exit 0 | ✓ | Re-run: all prep artifacts pass; data_verification verdict=ready, 7 full / 0 partial. |
| 6 | All committed tables have results files | ✓ | 8/8 tables in tables_to_replicate.json ↔ results/table_1..8.md. |
| 7 | SUMMARY.md / REPORT.md match results | ✗ (minor) | REPORT headline tally matches scoring.json exactly (1149/163/306, L=0.1242); but the reversal-spread trio and "7 of 8 VW" are stale ([m1]/[m2]). |
| 8 | No orphan folders | ✓ | Slug root clean. |
| 9 | Diagnoses paired with fix attempts | ✓ | 10 iteration entries in assumptions.md each carry Diagnosis / Next fix / Before / After / Status; iteration 10 correctly records "After metric: unchanged (fix deferred)". |
| 10 | Cell status verification | ✓ | Re-ran `scripts/score_replication.py --iteration 1`; aggregates identical (1149/163/0/306, loss 0.1242378). The 1-cell diagnostic-vs-canonical divergence is documented and canonical wins. |
| 11 | Corollary coverage | ✓ | C3 (T3 FF3 alphas), C4 (T4 WRSS), C5 (T5 size, T6 industry, T7 calendar, T8 events) — all computed; none silently skipped. |
| 12 | Claim coverage of committed selection | ✓ | My independently derived claim list (annual-lag pulse; annual spread positivity to 20y vs nonannual reversal; FF3 failure to explain; sigma^2_mu; independence of size/industry/calendar/events) maps 1:1 to C1–C5 and to committed tables; budget_flag present and honest (1,618 cells, full-grid commitment). |
| 13 | Sign conventions re-derived from paper | ✓ | 10-1 winner-minus-loser; reversal spreads negative as paper (L253); T3 zero-investment spread regression (rf cancels) corrected with evidence in inner iteration 7; no absolute-value comparisons or inflated tolerances found in `src/evaluate.py`. |
| 14 | Reporting discipline | ✓ (with [m1]/[m2]) | Claims cite t's (e.g., alpha 0.64 [4.7] vs paper 0.65 [5.11]); no SE-less headline statistics; no omitted computed rows spotted in the results grid. |
| 15 | REPORT.md headline freshness (DEV-010) | ✓ | Headline table matches eval/scoring.json byte-for-byte on all five tallies. |

OCR handling (Table 2/3 Years 16-20 rows lost at page breaks): verified sound. The encoded-from-prose targets trace to the paper's own summary sentences (L253: 146/107/115/67/68/66/52 bp EW; L257: VW 92/83/62/37 and nonannual -125/-55/-19/-39, -82/-43/-15/-25). Replicated VW annual spreads 0.86/0.91/0.76/0.29 and VW nonannual -0.80/-0.50/-0.27/-0.30 all Match within tolerance; the absent decile-grid cells are honestly declared replication-only in `results/table_2.md:43-44` rather than fabricated targets.

## 4. Issues the agent should have caught (didn't)

1. The T4 unit error was visible from inner iteration 8 onward (t = 362 at a lag where the paper prints 3.57 is a five-second sanity check); the SE-readings experiment (iteration 10, Task B) searched three wrong conventions before the x100 fingerprint was noticed. A units assert (mean and SE sharing units) would have caught it immediately.
2. The REPORT.md reversal-spread trio went stale after the Rule-B regeneration — a final "re-copy numbers from results/" pass was skipped for the claim-scoreboard prose even though the headline tally was refreshed.

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "Seasonality in the Cross-Section of Stock Returns" (Heston & Sadka 2008, JFE 87) for slug `heston_sadka_2008_seasonality_in_the_cross_section_of_stock_returns`. The previous agent run completed with verdict **REPLICATED** (audit 1 at `replications/heston_sadka_2008_seasonality_in_the_cross_section_of_stock_returns/logs/audit1.md`). Read the audit first.

## Issues to address (priority order)

### [M1] — MAJOR — Table 4 t-statistics inflated by exactly x100
`src/table4.py:66-68` computes `mean = v.mean() * 100.0` (table units) but `se = v.std(ddof=0) / sqrt(500)` (decimal^2), so `t = mean / se` is 100x too large: `results/table_4.md` prints 362.20 / -25.15 / -62.39 vs paper 3.57 / -0.26 / -0.65. Dividing by 100 gives 3.62 / -0.25 / -0.62 (within 1.5–4% of every paper cell). The fix was already specified in `preparations/assumptions.md` iteration 10 and deferred only because the inner-iteration cap was reached.

**Specific fix:**
1. In `src/table4.py` (the `out[g] = dict(...)` block), compute mean and SE in the SAME units — either drop the `* 100.0` from the mean used in `t`, or scale the SE by 100 — and keep `metrics["t4_mean_*_t"]` consistent.
2. Re-run the pipeline stage that regenerates `results/table_4.md` and `eval/metrics.json`; append a new iteration-log entry in `preparations/assumptions.md` (Diagnosis / Next fix / Before / After / Status).
3. Verification: t4_mean_all_t ≈ -0.25 (paper -0.26), t4_mean_nonannual_t ≈ -0.62 (paper -0.65), t4_mean_annual_t ≈ 3.62 (paper 3.57); all three cells flip FAIL → Match in the evaluator printout.

### [m1] — MINOR — REPORT.md prose values stale
The claim-scoreboard reversal-spread trio "-0.86/-1.19/-0.50" and "VW spreads 7 of 8 Match" do not match the final `results/table_2.md` / `eval/scoring.json` (-1.02/-1.20/-0.41…, and 9/9 VW spread cells Match).

**Specific fix:** re-copy the five reversal-spread values and the VW Match count from `results/table_2.md` / `eval/scoring.json` when you refresh REPORT.md at the end of the iteration.

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every iteration log entry in `assumptions.md` must have all five fields: Diagnosis, Next fix, Before metric, After metric, Status.
- **Read `rep/STUCK_AGENT_GUIDELINE.md` on your first debug cycle.**
- **10-iteration cap per problem.** Hard stop at 10 and escalate to the human.
- **Diagnoses must be paired with fix attempts (exit gate).**

## Inputs you should read

- `replications/heston_sadka_2008_seasonality_in_the_cross_section_of_stock_returns/logs/audit1.md` — this audit (full context)
- `replications/heston_sadka_2008_seasonality_in_the_cross_section_of_stock_returns/inputs/content.md` — paper ground truth
- `replications/heston_sadka_2008_seasonality_in_the_cross_section_of_stock_returns/preparations/` — prep contract
- `replications/heston_sadka_2008_seasonality_in_the_cross_section_of_stock_returns/src/main.py` + `src/table4.py` — current code
- `replications/heston_sadka_2008_seasonality_in_the_cross_section_of_stock_returns/data/` — cached intermediates

## What NOT to redo

- Skip re-reading `SKILL.md` — the contract is the same.
- `scripts/prep_validation.py` is loop-aware and safe to re-run.
- Skip re-doing the clickhouse catalog scan — `data_verification.json` is current.
- Do NOT re-litigate the y1-January residue: six variants were tested and the [STRUCTURAL-SAMPLE-VARIANCE] classification is evidenced (audit 1 accepts it as non-actionable). Same for the T1 short-lag and T3/T7/T8 small-magnitude t-cell residue.
- **DO** re-run any sanity checks you add or modify.

## Deliverables for this iteration

- `src/table4.py` — revised with the unit fix, logged in `assumptions.md`
- `results/table_4.md` — regenerated with corrected t's
- `eval/metrics.json` — regenerated; the auditor will re-run `scripts/score_replication.py --iteration 2`
- `preparations/assumptions.md` — new iteration-log entry for [M1] (and [m1] if addressed)
- `REPORT.md` — refreshed end-to-end from the final results (fix [m1]/[m2]); do NOT edit `SUMMARY.md` (the auditor owns it)

## Stop conditions

- **[M1] fixed and verified** (3 t-cells Match) → re-run prep_validation.py → declare success or note remaining residue in `REPORT.md`; the next audit updates `SUMMARY.md`.
- **10-iteration cap reached** on a single problem → escalate to the human and write a partial `REPORT.md`.
- The remaining FAIL residue is documented non-actionable ([STRUCTURAL-SAMPLE-VARIANCE] with evidence) — do not chase it.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

This is an unusually disciplined first iteration. The inner-loop trace shows real hypothesis testing rather than knob-turning: the delisting merge was adopted only after a vintage diagnostic (19/19 total-loss cases), the eligibility rule was switched to Rule B only after an A/B/C experiment plus long-interval confirmation, the T3 zero-investment convention bug was found and fixed with the correct difference-of-alphas construction, and the T4 NaN zero-fill bug was found by cross-validating against Table 1 internals. The known T4 unit error is the single actionable blemish — diagnosed to a one-line fix with a decisive arithmetic fingerprint (t/100 within 1.5–4% of all three paper cells simultaneously) and deferred solely because the inner cap was reached; it correctly remains in the loss denominator this iteration. The OCR-lost Table 2/3 Years 16-20 rows were encoded from the paper's own prose with line-number citations and the absent cells declared replication-only rather than fabricated — the right call. Signal Strength is dragged to 2 by the y1 Nonannual EW spread (r = 0.39, sign correct), which the replicator bounded with six tested variants and a matching regression counterpart (gamma_1 within 1%); I accept the [STRUCTURAL-SAMPLE-VARIANCE] classification as evidenced, but the worst-case-band rule keeps the dimension score at 2 this iteration. With M1 fixed next iteration I would expect Concrete Result ≈ 87.8%, Signal Strength 3 (worst cell becomes y1 All r = 0.55), and Methodology 5.
