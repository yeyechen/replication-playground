---
iteration: 2
slug: novymarx_2012_is_momentum_really_momentum
inner_iterations: 2
worker_spawns: 2
---

# Outer Iteration 2 — Reasoning Trace

**Briefing:** audit 1 (`logs/audit1.md`) returned verdict REPLICATED with `requires_iteration: true` and one actionable major. **Conventions applied this iteration:** none new — one existing convention CORRECTED (Assumption 9) on textual + multi-cell empirical evidence; `[CONVENTION-APPLIED]`/`[CONVENTION-SKIPPED]` inventory unchanged from iteration 1. Headline tally (canonical scorer, `eval/scoring.json` iteration 2): **428 Match / 45 FAIL / 0 MISSING / 67 no_effect, L = 0.0951** (iteration 1: 422/51/67, L = 0.1078).

## Inner iteration 1: [M1] breakpoint-convention robustness run
**Task spec → rep-worker:** Recompute Table 7 within-size-quintile momentum (Panels B–E) and the Table 6 conditional 6-2 grid under unconditional-NYSE inner breakpoints as a report-only variant; thin-cell diagnostics; no committed-metric changes.
**rep-worker report:** Variant closes the two open cells: pc_m62_q5 0.07 [0.49] → 0.36 [2.01] vs paper 0.40 [2.25]. Simultaneous alignment across independent cells: Panel D m62 q5 0.16 [0.66] vs paper 0.16 [0.68]; T5 er_cond62 grid 0.26/0.15/0.14/0.41/0.46 vs paper 0.26/0.26/0.29/0.39/0.49 (q1 exact); Panels B/E q5 improve. No thin cells (all series full-length).
**Replicator decision:** ADOPT the unconditional-NYSE convention — textual evidence (Table 7 note: "Portfolio break points based on NYSE stocks only", L1701 — covers all breakpoints in the table; "constructed within" refers to membership, not breakpoint computation) plus the multi-cell discriminating test. Assumption 9 corrected with a dated correction note; the within-subsample variant retained as the reported robustness alternative.

## Inner iteration 2: adoption re-run
**Task spec → rep-worker:** Make `inner_mode="uncond"` the default for T5/T6; swap robustness-section roles; re-run; verify no movement outside T5/T6.
**rep-worker report:** Exactly 120 metric values changed, all in T5/T6. T5 20/6/14 → 22/4/14; T6 95/5/5 → **99/1/5** (pc_m62_q5, pc_m62_q5_t, pe_m62_q1_t, pe_m62_q5_t flip to Match). New FAILs: alpha_cond127_q2_t, alpha_cond62_q2_t (near-zero t-cells of paper-insignificant estimates — Family B). Remaining FAILs: er_cond62_q3_t, alpha_cond127_q3_t (T5), pe_m62_q4_t (T6) — all Family B.
**Replicator decision:** ACCEPT. Canonical scorer run in write mode (`--iteration 2`): 428/45/67, L = 0.0951. Residue section corrected (no open cells; Family B 33→27; totals A 10 + B 27 + C 8 = 45). Audit point 4.2 addressed in REPORT.md (significance category now significant-to-significant for pc_m62_q5).

## Assumption decisions this iteration
- Assumption 9 CORRECTED (unconditional-NYSE inner breakpoints) — dated correction appended to the original entry, impact lines annotated; not silently overwritten.

## Per-cell evaluation
Canonical scorer output (`eval/scoring.json`, iteration 2):

```
status counts: Match 428 | FAIL 45 | MISSING 0 | no_effect 67 | skip 0
loss L = 0.0951   n_committed = 473   n_cells = 540
per_table: T1 29/1/6 · T2 39/12/3 · T3 62/6/10 · T4 91/9/23 ·
           T5 22/4/14 · T6 99/1/5 · T7 20/2/2 · T8 66/10/4
```

FAIL cells (45): unchanged from iteration 1 in T1/T2/T3/T4/T7/T8 (43 cells — Families A/B/C as documented); T5 now `er_cond62_q3_t, alpha_cond127_q2_t, alpha_cond127_q3_t, alpha_cond62_q2_t`; T6 now `pe_m62_q4_t`. Every name carries evidence in assumptions.md § Documented residue (+ iteration-2 correction note).

## Summary
The audit's single actionable major is resolved with a tested convention correction that closes both open cells and improves six additional cells; no other table moved. All FAIL residue is now in three evidenced families (A: 10 vintage cells; B: 27 near-zero t-cells; C: 8 tested-but-unresolved SUE cells). No open, untested cells remain. Loss improved 0.1078 → 0.0951.
