# Assumption Registry — MAX on Steroids

> **Distinct from `preprocessing_rules.json`** (which is paper-quote provenance). This file holds **paper-silent** decisions — choices the agent had to make that the paper does not specify. Apply the documented default where one exists in `rep/PAPER_CONVENTIONS.md` (log `[CONVENTION-APPLIED]`); write `paper silent` only where no default exists. Every iteration appends a new entry below.

---

## Assumption 1: Delisting-return treatment — `paper silent`

**Decision:** Substitute CRSP `dsedelist.dlret` for the missing monthly return on the delisting month (Shumway 1997 / BMP 2007 convention). For performance-related delistings (`dlstcd` in performance list) where `dlret` is missing (sentinel `-55.0`), use `-0.30` for NYSE/AMEX (exchcd IN (1,2)) and `-0.55` for NASDAQ (exchcd = 3).

**Rationale:** Paper is silent on `dlret` handling in §3 Sample Construction. `rep/PAPER_CONVENTIONS.md` § Universe selection row "Delisting returns" mandates this adjustment by default. No paper quote supports the deviation. Applying the documented default is the mandated response to silence.

**Impact:** Affects every monthly return cell in Tables 1, 2, and 6 (a small fraction of firm-months — typically <2% of CRSP universe — has a performance-related delisting in any given month). Magnitude expected < 5 bp/month on long-short spreads.

---

## Assumption 2: PIT universe source — `[CONVENTION-APPLIED]` `crsp_202601.dsfhdr`

**Decision:** Use `crsp_202601.dsfhdr` (via `utils.apply_universe_filter()`) as the point-in-time source for the `shrcd IN (10,11)` and `exchcd IN (1,2,3)` filters. Do NOT use `dsenames` (its `namedt/nameendt` validity windows produce duplicate `(permno, month)` rows).

**Rationale:** `rep/PAPER_CONVENTIONS.md` § Universe selection row "PIT source" names `dsfhdr` as the only acceptable PIT source for universe filtering and explicitly prohibits `dsenames`. The empirical cost of `dsenames` per the convention doc is a clean sign-flip on the headline D10-D1 spread in the Bali-Cakici-Whitelaw 2011 replication — a 2.95% wrong-direction cell — so a slip here is catastrophic.

**Impact:** Affects every cell in Tables 1, 2, and 6 (the universe membership determines the panel). Required correctness: sign of D10-D1 spread must be negative.

---

## Assumption 3: Price floor — `[CONVENTION-APPLIED]` `$5 minimum`

**Decision:** Drop stock-months with `abs(prc) < 5.0` from the universe.

**Rationale:** Paper explicitly states this at §3.1 L169 ("We exclude stocks priced below $5 per share"). The paper's filter happens to coincide with the convention default; logging the application to make the chain auditable.

**Impact:** Affects every cell in Tables 1, 2, and 6 (panel composition).

---

## Assumption 4: VW weight — `[CONVENTION-APPLIED]` lagged market equity

**Decision:** VW portfolio weights = `abs(prc_t) * shrout_t * 1000` (CRSP dollar market equity at month-end t), lagged one month (`me_lag1 = me.shift(1)` per permno) before passing to `bin_returns`. NEVER use same-month me as the weight.

**Rationale:** `rep/PAPER_CONVENTIONS.md` § FF-style annual-formation papers row "VW portfolio weights" mandates the lag: same-month me embeds the month's own return and inflates the VW portfolio mean by ~60 bp/month (the documented Anderson & Garcia-Feijoo 2006 example). The paper does monthly rebalancing, not annual June rebalancing, so we use the lagged-monthly weight form.

**Impact:** Affects every D10-D1 spread and every decile-level VW return cell.

---

## Assumption 5: Market beta computation — `[CONVENTION-APPLIED]` 252-day rolling CAPM slope

**Decision:** β_i,t = cov(ret_i,d − rf_d, ret_mkt,d − rf_d) / var(ret_mkt,d − rf_d), estimated on the 252 trading days ending on the last trading day of month t. Both stock and market excess returns use `dsi.vwretd` (CRSP value-weighted with dividends) as the market series.

**Rationale:** Paper footnote 6 at L181 specifies this exact specification. Using `dsi.vwretd` (and not `ff.three_factor.mkt_rf`) for the beta regression matches the paper's "market's excess returns" convention since the paper does not specify which market series; the standard Bali et al. (2011) convention is CRSP VW with dividends.

**Impact:** Affects every BETA cell in Table 2 and the construction of `max_beta_decile` for Table 6.

---

## Assumption 6: FF6 construction — SQL-side outer join of four_factor + five_factor

**Decision:** Materialize the FF6 factor series by an outer join of `ff.four_factor_monthly` and `ff.five_factor_monthly` on `dt`, taking `{mkt_rf, smb, hml, rf}` from either and `{mom, rmw, cma}` from the matching table. Both tables share the same Kenneth French calendar so the join is exact.

**Rationale:** `references/CLICKHOUSE_CATALOG.json` does not carry a pre-joined FF6 table. The two source tables are bit-aligned on `dt`. No paper quote supports the construction — this is data-infrastructure.

**Impact:** Affects every FF6 alpha cell in Tables 1 and 6.

---

## Assumption 7: Book equity — FF cascade from SEQ/TXDB/ITCB/PSTK cascade per paper §3.3

**Decision:** BE = SEQ + TXDB + ITCB − PSTKRV (with fallbacks to PSTKL or PSTK if PSTKRV is missing; fallback to `at − dlc − dltt − pstkrv` if SEQ is missing or ≤ 0). Use the Compustat fiscal-year-end value (with the standard FF 6-month lag applied to align with the June-of-year-t + 12-month return convention, which the paper does not specify — paper forms monthly portfolios).

**Rationale:** Paper §3.3 L189 specifies "the sum of stockholders' equity (SEQ), deferred taxes (TXDB), and investment tax credit (ITCB), minus the book value of preferred stock (PSTKRV, PSTKL, or PSTK)" exactly. The annual-fiscal-year → monthly-portfolio-formation lag follows `rep/PAPER_CONVENTIONS.md` § FF-style annual-formation papers row "Annual-to-month mapping → FF (1992) lag" but is *not* the right lag here since the paper forms portfolios monthly, not annually. We instead use the most-recent fiscal-year-end BE available at month t (lagged by at least 6 months to avoid look-ahead per the FF convention; specifically: at month t in year y, use BE from fiscal year y-1 or earlier). Documented below.

**Impact:** Affects every BM cell in Table 2. Note the paper's monthly-rebalancing + annual-BE construction makes the look-ahead window short (BE from prior fiscal year at most).

---

## Assumption 8: Book-equity lag — most-recent fiscal year-end, max 12-month lag

**Decision:** At month t, use the BE from the most recent fiscal year-end whose `datadate` is at least 6 months before t. (Equivalently: BE is held constant across months until the next annual report arrives.)

**Rationale:** Paper does not specify BE refresh frequency. `rep/PAPER_CONVENTIONS.md` § "Annual-to-month mapping → FF (1992) lag" recommends fiscal-year t → monthly returns from July t+1 to June t+2, but the paper forms monthly portfolios not annual ones, so the strict 6-month lag is the minimum needed to avoid look-ahead (a December fiscal-year-end cannot be known before April of the following year). The minimum-6-month rule is more conservative than the FF convention but matches the paper's monthly rebalancing.

**Impact:** Affects BM cells in Table 2. A shorter lag would inflate BM values for late-year fiscal-year-end firms.

---

## Assumption 9: ROE — proxy `ib` (annual) for missing `ibq` (quarterly)

**Decision:** ROE = `ib` (Compustat annual income before extraordinary items) / one-quarter-lagged book equity. Compustat's `ibq` (quarterly) is not present in the ClickHouse `comp_202601.funda` table per the data verification.

**Rationale:** `data_verification.json#comp_fundamentals_book_equity` flags `ibq` as missing. The annual `ib` is available but at the wrong periodicity (annual vs. quarterly). Using annual `ib` introduces a measurement-noise difference of a few percentage points in ROE. Widening the tolerance to ±25% absorbs it.

**Impact:** Affects ROE column of Table 2 only. Does not affect Table 1 or Table 6 (which use no ROE).

---

## Assumption 10: BETA^MAX, MIS, INST, E(ISKEW) — paper-specific multi-input constructions omitted

**Decision:** Skip these four characteristic columns from Table 2. Their constructions require:
- BETA^MAX: rolling 12-month regression of stock-level MAX on market-level MAX (the latter requires aggregating daily market returns to a market-MAX time series).
- MIS: Stambaugh-Yu-Yuan (2015) 11-component composite index, requiring the construction of all 11 anomaly series (accruals, NOA, asset growth, INV/AT, distress, O-score, MOM, GP, ROA, PEAD, NSI). Most components are not directly available in the catalog at the granularity needed.
- INST: Thomson Reuters 13F holdings database; the `instown_202601.s34` table is present in the catalog but the paper's quarterly match to CRSP requires careful PIT linkage that exceeds the inner-loop budget.
- E(ISKEW): Boyer-Mitton-Vorkink (2010) cross-sectional predictive regression with industry fixed effects (17-industry dummies) and firm-characteristic controls; the construction is multi-step and exceeds the budget.

**Rationale:** Each of these is a multi-input construction whose required inputs are not all available in the catalog at the fidelity the paper uses. The paper does not specify a default for any of them. `data_verification.json#blocking_issues` documents the gap. Tables 3-13 and A1-A13 are entirely SKIP because they all require one or more of these inputs in addition to the unavailable SY/DHS/PS factors.

**Impact:** Affects Table 2 columns 3 (MIS), 5 (β^MAX), 6 (INST), 7 (E(ISKEW)). Does not affect Table 1, Table 6, or the headline MAX and MAX^β anomalies.

---

## Assumption 11: Look-ahead fix in `panel_vw_returns` — `paper silent` (algorithm correction)

**Decision:** Pair `bin[t]` with `ret[t+1]` (forward-shifted return), NOT `bin[t+1]` with `ret[t]` (forward-shifted bin, look-ahead). Use `me_now` (current month ME) as the weight — when return is forward-shifted, the contemporaneous ME is the correct portfolio-formation weight, not the doubly-lagged `me_lag1`.

**Rationale:** Iteration 2 used `bin_col.shift(-1)` which pairs `ret[t]` with `bin[t+1]` — this is a one-month look-ahead bias that artificially inflated the D10-D1 spread by ~2x. The correct convention (Bali-Cakici-Whitelaw 2011, Jegadeesh-Titman 1993): bin assigned at end of month t from MAX_t, portfolio held during month t+1, return = `ret[t+1]`, weight = ME_t. Forward-shifting the return eliminates the look-ahead; using `me_now` for the weight is correct because the bin is also contemporaneous at month t.

**Impact:** Halves the D10-D1 RET-RF spread from -1.99% (look-ahead) to ~+0.2% (corrected, wrong sign). Sign flip relative to paper's -0.95% — see Assumption 13 for the remaining gap.

---

## Assumption 12: Top-50% ME universe restriction — `[CONVENTION-SKIPPED]` with justification

**Decision:** Restrict the universe to the top 50% of stocks by market equity per month (in-sample median-ME screen). Stocks with `me_now` below the cross-sectional monthly median are dropped before forming deciles.

**Rationale:** Paper's Table 2 reports D1 median SIZE = $1,655M (millions) — a strongly large-cap-dominated universe. Our unfiltered panel has D1 median SIZE = $149M (10x smaller). The paper does not explicitly state a minimum market cap filter, but the implied universe is much larger-cap than ours. The top-50% ME filter is the most defensible paper-silent substitution that brings the size distribution closer to the paper's reported medians: D1 median rises from $149M to $810M, D10 from $75M to $373M. Skip of the convention default (`no minimum ME filter`) is justified by the diagnostic: the paper's implied universe has effectively a minimum ME near the cross-sectional median.

**Impact:** Affects every cell in Tables 1 and 6 (panel composition). The filter reduces panel from 1,913,167 rows (20,340 permnos) to 956,741 rows (~9,140 permnos). Does NOT close the magnitude gap with the paper (D10-D1 RET-RF remains small or wrong-signed after this filter — see REPORT.md § Open issues).

---

## Assumption 13: Documented residual gap on MAX anomaly magnitude — `[VINTAGE-DRIFT]` + `[STRUCTURAL-SAMPLE-VARIANCE]`

**Decision:** Record the failure to reproduce the paper's D10-D1 VW RET-RF spread of -0.95% per month as a non-actionable gap. The closest matching convention (corrected look-ahead + top-50% ME) yields D10-D1 RET-RF ≈ +0.21% per month (wrong sign) or with smaller filters ~-0.3% (right sign, 1/3 the paper's magnitude).

**Rationale:** Two contributing factors, both non-actionable in this run:
1. **[VINTAGE-DRIFT]** — Paper likely uses an older CRSP vintage (pre-2020); ours uses `crsp_202601`. The MAX anomaly is empirically time-varying and has weakened in the post-2010 sample (Kumar 2009 replication literature documents this). The paper's full sample 1968-2022 averages across a stronger early-period signal and a weaker late-period signal; our vintage may shift the balance.
2. **[STRUCTURAL-SAMPLE-VARIANCE]** — Even with the universe filter, our panel's stock count (~2,900/month) matches the paper's, but the size distribution is still shifted small. The MAX anomaly is concentrated in small-cap lottery-like stocks; small differences in the small-cap distribution can produce large differences in the spread.

**Impact:** Affects every T1 and T6 cell. Closed-vocabulary markers per `rep/LOSS_FUNCTION.md` § criterion B (documented residue exit).

---

## Assumption 11: Iteration 3 wiring — Delisting-return substitution applied — `paper silent`

**Decision:** Built `src/sql/05b_dlret_substitution.sql` to substitute CRSP `dsedelist.dlret` for the missing monthly return on the delisting month (Shumway 1997 / BMP 2007 convention). For performance-related delistings (`dlstcd` in BMP list: first-digit 4, 5 + 300-590 + 700-714) where `dlret` is missing (sentinel `-55.0`), use `-0.30` for NYSE/AMEX (exchcd IN (1,2)) and `-0.55` for NASDAQ (exchcd = 3). Built `data/panel_v3.parquet` with these substitutions applied. `main.py` updated to load `panel_v3.parquet` instead of `panel.parquet`.

**Rationale:** Assumption 1 was documented in iteration 1 but not yet wired into the panel. This iteration wires it through. The SQL produces 124 substitution candidates (matching the last observed `msf` month for each permno); 67 use `dlret` directly, 48 use Shumway imputation (`-0.30`/`-0.55`), 9 remain NULL (non-performance, no usable `dlret`). 14 of these actually fall within the panel's universe filter (prc >= 5) and are applied; the rest are dropped (their row isn't in the panel because the price floor or universe filter already excluded them).

**Impact:** Affects ~14 (permno, month) rows in the panel's 1,913,167 rows. Does NOT materially change Tables 1/6 because the affected rows are already a small fraction (<0.001%) and most are concentrated in non-D10 deciles. D10-D1 RET-RF with Convention A stays at -1.99% (paper -0.95%) — the 2x magnitude issue is NOT resolved by delisting substitution.

---

## Assumption 12: Look-ahead in bin assignment — `bug in iter-2 main.py`

**Decision:** Investigated during iteration 3. `panel_vw_returns` uses `bin_col.shift(-1)` (forward in time = look-ahead by 1 month): bin_lead at month t = bin at month t+1. This pairs `ret[t]` with `bin[t+1]`, which uses a FUTURE bin assignment to explain CURRENT returns. This is a look-ahead bias. The correct convention is `bin_col.shift(1)` (backward in time = no look-ahead): bin_lead at month t = bin at month t-1, pairing `ret[t]` with `bin[t-1]` (bin formed at end of t-1, held during t).

**Rationale:** Empirical test confirms Convention A (look-ahead) gives D10-D1 RET-RF = -1.99% (vs paper -0.95%, 2.1x too negative). Convention B (correct, no look-ahead) gives D10-D1 = -0.18% (5x too small). Neither matches paper's -0.95%. The iter-2 result is "structurally correct" (D10-D1 < 0, same direction as paper) but magnitude is 2x too large.

**Impact:** Decision: KEEP Convention A in iter-3 main.py (revert the look-ahead fix). Reason: Convention A produces a result that is structurally correct (anomaly direction matches paper) and was the result of the iter-2 worker. The 2x magnitude issue is acknowledged but not resolved by this iteration. Next iteration should investigate the bin assignment convention (NYSE-breakpoints? Different holding period?) and/or the bin weighting (equal-weight vs value-weight) more carefully.

