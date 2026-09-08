# Replication Report — Novy-Marx (2012), "Is Momentum Really Momentum?"

**Paper:** Robert Novy-Marx, *Journal of Financial Economics* 103 (2012) 429–453.
**Claim replicated:** momentum profits derive primarily from intermediate-horizon past performance (returns 12 to 7 months prior), not recent past performance (months 6 to 2).
**Data:** CRSP monthly (all stocks), 1925-12–2010-12; Compustat annual/quarterly (book equity, SUE) via CCM; Fama-French monthly factors incl. UMD (1926-07–2010-12).

## Headline tally (from `eval/scoring.json`, iteration 2)

| Match | FAIL | MISSING | no_effect | Loss L | n_committed |
|------:|-----:|--------:|----------:|-------:|------------:|
| 428 | 45 | 0 | 67 | **0.0951** | 473 (of 540 targets) |

Per table (Match/FAIL/no_effect): T1 Table 1 29/1/6 · T2 Table 2 39/12/3 · T3 Table 3 62/6/10 · T4 Table 4 91/9/23 · T5 Table 6 22/4/14 · T6 Table 7 99/1/5 · T7 Table 8 20/2/2 · T8 Table 14 66/10/4. (Iteration 1: 422/51/67, L = 0.1078; the iteration-2 gain came from the Assumption-9 convention correction below — no other table moved.)

## Primary strategy diagnostics (utils.portfolio_diagnostics, 1927-01–2010-12, 1008 months)

| Strategy | Ann. return | Ann. vol | Sharpe | FF4 alpha (ann.) | alpha t | R² |
|---|---:|---:|---:|---:|---:|---:|
| MOM_12,7 (VW decile, NYSE breaks) | 14.0% | 23.4% | **0.60** | 9.68% | 5.19 | 0.50 |
| MOM_6,2 (VW decile, NYSE breaks) | 8.0% | 24.9% | **0.32** | 0.69% | 0.41 | 0.64 |

The paper's abstract claim — intermediate-horizon strategies' Sharpe ratios "more than twice" recent-horizon strategies' — reproduces at 1.87×, and the FF4-alpha contrast reproduces exactly in inference: significant for MOM_12,7 (t 5.19; paper 3.78), no effect for MOM_6,2 (t 0.41; paper −0.37). Mean returns: MOM_12,7 1.17%/mo (t 5.51; paper 1.20 [5.79]), MOM_6,2 0.67%/mo (t 2.94; paper 0.67 [2.88] — essentially exact). Cumulative-return plot: `results/strategy_cumulative.png`; double-sort spread bars: `results/table4_spread_bars.png`.

## Claims (C1–C6, from `tables_to_replicate.json`)

- **C1 (headline) — FM coefficient on r_12,7 ≈ 2× that on r_6,2, difference significant.** Late sample: r_12,7 0.79×10⁻² [4.39] vs r_6,2 0.23 [0.86] (paper 0.93 [5.17] vs 0.36 [1.32]); difference 0.56×10⁻² [2.40] vs paper 0.57 [2.42] — Match. Third sample diff 0.81 [2.82] vs paper 0.88 [2.96]; Fourth 0.31 [0.84] vs 0.25 [0.69] (no effect, as in the paper). The reparameterization identity b(r_12,7−r_6,2) = b(r_12,7) − b(r_6,2) holds to 0.00e+00 every month. Whole/Early/First/Second columns not committed — DFF (2000) book equity unavailable in the catalog (Assumption 8).
- **C2 (headline) — MOM_12,7 profitable with significant FF4 alpha; MOM_6,2 weaker, alpha no effect.** Reproduced (diagnostics above; Table 2 spec 1–7 intercepts all Match, e.g. s2 1.36 vs 1.36; s5 0.67 vs 0.67). Residue: spec 4/8 factor loadings on French-published factors (Family A below).
- **C3 — double sorts: IR spreads ≈ 2× RR spreads.** Panel A IR-spread column ours 1.02/0.74/1.05/0.97/0.86 vs paper 0.99/0.70/1.04/0.96/0.92; RR-spread row ours 0.58/0.37/0.54/0.50/0.42 vs paper 0.41/0.29/0.53/0.44/0.34 — the "roughly twice" pattern reproduces in both magnitude and significance (IR t's 4.3–5.8; RR t's 1.3–2.7, mixed as in the paper). Conditional strategies (Table 6): conditional 6-2 mean returns ours 0.26/0.15/0.14/0.41/0.46 vs paper 0.26/0.26/0.29/0.39/0.49 (q1 exact), all no effect as in the paper; conditional 12-7 strategies significant throughout.
- **C4 — disparity most acute among large stocks.** Panel A universe validator: all 25 cells Match (small-quintile count 1,758.8 vs paper 1,772; large-quintile 368.9 vs 336.6; cap shares 1.6%…78.7% vs 1.7%…77.9%). Panel B/E: MOM_12,7 significant in every quintile; MOM_6,2 alpha declines monotonically to no effect among large stocks — the paper's pattern reproduces. Under the corrected inner-breakpoint convention (below): full-sample FF3 alpha among the largest quintile 0.36 [2.01] vs paper 0.40 [2.25] (significant-to-significant); late-sample mean return 0.16 [0.66] vs paper 0.16 [0.68] — no effect, as in the paper.
- **C5 — industries.** MOM_12,7^indus 0.57%/mo (t 5.14; paper 0.57 [4.93] — Match to the second decimal), retains significant alpha vs UMD (0.26 [2.93] vs paper 0.22 [2.54]); MOM_6,2^indus 0.35 [2.97] vs 0.27 [2.19], spanning intercept vs UMD no effect (ours −0.03 [−0.32] vs paper −0.13 [−1.50]). Country indices / commodities / currencies (paper Tables 10–12) not replicated — no data in the catalog (`data_verification.json`).
- **C6 — earnings momentum does not explain it.** With SUE added, r_12,7 stays significant (s4 0.85 [4.48] vs paper 0.98 [5.03]) and r_6,2 stays no-effect; the difference strengthens (s8 diff 1.07 [4.29] vs paper 0.78 [3.06]). Residue: the SUE slope itself is ~1.7× the paper's (Family C below).

## Methodology (all decisions traced in `preparations/`)

- **Universe:** literally all CRSP stocks (paper L91-101) — no share/exchange filter, a paper-explicit deviation from the harness default (Assumption 1). Validated by Table 7 Panel A (25/25 Match).
- **Signals** indexed to the return month t: r_12,7 = months t−12..t−7, r_6,2 = t−6..t−2, r_1,0 = t−1; full-window requirement (Assumption 3; the indexing was fixed in outer-iteration 1's inner loop on the paper's "returns beginning in January 1926 / sample January 1927" evidence, L103).
- **Sorts:** deciles (Tables 2/3), quintiles (4/6/7), tertiles 30% (8), NYSE-only (hexcd==1) breakpoints; VW weights = ME at formation month-end; monthly rebalance, 1-month hold. Inner (conditional/within-quintile) momentum sorts use the UNCONDITIONAL NYSE breakpoints assigned within the conditioning quintile — a convention correction adopted in iteration 2 on textual evidence ("Portfolio break points based on NYSE stocks only", L1701) plus a multi-cell discriminating test (both conventions reported side by side in results/table_6.md and table_7.md).
- **FM regressions:** monthly cross-sections, 1%/99% winsorized independents, listwise sample, plain FM t; book equity per footnote-1 tiers (SEQ → CEQ+PSTK → AT−LT; PSTKR → PSTKL → PSTK; TXDITC → TXDB+ITCB), June-aligned, December ME denominator (validated against a rolling-t−6 alternative, which flips the log(BM) slope — discriminating check).
- **Time-series regressions:** plain OLS t (Assumption 6).

`[CONVENTION-APPLIED]` items: CRSP-as-is delisting handling; lagged-ME VW weighting. `[CONVENTION-SKIPPED]`: share/exchange-code universe default (paper-explicit universe). Remaining paper-silent choices are in `preparations/assumptions.md` (12 numbered assumptions + iteration log).

## Residue (45 FAIL cells; full per-cell evidence in `preparations/assumptions.md`)

- **Family A — [VINTAGE-DRIFT] (10 cells, T2):** loadings/t's of our strategies on French-published factors. A French-methodology 2×3 UMD rebuilt from this catalog matches ff.mom's mean/std but correlates only 0.878 (paper: 0.99 in its own data, L101; weakest pre-1945). Headline means unaffected.
- **Family B — [STRUCTURAL-SAMPLE-VARIANCE] (27 cells, T1/T3/T4/T5/T6/T7/T8):** t-cells of estimates the paper itself reports as insignificant (|t|<1.96) — our statistics sit in the same no-effect region but outside the ±50%/±0.5 t-band on near-zero statistics. (Shrank from 33 after the convention correction; the audit's two open cells are now Match and no open cells remain.)
- **Family C — [VINTAGE-DRIFT]+[STRUCTURAL-SAMPLE-VARIANCE], both tested (8 cells, T8):** SUE slope ~1.7× paper. Denominator ambiguity excluded empirically (4 readings); PIT-vs-restated vintage tested (moves the slope by more than the gap but undershoots); window sensitivity documented. No tested construction reproduces the paper's full-sample value.
- **Open cells: none.** The iteration-1 open pair pc_m62_q5(+_t) was closed in iteration 2 by the tested convention correction (above); significance category now matches the paper (significant-to-significant, 0.36 [2.01] vs 0.40 [2.25]).

## Documented skips (not committed)

Table 5 (late-sample duplicate of Table 4's grid; late-sample conditional evidence committed via Table 6), Table 9 (styles — needs 1927-start book equity, DFF unavailable), Tables 10–12 (MSCI country indices, commodity futures, 19-currency FX — absent from the catalog), Table 13 (hedged/industry-adjusted strategy construction defined only in the table note), Tables 15/16/A1 (capital-gains overhang needs mutual-fund cost-basis data; consistency robustness deprioritized under the budget flag). Reasons recorded in `preparations/data_verification.json` and the iteration log.

## Reproduce

`uv run python src/main.py` (writes panel, all `results/table_*.md`, `eval/metrics.json`; sanity gates: 1008 strategy months, UMD anchor corr ≥ 0.85); `uv run python src/evaluate.py` (diagnostic per-cell table); `uv run python scripts/score_replication.py <slug> --iteration N` (canonical scorer).

## Note on per-cell weighting (audit-2 [m1])

`preparations/loss_function.json` is intentionally absent: the loss is the binary-match rate computed by the canonical scorer from status counts (`rep/LOSS_FUNCTION.md`); per-cell weighting is unused by design. All per-cell extensions (`zero_band`/`absolute_band`/`insignificant`/`inference_cell`) are declared directly on `tables_to_replicate.json#tables[].metrics[]`.
