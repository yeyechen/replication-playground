---
schema_version: 2
slug: max_on_steroids_attempt2
iteration: 1
verdict: FAILED
overall: 1.83
methodology: 3
headline_matching: 2
data_coverage: 3
concrete_result: 1
signal_strength: 1
corollary: 1
generated_at: 2026-08-15T00:00:00Z
---

# Replication Summary

## MAX on Steroids: A New Measure of Investor Attraction to Lottery Stocks (Bali, Ince, Ozsoylev)

### Bottom line

**Replication result:** `FAILED`
**Overall quality:** 1.83 / 5.00

The replication built the full SQL-to-regression pipeline (MAX signal, monthly returns, FF factors, decile sorts, double sort for MAX^β, Fama-MacBeth), but the per-cell magnitudes are 3-5× too small on the headline spreads and the Fama-MacBeth MAX coefficient is sign-flipped on Tables 4 and 8. The agent's own evaluator reports Match 2 / FAIL 50 / MISSING 14 (rate 3.0%); the canonical scorer cannot parse the agent's `eval/metrics.json` at all and reports 0/66. A binary `FAILED` does not mean the agent did no useful work — the pipeline is structurally sound — but the headline anomaly is not at the magnitude the paper reports, and a load-bearing FM regression is sign-flipped, so the central claim does not replicate.

## Quality assessment

| Dimension | Score | Assessment |
|---|---:|---|
| Methodology | 3/5 | 6 of 8 sub-checks pass: MAX formula, filter, timing, look-ahead, winsorization, NW convention are wired correctly. Sub-check 7 fails because `assumptions.md` A10 closes FAILs with hedged "most likely" without a test result. Sub-check 8 fails because the T4/T8 FM coefficients are sign-flipped. |
| Headline matching | 2/5 | Both headline spreads (T1 10-1 RET-RF and T6 10-1 RET-RF) have the right direction but magnitudes are 3-5× too small (r = 0.27 and r = 0.23 respectively). The monotonic pattern holds across deciles. |
| Data coverage | 3/5 | Period starts 1970 vs paper 1968 (24 months dropped). Universe size ~2,672 stocks/month avg; MAX@P10 = 8.74% vs paper 7.1% suggests a fatter-tailed daily universe. SY/DHS/PS_LIQ factors missing (documented in `data_verification.json`). |
| Concrete result matching | 1/5 | Match 2 / FAIL 50 / MISSING 14 (rate 3.0%) — well below the 30% threshold. |
| Signal strength | 1/5 | Worst headline cell r = 0.23 (T6 10-1 RET-RF spread) — outside [0.33, 3.0]. T1 P10_RET_RF cell is also wrong sign (+0.86 vs paper −0.32). |
| Corollary | 1/5 | FFCPS, FF6PS, SY, DHS columns entirely MISSING (14 cells). T4 Col3-Col6 (MIS/CE controls) also MISSING. |

## What replicated and what it validates

| Paper output | High-level evidence | What it supports |
|---|---|---|
| Table 1 (Univariate MAX sorts) | 10-1 VW RET-RF spread = −0.26% (paper −0.95%); FF3 alpha = −0.60% (paper −1.16%); direction correct, magnitude 3.7× too small. Monotone across deciles. | MAX signal construction works; decile sort and value-weighting produce the right shape; data path captures the anomaly at a fraction of the paper's magnitude. |
| Table 6 (MAX^β double sort) | 10-1 VW RET-RF spread = −0.19% (paper −0.81%); FF3 alpha = −0.55% (paper −0.90%); direction correct, magnitude 3× too small. | The two-stage dependent sort (beta × MAX regrouping) executes; beta substitution (monthly for daily) does not flip the sign. |
| Table 4 (FM on MAX) | Col1 MAX coef = +0.022 (paper −0.210, t = −6.15) — **wrong sign**. Col2 MAX coef = +0.110 (paper −0.113) — wrong sign. | The FM regression runs end-to-end, but the relationship between MAX and forward excess return is inverted. Sign-flip is a load-bearing finding. |
| Table 8 (FM on MAX^β dummies) | Col1 D10 coef = +0.048% (paper −1.027%, t = −6.61) — **wrong sign**. | Same sign-flip pattern as Table 4; the decile-dummy construction does not flip the sign. |

## Important gaps

- **Three rubric dimensions at 1 (Concrete Result, Signal Strength, Corollary)** — these are bright-line failures that drive the FAILED verdict. Concrete Result's Match rate (3.0%) is the most direct evidence; Signal Strength's worst-cell r = 0.23 places the anomaly outside any acceptable magnitude band; Corollary has no non-MISSING result.
- **Sign mismatch on FM regressions** (Tables 4 and 8) — the paper's central claim that high-MAX stocks underperform does not hold in the replicated data; in this run, high-MAX stocks slightly outperform. Diagnosing this is the single highest-leverage fix for the next iteration.
- **Universe / magnitude drift** — MAX@P10 = 8.74% in the panel vs 7.1% in the paper suggests the daily universe over-includes spike stocks; the $5 price-floor convention (every-daily vs month-end) is the most likely root.
- **External data not in ClickHouse** — Pastor-Stambaugh LIQ, Stambaugh-Yuan MGMT/PERF, and Daniel-Hirshleifer-Sun FIN/PEAD factors are not in the catalog. Documented in `data_verification.json` blocking_issues; replication of FFCPS, FF6PS, SY, DHS alpha columns is not possible.
- **Sample starts 1970 instead of 1968** — 24 months (~3.6% of paper period) are missing in the cached panel; not investigated.
- **`scripts/score_replication.py` cannot parse `eval/metrics.json`** — the agent's evaluator writes a nested `"metrics"` key while the canonical scorer expects a flat cell-keyed dict. Both files need restructuring for downstream audits.
