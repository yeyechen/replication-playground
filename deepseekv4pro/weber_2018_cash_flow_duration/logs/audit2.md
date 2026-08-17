---
iteration: 2
verdict: REPLICATED
blocker_count: 0
actionable_major_count: 3
requires_iteration: true
---

# Audit Report 2 — weber_2018_attempt2_deepseek

**Verdict:** REPLICATED
**Date:** 2026-08-16
**Auditor notes:** Outer iteration 2 made real, demonstrated progress on all five audit-1 majors — the vintage-drift attribution was properly tested and rejected (the audit-1 demand), the T8 universe was corrected to the IBES-covered subset, the T12 conditional-tertile bug was found and fixed, and the FM-mean preest estimator was committed. Loss improved 0.3167→0.2864, crossing the Concrete-Result band to 4. Residuals are now clean and interpretable: a genuine open D9/D10 tail-composition question (demonstrated compositional, not vintage), the T8 SUE/EG gradient, T6 decile levels, and the T9 vintage-level gap. Two majors remain actionable.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 3 | 7/8 sub-checks pass. Diagnostic-evidence sub-check (7) is now exemplary — the audit-1 hedged vintage story was TESTED and rejected with a real alternative-vintage probe (A15). Sub-check 8 (statistical inference) still fails at the D10 tail (ff4_alpha_D10 sign flips; ff5_alpha_D10 r=22×). |
| Headline matching | 4 | Central claim C1/C2 replicates near-exactly: D1−D10 spread 1.106 vs 1.10 (0.5%), CAPM betas 10/10, CAPM alpha spread 1.29 vs 1.29, FF3/FF4/FF5 spread alphas all within tolerance. Individual D9/D10 bins still drift 30–45%. |
| Data coverage | 3 | Period exact (1963–2014, 612 months); join hygiene clean (0 dup); universe ME drift ~14% (1834 vs 2125); 2 documented substitutes (Moody's BE, Baker-Wurgler) + 3 partial IBES/FF sources. |
| Concrete result matching | 4 | 471/660 committed cells Match = 71.4% (band 4), up from 68.3% at audit 1; mechanically enforced. |
| Signal strength | 3 | Headline D1D10 spread cells all Match (worst r=0.80 on ff5_alpha_D1D10), but D10 tail cells within the headline tables (T2/T3) sign-flip (ff4_alpha_D10 −0.07 vs +0.149) and one (ff5_alpha_D10) is 22× off. |
| Corollary | 3 | 386/561 corollary cells Match = 68.8% (band 3); T10 (0.932) and T4 (0.879) strong, T6 (0.164), T9 (0.250), T8 (0.491) lag. |
| 7 | SUMMARY.md matches results/table_*.md | ✓ | Tally copied from eval/scoring.json (471/189/41, L=0.2864); matches REPORT.md headline exactly. |

## 2. Issues by severity

### Blockers (must fix)

None. The pipeline runs end-to-end, `prep_validation.py` exits 0, the headline magnitude (spread 1.106 vs 1.10) is within 0.5%, and the canonical scorer was run correctly this iteration (`scoring.json` iteration=2; `loss_trace.json` has exactly one clean row per outer iteration — the audit-1 m1 stale-row issue is fixed).

### Major (should fix)

- [M1] **D9/D10 tail FAIL cluster is now demonstrably OPEN (compositional, not vintage) with no demonstrated cause.** The rejection is correct work (A15: `comp_202401` reproduces the tail to 3 decimals), but the cells remain FAIL and the cause is unproven. The companion finding — on the IBES-covered subset mean_D10 = 0.325 vs paper 0.32 — shows the paper's low D10 mean is carried by large/covered firms, yet the paper's T2 is the full CRSP/Compustat universe, so this does NOT rescue the T2 cells. Next iteration must answer: what screen/construction makes Weber's tiny loss-makers in D10 earn less? A CF-floor-style duration-construction question.
  - File: `preparations/assumptions.md` §Iteration 12 / A15; `REPORT.md` §Known divergences ¶1; `results/iteration5_experiment_matrix.md`.
  - Likely cause: D10 contains tiny, young, loss-making firms (median me $40M, 70% negative ROE) whose bubble-era returns (+55.1% Jan-2001, verified real in raw CRSP) exceed the paper's. The duration construction (clean-surplus CF with the paper's cascade) evidently ranks these firms differently than the paper's.
  - Specific fix: probe the DSS/loss-firm cash-flow handling against the paper's duration construction (the iteration5 experiment matrix already shows a CF-floor variant moves D9/D10 in the right direction); record before/after D9/D10 means and D1D10 spread; if a defensible construction closes the tail, commit it, otherwise reopen and document as structural.

- [M2] **T6 decile levels run 10–50% high (L=0.836; 46 FAIL cells).** All five spread cells Match, so the volatility-management claim itself is validated, but the per-decile levels are systematically high and remain unattributed (largely downstream of the M1 tail composition plus RV-series construction uncertainty, per assumption A11).
  - File: `src/table6.py`; `REPORT.md` §Known divergences ¶3.
  - Likely cause: inherited D9/D10 tail composition + paper-silent daily-weighting/RV-series construction.
  - Specific fix: re-check after the M1 tail probe; do not attempt a standalone level tune this iteration (downstream).

- [M3] **T8 SUE/EG gradient still fails (L=0.509) after the audience-correct universe fix; SUE numerator is flat at ~0 at every decile.** σ-standardization per Livnat-Mendenhall (2006) was implemented yet the SRW numerator median ≈ 0 at every decile (D1 −0.015..D10 +0.010), so no surprise gradient exists to reproduce the paper's D1 +0.23 → D10 −0.47. EG levels remain ~half (D1 −0.95 vs 6.95).
  - File: `preparations/assumptions.md` §Iteration 11; `results/table_8.md` schema notes.
  - Likely cause: the paper's footnote-17 lookback/centering detail for SUE and the EPS-measure definition for EG are not encoded; the expected-surprise gradient lives in analyst expectations, not YoY Compustat EPS drift.
  - Specific fix: source the paper's footnote-17 SUE window/centering and the EG realized-EPS measure (IBES vs Compustat split-adjusted), re-run the SUE/EG blocks, and report whether the D1→D10 gradient appears. This is the C4 "analyst expectations" claim — currently only the LTG panel validates it.

- [M4] **T9 Panel A PTP level gap (L=0.750; PTP D5 33.1 vs 16.85) — attributed to a documented 2026-IBES-vintage level gap, non-actionable.** The extraction was validated correct (7-firm × 2-month spot-check, all implied returns sane +6.5%..+39.3%), and the implausible quintile values were reverse-split artifacts now fixed (A14). The residual PTP runs ~24–33% vs the paper's flat ~16%, a systematic level gap evidenced against the 2026 IBES vintage. No fix is available in the current catalog vintage.
  - File: `preparations/assumptions.md` A14; `results/table_9.md`.
  - Likely cause: vintage-level difference in consensus target-price implied returns across 2001–2014. Non-actionable this iteration.
  - Specific fix: none available; carry the documented gap. (actionable: false)

### Minor (cleanup)

- [m1] **T8 SUE3 extraneous `_se` and probe-artifact rows in results files.** `results/table_8.md` carries a large "Coverage"/"Schema discovery notes" block including raw median dumps and an `SUE1 ... sigma median D1=0.3386...` line; several values (SUE1/SUE2 medians) are reported twice. Cosmetic — the results file is over-verbose and muddies the per-cell read.
  - File: `results/table_8.md` §Coverage; `results/table_9.md` §Spot-check.
  - Specific fix: trim the diagnostic dumps to a summary; keep only the scored cell values + the one-line cause per divergence.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim | ✓ | T2 means decrease monotonically D1 (1.568) → D10 (0.462); spread 1.106 vs 1.10. |
| 2 | Headline-magnitude claim | ✓ | Spread 1.106 vs 1.10 (0.5%); D1 1.568 vs 1.43 (9.7%); betas 10/10. |
| 3 | Sample coverage ≥ 60% | ✓ | Panel 1,871,536 rows, 15,489 permnos, 51 sort years; fundamentals_duration 169,539 firm-years. |
| 4 | Data-source choice justified | ✓ | CRSP/Compustat/13F/IBES all catalog-present; Moody's + Baker-Wurgler substitutes documented in data_verification.json. |
| 5 | prep_validation.py exit 0 | ✓ | 47 rules, 11 tables, verdict=partial; scoring.json present (DEV-019). |
| 6 | All committed tables have results files | ✓ | 11 of 12 files present; Table 7 correctly uncommitted (sentiment data gap). |
| 7 | SUMMARY.md matches results/table_*.md | ✓ | 471/660 = 71.4% copied from scoring.json; matches REPORT.md headline. |
| 8 | No orphan folders | ✓ | No literal-brace/shell-error folders; scratch `vintage_probe_*.parquet` deleted. |
| 9 | Diagnoses paired with fix attempts | ✓ | Iterations 11–13 have Diagnosis/Next fix/Before/After/Status; vintage test has real before/after. |
| 10 | Cell status verification (re-run evaluator, diff vs scoring.json) | ✓ | `evaluate.py` reproduces canonical scorer exactly: Match=471 FAIL=189 no_effect=41, L=0.2864. |
| 11 | Corollary coverage | ✓ | C3 (sentiment) and C4/C5/C6 corollaries traversed; T8/T9 C4 gap surfaced as M3; T6/T9 as M2/M4. |
| 12 | Claim coverage of committed selection | ✓ | C1–C2 (headline), C4–C6 committed; C3 (Table 7) documented data-limited; budget_flag present. |
| 13 | Sign conventions re-derived from paper | ✗ | Spread sign (D1−D10 positive) correct per abstract L43, but ff4_alpha_D10 (paper −0.07 vs ours +0.149) and ff5_alpha_D10 (+0.010 vs +0.222) individual-cell signs still disagree — a tail-bin divergence, not a subtraction-order error, but not resolved this iteration. |
| 14 | Reporting discipline (grid completeness, claim citations, SE-less headlines) | ✓ | Spread t-stat 5.23 cited (SE 0.20); no reversal claims without licensing statistic. |
| 15 | REPORT.md headline freshness (matches scoring.json) | ✓ | REPORT.md tally (701/471/189/0/41, L=0.2864) equals scoring.json exactly. |

## 4. Issues the agent should have caught (didn't)

1. The **T8 SUE flatness** (M3) was correctly *diagnosed* as "the expected surprise gradient lives in analyst expectations, not YoY EPS drift," but the replicator parked it without resolving whether the paper's SUE is analyst-forecast-based (SUE3, which is the meaningful surprise variable) rather than seasonal-random-walk. The paper's section text ("high-duration stocks have negative earnings surprises") plus the SUE3 construction may be the intended target, not SUE1/SUE2. This deserved a direct read of footnote 17 against the three SUE variants before parking.
2. The **T6 level inflation** (M2) was carried as "downstream of M1" for a second consecutive iteration without a single RV-series construction diagnostic (daily-weighting sensitivity, std-equalization constant c). A cheap sensitivity check would distinguish a construction bug (fixable) from an inherited tail effect (non-actionable).

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "Cash flow duration and the term structure of equity returns" (Weber 2018, JFE 128, 486–503) for slug `weber_2018_attempt2_deepseek`. The previous agent run completed with verdict **REPLICATED** (audit 2 at `replications/weber_2018_attempt2_deepseek/logs/audit2.md`). Read the audit first.

## Issues to address (priority order)

### [M1] — MAJOR — demonstrate or reopen the D9/D10 tail construction (fix first)

The D9/D10 tail FAIL cluster (ff4_alpha_D10 sign flip, ff5_alpha_D10 r=22×, mean_D10 0.462 vs 0.32) is now demonstrably NOT vintage drift — a real alternative-vintage probe (comp_202401) reproduced the tail to 3 decimals. The cause is compositional: D10 contains tiny, loss-making firms (median me $40M, 70% negative ROE) whose returns exceed the paper's. The IBES-covered subset reproduces the paper's D10 (0.325 vs 0.32) but the paper's Table 2 is the full CRSP/Compustat universe, so the subset does NOT rescue the T2 cells. The open question is which screen/construction makes Weber's tiny loss-makers earn less.

**Specific fix:**
1. Read `src/main.py` duration construction (Dechow et al. 2004 clean-surplus CF, Eq. 2/3) and probe how negative-ROE / loss-making firms are handled; the DSS loss-firm handling (see `results/iteration5_experiment_matrix.md`) already moves D9/D10 in the right direction.
2. Test a defensible loss-firm CF treatment (e.g. CF-floor, or ROE-floor at the long-run value for negative-BV/loss firms) against the paper's stated construction; measure before/after D9/D10 means and the D1D10 spread.
3. Verification: if the tail moves toward the paper's D10 ≈ 0.32 and the alpha sign flips back (−0.07), commit it with a paper-cited rationale; otherwise reopen the FAIL and attach `[STRUCTURAL-SAMPLE-VARIANCE]` with the demonstrated composition evidence.

### [M2] — MAJOR — T6 decile-level inflation (after M1)

T6 has L=0.836 with all 5 spread cells Match but per-decile levels 10–50% high. Largely inherited from the M1 tail, but a construction diagnostic has never been run.

**Specific fix:**
1. In `src/table6.py`, run a daily-weighting sensitivity check (within-month EW vs a single daily return) and a c-constant (std-equalization) sensitivity check on the RV series (assumption A11).
2. Report which factor moves the levels; if levels collapse to the paper's after M1, close the item; otherwise document the RV-series construction gap as non-actionable.

### [M3] — MAJOR — T8 SUE/EG gradient (C4 "analyst expectations")

After the universe fix, only the LTG panel validates C4. SUE1/SUE2 (σ-standardized) have a flat numerator (~0 at every decile), so no surprise gradient exists to hit the paper's D1 +0.23 → D10 −0.47. EG levels are ~half the paper's.

**Specific fix:**
1. Read the paper's footnote 17 (`inputs/content.md`) for the SUE lookback/centering; verify whether the paper's "negative earnings surprises" (L2348) refers to an analyst-forecast-based SUE (SUE3: actual − meanest) rather than the seasonal-random-walk SUE1/SUE2.
2. Re-run the SUE block with the paper's exact window/centering (and confirm EG's realized-EPS source, IBES `act_epsus` vs split-adjusted Compustat `epspx`).
3. Verification: the SUE D1→D10 gradient should become monotonically decreasing; EG D1 should turn positive, matching the paper's direction.

### [M4] — MAJOR (non-actionable) — T9 PTP vintage level gap

Carry the documented T9 PTP level gap (~24–33% vs ~16%), evidenced against the 2026 IBES vintage. No fix available in the current catalog. Document, do not re-tune.

### [m1] — MINOR — trim T8/T9 results-file diagnostic dumps

`results/table_8.md` and `table_9.md` carry over-verbose schema/discovery/coverage blocks with raw median dumps and duplicated values. Trim to the scored cells + a one-line cause per divergence.

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every iteration log entry in `assumptions.md` must have all five fields (Diagnosis, Next fix, Before metric, After metric, Status).
- **Read `rep/STUCK_AGENT_GUIDELINE.md` on your first debug cycle.** Don't rediscover failures already documented.
- **10-iteration cap per problem.** Hard stop at 10 and escalate.
- **Diagnoses paired with fix attempts (exit gate).** Before declaring `partial`, verify every diagnosed problem has a non-empty `Next fix` + before/after metric.
- **Do not retire a FAIL with an untested causal story.** The audit-1 vintage-drift story was retired only because the alternative-vintage test was actually run. Keep that standard: every divergence you close must cite a demonstrated test result.
- **Run `python scripts/score_replication.py replications/<slug> --iteration <N>` ONCE, at the very end, with `<N>` = the OUTER iteration number (3 for the next pass), NOT an inner-loop counter.**

## Inputs you should read

- `replications/weber_2018_attempt2_deepseek/logs/audit2.md` — this audit (full context)
- `replications/weber_2018_attempt2_deepseek/inputs/content.md` — paper ground truth (esp. footnote 15/17 for T8, Section 2 Eq. 2/3 for duration)
- `replications/weber_2018_attempt2_deepseek/preparations/` — prep contract (rules, tables, assumptions iteration log)
- `replications/weber_2018_attempt2_deepseek/src/main.py`, `src/table6.py`, `src/table8_9.py` — current code (will be modified)
- `replications/weber_2018_attempt2_deepseek/data/` — cached intermediates
- `replications/weber_2018_attempt2_deepseek/results/iteration5_experiment_matrix.md` — the CF-floor variant evidence

## What NOT to redo

- Do NOT re-run the full pipeline from scratch — T2–T5 sorts and the core duration construction are validated (spread 1.106 vs 1.10, betas 10/10, T4 116/132, T5 45/55).
- Do NOT re-litigate the $5 price-floor (A2), NYSE-only breakpoint (A9), or conditional-vs-global duration tertiles (iteration 13) — those are settled with evidence.
- Do NOT re-run the vintage probe — vintage drift is rejected with evidence; the tail is composition, not vintage.
- Do NOT re-attempt a standalone T9 PTP level tune — it is a documented vintage gap.
- `scripts/prep_validation.py` is loop-aware and safe to re-run at any point.

## Deliverables for this iteration

- `src/main.py` (or `src/table6.py`/`table8_9.py`) — revised per M1/M2/M3
- `results/table_2.md`, `table_3.md`, `table_6.md`, `table_8.md`, `table_9.md` — updated per committed table
- `preparations/assumptions.md` — append a new iteration log entry per issue addressed (five fields each)
- `SUMMARY.md` — read the latest combined assessment; do NOT edit (auditor-owned)
- `REPORT.md` — updated; lead with the data-quality summary and the corollaries evaluated this iteration

## Stop conditions

- **All blockers fixed and verified** → re-run prep_validation.py and the scorer (correct outer iteration N) → declare success or note remaining majors.
- **10-iteration cap reached** → escalate and write a partial REPORT.md.
- **All blockers fixed but majors remain** → declare partial and document in REPORT.md.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

This iteration is the clearest example yet of the audit loop doing its job. The single most important audit-1 criticism — that the D9/D10 tail was "retired" on a hedged, untested vintage-drift story — was taken seriously: the replicator rebuilt the full duration pipeline on an older Compustat vintage, reproduced the tail to three decimals, rejected vintage as the cause, and reopened the cells as genuinely open. That is precisely the demonstrated-evidence standard the rubric's methodology sub-check 7 exists to enforce, and it means the remaining tail divergence is now honestly framed as an unexplained construction question rather than a smug "consistent with vintage." The other four majors were each addressed with substance, not shells: the T8 universe was corrected (LTG panel now reproduces), the T12 conditional-tertile bug was root-caused (26-firm empty bins → sign flips), the T9 extraction was validated correct with a real 7×2 spot-check (and the real bug — reverse-split artifacts — was fixed), and the FM-mean preest estimator was committed. The residual is a tidy, interpretable set: one open construction question (D9/D10), two downstream level gaps (T6, T9), and one unmet corollary (T8 SUE/EG). The headline claim — 1.10%/mo downward-sloping term structure — is solidly replicated. The one process blemish from audit 1 (wrong inner-iteration number in the scorer) is clean, and the loss_trace now has exactly one row per outer iteration.
