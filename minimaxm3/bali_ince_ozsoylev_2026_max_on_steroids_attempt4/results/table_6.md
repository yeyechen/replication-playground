# Table 6 — MAX^beta Decile Portfolios: VW Excess Returns and Factor Alphas

Sample: 1968-01 to 2022-12. Conditional 10x10 sort (BETA, then MAX). VW by prior-month ME. Newey-West t-stats with 6 lags.

MAX^beta construction (paper section 3.2): stocks first sorted into 10 BETA deciles each month, then within each BETA decile sorted into 10 MAX deciles. The 10 MAX^beta deciles are the regrouping of stocks by their inner MAX decile rank across the 10 BETA deciles.

| Portfolio | RET-RF | CAPM | FF3 | FFC4 | FF5 | FF6 |
|---|---|---|---|---|---|---|
| P1 | 0.73<br>(3.83) | 0.35<br>(1.72) | 0.39<br>(1.92) | 0.40<br>(1.79) | 0.43<br>(2.08) | 0.43<br>(1.95) |
| P2 | 0.60<br>(3.36) | 0.22<br>(1.17) | 0.25<br>(1.32) | 0.27<br>(1.36) | 0.30<br>(1.56) | 0.31<br>(1.55) |
| P3 | 0.62<br>(3.27) | 0.24<br>(1.20) | 0.29<br>(1.50) | 0.32<br>(1.56) | 0.35<br>(1.80) | 0.37<br>(1.81) |
| P4 | 0.67<br>(3.41) | 0.28<br>(1.40) | 0.32<br>(1.63) | 0.37<br>(1.73) | 0.36<br>(1.74) | 0.39<br>(1.79) |
| P5 | 0.56<br>(2.70) | 0.15<br>(0.71) | 0.19<br>(0.91) | 0.27<br>(1.22) | 0.30<br>(1.43) | 0.36<br>(1.62) |
| P6 | 0.53<br>(2.45) | 0.13<br>(0.59) | 0.16<br>(0.73) | 0.20<br>(0.85) | 0.25<br>(1.15) | 0.27<br>(1.17) |
| P7 | 0.62<br>(2.63) | 0.20<br>(0.85) | 0.24<br>(1.05) | 0.28<br>(1.08) | 0.33<br>(1.40) | 0.35<br>(1.34) |
| P8 | 0.54<br>(2.11) | 0.13<br>(0.50) | 0.16<br>(0.65) | 0.22<br>(0.79) | 0.26<br>(0.98) | 0.30<br>(1.02) |
| P9 | 0.35<br>(1.26) | -0.07<br>(-0.27) | -0.03<br>(-0.10) | 0.05<br>(0.17) | 0.07<br>(0.26) | 0.13<br>(0.41) |
| P10 | 0.29<br>(0.88) | -0.12<br>(-0.35) | 0.02<br>(0.05) | 0.10<br>(0.27) | 0.19<br>(0.56) | 0.24<br>(0.67) |
| 10-1 | -0.43<br>(-1.76) | -0.47<br>(-3.23) | -0.38<br>(-2.75) | -0.30<br>(-2.32) | -0.24<br>(-2.29) | -0.19<br>(-2.01) |

## Notes
- RET-RF column = time-series mean of value-weighted excess returns (no factor regression).
- All alphas in %/month.  Skipped models (per assumptions.md): SY, DHS, FFCPS, FF6PS (third-party / missing factors).