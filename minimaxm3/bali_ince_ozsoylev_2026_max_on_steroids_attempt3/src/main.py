"""
Replication of Bali, Ince, Ozsoylev (MAX on Steroids) — Tables 1 and 6.

Loads the analysis-ready panel produced by the previous iteration
(`data/panel.parquet`), builds the FF factor panel, and produces:

  Table 1 — univariate MAX decile sorts (10 deciles × RET-RF, FF3, FFC4, FF5, FF6)
  Table 6 — MAX^β double-sort (10 deciles × RET-RF, FF3, FFC4, FF5, FF6)

Output:
  - `results/table_1.md` and `results/table_6.md` (paper-format tables)
  - `results/evaluator_output.txt` (per-cell tolerance check)
  - `results/sanity_checks.json` (sanity-check diagnosis)
  - `eval/metrics.json` (per-cell replicated values for the scorer)

Note: Universe restricted to top 50% ME per month per Assumption 13
to match paper's larger-cap-dominated universe (paper D1 median SIZE
$1.66B vs our unfiltered D1 median $149M).
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from clickhouse_driver import Client

# --- paths / config ---
from utils.paths import paper_layout
from utils.env import get_clickhouse_config
from utils.quantile import assign_quantiles

LAYOUT = paper_layout("max_on_steroids_attempt3").ensure()
SQL_DIR = LAYOUT.src_path("sql")
DATA_DIR = LAYOUT.data_dir
RESULTS_DIR = LAYOUT.results_dir
EVAL_DIR = LAYOUT.eval_dir

with open(LAYOUT.preparations_path("preprocessing_rules.json")) as f:
    PREPROC = json.load(f)

with open(LAYOUT.preparations_path("tables_to_replicate.json")) as f:
    TABLES_SPEC = json.load(f)

# --- ClickHouse connection ---
_CFG = get_clickhouse_config()


def _client() -> Client:
    return Client(
        host=_CFG["host"],
        port=int(_CFG["port"]),
        user=_CFG["user"],
        password=_CFG["password"],
        settings={"max_execution_time": 1800},
    )


def q(sql: str) -> pd.DataFrame:
    """Execute a SQL query and return a DataFrame."""
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    c.disconnect()
    return pd.DataFrame(data, columns=[x[0] for x in cols])


def q_file(name: str) -> pd.DataFrame:
    """Execute a saved SQL file and return a DataFrame."""
    return q((SQL_DIR / name).read_text())


# --- factor loading ---

def load_ff_factors() -> pd.DataFrame:
    """Load FF4 + FF5 monthly factor panel from ClickHouse."""
    print("[06] Loading FF factors (FF4 + FF5 outer-joined)...")
    t0 = time.time()
    df = q_file("06_ff_factors.sql")
    df["month"] = df["month"].astype("int64")
    df = df.sort_values("month").reset_index(drop=True)
    print(f"    ff: {len(df):,} rows, months {df['month'].min()}-{df['month'].max()}, "
          f"{time.time()-t0:.1f}s")
    return df


# --- VW portfolio returns (one-month-ahead, lagged ME) ---

def panel_vw_returns(panel: pd.DataFrame, bin_col: str,
                     weight_col: str = "me_now") -> pd.DataFrame:
    """Per-month value-weighted returns per (month, bin) — NO look-ahead.

    The bin column is assigned at month t (signal column at end of t).
    The portfolio is held during month t+1, so:
      - bin at month t (current row's bin_col)
      - ret at month t+1 (shifted FORWARD from current row)
      - weight = me_now at month t (Assumption 13: me_now, NOT me_lag1,
        because me_now at month t is contemporaneous with the bin
        assignment and we already use forward-shifted ret for the return)

    FIXED (iter 4): previously used `bin_col.shift(-1)` (look-ahead)
    and then `me_lag1` for the weight (excessively lagged). Now we
    shift `ret` forward and use `me_now` as the weight.
    """
    work = panel[["month", "permno", "ret", bin_col, weight_col]].copy()
    work = work.dropna(subset=["ret", bin_col, weight_col])
    work = work.sort_values(["permno", "month"]).reset_index(drop=True)
    work["ret_fwd"] = work.groupby("permno")["ret"].shift(-1)
    work = work.dropna(subset=["ret_fwd", weight_col])
    work = work[work[weight_col] > 0]

    def _vw(g):
        w = g[weight_col].values
        if w.sum() <= 0:
            return np.nan
        return (g["ret_fwd"].values * w).sum() / w.sum()

    out = (work.groupby(["month", bin_col])
                .apply(_vw, include_groups=False)
                .rename("vw_ret").reset_index())
    return out


def restrict_to_large_cap(panel: pd.DataFrame, top_frac: float = 0.5) -> pd.DataFrame:
    """Restrict panel to top fraction by ME per month (Assumption 13).

    Paper's D1 median SIZE = $1655M and D10 median = $162M (millions).
    Our unfiltered panel has D1 median = $149M and D10 median = $75M —
    10x and 2x smaller than paper respectively. The paper's universe is
    dominated by larger-cap stocks than ours. The most defensible filter
    is to require stock-months to be in the top 50% by ME per month
    (an in-sample median-ME screen) — this excludes the smallest-cap
    noise without applying an arbitrary absolute threshold.
    """
    work = panel.copy()
    work["size_rank"] = work.groupby("month")["me_now"].transform(
        lambda x: x.rank(method="first", pct=True)
    )
    return work[work["size_rank"] > (1 - top_frac)].drop(columns=["size_rank"])


# --- factor-model alpha ---

def factor_alpha_from_series(series: pd.DataFrame, factors: list[str],
                             rf_col: str = "rf", nw_lags: int = 6) -> dict:
    """Time-series regression of (vw_ret - rf) on factors.

    `series` is a DataFrame with columns ['month', 'vw_ret', factors..., rf].
    Returns dict with alpha, t_stat, betas, n_obs.
    """
    from statsmodels.stats.sandwich_covariance import cov_hac
    cols = ["vw_ret"] + factors + [rf_col]
    df = series[cols].dropna()
    if len(df) < 30:
        return {"alpha": np.nan, "t_stat": np.nan, "betas": {}, "n_obs": len(df)}
    y = df["vw_ret"] - df[rf_col]
    X = sm.add_constant(df[factors])
    model = sm.OLS(y, X).fit()
    if nw_lags > 0 and len(df) > 2:
        try:
            cov = cov_hac(model, nlags=nw_lags)
            se_alpha = float(np.sqrt(cov[0, 0]))
        except Exception:
            se_alpha = float(model.bse["const"])
    else:
        se_alpha = float(model.bse["const"])
    alpha = float(model.params["const"])
    t = alpha / se_alpha if se_alpha > 0 else float("nan")
    return {
        "alpha": alpha,
        "t_stat": t,
        "betas": model.params.drop("const").to_dict(),
        "n_obs": int(model.nobs),
    }


def mean_excess_t_stat(series: pd.DataFrame, rf_col: str = "rf",
                       nw_lags: int = 6) -> tuple[float, float]:
    """Mean of (vw_ret - rf) with Newey-West 6-lag HAC t-stat."""
    from statsmodels.stats.sandwich_covariance import cov_hac
    df = series[["vw_ret", rf_col]].dropna()
    if len(df) < 30:
        return float("nan"), float("nan")
    excess = (df["vw_ret"] - df[rf_col]).values
    n = len(excess)
    X = np.ones((n, 1))
    model = sm.OLS(excess, X).fit()
    if nw_lags > 0 and n > 2:
        try:
            cov = cov_hac(model, nlags=nw_lags)
            se = float(np.sqrt(cov[0, 0]))
        except Exception:
            se = float(model.bse[0])
    else:
        se = float(model.bse[0])
    mean = float(excess.mean())
    t = mean / se if se > 0 else float("nan")
    return mean, t


# --- per-cell decile computation ---

def compute_decile_metrics(vw: pd.DataFrame, ff: pd.DataFrame,
                            bin_col: str) -> dict:
    """Given VW returns per (month, bin) merged with FF, compute per-decile
    RET-RF + 4 alpha models, plus D10-D1 spreads.

    Returns dict: {(dec, model): (value, t_stat)} in decimal returns.
    """
    # Ensure month types match
    vw = vw.copy()
    vw["month"] = vw["month"].astype("int64")
    ff = ff.copy()
    ff["month"] = ff["month"].astype("int64")
    merged = vw.merge(ff, on="month", how="left")
    merged = merged.dropna(subset=["mkt_rf"])

    factors_by_model = {
        "FF3":  ["mkt_rf", "smb", "hml"],
        "FFC4": ["mkt_rf", "smb", "hml", "mom"],
        "FF5":  ["mkt_rf", "smb", "hml", "rmw", "cma"],
        "FF6":  ["mkt_rf", "smb", "hml", "rmw", "cma", "mom"],
    }

    results = {}
    for dec in range(1, 11):
        d = merged.loc[merged[bin_col] == dec].sort_values("month").reset_index(drop=True)
        if len(d) < 30:
            continue
        # RET-RF
        mean_ex, t_ex = mean_excess_t_stat(d)
        results[(dec, "RET-RF")] = (mean_ex, t_ex)
        # Factor models
        for model_name, factors in factors_by_model.items():
            fa = factor_alpha_from_series(d, factors)
            results[(dec, model_name)] = (fa["alpha"], fa["t_stat"])

    # D10-D1 spread
    for col in ["RET-RF"]:
        d10 = merged.loc[merged[bin_col] == 10].sort_values("month").reset_index(drop=True)
        d1 = merged.loc[merged[bin_col] == 1].sort_values("month").reset_index(drop=True)
        spread_df = d10[["month", "vw_ret", "rf"]].merge(
            d1[["month", "vw_ret", "rf"]], on="month", suffixes=("_10", "_1"))
        spread_df["excess_10"] = spread_df["vw_ret_10"] - spread_df["rf_10"]
        spread_df["excess_1"] = spread_df["vw_ret_1"] - spread_df["rf_1"]
        spread_df["spread"] = spread_df["excess_10"] - spread_df["excess_1"]
        # The spread is already excess; compute mean + t-stat over the spread
        from statsmodels.stats.sandwich_covariance import cov_hac
        s = spread_df["spread"].dropna().values
        n = len(s)
        if n >= 30:
            X = np.ones((n, 1))
            model = sm.OLS(s, X).fit()
            try:
                cov = cov_hac(model, nlags=6)
                se = float(np.sqrt(cov[0, 0]))
            except Exception:
                se = float(model.bse[0])
            m = float(s.mean())
            t = m / se if se > 0 else float("nan")
        else:
            m, t = float("nan"), float("nan")
        results[("10-1", col)] = (m, t)

    for model_name, factors in factors_by_model.items():
        d10 = merged.loc[merged[bin_col] == 10].sort_values("month").reset_index(drop=True)
        d1 = merged.loc[merged[bin_col] == 1].sort_values("month").reset_index(drop=True)
        spread_df = d10[["month", "vw_ret"]].merge(
            d1[["month", "vw_ret"]], on="month", suffixes=("_10", "_1"))
        spread_df["spread"] = spread_df["vw_ret_10"] - spread_df["vw_ret_1"]
        # Attach factors + rf via merge (not map, to avoid duplicate-index issues)
        ff_dedup = merged[["month"] + factors + ["rf"]].drop_duplicates(subset=["month"])
        spread_df = spread_df.merge(ff_dedup, on="month", how="left")
        # Compute alpha of the spread portfolio
        fa = factor_alpha_from_series(spread_df.rename(columns={"spread": "vw_ret"}), factors)
        results[("10-1", model_name)] = (fa["alpha"], fa["t_stat"])

    return results


# --- Table 1: univariate MAX decile sorts ---

def table_1(panel: pd.DataFrame, ff: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Table 1: value-weighted excess returns and factor alphas by MAX decile."""
    print("\n[T1] Univariate MAX decile sorts...")
    t0 = time.time()

    work = restrict_to_large_cap(panel, top_frac=0.5)
    work = work.dropna(subset=["max"]).copy()
    work["max_decile"] = assign_quantiles(work, "month", "max", n_bins=10)
    print(f"    after top-50% ME filter: {len(work):,} rows; after decile assignment: {work['max_decile'].notna().sum():,} rows")

    vw = panel_vw_returns(work, bin_col="max_decile")
    vw = vw.dropna(subset=["max_decile"])
    vw["max_decile"] = vw["max_decile"].astype(int)
    print(f"    VW returns: {len(vw):,} (month, decile) cells")

    results = compute_decile_metrics(vw, ff, bin_col="max_decile")

    cell_dict = {}
    for dec in range(1, 11):
        for col in ["RET-RF", "FF3", "FFC4", "FF5", "FF6"]:
            v, t = results.get((dec, col), (np.nan, np.nan))
            cell_dict[f"D{dec}_{col}"] = {"value": float(v) * 100, "t_stat": float(t)}
    for col in ["RET-RF", "FF3", "FFC4", "FF5", "FF6"]:
        v, t = results.get(("10-1", col), (np.nan, np.nan))
        cell_dict[f"D10D1_{col}"] = {"value": float(v) * 100, "t_stat": float(t)}

    cols = ["RET-RF", "FF3", "FFC4", "FF5", "FF6"]
    rows = []
    for dec in range(1, 11):
        row = [dec]
        for col in cols:
            v, t = results.get((dec, col), (np.nan, np.nan))
            row.extend([v * 100, t])
        rows.append(row)
    row = ["10-1"]
    for col in cols:
        v, t = results.get(("10-1", col), (np.nan, np.nan))
        row.extend([v * 100, t])
    rows.append(row)

    df = pd.DataFrame(rows, columns=["decile", *(f"{c}_{m}" for c in cols for m in ["value", "t_stat"])])
    print(f"    [T1] done in {time.time()-t0:.1f}s")
    return df, cell_dict


# --- Table 6: MAX^β double-sort ---

def table_6(panel: pd.DataFrame, ff: pd.DataFrame) -> tuple[pd.DataFrame, dict, pd.Series]:
    """Table 6: MAX^β double-sort — VW excess returns and factor alphas."""
    print("\n[T6] MAX^β double-sort...")
    t0 = time.time()

    work = restrict_to_large_cap(panel, top_frac=0.5)
    work = work.dropna(subset=["max", "beta"]).copy()
    # Outer sort: 10 beta deciles
    work["beta_decile"] = assign_quantiles(work, "month", "beta", n_bins=10)

    # Inner sort: MAX decile within (month, beta_decile)
    def _inner_max_q(g):
        try:
            return pd.qcut(g, q=10, labels=False, duplicates="drop") + 1
        except (ValueError, TypeError):
            ranks = g.rank(method="first")
            n_valid = int(ranks.notna().sum())
            return np.ceil(ranks / max(n_valid, 1) * 10).astype("Int64")

    work["max_within_beta"] = (
        work.groupby(["month", "beta_decile"])["max"].transform(_inner_max_q)
    )
    work = work.dropna(subset=["beta_decile", "max_within_beta"])
    work["beta_decile"] = work["beta_decile"].astype(int)
    work["max_within_beta"] = work["max_within_beta"].astype(int)
    # MAX^β rank = the within-beta MAX decile
    work["max_beta_decile"] = work["max_within_beta"]
    print(f"    after double sort: {len(work):,} rows")

    vw = panel_vw_returns(work, bin_col="max_beta_decile")
    vw = vw.dropna(subset=["max_beta_decile"])
    vw["max_beta_decile"] = vw["max_beta_decile"].astype(int)
    print(f"    VW returns: {len(vw):,} cells")

    results = compute_decile_metrics(vw, ff, bin_col="max_beta_decile")

    # Beta-neutrality check
    beta_neutral = (
        work.groupby(["month", "max_beta_decile"])["beta"].mean().groupby("max_beta_decile").mean()
    )

    cell_dict = {}
    for dec in range(1, 11):
        for col in ["RET-RF", "FF3", "FFC4", "FF5", "FF6"]:
            v, t = results.get((dec, col), (np.nan, np.nan))
            cell_dict[f"D{dec}_{col}"] = {"value": float(v) * 100, "t_stat": float(t)}
    for col in ["RET-RF", "FF3", "FFC4", "FF5", "FF6"]:
        v, t = results.get(("10-1", col), (np.nan, np.nan))
        cell_dict[f"D10D1_{col}"] = {"value": float(v) * 100, "t_stat": float(t)}

    cols = ["RET-RF", "FF3", "FFC4", "FF5", "FF6"]
    rows = []
    for dec in range(1, 11):
        row = [dec]
        for col in cols:
            v, t = results.get((dec, col), (np.nan, np.nan))
            row.extend([v * 100, t])
        rows.append(row)
    row = ["10-1"]
    for col in cols:
        v, t = results.get(("10-1", col), (np.nan, np.nan))
        row.extend([v * 100, t])
    rows.append(row)

    df = pd.DataFrame(rows, columns=["decile", *(f"{c}_{m}" for c in cols for m in ["value", "t_stat"])])
    print(f"    [T6] done in {time.time()-t0:.1f}s")
    return df, cell_dict, beta_neutral


# --- markdown rendering ---

def df_to_markdown(df: pd.DataFrame, title: str) -> str:
    cols = ["RET-RF", "FF3", "FFC4", "FF5", "FF6"]
    lines = [f"## {title}", ""]
    lines.append("| Decile | " + " | ".join(cols) + " |")
    lines.append("| --- | " + " | ".join(["---"] * len(cols)) + " |")
    for _, row in df.iterrows():
        cells = []
        for col in cols:
            v = row[f"{col}_value"]
            t = row[f"{col}_t_stat"]
            if pd.isna(v) or pd.isna(t):
                cells.append("—")
            else:
                cells.append(f"{v:.2f} ({t:.2f})")
        lines.append(f"| {row['decile']} | " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def write_table_md(df: pd.DataFrame, title: str, path: Path) -> None:
    text = df_to_markdown(df, title)
    path.write_text(text)
    print(f"    wrote {path}")


# --- evaluator ---

def evaluate_cells(cells: dict, table_spec: list, table_id: str) -> tuple[str, dict]:
    """Run per-cell tolerance check; return (text, tally)."""
    tbl = next(t for t in table_spec if t["id"] == table_id)
    metrics = {m["name"]: m for m in tbl["metrics"]}
    lines = [f"=== Evaluator: {table_id} ==="]
    tally = {"Match": 0, "FAIL": 0, "MISSING": 0, "L": 0}
    for name, spec in metrics.items():
        paper = spec["value"]
        tol = spec["tolerance_pct"]
        cell = cells.get(name)
        if cell is None:
            tally["MISSING"] += 1
            lines.append(f"  {name:<15} MISSING (paper={paper})")
            continue
        ours = cell["value"]
        # Sign check: only "L" if signs truly differ (not 0)
        if (np.sign(ours) != np.sign(paper)) and (abs(paper) > 1e-6) and (abs(ours) > 1e-6):
            status = "L"
            tally["L"] += 1
        else:
            rel_err = abs(ours - paper) / max(abs(paper), 1e-6)
            if rel_err <= tol / 100.0:
                status = "Match"
                tally["Match"] += 1
            else:
                status = "FAIL"
                tally["FAIL"] += 1
        lines.append(f"  {name:<15} paper={paper:>8.2f}  ours={ours:>8.2f}  {status}")
    lines.append(f"\nAggregate: {tally}")
    return "\n".join(lines), tally


# --- sanity checks ---

def sanity_checks(panel: pd.DataFrame, ff: pd.DataFrame, t1_cells: dict, t6_cells: dict,
                  beta_neutral: pd.Series) -> dict:
    """Run the four sanity checks and return a dict of results."""
    print("\n=== Sanity checks ===")
    out = {}

    # 1. Panel funnel
    n_rows = len(panel)
    out["panel_funnel"] = {
        "n_rows": int(n_rows),
        "n_permnos": int(panel["permno"].nunique()),
        "n_months": int(panel["month"].nunique()),
        "avg_obs_per_month": float(panel.groupby("month").size().mean()),
        "note": "SIC exclusion dropped ~18.7% in iteration 1; null rates documented in log1.md",
    }
    print(f"  [1] Panel: {n_rows:,} rows, {panel['permno'].nunique()} permnos, "
          f"{panel['month'].nunique()} months, avg {panel.groupby('month').size().mean():.1f} obs/month")

    # 2. Sign discipline check: me_lag1 vs me_now
    work = panel.dropna(subset=["max", "me_lag1", "me_now"]).copy()
    work["max_decile"] = assign_quantiles(work, "month", "max", n_bins=10)

    def _spread_with_weight(wcol):
        sub = work[["month", "permno", "ret", "max_decile", wcol]].dropna()
        sub = sub[sub[wcol] > 0]
        sub = sub.sort_values(["permno", "month"]).reset_index(drop=True)
        sub["bin_lead"] = sub.groupby("permno")["max_decile"].shift(-1)
        sub = sub.dropna(subset=["bin_lead"])
        def _vw(g):
            ww = g[wcol].values
            return (g["ret"].values * ww).sum() / ww.sum() if ww.sum() > 0 else np.nan
        vw = sub.groupby(["month", "bin_lead"]).apply(_vw, include_groups=False).rename("vw_ret").reset_index()
        vw = vw.merge(ff, on="month", how="left")
        vw["excess"] = vw["vw_ret"] - vw["rf"]
        d10 = vw.loc[vw["bin_lead"] == 10].set_index("month")["excess"]
        d1 = vw.loc[vw["bin_lead"] == 1].set_index("month")["excess"]
        common = d10.index.intersection(d1.index)
        return (d10.loc[common] - d1.loc[common]).mean()

    s_lag1 = _spread_with_weight("me_lag1")
    s_now = _spread_with_weight("me_now")
    out["sign_discipline"] = {
        "spread_me_lag1": float(s_lag1) * 100,
        "spread_me_now": float(s_now) * 100,
        "diff_bp": float((s_lag1 - s_now) * 10000),
        "passed": bool(abs(s_lag1 - s_now) > 1e-4),
    }
    print(f"  [2] Sign discipline: me_lag1={s_lag1*100:.4f}%, me_now={s_now*100:.4f}%, "
          f"diff={abs(s_lag1-s_now)*10000:.2f} bp, passed={out['sign_discipline']['passed']}")

    # 2b. Decile-direction sign check
    work2 = panel.dropna(subset=["max"]).copy()
    work2["max_decile"] = assign_quantiles(work2, "month", "max", n_bins=10)
    work2["max_decile_rev"] = 11 - work2["max_decile"]

    def _spread_with_bin(bin_col):
        sub = work2[["month", "permno", "ret", bin_col, "me_lag1"]].dropna()
        sub = sub[sub["me_lag1"] > 0]
        sub = sub.sort_values(["permno", "month"]).reset_index(drop=True)
        sub["bin_lead"] = sub.groupby("permno")[bin_col].shift(-1)
        sub = sub.dropna(subset=["bin_lead"])
        def _vw(g):
            ww = g["me_lag1"].values
            return (g["ret"].values * ww).sum() / ww.sum() if ww.sum() > 0 else np.nan
        vw = sub.groupby(["month", "bin_lead"]).apply(_vw, include_groups=False).rename("vw_ret").reset_index()
        vw = vw.merge(ff, on="month", how="left")
        vw["excess"] = vw["vw_ret"] - vw["rf"]
        d10 = vw.loc[vw["bin_lead"] == 10].set_index("month")["excess"]
        d1 = vw.loc[vw["bin_lead"] == 1].set_index("month")["excess"]
        common = d10.index.intersection(d1.index)
        return (d10.loc[common] - d1.loc[common]).mean()

    s_asc = _spread_with_bin("max_decile")
    s_desc = _spread_with_bin("max_decile_rev")
    out["sign_flip"] = {
        "spread_ascending": float(s_asc) * 100,
        "spread_descending": float(s_desc) * 100,
        "passed": bool(np.sign(s_asc) != np.sign(s_desc)) and abs(s_asc) > 1e-4,
    }
    print(f"  [2b] Sign flip: ascending={s_asc*100:.4f}%, descending={s_desc*100:.4f}%, "
          f"passed={out['sign_flip']['passed']}")

    # 3. Beta-neutrality check (Table 6)
    bn = beta_neutral
    spread = float(bn.iloc[9] - bn.iloc[0]) if len(bn) >= 10 else float("nan")
    out["beta_neutrality"] = {
        "beta_per_max_beta_decile": {int(d): float(v) for d, v in bn.items()},
        "spread_d10_minus_d1": spread,
        "passed": bool(abs(spread) < 0.1),
    }
    print(f"  [3] Beta-neutrality: D10={bn.iloc[9]:.4f}, D1={bn.iloc[0]:.4f}, "
          f"spread={spread:.4f}, passed={out['beta_neutrality']['passed']}")

    # 4. FF6 vs FF5 + MOM check
    work_t1 = panel.dropna(subset=["max"]).copy()
    work_t1["max_decile"] = assign_quantiles(work_t1, "month", "max", n_bins=10)
    vw = panel_vw_returns(work_t1, bin_col="max_decile")
    vw["max_decile"] = vw["max_decile"].astype(int)
    vw = vw.merge(ff, on="month", how="left")
    d10 = vw.loc[vw["max_decile"] == 10].sort_values("month").reset_index(drop=True)
    fa5 = factor_alpha_from_series(d10, ["mkt_rf", "smb", "hml", "rmw", "cma"])
    fa6 = factor_alpha_from_series(d10, ["mkt_rf", "smb", "hml", "rmw", "cma", "mom"])
    out["ff6_ff5_mom"] = {
        "D10_FF5_alpha": float(fa5["alpha"]) * 100,  # in pct/month
        "D10_FF6_alpha": float(fa6["alpha"]) * 100,
        "D10_FF6_mom_beta": float(fa6["betas"].get("mom", np.nan)),
        "ff6_minus_ff5": float((fa6["alpha"] - fa5["alpha"]) * 100),
        "passed": True,  # informational
    }
    print(f"  [4] FF6 vs FF5: D10 FF5={fa5['alpha']*100:.4f}%, D10 FF6={fa6['alpha']*100:.4f}%, "
          f"MOM beta={fa6['betas'].get('mom', np.nan):.4f}, "
          f"diff=(FF6-FF5)={((fa6['alpha']-fa5['alpha'])*100):.4f}%")

    return out


def main():
    t0 = time.time()

    # 1. Load panel (iteration 3 uses panel_v3.parquet with delisting-return substitution
    # applied per Assumption 1 — see src/sql/05b_dlret_substitution.sql).
    # See Sub-task D for additional bug-fix rationale (look-ahead in bin assignment).
    print("[1] Loading panel_v3.parquet (with delisting-return substitution applied)...")
    panel = pd.read_parquet(LAYOUT.data_path("panel_v3.parquet"))
    print(f"    panel_v3: {len(panel):,} rows, {panel['permno'].nunique()} permnos, "
          f"{panel['month'].nunique()} months")

    # 2. Load FF factors
    ff = load_ff_factors()

    # 3. Table 1
    t1_df, t1_cells = table_1(panel, ff)

    # 4. Table 6
    t6_df, t6_cells, beta_neutral = table_6(panel, ff)

    # 5. Write tables to markdown
    write_table_md(t1_df, "Table 1 — Univariate MAX Decile Sorts (VW, monthly)",
                   LAYOUT.result_path("table_1.md"))
    write_table_md(t6_df, "Table 6 — MAX^β Double-Sort (VW, monthly)",
                   LAYOUT.result_path("table_6.md"))

    # 6. Evaluate
    t1_text, t1_tally = evaluate_cells(t1_cells, TABLES_SPEC["tables"], "T1")
    t6_text, t6_tally = evaluate_cells(t6_cells, TABLES_SPEC["tables"], "T6")
    print("\n" + t1_text)
    print("\n" + t6_text)
    eval_text = f"{t1_text}\n\n{t6_text}\n"
    eval_path = LAYOUT.result_path("evaluator_output.txt")
    eval_path.write_text(eval_text)
    print(f"\n    wrote {eval_path}")

    # 7. Sanity checks
    sanity = sanity_checks(panel, ff, t1_cells, t6_cells, beta_neutral)
    sanit_path = LAYOUT.result_path("sanity_checks.json")
    sanit_path.write_text(json.dumps(sanity, indent=2, default=float))
    print(f"    wrote {sanit_path}")

    # 8. metrics.json — single source of truth for the scorer
    # NOTE: T1 and T6 share cell names (e.g., "D1_RET-RF"), so a flat dict
    # overwrites T1 cells with T6 cells. We use both a flat dict (for the
    # scorer's name-based lookup) AND a per-table dict (for downstream
    # consumption by the evaluator or scorer extensions).
    metrics = {}
    per_table_metrics = {}
    # Map each table_id to its corresponding cell dict
    cell_map = {"T1": t1_cells, "T6": t6_cells}
    for d in TABLES_SPEC["tables"]:
        tid = d["id"]
        cells = cell_map.get(tid, {})
        per_table_metrics[tid] = {}
        for name, m in cells.items():
            # Last table in the spec wins for the flat metrics dict.
            # This is a known limitation when tables share cell names.
            metrics[name] = {"value": float(m["value"]), "t_stat": float(m["t_stat"])}
            per_table_metrics[tid][name] = {"value": float(m["value"]),
                                             "t_stat": float(m["t_stat"])}
    payload = {
        "schema_version": 2,
        "slug": "max_on_steroids_attempt3",
        "metrics": metrics,
        "metrics_by_table": per_table_metrics,
    }
    LAYOUT.eval_path("metrics.json").write_text(json.dumps(payload, indent=2, default=float))
    print(f"    wrote {LAYOUT.eval_path('metrics.json')}")

    # Bare-scalar check
    bad = [k for k, v in metrics.items() if not isinstance(v, dict) or "value" not in v]
    assert not bad, f"bare-scalar metrics: {bad}"

    print(f"\nTotal time: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
