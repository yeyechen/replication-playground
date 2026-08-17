---
iteration: 3
verdict: REPLICATED
blocker_count: 0
actionable_major_count: 0
requires_iteration: false
---

# Audit Report 3 — max_on_steroids_attempt5_deepseek

**Verdict:** REPLICATED
**Date:** 2026-08-16
**Auditor notes:** Audit-2's single actionable major (M1) — the ME-growth / CE pipeline defect inflating the CE coefficient 30× and inverting the T9 issuance-state ordering — is fixed with strong before/after evidence (corr(me_gr12,cumret12) 0.09→0.92; t2_ce_c4 −0.514→−0.0103 vs paper −0.017), landing the CE coefficient into Match and restoring the T9 state ordering. Loss 0.3623 → 0.3509 (+8 Match). The remaining FAIL/MISSING cells are all documented non-actionable residue ([THIRD-PARTY-DATASET] DHS/SY, [STRUCTURAL-SAMPLE-VARIANCE] interior decile / long-horizon / E(ISKEW) / β^MAX / ROE-IVOL scale cells). No blockers, no actionable majors remain.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 4 | 8/8 sub-checks pass; deviations documented (SY 1968-2016, DHS gap, log-form CE, E(ISKEW)/β^MAX offset) |
| Headline matching | 5 | T1 spread −1.02 vs −0.95, T3 −0.87 vs −0.81, CE −0.0103 vs −0.017; all headline cells Match, correct sign, monotonic |
| Data coverage | 3 | Period exact 1968-2022, universe close (1.74M stock-months, 17,856 permnos), 0-dup join; SY truncated, DHS absent |
| Concrete result matching | 3 | 455/701 committed cells Match (64.9%) — band 3 |
| Signal strength | 5 | Headline spread cells worst-case r ≈ 1.10 (T1 CAPM −1.54 vs −1.41) — all in [0.9, 1.1] |
| Corollary | 3 | C3(T8)/C4(T5) strong; C5(T9) 22/47 with max_lo residual ~2× but paper-insignificant cell |
| 7 | SUMMARY.md matches results/table_*.md | ✓ | Totals reproduce; T8 66M/30F now correct (audit-2 m1 fixed) |

## 2. Issues by severity

### Blockers (must fix)

None.

### Major (should fix)

None. Audit-2's M1 is resolved: `t2_ce_c4` = −0.0103 (paper −0.017) and `t6_ce_sprd` = 0.0161 (paper 0.019) are now within tolerance (confirmed in `eval/metrics.json`), and the T9 high-issuance state ordering is restored (max_hi −0.52, maxb_hi −0.77, maxb_lo −0.77 vs paper −0.72/−0.71/−0.65 — Match).

### Minor (cleanup)

- [m1] REPORT.md headline-section header says "iteration 2" while its body carries the iteration-3 tally (455M/222F/24M/7no, loss 0.3509).
  - File: `REPORT.md:11` ("## Headline tally (canonical scorer — eval/scoring.json, iteration 2)") and `REPORT.md:26` ("written by score_replication.py --iteration 2")
  - Likely cause: header/provenance text not refreshed when the tally was re-copied from the --iteration 3 scorer run.
  - Specific fix: change the two "iteration 2" references (lines 11 and 26) to "iteration 3"; no numbers change.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim | ✓ | T1/T3 RET-RF decline P1→P10; all spreads negative (paper sign) |
| 2 | Headline-magnitude claim | ✓ | T1 spread −1.02 vs −0.95 (r≈1.07); T3 −0.87 vs −0.81; CE −0.0103 vs −0.017 |
| 3 | Sample coverage ≥ 60% | ✓ | 1,743,269 stock-months, 17,856 permnos, full 1968-01→2022-12 (recomputed from panel.parquet) |
| 4 | Data-source choice justified | ✓ | CRSP vwretd/dsfhdr PIT, dsedelist delisting, PS-LIQ + SY M4.csv + FF user files — all cited in assumptions.md |
| 5 | prep_validation.py exit 0 | ✓ | "All present prep artifacts pass validation" |
| 6 | All committed tables have results files | ✓ | 9 tables → 9 table_*.md present |
| 7 | SUMMARY.md matches results/table_*.md | ✓ | Headline values reproduce; T8 66M/30F correct |
| 8 | No orphan folders | ✓ | No brace/glob-name folders |
| 9 | Diagnoses paired with fix attempts | ✓ | Iteration 14 carries full Diagnosis/Next fix/Before/After/Status |
| 10 | Cell status verification (scorer canonical) | ✓ | eval/scoring.json iteration 3: 455 Match / 222 FAIL / 24 MISSING / 7 no_effect; loss 0.3509; evaluate.py present |
| 11 | Corollary coverage | ✓ | C3(T8), C4(T5), C5(T9) each computed (T9 with documented max_lo residue) |
| 12 | Claim coverage of committed selection | ✓ | C1-C5 each covered by ≥1 table; budget_flag populated (>350 cells, full justification) |
| 13 | Sign conventions re-derived from paper | ✓ | Spreads 10-1 (high−low) negative per paper L273/L450; paper A7 state order −0.72/−0.43/−0.71/−0.65 |
| 14 | Reporting discipline (grids, citations, SE-less) | ✓ | Spreads carry NW t-stats; grids complete |
| 15 | REPORT.md headline freshness (DEV-010) | ✗ | Tally numbers ARE iteration 3 (455/222/0.3509), but header still labels them "iteration 2" (m1) |

## 4. Issues the agent should have caught (didn't)

1. The REPORT.md headline-tally provenance header was not relabeled from "iteration 2" to "iteration 3" when the numbers were refreshed from the canonical --iteration 3 scorer run (m1). The values themselves are correct and fresh; only the two surrounding "iteration 2" strings are stale.
2. The CE fix's documented side effect — T9 max_lo moved further from the paper (−0.90 vs −0.43, previously −0.66) — is reported honestly in assumptions.md Iteration 14 as [STRUCTURAL-SAMPLE-VARIANCE]. This is the correct call (the paper's max_lo is itself insignificant, t=−1.64), and the replicator did not attempt to spin it as a Match. No action required.

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "MAX on Steroids" (Bali, Ince & Ozsoylev) for slug `max_on_steroids_attempt5_deepseek`. The previous agent run completed with verdict **REPLICATED** (audit 3 at `replications/max_on_steroids_attempt5_deepseek/logs/audit3.md`). Read the audit first.

## Issues to address (priority order)

### [m1] — MINOR — refresh the REPORT.md headline-tally provenance label

`REPORT.md:11` and `REPORT.md:26` still say "iteration 2" while the tally block they describe is now the canonical iteration-3 tally (455 Match / 222 FAIL / 24 MISSING / 7 no_effect, loss 0.3509). The numbers are correct; only the two "iteration 2" strings are stale.

**Specific fix:**
1. Change the header at `REPORT.md:11` from "…iteration 2" to "…iteration 3".
2. Change `REPORT.md:26` from "`--iteration 2`" to "`--iteration 3`".
3. Do not touch any cell statuses or numeric values.

## Iteration discipline reminders

- This replication is at a documented-residue exit: all remaining non-Match cells carry a closed-vocabulary marker ([THIRD-PARTY-DATASET] DHS/SY, [STRUCTURAL-SAMPLE-VARIANCE] interior/long-horizon/E(ISKEW)/β^MAX/ROE-IVOL) with evidence in `assumptions.md`. The m1 cleanup above is the only remaining item; do not reopen closed residue unless you have a concrete new test result.
- If you do make any change, re-run the canonical scorer with `--iteration 3` (or the next audit number) and re-copy the tally into REPORT.md from `eval/scoring.json` — it is the sole source of truth for statuses.

## Inputs you should read

- `replications/max_on_steroids_attempt5_deepseek/logs/audit3.md` — this audit
- `replications/max_on_steroids_attempt5_deepseek/inputs/content.md` — paper ground truth
- `replications/max_on_steroids_attempt5_deepseek/preparations/assumptions.md` — Iteration 14 (CE fix evidence) and prior residue markers
- `replications/max_on_steroids_attempt5_deepseek/eval/scoring.json` — canonical tally (iteration 3)

## What NOT to redo

- Do not re-attempt the DHS/SY/BW-sentiment/PS-LIQ data gaps — documented [THIRD-PARTY-DATASET].
- Do not re-open the CE pipeline — the log-form fix is landed and evidenced (corr 0.92, coefficient into Match).
- Do not re-test E(ISKEW), β^MAX, ROE/IVOL-scale, or long-horizon Table-12 residues unless you have a new diagnostic that is not already in assumptions.md.

## Deliverables for this iteration

- `REPORT.md` — labels refreshed (m1); no numeric edits.
- Do NOT edit `SUMMARY.md` (auditor-owned).

## Stop conditions

- m1 fixed → re-run `prep_validation.py` to confirm exit 0 → declare success. No further outer iterations are expected.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

This is a clean third-iteration close. The trajectory is exemplary: audit 1 found five actionable majors (IVOL unit, DHS relabeling, ISKEW residual-moment bug, T9 index, ME-growth defect); audit 2 fixed four and deferred the ME-growth/CE defect to a concrete pipeline repair; iteration 3 closed that last item the way the earlier ISKEW bug was closed — by falsifying the initial hypothesis (the blowups were genuine CRSP share-restatements, not split-factor double-counting, per permno 89134's shrout 119→476,871) and adopting the canonically correct log-form Daniel-Titman net-issuance construction. The corr(me_gr12,cumret12) rise from 0.09 to 0.92 is the single most convincing piece of evidence in the whole replication: it shows the residual went from pure noise to a well-behaved net-issuance proxy, and the CE coefficient followed it into Match (−0.0103 vs −0.017). The honesty about the one adverse side effect (T9 max_lo drifting from −0.66 to −0.90 against the paper's insignificant −0.43) is the right posture — documented structural, no spin. The loss has been in a tight 0.351–0.374 band across three iterations with every remaining gap evidenced to a closed-vocabulary marker, which is why `requires_iteration` is now false: the replication has reached a documented-residue exit, not a strict zero-loss, and nothing actionable remains.
