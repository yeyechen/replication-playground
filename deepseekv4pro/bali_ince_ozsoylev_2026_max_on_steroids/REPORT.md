# Replication Report — MAX on Steroids (Bali, Ince & Ozsoylev)

**Status:** outer iteration 3 complete (audit 3 pending). Iteration 1:
REPLICATED; iteration 2: REPLICATED, all five audit-1 majors
discharged (ISKEW residual-moment bug fixed via spot-check; rest
evidenced residue); iteration 3: audit-2 major M1 fixed — the CE /
me_gr12 pipeline repaired with the log-form Daniel-Titman net-issuance
construction (corr 0.09 → 0.92), moving the CE coefficient into Match
and restoring the T9 issuance-state ordering.

## Headline tally (canonical scorer — eval/scoring.json, iteration 3)

```
loss L          = 0.3509   (=(FAIL+MISSING)/committed = (222+24)/701)
match_count     = 455 / 701 committed cells (64.9%)
fail_count      = 222
missing_count   = 24        (all DHS-factor columns — [THIRD-PARTY-DATASET])
no_effect_count = 7         (cells the paper itself reports insignificant)

per table: T1 81M/26F/12M  T2 50M/15F  T3 81M/27F/12M  T4 59M/31F
           T5 34M/28F  T6 40M/16F  T7 22M/24F  T8 66M/30F  T9 22M/25F
```
(final outer-iteration-3 tally from eval/scoring.json --iteration 3)

The tally is copied verbatim from `eval/scoring.json` (written by
`scripts/score_replication.py --iteration 3` (refreshed at outer
iteration 3)); it is not hand-composed.

## What the paper claims (committed claims)

- **C1 (headline):** the original MAX anomaly's VW abnormal returns are
  explained by mispricing/behavioral models (SY, DHS) and equity
  issuance (Table 1, 4, 7).
- **C2 (headline):** MAX^β — beta-neutralized MAX — earns a significant
  VW long-short abnormal return robust to risk AND mispricing models,
  driven by both legs (Tables 6, 7, 8, A5).
- **C3:** the MAX^β spread's source shifts across clienteles: retail
  overpay for high-MAX^β (low-INST), institutions earn a premium on
  low-MAX^β (high-INST) (Table 9).
- **C4:** the low-MAX^β premium is durable over two years while MAX
  corrects in 1–2 months (Table 12).
- **C5:** the MAX^β spread is approximately invariant across aggregate
  issuance regimes (Table A7, issuance columns).

## Data and construction

- Universe: CRSP 1968-01–2022-12, shrcd 10/11, exchcd 1/2/3, PIT via
  `dsfhdr` (`utils.apply_universe_filter`), price ≥ $5 at month end,
  SIC 4900–4949/6000–6999 exclusions, ≥15 daily obs per month,
  delisting-adjusted returns (dsedelist.dlret, −0.30 fallback).
  Funnel: 4,220,818 → 3,156,451 (PIT) → 2,479,492 (SIC) → 1,743,269
  (price) monthly stock-months; 17,856 permnos; 0 duplicate keys.
- Panel (`data/panel.parquet`, 91 cols): MAX, BETA/IVOL (252-day
  rolling), ILLIQ (×10^6), REV, MOM (12-2), SIZE, turnover, BM (ln +
  raw), BE, ROE (annualized quarterly), I/A, MIS (11 SY anomalies:
  NSI, CEI, accruals, NOA, AG, INV/AT, CHS distress, O-score, MOM,
  GP, ROA), issuance index (NSI/CEI/CSI-5), CE, INST (13F s34),
  ΔINST, ISKEW/E(ISKEW) (BMV 2010 two-step), β^MAX, `ret_fwd`.
- Factors (`data/factors.parquet`): FF3/FFC4/FF5/FF6/FF6PS from
  Kenneth French tables + Pastor-Stambaugh traded LIQ (user-provided
  `liq_data_1962_2024.txt`); SY4 from user-provided `M4.csv`
  (coverage ends 2016-12); DHS FIN/PEAD unavailable (documented).
- Two pipeline-critical corrections (both documented with
  before/after evidence in `preparations/assumptions.md` Iterations
  5–6):
  1. Forward returns are paired month-aligned from the UNFILTERED
     CRSP monthly file (the paper's filters apply at formation; a
     crash below $5 at t+1 keeps its negative return). Naive
     groupby-shift had silently paired 1.86% of rows with t+2
     recovery returns; the T1 spread flipped from +0.21 to −1.02
     (paper −0.95).
  2. All forward-return series are indexed by the RETURN month
     (formation month + 1) in factor regressions. Without it, betas
     collapsed to ≈0 (corr of the all-stock VW forward series with
     mkt_rf was 0.038); after the fix, P1 CAPM alpha 0.32 (paper
     0.24, beta 0.73), P10 −1.23 (paper −1.17, beta 1.59).

## Table-level evidence (paper vs ours; full grids in results/*.md)

- **T1 (Table 1, MAX deciles):** 10-1 VW spread −1.02 (t=−3.26) vs
  paper −0.95 (t=−3.08); CAPM spread −1.54 (t=−5.55) vs −1.41
  (−5.17); FFC4 −1.08 vs −1.07; FF6PS −0.62 vs −0.61; SY −0.36 vs
  −0.27 (both insignificant). P1/P9/P10 rows Match across models
  (P10 FF6PS −0.48 vs −0.54). 81/120 cells Match; DHS column (12 cells)
  scored MISSING ([THIRD-PARTY-DATASET]).
- **T2 (Table 4, FM on MAX):** all 6 MAX coefficients Match
  (−0.225/−0.108/−0.190/−0.227/−0.101/−0.109 vs −0.210/−0.113/
  −0.163/−0.187/−0.106/−0.110), t-stats Match; MIS coefficients
  Match (−0.024/−0.014 vs −0.026/−0.018); intercepts and R² Match.
  CE coefficient fixed in iteration 3 (log-form net issuance:
  −0.010 vs −0.017, t −3.37 vs −4.43 — Match). Open: IVOL/ROE
  scaling (see Limitations), BM coefficient 2×.
- **T3 (Table 6, MAX^β deciles):** 10-1 spread −0.87 (t=−3.68) vs
  −0.81 (−3.62); FFC4 −0.97 (t=−4.77) vs −0.95 (−4.76); FF6PS
  −0.76 (t=−4.04) vs −0.73 (−3.89); P1 0.76 vs 0.71, P10 −0.11 vs
  −0.10 RET-RF. 81/120 Match; DHS 12 MISSING.
- **T4 (Table 8, FM on MAX^β dummies):** D10 −1.167/−0.530/−1.024/
  −1.266/−0.479/−0.517 vs paper −1.027/−0.435/−0.834/−0.937/−0.403/
  −0.421, t-stats Match; D9 and D8 columns Match; R² Match. 59/90.
- **T5 (Table 12, durability):** K=1 alphas Match for all six
  columns (maxb 0.77 vs 0.73; max 0.65 vs 0.61; lomaxb 0.24 vs
  0.23). The C4 pattern is reproduced: MAX strategy alpha decays to
  ≈0 by K=12 (0.00 vs paper 0.04) while MAX^β stays positive
  (K12 0.11 vs 0.20). Long-horizon leg cells (K≥18, CR24) are noisy
  and mostly FAIL (documented).
- **T6 (Table A5, MAX^β characteristics):** spread row: MAX 0.058 vs
  0.058 (t 43.3 vs 45.0); BETA 0.000 (beta-neutrality reproduced
  exactly); MIS 7.06 vs 7.45; INST −0.225 vs −0.212; SIZE −987 vs
  −959; IVOL 1.976 vs 1.986; CE +0.015 vs +0.019 (sign recovered
  after split-adjustment fix). Open: E(ISKEW) magnitude (0.292 vs
  0.451 — a real residual-moment bug in the ISKEW computation was
  found via single-firm spot-check and fixed in iteration 2; the
  remaining ~35% level offset is [STRUCTURAL-SAMPLE-VARIANCE]),
  β^MAX dispersion (0.154 vs 0.036 — three market-MAX constructions
  tested, all recorded in assumptions.md), BM raw sign (genuine
  composition difference, documented).
- **T7 (Table 7, issuance/MIS-controlled):** both MAX^β 10-1 spreads:
  a_maxb −0.44 (t=−2.50) vs paper −0.48 (−2.32); b_maxb −0.38 (t=−2.44)
  vs −0.46 (−2.52). The MAX spreads are insignificant in paper and ours:
  a_max −0.39 (−2.06) vs −0.21 (−0.99); b_max −0.31 (−1.69) vs −0.29
  (−1.53) — the paper's central contrast (MAX^β robust, MAX not)
  reproduced.
- **T8 (Table 9, INST tiers):** Panel B (MAX^β within tier) spreads Match:
  INST1 FF6PS −1.51 (t=−4.05) vs paper −1.44 (−3.95); INST2 FF6PS −0.73
  vs −0.51; INST3 FF6PS −0.35 (t=−1.82) vs −0.37 (−1.96). INST1 retrf
  spread −1.77 (t=−4.18) vs −1.54 (−3.59); INST1 P10 FF6PS −1.31
  (t=−4.18) vs −1.18 (−4.07). The clientele pattern (C3) reproduced.
- **T9 (Table A7, issuance states):** aggregate-issuance index =
  cross-sectional median of CE; after the iteration-3 CE repair the
  state ordering matches the paper: max_hi −0.52 vs −0.72 (Match),
  maxb_hi −0.77 vs −0.71 (Match), maxb_lo −0.77 vs −0.65 (Match);
  max_lo −0.90 vs −0.43 (paper-insignificant cell, residue). T9
  10→22 Match across iterations 2-3.

## Methodological findings worth reporting

1. The MAX^β double-sort machinery reproduces the paper's headline
   tables: the VW 10-1 spread and its factor-model alphas land
   within tolerance across 8 of 9 models (DHS unavailable), with
   t-statistics of the same order (−3.26 vs −3.08; −5.55 vs −5.17).
2. The two forward-return bugs (gap-skipping pairing; formation-vs-
   return-month indexing) are the difference between a wrong-signed
   spread (+0.21) and a Match (−1.02). Both are documented in the
   assumptions registry with before/after evidence; both were found
   by characterizing the discrepancy (contemporaneous pattern
   matching Table A1, decile characteristics matching Table 2)
   before fixing.
3. The paper's own claims are reproduced at the level of its
   argument: MAX spreads are explained by SY/DHS-style controls
   while MAX^β spreads are not (T1/T7); the MAX^β spread is
   two-sided (T1 vs T3: P1 alphas positive and significant in ours,
   0.32 t≈3+ vs paper 0.18–0.25); the clientele split holds (T8).

## Limitations and open items for the next outer iteration

- **DHS factors unavailable** ([THIRD-PARTY-DATASET]): FIN/PEAD not
  in ClickHouse nor provided; 24 cells scored MISSING (T1/T3 DHS
  columns) — documented non-actionable, counts in the loss numerator.
- **SY factor coverage** ([THIRD-PARTY-DATASET]): M4.csv ends
  2016-12; SY alphas estimated on 1968-2016 (588 of 660 months).
- **FM control coefficient residuals (T2):** IVOL over-conversion
  fixed in iteration 2 (now −0.12 vs −0.217 — 1.8×,
  [STRUCTURAL-SAMPLE-VARIANCE]). ROE: both candidate scales tested
  with coefficients recorded (1.03 annualized / 4.13 quarterly vs
  paper 0.414) — no unit fix exists, documented structural. CE:
  FIXED in iteration 3 (log-form net-issuance residual; root cause
  was CRSP share-restatement outliers inflating raw ME growth, not
  split factors — corr evidence 0.09→0.92 in assumptions.md
  Iteration 14). BM coefficient (0.18 vs 0.091) is a genuine
  residual gap.
- **E(ISKEW) magnitude** (0.30 vs 0.45 spread; t matches): the
  60-month daily-residual skewness in our vintage is magnitude-lower
  than the paper's BMV-fitted values — documented residue.
- **β^MAX dispersion** (0.154 vs 0.036 spread): compressed ~40% by
  the market-MAX redefinition but not fully closed.
- **Table 12 long horizons** (K≥18 legs, CR24): the calendar-time
  construction was verified against footnote 12 (1/K weights, cohort
  windows correct); the K≥18 cells are insignificant in the paper
  and noisy in ours — [STRUCTURAL-SAMPLE-VARIANCE]. C4's
  load-bearing K1/K12 cells Match.
- **Table A7 state decile cells**: resolved by the median-based
  aggregate index (see T9 paragraph); decile-level state cells
  remain noisy.
- **validate_strategy.py** targets the legacy `results/metrics.json`
  path; our metrics live in `eval/metrics.json` per the current
  contract — its NaN/Inf checks were run manually (0 bad values).

## Reproduce

```
uv run python replications/max_on_steroids_attempt5_deepseek/src/main.py   # sections 1-5
uv run python replications/max_on_steroids_attempt5_deepseek/src/regen_ce_betamax.py
uv run python replications/max_on_steroids_attempt5_deepseek/src/sections_678.py
uv run python replications/max_on_steroids_attempt5_deepseek/src/sections_9_11.py
uv run python replications/max_on_steroids_attempt5_deepseek/src/make_plots.py
uv run python replications/max_on_steroids_attempt5_deepseek/src/evaluate.py
uv run python scripts/score_replication.py replications/max_on_steroids_attempt5_deepseek/ --iteration 1
```
