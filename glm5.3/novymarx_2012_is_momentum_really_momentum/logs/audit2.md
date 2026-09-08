---
iteration: 2
verdict: REPLICATED
blocker_count: 0
actionable_major_count: 0
requires_iteration: false
---

# Audit Report 2 — novymarx_2012_is_momentum_really_momentum

**Verdict:** REPLICATED
**Date:** 2026-09-08
**Auditor notes:** Audit-1 [M1] fully resolved via a properly tested convention correction; 428/473 committed cells Match (90.5%), L = 0.0951, no open cells remain; all 45 residual FAILs carry closed-vocabulary markers with executed test evidence (Families A/B/C).

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 5 | All 8 sub-checks pass; the one prior soft spot (2 open T6 cells) was closed by a discriminating convention test (textual citation content.md L1701 + multi-cell alignment), and every remaining FAIL family carries a quantitative test trail. |
| Headline matching | 5 | C1 diff row 0.56 [2.40] vs paper 0.57 [2.42]; C2 MOM_6,2 mean exactly 0.67 vs 0.67; FF4-alpha significance contrast reproduces exactly in inference; Sharpe ratio 1.87× vs the paper's "more than twice". |
| Data coverage | 5 | Period exact (1008 months, 1927-01..2010-12); Panel A universe validator 25/25 Match; 0 duplicate (permno, month); DFF absence documented as scope reduction. |
| Concrete result matching | 5 | 428/473 = 90.5% Match (band ≥85% in RUBRIC, ≥90% in SKILL — satisfies both); 0 MISSING, 0 SKIP. |
| Signal strength | 3 | Headline-table worst-case r: T2 intercept_s4 0.807/0.54 ≈ 1.49 (within [0.5, 2.0], outside [0.8, 1.2]); null-to-null confirmed on intercept_s8. Same band as audit 1 — the corrected convention did not touch T2. |
| Corollary | 5 | Non-headline tables T3–T8: 360/392 = 91.8% Match (band ≥80%); T6 improved 95→99 Match after the convention correction. |

## 2. Issues by severity

### Blockers (must fix)

None.

### Major (should fix)

None actionable. Residue review (documented, non-actionable):

- Family A — [VINTAGE-DRIFT] (10 cells, T2): FF-factor loading drift vs French-published series; tested via a French-methodology 2×3 UMD rebuild (corr 0.878). Non-actionable (external published-series vintage).
- Family B — [STRUCTURAL-SAMPLE-VARIANCE] (27 cells, T1/T3/T4/T5/T6/T7/T8): t-cells of estimates the paper itself reports as insignificant; our statistics sit in the same no-effect region but outside the ±50%/±0.5 band on near-zero values. Non-actionable (near-zero tail variance).
- Family C — [VINTAGE-DRIFT]+[STRUCTURAL-SAMPLE-VARIANCE], both tested (8 cells, T8): SUE slope ~1.7× paper; denominator ambiguity excluded over 4 readings, PIT-vintage test executed (moves the slope more than the gap but undershoots). No tested construction reproduces the paper value; documented residue.

### Minor (cleanup)

- [m1] `eval/scoring.json` top-level `loss` key is absent (loss lives under `aggregates`); the validator and scorer read `aggregates` so nothing breaks, but keep the schema consistent if other tooling reads it top-level. No action required unless tooling breaks.
- [m2] `preparations/loss_function.json` is absent — the scorer runs on status counts. Informational; adding it would only enable per-cell weights.
- [m3] Keep `src/evaluate.py` wired into the pipeline run (audit-1 [m2]); it reproduces every per-table tally, so it should stay the mechanical source of per-cell labels.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim | ✓ | T4 IR spreads 1.02/0.74/1.05/0.97/0.86 vs paper 0.99/0.70/1.04/0.96/0.92; T6 Panels B/C momentum means monotone-declining for m62. |
| 2 | Headline-magnitude claim | ✓ | Recomputed from `eval/metrics.json`: pc_m62_q5 0.3607 (closed cell, vs paper 0.40 [2.25], t 2.01); intercept_s4 0.807; ind_intercept_s1 0.567; all consistent with REPORT.md. |
| 3 | Sample coverage ≥ 60% | ✓ | Unchanged: 3.77M panel rows, 28,696 permnos, 1008 strategy months; Panel A counts within 1–2% of paper. |
| 4 | Data-source choice justified | ✓ | All-CRSP universe skip is paper-explicit (L91-101) with `[CONVENTION-SKIPPED]`; delisting/VW conventions `[CONVENTION-APPLIED]` with rationale. |
| 5 | prep_validation.py exit 0 | ✓ | Exit 0; all prep artifacts pass. |
| 6 | All committed tables have results files | ✓ | T1,T2,T3,T4,T6,T7,T8,T14 → 8 `results/table_*.md` files present. |
| 7 | REPORT.md values match artifacts | ✓ | Headline tally 428/45/0/67, L=0.0951 matches `eval/scoring.json`; per-claim anchor values spot-checked against metrics. |
| 8 | No orphan folders | ✓ | Slug root clean. |
| 9 | Diagnoses paired with fix attempts | ✓ | Iteration-6 entry (audit [M1]) has all five fields; iteration-7 adoption entry carries before/after tallies and a dated correction of Assumption 9 (not a silent overwrite). |
| 10 | Cell status verification | ✓ | Re-ran `src/evaluate.py`; every per-table tally identical to `eval/scoring.json` (T5 22/4/14, T6 99/1/5, T8 66/10/4, etc.). |
| 11 | Corollary coverage | ✓ | C3–C6 covered by committed tables with computed results; asset-class corollaries (Tables 10–12) documented as catalog-missing — non-actionable data limitation, not a silent skip. |
| 12 | Claim coverage of committed selection | ✓ | C1–C6 all covered; no fabricated claims; budget flag present (540 cells). |
| 13 | Sign conventions re-derived from paper | ✓ | W-L spreads and diff rows reproduce the paper's direction; sign disagreement occurs only on near-zero null cells where both |t|<1.96 (null-to-null, e.g. intercept_s8, pe_m62_q4). |
| 14 | Reporting discipline | ✓ | REPORT.md claims cite t-stats throughout; the corrected-convention cells are reported with both side-by-side grids in results/table_6.md and table_7.md (no omitted rows); no SE-less headline. |
| 15 | REPORT.md headline freshness | ✓ | Headline tally refreshed to iteration-2 values (428/45/0/67, L=0.0951) — matches `eval/scoring.json` exactly. |

## 4. Issues the agent should have caught (didn't)

1. Nothing material. The two newly-failing T5 t-cells (`alpha_cond127_q2_t`, `alpha_cond62_q2_t`) introduced by the convention switch are correctly reclassified into Family B with a dated correction note rather than hidden — the handling is what audit 1 asked for.
2. Cosmetic only: the scorer warning about the absent `loss_function.json` has now appeared on two consecutive iterations; either add the file or note in REPORT.md that per-cell weighting is intentionally unused.

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "Novy-Marx (2012), Is Momentum Really Momentum?" for slug
`novymarx_2012_is_momentum_really_momentum`. The previous agent run completed with verdict **REPLICATED**
(audit 2 at `replications/novymarx_2012_is_momentum_really_momentum/logs/audit2.md`). Read the
audit first.

## Issues to address (priority order)

### None — no blockers, no actionable majors

Audit 2 confirms the audit-1 [M1] fix: the unconditional-NYSE inner-breakpoint convention
(Assumption 9 corrected, iteration 7) closed the two open T6 cells (pc_m62_q5 0.36 [2.01] vs
paper 0.40 [2.25]) and improved T5/T6 to 22/4/14 and 99/1/5. Canonical tally: 428 Match /
45 FAIL / 0 MISSING / 67 no_effect, L = 0.0951. All 45 residual FAILs fall into three
documented residue families (A: vintage FF loadings; B: near-zero t-cells of paper-insignificant
estimates; C: tested-but-unresolved SUE slopes), each with executed test evidence in
`preparations/assumptions.md`. The loop-control signal is `requires_iteration: false`
(documented-residue exit).

### Optional cleanup only (do NOT spend an iteration on these alone)
1. [m1] Consider adding `preparations/loss_function.json` (even a trivial one) so the scorer
   stops warning, or note in REPORT.md that per-cell weighting is intentionally unused.
2. [m2] Keep `src/evaluate.py` wired into the pipeline run as the mechanical source of
   per-cell labels.

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every iteration log
  entry in `assumptions.md` must have all five fields: Diagnosis,
  Next fix, Before metric, After metric, Status.
- **Read `rep/STUCK_AGENT_GUIDELINE.md` on your first debug cycle.**
- **10-iteration cap per problem.** Hard stop at 10 and escalate to
  the human.
- **Diagnoses must be paired with fix attempts (exit gate).**

## Inputs you should read

- `replications/novymarx_2012_is_momentum_really_momentum/logs/audit2.md` — this audit
- `replications/novymarx_2012_is_momentum_really_momentum/REPORT.md` — current self-report
- `replications/novymarx_2012_is_momentum_really_momentum/preparations/assumptions.md` —
  residue evidence (Families A/B/C) and the dated Assumption-9 correction

## What NOT to redo

- **DO NOT re-litigate the residue families.** Family A (FF-loadings), Family B (near-zero
  t-cells), and Family C (SUE slopes) all carry executed test trails (2×3 UMD rebuild,
  4-denominator disambiguation, comp_pit vintage test). Revisit only if a code change
  elsewhere moves them.
- **DO NOT revert the Assumption-9 convention** — it is adopted on textual + discriminating
  empirical evidence; both conventions remain reported side by side in results/table_6.md
  and results/table_7.md.
- Skip re-reading SKILL.md; skip the clickhouse catalog scan; re-run prep_validation.py only
  if you change a prep artifact.

## Deliverables (only if you run a cleanup iteration)

- `REPORT.md` refreshed; headline tally from `eval/scoring.json`.
- New iteration log entries for anything touched (five fields each).

## Stop conditions

- **No blockers or actionable majors remain.** Unless the human requests the optional
  cleanup, the replication is complete; the auditor's SUMMARY.md verdict (REPLICATED) stands.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

This iteration is a model of how the audit loop should work. Audit 1 flagged exactly one
actionable item — two open cells retired on an untested hypothesis — and the replicator
responded with a robustness run that was genuinely discriminating: the unconditional-NYSE
inner-breakpoint reading aligns multiple independent cells simultaneously (pc_m62_q5,
Panel D m62 q5, the T5 conditional 6-2 grid with q1 exact at 0.26), is supported by the
paper's own table note ("Portfolio break points based on NYSE stocks only", L1701), and was
adopted with a dated correction of Assumption 9 rather than a silent overwrite. The
convention switch honestly netted two new near-zero-t FAILs, which were correctly classified
into Family B rather than hidden. The evaluator re-run reproduces every tally, REPORT.md's
headline is fresh, and the residue is fully marker-covered with test evidence. Loss improved
0.1078 → 0.0951; the remaining gap is documented, evidenced, and non-actionable
(vintage-against-published-series, near-zero-tail variance, and a tested-but-unresolved SUE
construction). Non-actionable data limitations that remain: DFF (2000) book equity
(Table 1 early columns, Table 9 skipped), country/commodity/FX asset classes (Tables 10–12),
and pre-1945 factor comovement drift. Loop exit under documented-residue criterion B is
justified.
