"""
Weber (2018) "Cash flow duration and the term structure of equity returns"
Table 3 — Fama-French 3-factor, 4-factor (adding MOM), and 5-factor (adding
RMW and CMA) alphas for the 10-duration deciles.

Methodology (per the paper / Replicator's spec):
  - At end of June each year t (1963..2013), sort stocks into 10 deciles
    based on `dur` (cash-flow duration).
  - Hold for 12 months (July t - June t+1).
  - Equal-weighted within each decile.
  - Excess returns = portfolio return - 1-month T-bill rate (rf from FF).
  - For each portfolio (D1..D10 and D1-D10 spread):
    - Regress r_excess[t] on FF3 = [mkt_rf, smb, hml]
    - Regress r_excess[t] on FF4 = [mkt_rf, smb, hml, mom]
    - Regress r_excess[t] on FF5 = [mkt_rf, smb, hml, rmw, cma]
  - Standard errors = HC0 (heteroskedasticity-robust).
  - Sample period: 1963-07 to 2014-06 (612 months).

Paper targets:
  - D1-D10: FF3 alpha = 0.84, FF4 alpha = 0.66, FF5 alpha = 0.48 (% per month)
  - D1 FF3 alpha = 0.46, D10 FF3 alpha = -0.38

Outputs:
  results/table_3.md — markdown table matching the paper's Table 3 layout.
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

from utils.paths import paper_layout
from utils.quantile import assign_quantiles


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
    """Assign 1..10 decile labels within each sort_year based on `dur`."""
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
    """Compute per-decile, per-month EW portfolio returns, joined to FF factors.

    Returns:
        DataFrame with columns [month_date, year, month, decile, ret, rf, mkt_rf,
        smb, hml, mom, rmw, cma, ret_excess].
    """
    sort_map = panel_annual[["permno", "sort_year", "decile"]].dropna(
        subset=["decile"]
    )
    sort_map["decile"] = sort_map["decile"].astype(int)

    df = panel_monthly.merge(
        sort_map, on=["permno", "sort_year"], how="inner",
    )
    print(f"  -> After sort_map merge: {len(df):,} rows")

    # Join with FF factors (using year/month, since panel_monthly and FF
    # already use year/month columns)
    ff_join = ff[["year", "month", "rf", "mkt_rf", "smb", "hml", "mom", "rmw", "cma"]].copy()
    df = df.merge(ff_join, on=["year", "month"], how="left")
    print(f"  -> After FF merge: {len(df):,} rows")

    # Coerce factors to float
    for col in ["rf", "mkt_rf", "smb", "hml", "mom", "rmw", "cma"]:
        df[col] = df[col].astype(float)

    # EW portfolio returns per (month_date, decile)
    grp = df.groupby(["month_date", "year", "month", "decile"], as_index=False).agg(
        ret=("ret_adj", "mean"),
        rf=("rf", "first"),
        mkt_rf=("mkt_rf", "first"),
        smb=("smb", "first"),
        hml=("hml", "first"),
        mom=("mom", "first"),
        rmw=("rmw", "first"),
        cma=("cma", "first"),
        n_stocks=("ret_adj", "size"),
    )
    grp["ret_excess"] = grp["ret"] - grp["rf"]

    # Apply sample period
    mask = (grp["month_date"] >= SAMPLE_START) & (grp["month_date"] <= SAMPLE_END)
    grp = grp.loc[mask].copy()
    return grp


# ---- Regression -----------------------------------------------------------
def run_factor_regression(
    r_excess: pd.Series,
    factors: pd.DataFrame,
    model_name: str,
) -> dict:
    """Run factor regression and return alpha, SE, t-stat.

    Parameters
    ----------
    r_excess : pd.Series indexed by month_date
    factors : DataFrame indexed by month_date with factor columns
    """
    merged = pd.concat([r_excess.rename("ret_excess"), factors], axis=1).dropna()
    y = merged["ret_excess"]
    X = sm.add_constant(merged[factors.columns])
    model = sm.OLS(y, X).fit(cov_type="HC0")
    alpha = model.params["const"] * 100.0  # pct per month
    se_alpha = model.bse["const"] * 100.0
    t_alpha = model.tvalues["const"]
    n_obs = int(model.nobs)
    return {
        "alpha_pct": float(alpha),
        "se_alpha_pct": float(se_alpha),
        "t_alpha": float(t_alpha),
        "n_obs": n_obs,
        "model": model_name,
    }


# ---- Build Table 3 ---------------------------------------------------------
def build_table_3(decile_rets: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Build Table 3: FF3/FF4/FF5 alphas for D1..D10 and D1-D10."""
    factor_cols = {
        "FF3": ["mkt_rf", "smb", "hml"],
        "FF4": ["mkt_rf", "smb", "hml", "mom"],
        "FF5": ["mkt_rf", "smb", "hml", "rmw", "cma"],
    }
    portfolios = list(range(1, N_BINS + 1)) + ["D1-D10"]
    rows = []
    raw = {}

    for port in portfolios:
        if port == "D1-D10":
            d1 = decile_rets[decile_rets["decile"] == 1].set_index("month_date")
            d10 = decile_rets[decile_rets["decile"] == 10].set_index("month_date")
            common = d1.index.intersection(d10.index)
            r_excess = (d1.loc[common, "ret"] - d10.loc[common, "ret"])  # zero cost
            r_excess.name = "ret_excess"
            x_label = "D1-D10"
        else:
            sub = decile_rets[decile_rets["decile"] == port].set_index("month_date")
            r_excess = sub["ret_excess"].copy()
            x_label = f"D{port}"

        # Restrict to sample period (already done at decile_rets level, but
        # align indexes anyway)
        r_excess = r_excess.sort_index()
        r_excess = r_excess.loc[
            (r_excess.index >= SAMPLE_START) & (r_excess.index <= SAMPLE_END)
        ]

        # Factors aligned to the same time index
        factors = decile_rets[
            decile_rets["decile"] == 1  # any single decile; ff values same across deciles
        ].set_index("month_date")[["mkt_rf", "smb", "hml", "mom", "rmw", "cma"]]
        factors = factors[~factors.index.duplicated(keep="first")].sort_index()
        factors = factors.loc[
            (factors.index >= SAMPLE_START) & (factors.index <= SAMPLE_END)
        ]

        raw[x_label] = {}
        row = {"Portfolio": x_label}
        for model_name, cols in factor_cols.items():
            result = run_factor_regression(
                r_excess, factors[cols], model_name
            )
            row[f"{model_name}_alpha"] = result["alpha_pct"]
            row[f"{model_name}_se"] = result["se_alpha_pct"]
            row[f"{model_name}_t"] = result["t_alpha"]
            raw[x_label][model_name] = result
        rows.append(row)

    return pd.DataFrame(rows), raw


# ---- Markdown output -------------------------------------------------------
def to_markdown(table: pd.DataFrame) -> str:
    md = []
    md.append("# Weber (2018) — Table 3: FF3/FF4/FF5 Duration Decile Alphas")
    md.append("")
    md.append("Sample period: July 1963 - June 2014 (612 months).")
    md.append("Sort: 10 deciles of equal-weighted cash-flow duration at end of June t.")
    md.append("Hold: 12 months (July t - June t+1).")
    md.append("Excess returns: portfolio return - 1-month T-bill rate (FF `rf`).")
    md.append("FF3 = Mkt-RF + SMB + HML")
    md.append("FF4 = FF3 + MOM")
    md.append("FF5 = FF3 + RMW + CMA")
    md.append("Standard errors: HC0 (heteroskedasticity-robust).")
    md.append("Regressions: monthly time-series; alphas in % per month.")
    md.append("")
    md.append("| Portfolio | FF3 alpha | FF3 SE | FF3 t | FF4 alpha | FF4 SE | FF4 t | FF5 alpha | FF5 SE | FF5 t |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    for _, r in table.iterrows():
        md.append(
            f"| {r['Portfolio']} | "
            f"{r['FF3_alpha']:.3f} | {r['FF3_se']:.3f} | {r['FF3_t']:.2f} | "
            f"{r['FF4_alpha']:.3f} | {r['FF4_se']:.3f} | {r['FF4_t']:.2f} | "
            f"{r['FF5_alpha']:.3f} | {r['FF5_se']:.3f} | {r['FF5_t']:.2f} |"
        )

    md.append("")
    md.append("## Comparison to paper values")
    md.append("")
    md.append("| Portfolio | Our FF3 alpha | Paper FF3 alpha | Our FF4 alpha | Paper FF4 alpha | Our FF5 alpha | Paper FF5 alpha |")
    md.append("|---|---|---|---|---|---|---|")
    paper_vals = {
        "D1-D10": (0.84, 0.66, 0.48),
        "D1": (0.46, None, None),
        "D10": (-0.38, None, None),
    }
    # Compute paper values for all deciles = None (paper only reports D1, D10 for FF3)
    for port_label in ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D1-D10"]:
        r_match = table[table["Portfolio"] == port_label]
        if r_match.empty:
            continue
        r = r_match.iloc[0]
        p3, p4, p5 = paper_vals.get(port_label, (None, None, None))
        md.append(
            f"| {port_label} | "
            f"{r['FF3_alpha']:.3f} | "
            f"{p3 if p3 is not None else '-'} | "
            f"{r['FF4_alpha']:.3f} | "
            f"{p4 if p4 is not None else '-'} | "
            f"{r['FF5_alpha']:.3f} | "
            f"{p5 if p5 is not None else '-'} |"
        )

    return "\n".join(md)


# ---- Main ------------------------------------------------------------------
def main():
    t0 = time.time()
    print(f"[table3] SLUG: {SLUG}")
    panel_annual, panel_monthly, ff = load_panels()
    print(f"  -> panel_annual: {len(panel_annual):,} rows")
    print(f"  -> panel_monthly: {len(panel_monthly):,} rows")
    print(f"  -> ff_factors: {len(ff):,} rows")

    print("[table3] Assigning deciles within each sort_year...")
    panel_annual = assign_deciles(panel_annual)

    print("[table3] Computing per-decile EW returns and FF factors merge...")
    decile_rets = compute_decile_returns(panel_annual, panel_monthly, ff)
    print(f"  -> {len(decile_rets):,} (month, decile) rows")
    print(f"  -> Distinct months: {decile_rets['month_date'].nunique()}")

    print("[table3] Building Table 3 (FF3/FF4/FF5 alphas)...")
    table, raw = build_table_3(decile_rets)
    print(table.to_string(index=False))

    md = to_markdown(table)
    out_md = RESULTS_DIR / "table_3.md"
    out_md.write_text(md)
    print(f"\n[table3] Wrote {out_md}")

    print()
    print("[table3] ==== Top-line summary ====")
    print(
        f"D1-D10: FF3 alpha = {raw['D1-D10']['FF3']['alpha_pct']:.3f}% "
        f"(SE = {raw['D1-D10']['FF3']['se_alpha_pct']:.3f}, "
        f"t = {raw['D1-D10']['FF3']['t_alpha']:.2f})"
    )
    print(
        f"D1-D10: FF4 alpha = {raw['D1-D10']['FF4']['alpha_pct']:.3f}% "
        f"(SE = {raw['D1-D10']['FF4']['se_alpha_pct']:.3f}, "
        f"t = {raw['D1-D10']['FF4']['t_alpha']:.2f})"
    )
    print(
        f"D1-D10: FF5 alpha = {raw['D1-D10']['FF5']['alpha_pct']:.3f}% "
        f"(SE = {raw['D1-D10']['FF5']['se_alpha_pct']:.3f}, "
        f"t = {raw['D1-D10']['FF5']['t_alpha']:.2f})"
    )

    print(f"\n[table3] Total elapsed: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
