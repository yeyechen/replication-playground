---
schema_version: 2
slug: weber_2018_attempt2_deepseek
iteration: 4
verdict: REPLICATED
overall: 3.17
methodology: 3
headline_matching: 4
data_coverage: 3
concrete_result: 3
signal_strength: 3
corollary: 3
generated_at: 2026-08-16T18:00:00Z
---

# Replication Summary

## Cash flow duration and the term structure of equity returns (Weber 2018, JFE 128, 486–503)

### Bottom line

**Replication result:** `REPLICATED`
**Overall quality:** 3.17 / 5.00

The paper's central claim — a downward-sloping term structure where high-duration stocks earn 1.10% per month less than short-duration stocks — replicates near-exactly: the long-short spread is 1.106%/mo (0.5% error), CAPM betas match 10/10, the CAPM alpha spread is 1.31 vs 1.29, and the FF3/FF4/FF5 spread alphas (0.80/0.64/0.38 vs 0.84/0.66/0.48) are all within tolerance. Outer iteration 4 closed the loop: both remaining plausibly-fixable threads were resolved with demonstrated test results (the SUE3 split-consistency fix was run and disproven as structural forecast-error symmetry; the loss-firm CF probe was documented-not-committed), and the loss has plateaued at 0.2864 for three consecutive iterations. A REPLICATED verdict reflects the headline evidence, not a full cell-for-cell match: 67.2% of committed cells Match, and the residue concentrates in the tail descriptives, the I/B/E/S SUE/EG gradient, and the volatility-managed decile levels — all now documented as non-actionable.

## Quality assessment

| Dimension | Score | Assessment |
|---|---:|---|
| Methodology | 3/5 | Construction traces to the paper; diagnostic-evidence discipline is exemplary (SUE3 fix actually run, V9 probed, T1 partitioned), but statistical inference still fails at the D10 tail (alpha sign flip). |
| Headline matching | 4/5 | Spread, betas, and alpha spreads match within ~20%; individual D9/D10 bins drift 30–45% but the headline monotonic slope is exact. |
| Data coverage | 3/5 | Period exact (1963–2014), join hygiene clean; ~14% universe-ME drift and 2 documented substitutes (Moody's BE, Baker-Wurgler sentiment). |
| Concrete result matching | 3/5 | 471/701 committed cells Match (67.2%) — band 3. |
| Signal strength | 3/5 | Headline spread cells all Match (worst r=0.80), but D10 tail cells within headline tables sign-flip (ff4_alpha_D10) or run ~20× off (ff5_alpha_D10). |
| Corollary | 3/5 | 356/558 corollary cells Match (63.8%); T10 (93%) and T4 (88%) strong; T6/T9/T8 lag. |

## What replicated and what it validates

| Paper output | High-level evidence | What it supports |
|---|---|---|
| Table 2 + 3 (term structure + factor alphas) | Spread 1.106 vs 1.10; betas 10/10; FF3/FF4/FF5 spreads all within tolerance | Duration construction, June sort, and the downward-sloping term structure that factors explain only partly (C1, C2). |
| Table 4 (12 parameter variations) | 116/132 cells Match; 10 of 11 non-pre-estimation rows within ±20% | Robustness of the duration measure to discount-rate, persistence, and horizon choices (C6). |
| Table 5 + 6 (subsamples + volatility-managed) | T5 spreads 4/5 Match; T6 all 5 spread cells Match (1.56 vs 1.46, 1.68 vs 1.58, …) | The premium is stable across subperiods and enlarged by volatility management (C6). |
| Table 10–12 (short-sale constraints) | T10 Low-RIOR spread 1.35 vs 1.32 (L=0.068, strongest table); T12 sign flips resolved | The premium is concentrated in short-sale-constrained stocks and holds within size/B-M bins (C5). |
| Table 8 (analyst expectations) | LTG panel reproduces on the IBES-covered subset (D1 12.71 vs 13.08, D10 29.09 vs 25.73) | Analysts extrapolate LTG forecasts upward in duration (part of C4); SUE/EG gradient unmet, demonstrated structural. |

## Important gaps

- **Duration-tail composition (D9/D10):** top-duration bins contain more tiny, loss-making firms than the paper's, inflating D10 returns and flipping the D10 factor-alphas. Demonstrated compositional (vintage rejected, CF-floor family exhausted, bin formation verified correct); the specific screen that makes Weber's tiny loss-makers earn less remains unidentified and non-actionable.
- **Table 8 SUE/EG gradient:** the seasonal-random-walk SUE numerator is flat by construction; SUE3 (the paper's actual mechanism) was re-derived split-consistently and shown to be sign-neutral because the 202601 IBES consensus forecast error is symmetric (45.5% beat / 50.1% miss) — a directional bias this vintage lacks. Non-actionable.
- **Volatility-managed decile levels (T6):** all spread cells match but per-decile levels run 10–50% high, inherited from the tail composition plus a paper-silent RV-series construction.
- **Baker-Wurgler sentiment and Moody's book equity unavailable** — Table 7 (claim C3) and Table 9 Panels B/C are not committed; Compustat-only BE drops pre-1980 firm-years (documented data limitations).
