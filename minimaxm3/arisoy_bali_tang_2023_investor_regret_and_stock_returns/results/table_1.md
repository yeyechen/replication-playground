# Table 1 — Univariate VW quintile portfolios sorted by REG

Sample: NYSE/AMEX/NASDAQ common stocks (shrcd 10,11), $5–$1000 price screen.
Sort: each month from 1963-07 to 2020-11, NYSE-only 20/40/60/80 percentiles of REG.
REG winsorized cross-sectionally at 1%/99% per month before sort.
Returns: next-month VW (me_lag1-weighted) excess returns. T = 689 months.
Alphas: time-series regressions with Newey-West (1987), 6 lags. Units: %/month.

Note: FFCPS, FF6PS, Q, Q+ models dropped (LIQ + q-factors not in ClickHouse).

| Quintile | REG (%) | Mean | CAPM | FF3 | FFC | FF5 | FF6 |
|---|---|---|---|---|---|---|---|---|
| Q1 | 2.10 | 0.46<br>[2.65] | -0.06<br>[-0.82] | -0.12<br>[-1.80] | -0.13<br>[-2.09] | -0.25<br>[-4.09] | -0.25<br>[-3.99] |
| Q2 | 12.02 | 0.46<br>[2.77] | -0.05<br>[-0.84] | -0.11<br>[-2.25] | -0.10<br>[-2.12] | -0.21<br>[-4.70] | -0.19<br>[-4.36] |
| Q3 | 21.07 | 0.63<br>[3.73] | 0.09<br>[1.64] | 0.04<br>[0.81] | 0.02<br>[0.47] | -0.07<br>[-1.47] | -0.07<br>[-1.43] |
| Q4 | 33.28 | 0.71<br>[4.04] | 0.13<br>[2.31] | 0.09<br>[1.77] | 0.12<br>[2.20] | 0.08<br>[1.61] | 0.11<br>[2.06] |
| Q5 | 85.10 | 0.82<br>[4.10] | 0.19<br>[2.79] | 0.26<br>[4.53] | 0.28<br>[4.71] | 0.36<br>[5.94] | 0.36<br>[5.95] |
| HL (5-1) | 83.00 | 0.36<br>[3.12] | 0.25<br>[2.02] | 0.38<br>[3.71] | 0.41<br>[4.11] | 0.61<br>[6.19] | 0.61<br>[6.22] |

Each cell: alpha (%/month) with NW(6) t-stat in brackets.

## Comparison with paper Table 1

Ours vs paper for each cell. Format: ours vs paper.

| Cell | Ours | Paper | Diff (%) |
|---|---|---|---|
| Q1_REG | 2.0978 (percent) | 1.5300 (percent) | 37.1% |
| Q2_REG | 12.0182 (percent) | 10.1300 (percent) | 18.6% |
| Q3_REG | 21.0714 (percent) | 18.0400 (percent) | 16.8% |
| Q4_REG | 33.2750 (percent) | 28.7300 (percent) | 15.8% |
| Q5_REG | 85.0995 (percent) | 71.6800 (percent) | 18.7% |
| Q1_Mean | 0.4589 (%/mo) | 0.3500 (%/mo) | 31.1% |
| Q2_Mean | 0.4581 (%/mo) | 0.4200 (%/mo) | 9.1% |
| Q3_Mean | 0.6337 (%/mo) | 0.5600 (%/mo) | 13.2% |
| Q4_Mean | 0.7093 (%/mo) | 0.7100 (%/mo) | 0.1% |
| Q5_Mean | 0.8154 (%/mo) | 0.7500 (%/mo) | 8.7% |
| HL_REG | 83.0017 (percent) | 70.1400 (percent) | 18.3% |
| HL_Mean | 0.3566 (%/mo) | 0.4000 (%/mo) | 10.9% |
| Q1_CAPM | -0.0591 (%/mo) | -0.1700 (%/mo) | 65.2%  **DIVERGENCE** |
| Q2_CAPM | -0.0461 (%/mo) | -0.0500 (%/mo) | 7.9% |
| Q3_CAPM | 0.0914 (%/mo) | 0.0300 (%/mo) | 204.8%  **DIVERGENCE** |
| Q4_CAPM | 0.1272 (%/mo) | 0.1200 (%/mo) | 6.0% |
| Q5_CAPM | 0.1888 (%/mo) | 0.1200 (%/mo) | 57.4%  **DIVERGENCE** |
| HL_CAPM | 0.2480 (%/mo) | 0.2900 (%/mo) | 14.5% |
| HL_CAPM_t | 2.0205 (t) | 4.1000 (t) | 50.7%  **DIVERGENCE** |
| Q1_FF3 | -0.1157 (%/mo) | -0.2200 (%/mo) | 47.4% |
| Q2_FF3 | -0.1054 (%/mo) | -0.1000 (%/mo) | 5.4% |
| Q3_FF3 | 0.0394 (%/mo) | -0.0200 (%/mo) | 297.0%  **DIVERGENCE** |
| Q4_FF3 | 0.0930 (%/mo) | 0.0900 (%/mo) | 3.4% |
| Q5_FF3 | 0.2603 (%/mo) | 0.1700 (%/mo) | 53.1%  **DIVERGENCE** |
| HL_FF3 | 0.3761 (%/mo) | 0.3900 (%/mo) | 3.6% |
| HL_FF3_t | 3.7126 (t) | 3.7900 (t) | 2.0% |
| Q1_FFC | -0.1326 (%/mo) | -0.2200 (%/mo) | 39.7% |
| Q2_FFC | -0.0996 (%/mo) | -0.1000 (%/mo) | 0.4% |
| Q3_FFC | 0.0241 (%/mo) | -0.0400 (%/mo) | 160.2%  **DIVERGENCE** |
| Q4_FFC | 0.1245 (%/mo) | 0.0800 (%/mo) | 55.6%  **DIVERGENCE** |
| Q5_FFC | 0.2780 (%/mo) | 0.2000 (%/mo) | 39.0% |
| HL_FFC | 0.4107 (%/mo) | 0.4100 (%/mo) | 0.2% |
| HL_FFC_t | 4.1081 (t) | 6.5200 (t) | 37.0% |
| Q1_FF5 | -0.2461 (%/mo) | -0.3300 (%/mo) | 25.4% |
| Q2_FF5 | -0.2110 (%/mo) | -0.1900 (%/mo) | 11.0% |
| Q3_FF5 | -0.0693 (%/mo) | -0.1400 (%/mo) | 50.5%  **DIVERGENCE** |
| Q4_FF5 | 0.0835 (%/mo) | 0.0400 (%/mo) | 108.7%  **DIVERGENCE** |
| Q5_FF5 | 0.3590 (%/mo) | 0.2700 (%/mo) | 32.9% |
| HL_FF5 | 0.6051 (%/mo) | 0.6000 (%/mo) | 0.8% |
| HL_FF5_t | 6.1921 (t) | 5.6700 (t) | 9.2% |
| Q1_FF6 | -0.2460 (%/mo) | -0.3100 (%/mo) | 20.6% |
| Q2_FF6 | -0.1943 (%/mo) | -0.1800 (%/mo) | 8.0% |
| Q3_FF6 | -0.0702 (%/mo) | -0.1400 (%/mo) | 49.8% |
| Q4_FF6 | 0.1117 (%/mo) | 0.0300 (%/mo) | 272.3%  **DIVERGENCE** |
| Q5_FF6 | 0.3632 (%/mo) | 0.2900 (%/mo) | 25.2% |
| HL_FF6 | 0.6092 (%/mo) | 0.6000 (%/mo) | 1.5% |
| HL_FF6_t | 6.2216 (t) | 4.9500 (t) | 25.7% |
| HL_Mean_t | 3.1224 (t) | 3.6600 (t) | 14.7% |

## M2 — Per-cell NW(6) standard errors and gap significance

For each per-quintile alpha cell, the NW(6) SE = |alpha / t-stat| and
the |gap/SE| = |paper - ours| / SE. A |gap/SE| < 3 means the gap is
consistent with sampling noise; |gap/SE| > 3 marks a structural mismatch.

| Cell | Ours (%/mo) | Paper (%/mo) | SE (%/mo) | |gap/SE| | Note |
|---|---:|---:|---:|---:|---|
| Q1_Mean | 0.4589 | 0.3500 | 0.1734 | 0.63 | within noise |
| Q2_Mean | 0.4581 | 0.4200 | 0.1655 | 0.23 | within noise |
| Q3_Mean | 0.6337 | 0.5600 | 0.1700 | 0.43 | within noise |
| Q4_Mean | 0.7093 | 0.7100 | 0.1757 | 0.00 | within noise |
| Q5_Mean | 0.8154 | 0.7500 | 0.1991 | 0.33 | within noise |
| HL_Mean | 0.3566 | 0.4000 | 0.1142 | 0.38 | within noise |
| Q1_CAPM | -0.0591 | -0.1700 | 0.0723 | 1.53 | within noise |
| Q2_CAPM | -0.0461 | -0.0500 | 0.0548 | 0.07 | within noise |
| Q3_CAPM | 0.0914 | 0.0300 | 0.0558 | 1.10 | within noise |
| Q4_CAPM | 0.1272 | 0.1200 | 0.0550 | 0.13 | within noise |
| Q5_CAPM | 0.1888 | 0.1200 | 0.0677 | 1.02 | within noise |
| HL_CAPM | 0.2480 | 0.2900 | 0.1227 | 0.34 | within noise |
| Q1_FF3 | -0.1157 | -0.2200 | 0.0643 | 1.62 | within noise |
| Q2_FF3 | -0.1054 | -0.1000 | 0.0468 | 0.11 | within noise |
| Q3_FF3 | 0.0394 | -0.0200 | 0.0488 | 1.22 | within noise |
| Q4_FF3 | 0.0930 | 0.0900 | 0.0525 | 0.06 | within noise |
| Q5_FF3 | 0.2603 | 0.1700 | 0.0575 | 1.57 | within noise |
| HL_FF3 | 0.3761 | 0.3900 | 0.1013 | 0.14 | within noise |
| Q1_FFC | -0.1326 | -0.2200 | 0.0634 | 1.38 | within noise |
| Q2_FFC | -0.0996 | -0.1000 | 0.0471 | 0.01 | within noise |
| Q3_FFC | 0.0241 | -0.0400 | 0.0514 | 1.25 | within noise |
| Q4_FFC | 0.1245 | 0.0800 | 0.0565 | 0.79 | within noise |
| Q5_FFC | 0.2780 | 0.2000 | 0.0590 | 1.32 | within noise |
| HL_FFC | 0.4107 | 0.4100 | 0.1000 | 0.01 | within noise |
| Q1_FF5 | -0.2461 | -0.3300 | 0.0602 | 1.39 | within noise |
| Q2_FF5 | -0.2110 | -0.1900 | 0.0448 | 0.47 | within noise |
| Q3_FF5 | -0.0693 | -0.1400 | 0.0471 | 1.50 | within noise |
| Q4_FF5 | 0.0835 | 0.0400 | 0.0519 | 0.84 | within noise |
| Q5_FF5 | 0.3590 | 0.2700 | 0.0605 | 1.47 | within noise |
| HL_FF5 | 0.6051 | 0.6000 | 0.0977 | 0.05 | within noise |
| Q1_FF6 | -0.2460 | -0.3100 | 0.0617 | 1.04 | within noise |
| Q2_FF6 | -0.1943 | -0.1800 | 0.0445 | 0.32 | within noise |
| Q3_FF6 | -0.0702 | -0.1400 | 0.0491 | 1.42 | within noise |
| Q4_FF6 | 0.1117 | 0.0300 | 0.0541 | 1.51 | within noise |
| Q5_FF6 | 0.3632 | 0.2900 | 0.0610 | 1.20 | within noise |
| HL_FF6 | 0.6092 | 0.6000 | 0.0979 | 0.09 | within noise |
