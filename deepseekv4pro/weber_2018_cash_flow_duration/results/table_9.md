# Table 9 Panel A — Price targets (ours)

TS-average of annual cross-sectional MEANS of five duration quintiles,
July 2001–June 2014.

| Row | D1 | D2 | D3 | D4 | D5 | D1D5 |
|---|---|---|---|---|---|---|
| PTB | 1.282 | 2.031 | 3.007 | 5.037 | 11.627 | -10.345 |
| PTP | 24.133 | 24.071 | 22.782 | 23.479 | 33.137 | -9.005 |

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

- PTG cusip match rate: 8781/10032 (87.5%)
- PTG firm-years after join: 28933
- PTG with BE: 28933  with price: 28543  with CRSP mcap: 28927
- PTG usable rows (be>0 & price>0 & mcap>0): 28539
- PTG target/price outliers dropped (tpr outside [0.5,2.0]): 2443

## Spot-check — large-firm consensus targets vs current price

| ticker | month | meanptg | medptg | numest | price | PTP (%) |
|---|---|---|---|---|---|---|
| AAPL | 2005-06 | 1.688 | 1.821 | 17 | 1.330 | 26.9 |
| AAPL | 2010-06 | 11.208 | 11.607 | 38 | 9.540 | 17.5 |
| MSFT | 2005-06 | 31.604 | 32.000 | 24 | 25.260 | 25.1 |
| MSFT | 2010-06 | 34.536 | 36.000 | 28 | 26.320 | 31.2 |
| GE | 2005-06 | 329.500 | 328.000 | 16 | 290.560 | 13.4 |
| GE | 2010-06 | 176.615 | 176.000 | 13 | 126.800 | 39.3 |
| IBM | 2005-06 | 93.933 | 92.000 | 15 | 76.300 | 23.1 |
| IBM | 2010-06 | 144.595 | 148.000 | 21 | 130.350 | 10.9 |
| JNJ | 2005-06 | 74.250 | 76.500 | 12 | 66.350 | 11.9 |
| JNJ | 2010-06 | 70.842 | 70.000 | 19 | 59.240 | 19.6 |
| WMT | 2005-06 | 19.197 | 19.250 | 14 | 16.620 | 15.5 |
| WMT | 2010-06 | 20.736 | 20.667 | 24 | 16.990 | 22.0 |
| KO | 2005-06 | 23.232 | 22.750 | 14 | 21.820 | 6.5 |
| KO | 2010-06 | 30.893 | 31.000 | 14 | 26.200 | 17.9 |
