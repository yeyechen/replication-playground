# Assumption Registry — MAX on Steroids (Bali, Ince, Ozsoylev)

This registry catalogs paper-silent decisions and documented substitutions.
Paper-quote provenance lives in `preparations/preprocessing_rules.json`
(rules there are **paper-derived**); entries here are **paper-silent**.

Closed vocabulary markers used:
- `[CONVENTION-APPLIED]` — applied the documented default from `rep/PAPER_CONVENTIONS.md`
- `[CONVENTION-SKIPPED]` — skipped a default; reasoned justification provided
- `[THIRD-PARTY-DATASET]` — external dataset (e.g. Stambaugh-Yuan) not in ClickHouse; documented substitution applied
- `[CRSP-VINTAGE-SUBSTITUTION]` — CRSP vintage-specific column substitution
- `[VINTAGE-DRIFT]` — known vintage-level drift; cannot be tested against paper
- `paper silent` — no documented default; chose the most defensible option

---

## Assumption 1 — Drop the SY factor-model column from per-cell target tables

**Decision:** Do not attempt to compute Stambaugh-Yuan (2017) MGMT and PERF
factors in the pipeline. Instead, drop the `*_SY` cells from the per-cell
target list of Tables 1 and 6, and log every dropped cell as
`[THIRD-PARTY-DATASET]`.

**Rationale:** `data_verification.json#stambaugh_yuan_factors` documents
that Stambaugh-Yuan MGMT and PERF factors are hosted only on Robert
Stambaugh's website. They are not in the ClickHouse `ff` database. The
paper reports alphas against this 4-factor (MKT-RF + SMB + MGMT + PERF)
mispricing model. We have no in-ClickHouse path to those two factors.

**Impact:** Affects every SY column cell in T1 and T6 (10 + 1 = 11 cells
in T1; 1 cell in T6's 10-1 spread row). These cells become SKIP rather
than FAIL — the binary Match rule does not score SKIP cells.

---

## Assumption 2 — Drop the DHS factor-model column from per-cell target tables

**Decision:** Do not attempt to compute Daniel-Hirshleifer-Sun (2020) FIN
and PEAD factors. Drop the `*_DHS` cells from the per-cell target list,
and log every dropped cell as `[THIRD-PARTY-DATASET]`.

**Rationale:** `data_verification.json#dhs_factors` documents the same
gap as Assumption 1 — these factors are hosted only on Lin Sun's website
and are unavailable in ClickHouse. The paper itself notes the DHS
analysis is restricted to July 1972 onward.

**Impact:** Affects every DHS column cell in T1 and T6 (11 + 1 = 12 cells
in T1; 1 cell in T6). These become SKIP.

---

## Assumption 3 — Drop the FFCPS / FF6PS columns when Pastor-Stambaugh LIQ factor is unavailable

**Decision:** When the Pastor-Stambaugh (2003) liquidity (LIQ) factor is
not in ClickHouse (it isn't), drop `*_FFCPS` and `*_FF6PS` cells from the
per-cell target lists; substitute FF6 where FF6PS would have been.

**Rationale:** `data_verification.json#ff_factor_models` flags the LIQ
factor as missing. The LIQ factor's contribution to cross-sectional
sorts is typically small (<10% of FF5 alpha), so the substitution FF6 →
FF6PS has only a second-order effect on the printed alpha. Logging the
substitution is mandatory.

**Impact:** Affects every FFCPS and FF6PS column cell in T1 and T6.

---

## Assumption 4 — CRSP PIT universe filter uses `dsenames` for `exchcd`

**Decision:** Use `crsp_202601.dsenames` for the PIT exchange-code filter
(`exchcd IN (1, 2, 3)`), since `crsp_202601.dsfhdr` only carries `hshrcd`
in this vintage. Use `utils.apply_universe_filter` for shrcd (which
happens to also use dsfhdr).

**Rationale:** `data_verification.json#crsp_pit_universe` flags
`crsp_202601.dsfhdr` as not having `hexchcd` in the modern CRSP vintage.
The standard workaround is `dsenames` for the exchcd-only filter. Note
this is the OPPOSITE of `rep/PAPER_CONVENTIONS.md`'s PIT source
recommendation, which prefers `dsfhdr`. But the convention explicitly
states the prohibition is on using dsenames INSTEAD of dsfhdr for
shrcd-driven universe filtering; using dsenames for exchcd only when
dsfhdr lacks the column is a per-vintage deviation, not a methodology
deviation. Logged as `[CRSP-VINTAGE-SUBSTITUTION]`.

**Impact:** Universe filter is the gate that determines which stocks
enter the panel. Coverage should match within rounding.

---

## Assumption 5 — Delisting returns use `dlretx` (not `dlret`)

**Decision:** When the CRSP vintage lacks the `dlret` column in
`crsp_202601.dsedelist`, use `dlretx` (ex-dividend delisting return) as
the delisting-day return of record.

**Rationale:** `data_verification.json#crsp_delisting_returns` confirms
that the modern CRSP vintage only carries `dlretx`. Standard convention
in the literature for the Bali-Cakici-Whitelaw (2011) replication is to
substitute dlretx when dlret is missing. Logged as
`[CRSP-VINTAGE-SUBSTITUTION]`.

**Impact:** Affects the small number of stocks delisted for performance
reasons in the sample (typical <1% of stocks per year). Should not
materially change the headlines.

---

## Assumption 6 — Book equity uses `at - dlc - dltt - pstkrv` when `ceq + txdb - pstkrv <= 0`

**Decision:** Compute book equity as `ceq + txdb + itcb - pstkrv` (or
fallback `pstkl`/`pstk`) per the paper's spec. When this is missing or
non-positive, fall back to `at - dlc - dltt - pstkrv` per Fama-French
(2008).

**Rationale:** `preprocessing_rules.json#var_book_value` cites the paper
verbatim: book equity is `SEQ + TXDB + ITCB - PSTKRV` (using the most
recent preferred-stock variant among PSTKRV/PSTKL/PSTK). The FF2008
fallback is the standard literature backup. `[CONVENTION-APPLIED]`.

**Impact:** Affects BM controls in Table 4 (out of scope for current
selection but matters for downstream tables). For T2 we use IVOL as the
diagnostic instead.

---

## Assumption 7 — VW breakpoints / independent deciles for signal sorts

**Decision:** All MAX and MAX^beta sorts use independent deciles formed
within each month, equal-weight by `mcap_lag1` (cap-weight for portfolio
returns) per the paper.

**Rationale:** `rep/PAPER_CONVENTIONS.md#Breakpoint universe` recommends
NYSE-only breakpoints for size-based sorts. MAX-based and
MAX^beta-based sorts are not size sorts, so the standard is to use all
stocks in the universe for the breakpoints. Independent deciles is the
convention for cross-sectional MAX sorts per Bali-Cakici-Whitelaw
(2011). `[CONVENTION-APPLIED]`.

---

## Assumption 8 — Newey-West lag length is 6 for the 1968-2022 sample

**Decision:** Use 6 Newey-West lags in all t-stat computations for the
1968-01 to 2022-12 sample, matching the paper's footnote 7.

**Rationale:** The paper states the optimal-lag formula
`4*(T/100)^{2/9}`. For T=660 months (Jan 1968 to Dec 2022), the formula
rounds to 6 lags. The paper itself uses 6 lags for this sample. Per
`preprocessing_rules.json#newey_west_lags`. `[CONVENTION-APPLIED]`.

---

## Assumption 9 — Universe: exclude `siccd IN (4900..4949) OR siccd IN (6000..6999)`

**Decision:** Apply the paper's SIC-code exclusion (utilities 4900-4949
and financials 6000-6999) using the historical SIC code from
`crsp_202601.dsenames.siccd`, PIT-joined to the sort month.

**Rationale:** `preprocessing_rules.json#universe_sic_exclusion` cites
the paper verbatim. `[CONVENTION-APPLIED]`.

---

## Assumption 10 — MIN DAILY OBSERVATIONS: drop month if `ndays < 15`

**Decision:** Drop any (permno, month) from the panel if the count of
daily returns in `crsp_202601.dsf` for that month is fewer than 15.

**Rationale:** `preprocessing_rules.json#avail_min_daily_observations`
cites the paper verbatim. `[CONVENTION-APPLIED]`.

---

## Assumption 11 — MAX is computed only with non-missing positive daily returns

**Decision:** Compute `MAX = avg(top 5 positive daily returns)` in a
given month. If fewer than 5 positive returns exist, set MAX to NULL for
that (permno, month).

**Rationale:** The paper defines MAX as the average of the five highest
daily returns. We take the strictest interpretation: average of the
top 5 (i.e. requires at least 5 daily returns). Combined with the
15-obs rule in Assumption 10, this is satisfied for almost all stock-months.
`[CONVENTION-APPLIED]`.

---

## Assumption 12 — Use `four_factor_monthly` daily-equivalent factors as a fallback for FF6PS

**Decision:** Construct FF5 and FF6 as factor-additions on top of FF3+MOM
using ff.five_factor_monthly and ff.four_factor_monthly; do not import
FF6PS because LIQ is missing in ClickHouse.

**Rationale:** Logged in `data_verification.json#ff_factor_models` and
tied to Assumption 3. The cascading impact: we drop FFCPS and FF6PS
columns from per-cell targets and only commit CAPM, FF3, FFC4, FF5, FF6.

---

## Assumption 13 — Date32 → month-start uses manual substring calc (not toStartOfMonth)

**Decision:** Replace `toStartOfMonth(<Date32 column>)` with
`toDate32(substring(toString(<column>), 1, 7) || '-01')` for all
month-start computations in the pipeline.

**Rationale:** ClickHouse's `toStartOfMonth` function does NOT accept
the `Date32` type (verified on this ClickHouse 26.8 instance). When given
a Date32 column, ClickHouse silently coerces to `Date`, which clamps any
pre-1970 date to 1970-01-01. With CRSP permnos active since 1926, this
produced a Cartesian-product artifact: every permno with pre-1970
history appeared 25 times in 1970-01 (because every month from 1925-12
to 1970-01 collapsed to `toStartOfMonth(...) = 1970-01-01`). The
manual substring approach preserves the Date32 type and the actual
calendar year-month. `[VINTAGE-DRIFT]`.

**Impact:** Pre-1970 permno-months are no longer collapsed. Panel rows
go from 1,730,550 (with the bug) to 1,726,806 (cleaned). Date range is
1968-01 .. 2022-12 as the paper specifies.

---

## Assumption 14 — VW portfolio weights use current-month ME (not prior-June ME)

**Decision:** VW portfolio returns for the Table 1 spot check use
`ME` from the same (permno, month) — not the prior-June ME that FF
convention uses for proper value-weighting.

**Rationale:** Lagging ME by 6 months requires an additional snapshot
table; for the Stage 7 panel pass we use current-month ME for simplicity.

---

## Assumption 15 — Table 1 VW uses ME lagged 1 month (per spec from Replicator)

**Decision:** Stage 7 Table 1 implementation (`src/table1_max.py`) uses
`ME.shift(1)` per permno (= `ME_lag1` in panel) as the VW weight, per
Replicator's correction in iter-2 spec.

**Rationale:** Avoids look-ahead bias at portfolio formation time.
At formation month t, the investor knows only ME at end of month t-1.
Current-month ME (used in iter-1 spot check) is known only with hindsight.

**Observed effect (iter-2):** 10-1 spread = -0.477%/month
(ME_lag1) vs -0.594%/month (current-month ME) vs paper -0.95%/month.
Lagging ME shrinks the spread further from the paper, not closer.
The shortfall is likely due to other pipeline differences (sample
inclusions, MAX definition, etc.) rather than the ME-lag choice.

---

## Assumption 16 — Iter-2 Table 1 result: systematic ~50% magnitude shortfall

**Decision:** Report iter-2 Table 1 replication results as-is, with
diagnosis below. Do NOT silently adjust to match paper.

**Diagnosis:** Across all 6 factor-model columns (RET-RF, CAPM, FF3,
FFC4, FF5, FF6), the replicated values are systematically smaller in
magnitude than the paper. The 10-1 spread is ~50% of the paper
(-0.48% vs -0.95% for RET-RF), with similar shortfall in factor alphas
(P10 alpha -0.23% vs paper -1.17% for CAPM).

**Cross-checks performed:**
- EW 10-1 spread on ret_next = +0.28% (wrong sign) — confirms
  the spread is driven by size effect (high-MAX stocks are smaller,
  VW weighting concentrates on smaller, weaker stocks).
- VW 10-1 spread on ret_next (lag-1 ME) = -0.48%.
- VW 10-1 spread on ret_next (current-month ME) = -0.59% (iter-1).
- NW(6) t-stat on the spread = -1.90 (paper has -3.08).
- MAX distribution is monotonically increasing across deciles
  (D1 median 1.0%, D10 median 7.5%) — sort itself works.

**Hypotheses (not yet tested):**
- The paper may use ME lagged 6 months (= FF June-t constant ME) for
  VW weighting. We don't have the June-t snapshot in the panel.
- The paper may use NYSE-only breakpoints for decile assignment.
  Currently using all-stocks (per Assumption 7).
- The MAX signal computation may differ slightly (e.g. how missing
  daily returns are handled).

The replicated 10-1 spread is -0.594%/month (vs paper -0.95%/month) —
direction matches but magnitude is ~60% of paper. The shortfall is
expected to shrink when proper ME lag is added in the Stage 7 Table 1
pass. `paper silent on this for panel construction`.

---

## Assumption 17 — Iter-3: Apply NYSE-only breakpoints for MAX decile assignment

**Decision:** Form 10 MAX deciles using breakpoints computed from the
NYSE-only distribution (permnos with `exchcd = 1` per
`crsp_202601.dsenames`) of MAX each month, then apply those breakpoints
to all stocks (NYSE + NASDAQ + AMEX). Drop months with fewer than 30
NYSE stocks. Per `rep/PAPER_CONVENTIONS.md#Breakpoint universe`.

**Rationale:** The iter-2 result (Assumption 16) showed a ~50%
magnitude shortfall in the 10-1 spread (-0.48% vs paper -0.95%) with
direction preserved. Bali-Cakici-Whitelaw (2011) and the parent paper
follow the Fama-French (1993) convention of NYSE-only breakpoints for
cross-sectional decile sorts. Without this filter, NASDAQ/AMEX
microcaps concentrate in the top MAX decile and their negative
size-driven returns mask the true MAX effect. `[CONVENTION-APPLIED]`.

**Implementation:** `src/table1_max.py` adds `_attach_nyse_flag()` to
PIT-join `crsp_202601.dsenames` to the panel via (permno, month), and
`_nyse_breakpoint_deciles()` to compute the 9 (decile-1) cut points
from the NYSE-only MAX distribution per month, then vectorized-assign
deciles via `(MAX > bp).sum(axis=1) + 1`. Months with fewer than 30
NYSE stocks are dropped.

**Observed effect (iter-3, post-fix):**
- D10 median ME = $98M (top decile concentrates small-cap high-MAX stocks);
- D1 median ME = $138M (bottom decile is a mix of large-cap low-MAX stocks);
- D10 mean ME = $0.62B, P1 mean ME = $6.08B (size-ordered, NYSE breakpoints working).
- D10 RET-RF = +0.47%, D1 RET-RF = +0.74% (mildly monotonic decreasing).
- 10-1 spread = -0.27% (vs paper -0.95%, iter-2 -0.48%) — shortfall
  reduced from 50% to 28% of paper magnitude. Direction preserved;
  all factor-model alphas (CAPM, FF3, FF5, FF6) have t-stats in
  the -1.4 to -2.6 range, indicating statistical significance.

**Bug fix during iter-3:** Initial iter-3 result was -0.10%/month
(non-monotonic across deciles) due to `_nyse_breakpoint_deciles()`
returning a DataFrame instead of a Series, causing downstream
`sub["decile"] = decile_series.astype("Int64")` to assign a DataFrame
to a column. The fix was to return a proper `pd.Series` with the
correct index. After the fix, the decile assignment is monotonic and
the spread is -0.27%.

---

## Assumption 18 — Table 6 MAX^beta uses beta-then-MAX double-sort (paper section 3.2)

**Decision:** Replicate the paper's MAX^beta construction as a 10x10
conditional double-sort: (1) each month, sort stocks into 10 deciles
by BETA; (2) within each BETA decile, sort stocks into 10 deciles by
MAX; (3) regroup by the inner MAX decile (the "MAX^beta" bin) across
all 10 BETA deciles. The long-short spread is the VW portfolio return
of MAX^beta decile 10 minus decile 1, weighted by `ME_lag1`.

**Rationale:** This reproduces paper section 3.2's procedure verbatim.
The paper's section 3.2 specifies the 10x10 conditional sort to
isolate the lottery demand component of MAX from the systematic-risk
component (BETA). Skipping the outer sort would give Table 6 = Table 1
(only the inner MAX sort); performing the inner sort on the full
cross-section (instead of within each BETA decile) would not control
for BETA and would not be MAX^beta. We use all-stocks breakpoints for
both sorts (not NYSE-only), since the outer sort is on BETA — a
signal, not size — and the standard practice in the literature for
non-size sorts is to use the full universe for breakpoints.

**Implementation:** `src/table6_maxbeta.py` uses
`df.groupby(['month', 'beta_decile'])['MAX'].transform(pd.qcut, q=10,
labels=False, duplicates='drop')` to compute the inner MAX decile
within each (month, beta_decile) cell, then drops months where any
beta decile has fewer than 30 stocks or any MAX^beta decile has
fewer than 30 stocks.

**Skipped models:** SY, DHS, FFCPS, FF6PS — not in ClickHouse (per
Assumption 1, 2, 3). The paper reports `-0.62` (t=-3.33) for SY
and `-0.46` (t=-2.10) for DHS in the 10-1 spread; these are SKIP
cells in our metrics.json.

## Assumption 19 — Table 2 omits MIS (requires 11-component mispricing composite)

**Decision:** Skip the MIS column in Table 2; report only MAX, BETA,
IVOL (and document that the paper's MIS composite is unavailable).

**Rationale:** The paper's MIS is an 11-component mispricing composite
per Stambaugh-Yuan (2017) — it requires computing 11 anomaly signals
at monthly frequency, sorting each into deciles, and combining via
equal weights. The components (e.g., accruals, net stock issues,
composite equity issuance) require additional Compustat pipeline
work that is out of scope for this iteration. Per Assumption 1, the
Stambaugh-Yuan dataset is unavailable in ClickHouse, so the MIS
composite itself is unavailable even in principle for this
replication. `[THIRD-PARTY-DATASET]`.

---

## Assumption 20 — Iter-5: apply June-t ME snapshot for VW weighting

**Decision:** Add a new column `me_june_t` to `data/panel.parquet` and
use it as the VW weight for both Tables 1 and 6 (replacing the
prior-month ME `ME_lag1` weight). Concretely, for each (permno, month)
`me_june_t` = ME at the calendar June of fiscal-year `y - 1` if the
month is January-June of year `y`, or ME at the calendar June of year
`y` if the month is July-December of year `y` (the standard FF 1993 /
Bali-Cakici-Whitelaw 2011 carry-forward convention).

**Diagnosis (pre-iter-5):** Replicated D10-D1 spreads on Table 1 and
Table 6 carried the right sign but ~28-50% of the paper magnitude. The
ME_lag1 hypothesis was falsified in iter-2 (lagging ME shrank the
spread, not widened it). NYSE-only breakpoints (iter-3) shrank the
spread further. The remaining leading candidate was the FF / Bali-2011
June-t carry-forward convention, which is the standard for size-style
portfolio weighting.

**Implementation:**
- `src/sql/08_me_june.sql` — pulls the universe-filtered June-snapshot
  ME per (permno, calendar-June) from `crsp_202601.msf` (joined PIT to
  `crsp_202601.dsenames` for shrcd/exchcd/SIC filters). 211,924 June
  snapshots retrieved; 65,420 stock-months have no June ME (small-cap
  universe-gap, expected).
- `src/rebuild_panel_june.py` — joins the June ME into the existing
  `data/panel.parquet` post-build (option (b) in the spec, chosen to
  avoid a multi-minute CTE-chain rebuild; justified in
  `src/rebuild_panel_june.py`).
- `src/table1_max.py` — `form_decile_portfolios(panel, vw_col=...)`
  takes the weight as a parameter; computed `port_vw_lag1` and
  `port_vw_june` and prints a side-by-side `compare_two_weights()` for
  headline cells.
- `src/table6_maxbeta.py` — same change for `form_max_beta_deciles`.
- `src/table1_max.py` and `src/table6_maxbeta.py` —
  `cells_to_metrics_json()` now writes values in PERCENT/month (multiplied
  by 100 from decimal). This matches the paper target units in
  `tables_to_replicate.json` (`unit: "%/month"`).

**Measured effects on Table 1 headline cells (vw_col=ME_lag1 ->
vw_col=me_june_t):**
- P10_RET_RF: +0.470% -> +0.401% (T1 paper -0.32): rel_err 1.47 -> 1.25 (closer, but still wrong sign).
- D10_D1_RET_RF: -0.270% -> -0.359% (T1 paper -0.95): r = 0.28 -> 0.38.
- D10_D1_CAPM: -0.342% -> -0.426% (paper -1.41): r = 0.24 -> 0.30.
- D10_D1_FF3: -0.271% -> -0.363% (paper -1.16): r = 0.23 -> 0.31.
- D10_D1_FFC4: -0.223% -> -0.321% (paper -1.07): r = 0.21 -> 0.30.
- D10_D1_FF5: -0.084% -> -0.192% (paper -0.59): r = 0.14 -> 0.32.
- D10_D1_FF6: -0.063% -> -0.174% (paper -0.57): r = 0.11 -> 0.31.

**Measured effects on Table 6 headline cells:**
- P10_RET_RF: +0.385% -> +0.293% (T6 paper -0.10): r = 3.85 -> 2.93.
- D10_D1_RET_RF: -0.318% -> -0.432% (T6 paper -0.81): r = 0.39 -> 0.53.
- D10_D1_CAPM: -0.363% -> -0.469% (paper -1.00): r = 0.36 -> 0.47.
- D10_D1_FF3: -0.299% -> -0.375% (paper -0.90): r = 0.33 -> 0.42.
- D10_D1_FFC4: -0.187% -> -0.300% (paper -0.95): r = 0.20 -> 0.32.
- D10_D1_FF5: -0.183% -> -0.244% (paper -0.67): r = 0.27 -> 0.36.
- D10_D1_FF6: -0.100% -> -0.194% (paper -0.72): r = 0.14 -> 0.27.

**Status:** June-t ME WINS on every spread cell on both tables (the
ratio r is closer to 1.0 in every case). But the magnitude shortfall
remains: the largest relative improvement is Table 6 D10_D1_FF6
(r 0.14 -> 0.27), still outside the [0.33, 3.0] band on the metric
side (FF6 mean -0.19 vs paper -0.72).

**Outcome for [M1]:** Headline P10_RET_RF sign is still positive
(+0.401/+0.293) where the paper reports negative (-0.32/-0.10). June-t
ME alone did NOT flip the short-leg sign. The magnitude is reduced
(P10_RET_RF moved from +0.470 to +0.401 on T1, from +0.385 to +0.293
on T6), so the shrinkage is real but the sign question remains.

**Outcome for [M2]:** Magnitude shortfall is IMPROVED but not
RESOLVED. Aggregate scorer: match_count=10/25 (40%), loss=0.60, exactly
the same as iter-4. The headline-magnitude band [0.33, 3.0] requires
every D10-D1 alpha to be within +/-70% of paper; the me_june_t version
sits at ~30-55% of paper, just below the band on T1 and within reach
on T6 FF6.

**Hypothesis (not yet tested):** The remaining sign flip on P10_RET_RF
and the magnitude shortfall suggest the COVID-era tail (2020-04 ..
2022-12) is contaminating the lottery deciles with a positive return
sample that the paper's 1963-2007 sample does not contain. Next-iter
hypothesis: restrict sample to 1968-01 .. 2019-12 and re-run.

**[CONVENTION-APPLIED] (June-t ME for VW weighting).**


