---
schema_version: 2
slug: graves_2025_what_lies_beneath_zero_censoring_demand_estimation_and_hidden_belief
iteration: 2
verdict: FAILED
overall: 1.83
methodology: 3
headline_matching: 1
data_coverage: 4
concrete_result: 1
signal_strength: 1
corollary: 1
generated_at: 2026-08-14T15:30:00Z
---

# Replication Summary — Iteration 2

## What Lies Beneath Zero: Censoring, Demand Estimation, and Hidden Beliefs — Graves (2025)

### Bottom line

**Replication result:** `FAILED`
**Overall quality:** 1.83 / 5.00

The paper's central empirical claim — that the Hidden Beliefs Index (HBI) long-short annualized four-factor alpha is 8.50% (t-stat 9.27, Newey-West) and predicts returns monotonically across size deciles — was not tested by this replication. SCQR estimation across ~247,997 institution-quarter pairs requires ~25M LP solves; the agent executed only the data pipeline, Table 1 partial, and (iteration 2) a top-500 rigid/dynamic classification feasibility study. All 6 evaluated Table 1 cells (Num Inst + Tot Inst AUM for 2013-2016, 2017-2020, 2021) match the paper within ±20% tolerance. Tables 3, 4, and 6 — the 17 cells that test the headline claim — are MISSING and flagged `[COMPUTE-INFEASIBLE]`. The replicator correctly applied the documented-residue exit criterion and closed the outer loop.

### Iteration 2 changes from iteration 1

| Audit item (iter 1) | Resolution (iter 2) | Evidence |
|---|---|---|
| `[M2]` Rigid/dynamic classification deferred | **RESOLVED** | `src/classify_rigid_dynamic.py`; 21,867 `(mgrno, q)` classified (52 rigid / 21,815 dynamic); `data/manager_classification.parquet`; `results/table_1_top500.md`. |
| `[M3]` Documentation inconsistency (`data_sources` said "Compustat Quarterly" but table is `funda` annual) | **RESOLVED** | `preparations/candidate_assessment.json` aligned with `data_verification.json`. |
| `[B1]` SCQR pipeline compute-infeasible (headline signal) | **NOT RESOLVED** (carry-over blocker) | Top-10 × 2020Q4 feasibility study attempted in `logs/log2.md` as "in-progress"; no committed artifact. Documented in `preparations/assumptions.md` A1, A6, A11, A15 with `[COMPUTE-INFEASIBLE]` markers. |
| `[M4]` Top-500 sub-sample not committed/labeled | **NEW (iter 2)** | `results/table_1_top500.md` cells not in `eval/scoring.json` — neither committed-with-flag nor moved to feasibility/. |

### Quality assessment

| Dimension | Score | Assessment |
|---|---:|---|
| Methodology | 3/5 | Data pipeline (ClickHouse SQL) implemented faithfully; universe filter (shrcd 10/11, exchcd 1/2/3, ≥25 holdings) correct; FF2015 conventions, book-equity formulas, and Jaccard similarity choice all documented. SCQR estimation, HBI/OBI construction, factor regression, three-lag averaging, size-decile construction — none exercised; cannot audit. |
| Headline matching | 1/5 | The single headline number is the HBI long-short annualized alpha of 8.50% / t-stat 9.27 (Table 4). Zero cells testing it were attempted. |
| Data coverage | 4/5 | All required catalog tables (`tr_13f_202401.s34`, `s34names`, `crsp_202601.{dsf,msf}`, `comp_202601.funda`, `ccmxpf_linktable`) are `full`; period is truncated to 2010Q1–2021Q4 (~67% of paper's 1984Q4–2021Q4 window); ≥25-holdings universe implemented and validated; conventions documented. |
| Concrete result matching | 1/5 | Match rate = 6 / 23 = 26.1% (Match=6, FAIL=0, MISSING=17, SKIP=0). Per `audit/RUBRIC.md`, score 1 if Match rate <30% — band maps to 1 mechanically. |
| Signal strength | 1/5 | All headline cells (paper Tables 3, 4, 6) are MISSING; cannot compute any `r = |replicated/paper|` value. |
| Corollary | 1/5 | Paper corollaries (subsample stability by institution type, multi-quarter HBI persistence, OBI null pattern, robustness to alternative consideration sets) all depend on HBI/OBI construction that was not exercised; no corollary cells computed. |

### Table-level evidence (concrete)

| Paper output | Replicated? | High-level evidence | What it supports |
|---|---|---|---|
| Table 1 — Num Inst + Tot Inst AUM (3 periods, 6 cells) | **6 / 6 MATCH** | 2013-2016: 4002 vs 3733, $15,232B vs $14,000B; 2017-2020: 5231 vs 4752, $19,755B vs $20,587B; 2021: 4838 vs 5970, $28,658B vs $31,962B. Rel-err 4–19%, within ±20% tolerance. | Data infrastructure works: 13F panel is correct, ≥25-holdings filter correctly applied, AUM aggregation matches paper magnitudes. |
| Table 1 — Rigid/Dynamic AUM cells (top-500 sub-sample) | **NOT COMMITTED** | `results/table_1_top500.md` shows 2013-2016 rigid=$29B, dynamic=$53,008B; 2017-2020 rigid=$12B, dynamic=$69,933B; 2021 rigid=$0, dynamic=$31,844B. Top-500 sub-sample is not a faithful cell match for paper Table 1. | Methodology proof-of-concept for `[M2]`; not a score-contributing deliverable. |
| Table 2 — Consideration sets & holdings (9 cells) | MISSING | `[COMPUTE-INFEASIBLE]` — requires NAICS-4 expansion + rigid/dynamic classification. | Not tested. |
| Table 3 — Size × HBI quintile portfolio alphas (3 cells) | MISSING | `[COMPUTE-INFEASIBLE]` — requires full SCQR + HBI + sort + FF4 factor regression. | Headline monotonic-direction claim not tested. |
| Table 4 — HBI long-short by size decile (3 cells) | MISSING | `[COMPUTE-INFEASIBLE]` — depends on Table 3 portfolios. | **Headline alpha/t-stat not tested** (8.50% / t = 9.27 lives here). |
| Table 6 — Size × OBI quintile portfolio alphas (2 cells) | MISSING | `[COMPUTE-INFEASIBLE]` — same pipeline as Table 3 but uses overt beliefs. | OBI-null-spread corollary not tested. |
| Tables 5, 7–13 | OUT OF SCOPE | Not committed in `tables_to_replicate.json` (Table 5) or excluded (7–13). | Not tested. |

### Important limitations

1. **Compute-infeasible core.** The headline claim rests on the full SCQR pipeline (~25M LP solves ≈ ~250 days single-thread, or 30+ days on a 32-core node with HiGHS/ECOS). Within a single replication session this is not tractable. This is the dominant reason this is FAILED. Documented in `preparations/assumptions.md` A1, A6, A11, A15 with `[COMPUTE-INFEASIBLE]` markers.
2. **Sub-period substitution.** Sub-period 2010Q1–2021Q4 (~12 years) replaces paper's 1984Q4–2021Q4 (~37 years). The institutional ownership regime in 1984–2009 is materially different.
3. **Universe-filter silence.** Paper says "common stocks" without specifying CRSP share codes; replication applies standard convention (shrcd 10/11).
4. **Rigid/dynamic classification only on top-500.** Full-sample 12-quarter self-join (320K × 12 ≈ 3.8M join rows) is rejected on ClickHouse timeout; iteration 2's Python implementation against the cached top-500 parquet is tractable but covers ~80% of AUM not ~100%.
5. **L1 weight-stability criterion (Definition 1, criterion 2) not implemented.** Only criterion 1 (overlap ≥95%) was applied. See `preparations/assumptions.md` A16.
6. **No backtest.** Tables 3, 4, 6 cannot be replicated without the SCQR pipeline.
7. **Manager-type sub-analyses (paper §8).** TR s34 `typecode` join is set up but not used in any committed table.
8. **Iteration-2 SCQR feasibility (top-10 × 2020Q4) is logged as "in-progress" but not committed.** Either complete it or formally mark `[DEFERRED]` in `assumptions.md`.

### Score summary

| Dim | Score | Why |
|---|---:|---|
| methodology | 3 | Partial: universe/infrastructure rules faithful; SCQR cannot be audited. |
| headline_matching | 1 | HBI alpha / t-stat headline not tested. |
| data_coverage | 4 | Catalog full; period truncated to ~67% of paper window. |
| concrete_result | 1 | Match rate 26.1% (6 of 23 committed cells); per rubric, <30% maps to band 1. 6/6 attempted cells match within ±20%. |
| signal_strength | 1 | No headline cell has a value. |
| corollary | 1 | No corollary computed. |

**Verdict = FAILED:** overall = 1.83 < 3.0 AND four dimensions = 1 (kill-switch triggered: headline_matching, signal_strength, corollary, concrete_result).

The replicator correctly applied the documented-residue exit criterion (`rep/LOSS_FUNCTION.md` criterion B): every remaining MISSING cell is evidenced with a `[COMPUTE-INFEASIBLE]` marker. The methodology that *can* be exercised has been exercised and matches. The headline HBI/OBI signal requires distributed compute that is outside this harness.

## What replicated and what it validates

**Replicated (data infrastructure):** Table 1 partial (6 of 6 attempted cells). This validates that:
- The ClickHouse 13F institutional holdings data covers the paper's sample correctly (320,434 institution-quarter rows for sub-period 2010-2021).
- The ≥25-holdings minimum filter is correctly applied.
- AUM aggregation by paper's period windows produces paper-comparable magnitudes.
- The top-500 institution set can be classified as rigid vs dynamic (52 rigid / 21,815 dynamic = 0.2% rigid, broadly consistent with paper's expectation that most institutional AUM is in dynamic mandates).

**Not replicated (central empirical claim):** The HBI long-short annualized alpha of 8.50% / t-stat 9.27. This requires the full SCQR pipeline (~25M LP solves), which is compute-infeasible within a single replication session. Documented with `[COMPUTE-INFEASIBLE]` markers per cell.

## Important gaps

- **Compute-infeasibility of the headline signal.** This is the dominant gap. The paper's HBI long-short alpha / t-stat cannot be replicated without running ~25M LP solves (multi-day distributed compute).
- **Sub-period substitution.** 2010Q1-2021Q4 (~67% of paper's full 1984-2021 sample). The HBI signal may behave differently in the earlier period due to different institutional ownership regime.
- **Rigid/dynamic only on top-500 sub-sample.** Full-sample 12-quarter self-join is too expensive; iteration 2's Python implementation covers ~80% of AUM not 100%.
- **L1 weight-stability criterion (Definition 1, criterion 2) not implemented.** Only overlap ≥95% criterion applied. Paper's full Table 1 Rigid AUM uses both criteria.
- **Tables 2 (consideration set statistics), 5 (lag persistence), 7-13 (robustness, mutual fund) all out of scope.** Either require NAICS-4 expansion (Table 2), additional SCQR runs (Table 5, 7), or alternative datasets (Tables 8-13).
- **Manager-type sub-analyses (paper §8) not implemented.** TR s34 `typecode` join is set up but not used in any committed table.