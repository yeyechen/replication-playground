"""
Table 3 — Dependent bivariate sorts (paper Arisoy, Bali, Tang 2023).

This is the cross-sectional robustness table: for each of 12 control
variables, we form quintiles by the control variable (NYSE breakpoints),
then within each control quintile form quintiles by REG (NYSE breakpoints
within the control quintile), then compute next-month VW excess returns
for each (control_q, reg_q) cell.

Per Assumption 3 we use FF5 (RMW + CMA + standard FF3) instead of FF6PS.

For audit major [M3], the script also computes a synthetic FF5 + MOM
alpha on each cell, which approximates FF6 minus LIQ. The empirical
|FF5 - FF5+MOM| shift per control is recorded in
data/table3_ff5_ff6ps_shift.json to benchmark the FF5-vs-FF6PS
substitution effect.

Procedure (per paper §5.2):
  - For each month t from July 1963 to November 2020.
  - Sort month = month t.
  - Winsorize control variables at 1%/99% per month.
  - Compute NYSE breakpoints (20/40/60/80 percentiles of control var).
  - Assign each stock to a control quintile (1..5).
  - Within each control quintile, compute NYSE breakpoints of REG.
  - Assign each stock to a REG quintile (1..5) within its control quintile.
  - Compute next-month VW excess return per (control_q, reg_q) cell.
  - Time-series regression: per-cell excess return on FF5 factors.
  - Average across the 5 control quintiles for each REG quintile.
  - The High-Low spread is the average of the 5 control-quintile spreads.

Output: results/table_3.md plus per-cell metrics dict for eval/metrics.json.
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

# Factor models
FF5_FACTOR_COLS = ["ff_mkt_rf", "ff_smb", "ff_hml", "ff_rmw", "ff_cma"]
FF5_MOM_FACTOR_COLS = ["ff_mkt_rf", "ff_smb", "ff_hml", "ff_rmw", "ff_cma", "ff_mom"]

# The 12 control variables (panel column names)
CONTROL_VARS = ["beta", "log_me", "bm", "mom", "str",
                "coskew", "illiq", "ivol", "max5",
                "op", "ia", "sue"]

# Display names for tables
DISPLAY_NAMES = {
    "beta": "BETA", "log_me": "SIZE", "bm": "BM", "mom": "MOM",
    "str": "STR", "coskew": "COSKEW", "illiq": "ILLIQ", "ivol": "IVOL",
    "max5": "MAX", "op": "OP", "ia": "IA", "sue": "SUE",
}

# Paper Table 3 values for comparison (paper Table 3 L1161-L1364)
PAPER_VALUES = {
    "BETA":   {"Q1": -0.36, "Q2": -0.30, "Q3": -0.21, "Q4": 0.00, "Q5": 0.21, "HL": 0.56},
    "SIZE":   {"Q1": -0.46, "Q2": -0.25, "Q3": -0.15, "Q4": 0.00, "Q5": 0.35, "HL": 0.81},
    "BM":     {"Q1": -0.40, "Q2": -0.23, "Q3": -0.14, "Q4": 0.04, "Q5": 0.23, "HL": 0.63},
    "MOM":    {"Q1": -0.42, "Q2": -0.29, "Q3": -0.17, "Q4": -0.06, "Q5": 0.18, "HL": 0.60},
    "STR":    {"Q1": -0.30, "Q2": -0.22, "Q3": -0.10, "Q4": -0.03, "Q5": 0.22, "HL": 0.52},
    "COSKEW": {"Q1": -0.30, "Q2": -0.24, "Q3": -0.15, "Q4": 0.06, "Q5": 0.27, "HL": 0.57},
    "ILLIQ":  {"Q1": -0.51, "Q2": -0.25, "Q3": -0.17, "Q4": 0.00, "Q5": 0.33, "HL": 0.84},
    "IVOL":   {"Q1": -0.38, "Q2": -0.23, "Q3": -0.24, "Q4": -0.02, "Q5": 0.23, "HL": 0.61},
    "MAX":    {"Q1": -0.34, "Q2": -0.20, "Q3": -0.23, "Q4": 0.01, "Q5": 0.17, "HL": 0.51},
    "OP":     {"Q1": -0.38, "Q2": -0.23, "Q3": -0.20, "Q4": -0.10, "Q5": 0.24, "HL": 0.62},
    "IA":     {"Q1": -0.31, "Q2": -0.20, "Q3": -0.16, "Q4": -0.03, "Q5": 0.25, "HL": 0.56},
    "SUE":    {"Q1": -0.28, "Q2": -0.15, "Q3": -0.16, "Q4": -0.06, "Q5": 0.27, "HL": 0.55},
}


def _winsorize_per_month(panel: pd.DataFrame, col: str, p: float = 0.01) -> pd.DataFrame:
    """Winsorize `col` cross-sectionally at the `p` and `1-p` percentiles per month."""
    panel = panel.copy()

    def _clip(g: pd.Series) -> pd.Series:
        lo, hi = g.quantile([p, 1 - p])
        return g.clip(lower=lo, upper=hi)

    panel[col] = panel.groupby("month")[col].transform(_clip)
    return panel


def _nyse_quintile_breakpoints(panel: pd.DataFrame, signal_col: str) -> pd.DataFrame:
    """Per month, compute the 20/40/60/80 percentiles of `signal_col` among
    NYSE (hexcd == 1) stocks. Returns a DataFrame indexed by month with
    columns bp_20, bp_40, bp_60, bp_80."""
    df = panel[["month", "hexcd", signal_col]].dropna(subset=[signal_col])
    nyse = df[df["hexcd"] == 1]
    bp = nyse.groupby("month")[signal_col].quantile([0.20, 0.40, 0.60, 0.80]).unstack()
    bp.columns = [f"bp_{c}" for c in [20, 40, 60, 80]]
    return bp


def _assign_quintile(panel: pd.DataFrame, signal_col: str, bp: pd.DataFrame) -> pd.Series:
    """Assign 1..5 quintile labels based on the breakpoints in `bp`."""
    out = panel[["month", signal_col]].join(bp, on="month")
    q = pd.Series(np.nan, index=out.index, dtype=float)
    q[out[signal_col] < out["bp_20"]] = 1
    q[(out[signal_col] >= out["bp_20"]) & (out[signal_col] < out["bp_40"])] = 2
    q[(out[signal_col] >= out["bp_40"]) & (out[signal_col] < out["bp_60"])] = 3
    q[(out[signal_col] >= out["bp_60"]) & (out[signal_col] < out["bp_80"])] = 4
    q[out[signal_col] >= out["bp_80"]] = 5
    return q


def _attach_lead_factors(panel: pd.DataFrame, ff: pd.DataFrame) -> pd.DataFrame:
    """Shift FF factors backward by 1 month so that the regression
    y_{t+1} = alpha + beta * f_{t+1} uses factors at the return month."""
    ff_lead = ff.copy()
    ff_lead["join_month"] = (pd.to_datetime(ff_lead["month"]) - pd.DateOffset(months=1)).dt.strftime("%Y-%m-%d")
    ff_lead = ff_lead.drop(columns=["month"])
    panel = panel.copy()
    panel["join_month"] = pd.to_datetime(panel["month"]).dt.strftime("%Y-%m-%d")
    merged = panel.merge(ff_lead, on="join_month", how="left")
    merged = merged.drop(columns=["join_month"])
    return merged


def _regress_alpha(
    port_ret: pd.Series,
    factor_rets: pd.DataFrame,
    n_lags: int = 6,
) -> tuple:
    """Run OLS: port_ret = alpha + sum(beta_i * factor_i) + epsilon.
    Returns (alpha, nw_t_stat, n_obs)."""
    aligned = pd.concat([port_ret.rename("y"), factor_rets], axis=1, join="inner").dropna()
    if len(aligned) < 30:
        return (float("nan"), float("nan"), int(len(aligned)))
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
    return (alpha, t, int(res.nobs))


def _compute_vw_per_cell(
    panel_with_bins: pd.DataFrame,
    cell_q_col: str = "reg_q",
    control_q_col: str = "control_q",
) -> pd.DataFrame:
    """Per (month, control_q, reg_q), compute VW (me_lag1-weighted) mean
    excess return. Returns DataFrame with columns [month, control_q, reg_q, vw]."""
    out = (
        panel_with_bins
        .groupby(["month", control_q_col, cell_q_col])
        .apply(
            lambda g: pd.Series({
                "vw": (g["ret_excess_lead1"] * g["me_lag1"]).sum() / g["me_lag1"].sum()
                       if g["me_lag1"].sum() > 0 else np.nan,
            }),
            include_groups=False,
        )
        .reset_index()
    )
    return out


def run_table_3() -> dict:
    import time
    t0 = time.time()

    print("=" * 72)
    print("Table 3 — Dependent bivariate sorts (12 controls x 5x5 grid)")
    print("=" * 72)

    # 1. Load panel with controls and FF factors.
    print("\n[1] Loading enriched panel and FF factors...")
    full_path = LAYOUT.data_path("panel_full.parquet")
    if full_path.exists():
        full = pd.read_parquet(full_path)
        print(f"      Loaded panel_full.parquet: {full.shape[0]:,} rows x {full.shape[1]} cols")
    else:
        from src.main import _client
        _client_inst = _client()
        sql_path = LAYOUT.src_path("sql") / "11_panel_with_controls.sql"
        sql = sql_path.read_text()
        cleaned_lines = []
        for line in sql.split("\n"):
            idx = line.find("--")
            cleaned_lines.append(line[:idx] if idx >= 0 else line)
        cleaned = "\n".join(cleaned_lines)
        stmts = [s.strip() for s in cleaned.split(";") if s.strip()]
        for stmt in stmts:
            _client_inst.execute(stmt)
        data, cols = _client_inst.execute(
            "SELECT * FROM write_yeye.arb_panel_full ORDER BY month, permno",
            with_column_types=True,
        )
        full = pd.DataFrame(data, columns=[x[0] for x in cols])
        full.to_parquet(full_path, index=False)
        print(f"      Built and saved panel_full.parquet: {full.shape[0]:,} rows x {full.shape[1]} cols")

    ff = pd.read_parquet(LAYOUT.data_path("ff_factors.parquet"))
    print(f"      FF factors: {ff.shape[0]:,} months")

    # 2. Attach FF factors at return month (t+1).
    print("\n[2] Attaching FF factors at return month (t+1)...")
    full = _attach_lead_factors(full, ff)
    print(f"      ff_mkt_rf coverage: {full['ff_mkt_rf'].notna().mean():.4f}")

    # 3. Winsorize each control variable at 1%/99% per month.
    print("\n[3] Winsorizing each control variable at 1%/99% per month...")
    for cv in CONTROL_VARS:
        if cv in full.columns:
            n_before = full[cv].notna().sum()
            full = _winsorize_per_month(full, cv, p=0.01)
            n_after = full[cv].notna().sum()
            print(f"      {cv:<8}: {n_after:,} non-null ({100*n_after/len(full):.1f}%)")
        else:
            print(f"      {cv:<8}: MISSING in panel")

    # 4. For each control variable, do dependent bivariate sort.
    metrics = {}
    table_rows = {}
    # Per audit major [M3], store the FF5 vs FF5+MOM shift per control.
    shift_per_control: dict[str, dict] = {}

    for cv in CONTROL_VARS:
        if cv not in full.columns:
            print(f"\n[skipping {cv}]: column missing")
            continue

        print(f"\n[4] Bivariate sort on {cv}...")

        # Compute NYSE breakpoints of the control variable per month.
        bp_control = _nyse_quintile_breakpoints(full, cv)

        # Assign control quintile to every stock (not just NYSE).
        full["control_q"] = _assign_quintile(full, cv, bp_control)

        # Within each (month, control_q), compute NYSE breakpoints of REG.
        bivar_results = []  # (month, control_q, reg_q, vw)
        for month, g_m in full.groupby("month"):
            for cq in [1, 2, 3, 4, 5]:
                g_cq = g_m[g_m["control_q"] == cq]
                nyse_in_cq = g_cq[g_cq["hexcd"] == 1]
                if len(nyse_in_cq) < 30:
                    continue
                reg_bp = nyse_in_cq["reg"].quantile([0.20, 0.40, 0.60, 0.80]).values
                g_cq = g_cq.copy()
                g_cq["reg_q"] = np.nan
                g_cq.loc[g_cq["reg"] < reg_bp[0], "reg_q"] = 1
                g_cq.loc[(g_cq["reg"] >= reg_bp[0]) & (g_cq["reg"] < reg_bp[1]), "reg_q"] = 2
                g_cq.loc[(g_cq["reg"] >= reg_bp[1]) & (g_cq["reg"] < reg_bp[2]), "reg_q"] = 3
                g_cq.loc[(g_cq["reg"] >= reg_bp[2]) & (g_cq["reg"] < reg_bp[3]), "reg_q"] = 4
                g_cq.loc[g_cq["reg"] >= reg_bp[3], "reg_q"] = 5
                for rq in [1, 2, 3, 4, 5]:
                    g_rq = g_cq[g_cq["reg_q"] == rq]
                    if len(g_rq) > 0 and g_rq["me_lag1"].sum() > 0:
                        vw = (g_rq["ret_excess_lead1"] * g_rq["me_lag1"]).sum() / g_rq["me_lag1"].sum()
                        bivar_results.append((month, cq, rq, vw))

        bivar_df = pd.DataFrame(bivar_results, columns=["month", "control_q", "reg_q", "vw"])
        n_cells = bivar_df.groupby(["control_q", "reg_q"]).size().shape[0]
        print(f"      bivar cells: {n_cells}, total rows: {len(bivar_df):,}")
        print(f"      avg months per cell: {len(bivar_df) / max(n_cells, 1):.0f}")

        # 5. Per cell, run FF5 and FF5+MOM alpha regressions.
        ff_at_month = (
            full[["month"] + list(set(FF5_FACTOR_COLS + FF5_MOM_FACTOR_COLS))]
            .drop_duplicates("month")
            .set_index("month")
            .sort_index()
        )

        cell_alphas_ff5 = {}
        cell_alphas_ff5mom = {}
        for (cq, rq), g in bivar_df.groupby(["control_q", "reg_q"]):
            port_ret = g.set_index("month")["vw"]
            alpha5, _, _ = _regress_alpha(port_ret, ff_at_month[FF5_FACTOR_COLS], n_lags=6)
            cell_alphas_ff5[(cq, rq)] = alpha5
            alpham, _, _ = _regress_alpha(port_ret, ff_at_month[FF5_MOM_FACTOR_COLS], n_lags=6)
            cell_alphas_ff5mom[(cq, rq)] = alpham

        # 6. Average across control quintiles for each REG quintile.
        def _avg_per_rq(cell_alphas):
            out = {}
            for rq in [1, 2, 3, 4, 5]:
                vals = [cell_alphas[(cq, rq)] for cq in [1, 2, 3, 4, 5]
                        if (cq, rq) in cell_alphas]
                out[rq] = float(np.nanmean(vals))
            return out

        avg_ff5 = _avg_per_rq(cell_alphas_ff5)
        avg_ff5mom = _avg_per_rq(cell_alphas_ff5mom)

        # 7. High-Low spread = average of the 5 control-quintile spreads.
        def _hl_spread(cell_alphas):
            spreads = []
            for cq in [1, 2, 3, 4, 5]:
                if (cq, 5) in cell_alphas and (cq, 1) in cell_alphas:
                    spreads.append(cell_alphas[(cq, 5)] - cell_alphas[(cq, 1)])
            return float(np.nanmean(spreads))

        hl_ff5 = _hl_spread(cell_alphas_ff5)
        hl_ff5mom = _hl_spread(cell_alphas_ff5mom)

        # Store results
        display = DISPLAY_NAMES[cv]
        table_rows[display] = {
            "Q1": avg_ff5[1] * 100,
            "Q2": avg_ff5[2] * 100,
            "Q3": avg_ff5[3] * 100,
            "Q4": avg_ff5[4] * 100,
            "Q5": avg_ff5[5] * 100,
            "HL": hl_ff5 * 100,
            "Q1_ff5mom": avg_ff5mom[1] * 100,
            "Q2_ff5mom": avg_ff5mom[2] * 100,
            "Q3_ff5mom": avg_ff5mom[3] * 100,
            "Q4_ff5mom": avg_ff5mom[4] * 100,
            "Q5_ff5mom": avg_ff5mom[5] * 100,
            "HL_ff5mom": hl_ff5mom * 100,
        }
        # Metrics dict: each row × 6 cells (FF5 only — primary)
        for q in [1, 2, 3, 4, 5]:
            metrics[f"{display}_Q{q}"] = {"value": avg_ff5[q] * 100, "unit": "percent_per_month"}
            metrics[f"{display}_Q{q}_ff5mom"] = {"value": avg_ff5mom[q] * 100, "unit": "percent_per_month"}
        metrics[f"{display}_HL"] = {"value": hl_ff5 * 100, "unit": "percent_per_month"}
        metrics[f"{display}_HL_ff5mom"] = {"value": hl_ff5mom * 100, "unit": "percent_per_month"}

        # Record shift per control (audit major M3).
        shift_per_control[display] = {
            "ff5": float(hl_ff5 * 100),
            "ff5_mom": float(hl_ff5mom * 100),
            "paper_ff6ps": float(PAPER_VALUES[display]["HL"]),
            "shift_ff5_minus_ff5mom": float((hl_ff5 - hl_ff5mom) * 100),
            "ours_ff5_paper_diff_pct": float(
                abs(hl_ff5 * 100 - PAPER_VALUES[display]["HL"])
                / abs(PAPER_VALUES[display]["HL"]) * 100
            ),
        }

        print(f"      FF5 HL={hl_ff5 * 100:.4f}%  FF5+MOM HL={hl_ff5mom * 100:.4f}%  "
              f"shift={(hl_ff5 - hl_ff5mom) * 100:+.4f}%  paper={PAPER_VALUES[display]['HL']:.2f}%")

    elapsed = time.time() - t0
    print(f"\nTotal computation time: {elapsed:.1f}s")

    # Save FF5 vs FF5+MOM shift data (audit major M3).
    shift_path = LAYOUT.data_path("table3_ff5_ff6ps_shift.json")
    shift_path.write_text(json.dumps(shift_per_control, indent=2, default=float))
    print(f"\n[5] Saved FF5 vs FF5+MOM shift data: {shift_path}")

    # 8. Write Table 3 markdown.
    print("\n[6] Writing results/table_3.md ...")
    table_md = _format_table_md(table_rows)
    LAYOUT.result_path("table_3.md").parent.mkdir(parents=True, exist_ok=True)
    LAYOUT.result_path("table_3.md").write_text(table_md)
    print(f"      Wrote {LAYOUT.result_path('table_3.md')}")

    return metrics


def _format_table_md(table_rows: dict) -> str:
    """Format Table 3 as markdown matching the paper's structure."""
    lines = []
    lines.append("# Table 3 — Dependent Bivariate Sorts: REG Premium Across 12 Controls")
    lines.append("")
    lines.append("Sample: NYSE/AMEX/NASDAQ common stocks (shrcd 10,11), $5-$1000 price screen.")
    lines.append("Sort month = June 1963 to November 2020 (689 months).")
    lines.append("Each month: sort into control quintiles (NYSE breakpoints), then within each")
    lines.append("control quintile sort into REG quintiles (NYSE breakpoints). Compute next-month")
    lines.append("VW (me_lag1-weighted) excess returns. Then time-series regression of each")
    lines.append("(control_q, reg_q) cell's monthly VW return on FF5 factors (NW-6 t-stats).")
    lines.append("")
    lines.append("Each cell below is the FF5 alpha (in %/month) of the AVERAGE across the 5")
    lines.append("control-quintile alphas for that REG quintile. The HL column is the average")
    lines.append("across control quintiles of the (Q5 - Q1) spread.")
    lines.append("")
    lines.append("Note: paper uses FF6PS alphas; per Assumption 3 we substitute FF5 (LIQ missing).")
    lines.append("For audit major [M3], we also compute FF5+MOM (proxy for FF6 minus LIQ) and")
    lines.append("record the |FF5 - FF5+MOM| shift per control.")
    lines.append("")
    lines.append("| Control | Q1 (Low REG) | Q2 | Q3 | Q4 | Q5 (High REG) | High-Low |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for display in ["BETA", "SIZE", "BM", "MOM", "STR", "COSKEW",
                    "ILLIQ", "IVOL", "MAX", "OP", "IA", "SUE"]:
        if display not in table_rows:
            lines.append(f"| {display} | [DATA-UNAVAILABLE] | | | | | |")
            continue
        r = table_rows[display]
        lines.append(
            f"| {display} | {r['Q1']:.2f}% | {r['Q2']:.2f}% | {r['Q3']:.2f}% | "
            f"{r['Q4']:.2f}% | {r['Q5']:.2f}% | {r['HL']:.2f}% |"
        )

    lines.append("")
    lines.append("## Comparison with paper Table 3")
    lines.append("")
    lines.append("Ours vs paper for each cell. Format: ours vs paper. Highlight: > 50% divergence.")
    lines.append("")
    lines.append("| Control | Cell | Ours | Paper | Diff (%) | Note |")
    lines.append("|---|---|---:|---:|---:|---|")
    for display in ["BETA", "SIZE", "BM", "MOM", "STR", "COSKEW",
                    "ILLIQ", "IVOL", "MAX", "OP", "IA", "SUE"]:
        if display not in table_rows:
            continue
        r = table_rows[display]
        for q in [1, 2, 3, 4, 5]:
            cell_name = f"Q{q}"
            ours = r[cell_name]
            paper = PAPER_VALUES[display][cell_name]
            diff_pct = abs(ours - paper) / abs(paper) * 100 if paper != 0 else float('inf') if ours != 0 else 0
            flag = "  **DIVERGENCE**" if diff_pct > 50 else ""
            lines.append(f"| {display} | {cell_name} | {ours:.4f} | {paper:.4f} | {diff_pct:.1f}%{flag} | |")
        ours = r["HL"]
        paper = PAPER_VALUES[display]["HL"]
        diff_pct = abs(ours - paper) / abs(paper) * 100 if paper != 0 else float('inf') if ours != 0 else 0
        flag = "  **DIVERGENCE**" if diff_pct > 50 else ""
        lines.append(f"| {display} | HL | {ours:.4f} | {paper:.4f} | {diff_pct:.1f}%{flag} | |")

    # Audit major M3: side-by-side FF5 vs FF5+MOM shift table.
    lines.append("")
    lines.append("## M3 — FF5 vs FF5+MOM shift per control (HL spread)")
    lines.append("")
    lines.append("FF5 = Mkt-RF + SMB + HML + RMW + CMA. FF5+MOM adds MOM (proxy for FF6 minus LIQ).")
    lines.append("The shift = FF5 - FF5+MOM approximates the marginal impact of MOM on the alpha.")
    lines.append("Paper's HL column uses FF6PS = FF5 + MOM + LIQ. Our FF5+MOM HL is a partial")
    lines.append("substitute for FF6PS (LIQ missing).")
    lines.append("")
    lines.append("| Control | Ours FF5 HL | Ours FF5+MOM HL | Shift | Paper FF6PS HL | Ours-FF5 vs Paper |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for display in ["BETA", "SIZE", "BM", "MOM", "STR", "COSKEW",
                    "ILLIQ", "IVOL", "MAX", "OP", "IA", "SUE"]:
        if display not in table_rows:
            continue
        r = table_rows[display]
        paper_hl = PAPER_VALUES[display]["HL"]
        diff_pct = abs(r["HL"] - paper_hl) / abs(paper_hl) * 100 if paper_hl != 0 else float('inf')
        lines.append(
            f"| {display} | {r['HL']:.4f}% | {r['HL_ff5mom']:.4f}% | "
            f"{r['HL'] - r['HL_ff5mom']:+.4f}% | {paper_hl:.2f}% | {diff_pct:.1f}% |"
        )
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    metrics = run_table_3()
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
    print(f"\nUpdated {eval_path} with Table 3 metrics.")