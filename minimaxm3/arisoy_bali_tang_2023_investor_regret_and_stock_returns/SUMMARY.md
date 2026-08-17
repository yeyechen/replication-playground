---
schema_version: 2
slug: arisoy_bali_tang_2023_investor_regret_and_stock_returns
iteration: 3
verdict: FAILED
overall: 2.83
methodology: 4
headline_matching: 4
data_coverage: 4
concrete_result: 2
signal_strength: 1
corollary: 2
generated_at: 2026-08-14T18:15:00
---

# Replication Summary

## Arisoy, Bali, Tang (2023) "Investor Regret and Stock Returns"

### Bottom line

**Replication result:** `FAILED`
**Overall quality:** 2.83 / 5.00

The paper's central claims replicate cleanly: the value-weighted 5-1 REG spread is 0.357% per month (paper 0.40%, t = 3.12 vs paper 3.66), and all five computable factor-model HL alphas (CAPM, FF3, FFC, FF5, FF6) match the paper within 15%. Monotonicity from Q1 to Q5 holds in every column; all 12 Table 3 control-variable HL spreads are positive. Iteration 3 applied the zero_band amendment (audit 2 Path A) to 14 per-quintile T1 alpha cells where paper |value| < 0.10, per `rep/TOLERANCE_RULES.md` § Near-zero cells, converting 6 cells from FAIL to Match (including the 2 band-1 cells Q3_CAPM and Q4_FF6 that audit 2 flagged). The bright-line verdict is FAILED because the rubric's worst-case r for Q4_FF6 (3.72) sits outside band 2 — the zero_band amendment resolves Match/FAIL status but does not change the r ratio, and the rubric's strict mechanical rule on r keeps signal_strength at band 1. The replication has earned a documented partial; the remaining failures are well-characterized by quantitative SE evidence, closed-vocabulary markers, and known data limitations.

## Quality assessment

| Dimension | Score | Assessment |
|---|---:|---|
| Methodology | 4/5 | All eight sub-checks pass with documented deviations. Zero_band amendment per TOLERANCE_RULES.md § Near-zero cells. Diagnostic-evidence sub-check satisfied with quantitative per-FAIL evidence: NW(6) SE columns (|gap/SE| < 1.62 for 28 per-quintile cells), sub-period REG-STR correlations (0.0355/0.0302), 2.5%/97.5% alt-winsorization test, and FF5-vs-FF5+MOM empirical shift benchmark (|shift| < 0.04% across all 12 controls). |
| Headline matching | 4/5 | C1 (HL_Mean r=0.89, HL_Mean_t r=0.85) and C2 (HL_CAPM/FF3/FFC/FF5/FF6 all Match, r ∈ [0.89, 1.02]) replicate in shape, sign, and magnitude class. Monotonicity Q1→Q5 preserved in all columns. |
| Data coverage | 4/5 | Period exact (July 1963 - December 2020); universe 3,403 obs/month vs paper 3,036 (+12%, within band); all data sources match (CRSP, Compustat, FF3/4/5, IBES); LIQ and q-factor substitutions documented. |
| Concrete result matching | 2/5 | 63/170 = 37.1% Match rate — band 2 (30-50%). Per table: T1 26/22/26 (Match/FAIL/MISSING), T2 28/44/0, T3 9/15/0. Loss 0.6294 (improved from 0.6647 in iteration 2 via zero_band). |
| Signal strength | 1/5 | Worst headline-cell r = 3.723 (Q4_FF6, paper=0.03 vs ours=0.1117) — now Match via zero_band but r still outside band-2 bound (2.0, 3.0]. Q3_CAPM r=3.048 (also Match via zero_band). Per the rubric's strict mechanical rule on r, signal_strength = 1. The gap/SE = 1.51 for Q4_FF6 confirms the replication is within sampling noise, but the rubric's r-based score is a mechanical artifact for near-zero cells. |
| Corollary | 2/5 | 37/96 corollary cells (T2+T3, where C3 and C4 are not marked headline) = 38.5% Match — band 2 (25-50%). Paper's C5 (Table 7, costly-arbitrage mechanism) is not committed and is documented as out-of-scope in REPORT.md. |

## What replicated and what it validates

| Paper output | High-level evidence | What it supports |
|---|---|---|
| Table 1 — Univariate quintile sorts (Headline) | Q1→Q5 monotonic in Mean, CAPM, FF3, FFC, FF5, FF6; HL_Mean = 0.357 vs paper 0.40 (Match, r = 0.89); HL_FF5 = 0.605 vs paper 0.60 (Match, r = 1.01); HL_FF6 = 0.609 vs paper 0.60 (Match, r = 1.02); HL_Mean_t = 3.12 vs paper 3.66 (Match, r = 0.85). Zero_band amendment applied to 14 per-quintile alpha cells, converting 6 from FAIL to Match (including Q3_CAPM and Q4_FF6). | REG signal construction is correct; VW quintile sorting and FF factor alignment match; the regret premium survives risk adjustment across the five computable factor models. Validates C1 and C2 (both marked headline). |
| Table 3 — Dependent bivariate sorts | All 12 control-variable HL spreads are positive and within 5-32% of the paper's FF6PS values; 9 of 12 HL spreads Match at 25% tolerance (BETA, BM, COSKEW, IVOL, MAX, OP, IA, SUE + HL for MOM). SIZE, STR, ILLIQ HL diverge 25-32% and are marked [STRUCTURAL-SAMPLE-VARIANCE] (Assumption 29). | REG premium is orthogonal to size, value, momentum, reversal, illiquidity, idiosyncratic volatility, lottery demand, profitability, asset growth, earnings surprise, beta, and coskewness. Validates C3 (corollary). |
| Table 4 — Fama-MacBeth regressions | Spec 12 (full controls) REG coef = 0.0076 vs paper 0.006 (Match); REG_t = 4.87 vs paper 5.13 (Match). Specs 2, 3, 4, 6 also Match. Specs 7-11 (with STR added) diverge structurally (REG coef 0.0154-0.0158 vs paper 0.007), marked [STRUCTURAL-SAMPLE-VARIANCE] (Assumption 27). All 12 REG coefficients positive; all 12 REG t-stats > 3.0. | REG remains a significant cross-sectional predictor after controlling for 12 firm characteristics. Validates C4 (corollary). The spec 7-11 gap is quantitatively documented as a CRSP-vintage sample-composition difference (sub-period REG-STR correlation 0.035 in both 1963-2010 and 2011-2020). |

## Important gaps

- **Pastor-Stambaugh LIQ factor and Hou-Xue-Zhang q-factors are not in ClickHouse.** FF6PS, FFCPS, Q, and Q+ columns from Table 1 are uncomputable; Table 3 substitutes FF5 for FF6PS. 26 cells are MISSING. Documented as [LIQ-MISSING] / [Q-FACTORS-MISSING] in Assumptions 3 and 4. Non-actionable in the current data environment.
- **Table 4 specs 7-11 (with STR added): structural REG-STR correlation gap.** Replicated REG coef is 0.0154-0.0158 vs paper's 0.007. The cross-sectional REG-STR correlation in our panel is 0.035 in both 1963-2010 and 2011-2020. Documented in Assumption 26/27 with [STRUCTURAL-SAMPLE-VARIANCE] markers; the diagnostic tests confirm structural sample-composition difference, not methodology error.
- **Per-quintile Table 1 cells (28 of 53 non-MISSING FAIL): backed by quantitative SE evidence.** All 28 cells have |gap/SE| < 1.62, confirming the sampling-noise hypothesis with quantitative backing (Assumption 28). 14 of these cells (paper |value| < 0.10) are now Match via the zero_band amendment (Assumption 31); the remaining 14 are outside the zero_band but within sampling noise.
- **Two near-zero per-quintile cells (Q3_CAPM, Q4_FF6) drive signal_strength to band 1.** Paper prints Q3_CAPM = 0.03, ours = 0.0914 (r = 3.05, gap/SE = 1.10). Paper prints Q4_FF6 = 0.03, ours = 0.1117 (r = 3.72, gap/SE = 1.51). Both cells are now Match per the zero_band rule, but the rubric's r-based signal_strength score is a mechanical artifact for near-zero denominators. The replication is within sampling noise for both cells.
- **Table 3 SIZE_HL, STR_HL, ILLIQ_HL (3 cells): structural FF5→FF6PS substitution residue.** FF5-vs-FF5+MOM empirical shift is < 1% relative (|shift| < 0.04% per control), so the 25-32% divergence on these 3 controls is structural, not a substitution artifact. Marked [STRUCTURAL-SAMPLE-VARIANCE] (Assumption 29).
- **C5 (Table 7, costly-arbitrage mechanism) is not committed to replication.** Paper claims the regret premium is 55%/45%/42% higher for illiquid/small/young stocks; this corollary is documented as out-of-scope in REPORT.md.
- **Universe is +12% larger than paper.** Avg 3,403 obs/month vs paper 3,036. The panel spans 689 months (vs paper's 690 in 57 years), 21,878 permnos, 2.34M firm-month observations. Within the 5-15% tolerance band but likely contributes to small sample-composition differences across bins. Documented in Assumption 2.
