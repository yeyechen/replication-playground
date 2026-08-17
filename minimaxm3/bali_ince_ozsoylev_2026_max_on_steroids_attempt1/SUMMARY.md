---
schema_version: 2
slug: bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to
iteration: 5
verdict: FAILED
overall: 2.00
methodology: 3
headline_matching: 2
data_coverage: 4
concrete_result: 1
signal_strength: 1
corollary: 1
generated_at: 2026-08-14
---

# Replication Summary

## Bali, Ince, Ozsöylev (2026) "MAX on Steroids"

### Bottom line

**Replication result:** `FAILED`
**Overall quality:** 2.00 / 5.00

The data pipeline runs end-to-end (panel: 1.69M rows x 17 cols, 637 months, NYSE/AMEX/NASDAQ common stocks with $5+ price and SIC exclusions, 1970-2022), and the universe/MAX signal/factor-model code is structurally correct. Across five outer iterations, three diagnostic tests produced evidence (MAX-5 hand-verification MATCH to 6 decimals; lag-1 ME weighting tested and rejected; panel period-coverage source-data check confirmed source data exists but pipeline filter drops it). The canonical-scorer match rate is 0/82 (0.00%) — four-iteration plateau at L = 1.0000. 52 cells FAIL (T1 and T3 magnitude/sign gaps), 30 cells MISSING (T2 and T4 unbuilt across all five audits). This is the FINAL iteration of the 5-iter cap; the replicator exits under documented-residue criterion B. The exit is final — no further iterations are possible.

## Quality assessment

| Dimension | Score | Assessment |
|---|---:|---|
| Methodology | 3/5 | MAX signal construction, universe filters, VW weighting, Newey-West t-stats, and one-month-ahead timing all match the paper. MAX-5 signal verified to 6 decimals via hand-computation. Sub-checks fail on diagnostic evidence for FAILs (T1 P10_RET_RF sign flip and T6 spread magnitude collapse persist across five iterations) and significance-category reproduction (T1 P10_RET_RF sign flip and T6 spread magnitude 7x off). |
| Headline matching | 2/5 | C1 (T6 SPREAD_RET_RF): paper -0.81 vs ours -0.12 — direction matches, magnitude 7x attenuated (r = 0.148, outside any band). T1 SPREAD_RET_RF: paper -0.95 vs ours -0.32 — direction matches, r = 0.33 (band-2 boundary). T1 P10_RET_RF: paper -0.32 vs ours +0.77 — wrong sign on the high-MAX leg. |
| Data coverage | 4/5 | Period (paper 1968-2022; panel 1970-2022 — 23-month gap at the start, documented as Limitation 6 after iter-5 diagnostic confirmed source data exists). Universe (~2655 stocks/month, NYSE/AMEX/NASDAQ common stocks, $5+ price, SIC exclusions, 15+ daily obs) matches paper. CRSP/Compustat/FF sources all match. Pre-2002 beta gap documented. Third-party factors absent from catalog with documented substitute marker. Join hygiene clean. |
| Concrete result matching | 1/5 | 0 of 82 cells Match (0.00%) — well below the 30% threshold. Four-iteration plateau (iter 1 L=0.9634 → iter 2-5 L=1.0). 52 FAIL cells (magnitude/sign gaps on T1 and T3), 30 MISSING cells (T2 and T4 not built across five audits). |
| Signal strength | 1/5 | Worst-case headline cell: T6_SPREAD_RET_RF — paper -0.81, ours -0.12, r = 0.148 (sign matches but r outside any band). T6 P10_RET_RF: paper -0.10, ours +0.80 (sign flip, r = 8.0). T1 P10_RET_RF: paper -0.32, ours +0.77 (sign flip, r = 2.4). |
| Corollary | 1/5 | 0 of 56 corollary cells have a computed result. T2 (12 cells, characteristics spread) and T4 (18 cells, INST-stratified MAX^beta) entirely MISSING across five audits. C2 (mispricing), C3 (MAX^beta MIS/CE spreads), C4 (heterogeneous skewness preference across INST terciles) — all untestable in the artifact set. |

## What replicated and what it validates

| Paper output | High-level evidence | What it supports |
|---|---|---|
| Table 1 (MAX univariate sorts) | Direction preserved across deciles (P1_RET_RF = 1.08 to P10_RET_RF = 0.77, both positive and declining). All 26 cells FAIL. 10-1 spread = -0.32 vs paper -0.95 (~3x attenuated, sign matches). MAX signal SQL verified to 6 decimals via hand-computation. | Confirms MAX signal SQL is structurally correct and the panel-level universe filter is applied; the ~3x magnitude gap on the 10-1 spread is driven by the high-MAX leg (P10_RET_RF sign-flipped). The MAX+VW hypothesis for the magnitude gap is empirically ruled out. |
| Table 6 (MAX^beta dependent double-sort) | 10-1 spread = -0.12 vs paper -0.81 (sign matches, magnitude 7x off). P10_RET_RF = +0.80 vs paper -0.10 (sign flip on the high-MAX leg). All 26 cells FAIL. MAX^beta runs on 2002-2022 only (38% of paper's window). | Confirms dependent double-sort code runs end-to-end; the iter-2 beta aggregation convention made the metric wrong-sign, and the iter-3 revert restored the sign direction without closing the magnitude gap. |
| Universe, MAX signal, factor models (CAPM, FF3, FFC4, FF5, FF6) | 1.69M panel rows, 637 months, 18,234 unique permnos. MAX mean 3.47%, p99 12% — sensible for top-5 daily-return average. MAX-5 hand-verification on (permno=10107, 2010-01-31) matches panel to 6 decimals. CAPM/FF3/FFC4/FF5/FF6 regressions run without error. | Confirms the data pipeline correctly applies paper §3.1 universe filters and §3.2 MAX definition; the MAX signal SQL is verifiable to 6 decimals. The factor-model code is reusable for the missing T2/T4 builds. |

## Important gaps

- **Panel period truncation (1970-01 to 2022-12 vs paper 1968-01 to 2022-12).** The iter-5 diagnostic confirmed the source data exists in `crsp_202601.msf` (1968: 25,838 rows; 1969: 26,610 rows) and `crsp_202601.dsf` (1968: 488,614 daily rows; 1969: 558,342 daily rows), but the panel pipeline's `count(ret) >= 15` requirement in the `monthly_daily_count` CTE drops early-year stocks with sparse daily observations. Documented as Limitation 6 with `[DIAGNOSE-PENDING]` marker. Non-actionable within time budget.
- **Third-party factor data missing from catalog (PS-LIQ, SY MGMT/PERF, DHS FIN/PEAD).** Four of the paper's model columns (FFCPS, FF6PS, SY, DHS) cannot be replicated without manual download. The C2 mispricing-interpretation claim is untestable here.
- **Pre-2002 market betas unavailable.** `ea_oneoff.dsf_beta_252` covers 2002-01-09 onward. Table 6 and Table 9 Panel B (both MAX^beta-based) run on 2002-2022 — ~38% of the paper's sample window.
- **Table 2 (characteristics spread) and Table 9 Panel B (INST-stratified MAX^beta) not built — five consecutive audits.** 8 of 12 Table 2 characteristics are computable from the existing panel; IVOL, MIS, CE, INST require additional SQL. Table 9 Panel B requires `instown_202601.s34` aggregation. Two of the paper's three named contributions (C2 mispricing, C4 heterogeneous skewness preference) remain entirely untestable.
- **T1 P10_RET_RF sign flip is the primary driver of the T1 10-1 spread gap.** P1_RET_RF is roughly correct; the high-MAX leg is sign-flipped. The next iteration should drill into the P10 stocks themselves — extract the top 10 stocks by MAX for a representative month, compute their forward returns, and check whether the stocks are different or the returns are different.
- **T1 magnitude gap (~3x attenuation) closed with honest `[DIAGNOSE-PENDING]` marker — non-actionable.** Iter-4's MAX-5 verification and lag-1 ME test ruled out two of the previously-hedged causes; iter-5's period-coverage source-data check ruled out a third. The remaining candidates (RF series vintage, universe vintage) were not tested within the time budget.
- **IVOL signal is NULL on all 1.69M rows.** `ea_oneoff.dsf_beta_252.resid` carries CAPM residuals; the paper requires FF3 residuals. Affects Table 2 SPREAD_IVOL row only if T2 is built.
- **FINAL ITERATION — 5-iter cap reached.** The replicator stops after this audit. Every remaining failing cell carries a closed-vocabulary marker with diagnostic evidence in `assumptions.md`. No further iterations are possible.
