"""
Table replication: Tables 1, 6, 9 Panel B, 2.

Loads data/panel.parquet and the FF factors from ClickHouse, then computes
value-weighted decile portfolio sorts and factor-model alphas.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import statsmodels.api as sm
from clickhouse_driver import Client

from utils.env import get_clickhouse_config
from utils.paths import paper_layout


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SLUG = "bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to"
LAYOUT = paper_layout(SLUG)
LAYOUT.ensure()

PANEL_PATH = LAYOUT.data_path("panel.parquet")
RESULTS_DIR = LAYOUT.results_dir
EVAL_DIR = LAYOUT.eval_dir
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def _client() -> Client:
    cfg = get_clickhouse_config()
    return Client(host=cfg["host"], port=cfg["port"], user=cfg["user"], password=cfg["password"])


# ---------------------------------------------------------------------------
# FF factor loaders
# ---------------------------------------------------------------------------

def load_ff_factors() -> pd.DataFrame:
    """Load monthly Fama-French factors and merge to construct FF3/FFC4/FF5/FF6.

    ff.three_factor and ff.four_factor are DAILY; we aggregate to month-end.
    ff.five_factor_monthly and ff.four_factor_monthly are pre-aggregated monthly.
    """
    c = _client()
    # Daily three_factor -> monthly aggregation in SQL
    q3 = """
    SELECT
        toLastDayOfMonth(toDate32(parseDateTimeBestEffort(dt))) AS month,
        sum(mkt_rf) AS mkt_rf,
        sum(smb) AS smb3,
        sum(hml) AS hml3,
        sum(rf) AS rf3
    FROM ff.three_factor
    GROUP BY toLastDayOfMonth(toDate32(parseDateTimeBestEffort(dt)))
    """
    # four_factor_monthly has mom directly (and is monthly already)
    q4 = "SELECT toDate32(parseDateTimeBestEffort(dt)) AS month, sum(mom) AS mom FROM ff.four_factor_monthly GROUP BY toDate32(parseDateTimeBestEffort(dt))"
    q5 = "SELECT toDate32(parseDateTimeBestEffort(dt)) AS month, sum(rmw) AS rmw, sum(cma) AS cma FROM ff.five_factor_monthly GROUP BY toDate32(parseDateTimeBestEffort(dt))"
    f3 = c.execute(q3, with_column_types=True)
    f4 = c.execute(q4, with_column_types=True)
    f5 = c.execute(q5, with_column_types=True)

    def to_df(res):
        data, cols = res
        return pd.DataFrame(data, columns=[c[0] for c in cols])

    df3 = to_df(f3)
    df4 = to_df(f4)
    df5 = to_df(f5)

    # ff.four_factor_monthly and ff.five_factor_monthly appear to be already monthly (table names say "monthly")
    # but their row counts (1192, 748) suggest monthly. Yet the sums I compute match.
    # However if they're truly monthly, summing gives wrong values. Use avg / max instead for safety.
    # Inspect: use any() or last value instead of sum for monthly sources.
    # Since we know df4 and df5 are monthly (consistent IDs), take the value not sum.
    q4b = "SELECT toDate32(parseDateTimeBestEffort(dt)) AS month, any(mom) AS mom FROM ff.four_factor_monthly GROUP BY toDate32(parseDateTimeBestEffort(dt))"
    q5b = "SELECT toDate32(parseDateTimeBestEffort(dt)) AS month, any(rmw) AS rmw, any(cma) AS cma FROM ff.five_factor_monthly GROUP BY toDate32(parseDateTimeBestEffort(dt))"
    f4 = c.execute(q4b, with_column_types=True)
    f5 = c.execute(q5b, with_column_types=True)
    df4 = to_df(f4)
    df5 = to_df(f5)

    ff = df3.merge(df4, on="month", how="outer").merge(df5, on="month", how="outer")
    for col in ff.columns:
        if col != "month":
            ff[col] = pd.to_numeric(ff[col], errors="coerce")
    ff = ff.sort_values("month").reset_index(drop=True)
    return ff


def construct_factor_models(ff: pd.DataFrame) -> dict:
    """Construct the factor-model columns.

    Returns a dict mapping model name -> list of column names + RF.
    """
    cols = {
        "CAPM":  ["mkt_rf"],
        "FF3":   ["mkt_rf", "smb3", "hml3"],
        "FFC4":  ["mkt_rf", "smb3", "hml3", "mom"],
        "FF5":   ["mkt_rf", "smb3", "hml3", "rmw", "cma"],
        "FF6":   ["mkt_rf", "smb3", "hml3", "rmw", "cma", "mom"],
    }
    out = {}
    for name, factors in cols.items():
        out[name] = {"factors": factors, "rf": "rf3"}
    return out


# ---------------------------------------------------------------------------
# Portfolio helpers
# ---------------------------------------------------------------------------

def assign_deciles(panel: pd.DataFrame, signal: str, n: int = 10) -> pd.DataFrame:
    """Assign NYSE-quintile/decile based on the signal column.

    Following the paper's convention: assign deciles within each month using
    all stocks in the panel. We use a simple qcut across all stocks per month.
    """
    out = panel.copy()
    out["bin"] = out.groupby("month")[signal].transform(
        lambda x: pd.qcut(x.rank(method="first"), q=n, labels=False, duplicates="drop") + 1
    )
    out["bin"] = out["bin"].astype("Int64")
    return out


def value_weighted_returns(panel_with_bin: pd.DataFrame, ret_col: str = "ret_fwd", bin_col: str = "bin") -> pd.DataFrame:
    """Compute value-weighted portfolio returns per (month, bin) using market equity."""
    out = (
        panel_with_bin.dropna(subset=[bin_col, ret_col, "me"])
        .assign(weighted_ret=lambda d: d[ret_col] * d["me"])
        .groupby(["month", bin_col])
        .agg(
            vw_ret=("weighted_ret", "sum"),
            me=("me", "sum"),
            n_stocks=("permno", "nunique"),
        )
        .reset_index()
    )
    out = out.rename(columns={bin_col: "bin"})
    out["vw_ret"] = out["vw_ret"] / out["me"]
    return out


def compute_long_short(ret_by_bin: pd.DataFrame, long_bin: int = 10, short_bin: int = 1) -> pd.DataFrame:
    """Compute long-short spread: D_long - D_short."""
    long_leg = ret_by_bin[ret_by_bin["bin"] == long_bin][["month", "vw_ret"]].rename(columns={"vw_ret": "ls_ret"})
    short_leg = ret_by_bin[ret_by_bin["bin"] == short_bin][["month", "vw_ret"]].rename(columns={"vw_ret": "sh_ret"})
    out = long_leg.merge(short_leg, on="month", how="inner")
    out["ls_spread"] = out["ls_ret"] - out["sh_ret"]
    return out


def newey_west_alpha(y: pd.Series, X: pd.DataFrame, lags: int = 6) -> tuple:
    """Run OLS with Newey-West HAC standard errors and return alpha, t-stat, n."""
    aligned = pd.concat([y.rename("y"), X], axis=1).dropna()
    n = len(aligned)
    if n < 30:
        return np.nan, np.nan, n
    yv = aligned["y"].astype(float).values
    Xv = sm.add_constant(aligned.drop(columns="y").astype(float).values)
    res = sm.OLS(yv, Xv).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return float(res.params[0]), float(res.tvalues[0]), n


# ---------------------------------------------------------------------------
# Table 1 / Table 6 / Table 9 builders
# ---------------------------------------------------------------------------

def build_decile_table(panel: pd.DataFrame, signal: str, ff: pd.DataFrame, lags: int = 6) -> dict:
    """For a signal, compute the decile portfolio table.

    Returns a dict: {bin -> {metric: value, ...}, 'spread': {...}, 'models': [...]}.
    """
    p = assign_deciles(panel.dropna(subset=[signal, "ret_fwd"]).copy(), signal, n=10)
    rets = value_weighted_returns(p, "ret_fwd")
    rets = rets.merge(ff, on="month", how="inner")
    rets["vw_excess"] = rets["vw_ret"] - rets["rf3"] / 100.0  # RF is in %

    # Aggregate per bin
    out = {}
    for bin_id in range(1, 11):
        sub = rets[rets["bin"] == bin_id].copy()
        if sub.empty:
            continue
        # RET-RF (excess return)
        mean_excess = sub["vw_excess"].mean() * 100  # to pct per month
        # t-stat
        t_excess = sub["vw_excess"].mean() / (sub["vw_excess"].std() / np.sqrt(len(sub))) if len(sub) > 1 else np.nan

        out[f"P{bin_id}"] = {
            "vw_ret_rf": (mean_excess, t_excess),
            "n_months": int(len(sub)),
        }

    # 10-1 spread
    long_leg = rets[rets["bin"] == 10]["vw_excess"]
    short_leg = rets[rets["bin"] == 1]["vw_excess"]
    if len(long_leg) and len(short_leg):
        spread = long_leg.values - short_leg.values
        out["10-1"] = {
            "vw_ret_rf": (float(np.nanmean(spread) * 100), float(np.nanmean(spread) / (np.nanstd(spread) / np.sqrt(len(spread))))),
            "n_months": int(len(spread)),
        }
    else:
        out["10-1"] = {"vw_ret_rf": (np.nan, np.nan), "n_months": 0}

    # Alphas per model
    models = construct_factor_models(ff)
    factor_data = rets.dropna(subset=["vw_ret"] + ["mkt_rf", "smb3", "hml3", "mom", "rmw", "cma"]).copy()
    factor_data["ex_ret"] = factor_data["vw_ret"] - factor_data["rf3"] / 100.0
    # Factor columns in decimal; ff3/5 are in pct.
    for col in ["mkt_rf", "smb3", "hml3", "mom", "rmw", "cma"]:
        factor_data[col] = factor_data[col] / 100.0  # pct -> decimal

    for model_name, cfg in models.items():
        factors = cfg["factors"]
        # Per bin
        for bin_id in range(1, 11):
            sub = factor_data[factor_data["bin"] == bin_id]
            if sub.empty or len(sub) < 30:
                continue
            alpha, t_stat, n = newey_west_alpha(sub["ex_ret"], sub[factors], lags=lags)
            key = f"P{bin_id}"
            if "alphas" not in out[key]:
                out[key]["alphas"] = {}
            out[key]["alphas"][model_name] = (alpha * 100, t_stat, n)  # alpha in pct
        # Spread (D10 - D1) via merge on month
        long_leg = factor_data[factor_data["bin"] == 10][["month", "ex_ret"] + factors].rename(
            columns={c: f"L_{c}" for c in ["ex_ret"] + factors}
        )
        short_leg = factor_data[factor_data["bin"] == 1][["month", "ex_ret"] + factors].rename(
            columns={c: f"S_{c}" for c in ["ex_ret"] + factors}
        )
        spread = long_leg.merge(short_leg, on="month", how="inner")
        if spread.empty:
            continue
        for f in factors:
            spread[f] = spread[f"L_{f}"] - spread[f"S_{f}"]
        spread["ex_ret"] = spread["L_ex_ret"] - spread["S_ex_ret"]
        spread = spread[["ex_ret"] + factors].dropna()
        if len(spread) >= 30:
            alpha, t_stat, n = newey_west_alpha(spread["ex_ret"], spread[factors], lags=lags)
            if "alphas" not in out["10-1"]:
                out["10-1"]["alphas"] = {}
            out["10-1"]["alphas"][model_name] = (alpha * 100, t_stat, n)

    return out


def build_maxbeta_table(panel: pd.DataFrame, ff: pd.DataFrame, lags: int = 6) -> dict:
    """Build MAX^beta decile table: dependent double sort on beta then MAX within beta.

    Returns dict with same structure as build_decile_table.
    """
    p = panel.dropna(subset=["max_5", "beta_m", "me", "ret_fwd"]).copy()
    # Filter implausible beta values
    p = p[(p["beta_m"] > -2) & (p["beta_m"] < 5)].copy()
    # 10 beta bins per month
    p["beta_bin"] = p.groupby("month")["beta_m"].transform(
        lambda x: pd.qcut(x.rank(method="first"), q=10, labels=False, duplicates="drop") + 1
    ).astype("Int64")
    # 10 MAX bins within each (month, beta_bin)
    p["max_bin"] = p.groupby(["month", "beta_bin"])["max_5"].transform(
        lambda x: pd.qcut(x.rank(method="first"), q=10, labels=False, duplicates="drop") + 1
    ).astype("Int64")
    # Regroup: MAX^beta rank = max_bin across beta bins (the paper's regrouping)
    p["maxbeta_bin"] = p["max_bin"].astype("Int64")
    # Drop the bin column to avoid the wrong column being used downstream
    if "bin" in p.columns:
        p = p.drop(columns=["bin"])

    rets = value_weighted_returns(p.dropna(subset=["maxbeta_bin"]), "ret_fwd", bin_col="maxbeta_bin")
    rets = rets.merge(ff, on="month", how="inner")
    rets["vw_excess"] = rets["vw_ret"] - rets["rf3"] / 100.0

    out = {}
    for bin_id in range(1, 11):
        sub = rets[rets["bin"] == bin_id].copy()
        if sub.empty:
            continue
        mean_excess = sub["vw_excess"].mean() * 100
        t_excess = sub["vw_excess"].mean() / (sub["vw_excess"].std() / np.sqrt(len(sub))) if len(sub) > 1 else np.nan
        out[f"P{bin_id}"] = {"vw_ret_rf": (mean_excess, t_excess), "n_months": int(len(sub))}

    long_leg = rets[rets["bin"] == 10]["vw_excess"]
    short_leg = rets[rets["bin"] == 1]["vw_excess"]
    if len(long_leg) and len(short_leg):
        spread = long_leg.values - short_leg.values
        out["10-1"] = {
            "vw_ret_rf": (float(np.nanmean(spread) * 100), float(np.nanmean(spread) / (np.nanstd(spread) / np.sqrt(len(spread))))),
            "n_months": int(len(spread)),
        }
    else:
        out["10-1"] = {"vw_ret_rf": (np.nan, np.nan), "n_months": 0}

    models = construct_factor_models(ff)
    factor_data = rets.dropna(subset=["vw_ret"] + ["mkt_rf", "smb3", "hml3", "mom", "rmw", "cma"]).copy()
    factor_data["ex_ret"] = factor_data["vw_ret"] - factor_data["rf3"] / 100.0
    for col in ["mkt_rf", "smb3", "hml3", "mom", "rmw", "cma"]:
        factor_data[col] = factor_data[col] / 100.0

    for model_name, cfg in models.items():
        factors = cfg["factors"]
        for bin_id in range(1, 11):
            sub = factor_data[factor_data["bin"] == bin_id]
            if sub.empty or len(sub) < 30:
                continue
            alpha, t_stat, n = newey_west_alpha(sub["ex_ret"], sub[factors], lags=lags)
            key = f"P{bin_id}"
            if "alphas" not in out[key]:
                out[key]["alphas"] = {}
            out[key]["alphas"][model_name] = (alpha * 100, t_stat, n)
        # Spread via merge on month (avoids full_outer memory blowup)
        long_leg = factor_data[factor_data["bin"] == 10][["month", "ex_ret"] + factors].rename(
            columns={c: f"L_{c}" for c in ["ex_ret"] + factors}
        )
        short_leg = factor_data[factor_data["bin"] == 1][["month", "ex_ret"] + factors].rename(
            columns={c: f"S_{c}" for c in ["ex_ret"] + factors}
        )
        spread = long_leg.merge(short_leg, on="month", how="inner")
        if spread.empty:
            continue
        for f in factors:
            spread[f] = spread[f"L_{f}"] - spread[f"S_{f}"]
        spread["ex_ret"] = spread["L_ex_ret"] - spread["S_ex_ret"]
        spread = spread[["ex_ret"] + factors].dropna()
        if len(spread) >= 30:
            alpha, t_stat, n = newey_west_alpha(spread["ex_ret"], spread[factors], lags=lags)
            if "alphas" not in out["10-1"]:
                out["10-1"]["alphas"] = {}
            out["10-1"]["alphas"][model_name] = (alpha * 100, t_stat, n)

    return out


def format_table_md(table_name: str, table: dict, paper_targets: dict, model_cols: list) -> str:
    """Format a table into Markdown using the paper's value/tolerance format."""
    lines = [f"# {table_name}", ""]
    lines.append("| Bin | RET-RF (pct) | " + " | ".join(model_cols) + " |")
    lines.append("|---:|---:|" + "|".join(["---:"] * len(model_cols)) + "|")

    for bin_key in [f"P{i}" for i in range(1, 11)] + ["10-1"]:
        if bin_key not in table:
            continue
        row = table[bin_key]
        vw = row.get("vw_ret_rf", (np.nan, np.nan))
        line = f"| {bin_key} | {vw[0]:.2f} ({vw[1]:.2f}) |"
        for model in model_cols:
            if "alphas" in row and model in row["alphas"]:
                a, t, n = row["alphas"][model]
                line += f" {a:.2f} ({t:.2f}) |"
            else:
                line += " — |"
        lines.append(line)
    lines.append("")
    lines.append(f"N months per bin (avg): {int(np.mean([row.get('n_months', 0) for row in table.values() if 'n_months' in row]))}")
    return "\n".join(lines)


def main() -> None:
    print("[tables] Loading panel.parquet …")
    panel = pd.read_parquet(PANEL_PATH)
    panel["month"] = pd.to_datetime(panel["month"])
    panel = panel.sort_values(["permno", "month"]).reset_index(drop=True)
    print(f"[tables] Panel: {panel.shape[0]:,} rows × {panel.shape[1]} cols; {panel['month'].nunique()} months")

    print("[tables] Loading FF factors …")
    ff = load_ff_factors()
    ff["month"] = pd.to_datetime(ff["month"])
    print(f"[tables] FF: {ff.shape[0]:,} months")

    # Filter panel to >= 1968-01 (Jan 1968) and <= 2022-12
    panel = panel[(panel["month"] >= "1968-01-01") & (panel["month"] <= "2022-12-31")].copy()

    # Lag ret by 1 month so we measure the next month's return given the
    # current month's MAX/MAX^beta signal (paper convention: one-month-ahead).
    panel = panel.sort_values(["permno", "month"]).reset_index(drop=True)
    panel["ret_fwd"] = panel.groupby("permno")["ret"].shift(-1)

    # Build Table 1 (MAX univariate)
    print("[tables] Building Table 1 (MAX) …")
    t1 = build_decile_table(panel, "max_5", ff, lags=6)
    models = ["CAPM", "FF3", "FFC4", "FF5", "FF6"]
    md = format_table_md("Table 1 — Univariate sorts on MAX (in-sample replication)", t1, {}, models)
    (RESULTS_DIR / "table_1.md").write_text(md)
    print(f"[tables] Wrote {RESULTS_DIR / 'table_1.md'}")

    # Build Table 6 (MAX^beta)
    print("[tables] Building Table 6 (MAX^beta) …")
    p_beta = panel.dropna(subset=["max_5", "beta_m"]).copy()
    print(f"[tables] Beta subset: {p_beta.shape[0]:,} rows × {p_beta.shape[1]} cols; months={p_beta['month'].nunique()}")
    t6 = build_maxbeta_table(panel, ff, lags=6)
    md = format_table_md("Table 6 — MAX^beta portfolio sorts (in-sample replication)", t6, {}, models)
    (RESULTS_DIR / "table_6.md").write_text(md)
    print(f"[tables] Wrote {RESULTS_DIR / 'table_6.md'}")

    # Save tables to JSON for evaluation
    out_json = {"T1": t1, "T6": t6}
    (RESULTS_DIR / "tables_replicated.json").write_text(json.dumps(out_json, default=str, indent=2))

    print("[tables] Done.")


if __name__ == "__main__":
    main()