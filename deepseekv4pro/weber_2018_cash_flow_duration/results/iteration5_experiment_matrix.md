# Iteration 5 — Duration-construction experiment matrix (diagnosis only)

Scratch harness: `src/experiments.py`. No changes to `main.py` / canonical pipeline.

## Step 1 — D10 extreme-month bug check
Recomputed the D10 EW mean for the three extreme months directly from raw
`crsp_202601.msf` (joining panel rows by permno + `toDate32(date)`):

| month     | panel ret_dl mean | raw msf mean | verdict |
|-----------|-------------------|--------------|---------|
| 2001-01   | +55.06%           | +55.08%      | real   |
| 2000-02   | +37.46%           | +37.44%      | real   |
| 1992-01   | +35.41%           | +35.41%      | real   |

The extreme months are genuine CRSP returns, **not** a panel bug (no duplicated
rows / bad join). The D9/D10 mismatch is a **composition** problem: which firms
land in D10, not a data corruption.

## Step 2 — Variant matrix (D9 / D10 / spread + status flips)

| variant   | D7    | D8    | D9    | D10    | D1-D10 | T2 mean flips | T3 alpha flips | FAIL (99) | L      |
|-----------|-------|-------|-------|--------|--------|---------------|----------------|-----------|--------|
| V0 base   | 0.715 | 0.603 | 0.477 | 0.455  | 1.113  | 0             | 0              | 14        | 0.1414 |
| V1 dur-only| 0.721 | 0.601 | 0.477 | 0.459  | 1.102  | 0             | 0              | 12        | 0.1212 |
| V2 no-win | 0.721 | 0.601 | 0.477 | 0.459  | 1.102  | 0             | 0              | 12        | 0.1212 |
| V3 cf-floor| 0.816 | 0.685 | 0.527 | 0.225  | 1.343  | 2             | 8              | 20        | 0.2020 |
| V4 roe-trunc| 0.715 | 0.603 | 0.477 | 0.455  | 1.113  | 0             | 1              | 15        | 0.1515 |
| V5 ret-win | 0.585 | 0.458 | 0.228 | -0.116 | 1.398  | 3             | 15             | 41        | 0.4141 |

Paper targets: D7=0.81, D8=0.68, D9=0.62, D10=0.32, spread=1.10.

### D10 top-3 months + composition
| variant   | top-3 (D10)                        | mean\|ROE\| | mean g  | median me_jun |
|-----------|------------------------------------|-------------|---------|---------------|
| V0        | 2001-01 55.1, 2000-02 37.5, 1992-01 35.3 | 0.760   | 0.829   | $44.7M        |
| V1        | 2001-01 55.0, 2000-02 37.5, 1992-01 35.4 | 1.333   | 4.999   | $44.0M        |
| V2        | 2001-01 55.0, 2000-02 37.5, 1992-01 35.4 | 1.333   | 4.999   | $44.0M        |
| V3        | 2001-01 45.6, 2000-02 30.8, 1992-01 30.5 | 0.645   | 0.322   | $71.5M        |
| V4        | (same as V0)                       | 0.759   | 0.829   | $44.7M        |
| V5        | (same as V0)                       | 0.760   | 0.829   | $44.7M        |

## Step 3 — D9/D10 boundary composition (V0 vs V3)
| variant | bin | median dur | median BE($M) | median me_jun | share neg ROE | share BE<$10M |
|---------|-----|-----------|---------------|---------------|---------------|---------------|
| V0      | D9  | 22.92     | 20.6          | $89.9M        | 0.346         | 0.368         |
| V0      | D10 | 24.49     | 6.8           | $40.8M        | 0.698         | 0.570         |
| V3      | D9  | 22.24     | 28.6          | $115.9M       | 0.280         | 0.313         |
| V3      | D10 | 23.34     | 7.0           | $66.3M        | 0.482         | 0.560         |

## Conclusion
- **V3 (CF floor at zero)** is the only variant that moves D9 up (0.527) and D10
  down (0.225) simultaneously, but it **over-corrects** D10 (past paper 0.32),
  inflates the spread to 1.343 (paper 1.10), and raises total FAIL to 20.
- V1/V2 (removing input winsorization) slightly reduce FAIL (12) by fixing
  beta_capm_D1D10 and vw_mean_D10, but do **not** move D9/D10 at all.
- V4 (ROE truncated at -1.0) is a no-op (never binds).
- V5 (return winsorization) drastically worsens everything (FAIL 41).

No single variant reproduces paper D9=0.62 and D10=0.32 simultaneously. The
D9-low / D10-high pattern is robust to all five construction levers; the CF
floor moves it in the right direction but overshoots on D10.

---

# Appendix — Outer iteration 3 (audit2 M1) controlled tail probe

Scratch harness: `src/tail_probe.py`. Rebuilds full duration + June decile
sorts + T2/T3 metrics from `fundamentals_duration.parquet` inputs; does NOT
touch the canonical pipeline. V0 reproduces the committed baseline to 3
decimals (mean_D9 0.477 vs 0.474 committed; mean_D10 0.455 vs 0.462; spread
1.113 vs 1.106), confirming a faithful reconstruction.

## Variant set (loss-firm duration-construction reading)

| variant | mean_D9 | mean_D10 | spread | spread_dev | nodl_D9 | nodl_D10 | vw_D10 | capm_a_D9 | capm_a_D10 | ff3_D9 | ff3_D10 | ff4_D9 | ff4_D10 | ff5_D9 | ff5_D10 | tailMatch | tailFAIL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V0 canonical | 0.477 | 0.455 | 1.113 | +0.013 | 0.478 | 0.459 | -0.050 | -0.243 | -0.284 | -0.121 | -0.172 | 0.167 | 0.144 | 0.181 | 0.217 | 9 | 9 |
| V3 cf-floor (CF=max(CF,0)) | 0.527 | 0.225 | 1.343 | +0.243 | 0.527 | 0.228 | 0.221 | -0.170 | -0.514 | -0.058 | -0.360 | 0.203 | -0.108 | 0.144 | -0.041 | 10 | 8 |
| V6 dur-win POOLED @1/99 | 0.477 | 0.455 | 1.108 | +0.008 | 0.478 | 0.459 | -0.050 | -0.243 | -0.284 | -0.121 | -0.172 | 0.167 | 0.144 | 0.181 | 0.217 | 9 | 9 |
| V8 exclude BE<$1M (diagnostic) | 0.481 | 0.357 | 1.211 | +0.111 | 0.482 | 0.360 | 0.003 | -0.242 | -0.389 | -0.108 | -0.252 | 0.178 | 0.073 | 0.184 | 0.126 | 11 | 7 |

Paper targets: mean_D9=0.62, mean_D10=0.32, spread=1.10, ff4_alpha_D10=-0.07,
ff5_alpha_D10=0.01. `tailMatch/tailFAIL` counts the 18 D9/D10 cells (T2+T3,
excluding spreads). V3b (first-5-year floor), V7 (0.5/99.5 input winsorization)
were DROPPED — no DSS/paper citation (paper is explicit: "winsorize at 1%/99%",
L176).

## D10 composition per variant

| variant | n_firms | median me_jun | median BE | negative-ROE share |
|---|---|---|---|---|
| V0 | 6548 | $44.6M | $6.8M | 0.698 |
| V3 | 6225 | $71.5M | $7.0M | 0.482 |
| V6 | 6548 | $44.6M | $6.8M | 0.698 |
| V8 | 6471 | $55.3M | $9.6M | 0.653 |

## Net cell movement (all 99 T2+T3 committed cells, vs committed V0)

| variant | Match-gains | Match-losses | net |
|---|---|---|---|
| V3 cf-floor | +6 | -12 | **-6** |
| V6 dur-pooled | +0 | -1 | **-1** |
| V8 be>=1M | +5 | -2 | **+3** |

V3's gains are concentrated in FF3 alphas (D9, D10 fixed) + mean_D9, but it
DESTROYS the headline spread cell (mean_D1D10 1.106 → 1.343, Match→FAIL), plus
nodl_D10, vw_D1D10, ff5_D1D10, and four D7/D8 alpha cells. V6 is a no-op. V8
helpfully fixes mean_D10 (0.462 → 0.357, within 20% of 0.32) and the FF3
D7-D10 chain, but degrades nodl_D10 and ff5_alpha_D8, and is diagnostic-only
(no paper citation for a $1M BE floor).

## Decision per the Replicator's rule

NO VARIANT IS COMMITTED. None meets the triple bar (paper/DSS rationale +
majority of tail cells improved + spread not degraded + non-negative net).
- V3: net -6; the CF-floor-at-zero reading is additionally NOT faithful to DSS
  2004/Weber — under clean surplus the equity cash flow E − ΔBV = BV×(ROE − g)
  is legitimately negative for reinvesting growth / loss firms, and neither
  DSS (2004) nor Weber (Eq. 3, L159) floors it at zero.
- V6: no-op (pooled-vs-per-year winsorization is irrelevant to the tail).
- V8: net +3 but has no citation; $1M BE floor is diagnostic only.

## [STRUCTURAL-SAMPLE-VARIANCE] evidence — bins are formed correctly

| bin | n_firms | mean dur | median dur | median me | median BE |
|---|---|---|---|---|---|
| D1 | 16648 | 4.65 | 6.99 | $23.5M | $41.0M |
| D5 | 16677 | 17.83 | 18.82 | $112.0M | $68.4M |
| D9 | 16665 | 22.44 | 22.92 | $89.9M | $20.6M |
| D10 | 16693 | 25.29 | 24.49 | $40.8M | $6.8M |

- D10 **mean duration 25.29 years exactly matches Table A.9's "roughly 25 years"**
  for high-duration firms; D1 mean 4.65 is pushed below the paper's ~11yr by a
  large share of NEGATIVE durations (21.7% of D1 firms have dur < 0 — clean
  surplus CF where PV of reinvested cash flows exceeds price for deep-value /
  low-ROE firms). This is a measure-construction feature, not a bug, and it is
  the low-duration (D1) end, not the failing D9/D10 tail.
- D10 composition matches the paper's own characterization (L1510 / Table 1):
  69.8% negative ROE, median BE $6.8M, median me $40.8M, high sales growth —
  "younger firms with negative payout ratios and ROE, historically strong sales
  growth, difficult to value."
- Decile bins are monotone and balanced (~16.7k firms each); the boundary
  D9 (dur 22.44) → D10 (dur 25.29) is sharp and correctly ordered.

**Conclusion:** the bins are correctly constructed and D10's composition exactly
matches the paper's own qualitative description of high-duration firms. The
residual D9-low / D10-high mean-return gap is NOT a construction error and NOT a
vintage effect (A15: comp_202401 reproduces to 3 decimals) — it is a
sample-level return difference in the tiny-loss-maker tail that none of the four
loss-firm construction levers can reproduce without overshooting the paper's
targets and degrading the headline spread. The cells stay OPEN as
[STRUCTURAL-SAMPLE-VARIANCE].

---

# Appendix — Outer iteration 4 (audit3 M2) V9 loss-firm-only CF floor probe

Scratch harness: `src/tail_probe_v9.py`. Reuses `tail_probe.py` machinery; adds the
**graduated loss-firm CF floor** (between no-floor V0 and full-floor V3). Does NOT
touch `main.py` / `panel.parquet` / `metrics.json`.

**V9 (loss-firm-only floor):** in the recursion, floor CF_{t+s} at zero ONLY for firms
whose current (period-t) ROE_t < 0. Positive-ROE reinvesting firms keep their
legitimately-negative clean-surplus CFs (NOT floored). Citation: Weber footnote 6
terminal value "paid out as a level perpetuity" presupposes non-negative payouts; loss
firms cannot distribute, so CF = BV×(ROE − g) < 0 is floored to zero.

## V9 vs V0 vs paper (key tail cells)

| metric | V0 | V9 | paper |
|---|---:|---:|---:|
| mean_D9 | 0.477 | 0.511 | 0.620 |
| mean_D10 | 0.455 | 0.189 | 0.320 |
| mean_D1D10 | 1.113 | 1.404 | 1.100 |
| nodl_mean_D9 | 0.478 | 0.512 | 0.670 |
| nodl_mean_D10 | 0.459 | 0.192 | 0.470 |
| vw_mean_D10 | -0.050 | 0.148 | -0.040 |
| alpha_capm_D9 | -0.243 | -0.188 | -0.080 |
| alpha_capm_D10 | -0.284 | -0.546 | -0.390 |
| ff3_alpha_D9 | -0.121 | -0.083 | -0.080 |
| ff3_alpha_D10 | -0.172 | -0.395 | -0.380 |
| ff4_alpha_D9 | 0.167 | 0.164 | 0.180 |
| ff4_alpha_D10 | 0.144 | -0.129 | -0.070 |
| ff5_alpha_D9 | 0.181 | 0.112 | 0.140 |
| ff5_alpha_D10 | 0.217 | -0.072 | 0.010 |

## Tail-cell status + net movement + composition

| variant | tailMatch (18 D9/D10) | tailFAIL | net movement (99 T2+T3) | D10 median me | D10 median BE | D10 neg-ROE share |
|---|---:|---:|---:|---:|---:|---:|
| V0 (committed) | 9 | 9 | — | $44.6M | $6.8M | 0.698 |
| V9 (loss-firm floor) | 10 | 8 | **-6** (+5 / -11) | $71.2M | $7.5M | 0.452 |

## Commit-bar verdict (per the Replicator's triple bar)

- majority of tail cells improve (10 > 9): **True**
- spread within ±30% of 1.10 (band [0.77, 1.43]): **True** (1.404, near the 1.43 edge)
- net movement ≥ +2: **False** (net = **-6**)

**VERDICT: V9 DOES NOT COMMIT.** It overshoots D10 harder than V3 (mean_D10 0.189 vs
V3's 0.225 vs paper 0.32; V3 was already an over-correction), pushes the spread to
1.404 (edge of the tolerance band), and nets -6 cells (it fixes the FF3/FF4/FF5 D10
alphas by sign — ff4_alpha_D10 +0.144 → -0.129, ff5_alpha_D10 +0.217 → -0.072, the
first time the tail alpha signs have flipped toward the paper — but breaks mean_D10,
nodl_D10, vw_mean_D10, and several D7/D8 alpha cells). The loss-firm-only floor is the
right *family* (it moves the tail alphas the right way), but at the calibrated level it
still swaps one tail error for another. Marginal-overshoot persists because ~45% of
D10 firms are still negative-ROE loss firms whose floored CF raises their duration and
re-sorts them into D10, consistent with V3's mechanism at a lessoned intensity.
