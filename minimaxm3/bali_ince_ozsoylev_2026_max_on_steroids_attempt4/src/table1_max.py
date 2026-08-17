"""
MAX on Steroids — Table 1 (Univariate MAX decile sort).

Replicates paper Table 1 (page 57, L974-L1144). Reports the 10 MAX-decile
portfolios' one-month-ahead VW excess returns (RET - RF) and factor-model
alphas under 5 models retained (CAPM, FF3, FFC4, FF5, FF6).

Per `preparations/assumptions.md`:
  - Skip SY / DHS columns (Assumption 1, 2) — not in ClickHouse.
  - Skip FFCPS / FF6PS columns (Assumption 3) — LIQ not in ClickHouse.
  - NYSE-only breakpoints for decile assignment (Assumption 17).

Critical fixes vs iter-1 spot check (src/main.py:quick_table1_spot_check):
  a) VW weights use PRIOR-MONTH ME = ME.shift(1) per permno.
  b) BETA winsorized cross-sectionally at 1%/99% per month before sorts.
  c) Newey-West t-stats use 6 lags (preprocessing_rules.json#newey_west_lags).
  d) FF6 includes BOTH MOM and RMW/CMA = FF5 + MOM = 6 factors.
  e) ITER-3: NYSE-only breakpoints for decile assignment (10 deciles cut
     on the NYSE-only distribution of MAX each month, then applied to all
     stocks). Drops months with < 30 NYSE stocks.

Factor models:
  - CAPM:    mkt_rf
  - FF3:     mkt_rf, smb, hml
  - FFC4:    mkt_rf, smb, hml, mom
  - FF5:     mkt_rf, smb, hml, rmw, cma
  - FF6:     mkt_rf, smb, hml, mom, rmw, cma
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from utils.env import get_clickhouse_config  # noqa: E402
from utils.paths import paper_layout  # noqa: E402
from utils.regressions import factor_alpha  # noqa: E402
from utils.quantile import assign_quantiles  # noqa: E402

SLUG = "max_on_steroids_attempt4"
LAYOUT = paper_layout(SLUG)
LAYOUT.ensure()

PANEL_PATH = LAYOUT.data_path("panel.parquet")
RESULTS_DIR = LAYOUT.result_path  # function: result_path(name) -> Path
EVAL_PATH = LAYOUT.eval_path("metrics.json")

# --- configuration ---------------------------------------------------------

N_BINS = 10
NW_LAGS = 6                      # preprocessing_rules.json#newey_west_lags
WINSORIZE_PCT = 0.01             # 1% / 99% winsorization

# Factor models: (display_name, [factor_cols])
FACTOR_MODELS = [
    ("RET-RF", []),              # raw excess return (no regression)
    ("CAPM",   ["mkt_rf"]),
    ("FF3",    ["mkt_rf", "smb", "hml"]),
    ("FFC4",   ["mkt_rf", "smb", "hml", "mom"]),
    ("FF5",    ["mkt_rf", "smb", "hml", "rmw", "cma"]),
    ("FF6",    ["mkt_rf", "smb", "hml", "mom", "rmw", "cma"]),
]
SKIP_MODELS = {"SY", "DHS", "FFCPS", "FF6PS"}


# --- ClickHouse connection -------------------------------------------------

import os
from clickhouse_driver import Client

_CFG = get_clickhouse_config()


def _client() -> Client:
    return Client(
        host=_CFG["host"],
        port=int(_CFG["port"]),
        user=_CFG["user"],
        password=_CFG["password"],
        database=_CFG.get("database", "default"),
        settings={"max_execution_time": 300},
    )


def q(sql: str) -> pd.DataFrame:
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


# --- 1. Load FF factors ----------------------------------------------------


def load_ff_factors() -> pd.DataFrame:
    """Load FF factors from ClickHouse; merge 4-factor and 5-factor tables."""
    sql = """
    SELECT
        toDate32(f4.dt)  AS month,
        f4.mkt_rf        AS mkt_rf,
        f4.smb           AS smb,
        f4.hml           AS hml,
        f4.rf            AS rf,
        f4.mom           AS mom,
        f5.rmw           AS rmw,
        f5.cma           AS cma
    FROM ff.four_factor_monthly AS f4
    LEFT JOIN ff.five_factor_monthly AS f5
        ON toDate32(f4.dt) = toDate32(f5.dt)
    WHERE toDate32OrNull(f4.dt) >= toDate32('1968-01-01')
      AND toDate32OrNull(f4.dt) <= toDate32('2022-12-31')
    SETTINGS max_execution_time = 60
    """
    df = q(sql)
    df["month"] = pd.to_datetime(df["month"])
    # Convert FF month-end dates to month-start of the SAME calendar month
    # so they merge with the panel's month-start keys.
    df["month"] = df["month"] - pd.offsets.MonthBegin(1)
    # month-start-of-month rebuild from year-month (avoids any timezone weirdness)
    df["month"] = pd.to_datetime(df["month"].dt.strftime("%Y-%m") + "-01")
    print(f"[ff] loaded {len(df)} months of FF factors "
          f"({df['month'].min()} .. {df['month'].max()})")
    return df


# --- 2. Build panel with ME_lag1, BETA winsorized --------------------------


def prepare_panel(panel: pd.DataFrame) -> pd.DataFrame:
    """Add ME_lag1 (prior-month ME per permno) AND/OR me_june_t (June snapshot,
    FF 1993 / Bali-2011 carry-forward convention) and winsorize BETA
    cross-sectionally.

    The panel.parquet (post-iter5) carries BOTH ME_lag1 (backup) AND me_june_t.
    prepare_panel() preserves both columns and recomputes ME_lag1 if missing.
    """
    panel = panel.copy()
    panel["month"] = pd.to_datetime(panel["month"])
    panel = panel.sort_values(["permno", "month"]).reset_index(drop=True)

    # (a) ME_lag1: prior-month ME per permno (kept as backup column).
    if "ME_lag1" not in panel.columns:
        panel["ME_lag1"] = panel.groupby("permno")["ME"].shift(1)

    # (b) Winsorize BETA cross-sectionally at 1% / 99% per month
    def _w(s: pd.Series) -> pd.Series:
        lo, hi = s.quantile([WINSORIZE_PCT, 1 - WINSORIZE_PCT])
        return s.clip(lower=lo, upper=hi)

    panel["BETA_w"] = (
        panel.groupby("month")["BETA"].transform(_w)
    )

    return panel


# --- 3. Decile sort + VW portfolio returns ---------------------------------


def _attach_nyse_flag(sub: pd.DataFrame) -> pd.DataFrame:
    """PIT-attach `is_nyse` flag to each row of `sub` using dsenames.

    Sub must have columns permno and month. Returns sub with new
    bool column `is_nyse` (True iff permno was on NYSE=1 at month-end).
    """
    sql = """
    SELECT
        toInt32(d.permno)                              AS permno,
        toDate32(substring(toString(d.date), 1, 7) || '-01') AS month,
        n.exchcd                                       AS exchcd
    FROM crsp_202601.dsf AS d
    INNER JOIN crsp_202601.dsenames AS n
        ON d.permno = n.permno
       AND toDate32OrNull(d.date) >= toDate32OrNull(n.namedt)
       AND toDate32OrNull(d.date) <= ifNull(toDate32OrNull(n.nameendt),
                                           toDate32('2099-12-31'))
    WHERE toDate32OrNull(d.date) >= toDate32('1968-01-01')
      AND toDate32OrNull(d.date) <= toDate32('2022-12-31')
      AND n.shrcd IN (10, 11)
    SETTINGS max_execution_time = 300
    """
    exch = q(sql)
    exch["month"] = pd.to_datetime(exch["month"])
    # If a permno has multiple name-history rows in the same month
    # (rare), pick the last day-of-month entry.
    exch = exch.sort_values(["permno", "month"]).drop_duplicates(
        subset=["permno", "month"], keep="last"
    )
    exch["is_nyse"] = exch["exchcd"] == 1
    exch = exch[["permno", "month", "is_nyse"]]

    out = sub.merge(exch, on=["permno", "month"], how="left")
    out["is_nyse"] = out["is_nyse"].fillna(False).astype(bool)
    return out


def _nyse_breakpoint_deciles(sub: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    """Form 10 decile breakpoints using NYSE-only MAX distribution each month.

    Returns (decile_series, breakpoint_stats) where:
      - decile_series is a pandas Series aligned to sub's index (1..10,
        or NaN when MAX is NaN). Position-based: index does not matter
        for assignment; the caller uses ``sub["decile"] = decile_series.values``.
      - breakpoint_stats has columns ['month', 'n_nyse', 'n_total'].
    """
    flagged = _attach_nyse_flag(sub)
    nyse = flagged[flagged["is_nyse"]].copy()
    breakpoint_stats = (
        flagged.groupby("month")
        .agg(n_nyse=("is_nyse", "sum"), n_total=("is_nyse", "count"))
        .reset_index()
    )

    # Per-month NYSE breakpoints: 9 cut points (10 deciles)
    quantiles = np.linspace(0, 1, N_BINS + 1)[1:-1]
    bp = (
        nyse.groupby("month")["MAX"]
        .quantile(quantiles)
        .unstack(level=-1)  # columns: 0.1, 0.2, ..., 0.9
        .reset_index()
    )
    bp.columns = ["month"] + [f"bp_{i}" for i in range(1, N_BINS)]

    # Apply breakpoints to ALL stocks (NYSE + non-NYSE)
    out = flagged.merge(bp, on="month", how="left")

    # Vectorized decile assignment: compare MAX against each breakpoint
    bp_cols = [f"bp_{i}" for i in range(1, N_BINS)]
    arr = out[bp_cols].values         # shape (n, 9)
    mx = out["MAX"].values[:, None]   # shape (n, 1)
    # decile = 1 + count of breakpoints strictly less than MAX
    dec = (mx > arr).sum(axis=1) + 1  # 1..10
    # Stocks with MAX = NaN -> NaN; with MAX below all breakpoints -> 1;
    # above all -> 10; ties on breakpoints get an arbitrary side per ">"
    # (this is the standard CCK convention)
    decile_series = pd.Series(
        np.where(out["MAX"].notna(), dec, np.nan),
        index=out.index,
        name="decile",
    )

    return decile_series, breakpoint_stats


def form_decile_portfolios(panel: pd.DataFrame, vw_col: str = "ME_lag1") -> pd.DataFrame:
    """Form 10 MAX deciles per month using NYSE-only breakpoints; compute VW excess returns.

    Iter-3: breakpoints are computed from the NYSE-only distribution of MAX each
    month (per Fama-French 1993 / Bali-Cakici-Whitelaw 2011 convention), then
    applied to all stocks (NYSE + NASDAQ + AMEX). Drops months with fewer than
    30 NYSE stocks.

    Iter-5: `vw_col` controls the VW weight. Default "ME_lag1" (prior-month ME
    per permno); passing "me_june_t" switches to the FF93/Bali-2011 carry-forward
    June snapshot held constant for 12 months.

    Returns DataFrame with columns ['month','decile','ret_vw'].
    """
    sub = panel.dropna(subset=["MAX", "BETA_w", "ret_excess_next", vw_col]).copy()
    sub = sub[sub[vw_col] > 0]

    # NYSE-only-breakpoint decile assignment
    decile_series, bp_stats = _nyse_breakpoint_deciles(sub)
    # Use .values to assign by position (the index from the merge may not
    # be aligned with sub's index after dropping NaN rows).
    sub = sub.copy()
    sub["decile"] = pd.Series(decile_series.values, index=sub.index).astype("Int64")

    # Drop months with fewer than 30 NYSE stocks (per spec)
    keep_months = bp_stats[bp_stats["n_nyse"] >= 30]["month"]
    sub = sub[sub["month"].isin(keep_months)].copy()
    sub = sub.dropna(subset=["decile"])
    sub["decile"] = sub["decile"].astype(int)

    # VW per (month, decile) using the chosen weight
    grp = sub.groupby(["month", "decile"])
    vw = (grp.apply(lambda g: pd.Series({
        "vw_sum": (g["ret_excess_next"] * g[vw_col]).sum(),
        "w_sum":  g[vw_col].sum(),
    }), include_groups=False).reset_index())
    vw["ret_vw"] = vw["vw_sum"] / vw["w_sum"]

    print(f"[table1] {vw['month'].nunique()} months used for portfolio sorts "
          f"(vw={vw_col})")
    print(f"[table1] decile counts (avg per month): "
          f"{vw.groupby('decile').size().mean():.1f}")
    return vw[["month", "decile", "ret_vw"]]


def vw_with_june_t_me(panel: pd.DataFrame) -> pd.DataFrame:
    """Convenience wrapper: same as form_decile_portfolios with vw_col='me_june_t'."""
    return form_decile_portfolios(panel, vw_col="me_june_t")


# --- 4. Per-cell alphas ----------------------------------------------------


def compute_cell_alphas(
    port_vw: pd.DataFrame,
    ff: pd.DataFrame,
) -> dict:
    """For each (decile, factor model), compute alpha + NW t-stat.

    Returns dict: cell_label -> {'value': alpha_monthly, 't': t_stat, 'n': n_obs}
    """
    # Merge portfolio returns with FF factors on month
    df = port_vw.merge(ff, on="month", how="inner").sort_values("month")

    # Build wide table: one column per decile for ret_vw
    df_wide = df.pivot(index="month", columns="decile", values="ret_vw").sort_index()

    # Portfolio excess returns: the panel's ret_excess_next already has rf subtracted.
    # So VW ret_vw is the excess return directly (since VW subtracts at the
    # stock level before aggregating). No further rf subtraction.
    # Sanity: this matches the paper's "value-weighted average one-month-ahead
    # excess returns (RET – RF)".

    cells = {}

    for model_name, factors in FACTOR_MODELS:
        for decile in sorted(int(c) for c in df_wide.columns):
            label = f"P{int(decile)}_{model_name.replace('-', '_')}"
            series = df_wide[decile].dropna()

            if model_name == "RET-RF":
                # Plain time-series mean (alpha = mean excess return); no regression
                # NW t-stat on the mean of the return series
                alpha_m = float(series.mean())
                n = len(series)
                # HAC SE on the mean: sqrt(sum_lag(2/2 * lag * autocov) / n^2)
                # Standard NW t-stat formula applied to a constant-only model.
                # Use statsmodels OLS with intercept for proper NW SE.
                try:
                    import statsmodels.api as sm
                    from statsmodels.stats.sandwich_covariance import cov_hac
                    y = series.values.astype(float)
                    X = np.ones((n, 1))
                    mod = sm.OLS(y, X).fit()
                    cov = cov_hac(mod, nlags=NW_LAGS)
                    se = float(np.sqrt(cov[0, 0]))
                    t = alpha_m / se if se > 0 else float("nan")
                except Exception:
                    t = float("nan")
                cells[label] = {
                    "value": alpha_m,
                    "t": t,
                    "n": n,
                }
            else:
                # Run factor_alpha regression; pass factors as extra cols
                ff_aligned = df[["month", "rf"] + factors].drop_duplicates().set_index("month")
                port = series.to_frame("ret")
                res = factor_alpha(
                    port, ff_aligned, factors=factors, rf_col="rf",
                    ret_col="ret", n_lags=NW_LAGS, freq="M",
                )
                cells[label] = {
                    "value": float(res["alpha_monthly"]),
                    "t": float(res["t_alpha_newey_west"]),
                    "n": int(res["n_obs"]),
                }

    # Spread row: D10 - D1 for each model
    for model_name, _ in FACTOR_MODELS:
        label = f"D10_D1_{model_name.replace('-', '_')}"
        d10_key = f"P10_{model_name.replace('-', '_')}"
        d1_key = f"P1_{model_name.replace('-', '_')}"
        d10 = cells[d10_key]
        d1 = cells[d1_key]
        cells[label] = {
            "value": d10["value"] - d1["value"],
            "t": float("nan"),   # spread t-stat computed separately below
            "n": min(d10["n"], d1["n"]),
        }

    # Spread NW t-stats via factor_alpha on the spread series
    for model_name, factors in FACTOR_MODELS:
        label = f"D10_D1_{model_name.replace('-', '_')}"
        d10_w = df_wide[10].dropna()
        d1_w = df_wide[1].dropna()
        spread = (d10_w - d1_w).dropna()
        spread = spread.to_frame("ret")

        if model_name == "RET-RF":
            try:
                import statsmodels.api as sm
                from statsmodels.stats.sandwich_covariance import cov_hac
                n = len(spread)
                y = spread["ret"].values.astype(float)
                X = np.ones((n, 1))
                mod = sm.OLS(y, X).fit()
                cov = cov_hac(mod, nlags=NW_LAGS)
                se = float(np.sqrt(cov[0, 0]))
                t = float(spread["ret"].mean() / se) if se > 0 else float("nan")
            except Exception:
                t = float("nan")
        else:
            ff_aligned = df[["month", "rf"] + factors].drop_duplicates().set_index("month")
            res = factor_alpha(
                spread, ff_aligned, factors=factors, rf_col="rf",
                ret_col="ret", n_lags=NW_LAGS, freq="M",
            )
            t = float(res["t_alpha_newey_west"])
        cells[label]["t"] = t

    return cells


# --- 5. Output: markdown + JSON metrics ------------------------------------


def cells_to_markdown(cells: dict) -> str:
    """Build markdown grid mirroring paper Table 1 format."""
    model_cols = [m[0] for m in FACTOR_MODELS]
    n_decile_rows = N_BINS
    n_spread_rows = 1
    total_rows = n_decile_rows + n_spread_rows

    lines = []
    lines.append("# Table 1 — MAX Decile Portfolios: VW Excess Returns and Factor Alphas")
    lines.append("")
    lines.append("Sample: 1968-01 to 2022-12 (660 months). "
                 "Independent decile sorts by MAX. "
                 "VW by prior-month ME. "
                 "Newey-West t-stats with 6 lags in parentheses.")
    lines.append("")

    # Header
    header = "| Portfolio | " + " | ".join(model_cols) + " |"
    sep = "|" + "|".join(["---"] * (len(model_cols) + 1)) + "|"
    lines.append(header)
    lines.append(sep)

    def fmt_cell(label: str) -> str:
        c = cells[label]
        v = c["value"] * 100
        t = c["t"]
        if pd.isna(v):
            return "—"
        return f"{v:.2f}<br>({t:.2f})" if not pd.isna(t) else f"{v:.2f}"

    for d in range(1, N_BINS + 1):
        row = [f"P{d}"]
        for m in model_cols:
            label = f"P{d}_{m.replace('-', '_')}"
            row.append(fmt_cell(label))
        lines.append("| " + " | ".join(row) + " |")

    # Spread row
    row = ["10-1"]
    for m in model_cols:
        label = f"D10_D1_{m.replace('-', '_')}"
        row.append(fmt_cell(label))
    lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("## Notes")
    lines.append("- RET-RF column = time-series mean of value-weighted excess returns "
                 "(no factor regression).")
    lines.append("- All alphas in %/month.  Skipped models (per assumptions.md): "
                 "SY, DHS, FFCPS, FF6PS (third-party / missing factors).")
    lines.append("- `*_SY` and `*_DHS` cells: SKIP (Stambaugh-Yuan / DHS factors "
                 "not in ClickHouse).")
    lines.append("- `*_FFCPS` and `*_FF6PS` cells: SKIP (Pastor-Stambaugh LIQ "
                 "not in ClickHouse).")
    return "\n".join(lines)


def cells_to_paper_grid(cells: dict) -> str:
    """Build paper-style grid: 'value (t-stat)' per cell, plain text."""
    model_cols = [m[0] for m in FACTOR_MODELS]
    lines = []
    lines.append("=" * 100)
    lines.append("TABLE 1: MAX DECILE PORTFOLIOS — VW EXCESS RETURNS AND FACTOR ALPHAS")
    lines.append("=" * 100)
    header = f"{'Portfolio':<10} | " + " | ".join(f"{c:>14}" for c in model_cols)
    lines.append(header)
    lines.append("-" * len(header))

    def fmt(label: str) -> str:
        c = cells[label]
        v = c["value"] * 100
        t = c["t"]
        if pd.isna(v):
            return "—"
        if pd.isna(t):
            return f"{v:7.2f}"
        return f"{v:5.2f} ({t:5.2f})"

    for d in range(1, N_BINS + 1):
        row = f"P{d:<9} | " + " | ".join(
            fmt(f"P{d}_{m.replace('-', '_')}") for m in model_cols
        )
        lines.append(row)

    spread_row = f"{'10-1':<10} | " + " | ".join(
        fmt(f"D10_D1_{m.replace('-', '_')}") for m in model_cols
    )
    lines.append(spread_row)
    lines.append("=" * 100)
    lines.append("Format: value (t-stat), values in %/month, t-stats Newey-West(6)")
    return "\n".join(lines)


def cells_to_metrics_json(cells: dict, paper_target: dict | None = None) -> dict:
    """Format cells for eval/metrics.json (only the cells the evaluator consumes).

    Converts decimal monthly alpha to PERCENT/month to match the paper target
    units (per tables_to_replicate.json `unit: "%/month"`). Factor-model
    intercepts from factor_alpha are returned in decimal.

    Includes SKIP entries for *_SY, *_DHS, *_FFCPS, *_FF6PS cells that are
    in the paper target list but unavailable in ClickHouse (per
    assumptions.md).
    """
    metrics = {}
    for label, c in cells.items():
        v = float(c["value"]) if not pd.isna(c["value"]) else None
        # Convert decimal -> PERCENT to match paper target units ("%/month").
        if v is not None:
            v_pct = v * 100.0
        else:
            v_pct = None
        metrics[label] = {
            "value": v_pct,
            "t_stat": float(c["t"]) if not pd.isna(c["t"]) else None,
            "n_obs": int(c["n"]),
            "unit": "%/month",
        }

    # Add SKIP entries for paper-target cells we cannot compute
    if paper_target is not None:
        skip_suffixes = ("_SY", "_DHS", "_FFCPS", "_FF6PS")
        for label in paper_target:
            if label in metrics:
                continue
            if any(label.endswith(s) for s in skip_suffixes):
                metrics[label] = {
                    "value": None,
                    "t_stat": None,
                    "n_obs": 0,
                    "unit": "ratio",
                    "status": "SKIP",
                    "skip_reason": "third-party factor unavailable in ClickHouse",
                }
    return metrics


def compare_to_paper(cells: dict, paper_target: dict) -> str:
    """Compare replicated cells to paper values; print side-by-side."""
    lines = []
    lines.append("=" * 100)
    lines.append("TABLE 1: REPLICATED vs PAPER (30% tolerance)")
    lines.append("=" * 100)
    lines.append(f"{'Cell':<14} | {'Replicated':>12} | {'Paper':>10} | {'%Diff':>10} | Status")

    n_match = 0
    n_fail = 0
    n_skip = 0
    for label, c in cells.items():
        rep_v = c["value"] * 100  # %/month

        # Map label to paper target key
        # Cells are P1_RET_RF, D10_D1_FF5, etc.
        # Paper target keys are the same: P1_RET_RF, D10_D1_FF5, etc.
        paper_v = paper_target.get(label)
        if paper_v is None:
            # Cell not in paper target list - likely a SKIP
            if "_SY" in label or "_DHS" in label or "_FFCPS" in label or "_FF6PS" in label:
                n_skip += 1
                lines.append(f"{label:<14} | {'':>12} | {'':>10} | {'':>10} | SKIP")
            else:
                lines.append(f"{label:<14} | {rep_v:>10.3f}% | {'(missing)':>10} | {'':>10} | N/A")
            continue

        if paper_v == 0:
            pct_diff = float("inf") if abs(rep_v) > 1e-6 else 0.0
        else:
            pct_diff = abs((rep_v - paper_v) / paper_v) * 100

        # 30% tolerance per tables_to_replicate.json
        within_tol = pct_diff <= 30
        status = "Match" if within_tol else "FAIL"
        if within_tol:
            n_match += 1
        else:
            n_fail += 1
        lines.append(
            f"{label:<14} | {rep_v:>10.3f}% | {paper_v:>8.2f}% | {pct_diff:>8.1f}% | {status}"
        )

    lines.append("=" * 100)
    lines.append(f"Match: {n_match}  FAIL: {n_fail}  SKIP: {n_skip}")
    return "\n".join(lines)


def compare_two_weights(cells_lag1: dict, cells_june: dict,
                        paper_target: dict) -> str:
    """Side-by-side comparison of two VW-weighting schemes (lag-1 vs June-t)
    for headline cells only. Per spec: ME_lag1 result | me_june_t result |
    paper | r_old | r_new.
    """
    headline = [
        "P1_RET_RF", "P10_RET_RF", "D10_D1_RET_RF",
        "D10_D1_CAPM", "D10_D1_FF3", "D10_D1_FFC4",
        "D10_D1_FF5", "D10_D1_FF6",
    ]
    lines = []
    lines.append("=" * 110)
    lines.append("HEADLINE COMPARISON: ME_lag1 vs me_june_t (Table 1)")
    lines.append("=" * 110)
    lines.append(f"{'Cell':<14} | {'ME_lag1':>10} | {'me_june_t':>10} | "
                 f"{'paper':>8} | {'r_old':>6} | {'r_new':>6} | winner")
    for label in headline:
        cl = cells_lag1.get(label, {}).get("value", float("nan"))
        cj = cells_june.get(label, {}).get("value", float("nan"))
        pv = paper_target.get(label)
        if pv is None:
            continue
        # r = |rep / paper|, capped at sensible level
        def _r(v: float) -> float:
            if not np.isfinite(v) or pv == 0:
                return float("nan")
            return float(abs((v * 100) / pv))

        cl_pct = cl * 100 if np.isfinite(cl) else float("nan")
        cj_pct = cj * 100 if np.isfinite(cj) else float("nan")
        r_old = _r(cl)
        r_new = _r(cj)
        # winner: closer to (0.5..2.0) range OR sign match?
        # Pick the one with |r-1.0| closer to 0.
        old_d = abs(r_old - 1.0) if np.isfinite(r_old) else float("inf")
        new_d = abs(r_new - 1.0) if np.isfinite(r_new) else float("inf")
        if not np.isfinite(old_d) and not np.isfinite(new_d):
            winner = "?"
        elif new_d < old_d:
            winner = "june"
        elif old_d < new_d:
            winner = "lag1"
        else:
            winner = "tie"
        lines.append(
            f"{label:<14} | {cl_pct:>9.3f}% | {cj_pct:>9.3f}% | "
            f"{pv:>7.2f}% | {r_old:>5.2f} | {r_new:>5.2f} | {winner}"
        )
    lines.append("=" * 110)
    lines.append("r = |replicated/paper|; closer to 1.0 is better. "
                 "r ∈ [0.33, 3.0] is the headline-magnitude band.")
    return "\n".join(lines)


# --- 5b. Diagnostics (FIX B, FIX C) -----------------------------------------


def _check_me_lag(panel: pd.DataFrame) -> None:
    """FIX B: confirm ME.shift(1) per permno is truly a 1-month lag.

    Method: take a fresh copy of the panel, sort by (permno, month), and
    compute ME_lag1_check = groupby(permno).ME.shift(1). Then for each row
    at month t, find the prior row's ME directly (via the same sorted frame)
    and compare element-wise.
    """
    sub = panel[["permno", "month", "ME"]].dropna().copy()
    sub = sub.sort_values(["permno", "month"]).reset_index(drop=True)
    sub["ME_lag1_check"] = sub.groupby("permno")["ME"].shift(1)
    # The ME at month t-1 should equal ME_lag1_check at month t — both
    # reference the same cell of the sorted frame. Compare on the rows
    # where ME_lag1_check is non-null.
    valid = sub.dropna(subset=["ME_lag1_check"]).copy()
    # Use the row's ME compared to ME_lag1_check (correct framing: at the
    # same row, ME_lag1_check == ME(t-1) by construction).
    # We compare ME_lag1_check to ME.shift(1) at the *same index* — this is
    # a tautology — instead we want to verify that the EMPIRICAL ME at
    # month t-1 (via merge) matches ME_lag1 at month t.
    # Build a self-merge:
    a = sub[["permno", "month", "ME"]].rename(columns={"ME": "ME_t"})
    b = sub[["permno", "month", "ME"]].rename(columns={"ME": "ME_t_minus_1"})
    b["month"] = b["month"] + pd.DateOffset(months=1)
    j = a.merge(b, on=["permno", "month"], how="inner")
    j["ME_lag1_from_merge"] = sub.set_index(["permno", "month"]).reindex(
        pd.MultiIndex.from_arrays([j["permno"], j["month"]])
    )["ME_lag1_check"].values
    match = np.isclose(
        j["ME_lag1_from_merge"], j["ME_t_minus_1"], rtol=1e-6, atol=1e-3
    )
    match_rate = match.mean()
    print(f"[FIX B] ME_lag1 == ME_(t-1) match rate: {match_rate:.4f} "
          f"({match.sum()}/{len(match)})")

    # Distribution of month gaps between consecutive rows per permno
    chk = panel[["permno", "month"]].dropna().copy()
    chk = chk.sort_values(["permno", "month"]).reset_index(drop=True)
    chk["month_diff"] = (
        chk.groupby("permno")["month"].diff().dt.days / 30.4375
    )
    print("[FIX B] Consecutive-row month-gap distribution (per permno):")
    print(chk["month_diff"].describe().to_string())


def _diagnose_d10_d1_me(port_vw: pd.DataFrame, panel: pd.DataFrame) -> None:
    """FIX C: print D10 / P1 / D1 mean ME and per-decile counts.

    Uses the panel's decile assignment at the (panel, decile) level
    (post-NYSE-breakpoint deciles) to compute decile mean ME.
    """
    sub = panel.dropna(subset=["MAX", "BETA_w", "ret_excess_next", "ME_lag1"]).copy()
    sub = sub[sub["ME_lag1"] > 0]
    decile_series, bp_stats = _nyse_breakpoint_deciles(sub)
    # Use .values + matching index to assign by position (matches
    # the production code path in form_decile_portfolios).
    sub = sub.copy()
    sub["decile"] = pd.Series(decile_series.values, index=sub.index).astype("Int64")
    keep_months = bp_stats[bp_stats["n_nyse"] >= 30]["month"]
    sub = sub[sub["month"].isin(keep_months)].copy()
    sub = sub.dropna(subset=["decile"])
    sub["decile"] = sub["decile"].astype(int)

    me_by_dec = sub.groupby("decile")["ME_lag1"].agg(["mean", "median", "count"])
    print("[FIX C] NYSE-breakpoint decile → ME_lag1 stats:")
    print(me_by_dec.to_string())
    d10_mean = float(me_by_dec.loc[10, "mean"])
    p1_mean = float(me_by_dec.loc[1, "mean"])
    print(f"[FIX C] D10 mean ME: ${d10_mean/1e9:.2f}B    "
          f"P1 mean ME: ${p1_mean/1e9:.2f}B")
    print(f"[FIX C] NYSE-months used: {len(keep_months)} / "
          f"{bp_stats['month'].nunique()} total months")


# --- 6. main ---------------------------------------------------------------


def main() -> int:
    print(f"[table1] loading panel from {PANEL_PATH}")
    panel = pd.read_parquet(PANEL_PATH)
    print(f"[table1] panel: {len(panel):,} rows x {panel.shape[1]} cols")

    # 1. Load FF factors
    ff = load_ff_factors()

    # 2. Build prior-month ME, winsorize BETA
    panel = prepare_panel(panel)

    # --- FIX B: verify ME_lag1 is actually a 1-month lag -----------------
    _check_me_lag(panel)

    # 3. Form deciles + VW portfolio returns (NYSE-only breakpoints, iter-3)
    #    — and a SECOND pass with me_june_t as the VW weight (iter-5).
    port_vw_lag1 = form_decile_portfolios(panel, vw_col="ME_lag1")
    port_vw_june = form_decile_portfolios(panel, vw_col="me_june_t")

    # --- FIX C: sanity-check VW weights via large-cap ME stats -----------
    _diagnose_d10_d1_me(port_vw_lag1, panel)

    # 4. Compute per-cell alphas (P1..P10 + 10-1 for 6 factor models = 66 cells)
    cells_lag1 = compute_cell_alphas(port_vw_lag1, ff)
    cells_june = compute_cell_alphas(port_vw_june, ff)

    # 5a. Print paper-grid to console (lag-1, then june)
    print()
    print("--- ME_lag1 (iter-3 default) ---")
    print(cells_to_paper_grid(cells_lag1))
    print()
    print("--- me_june_t (iter-5 fix) ---")
    print(cells_to_paper_grid(cells_june))

    # 5b. Print side-by-side vs paper
    paper_target_path = LAYOUT.input_path("tables_to_replicate.json")
    with open(paper_target_path) as f:
        paper_cfg = json.load(f)
    paper_target = {
        m["name"]: m["value"]
        for t in paper_cfg["tables"] if t["id"] == "T1"
        for m in t["metrics"]
    }
    print()
    print(compare_two_weights(cells_lag1, cells_june, paper_target))
    print()
    print(compare_to_paper(cells_june, paper_target))

    # 6. Save results (iter-5: write the me_june_t version as canonical)
    RESULTS_DIR("").mkdir(parents=True, exist_ok=True)
    md = cells_to_markdown(cells_june)
    (RESULTS_DIR("table_1_v2.md")).write_text(md)
    print(f"\n[table1] saved {RESULTS_DIR('table_1_v2.md')}")
    # Overwrite table_1.md with the me_june_t version per spec
    (RESULTS_DIR("table_1.md")).write_text(md)
    print(f"[table1] saved {RESULTS_DIR('table_1.md')}")

    # Save paper-grid + comparison + headline comparison as plain text
    grid_text = (
        "=== ME_lag1 (iter-3 baseline) ===\n"
        + cells_to_paper_grid(cells_lag1)
        + "\n\n=== me_june_t (iter-5 fix) ===\n"
        + cells_to_paper_grid(cells_june)
        + "\n\n" + compare_two_weights(cells_lag1, cells_june, paper_target)
        + "\n\n" + compare_to_paper(cells_june, paper_target)
    )
    (RESULTS_DIR("table_1_results.txt")).write_text(grid_text)
    print(f"[table1] saved {RESULTS_DIR('table_1_results.txt')}")

    # 7. Save eval/metrics.json (using the me_june_t cells)
    EVAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    metrics = cells_to_metrics_json(cells_june, paper_target=paper_target)
    payload = {"schema_version": 2, "slug": SLUG, "metrics": metrics}
    EVAL_PATH.write_text(json.dumps(payload, indent=2, default=float))
    print(f"[table1] saved {EVAL_PATH} ({len(metrics)} cells)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
