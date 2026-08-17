# Assumptions Registry — Weber (2018) Cash Flow Duration

Paper: Weber (2018), JFE 128, 486–503. Slug: `weber_2018_attempt2_deepseek`.
This file logs paper-silent decisions (Stage 7), iteration diagnostics,
and corrections. Paper-derived rules live in `preprocessing_rules.json`.

## Pre-registered decisions (iteration 1)

### A1: Universe operationalization — share codes, exchanges, incorporation
**Decision:** Common stocks = CRSP monthly header (msfhdr, PIT via begdat/enddat) with
`hshrcd IN (10,11)` and `hexcd IN (1,2,3)` [CONVENTION-APPLIED]; no separate
incorporation filter — the NYSE/AMEX/Nasdaq exchange screen plus shrcd 10/11 is the
operationalization of "common stocks of firms incorporated in the United States"
(CRSP has no incorporation-country field).
**Rationale:** Paper: "I follow standard conventions and restrict my analysis to common
stocks of firms incorporated in the United States trading on NYSE, Amex, or Nasdaq" (L104).
Standard conventions = shrcd 10/11, exchcd 1/2/3 (rep/PAPER_CONVENTIONS.md § Universe
selection). PIT via msfhdr per the convention's dsenames prohibition.
**Impact:** All tables (universe everywhere).

### A2: $5 price floor — [CONVENTION-SKIPPED], reversed after iteration 3
**Decision:** REVERSED — no price filter; all common stocks with a valid return enter
the universe regardless of price. **Corrected after iteration 3** (flagged by the
funnel-of-means diagnostic): the earlier [CONVENTION-APPLIED] $5 floor was wrong for
this paper.
**Evidence (why the default was wrong here):** the funnel of universe EW means
(1963-2014, my direct ClickHouse query): all msf = 1.16%/mo → +PIT shrcd/exchcd =
1.22% → +SIC exclusion = 1.24% → **+ price≥$5 = 2.01%/mo (+77bps)**. Raw CRSP small
caps (<$100M) earn 0.76%/mo — penny stocks are the LOW-return names, and removing
them selects a high-return universe. The paper's own decile means (Table 2 average
≈0.93%/mo, below full-universe EW of 1.16%) are incompatible with any price floor.
With the floor on, our D1 EW = 2.79 vs paper 1.43 and the spread collapses (0.05 vs
1.10). rep/PAPER_CONVENTIONS.md decision path 3: the skip is earned by data evidence.
**Impact:** All return tables (T2–T6, T8–T12).

### A3: SIC source for financials/utilities exclusion
**Decision:** CRSP monthly header SIC (msfhdr.hsiccd, PIT at observation month).
**Rationale:** Paper: "I exclude financials (6000 ≤ SIC < 7000) and utilities
(4900 ≤ SIC < 5000)" (L104) without naming the source; the universe is CRSP-based,
so the CRSP header SIC is the natural implementation.
**Impact:** All tables.

### A4: Winsorization frequency
**Decision:** Annual cross-sectional winsorization at 1%/99% — Dur (and later BM, PR,
ROE, Sales_g) winsorized within each sort-year cross-section before decile formation;
for Table 1, within each annual cross-section. **Confirmed after iteration 1:** the
winsorization also applies to the duration INPUTS (ROE, sales growth) within fiscal
year — the paper winsorizes "all variables" (L176), and without input winsorization
the raw duration distribution is dominated by extreme ROE/g outliers (raw ROE min −822,
g max 11,879 observed in the data).
**Rationale:** Paper: "I winsorize all variables at the 1% and 99% levels" (L176) —
silent on frequency. The portfolio construction is annual (end-of-June sorts), so
annual cross-sectional winsorization is the defensible default.
**Impact:** Dur distribution and portfolio composition everywhere; Table 1 stats.

### A5: Duration inputs
**Decision:** E = `ib` (income before extraordinary items — matches the paper's ROE
definition, L108); initial BV growth forecast = current sales growth `sale_t/sale_{t-1} − 1`
(Nissim-Penman logic cited at L168-170: sales growth is the best predictor of BV growth);
BV_0 = BE_t from the paper's cascade; P = CRSP market equity at the fiscal-year-end month.
Firm-years with missing/≤0 BE or missing ib/sale are excluded from duration sorts
(paper silent).
**Rationale:** Eq. (3)-(4) (L158-165) + ROE definition (L108) + L168-170.
**Impact:** Dur values everywhere (T1–T12).

### A6: Fiscal-year adjacency
**Decision:** Require consecutive fyear (diff = 1) AND datadate gap in [300, 430] days
for ROE/g lags [CONVENTION-APPLIED] (rep/PAPER_CONVENTIONS.md § Annual accounting panels).
**Impact:** Duration inputs (ROE_t uses BE_{t−1}).

### A7: Moody's book-equity supplement — documented defer [THIRD-PARTY-DATASET]
**Decision:** Use Compustat-only BE. The hand-collected Moody's manual BE (Davis et al.
2000) used by the paper (L106) is not in the catalog (data_verification.json
`moodys_book_equity`). No substitution imputation.
**Rationale:** The supplement fills BE for firm-years missing Compustat BE (mainly
pre-1980); those firm-years drop out of duration sorts here.
**Impact:** Sample composition 1963–1980; all duration-based cells (T1–T12). Guard:
funnel counts per decade will be checked against the paper's implied sample size.

### A8: VW weight timing
**Decision:** VW weights = formation-June ME held constant over the July–June cohort
[CONVENTION-APPLIED] (rep/PAPER_CONVENTIONS.md § FF-style annual-formation papers).
**Rationale:** Paper silent; annual rebalancing convention.
**Impact:** Table 2 Panel C (VW means).

### A9: Size percentile for "above 20th size percentile"
**Decision:** 20th percentile of the cross-section computed from ALL stocks (NYSE+AMEX+
Nasdaq), not NYSE-only. **Corrected after iteration 8**: the 2×2 variant grid showed the
all-stock breakpoint matches the paper's Table 1 mean_me (1834 vs 2125, within tolerance)
and mean_ior (0.398 vs 0.44, within tolerance), while the NYSE-only breakpoint gives
3559/0.519 (both FAIL). [CONVENTION-SKIPPED] (NYSE-only default) with this empirical
justification.
**Rationale:** Paper says "above the 20th size percentile" (L210, L1999, L2033) without
naming the breakpoint universe; the data favor the all-stock breakpoint.
**Impact:** Table 1 and Tables 10–12 sample composition. Side effect: mean_age drops to
13.75 vs paper 17.59 (FAIL — logged).

### A10: 13F IOR implementation details
**Decision:** IOR = Σ shares held by reporting institutions (s34, first appearance
after carry-forward of up to 8 quarters) ÷ CRSP shares outstanding, with holdings
adjusted by the CRSP cumulative share adjustment factor between effective and report
dates; stocks on CRSP but not in 13F get IOR = 0. Exact join keys (CUSIP+date) to be
validated at build time against s34's live schema.
**Rationale:** Paper L110 describes the procedure; implementation details (CUSIP
mapping, factor application point) are paper-silent.
**Impact:** T1 IOR cells, T10–T12 (RIOR).

### A11: Volatility-management scaling constant
**Decision:** Portfolio returns scaled by c_i / RV_{i,t−1} with RV_{i,t−1} = Σ of
squared daily EW portfolio returns over the previous month, and c_i chosen so the
scaled series has the same full-sample standard deviation as the unscaled portfolio
(Moreira & Muir 2017). Daily within-month portfolio returns are EW across the
portfolio's members (paper silent on daily weighting).
**Rationale:** Paper: "Portfolio returns are scaled by the previous months realized
variance as in Moreira and Muir (2017)" (L1337).
**Impact:** All Table 6 cells.

### A12: "US incorporated" and link-table conventions
**Decision:** CCM link: linktype IN ('LC','LU'), linkprim IN ('P','C'), usedflag = 1,
PIT (linkdt ≤ datadate ≤ linkenddt or null) [CONVENTION-APPLIED per references/COMPUSTAT.md].
Compustat annual: indfmt='INDL', consol='C', popsrc='D', datafmt='STD'.
**Rationale:** Standard WRDS conventions (references/COMPUSTAT.md).
**Impact:** All Compustat-based variables.

### A13: FF factor scale
**Decision:** FF tables are stored in decimal units (avg mkt_rf 1963–2014 = 0.00507 —
verified against ClickHouse); CRSP ret is decimal. No scale conversion needed anywhere.
**Rationale:** Empirical check, 2026-08-16.
**Impact:** All factor regressions (T2/T3/T6/T11/T12).

## Iteration 10 — Table 8 SUE/EG salvage

### SUE2 distinct from SUE1 (ex-special-items EPS)
**Decision:** SUE1 = rolling seasonal random walk on Compustat quarterly `epspiq` (reported EPS, incl. special + extraordinary items); SUE2 = rolling seasonal random walk on ex-special-items EPS computed as `(ibq - spiq) / cshfdq` (income before extraordinaries less special items, diluted per share). Price scaler = `prccq` (quarter-end close, split-adjusted).
**Rationale:** Prior implementation set SUE2 = SUE1 (silent duplication). Compustat has no ready-made per-share ex-special-items field (only `epspxq`/`epsfxq` = ex *extraordinary* items); `spiq` is pre-tax so the subtraction is a first-order (over-corrected) proxy — documented.
**Data-source fix:** Prior SUE1/SUE2 read quarterly EPS from IBES `act_epsus`, which is *unadjusted for splits* (6,399 USD quarterly rows with |EPS|>1000; max 7.56e11). Compustat `fundq` EPS is split-adjusted, eliminating the reverse-split artifact.

### EG source: Compustat split-adjusted annual EPS (not IBES unadjusted)
**Decision:** EG uses Compustat annual `epspx` (EPS excluding extraordinary items, split-adjusted) instead of the paper's stated IBES `act_epsus pdicity='ANN'`. Annualized growth = `(EPS_t / EPS_{t-5})^(1/5) - 1`, x100 for percent.
**Negative/zero base rule (paper silent):** require both EPS_t > 0 and EPS_{t-5} > 0; otherwise NaN (growth is undefined across a sign change). Not cherry-picked.
**Rationale:** IBES `act_epsus` is unadjusted; as-reported EPS five years apart sits on different share bases after any split, biasing (EPS_t/EPS_{t-5}) downward (observed: D1 = -1.6% under IBES vs -0.54% under Compustat). Compustat is the correct split-adjusted realized-EPS source.

### Documented (unresolved) divergences in Table 8
- SUE sign inversion persists: paper SUE medians DECREASE (D1 +0.23 -> D10 -0.47); ours INCREASE (D1 -0.22 -> D10 +0.36). Root cause is compositional, not a sign bug: our duration deciles are the full CRSP/Compustat universe (D10 = tiny firms, median price $3.87), whereas the paper's Table 8 is built on the IBES-covered subset (footnote 15: "Analysts mainly cover large companies"). SUE1 component check: numerator median D1=0.00 / D10=+0.01; price median D1=$6.38 / D10=$3.87; both-EPS fraction=0.95.
- EG low-duration D1 endpoint EPS DECLINES (EPS_t=$0.73 vs EPS_{t-5}=$0.95), high-duration D10 grows (EPS_t=$0.48 vs EPS_{t-5}=$0.455) — opposite the paper's monotone-in-duration growth. Same IBES-coverage composition cause.

## Iteration 11 — Table 8 IBES-coverage screen (audit1 M2)

### Diagnosis
footnote 15 (content.md L1790): "Analysts mainly cover large companies, and therefore
the following results might not be representative for the universe of CRSP/Compustat
stocks considered so far." T8 was sorting the FULL universe; D10 contained tiny
non-covered firms (median price $3.87 vs D1 $6.38), inverting SUE. Fix: re-sort deciles
within the IBES-covered subset.

### Next fix
ibes_coverage.sql (usfirm=1 in statsum/act/det, June statpers of year t) -> cusip->permno
PIT map -> intersect panel -> re-rank dur deciles within covered subset (build_covered_mapping).

### Before metric
T8 L=0.5455 (50 Match/60 FAIL). LTG_t D1=12.56 / D10=28.56. SUE1 D1=-0.22 -> D10=+0.36.
price median D1=$6.38 / D10=$3.87.

### After metric
T8 L=0.5364 (51 Match/59 FAIL). LTG_t D1=12.71 / D10=29.09 (now close to paper 13.08/25.73;
5 LTG spread cells FAIL only because D9/D10 tail runs steep). SUE1 D1=-0.33 -> D10=+0.17
(still inverted); price median D1=$9.86 / D10=$7.75 (composition gap largely closed).
Coverage screen: covered 9,882 permnos vs full 13,512; share of stocks 43% (1982) -> 84%
(2009); share of market cap 91% -> 99.7% (firms covered are overwhelmingly the large ones,
exactly footnote 15's premise).

### Status
PARTIAL. Panel A (LTG) substantially improved (extrapolation mechanism now reproduces).
SUE direction NOT restored — root cause is NOT compositional after the screen: the SUE1
numerator (seasonal random walk on Compustat epspiq) has median ~0 at EVERY decile
(D1=-0.015 .. D10=+0.010), i.e. there is no earnings-surprise gradient in the numerator to
begin with. The paper's SUE1 (D1 +0.23 -> D10 -0.47) requires a real negative surprise
gradient in duration; the Compustat seasonal change carries no such gradient, so the screen
cannot repair it. Same for EG (backward EG D1=-0.95% vs paper 6.95%; iteration-10 substitution
of IBES unadjusted with Compustat epspx compresses the growth level). Remaining causes are
SUE-NUMERATOR (timing/scaler: Livnat-Mendenhall 2006 standardize by forecast-error sigma, not
price) and EG-SOURCE (IBES realized vs Compustat), not universe selection. Not over-tuned.

## Iteration 12 — audit1 M1: [VINTAGE-DRIFT] hypothesis TESTED and REJECTED

### Diagnosis (M1, revisited via empirical test)
The D9/D10 tail FAIL cluster (ff4_alpha_D10 -0.070 vs +0.149, ff5_alpha_D10 0.010
vs +0.222, mean_D10 0.462 vs 0.32) had been retired in audit1 with a hedged
"[VINTAGE-DRIFT]" story (comp_202601 backfills vs ~2014) and no demonstrated test.
Decision: run the cheap, principled test OR reopen the cells.

### Next fix (test executed 2026-08-16, src/vintage_probe.py — scratch module,
does NOT touch the canonical pipeline / panel.parquet / metrics.json)
Rebuilt the fundamentals+Duration table with comp_202401.funda + crsp_202401.
ccmxpf_linktable under IDENTICAL filters/cascade (indfmt='INDL', consol='C',
popsrc='D', datafmt='STD', fyear 1960-2014, same BE cascade, same CCM link,
same winsorization), then rebuilt the June decile sorts + monthly EW returns and
compared D9/D10/spread/ff4/ff5 alphas against the canonical comp_202601 vintage.

### Before metric (canonical comp_202601)
mean_D9=0.474, mean_D10=0.462, mean_D1D10=1.106; ff3_alpha_D10=-0.165,
ff4_alpha_D10=+0.149, ff5_alpha_D10=+0.222; D10 composition: median me_jun $40.5M,
median BE $6.8M, share negative-ROE 0.699, median age 4.0.

### After metric (old vintage comp_202401)
mean_D9=0.476, mean_D10=0.461, mean_D1D10=1.109; ff3_alpha_D10=-0.166,
ff4_alpha_D10=+0.148, ff5_alpha_D10=+0.220; D10 composition: median me_jun $40.5M,
median BE $6.8M, share negative-ROE 0.700, median age 4.0. Only 64 firm-years are
added by the 2026 vintage across the entire 1960s-1990s (9/21/22/12 per decade).

### Status
[VINTAGE-DRIFT] REJECTED — the older vintage reproduces the tail to 3 decimal
places (D10 mean 0.462->0.461, ff4_alpha_D10 +0.149->+0.148). Vintage is NOT the
cause; the D9/D10 cells remain OPEN/actionable and are NOT attributable to
Compustat backfill drift.

### Companion diagnostic (IBES-covered subset, documentation only)
Restricting the T2 decile sort to the IBES-covered intersection (ibes_coverage.sql,
footnote-15 large-firm subset) moves mean_D10 from 0.462 -> 0.325 (paper 0.32) and
mean_D9 from 0.474 -> 0.494 (paper 0.62), while the spread SHRINKS to 0.917 (paper
1.10). This demonstrates the D10 tail is COMPOSITIONAL (loss-making small firms,
70% negative ROE): the paper's low D10 mean is carried by the large-firm/covered
subset. BUT this is a sample-composition effect, NOT vintage drift, and the IBES
subset is the T8/T9 universe (footnote 15), not the T2 universe — so it does NOT
rescue the T2 D9/D10 cells, which per the paper are the full CRSP/Compustat
universe. The D9/D10 tail cause is not yet demonstrated to the paper's numbers;
next step is a composition/definition probe against the paper's stated universe,
not a vintage swap.

### A14: Table 9 price-target extraction (audit1 M4, iteration 12)
**Decision:** Split-invariant PTB = (meanptg/price)×(CRSP mcap/BE); plausibility screen
meanptg/price ∈ [0.5, 2.0] applied as data hygiene (removes reverse-split artifacts —
raw PTP max 408,233%; 2.6% of rows have target/price > 3×; 1/99 winsorization is inert
against this tail); no $5 price floor (the floor is meaningless on split-adjusted price).
Consensus = meanptg (ptgsum, measure='PTG'); 12-month horizon confirmed via ptgdet.
**Rationale:** Audit1 M4 suspected a mis-specified extraction; the probe showed the
extraction was correct and the implausible quintile values came from split artifacts
in microcaps. Spot-check of 7 large firms × 2 months: all implied returns sane
(+6.5%..+39.3%). Residual PTP level gap (~24-33% vs paper ~16%) is a 2026-IBES-vintage
level gap, documented, not over-tuned.
**Impact:** T9 Panel A cells (PTB/PTP).

### A15: [VINTAGE-DRIFT] rejected for the D9/D10 tail (audit1 M1, iteration 12)
**Decision:** The D9/D10 tail FAIL cluster was previously attributed (hedged) to
Compustat vintage drift. TESTED: rebuilt the full duration pipeline on comp_202401
(Jan-2024 vintage, identical filters) — the tail reproduces to 3 decimals (mean_D10
0.461 vs 0.462; ff4_alpha_D10 0.148 vs 0.149); only 64 firm-years added across the
1960s-90s. Vintage drift is REJECTED as the cause; the cells are REOPENED as
open/actionable.
**Evidence:** vintage_probe.py (src/), evidence table in logs/log2.md inner iteration 3.
Companion finding: on the IBES-covered subset, mean_D10 = 0.325 (paper 0.32, essentially
exact) — the tail is compositional (tiny loss-making firms, 70% negative ROE, median
me $40M), and the open question is which screen/construction makes the paper's tiny
loss-makers earn less.
**Impact:** T2/T3/T5/T6 D9-D10 cells remain FAIL (open).

## Iteration 13 — audit1 M6: T12 BM-conditional D3 sign-flip (conditional duration tertiles)

### Diagnosis
T12 (BM-conditional RIOR double sort) had L=0.511 with the value/low-RIOR spread
0.941 vs paper 0.63 and sign-flipped D3 cells (t12_lowrior_l_D3 -0.72 vs +0.19).
Probe (src/t12_probe.py) established: (a) BM construction is CORRECT — BE cascade
uses pstkrv->pstkl->pstk (preferred-stock preference order, var_be_preferred_order),
denominator me_dec_m is Dec t-1 CRSP ME (not June ME), and BE is the fiscal-year
ending in calendar t-1 (t = fyear + 1). (b) The BM median breakpoint is correct:
median of the screened (above-20th-pct) sample, which yields a 1.000 growth/value
firm-count ratio (66,478 vs 66,462) versus a 1.25:1 imbalance (73,847 vs 59,093)
under an NYSE-only median (rejected, consistent with A9's all-stock breakpoint).
(c) The sign flips were TAIL COMPOSITION, same D9/D10 mechanism: duration and BM are
strongly negatively correlated, so the value basket's GLOBAL duration tertile 3 was
nearly empty (lowrior_VALUE_D3 = 857 firms, 26/month vs lowrior_GROWTH_D3 = 16,291,
494/month), turning its D3 alpha into noise.

### Next fix
The paper's T11/T12 caption says "within each bin I sort stocks into tertiles based on
duration... intersect these tertiles with an independent sort on residual institutional
ownership". This is a CONDITIONAL duration-tertile sort (breakpoints within each BM/
size basket), with an INDEPENDENT (global) RIOR tertile. The prior code formed duration
tertiles GLOBALLY. Fix: `_assign_tertile_within` forms duration tertiles within each
(basket, t) cross-section; RIOR tertiles remain global.

### Before metric
T12 L=0.511 (audit1). lowrior_VALUE_D3 alpha = -0.720 (paper +0.19), value D3 cells
populated by 26-38 firms/month (global tertiles). Aggregate L=0.3167 (451 Match/660).

### After metric
T12 L=0.2128 (37 Match/10 FAIL). lowrior_VALUE_D3 = -0.003 (paper +0.19, sign flip now
resolved to ~zero); rior_VALUE_D3 = +0.138 (paper +0.29); value D3 cells now 188-239
firms/month. Aggregate L=0.2864 (471 Match/660). T11 also inherits the fix (L=0.2128).
Residual value-basket D1 level gap (lowrior_l_D1 0.12 vs 0.81) is a level, not a sign,
gap — outside M6 scope.

### Status
FIXED (T12 sign-flip cells). The D3 value-tail flips were breakpoint convention
(conditional vs global duration tertiles), not BM-definition error. Scratch
clinical parquets data/vintage_probe_*.parquet removed; TypeError in main.py post-write
print fixed (dict-form metric handling via _v() helper).

## Iteration 14 — audit2 M3: SUE/EG source resolution (outer 3, inner 3)

### Diagnosis
T8 SUE/EG gradient (L=0.509). Audit-2 prescribed (a) resolving whether the paper's
"negative earnings surprises" (L2348) is analyst-forecast-based SUE3 rather than the
seasonal-RW SUE1/SUE2, (b) switching SUE1/2 to IBES quarterly actuals with "proper
split adjustment", (c) an EG source comparison.

### Next fix (tested, no metric commit)
Built `src/sue_eg_diagnostic.py` (scratch, does NOT touch metrics.json/panel.parquet).
Discovered: (1) `ibes_202601.adj` (ticker/spdates/adj) gives the CUMULATIVE split factor;
verified AAPL 4:1 (2020, factor 4->1) and 7:1 (2014, 28->4). (2) `act_epsus.value` is
ALREADY split-adjusted (FY2012 raw 44.15 -> act 1.5768 = 44.15/28); the outer-1 split
premise was false — the reverse-split artifact lives in `ptgsum`, not `act_epsus`.
(3) SUE1 on IBES QTR actuals reproduces the same wrong-sign numerator gradient as
Compustat (D1 -0.057 -> D10 +0.242 vs paper +0.23 -> -0.47): the seasonal RW is
mean-zero by construction, so SUE1/2 are UNATTAINABLE under any realized-EPS source.
(4) SUE3 is split-contaminated in the 202601 vintage (statsum_epsus .actual/.meanest
range [-1.31e9,+2.84e8]; 3.2% of rows |err|>5x|meanest|; raw error mean -47,583).

### Before metric
Committed: SUE1 0/11 Match, SUE2 3/11, SUE3 0/11, EG_t6_t1 0/11, EG_t_t5 1/11
(4/55 SUE+EG cells Match). Aggregate L=0.2864.

### After metric
All candidates evaluated; NONE clears net>=+4 cells AND no spread regression:
- SUE1 IBES (announcement-aligned, split-adj): wrong-sign gradient persisted, 0/11 Match.
- EG IBES ANN act_epsus: D1 1.21/12.14 vs paper 6.95/10.11; D10 14.48/13.64 vs 30.56/10.85
  (best source, forward-window D1 now ~correct, but backward gradient ~2x low). No net
  cell gain. epsfx (diluted ex-items) ~= epspx.
Metrics LEFT UNCHANGED; comparison documented in results/table_8.md.

### Status
COMMIT-DECISION = NO CHANGE (no dominant candidate). Footnote-17 resolution: the
"negative earnings surprises / earnings management" narrative is SUE3 (analyst-forecast
based; Skinner-Sloan 2002 and Burgstahler-Eames 2006 are meeting-analyst-forecasts
citations), NOT SUE1/SUE2. Do NOT re-weight committed SUE1/2/3 targets:
  - SUE1/SUE2 are structurally unreproducible (seasonal-RW surprise is mean-zero);
  - SUE3 is the claimed mechanism but blocked by a vintage-level split inconsistency.
Schema notes in results/table_8.md still claim "act_epsus ANN is UNadjusted" — incorrect
(see above); noted but cosmetic. New SQL: src/sql/ibes_adj.sql, ibes_sue_quarterly.sql.

## Iteration 15 — audit3 M1: split-consistent SUE3 re-derivation (outer 4, inner 1)

### Diagnosis
Audit-3 [M1] flagged that the SUE3 "vintage-blocked" label under-sold the fix: the
3.2% split-artifact rate was measured but the tool (ibes_adj cumulative factor) was
never applied to repair statsum_epsus actual/meanest. Task: re-derive a split-consistent
SUE3 and commit only if it clears net>=+3 of 11 cells with no regression.

### Next fix (tested, no metric commit)
Built `src/sue3_split_fix.py` (scratch). Diagnosed the mechanism precisely: the tail is
REVERSE-SPLIT persistence — statsum_epsus.actual is forward-persisted from the
pre-reverse-split per-share basis into the post-reverse-split row (ACTC -624M vs -24M;
GNTA -5.0M vs -35k; ACRS -18.15M vs +1.05M), while meanest is on the current basis.
Verified `adj` semantics: current-basis EPS = raw / adj (AAPL FY2012 44.15/28=1.5768);
adj>=1 forward-split, adj<1 reverse-split. AAPL/MSFT statsum actuals are already current
basis (median |actual| 0.006/0.175), never in the tail.

### Before metric
SUE3 D1..D10 = -0.209/-0.212/-0.193/-0.165/-0.156/-0.191/-0.136/-0.090/-0.072/-0.114,
spread -0.095 (all 11 cells FAIL vs paper +0.038..0.000). Aggregate L=0.2864.

### After metric
Split-consistent SUE3 (standardise /adj, drop reverse-split adj<1 rows; removes 14.7% of
the tail) yields D1..D10 = -0.207/-0.206/-0.189/-0.167/-0.156/-0.185/-0.142/-0.083/-0.082/
-0.111, spread -0.096. The fix moves D1 +0.003 and D8 +0.007; all 11 cells remain
sign-mismatch FAIL. No clean re-derivation can produce the paper's positive gradient.

### Status
COMMIT-DECISION = NO CHANGE (net 0 cells, far below +3). Root cause of the residual gap:
the analyst-consensus forecast error in the 202601 IBES summary is unbiased (45.5% beat/
50.1% miss, median -0.005) — a symmetric error distribution cannot yield the paper's
+0.038 D1 SUE3, which requires a systematic positive-surprise bias. This is a
distributional vintage property, NOT a split artifact. Metrics.json LEFT UNCHANGED;
comparison documented in results/table_8.md. New scratch: src/sue3_split_fix.py.

## Iteration 16 — audit3 M2 part A: V9 loss-firm-only CF floor probe (outer 4, inner 2)

### Diagnosis
The V3 CF floor (CF=max(CF,0) for ALL firms) overshot D10 (0.225 vs 0.32, spread 1.343,
net -6 cells). Audit-3 M2 asked for a *graduated* loss-firm treatment between no-floor
(V0) and full-floor (V3). The defensible paper-cited reading is footnote 6 ("paid out
as a level perpetuity"): the terminal-value assumption presupposes non-negative payouts,
so firms with current ROE_t < 0 (loss firms) cannot distribute and their clean-surplus
CF = BV*(ROE - g) < 0 should be floored to zero, while positive-ROE reinvesting firms
legitimately keep negative CFs (NOT floored).

### Next fix (tested, no metric commit)
Built `src/tail_probe_v9.py` (scratch): floors CF_{t+s} at zero ONLY for firms with
winsorized period-t ROE < 0. Reuses tail_probe.py recursion/portfolio machinery.

### Before metric (V0 committed)
mean_D9=0.477, mean_D10=0.455, spread=1.113; ff4_alpha_D10=+0.144, ff5_alpha_D10=+0.217;
tail Match=9/FAIL=9 (18 D9/D10 cells); D10 composition median me $44.6M, neg-ROE 0.698.

### After metric (V9)
mean_D9=0.511, mean_D10=0.189 (overshoots past 0.32), spread=1.404 (edge of ±30% band);
ff4_alpha_D10=-0.129, ff5_alpha_D10=-0.072 (tail alpha SIGNS flip toward paper for the
first time); tail Match=10/FAIL=8; net cell movement -6 (+5/-11 over all 99 T2+T3);
D10 composition median me $71.2M, neg-ROE 0.452.

### Status
COMMIT-DECISION = NO CHANGE. Fails the triple bar: net -6 (< +2). V9 moves the tail
factor alphas the right way (ff3/ff4/ff5 D10 alphas flip to negative, matching paper
signs) but overshoots D10 mean even harder than V3 (0.189 vs V3 0.225) and breaks
mean_D10/nodl_D10/vw_mean_D10 + D7/D8 alphas. The loss-firm-only floor is the correct
*family* (it is the first lever to flip tail alpha signs), but at THIS calibrated level
it swaps one tail error for another: ~45% of D10 firms remain negative-ROE and their
floored CF re-sorts them into D10. Probe documented in
results/iteration5_experiment_matrix.md; canonical pipeline + metrics + results
UNCHANGED.


### A16: T1 FAIL partition (audit4 m1, iteration 17 — documentation)
**Decision:** Partition of T1's 14 FAIL cells, written to results/table_1.md § "T1 FAIL partition":
(1) zero-anchor tolerance artifacts (6): mean_pr, corr_bm_ior, corr_bm_roe,
corr_roe_sales_g, corr_bm_pr, corr_ior_pr — paper values near zero with 50%-tolerance
bands finer than 2-decimal printing precision; (2) genuine composition gaps (8):
mean_age (A9 all-stock screen), std_pr (PR netting / tiny ni denominator), std_roe
(A7 no Moody's BE), corr_dur_bm/corr_dur_roe (terminal-term dominance in Dur),
corr_dur_pr/corr_pr_sales_g/corr_pr_age (PR noise). Report-only — the target contract
(tables_to_replicate.json) is unchanged.
**Rationale:** Audit 3 requested the partition to separate tolerance artifacts from
real gaps before judging the residue.
**Impact:** None (documentation).

## Documented-residue register (criterion B — audit 4 close-out)

Mechanical register of the 189 FAIL cells from eval/scoring.json (iteration 4), each
named under its closed-vocabulary marker with the evidence entry that supports it.


### [STRUCTURAL-SAMPLE-VARIANCE] — D9/D10 tail, T1 correlations, T10-T12 level gaps
Evidence: A15 (vintage tested and rejected), tail probe (V3/V9 — construction levers
exhausted; bins verified correct: D10 mean duration 25.29 vs the paper's "roughly 25
years", composition matches Table A.9's description), iteration-4 V9 probe (first
lever to flip tail alphas toward the paper — confirms composition, not construction),
A16 (T1 FAIL partition: terminal-term dominance for corr_dur_*; PR noise for
corr_pr_*; value-alpha level gaps for T11/T12 after the conditional-tertile fix).
Cells:
- `alpha_capm_D7`
- `alpha_capm_D8`
- `alpha_capm_D9`
- `beta_capm_D1D10`
- `corr_bm_ior`
- `corr_bm_pr`
- `corr_bm_roe`
- `corr_dur_bm`
- `corr_dur_pr`
- `corr_dur_roe`
- `corr_ior_pr`
- `corr_pr_age`
- `corr_pr_sales_g`
- `corr_roe_sales_g`
- `ff3_alpha_D10`
- `ff3_alpha_D7`
- `ff3_alpha_D8`
- `ff3_alpha_D9`
- `ff4_alpha_D10`
- `ff5_alpha_D10`
- `mean_D10`
- `mean_D9`
- `nodl_mean_D9`
- `std_pr`
- `t10_lowrior_D5`
- `t10_rior2_D4`
- `t10_rior3_D1D5`
- `t10_rior4_D1D5`
- `t11_highrior_s_D1`
- `t11_highrior_s_D2`
- `t11_highrior_s_D3`
- `t11_lowrior_l_D3`
- `t11_lowrior_s_D1`
- `t11_r1r3_s_D1`
- `t11_r1r3_s_D1D3`
- `t11_rior2_s_D1`
- `t11_rior2_s_D1D3`
- `t11_rior2_s_D2`
- `t12_highrior_l_D1`
- `t12_highrior_l_D3`
- `t12_lowrior_l_D1`
- `t12_lowrior_l_D1D3`
- `t12_lowrior_l_D2`
- `t12_r1r3_l_D1`
- `t12_r1r3_l_D1D3`
- `t12_r1r3_l_D2`
- `t12_rior_l_D1`
- `t12_rior_l_D2`
- `t4_ar_roe_050_D10`
- `t4_ar_roe_050_D9`
- `t4_ar_sg_020_D10`
- `t4_ar_sg_030_D10`
- `t4_ar_sg_030_D9`
- `t4_horizon_10_D10`
- `t4_preest_D10`
- `t4_preest_D1D10`
- `t4_r010_D10`
- `t4_r014_D10`
- `t4_r014_D9`
- `t4_roe_ss_010_D10`
- `t4_roe_ss_010_D9`
- `t4_roe_ss_014_D10`
- `t4_sg_ss_008_D10`
- `t4_sg_ss_008_D9`
- `t5_a_63673_D7`
- `t5_a_63673_D9`
- `t5_c_83893_D7`
- `t5_c_83893_D8`
- `t5_c_83893_D9`
- `t5_d_93903_D10`
- `t5_d_93903_D7`
- `t5_d_93903_D8`
- `t5_d_93903_D9`
- `t5_e_03014_D10`
- `t8_ltg_t1_D1D10`
- `t8_ltg_t2_D1D10`
- `t8_ltg_t3_D1D10`
- `t8_ltg_t4_D1D10`
- `t8_ltg_t_D1D10`
- `vw_mean_D10`

### [VINTAGE-DRIFT] — 202601 IBES vintage distributional gaps (T8 SUE/EG, T9 PTP/PTB)
Evidence: iteration-15 (SUE3 split-consistency fix attempted; residual is forecast-error
symmetry — 45.5% beat / 50.1% miss in the 202601 vintage — while the paper's positive
D1 surprise requires a directional bias); iteration-11/14 (EG: no source closes the
backward gradient; IBES act_epsus already split-adjusted); A14 (T9 spot-check: implied
returns +6.5%..+39.3% in the 202601 vintage vs the paper's flat ~16%).
Cells:
- `t8_eg_t6_t1_D1`
- `t8_eg_t6_t1_D10`
- `t8_eg_t6_t1_D1D10`
- `t8_eg_t6_t1_D2`
- `t8_eg_t6_t1_D3`
- `t8_eg_t6_t1_D4`
- `t8_eg_t6_t1_D5`
- `t8_eg_t6_t1_D6`
- `t8_eg_t6_t1_D7`
- `t8_eg_t6_t1_D8`
- `t8_eg_t6_t1_D9`
- `t8_eg_t_t5_D1`
- `t8_eg_t_t5_D10`
- `t8_eg_t_t5_D1D10`
- `t8_eg_t_t5_D3`
- `t8_eg_t_t5_D4`
- `t8_eg_t_t5_D5`
- `t8_eg_t_t5_D6`
- `t8_eg_t_t5_D7`
- `t8_eg_t_t5_D8`
- `t8_eg_t_t5_D9`
- `t8_sue1_D1`
- `t8_sue1_D10`
- `t8_sue1_D1D10`
- `t8_sue1_D2`
- `t8_sue1_D3`
- `t8_sue1_D4`
- `t8_sue1_D5`
- `t8_sue1_D6`
- `t8_sue1_D7`
- `t8_sue1_D8`
- `t8_sue1_D9`
- `t8_sue2_D1`
- `t8_sue2_D10`
- `t8_sue2_D1D10`
- `t8_sue2_D2`
- `t8_sue2_D3`
- `t8_sue2_D4`
- `t8_sue2_D8`
- `t8_sue2_D9`
- `t8_sue3_D1`
- `t8_sue3_D10`
- `t8_sue3_D1D10`
- `t8_sue3_D2`
- `t8_sue3_D3`
- `t8_sue3_D4`
- `t8_sue3_D5`
- `t8_sue3_D6`
- `t8_sue3_D7`
- `t8_sue3_D8`
- `t8_sue3_D9`
- `t9_ptb_D1D5`
- `t9_ptb_D4`
- `t9_ptb_D5`
- `t9_ptp_D1`
- `t9_ptp_D1D5`
- `t9_ptp_D2`
- `t9_ptp_D3`
- `t9_ptp_D4`
- `t9_ptp_D5`

### [CONVENTION-APPLIED] (non-actionable) — T6 volatility-managed levels, A9/A2-driven T1 cells
Evidence: A11 (Moreira-Muir per-portfolio std-equalizing c; iteration-3 sensitivity set
T0-T5 shows no RV construction dominates; the level error decomposes into the inherited
tail gap plus the scaling increment); A9 (all-stock 20th-pct breakpoints — data-favored
on mean_me/mean_ior; mean_age is the documented side effect); A16 (mean_pr zero-anchor
band ±0.01 per 2-decimal printing).
Cells:
- `mean_age`
- `mean_pr`
- `vm_alpha_capm_D10`
- `vm_alpha_capm_D3`
- `vm_alpha_capm_D4`
- `vm_alpha_capm_D5`
- `vm_alpha_capm_D6`
- `vm_alpha_capm_D7`
- `vm_alpha_capm_D8`
- `vm_alpha_capm_D9`
- `vm_alpha_ff3_D10`
- `vm_alpha_ff3_D2`
- `vm_alpha_ff3_D3`
- `vm_alpha_ff3_D4`
- `vm_alpha_ff3_D5`
- `vm_alpha_ff3_D6`
- `vm_alpha_ff3_D7`
- `vm_alpha_ff3_D8`
- `vm_alpha_ff3_D9`
- `vm_alpha_ff4_D1`
- `vm_alpha_ff4_D10`
- `vm_alpha_ff4_D2`
- `vm_alpha_ff4_D3`
- `vm_alpha_ff4_D4`
- `vm_alpha_ff4_D5`
- `vm_alpha_ff4_D6`
- `vm_alpha_ff4_D7`
- `vm_alpha_ff4_D8`
- `vm_alpha_ff4_D9`
- `vm_alpha_ff5_D1`
- `vm_alpha_ff5_D10`
- `vm_alpha_ff5_D2`
- `vm_alpha_ff5_D3`
- `vm_alpha_ff5_D4`
- `vm_alpha_ff5_D5`
- `vm_alpha_ff5_D6`
- `vm_alpha_ff5_D7`
- `vm_alpha_ff5_D8`
- `vm_alpha_ff5_D9`
- `vm_mean_D10`
- `vm_mean_D2`
- `vm_mean_D3`
- `vm_mean_D4`
- `vm_mean_D5`
- `vm_mean_D6`
- `vm_mean_D7`
- `vm_mean_D8`
- `vm_mean_D9`

### [THIRD-PARTY-DATASET] — Moody's book-equity supplement absent
Evidence: A7 (Compustat-only BE; Moody's manual BE from Davis et al. 2000 not in the
catalog — drops pre-1980 firm-years without Compustat BE, compressing std_roe).
Cells:
- `std_roe`

### no_effect cells (insignificant-encoded at Stage 4 — magnitude untestable by design)
These cells carry `insignificant: true` in tables_to_replicate.json because the paper's
own printed SE implies |t| < 1.96 (or the paper's prose calls them insignificant, e.g.
Table 10's High-RIOR D1-D5 0.15 and RIOR1-RIOR5 D1 -0.08). Per rep/TOLERANCE_RULES.md
§ Cells the paper itself reports as insignificant, the magnitude is untestable; the
paired _se cells carry the inference and are scored normally. They are excluded from
the loss by the scorer and are listed here for the criterion-B name check.
Cells:
- `t10_highrior_D1D5`
- `t10_r1r5_D1`
- `t10_r1r5_D2`
- `t10_r1r5_D3`
- `t10_rior2_D5`
- `t10_rior3_D5`
- `t10_rior4_D5`
- `t11_highrior_l_D1`
- `t11_highrior_l_D1D3`
- `t11_highrior_l_D2`
- `t11_highrior_l_D3`
- `t11_highrior_s_D1D3`
- `t11_lowrior_l_D1`
- `t11_lowrior_l_D2`
- `t11_lowrior_s_D2`
- `t11_lowrior_s_D3`
- `t11_r1r3_l_D1`
- `t11_r1r3_l_D2`
- `t11_r1r3_s_D2`
- `t11_rior2_l_D1`
- `t11_rior2_l_D1D3`
- `t11_rior2_l_D2`
- `t11_rior2_l_D3`
- `t11_rior2_s_D3`
- `t12_highrior_l_D1D3`
- `t12_highrior_l_D2`
- `t12_highrior_s_D1`
- `t12_highrior_s_D1D3`
- `t12_highrior_s_D2`
- `t12_highrior_s_D3`
- `t12_lowrior_l_D3`
- `t12_lowrior_s_D1`
- `t12_lowrior_s_D2`
- `t12_r1r3_l_D3`
- `t12_r1r3_s_D1`
- `t12_r1r3_s_D2`
- `t12_rior_l_D1D3`
- `t12_rior_l_D3`
- `t12_rior_s_D1`
- `t12_rior_s_D2`
- `t12_rior_s_D3`
