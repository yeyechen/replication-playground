---
iteration: 1
verdict: REPLICATED
blocker_count: 0
actionable_major_count: 1
requires_iteration: true
---

# Audit Report 1 — novymarx_2012_is_momentum_really_momentum

**Verdict:** REPLICATED
**Date:** 2026-09-08
**Auditor notes:** Strong first iteration — 422/473 committed cells Match (89.2%), L = 0.1078, headline claims C1/C2 reproduce nearly exactly; residue is well-evidenced vintage/no-effect-tail variance plus two open cells with an untested hypothesis.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 4 | 7-8/8 sub-checks pass; the one soft spot is 2 open T6 cells with a diagnosed-but-untested hypothesis; all other FAILs carry quantitative test trails (SUE 4-denominator + PIT-vintage tests, UMD 2×3 rebuild). |
| Headline matching | 5 | C1 diff row 0.56 [2.40] vs paper 0.57 [2.42]; C2 means essentially exact (MOM_6,2 0.67 vs 0.67); FF4-alpha significant/no-effect contrast reproduces in inference. |
| Data coverage | 5 | Period exact (1008 months, 1927-01..2010-12); universe validated by Table 7 Panel A 25/25 Match (small quintile 1,758.8 vs 1,772); 0 duplicate (permno, month); DFF absence documented as scope reduction, not silent substitution. |
| Concrete result matching | 5 | 422/473 = 89.2% Match (band ≥85%); 0 MISSING, 0 SKIP. |
| Signal strength | 3 | Headline-table worst-case r: T2 intercept_s4 0.807/0.54 ≈ 1.49; T1 r62_late 0.23/0.36 ≈ 0.64 — inside [0.5, 2.0] but not [0.8, 1.2]; null cells null-to-null confirmed (intercept_s8). |
| Corollary | 5 | Non-headline tables T4/T5/T6/T7/T8: 292/324 = 90.1% Match (band ≥80%). |

## 2. Issues by severity

### Blockers (must fix)

None.

### Major (should fix)

- [M1] Two open T6 cells (`pc_m62_q5`, `pc_m62_q5_t`; ours 0.07 [0.49] vs paper 0.40 [2.25]) carry an explicitly untested hypothesis — iteration-4 entry proposes conditional-sort inner-breakpoint convention (Assumption 9, within-subsample vs unconditional NYSE) and universe-composition tilts, but no robustness run was executed. Cells are honestly left open, not retired — but per continuation semantics this is actionable.
  - File: `preparations/assumptions.md` (Iteration 4 entry, "T5 right-block" / Documented residue "Open" section); cells in `results/table_7.md`.
  - Likely cause: within-quintile momentum breakpoints computed on all subsample members vs unconditional NYSE breakpoints; possibly compounded by the all-stocks universe's microcap tail.
  - Specific fix: run the already-named candidate robustness — recompute Table 7 Panel C m62_q5 (and the T5 conditional grid) under unconditional NYSE inner breakpoints, report both, and either close the cells or attach a tested-cause marker.

### Minor (cleanup)

- [m1] `eval/scoring.json` top-level `loss` key is None (loss lives under `aggregates`); harmless for the validator but inconsistent with the front-matter schema if other tooling reads it top-level. No action needed unless tooling breaks.
- [m2] `src/evaluate.py` prints a diagnostic tally only; per-cell labels in `results/table_*.md` were pasted from its output. They all survive recomputation (auditor re-ran; T8 tally identical), so this is hygiene only — keep the evaluator wired into the pipeline.
- [m3] Pre-1945 UMD-anchor comovement (corr 0.878 vs paper's 0.99) is attributed to vintage at the strategy level; the replicator names per-month cross-section forensics of 1927-1945 as out of scope. Acceptable residue; do not spend an iteration on it unless FF4-loading FAILs widen.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim | ✓ | T4 IR spreads 1.02/0.74/1.05/0.97/0.86 vs paper 0.99/0.70/1.04/0.96/0.92; T6 Panels B/C momentum means monotone-declining for m62 as paper claims. |
| 2 | Headline-magnitude claim | ✓ | MOM_12,7 1.17%/mo (paper 1.20), MOM_6,2 0.67 (0.67), ind_intercept_s1 0.567 (0.57) — recomputed from `eval/metrics.json`, consistent with REPORT.md. |
| 3 | Sample coverage ≥ 60% | ✓ | 3,770,504 panel rows × 15 cols, 28,696 permnos; 1008 strategy months; Panel A firm counts within 1-2% of paper. |
| 4 | Data-source choice justified | ✓ | All-CRSP universe skip is paper-explicit (L91-101) with a `[CONVENTION-SKIPPED]` justification validated by Table 7 Panel A; delisting/VW conventions `[CONVENTION-APPLIED]` with rationale. |
| 5 | prep_validation.py exit 0 | ✓ | Exit 0; only the expected pre-audit warning (no audit file yet). |
| 6 | All committed tables have results files | ✓ | T1,T2,T3,T4,T6,T7,T8 → `results/table_{1,2,3,4,6,7,8,14}.md`, all 8 present. |
| 7 | REPORT.md values match artifacts | ✓ | Spot-checked intercept_s5 0.6659, sue_s4 38.16, ind_intercept_s1 0.5666, pa_nfirms_q1 1758.8, pa_pcap_q5 78.72, A_RR1_SP 1.018 — all match `eval/metrics.json` and results grids. |
| 8 | No orphan folders | ✓ | Slug root clean; only expected directories. |
| 9 | Diagnoses paired with fix attempts | ✓ | Iteration log entries all carry Diagnosis / Next fix / Before / After / Status; the two "none remaining within budget" entries cite executed tests. |
| 10 | Cell status verification | ✓ | Re-ran `src/evaluate.py`; per-cell statuses and tallies agree with `eval/scoring.json` on every table checked (T8 identical: 66/10/4, L=0.132). |
| 11 | Corollary coverage | ✓ | C3-C6 all covered by committed tables with computed results; asset-class corollaries (Tables 10-12) documented as catalog-missing in data_verification.json — non-actionable data limitation, not a silent skip. |
| 12 | Claim coverage of committed selection | ✓ | C1-C6 all covered; claim list matches the paper's substantive claims; no fabricated claims; budget_flag present (540 cells). |
| 13 | Sign conventions re-derived | ✓ | W-L spreads and diff row derived from paper definitions (winner-minus-loser, same-regression difference); signs reproduce; only near-zero null cells flip sign (both |t|<1.96, null-to-null confirmed). |
| 14 | Reporting discipline | ✓ | REPORT.md claims cite t-stats throughout; no SE-less headline; grid rows complete. |
| 15 | REPORT.md headline freshness | ✓ | Headline tally 422/51/0/67, L=0.1078 matches `eval/scoring.json` exactly. |

## 4. Issues the agent should have caught (didn't)

1. The T6 open-cell hypothesis (inner-breakpoint convention) was named in iteration 4 and explicitly deferred "if iteration budget remains" — the budget was then spent on SUE diagnostics, and the deferral was never revisited before close-out. A single cheap robustness run would have closed or evidenced the two open cells.
2. The `pc_m62_q5` narrative in REPORT.md says "our estimate is smaller than the paper's, in the paper's claimed direction" — correct, but the paper's cell is significant (t 2.25) while ours is not; the significance-category drop deserved explicit statement (significant-to-null on a secondary cell).

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "Novy-Marx (2012), Is Momentum Really Momentum?" for slug
`novymarx_2012_is_momentum_really_momentum`. The previous agent run completed with verdict **REPLICATED**
(audit 1 at `replications/novymarx_2012_is_momentum_really_momentum/logs/audit1.md`). Read the
audit first.

## Issues to address (priority order)

### [M1] — MAJOR — two open T6 cells with an untested hypothesis
`T6:pc_m62_q5` and `T6:pc_m62_q5_t` (paper 0.40 [2.25]; ours 0.07 [0.49]) are the only FAIL cells
left without a tested cause. The iteration-4 entry (`preparations/assumptions.md`) names two
candidate causes — conditional-sort inner breakpoints computed within the conditioning subsample
(Assumption 9) vs unconditional NYSE breakpoints, and all-stocks-universe microcap tilt — but no
robustness run was executed.

**Specific fix:**
1. Recompute the Table 7 Panel C m62 row (and, if cheap, the T5 conditional 6-2 grid) under
   unconditional NYSE inner breakpoints as a robustness variant in `src/main.py`.
2. Report both conventions side by side in `results/table_7.md`; keep the base convention that
   matches the paper's reading of "constructed within" (Assumption 9).
3. Either the variant closes the cells (adopt or document) or it does not — attach the test result
   to the iteration log entry and mark the cells with the evidenced closed-vocabulary marker
   (`[STRUCTURAL-SAMPLE-VARIANCE]` or `[VINTAGE-DRIFT]`) or leave them FAIL with the new evidence.
4. Verification: the two cells' status in `eval/scoring.json` should either flip to Match or carry a
   marker with a test result; no cell may remain "open, hypothesis untested".

### [m1] — MINOR — cleanup
Keep `src/evaluate.py` wired into the pipeline run so per-cell statuses in `results/table_*.md` are
always regenerated mechanically.

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every iteration log
  entry in `assumptions.md` must have all five fields: Diagnosis,
  Next fix, Before metric, After metric, Status. A diagnosis without
  a Next fix is incomplete — do not move on.
- **Read `rep/STUCK_AGENT_GUIDELINE.md` on your first debug cycle.**
  Don't rediscover failures that are already documented.
- **10-iteration cap per problem.** Hard stop at 10 and escalate to
  the human. A documented partial is more valuable than a paper-
  claiming success that does not actually replicate.
- **Diagnoses must be paired with fix attempts (exit gate).** Before
  declaring `partial`, walk `assumptions.md` and verify every
  diagnosed problem has at least one log entry with a non-empty
  `Next fix` line and a before/after metric.

## Inputs you should read

- `replications/novymarx_2012_is_momentum_really_momentum/logs/audit1.md` — this audit (full context)
- `replications/novymarx_2012_is_momentum_really_momentum/inputs/content.md` — paper ground truth
- `replications/novymarx_2012_is_momentum_really_momentum/preparations/` — prep contract (rules,
  tables selected, data verification, assumptions iteration log)
- `replications/novymarx_2012_is_momentum_really_momentum/src/main.py` — current code (will be
  modified)
- `replications/novymarx_2012_is_momentum_really_momentum/data/` — cached intermediates (recompute
  spot-checks from these)

## What NOT to redo

- Skip re-reading `SKILL.md` — the contract is the same.
- `scripts/prep_validation.py` is loop-aware (DEV-009) and safe to
  re-run at any point — mid-loop states no longer produce false
  errors. Re-run it if you changed a prep artifact; otherwise it is
  optional.
- Skip re-doing the clickhouse catalog scan — `data_verification.json`
  is current.
- **DO NOT** re-litigate the SUE residue (Family C) or the FF4-loading
  residue (Family A) — both carry executed test trails (4-denominator
  disambiguation, comp_pit PIT vintage, French 2×3 rebuild). Only
  revisit if a code change elsewhere moves them.
- **DO** re-run any sanity checks you add or modify — they are the
  gate that catches regressions.

## Deliverables for this iteration

- `replications/novymarx_2012_is_momentum_really_momentum/src/main.py` — revised with fix attempts
  logged per issue above
- `replications/novymarx_2012_is_momentum_really_momentum/results/table_7.md` (and any other
  touched table) — updated
- `replications/novymarx_2012_is_momentum_really_momentum/preparations/assumptions.md` — append a
  new iteration log entry for every issue addressed (Diagnosis, Next fix, Before metric, After
  metric, Status)
- `replications/novymarx_2012_is_momentum_really_momentum/SUMMARY.md` — read the latest combined
  assessment to understand the auditor's verdict and score; do NOT edit (the auditor owns this file)
- `replications/novymarx_2012_is_momentum_really_momentum/REPORT.md` — updated; lead with the
  data-quality summary and refresh the headline tally from `eval/scoring.json`

## Stop conditions

- **All blockers fixed and verified** → re-run prep_validation.py
  and any sanity checks → if both pass, declare success or note
  remaining majors in `REPORT.md`; the next audit updates `SUMMARY.md`.
- **10-iteration cap reached** on a single problem → escalate to
  the human and write a partial `REPORT.md`; do not edit `SUMMARY.md`.
- **All blockers fixed but majors remain** → declare partial and
  document the gap in `REPORT.md`. The auditor's `SUMMARY.md` verdict
  (REPLICATED / FAILED) is independent of this loop decision.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

This is an unusually disciplined first iteration. The inner-loop trace shows genuine
diagnose-fix-verify cycles (the one-month signal-indexing fix was pinned to paper evidence and
moved MOM_12,7 from 0.99 to 1.17%/mo; the worker correctly rejected a spec error in the FM diff-row
construction), honest FAIL accounting (no status inflation — the auditor's evaluator re-run
reproduces every tally), and real hypothesis testing before retiring FAILs (SUE: 4-denominator
disambiguation plus a PIT-vintage comparison; UMD anchor: a French-methodology 2×3 rebuild). The
residue families are properly marked with closed-vocabulary markers and quantitative evidence. The
single actionable gap is the deferred breakpoint-convention robustness for the two open T6 cells.
Non-actionable limitations: DFF (2000) book equity missing (T1 early columns, Table 9 skipped),
country/commodity/FX asset classes absent from the catalog (Tables 10-12), and pre-1945 factor
comovement drift against French-published series.
