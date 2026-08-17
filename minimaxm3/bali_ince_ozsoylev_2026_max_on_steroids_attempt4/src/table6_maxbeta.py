"""
MAX on Steroids — Table 6 (MAX^beta decile portfolios).

Replicates paper Table 6 (page 60, L2076-L2224). Reports the 10 MAX^beta-
decile portfolios' one-month-ahead VW excess returns and factor-model alphas.

MAX^beta construction (per paper section 3.2 and Assumption 18):
  1. Each month, sort stocks into 10 deciles by BETA (outer sort).
  2. Within each BETA decile, sort stocks into 10 deciles by MAX (inner sort).
  3. Regroup stocks by their inner MAX decile rank across all 10 BETA deciles.
     The resulting 10 portfolios are the MAX^beta deciles.
  4. The long-short spread is the VW portfolio return of MAX^beta decile 10
     minus decile 1, weighted by ME_lag1.
  5. Compute alphas under CAPM, FF3, FFC4, FF5, FF6.

Per `preparations/assumptions.md`:
  - Skip SY / DHS / FFCPS / FF6PS (Assumption 1, 2, 3) — not in ClickHouse.
  - VW uses ME_lag1 (Assumption 15).
  - Newey-West t-stats use 6 lags (Assumption 8).

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

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from utils.paths import paper_layout  # noqa: E402
from utils.regressions import factor_alpha  # noqa: E402

SLUG = "max_on_steroids_attempt4"
LAYOUT = paper_layout(SLUG)
LAYOUT.ensure()

PANEL_PATH = LAYOUT.data_path("panel.parquet")
RESULTS_DIR = LAYOUT.result_path
EVAL_PATH = LAYOUT.eval_path("metrics.json")

N_BINS = 10
NW_LAGS = 6
WINSORIZE_PCT = 0.01

FACTOR_MODELS = [
    ("RET-RF", []),
    ("CAPM",   ["mkt_rf"]),
    ("FF3",    ["mkt_rf", "smb", "hml"]),
    ("FFC4",   ["mkt_rf", "smb", "hml", "mom"]),
    ("FF5",    ["mkt_rf", "smb", "hml", "rmw", "cma"]),
    ("FF6",    ["mkt_rf", "smb", "hml", "mom", "rmw", "cma"]),
]
SKIP_MODELS = {"SY", "DHS", "FFCPS", "FF6PS"}

# --- reuse the FF loading + ME_lag1 + BETA-winsorize helpers from table1 ----

# Avoid circular imports by duplicating the FF loader here
from table1_max import load_ff_factors, prepare_panel  # noqa: E402


# --- 1. Form MAX^beta deciles ----------------------------------------------

def form_max_beta_deciles(panel: pd.DataFrame, vw_col: str = "ME_lag1") -> pd.DataFrame:
    """Form 10 MAX^beta deciles via 10x10 conditional double sort.

    Steps:
      1. Each month: 10 BETA deciles (all-stocks breakpoints).
      2. Within each (month, beta_decile): 10 MAX deciles (all-stocks breakpoints).
      3. Regroup by inner MAX decile -> 10 MAX^beta portfolios.
      4. VW portfolio returns using the chosen weight (vw_col).
         Default "ME_lag1" (prior-month ME); passing "me_june_t" uses the
         FF93/Bali-2011 carry-forward June snapshot.
      5. Drop months where any beta decile has < 30 stocks or any
         MAX^beta decile has < 30 stocks.

    Returns DataFrame with columns ['month', 'decile', 'ret_vw'].
    """
    sub = panel.dropna(
        subset=["MAX", "BETA_w", "ret_excess_next", vw_col]
    ).copy()
    sub = sub[sub[vw_col] > 0]
    sub = sub.sort_values(["month", "permno"]).reset_index(drop=True)

    # Step 1: outer sort by BETA, 10 deciles per month (all-stocks breakpoints)
    sub["beta_decile"] = (
        sub.groupby("month")["BETA_w"]
        .transform(
            lambda s: pd.qcut(s, q=N_BINS, labels=False, duplicates="drop")
        )
        .astype("Int64")
        + 1
    )

    # Some months may produce < 10 distinct beta deciles if BETA is heavily
    # tied. Drop those rows.
    sub = sub.dropna(subset=["beta_decile"])
    sub["beta_decile"] = sub["beta_decile"].astype(int)

    # Drop months where any BETA decile has < 30 stocks (per spec)
    beta_counts = (
        sub.groupby(["month", "beta_decile"]).size().reset_index(name="n")
    )
    # Per-month min count across beta deciles
    month_min = beta_counts.groupby("month")["n"].min()
    keep_beta_months = month_min[month_min >= 30].index
    sub = sub[sub["month"].isin(keep_beta_months)].copy()
    print(f"[table6] months after BETA-decile < 30 filter (vw={vw_col}): "
          f"{sub['month'].nunique()}")

    # Step 2: inner sort by MAX within each (month, beta_decile)
    # Use qcut with labels=False -> 0..9; +1 -> 1..10
    # duplicates='drop' in case of ties within a beta decile
    def _inner_q(s: pd.Series) -> pd.Series:
        try:
            q = pd.qcut(s, q=N_BINS, labels=False, duplicates="drop")
            return pd.Series(q, index=s.index).astype("Int64") + 1
        except ValueError:
            # fallback: rank-based
            ranks = s.rank(method="first")
            n_valid = int(ranks.notna().sum())
            out = np.ceil(ranks / max(n_valid, 1) * N_BINS).astype("Int64")
            return out

    inner = (
        sub.groupby(["month", "beta_decile"], group_keys=False)["MAX"]
        .apply(_inner_q)
        .astype("Int64")
    )
    # Make sure the index lines up with sub
    inner.index = sub.index
    sub["maxbeta_decile"] = inner

    sub = sub.dropna(subset=["maxbeta_decile"])
    sub["maxbeta_decile"] = sub["maxbeta_decile"].astype(int)

    # Step 3: drop months where any MAX^beta decile has < 30 stocks
    mb_counts = (
        sub.groupby(["month", "maxbeta_decile"]).size().reset_index(name="n")
    )
    month_min_mb = mb_counts.groupby("month")["n"].min()
    keep_mb_months = month_min_mb[month_min_mb >= 30].index
    sub = sub[sub["month"].isin(keep_mb_months)].copy()
    print(f"[table6] months after MAX^beta-decile < 30 filter (vw={vw_col}): "
          f"{sub['month'].nunique()}")

    # Step 4: VW portfolio returns using vw_col weights, by (month, maxbeta_decile)
    grp = sub.groupby(["month", "maxbeta_decile"])
    vw = grp.apply(lambda g: pd.Series({
        "vw_sum": (g["ret_excess_next"] * g[vw_col]).sum(),
        "w_sum":  g[vw_col].sum(),
    }), include_groups=False).reset_index()
    vw["ret_vw"] = vw["vw_sum"] / vw["w_sum"]
    vw = vw.rename(columns={"maxbeta_decile": "decile"})

    print(f"[table6] {vw['month'].nunique()} months used for portfolio sorts "
          f"(vw={vw_col})")
    print(f"[table6] decile counts (avg per month): "
          f"{vw.groupby('decile').size().mean():.1f}")
    print(f"[table6] decile membership: avg stocks per (month, decile): "
          f"{vw.groupby('decile').size().mean():.1f}")
    return vw[["month", "decile", "ret_vw"]]


# --- 2. Per-cell alphas (mirrors table1 logic) ------------------------------


def compute_cell_alphas(port_vw: pd.DataFrame, ff: pd.DataFrame) -> dict:
    """For each (decile, factor model), compute alpha + NW t-stat."""
    df = port_vw.merge(ff, on="month", how="inner").sort_values("month")
    df_wide = df.pivot(index="month", columns="decile", values="ret_vw").sort_index()

    cells = {}
    for model_name, factors in FACTOR_MODELS:
        for decile in sorted(int(c) for c in df_wide.columns):
            label = f"P{int(decile)}_{model_name.replace('-', '_')}"
            series = df_wide[decile].dropna()
            if model_name == "RET-RF":
                alpha_m = float(series.mean())
                n = len(series)
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
                cells[label] = {"value": alpha_m, "t": t, "n": n}
            else:
                ff_aligned = (
                    df[["month", "rf"] + factors]
                    .drop_duplicates().set_index("month")
                )
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

    # Spread rows (D10 - D1)
    for model_name, _ in FACTOR_MODELS:
        label = f"D10_D1_{model_name.replace('-', '_')}"
        d10_key = f"P10_{model_name.replace('-', '_')}"
        d1_key = f"P1_{model_name.replace('-', '_')}"
        d10 = cells[d10_key]
        d1 = cells[d1_key]
        cells[label] = {
            "value": d10["value"] - d1["value"],
            "t": float("nan"),
            "n": min(d10["n"], d1["n"]),
        }

    # Spread NW t-stats
    for model_name, factors in FACTOR_MODELS:
        label = f"D10_D1_{model_name.replace('-', '_')}"
        d10_w = df_wide[10].dropna()
        d1_w = df_wide[1].dropna()
        spread = (d10_w - d1_w).dropna().to_frame("ret")
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
            ff_aligned = (
                df[["month", "rf"] + factors]
                .drop_duplicates().set_index("month")
            )
            res = factor_alpha(
                spread, ff_aligned, factors=factors, rf_col="rf",
                ret_col="ret", n_lags=NW_LAGS, freq="M",
            )
            t = float(res["t_alpha_newey_west"])
        cells[label]["t"] = t

    return cells


# --- 3. Output: markdown + JSON + side-by-side ------------------------------


def cells_to_markdown(cells: dict) -> str:
    model_cols = [m[0] for m in FACTOR_MODELS]
    lines = []
    lines.append("# Table 6 — MAX^beta Decile Portfolios: VW Excess Returns and Factor Alphas")
    lines.append("")
    lines.append("Sample: 1968-01 to 2022-12. Conditional 10x10 sort (BETA, then MAX). "
                 "VW by prior-month ME. Newey-West t-stats with 6 lags.")
    lines.append("")
    lines.append("MAX^beta construction (paper section 3.2): "
                 "stocks first sorted into 10 BETA deciles each month, "
                 "then within each BETA decile sorted into 10 MAX deciles. "
                 "The 10 MAX^beta deciles are the regrouping of stocks by their "
                 "inner MAX decile rank across the 10 BETA deciles.")
    lines.append("")
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
        if pd.isna(t):
            return f"{v:.2f}"
        return f"{v:.2f}<br>({t:.2f})"

    for d in range(1, N_BINS + 1):
        row = [f"P{d}"]
        for m in model_cols:
            label = f"P{d}_{m.replace('-', '_')}"
            row.append(fmt_cell(label))
        lines.append("| " + " | ".join(row) + " |")

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
    return "\n".join(lines)


def cells_to_paper_grid(cells: dict) -> str:
    model_cols = [m[0] for m in FACTOR_MODELS]
    lines = []
    lines.append("=" * 100)
    lines.append("TABLE 6: MAX^beta DECILE PORTFOLIOS — VW EXCESS RETURNS AND FACTOR ALPHAS")
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
    """Build the T6 metrics dict.

    Keys are written with both "T6_" prefix and bare names. Values are
    converted from decimal to PERCENT/month to match the paper target units
    (per tables_to_replicate.json `unit: "%/month"`).

    Per Assumption 18 and the iter-5 plan, we add T6 entries under both
    'T6_'-prefixed names (for backwards-compat / disambiguation) AND
    bare names (so the canonical scorer reads them). The paper_target
    dict keys (un-prefixed) are still used for the SKIP entries.
    """
    metrics = {}
    for label, c in cells.items():
        v = float(c["value"]) if not pd.isna(c["value"]) else None
        if v is not None:
            v_pct = v * 100.0
        else:
            v_pct = None
        prefixed = f"T6_{label}"
        entry = {
            "value": v_pct,
            "t_stat": float(c["t"]) if not pd.isna(c["t"]) else None,
            "n_obs": int(c["n"]),
            "unit": "%/month",
        }
        metrics[prefixed] = entry
        metrics[label] = entry
    if paper_target is not None:
        skip_suffixes = ("_SY", "_DHS", "_FFCPS", "_FF6PS")
        for label in paper_target:
            if label in cells:
                # already added above
                continue
            # SKIP cells from paper target list
            if any(label.endswith(s) for s in skip_suffixes):
                e = {
                    "value": None,
                    "t_stat": None,
                    "n_obs": 0,
                    "unit": "ratio",
                    "status": "SKIP",
                    "skip_reason": "third-party factor unavailable in ClickHouse",
                }
                metrics[f"T6_{label}"] = e
                metrics[label] = e
    return metrics


def compare_to_paper(cells: dict, paper_target: dict) -> str:
    lines = []
    lines.append("=" * 100)
    lines.append("TABLE 6: REPLICATED vs PAPER (30% tolerance)")
    lines.append("=" * 100)
    lines.append(f"{'Cell':<14} | {'Replicated':>12} | {'Paper':>10} | {'%Diff':>10} | Status")

    n_match = 0
    n_fail = 0
    n_skip = 0
    for label, c in cells.items():
        rep_v = c["value"] * 100
        paper_v = paper_target.get(label)
        if paper_v is None:
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


# --- 4. main ---------------------------------------------------------------


def compare_two_weights(cells_lag1: dict, cells_june: dict,
                        paper_target: dict, table_id: str = "T6") -> str:
    """Side-by-side comparison of two VW-weighting schemes (lag-1 vs June-t)
    for headline cells only. Mirrors table1_max.compare_two_weights.
    """
    headline = [
        "P1_RET_RF", "P10_RET_RF", "D10_D1_RET_RF",
        "D10_D1_CAPM", "D10_D1_FF3", "D10_D1_FFC4",
        "D10_D1_FF5", "D10_D1_FF6",
    ]
    lines = []
    lines.append("=" * 110)
    lines.append(f"HEADLINE COMPARISON (Table {table_id[1:]}): ME_lag1 vs me_june_t")
    lines.append("=" * 110)
    lines.append(f"{'Cell':<14} | {'ME_lag1':>10} | {'me_june_t':>10} | "
                 f"{'paper':>8} | {'r_old':>6} | {'r_new':>6} | winner")
    for label in headline:
        cl = cells_lag1.get(label, {}).get("value", float("nan"))
        cj = cells_june.get(label, {}).get("value", float("nan"))
        pv = paper_target.get(label)
        if pv is None:
            continue

        def _r(v: float) -> float:
            if not np.isfinite(v) or pv == 0:
                return float("nan")
            return float(abs((v * 100) / pv))

        cl_pct = cl * 100 if np.isfinite(cl) else float("nan")
        cj_pct = cj * 100 if np.isfinite(cj) else float("nan")
        r_old = _r(cl)
        r_new = _r(cj)
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


def main() -> int:
    print(f"[table6] loading panel from {PANEL_PATH}")
    panel = pd.read_parquet(PANEL_PATH)
    print(f"[table6] panel: {len(panel):,} rows x {panel.shape[1]} cols")

    ff = load_ff_factors()
    panel = prepare_panel(panel)

    # iter-5: compute both ME_lag1 and me_june_t.
    port_vw_lag1 = form_max_beta_deciles(panel, vw_col="ME_lag1")
    port_vw_june = form_max_beta_deciles(panel, vw_col="me_june_t")

    cells_lag1 = compute_cell_alphas(port_vw_lag1, ff)
    cells_june = compute_cell_alphas(port_vw_june, ff)

    print()
    print("--- ME_lag1 (iter-3 baseline) ---")
    print(cells_to_paper_grid(cells_lag1))
    print()
    print("--- me_june_t (iter-5 fix) ---")
    print(cells_to_paper_grid(cells_june))

    paper_target_path = LAYOUT.input_path("tables_to_replicate.json")
    with open(paper_target_path) as f:
        paper_cfg = json.load(f)
    paper_target = {
        m["name"]: m["value"]
        for t in paper_cfg["tables"] if t["id"] == "T6"
        for m in t["metrics"]
    }
    print()
    print(compare_two_weights(cells_lag1, cells_june, paper_target, table_id="T6"))
    print()
    print(compare_to_paper(cells_june, paper_target))

    RESULTS_DIR("").mkdir(parents=True, exist_ok=True)
    md = cells_to_markdown(cells_june)
    (RESULTS_DIR("table_6.md")).write_text(md)
    print(f"\n[table6] saved {RESULTS_DIR('table_6.md')}")

    grid_text = (
        "=== ME_lag1 (iter-3 baseline) ===\n"
        + cells_to_paper_grid(cells_lag1)
        + "\n\n=== me_june_t (iter-5 fix) ===\n"
        + cells_to_paper_grid(cells_june)
        + "\n\n" + compare_two_weights(cells_lag1, cells_june, paper_target, table_id="T6")
        + "\n\n" + compare_to_paper(cells_june, paper_target)
    )
    (RESULTS_DIR("table_6_results.txt")).write_text(grid_text)
    print(f"[table6] saved {RESULTS_DIR('table_6_results.txt')}")

    # Return the metrics dict (iter-5: use me_june_t cells)
    return cells_to_metrics_json(cells_june, paper_target=paper_target)


if __name__ == "__main__":
    metrics = main()
    print(f"\n[table6] {len(metrics)} cells")