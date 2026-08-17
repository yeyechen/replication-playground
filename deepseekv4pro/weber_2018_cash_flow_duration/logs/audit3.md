---
iteration: 3
verdict: REPLICATED
blocker_count: 0
actionable_major_count: 1
requires_iteration: true
---

# Audit Report 3 — weber_2018_attempt2_deepseek

**Verdict:** REPLICATED
**Date:** 2026-08-16
**Auditor notes:** Outer iteration 3 did not move a single scored cell — loss is flat at 0.2864 (second consecutive iteration). Its value is diagnostic: all three audit-2 majors (M1 D9/D10 tail, M2 T6 RV series, M3 T8 SUE/EG) were investigated with real tests rather than parked, and the replicator demonstrated that the SRW-SUE gradient is mean-zero-by-construction and that act_epsus is already split-adjusted (the audit-2 premise was false). The reproduction is disciplined but has reached a genuine plateau, and two threads remain plausibly fixable rather than closed-vocabulary residue.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 3 | 7/8 sub-checks pass. Diagnostic-evidence (sub-check 7) is now exemplary (M1/M2/M3 all tested). Statistical-inference (sub-check 8) still fails at the D10 tail (ff4_alpha_D10 sign flip, ff5_alpha_D10 r=20×). |
| Headline matching | 4 | Central claim replicates: D1−D10 spread 1.106 vs 1.10 (0.5%), CAPM alpha spread 1.31 vs 1.29, FF3/FF4/FF5 spread alphas 0.80/0.64/0.38 vs 0.84/0.66/0.48 (all within tolerance). Individual D9/D10 bins drift 30–45%. |
| Data coverage | 3 | Period exact (1963–2014, 612 months); join hygiene clean; universe ME drift ~14% (1834 vs 2125); 2 documented substitutes (Moody's BE, Baker-Wurgler sentiment). |
| Concrete result matching | 3 | **471/701 = 67.2% — band 3** (mechanically enforced; corrected from audit-2's erroneous band 4, which used 471/660). |
| Signal strength | 3 | Headline spread cells all Match (worst r=0.80 on ff5_alpha_D1D10); D10 tail cells within headline tables sign-flip (ff4_alpha_D10) and one (ff5_alpha_D10) is ~20× off. |
| Corollary | 3 | 356/558 corollary cells Match = 63.8% (band 3); T10 (93%), T4 (88%) strong; T6 (16%), T9 (25%), T8 (49%) lag. |
| 7 | SUMMARY.md matches results/table_*.md | ✓ | Tally 471/189/41 (L=0.2864) copied from eval/scoring.json; matches REPORT.md headline. |

## 2. Issues by severity

### Blockers (must fix)

None. `prep_validation.py` exits 0 except for the DEV-034 `concrete_result` band mismatch carried over from audit 2 (fixed in this audit's SUMMARY.md). Pipeline runs end-to-end; scorer stamped correctly (`scoring.json` iteration=3; `loss_trace.json` has exactly one clean row per outer iteration).

### Major (should fix)

- [M1] **T8 SUE3 remains blocked by a *fixable* data defect, not a structural wall.** (Post-iteration-4 annotation: `actionable: false` — the prescribed split-consistency fix was attempted in outer iteration 4 and disproven; the residual is structural forecast-error symmetry in the 202601 vintage, see log4.md.) The replicator correctly demonstrated SUE1/SUE2 (seasonal random walk) are mean-zero-by-construction and therefore cannot reproduce the paper's +0.23→−0.47 gradient — that part is genuinely non-actionable. But the footnote-17 resolution names SUE3 (analyst-forecast-based) as the *paper's actual mechanism*, and SUE3 is blocked only because `statsum_epsus` actual/meanest is split-inconsistent in the 202601 vintage (raw errors to −1.3e9; 3.2% rows |err|>5×|meanest|). The diagnostics themselves produced the tool to fix this: `ibes_adj` gives the cumulative split factor, and `act_epsus` is already split-adjusted. A split-consistent re-derivation of `statsum_epsus` (applying `ibes_adj.adj` to un-split the actual/meanest) is a plausible, previously-unattempted fix that would let the paper's named mechanism be scored.
  - File: `preparations/assumptions.md` §Iteration 14; `results/table_8.md`.
  - Likely cause: statsum_epsus rows sit on mixed post-split share bases; the 3.2% split-artifact rows dominate the surprise distribution.
  - Specific fix: re-derive statsum_epsus actual and meanest on a split-consistent basis using the `ibes_adj` cumulative factor already discovered; re-run the SUE3 block and check whether the D1→D10 surprise gradient becomes monotonically decreasing.

- [M2] **Loss is flat at 0.2864 for the second consecutive iteration, and the two largest FAIL clusters are not yet closed-vocabulary.** The D9/D10 tail remains OPEN (the M1 construction probe exhausted CF-floor/winsorization/BE-floor, but the closest lever — the V3 CF-floor — moved D10 *through* the target to 0.225, i.e. it is the right family of fix, just not calibrated to hit 0.32 without breaking the spread). Separately, the 14 T1 descriptive FAILs include genuine composition/construction gaps (std_pr 3.24 vs 2.10, std_roe 0.39 vs 0.54, mean_age 13.75 vs 17.59, corr_dur_pr −0.011 vs −0.10) that carry no closed-vocabulary marker; many near-zero correlation cells are a tolerance artifact (rel_err explodes against zero anchors), but the non-zero-anchor mean/std cells are real.
  - File: `preparations/assumptions.md` §Iteration 12/14, A15; `results/table_1.md`.
  - Likely cause: T1 descriptive mismatches are a mix of (a) the documented all-stock 20th-pct screen (mean_age, A9) and (b) residual sample-composition differences in the tiny-loss-maker tail; the V3 CF-floor is the only lever that has ever moved D10 in the right direction.
  - Specific fix: (a) probe a *graduated* loss-firm CF/book treatment (between no-floor and the full CF-floor) to land D10 near 0.32 without the spread overshoot; (b) partition the T1 correlation/std mismatches by the same tail-composition split and split out tolerance artifacts (zero-anchor rel_err) from genuine gaps.

### Minor (cleanup)

- [m1] **Iteration log carries stale template blocks.** `logs/log3.md` § "Assumption decisions this iteration", "Per-cell evaluation" and "Summary (pending)" (bottom of file) are empty duplicate template sections left over from the scaffold. Prune them so the log reflects only the three inner iterations that ran.
  - File: `logs/log3.md` (bottom 10 lines).

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim | ✓ | T2 means decrease D1 (1.568) → D10 (0.462); spread 1.106 vs 1.10. |
| 2 | Headline-magnitude claim | ✓ | Spread 1.106 vs 1.10 (0.5%); D1 1.568 vs 1.43 (~10%); betas 10/10. |
| 3 | Sample coverage ≥ 60% | ✓ | Panel 1,871,536 rows; fundamentals_duration 169,539 firm-years. |
| 4 | Data-source choice justified | ✓ | CRSP/Compustat/13F/IBES catalog-present; Moody's + Baker-Wurgler substitutes documented. |
| 5 | prep_validation.py exit 0 | ✗ | Fails DEV-034 only: `concrete_result=4` vs band 3 (67.2%) — corrected in this audit's SUMMARY.md; all other gates pass. |
| 6 | All committed tables have results files | ✓ | 11 of 12 present; Table 7 uncommitted (sentiment data gap). |
| 7 | SUMMARY.md matches results/table_*.md | ✓ | 471/701 = 67.2% (band 3) after correction; matches scoring.json tally. |
| 8 | No orphan folders | ✓ | No literal-brace/shell-error folders; scratch vintage parquets deleted. |
| 9 | Diagnoses paired with fix attempts | ✓ | Iterations 12–14 have Diagnosis/Next fix/Before/After/Status; M1/M2/M3 each has a real before/after. |
| 10 | Cell status verification (re-run evaluator, diff vs scoring.json) | ✓ | scoring.json tally 471/189/41 (L=0.2864) matches REPORT.md and log3.md exactly. |
| 11 | Corollary coverage | ✓ | C3 (sentiment, T7) documented data-limited; C4/C5/C6 corollaries traversed (T4–T12); C4 SU/EG gap surfaced as M1 here. |
| 12 | Claim coverage of committed selection | ✓ | C1–C2 headline, C4–C6 committed; C3 documented THIRD-PARTY-DATASET; budget_flag present. |
| 13 | Sign conventions re-derived from paper | ✗ | Spread sign (D1−D10 positive) correct per abstract; ff4_alpha_D10 (ours +0.149 vs paper −0.07) and ff5_alpha_D10 (+0.222 vs +0.01) individual-cell signs still disagree — tail-bin divergence, not subtraction-order, unresolved. |
| 14 | Reporting discipline (grid completeness, claim citations, SE-less headlines) | ✓ | Spread t-stat 5.23 cited (SE 0.20); no reversal claim without licensing statistic. |
| 15 | REPORT.md headline freshness (matches scoring.json) | ✓ | REPORT.md tally (701 cells, 471/189/41, L=0.2864) equals scoring.json exactly. |

## 4. Issues the agent should have caught (didn't)

1. **The SUE3 "vintage-blocked" label under-sells the fix.** The footer-17 resolution itself identified SUE3 as the paper's mechanism, and the split-inconsistency in `statsum_epsus` was *measured* (3.2% |err|>5×|meanest|) but never *repaired* — even though the same diagnostic run produced the exact tool (the `ibes_adj` cumulative split factor, and the finding that `act_epsus` is already split-adjusted) that would let a split-consistent statsum_epsus be built. This is a case where "documented data limitation" boxes what is actually a one-shot data-hygiene fix.
2. **The DEV-034 `concrete_result` drift was not caught at the end of outer iteration 2.** audit2's SUMMARY.md wrote `concrete_result: 4` against a 471/660 rate, when the validator's authoritative denominator is `n_cells - skip_count = 701`, yielding 67.2% → band 3. The replicator's own `scoring.json` records `n_committed: 660` (no_effect-excluded), which disagrees with the validator's `n_cells - skip`. This off-by-no_effect denominator gap should have been surfaced rather than propagated.

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "Cash flow duration and the term structure of equity returns" (Weber 2018, JFE 128, 486–503) for slug `weber_2018_attempt2_deepseek`. The previous agent run completed with verdict **REPLICATED** (audit 3 at `replications/weber_2018_attempt2_deepseek/logs/audit3.md`). Read the audit first. Loss is flat at 0.2864 (iterations 2 → 3); the remaining work is to close two threads that are plausibly fixable, not residue.

## Issues to address (priority order)

### [M1] — MAJOR — T8 SUE3: fix the split inconsistency, don't accept "vintage-blocked"

SUE1/SUE2 (seasonal random walk) are genuinely unattainable — you proved the SRW surprise is mean-zero by construction. But footnote 17 names SUE3 (analyst-forecast-based, actual − meanest) as the paper's real mechanism, and SUE3 is only blocked by a *measured* split inconsistency in `statsum_epsus` (202601 vintage: raw errors to −1.3e9; 3.2% of rows |err|>5×|meanest|) — not by missing data. You already hold the fix: `ibes_adj` gives the cumulative split factor, and `act_epsus` is already split-adjusted.

**Specific fix:**
1. In `src/sue_eg_diagnostic.py` (or a new scratch module), build a split-consistent `statsum_epsus` actual/meanest by applying the `ibes_adj.adj` cumulative factor to un-split rows onto a common share base (mirroring how you confirmed `act_epsus` is split-adjusted).
2. Re-run the SUE3 block (forecast-error-σ standardization per Livnat-Mendenhall) on the cleaned series.
3. Verification: the SUE3 D1→D10 surprise should become monotonically decreasing; if the +0.23 → −0.47 gradient appears, commit and re-run the scorer with `--iteration 4`.

### [M2] — MAJOR — break the flat loss: calibrate the tail lever, and partition the T1 descriptive FAILs

Loss is 0.2864 for the second consecutive iteration. The V3 CF-floor lever is the only construction that ever moved D10 in the right direction (it overshot to 0.225 vs the 0.32 target and broke the spread) — that means loss-firm CF handling is the right *family*, not a dead end. Separately, 14 T1 descriptive cells FAIL without any closed-vocabulary marker; several are genuine composition gaps (std_pr 3.24 vs 2.10, std_roe 0.39 vs 0.54, mean_age 13.75 vs 17.59, corr_dur_pr −0.011 vs −0.10), while some near-zero correlation cells are tolerance artifacts (rel_err explodes against zero anchors).

**Specific fix:**
1. Probe a *graduated* loss-firm treatment (between the no-floor baseline and the full CF-floor) — e.g., floor CF at the long-run value only for negative-BV/reinvesting firms with a paper-cited rationale — targeting D10 ≈ 0.32 without the spread overshoot (spread must stay ≈ 1.10).
2. For T1: split the correlation FAILs into zero-anchor tolerance artifacts vs genuine gaps (std_pr, std_roe, corr_dur_pr are the substantive ones), and document the tail-composition contribution for each, mirroring the A15 evidence discipline.
3. Verification: report before/after D9/D10 means + spread for the tail probe, and a two-way partition of T1 FAILs; do not commit any change that nets negative cells.

### [m1] — MINOR — clean the iteration log template

`logs/log3.md` retains empty duplicate template sections ("Assumption decisions this iteration", "Per-cell evaluation", "Summary (pending)") at the bottom. Prune them so the log reflects only the three inner iterations that actually ran.

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every `assumptions.md` entry must carry all five fields (Diagnosis, Next fix, Before metric, After metric, Status).
- **Do not retire a FAIL with an untested causal story.** The "SUE3 is vintage-blocked" label is a measured, not demonstrated, block — the 3.2% split-artifact rate is a symptom; run the split-consistency fix before re-labeling.
- **Close-vocabulary markers require per-cell evidence.** `[STRUCTURAL-SAMPLE-VARIANCE]`, `[CONVENTION-APPLIED]`, `[THIRD-PARTY-DATASET]`, `[VINTAGE-DRIFT]` must be attached to *specific* cells with a test result, not asserted in bulk.
- **Run `python scripts/score_replication.py replications/<slug> --iteration 4` ONCE, at the very end** (outer iteration number, not an inner-loop counter).
- **Watch the DEV-034 denominator.** `prep_validation.py` computes the concrete-result band as `match_count / (n_cells - skip_count)` over ALL committed cells (denominator = 701 here, *including* no_effect, which is the authoritative band). Do not write `concrete_result` from the scorer's `n_committed` field (660).

## Inputs you should read

- `replications/weber_2018_attempt2_deepseek/logs/audit3.md` — this audit (full context)
- `replications/weber_2018_attempt2_deepseek/inputs/content.md` — paper ground truth (footnote 15/17 for T8; Section 2 Eq. 2/3 for duration)
- `replications/weber_2018_attempt2_deepseek/preparations/` — prep contract (esp. `assumptions.md` §Iteration 12/14)
- `replications/weber_2018_attempt2_deepseek/src/sue_eg_diagnostic.py`, `src/table8_9.py` — SUE/EG code
- `replications/weber_2018_attempt2_deepseek/data/` — cached intermediates
- `replications/weber_2018_attempt2_deepseek/results/iteration5_experiment_matrix.md` — the CF-floor variant evidence

## What NOT to redo

- Do NOT re-litigate SUE1/SUE2 (structurally mean-zero — demonstrated). Focus on SUE3.
- Do NOT re-run the vintage probe (comp_202401) — vintage is rejected with evidence (A15).
- Do NOT re-attempt a standalone T9 PTP level tune or a standalone T6 RV-series level tune (both documented non-actionable).
- Do NOT re-derive the core duration construction (spread 1.106 vs 1.10, betas 10/10, T4 116/132, T10 L=0.068) — validated.

## Deliverables for this iteration

- `src/sue_eg_diagnostic.py` (or a new scratch module) — split-consistent SUE3
- `src/main.py` (if the tail lever lands) — graduated loss-firm CF treatment
- `results/table_1.md`, `results/table_8.md`, `results/table_2.md` — updated for any committed change
- `preparations/assumptions.md` — new iteration log entry per issue (five fields each)
- `SUMMARY.md` — read only; do NOT edit (auditor-owned)
- `REPORT.md` — updated, lead with the data-quality summary and the SUE3/tail outcomes

## Stop conditions

- **All majors fixed and verified** → re-run prep_validation.py and the scorer (`--iteration 4`) → declare success or partial.
- **10-iteration cap reached** → escalate and write a partial REPORT.md.
- **A major is genuinely non-actionable** → attach the correct closed-vocabulary marker with a *demonstrated* test result, not a hedge.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

Outer iteration 3 is a pure-diagnostic pass: zero scored cells moved, and yet it is not dead weight — it retired two audit-2 premises that were actually false (that IBES `act_epsus` is unadjusted, and that a real EPS source could produce the SRW-SUE gradient). The D9/D10 tail is now framed honestly as compositional with verified bin formation (D10 mean duration 25.29 ≈ the paper's "roughly 25 years"). The one thing that nags is the SUE3 handling: the replicator *found* the footnote-17 answer (SUE3 is the mechanism), *measured* the blocking datum (3.2% split-artifact rate), and *had* the tool (the `ibes_adj` factor) all in the same pass, yet still wrote "vintage-blocked." That is a documented data limitation wrapping a fixable one-shot join — and it is the single clearest path to actually move the loss off its plateau. The `concrete_result` band correction (4 → 3) is mechanical, not a downgrade in quality: it reflects that the validator's authoritative denominator (701) includes the 41 no_effect cells the scorer's own `n_committed` (660) quietly excludes — an internal-consistency gap worth flagging upstream.
