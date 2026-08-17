# Table 1 — MAX Decile Portfolios: VW Excess Returns and Factor Alphas

Sample: 1968-01 to 2022-12 (660 months). Independent decile sorts by MAX. VW by prior-month ME. Newey-West t-stats with 6 lags in parentheses.

| Portfolio | RET-RF | CAPM | FF3 | FFC4 | FF5 | FF6 |
|---|---|---|---|---|---|---|
| P1 | 0.76<br>(4.84) | 0.38<br>(2.25) | 0.41<br>(2.37) | 0.44<br>(2.50) | 0.41<br>(2.41) | 0.43<br>(2.51) |
| P2 | 0.68<br>(3.82) | 0.28<br>(1.52) | 0.31<br>(1.71) | 0.39<br>(2.10) | 0.32<br>(1.74) | 0.39<br>(2.05) |
| P3 | 0.66<br>(3.80) | 0.28<br>(1.53) | 0.33<br>(1.80) | 0.37<br>(1.98) | 0.39<br>(2.11) | 0.42<br>(2.24) |
| P4 | 0.73<br>(3.93) | 0.35<br>(1.81) | 0.37<br>(1.95) | 0.43<br>(2.19) | 0.39<br>(1.98) | 0.44<br>(2.16) |
| P5 | 0.71<br>(3.67) | 0.33<br>(1.61) | 0.36<br>(1.76) | 0.42<br>(1.99) | 0.43<br>(2.13) | 0.48<br>(2.26) |
| P6 | 0.51<br>(2.36) | 0.13<br>(0.57) | 0.15<br>(0.71) | 0.21<br>(0.94) | 0.20<br>(0.90) | 0.25<br>(1.06) |
| P7 | 0.64<br>(2.67) | 0.23<br>(0.98) | 0.29<br>(1.22) | 0.37<br>(1.51) | 0.37<br>(1.52) | 0.42<br>(1.70) |
| P8 | 0.65<br>(2.61) | 0.24<br>(0.97) | 0.30<br>(1.22) | 0.34<br>(1.28) | 0.35<br>(1.38) | 0.38<br>(1.40) |
| P9 | 0.55<br>(1.93) | 0.13<br>(0.45) | 0.22<br>(0.84) | 0.33<br>(1.16) | 0.45<br>(1.65) | 0.52<br>(1.78) |
| P10 | 0.40<br>(1.17) | -0.04<br>(-0.13) | 0.05<br>(0.15) | 0.12<br>(0.32) | 0.22<br>(0.65) | 0.26<br>(0.69) |
| 10-1 | -0.36<br>(-1.33) | -0.43<br>(-2.98) | -0.36<br>(-2.77) | -0.32<br>(-2.25) | -0.19<br>(-2.04) | -0.17<br>(-1.71) |

## Notes
- RET-RF column = time-series mean of value-weighted excess returns (no factor regression).
- All alphas in %/month.  Skipped models (per assumptions.md): SY, DHS, FFCPS, FF6PS (third-party / missing factors).
- `*_SY` and `*_DHS` cells: SKIP (Stambaugh-Yuan / DHS factors not in ClickHouse).
- `*_FFCPS` and `*_FF6PS` cells: SKIP (Pastor-Stambaugh LIQ not in ClickHouse).