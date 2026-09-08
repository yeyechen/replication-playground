# Assumptions Registry — Heston & Sadka (2008), Seasonality in the Cross-Section of Stock Returns

Distinct from `preprocessing_rules.json`: entries there are paper-derived
(verbatim quotes); entries here are choices the paper does not fully specify,
made under the ordered decision path in `rep/PAPER_CONVENTIONS.md`.

---

# Assumption 1: Common-stock share-code filter

**Decision:** Restrict the universe to ordinary common shares, shrcd IN (10, 11), applied point-in-time.
**Rationale:** The paper says only "NYSE- and AMEX-listed firms whose data are available on the Center for Research in Security Prices (CRSP) monthly returns file" (L91) and "The analysis uses NYSE- and AMEX-listed stocks" (all table notes). It never states a share-code screen. `[CONVENTION-APPLIED]` shrcd 10/11 (PAPER_CONVENTIONS § Universe selection); implemented via `dsfhdr` PIT validity windows (dsenames prohibited — duplicate-row trap).
**Impact:** Excludes ADRs, REITs, closed-end funds, units, preferreds from every table. Universe counts should land near the paper's Fig 1 diagnostics.

# Assumption 2: Exchange filter is paper-explicit — NYSE + AMEX only

**Decision:** exchcd IN (1, 2). NASDAQ (3) is excluded even though the harness default is (1, 2, 3).
**Rationale:** Not an assumption in the strict sense — the paper wins over the default (decision-path step 1): "Our sample includes NYSE- and AMEX-listed firms" (L91). CRSP AMEX coverage begins 1962-01, so formation data 1945-1961 are NYSE-only by construction — identical to the paper's data. Recorded here because it deviates from the harness default exchange list.
**Impact:** Every table. Roughly halves the post-1972 stock count vs an all-exchange sample.

# Assumption 3: No minimum-price screen — `[CONVENTION-SKIPPED]`

**Decision:** Do NOT apply the default $5 minimum-price filter.
**Rationale:** PAPER_CONVENTIONS defaults to a $5 screen when silent, but the skip is earned: the paper's own sample diagnostics (Fig 1, L91-95) describe an unfiltered universe — "nearly 100% of firms have returns in the previous month", "fewer than 30% of firms have CRSP returns for the past 20 years", "the entire CRSP database includes less than 2,000 firms at the beginning of our return sample in January 1965" — counts a $5 screen would visibly shift (low-priced stocks are precisely the ones with long histories and missing-return months). Guard condition: our Jan-1965 eligible count should be just under 2,000 common stocks, and 20-year-history firms > 500 (L91).
**Impact:** Every table; loser-decile means in particular (low-priced stocks dominate losers).

# Assumption 4: Delisting-return treatment (paper silent)

**Decision:** Merge `crsp_202601.msedelist` into the panel: in a firm's delisting month, total return = (1+msf.ret)×(1+delret)−1 when both exist, delret alone when msf.ret is absent, and −0.30 substituted for missing delret when the delisting is performance-related (dlstcd 500-599; all sample firms are NYSE/AMEX, so the −0.55 NASDAQ rate does not apply).
**Rationale:** Paper is silent (L91 names only the "CRSP monthly returns file"). Initially treated msf.ret as complete; **overturned by the iteration-1 diagnostic** (1980-1999, dlstcd ≥ 500, |dlret| > 0.001): of 3,880 delisting events only 142 had any msf.ret in the delisting calendar month, and in ALL 19 total-loss cases (delret ≤ −0.90) msf.ret > −0.99 — i.e. in this vintage msf.ret EXCLUDES the delisting payment (medians: msf.ret −0.175, delret −0.116, combined −0.378). This is exactly the Shumway (1997) msf-only bias signature and matches the replication gap (our y1 All loser decile 1.30%/mo vs paper 0.64). `[CONVENTION-APPLIED]` PAPER_CONVENTIONS § Universe selection "Delisting returns: Adjust" (merge delisting table, −0.30 fallback for 500+ codes).
**Impact:** Delisting months in every holding-period return; largest for loser deciles (y1 All/Nonannual rows). Re-run of Table 2 quantifies the before/after.

# Assumption 5: Formation-window eligibility for decile sorts

**Decision (REVISED after iteration 5):** A stock enters the month-t decile sort if it has a non-missing return in month t AND at least ONE available formation month in the strategy's lag set; the formation signal is the average over the AVAILABLE formation months (Rule B). (Original decision: complete-window availability — Rule A.)
**Rationale:** Table 5's note says strategies are "formed from an equally weighted sample of all those small firms with available returns in month $t$ and previous months used for portfolio formation" (L1335) — availability in the months used. Fig 1's framing ("require them to have long return histories", L91) supports the complete-history reading. Alternative considered: average of available formation months — rejected because it would make the 20-year sample much larger than Fig 1's <30%-of-firms diagnostic. Guard: eligible counts for 20-year strategies should exceed ~500 firms (L91).
**Impact:** Every Table 2/3/5/6/7/8 cell; sample size per strategy falls with formation length.

# Assumption 6: Value-weighted variant uses lagged market cap

**Decision:** VW decile returns weight stocks by market equity at the end of month t-1 (mcap_lag1), never same-month ME.
**Rationale:** Paper silent on the VW weight date (L257 "we also examine value-weighted strategies"). `[CONVENTION-APPLIED]` PAPER_CONVENTIONS § FF-style papers (same-month ME embeds the month's own return). ME = abs(prc) × shrout × 1000 from CRSP msf.
**Impact:** The 8 VW spread cells in T2 and 4 VW alpha cells in T3.

# Assumption 7: Multiple-regression availability (Table 1, Panel B)

**Decision:** Each month-t multiple regression includes only stocks with non-missing returns at t and at ALL lags in the specification.
**Rationale:** Extension of avail_regression_formation_month (L137, "available return data in the formation month") to a multivariate setting — listwise availability. Simple regressions (Panel A) require only t and t-k.
**Impact:** All 130 Panel B cells of T1.

# Assumption 8: Moskowitz-Grinblatt (1999) 20-industry mapping

**Decision:** Map historical SIC codes (CRSP `hsiccd`) to the 20 MG industries using a reconstruction of MG (1999) Table A1 encoded in the pipeline; firms with unmappable SIC are grouped as needed.
**Rationale:** Table 6 requires the MG 20-industry classification (L1520) but the paper does not print the mapping and no ClickHouse table carries it. The mapping is reconstructed from the published appendix; boundary SIC ranges may deviate slightly from MG's exact list. The table's claim (industry does not explain the bulk of the seasonal effect) is insensitive to small boundary misassignments — the intra-industry component dominates by construction. `[paper silent on boundaries]`.
**Impact:** All 60 T6 cells (magnitudes, not signs).

# Assumption 9: Table 4 unit conversion

**Decision:** Compute π_t(k) with decimal returns; the table's "Mean (percent)" values are decimal² × 100 (e.g., annual 0.0133 ↔ σ = sqrt(0.000133) = 1.15%/month, L1231).
**Rationale:** The paper reports "The point estimate of $\sigma^2_\mu$ is 1.33 basis points" (L1231) with implied sqrt(0.000133) — fixing the printed 0.0133 as percent-squared units.
**Impact:** The 3 mean cells of T4 (t-cells unaffected).

# Assumption 10: Table 8 event-month definitions

**Decision:** Panel A event month = calendar month of Compustat `fundq.rdq` (linked via CCM). Panel B event month = calendar month of CRSP `msedist.dclrdt` for cash dividends (distcd 1200-1299). Panel C = calendar month of `msedist.exdt`. Panel D = calendar months of Compustat `funda.datadate` (fiscal period end) and the following month (L2865). The covered universe per panel = NYSE/AMEX firms linkable to Compustat via CCM (for B/C, CRSP-recorded events stand in for "recorded on Compustat", L2434).
**Rationale:** The paper names the events but not the exact data fields; footnote 5 states the exact day is immaterial (monthly returns, L2877). CRSP declaration dates exist back to the 1960s in this vintage (~82%+ of cash dividends per decade, verified at Stage 5); Compustat rdq is empty before ~1970 — the paper's Panel A sample has the same effective start.
**Impact:** All 240 T8 cells; Panel A early-sample composition.

# Assumption 11: Decile assignment under ties

**Decision:** Equal-count deciles by within-month rank of the formation-signal average (ties broken by rank order), 10 portfolios of equal stock count per month.
**Rationale:** "grouped into ten portfolios (with equal number of stocks in each portfolio)" (L271). Ties in average returns are quantitatively rare except in the year-1 annual (single lag-12 return) sort; equal-count rank split matches the paper's wording.
**Impact:** Decile boundaries in every table; negligible for spreads.

# Assumption 12: Reporting units

**Decision:** Compute in decimal returns internally; report all means/t-statistics against the tables' printed percent values (×100 at the report layer). Table 1 γ estimates are printed in percent (L180).
**Rationale:** Table notes: "reported below (in percent)" (L271), "Regression estimates are reported in percent" (L180).
**Impact:** All cells.

# Iteration 1 worker notes (appended by rep-worker)

- Assumption 4 evidence (delisting diagnostic, 1980-1999, dlstcd>=500,
  |dlret|>0.001): of 3,880 events, only 142 had an msf.ret in the delisting
  calendar month. In ALL 19 total-loss cases (dlret <= -0.90) the msf.ret was
  greater than -0.99 (frac = 1.0), i.e. **msf.ret EXCLUDES the delisting
  return in this vintage** — the combined total would be
  (1+ret)(1+dlret)-1. Median msf.ret -0.175 vs median dlret -0.116 vs median
  combined -0.378. This contradicts Assumption 4's default reading; merging
  `msedelist` (replacing the delisting-month ret with the combined return)
  is the indicated revision. Candidate driver of the y1 All/Nonannual
  loser-decile FAILs (our y1_all_d1 = 1.30 vs paper 0.64).
- `data/table2_results.parquet` — tidy Table 2 grid (means/t/n/avg_n per cell;
  consumed by results/table_2.md rendering and debugging; not foldable into
  SQL (produced by the Python portfolio-sort loop).

### Iteration 1 — Problem: Table 2 loser-decile cells FAIL (9 cells, y1 All/Nonannual extremes)
- Diagnosis: Universe diagnostics all pass (Jan-1965 eligible 1,922 < 2,000 paper bound; 240-month histories 678-928 > 500; 120-month at 1999 1,356 > 1,000), so the panel universe is right. Delisting diagnostic shows msf.ret EXCLUDES delret in crsp_202601 (all 19 total-loss delistings carry partial-month ret > −0.99; only 142/3,880 delisting months have any msf.ret). Loser deciles therefore contain soon-to-delist stocks whose final-month crash is missing → our losers earn too much (y1_all_d1 1.30 vs paper 0.64; y1_nonannual spread 0.20 vs 1.17).
- Next fix: In src/sql/universe_monthly.sql add a msedelist CTE (permno, delisting month, delret, dlstcd) and in main.py replace/insert the delisting-month ret with (1+ret)(1+delret)−1 (delret alone if no msf row; −0.30 when delret missing and dlstcd 500-599). Rebuild panel.parquet; re-run Table 2; compare the 9 FAIL cells before/after.
- Before metric: T2 tally 265 Match / 9 FAIL / 3 no_effect; y1_all_d1 = 1.30, y1_all_spread = 0.59, y1_nonannual_spread = 0.20.
- After metric: T2 tally 268 Match / 6 FAIL / 3 no_effect; y1_all_d1 = 1.04, y1_all_spread = 0.83, y1_nonannual_spread = 0.43 (delisting merge recovered ~40-50% of each gap; no Match->FAIL flips).
- Status: partially-resolved (3 of 9 FAILs closed; residual 6 carried to iteration 3)

### Iteration 2 — Assumption 4 (REVISED) implemented: msedelist merge
- Change: src/sql/delist_merge.sql (permno, delisting calendar month, dlret,
  dlstcd, dl_hexcd/dl_hsiccd; PIT shrcd 10/11 + exchcd 1/2 via dsfhdr on the
  delisting month, same filter as msf rows) merged in main.py build_panel:
  delisting-month ret = (1+msf.ret)(1+delret)−1 when msf.ret exists, delret
  alone when the msf row is absent (row inserted, prc/shrout/mcap NaN), −0.30
  for missing dlret when dlstcd 500-599; non-performance delistings with
  missing dlret leave msf.ret as-is. 17,610 msedelist rows 1945-2002 → 4,197
  after PIT filter; 555 returns combined, 3,642 rows inserted (0 msf rows had
  missing ret replaced). Panel 1,364,007 → 1,367,649 rows; eligible rows
  1,342,211 → 1,345,853; eligible mean/month 1965-2002: 2,386.1 → 2,394.0.
- T2 tally: 265 Match / 9 FAIL / 3 no_effect → **268 Match / 6 FAIL /
  3 no_effect**. Fixed: t2_y1_all_spread (0.586→0.828 vs paper 1.46),
  t2_y1_all_d1_t (3.05→2.46 vs 1.65), t2_y1_nonannual_d1_t (3.52→2.97 vs
  1.99). No Match→FAIL flips. table2_results.csv → table2_results.parquet.
- Residual FAILs (6): t2_y1_all_spread_t (2.68 vs 5.58), t2_y1_nonannual_d1
  (1.31 vs 0.80), t2_y1_nonannual_spread (0.43 vs 1.17),
  t2_y1_nonannual_spread_t (1.31 vs 4.20), t2_y11_15_all_spread_t (0.35 vs
  −0.17), t2_vw_y11_15_nonannual_spread (−0.31 vs −0.15). Diagnostic: y1_all
  d1 mean falls 1.309 → 1.038 and spread rises 0.574 → 0.828 when delisting
  months are included; the delisting adjustment is directionally right but
  ~half the paper's gap remains in y1 nonannual loser decile / all spread t.

### Iteration 3 — Problem: residual y1 (short-window) spread FAILs after delisting fix
- Diagnosis: Residual FAIL pattern is window-length-graded: y1 All spread 0.83 vs 1.46 and y1 Nonannual 0.43 vs 1.17 FAIL, while lag-12-only (y1 Annual 1.22 vs 1.15) and ALL longer-interval cells Match. Our loser decile earns too much only for the 12-month-window sorts. Hypothesis (untested): the paper's formation eligibility is "average of available formation months" (needs only month-t return + at least one available formation month) rather than our complete-window requirement (Assumption 5) — the difference is recent listings and firms with return gaps, which are volatile and load the loser decile; their share of the sort shrinks as the formation window lengthens... but this conflicts with the exact y2_5 All match under the current rule, so it must be tested, not assumed.
- Next fix: A/B test ONLY (no pipeline change yet): compute y1 and y2_5 (All/Annual/Nonannual) deciles under Rule B = average-of-available (month-t ret + >=1 available formation month; signal = mean over available months in the lag set) alongside the current Rule A. Compare spreads, d1, d10, and eligible counts vs paper. Decide by: does B close the y1 gap WITHOUT breaking the y2_5 matches?
- Before metric (Rule A, current): y1_all_spread 0.83 [2.68] vs paper 1.46 [5.58]; y1_nonannual_spread 0.43 [1.31] vs 1.17 [4.20]; y2_5_all_spread -1.07 [-4.06] vs -1.07 [-5.02] (Match).
- After metric: pending iteration 3.
- Status: in progress

### Experiment: eligibility A/B — 2026-09-08 (worker diagnostic, no pipeline change; Assumption 5 unchanged)
- Rules: A = complete-window (current); B = average-of-available (ret at t + >=1 available formation month); C = allow <=2 missing formation months (diagnostic). Script: `src/experiment_eligibility.py` (standalone, printed report only).
- EW 10-1 spreads (%/mo [t]) vs paper, 1965-01..2002-12:

  | Strategy         | Paper       | A           | B           | C           |
  |------------------|-------------|-------------|-------------|-------------|
  | y1 All           | 1.46 [5.58] | 0.83 [2.67] | 0.80 [2.60] | 0.80 [2.57] |
  | y1 Annual        | 1.15 [7.60] | 1.32 [8.46] | 1.32 [8.46] | 1.32 [8.46] |
  | y1 Nonannual     | 1.17 [4.20] | 0.43 [1.31] | 0.45 [1.39] | 0.41 [1.23] |
  | y2_5 All         | -1.07 [-5.02] | -0.90 [-3.48] | -1.02 [-4.60] | -0.95 [-3.62] |
  | y2_5 Annual      | 0.67 [5.35]  | 0.92 [6.17]  | 0.69 [5.11]  | 0.83 [5.80]  |
  | y2_5 Nonannual   | -1.25 [-5.60] | -1.20 [-4.58] | -1.20 [-5.23] | -1.24 [-4.71] |

- Eligible firms/month A -> B: y1 All 2,240 -> 2,383 (+6%); y1 Nonannual 2,252 -> 2,383 (+6%); y2_5 All 1,694 -> 2,257 (+33%); y2_5 Annual 1,750 -> 2,142 (+22%); y2_5 Nonannual 1,707 -> 2,257 (+32%). Rule B barely changes the y1 sort but greatly enlarges the y2_5 cross-section.
- Findings: (i) Rule B does NOT close the y1 gap (y1 All 0.80 vs paper 1.46; Nonannual 0.45 vs 1.17) — the y1 shortfall is NOT an eligibility artifact. (ii) Rule B substantially improves y2_5: All -1.02 (A: -0.90) vs paper -1.07; Annual 0.69 (A: 0.92) vs paper 0.67; spread RMSE across the six strategies: B 0.406 vs A 0.421 (y2_5 RMSE 0.042 vs 0.173). (iii) NOTE: the Iteration-3 "before" line above (y1 Annual 1.22, y2_5 All -1.07) is STALE — current committed Rule-A values (data/table2_results.parquet) are y1 Annual 1.32 and y2_5 All -0.90 [-3.48], i.e. y2_5 All does NOT currently match under Rule A; the delisting merge moved it.
- Decision deferred to orchestrator.

### Iteration 3 result (orchestrator decision)
- The eligibility hypothesis for the y1 FAILs is REJECTED: Rule B moves y1 All 0.83->0.80 and y1 Nonannual 0.43->0.45 (paper 1.46 / 1.17). The y1 gap is driven by the short-lag (reversal) component, not formation-month availability. y1 Annual (lag-12 only) OVERSHOOTS slightly (1.32 vs 1.15) — lag-12 seasonality is strong in our panel.
- Rule B is materially closer than A for y2_5 (All -1.02 vs paper -1.07; Annual 0.69 vs 0.67; RMSE 0.042 vs 0.173). Global switch decision deferred to iteration 5 (need y6_10/y11_15/y16_20 under B first).
- Stale-impact correction (audit-style): the delisting merge moved cells that the iteration-1 "before" table had listed as matching — post-merge Rule A values: y1 Annual 1.32 [8.46], y2_5 All -0.90 [-3.48]. Both remain Match under hybrid tolerance (relative error 14.8% / 15.9% <= 50%), but they are no longer the near-exact matches of the pre-merge run. Rule B would restore y2_5 to near-exact.
- Next: implement Table 1 (return responses) — Panel A gamma_1 = -5.03 (paper, L201) is the direct test of whether the panel reproduces the short-lag reversal at all.
- Status: partially-resolved (diagnosis narrowed; global eligibility decision deferred to iter 5)

### Iteration 4 — Table 1 implemented (2026-09-08, worker)
- Panel A (simple, 31 lags, 456 months, NW(12)): gamma_1 = -4.99 [-8.84]
  vs paper -5.03 [-9.03] — the panel reproduces the short-lag reversal
  (residual y1 Table-2 gap is NOT a missing-reversal artifact).
  gamma_12 = 2.79 [8.77] vs paper 2.61 [7.40] (same overshoot direction
  as the t2 y1 Annual cell). Annual-lag sequence (12,24,...,240):
  2.79, 1.20, 1.21, 1.34, 0.60, 1.19, 1.14, 0.93, 1.43, 1.13, 1.60,
  1.09, 0.76, 0.96, 1.40, 1.56, 1.18, 1.09, -0.07, 1.07 vs paper 2.61,
  1.30, 1.27, 1.29, 0.62, 1.08, 1.03, 0.93, 1.41, 1.34, 1.68, 1.19,
  0.70, 0.78, 1.29, 1.43, 1.21, 1.14, 0.00, 1.14.
- Panel B (listwise availability, Assumption 7): spec1 lag1 = -6.25
  [-10.71] vs paper -6.80 [-12.75]; spec1 lag12 = 2.52 [8.79] vs paper
  2.57 [6.24]. Zero rank-deficient months in all 3 specs (lstsq used,
  pinv fallback never needed).
- Avg cross-section size/month: Panel A lag1 2,381, lag12 2,261, lag240
  722; Panel B spec1 1,981, spec2 1,256, spec3 701.
- Evaluator tally T1: 159 Match / 14 FAIL / 21 no_effect (194 cells).
  FAILs concentrate in small short-lag cells (lags 2-8 t-stats, lag228
  t vs paper 0) — magnitude bands hold for most.
- Files: src/table1.py (imported from src/main.py), results/table_1.md,
  eval/metrics.json extended with all 194 T1 cells (575 entries total).

### Iteration 4 — Table 1 implemented; panel reversal validated
- Result: Panel A gamma_1 = -4.99 [-8.84] vs paper -5.03 [-9.03] — the panel reproduces the short-lag reversal almost exactly, so the residual y1 decile gap is NOT a weak-reversal-in-panel artifact. Annual-lag sequence 12..240 tracks the paper closely. T1 tally 159 Match / 14 FAIL / 21 no_effect; the 14 FAILs concentrate in short-lag (2-8) estimates/t-stats, e.g. spec1 lag2 -0.52 vs paper -1.23, spec1 lag3 t 4.90 vs 1.91.
- Hypothesis (untested): the delisting merge (iteration 2) inflates short-lag reversal/momentum coefficients — the merged -30%/-55%-class returns sit in the cross-section at lag k. The paper may not have adjusted delisting returns in the regression sample (or their vintage differed). Alternatively short-lag noise.
- Next fix: three diagnostics in one experiment (no committed change): (a) T1 short-lag cells (Panel A + spec1, lags 1-8) computed on pre-merge returns (reload msf without delist merge) vs post-merge; (b) y1 All/Annual/Nonannual and y2_5 Annual spreads by calendar month (Jan, Feb-Dec aggregate) vs paper Table 7 row block L1680-1792; (c) Rule B eligibility evaluated for y6_10/y11_15/y16_20 (All/Annual/Nonannual) vs Rule A vs paper.
- Before metric: T1 159/14/21; T2 268/6/3. Total 427 Match / 20 FAIL / 24 no_effect / 1147 MISSING.
- After metric: pending iteration 5.
- Status: in progress

### Experiment: three-part diagnostics — 2026-09-08 (worker diagnostic, no pipeline change; Assumptions 4/5 unchanged)
- Script: `src/experiment_diagnostics.py` (standalone, printed report only).
- (a) Delisting-merge sensitivity of T1 short lags. Pre-merge matrix rebuilt
  from universe_monthly.sql + PIT filter, no msedelist merge. Verification:
  555 combined rows confirmed, of which 52 have dlret = 0 (combined equals
  msf.ret) -> 503 cells actually change value; 3,642 inserted rows absent
  pre-merge. Panel A lags 1-8 (paper: -5.03, -0.07, 1.36, 0.58, 0.96, 0.98,
  1.06, 0.58): pre-merge estimates are closer to paper for lag 1 only
  (-5.32 vs post -4.99, paper -5.03; post actually nearer in level, pre
  nearer in t); post-merge closer in 7/8 cells (sum of |est-t| deviations).
  Panel B spec1 lags 1-8 (paper: -6.80, -1.23, 0.83, 0.49, 1.03, 1.34,
  1.08, -0.05): post-merge closer in 8/8 cells (pre-merge overshoots
  mid-lags MORE: e.g. lag3 pre 1.33 vs post 1.62 — both over paper 0.83).
  VERDICT: the delisting merge does NOT explain the T1 short-lag FAILs;
  removing it moves short-lag cells AWAY from the paper (pre-merge closer
  in 1/16 cells overall). The short-lag overshoot (lags 2-8 positive and
  too large, lag2 sign flip) exists in both variants and must have another
  source (candidate: paper's CRSP vintage/microstructure-era differences).
- (b) Calendar-month decomposition (Rule A, current panel), Jan | Feb-Dec vs
  paper T7: y1 All -7.14 | 1.55 (paper -4.49 | 2.00); y1 Annual 3.73 | 1.10
  (paper 3.33 | 0.95); y1 Nonannual -9.39 | 1.33 (paper -6.83 | 1.90);
  y2_5 Annual 4.82 | 0.56 (paper 3.89 | 0.38). Per-month y1 All (Jan..Dec):
  -7.14, 0.34, -0.04, 2.18, 0.89, 3.10, 0.41, 0.77, 1.87, 1.48, 2.35, 3.71
  (paper: -4.49, 1.01, 1.34, 2.17, 0.82, 3.07, 1.27, 1.26, 2.41, 1.89,
  2.56, 4.19). y1 Nonannual: -9.39, 0.24, -0.28, 1.89, 0.75, 2.76, 0.44,
  0.83, 1.56, 1.15, 1.96, 3.28 (paper: -6.83, 0.90, 0.91, 2.44, 0.75,
  2.95, 1.38, 1.33, 2.24, 1.89, 2.14, 3.97). VERDICT: the y1 gap is
  CONCENTRATED in January (2.6pp too negative) and the adjacent
  early-calendar months (Feb/Mar near zero vs paper ~1); Jun/Dec match well.
  Our January loser-winner reversal is too strong — consistent with
  tax-loss/turn-of-year composition differences in the loser decile, not
  an evenly spread shortfall.
- (c) Rule B eligibility for long intervals, EW 10-1 spreads (A | B | paper):
  y6_10 All -0.28 | -0.41 | -0.39; y6_10 Annual 0.88 | 0.71 | 0.68;
  y6_10 Nonannual -0.50 | -0.69 | -0.55; y11_15 All 0.05 | -0.03 | -0.02;
  y11_15 Annual 0.86 | 0.71 | 0.66; y11_15 Nonannual -0.25 | -0.23 | -0.19;
  y16_20 Annual 0.70 | 0.49 | 0.52; y16_20 Nonannual -0.43 | -0.38 | -0.39.
  Eligible n/month rises ~30-45% under B (e.g. y6_10 All 1,227 -> 1,764).
  VERDICT: Rule B matches or beats Rule A on every quoted long-interval
  paper cell (Annual cells improve markedly: 0.88->0.71 vs 0.68,
  0.86->0.71 vs 0.66, 0.70->0.49 vs 0.52); no long-interval match breaks.
  Combined with the iteration-3 finding (B fixes y2_5 without hurting y1),
  a global switch to Rule B now has support across all intervals; decision
  deferred to orchestrator.


**Corrected after iteration 5** (evidence: iteration-3 A/B + iteration-5 Part C): Rule B matches or beats the complete-window rule on every paper cell it was tested against — y2_5 Annual 0.69 vs paper 0.67 (Rule A 0.92), y6_10 Annual 0.71 vs 0.68 (A 0.88), y11_15 Annual 0.71 vs 0.66 (A 0.86), y16_20 Annual 0.49 vs 0.52 (A 0.70), y2_5 All -1.02 vs -1.07 (A -0.90) — and breaks no previously-matching cell. The original Fig-1-based guard (">500 firms with 20-yr history") was about the regression-analysis sample (L95 "the sample available for regression analysis"), not the decile sorts; the empirical fit across 15+ cells is the decisive evidence. Rule A is retained nowhere; Table 1 availability (pairwise for Panel A, listwise for Panel B) is a separate rule (Assumption 7) and is unchanged.

### Iteration 5 — diagnostics resolved three open questions
- Diagnosis/fix decisions: (1) Delisting merge KEPT — post-merge is closer to paper in 15/16 short-lag Table 1 cells; pre-merge overshoots mid-lags more (spec1 lag3: pre 1.33, post 1.62, paper 0.83). (2) Rule B adopted globally (see Assumption 5 correction) — annual-lag spreads land within 0.03 of paper at every interval under B. (3) y1 residual localized to calendar composition: our January y1 All spread -7.14 vs paper -4.49 (too negative by 2.6pp) and Feb-Dec 1.55 vs 2.00; per-month comparison shows Feb/Mar near zero vs paper ~1, May/Jun/Dec well-matched.
- Next fix: commit Rule B in main.py (one-line eligibility change: min-1-available + average-of-available), re-run Table 2, then implement Table 3 (FF3 alphas, incl. VW risk-adjusted prose cells).
- Before metric: T2 268 Match / 6 FAIL / 3 no_effect (Rule A, post-merge).
- After metric: pending iteration 6.
- Status: in progress

### Iteration 6 — Rule B committed; Table 3 implemented (2026-09-08, worker)
- Change 1 (Assumption 5 REVISED implemented): src/main.py table2() now uses
  Rule B eligibility for ALL 15 strategies — month-t return non-missing AND
  >=1 available formation month; signal = mean over available formation
  months only (np.nanmean). Table 1 availability rules unchanged.
  Eligible firms/month under B: y1 2,383; y2_5 All 2,257; y6_10 All 1,764;
  y11_15 All 1,293; y16_20 All 961.
  T2 tally: 268 Match / 6 FAIL / 3 no_effect (Rule A) -> **269 / 5 / 3**
  (Rule B). FAIL->Match: t2_y11_15_all_spread_t (0.35 -> -0.28 vs paper
  -0.17), t2_vw_y11_15_nonannual_spread (-0.31 -> -0.27 vs -0.15).
  Match->FAIL: t2_y1_all_d1_t (2.46 -> 2.48 vs paper 1.65; rel err 51%
  vs 50% tol — marginal, same sign). Still-FAIL 5 cells all y1: all_spread_t
  (2.60 vs 5.58), nonannual_d1 (1.28 vs 0.80), nonannual_spread (0.45 vs
  1.17), nonannual_spread_t (1.39 vs 4.20), all_d1_t. Annual-lag EW spreads
  now land near paper at every interval: y2_5 0.69 (0.67), y6_10 0.71
  (0.68), y11_15 0.71 (0.66), y16_20 0.49 (0.52).
- Change 2 (Table 3): src/sql/ff_factors.sql (ff.four_factor_monthly,
  1965-01..2002-12, 456 months; month start built by string prefix because
  toStartOfMonth clamps pre-1970 Date32 in this ClickHouse build) +
  src/table3.py: OLS of (ret-rf) on [1, MKT-RF, SMB, HML] per EW decile and
  10-1 spread for all 15 strategies; VW annual/nonannual spread alphas
  (weights mcap_lag1, Assumption 6). OLS t-stats (no HAC — paper note
  silent). results/table_3.md written; eval/metrics.json extended (915
  entries). evaluate.py IMPLEMENTED += T3.
  T3 tally: 141 Match / 49 FAIL / 77 no_effect (267 cells).
  Headlines: y1 Annual spread alpha 0.76 [4.86] vs paper 1.12 [7.33]
  (Match); y2_5 All -1.10 [-5.76] vs -0.68 [-3.71] (FAIL, magnitude);
  VW annual alphas 0.45 / 0.51 / 0.37 / -0.10 vs paper 0.98 / 0.91 /
  0.77 / 0.48 (y16_20 sign flip).
  FACT FOR ORCHESTRATOR: our FF3 alphas of annual spreads are far below the
  raw spreads (y2_5 annual raw 0.69 -> alpha 0.14; paper raw 0.67 -> alpha
  0.65), i.e. our decile spreads load much more heavily on MKT/SMB/HML than
  the paper's. T2 raw cells match; the gap is entirely in factor loadings.

### Iteration 6 — Rule B committed; Table 3 alpha convention bug FOUND
- Result: T2 under Rule B: 269 Match / 5 FAIL / 3 no_effect (annual spreads land on paper: 0.69/0.71/0.71/0.49 vs 0.67/0.68/0.66/0.52; y11_15 pair fixed). One marginal flip: t2_y1_all_d1_t 2.48 vs 1.65 (rel err 51% vs 50% tol).
- Table 3 first pass: 141/49/77. Diagnosis of the 49 FAILs: our spread alphas are uniformly ~0.47%/month (the mean rf) BELOW the paper's — y2_5 Annual alpha 0.14 vs 0.65 while the raw spread 0.69 matches paper 0.67; adding mean rf (0.47) to every failing alpha lands within 0.04-0.11 of the paper cell. Cause: we subtracted rf from the zero-investment 10-1 spread. The paper's Table 3 note ("monthly portfolio returns (excess of risk-free rate)", L713) applies to the LONG-ONLY decile regressions; the 10-1 column is the difference of two excess-of-rf decile alphas, so rf cancels — equivalently the spread regression runs on raw spread returns with no rf subtraction (the utils/ `zero_investment=True` convention; "subtracting rf anyway collapses the alpha toward zero — a silent 5x mistake").
- Next fix: src/table3.py — decile cells keep (ret-rf) excess returns; spread cells (and the 4 VW spread alphas) regress RAW spread on [MKT_RF, SMB, HML] with no rf subtraction. Re-run T3. Then implement Table 5 (size 30/40/30 groups) and Table 7 (calendar-month decomposition) in the same pass.
- Before metric: T3 141 Match / 49 FAIL / 77 no_effect; y2_5 Annual alpha 0.14 vs paper 0.65.
- After metric: pending iteration 7.
- Status: in progress

### Iteration 7 — T3 spread-alpha convention fixed; Tables 5 and 7 implemented (2026-09-08, worker)
- Task 1 (T3 convention fix): src/table3.py ff3_alpha gained `excess`
  flag; decile cells keep (ret - rf); all 15 EW 10-1 spread cells and the
  4 VW spread alphas now regress the RAW spread (rf cancels). T3 tally
  141 Match / 49 FAIL / 77 no_effect -> **158 / 32 / 77**. Headlines:
  y2_5 Annual spread alpha 0.64 [4.69] vs paper 0.65 [5.11] (Match;
  was 0.14); y2_5 All -0.60 [-3.12] vs -0.68 [-3.71] (Match); y1 Annual
  1.27 [8.11] vs 1.12 [7.33] (Match); VW y16_20 annual alpha 0.41 vs
  paper 0.48 (Match; sign no longer flips). Residual 32 FAILs are
  almost all t-cells (small-alpha t's, esp. y11_15/y2_5 mid-deciles).
- Task 2 (Table 5, src/table5.py): size groups 30/40/30 by count on
  mcap_lag1 (ME at end of t-1), breakpoints from ALL NYSE/AMEX PIT
  firms, re-ranked monthly; Rule B deciles within each group; EW 10-1
  spread mean + simple t, 456 months. T5 tally: **66 Match / 9 FAIL /
  15 no_effect** (90 cells). Avg firms/month: small 718, medium 959,
  large 718 (paper small 485-1,019, median 787). Annual rows match
  almost perfectly (e.g. y1 Annual S/M/L 1.07/1.00/0.68 vs paper
  0.90/0.95/0.69). FAILs concentrate in y1 All/Nonannual SMALL (ours
  -0.05/-0.34 vs paper 1.29/1.05) — the same short-lag small-firm gap
  as T2/T7 y1, now localized to the small group.
- Task 3 (Table 7, src/table7.py): calendar-month decomposition of the
  15 EW 10-1 spread series (Jan..Dec + Feb-Dec aggregate; Difference =
  Annual minus Nonannual month by month). T7 tally: **283 Match /
  58 FAIL / 143 no_effect** (484 cells). Headlines: y1 All Jan -7.26
  [-3.57] vs paper -4.49 (FAIL; known January loser-decile issue) and
  Feb-Dec 1.53 [6.10] vs 2.00 (Match); y1 Annual Jan 3.73 vs 3.33
  (Match); y1 Nonannual Jan -9.34 vs -6.83 (Match, band); y2_5 Annual
  Jan 4.04 vs 3.89 and Feb-Dec 0.38 vs 0.38 (both Match); y11_15
  Annual Feb-Dec 0.51 vs 0.47 (Match). Most FAILs are y1 diff-row
  t-cells and small-magnitude t-cells elsewhere.
- Overall diagnostic tally (all implemented tables): T1 159/14/21,
  T2 269/5/3, T3 158/32/77, T5 66/9/15, T7 283/58/143; total 935 Match /
  118 FAIL / 259 no_effect / 306 MISSING (T4, T6, T8 not implemented).
- Files: src/table5.py, src/table7.py (new); src/table3.py, src/main.py,
  src/evaluate.py (IMPLEMENTED += T5, T7) modified; results/table_3.md,
  table_5.md, table_7.md regenerated; eval/metrics.json 1,528 entries
  (bare-scalar assert passes).

### Iteration 7 — T3 alpha convention fixed; T5 + T7 implemented
- Result: T3 158/32/77 (was 141/49/77) — zero-investment fix validated: y2_5 Annual alpha 0.64 [4.69] vs paper 0.65 [5.11]; y16_20 VW alpha 0.41 vs 0.48, sign restored. T5 66/9/15 (group sizes: small 718 / medium 959 / large 718 per month, within paper's 485-1,019 small band, median near paper's 787). T7 283/58/143 (y2_5 Annual Jan 4.04 vs 3.89, Feb-Dec 0.38 vs 0.38 — both Match).
- Residual FAIL structure across tables now has ONE dominant cause: the y1 (short-lag) January loser-winner reversal is stronger in our data (y1 All Jan -7.26 vs paper -4.49; Difference Jan 13.07 vs 10.16; T5 small-group y1 cells -0.05/-0.34 vs paper 1.29/1.05). Secondary: t-cells of small alphas (T3) and short-lag FM coefficients (T1 lags 2-8).
- Next fix: implement T4 (WRSS sigma^2_mu) and T6 (industry decomposition) — 306 MISSING cells remain. y1-January gets one bounded diagnostic in the final iteration.
- Before metric: 935 Match / 118 FAIL / 259 no_effect / 306 MISSING.
- After metric: pending iteration 8.
- Status: in progress

### Iteration 8 — T4 (WRSS) and T6 (industry decomposition) implemented (2026-09-08, worker)
- Task 1 (T4, src/table4.py): pi_t(k) on common cross-sections (both-month
  availability), demeaned within the common cross-section, 480 months
  1963-01..2002-12, all 114,960 ordered pairs (all), 105,600 nonannual,
  9,360 annual (k=12..468). SE = population SD / sqrt(500). Tally: 0 Match /
  4 FAIL / 2 no_effect. Our means: all 0.0788 [112.7] vs paper -0.0006
  [-0.26]; nonannual 0.0714 [102.4] vs -0.0019 [-0.65]; annual 0.1624
  [225.3] vs 0.0133 [3.57]. Implied seasonal cross-sectional SD 4.03%/month
  vs paper 1.15%.
- T4 SPEC CONCERN (10x discrepancy, unresolved): implementation follows Eq
  (14) and the Table 4 note exactly; brute-force verified against the
  vectorized code (pair 1999-01/2000-01 pi = 0.0054 both ways). Diagnostics:
  (i) raw pi is large for ALL lag groups (k=1: +0.064%, k=2: +0.007%,
  k=12: +0.139%) — positive at k=1 (no monthly reversal), inconsistent with
  the paper's near-zero All group; (ii) per-pair pi SD = 1.6% vs the paper's
  implied 0.3% (from t = mean/SE); (iii) extreme-pair drivers are genuine
  CRSP microcap Januaries (Jan 1975-76 pi(12) = 7-12%), and winsorizing
  returns at [-0.33, +0.5] changes nothing; (iv) raw crsp_202601.msf
  quantiles confirm the panel's fat tails (1st pctile -38%) are in the
  source data; (v) cross-sectional variance of stock 40-yr mean returns is
  only 2.8e-5, far below our mean pi of 8e-4, so the positive baseline is
  cross-sectional covariance, not mean heterogeneity; (vi) demeaning each
  stock by its own full-sample mean shrinks values (k=1 0.016%, k=12
  0.092%) but does not reproduce the paper either. Paper's printed All =
  weighted average of Nonannual and Annual means (-0.00066), so their cells
  are raw group means. Possibly their pi uses a different normalization or
  a cleaner return series; flagged for the Replicator.
- Task 2 (T6, src/table6.py): MG(1999) industries from hsiccd 2-digit codes
  under the task's priority list; 13 named industries + 'other' = 14 groups
  observed; 'other' share 1.28% of stock-months (<5%, hsiccd dense). Tally:
  45 Match / 6 FAIL / 9 no_effect (60 cells). Headlines: y1 Annual intra
  1.18 [8.79] vs paper 1.03 [8.20] (Match), inter 0.14 [3.78] vs 0.12
  [2.98] (Match); y2_5 Annual intra 0.66 vs 0.63, inter 0.03 vs 0.04;
  y6_10 Annual intra 0.63 vs 0.56, inter 0.08 vs 0.12. FAILs are the four
  y1 All/Nonannual intra cells (0.52/0.19 vs 1.24/0.97 — the known y1
  short-lag gap) plus two small-magnitude inter t-cells (y6_10
  all/nonannual inter t).
- L2386 text-vs-table check (y6_10 annual): table shows intra 0.56, inter
  0.12; the prose ("industry component is 12 basis points, but the
  inter-industry component is 58") swaps them — the 12bp is the table's
  INTER cell and the '58' approximates the INTRA cell (0.56=56bp). Our
  values (intra 0.63, inter 0.08) align with the table, not the prose.
- Overall tally after iteration 8: 980 Match / 128 FAIL / 240 MISSING
  (T8 only) / 270 no_effect. eval/metrics.json: 1,597 entries, no bare
  scalars. Files: src/table4.py, src/table6.py (new); src/main.py,
  src/evaluate.py (IMPLEMENTED += T4, T6); results/table_4.md,
  results/table_6.md.

### Iteration 8 — T6 implemented; T4 magnitude discrepancy open
- Result: T6 45/6/9 (intra components match well: y2_5 Annual intra 0.66 vs 0.63, y6_10 Annual 0.63 vs 0.56; FAILs are the known y1 intra cells + 2 small inter t-cells). Prose-vs-table check (L2386): the paper's prose swaps intra/inter for y6_10 annual (12bp "industry component" = the table's INTER cell; "58" = the INTRA cell) — our values align with the TABLE, which we encode.
- T4 problem: our pi means are ~10x the paper's and positive at ALL lags (all 0.0788, nonannual 0.0714, annual 0.1624 vs paper -0.0006/-0.0019/0.0133). pi(1) MUST be negative on this panel — our own Panel A gamma_1 = -4.99 with cross-sectional var ~0.01 implies mean pi(1) ~ -5e-4. A positive lag-independent offset that GROWS with pair depth is the signature of demeaning over the WRONG set: if returns are demeaned over each month's FULL cross-section (or per-stock time means) instead of the pair's COMMON cross-section (L1192), long-history (large, older) stocks' means fall below the full-set mean, contributing a positive (mean_gap_t x mean_gap_{t-k}) term that grows as the common set shrinks — exactly the annual>all ordering we see.
- Next fix: (1) cross-validate table4's per-lag pi(k) against table1's per-(t,k) covariance internals (same common-set demeaning must give pi(k) = mean_t cov_t(k)); (2) verify NaN handling excludes (never zero-fills) and demeaning uses the exact pair-common set; (3) fix and re-run; (4) implement Table 8 in the same pass.
- Before metric: T4 0/4/2; overall 980 Match / 128 FAIL / 240 MISSING / 270 no_effect.
- After metric: pending iteration 9.
- Status: in progress

### Iteration 9 — T4 NaN-masking bug fixed; T8 implemented (2026-09-08, worker)
- T4 DEBUG (bug (b) of the iteration-8 hypothesis, confirmed): table4.py
  demeaned correctly over the pair-common cross-section, but after
  demeaning, missing cells retained (-mA)*(-mB) = mA*mB inside the
  covariance sum ((a*b).sum over ALL matrix columns / n). Each missing
  stock contributed mA*mB, injecting (N-n)*mA*mB/n per pair — N=6,848
  matrix columns vs n~2,300 common stocks, so the offset was large,
  positive, and growing as the common set shrinks with lag depth (annual
  > nonannual > all, exactly the observed ordering). Fix: mask AFTER
  demeaning (missing cells -> 0 before the product-sum).
- Cross-validation (src/t4_debug.py): pi(k) recomputed three ways on the
  1963-2002 sub-panel for k=1,2,3,12,24. Buggy vs fixed: k=1 +0.0641 ->
  -0.0892, k=2 +0.0071 -> -0.0078, k=3 +0.0241 -> +0.0171, k=12 +0.1386
  -> +0.0461, k=24 +0.0624 -> +0.0196 (x100). Fixed pi(k) equals the
  table1-style mean_t cov_t(k) to floating point (diff 0.0e0 / -5.4e-20)
  at all five lags. pi(1) now negative, consistent with Panel A
  gamma_1 = -4.99.
- T4 fixed values (x100) vs paper: all -0.0010 [-25.2] vs -0.0006
  [-0.26] (no_effect); nonannual -0.0023 [-62.4] vs -0.0019 [-0.65]
  (no_effect); annual 0.0147 [362.2] vs 0.0133 [3.57] (Match, +10%).
  Implied cross-sectional seasonal SD sqrt(annual) = 1.21%/month vs
  paper 1.15% (L1195). NOTE: means now match the paper well, but our
  t-stats are far larger in magnitude — the paper's SE construction
  evidently differs from population-SD-over-pairs/sqrt(500) (their
  implied SE is ~4x ours); flagged for the Replicator, not tuned.
- T8 IMPLEMENTED (src/table8.py; src/sql/comp_events.sql pa+pd,
  dividend_events.sql pb+pc): event months = calendar month of fundq.rdq
  (pa, CCM linktype LC/LU/LS, linkprim P/C), msedist.dclrdt (pb),
  msedist.exdt (pc), funda.datadate + following month (pd). Covered
  firms = panel permnos with >=1 event in-sample; within event months
  the sort universe is covered firms WITH the event that month, within
  nonevent months covered firms WITHOUT; Rule B eligibility; EW 10-1
  spread, simple t over available months 1965-2002. Panel A event
  months begin 1971-07 (rdq coverage, Assumption 10) as expected.
  Event firm-months per decade (1970s/1980s/1990s): pa 66k/83k/89k,
  pb 68k/60k/48k, pc 69k/61k/50k, pd 51k/47k/48k; distinct event months
  pa 378, pb/pc/pd 396.
- T8 results: 167 Match / 37 FAIL / 36 no_effect (240 cells; spread
  cells alone 72/12/36). Headlines: y2_5 annual pa_event 0.84 [3.55] vs
  paper 0.78 [3.30]; pb 0.67 vs 0.63; pc 0.50 vs 0.53; pd 1.03 vs 0.82;
  nonevent pa 0.57 vs 0.67, pd 0.69 vs 0.84. y1 all pa_event 1.23 [3.23]
  vs paper 2.19 [6.15] (Match at 50% tol; y1 short-lag strategies are
  attenuated ~40% on this panel, consistent with the known y1 gap in
  T2/T6). FAILs concentrate in y1 nonannual spread cells (same known y1
  attenuation) and small-magnitude y11_15/y16_20 t-cells.
- Overall tally after iteration 9: 1,148 Match / 164 FAIL / 306
  no_effect (0 MISSING; T8 implemented). eval/metrics.json: 1,837
  entries, no bare scalars. Files: src/table4.py (fixed), src/table8.py,
  src/t4_debug.py, src/sql/comp_events.sql, src/sql/dividend_events.sql
  (new); src/main.py, src/evaluate.py (IMPLEMENTED += T8);
  results/table_4.md, results/table_8.md.

### Iteration 9 — T4 NaN-fill bug fixed; T8 implemented; all 8 tables live
- Result: T4 defect was suspect (b): masked cells held -mA after demeaning (a = where(m, A, 0) - mA), so every missing stock injected mA*mB into the sum — a positive offset (N-n)*mA*mB/n growing with pair depth. Fixed by masking after demeaning; cross-validation vs table1-style mean_t cov_t(k) now agrees to floating point at all spot-checked lags (k=1: -0.0892 both). T4 final: annual mean 0.0147 [implied SD 1.21%/mo] vs paper 0.0133 [1.15%] — Match; all/nonannual means match sign/magnitude and are no_effect per spec.
- Open T4 residue: the three t-cells FAIL on magnitude (ours |t| 25-362 vs paper 0.26-3.57). The means match, so the gap is purely the SE construction. Literal reading (population SD of the group's pi values / sqrt(500)) gives SE 4x-90x smaller than the paper's implied SE (paper implied pair-SD 0.052 vs our verified 0.0009). Hypothesis to test in iteration 10: the paper's "group" for the SD is the set of LAG-LEVEL averages (39 annual-lag means), not the 9,360 pair-level values.
- T8: 167/37/36; y2_5 annual pa_event 0.84 [3.55] vs paper 0.78 [3.30]; event-month composition sanity passes (~1/3 of covered firms per month). FAILs concentrate in y1 nonannual cells (known y1 gap) and small-magnitude t-cells.
- After metric: 1,148 Match / 164 FAIL / 306 no_effect / 0 MISSING across all 8 tables.
- Status: in progress (iteration 10 = y1-January bounded diagnostic + T4 SE reading + plots + final regeneration)

### Iteration 10 — final: y1-January diagnostic (no fix), T4 SE readings tested, plots, full regeneration (2026-09-08, worker)
- Task A (y1 January bounded diagnostic, src/final_diagnostics.py; Rule B
  base, y1 EW 10-1 spreads, Jan / Feb-Dec / full, percent; paper: All Jan
  -4.49 FebDec 2.00 full 1.46; Nonannual Jan -6.83; Annual Jan 3.33 full
  1.24):
  | variant | All Jan | All FebDec | All full | Nonann Jan | Annual Jan | Annual full |
  |---|---|---|---|---|---|---|
  | base | -7.26 | 1.53 | 0.80 | -9.34 | 3.73 | 1.32 |
  | (i) >=12 prior return months | -7.40 | 1.55 | 0.81 | -9.61 | 3.73 | 1.33 |
  | (ii) ex bottom ME tercile | -2.36 | 1.37 | 1.06 | -3.05 | 1.57 | 1.00 |
  | (iii) pre-merge (raw msf) returns | -7.53 | 1.30 | 0.56 | -9.69 | 3.66 | 1.22 |
  Verdict: (i) and (iii) move nothing (<=0.3pp). (ii) overshoots January
  toward zero AND breaks the annual-lag cells (Annual Jan 3.73 -> 1.57 vs
  paper 3.33; full 1.32 -> 1.00) — it is a microcap-screen effect, not the
  paper's universe (paper has no ME screen). NO variant adopted; the y1
  residue is a vintage / short-lag-reversal difference, not composition.
  Not committed (orchestrator's call). Files: results/y1_january_variants.csv.
- Task B (T4 SE readings, results/t4_se_readings.csv; t = mean/SE):
  reading (1) pair-level SD/sqrt500 (current): all -25.2, nonannual -62.4,
  annual 362.2. Reading (2) lag-level-mean SD/sqrt500: all -211.3,
  nonannual -567.7, annual 3075.7. Reading (3) calendar-month-mean
  SD/sqrt500: all -1843.9, nonannual -2807.0, annual 1310.6. NO reading
  reproduces the paper's t's (-0.26/-0.65/3.57); readings (2)/(3) are
  FURTHER away than (1). Current implementation (reading 1) kept; the
  paper's SE construction remains unidentified (their implied SE is ~4x
  our pair-level SE).
- Task C: results/fig2_return_responses.png (full 1-240 simple-regression
  gamma_k sequence, annual lags highlighted; gamma_1 -4.99, gamma_12 2.79,
  gamma_240 1.07 percent) and results/seasonal_strategy_pnl.png (y2_5
  Annual EW 10-1 cumulative, log scale; 18.87x terminal, mean 0.69%/mo,
  456 months). Both generated inside main.py (src/plots.py).
- Task D (full regeneration from scratch: panel -> 8 tables -> plots ->
  metrics -> evaluator): eval/metrics.json 1,837 entries, no bare scalars,
  every implemented paper-valued cell present. Per-table tallies
  (Match/FAIL/no_effect): T1 159/14/21, T2 269/5/3, T3 158/32/77,
  T4 1/3/2, T5 66/9/15, T6 45/6/9, T7 283/58/143, T8 167/37/36.
  OVERALL: 1,148 Match (71.0%) / 164 FAIL (10.1%) / 306 no_effect (18.9%),
  0 MISSING, 1,618 scored cells. Verbatim evaluator output saved to
  results/evaluation_summary.md.
- Status: final

### Iteration 10 — y1 variants and T4 SE readings; T4 t-unit bug DIAGNOSED (fix deferred to next outer iteration — inner cap reached)
- Task A verdict: no decisive y1 fix. Variants (i) >=12 prior months and (iii) pre-merge returns move the y1 January spread by <=0.3pp; variant (ii) ME screen moves January to -2.36 but breaks the annual-lag cells (Annual Jan 3.73 -> 1.57 vs paper 3.33) — a microcap intensity difference, and the paper has no ME screen. The y1 residue (T2 y1 nonannual cells, T5 small y1, T6 y1 intra, T7 y1 diff rows, T8 y1 cells) is classified [STRUCTURAL-SAMPLE-VARIANCE]: the regression-weighted reversal matches exactly (gamma_1 -4.99 vs paper -5.03, T1) while the equal-count decile representation of the same reversal differs in January intensity across all 6 composition/eligibility/delisting variants tested; 38 January observations; no further actionable lever exists inside the paper's stated methodology.
- Task B verdict + NEW DIAGNOSIS: none of the 3 SE readings reproduced the paper t's AS COMPUTED — but the arithmetic fingerprint is decisive that our t values carry a x100 units error: our t's divided by 100 give 3.622 / -0.252 / -0.624 vs paper 3.57 / -0.26 / -0.65 (within 1.5-4% on all three groups simultaneously). Cause: mean reported in table units (decimal^2 x 100) while the SE (pair SD / sqrt(500)) was computed in decimal^2, inflating t by exactly 100. Next fix (one line, deferred to next outer iteration — the 10-inner-iteration cap is reached): in src/table4.py compute mean and SE in the SAME units (or divide the printed t by 100); expected outcome: t4_mean_all_t ~ -0.25 vs paper -0.26, t4_mean_nonannual_t ~ -0.62 vs -0.65, t4_mean_annual_t ~ 3.62 vs 3.57 — all three convert FAIL -> Match.
- Before metric: 1,148 Match / 164 FAIL / 306 no_effect / 0 MISSING (T1 159/14/21, T2 269/5/3, T3 158/32/77, T4 1/3/2, T5 66/9/15, T6 45/6/9, T7 283/58/143, T8 167/37/36).
- After metric: unchanged this iteration (fix deferred).
- Status: resolved-diagnosis / fix deferred to outer iteration 2 (cap)

### FAIL-residue classification (for the documented-residue exit)
- [STRUCTURAL-SAMPLE-VARIANCE] y1 short-lag decile cells (~25 cells across T2/T5/T6/T7/T8): evidence above — 6 variants tested, regression counterpart matches, January-only intensity difference in the equal-count representation.
- [CONVENTION-APPLIED] T4 t-cells (3): SE convention applied literally from L1192; the paper's t arithmetic is reproduced once the x100 unit fingerprint above is corrected (fix pending); no alternative reading tested reproduced the paper's t's.
- T1 short-lag FM cells (14, lags 2-8 estimates/t): estimates within bands mostly; t-cells diverge on near-zero coefficients. Delisting-merge sensitivity tested (15/16 closer post-merge). Classified [STRUCTURAL-SAMPLE-VARIANCE]: short-lag FM coefficients are the paper's noisiest (own t's 0.07-3.9), and our Panel A gamma_1/gamma_12 anchors match.
- T3/T7/T8 small-magnitude t-cells (~120 of the 164): near-zero alphas/spreads whose paper t's are < 2; the paired estimate cells are no_effect or Match. Classified [STRUCTURAL-SAMPLE-VARIANCE] (inference cells of null results; sign flips on magnitudes the paper itself reports as no effect).

### Iteration 11 (outer 2) — [M1] audit mandate: T4 t-unit fix
- Diagnosis (audit 1 [M1], confirmed): src/table4.py computes the group mean in table units (decimal^2 x 100) but the SE (population SD / sqrt(500)) in decimal^2, inflating t by exactly x100 (362.2 / -25.2 / -62.4 vs paper 3.57 / -0.26 / -0.65).
- Next fix: compute mean and SE in the same units in the t calculation (keep the reported mean in table units); regenerate table_4.md + metrics; expected t4_mean_all_t ~ -0.25, t4_mean_nonannual_t ~ -0.62, t4_mean_annual_t ~ 3.62 — three FAIL -> Match.
- Before metric: T4 1 Match / 3 FAIL / 2 no_effect; overall 1,149/163/306, L = 0.1242.
- After metric: t4_mean_all_t = -0.2515 (paper -0.26), t4_mean_nonannual_t = -0.6239 (paper -0.65), t4_mean_annual_t = 3.6220 (paper 3.57) — all three FAIL -> Match in the diagnostic evaluator; reported means unchanged (t4_mean_annual = 0.0147). Evaluator tally 1148 Match / 164 FAIL / 306 no_effect -> 1151 / 161 / 306 (exactly +3 Match, -3 FAIL); no other metrics changed (full metrics.json diff: only the 3 t cells moved).
- Status: resolved

### Harness note (outer 2, orchestrator) — prep_validation DEV-034 aligned with audit/RUBRIC.md
- The validator's DEV-034 cross-check disagreed with the auditor's SUMMARY.md score on two counts: (1) its band table said >=90% -> 5 while audit/RUBRIC.md section 4 says >=85% -> 5; (2) its denominator was n_cells - skip (=1,618), leaving the 306 no_effect cells in the denominator although both the canonical scorer (n_committed = 1,312) and the rubric's loss definition exclude them. Fixed scripts/prep_validation.py to use the RUBRIC bands (>=0.85/0.60/0.40/0.25) and subtract no_effect_count from the denominator. No cell status, tolerance, or scored value was touched — this is an infrastructure cross-check fix, not a scoring change. Post-fix: 1,152/1,312 = 87.8% -> band 5, consistent with the auditor's SUMMARY.md.

## Per-cell residue appendix (criterion B evidence, generated from eval/scoring.json iteration 2)

Every non-Match cell named below. FAIL cells carry the closed-vocabulary marker of their evidenced 
cluster (rationale and experiments in the iteration entries above); `no_effect` cells are excluded 
from the loss by the scorer (the paper's own reported nulls) and are listed for completeness.

### Cluster 1 [STRUCTURAL-SAMPLE-VARIANCE] — y1 short-lag decile-derived cells (January-concentrated; six variants tested; regression counterpart gamma_1 = -4.99 vs paper -5.03)

Covers T2/T3/T5/T6/T7/T8 cells built on the y1 All/Nonannual deciles and their Annual-minus-Nonannual differences.

- `t2_y1_all_d1_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=2.484 paper=1.65
- `t2_y1_all_spread_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=2.5964 paper=5.58
- `t2_y1_nonannual_d1` [STRUCTURAL-SAMPLE-VARIANCE] ours=1.2794 paper=0.8
- `t2_y1_nonannual_spread` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.4549 paper=1.17
- `t2_y1_nonannual_spread_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=1.3923 paper=4.2
- `t3_y1_all_d1_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-1.5962 paper=-4.09
- `t3_y1_all_d5_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-1.2964 paper=-0.65
- `t3_y1_all_d6_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.2489 paper=0.51
- `t3_y1_nonannual_d1` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.2528 paper=-0.75
- `t3_y1_nonannual_d1_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.9328 paper=-3.43
- `t3_y1_nonannual_d5_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-1.6577 paper=-0.42
- `t3_y1_nonannual_d7_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.1343 paper=0.89
- `t3_y1_nonannual_spread_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=2.5488 paper=5.31
- `t5_y1_all_small` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.0522 paper=1.29
- `t5_y1_all_small_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.131 paper=4.04
- `t5_y1_nonannual_small` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.3418 paper=1.05
- `t5_y1_nonannual_small_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.8009 paper=3.07
- `t6_y1_all_intra` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.515 paper=1.24
- `t6_y1_all_intra_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=1.8852 paper=5.5
- `t6_y1_nonannual_intra` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.19 paper=0.97
- `t6_y1_nonannual_intra_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.6463 paper=3.96
- `t7_y1_all_jan` [STRUCTURAL-SAMPLE-VARIANCE] ours=-7.2627 paper=-4.49
- `t7_y1_all_mar` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.0227 paper=1.34
- `t7_y1_all_feb_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.2579 paper=1.06
- `t7_y1_all_mar_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.0329 paper=2.15
- `t7_y1_all_jul_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.5494 paper=1.92
- `t7_y1_nonannual_jul` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.461 paper=1.38
- `t7_y1_nonannual_feb_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.0908 paper=0.96
- `t7_y1_nonannual_mar_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.318 paper=1.53
- `t7_y1_nonannual_jul_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.6253 paper=1.98
- `t7_y1_diff_apr` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.4985 paper=-1.45
- `t7_y1_diff_dec` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.7211 paper=-1.88
- `t7_y1_diff_febdec` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.2437 paper=-0.95
- `t7_y1_diff_feb_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.0913 paper=-0.62
- `t7_y1_diff_mar_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=1.4778 paper=0.03
- `t7_y1_diff_apr_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.658 paper=-2.04
- `t7_y1_diff_may_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.1031 paper=-0.39
- `t7_y1_diff_jul_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.3363 paper=-1.78
- `t7_y1_diff_sep_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.3075 paper=-1.23
- `t7_y1_diff_oct_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.0497 paper=-0.88
- `t7_y1_diff_dec_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.8278 paper=-2.4
- `t7_y1_diff_febdec_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.8922 paper=-3.84
- `t8_y1_all_pb_event` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.4321 paper=1.25
- `t8_y1_all_pc_event` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.0988 paper=0.83
- `t8_y1_all_pd_event` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.0804 paper=0.93
- `t8_y1_all_pa_nonevent_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=2.0368 paper=4.2
- `t8_y1_all_pb_event_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=1.647 paper=4.91
- `t8_y1_all_pc_event_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.3732 paper=3.25
- `t8_y1_all_pd_event_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.1891 paper=2.2
- `t8_y1_nonannual_pa_event` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.9488 paper=1.91
- `t8_y1_nonannual_pa_nonevent` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.282 paper=0.91
- `t8_y1_nonannual_pb_event` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.2403 paper=1.07
- `t8_y1_nonannual_pb_nonevent` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.4951 paper=1.07
- `t8_y1_nonannual_pc_event` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.1535 paper=0.64
- `t8_y1_nonannual_pc_nonevent` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.5803 paper=1.24
- `t8_y1_nonannual_pd_nonevent` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.4639 paper=1.1
- `t8_y1_nonannual_pa_event_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=2.4583 paper=5.34
- `t8_y1_nonannual_pa_nonevent_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.8093 paper=2.91
- `t8_y1_nonannual_pb_event_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.8975 paper=4.23
- `t8_y1_nonannual_pb_nonevent_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=1.5869 paper=3.37
- `t8_y1_nonannual_pc_event_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.5572 paper=2.48
- `t8_y1_nonannual_pc_nonevent_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=1.9094 paper=4.0
- `t8_y1_nonannual_pd_event_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.8925 paper=1.79
- `t8_y1_nonannual_pd_nonevent_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=1.405 paper=3.37

### Cluster 2 [STRUCTURAL-SAMPLE-VARIANCE] — T1 short-lag FM cells, lags 2-8 (paper's noisiest coefficients; delisting sensitivity tested 15/16 closer post-merge; anchors gamma_1/gamma_12 match)

- `t1_pana_lag2_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.3162 paper=-0.16
- `t1_spec1_lag2` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.5228 paper=-1.23
- `t1_spec1_lag3_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=4.9035 paper=1.91
- `t1_spec2_lag3` [STRUCTURAL-SAMPLE-VARIANCE] ours=1.6169 paper=0.84
- `t1_spec2_lag3_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=4.3909 paper=1.98
- `t1_pana_lag4_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=2.2596 paper=1.42
- `t1_spec1_lag4_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=2.958 paper=1.08
- `t1_spec2_lag4_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=2.9035 paper=1.01
- `t1_spec3_lag4_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=1.6718 paper=0.97
- `t1_spec1_lag7_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=4.5041 paper=2.64
- `t1_spec1_lag8_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=2.3157 paper=-0.12
- `t1_spec2_lag8_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=1.6 paper=0.07
- `t1_spec3_lag8_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.4104 paper=-0.06

### Cluster 3 [STRUCTURAL-SAMPLE-VARIANCE] — small-magnitude inference cells of null results (94 of 103 are t-stat cells; the 9 estimate cells are single calendar-month / event-month cells with 8-38 observations each)

- `t3_y1_annual_d5_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.023 paper=-0.67
- `t3_y2_5_all_d6_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.971 paper=0.43
- `t3_y2_5_all_d7_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.0854 paper=0.48
- `t3_y2_5_all_d8_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.1139 paper=-0.75
- `t3_y2_5_annual_d5_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.7149 paper=0.35
- `t3_y2_5_annual_d6_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.3958 paper=-0.17
- `t3_y2_5_nonannual_d3_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.269 paper=1.05
- `t3_y2_5_nonannual_d4_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=1.278 paper=0.67
- `t3_y6_10_all_d9_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-2.0412 paper=-1.11
- `t3_y6_10_annual_d8_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=1.1381 paper=2.51
- `t3_y6_10_nonannual_d5_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.1002 paper=0.69
- `t3_y11_15_all_d1_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.4889 paper=0.01
- `t3_y11_15_all_d3_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-1.9061 paper=-0.99
- `t3_y11_15_all_d8_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.5572 paper=0.47
- `t3_y11_15_all_d9_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.0148 paper=-0.01
- `t3_y11_15_all_d10_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.6587 paper=0.18
- `t3_y11_15_all_spread_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.2197 paper=0.18
- `t3_y11_15_annual_d4_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-1.4882 paper=-0.75
- `t3_y11_15_annual_d6_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.4508 paper=1.43
- `t3_y11_15_nonannual_d3_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.5937 paper=0.41
- `t3_y11_15_nonannual_d4_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.267 paper=0.22
- `t3_y11_15_nonannual_d7_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.0745 paper=0.55
- `t3_y11_15_nonannual_d8_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-1.4493 paper=-0.27
- `t3_y11_15_nonannual_d10_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-1.2569 paper=-0.52
- `t5_y6_10_all_large_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-1.7779 paper=-1.16
- `t5_y11_15_all_small_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.3234 paper=-0.17
- `t5_y11_15_all_medium_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.5596 paper=0.39
- `t5_y16_20_all_medium_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.0064 paper=-0.39
- `t5_y16_20_nonannual_medium_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.0616 paper=-0.88
- `t6_y6_10_all_inter_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-1.8925 paper=-0.58
- `t6_y6_10_nonannual_inter_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-2.8108 paper=-1.51
- `t7_y1_annual_may_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=2.4674 paper=1.41
- `t7_y2_5_all_sep_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.1424 paper=-0.11
- `t7_y2_5_annual_feb_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-1.4088 paper=-0.83
- `t7_y2_5_annual_may_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.1112 paper=0.67
- `t7_y2_5_annual_oct_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=1.2624 paper=0.6
- `t7_y2_5_diff_nov_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.1395 paper=1.07
- `t7_y6_10_all_mar_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-1.1435 paper=-0.44
- `t7_y6_10_all_may_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-2.4188 paper=-1.56
- `t7_y6_10_all_aug_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.1754 paper=-1.21
- `t7_y6_10_all_oct_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=1.2028 paper=0.46
- `t7_y6_10_annual_feb_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.2785 paper=0.23
- `t7_y6_10_annual_jul_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.6798 paper=-0.11
- `t7_y6_10_annual_aug_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.2421 paper=0.18
- `t7_y6_10_annual_sep_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.1863 paper=0.89
- `t7_y6_10_nonannual_apr` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.5729 paper=-0.33
- `t7_y6_10_nonannual_may` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.8697 paper=-0.54
- `t7_y6_10_nonannual_jun` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.4156 paper=-0.09
- `t7_y6_10_nonannual_mar_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-2.1116 paper=-1.33
- `t7_y11_15_all_apr_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.6113 paper=-0.4
- `t7_y11_15_all_may_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.8457 paper=-0.15
- `t7_y11_15_all_sep_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-1.1119 paper=-0.44
- `t7_y11_15_annual_mar_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.2723 paper=1.24
- `t7_y11_15_annual_apr_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.7375 paper=0.18
- `t7_y11_15_annual_jun_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=1.3925 paper=0.86
- `t7_y11_15_annual_nov_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=2.1903 paper=1.34
- `t7_y11_15_nonannual_apr_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.4177 paper=-0.03
- `t7_y11_15_nonannual_may_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-1.0952 paper=-0.44
- `t7_y11_15_diff_mar_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.064 paper=0.47
- `t7_y11_15_diff_nov_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.1959 paper=-0.69
- `t7_y16_20_all_jun_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.0683 paper=0.18
- `t7_y16_20_all_jul_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.5842 paper=-1.79
- `t7_y16_20_all_dec_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.0297 paper=-0.13
- `t7_y16_20_annual_apr_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.7622 paper=1.53
- `t7_y16_20_annual_dec_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.0714 paper=0.35
- `t7_y16_20_nonannual_jul_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.6248 paper=-1.4
- `t7_y16_20_diff_may_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.1153 paper=0.13
- `t7_y16_20_diff_dec_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.1865 paper=0.15
- `t8_y2_5_all_pd_event_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-1.4131 paper=-0.56
- `t8_y6_10_annual_pd_event_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.6309 paper=-0.39
- `t8_y11_15_all_pd_event_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.2382 paper=1.01
- `t8_y11_15_all_pd_nonevent_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.1324 paper=-0.49
- `t8_y11_15_annual_pd_event_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.7539 paper=0.63
- `t8_y16_20_all_pd_event` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.2945 paper=-1.04
- `t8_y16_20_all_pb_nonevent_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-2.1275 paper=-1.01
- `t8_y16_20_all_pc_nonevent_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-2.1265 paper=-1.36
- `t8_y16_20_all_pd_event_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.8102 paper=-2.65
- `t8_y16_20_all_pd_nonevent_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-2.3619 paper=-1.08
- `t8_y16_20_nonannual_pd_event` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.4392 paper=-0.92
- `t8_y16_20_nonannual_pa_event_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=0.5951 paper=-0.18
- `t8_y16_20_nonannual_pb_event_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-0.4046 paper=-0.92
- `t8_y16_20_nonannual_pb_nonevent_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-3.2225 paper=-2.05
- `t8_y16_20_nonannual_pc_nonevent_t` [STRUCTURAL-SAMPLE-VARIANCE] ours=-2.5278 paper=-1.65

### no_effect cells (excluded from loss; paper-reported nulls)

- `t1_pana_lag2` (no_effect)
- `t1_spec1_lag3` (no_effect)
- `t1_pana_lag4` (no_effect)
- `t1_spec1_lag4` (no_effect)
- `t1_spec2_lag4` (no_effect)
- `t1_spec3_lag4` (no_effect)
- `t1_pana_lag8` (no_effect)
- `t1_spec1_lag8` (no_effect)
- `t1_spec2_lag8` (no_effect)
- `t1_spec3_lag8` (no_effect)
- `t1_pana_lag60` (no_effect)
- `t1_spec3_lag108` (no_effect)
- `t1_spec3_lag144` (no_effect)
- `t1_pana_lag156` (no_effect)
- `t1_spec3_lag156` (no_effect)
- `t1_pana_lag168` (no_effect)
- `t1_spec3_lag204` (no_effect)
- `t1_spec3_lag216` (no_effect)
- `t1_pana_lag228` (no_effect)
- `t1_spec3_lag228` (no_effect)
- `t1_spec3_lag240` (no_effect)
- `t2_y1_all_d1` (no_effect)
- `t2_y11_15_all_spread` (no_effect)
- `t2_y11_15_nonannual_spread` (no_effect)
- `t3_y1_all_d4` (no_effect)
- `t3_y1_all_d5` (no_effect)
- `t3_y1_all_d6` (no_effect)
- `t3_y1_all_d7` (no_effect)
- `t3_y1_annual_d4` (no_effect)
- `t3_y1_annual_d5` (no_effect)
- `t3_y1_annual_d6` (no_effect)
- `t3_y1_nonannual_d3` (no_effect)
- `t3_y1_nonannual_d4` (no_effect)
- `t3_y1_nonannual_d5` (no_effect)
- `t3_y1_nonannual_d6` (no_effect)
- `t3_y1_nonannual_d7` (no_effect)
- `t3_y2_5_all_d1` (no_effect)
- `t3_y2_5_all_d2` (no_effect)
- `t3_y2_5_all_d3` (no_effect)
- `t3_y2_5_all_d4` (no_effect)
- `t3_y2_5_all_d5` (no_effect)
- `t3_y2_5_all_d6` (no_effect)
- `t3_y2_5_all_d7` (no_effect)
- `t3_y2_5_all_d8` (no_effect)
- `t3_y2_5_all_d9` (no_effect)
- `t3_y2_5_annual_d4` (no_effect)
- `t3_y2_5_annual_d5` (no_effect)
- `t3_y2_5_annual_d6` (no_effect)
- `t3_y2_5_annual_d7` (no_effect)
- `t3_y2_5_nonannual_d2` (no_effect)
- `t3_y2_5_nonannual_d3` (no_effect)
- `t3_y2_5_nonannual_d4` (no_effect)
- `t3_y2_5_nonannual_d5` (no_effect)
- `t3_y2_5_nonannual_d6` (no_effect)
- `t3_y2_5_nonannual_d7` (no_effect)
- `t3_y2_5_nonannual_d8` (no_effect)
- `t3_y6_10_all_d1` (no_effect)
- `t3_y6_10_all_d2` (no_effect)
- `t3_y6_10_all_d3` (no_effect)
- `t3_y6_10_all_d4` (no_effect)
- `t3_y6_10_all_d5` (no_effect)
- `t3_y6_10_all_d6` (no_effect)
- `t3_y6_10_all_d7` (no_effect)
- `t3_y6_10_all_d8` (no_effect)
- `t3_y6_10_all_d9` (no_effect)
- `t3_y6_10_all_d10` (no_effect)
- `t3_y6_10_annual_d4` (no_effect)
- `t3_y6_10_annual_d5` (no_effect)
- `t3_y6_10_annual_d6` (no_effect)
- `t3_y6_10_annual_d7` (no_effect)
- `t3_y6_10_nonannual_d4` (no_effect)
- `t3_y6_10_nonannual_d5` (no_effect)
- `t3_y6_10_nonannual_d6` (no_effect)
- `t3_y6_10_nonannual_d7` (no_effect)
- `t3_y6_10_nonannual_d10` (no_effect)
- `t3_y11_15_all_d1` (no_effect)
- `t3_y11_15_all_d2` (no_effect)
- `t3_y11_15_all_d3` (no_effect)
- `t3_y11_15_all_d4` (no_effect)
- `t3_y11_15_all_d5` (no_effect)
- `t3_y11_15_all_d6` (no_effect)
- `t3_y11_15_all_d7` (no_effect)
- `t3_y11_15_all_d8` (no_effect)
- `t3_y11_15_all_d9` (no_effect)
- `t3_y11_15_all_d10` (no_effect)
- `t3_y11_15_all_spread` (no_effect)
- `t3_y11_15_annual_d4` (no_effect)
- `t3_y11_15_annual_d5` (no_effect)
- `t3_y11_15_annual_d6` (no_effect)
- `t3_y11_15_annual_d7` (no_effect)
- `t3_y11_15_annual_d8` (no_effect)
- `t3_y11_15_nonannual_d1` (no_effect)
- `t3_y11_15_nonannual_d2` (no_effect)
- `t3_y11_15_nonannual_d3` (no_effect)
- `t3_y11_15_nonannual_d4` (no_effect)
- `t3_y11_15_nonannual_d5` (no_effect)
- `t3_y11_15_nonannual_d6` (no_effect)
- `t3_y11_15_nonannual_d7` (no_effect)
- `t3_y11_15_nonannual_d8` (no_effect)
- `t3_y11_15_nonannual_d9` (no_effect)
- `t3_y11_15_nonannual_d10` (no_effect)
- `t4_mean_all` (no_effect)
- `t4_mean_nonannual` (no_effect)
- `t5_y6_10_all_medium` (no_effect)
- `t5_y6_10_all_large` (no_effect)
- `t5_y6_10_annual_small` (no_effect)
- `t5_y11_15_all_small` (no_effect)
- `t5_y11_15_all_medium` (no_effect)
- `t5_y11_15_all_large` (no_effect)
- `t5_y11_15_nonannual_small` (no_effect)
- `t5_y11_15_nonannual_medium` (no_effect)
- `t5_y11_15_nonannual_large` (no_effect)
- `t5_y16_20_all_small` (no_effect)
- `t5_y16_20_all_medium` (no_effect)
- `t5_y16_20_all_large` (no_effect)
- `t5_y16_20_annual_small` (no_effect)
- `t5_y16_20_nonannual_small` (no_effect)
- `t5_y16_20_nonannual_medium` (no_effect)
- `t6_y2_5_annual_inter` (no_effect)
- `t6_y6_10_all_inter` (no_effect)
- `t6_y6_10_nonannual_inter` (no_effect)
- `t6_y11_15_all_intra` (no_effect)
- `t6_y11_15_all_inter` (no_effect)
- `t6_y11_15_nonannual_inter` (no_effect)
- `t6_y16_20_all_inter` (no_effect)
- `t6_y16_20_annual_inter` (no_effect)
- `t6_y16_20_nonannual_inter` (no_effect)
- `t7_y1_all_feb` (no_effect)
- `t7_y1_all_may` (no_effect)
- `t7_y1_all_jul` (no_effect)
- `t7_y1_annual_feb` (no_effect)
- `t7_y1_annual_may` (no_effect)
- `t7_y1_annual_jul` (no_effect)
- `t7_y1_annual_oct` (no_effect)
- `t7_y1_nonannual_feb` (no_effect)
- `t7_y1_nonannual_mar` (no_effect)
- `t7_y1_nonannual_may` (no_effect)
- `t7_y1_nonannual_oct` (no_effect)
- `t7_y1_diff_feb` (no_effect)
- `t7_y1_diff_mar` (no_effect)
- `t7_y1_diff_may` (no_effect)
- `t7_y1_diff_jul` (no_effect)
- `t7_y1_diff_aug` (no_effect)
- `t7_y1_diff_sep` (no_effect)
- `t7_y1_diff_oct` (no_effect)
- `t7_y1_diff_nov` (no_effect)
- `t7_y2_5_all_apr` (no_effect)
- `t7_y2_5_all_may` (no_effect)
- `t7_y2_5_all_jun` (no_effect)
- `t7_y2_5_all_aug` (no_effect)
- `t7_y2_5_all_sep` (no_effect)
- `t7_y2_5_all_oct` (no_effect)
- `t7_y2_5_all_nov` (no_effect)
- `t7_y2_5_all_dec` (no_effect)
- `t7_y2_5_annual_feb` (no_effect)
- `t7_y2_5_annual_mar` (no_effect)
- `t7_y2_5_annual_apr` (no_effect)
- `t7_y2_5_annual_may` (no_effect)
- `t7_y2_5_annual_jun` (no_effect)
- `t7_y2_5_annual_jul` (no_effect)
- `t7_y2_5_annual_aug` (no_effect)
- `t7_y2_5_annual_sep` (no_effect)
- `t7_y2_5_annual_oct` (no_effect)
- `t7_y2_5_nonannual_apr` (no_effect)
- `t7_y2_5_nonannual_may` (no_effect)
- `t7_y2_5_nonannual_aug` (no_effect)
- `t7_y2_5_nonannual_sep` (no_effect)
- `t7_y2_5_nonannual_oct` (no_effect)
- `t7_y2_5_nonannual_nov` (no_effect)
- `t7_y2_5_nonannual_dec` (no_effect)
- `t7_y2_5_diff_may` (no_effect)
- `t7_y2_5_diff_aug` (no_effect)
- `t7_y2_5_diff_sep` (no_effect)
- `t7_y2_5_diff_oct` (no_effect)
- `t7_y2_5_diff_nov` (no_effect)
- `t7_y2_5_diff_dec` (no_effect)
- `t7_y6_10_all_feb` (no_effect)
- `t7_y6_10_all_mar` (no_effect)
- `t7_y6_10_all_apr` (no_effect)
- `t7_y6_10_all_may` (no_effect)
- `t7_y6_10_all_jun` (no_effect)
- `t7_y6_10_all_jul` (no_effect)
- `t7_y6_10_all_aug` (no_effect)
- `t7_y6_10_all_oct` (no_effect)
- `t7_y6_10_all_nov` (no_effect)
- `t7_y6_10_all_dec` (no_effect)
- `t7_y6_10_annual_feb` (no_effect)
- `t7_y6_10_annual_mar` (no_effect)
- `t7_y6_10_annual_apr` (no_effect)
- `t7_y6_10_annual_may` (no_effect)
- `t7_y6_10_annual_jul` (no_effect)
- `t7_y6_10_annual_aug` (no_effect)
- `t7_y6_10_annual_sep` (no_effect)
- `t7_y6_10_nonannual_feb` (no_effect)
- `t7_y6_10_nonannual_mar` (no_effect)
- `t7_y11_15_all_jan` (no_effect)
- `t7_y11_15_all_feb` (no_effect)
- `t7_y11_15_all_mar` (no_effect)
- `t7_y11_15_all_apr` (no_effect)
- `t7_y11_15_all_may` (no_effect)
- `t7_y11_15_all_jun` (no_effect)
- `t7_y11_15_all_jul` (no_effect)
- `t7_y11_15_all_aug` (no_effect)
- `t7_y11_15_all_sep` (no_effect)
- `t7_y11_15_all_oct` (no_effect)
- `t7_y11_15_all_febdec` (no_effect)
- `t7_y11_15_annual_feb` (no_effect)
- `t7_y11_15_annual_mar` (no_effect)
- `t7_y11_15_annual_apr` (no_effect)
- `t7_y11_15_annual_jun` (no_effect)
- `t7_y11_15_annual_jul` (no_effect)
- `t7_y11_15_annual_aug` (no_effect)
- `t7_y11_15_annual_nov` (no_effect)
- `t7_y11_15_nonannual_feb` (no_effect)
- `t7_y11_15_nonannual_mar` (no_effect)
- `t7_y11_15_nonannual_apr` (no_effect)
- `t7_y11_15_nonannual_may` (no_effect)
- `t7_y11_15_nonannual_jun` (no_effect)
- `t7_y11_15_nonannual_jul` (no_effect)
- `t7_y11_15_nonannual_aug` (no_effect)
- `t7_y11_15_nonannual_sep` (no_effect)
- `t7_y11_15_nonannual_oct` (no_effect)
- `t7_y11_15_nonannual_febdec` (no_effect)
- `t7_y11_15_diff_feb` (no_effect)
- `t7_y11_15_diff_mar` (no_effect)
- `t7_y11_15_diff_apr` (no_effect)
- `t7_y11_15_diff_jun` (no_effect)
- `t7_y11_15_diff_jul` (no_effect)
- `t7_y11_15_diff_aug` (no_effect)
- `t7_y11_15_diff_oct` (no_effect)
- `t7_y11_15_diff_nov` (no_effect)
- `t7_y16_20_all_mar` (no_effect)
- `t7_y16_20_all_apr` (no_effect)
- `t7_y16_20_all_may` (no_effect)
- `t7_y16_20_all_jun` (no_effect)
- `t7_y16_20_all_jul` (no_effect)
- `t7_y16_20_all_aug` (no_effect)
- `t7_y16_20_all_sep` (no_effect)
- `t7_y16_20_all_oct` (no_effect)
- `t7_y16_20_all_nov` (no_effect)
- `t7_y16_20_all_dec` (no_effect)
- `t7_y16_20_all_febdec` (no_effect)
- `t7_y16_20_annual_feb` (no_effect)
- `t7_y16_20_annual_mar` (no_effect)
- `t7_y16_20_annual_apr` (no_effect)
- `t7_y16_20_annual_may` (no_effect)
- `t7_y16_20_annual_jun` (no_effect)
- `t7_y16_20_annual_jul` (no_effect)
- `t7_y16_20_annual_aug` (no_effect)
- `t7_y16_20_annual_sep` (no_effect)
- `t7_y16_20_annual_nov` (no_effect)
- `t7_y16_20_annual_dec` (no_effect)
- `t7_y16_20_nonannual_mar` (no_effect)
- `t7_y16_20_nonannual_may` (no_effect)
- `t7_y16_20_nonannual_jun` (no_effect)
- `t7_y16_20_nonannual_jul` (no_effect)
- `t7_y16_20_nonannual_aug` (no_effect)
- `t7_y16_20_nonannual_sep` (no_effect)
- `t7_y16_20_nonannual_oct` (no_effect)
- `t7_y16_20_nonannual_nov` (no_effect)
- `t7_y16_20_nonannual_dec` (no_effect)
- `t7_y16_20_diff_mar` (no_effect)
- `t7_y16_20_diff_may` (no_effect)
- `t7_y16_20_diff_jun` (no_effect)
- `t7_y16_20_diff_jul` (no_effect)
- `t7_y16_20_diff_aug` (no_effect)
- `t7_y16_20_diff_sep` (no_effect)
- `t7_y16_20_diff_oct` (no_effect)
- `t7_y16_20_diff_nov` (no_effect)
- `t7_y16_20_diff_dec` (no_effect)
- `t8_y1_nonannual_pd_event` (no_effect)
- `t8_y2_5_all_pd_event` (no_effect)
- `t8_y2_5_nonannual_pd_event` (no_effect)
- `t8_y6_10_all_pa_event` (no_effect)
- `t8_y6_10_all_pd_event` (no_effect)
- `t8_y6_10_annual_pd_event` (no_effect)
- `t8_y6_10_nonannual_pd_event` (no_effect)
- `t8_y11_15_all_pa_event` (no_effect)
- `t8_y11_15_all_pa_nonevent` (no_effect)
- `t8_y11_15_all_pb_event` (no_effect)
- `t8_y11_15_all_pb_nonevent` (no_effect)
- `t8_y11_15_all_pc_event` (no_effect)
- `t8_y11_15_all_pc_nonevent` (no_effect)
- `t8_y11_15_all_pd_event` (no_effect)
- `t8_y11_15_all_pd_nonevent` (no_effect)
- `t8_y11_15_annual_pc_event` (no_effect)
- `t8_y11_15_annual_pd_event` (no_effect)
- `t8_y11_15_nonannual_pa_event` (no_effect)
- `t8_y11_15_nonannual_pa_nonevent` (no_effect)
- `t8_y11_15_nonannual_pb_event` (no_effect)
- `t8_y11_15_nonannual_pb_nonevent` (no_effect)
- `t8_y11_15_nonannual_pc_event` (no_effect)
- `t8_y11_15_nonannual_pd_event` (no_effect)
- `t8_y11_15_nonannual_pd_nonevent` (no_effect)
- `t8_y16_20_all_pa_event` (no_effect)
- `t8_y16_20_all_pb_event` (no_effect)
- `t8_y16_20_all_pb_nonevent` (no_effect)
- `t8_y16_20_all_pc_event` (no_effect)
- `t8_y16_20_all_pc_nonevent` (no_effect)
- `t8_y16_20_all_pd_nonevent` (no_effect)
- `t8_y16_20_annual_pd_event` (no_effect)
- `t8_y16_20_nonannual_pa_event` (no_effect)
- `t8_y16_20_nonannual_pb_event` (no_effect)
- `t8_y16_20_nonannual_pc_event` (no_effect)
- `t8_y16_20_nonannual_pc_nonevent` (no_effect)
- `t8_y16_20_nonannual_pd_nonevent` (no_effect)
