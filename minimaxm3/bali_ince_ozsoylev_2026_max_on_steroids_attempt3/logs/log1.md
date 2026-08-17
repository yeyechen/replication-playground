---
iteration: 1
slug: max_on_steroids_attempt3
inner_iterations: 2
worker_spawns: 2
---

# Outer Iteration 1 — Reasoning Trace

## Inner iteration 1: Build analysis-ready panel

**Task spec → rep-worker:** Build `data/panel.parquet` with 16 columns covering Jan 1968 - Dec 2022 (one row per permno-month), universe-filtered via `crsp_202601.dsfhdr` PIT (shrcd IN 10/11, exchcd IN 1/2/3), $5 price floor, SIC exclusion (4900-4949, 6000-6999). Required columns: `month`, `permno`, `ret`, `me_lag1`, `me_now`, `max`, `beta`, `ivol`, `bm`, `mom`, `rev`, `illiq`, `ce`, `roe`, `ia`, `sic`. Push filtering + aggregation to ClickHouse SQL.

**rep-worker report:** 1,913,167 rows, 20,340 unique permnos, 660 months (1968-01 to 2022-12). Avg obs/month: 2,898.7. SIC exclusion dropped 439,929 rows (18.7%). Column coverage: `ret` mean 0.0201/null 0.86%, `max` mean 0.0348/null 0.67%, `beta` mean 0.879/null 38.56%, `ivol` mean 0.0270/null 38.56%, `bm` mean −0.797/null 14.91%, `mom` mean 0.225/null 9.77%, `illiq` mean 1.166 (×1e6)/null 8.32%, `ce` mean −0.156/null 11.77%, `roe` mean 0.088/null 13.82%, `ia` mean 0.105/null 13.04%. Sanity check: permno=14593 = Apple (not IBM per CRSP), beta ≈ 1.1-1.3 consistent with Apple.

**Replicator decision:** ACCEPT. Dimensions reasonable; null-rates explainable. The permno=14593/IBM issue is a spec mislabel. The `bm` log-vs-level discrepancy flagged for iteration 2.

## Inner iteration 2: Implement Tables 1 and 6

**Task spec → rep-worker:** Sort panel by MAX decile (Table 1) and MAX^β double-sort (Table 6); compute value-weighted next-month excess returns and FF3/FFC4/FF5/FF6 alphas with Newey-West 6-lag HAC t-stats; run 4 sanity checks (panel funnel, sign discipline with me_lag1 vs me_now, ascending vs descending sort, beta-neutrality for Table 6, FF6 vs FF5+MOM); write evaluator that prints per-cell tolerance check + aggregate tally.

**rep-worker report:**
- Table 1 VW RET-RF (pct/mo): D1=1.41, D2=1.09, D3=0.92, D4=0.81, D5=0.56, D6=0.40, D7=0.07, D8=0.16, D9=−0.37, D10=−0.59, D10-D1=−1.99 (t=−4.09)
- Table 1 FF3 alpha: D1=1.03, D10=−1.46, D10-D1=−2.85 (t=−9.87)
- Table 6 VW RET-RF: D1=1.16, D10=−0.24, D10-D1=−1.40 (t=−2.95)
- All 4 sanity checks PASS:
  - Sign discipline: me_lag1 weights give D10-D1=−2.01%, me_now gives +0.60% (260 bp diff; same-month weights flip the sign as expected)
  - Sign-flip: ascending=−1.99%, descending=+1.99% (flips as expected)
  - Beta-neutrality for Table 6: mean beta across MAX^β deciles is 0.877 (D1) to 0.938 (D10), spread 0.060 (within 0.1 tolerance)
  - FF6 vs FF5+MOM: D10 FF5=−0.98, FF6=−0.86, MOM beta=−0.168, diff +0.12% consistent
- Evaluator: 9 Match, 30 FAIL for T1 (L_T1 = 0.77); 9 Match, 45 FAIL for T6 (L_T6 = 0.83)

**Replicator decision:** REVISE — magnitudes are systematically 2x too large (D10-D1 RET-RF paper −0.95 vs ours −1.99, ratio 2.1). Sign pattern matches paper. Algorithm appears correct per sanity checks. Most likely cause: missing delisting-return substitution (Assumption 1 not yet wired into the panel); the `WHERE ret > -1.0` filter excludes performance-related delistings but doesn't substitute −30%/−55%. The paper's Shumway-style substitution keeps these firms in the panel with reasonable returns.

### Diagnosis
- Pre-edit metric: D10-D1_RET-RF = −1.99% (ours) vs −0.95% (paper). Ratio 2.1.
- D1 (low MAX) is biased high (ours 1.16 vs paper 0.63, +85%); D10 (high MAX) is biased LOW (ours −0.24 vs paper −0.32, +25%).
- The asymmetry points to the panel including stocks the paper excludes via proper delisting handling (or excluding stocks the paper includes).
- All sanity checks pass → algorithm is correct; data path needs fixing.

### Next fix
- Iteration 3: Add a CRSP `dsedelist` join that substitutes `dlret` for the missing-month `ret` on the delisting month. For performance-related delistings (codes 500-599, 400-499, 700-714) where `dlret` is missing, use −30% for NYSE/AMEX (exchcd IN 1,2) and −55% for NASDAQ (exchcd = 3).
- Also re-check whether `max` should be `max/100` (i.e., in percent units vs decimal). Paper's Table 2 reports MAX as decimal (D1=0.010); our column median is 0.029 which is ~3% per day, consistent with MAX(5) per day in decimal. Verify with a single-stock spot check.
- After panel fix, re-run Tables 1 and 6 (no need to re-implement the algorithms).

## Assumption decisions this iteration
- A1 (delisting treatment): wired into pipeline in iteration 3.

## Per-cell evaluation
T1: Match=9, FAIL=30, MISSING=0, L=30/39=0.77
T6: Match=9, FAIL=45, MISSING=0, L=45/54=0.83
T2: MISSING=110 (Table 2 not yet implemented)

## Summary
Iteration 1 produced the panel (1.91M rows, 16 columns). Iteration 2 implemented Tables 1 and 6 with all 4 sanity checks passing but a systematic 2x magnitude mismatch. Sign pattern is correct. Next: wire up delisting-return substitution (Assumption 1) and verify `max` units; re-run Tables 1 and 6.
