# Table 8 — Analyst expectations (ours)

TS-average of annual cross-sectional MEANS (Panels A/B) and MEDIANS (Panel C)
of ten duration deciles, June 1982–June 2009, sorted on the **IBES-covered** subset (footnote 15).

| Row | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D1D10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LTG_t | 12.707 | 13.403 | 14.156 | 14.988 | 15.662 | 16.860 | 18.114 | 20.177 | 24.150 | 29.086 | -16.379 |
| LTG_t1 | 12.754 | 13.425 | 13.958 | 14.625 | 15.308 | 16.401 | 17.346 | 19.123 | 22.386 | 26.527 | -13.773 |
| LTG_t2 | 12.782 | 13.312 | 13.740 | 14.435 | 15.001 | 15.852 | 16.636 | 18.098 | 20.680 | 23.958 | -11.176 |
| LTG_t3 | 12.622 | 13.169 | 13.551 | 14.206 | 14.632 | 15.452 | 16.056 | 17.221 | 19.288 | 21.712 | -9.090 |
| LTG_t4 | 12.528 | 12.962 | 13.186 | 13.812 | 14.148 | 14.821 | 15.358 | 16.444 | 17.963 | 20.158 | -7.630 |
| EG_{t-6:t-1} | -0.946 | 0.817 | 2.950 | 2.634 | 3.631 | 4.317 | 4.734 | 4.137 | 3.400 | 7.520 | -8.467 |
| EG_{t:t+5} | 7.049 | 5.537 | 3.018 | 2.840 | 2.237 | 2.304 | 1.865 | 2.266 | 2.130 | 6.919 | 0.130 |
| SUE1 | -0.074 | -0.037 | -0.007 | 0.011 | 0.052 | 0.037 | 0.065 | 0.076 | 0.076 | 0.061 | -0.135 |
| SUE2 | -0.074 | -0.202 | -0.063 | 0.065 | 0.249 | 0.153 | 0.125 | 0.298 | 0.161 | 0.139 | -0.213 |
| SUE3 | -0.209 | -0.212 | -0.193 | -0.165 | -0.156 | -0.191 | -0.136 | -0.090 | -0.072 | -0.114 | -0.095 |

## Schema discovery notes

- **LTG** in `ibes_202601.statsum_epsus` `fpi='0'` AND `fiscalp='LTG'` (NOT measure='Ltg').
  Per-analyst detail in `det_epsus` `fpi='0'` (value is a %, e.g. 20.0 / 85.0).
- **statpers** = monthly statistical period date (3rd Thu, String; e.g. '2005-06-16').
  June cross-section = `toMonth(statpers)=6`.
- **IBES cusip not standard**: non-US listings use EX/ER/LM/FJ… prefixes.
  `usfirm=1` filter yields standard 8-digit cusips matching `dsenames.ncusip` ~95.5%.
- **EG** via Compustat annual `epspx` (split-adjusted), annualized 5-yr growth; the
  paper specifies IBES act_epsus ANN but that file is UNadjusted for splits.
  Windows per Panel B labels: EG_{t-6:t-1} = (EPS_{t-1}/EPS_{t-6})^{1/5}-1 (x100;
  endpoint FYE t-1), EG_{t:t+5} = (EPS_{t+5}/EPS_t)^{1/5}-1 (x100; endpoint FYE t+5).
- **SUE1/SUE2** Livnat-Mendenhall (2006) sigma-standardization (NOT price-scaling):
  SUE = (EPS_q - EPS_{q-4}) / std(prior 8 seasonal differenced errors), require >=4
  prior differences, sample std. SUE1 on `epspiq` (reported); SUE2 on ex-special-items
  (ibq - spiq)/cshfdq. Split-adjusted Compustat fundq. Uses annual cross-sectional MEDIANS.
- **SUE3** = (actual - meanest) / std(prior analyst forecast errors), both `actual` and
  `meanest` from `statsum_epsus` (same split-adjusted basis), require >=4 prior errors.
- **EG window fix (this iteration)**: prior code's endpoint comments referenced EPS_t /
  EPS_{t-5}; the window is now explicit: backward ends at FYE t-1, forward ends at FYE t+5.
- **Price targets** in `ibes_202601.ptgsum` `measure='PTG'`, `meanptg` (split-adjusted
  $/share 12-mo-ahead); price in `actpsum_epsus.price` at same statpers.
- **PTG aggregate fields**: `numest` (analyst count), `meanptg` (mean consensus — used),
  `medptg` (median consensus), `stdev`/`ptghigh`/`ptglow` (dispersion). `ptgsum` has no
  horizon column; the 12-mo-ahead horizon lives in the detail table `ptgdet.horizon='12'`.
- **REVERSE-SPLIT split-adjustment artifact (this iteration)**: for microcaps that did
  reverse splits, `meanptg` mixes per-analyst targets on incompatible split bases (e.g.
  FCCM 2002: ptghigh=1540 vs ptglow=15 for a ~$2 stock), inflating meanptg/price to
  100x..4000x (max PTP 408,233%). Screen drops tpr outside [0.5, 2.0].
- **PTB split-invariant form (this iteration)**: PTB = (meanptg/price) × (CRSP mcap / BE).
  `meanptg×shout` was split-inconsistent (`shout` not on the target's split basis), making
  D5=12.25 implausible. BE is Compustat total book equity ($M); CRSP mcap is $/share.

## Coverage

- LTG cusip match rate: 14120/14868 (95.0%)
- LTG firms before fn16 screen: 55094
- LTG firms after fn16 (nonmissing all periods): 25670
- EG qualifying firm-5yr-growth obs: 78127
- EG endpoint EPS_t median D1/D10: 1.05 / 1.07
- EG endpoint EPS_(t-5) median D1/D10: 1.25 / 1.05
- EG backward obs / forward obs: 31990 / 29022
- SUE pool: 279540  (S1=243135 S2=92677 S3=155693)
- SUE1 both-EPS fraction: 0.8074461599741578
- SUE1 seasonal |numerator| median D1=-0.010000000000000009 D10=0.01999999999999999  sigma median D1=0.3386620191277156 D10=0.21181190848738662
- SUE3 sigma_analyst coverage: 236715 computable / 285445 errors (79.3%)
- SUE winsorized-used flags: S1=False S2=False S3=False
- SUE1 raw medians D1..D10: {1: -0.07382677389660885, 2: -0.036513377894559676, 3: -0.006626236617831469, 4: 0.011063304748479056, 5: 0.051885233539483634, 6: 0.03720687121411111, 7: 0.06487860372601748, 8: 0.07607084882306628, 9: 0.07620506995410502, 10: 0.06095401348374924}
- SUE1 winsorized medians D1..D10: {1: -0.07382677389660885, 2: -0.036513377894559676, 3: -0.006626236617831469, 4: 0.011063304748479056, 5: 0.051885233539483634, 6: 0.03720687121411111, 7: 0.06487860372601748, 8: 0.07607084882306628, 9: 0.07620506995410502, 10: 0.06095401348374924}
- LTG_t decile means (ours): {1: 12.70695612667579, 2: 13.403457421496412, 3: 14.15583488003147, 4: 14.987723145312914, 5: 15.662382620888067, 6: 16.859728598373806, 7: 18.113929430387493, 8: 20.177138990155438, 9: 24.149504902843745, 10: 29.086155331620645}
- IBES-covered permnos: 9882 (full universe 13512)
- IBES ANN-actuals EG (documentation only) D1/D10: {'t6_t1_D1': 1.2625139011677133, 't6_t1_D10': 14.60266874938424, 't_t5_D1': 11.534289269112945, 't_t5_D10': 13.907236072628518}

### IBES coverage per sort year (share of full universe)
| year | full n | covered n | share stocks | share ME |
|---|---|---|---|---|
| 1982 | 3501 | 1513 | 43.2% | 91.4% |
| 1983 | 3517 | 1672 | 47.5% | 92.7% |
| 1984 | 3859 | 2102 | 54.5% | 95.9% |
| 1985 | 3896 | 2068 | 53.1% | 95.6% |
| 1986 | 3841 | 2076 | 54.0% | 97.1% |
| 1987 | 3976 | 2207 | 55.5% | 97.6% |
| 1988 | 4052 | 2140 | 52.8% | 97.4% |
| 1989 | 3848 | 2127 | 55.3% | 97.6% |
| 1990 | 3747 | 2118 | 56.5% | 97.7% |
| 1991 | 3711 | 2079 | 56.0% | 98.3% |
| 1992 | 3729 | 2237 | 60.0% | 98.3% |
| 1993 | 4009 | 2536 | 63.3% | 98.2% |
| 1994 | 4430 | 2900 | 65.5% | 98.3% |
| 1995 | 4641 | 3057 | 65.9% | 98.1% |
| 1996 | 4841 | 3346 | 69.1% | 98.6% |
| 1997 | 5212 | 3725 | 71.5% | 98.9% |
| 1998 | 5112 | 3675 | 71.9% | 98.8% |
| 1999 | 4689 | 3450 | 73.6% | 99.4% |
| 2000 | 4570 | 3365 | 73.6% | 99.2% |
| 2001 | 4304 | 3069 | 71.3% | 99.1% |
| 2002 | 3847 | 2676 | 69.6% | 99.1% |
| 2003 | 3532 | 2554 | 72.3% | 99.3% |
| 2004 | 3381 | 2598 | 76.8% | 99.3% |
| 2005 | 3351 | 2675 | 79.8% | 99.4% |
| 2006 | 3263 | 2671 | 81.9% | 99.4% |
| 2007 | 3192 | 2660 | 83.3% | 99.4% |
| 2008 | 3147 | 2608 | 82.9% | 99.5% |
| 2009 | 2906 | 2443 | 84.1% | 99.7% |

## Audit-2 [M3] SUE/EG source-candidate comparison (this iteration, outer 3 inner 3)

Commit-decision evidence. No candidate below clears the "net >= +4 cells AND no
spread-cell regression" bar, so the committed metrics are LEFT UNCHANGED and the
comparison is recorded here. `src/sue_eg_diagnostic.py` is the reproducible harness.

### Task 1 — I/B/E/S split-adjustment discovery (DISPROVES audit premise 2)
`ibes_202601.adj` carries one row per (ticker, split date, cumulative `adj` factor).
AAPL factors: 224 -> 112 -> 56 -> 28 -> 4 -> 1 across 1981..2020 (the 2014 7:1 is
28->4; the 2020 4:1 is 4->1). MSFT: 288 -> ... -> 2 -> 1 (nine splits 1985..2003).
**`act_epsus.value` is ALREADY split-adjusted to the current common share basis.**
Reconciliation: AAPL FY2012 raw EPS $44.15 -> act_epsus 1.5768 = 44.15/28; FY2013
$39.75 -> 1.4196 = 39.75/28. The outer-1 switch of SUE1/2 away from IBES on
"split-adjustment" grounds rested on a false premise — the reverse-split artifact
found in outer-1 lives in the price-target file (`ptgsum`), NOT in `act_epsus` EPS.
Both Compustat `epspx` and IBES `act_epsus` are split-adjusted; no cumulative-`adj`
operation is required on the actuals.

### Task 2 — SUE1/SUE2 on IBES quarterly actuals (candidate, NOT committed)
Seasonal-RW SUE (announcement-aligned via anndats) on split-adjusted IBES QTR actuals
(n=726,572 mapped; 205,293 with >=4 prior seasonal diffs):
SUE1 D1..D10 medians = -0.057, 0.020, 0.074, 0.194, 0.310, 0.387, 0.530, 0.645,
0.599, 0.242 (spread -0.299 vs paper +0.70). The seasonal-diff numerator median runs
D1 -0.0076 -> D10 +0.0208 (dollars/share) — the SAME positive-in-D slope, i.e. the
**wrong sign** gradient, that the Compustat source also produces. The seasonal random
walk's predicted surprise is mean-zero BY CONSTRUCTION; it cannot produce the paper's
D1 +0.23 -> D10 -0.47 regardless of EPS source. Switching Compustat -> IBES moves each
decile by ~0.03-0.10 but preserves the flat/wrong-signed structure. Cell movement vs
committed: no net improvement.

### Task 3 — SUE3 check (the variable the paper is actually about)
SUE3 = (actual - meanest)/sigma_analyst. Two problems predate any split question:
1. **Split-inconsistent outliers**: statsum_epsus `.actual`/`.meanest` range over
   [-1.31e9, +2.84e8] in the June snapshots (ACTC -9.6e7, GNTA -5.0e6, NEXM -3.5e5,
   NCT -3.1e4, …). ~3.2% of rows have |actual-meanest| > 5x|meanest|. Raw error mean
   is -47,583 (dominated by these reverse-split firms).
2. After dropping |err|>5x|meanest|: median err -0.0038 (48.5% of firms beat, 51.8%
   miss) — a weak/mixed tilt, NOT the paper's clean D1 +0.038 -> D10 0.000 decline.
Committed SUE3 D1..D10 (all ~-0.21 to -0.09) therefore INHERITS the reverse-split
contamination: its sign is an artifact, and its gradient (flattening toward D10) is
directionally consistent with the paper but offset. A split-consistent `actual`/`meanest`
pairing for SUE3 is not available in the current 202601 vintage (act_epsus has no paired
forecast; surpsum.suescore is the proprietary IBES score, not Livnat-Mendenhall).

### Task 4 — EG source comparison (three realized-EPS measures)
EG_{t-6:t-1} D1/D10 (paper 6.95 / 30.56): Compustat epspx = -0.53 / 7.81; IBES ANN
act_epsus = 1.21 / 14.48; Compustat epsfx = -0.61 / 7.05.
EG_{t:t+5} D1/D10 (paper 10.11 / 10.85): epspx = 7.48 / 7.28; IBES act = 12.14 / 13.64;
epsfx = 7.28 / 7.82.
IBES act_epsus is the best single source (positive D1 in the backward window, ~half the
paper's levels) but still ~2x below the paper's backward-window D10 (14.5 vs 30.6). No
source closes the backward-EG gradient; the paper's 30.56 D10 backward growth is not
reproduced under any realized-EPS measure in the current vintage.

### Task 5 — footnote-17 resolution (report-only; committed targets unchanged)
Footnote 17 (L1929) states the three SUE variants "following Livnat and Mendenhall
(2006)" and immediately ties the discussion to "Research in accounting associates
earnings that just meet analyst forecasts with earnings management (Skinner and Sloan
2002; Burgstahler and Eames 2006)." Both citations are about meeting ANALYST forecasts.
The conclusion narrative (L2348: "negative earnings surprises ... earnings management")
therefore refers to **SUE3 (analyst-forecast-based)**, not the seasonal-random-walk
SUE1/SUE2. The seasonal-RW SUE1/SUE2 measures are included in the paper only for
robustness across SUE definitions; the substantive "expectations" claim is carried by
SUE3. Given (a) SUE1/2 cannot produce a duration gradient by construction and (b) SUE3
is the claimed mechanism but is split-contaminated in this vintage, the committed SUE1/
SUE2/SUE3 targets should NOT be re-weighted on the current evidence: the SUE1/SUE2 cells
are unattainable under any realized-EPS seasonal-RW source, and the SUE3 cells are
blocked by a vintage-level split-inconsistency rather than an implementation error.

(For the record: the schema note above that says "act_epsus ANN ... is UNadjusted for
splits" is WRONG — see Task 1. Renaming this note is cosmetic and out of scope here.)

### Decile composition after the coverage screen (median June price / ME)
| Decile | n | median price ($) | median ME ($) |
|---|---|---|---|
| D1 | 7221 | 10.25 | 95956500 |
| D2 | 7239 | 13.50 | 169262500 |
| D3 | 7232 | 16.00 | 228592500 |
| D4 | 7237 | 17.25 | 278448660 |
| D5 | 7238 | 18.08 | 322538080 |
| D6 | 7231 | 19.28 | 350627750 |
| D7 | 7233 | 19.50 | 370197000 |
| D8 | 7236 | 20.00 | 405937350 |
| D9 | 7235 | 18.12 | 335907250 |
| D10 | 7245 | 8.00 | 137009700 |

## Audit-3 [M1] — split-consistent SUE3 re-derivation (outer 4, inner 1)

Commit-decision evidence. The audit measured a 3.2% tail in `statsum_epsus` June
snapshots and prescribed a split-consistent re-derivation. Repro harness:
`src/sue3_split_fix.py` (scratch, does NOT touch metrics.json).

### Split-inconsistency mechanism (diagnosed)
The tail is **reverse-split persistence**, not unpaired bases in the same snapshot.
`statsum_epsus.actual` is forward-persisted from the pre-reverse-split per-share basis
into the post-reverse-split row, while `meanest` is written on the row's current basis.
A reverse split collapses the share count and makes stale per-share EPS misleadingly
large. Measured 4.11% of rows have |err|>5x|meanest| (12,364/300,691; the audit's 3.2%
used a stricter pre-filter). Concrete examples (all actual on a stale basis):
- ACTC 03818830 fpedats 2006-12-31: actual -624,000,000 vs meanest -24,000,000
- GNTA 37245M50 fpedats 2008-06-30: actual -5,025,000 vs meanest -35,000
- ACRS 52729M10 fpedats 1998-03-31: actual -18,150,000 vs meanest 1,050,000

The cumulative split factor `adj` (verified: current-basis EPS = raw / adj; AAPL FY2012
44.15/28 = 1.5768) is >= 1 for forward-split firms and < 1 for reverse-split firms.
AAPL/MSFT spot-check: statsum actuals are already on the current basis (median |actual|
0.006 / 0.175), never in the tail — the contamination is confined to reverse-split firms.

### Split-consistent re-derivation + result
Standardised actual/meanest to the current basis (`/adj`) and dropped reverse-split rows
(`adj < 1`), removing the 14.7% of the tail attributable to reverse splits. Result:

| screen | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D1D10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| none (committed) | -0.209 | -0.212 | -0.193 | -0.165 | -0.156 | -0.191 | -0.136 | -0.090 | -0.072 | -0.114 | -0.095 |
| drop_revsplit | -0.207 | -0.206 | -0.189 | -0.167 | -0.156 | -0.185 | -0.142 | -0.083 | -0.082 | -0.111 | -0.096 |
| paper | 0.038 | 0.022 | 0.030 | 0.018 | 0.028 | 0.020 | 0.029 | 0.014 | 0.000 | 0.000 | 0.038 |

The fix moves D1 by +0.003 (all 11 cells remain sign-mismatch FAIL). **Commit bar NOT
met** (net 0, far below +3-of-11); metrics.json LEFT UNCHANGED.

### Residual gap (likely cause)
The forecast-error distribution is essentially symmetric around zero: 45.5% beat / 50.1%
miss (4.6% exact zero), median error -0.005, winsorized mean -0.113 $/share. A
symmetric, unbiased consensus forecast can only yield a near-zero sign-neutral SUE3
gradient. The paper's positive D1 (+0.038) implies analyst forecasts *systematically
under-estimate* long-duration firms (a positive-surprise bias); the 202601 summary
forecasts show no such directional bias. This is a distributional property of the
vintage (unbiased forecasts), not a split artifact, so no re-derivation closes the gap.
