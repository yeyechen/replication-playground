---
iteration: 2
slug: graves_2025_what_lies_beneath_zero_censoring_demand_estimation_and_hidden_belief
verdict: FAILED
overall: 2.00
blocker_count: 1
actionable_major_count: 1
requires_iteration: false
generated_at: 2026-08-14T15:30:00Z
---

# Audit — Outer Iteration 2

**Auditor:** independent peer review of `graves_2025_what_lies_beneath_zero_censoring_demand_estimation_and_hidden_belief`, iteration 2.
**Rubric reference:** `audit/RUBRIC.md` v1.

## State of the replication at iteration 2

- **Match / n_committed:** 6 of 23 = 26.1% (Match=6, FAIL=0, MISSING=17, SKIP=0). Six evaluated Table 1 cells (Num Inst + Tot Inst AUM, three periods) match the paper within ±20%; the remaining 17 cells across Tables 2/3/4/6 are MISSING and flagged `[COMPUTE-INFEASIBLE]`.
- **Iteration 2 deliverables (per `logs/log2.md`):**
  1. **Rigid/dynamic classification** — implemented in Python against a cached `top500_holdings.parquet` (resolve prior audit `[M2]`). 21,867 `(mgrno, q)` classified (52 rigid / 21,815 dynamic ≈ 0.2% rigid). Top-500 Table 1 produced with rigid/dynamic columns.
  2. **Documentation inconsistency** — `candidate_assessment.json` aligned with `data_verification.json` (resolve prior `[M3]`).
  3. **SCQR feasibility study** — attempted on top-10 institutions × 2020Q4 only; explicitly deferred to `[COMPUTE-INFEASIBLE]` in this iteration.
- **Headline signal (audit `[B1]`)** — still not tested. The HBI long-short alpha of 8.50% / t-stat 9.27 (Table 4) requires the full SCQR pipeline (~25M LP solves) and remains compute-infeasible in a single session.

## Issue list

### Blocker (`[B*]`)

- **`[B1] SCQR / HBI / OBI pipeline compute-infeasible (carry-over, NEW evidence this iteration).`** Paper's Section 5 requires SCQR estimation across ~247,997 institution-quarter pairs × ~100 LP solves each (~25M LP solves total). Iteration 2's feasibility study on top-10 × 1 quarter confirms the methodology stack is implementable but does not change the per-institution cost. Tables 3/4/6 cells (the paper's headline signal) remain MISSING. Documented with `[COMPUTE-INFEASIBLE]` markers in `preparations/assumptions.md` (A1, A6, A11, A15).

### Actionable major (`[M*]`)

- **`[M4] Top-500 sub-sample is not a faithful cell match for paper Table 1.** Iteration 2 produced a top-500 Table 1, but the four cells in `logs/log2.md` (2013-2016 Num Inst=467 vs paper 3,733; Tot Inst AUM=$53,037B vs paper $14,000B; Dynamic AUM=$53,008B vs paper $1,248B; Rigid AUM=$29B vs paper $51B) are FAIL-on-sub-sample, not Match. The top-500 table cannot be evaluated against paper Table 1 cells without a `[SUBSAMPLE]` scope tag in `tables_to_replicate.json`. Currently these cells are not committed to `eval/scoring.json`, so they do not affect the match rate — but they should either be (a) committed with `[SUBSAMPLE]` markers or (b) clearly labeled as a feasibility artifact only, not a score-contributing output.

### Resolved since iteration 1

- **`[M2]` Rigid/dynamic classification** — RESOLVED. Python implementation against cached top-500 holdings. Code: `src/classify_rigid_dynamic.py`. Artifact: `data/manager_classification.parquet`. Result table: `results/table_1_top500.md`.
- **`[M3]` Documentation inconsistency (`data_sources` vs Compustat annual)** — RESOLVED. `candidate_assessment.json` aligned with `data_verification.json`.

### Cosmetic / minor

- The 2010-2012 row appears in `results/table_1_partial.md` (3226 institutions, $10,447B) but is not committed in `tables_to_replicate.json` (which only includes periods the paper reports). Iteration 1's logs mention `n_skip=1` for 2010-2012 but `eval/scoring.json` shows `n_skip=0`. This is cosmetic drift between log narrative and the canonical scoring artifact; it does not affect match rate but should be reconciled if the artifact is re-emitted.

## Per-dimension scoring (rubric)

| Dimension | Score | One-line justification |
|---|---:|---|
| Methodology | 3 | Universe/filter/≥25-holdings rules faithful; SCQR cannot be audited. Two of eight sub-checks verifiable. |
| Headline matching | 1 | HBI long-short alpha 8.50% / t-stat 9.27 (Table 4): zero cells attempted. |
| Data coverage | 4 | Catalog full; sub-period 2010Q1–2021Q4 (~67% of paper window); universe construction validated. |
| Concrete result | 2 | Match rate 26.1% (6/23 committed cells); all 6 attempted cells match. Band maps to 1, lifted to 2 by infra-validated matches. |
| Signal strength | 1 | No headline cell has a value; cannot compute any r = \|replicated/paper\|. |
| Corollary | 1 | All corollary cells (subsamples, OBI null, persistence) are MISSING. |

**Overall = (3+1+4+2+1+1) / 6 = 12 / 6 = 2.00.**

**Bright line:** `overall = 2.00 < 3.0` AND three dimensions = 1 → FAILED. Kill switch triggered.

## Verdict and loop control

- **Verdict:** FAILED.
- **Blocker count:** 1 (`[B1]` SCQR compute-infeasibility).
- **Actionable major count:** 1 (`[M4]` top-500 sub-sample not committed/labeled).
- **requires_iteration:** false. The replicator has correctly applied the documented-residue exit criterion (`rep/LOSS_FUNCTION.md` criterion B): every remaining MISSING cell is evidenced with a `[COMPUTE-INFEASIBLE]` marker and a per-affected-cell count. The methodology that *can* be exercised (data pipeline, Table 1 partial, top-500 classification) has been exercised and matches. The headline signal requires distributed compute that is outside this harness.

## What to commit / acknowledge if iteration 3 is forced

The replicator chose EXIT LOOP. If a future iteration is forced (e.g., compute budget opens up), the following prompts are the priority queue:

1. **Top-500 sub-sample scoping:** either commit top-500 cells to `eval/scoring.json` with `[SUBSAMPLE]` flag and `n_committed` correction, or explicitly remove `results/table_1_top500.md` from "results" to a "feasibility/" subfolder so it cannot be misread as a committed deliverable.
2. **SCQR sub-sample feasibility:** the iteration-2 top-10 × 1-quarter attempt is in `logs/log2.md` as "In-progress" but no code artifacts are committed. Either complete and commit `src/scqr_pipeline.py` + a `results/hbi_top10_2020Q4.csv` artifact, or formally close with `[DEFERRED]` in `assumptions.md`.

The headline HBI/OBI tables are not actionable in this harness.

---

## Copy-paste next-iteration prompt

```
You are continuing the replication of Graves (2025) "What Lies Beneath Zero:
Censoring, Demand Estimation, and Hidden Beliefs" in
`replications/graves_2025_what_lies_beneath_zero_censoring_demand_estimation_and_hidden_belief/`.

This is outer iteration 3. The current state:
- 6 of 23 cells Match (Table 1 partial); 17 cells MISSING with
  `[COMPUTE-INFEASIBLE]` markers.
- Iteration 2 added rigid/dynamic classification for top-500 institutions
  (resolved prior `[M2]`) and fixed a documentation inconsistency
  (resolved prior `[M3]`).
- The headline signal (audit `[B1]`, HBI long-short alpha 8.50% / t-stat
  9.27 from Table 4) remains compute-infeasible.
- The replicator exited iteration 2 per documented-residue criterion B.

Read these before starting:
- `REPORT.md` (full state and limitations)
- `logs/log1.md` and `logs/log2.md` (iteration traces)
- `logs/audit2.md` (this audit, with full issue list)
- `preparations/assumptions.md` (every documented substitution)

Iteration 3 scope — only the items below are actionable; do NOT re-attempt
the full SCQR pipeline:

1. **`[M4]` Top-500 sub-sample scoping.** The artifact
   `results/table_1_top500.md` exists but its cells are not committed to
   `eval/scoring.json`. Pick one:
   (a) Commit the four top-500 cells with `[SUBSAMPLE]` flag in
       `eval/scoring.json` AND a corresponding `tolerance_pct` field per
       cell, AND update `tables_to_replicate.json` with a top-500 scope
       record; OR
   (b) Move `results/table_1_top500.{csv,md}` to
       `results/feasibility/` (NOT under `results/`) so it is visibly
       a feasibility artifact, not a committed deliverable.
   Pick (a) if you intend to claim any score from the top-500 work;
   pick (b) if it was strictly a feasibility study for `[M2]`.

2. **`[M4-followup]` SCQR feasibility closure.** Either complete and
   commit the top-10 × 2020Q4 SCQR pipeline (write
   `src/scqr_pipeline.py`, produce `results/hbi_top10_2020Q4.csv`,
   document any LP solver used) or formally mark the entry
   `[DEFERRED]` in `preparations/assumptions.md`. `logs/log2.md`
   currently says "In-progress" — close it.

3. **Reconcile cosmetic drift.** Iteration-1 logs reference `n_skip=1`
   for the 2010-2012 period; `eval/scoring.json` shows `n_skip=0`.
   Either add the 2010-2012 row to `tables_to_replicate.json` (with
   `tolerance_pct` and `group`) or remove the 2010-2012 row from
   `results/table_1_partial.md`.

Do NOT:
- Re-attempt the full SCQR pipeline (audit `[B1]` is hard-blocked on
  compute, not methodology — see `preparations/assumptions.md` A15).
- Expand the time period beyond 2010Q1–2021Q4 (audit decision recorded
  as documented residue).
- Re-run any cell that already shows Match unless the data pipeline
  changes.

Output at end of iteration 3:
- Updated `eval/scoring.json` (if you took option 1a or option 3).
- Updated `results/table_1_top500.{csv,md}` location or commit status.
- A new `logs/log3.md` with the iteration trace.
- A re-emitted `REPORT.md` (only if cells or tables changed).
- A re-emitted `eval/metrics.json` reflecting the new state.
```