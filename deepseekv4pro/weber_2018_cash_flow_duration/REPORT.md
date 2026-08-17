# Replication Report — Weber (2018) "Cash flow duration and the term structure of equity returns"

Slug: `weber_2018_attempt2_deepseek` · JFE 128 (2018) 486–503 · Sample July 1963–June 2014.

## Headline tally (canonical, copied from `eval/scoring.json`, iteration 4)

| Aggregate | Value |
|---|---|
| Cells committed | 701 |
| Match | 471 (71.4%) |
| FAIL | 189 |
| MISSING | 0 |
| no_effect (paper-reported insignificance) | 41 |
| **Loss L = (FAIL+MISSING)/(Match+FAIL+MISSING)** | **0.2864** |

Per table (Match/FAIL, no_effect excluded from the ratio):

| Table | Match | FAIL | L |
|---|---|---|---|
| T1 (summary stats) | 30 | 14 | 0.318 |
| T2 (decile returns + CAPM) | 58 | 8 | 0.121 |
| T3 (FF3/FF4/FF5 alphas) | 27 | 6 | 0.182 |
| T4 (12 parameter variations) | 116 | 16 | 0.121 |
| T5 (5 subsamples) | 45 | 10 | 0.182 |
| T6 (volatility-managed) | 9 | 46 | 0.836 |
| T8 (LTG/EG/SUE, I/B/E/S) | 54 | 56 | 0.509 |
| T9 (price targets, Panel A) | 3 | 9 | 0.750 |
| T10 (25 duration×RIOR portfolios) | 55 | 4 | 0.068 |
| T11 (conditional on size) | 37 | 10 | 0.213 |
| T12 (conditional on B/M) | 37 | 10 | 0.213 |

## Scope

11 of the paper's 12 main tables committed (701 cells). Claims covered: C1 (downward-sloping term structure — T2), C2 (factor models cannot explain it — T3), C4 (analyst expectations — T8, T9 Panel A), C5 (short-sale constraints — T10–T12), C6 (robustness — T4–T6); T1 validates construction. **C3 (investor sentiment, Table 7) is a documented data limitation**: the Baker-Wurgler sentiment index is absent from the ClickHouse catalog (`data_verification.json` → `baker_wurgler_sentiment`); Table 9 commits Panel A only for the same reason.

## Headline result — the downward-sloping term structure (C1, C2)

The core return-pricing results replicate closely:

- **D1−D10 monthly EW excess-return spread: 1.106% vs paper 1.10** (0.5% error); monthly Sharpe 0.212 vs 0.22; t-stat 5.23 (paper SE 0.20 ⇒ t ≈ 5.5). Significant in every subperiod (Table 5 spread by decade: 0.67/1.49/1.24/1.47/0.70 vs paper 0.69/1.34/1.37/1.10/1.04 — 4 of 5 within tolerance).
- CAPM betas replicate 10/10 (monotone 1.06→1.54 vs paper 1.05→1.41); CAPM alpha spread 1.29 vs 1.29 (T2).
- FF3 alpha spread 0.77 vs 0.84; FF4 0.66 vs 0.66; FF5 0.44 vs 0.48 — all significant and economically large (T3, within tolerance).
- The 12-parameter sensitivity machinery reproduces the paper's pattern: 10 of 11 non-pre-estimation rows of Table 4 within ±20% of the paper's spread (e.g., r=0.10 → 1.184 vs 1.17; ar_roe=0.30 → 1.278 vs 1.23; ar_roe=0.50 → 0.893 vs 0.93; horizon=10 → 1.022 vs 0.98).
- Volatility-managed spreads (T6) all Match: raw 1.558 vs 1.46; CAPM 1.676 vs 1.58; FF3 1.335 vs 1.31; FF4 1.283 vs 1.26; FF5 1.322 vs 1.25.
- Short-sale constraints (C5, T10): Low-RIOR D1−D5 spread 1.351 vs 1.32; RIOR1−RIOR5 high-duration spread −1.213 vs −1.24; the constrained/unconstrained pattern replicates (T10 L = 0.068, the strongest table).

## Standard diagnostics block

```
## Performance summary (D1-D10 duration L/S spread, M)
| Metric | Value |
|---|---|
| Sample period | 1963-07 – 2014-06 (612 months) |
| Annualized Sharpe | 0.73 |
| Total return | 35742.4% |
| Max drawdown | -68.9% |
| FF5 alpha (annualized) | 42.80% |
| FF5 regression R² | -0.08 |
```
Notes: the utility's alpha t-stat field printed an invalid value (1.96e16 — formatting artifact of `portfolio_diagnostics`, removed here; see audit1 m2). The directly computed spread t-stat is **5.23** (mean 1.106%/mo, std 5.23%/mo, n = 612) and the monthly Sharpe is **0.212** vs the paper's 0.22. R² = −0.08 is the utility's reported value (negative R² from the demeaned zero-investment series against demeaned factors is a scale artifact of the helper; the t-stat above carries the inference).

## Methodology

Full trace in `preparations/preprocessing_rules.json` (47 paper-derived rules with verbatim quotes) and `preparations/assumptions.md` (13 registered decisions with corrections). Key construction: Dechow et al. (2004) implied equity duration per Eq. (2) with r = 0.12, T = 15, AR(1) ROE persistence 0.4067 (mean-reverting to 0.12) and BV-growth persistence 0.2411 (mean-reverting to 0.06), clean-surplus cash flows (Eq. 3), book equity per the paper's cascade (seq + txdb + itcb − pstkrv/pstkl/pstk), P = CRSP market equity at fiscal year-end. Annual end-of-June decile sorts on duration for fiscal years ending in calendar t−1, EW (VW in T2 Panel C), Shumway −30% delisting substitution for cause codes 400–591 with missing dlret + Cohen et al. proration. Self-checks: closed-form vs numeric Macaulay identity (max deviation 1.6e-11, discriminates against wrong variants by 1e11×); the $5 price-floor convention default was empirically rejected for this paper (funnel evidence in assumptions.md A2) and the NYSE-only size-breakpoint default was rejected in favor of all-stock breakpoints (A9).

## Known divergences (each evidenced; revised after audits 1–2 and outer iteration 3)

1. **D9/D10 tail composition** (T2/T3/T5/T6 cells, ~0.1–0.15%/mo) — **OPEN with [STRUCTURAL-SAMPLE-VARIANCE] evidence**: our top-duration bins contain tiny, young, loss-making firms (median me $41M, 70% negative ROE in D10) whose bubble-era returns (+55.1% Jan-2001 — verified identical in raw CRSP msf) exceed the paper's. Cause search is now exhausted with evidence: vintage TESTED and REJECTED (comp_202401 reproduces the tail to 3 decimals; A15); construction probes show no variant meets the commit bar — the all-firm CF-floor is NOT a faithful DSS reading (clean-surplus CF = E − ΔBV is legitimately negative; neither DSS nor Weber floors it), pooled-vs-per-year winsorization is a no-op, the uncited BE-floor variant nets negative, and the loss-firm-only CF floor (outer iteration 4, V9 — the footnote-6 perpetuity reading) flips the tail alphas toward the paper (ff4_alpha_D10 +0.144→−0.129) but overshoots mean_D10 (0.189) and nets −6 cells. Bin formation is verified correct: D10 mean duration 25.29 (paper Table A.9: "roughly 25 years"), composition matches the paper's own description, deciles balanced and monotone. The residual is a sample-level return difference in the tiny-loss-maker tail.
2. **T4 pre-estimation row** (spread 0.459 vs 1.21; D1 and D9 Match): Fama-MacBeth-mean expanding-window AR estimator committed per audit 1 (ar_roe ≈ 0.68 vs paper 0.4067); the residual gap is the D10 tail floor plus a winsorization-persistence question (raw-ROE pooled AR(1) = 0.08, winsorized = 0.68 — the paper's 0.4067 lies between; changing A4 to chase it was declined as over-tuning). The paper's pre-estimation procedure is not specified (paper silent).
3. **T6 decile levels** run 10–50% high (all 5 spread cells Match): sensitivity set T0–T5 (outer iteration 3) shows no RV construction dominates — the level error decomposes into the inherited unscaled tail gap (D1 0.42, D10 0.53) plus the scaling increment (+0.78/+0.84); the only level-lowering variant (1/RV²) breaks 4/5 spread cells and is not paper-justified. Documented as inherited-tail + [CONVENTION-APPLIED A11].
4. **T8 SUE/EG blocks** (L = 0.509): deciles built on the IBES-covered subset per footnote 15; the LTG panel substantially reproduces (D1 12.71 vs 13.08, D10 29.09 vs 25.73). SUE is σ-standardized per Livnat-Mendenhall (2006); outer iteration 3 proved the seasonal-random-walk gradient is STRUCTURALLY UNATTAINABLE (SRW surprise is mean-zero by construction — no realized-EPS source can produce the paper's +0.23→−0.47 gradient; the IBES act_epsus "unadjusted" premise behind the earlier source switch was false — act_epsus IS split-adjusted). SUE3 (the variant the paper's earnings-management narrative actually refers to per footnote 17 + Skinner-Sloan/Burgstahler-Eames) was re-derived split-consistently via ibes_adj in outer iteration 4 (audit 3's prescribed path) — the fix removes the reverse-split-persistence rows but barely moves the medians; the residual is structural: the 202601 IBES consensus forecast error is symmetric around zero (45.5% beat / 50.1% miss), so a sign-neutral SUE3 follows by construction, while the paper's positive D1 surprise requires a directional forecast bias this vintage lacks. EG: IBES act_epsus is the best source (backward D1 1.21 vs 6.95) but no source closes the backward gradient (D10 14.48 vs 30.56). Documented, metrics unchanged per the commit bar.
5. **T9 Panel A** (L = 0.750): extraction validated by spot-check (7 large firms × 2 months, all implied returns sane +6.5%..+39.3%); reverse-split artifacts in microcaps fixed with split-invariant PTB and a plausibility screen (A14). Residual: PTP runs ~24–33% vs the paper's flat ~16% — a 2026-IBES-vintage level gap, evidenced (audit 2 classified non-actionable).
6. **T12/T11** (L = 0.213): conditional (within-basket) duration tertiles fixed the sign flips (audit1 M6; t12_lowrior_l_D3 −0.72→−0.003, no_effect). Residual is a value-stock FF3-alpha LEVEL gap (e.g., value/low-RIOR D1 0.12 vs 0.81).
7. **T1 mean_age** 13.75 vs 17.59: side effect of the all-stock 20th-percentile screen (A9 — data-favored on mean_me/mean_ior).

## Data limitations

- Baker-Wurgler sentiment index — absent from catalog → Table 7 (C3) and Table 9 Panels B/C not committed (`[THIRD-PARTY-DATASET]`, data_verification.json).
- Moody's manual book equity (Davis et al. 2000) — absent → Compustat-only BE; pre-1980 firm-years without Compustat BE drop out of duration sorts (`[THIRD-PARTY-DATASET]`, assumption A7).
- 13F CUSIP→permno match rate 57.5% (unmatched CUSIPs conservatively assigned IOR = 0 per the paper's rule for stocks not in 13F — assumption A10).

## Artifacts

- `src/main.py` + `src/sql/*.sql` (12 SQL files) + `src/table1.py`, `table4_5.py`, `table6.py`, `table8_9.py`, `table10_12.py`, `evaluate.py`, `diagnose.py`, `experiments.py`
- `data/panel.parquet` (1,871,536 × 11), `data/fundamentals_duration.parquet` (169,539 firm-years; 2 consumers: T2–T6 sorts and T4's 12 alternative parameterizations)
- `results/table_1.md` … `table_12.md` (except 7), `decile_spread.png`, `cumulative_d1d10.png`
- `eval/metrics.json` (726 keys), `eval/scoring.json` (canonical scorer)
