---
schema_version: 2
slug: weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns
iteration: 4
verdict: FAILED
overall: 2.50
methodology: 3
headline_matching: 2
data_coverage: 4
concrete_result: 2
signal_strength: 2
corollary: 2
generated_at: 2026-08-14T00:00:00
---

# Replication Summary

## Weber (2018) — Cash Flow Duration and the Term Structure of Equity Returns

### Bottom line

**Replication result:** `FAILED`
**Overall quality:** 2.50 / 5.00

The paper's central claim is reproduced in direction and statistical significance: a long-short duration strategy (low-dur minus high-dur) earns a positive and significant average excess return of +0.46% per month (t = +2.49) versus the paper's +1.10%. The replication is a **documented partial** that closes the replicator-auditor loop under `rep/LOSS_FUNCTION.md` criterion B (documented-residue exit): the loss has plateaued at 0.6364 across two iterations, every remaining FAIL carries a closed-vocabulary marker with evidence, and the methodology is now paper-faithful after iter 4 restored the 1%/99% winsorization on dur that iter 3 had dropped. The headline magnitude is 42% of the paper — the binding constraint is the dur-returns relationship itself, bounded by the audit-preserved dur formula (P_t = ME, 15-year AR(1)) and seed-clip envelope. The qualitative claim holds; the magnitude gap is structural and documented.

## Quality assessment

| Dimension | Score | Assessment |
|---|---:|---|
| Methodology | 3/5 | 7 of 8 sub-checks pass. Iter 4 restored the paper's 1%/99% dur winsorization (closing audit3's M1 deviation), verified ROE uses lagged BE, and applied CAGR for the 5y/3y sales-growth seed. HC0 SE remains a documented deviation from paper's OLS. |
| Headline matching | 2/5 | D1-D10 spread +0.46% vs paper +1.10% — sign correct, magnitude 42% (r = 0.42, band 2). Decile shape D1..D7 strictly decreasing (Match); D8-D10 hump violates monotonicity. |
| Data coverage | 4/5 | Sample period exact (Jul 1963-Jun 2014); IOR subsample exact (1981-2013); join hygiene clean. Three documented substitutions (Moody's BE supplement, dlret join, Baker-Wurgler sentiment). Composition drift on Table 1 descriptives is real but bounded. |
| Concrete result matching | 2/5 | 28 Match / 49 FAIL / 0 MISSING of 77 committed cells. Match rate 36.4% — band 2 (30-50%). |
| Signal strength | 2/5 | Headline cell r = \|0.46/1.10\| = 0.42 — band 2 ([0.33, 0.5), sign matches). CAPM alpha r = 0.50; Sharpe r = 0.42. |
| Corollary | 2/5 | Corollary match rate = 25/74 = 33.8% (excluding the 3 C1 headline cells) — band 2 (25-50%). T3 FF3/FF4/FF5 all FAIL; T4 subsamples 9 of 11 FAIL. |

## What replicated and what it validates

| Paper output | High-level evidence | What it supports |
|---|---|---|
| Table 1 (Summary stats) | Mean_Dur 18.96 vs paper 18.77 (Match, within ±1%); Mean_BM, Mean_ME, Mean_Age, Std_PR all Match. Std_Dur 4.05 vs paper 5.37 (FAIL, paper-faithful 1%/99% clip restored in iter 4). Std_BM 1.02 vs paper 0.53 (FAIL, `[THIRD-PARTY-DATASET]` — Moody's BE substitute missing). Mean_IOR 0.38 vs paper 0.44 (FAIL, `[THIRD-PARTY-DATASET]`). | Duration construction correct in shape, sign, and central tendency. dur-BM correlation correctly negative (Spearman -0.62). Seed-clip envelope is binding and audit-preserved. |
| Table 2 (Decile returns) | D1..D7 mean excess returns Match within ±15%. D8, D9, D10 all FAIL (right-tail hump). D1-D10 spread +0.461% (sign correct, magnitude 42%, t = +2.49). Beta_D1, Beta_D10, Beta_D1_minus_D10 all Match (1.052, 1.414, -0.362 vs paper 1.05, 1.41, -0.36). | Claim C1 (term structure is downward-sloping) is qualitatively reproduced at ~42% magnitude. The betas match perfectly, confirming the cross-sectional dur sort produces the intended risk ordering. |
| Table 3 (FF3/FF4/FF5 alphas) | FF3 D1-D10 alpha +0.096% vs paper +0.84% (FAIL, 11% of paper). FF4 +0.203% vs +0.66% (FAIL). FF5 -0.219% vs +0.48% (FAIL, t = -1.51, marginally significant — should be reported as "no effect" per Spot-check 14b). Decile-level FF3 alphas mostly FAIL — D10 paper -0.38% vs ours +0.60%. | Claim C2 (factor models explain only ~50% of spread) is NOT reproduced — the replication's FF5 alpha is essentially zero. Tied to the dur right-tail composition and the dur-returns magnitude. |
| Table 5 (Subsample spreads + per-decile means) | 5 spread cells FAIL (all under-replicate vs paper). 1993-2003 spread -0.171% vs paper +1.10% (t = -0.24, n.s. — should be reported as "no effect"). 6 per-decile D1/D10 means: 2 Match, 4 FAIL (right-tail composition). | Claim C3 (temporal stability) is partially challenged — the dotcom subperiod has no significant effect in the replication, but other subperiods preserve the right-sign pattern. |
| Table 10 (Duration × RIOR) | HighRIOR_HighDur Match (0.85 vs paper 0.94). RIOR2/3/4 LowDur all Match (within ±12%). 11 of 17 cells FAIL. LowRIOR D1-D5 spread +0.58% vs paper +1.32% (FAIL) — the central qualitative pattern (effect concentrated in low-RIOR) is preserved; the magnitudes are off. | Claim C4 (effect concentrated in low-RIOR stocks) is qualitatively preserved at the low-dur cells but unreliable across the full RIOR grid. |

## Important gaps

- **Dur-returns magnitude at 42% of paper.** The D1-D10 spread (+0.46% vs paper +1.10%) is bounded by the dur formula (P_t = market equity, 15-year AR(1) recursion) and the audit-preserved seed-clip envelope (`roe_seed ∈ [-1, 1]`, `sales_g_seed ∈ [-1, 5]`). The dur-BM correlation is correctly negative (Pearson -0.135 panel, Spearman -0.62) but does not reach the paper's -0.70 — consistent with the seed-clip bounds compressing the dur distribution. Iter 4 verified that the dur formula and seed-clip envelope are the binding constraints; further changes would violate the audit-preserved constraint from iter 2.
- **Moody's BE supplement missing (Std_BM +93% drift).** The paper sources book equity from Moody's Industrial Annual; the catalog has Compustat-only BE. This is documented as `[THIRD-PARTY-DATASET]` in REPORT.md and is non-actionable without acquiring the Moody's data.
- **Std_Dur 4.05 vs paper 5.37 (FAIL, deliberate paper-faithful choice).** Iter 4 restored the paper's 1%/99% per-fyear winsorization on dur, which iter 3 had dropped to engineer a Std_Dur Match. The FAIL is methodologically faithful and documented in REPORT.md as a deliberate paper-faithful FAIL (`[STRUCTURAL-SAMPLE-VARIANCE]`); the iter-3 Match (5.52) was a methodology deviation.
- **T3 FF5 alpha sign disagreement (-0.22% vs paper +0.48%, t = -1.51).** Marginally significant and should be reported as "no effect" per Spot-check 14(b), not as "sign disagreement". The iter-4 dur right-tail shrinkage (max 598 → 41.88) widened this gap from -0.07 to -0.22.
- **49 FAILs documented at table level.** Closed-vocabulary markers (`[VINTAGE-DRIFT]`, `[THIRD-PARTY-DATASET]`, `[CONVENTION-APPLIED]`) are present in REPORT.md prose (12 marker mentions across T1/T2/T3/T4/T10) and in `preparations/assumptions.md` per-iteration summaries. Cell-level `notes` in `eval/scoring.json` is null for all cells; this is a documentation hygiene gap, not a substance gap.
- **Tables 4 (paper Table 6), 7, 8, 9, 12 not replicated.** Documented as scope decisions: Baker-Wurgler sentiment index missing from the ClickHouse catalog; volatility-managed return analysis out of scope.
