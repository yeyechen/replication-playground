---
iteration: 4
slug: weber_2018_attempt2_deepseek
inner_iterations: 2
worker_spawns: 2
---

# Outer Iteration 4 — Reasoning Trace

**Briefing:** audit3.md — verdict REPLICATED, requires_iteration: true, 2 actionable majors: M1 (T8 SUE3 blocked only by a measured split inconsistency in statsum_epsus — apply the ibes_adj cumulative split factor to re-derive a split-consistent SUE3; previously-unattempted fix path), M2 (a) graduated/loss-firm CF treatment probe with the commit bar; (b) partition T1 FAILs into zero-anchor artifacts vs genuine composition gaps), plus m1 (log3 cleanup — done by the Replicator).

**Replicator decisions this iteration:** M1 path attempted and disproven (SUE3 structural); V9 probe documented, not committed (net −6); T1 FAIL partition written. See entries below.

## Inner iteration 1: M1 — SUE3 split-consistency fix

**Task spec → rep-worker:** Diagnose the statsum split inconsistency mechanism; implement the ibes_adj-based split-consistent SUE3 re-derivation; commit only if net ≥ +3 SUE3 cells.

**rep-worker report (key numbers):**
- Mechanism: reverse-split persistence — statsum_epsus.actual is forward-persisted from the pre-reverse-split basis (examples: ACTC −624M vs −24M; GNTA −5.0M vs −35k). 14.7% of the tail is reverse-split rows; the fix removes them.
- Split-consistent SUE3: D1 −0.209→−0.207, D8 −0.090→−0.083 — essentially no movement. All 11 cells remain sign-mismatch FAIL. Net 0 → metrics untouched.
- Root cause beyond splits: the 202601 consensus forecast error is SYMMETRIC around zero (45.5% beat / 50.1% miss; median −0.005 $/share) — a sign-neutral SUE3 by construction. The paper's positive D1 surprise requires a directional forecast bias this vintage lacks. Structural.

**Replicator decision:** ACCEPT — the audit-3 M1 path was attempted and disproven with evidence; SUE3 closed as structural (forecast-unbiasedness), documented in results/table_8.md + assumptions §Iteration 15.

## Inner iteration 2: M2 — loss-firm CF probe + T1 FAIL partition

**Task spec → rep-worker:** V9 loss-firm-only CF floor probe (footnote-6 perpetuity reading; commit bar: majority tail + spread within ±30% + net ≥ +2 + paper-cited); T1 FAIL partition (zero-anchor artifacts vs genuine gaps, report only).

**rep-worker report (key numbers):**
- V9: mean_D10 0.455→0.189 (overshoots), spread 1.113→1.404 (within band but at the edge), tail cells 9→10 Match, net −6 → NOT committed. One new finding: V9 is the first lever to flip the tail factor alphas toward the paper (ff4_alpha_D10 +0.144→−0.129, ff5_alpha_D10 +0.217→−0.072).
- T1 partition: 6 zero-anchor artifacts (mean_pr, corr_bm_ior, corr_bm_roe, corr_roe_sales_g, corr_bm_pr, corr_ior_pr — bands finer than 2-decimal printing) + 8 genuine gaps (mean_age→A9 screen; std_pr→PR netting/ni denominator; std_roe→A7 no Moody's; corr_dur_bm/corr_dur_roe→terminal-term dominance; corr_dur_pr/corr_pr_sales_g/corr_pr_age→PR noise). Written to results/table_1.md + assumptions §Iteration 16.

**Replicator decision:** ACCEPT — no commit (bar failed decisively); both evidence artifacts written. Metrics unchanged; scorer stamped --iteration 4 (L = 0.2864, 471/189/41 — loss plateaued for the third consecutive iteration).

## Assumption decisions this iteration
- M1: SUE3 closed as structural (forecast-error symmetry in the 202601 vintage) — evidence in results/table_8.md + §Iteration 15.
- M2(a): V9 documented in the experiment matrix; the loss-firm-only floor is the first lever that flips the tail alphas toward the paper, but overshoots mean_D10 → not committed.
- M2(b): T1 FAIL partition (6 zero-anchor / 8 genuine) in results/table_1.md; target contract unchanged.

## Per-cell evaluation
<!-- CANONICAL scorer output: scripts/score_replication.py --iteration 4 → eval/scoring.json -->
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
Outer iteration 4 addressed both audit-3 majors with evidence: M1 (SUE3 split-consistency fix attempted; residual proven structural — forecast-error symmetry), M2 (V9 loss-firm CF probe documented, not committed; T1 FAIL partition written). Loss plateaued at 0.2864 (471/189/41) for the third consecutive iteration. Every remaining FAIL cluster now carries evidence (structural-variance, structural-forecast-symmetry, vintage-level gap, inherited-tail + convention, zero-anchor artifacts, or genuine composition gaps with attributed causes). Proceeding to audit 4.
