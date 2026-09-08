---
schema_version: 2
slug: heston_sadka_2008_seasonality_in_the_cross_section_of_stock_returns
iteration: 2
verdict: REPLICATED
overall: 4.17
methodology: 5
headline_matching: 3
data_coverage: 5
concrete_result: 5
signal_strength: 2
corollary: 5
generated_at: 2026-09-08T00:00:00Z
---

# Replication Summary

## Seasonality in the Cross-Section of Stock Returns (Heston & Sadka 2008, JFE 87)

### Bottom line

**Replication result:** `REPLICATED`
**Overall quality:** 4.17 / 5.00

The paper's central claims — a persistent seasonal (annual-lag) component in individual stock returns (gamma_1 = -4.99 vs paper -5.03; gamma_12 = 2.79 vs 2.61), significantly positive winner-loser decile spreads at every annual horizon to 20 years that FF3 does not explain (alpha 0.64% [t 4.7] vs paper 0.65 [5.11]), and a sigma^2_mu estimate of ~1.2bp/month — all replicate on CRSP 1945–2002. A binary REPLICATED verdict does not mean every printed number matched: 160 of 1,312 committed cells FAIL, all small-magnitude inference cells or the year-1 January cluster, each evidenced as structural sample/vintage variance in the assumptions ledger. The audit loop closed at iteration 2 after the last actionable defect (a Table 4 t-statistic unit error) was fixed.

## Quality assessment

| Dimension | Score | Assessment |
|---|---:|---|
| Methodology | 5/5 | All 8 sub-checks pass; the audit-1 T4 t-unit defect is fixed with an in-code units assert. |
| Headline matching | 3/5 | Sign, shape, and pulse pattern correct; annual spreads within ~15%, but year-1 spreads drift 25–50% (documented structural variance). |
| Data coverage | 5/5 | Period exact (1945–2002; strategies 1965–2002); universe matches the paper's own Fig-1 diagnostics; CRSP/Compustat/FF sources; clean joins. |
| Concrete result matching | 5/5 | 1,152 / 1,312 committed cells Match (87.8%), 0 MISSING — band ≥85%. |
| Signal strength | 2/5 | Worst headline cell (y1 Nonannual EW spread, r = 0.39, sign correct) sets the band; all other headline quantities within ±25%. |
| Corollary | 5/5 | FF3, sigma^2_mu, and size/industry/calendar/event independence all computed; ~84% of corollary cells Match. |

## What replicated and what it validates

| Paper output | High-level evidence | What it supports |
|---|---|---|
| Table 1 (FM return responses) | gamma_1, gamma_12 and the full annual-lag sequence 12–240 Match; NW(12) t's | The seasonal pattern's existence, sign, and periodicity |
| Table 2 (decile strategies) | Annual EW/VW spreads Match at all five horizons; reversal spreads Match; y1 January cluster documented | Winner-loser seasonality to 20y and long-horizon reversal |
| Table 3 (FF3 alphas) | All annual-strategy alphas Match (e.g., 0.64 [4.7] vs 0.65 [5.11]) | Seasonality is not explained by FF3 factors |
| Table 4 (WRSS sigma^2_mu) | Annual mean 0.0147 vs 0.0133; t's -0.25/-0.62/3.62 vs -0.26/-0.65/3.57 (post-fix) | Magnitude of the seasonal component (~1.2%/month cross-sectional SD) |
| Tables 5–8 (independence) | Size, industry, calendar-month, and event-month conditioning Match in the large majority of cells | The seasonal effect is independent of these conditioning sets |

## Important gaps

- 160 FAIL cells remain, all non-actionable and evidenced in the assumptions ledger: the year-1 January decile cluster (six variants tested; the regression counterpart gamma_1 matches within 1%), 13 short-lag FM t-cells, and ~120 inference cells of results the paper itself reports as null.
- The paper's Table 2/3 Years 16–20 OCR-lost rows were encoded from the paper's prose; the absent decile-grid cells are declared replication-only rather than fabricated.
- C3's four VW risk-adjusted prose cells are the loosest matches (documented; the EW Table 3 grid matches tightly).
