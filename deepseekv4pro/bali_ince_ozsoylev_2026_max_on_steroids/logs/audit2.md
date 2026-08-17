---
iteration: 2
verdict: REPLICATED
blocker_count: 0
actionable_major_count: 1
requires_iteration: true
---

# Audit Report 2 — max_on_steroids_attempt5_deepseek

**Verdict:** REPLICATED
**Date:** 2026-08-16
**Auditor notes:** The iteration-2 fixes landed on every audit-1 major: IVOL unit fixed, DHS relabeled MISSING, a real ISKEW residual-moment bug was found via single-firm spot-check and corrected, and T9 moved 10→18 Match via a median aggregate-issuance index. Loss 0.3738 → 0.3623. The one remaining actionable item is a pipeline-level ME-growth (`me_gr12`) data defect that inflates the CE coefficient 30× and inverts the T9 MAX-state ordering.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 4 | 8/8 sub-checks pass; deviations documented (SY 1968-2016, DHS gap, CE structural, E(ISKEW)/β^MAX offset) |
| Headline matching | 5 | T1 spread −1.02 vs −0.95, T3 −0.87 vs −0.81; all headline spreads/t-stats Match, correct sign, monotonic profiles |
| Data coverage | 3 | Period exact 1968-2022, universe close (1.74M stock-months, 17,856 permnos), 0-dup join; SY truncated, DHS absent |
| Concrete result matching | 3 | 447/701 committed cells Match (63.8%) — band 3 |
| Signal strength | 5 | Headline spread cells worst-case r ≈ 1.10 (T1 CAPM −1.54 vs −1.41) — all in [0.9, 1.1] |
| Corollary | 3 | C3(T8)/C4(T5) strong; C5(T9) improved 18/47 (38%) but remains weakest |
| 7 | SUMMARY.md matches results/table_*.md | ✓ | T8 per-table split is stale-by-1 (see m1) but total Mix/FAIL reproduce |

## 2. Issues by severity

### Blockers (must fix)

None.

### Major (should fix)

- [M1] ME-growth pipeline defect inflates the CE coefficient 30× and corrupts the T9 issuance state split.
  - File: `src/main.py` (the 12-month market-equity growth `me_gr12` feeding `ce=`cei`); `results/table_4.md` (ce −0.514 vs paper −0.017), `results/table_a7.md` (MAX-state ordering)
  - Evidence: `preparations/assumptions.md` Iteration 12 records corr(me_gr12, cumret12) = 0.09 (split-adjusted 0.071), where Daniel-Titman net issuance requires ≈0.95 (the 12-mo ME growth must nearly cancel the 12-mo return); me_gr12 std = 6.8 (≈40× the return std 0.83), so `ce` is pure ME noise. Four FM variants (raw, pre-winsorized, |ce|>10-dropped, ln(1+ce)) all failed to reach −0.017; a synthetic well-behaved ce still gave −2.52, confirming a source construction bug rather than an FM-application bug.
  - Likely cause: near-zero/stale 12-mo-lagged market-equity ratios blow up the ME-growth ratio (split-adjustment mismatch on the lag).
  - Specific fix: repair the `me_gr12` split-adjustment in `main.py` (12-mo-lagged ME must re-use the contemporaneous split factor so ME growth ≈ cumulative return), re-derive `ce`, re-run `sections_678.py` + `sections_9_11.py` + canonical scorer `--iteration 3`; expect t2_ce_c4 to move toward −0.017 and the T9 MAX-state spreads to re-invert correctly.

### Minor (cleanup)

- [m1] T8 per-table tally is stale: `REPORT.md` and `logs/log2.md` both report T8 64M/32F, but the canonical `eval/scoring.json --iteration 2` records T8 66 Match / 30 FAIL (total Match=447 is consistent everywhere; the internal T8 split drifted by 2 on the fresh scorer run).
  - File: `REPORT.md` (headline tally, "T8 64M/32F"), `logs/log2.md` (final per-cell table)
  - Specific fix: re-copy the T8 split from `eval/scoring.json` (66M/30F) into REPORT.md; no cell statuses change.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim | ✓ | T1/T3 RET-RF decline P1→P10; spreads negative (paper sign) |
| 2 | Headline-magnitude claim | ✓ | T1 spread −1.02 vs −0.95 (r≈1.07); T3 −0.87 vs −0.81 |
| 3 | Sample coverage ≥ 60% | ✓ | 1.74M stock-months, 17,856 permnos, full 660 months; data_verification coverage_pct 69 |
| 4 | Data-source choice justified | ✓ | CRSP vwretd, dsfhdr PIT, dsedelist delisting, PS-LIQ user file — all cited in assumptions.md |
| 5 | prep_validation.py exit 0 | ✓ | Passes after the audit-1 front-matter count fix (5→4 actionable majors) |
| 6 | All committed tables have results files | ✓ | 9 tables → 9 table_*.md present |
| 7 | SUMMARY.md matches results/table_*.md | ✓ | Totals reproduce; T8 per-table split off by 2 (m1) |
| 8 | No orphan folders | ✓ | No brace/glob-name folders |
| 9 | Diagnoses paired with fix attempts | ✓ | Iterations 12-13 all carry Diagnosis/Before/After/Status |
| 10 | Cell status verification (scorer canonical) | ✓ | score_replication.py reproduces 447/230/24/7; evaluate.py aligned, 0 divergent |
| 11 | Corollary coverage | ✓ | C3(T8), C4(T5), C5(T9) each computed; T9 weak but computed |
| 12 | Claim coverage of committed selection | ✓ | C1-C5 each covered by ≥1 table; omitted tables are robustness/appendix (scope-guardrail OK) |
| 13 | Sign conventions re-derived from paper | ✓ | Spreads 10-1 (high−low); paper L1122/L2204 negative; sign matches |
| 14 | Reporting discipline (grids, citations, SE-less) | ✓ | Spreads carry NW t-stats; "significant" claims cite t; grids complete |
| 15 | REPORT.md headline freshness (DEV-010) | ✗ | Total Match (=447) fresh, but T8 split copied as 64/32 vs canonical 66/30 |

## 4. Issues the agent should have caught (didn't)

1. The T8 per-table split drifted by 2 cells (−2 FAIL / +2 Match in T8) between the pre-final tally the log records and the fresh canonical scorer run, and neither REPORT.md nor log2's final grid was re-copied from `eval/scoring.json` after the final scorer invocation. The total is correct; the T8 row is stale (m1).
2. The CE coefficient's 30× discrepancy was investigated thoroughly (four variants, synthetic-probe) but the root cause — the `me_gr12` ME-growth split-adjustment defect evidenced by corr 0.09 vs the expected 0.95 — was deferred to "repair main.py" rather than repaired in-scope. It is the single highest-leverage remaining fix: it likely cascades into the T9 inversion and the BM sign/composition gap, so a future audit should verify the fix actually lands in main.py rather than being re-deferred.

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "MAX on Steroids" (Bali, Ince & Ozsoylev) for slug `max_on_steroids_attempt5_deepseek`. The previous agent run completed with verdict **REPLICATED** (audit 2 at `replications/max_on_steroids_attempt5_deepseek/logs/audit2.md`). Read the audit first.

## Issues to address (priority order)

### [M1] — MAJOR — repair the ME-growth pipeline defect (CE coefficient + T9 state split)

The CE coefficient in Table 4 is 30× too large (−0.514 vs paper −0.017) and the T9 issuance-state MAX ordering is inverted, both traced in `assumptions.md` Iteration 12/13 to a corrupted 12-month market-equity growth series: corr(me_gr12, cumret12) = 0.09 (should be ≈0.95 for Daniel-Titman net issuance, where `ce = me_gr12 − cumret12` should be a small residual), and me_gr12 std = 6.8 (≈40× the return std 0.83). The four FM variants already tested all moved the coefficient only to −0.51/−0.30, and a synthetic well-behaved ce still gave −2.52, confirming the defect is in the `ce` source, not the FM application.

**Specific fix:**
1. In `src/main.py`, locate the 12-month market-equity growth computation (`me_gr12`) and its lagged-ME denominator. The near-zero/stale lagged-ME ratios blow up the growth ratio — repair the split-adjustment so the 12-mo-lagged ME re-uses the contemporaneous split factor, forcing ME growth ≈ cumulative return.
2. Recompute `ce` (= `cei`) from the corrected `me_gr12`, keeping the paper's literal firm-level CE and the monthly 1/99 FM winsorization.
3. Re-run `sections_678.py` (FM CE coefficient) and `sections_9_11.py` (T9 issuance-state split), then `evaluate.py` and `scripts/score_replication.py replications/max_on_steroids_attempt5_deepseek/ --iteration 3`.
4. Verification: corr(me_gr12, cumret12) should rise to ≈0.9; t2_ce_c4 should move toward −0.017 (t −4.43); the T9 MAX-state spreads should re-order so the high-issuance state carries the larger MAX premium (paper max_hi −0.72 / max_lo −0.43).

### [m1] — MINOR — refresh the T8 per-table tally

`eval/scoring.json --iteration 2` records T8 66 Match / 30 FAIL; `REPORT.md` and `logs/log2.md` still say 64/32. Re-copy the T8 split (66M/30F) into REPORT.md. No cell statuses change.

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every `assumptions.md` entry needs all five fields (Diagnosis, Next fix, Before metric, After metric, Status).
- **Read `rep/STUCK_AGENT_GUIDELINE.md` on your first debug cycle.**
- **Repair in-scope, don't re-defer.** The CE root cause was already diagnosed to main.py in iteration 2; this iteration must attempt the pipeline fix, not re-document the diagnosis.
- **Confirm cell moves re-copy REPORT.md headline tally and per-table splits from `eval/scoring.json`** (the canonical scorer is the only source of truth for statuses).

## Inputs you should read

- `replications/max_on_steroids_attempt5_deepseek/logs/audit2.md` — this audit
- `replications/max_on_steroids_attempt5_deepseek/inputs/content.md` — paper ground truth
- `replications/max_on_steroids_attempt5_deepseek/preparations/assumptions.md` — Iterations 12/13 (CE root cause)
- `replications/max_on_steroids_attempt5_deepseek/src/main.py` — the `me_gr12` / `ce` construction (will be modified)
- `replications/max_on_steroids_attempt5_deepseek/src/regen_ce_betamax.py` — CE/β^MAX regen

## What NOT to redo

- Skip re-reading `SKILL.md` — the contract is unchanged.
- Skip the clickhouse catalog scan — `data_verification.json` is current.
- DHS/SY/BW-sentiment/PS-LIQ gaps are documented [THIRD-PARTY-DATASET]; do not re-attempt.
- IVOL (1.8×), ROE (2.5×), E(ISKEW) (−35% level), β^MAX (−40% dispersion), and long-horizon K≥18 cells are documented [STRUCTURAL-SAMPLE-VARIANCE]; leave as residue unless the M1 fix indirectly moves them.

## Deliverables for this iteration

- `src/main.py` revised with the `me_gr12` split-adjustment fix, logged in `assumptions.md`
- `results/table_4.md`, `results/table_a7.md` updated if the CE fix moves cells
- `preparations/assumptions.md` — append a new iteration-log entry for the M1 fix (all five fields)
- `REPORT.md` — refreshed headline tally and corrected T8 per-table split
- Do NOT edit `SUMMARY.md` (auditor-owned)

## Stop conditions

- M1 fixed and verified (corr ≈0.9, CE within ~40% of −0.017, T9 ordering correct) → re-run `prep_validation.py` → declare success or note remaining residue.
- If the ME-growth fix provably cannot recover the CE coefficient after a documented 2-variant attempt, mark it `[STRUCTURAL-SAMPLE-VARIANCE]` with the before/after evidence and stop — do not silently leave it 30×.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

This replication is in excellent shape for a second outer iteration. The most impressive piece is the M3b ISKEW diagnose-and-fix: rather than accepting the −35% E(ISKEW) offset as "structural", the worker ran a single-firm spot-check (permno 59328, 1998-01), hand-computed the FF3 residual skewness (−0.2436), and found a real bug — the rolling residual-moment expansion was omitting the intercept β₀, biasing Sr₃ ~51×. After the fix the per-permno value matched the hand computation exactly. That single demonstration redeems the entire E(ISKEW) method as correct-by-construction and leaves only a genuine level-offset as residue. The symmetry with the CE situation is instructive: the CE 30× gap has *not* yet received the same treatment — the worker traced it to the `me_gr12` pipeline (corr 0.09) but deferred the actual repair to "main.py" rather than closing it the way ISKEW was closed. That asymmetry is the one meaningful remaining gap, and it is why `requires_iteration` remains true even though the bright-line verdict is REPLICATED. The headline claims (MAX explained by mispricing; MAX^β robustness) are already reproduced within ~10% and are not in question.
