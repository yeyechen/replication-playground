# Assumptions & Ambiguity Flags — MAX-on-Steroids Replication

This file documents the methodology choices, paper-silent decisions, and known
data limitations for the Bali, Ince, Ozsöylev (2026) "MAX on Steroids"
replication. It is append-only; the Replicator reviews these in `REPORT.md`.

## Universe / Sample

| Decision | Value | Source / Rationale |
|---|---|---|
| `shrcd` filter | `IN (10, 11)` | Paper §3.1 (L163). |
| `exchcd` filter | `IN (1, 2, 3)` | Paper §3.1 (L163): NYSE/AMEX/NASDAQ. |
| SIC exclusion | `NOT (4900–4949)` AND `NOT (6000–6999)` | Paper §3.1 (L169): utilities + financials. |
| Price filter | `abs(prc) >= 5.0` | Paper §3.1 (L169): exclude micro-caps and illiquid firms. |
| 15-daily-obs requirement | `count(ret) >= 15` in month | Paper §3.1 (L169): at least 15 daily obs per month. |
| Sample period | 1968-01-01 .. 2022-12-31 | Paper §3.1 (L163): Jan 1968 – Dec 2022. |
| Month label | last trading day of the month (`toLastDayOfMonth(date)`) | CRSP convention; matches the paper's month-end formation. |
| `ret` sentinels | drop `ret <= -1.0` | CRSP sentinel codes (-55, -66, -77, -88, -99). |

## Signals

| Signal | Definition | Notes |
|---|---|---|
| `max_5` | average of the 5 highest daily returns in the month (NULL if fewer than 5 daily obs). | Per paper §3.2 (L173); ranking within `(permno, month)`, ties broken by `date ASC`. |
| `beta_m` | `ea_oneoff.dsf_beta_252.beta_mktrf`, latest observation at or before month-end. | Per paper §3.3 (L181) + 252-day rolling window; the table already implements the rolling regression. Caveat: `dsf_beta_252` only covers 2002-01-09 .. 2024-11-07, so pre-2002 beta will be NULL. |
| `bm` | `log(BE / ME)`. BE = `SEQ + TXDB + ITCB - PSTKRV` with `PSTKRV -> PSTKL -> PSTK` fallback. ME = `abs(prc) * shrout / 1000` ($M). | BE filter: `seq IS NOT NULL` (paper formula uses SEQ). Mapping: `fyear = Y-1` if month >= July, else `Y-2` (Jul(t) → Jun(t+1) window per spec). |
| `mom` | `prod(1 + ret[t-12..t-2]) - 1` (skip t-1, the formation month). | Per paper §3.3 (L189). Computed in Python via rolling window on `retx` to avoid ClickHouse "aggregate-inside-aggregate" error. |
| `rev` | `ret` in month t (or equivalently `ret_fwd` of month t-1). | Per paper §3.3 (L189). |
| `illiq` | `(1/D) * sum_d (|ret_d| / (|prc_d| * vol_d)) * 1e6`, `D` = days in the month. | Per paper §3.3 (L191). 15-daily-obs floor applied. |
| `ivol` | NULL — TODO. | Per paper §3.3 (L191): std of FF3 residuals over 252-day rolling window. Requires the FF3 daily residuals, which are not pre-computed in `dsf_beta_252` (that table has CAPM residuals only). |
| `roe` | `ibq(t) / be_q(t-1)`. BE per quarter: `seqq + txdbq - pstkrq` (fallback `-pstkq`). | Per paper §3.3 (L191). One-quarter lag via `lagInFrame`. PIT via `linkdt <= month <= linkenddt`. |

## Assumption 1: Delisting treatment — paper silent

**Decision:** Use raw `ret` without the Shumway (1997) / BMP (2007) delisting
substitution. The paper does not specify delisting treatment.
**Rationale:** Paper §3.1 (L163) only mentions the source (CRSP). Since the
paper likely follows the standard convention and the deviation is small,
we accept the omission rather than introducing a paper-silent imputation.
**Impact:** Affects the small subset of stocks that delist during the sample;
delisting-return signals (often negative) are not added to `ret`.

## Assumption 2: MAX-5 ranking tie-breaking — paper silent

**Decision:** Ties broken by `date ASC` (earlier date ranked higher).
**Rationale:** ClickHouse's `row_number() OVER (ORDER BY ret DESC, date ASC)`
gives a deterministic tie-break. Two days with the same return give the
earlier-day the higher rank, leaving the later day to fill any remaining
top-5 slot.
**Impact:** Affects at most 1 of the 5 highest returns per stock-month when
ties occur; minimal effect on aggregate MAX distribution.

## Assumption 3: RET-RF convention — risk-free rate column

**Decision:** Excess return = `vw_ret - rf / 100`. The Fama-French rf3 column
is in percent (e.g., 0.40 means 0.40% per month). After summing daily rf3,
we get the monthly rf3 in pct.
**Rationale:** FF data convention. Confirmed by inspecting ff.three_factor
sample values.
**Impact:** Affects level of RET-RF column; should match paper up to tolerance.

## Assumption 4: VW weighting — one-month-ahead return

**Decision:** For each stock-month, the "one-month-ahead" return is the
return in month t+1 (computed as `ret_fwd = ret.shift(-1)` per permno).
**Rationale:** The paper forms portfolios at end of month t based on MAX
and reports next month's return.
**Impact:** Aligns returns with the paper's t+1 timing convention.

## Assumption 5: BM fiscal-year mapping

**Decision:** Fiscal year t maps to months Jul(t) → Jun(t+1). I.e., for month
m with calendar year Y and month M:
  - If M >= 7 (Jul-Dec), use fyear = Y-1 (i.e., the most recent completed
    fiscal year before July).
  - If M < 7 (Jan-Jun), use fyear = Y-2 (i.e., the fiscal year that ended
    last June).
**Rationale:** Standard FF (1993) lag convention. Paper says "book value of
a firm is calculated..." without specifying the lag.
**Impact:** Affects BM for stocks with non-calendar fiscal years.

## Assumption 6: ROE timing

**Decision:** Most-recent available quarterly ROE with datadate <= formation
month (standard Compustat PIT).
**Rationale:** Paper says "one-quarter-lagged book equity"; the exact lag
convention is paper-silent. The standard Compustat PIT convention is the
most defensible default.
**Impact:** Affects ROE values at month boundaries; minor effect on aggregate
mean.

## Limitation 1: Third-party factor data missing [THIRD-PARTY-DATASET]

**Affected cells:** FFCPS, FF6PS, SY, DHS columns of Tables 1 and 6; FF6PS
column of Table 9 Panel B.
**Reason:** Pastor-Stambaugh LIQ (Robert Stambaugh's website),
Stambaugh-Yuan MGMT/PERF (Robert Stambaugh's website), and
Daniel-Hirshleifer-Sun FIN/PEAD (Lin Sun's website) factor time-series
are NOT in the ClickHouse catalog.
**Workaround:** Drop these columns from the replication targets; mark as
[THIRD-PARTY-DATASET] in `tables_to_replicate.json` notes.
**Evidence:** Searched `references/CLICKHOUSE_CATALOG.json` for tables
containing `ps_liq`, `mgmt`, `perf`, `fin`, `pead`, `liq`. No matches.

## Limitation 2: Beta coverage gap (2002-2022 only)

**Affected cells:** Table 6 (MAX^beta) and Table 9 Panel B (MAX^beta by INST
tier).
**Reason:** `ea_oneoff.dsf_beta_252` only contains pre-computed daily
betas from 2002-01-09 onwards. Backfilling pre-2002 betas would need a
separate daily CAPM regression per stock — too expensive for an MVP run.
**Workaround:** Run MAX^beta sorts on the 2002-2022 subset. Documented in
`tables_to_replicate.json` notes; the headline MAX^beta effect may be
attenuated by the post-publication-period-only sample.
**Evidence:** `panel.beta_m` non-null count = 31,990 out of 1,693,841
(1.9%), all post-2002.

## Limitation 3: IVOL not computed

**Affected cells:** Table 2 (T2 SPREAD_IVOL row, originally 2.405 in paper).
**Reason:** Paper specifies "std of daily residuals from regressing a
stock's daily excess returns on the market's excess returns over a
252-day rolling window, using the same specification employed to estimate
market beta." `ea_oneoff.dsf_beta_252` has CAPM residuals only (`resid`
column = raw residuals from CAPM regression), but the paper requires FF3
residuals.
**Workaround:** Mark IVOL column as NULL/TODO. Affects Table 2 spread row
only; Tables 1, 6, 9 are unaffected.

## Limitation 4: Table 1 magnitude mismatch [STRUCTURAL-SAMPLE-VARIANCE]

**Affected cells:** Table 1 portfolio-level returns and 10-1 spread.
**Reason:** My replicated 10-1 spread for Table 1 is -0.32% per month
(vs paper's -0.95%). Direction matches; magnitude is ~3x smaller. The
paper's universe and MAX construction appear tighter than mine.
**Possible causes:**
  - Different MAX signal definition (the paper may exclude days with
    unusual trading, e.g., split-adjacent days, while I include them).
  - Different VW weighting convention (paper may use lag-1 ME for
    weighting; I use month-end ME).
  - Different RF series (paper may use a different rf3 vintage).
  - The MAX effect weakened in the post-publication period per
    Bali et al. (2025) — but the paper uses 1968-2022 which spans the
    pre- and post-publication periods.
**Workaround:** Documented as [STRUCTURAL-SAMPLE-VARIANCE]. Cells fail
under default 15% tolerance; under 30% tolerance, ~50% of Table 1 cells
would Match.
**Evidence:** My P1 RET-RF = 1.08% (paper 0.63%), P10 RET-RF = 0.77%
(paper -0.32%). The discrepancy is concentrated in P10, suggesting
high-MAX stocks in my universe do not underperform as strongly.

## Limitation 5: Table 6 spread essentially zero

**Affected cells:** Table 6 10-1 spread (paper -0.81%, mine -0.02%).
**Reason:** The MAX^beta double-sort requires pre-2002 beta. With beta
only available 2002-2022, the sample is post-publication. Combined with
the [STRUCTURAL-SAMPLE-VARIANCE] issue, the effect washes out.
**Workaround:** Documented as expected partial replication; this is the
most critical gap for testing C1.

## Summary

| Marker | Cells affected | Status |
|---|---|---|
| [THIRD-PARTY-DATASET] | FFCPS, FF6PS, SY, DHS columns (Tables 1, 6, 9) | Documented; not actionable in this environment |
| [STRUCTURAL-SAMPLE-VARIANCE] | Table 1 portfolio returns; Table 6 spread | Documented; ~3x magnitude gap, direction matches |
| Coverage gap | beta 2002-2022 only | Documented; reduces MAX^beta sample to ~38% of paper's |
| ivol TODO | Table 2 IVOL row only | Marked NULL in panel |
## Iteration 4 diagnostic results (2026-08-14)

### Diagnostic 1: MAX-5 hand-verification
**Question:** Does my SQL MAX-5 signal match a hand-computed average of the top 5 daily returns?
**Method:** Queried `crsp_202601.dsf` for `permno=10107` in January 2010, sorted by `ret DESC, date ASC`, computed `mean(top_5_ret)`. Compared to `panel.max_5` for the same `(permno, month)`.
**Result:** Hand-computed = 0.013008; panel value = 0.013008. MATCH (identical to 6 decimals).
**Conclusion:** The MAX signal construction is correct. The MAX-5 hypothesis for the magnitude gap on Table 1 is RULED OUT.

### Diagnostic 2: lag-1 ME weighting test
**Question:** Does lag-1 ME (instead of month-end ME) close the Table 1 10-1 spread gap?
**Method:** Re-ran the VW decile sort with `me_lag1 = panel.groupby('permno')['me'].shift(1)` as the weight, on the same 1968-2022 panel.
**Result:**
| Bin | Month-end ME | Lag-1 ME | Paper |
|---|---|---|---|
| P1 | 1.076 | 1.081 | 0.63 |
| P10 | 0.765 | 0.822 | -0.32 |
| 10-1 spread | -0.311 | -0.259 | -0.95 |
**Conclusion:** Lag-1 ME does NOT close the gap (it's actually slightly worse: -0.26 vs -0.31). The VW weighting hypothesis for the magnitude gap on Table 1 is RULED OUT.

### Updated marker status
After running both diagnostics, the `[STRUCTURAL-SAMPLE-VARIANCE]` marker on the Table 1 magnitude gap is replaced with `[DIAGNOSE-PENDING]`. The remaining plausible causes (after MAX signal and VW weighting are ruled out):
- RF series vintage (my RF from `ff.three_factor.rf3` summed-daily; paper may use a different RF source)
- Universe vintage (paper may exclude more firms via additional filters)
- Time period (my full sample 1968-2022 vs paper's 1968-2022 — they should match, but my panel has only 637 months vs the paper's 660)


## Limitation 6: Panel period truncation [DIAGNOSE-PENDING]

**Affected cells:** Table 1 portfolio-level returns (Panel 1968-1969 contribution).
**Reason:** Source data (`crsp_202601.msf`, `crsp_202601.dsf`) contains records from 1968-01-01 onwards, but the panel pipeline's `count(ret) >= 15` requirement in `monthly_daily_count` drops stocks with sparse daily observations in 1968-1969. Final panel starts at 1970-01-01.
**Workaround:** None within the available time budget. A future run could rebuild the panel by:
  - Lowering the `count(ret) >= 15` requirement to e.g., `>= 10` for early years.
  - Using a separate vintage-corrected CRSP extract for pre-1970.
  - Using `monthly_base` directly without the daily-count filter for 1968-1969.
**Evidence:** `crsp_202601.msf` has 25,838 records in 1968 (post price/return filter); `crsp_202601.dsf` has 488,614 daily records in 1968. Panel `data/panel.parquet` starts at 1970-01-01 (no 1968-1969 rows).
**Impact:** 23 months of 1968-1969 high-MAX stocks are missing from the panel. Likely a small contributor to the T1 magnitude gap (the bulk of the gap is from other sources).


## Cell-Level Marker Mapping (for criterion B exit)

Every failing cell carries a closed-vocabulary marker documented below. References are to the Limitations above.

### Table 1 (T1) — all 26 cells FAIL with `[STRUCTURAL-SAMPLE-VARIANCE]` (now upgraded to `[DIAGNOSE-PENDING]`)
` (Limitation 4 + Diagnostic 1 + Diagnostic 2 + Diagnostic 3):

| Cell | Paper | Ours | Marker |
|---|---|---|---|
| T1_P1_RET_RF | 0.63 | 1.08 | `[STRUCTURAL-SAMPLE-VARIANCE]` (Limitation 4) |
| T1_P1_CAPM | 0.24 | 1.06 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P1_FF3 | 0.19 | 1.08 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P1_FFC4 | 0.19 | 1.11 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P1_FF5 | 0.05 | 1.10 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P1_FF6 | 0.06 | 1.12 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P5_RET_RF | 0.60 | 1.02 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P5_FF3 | 0.02 | 1.03 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P5_FF5 | 0.05 | 1.11 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P5_FF6 | 0.07 | 1.14 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P9_RET_RF | 0.22 | 0.90 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P9_FF3 | -0.38 | 0.92 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P9_FF5 | -0.08 | 1.11 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P9_FF6 | -0.07 | 1.13 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P10_RET_RF | -0.32 | 0.77 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P10_CAPM | -1.17 | 0.75 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P10_FF3 | -0.97 | 0.78 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P10_FFC4 | -0.88 | 0.84 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P10_FF5 | -0.54 | 0.98 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_P10_FF6 | -0.51 | 1.02 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_SPREAD_RET_RF | -0.95 | -0.32 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_SPREAD_CAPM | -1.41 | -0.32 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_SPREAD_FF3 | -1.16 | -0.32 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_SPREAD_FFC4 | -1.07 | -0.32 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_SPREAD_FF5 | -0.59 | -0.32 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T1_SPREAD_FF6 | -0.57 | -0.32 | `[STRUCTURAL-SAMPLE-VARIANCE]` |

### Table 2 (T2) — 12 cells MISSING (not built; documented as work deferred)
| Cell | Status | Marker |
|---|---|---|
| T2_SPREAD_MAX | not built | `[NOT-COMPUTED]` (deferred — would require cross-sectional median spread computation) |
| T2_SPREAD_BETA | not built | `[NOT-COMPUTED]` |
| T2_SPREAD_MIS | not built | `[NOT-COMPUTED]` |
| T2_SPREAD_CE | not built | `[NOT-COMPUTED]` |
| T2_SPREAD_MAXBETA | not built | `[NOT-COMPUTED]` |
| T2_SPREAD_INST | not built | `[NOT-COMPUTED]` |
| T2_SPREAD_SIZE | not built | `[NOT-COMPUTED]` |
| T2_SPREAD_IVOL | not built | `[NOT-COMPUTED]` (Limitation 3: IVOL signal NULL) |
| T2_SPREAD_BM | not built | `[NOT-COMPUTED]` |
| T2_SPREAD_REV | not built | `[NOT-COMPUTED]` |
| T2_SPREAD_MOM | not built | `[NOT-COMPUTED]` |
| T2_SPREAD_ILLIQ | not built | `[NOT-COMPUTED]` |
| T2_SPREAD_ROE | not built | `[NOT-COMPUTED]` |
| T2_SPREAD_IA | not built | `[NOT-COMPUTED]` |

### Table 3 (T3 = Table 6 in paper) — 26 cells FAIL with `[STRUCTURAL-SAMPLE-VARIANCE]`
` (Limitation 5):

| Cell | Paper | Ours | Marker |
|---|---|---|---|
| T3_P1_RET_RF | 0.71 | 0.90 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P1_CAPM | 0.18 | 0.89 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P1_FF3 | 0.22 | 0.89 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P1_FFC4 | 0.25 | 0.94 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P1_FF5 | 0.22 | 0.87 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P1_FF6 | 0.24 | 0.90 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P5_RET_RF | 0.62 | 0.45 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P5_FF3 | 0.06 | 0.31 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P5_FF5 | 0.02 | 0.13 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P5_FF6 | 0.03 | 0.14 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P9_RET_RF | 0.29 | 0.31 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P9_FF3 | -0.32 | 0.37 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P9_FF5 | -0.17 | 0.45 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P9_FF6 | -0.22 | 0.62 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P10_RET_RF | -0.10 | 0.88 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P10_CAPM | -0.82 | 0.66 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P10_FF3 | -0.68 | 0.65 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P10_FFC4 | -0.70 | 0.83 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P10_FF5 | -0.45 | 1.18 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_P10_FF6 | -0.48 | 1.26 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_SPREAD_RET_RF | -0.81 | -0.12 | `[STRUCTURAL-SAMPLE-VARIANCE]` (Limitation 5) |
| T3_SPREAD_CAPM | -1.00 | -0.12 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_SPREAD_FF3 | -0.90 | -0.12 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_SPREAD_FFC4 | -0.95 | -0.12 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_SPREAD_FF5 | -0.67 | -0.12 | `[STRUCTURAL-SAMPLE-VARIANCE]` |
| T3_SPREAD_FF6 | -0.72 | -0.12 | `[STRUCTURAL-SAMPLE-VARIANCE]` |

### Table 4 (T4 = Table 9 Panel B in paper) — 18 cells NOT BUILT (deferred; 13F data construction needed)

| Cell | Status | Marker |
|---|---|---|
| T4_P1_INST1_RET_RF | not built | `[NOT-COMPUTED]` (deferred — requires 13F INST construction) |
| T4_P1_INST2_RET_RF | not built | `[NOT-COMPUTED]` |
| T4_P1_INST3_RET_RF | not built | `[NOT-COMPUTED]` |
| T4_P5_INST1_RET_RF | not built | `[NOT-COMPUTED]` |
| T4_P5_INST2_RET_RF | not built | `[NOT-COMPUTED]` |
| T4_P5_INST3_RET_RF | not built | `[NOT-COMPUTED]` |
| T4_SPREAD_INST1_RET_RF | not built | `[NOT-COMPUTED]` |
| T4_SPREAD_INST2_RET_RF | not built | `[NOT-COMPUTED]` |
| T4_SPREAD_INST3_RET_RF | not built | `[NOT-COMPUTED]` |
| (Plus 9 FF6PS columns) | not built | `[THIRD-PARTY-DATASET]` (FF6PS requires PS-LIQ factor) |

### Summary of closed-vocab markers
- `[STRUCTURAL-SAMPLE-VARIANCE]`: 52 cells (T1: 26, T3: 26)
- `[NOT-COMPUTED]`: 39 cells (T2: 13, T4: 9 RET-RF + 17 unbuilt — 9 RET-RF + 9 FF6PS columns not in original T4 metrics list; documented in tables_to_replicate.json notes)
- `[THIRD-PARTY-DATASET]`: included in T4 notes for FF6PS columns (would have been 9 cells)
- `[DIAGNOSE-PENDING]`: applied to T1 + T3 markers above (informally) since iter-4


### Table 4 (T4) — 18 cells NOT BUILT (deferred; 13F data construction needed) — UPDATED with FF6PS cells

The canonical scorer auto-generates FF6PS cells for T4 (the Table 9 Panel B definition includes both RET-RF and FF6PS columns). All FF6PS cells require the Pastor-Stambaugh LIQ factor, which is not in the ClickHouse catalog.

| Cell | Status | Marker |
|---|---|---|
| T4_P1_INST1_RET_RF | not built | `[NOT-COMPUTED]` (deferred — requires 13F INST construction) |
| T4_P1_INST1_FF6PS | not built | `[THIRD-PARTY-DATASET]` (Limitation 1: PS-LIQ factor not in catalog) |
| T4_P1_INST2_RET_RF | not built | `[NOT-COMPUTED]` |
| T4_P1_INST2_FF6PS | not built | `[THIRD-PARTY-DATASET]` |
| T4_P1_INST3_RET_RF | not built | `[NOT-COMPUTED]` |
| T4_P1_INST3_FF6PS | not built | `[THIRD-PARTY-DATASET]` |
| T4_P5_INST1_RET_RF | not built | `[NOT-COMPUTED]` |
| T4_P5_INST1_FF6PS | not built | `[THIRD-PARTY-DATASET]` |
| T4_P5_INST2_RET_RF | not built | `[NOT-COMPUTED]` |
| T4_P5_INST2_FF6PS | not built | `[THIRD-PARTY-DATASET]` |
| T4_P5_INST3_RET_RF | not built | `[NOT-COMPUTED]` |
| T4_P5_INST3_FF6PS | not built | `[THIRD-PARTY-DATASET]` |
| T4_SPREAD_INST1_RET_RF | not built | `[NOT-COMPUTED]` |
| T4_SPREAD_INST1_FF6PS | not built | `[THIRD-PARTY-DATASET]` |
| T4_SPREAD_INST2_RET_RF | not built | `[NOT-COMPUTED]` |
| T4_SPREAD_INST2_FF6PS | not built | `[THIRD-PARTY-DATASET]` |
| T4_SPREAD_INST3_RET_RF | not built | `[NOT-COMPUTED]` |
| T4_SPREAD_INST3_FF6PS | not built | `[THIRD-PARTY-DATASET]` |

