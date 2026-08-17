---
iteration: 4
verdict: REPLICATED
blocker_count: 0
actionable_major_count: 0
requires_iteration: false
---

# Audit Report 4 — weber_2018_attempt2_deepseek

**Verdict:** REPLICATED
**Date:** 2026-08-16
**Auditor notes:** Outer iteration 4 addressed both audit-3 majors with demonstrated test results, and the loss has now plateaued at L = 0.2864 for three consecutive scorer iterations (2, 3, 4) with no scored cell moved. The documented-residue exit (rep/LOSS_FUNCTION.md criterion B) is met: every remaining FAIL cluster now carries a closed-vocabulary marker or an equivalent evidenced cause attribution, and no actionable major or blocker remains. This is a genuine convergence, not a stalled pass.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 3 | 7/8 sub-checks pass. Diagnostic evidence (sub-check 7) is exemplary — the SUE3 split-consistency fix was attempted and disproven with measured before/after, not parked. Statistical inference (sub-check 8) still fails at the D10 tail (ff4_alpha_D10 sign flip, ff5_alpha_D10 r≈20×). |
| Headline matching | 4 | Central claim replicates: D1−D10 spread 1.106 vs 1.10 (0.5%), CAPM alpha spread 1.31 vs 1.29, FF3/FF4/FF5 spread alphas 0.80/0.64/0.38 vs 0.84/0.66/0.48, betas 10/10. Individual D9/D10 bins drift 30–45%. |
| Data coverage | 3 | Period exact (1963–2014, 612 months); join hygiene clean; universe ME drift ~14% (1834 vs 2125); 2 documented substitutes (Moody's BE, Baker-Wurgler sentiment). |
| Concrete result matching | 3 | **471/701 = 67.2% — band 3** (mechanically enforced by prep_validation DEV-034). |
| Signal strength | 3 | Headline spread cells all Match (worst r=0.80 on ff5_alpha_D1D10); D10 tail cells within headline tables sign-flip (ff4_alpha_D10) and one (ff5_alpha_D10) is ~20× off. |
| Corollary | 3 | 356/558 corollary cells Match = 63.8% (band 3); T10 (93%), T4 (88%) strong; T6 (16%), T9 (25%), T8 (49%) lag. |
| 7 | SUMMARY.md matches results/table_*.md | ✓ | Tally 471/189/41 (L=0.2864) copied from eval/scoring.json; matches REPORT.md headline. |

**Overall = 3.17 / 5.00** (mean of 3,4,3,3,3,3). Verdict REPLICATED (overall ≥ 3.0, no dimension = 1).

## 2. Issues by severity

### Blockers (must fix)

None. `prep_validation.py` exits 0 (all present-prep-artifact gates pass). Pipeline runs end-to-end; scorer stamped correctly (`scoring.json` iteration=4; `loss_trace.json` has exactly one clean row per outer iteration 1–4).

### Major (should fix)

None actionable. The two audit-3 majors were both closed with a demonstrated test result this iteration:

- [M1 — RESOLVED, non-actionable] **T8 SUE3.** The prescribed split-consistency fix was implemented (`src/sue3_split_fix.py`), applied the `ibes_adj` cumulative factor, and removed the 14.7% reverse-split-persistence tail rows. Result: D1 −0.209→−0.207, D8 −0.090→−0.083 — no cell moves. The residual is demonstrated structural: the 202601 IBES consensus forecast error is symmetric around zero (45.5% beat / 50.1% miss, median −0.005 $/share), so a sign-neutral SUE3 gradient follows by construction and the paper's positive D1 (+0.038) requires a directional forecast bias this vintage lacks. Distributional, not a split artifact. Evidence in `results/table_8.md` § "Audit-3 [M1]" and `assumptions.md` §Iteration 15.
- [M2 — RESOLVED] **(a) V9 loss-firm CF probe** documented, not committed (net −6, fails triple bar); **(b) T1 FAIL partition** written (see Minor-of-record note below). The V9 probe is the first lever to flip tail factor-alpha signs toward the paper (ff4_alpha_D10 +0.144→−0.129) but overshoots mean_D10 (0.189) and breaks the spread — the right *family*, not calibrated. This is the residual D9/D10 `[STRUCTURAL-SAMPLE-VARIANCE]` evidence, not a new open thread.

Note: the T1 partition (6 zero-anchor artifacts + 8 genuine composition gaps with attributed causes) lives in `results/table_1.md` § "T1 FAIL partition", not in a separate `assumptions.md` iteration entry — a minor documentation-placement inconsistency, not a findings gap.

### Minor (cleanup)

- [m1] **T1 partition has no corresponding `assumptions.md` iteration entry.** The partition is fully documented in `results/table_1.md` (Buckets 1 and 2, with per-cell causes) and referenced in `logs/log4.md` inner-iteration 2, but there is no "Iteration 16 part B" section in `assumptions.md` (§Iteration 16 covers only the V9 probe). The five-field discipline (Diagnosis/Next fix/Before/After/Status) is therefore incomplete for the T1 partition. Cosmetic-only — the partition is report-only and changes no metrics.
  - File: `preparations/assumptions.md` (ends at §Iteration 16, line ~411).
  - Specific fix: optionally append a short "Iteration 17" note logging the T1 partition for traceability. Not required for convergence.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim | ✓ | T2 means decrease D1 (1.568) → D10 (0.462); spread 1.106 vs 1.10. |
| 2 | Headline-magnitude claim | ✓ | Spread 1.106 vs 1.10 (0.5%); D1 1.568 vs 1.43 (~10%); betas 10/10. |
| 3 | Sample coverage ≥ 60% | ✓ | Panel 1,871,536 rows; fundamentals_duration 169,539 firm-years. |
| 4 | Data-source choice justified | ✓ | CRSP/Compustat/13F/IBES catalog-present; Moody's + Baker-Wurgler substitutes documented (A7, data_verification). |
| 5 | prep_validation.py exit 0 | ✓ | All present-prep-artifact gates pass; no DEV-034 error (concrete_result=3 matches 471/701). |
| 6 | All committed tables have results files | ✓ | 11 of 12 present; Table 7 uncommitted (sentiment data gap). |
| 7 | SUMMARY.md matches results/table_*.md | ✓ | 471/701 = 67.2% (band 3); matches scoring.json tally exactly. |
| 8 | No orphan folders | ✓ | No literal-brace/shell-error folders. |
| 9 | Diagnoses paired with fix attempts | ✓ | §Iteration 15 (SUE3) and 16 (V9) each have full five-field before/after. (T1 partition is the m1 caveat above.) |
| 10 | Cell status verification | ✓ | scoring.json tally 471/189/41 (L=0.2864) matches REPORT.md and log4.md exactly; `src/evaluate.py` present. |
| 11 | Corollary coverage | ✓ | C3 (sentiment) documented THIRD-PARTY-DATASET; C4/C5/C6 traversed (T4–T12). |
| 12 | Claim coverage of committed selection | ✓ | C1–C2 headline, C4–C6 committed; C3 documented data-limited; budget_flag present. |
| 13 | Sign conventions re-derived from paper | ✗ | Spread sign correct; ff4_alpha_D10 (ours +0.149 vs paper −0.07) and ff5_alpha_D10 (+0.222 vs +0.01) individual-cell signs still disagree — tail-bin divergence, not subtraction-order, now evidenced as structural. |
| 14 | Reporting discipline | ✓ | Spread t-stat 5.23 cited (SE 0.20); no reversal claim without licensing statistic. |
| 15 | REPORT.md headline freshness | ✓ | REPORT.md tally (701 cells, 471/189/41, L=0.2864) equals scoring.json exactly. |

## 4. Issues the agent should have caught (didn't)

1. **The SUE3 "distributional" finding was the correct call, but the label could have been crisper.** §Iteration 15 and `table_8.md` correctly flip the cause from "split inconsistency" to "forecast-error symmetry" — but the residual is a forecasting-bias property of the 202601 IBES vintage (unbiased consensus), which is arguably a `[STRUCTURAL-SAMPLE-VARIANCE]`-class marker rather than being left described as "structural" in prose only. The four closed-vocabulary markers are the contract's exit path; attaching one explicitly to the SUE3 cells would make the criterion-B trail airtight. This is wording, not substance — the demonstrated evidence fulfills the "demonstration, not hedge" bar independently.

2. **V9's sign-flip on the tail alphas is a genuinely useful diagnostic that the report under-sells as "net −6."** The fact that flooring loss-firms' CF flips ff3/ff4/ff5 D10 alpha signs toward the paper is evidence that the *right* firm set is being identified but the *wrong* magnitude is applied. The report treats this as a failed probe; it is better read as confirmation that no paper-cited CF treatment reproduces the tail — reinforcing (not weakening) the structural-composition conclusion.

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "Cash flow duration and the term structure of equity returns" (Weber 2018, JFE 128, 486–503) for slug `weber_2018_attempt2_deepseek`. The previous agent run completed with verdict **REPLICATED** (audit 4 at `replications/weber_2018_attempt2_deepseek/logs/audit4.md`). Read the audit first.

**The loop has converged.** Loss is flat at 0.2864 for three consecutive scorer iterations (2, 3, 4), and audit 4 recorded `requires_iteration: false` under the documented-residue exit (criterion B): every remaining FAIL cluster carries a closed-vocabulary marker or equivalent evidenced attribution. You should ordinarily **not** re-enter the loop.

If you are re-entering anyway (e.g. a robustness re-run, or a new data vintage became available), the only open threads are:

## Issues to address (priority order)

### [m1] — MINOR — log the T1 FAIL partition in the iteration log

The 14-cell T1 FAIL partition (6 zero-anchor tolerance artifacts + 8 genuine composition gaps) is fully written in `results/table_1.md` but has no matching `assumptions.md` iteration entry. §Iteration 16 covers only the V9 probe.

**Specific fix:**
1. Append a short "Iteration 17 — audit3 M2 part B: T1 FAIL partition (report-only)" section to `preparations/assumptions.md` with Diagnosis (14 FAILs mix zero-anchor rel_err artifacts and genuine composition gaps), Before (14 FAIL), After (6 artifacts / 8 gaps, zero metric change), Status (NO CHANGE — report-only).
2. Verification: five-field discipline restored; no `eval/scoring.json` or metrics.json change.

### [M1 — non-actionable] — T8 SUE3 forecast-error symmetry (do NOT re-attempt)

The paper's positive D1 SUE surprise requires a directional analyst-forecast bias that the 202601 IBES vintage does not have (45.5% beat / 50.1% miss, median −0.005). The split-consistency fix was already applied and disproven. If the cycle director asks for one cosmetic improvement: attach the `[STRUCTURAL-SAMPLE-VARIANCE]` marker explicitly to the SUE3 cells in `table_8.md`, matching the D9/D10 tail framing.

## Iteration discipline reminders

- **Do not re-open a demonstrated non-actionable cluster.** SUE1/SUE2 (SRW mean-zero), SUE3 (forecast symmetry), D9/D10 tail (composition, vintage rejected, CF-floor probes exhausted), T6 levels (inherited-tail + convention), T9 (vintage level) are all closed with test results. Re-chasing them only burns compute.
- **Run `scripts/score_replication.py --iteration <N>` ONCE at the end** if and only if you commit a metric change.
- **Keep the DEV-034 denominator in mind**: concrete-result band uses `match_count / (n_cells - skip_count) = 471/701`.

## What NOT to redo

- Do NOT re-derive the core duration construction (spread 1.106 vs 1.10, betas 10/10) — validated.
- Do NOT re-run the vintage probe (vintage rejected with evidence A15).
- Do NOT re-attempt SUE1/SUE2/SUE3 or the CF-floor family (V3/V9) without a *new* paper-cited rationale not already tested.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

Outer iteration 4 is the close-out pass the loop was waiting for. It is a small iteration — zero scored cells moved — but it converted two "plausibly fixable" audit-3 majors into *demonstrated* non-actionable residue. The SUE3 result is the cleanest kind of negative result: a prescribed fix was actually run (not argued around), produced a measured no-op (−0.209→−0.207), and surfaced the true structural cause (symmetric forecast errors) that no re-derivation can defeat. The V9 loss-firm probe, read correctly, is positive evidence *for* the structural conclusion rather than a failed calibration: it flips the tail alpha signs but overshoots the mean, proving the tail is a composition/return-level difference, not a construction error. The T1 partition finally gives the 14 descriptive FAILs a defensible two-way taxonomy. Together these satisfy criterion B honestly — the residue is documented, each cluster has an attributed cause backed by a test result, and there is no lever left that a next iteration could plausibly pull without chasing noise. This is a correct exit.
