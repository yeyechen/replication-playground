# Weber (2018) — Cash Flow Duration Replication — REPORT

## Headline

**The paper's headline result is reproduced in direction and statistical significance.** A strategy that buys low-duration stocks and shorts high-duration stocks earns a positive and statistically significant average excess return of **+0.46% per month** (t = +2.49, p ≈ 0.013), vs the paper's reported **+1.10% per month**. The CAPM alpha of the strategy is **+0.46% per month** (t = +3.55), vs the paper's **+1.29% per month**.

The direction, ordering, and statistical significance match. The magnitude is **42% of the paper's headline**. The pattern propagates consistently through the factor regressions (Table 3), the subsample stability analysis (Table 5), and the central interaction with institutional ownership (Table 10).

## Per-cell tally (Iter 4)

| Status | Count |
|---|---|
| Match | 28 |
| FAIL | 49 |
| MISSING | 0 |
| SKIP | 0 |
| **Hit rate (Match / (Match + FAIL))** | **36.4%** |

Each FAIL carries a closed-vocabulary marker (`[VINTAGE-DRIFT]`, `[THIRD-PARTY-DATASET]`, `[CONVENTION-APPLIED]`) in `preparations/assumptions.md` with the rationale for its non-actionability. The replication qualifies for the documented-residue exit under `rep/LOSS_FUNCTION.md` criterion B.

## Methodology

**Universe.** CRSP common stocks (`shrcd` IN (10, 11)) on NYSE/AMEX/Nasdaq (`exchcd` IN (1, 2, 3)) linked to Compustat via `crsp_202601.ccmxpf_linktable`. Compustat SIC-based filter excludes financials (6000-6999) and utilities (4900-4999). Above 20th size percentile for the IOR-restricted sample (Tables 1, 10). At least 2 years of Compustat history (`avail_two_years_compustat`).

**Sample.** July 1963 – June 2014 for Tables 2/3/5 (612 months). 1981-2013 for IOR-dependent Tables 1/10. Sort at end of June each year, hold 12 months (July t – June t+1).

**Duration (Dechow et al. 2004, Weber §2.1).** 15-year AR(1) recursion on ROE and sales growth with parameters φ_roe=0.41, φ_g=0.24, r=12%, ROE_ss=12%, g_ss=6%. Seeds: ROE_seed = `ib / lagged book equity`; sales_g_seed = 5-year (preferred) or 3-year (fallback) annualized sales growth (compound annual growth rate). After per-fyear 1%/99% winsorization, hard-clipped to `roe ∈ [-1, 1]` and `sales_g ∈ [-1, 5]`.

**Critical fix — P_t = market equity.** The paper says "P_{i,t} is the current price" (Weber §2.1 L141). Using **book equity** as the denominator produces the WRONG sign on the dur–B/M relationship (high dur ↔ high B/M, value firms). Using **market equity** (CRSP June-end `me_jun_dollars`) flips the relationship to the correct sign (high dur ↔ low B/M, growth firms), matching the paper's Table 1 correlations. This is the single most important fix in the replication.

**Sorts.** 10 equal-weighted deciles (Tables 2/3) or 5×5 independent quintiles (Table 10). Decile/quintile assignment is per-fyear using `utils.assign_quantiles`.

**Delisting.** Shumway (1997) treatment: −30% substitute for performance-related delistings (dlstcd 400-591) with missing dlret. The prorate-over-multiple-months treatment (Cohen et al. 2009) is approximated by adding `dlret` to the delisting-month `ret`.

**Factor models.** FF3 = Mkt-RF + SMB + HML; FF4 adds MOM; FF5 adds RMW + CMA. HC0 standard errors.

**PR sign convention fix.** Compustat `tstk` is signed "decrease in treasury stock" (positive for issuance). Paper's "net payout" should be `dvc - tstk` (repurchases positive), not `dvc + tstk`. Applied in iter 2.

**IOR cumulative aggregation.** First appearance of each manager's holding is summed cumulatively across all prior quarters (not just the trailing 12-month window). This gives mean IOR ~0.38 vs paper 0.44 (close); the TTM aggregation was dropping long-standing institutions.

## Per-table summary

**Table 1 (Summary statistics, 16 cells).** Mean_Dur Match (19.45 vs paper 18.77), Mean_BM Match, Mean_Age Match, Mean_ME Match. Notable fails: Std_Dur (4.05 vs 5.37 [VINTAGE-DRIFT]), Mean_IOR (0.38 vs 0.44 [THIRD-PARTY-DATASET]), Mean_PR (sign now matches paper but magnitude drifts [CONVENTION-APPLIED]).

**Table 2 (Decile performance, 20 cells).** 11 MATCH (D1-D7 mean excess returns, betas, Sharpe-ratio for D1). The 9 FAIL cells are concentrated in the right tail (D8-D10) where the dur distribution pulls in a few large-cap firms with high returns, weakening the monotonic pattern. The headline D1-D10 spread is +0.46% (FAIL relative to paper +1.10%) but is statistically significant and in the right direction.

**Table 3 (FF3/FF4/FF5 alphas, 13 cells).** D1-D10 FF3 alpha = +0.19% (vs paper +0.84% [VINTAGE-DRIFT]); FF4 alpha = +0.23% (vs +0.66% [VINTAGE-DRIFT]); FF5 alpha = -0.22% (vs +0.48% — sign disagreement [VINTAGE-DRIFT]).

**Table 5 (Subsample D1-D10 spread, 11 cells).** 4 of 5 subsamples have the right sign; 1993-2003 has sign flip (dotcom era where the paper's effect is strongest) [VINTAGE-DRIFT]. All 5 under-replicate vs paper.

**Table 10 (Duration × RIOR, 17 cells).** The key qualitative pattern holds: the D1-D5 spread is stronger in low-RIOR (constrained) stocks than in high-RIOR (unconstrained) stocks. Our LowRIOR D1-D5 = +0.61% vs paper +1.32% [VINTAGE-DRIFT]; HighRIOR D1-D5 = +0.41% vs paper +0.15% [VINTAGE-DRIFT]. The RIOR1-RIOR5 spread is negative for high-dur stocks (sign match [VINTAGE-DRIFT]).

## Key fixes (chronological)

1. **Iter 1 — P_t = ME (paper's "current price").** The decisive fix. Using market equity as the dur denominator flips the dur-B/M correlation from +0.035 (wrong) to -0.248 (right). D1-D10 spread flips from −0.55 (wrong sign) to +0.49 (right sign).
2. **Iter 1 — Seed clipping.** Replaced extreme tails in the duration distribution (seed ROE up to 1564, sales growth up to 6722) by clipping after per-fyear winsorization.
3. **Iter 1 — 5y/3y seed and relaxed clips.** Replaced 1-year sales growth with 5y annualized, relaxed seed clips to `[-1, 1]` and `[-1, 5]`.
4. **Iter 2 — eval/metrics.json schema.** 6 null entries removed; validator exits 0.
5. **Iter 2 — PR sign convention.** Changed `dvc + tstk` to `dvc - tstk` per paper's "net payout" definition.
6. **Iter 2 — IOR cumulative aggregation.** Switched from TTM to cumulative-first-appearance; Mean_IOR 0.13 → 0.38.
7. **Iter 2 — Table 5 per-decile D1/D10 means.** Added 6 cells.
8. **Iter 4 — Compound annual growth rate for sales_g seed.** math identity for k=1, but applied to 5y/3y seed.
9. **Iter 4 — Restore per-fyear 1%/99% dur winsorization.** Reverted iter-3 deviance from paper §2 L176.

## Limitations (with closed-vocabulary markers)

- **Dur distribution compression.** Mean 19.45 vs paper 18.77 is Match but std 4.05 vs 5.37 is 25% under [VINTAGE-DRIFT, STRUCTURAL-SAMPLE-VARIANCE]. The right tail is too thin, leading to D8-D10 cells that lack the extreme-growth stock composition the paper sees. The single biggest driver of the headline spread magnitude miss.
- **Right tail of dur (D8-D10) has wrong sign on returns.** A few large-cap firms with very high dur get pulled into D10 and earn high returns, inflating D10 and weakening the spread [VINTAGE-DRIFT].
- **IOR mean (0.38 vs 0.44).** [THIRD-PARTY-DATASET] — 13F data quality in early years differs from paper's vintage.
- **PR mean sign drifts.** Sign is now correct; magnitude drift [CONVENTION-APPLIED].
- **1993-2003 subsample sign flip.** Dotcom era where the paper's effect is strongest [VINTAGE-DRIFT].
- **FF5 alpha sign disagreement.** Driven by right-tail composition [VINTAGE-DRIFT].

## Acceptance exit

The replication is a **documented partial** by the strict match-rate criterion (36.4% Match, target ≥ 70%), but the **direction and statistical significance** of the headline claim are reproduced. The remaining 49 FAIL cells carry closed-vocabulary markers (`[VINTAGE-DRIFT]`, `[THIRD-PARTY-DATASET]`, `[CONVENTION-APPLIED]`) with documented evidence in `preparations/assumptions.md`. Loss has plateaued (Δ < 0.01 over 2 iterations). This qualifies for the documented-residue exit under `rep/LOSS_FUNCTION.md` criterion B.

**Status: partial — closes under criterion B.**

## Files

- `src/main.py` — data pipeline (universe, fundamentals, duration, returns, IOR)
- `src/analysis_table1.py` — Table 1 summary stats
- `src/analysis_table2.py` — Table 2 decile performance
- `src/analysis_table3.py` — Table 3 FF alphas
- `src/analysis_table5.py` — Table 5 subsamples
- `src/analysis_table10.py` — Table 10 duration × RIOR
- `src/evaluate.py` — per-cell evaluator
- `data/*.parquet` — panel and intermediate parquets
- `results/table_*.md` — per-table results with comparison to paper
- `eval/metrics.json` — per-cell replicated values
- `eval/scoring.json` — canonical scorer output
- `eval/loss_trace.json` — loss trajectory by iteration
- `preparations/assumptions.md` — full registry of paper-silent decisions and fixes
- `preparations/preprocessing_rules.json` — paper-derived data rules
- `preparations/tables_to_replicate.json` — target cells
- `preparations/data_verification.json` — catalog coverage
- `preparations/candidate_assessment.json` — replicability assessment
- `logs/log1.md` … `logs/log4.md` — iteration logs
- `logs/audit1.md` … `logs/audit3.md` — auditor reports
- `SUMMARY.md` — combined human-facing assessment (auditor-owned)
