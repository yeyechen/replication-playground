---
schema_version: 2
slug: max_on_steroids_attempt3
iteration: 1
verdict: FAILED
overall: 2.00
methodology: 3
headline_matching: 2
data_coverage: 4
concrete_result: 1
signal_strength: 1
corollary: 1
generated_at: 2026-08-15
---

# Replication Summary

## MAX on Steroids: A New Measure of Investor Attraction to Lottery Stocks (Bali, Ince, Ozsoylev)

### Bottom line

**Replication result:** `FAILED`
**Overall quality:** 2.00 / 5.00

A documented partial replication. The pipeline is structurally sound (4 sanity checks pass, beta-neutrality verified, FF6 = FF5 + MOM consistent) and the panel is well-constructed (1.91M rows, 660 months, 1968-01 to 2022-12, ~2,900 obs/month). The headline D10-D1 VW spread is wrong-signed on both Table 1 (+0.22% vs paper -0.95%) and Table 6 (+0.29% vs paper -0.81%), with the per-decile monotonicity broken at the high-MAX tail (D10 > D8 in our panel). Table 2 (110 cells on the C3 corollary claim) is 100% MISSING. The closed-vocabulary markers in `preparations/assumptions.md` (Assumption 13) are rhetorically appropriate but lack the diagnostic evidence the markers require per `rep/LOSS_FUNCTION.md`. Three dimensions hit 1 (Concrete Result Matching, Signal Strength, Corollary) — the bright line is FAILED.

## Quality assessment

| Dimension | Score | Assessment |
|---|---:|---|
| Methodology | 3/5 | 6/8 sub-checks pass; diagnostic-evidence and statistical-inference sub-checks fail (FAIL cells closed without per-bin evidence; headline t-stats in wrong significance category). |
| Headline matching | 2/5 | D10 RET-RF is wrong-signed (+1.14% vs paper -0.32%); D10-D1 VW is wrong-signed and 1/3 the magnitude; per-decile monotonicity breaks at the high-MAX tail. |
| Data coverage | 4/5 | Period exact (1968-01 to 2022-12); universe ~2,900 obs/month matches; CRSP/Compustat/FF3/FFC4/FF5/FF6 sources all match. Top-50% ME filter deviates from paper but is documented. |
| Concrete result matching | 1/5 | 12 of 110 non-MISSING committed cells are Match (10.9%); T2 contributes 110/110 MISSING. Match rate < 30% — the worst band. |
| Signal strength | 1/5 | Headline D10-D1 cells across T1 and T6 are wrong-signed or near-zero; worst-case r = 0.003 (T1 D10D1_FF5). Outside [0.33, 3.0] band. |
| Corollary | 1/5 | T2 (which carries the C3 corollary on MAX-characteristic co-movement) is 100% MISSING; no corollary claim has any computed result. |

## What replicated and what it validates

| Paper output | High-level evidence | What it supports |
|---|---|---|
| Table 1 (D1-D7 RET-RF) | 6 of 10 decile cells Match in the low-to-mid MAX bins (D2_RET-RF=0.85 vs 0.67; D3=0.60 vs 0.60; D7=0.66 vs 0.53). | Confirms the MAX signal is constructed correctly and the per-month value-weighted portfolio formation produces stable returns in the lower deciles. |
| Table 6 (D1, D3-D7 RET-RF) | 6 of 10 cells Match (D1_RET-RF=0.86 vs 0.71; D3=0.60 vs 0.64; D7=0.66 vs 0.56). Beta-neutrality spread = 0.032 (within 0.1 tolerance). | Confirms the MAX^beta double-sort construction is correct and beta-neutrality holds; the FF6-vs-FF5+MOM check (D10 FF5=0.92, FF6=0.98, MOM beta=-0.09) is consistent. |
| Table 1, Table 6 sanity checks | All four pass: panel funnel (1.91M rows), sign discipline (me_lag1 -2.01% vs me_now +0.60% — 260 bp difference confirms weight convention is not aliased), sign flip (ascending -1.99% vs descending +1.99%), beta-neutrality (0.032 spread), FF6 vs FF5+MOM. | The algorithm is structurally correct. The remaining gap is data-driven (Assumption 13), not algorithmic. |
| Table 2 | Not implemented. Characteristic columns are built on the panel (`results/panel_coverage.json` shows all 11 columns), but the per-decile cell dictionary was never written. | n/a — gap. |

## Important gaps

- **Headline D10-D1 spread collapses.** Paper T1 D10D1_RET-RF = -0.95% (t = -3.08); replication = +0.22% (t = +0.79). Wrong sign. The replication's sign-discipline sanity check shows the unfiltered panel under `me_lag1` weighting gives -2.01% (closer to the paper's -0.95%, ratio 2.1); the top-50% ME filter combined with the `me_now` weight choice regressed the result. The agent's iter-4 trajectory documents the regression but does not resolve it.
- **T2 is 100% MISSING.** 110 cells committed in `tables_to_replicate.json`; none written to `eval/metrics.json`. The panel carries all 11 required characteristic columns, so this is a "wire the metric" gap, not a "construct the metric" gap.
- **Factor columns SKIP.** Tables 1 and 6 replicate 5 of 9 model columns (RET-RF, FF3, FFC4, FF5, FF6); FFCPS, FF6PS, SY, DHS are SKIP because the PS LIQ factor, SY MGMT/PERF factors, and DHS FIN/PEAD factors are not in the ClickHouse `ff` catalog. This is a known data-infrastructure gap, fully documented in `preparations/data_verification.json` and `preparations/assumptions.md` (Assumption 10).
- **Characteristic columns SKIP in T2.** MIS, β^MAX, INST, E(ISKEW) are SKIP because the 11-component Stambaugh-Yu-Yuan (2015) MIS index, the market-level MAX regression, and the Boyer-Mitton-Vorkink (2010) predictive regression each require inputs the catalog does not carry at the required fidelity.
- **Closed-vocabulary markers lack evidence.** `[VINTAGE-DRIFT]` and `[STRUCTURAL-SAMPLE-VARIANCE]` (Assumption 13) cite rationales but no per-stage ratio table or per-bin (decile-level) N/MAX/SIZE comparison — the evidence the markers require per `rep/LOSS_FUNCTION.md`. Without those, a criterion-B exit is not properly evidenced.
- **Tables 3-5, 7-13, A1-A13 SKIP.** All depend on at least one unavailable factor series (FFCPS/FF6PS/SY/DHS), the BW sentiment index, the 11-component MIS index, the 13F institutional holdings quarterly merge, or the E(ISKEW) regression. Documented in the budget_flag of `tables_to_replicate.json`.
- **REPORT.md headline tally is stale.** Reports "13 Match / 53 FAIL / 154 MISSING" but `eval/scoring.json` shows 12 Match / 98 FAIL / 110 MISSING (DEV-010 regression). The canonical scorer is authoritative.
