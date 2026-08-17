---
iteration: 1
verdict: REPLICATED
blocker_count: 0
actionable_major_count: 5
requires_iteration: true
---

# Audit Report 1 — weber_2018_attempt2_deepseek

**Verdict:** REPLICATED
**Date:** 2026-08-16
**Auditor notes:** The core return-pricing claims (downward-sloping term structure, 1.10%/mo spread; factor-model alphas) replicate near-exactly, but one-third of committed cells fail, concentrated in the duration tail (D9/D10), the I/B/E/S tables (T8/T9), and the short-sale-constraint tail (T12). Several FAIL clusters are retired with hedged causal stories rather than demonstrated tests — those are actionable.

## 1. Scores

| Dimension | Score | Key finding |
|-----------|------:|-------------|
| Methodology | 3 | Formula/timing/filter/winsorization/look-ahead/lag all trace to the paper; deviations (A2, A4, A9) are earned with empirical evidence; inference sub-check 8 fails at the tail (D10 alpha sign flips). |
| Headline matching | 4 | D1−D10 spread 1.106% vs paper 1.10% (0.5% error); CAPM betas 10/10; alpha spread 1.29 vs 1.29; monotonic downward slope preserved. Individual D9/D10 bins drift 30–45%. |
| Data coverage | 3 | Period exact (1963–2014, 51 years); join hygiene clean (0 dup); 2 documented substitutes (Moody's BE, Baker-Wurgler sentiment) plus mean_me drift ~14%. |
| Concrete result matching | 3 | 451/660 committed cells Match = 68.3% (band 3); mechanically enforced. |
| Signal strength | 3 | Headline spread cells all Match (r 0.80–1.005) but D10 tail cells sign-flip (ff4_alpha_D10 −0.07→+0.149; ff5_alpha_D10 0.01→0.22) and D10 mean r=1.445. |
| Corollary | 3 | 366/561 corollary cells Match = 65.2% (band 3); C3 (sentiment, Table 7) is a documented non-actionable data gap. |
| 7 | SUMMARY.md matches results/table_*.md | ✓ | tally copied from eval/scoring.json; no SUMMARY yet this iteration (auditor writes it). |

## 2. Issues by severity

### Blockers (must fix)

None. The pipeline runs end-to-end, `prep_validation.py` exits 0, and the headline magnitude (spread 1.106% vs 1.10%) is within 0.5%. The $5 price-floor (A2) and NYSE-only breakpoint (A9) convention defaults were correctly rejected with funnel/variant-grid evidence — these are the two places a methodology blocker would have lived, and both are handled correctly.

### Major (should fix)

- [M1] **D9/D10 tail FAIL cluster retired on an untested `[VINTAGE-DRIFT]` story.** ff4_alpha_D10 sign flips (paper −0.070 vs ours +0.149), ff5_alpha_D10 (0.010 vs 0.222, r=22), alpha_capm_D9 (r=3.07), mean_D10 (0.462 vs 0.32). The report attributes this to Compustat vintage (`comp_202601` vs ~2014) with hedged language ("candidate marker", "consistent with") and no demonstrated test.
  - File: `preparations/assumptions.md` ("Documented (unresolved) divergences"); `REPORT.md` §Known divergences ¶1.
  - Likely cause: unverified vintage-drift attribution; the extreme months (Jan-2001 +55.1%) were shown to be real in raw CRSP but the compositional cause (tiny/loss-making dot-com firms in D10) was not compared against an older Compustat vintage or an IBES-covered subset.
  - Specific fix: run the ~100-firm D10 composition probe against an alternative vintage or against the IBES-covered intersection (which M2 already motivates), and record the before/after mean return; if the drifts persist, reopen the FAIL rather than carrying the unproven marker.

- [M2] **T8 SUE sign inversion + EG reversal (L=0.564) evaluated against the wrong sample.** The paper's Table 8 deciles are built on the I/B/E/S-covered subset (footnote 15: "Analysts mainly cover large companies"), but the replication sorts the full CRSP/Compustat universe, so D10 contains tiny non-covered firms (median price $3.87 vs D1 $6.38). The divergence is diagnosed but the obvious fix — restrict the T8 sort to the IBES-covered intersection — was never attempted.
  - File: `src/table8_9.py`; `preparations/assumptions.md` §Iteration 10.
  - Likely cause: full-universe vs analyst-covered sample mismatch.
  - Specific fix: add the IBES-coverage screen to the T8 sort universe and re-run; verify whether SUE monotonicity (D1 +0.23 → D10 −0.47) and EG sign restore.

- [M3] **T4 pre-estimation row (spread 0.375 vs paper 1.21, r=0.31) left at a paper-silent placeholder.** The pooled expanding-window AR(1) yields ar_roe ≈ 0.62 vs the paper's full-sample 0.4067. The log flags a candidate (Fama-MacBeth mean of annual cross-sectional AR(1)s) but never tests it.
  - File: `src/table4_5.py` (preest row); `REPORT.md` ¶2.
  - Likely cause: paper-silent pre-estimation procedure; pooled AR(1) is the wrong aggregation.
  - Specific fix: implement the Fama-MacBeth AR estimator for ar_roe/ar_sg and re-run the preest row; compare spread to 1.21.

- [M4] **T9 Panel A collapses (3/12 Match, L=0.75).** PTB D5 = 12.254 and PTP D5 = 60.945 are far off plausible values, indicating the discovery-based `ptgsum` consensus-target extraction is mis-specified rather than mildly off.
  - File: `src/table8_9.py`; `results/table_9.md`.
  - Likely cause: `meanptg`/`measure='PTG'` schema read is wrong (or price-base mismatch), not a sample issue.
  - Specific fix: spot-check the `ptgsum` extraction against a handful of known firms' June consensus targets and correct the aggregation; re-run.

- [M6] **T12 value/low-RIOR tail (L=0.511): value/low spread 0.941 vs 0.63, and several sign flips in D3 cells.** Same BM-definition sensitivity + tail-composition issue as M1, unprobed.
  - File: `src/table10_12.py`; `results/table_12.md`.
  - Likely cause: BM-definition (BE cascade with no Moody's supplement) interacting with the duration tail.
  - Specific fix: probe the BM breakpoint definition against the paper's and the D3 sign-flip cells (t12_lowrior_l_D3 −0.72 vs +0.19) with a sample comparison.

- [M5] **T6 decile levels run 10–50% high (L=0.836; spread cells all Match).** Attributed to the per-portfolio Moreira-Muir scaling convention plus the D9/D10 tail. The spread cells validate the volatility-management claim itself; the levels inherit M1/M2. Treat as non-actionable-in-isolation: it is downstream of the tail fix.
  - File: `src/table6.py`; `REPORT.md` ¶3.
  - Likely cause: RV-series construction is paper-silent on daily weighting + inherited tail composition.
  - Specific fix: re-check after M1/M2; do not attempt a standalone level-tune this iteration.

### Minor (cleanup)

- [m1] **Scorer run with the wrong iteration number.** The replicator ran `score_replication.py` with `--iteration 10` (inner-loop count) instead of the outer-iteration `1`, leaving a stale `iteration: 10` row in `eval/loss_trace.json` and `iteration: 10` in `scoring.json`. The auditor re-ran with `--iteration 1` and confirmed `match_rate=0.6833, loss=0.3167`; the stale `iteration: 10` row in `loss_trace.json` remains and should be removed so there is one row per outer iteration. No numeric impact.
  - File: `eval/loss_trace.json`.
  - Specific fix: drop the `iteration: 10` row (or accept it as overwritten; the scorer is keyed by iteration).

- [m2] **REPORT.md diagnostic-block artifact.** The "FF5 alpha (annualized) t = 19627033255666304.00" and "R² = −0.08" are formatting artifacts carried from the utility; the report correctly annotates them but a reader skimming the code block will see an absurd t-stat. Cosmetic.
  - File: `REPORT.md` §Standard diagnostics block.

## 3. Verification spot-checks (recomputed by auditor)

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Monotonic-direction claim | ✓ | T2 mean returns decrease monotonically D1 (1.568) → D10 (0.462). |
| 2 | Headline-magnitude claim | ✓ | Spread 1.106 vs 1.10 (0.5%); D1 1.568 vs 1.43 (9.7%); betas 10/10. |
| 3 | Sample coverage ≥ 60% | ✓ | Panel 1,871,536 rows, 15,489 permnos, 51 sort years; mean/median firm counts match 2014-vintage expectations post-floor-removal. |
| 4 | Data-source choice justified | ✓ | CRSP/Compustat/13F/IBES all catalog-present; Moody's + Baker-Wurgler substitutes documented in data_verification.json (blocking_issues). |
| 5 | prep_validation.py exit 0 | ✓ | All prep artifacts pass (47 rules, 11 tables, verdict=partial). |
| 6 | All committed tables have results files | ✓ | 11 of 12 results files present; Table 7 correctly uncommitted (sentiment data gap). |
| 7 | SUMMARY.md matches results/table_*.md | ✓ | No SUMMARY yet; tally here copied from eval/scoring.json (451/660 = 68.3%). |
| 8 | No orphan folders | ✓ | No literal-brace / shell-error folders. |
| 9 | Diagnoses paired with fix attempts | ✓ | All major FAIL clusters have a log entry with diagnosis + next-fix + before/after metrics (iterations 3–10). |
| 10 | Cell status verification (re-run evaluator, diff vs eval/scoring.json) | ✓ | `evaluate.py` reproduces the canonical scorer exactly (Match=451 FAIL=209 no_effect=41); audit re-ran the scorer directly and confirmed. |
| 11 | Corollary coverage | ✓ | C3 surfaced as non-actionable data gap ([THIRD-PARTY-DATASET]); C5/C6 corollaries computed (T4/T5/T6/T10/T11/T12). |
| 12 | Claim coverage of committed selection | ✓ | C1–C2 (headline), C4–C6 committed; C3 (Table 7) documented as data-limited in data_verification.json + REPORT.md. Claim list honest. |
| 13 | Sign conventions re-derived from paper | ✗ | Spread sign (Long-short D1−D10 positive, downward slope) is correct per abstract L43; but ff4_alpha_D10 and ff5_alpha_D10 individual-cell signs disagree with the paper (print base −0.07 / +0.01 vs ours +0.149 / +0.222) — a tail-bin divergence, not a subtraction-order error, but not a documented printing convention. |
| 14 | Reporting discipline (grid completeness, claim citations, SE-less headlines) | ✓ | Spread t-stat 5.23 cited (SE 0.20); no reversal claims without licensing statistic. |
| 15 | REPORT.md headline freshness (matches eval/scoring.json) | ✓ | REPORT.md tally (701/451/209/0/41, L=0.3167) equals scoring.json exactly. |

## 4. Issues the agent should have caught (didn't)

1. The **T8 sample-spec mismatch** (M2) — the paper's footnote 15 explicitly says the analyst tables use a large-firm-covered subset, yet the replication sorted the full universe and then spent iteration 10 "salvaging" a sign inversion that is almost certainly a universe spec, not a data bug. This should have been caught on first read of the T8 cell targets.
2. The **T9 Panel A magnitude collapse** (M4) — PTB of 12.25 and PTP of 60.95 for the top duration quintile are implausible on their face and should have triggered an extraction-probe before being written to results.
3. Treating **vintage drift as the explanation** (M1) without running the one cheap test it implies (an older-vintage or IBES-subset comparison). "Consistent with vintage drift" is a hypothesis, not a demonstration, and the log itself acknowledged the alternative (composition) as viable.

## 5. Next-iteration prompt (copy-paste this into the next agent run)

--- BEGIN COPY HERE ---

You are continuing the replication of "Cash flow duration and the term structure of equity returns" (Weber 2018, JFE 128, 486–503) for slug `weber_2018_attempt2_deepseek`. The previous agent run completed with verdict **REPLICATED** (audit 1 at `replications/weber_2018_attempt2_deepseek/logs/audit1.md`). Read the audit first.

## Issues to address (priority order)

### [M2] — MAJOR — T8 sample-spec mismatch (fix first; likely unlocks the largest FAIL cluster)
Table 8 (I/B/E/S analyst expectations) has L=0.564 with a SUE sign inversion and an EG reversal. The paper's footnote 15 (see inputs/content.md, "Analysts mainly cover large companies") means the T8 deciles are built on the I/B/E/S-covered subset, but the replication sorted the full CRSP/Compustat universe, so D10 contains tiny non-covered firms (median price $3.87 vs D1 $6.38).

**Specific fix:**
1. In `src/table8_9.py`, restrict the T8 sort universe to firms present in the I/B/E/S coverage used for the LTG/SUE/EG variables (the `usfirm=1` + `usfirm=1` cusip-matched subset already computed for LTG coverage).
2. Re-run the SUE and EG blocks and verify whether the SUE monotonicity (D1 +0.23 → D10 −0.47, decreasing) and EG sign restore.
3. Verification: after the fix, the SUE decile pattern should DECREASE in duration and the EG D1 should turn positive/neutral, matching the paper's direction.

### [M1] — MAJOR — demonstrate or reopen the D9/D10 tail attribution
ff4_alpha_D10 sign-flips (−0.070 vs +0.149), ff5_alpha_D10 (0.010 vs 0.222), mean_D10 (0.462 vs 0.32) are retired on a hedged `[VINTAGE-DRIFT]` story. Either demonstrate the cause or reopen the FAIL.

**Specific fix:**
1. Run the ~100-observation D10 composition probe on an alternative dataset cut: compare D10's top-month returns and firm composition between the current `comp_202601` vintage and either the IBES-covered subset (from M2) or a documented older vintage if reachable.
2. Record before/after mean D10 return and the D10 firm-size/ROE distribution.
3. Verification: if the divergence persists under the alternative cut, reopen the FAIL cells in `assumptions.md`; if the subset closes it, document the demonstrated cause and attach `[STRUCTURAL-SAMPLE-VARIANCE]`.

### [M3] — MAJOR — test the paper-silent pre-estimation procedure
T4 preest row spread is 0.375 vs paper 1.21 (r=0.31) because the pooled expanding-window AR(1) gives ar_roe ≈ 0.62 vs the paper's 0.4067.

**Specific fix:**
1. In `src/table4_5.py`, replace the pooled AR(1) with a Fama-MacBeth-style mean of annual cross-sectional AR(1) estimates of ROE (and BV-growth) persistence.
2. Re-run the preest row with the recovered ar_roe.
3. Verification: the preest spread should move toward 1.21; report the recovered ar_roe.

### [M4] — MAJOR — probe the T9 ptgsum extraction
T9 Panel A (3/12 Match) has implausible quintile values (PTB D5=12.254, PTP D5=60.945), indicating a mis-specified consensus-target read.

**Specific fix:**
1. In `src/table8_9.py`, spot-check the `ibes_202601.ptgsum` extraction (`measure='PTG'`, `meanptg`) against 3–5 known firms' June consensus target prices.
2. Confirm the price base (`actpsum_epsus.price`) and statpers window are correct.
3. Verification: PTB/PTP quintile means should fall in a plausible range (single-digit PTB, PTP near 100% not thousands of percent); re-run after correcting.

### [M6] — MAJOR — probe the T12 BM-conditional tail
T12 L=0.511; value/low spread 0.941 vs 0.63 and D3 sign flips (t12_lowrior_l_D3 −0.72 vs +0.19).

**Specific fix:**
1. In `src/table10_12.py`, verify the BM breakpoint definition against the paper's (BE cascade including the preferred-stock preference order) and identify the D3 sign-flip cells' sample.
2. Verification: report whether the sign flips are breakpoint-drift or BM-definition, and re-run.

### [m1] — MINOR — cleanup the stale loss_trace row
Remove the `iteration: 10` row from `eval/loss_trace.json` so there is one row per outer iteration.

### [m2] — MINOR — tidy the REPORT.md diagnostics block
Fix the "FF5 alpha t = 1.96e16" and "R² = −0.08" artifact values in `REPORT.md` so the code block is not misleading.

## Iteration discipline reminders

- **Diagnose → commit-fix → fix → verify.** Every iteration log entry in `assumptions.md` must have all five fields: Diagnosis, Next fix, Before metric, After metric, Status. A diagnosis without a Next fix is incomplete — do not move on.
- **Read `rep/STUCK_AGENT_GUIDELINE.md` on your first debug cycle.** Don't rediscover failures that are already documented.
- **10-iteration cap per problem.** Hard stop at 10 and escalate to the human. A documented partial is more valuable than a paper-claiming success that does not actually replicate.
- **Diagnoses must be paired with fix attempts (exit gate).** Before declaring `partial`, walk `assumptions.md` and verify every diagnosed problem has at least one log entry with a non-empty `Next fix` line and a before/after metric.
- **Run `python scripts/score_replication.py replications/<slug> --iteration <N>` ONCE, at the very end, with `<N>` = the OUTER iteration number (the audit number, e.g. 2 for the next outer pass), NOT an inner-loop counter.** Do not leave stale rows in `eval/loss_trace.json`.

## Inputs you should read

- `replications/weber_2018_attempt2_deepseek/logs/audit1.md` — this audit (full context)
- `replications/weber_2018_attempt2_deepseek/inputs/content.md` — paper ground truth (esp. footnote 15 for T8, Table 4 note for preest)
- `replications/weber_2018_attempt2_deepseek/preparations/` — prep contract (rules, tables selected, assumptions iteration log)
- `replications/weber_2018_attempt2_deepseek/src/main.py` and `src/table*_*.py` — current code (will be modified)
- `replications/weber_2018_attempt2_deepseek/data/` — cached intermediates (recompute spot-checks from these)

## What NOT to redo

- Do NOT re-run the whole pipeline from scratch — the core duration construction and T2–T6 sorts are validated (spread 1.106 vs 1.10, betas 10/10).
- Do NOT re-litigate the $5 price-floor (A2) or NYSE-only breakpoint (A9) decisions — both were correctly reversed with funnel/variant-grid evidence.
- Do NOT re-attempt standalone T6 level tuning — it is downstream of M1/M2.
- `scripts/prep_validation.py` is loop-aware and safe to re-run at any point.

## Deliverables for this iteration

- `src/table8_9.py`, `src/table4_5.py`, `src/table10_12.py` — revised per the fixes above
- `results/table_8.md`, `table_9.md`, `table_4.md`, `table_12.md` — updated per committed table (one per entry)
- `preparations/assumptions.md` — append a new iteration log entry per issue addressed (Diagnosis, Next fix, Before metric, After metric, Status)
- `SUMMARY.md` — read the latest combined assessment; do NOT edit (auditor-owned)
- `REPORT.md` — updated; lead with the data-quality summary and the corollaries evaluated this iteration

## Stop conditions

- **All blockers fixed and verified** → re-run prep_validation.py and the scorer (with the correct outer iteration N) → if both pass, declare success or note remaining majors in `REPORT.md`.
- **10-iteration cap reached** on a single problem → escalate to the human and write a partial `REPORT.md`; do not edit `SUMMARY.md`.
- **All blockers fixed but majors remain** → declare partial and document the gap in `REPORT.md`.

--- END COPY HERE ---

## 6. Auditor's notes (free-form)

This is a strong replication of the paper's central claim — the 1.10%/mo duration spread reproduces to 0.5%, the CAPM betas reproduce 10/10, the factor-model spread alphas, the parameter-sensitivity machinery (10/12 rows), the volatility-managed spreads, and the short-sale-constraint headline (T10 L=0.068) are all essentially exact. The failure pattern is clean and interpretable: it concentrates at the two extreme-duration bins (D9/D10) and in the three I/B/E/S- and BM-conditional tables whose universe differs from the paper's (analyst-covered subset, BM definition). The replication's self-discipline is high — the two convention defaults most likely to corrupt the cross-section ($5 price floor, NYSE-only breakpoints) were correctly caught and reversed with funnel/variant-grid evidence rather than assumed. The residual is a set of identifiable sample/definition mismatches at the tail, not a broken construction: the fixes above are targeted and cheap. The one process blemish is running the canonical scorer with an inner-loop iteration number, which is cosmetic but indicates the replicator lost track of the outer/inner distinction at the close.
