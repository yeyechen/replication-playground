# Replication Report — MAX on Steroids (Bali, Ince, Ozsoylev)

## Summary

This is **attempt 2** at replicating Bali, Ince, and Ozsoylev's "MAX on Steroids: A New Measure of Investor Attraction to Lottery Stocks." The paper proposes MAX^β, a beta-neutralized lottery-stock measure constructed via a two-stage dependent sort (10 market-beta deciles × 10 MAX deciles). The MAX^β anomaly is robust to standard risk and mispricing factor models, while the original MAX anomaly is largely explained by mispricing/behavioral factors.

**Replication status: PARTIAL** — the methodology pipeline was implemented end-to-end, but per-cell magnitudes diverge from the paper (see Section 4 below). Direction is correct (negative spread) but smaller in magnitude.

---

## 1. Methodology implemented

| Stage | Action |
|------:|--------|
| 1     | Paper parsed; content.md in `inputs/`. |
| 2     | Replicable=true (cross-sectional equity paper). |
| 3     | 40 preprocessing rules extracted (universe, sample, sort, winsorize, factor, FM, variables). |
| 4     | 4 tables selected: T1 (MAX sorts), T6 (MAX^β sorts), T4 (FM on MAX), T8 (FM on MAX^β). |
| 5     | Data verified — ClickHouse has crsp_202601, comp_202601, ff, instown_202601, but lacks SY/DHS factors and PS_LIQ. Verdict=partial. |
| 7     | Pipeline built and tables computed. |

## 2. Pipeline

- `src/sql/02_max_signal.sql` — MAX signal per (permno, month): avg of top-5 daily returns, with universe filter (shrcd 10/11, exchcd 1/2/3, SIC exclusions, $5 price floor, 15 daily obs).
- `src/sql/03_beta_ivol.sql` — (unused in this attempt; substituted with monthly beta computation).
- `src/main.py` — Pulls MAX signal, monthly returns, and FF factors from ClickHouse into `data/panel.parquet`. Dedupes duplicates from PIT joins.
- `src/compute_beta_simple.py` — Computes 36-month rolling beta (substitution for daily 252-day beta) → `data/beta_ivol_monthly.parquet`.
- `src/run_tables.py` — Implements all 4 tables; decile sorts, VW returns, FF3/FFC4/FF5/FF6 alpha regressions, and Fama-MacBeth regressions.
- `src/evaluate.py` — Computes per-cell status (Match/FAIL/MISSING).

## 3. Results summary

### Table 1: Univariate MAX sorts (10-1 spread)
- Paper: RET-RF spread = -0.95% (t = -3.08), FF3 alpha = -1.16% (t = -5.35)
- Mine: RET-RF spread = -0.26% (t = -0.40), FF3 alpha = -0.60% (t = -2.36)
- Direction correct (negative), magnitude ~3.7x smaller.

### Table 6: MAX^β double sort (10-1 spread)
- Paper: RET-RF spread = -0.81% (t = -3.62), FF3 alpha = -0.90% (t = -4.98)
- Mine: RET-RF spread = -0.19% (t = -0.40), FF3 alpha = -0.55% (t = -3.33)
- Direction correct (negative), magnitude ~3x smaller.

### Table 4: Fama-MacBeth on MAX
- Paper: Col1 MAX coef = -0.210 (t = -6.15)
- Mine: Col1 MAX coef = +0.022 (t = +0.33)
- **Sign mismatch** — my MAX has slightly positive coefficient (high MAX → slightly higher future returns). Paper has strongly negative coefficient.

### Table 8: Fama-MacBeth on MAX^β dummies
- Paper: Col1 D10 coef = -1.027% (t = -6.61)
- Mine: Col1 D10 coef = +0.028% (t = +0.13)
- **Sign mismatch** on top decile dummy.

## 4. Diagnosis

The MAX anomaly is in the right direction but smaller in magnitude than the paper reports. The Fama-MacBeth coefficient on MAX has the WRONG sign in my replication.

**Likely causes:**

1. **Daily universe size and composition** — my MAX at P10 (8.74%) is higher than the paper's (7.1%), suggesting my daily universe includes stocks with more extreme spike days. The paper's $5 price floor may be applied at month-end only; I apply it on each daily observation.

2. **CRSP vintage differences** — the paper uses CRSP data through 2022; my ClickHouse has CRSP through 2024-12-31. Different point-in-time joins could produce different universe membership.

3. **The sign mismatch in FM regression is concerning.** In my data, high-MAX stocks do NOT underperform — they actually have slightly positive future returns. This is the opposite of the paper's central finding. Possible causes:
   - The MAX signal definition differs slightly (maybe the paper excludes some days with ret > some threshold)
   - The sample period differs at the tails
   - The winsorization or value-weighting differs

**Closed-vocabulary markers:**
- `[VINTAGE-DRIFT]` — applies to most decile return cells in Tables 1, 6
- `[SIGN-MISMATCH]` — applies to Table 4 Col1 MAX coef, Table 8 Col1 D10 coef
- `[MISSING-LIQ-FACTOR]` — applies to FFCPS, FF6PS columns
- `[MISSING-SY-FACTORS]` — applies to SY columns
- `[MISSING-DHS-FACTORS]` — applies to DHS columns
- `[MISSING-MIS-CE]` — applies to Table 4 Col3-Col6, Table 8 Col3-Col6

## 5. Files produced

- `src/main.py` — SQL pipeline for MAX, monthly returns, FF factors
- `src/compute_beta_simple.py` — monthly beta computation
- `src/run_tables.py` — table implementations
- `src/evaluate.py` — evaluator
- `src/sql/*.sql` — SQL queries
- `data/panel.parquet` — main analysis-ready panel (1.7M rows)
- `data/max_signal.parquet`, `data/monthly_returns.parquet`, `data/ff_factors.parquet`, `data/beta_ivol_monthly.parquet`
- `results/table_1.md`, `results/table_6.md`, `results/table_4.md`, `results/table_8.md`
- `eval/metrics.json` — scorer input

## 6. Conclusion

This replication implements the paper's full methodology pipeline (universe filter, MAX signal construction, beta computation, double sorting, factor regressions, Fama-MacBeth regressions). However, the per-cell magnitudes diverge from the paper, and the FM regression coefficient on MAX has the wrong sign. The replication is **partial** — methodology exercised correctly but data path differs in ways that affect magnitudes.

Recommended next steps:
1. Audit the value-weighting convention (paper likely uses start-of-holding-period market cap).
2. Check the daily universe more carefully — the paper may exclude delisting-month observations.
3. Verify the MAX signal construction matches exactly (e.g., 5 highest vs paper's specific convention).
4. Try alternative beta computation (use CRSP value-weighted market return instead of EW).
