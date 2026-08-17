---
iteration: 1
verdict: FAILED
blocker_count: 1
actionable_major_count: 4
requires_iteration: true
---

# Audit Report 1 — max_on_steroids_attempt2

**Verdict:** FAILED
**Date:** 2026-08-15
**Auditor notes:** Methodology pipeline built end-to-end, but per-cell magnitudes are 3-5× too small on the headline spreads and the Fama-MacBeth MAX coefficient has the wrong sign on Tables 4 and 8. Match rate from the agent's own evaluator is 3.0% (2/66) with 50 FAIL and 14 MISSING. Three rubric dimensions score 1 (Concrete Result, Signal Strength, Corollary), pulling the overall to 1.83.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 3/5 | 6 of 8 sub-checks pass; FAIL closed by hedged "most likely" without a test (sub-check 7); sign-flip on T4/T8 FM regression breaks sub-check 8. |
| Headline matching | 2/5 | Both headline spreads have the right sign and shape but magnitude is 3-5× too small (T1 10-1 spread ratio 0.27; T6 ratio 0.23). |
| Data coverage | 3/5 | Sample starts 1970 vs paper 1968 (24 months dropped); MAX@P10 = 8.74% vs paper 7.1% suggests ~20% universe composition drift; SY/DHS/PS_LIQ absent (documented). |
| Concrete result matching | 1/5 | Agent's own evaluator: Match 2 / FAIL 50 / MISSING 14 (rate 3.0%, <30%). |
| Signal strength | 1/5 | Worst headline r = 0.23 (T6 10-1 RET-RF spread) — outside [0.33, 3.0]. T1 P10_RET_RF cell also wrong sign (+0.86 vs paper −0.32). |
| Corollary | 1/5 | No corollary result has any computed match; 14 cells are MISSING outright (FFCPS, FF6PS, SY, DHS columns). |
| 7 | SUMMARY.md matches results/table_*.md | n/a (SUMMARY.md not yet authored by replicator; auditor owns it) | n/a |

**Overall: 1.83 / 5.00 — FAILED** (mean of six dimensions; 3 of 6 = 1 → kill switch)

## 2. Issues by severity

### Blockers (must fix)

- [B1] **Headline sign-flip on T4 Col1 MAX and T8 Col1 D10.** Paper expects MAX coefficient = −0.210 (t = −6.15) and D10 = −1.027% (t = −6.61); replication gives +0.022 (t = +0.33) and +0.048% (t = +0.13) respectively. In our panel, high-MAX stocks have **slightly positive** future excess returns — the opposite of the paper's central finding. This is a load-bearing methodology bug that invalidates Tables 4 and 8.
  - File: `src/run_tables.py:269-362` (table4) and `src/run_tables.py:365-472` (table8)
  - Likely cause: `ret_xs = ret_fwd1 − rf` and FM regression are correctly wired, but the relationship between MAX and future returns is inverted. Possible roots: (a) the daily universe construction over-counts "spike days" so MAX picks up stale information; (b) the `ret_fwd1` is aligned on month boundaries that are off by one (current month vs next month); (c) the missing-month `ret` (e.g., `nan`/missing days) is being treated as zero by OLS, biasing `ret_xs` toward zero. Without a per-stock-month trace, the cause cannot be pinpointed.
  - Specific fix: (i) verify `ret_fwd1` actually equals `lead(ret)` within permno (not a different alias); (ii) check whether `ret = 0` rows inflate the cross-section; (iii) for each (month, decile), print n_obs and confirm sign of mean(ret_xs) per decile; (iv) try winsorizing `ret_xs` (paper does not, but the missing-return treatment may need it).

### Major (should fix)

- [M1] **All headline magnitudes are 3-5× too small.** T1 10-1 RET-RF spread = −0.26% vs paper −0.95% (r = 0.27). T6 10-1 RET-RF spread = −0.19% vs paper −0.81% (r = 0.23). T1 10-1 FF3 alpha = −0.60% vs paper −1.16% (r = 0.52). T6 10-1 FF3 alpha = −0.55% vs paper −0.90% (r = 0.61). The direction is right but the effect is anemic.
  - File: `src/run_tables.py:118-179` (table1) and `src/run_tables.py:182-266` (table6)
  - Likely cause: my independent recomputation of the panel shows MAX@P10 = 8.83% vs paper 7.1%. The MAX signal's right tail is too fat (likely because the daily universe includes more "spike" stocks than the paper). The 10-1 spread is monotone but the level is suppressed because the bottom decile is also inflated.
  - Specific fix: (i) re-derive MAX with a stricter 15-obs monthly minimum (paper §3.1 L167-169); (ii) re-check whether the $5 price floor is being applied to every daily obs vs month-end — assumption A4 says "every daily observation" but the paper convention is month-end; (iii) check whether the panel uses a permno-with-deduplication on msenames that drops name-boundary observations the paper keeps.

- [M2] **Sample starts 1970 vs paper 1968.** The cached panel begins at 197001; the paper's sample is January 1968 – December 2022. ~24 months (4% of the sample) are missing.
  - File: `data/panel.parquet`; `src/sql/02_max_signal.sql`
  - Likely cause: the MAX SQL filters daily data `>= '1967-01-01'`, but the MAX computation itself requires 15 daily obs (≥12 months prior); with 1967-1969 daily data, the MAX can be computed for 1968 but the join may be dropping it.
  - Specific fix: re-run the panel with the MAX SQL query; check whether MAX in `data/max_signal.parquet` covers 1968-01 onwards; if not, debug the 15-daily-obs minimum to ensure the lookback buffer is honored.

- [M3] **`Canonical scorer cannot parse eval/metrics.json`.** `scripts/score_replication.py` reads `eval/metrics.json` with key convention `table_1#P1_RET_RF` (per the canonical schema), but the agent's `src/evaluate.py` writes a nested `metrics` object whose top-level key is the literal string `"metrics"`, leaving the canonical scorer to flag every cell MISSING. The audit must therefore rely on the agent's own evaluator tally (Match 2 / FAIL 50 / MISSING 14) rather than `eval/scoring.json`.
  - File: `src/evaluate.py:209-217` (write block); `scripts/score_replication.py`
  - Specific fix: in `src/evaluate.py`, write `eval/metrics.json` as `{ "<cell>": { "value": ..., "t_stat": ... }, ... }` (flat dict keyed by cell name), not nested under `"metrics"`. The canonical scorer also expects `paper`, `ours`, `tolerance_pct`, `status`, `rel_err` per cell; agent's metrics.json needs restructuring.

- [M4] **`assumptions.md A10 closes FAILs without diagnostic evidence`.** Assumption 10 reads: *"Possible causes: CRSP vintage differences; Universe filter differences; Sample inclusion criteria; The MAX signal picks up too many spike days..."* No test result (sample comparison, alternative-vintage re-run, filter re-run) backs any of these. Per Step 5 sub-check 7, this is "retired with hedged language" — actionable.
  - File: `preparations/assumptions.md:57-67`
  - Specific fix: pick one specific candidate cause and run the cheap test it implies. For example: if the cause is the daily-universe over-inclusion of spike days, restrict the universe to month-end $5 (instead of every-daily $5) and recompute Table 1 10-1 spread; record the new before/after spread in `assumptions.md` A10b.

### Minor (cleanup)

- [m1] **Two duplicate `if __name__ == "__main__"` blocks in main.py.** `src/main.py:251` and `src/main.py:256`. Harmless but evidence of careless merge.
- [m2] **Agent's `src/evaluate.py` key matcher has a relaxed-match bug.** At `src/evaluate.py:154-156`, when `target_name == suffix.replace('-', '_')` fails, it falls back to `target_name.startswith(suffix.split('_')[0])` — which means a target named `P10_P1_FF3_alpha_spread` will match the very first metric key starting with `P10` (which is `P10_RET-RF`). All FF3/FFC4/FF5/FF6 alpha cells therefore read the P1 RET-RF value (1.12) instead of the actual alpha. This explains why every T1/T6 alpha column shows the same `Ours = 1.12`. The Match 2 / FAIL 50 tally is partly an artifact of the matcher, but the magnitudes are still wrong so the verdict stands.
- [m3] **Universe drift not directly reported.** Paper does not state avg stocks/month, but the MAX@P10 ratio (8.74% vs 7.1%) is consistent with a fatter-tailed daily universe. The audit would benefit from a per-month stock-count log in `REPORT.md`; this is missing.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim | ✓ (T1 partial) | T1 VW RET-RF decile means: P1=1.12%, P10=0.86% — negative monotonic; t = −0.40 (paper t = −3.08). Direction correct. |
| 2 | Headline-magnitude claim | ✗ | T1 10-1 spread: ours −0.26% vs paper −0.95% (r = 0.27). T6: −0.19% vs −0.81% (r = 0.23). |
| 3 | Sample coverage ≥ 60% | ✓ | 1,699,402 panel rows from 19,098 permnos over 636 months; ~2,672 stocks/month avg. Paper period is 660 months but starts 1968 — 24 months missing (~3.6%). |
| 4 | Data-source choice justified | ✓ (partial) | CRSP/FF fully covered; SY/DHS/PS_LIQ substitutions are logged in `data_verification.json` blocking_issues and `assumptions.md` A2-A3. |
| 5 | prep_validation.py exit 0 | ✓ | `python scripts/prep_validation.py replications/max_on_steroids_attempt2` exits 0 (only a WARN about no audit yet, expected). |
| 6 | All committed tables have results files | ✓ | T1 → table_1.md, T6 → table_6.md, T4 → table_4.md, T8 → table_8.md all present. |
| 7 | SUMMARY.md matches results/table_*.md | n/a | SUMMARY.md not yet authored (auditor owns it). |
| 8 | No orphan folders | ✓ | `ls` clean. |
| 9 | Diagnoses paired with fix attempts | ✗ | `assumptions.md` has 10 entries, but A10 closes with a list of possible causes and no before/after metric. A2 (SY/DHS skipped) and A5 (MIS/CE skipped) similarly have no before/after metric. |
| 10 | Cell status verification (re-run evaluator) | ✗ | Re-ran `evaluate.py` — Match 2 / FAIL 50 / MISSING 14 reproduces. Canonical scorer cannot parse the file (see M3) — all 66 cells read as MISSING. |
| 11 | Corollary coverage | ✗ | FFCPS, FF6PS, SY, DHS columns entirely MISSING (14 cells). T4 Col3-Col6 also MISSING (MIS/CE skipped). |
| 12 | Claim coverage of committed selection | ✓ (with gaps) | C1, C2, C3, C4 covered by T1, T6, T4, T8 respectively. Coverage gaps: SY/DHS test of the central hypothesis (C1, C2) cannot be run because factors missing — but this is documented. |
| 13 | Sign conventions re-derived from paper | ✗ | T4 Col1 MAX: paper defines MAX as lottery-stock measure with negative predictive power (L360, "average slope on MAX turns out to be negative"). Replicator gets +0.022 — sign-flipped. T8 Col1 D10: paper expects −1.027%, replicator gets +0.048% — sign-flipped. |
| 14 | Reporting discipline | ✗ | REPORT.md §3 lists per-table comparison; missing t-stat citations on the spread comparisons (e.g., "FF3 alpha = -0.60% (t = -2.36)" — paper t = -5.35; replicator acknowledges smaller magnitude but doesn't quantify the magnitude gap explicitly). |
| 15 | REPORT.md headline freshness (DEV-010) | n/a | No headline tally in REPORT.md (no Match/FAIL/MISSING aggregate line). |

## 4. Issues the agent should have caught (didn't)

1. **Universe drift diagnosis is untested.** Agent's REPORT.md §4 says *"my MAX at P10 (8.74%) is higher than the paper's (7.1%), suggesting my daily universe includes stocks with more extreme spike days."* No test result backs this — running the panel with month-end $5 vs every-daily $5 (a 5-line code change) would close or open the case.
2. **The `evaluate.py` key matcher is buggy** (m2) — this means the printed per-cell table in eval output is unreliable. The agent reports Match 2 / FAIL 50 / MISSING 14 but the printed `Ours` values for the FF3/FFC4/FF5/FF6 columns are all 1.12 (the P1 RET-RF value). The MATCH 2 likely refers to cells whose target name happens to start with the matching metric's first segment.
3. **Table 4 sign mismatch is not paired with a fix attempt.** Per assumption A10, the agent acknowledges the sign is flipped but the iteration log's "Status" line just says "Open" without any next-step.
4. **Panel starts 1970 but the paper starts 1968.** No check or note in REPORT.md.

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "MAX on Steroids: A New Measure of Investor Attraction to Lottery Stocks" (Bali, Ince, Ozsoylev) for slug `max_on_steroids_attempt2`. The previous agent run completed with verdict **FAILED** (audit 1 at `replications/max_on_steroids_attempt2/logs/audit1.md`). Read the audit first.

## Issues to address (priority order)

### [B1] — BLOCKER — fix first

T4 Col1 MAX coefficient is +0.022 (paper −0.210, t = −6.15). T8 Col1 D10 coefficient is +0.048% (paper −1.027%, t = −6.61). In the replicated data, high-MAX stocks have **slightly positive** future excess returns, the opposite of the paper's central finding.

**Specific fix:**
1. In `src/run_tables.py:269-362` (table4) and `src/run_tables.py:365-472` (table8), add a `print` for the per-decile mean of `ret_xs` to confirm the cross-sectional relationship.
2. Verify `ret_fwd1` is correctly computed as `groupby('permno')['ret'].shift(-1)` (i.e., next month's return) — check `src/main.py:236-240`. If `ret_fwd1` is misaligned, every regression coefficient is biased.
3. Check whether `ret = 0` (no-trade, no-return) months are inflating the cross-section. The paper requires ≥15 daily obs in the formation month but does not require non-zero monthly `ret`. Filter: drop rows where the formation month has fewer than 15 daily observations of `ret != 0` (not just `ret not null`).
4. Re-run; expect T4 Col1 MAX coef to be negative (within ±30% of −0.210) and T8 Col1 D10 to be negative (within ±30% of −1.027%).

### [M1] — MAJOR — fix after [B1]

All headline spreads are 3-5× too small (T1 10-1 RET-RF: −0.26% vs −0.95%, r = 0.27; T6 10-1: −0.19% vs −0.81%, r = 0.23). The direction is correct but the magnitude is anemic.

**Specific fix:**
1. The cached panel shows MAX@P10 = 8.74% vs paper 7.1% — the right tail is too fat. Try restricting the $5 price floor to month-end only (not every-daily). Update `src/sql/02_max_signal.sql` to apply `prc >= 5` on month-end, not on every observation. Recompute `data/max_signal.parquet` and `data/panel.parquet`.
2. Re-run table1 and table6; expect 10-1 RET-RF spread to move toward −0.95% (T1) and −0.81% (T6).
3. Document the change in `assumptions.md` A4b with before/after spreads.

### [M2] — MAJOR — fix after [M1]

Sample starts 197001 but the paper's sample is January 1968 – December 2022. ~24 months are missing.

**Specific fix:**
1. Inspect `data/panel.parquet` min month (currently 197001). Verify `src/sql/02_max_signal.sql` allows formation months starting 1968 by extending the lookback buffer to 1967.
2. Rerun `src/main.py`. Expect `panel.month.min() == 196801`.
3. Recompute table1 / table6 with the extended sample; document in `assumptions.md`.

### [M3] — MAJOR — fix after [M2]

`scripts/score_replication.py` cannot read `eval/metrics.json` because the file is nested under `"metrics"` instead of being a flat cell-keyed dict.

**Specific fix:**
1. In `src/evaluate.py:209-217`, change the write block to emit `{"<cell>": {"value": ..., "t_stat": ..., "paper": ..., "tolerance_pct": ..., "status": "Match" | "FAIL" | "MISSING"}, ...}` flat dict.
2. Verify by running `python scripts/score_replication.py replications/max_on_steroids_attempt2 --iteration <N>`. Expect non-MISSING status for the 50 cells the agent's evaluator scored as Match or FAIL.
3. Also fix the matcher bug at `src/evaluate.py:154-156` (the relaxed `target_name.startswith(suffix.split('_')[0])` fallback). Replace with an exact `target_name == suffix.replace('-', '_')` match; if no match, mark MISSING.

### [M4] — MAJOR — fix after [M3]

`assumptions.md` A10 closes FAILs with hedged "most likely due to vintage" without a test result. Per Step 2 sub-check 7 of the auditor rubric, this fails the diagnostic-evidence sub-check.

**Specific fix:**
1. After [M1] resolves, append a new entry `A10b: After M1 fix` to `preparations/assumptions.md` with: before metric (e.g., T1 10-1 spread = −0.26%), after metric (e.g., T1 10-1 spread = −0.78%), and a one-line "Status: PASS" or "Status: partial — closer but not within tolerance."

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every iteration log entry in `assumptions.md` must have all five fields: Diagnosis, Next fix, Before metric, After metric, Status. A diagnosis without a Next fix is incomplete — do not move on.
- **Read `rep/STUCK_AGENT_GUIDELINE.md` on your first debug cycle.** Don't rediscover failures that are already documented.
- **10-iteration cap per problem.** Hard stop at 10 and escalate to the human. A documented partial is more valuable than a paper-claiming success that does not actually replicate.
- **Diagnoses must be paired with fix attempts (exit gate).** Before declaring `partial`, walk `assumptions.md` and verify every diagnosed problem has at least one log entry with a non-empty `Next fix` line and a before/after metric.

## Inputs you should read

- `replications/max_on_steroids_attempt2/logs/audit1.md` — this audit (full context)
- `replications/max_on_steroids_attempt2/inputs/content.md` — paper ground truth
- `replications/max_on_steroids_attempt2/preparations/` — prep contract (rules, tables selected, data verification, assumptions iteration log)
- `replications/max_on_steroids_attempt2/src/main.py` and `src/run_tables.py` — current code (will be modified)
- `replications/max_on_steroids_attempt2/data/` — cached intermediates (recompute spot-checks from these)

## What NOT to redo

- Skip re-reading `SKILL.md` — the contract is the same.
- `scripts/prep_validation.py` is loop-aware (DEV-009) and safe to re-run at any point — mid-loop states no longer produce false errors. Re-run it if you changed a prep artifact; otherwise it is optional.
- Skip re-doing the clickhouse catalog scan — `data_verification.json` is current.
- **DO** re-run any sanity checks you add or modify — they are the gate that catches regressions.

## Deliverables for this iteration

- `replications/max_on_steroids_attempt2/src/main.py` and `src/run_tables.py` — revised with fix attempts logged per issue above
- `replications/max_on_steroids_attempt2/results/table_<n>.md` — updated for each committed table
- `replications/max_on_steroids_attempt2/data/panel.parquet` — re-derived with extended sample (M2) and month-end price floor (M1)
- `replications/max_on_steroids_attempt2/preparations/assumptions.md` — append a new iteration log entry for every issue addressed (Diagnosis, Next fix, Before metric, After metric, Status)
- `replications/max_on_steroids_attempt2/REPORT.md` — updated; lead with the data-quality summary (sample period, universe size, signal mean/std vs paper, headline-magnitude comparison, table count, corollaries evaluated this iteration)
- `replications/max_on_steroids_attempt2/eval/metrics.json` — restructured (M3) so `scripts/score_replication.py` can read it

## Stop conditions

- **All blockers fixed and verified** → re-run prep_validation.py and any sanity checks → if both pass, declare success or note remaining majors in `REPORT.md`; the next audit updates `SUMMARY.md`.
- **10-iteration cap reached** on a single problem → escalate to the human and write a partial `REPORT.md`; do not edit `SUMMARY.md`.
- **All blockers fixed but majors remain** → declare partial and document the gap in `REPORT.md`. The auditor's `SUMMARY.md` verdict (REPLICATED / FAILED) is independent of this loop decision.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

The pipeline is structurally complete — SQL → monthly returns → FF factors → panel → decile sorts → VW returns → NW t-stats → factor alphas → FM regressions. The agent's REPORT.md is candid and the iteration log captures the major decisions. However, three independent red flags converge on a methodology bug:

1. **T4/T8 sign mismatch** (B1) — high-MAX stocks should underperform, but in this replication they slightly outperform. This is the paper's headline claim inverted. Without diagnosing the cause (off-by-one alignment of `ret_fwd1`? `ret=0` treatment? wrong dependent variable?), no iteration can move forward.
2. **Magnitude gap** (M1) — the daily universe appears to over-include spike days; MAX@P10 = 8.74% vs 7.1% in the paper is the most concrete evidence. The $5 price-floor convention (every-daily vs month-end) is the most likely root.
3. **Sample truncation** (M2) — 24 months dropped at the start, small but unexplained.

The agent's evaluator (`src/evaluate.py`) has a relaxed-match bug that makes its per-cell output untrustworthy — see [m2]. The Match 2 / FAIL 50 / MISSING 14 tally is reproducible but the printed per-cell values are partly artifacts. The canonical scorer (`scripts/score_replication.py`) cannot parse the agent's metrics.json at all (M3) — both files are needed for a clean audit.

Three dimensions at 1 (Concrete Result, Signal Strength, Corollary) drive the FAILED verdict mechanically. The paper's central anomaly (MAX underperformance, MAX^beta robustness) is in the right direction but is not at the magnitude the paper reports, and the FM regressions are sign-flipped.