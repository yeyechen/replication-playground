---
schema_version: 2
slug: max_on_steroids_attempt4
iteration: 1
verdict: FAILED
overall: 3.00
methodology: 4
headline_matching: 3
data_coverage: 4
concrete_result: 2
signal_strength: 1
corollary: 4
generated_at: 2026-08-15
---

# Replication Summary

## MAX on Steroids: A New Measure of Investor Attention to Lottery Stocks (Bali, Ince, Ozsoylev)

### Bottom line

**Replication result:** `FAILED`
**Overall quality:** 3.00 / 5.00

The replication faithfully implements Bali-Ince-Ozsoylev's MAX and MAX^beta portfolio sorts on a clean 1968-2022 panel of CRSP common stocks. The construction-validation claim (C3) is strongly supported — Table 2's cross-sectional medians of MAX, BETA, and IVOL across MAX deciles match in 8 of 9 cells. The headline anomaly direction (negative 10-1 spread) is reproduced in every signed cell. However, the magnitude shortfall on Tables 1 and 6 (replicated spread is 11-50% of the paper's) is paired with a sign flip on P10_RET_RF — the high-MAX portfolio earns +0.47%/mo in the replication where the paper reports -0.32. This sign flip on a load-bearing headline cell drives the rubric's kill-switch on Signal Strength and makes the binary verdict FAILED. The single highest-leverage next-iteration fix is switching from 1-month-lagged ME to the standard June-t ME snapshot used by FF1993 and Bali-Cakici-Whitelaw (2011).

## Quality assessment

| Dimension | Score | Assessment |
|---|---:|---|
| Methodology | 4/5 | Universe filter (shrcd 10/11, exchcd 1/2/3, SIC exclusions, $5 price floor, 15-day minimum), 252-day rolling BETA/IVOL, MAX = top-5 daily returns, VW by ME_lag1, NW(6) t-stats, FF3/FFC4/FF5/FF6 regressions — all faithfully implemented. Sub-check 7 (diagnostic evidence for FAILs) is the only gap: the magnitude-shortfall hypotheses are listed but the leading one (June-t ME snapshot) is not yet tested. |
| Headline matching | 3/5 | Direction matches on every signed headline cell (10-1 RET-RF and the five alpha columns on both Tables 1 and 6); magnitude is 11-50% of paper. Right sign, rough shape, large magnitude drift — band 3. |
| Data coverage | 4/5 | Period exact (1968-01 to 2022-12, 660 months), ~2,616 obs/month matches the paper's universe density, documented CRSP vintage substitutions (dlretx for dlret, dsenames for exchcd, FF6 in lieu of FF6PS), join hygiene clean. |
| Concrete result matching | 2/5 | 10 Match / 15 FAIL / 0 MISSING / 0 SKIP across 25 committed cells (40.0% match rate) — band 2. |
| Signal strength | 1/5 | P10_RET_RF carries the wrong sign on Tables 1 and 6 (paper -0.32 / -0.10; replication +0.47 on both). Every other headline D10-D1 alpha has r ∈ [0.11, 0.33], outside the [0.33, 3.0] band. Wrong sign on a headline cell triggers the dimension-1 kill-switch. |
| Corollary | 4/5 | C3 (cross-sectional confounding) is well-supported by 8/9 Table 2 cells matching. C4 (MAX^beta neutralization) is not in the committed selection but is implicitly exercised by Table 6's construction. |

## What replicated and what it validates

| Paper output | High-level evidence | What it supports |
|---|---|---|
| Table 1 (Univariate MAX deciles) | Long leg P1_RET_RF matches paper (+0.74 vs +0.63, Match); high-MAX P10_RET_RF fails (sign disagreement); D10-D1 RET-RF and the five alpha columns all correctly signed but ~30% of paper's magnitude (FAIL on 7 cells). | The paper's direction-of-effect claim C1 is reproduced; the magnitude-claim is not. |
| Table 2 (Cross-sectional medians) | P1_MAX, P10_MAX, D10_D1_MAX, P1_BETA, P10_BETA, P1_IVOL, P10_IVOL, D10_D1_IVOL all Match within tolerance; D10_D1_BETA FAIL (replicated 0.626 vs paper 0.462, r = 1.35). MAX, BETA, IVOL all increase monotonically across deciles. | The paper's C3 cross-sectional-confounding claim is strongly supported. The sort logic, the universe filter, and the BETA/IVOL construction all validate. |
| Table 6 (MAX^beta conditional sort) | Same pattern as Table 1: long leg matches, short leg fails on sign, D10-D1 spread correctly signed but ~30% of paper's magnitude (FAIL on 7 cells). | The paper's C2 claim (MAX^beta produces a robust anomaly) is direction-validated; magnitude is short. |

## Important gaps

- **Third-party factors (SY, DHS, FFCPS, FF6PS) are not in ClickHouse** and were dropped per `assumptions.md` A1-A3 (logged as `[THIRD-PARTY-DATASET]`). The paper's central novel claim that MAX^beta is robust to SY/DHS while MAX is not cannot be exercised in this pipeline without external CSV loading. Non-actionable in the current ClickHouse catalog.
- **The MIS composite (Stambaugh-Yuan 2017)** requires 11 firm-level Compustat characteristics (Assumption 19). The Compustat pipeline is in place but the composite is not constructed; Table 2's MIS column is dropped.
- **VW weighting convention is a known unresolved hypothesis.** The replication uses 1-month-lagged ME; the paper most likely uses the June-t ME snapshot (FF1993/Bali 2011 convention). Switching the VW weight to June-t ME is the single highest-leverage next-iteration fix and would resolve M1 (sign disagreement on P10_RET_RF) and likely most of M2 (magnitude shortfall on the 10-1 spreads). Currently documented as `[VINTAGE-DRIFT]` + `[STRUCTURAL-SAMPLE-VARIANCE]` in `assumptions.md` A16/A17.
- **CRSP 2026 vintage carries 2020-2021 COVID-era lottery tail** that the paper did not have. If the June-t ME fix is insufficient, restricting the sample to 1968-2019 may close the magnitude gap.
- **Stale `eval/scoring.json`** contains pre-binary-match aggregates (n_committed=35, loss=0.71). The canonical scorer overwrites it on each run; this is hygiene, not substantive.
