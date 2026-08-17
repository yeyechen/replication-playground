# Table 4 — Weber (2018) robustness (ours vs paper)

| Row | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D1D10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| t4_r010 | 1.575 vs 1.450 | 1.245 vs 1.230 | 1.174 vs 1.130 | 1.071 vs 1.060 | 0.959 vs 1.000 | 0.945 vs 0.950 | 0.730 vs 0.810 | 0.610 vs 0.680 | 0.511 vs 0.660 | 0.391 vs 0.280 | 1.184 vs 1.170 |
| t4_r014 | 1.565 vs 1.420 | 1.267 vs 1.240 | 1.143 vs 1.130 | 1.062 vs 1.030 | 0.992 vs 1.040 | 0.928 vs 0.940 | 0.716 vs 0.840 | 0.594 vs 0.640 | 0.456 vs 0.650 | 0.494 vs 0.330 | 1.071 vs 1.100 |
| t4_ar_roe_030 | 1.579 vs 1.480 | 1.284 vs 1.210 | 1.166 vs 1.130 | 1.115 vs 1.120 | 0.985 vs 0.980 | 0.946 vs 0.970 | 0.734 vs 0.800 | 0.642 vs 0.730 | 0.456 vs 0.560 | 0.301 vs 0.250 | 1.278 vs 1.230 |
| t4_ar_roe_050 | 1.517 vs 1.340 | 1.270 vs 1.300 | 1.146 vs 1.100 | 1.026 vs 1.060 | 0.968 vs 0.970 | 0.896 vs 0.950 | 0.704 vs 0.820 | 0.594 vs 0.650 | 0.486 vs 0.660 | 0.624 vs 0.420 | 0.893 vs 0.930 |
| t4_roe_ss_010 | 1.544 vs 1.400 | 1.272 vs 1.270 | 1.150 vs 1.120 | 1.051 vs 1.040 | 0.957 vs 1.010 | 0.882 vs 0.960 | 0.725 vs 0.810 | 0.600 vs 0.670 | 0.456 vs 0.610 | 0.589 vs 0.360 | 0.955 vs 1.040 |
| t4_roe_ss_014 | 1.573 vs 1.450 | 1.268 vs 1.240 | 1.157 vs 1.110 | 1.077 vs 1.080 | 0.988 vs 0.990 | 0.922 vs 0.950 | 0.738 vs 0.820 | 0.639 vs 0.700 | 0.517 vs 0.650 | 0.329 vs 0.260 | 1.243 vs 1.180 |
| t4_ar_sg_020 | 1.564 vs 1.420 | 1.245 vs 1.250 | 1.185 vs 1.140 | 1.031 vs 1.020 | 0.984 vs 1.010 | 0.922 vs 0.950 | 0.722 vs 0.800 | 0.604 vs 0.700 | 0.494 vs 0.630 | 0.465 vs 0.330 | 1.099 vs 1.090 |
| t4_ar_sg_030 | 1.585 vs 1.450 | 1.244 vs 1.220 | 1.166 vs 1.130 | 1.080 vs 1.070 | 0.997 vs 1.030 | 0.942 vs 0.970 | 0.715 vs 0.810 | 0.606 vs 0.670 | 0.433 vs 0.590 | 0.448 vs 0.300 | 1.138 vs 1.150 |
| t4_sg_ss_008 | 1.546 vs 1.440 | 1.267 vs 1.230 | 1.154 vs 1.130 | 1.057 vs 1.070 | 0.953 vs 0.980 | 0.900 vs 0.960 | 0.713 vs 0.810 | 0.619 vs 0.710 | 0.453 vs 0.640 | 0.560 vs 0.260 | 0.986 vs 1.180 |
| t4_sg_ss_004 | 1.565 vs 1.400 | 1.259 vs 1.250 | 1.166 vs 1.150 | 1.087 vs 1.040 | 0.968 vs 0.970 | 0.941 vs 0.960 | 0.724 vs 0.820 | 0.648 vs 0.670 | 0.497 vs 0.620 | 0.353 vs 0.390 | 1.211 vs 1.010 |
| t4_horizon_10 | 1.552 vs 1.390 | 1.264 vs 1.260 | 1.161 vs 1.120 | 1.036 vs 1.070 | 0.985 vs 0.960 | 0.920 vs 0.940 | 0.707 vs 0.830 | 0.615 vs 0.670 | 0.451 vs 0.600 | 0.530 vs 0.410 | 1.022 vs 0.980 |
| t4_preest | 1.390 vs 1.360 | 1.187 vs 1.180 | 1.105 vs 1.050 | 0.995 vs 0.980 | 0.917 vs 0.960 | 0.819 vs 0.900 | 0.672 vs 0.740 | 0.576 vs 0.610 | 0.663 vs 0.590 | 0.931 vs 0.140 | 0.459 vs 1.210 |

Format: `ours vs paper` per cell.

---

## Pre-estimation row (t4_preest) — procedure note

The pre-estimation row estimates the AR(1) persistence parameters `ar_roe`
and `ar_sg` out-of-sample per sort year t via a Fama-MacBeth-style estimator:
for each fiscal year `y` with `fyear <= t-2` (out-of-sample w.r.t. the June-t
sort), run the cross-sectional regression `ROE_{i,y} = a + b*ROE_{i,y-1} + e`
(and analogously for sales-growth persistence `g`), then take the simple mean
of the annual b's over all such years. The duration recursion then uses these
per-sort-year coefficients (other parameters at baseline). This replaces a
pooled expanding-window AR(1) no-intercept estimator that recovered
`ar_roe ≈ 0.62` (vs the paper's full-sample 0.4067) and produced a preest
spread of 0.375 vs the paper's 1.21. The FM-mean estimator is the standard
robust cross-sectional aggregator and is the committed variant.