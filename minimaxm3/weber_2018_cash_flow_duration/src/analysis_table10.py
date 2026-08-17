"""
Weber (2018) "Cash flow duration and the term structure of equity returns"
Table 10 — 25-portfolio analysis (5 duration quintiles x 5 RIOR quintiles).

Methodology (per the paper / Replicator's spec):
  - Sample: 1981-2013 (IOR-restricted sample).
  - Drop the 20% smallest stocks (above 20th size percentile).
  - For each sort_year, compute the cross-sectional regression:
      log(IOR / (1 - IOR)) = alpha + beta1 * log(ME) + beta2 * (log(ME))^2 + RIOR
    The residual is "RIOR" (the sorting variable).
  - Clip IOR to [0.0001, 0.9999] before the logit transformation.
  - Form independent sorts into 5 duration quintiles and 5 RIOR quintiles.
  - Compute mean excess returns (EW) for each of the 25 cells.

Outputs:
  results/table_10.md — markdown table with mean excess returns.
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

SAMPLE_START = 1981
SAMPLE_END = 2013

IOR_LOWER = 0.0001
IOR_UPPER = 0.9999

N_BINS_DUR = 5
N_BINS_RIOR = 5


# ---- Loaders ---------------------------------------------------------------
def load_panels():
    panel_annual = pd.read_parquet(DATA_DIR / "panel_annual.parquet")
    panel_monthly = pd.read_parquet(DATA_DIR / "panel_monthly.parquet")
    panel_monthly["month_date"] = pd.to_datetime(panel_monthly["month_date"])
    ff = pd.read_parquet(DATA_DIR / "ff_factors.parquet")
    ff["dt"] = pd.to_datetime(ff["dt"])
    return panel_annual, panel_monthly, ff


def filter_above_size_pct(df: pd.DataFrame, pct: float = 20) -> pd.DataFrame:
    df = df.copy()
    cutoff = df.groupby("sort_year")["me_jun_dollars"].transform(
        lambda x: x.quantile(pct / 100.0)
    )
    return df.loc[df["me_jun_dollars"] >= cutoff].copy()


# ---- Compute RIOR per (sort_year) -----------------------------------------
def compute_rior(df: pd.DataFrame) -> pd.DataFrame:
    """Compute residual institutional ownership (RIOR) per (sort_year).

    For each sort_year cross-section, regress logit(IOR) on log(ME) and
    log(ME)^2; the residual is RIOR.

    IOR is clipped to [IOR_LOWER, IOR_UPPER] before the logit.
    """
    df = df.copy()
    df["ior_clip"] = df["ior"].clip(IOR_LOWER, IOR_UPPER)
    df["logit_ior"] = np.log(df["ior_clip"] / (1.0 - df["ior_clip"]))
    df["ln_me"] = df["ln_me_jun"]
    df["ln_me_sq"] = df["ln_me"] ** 2

    rows = []
    for year, group in df.groupby("sort_year"):
        valid = group.dropna(subset=["logit_ior", "ln_me", "ln_me_sq"])
        if len(valid) < 10:
            continue
        y = valid["logit_ior"]
        X = sm.add_constant(valid[["ln_me", "ln_me_sq"]])
        try:
            model = sm.OLS(y, X).fit()
            group_out = valid[["permno", "sort_year", "ior"]].copy()
            group_out["rior"] = model.resid
            rows.append(group_out)
        except Exception:
            continue
    if not rows:
        return pd.DataFrame(columns=["permno", "sort_year", "ior", "rior"])
    out = pd.concat(rows, ignore_index=True)
    return out


# ---- Assign quintiles -----------------------------------------------------
def assign_quintiles(df: pd.DataFrame) -> pd.DataFrame:
    """Assign 5 quintiles for both dur and RIOR within each sort_year."""
    df = df.copy()
    df["dur_q"] = assign_quantiles(
        df, date_col="sort_year", signal_col="dur", n_bins=N_BINS_DUR,
        warn_fallback=False,
    )
    df["rior_q"] = assign_quantiles(
        df, date_col="sort_year", signal_col="rior", n_bins=N_BINS_RIOR,
        warn_fallback=False,
    )
    return df


# ---- Build 25-portfolio EW returns ----------------------------------------
def compute_25_returns(
    panel_annual_with_q: pd.DataFrame,
    panel_monthly: pd.DataFrame,
    ff: pd.DataFrame,
) -> pd.DataFrame:
    """Compute per-(dur_q, rior_q, month) equal-weighted excess return.

    Returns:
        DataFrame with columns [month_date, year, month, dur_q, rior_q,
        ret_excess, n_stocks].
    """
    sort_map = panel_annual_with_q[["permno", "sort_year", "dur_q", "rior_q"]].dropna(
        subset=["dur_q", "rior_q"]
    )
    sort_map["dur_q"] = sort_map["dur_q"].astype(int)
    sort_map["rior_q"] = sort_map["rior_q"].astype(int)

    df = panel_monthly.merge(
        sort_map, on=["permno", "sort_year"], how="inner",
    )

    ff_join = ff[["year", "month", "rf"]].copy()
    df = df.merge(ff_join, on=["year", "month"], how="left")
    df["rf"] = df["rf"].astype(float)

    grp = df.groupby(
        ["month_date", "year", "month", "dur_q", "rior_q"], as_index=False,
    ).agg(
        ret=("ret_adj", "mean"),
        rf=("rf", "first"),
        n_stocks=("ret_adj", "size"),
    )
    grp["ret_excess"] = grp["ret"] - grp["rf"]
    return grp


# ---- Build Table 10 -------------------------------------------------------
def build_table_10(cell_rets: pd.DataFrame) -> pd.DataFrame:
    """Compute the 5x5 mean excess returns matrix (with summary statistics)."""
    SAMPLE_START_TS = pd.Timestamp("1981-07-01")
    SAMPLE_END_TS   = pd.Timestamp("2014-06-30")
    cell_rets = cell_rets.loc[
        (cell_rets["month_date"] >= SAMPLE_START_TS)
        & (cell_rets["month_date"] <= SAMPLE_END_TS)
    ].copy()

    # Compute mean excess returns per (dur_q, rior_q) — in %
    g = cell_rets.groupby(["dur_q", "rior_q"], as_index=False).agg(
        mean_excess=("ret_excess", lambda x: x.mean() * 100.0),
        n_months=("month_date", "nunique"),
    )

    # Pivot to 5x5 matrix
    matrix = g.pivot(index="dur_q", columns="rior_q", values="mean_excess")
    matrix = matrix.reindex(index=range(1, N_BINS_DUR + 1), columns=range(1, N_BINS_RIOR + 1))
    return matrix


def add_spreads(matrix: pd.DataFrame) -> pd.DataFrame:
    """Add D1-D5 spread (per RIOR quintile) and RIOR1-RIOR5 spread (per dur quintile)."""
    out = matrix.copy()
    out["D1-D5"] = out[1] - out[5]
    out.loc["RIOR1-RIOR5"] = [matrix.iloc[i, 0] - matrix.iloc[i, 4]
                               for i in range(N_BINS_DUR)]
    return out


# ---- Markdown output -------------------------------------------------------
def to_markdown(matrix: pd.DataFrame) -> str:
    md = []
    md.append("# Weber (2018) — Table 10: Duration x Residual IOR Portfolio Returns")
    md.append("")
    md.append("Sample: 1981-2013 (paper §2 L176, IOR-restricted sample).")
    md.append("Universe: above 20th size percentile.")
    md.append("Sorting: 5 duration quintiles x 5 residual IOR quintiles, independent sorts.")
    md.append("Equal-weighted portfolio returns. Excess returns = portfolio return - RF.")
    md.append("Means reported in % per month.")
    md.append("")
    md_lines = []
    # Build a header
    header = "| Duration \\\\ RIOR |"
    for q in range(1, N_BINS_RIOR + 1):
        header += f" Q{q} |"
    header += " D1-D5 |"
    md_lines.append(header)
    md_lines.append("|---" + "|---" * (N_BINS_RIOR + 1) + "|")

    for dur_q in range(1, N_BINS_DUR + 1):
        line = f"| Q{dur_q} |"
        for rior_q in range(1, N_BINS_RIOR + 1):
            val = matrix.loc[dur_q, rior_q]
            line += f" {val:.3f} |"
        spread = matrix.loc[dur_q, 1] - matrix.loc[dur_q, 5]
        line += f" {spread:.3f} |"
        md_lines.append(line)

    # Add RIOR1-RIOR5 spread row
    line = "| RIOR1-RIOR5 |"
    for dur_q in range(1, N_BINS_DUR + 1):
        rior1 = matrix.loc[dur_q, 1]
        rior5 = matrix.loc[dur_q, 5]
        spread = rior1 - rior5
        line += f" {spread:.3f} |"
    line += " - |"  # No double-spread
    md_lines.append(line)

    md.extend(md_lines)

    md.append("")
    md.append("## Cell-mean tables (decimal)")
    md.append("")
    md.append("D1-D5 spread by RIOR quintile (low dur - high dur):")
    md.append("")
    md.append("| RIOR Q | D1-D5 | Low-Dur cell | High-Dur cell |")
    md.append("|---|---|---|---|")
    for rior_q in range(1, N_BINS_RIOR + 1):
        spread = matrix.loc[1, rior_q] - matrix.loc[5, rior_q]
        md.append(
            f"| Q{rior_q} | {spread:.3f} | "
            f"{matrix.loc[1, rior_q]:.3f} | {matrix.loc[5, rior_q]:.3f} |"
        )

    md.append("")
    md.append("RIOR1-RIOR5 spread by duration quintile (low RIOR - high RIOR):")
    md.append("")
    md.append("| Dur Q | RIOR1-RIOR5 | Low-RIOR cell | High-RIOR cell |")
    md.append("|---|---|---|---|")
    for dur_q in range(1, N_BINS_DUR + 1):
        spread = matrix.loc[dur_q, 1] - matrix.loc[dur_q, 5]
        md.append(
            f"| Q{dur_q} | {spread:.3f} | "
            f"{matrix.loc[dur_q, 1]:.3f} | {matrix.loc[dur_q, 5]:.3f} |"
        )

    md.append("")
    md.append("## Comparison to paper")
    md.append("")
    md.append("Paper Table 10 (means in % per month):")
    md.append("")
    md.append("| | Paper | Ours |")
    md.append("|---|---|---|")
    md.append(f"| Low RIOR, D1 | 1.02 | {matrix.loc[1, 1]:.3f} |")
    md.append(f"| Low RIOR, D5 (high dur) | -0.30 | {matrix.loc[5, 1]:.3f} |")
    md.append(f"| Low RIOR, D1-D5 | 1.32 | {matrix.loc[1, 1] - matrix.loc[5, 1]:.3f} |")
    md.append(f"| High RIOR, D1 | 1.09 | {matrix.loc[1, 5]:.3f} |")
    md.append(f"| High RIOR, D5 | 0.94 | {matrix.loc[5, 5]:.3f} |")
    md.append(f"| High RIOR, D1-D5 | 0.15 | {matrix.loc[1, 5] - matrix.loc[5, 5]:.3f} |")
    md.append(f"| RIOR1-RIOR5, low dur | -0.08 | {matrix.loc[1, 1] - matrix.loc[1, 5]:.3f} |")
    md.append(f"| RIOR1-RIOR5, high dur | -1.24 | {matrix.loc[5, 1] - matrix.loc[5, 5]:.3f} |")

    return "\n".join(md)


# ---- Main ------------------------------------------------------------------
def main():
    t0 = time.time()
    print(f"[table10] SLUG: {SLUG}")
    panel_annual, panel_monthly, ff = load_panels()
    print(f"  -> panel_annual: {len(panel_annual):,} rows")
    print(f"  -> panel_monthly: {len(panel_monthly):,} rows")
    print(f"  -> ff_factors: {len(ff):,} rows")

    # Sample filter (1981-2013)
    df = panel_annual.loc[
        (panel_annual["sort_year"] >= SAMPLE_START)
        & (panel_annual["sort_year"] <= SAMPLE_END)
    ].copy()
    print(f"  -> After year filter: {len(df):,} rows")

    # Above 20th size percentile
    df = filter_above_size_pct(df, pct=20)
    print(f"  -> After 20th size percentile filter: {len(df):,} rows")

    # Compute RIOR per sort_year
    print("[table10] Computing RIOR per sort_year...")
    rior_df = compute_rior(df)
    print(f"  -> {len(rior_df):,} (permno, sort_year) RIOR rows")

    # Merge RIOR back into df
    df = df.merge(
        rior_df[["permno", "sort_year", "rior"]],
        on=["permno", "sort_year"], how="left",
    )
    n_with_rior = df["rior"].notna().sum()
    print(f"  -> {n_with_rior:,} rows have valid RIOR")

    # Assign 5-dur-quintiles and 5-RIOR-quintiles (independent sorts)
    print("[table10] Assigning 5 quintiles for dur and RIOR (independent sorts)...")
    df = assign_quintiles(df)

    # Per-cell EW returns
    print("[table10] Computing per-cell EW returns...")
    cell_rets = compute_25_returns(df, panel_monthly, ff)
    print(f"  -> {len(cell_rets):,} (month, dur_q, rior_q) rows")
    print(f"  -> Distinct months: {cell_rets['month_date'].nunique()}")
    print(f"  -> Distinct (dur_q, rior_q) cells: "
          f"{cell_rets.groupby(['dur_q','rior_q']).ngroups}")

    # Build the 5x5 matrix
    print("[table10] Building 5x5 matrix...")
    matrix = build_table_10(cell_rets)
    print()
    print(matrix.to_string())

    md = to_markdown(matrix)
    out_md = RESULTS_DIR / "table_10.md"
    out_md.write_text(md)
    print(f"\n[table10] Wrote {out_md}")

    print(f"\n[table10] Total elapsed: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
