---
iteration: 3
slug: weber_2018_attempt2_deepseek
inner_iterations: 3
worker_spawns: 3
---

# Outer Iteration 3 — Reasoning Trace

**Briefing:** audit2.md — verdict REPLICATED, requires_iteration: true, 2 actionable majors: M1 (D9/D10 tail construction probe — loss-firm CF handling vs the paper's Eq. 2/3; commit with paper-cited rationale or reopen with [STRUCTURAL-SAMPLE-VARIANCE] evidence), M2 (T6 RV-series sensitivity — distinguish construction bug from inherited tail effect), plus M3 (T8 SUE/EG: resolve SUE3-vs-SUE1/2 per footnote 17 + IBES actuals source + EG source). M4 (T9 PTP vintage gap) carried as non-actionable. Scorer must run with --iteration 3.

**Replicator decisions this iteration:** M1 reopen with structural-variance evidence; M2 decomposition documented; M3 source question resolved (see entries below).

## Inner iteration 1: M1 — D9/D10 tail construction probe

**Task spec → rep-worker:** Controlled probe of duration-construction variants (V3 CF-floor, V6 pooled Dur winsorization, V8 BE≥$1M diagnostic; V3b/V7 dropped as uncited) with a strict commit bar (paper/DSS-cited rationale + majority of 18 tail cells + no spread degradation + non-negative net cell movement).

**rep-worker report (key numbers):**
- Citation check: the CF-floor is NOT a faithful DSS reading — clean-surplus CF = E − ΔBV is legitimately negative for loss/reinvesting firms; neither DSS (2004) nor Weber floors it.
- V3: D10 0.225 (overshoots 0.32), spread 1.343 (breaks the headline cell), net −6 cells → rejected.
- V6: no-op. V8 (BE≥$1M, diagnostic-only, uncited): D10 0.357, net +3, but degrades nodl_D10/ff5_alpha_D8 → not committable.
- [STRUCTURAL-SAMPLE-VARIANCE] evidence: D10 mean duration 25.29 (paper Table A.9 "roughly 25 years" ✓); composition matches the paper's own description (70% negative ROE, median BE $6.8M, me $40.8M); bins balanced and correctly ordered. The 18 tail cells stay OPEN, evidenced.

**Replicator decision:** ACCEPT the reopen — no variant committed (none meets the bar); the tail is documented as sample-level with the structural-variance evidence package (vintage excluded in iteration 12, construction levers excluded now). Proceed to M2.

## Inner iteration 2: M2 — T6 RV-series sensitivity

**Task spec → rep-worker:** Sensitivity set T0-T5 varying only the RV series (EW/VW/stability-screen/market-RV/monthly/inverse-variance), decomposition of the level error into inherited baseline vs scaling-induced, no commit.

**rep-worker report (key numbers):**
- T0 canonical reproduces committed table_6.md cell-for-cell (internal consistency ✓).
- No variant dominates: T0 best on spreads (5/5); T5 (1/RV²) lowers levels (MAE 0.278 vs 0.553) but breaks 4/5 spread cells and is not paper-justified.
- Decomposition: unscaled D1 1.568 vs paper 1.99 (inherited err 0.42); scaling adds +0.78. D10: inherited 0.53, scaling +0.84. The level gap is downstream of the M1 tail composition, not an RV construction bug.

**Replicator decision:** ACCEPT — no RV variant committed; T6 levels documented as inherited-tail + [CONVENTION-APPLIED A11] with the decomposition evidence.

## Inner iteration 3: M3 — T8 SUE/EG source resolution

**Task spec → rep-worker:** Discover ibes.adj; rebuild SUE1/2 on IBES quarterly actuals (announcement-aligned, σ-standardized); SUE3 split-consistency check; EG 3-source comparison; footnote-17 resolution; commit only if net ≥ +4 cells and no regression.

**rep-worker report (key numbers):**
- act_epsus IS already split-adjusted (AAPL FY2012 44.15 → 1.5768 = 44.15/28 exact) — the outer-1 source switch rested on a false premise.
- IBES-actuals SUE1: same wrong-sign upward-in-duration slope — the SRW surprise is mean-zero BY CONSTRUCTION; no realized-EPS source can produce the paper's +0.23→−0.47 gradient.
- SUE3 blocked: statsum_epsus actual/meanest split-inconsistent in the 202601 vintage (raw errors to −1.3e9; 3.2% rows |err|>5×|meanest|).
- EG 3-source: IBES act_epsus best (backward D1 1.21 vs 6.95; forward D1 12.14 vs 10.11) but backward D10 14.48 vs 30.56 — no source closes the backward gradient.
- Footnote-17 resolution: the paper's "negative earnings surprises / earnings management" conclusion refers to SUE3 (analyst-forecast-based; Skinner-Sloan/Burgstahler-Eames are meeting-analyst-forecast citations).
- No candidate dominated → metrics untouched (T8 stays 54/56). Evaluator reproduces the audit-2 baseline exactly.

**Replicator decision:** ACCEPT — T8 SUE/EG is now documented as structurally/vintage-blocked with evidence (not implementation error). All three audit-2 majors are addressed. Scorer stamped with --iteration 3 (L = 0.2864, unchanged — no metrics moved this iteration). REPORT.md divergence register updated.

## Assumption decisions this iteration
- M1: no variant committed; tail reopened with [STRUCTURAL-SAMPLE-VARIANCE] evidence (bin formation verified: D10 mean dur 25.29 ≈ paper's "roughly 25 years"; construction levers and vintage excluded with evidence).
- M2: no RV variant committed; T6 levels documented as inherited-tail + [CONVENTION-APPLIED A11] with the baseline-vs-scaling decomposition.
- M3: SUE1/2 gradient structurally unattainable; SUE3 vintage-blocked; EG best source identified but gradient not closed. Metrics unchanged.

## Per-cell evaluation
<!-- CANONICAL scorer output: scripts/score_replication.py --iteration 3 → eval/scoring.json -->
| Table | Match | FAIL | no_effect | L |
|-------|-------|------|-----------|-----|
| T1 | 30 | 14 | 0 | 0.318 |
| T2 | 58 | 8 | 0 | 0.121 |
| T3 | 27 | 6 | 0 | 0.182 |
| T4 | 116 | 16 | 0 | 0.121 |
| T5 | 45 | 10 | 0 | 0.182 |
| T6 | 9 | 46 | 0 | 0.836 |
| T8 | 54 | 56 | 0 | 0.509 |
| T9 | 3 | 9 | 0 | 0.750 |
| T10 | 55 | 4 | 7 | 0.068 |
| T11 | 37 | 10 | 17 | 0.213 |
| T12 | 37 | 10 | 17 | 0.213 |
| **Total** | **471** | **189** | **41** | **L = 0.2864** |

## Summary
Outer iteration 3 closed all three audit-2 majors with evidence: M1 (tail: vintage + construction levers exhausted, bins verified correct, [STRUCTURAL-SAMPLE-VARIANCE] evidence), M2 (T6: no RV construction dominates; inherited-tail decomposition), M3 (SUE structurally unattainable, SUE3 vintage-blocked, EG best source documented). L = 0.2864 (471/189). No metrics changed this iteration. Proceeding to audit 3.
