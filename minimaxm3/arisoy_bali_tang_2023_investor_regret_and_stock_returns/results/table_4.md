# Table 4 — Fama-MacBeth Cross-Sectional Regressions

Dependent variable: one-month-ahead excess returns (`ret_excess_lead1`).
Regressor of interest: REG (sign-flipped; higher = higher regret).
Panel: monthly cross-section of NYSE/AMEX/NASDAQ common stocks (shrcd 10,11),
$5–$1000 price screen, July 1963 to November 2020 (T months = 688).
Sample period for SPEC: each spec drops firm-months with NaN in any of its
regressors. Sample period sizes shown below.
Time-series statistic: Newey-West (1987) with 6 lags.

Specifications 1-6 (panel A) progressively add controls;
specifications 7-12 (panel B) replicate 1-6 + STR (short-term reversal).

Primary winsorization is 1%/99% per month (Assumption 14). Alternative
2.5%/97.5% per month is shown for audit major [M1] comparison.

| Spec | Description |
|---:|---|
| 1 | reg |
| 2 | reg, beta, log_me, bm |
| 3 | reg, beta, log_me, bm, mom |
| 4 | reg, beta, log_me, bm, mom, illiq, coskew, ivol, max5 |
| 5 | reg, beta, log_me, bm, mom, illiq, coskew, ivol, max5, op, ia |
| 6 | reg, beta, log_me, bm, mom, illiq, coskew, ivol, max5, op, ia, sue |
| 7 | reg, str |
| 8 | reg, beta, log_me, bm, str |
| 9 | reg, beta, log_me, bm, mom, str |
| 10 | reg, beta, log_me, bm, mom, illiq, coskew, ivol, max5, str |
| 11 | reg, beta, log_me, bm, mom, illiq, coskew, ivol, max5, op, ia, str |
| 12 | reg, beta, log_me, bm, mom, illiq, coskew, ivol, max5, op, ia, sue, str |

**Table 4a — REG coefficient (mean across monthly OLS)**

| Variable | (1) | (2) | (3) | (4) | (5) | (6) | (7) | (8) | (9) | (10) | (11) | (12) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| REG coef | +0.016 | +0.016 | +0.016 | +0.012 | +0.012 | +0.008 | +0.015 | +0.016 | +0.016 | +0.012 | +0.012 | +0.008 |
| REG t-stat (NW-6) | +10.09 | +10.45 | +10.76 | +9.16 | +9.46 | +4.84 | +9.98 | +10.52 | +10.84 | +9.29 | +9.58 | +4.87 |
| REG SE | +0.00155 | +0.00151 | +0.00145 | +0.00134 | +0.00131 | +0.00157 | +0.00155 | +0.00150 | +0.00144 | +0.00132 | +0.00130 | +0.00156 |

**Table 4b — REG coefficient + t-stat per specification**

| Specification | Controls (besides REG) | T (months) | REG coef | REG t-stat | REG SE |
|---|---|---:|---:|---:|---:|
| 1 | REG only | 688 | +0.0156 | +10.087 | +0.00155 |
| 2 | REG, beta, log_me, bm | 676 | +0.0158 | +10.449 | +0.00151 |
| 3 | REG, beta, log_me, bm, mom | 676 | +0.0156 | +10.757 | +0.00145 |
| 4 | REG, beta, log_me, bm, mom, illiq, coskew, ivol, max5 | 676 | +0.0123 | +9.164 | +0.00134 |
| 5 | REG, beta, log_me, bm, mom, illiq, coskew, ivol, max5, op, ia | 676 | +0.0124 | +9.461 | +0.00131 |
| 6 | REG, beta, log_me, bm, mom, illiq, coskew, ivol, max5, op, ia, sue | 338 | +0.0076 | +4.839 | +0.00157 |
| 7 | REG, str | 687 | +0.0154 | +9.977 | +0.00155 |
| 8 | REG, beta, log_me, bm, str | 676 | +0.0158 | +10.516 | +0.00150 |
| 9 | REG, beta, log_me, bm, mom, str | 676 | +0.0156 | +10.837 | +0.00144 |
| 10 | REG, beta, log_me, bm, mom, illiq, coskew, ivol, max5, str | 676 | +0.0122 | +9.288 | +0.00132 |
| 11 | REG, beta, log_me, bm, mom, illiq, coskew, ivol, max5, op, ia, str | 676 | +0.0124 | +9.576 | +0.00130 |
| 12 | REG, beta, log_me, bm, mom, illiq, coskew, ivol, max5, op, ia, sue, str | 338 | +0.0076 | +4.874 | +0.00156 |

**Table 4c — Alternative winsorization (2.5%/97.5% per month)**

Audit major [M1]: test whether tighter winsorization closes the specs 7-11 gap.

| Spec | REG coef (1%/99%) | REG coef (2.5%/97.5%) | Δ coef | REG t (1%/99%) | REG t (2.5%/97.5%) |
|---|---:|---:|---:|---:|---:|
| 1 | +0.0156 | +0.0165 | +0.0009 | +10.087 | +10.134 |
| 2 | +0.0158 | +0.0169 | +0.0011 | +10.449 | +10.597 |
| 3 | +0.0156 | +0.0167 | +0.0011 | +10.757 | +10.914 |
| 4 | +0.0123 | +0.0131 | +0.0008 | +9.164 | +9.287 |
| 5 | +0.0124 | +0.0132 | +0.0008 | +9.461 | +9.598 |
| 6 | +0.0076 | +0.0080 | +0.0004 | +4.839 | +4.792 |
| 7 | +0.0154 | +0.0164 | +0.0009 | +9.977 | +10.044 |
| 8 | +0.0158 | +0.0169 | +0.0011 | +10.516 | +10.677 |
| 9 | +0.0156 | +0.0167 | +0.0011 | +10.837 | +11.008 |
| 10 | +0.0122 | +0.0131 | +0.0008 | +9.288 | +9.431 |
| 11 | +0.0124 | +0.0132 | +0.0008 | +9.576 | +9.732 |
| 12 | +0.0076 | +0.0080 | +0.0004 | +4.874 | +4.841 |

## Comparison with paper Table 4

Paper reports coefficients in decimal units and t-stats as float.
Format: ours vs paper.

| Spec | REG_coef ours | REG_coef paper | Diff (%) | REG_t ours | REG_t paper | Diff (%) |
|---|---:|---:|---:|---:|---:|---:|
| 1 | +0.0156 | +0.011 | 42.2% **DIVERGENCE** | +10.087 | +6.44 | 56.6% **DIVERGENCE** |
| 2 | +0.0158 | +0.014 | 12.8% | +10.449 | +8.23 | 27.0% |
| 3 | +0.0156 | +0.014 | 11.6% | +10.757 | +8.18 | 31.5% **DIVERGENCE** |
| 4 | +0.0123 | +0.011 | 11.4% | +9.164 | +7.15 | 28.2% |
| 5 | +0.0124 | +0.009 | 38.1% **DIVERGENCE** | +9.461 | +6.70 | 41.2% **DIVERGENCE** |
| 6 | +0.0076 | +0.008 | 5.3% | +4.839 | +6.60 | 26.7% |
| 7 | +0.0154 | +0.007 | 120.6% **DIVERGENCE** | +9.977 | +4.19 | 138.1% **DIVERGENCE** |
| 8 | +0.0158 | +0.007 | 125.8% **DIVERGENCE** | +10.516 | +4.94 | 112.9% **DIVERGENCE** |
| 9 | +0.0156 | +0.007 | 123.5% **DIVERGENCE** | +10.837 | +4.85 | 123.4% **DIVERGENCE** |
| 10 | +0.0122 | +0.008 | 52.8% **DIVERGENCE** | +9.288 | +5.62 | 65.3% **DIVERGENCE** |
| 11 | +0.0124 | +0.007 | 77.3% **DIVERGENCE** | +9.576 | +5.65 | 69.5% **DIVERGENCE** |
| 12 | +0.0076 | +0.006 | 26.4% | +4.874 | +5.13 | 5.0% |

## M1 — STR-REG gap diagnosis

Cross-sectional REG-STR correlation in our panel is 0.035 (median across
months), versus the paper's implied much stronger overlap (paper specs 1-6
REG coef drops 36% when STR is added (0.011 → 0.007); in our data the drop
is 0% (0.0156 → 0.0154). Alternative 2.5%/97.5% winsorization does not close
the gap (alt spec 7 REG coef ≈ 0.016, same as primary). The gap is therefore
a structural sample-composition difference, not a winsorization artifact.

Cross-sectional correlations by sub-period:

| Period | n_months | mean corr | median corr |
|---|---:|---:|---:|
| Full sample 1963-2020 | 688 | +0.0346 | +0.0348 |
| Sub-period 1963-2010 | 569 | +0.0355 | +0.0331 |
| Sub-period 2011-2020 | 119 | +0.0302 | +0.0393 |

The correlation is consistently low (~0.03) in both sub-periods, indicating
that the REG-STR gap is structural across the entire sample.
