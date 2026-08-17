"""
Weber (2018) "Cash flow duration and the term structure of equity returns"
Table 2 — Decile-sorted portfolio performance.

Panel A: Mean excess returns, CAPM betas, CAPM alphas
Panel B: Sharpe ratios

Methodology (per the paper / Replicator's spec):
  - At end of June each year t (1963..2013), sort stocks into 10 deciles
    based on `dur` (cash-flow duration, capped at 50).
  - Hold for 12 months (July t - June t+1).
  - Equal-weighted within each decile.
  - Excess returns = portfolio return - 1-month T-bill rate (RF from FF).
  - Mean excess returns = time-series average over months 1963-07..2014-06.
  - Standard errors = OLS standard errors of the mean (HC0).
  - Factor regressions: r_excess = alpha + beta * Mkt-RF (CAPM), HC0.

Outputs:
  results/table_2.md — markdown table matching the paper's Table 2 layout
  results/table_2_summary.json — numeric dump for downstream comparison
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

from utils.paths import paper_layout


# ---- Configuration ---------------------------------------------------------
SLUG = "weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns"
LAYOUT = paper_layout(SLUG)
DATA_DIR = LAYOUT.data_path("")
RESULTS_DIR = LAYOUT.result_path("")

# Sample period for the time-series regressions (paper §2 L176)
SAMPLE_START = pd.Timestamp("1963-07-01")
SAMPLE_END   = pd.Timestamp("2014-06-30")

N_BINS = 10  # deciles


# ---- Loaders ---------------------------------------------------------------
def load_panels() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the three cached parquets."""
    panel_annual = pd.read_parquet(DATA_DIR / "panel_annual.parquet")
    panel_monthly = pd.read_parquet(DATA_DIR / "panel_monthly.parquet")
    panel_monthly["month_date"] = pd.to_datetime(panel_monthly["month_date"])
    ff = pd.read_parquet(DATA_DIR / "ff_factors.parquet")
    ff["dt"] = pd.to_datetime(ff["dt"])
    return panel_annual, panel_monthly, ff


# ---- Decile assignment (within each sort_year) -----------------------------
def assign_deciles(panel_annual: pd.DataFrame) -> pd.DataFrame:
    """Assign 1..10 decile labels within each sort_year based on `dur`.

    Uses all-stocks breakpoints (paper does not specify NYSE-only).
    """
    from utils.quantile import assign_quantiles

    df = panel_annual.copy()
    df["decile"] = assign_quantiles(
        df, date_col="sort_year", signal_col="dur", n_bins=N_BINS,
        warn_fallback=False,
    )
    return df


# ---- Per-decile EW returns -------------------------------------------------
def compute_decile_returns(
    panel_annual: pd.DataFrame,
    panel_monthly: pd.DataFrame,
    ff: pd.DataFrame,
) -> pd.DataFrame:
    """Compute per-decile, per-month EW portfolio returns.

    Steps:
      1. Attach the decile label (per sort_year) to each monthly stock row.
      2. For each (month, decile), compute the EW mean of ret_adj.
      3. Merge with the FF factor `rf` to form excess returns.
      4. Restrict to the holding window: months with sort_year >= 1963 and
         month_date <= 2014-06-30.

    Returns:
        DataFrame with columns [month_date, decile, ret, rf, ret_excess].
    """
    # 1. Attach decile label
    sort_map = panel_annual[["permno", "sort_year", "decile"]].dropna(
        subset=["decile"]
    )
    sort_map["decile"] = sort_map["decile"].astype(int)

    df = panel_monthly.merge(
        sort_map, on=["permno", "sort_year"], how="inner",
    )

    # 2. Per-decile EW returns (per month)
    #    Need rf from FF before grouping by decile; left join ff on (year, month)
    ff_join = ff[["year", "month", "rf", "mkt_rf"]].copy()
    df = df.merge(ff_join, on=["year", "month"], how="left")

    # Coerce rf to float
    df["rf"] = df["rf"].astype(float)
    df["mkt_rf"] = df["mkt_rf"].astype(float)

    # 3. EW portfolio returns per (month_date, decile)
    grp = df.groupby(["month_date", "decile"], as_index=False).agg(
        ret=("ret_adj", "mean"),
        rf=("rf", "first"),
        n_stocks=("ret_adj", "size"),
    )
    grp["ret_excess"] = grp["ret"] - grp["rf"]

    # 4. Apply the sample period for the time-series (1963-07..2014-06)
    mask = (grp["month_date"] >= SAMPLE_START) & (grp["month_date"] <= SAMPLE_END)
    grp = grp.loc[mask].copy()

    # Restrict to complete months: 1963-07..2014-06 = 612 months
    return grp


# ---- Annual diagnostics ----------------------------------------------------
def annual_diagnostics(
    panel_annual: pd.DataFrame,
) -> pd.DataFrame:
    """Per-(sort_year, decile) stock counts and average duration."""
    g = (
        panel_annual.dropna(subset=["decile"])
        .groupby(["sort_year", "decile"], as_index=False)
        .agg(
            n_stocks=("permno", "size"),
            dur_mean=("dur", "mean"),
        )
    )
    return g


# ---- Table 2 Panel A: mean excess returns, CAPM betas, CAPM alphas ---------
def build_panel_a(decile_rets: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Construct Panel A: per-decile mean excess return, CAPM beta, alpha.

    Returns:
        (panel_a_df, raw_results_dict)
    """
    raw = {}
    rows = []
    months = (
        decile_rets["month_date"].sort_values().unique()
    )  # for the empty-spread check

    for decile in list(range(1, N_BINS + 1)) + ["D1-D10"]:
        if decile == "D1-D10":
            # Build the spread series (month-aligned)
            d1 = decile_rets[decile_rets["decile"] == 1].set_index("month_date")
            d10 = decile_rets[decile_rets["decile"] == 10].set_index("month_date")
            common = d1.index.intersection(d10.index)
            r_excess = (d1.loc[common, "ret"] - d10.loc[common, "ret"])  # zero cost, no rf
            r_excess.name = "ret_excess"
            x_label = "D1-D10"
        else:
            sub = decile_rets[decile_rets["decile"] == decile].set_index("month_date")
            r_excess = sub["ret_excess"].copy()
            x_label = f"D{decile}"

        # Cap to the sample period
        r_excess = r_excess.sort_index()
        r_excess = r_excess.loc[
            (r_excess.index >= SAMPLE_START) & (r_excess.index <= SAMPLE_END)
        ]
        n_obs = r_excess.notna().sum()

        # Mean excess return (monthly, in percent)
        mean_excess = r_excess.mean() * 100.0
        # SE of the mean (HC0)
        X_const = np.ones((len(r_excess), 1))
        model_mean = sm.OLS(r_excess.values, X_const).fit(cov_type="HC0")
        se_mean = model_mean.bse[0] * 100.0
        t_mean = model_mean.tvalues[0]

        # CAPM beta: regress r_excess on Mkt-RF
        # Pull Mkt-RF for the same months
        ff = pd.read_parquet(DATA_DIR / "ff_factors.parquet")
        ff["dt"] = pd.to_datetime(ff["dt"])
        ff_idx = ff.set_index("dt")[["mkt_rf"]]
        # Make sure index is month-end
        ff_idx = ff_idx[~ff_idx.index.duplicated(keep="first")]

        # Match indexes (use year/month)
        ff_idx = ff_idx.copy()
        ff_idx["year"] = ff_idx.index.year
        ff_idx["month"] = ff_idx.index.month
        rdf = pd.DataFrame({"ret_excess": r_excess.values,
                            "month_date": r_excess.index})
        rdf["year"] = rdf["month_date"].dt.year
        rdf["month"] = rdf["month_date"].dt.month

        merged = rdf.merge(
            ff_idx[["year", "month", "mkt_rf"]],
            on=["year", "month"], how="left",
        )
        merged = merged.dropna(subset=["ret_excess", "mkt_rf"])

        y = merged["ret_excess"].values
        X = sm.add_constant(merged["mkt_rf"].values)  # [const, beta]
        model_capm = sm.OLS(y, X).fit(cov_type="HC0")
        alpha = model_capm.params[0] * 100.0  # pct per month
        beta = model_capm.params[1]
        se_alpha = model_capm.bse[0] * 100.0
        se_beta = model_capm.bse[1]
        t_alpha = model_capm.tvalues[0]
        t_beta = model_capm.tvalues[1]
        r2 = model_capm.rsquared

        raw[x_label] = {
            "n_obs": int(n_obs),
            "mean_excess_pct": float(mean_excess),
            "se_mean_pct": float(se_mean),
            "t_mean": float(t_mean),
            "alpha_pct": float(alpha),
            "se_alpha_pct": float(se_alpha),
            "t_alpha": float(t_alpha),
            "beta": float(beta),
            "se_beta": float(se_beta),
            "t_beta": float(t_beta),
            "r2": float(r2),
        }

        rows.append({
            "decile": x_label,
            "mean_excess": mean_excess,
            "se_mean": se_mean,
            "t_mean": t_mean,
            "beta": beta,
            "se_beta": se_beta,
            "t_beta": t_beta,
            "alpha": alpha,
            "se_alpha": se_alpha,
            "t_alpha": t_alpha,
            "r2": r2,
            "n_obs": n_obs,
        })

    panel_a = pd.DataFrame(rows)
    return panel_a, raw


# ---- Table 2 Panel B: Sharpe ratios ----------------------------------------
def build_panel_b(decile_rets: pd.DataFrame) -> pd.DataFrame:
    """Construct Panel B: per-decile Sharpe ratio = mean(excess) / std(excess)."""
    rows = []
    for decile in list(range(1, N_BINS + 1)) + ["D1-D10"]:
        if decile == "D1-D10":
            d1 = decile_rets[decile_rets["decile"] == 1].set_index("month_date")
            d10 = decile_rets[decile_rets["decile"] == 10].set_index("month_date")
            common = d1.index.intersection(d10.index)
            r_excess = (d1.loc[common, "ret"] - d10.loc[common, "ret"])
            x_label = "D1-D10"
        else:
            sub = decile_rets[decile_rets["decile"] == decile].set_index("month_date")
            r_excess = sub["ret_excess"].copy()
            x_label = f"D{decile}"

        r_excess = r_excess.sort_index()
        r_excess = r_excess.loc[
            (r_excess.index >= SAMPLE_START) & (r_excess.index <= SAMPLE_END)
        ]
        sharpe = r_excess.mean() / r_excess.std() if r_excess.std() > 0 else np.nan
        rows.append({"decile": x_label, "sharpe": sharpe, "n_obs": r_excess.notna().sum()})
    return pd.DataFrame(rows)


# ---- Markdown output -------------------------------------------------------
def to_markdown(panel_a: pd.DataFrame, panel_b: pd.DataFrame) -> str:
    """Format Panel A + Panel B as a single markdown table."""
    # ---- Panel A ----
    md = []
    md.append("# Weber (2018) — Table 2: Decile-Sorted Portfolio Performance")
    md.append("")
    md.append("Sample period: July 1963 - June 2014 (612 months).")
    md.append("Sort: 10 deciles of equal-weighted cash-flow duration at end of June t.")
    md.append("Hold: 12 months (July t - June t+1).")
    md.append("Excess returns: portfolio return - 1-month T-bill rate (FF `rf`).")
    md.append("Standard errors: HC0 (heteroskedasticity-robust).")
    md.append("Regressions: monthly time-series in percent.")
    md.append("")
    md.append("## Panel A: Mean excess return, CAPM beta, CAPM alpha")
    md.append("")
    md.append("| Decile | Mean excess (%, monthly) | SE mean | t_mean | Beta vs Mkt-RF | SE beta | t_beta | Alpha (%, monthly) | SE alpha | t_alpha | R² | N months |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for _, r in panel_a.iterrows():
        md.append(
            f"| {r['decile']} | "
            f"{r['mean_excess']:.3f} | {r['se_mean']:.3f} | {r['t_mean']:.2f} | "
            f"{r['beta']:.3f} | {r['se_beta']:.3f} | {r['t_beta']:.2f} | "
            f"{r['alpha']:.3f} | {r['se_alpha']:.3f} | {r['t_alpha']:.2f} | "
            f"{r['r2']:.3f} | {int(r['n_obs'])} |"
        )

    md.append("")
    md.append("## Panel B: Sharpe ratio")
    md.append("")
    md.append("| Decile | Sharpe ratio (monthly) | N months |")
    md.append("|---|---|---|")
    for _, r in panel_b.iterrows():
        md.append(
            f"| {r['decile']} | {r['sharpe']:.3f} | {int(r['n_obs'])} |"
        )

    return "\n".join(md)


# ---- Main ------------------------------------------------------------------
def main():
    t0 = time.time()
    print(f"[table2] SLUG: {SLUG}")
    print(f"[table2] Loading panels...")

    panel_annual, panel_monthly, ff = load_panels()
    print(f"  -> panel_annual: {len(panel_annual):,} rows")
    print(f"  -> panel_monthly: {len(panel_monthly):,} rows")
    print(f"  -> ff_factors: {len(ff):,} rows")

    # Annual diagnostics
    print("[table2] Assigning deciles within each sort_year...")
    panel_annual = assign_deciles(panel_annual)
    ann = annual_diagnostics(panel_annual)
    print(f"  -> {len(ann):,} (sort_year, decile) combinations")
    print(f"  -> Mean n_stocks per sort_year (avg across deciles): "
          f"{ann.groupby('sort_year')['n_stocks'].sum().mean():.0f}")
    print(f"  -> Mean n_stocks per (sort_year, decile): "
          f"{ann['n_stocks'].mean():.1f}")
    print(f"  -> Min/max n_stocks per (sort_year, decile): "
          f"{ann['n_stocks'].min()} / {ann['n_stocks'].max()}")

    # Per-decile returns
    print("[table2] Computing per-decile EW returns (per month)...")
    decile_rets = compute_decile_returns(panel_annual, panel_monthly, ff)
    print(f"  -> {len(decile_rets):,} (month, decile) rows")
    print(f"  -> Month range: {decile_rets['month_date'].min()} .. "
          f"{decile_rets['month_date'].max()}")
    print(f"  -> Distinct months: {decile_rets['month_date'].nunique()}")
    print(f"  -> Distinct deciles: {sorted(decile_rets['decile'].unique())}")

    # Panel A
    print("[table2] Building Panel A (mean excess returns, CAPM beta, alpha)...")
    panel_a, raw_a = build_panel_a(decile_rets)
    print(panel_a.to_string(index=False))

    # Panel B
    print("[table2] Building Panel B (Sharpe ratios)...")
    panel_b = build_panel_b(decile_rets)
    print(panel_b.to_string(index=False))

    # ---- Summary stats ----
    print()
    print("[table2] ==== Top-line summary ====")
    d1d10 = raw_a["D1-D10"]
    print(f"D1-D10 excess return: {d1d10['mean_excess_pct']:.3f}% per month "
          f"(SE = {d1d10['se_mean_pct']:.3f}, t = {d1d10['t_mean']:.2f})")
    print(f"D1-D10 CAPM alpha:    {d1d10['alpha_pct']:.3f}% per month "
          f"(SE = {d1d10['se_alpha_pct']:.3f}, t = {d1d10['t_alpha']:.2f})")
    print(f"D1-D10 beta:          {d1d10['beta']:.3f} (SE = {d1d10['se_beta']:.3f})")
    print(f"D1-D10 R²:            {d1d10['r2']:.3f}")
    print(f"D1-D10 N months:      {d1d10['n_obs']}")

    # ---- Write outputs ----
    md = to_markdown(panel_a, panel_b)
    out_md = RESULTS_DIR / "table_2.md"
    out_md.write_text(md)
    print(f"\n[table2] Wrote {out_md}")

    # Numeric dump for downstream
    out_json = RESULTS_DIR / "table_2_summary.json"
    out_json.write_text(json.dumps({
        "panel_a": raw_a,
        "panel_b": {r["decile"]: {"sharpe": float(r["sharpe"]),
                                    "n_obs": int(r["n_obs"])}
                    for _, r in panel_b.iterrows()},
        "annual_diagnostics": {
            "mean_n_stocks_per_decile_year": float(ann["n_stocks"].mean()),
            "min_n_stocks_per_decile_year": int(ann["n_stocks"].min()),
            "max_n_stocks_per_decile_year": int(ann["n_stocks"].max()),
            "mean_n_stocks_per_year": float(ann.groupby('sort_year')['n_stocks'].sum().mean()),
            "n_sort_years": int(panel_annual["sort_year"].nunique()),
            "n_deciles": int(panel_annual["decile"].dropna().nunique()),
            "sample_period": {
                "start": "1963-07-01",
                "end": "2014-06-30",
                "n_months": 612,
            },
        },
    }, indent=2))
    print(f"[table2] Wrote {out_json}")

    print(f"\n[table2] Total elapsed: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
