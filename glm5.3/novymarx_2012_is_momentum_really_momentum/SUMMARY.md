---
schema_version: 2
slug: novymarx_2012_is_momentum_really_momentum
iteration: 2
verdict: REPLICATED
overall: 4.67
methodology: 5
headline_matching: 5
data_coverage: 5
concrete_result: 5
signal_strength: 3
corollary: 5
generated_at: 2026-09-08T00:00:00Z
---

# Replication Summary

## Novy-Marx (2012), "Is Momentum Really Momentum?"

### Bottom line

**Replication result:** `REPLICATED`
**Overall quality:** 4.67 / 5.00

The paper's central claim — that momentum profits derive primarily from intermediate-horizon past performance (months 12 to 7), not recent performance (months 6 to 2) — reproduces almost exactly: the FM coefficient-difference row is 0.56 [t 2.40] vs the paper's 0.57 [2.42], the MOM_6,2 mean return matches to the second decimal (0.67 vs 0.67), and the FF4-alpha significance contrast (significant for MOM_12,7, no effect for MOM_6,2) reproduces exactly in inference. A binary REPLICATED does not mean every reported number matched: 45 of 473 committed cells (9.5%) remain outside tolerance, all in three documented residue families (French-series vintage drift, near-zero t-cells of paper-insignificant estimates, and a tested-but-unresolved SUE construction).

## Quality assessment

| Dimension | Score | Assessment |
|---|---:|---|
| Methodology | 5/5 | All construction choices traced to paper text or tested conventions; the audit-1 gap (two open cells) was closed by a discriminating breakpoint-convention test with a dated correction. |
| Headline matching | 5/5 | C1 and C2 reproduce in shape, sign, magnitude, and significance category; Sharpe ratio 1.87x vs the paper's "more than twice". |
| Data coverage | 5/5 | Exact sample period (1008 months, 1927-2010); universe validated 25/25 cells against the paper's own Table 7 Panel A; clean joins. |
| Concrete result matching | 5/5 | 428/473 committed cells Match (90.5%); 0 MISSING, 0 SKIP. |
| Signal strength | 3/5 | Worst headline-table cell r = 1.49 (T2 intercept_s4 0.81 vs 0.54) — right sign and magnitude class, but outside the +/-20% band. |
| Corollary | 5/5 | Non-headline tables 360/392 Match (91.8%); the audit-1 open cells are now Match. |

## What replicated and what it validates

| Paper output | High-level evidence | What it supports |
|---|---|---|
| Table 1 (FM regressions) | r_12,7 vs r_6,2 coefficient difference 0.56 [2.40] vs paper 0.57 [2.42]; reparameterization identity exact | The headline FM claim: intermediate-horizon returns predict with ~2x the slope of recent returns, difference significant |
| Tables 2-3 (strategy spans) | Intercepts 7/8 Match (e.g. s2 1.36 vs 1.36, s5 0.67 vs 0.67); MOM_12,7 FF4 alpha significant, MOM_6,2 alpha no effect | The profitability and factor-model claim across spanning regressions |
| Table 4 (double sorts) | IR spreads 1.02/0.74/1.05/0.97/0.86 vs paper 0.99/0.70/1.04/0.96/0.92; IR ~ 2x RR pattern | Intermediate-horizon information survives controlling on recent-horizon sorts |
| Table 6 (conditional strategies) | 99/105 cells Match; corrected inner-breakpoint convention closes the q5 large-stock cells (0.36 [2.01] vs paper 0.40 [2.25]) | Conditional-sort evidence, including the large-stock corollary |
| Table 7 (size quintiles) | Panel A universe validator 25/25 Match; MOM_12,7 significant in every quintile, MOM_6,2 fades among large stocks | The "disparity most acute among large stocks" claim and the universe construction |
| Table 8 (industries / SUE) | Industry intercept 0.57 [5.14] vs paper 0.57 [4.93]; with SUE added, r_12,7 stays significant | Industry-momentum corollary; earnings momentum does not subsume intermediate-horizon momentum (SUE slope itself is 1.7x paper — documented residue) |

## Important gaps

- DFF (2000) 1927-start book equity is unavailable in the catalog — Table 1 whole/early/first/second columns and Table 9 (styles) are out of scope (non-actionable data limitation).
- Asset-class corollaries (Tables 10-12: country indices, commodities, FX) are absent from the data catalog (non-actionable).
- Loadings on French-published factor series drift pre-1945 (corr 0.878 vs paper's 0.99); tested via a French-methodology 2x3 UMD rebuild — vintage residue (non-actionable).
- SUE slopes run ~1.7x the paper; denominator and PIT-vintage causes both tested, neither reproduces the paper value (documented, tested-but-unresolved residue).
- No actionable gaps remain; loop exited under the documented-residue criterion.
