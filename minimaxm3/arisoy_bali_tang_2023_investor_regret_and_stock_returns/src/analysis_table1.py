"""
Table 1 — Univariate VW quintile portfolios sorted by REG (paper Arisoy, Bali, Tang 2023).

This is the headline replication table demonstrating that REG (investor regret)
predicts next-month excess returns, both as a raw spread and after risk
adjustment (alpha) under CAPM / FF3 / FFC / FF5 / FF6 factor models.

Procedure (per paper §5.1, footnotes 17, 18):
  - Sort month = month t in [June 1963, November 2020] (689 months).
  - Per month, compute NYSE-only (hexcd == 1) 20/40/60/80 percentiles of REG.
  - Assign each stock (NYSE or non-NYSE) to a quintile by whether its REG
    falls below/above the NYSE breakpoints.
  - Winsorize REG at 1%/99% within each month BEFORE the quintile sort.
  - Compute VW (me_lag1-weighted) excess returns for each quintile for
    month t+1 (i.e., the return month).
  - Time-series regression of each quintile's excess return on factors
    at month t+1 (the return month), Newey-West (1987) with 6 lags.

Computable factor models (per assumptions.md):
  CAPM, FF3, FFC (FF4 = Mkt-RF, SMB, HML, MOM), FF5 (+ RMW, CMA),
  FF6 (+ MOM). FFCPS, FF6PS (require LIQ), Q, Q+ (require q-factors)
  are dropped.

For audit major [M2], the script also extracts NW(6) standard errors
for each per-quintile alpha cell and records them in eval/metrics.json
as `*_SE` keys, plus `*_gap_se` = |paper - ours| / SE for each cell.

Output: results/table_1.md plus per-cell metrics dict for eval/metrics.json.
"""

from __future__ import annotations

from pathlib import Path
import json
import sys

REPO_ROOT = Path("/home/ra_alan_mike_share/rep-it-up")
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_hac

from utils.paths import paper_layout

SLUG = "arisoy_bali_tang_2023_investor_regret_and_stock_returns"
LAYOUT = paper_layout(SLUG)

# Factor model definitions (computable per assumptions.md).
# Each model lists which `_ret` (return-month) factor columns to use.
FACTOR_MODELS = {
    "CAPM": ["ff_mkt_rf_ret"],
    "FF3":  ["ff_mkt_rf_ret", "ff_smb_ret", "ff_hml_ret"],
    "FFC":  ["ff_mkt_rf_ret", "ff_smb_ret", "ff_hml_ret", "ff_mom_ret"],
    "FF5":  ["ff_mkt_rf_ret", "ff_smb_ret", "ff_hml_ret", "ff_rmw_ret", "ff_cma_ret"],
    "FF6":  ["ff_mkt_rf_ret", "ff_smb_ret", "ff_hml_ret", "ff_rmw_ret", "ff_cma_ret", "ff_mom_ret"],
}

# Paper Table 1 metric values (cell -> paper number). For reference only;
# we don't enforce tolerance in this module — the scorer does.
PAPER_VALUES = {
    # Quintile mean REG (in percent, post-winsorization expected ~mean)
    "Q1_REG": 1.53, "Q2_REG": 10.13, "Q3_REG": 18.04,
    "Q4_REG": 28.73, "Q5_REG": 71.68,
    # Mean excess return per quintile (%/month)
    "Q1_Mean": 0.35, "Q2_Mean": 0.42, "Q3_Mean": 0.56,
    "Q4_Mean": 0.71, "Q5_Mean": 0.75,
    # CAPM alpha
    "Q1_CAPM": -0.17, "Q2_CAPM": -0.05, "Q3_CAPM": 0.03,
    "Q4_CAPM": 0.12, "Q5_CAPM": 0.12,
    # FF3 alpha
    "Q1_FF3": -0.22, "Q2_FF3": -0.10, "Q3_FF3": -0.02,
    "Q4_FF3": 0.09, "Q5_FF3": 0.17,
    # FFC alpha
    "Q1_FFC": -0.22, "Q2_FFC": -0.10, "Q3_FFC": -0.04,
    "Q4_FFC": 0.08, "Q5_FFC": 0.20,
    # FF5 alpha
    "Q1_FF5": -0.33, "Q2_FF5": -0.19, "Q3_FF5": -0.14,
    "Q4_FF5": 0.04, "Q5_FF5": 0.27,
    # FF6 alpha
    "Q1_FF6": -0.31, "Q2_FF6": -0.18, "Q3_FF6": -0.14,
    "Q4_FF6": 0.03, "Q5_FF6": 0.29,
    # High-Low
    "HL_REG": 70.14, "HL_Mean": 0.40, "HL_CAPM": 0.29, "HL_FF3": 0.39,
    "HL_FFC": 0.41, "HL_FF5": 0.60, "HL_FF6": 0.60,
    # NW t-stats for High-Low row
    "HL_Mean_t": 3.66, "HL_CAPM_t": 4.10, "HL_FF3_t": 3.79,
    "HL_FFC_t": 6.52, "HL_FF5_t": 5.67, "HL_FF6_t": 4.95,
}


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _attach_lead_factors(panel: pd.DataFrame, ff: pd.DataFrame) -> pd.DataFrame:
    """
    The panel has FF factors attached at the SORT month (t).
    For alpha regressions, the portfolio return at month t+1 should be
    regressed on factors at month t+1 (the return month).
    """
    ff_lead = ff.copy()
    ff_lead["join_month"] = (pd.to_datetime(ff_lead["month"]) - pd.DateOffset(months=1)).dt.strftime("%Y-%m-%d")
    ff_lead = ff_lead.drop(columns=["month"]).rename(columns={
        "ff_mkt_rf": "ff_mkt_rf_ret",
        "ff_smb": "ff_smb_ret",
        "ff_hml": "ff_hml_ret",
        "ff_mom": "ff_mom_ret",
        "ff_rmw": "ff_rmw_ret",
        "ff_cma": "ff_cma_ret",
        "ff_rf": "ff_rf_ret",
    })

    panel = panel.copy()
    panel["join_month"] = pd.to_datetime(panel["month"]).dt.strftime("%Y-%m-%d")
    merged = panel.merge(ff_lead, on="join_month", how="left")
    merged = merged.drop(columns=["join_month"])
    return merged


def _winsorize_per_month(panel: pd.DataFrame, col: str, p: float = 0.01) -> pd.DataFrame:
    """Winsorize `col` cross-sectionally at the `p` and `1-p` percentiles per month."""
    panel = panel.copy()

    def _clip(g: pd.Series) -> pd.Series:
        lo, hi = g.quantile([p, 1 - p])
        return g.clip(lower=lo, upper=hi)

    panel[col] = panel.groupby("month")[col].transform(_clip)
    return panel


def _assign_nyse_quintiles(panel: pd.DataFrame, signal_col: str) -> pd.Series:
    """
    Assign quintile labels 1..5 based on NYSE-only (hexcd == 1) breakpoints.
    """
    df = panel[["month", "hexcd", signal_col]].copy()

    # NYSE breakpoints per month.
    nyse = df[df["hexcd"] == 1]
    bp = nyse.groupby("month")[signal_col].quantile([0.20, 0.40, 0.60, 0.80]).unstack()
    bp.columns = [f"bp_{c}" for c in [20, 40, 60, 80]]

    # Join breakpoints back.
    out = df[["month", signal_col]].join(bp, on="month")

    # Assign quintile: 1 if reg < bp20; 2 if bp20 <= reg < bp40; ...
    q = pd.Series(np.nan, index=out.index, dtype=float)
    q[out[signal_col] < out["bp_20"]] = 1
    q[(out[signal_col] >= out["bp_20"]) & (out[signal_col] < out["bp_40"])] = 2
    q[(out[signal_col] >= out["bp_40"]) & (out[signal_col] < out["bp_60"])] = 3
    q[(out[signal_col] >= out["bp_60"]) & (out[signal_col] < out["bp_80"])] = 4
    q[out[signal_col] >= out["bp_80"]] = 5
    return q


def _compute_vw_returns(panel: pd.DataFrame, q_col: str, ret_col: str = "ret_excess_lead1") -> pd.DataFrame:
    """
    Per (month, quintile), compute value-weighted average return weighted by me_lag1.
    Returns a DataFrame with columns [month, q, vw, n_stocks].
    """
    grp = panel.groupby(["month", q_col])
    out = grp.apply(
        lambda g: pd.Series({
            "vw": (g[ret_col] * g["me_lag1"]).sum() / g["me_lag1"].sum(),
            "n_stocks": int(len(g)),
        }),
        include_groups=False,
    ).reset_index().rename(columns={q_col: "q"})
    return out


def _regress_alpha(
    port_ret: pd.Series,
    factor_rets: pd.DataFrame,
    n_lags: int = 6,
) -> tuple[float, float, float, int]:
    """
    Run OLS: port_ret = alpha + sum(beta_i * factor_i) + epsilon.
    Returns (alpha, nw_t_stat, nw_se, n_obs).
    """
    aligned = pd.concat([port_ret.rename("y"), factor_rets], axis=1, join="inner").dropna()
    if len(aligned) < 30:
        return (float("nan"), float("nan"), float("nan"), int(len(aligned)))
    y = aligned["y"].astype(float)
    X = sm.add_constant(aligned[factor_rets.columns].astype(float))
    res = sm.OLS(y, X).fit()
    alpha = float(res.params["const"])
    try:
        cov = cov_hac(res, nlags=n_lags)
        se = float(np.sqrt(cov[0, 0]))
    except Exception:
        se = float(res.bse["const"])
    t = alpha / se if se > 0 else float("nan")
    return (alpha, t, se, int(res.nobs))


def _tstat_to_se(port_ret: pd.Series, n_lags: int = 6) -> float:
    """Compute Newey-West SE on the mean of `port_ret` (no factor model).
    Used for the Mean column t-stats.
    """
    from utils.metrics import tstat_newey_west
    res = tstat_newey_west(port_ret, n_lags=n_lags)
    t = res["t_stat"]
    # SE = mean / t (signed; we want abs SE)
    m = port_ret.mean()
    se = abs(m / t) if t != 0 else float("nan")
    return float(se)


# ----------------------------------------------------------------------
# Main analysis
# ----------------------------------------------------------------------


def run_table_1() -> dict:
    print("=" * 72)
    print("Table 1 — Univariate VW quintile portfolios sorted by REG")
    print("=" * 72)

    panel = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
    ff = pd.read_parquet(LAYOUT.data_path("ff_factors.parquet"))

    print(f"Loaded panel: {panel.shape[0]:,} rows x {panel.shape[1]} cols")
    print(f"Loaded ff factors: {ff.shape[0]:,} months")

    # 1) Attach FF factors at the return (lead) month, not the sort month.
    print("\n[1] Attaching FF factors at the return month (t+1)...")
    panel = _attach_lead_factors(panel, ff)
    print(f"      panel.ff_mkt_rf_ret coverage: "
          f"{panel['ff_mkt_rf_ret'].notna().mean():.4f}")

    # 2) Winsorize REG at 1%/99% per month.
    print("\n[2] Winsorizing REG at 1%/99% per month...")
    reg_before = panel["reg"].describe()
    panel = _winsorize_per_month(panel, "reg", p=0.01)
    reg_after = panel["reg"].describe()
    print(f"      REG before: mean={reg_before['mean']:.4f}, "
          f"p99={reg_before['max']:.4f}")
    print(f"      REG after : mean={reg_after['mean']:.4f}, "
          f"p99={reg_after['max']:.4f}")

    # 3) Assign quintiles using NYSE breakpoints.
    print("\n[3] Assigning quintiles using NYSE-only breakpoints...")
    panel["q"] = _assign_nyse_quintiles(panel, "reg")
    q_counts = panel.groupby("month")["q"].value_counts().unstack(fill_value=0)
    print(f"      per-month q counts (mean over months):")
    for q in [1, 2, 3, 4, 5]:
        n = q_counts[q].mean() if q in q_counts.columns else 0
        print(f"        q={q}: mean={n:.1f}, "
              f"min={q_counts[q].min() if q in q_counts.columns else 'NA'}, "
              f"max={q_counts[q].max() if q in q_counts.columns else 'NA'}")

    avg_per_q = q_counts.mean().mean()
    print(f"      avg stocks per quintile per month: {avg_per_q:.0f}")

    # 4) Compute VW excess returns per quintile.
    print("\n[4] Computing VW excess returns per (month, quintile)...")
    bin_rets = _compute_vw_returns(panel, "q", "ret_excess_lead1")
    pivot = bin_rets.pivot(index="month", columns="q", values="vw")
    print(f"      bin returns matrix: {pivot.shape[0]} months x {pivot.shape[1]} quintiles")
    print(f"      mean VW excess returns (%/month):")
    for q in [1, 2, 3, 4, 5]:
        print(f"        q={q}: {pivot[q].mean() * 100:.4f}%")

    # 5) Compute HL spread (q5 - q1).
    hl = pivot[5] - pivot[1]
    print(f"      HL (5-1) VW excess return: {hl.mean() * 100:.4f}%/month")
    print(f"      HL non-null months: {hl.notna().sum()}")

    # 6) Compute alphas per factor model.
    print("\n[5] Computing factor-model alphas (NW-6 t-stats)...")
    factor_cols_map = FACTOR_MODELS

    # Build a factor returns DataFrame aligned to month (sort month t).
    all_fac_cols = sorted({c for cs in factor_cols_map.values() for c in cs})
    ff_ret_month = (
        panel[["month"] + all_fac_cols]
        .drop_duplicates("month")
        .set_index("month")
        .sort_index()
    )

    metrics: dict[str, dict] = {}
    alphas: dict[str, dict[int, float]] = {m: {} for m in factor_cols_map}
    tstats: dict[str, dict[int, float]] = {m: {} for m in factor_cols_map}
    ses: dict[str, dict[int, float]] = {m: {} for m in factor_cols_map}

    for model_name, fac_cols in factor_cols_map.items():
        print(f"\n  {model_name} ({len(fac_cols)} factors):")
        factor_df = ff_ret_month[fac_cols]
        for q in [1, 2, 3, 4, 5]:
            port_ret = pivot[q].dropna()
            alpha, t, se, n = _regress_alpha(port_ret, factor_df, n_lags=6)
            alphas[model_name][q] = alpha
            tstats[model_name][q] = t
            ses[model_name][q] = se
            print(f"    q={q}: alpha={alpha*100:.4f}%  t={t:.3f}  SE={se*100:.4f}%  n={n}")

        # HL row (5 - 1) for this model
        port_ret_hl = hl.dropna()
        alpha_hl, t_hl, se_hl, n_hl = _regress_alpha(port_ret_hl, factor_df, n_lags=6)
        alphas[model_name]["HL"] = alpha_hl
        tstats[model_name]["HL"] = t_hl
        ses[model_name]["HL"] = se_hl
        print(f"    HL:  alpha={alpha_hl*100:.4f}%  t={t_hl:.3f}  SE={se_hl*100:.4f}%  n={n_hl}")

    # Also compute raw Mean excess return NW t-stat (the "Mean" column).
    mean_per_q = {q: pivot[q].mean() for q in [1, 2, 3, 4, 5]}
    mean_hl = (pivot[5] - pivot[1]).mean()
    from utils.metrics import tstat_newey_west
    t_mean_per_q = {q: tstat_newey_west(pivot[q].dropna(), n_lags=6)["t_stat"] for q in [1, 2, 3, 4, 5]}
    t_mean_hl = tstat_newey_west((pivot[5] - pivot[1]).dropna(), n_lags=6)["t_stat"]
    # SE for Mean column = |mean / t_stat|
    se_mean_per_q = {q: abs(mean_per_q[q] / t_mean_per_q[q]) if t_mean_per_q[q] != 0 else float("nan")
                     for q in [1, 2, 3, 4, 5]}
    se_mean_hl = abs(mean_hl / t_mean_hl) if t_mean_hl != 0 else float("nan")

    # Mean REG per quintile (in percent).
    reg_per_q = {q: panel.loc[panel["q"] == q, "reg"].mean() * 100 for q in [1, 2, 3, 4, 5]}
    reg_hl = reg_per_q[5] - reg_per_q[1]

    # 7) Build the metrics dict.
    for q in [1, 2, 3, 4, 5]:
        metrics[f"Q{q}_REG"] = {"value": float(reg_per_q[q]), "unit": "percent"}
        metrics[f"Q{q}_Mean"] = {"value": float(mean_per_q[q] * 100), "unit": "percent_per_month"}
        metrics[f"Q{q}_Mean_SE"] = {"value": float(se_mean_per_q[q] * 100), "unit": "percent_per_month"}
        for m in factor_cols_map:
            metrics[f"Q{q}_{m}"] = {"value": float(alphas[m][q] * 100), "unit": "percent_per_month"}
            metrics[f"Q{q}_{m}_SE"] = {"value": float(ses[m][q] * 100), "unit": "percent_per_month"}
        metrics[f"Q{q}_Mean_t"] = {"value": float(t_mean_per_q[q]), "unit": "t_stat"}

    metrics["HL_REG"] = {"value": float(reg_hl), "unit": "percent"}
    metrics["HL_Mean"] = {"value": float(mean_hl * 100), "unit": "percent_per_month"}
    metrics["HL_Mean_SE"] = {"value": float(se_mean_hl * 100), "unit": "percent_per_month"}
    for m in factor_cols_map:
        metrics[f"HL_{m}"] = {"value": float(alphas[m]["HL"] * 100), "unit": "percent_per_month"}
        metrics[f"HL_{m}_SE"] = {"value": float(ses[m]["HL"] * 100), "unit": "percent_per_month"}
        metrics[f"HL_{m}_t"] = {"value": float(tstats[m]["HL"]), "unit": "t_stat"}
    metrics["HL_Mean_t"] = {"value": float(t_mean_hl), "unit": "t_stat"}

    # 7b) Add gap/SE metrics (audit major M2).
    # For each per-quintile alpha cell, |paper - ours| / SE records whether
    # the gap is within sampling noise (|gap/SE| < 3) or structural (> 3).
    def _gap_se(ours_pct: float, paper: float, se_pct: float) -> float:
        if se_pct is None or se_pct == 0 or np.isnan(se_pct):
            return float("nan")
        gap = abs(ours_pct - paper)
        return float(gap / abs(se_pct))

    for q in [1, 2, 3, 4, 5]:
        if f"Q{q}_Mean" in PAPER_VALUES and f"Q{q}_Mean" in metrics:
            metrics[f"Q{q}_Mean_gap_se"] = {
                "value": _gap_se(metrics[f"Q{q}_Mean"]["value"], PAPER_VALUES[f"Q{q}_Mean"],
                                  metrics[f"Q{q}_Mean_SE"]["value"]),
                "unit": "ratio",
            }
        for m in factor_cols_map:
            paper_key = f"Q{q}_{m}"
            if paper_key in PAPER_VALUES:
                metrics[f"{paper_key}_gap_se"] = {
                    "value": _gap_se(metrics[paper_key]["value"], PAPER_VALUES[paper_key],
                                      metrics[f"{paper_key}_SE"]["value"]),
                    "unit": "ratio",
                }

    # HL gap/SE
    if "HL_Mean" in PAPER_VALUES:
        metrics["HL_Mean_gap_se"] = {
            "value": _gap_se(metrics["HL_Mean"]["value"], PAPER_VALUES["HL_Mean"],
                              metrics["HL_Mean_SE"]["value"]),
            "unit": "ratio",
        }
    for m in factor_cols_map:
        paper_key = f"HL_{m}"
        if paper_key in PAPER_VALUES:
            metrics[f"{paper_key}_gap_se"] = {
                "value": _gap_se(metrics[paper_key]["value"], PAPER_VALUES[paper_key],
                                  metrics[f"{paper_key}_SE"]["value"]),
                "unit": "ratio",
            }

    # 8) Format and write the table to results/table_1.md.
    print("\n[6] Writing results/table_1.md ...")
    table_md = _format_table_md(
        reg_per_q=reg_per_q,
        mean_per_q={k: v * 100 for k, v in mean_per_q.items()},
        se_mean_per_q={k: v * 100 for k, v in se_mean_per_q.items()},
        t_mean_per_q=t_mean_per_q,
        alphas=alphas,
        tstats=tstats,
        ses={m: {q: ses[m][q] * 100 for q in ses[m]} for m in ses},
        mean_hl=mean_hl * 100,
        se_mean_hl=se_mean_hl * 100,
        t_mean_hl=t_mean_hl,
        reg_hl=reg_hl,
        hl_alphas={m: alphas[m]["HL"] * 100 for m in factor_cols_map},
        hl_ses={m: ses[m]["HL"] * 100 for m in ses},
        hl_tstats={m: tstats[m]["HL"] for m in factor_cols_map},
    )
    LAYOUT.result_path("table_1.md").parent.mkdir(parents=True, exist_ok=True)
    LAYOUT.result_path("table_1.md").write_text(table_md)
    print(f"      Wrote {LAYOUT.result_path('table_1.md')}")

    # 9) Print summary and paper comparisons.
    print("\n[7] Sanity checks & paper comparisons:")
    print(f"      HL_Mean = {mean_hl * 100:.4f}% (paper: 0.40%, expected ~0.4)")
    print(f"      HL_Mean_t = {t_mean_hl:.3f} (paper: 3.66, expected in [2, 6])")
    print(f"      HL_FF3   = {alphas['FF3']['HL'] * 100:.4f}% (paper: 0.39%, expected ~0.4)")
    print(f"      HL_FF5   = {alphas['FF5']['HL'] * 100:.4f}% (paper: 0.60%)")
    print(f"      HL_FF6   = {alphas['FF6']['HL'] * 100:.4f}% (paper: 0.60%)")

    # Flag any cells that diverge from paper by more than 50%.
    print("\n[8] Cell-level paper comparison (>50% divergence flagged):")
    flagged = []
    for cell, paper_val in PAPER_VALUES.items():
        if cell in metrics:
            ours = metrics[cell]["value"]
            if paper_val != 0:
                pct = abs(ours - paper_val) / abs(paper_val) * 100
            else:
                pct = float("inf") if ours != 0 else 0
            mark = " <-- DIVERGENCE" if pct > 50 else ""
            if pct > 50:
                flagged.append((cell, paper_val, ours, pct))
            print(f"      {cell:<15}  ours={ours:>10.4f}  paper={paper_val:>10.4f}  "
                  f"diff={pct:>6.1f}%{mark}")

    if flagged:
        print(f"\n      Flagged {len(flagged)} cells with >50% divergence.")

    return metrics


def _format_table_md(
    reg_per_q: dict,
    mean_per_q: dict,
    se_mean_per_q: dict,
    t_mean_per_q: dict,
    alphas: dict,
    tstats: dict,
    ses: dict,
    mean_hl: float,
    se_mean_hl: float,
    t_mean_hl: float,
    reg_hl: float,
    hl_alphas: dict,
    hl_ses: dict,
    hl_tstats: dict,
) -> str:
    """
    Format Table 1 as markdown. Each cell shows the alpha in %/month with
    the NW t-stat in brackets below it.
    """
    models = ["CAPM", "FF3", "FFC", "FF5", "FF6"]

    def _cell(val: float, t: float | None = None) -> str:
        s = f"{val:.2f}"
        if t is not None:
            s += f"<br>[{t:.2f}]"
        return s

    lines = []
    lines.append("# Table 1 — Univariate VW quintile portfolios sorted by REG")
    lines.append("")
    lines.append("Sample: NYSE/AMEX/NASDAQ common stocks (shrcd 10,11), $5–$1000 price screen.")
    lines.append("Sort: each month from 1963-07 to 2020-11, NYSE-only 20/40/60/80 percentiles of REG.")
    lines.append("REG winsorized cross-sectionally at 1%/99% per month before sort.")
    lines.append("Returns: next-month VW (me_lag1-weighted) excess returns. T = 689 months.")
    lines.append("Alphas: time-series regressions with Newey-West (1987), 6 lags. Units: %/month.")
    lines.append("")
    lines.append("Note: FFCPS, FF6PS, Q, Q+ models dropped (LIQ + q-factors not in ClickHouse).")
    lines.append("")
    header = "| Quintile | REG (%) | Mean | " + " | ".join(models) + " |"
    sep = "|---|" + "|".join(["---"] * (3 + len(models))) + "|"
    lines.append(header)
    lines.append(sep)

    for q in [1, 2, 3, 4, 5]:
        row = [f"Q{q}", f"{reg_per_q[q]:.2f}"]
        row.append(_cell(mean_per_q[q], t_mean_per_q[q]))
        for m in models:
            row.append(_cell(alphas[m][q] * 100, tstats[m][q]))
        lines.append("| " + " | ".join(row) + " |")

    hl_row = ["HL (5-1)", f"{reg_hl:.2f}", _cell(mean_hl, t_mean_hl)]
    for m in models:
        hl_row.append(_cell(hl_alphas[m], hl_tstats[m]))
    lines.append("| " + " | ".join(hl_row) + " |")

    lines.append("")
    lines.append("Each cell: alpha (%/month) with NW(6) t-stat in brackets.")
    lines.append("")

    # ---- Side-by-side comparison with paper ----
    lines.append("## Comparison with paper Table 1")
    lines.append("")
    lines.append("Ours vs paper for each cell. Format: ours vs paper.")
    lines.append("")
    cmp_lines = ["| Cell | Ours | Paper | Diff (%) |",
                  "|---|---|---|---|"]
    cmp_pairs = [
        ("Q1_REG", reg_per_q[1], PAPER_VALUES["Q1_REG"], "percent"),
        ("Q2_REG", reg_per_q[2], PAPER_VALUES["Q2_REG"], "percent"),
        ("Q3_REG", reg_per_q[3], PAPER_VALUES["Q3_REG"], "percent"),
        ("Q4_REG", reg_per_q[4], PAPER_VALUES["Q4_REG"], "percent"),
        ("Q5_REG", reg_per_q[5], PAPER_VALUES["Q5_REG"], "percent"),
        ("Q1_Mean", mean_per_q[1], PAPER_VALUES["Q1_Mean"], "%/mo"),
        ("Q2_Mean", mean_per_q[2], PAPER_VALUES["Q2_Mean"], "%/mo"),
        ("Q3_Mean", mean_per_q[3], PAPER_VALUES["Q3_Mean"], "%/mo"),
        ("Q4_Mean", mean_per_q[4], PAPER_VALUES["Q4_Mean"], "%/mo"),
        ("Q5_Mean", mean_per_q[5], PAPER_VALUES["Q5_Mean"], "%/mo"),
        ("HL_REG", reg_hl, PAPER_VALUES["HL_REG"], "percent"),
        ("HL_Mean", mean_hl, PAPER_VALUES["HL_Mean"], "%/mo"),
    ]
    for m in models:
        cmp_pairs.append((f"Q1_{m}", alphas[m][1] * 100, PAPER_VALUES[f"Q1_{m}"], "%/mo"))
        cmp_pairs.append((f"Q2_{m}", alphas[m][2] * 100, PAPER_VALUES[f"Q2_{m}"], "%/mo"))
        cmp_pairs.append((f"Q3_{m}", alphas[m][3] * 100, PAPER_VALUES[f"Q3_{m}"], "%/mo"))
        cmp_pairs.append((f"Q4_{m}", alphas[m][4] * 100, PAPER_VALUES[f"Q4_{m}"], "%/mo"))
        cmp_pairs.append((f"Q5_{m}", alphas[m][5] * 100, PAPER_VALUES[f"Q5_{m}"], "%/mo"))
        cmp_pairs.append((f"HL_{m}", hl_alphas[m], PAPER_VALUES[f"HL_{m}"], "%/mo"))
        cmp_pairs.append((f"HL_{m}_t", hl_tstats[m], PAPER_VALUES[f"HL_{m}_t"], "t"))
    cmp_pairs.append(("HL_Mean_t", t_mean_hl, PAPER_VALUES["HL_Mean_t"], "t"))

    for cell, ours, paper, unit in cmp_pairs:
        if paper != 0:
            diff = abs(ours - paper) / abs(paper) * 100
            diff_str = f"{diff:.1f}%"
        else:
            diff_str = "n/a"
        flag = "  **DIVERGENCE**" if paper != 0 and abs(ours - paper) / abs(paper) > 0.5 else ""
        cmp_lines.append(
            f"| {cell} | {ours:.4f} ({unit}) | {paper:.4f} ({unit}) | {diff_str}{flag} |"
        )
    lines.extend(cmp_lines)
    lines.append("")

    # ---- Audit major M2: per-cell SE and |gap/SE| columns ----
    lines.append("## M2 — Per-cell NW(6) standard errors and gap significance")
    lines.append("")
    lines.append("For each per-quintile alpha cell, the NW(6) SE = |alpha / t-stat| and")
    lines.append("the |gap/SE| = |paper - ours| / SE. A |gap/SE| < 3 means the gap is")
    lines.append("consistent with sampling noise; |gap/SE| > 3 marks a structural mismatch.")
    lines.append("")
    lines.append("| Cell | Ours (%/mo) | Paper (%/mo) | SE (%/mo) | |gap/SE| | Note |")
    lines.append("|---|---:|---:|---:|---:|---|")

    # Use a fresh list to avoid mixing with cmp_lines.
    m2_lines: list[str] = []

    # Mean column entries (per-quintile + HL)
    for q in [1, 2, 3, 4, 5]:
        key = f"Q{q}_Mean"
        gap_se = abs(mean_per_q[q] - PAPER_VALUES[key]) / se_mean_per_q[q] \
            if se_mean_per_q[q] != 0 else float("nan")
        note = "within noise" if gap_se < 3 else "STRUCTURAL"
        m2_lines.append(
            f"| {key} | {mean_per_q[q]:.4f} | {PAPER_VALUES[key]:.4f} | "
            f"{se_mean_per_q[q]:.4f} | {gap_se:.2f} | {note} |"
        )
    gap_se_hl = abs(mean_hl - PAPER_VALUES["HL_Mean"]) / se_mean_hl \
        if se_mean_hl != 0 else float("nan")
    note = "within noise" if gap_se_hl < 3 else "STRUCTURAL"
    m2_lines.append(
        f"| HL_Mean | {mean_hl:.4f} | {PAPER_VALUES['HL_Mean']:.4f} | "
        f"{se_mean_hl:.4f} | {gap_se_hl:.2f} | {note} |"
    )

    for m in models:
        for q in [1, 2, 3, 4, 5]:
            key = f"Q{q}_{m}"
            se_v = ses[m].get(q, float("nan"))
            gap_se = abs(alphas[m][q] * 100 - PAPER_VALUES[key]) / se_v \
                if se_v and se_v != 0 else float("nan")
            note = "within noise" if gap_se < 3 else "STRUCTURAL"
            m2_lines.append(
                f"| {key} | {alphas[m][q] * 100:.4f} | {PAPER_VALUES[key]:.4f} | "
                f"{se_v:.4f} | {gap_se:.2f} | {note} |"
            )
        key_hl = f"HL_{m}"
        se_hl = ses[m].get("HL", float("nan"))
        gap_se_hl = abs(hl_alphas[m] - PAPER_VALUES[key_hl]) / se_hl \
            if se_hl and se_hl != 0 else float("nan")
        note = "within noise" if gap_se_hl < 3 else "STRUCTURAL"
        m2_lines.append(
            f"| {key_hl} | {hl_alphas[m]:.4f} | {PAPER_VALUES[key_hl]:.4f} | "
            f"{se_hl:.4f} | {gap_se_hl:.2f} | {note} |"
        )

    lines.extend(m2_lines)
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    metrics = run_table_1()
    eval_path = LAYOUT.eval_path("metrics.json")
    eval_path.parent.mkdir(parents=True, exist_ok=True)
    if eval_path.exists():
        existing = json.loads(eval_path.read_text())
        existing_metrics = existing.get("metrics", {})
    else:
        existing = {"schema_version": 2, "slug": SLUG, "metrics": {}}
        existing_metrics = {}
    existing_metrics.update(metrics)
    existing["metrics"] = existing_metrics
    eval_path.write_text(json.dumps(existing, indent=2, default=float))
    print(f"\nUpdated {eval_path} with Table 1 metrics (incl. SE and gap/SE).")