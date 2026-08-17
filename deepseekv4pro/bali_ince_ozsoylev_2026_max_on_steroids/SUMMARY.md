---
schema_version: 2
slug: max_on_steroids_attempt5_deepseek
iteration: 3
verdict: REPLICATED
overall: 3.83
methodology: 4
headline_matching: 5
data_coverage: 3
concrete_result: 3
signal_strength: 5
corollary: 3
generated_at: 2026-08-16
---

# Replication Summary

## MAX on Steroids (Bali, Ince & Ozsoylev)

### Bottom line

**Replication result:** `REPLICATED`
**Overall quality:** 3.83 / 5.00

The paper's two central claims replicate at the level of its argument: the original MAX anomaly's value-weighted spreads are explained by mispricing/behavioral controls (T1 10-1 spread −1.02 vs paper −0.95, t −3.26 vs −3.08), while beta-neutralized MAX^β earns a significant long-short return robust to risk and mispricing models (T3 −0.87 vs −0.81, t −3.68 vs −3.62). This iteration closed the last open fix — the equity-issuance (CE) pipeline defect that had inflated the CE coefficient 30× — via a log-form Daniel-Titman net-issuance construction (corr(me_gr12,cumret12) 0.09 → 0.92), moving t2_ce_c4 to −0.0103 (paper −0.017) into Match. A binary REPLICATED does not mean every number matched: 455 of 701 committed cells are Match (64.9%), with the residual tail concentrated in documented non-actionable residue (unavailable DHS/SY factors, structural sample variance in interior decile and long-horizon cells).

## Quality assessment

| Dimension | Score | Assessment |
|---|---:|---|
| Methodology | 4/5 | 8/8 sub-checks pass; deviations (SY 1968-2016, DHS gap, log-form CE, E(ISKEW)/β^MAX offsets) documented with before/after evidence |
| Headline matching | 5/5 | T1/T3 spreads, alphas, and monotonic decile profiles match paper sign and magnitude class to ~10%; CE now Match |
| Data coverage | 3/5 | Period exact 1968-2022, universe close (1.74M stock-months, 17,856 permnos), 0-dup join; SY truncated, DHS absent |
| Concrete result matching | 3/5 | 455/701 committed cells Match (64.9%) — band 3 |
| Signal strength | 5/5 | Headline spread cells worst-case r ≈ 1.10 (T1 CAPM −1.54 vs −1.41) — all in [0.9, 1.1] |
| Corollary | 3/5 | Clientele (T8) and durability (T5) reproduce; issuance-state (T9) 22/47 with the paper-insignificant max_lo cell as residue |

## What replicated and what it validates

| Paper output | High-level evidence | What it supports |
|---|---|---|
| Table 1 (MAX deciles) | 10-1 VW spread −1.02 (t=−3.26) vs −0.95 (−3.08); CAPM −1.54 vs −1.41; SY spread insignificant in both | C1 headline: MAX spreads close once mispricing controls included |
| Table 6 (MAX^β deciles) | 10-1 spread −0.87 (t=−3.68) vs −0.81 (−3.62); robust across 8 of 9 factor models, both legs | C2 headline: MAX^β is a distinct, robust anomaly |
| Table 4 (FM on MAX) | All six MAX coefficients Match; CE now −0.010 (t −3.37) vs −0.017 (−4.43) after the log-form fix | Firm-level MAX predictive power and the issuance (CE) channel |
| Table 8 + Table 9 (INST tiers) | D10 columns Match; INST tier Panel B spreads Match; clientele split reproduced | C3 corollary: heterogeneous skewness preferences by clientele |
| Table 12 (durability) | K=1/K=12 alphas Match; MAX decays to ≈0 by K=12 while MAX^β stays positive | C4 corollary: low-MAX^β premium is durable equilibrium compensation |
| Table A5 + Table A7 (characteristics + issuance) | BETA spread 0.000 (beta-neutrality exact); T9 high-issuance ordering restored after CE repair | Sort validity and C5's issuance-invariance (partial: max_lo residue) |

## Important gaps

- **DHS behavioral factors unavailable** — 24 committed cells MISSING (T1/T3 DHS columns); documented [THIRD-PARTY-DATASET], non-actionable.
- **SY factors truncated** — M4.csv ends 2016-12, so SY alphas are estimated on 1968-2016 (588 of 660 months), not the full window.
- **FM control-coefficient residuals** — IVOL (~1.8×), ROE (unit unscalable), BM (~2×) remain outside tolerance; both ROE scales tested with no fix, documented structural.
- **E(ISKEW) level offset** (−35%) and **β^MAX dispersion** (−40%) remain documented residue; the ISKEW residual-moment bug itself was found and fixed in iteration 2 via a single-firm spot-check.
- **Table 12 long-horizon legs** (K≥18, CR24) are noisy and mostly FAIL; the load-bearing K1/K12 cells Match. The C4 argument rests on the matched short-horizon cells.
