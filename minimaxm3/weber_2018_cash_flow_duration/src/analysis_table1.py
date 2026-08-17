"""
Weber (2018) "Cash flow duration and the term structure of equity returns"
Table 1 — Summary statistics (annual cross-sectional means and standard
deviations, time-series averaged).

Methodology (per the paper / Replicator's spec):
  - Sample: 1981-2013 (paper uses 1981-2014 for IOR-restricted sample).
  - Universe: above the 20th size percentile (paper convention).
  - Per the Replicator's spec:
      1. For each variable, winzorize at 1% / 99% per (sort_year).
      2. Compute per-(sort_year) cross-sectional mean and std.
      3. Take the time-series average (mean of yearly means).
  - IOR is set to 0 where missing per paper §2 L110.
  - ME is reported in millions.

Outputs:
  results/table_1.md — markdown table matching the paper's Table 1 layout.
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd

from utils.paths import paper_layout


# ---- Configuration ---------------------------------------------------------
SLUG = "weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns"
LAYOUT = paper_layout(SLUG)
DATA_DIR = LAYOUT.data_path("")
RESULTS_DIR = LAYOUT.result_path("")

# Sample period (per Replicator's spec — IOR-restricted sample)
SAMPLE_START = 1981
SAMPLE_END = 2013


# ---- Loaders ---------------------------------------------------------------
def load_panel() -> pd.DataFrame:
    """Load panel_annual.parquet."""
    df = pd.read_parquet(DATA_DIR / "panel_annual.parquet")
    return df


def filter_above_size_pct(df: pd.DataFrame, pct: float = 20) -> pd.DataFrame:
    """Filter to stocks above the 20th size percentile (paper convention).

    The 20th size percentile is defined per (sort_year) cross-section:
    keep rows whose `me_jun_dollars` >= the 20th percentile of `me_jun_dollars`
    within the same `sort_year`.
    """
    df = df.copy()
    cutoff = df.groupby("sort_year")["me_jun_dollars"].transform(
        lambda x: x.quantile(pct / 100.0)
    )
    return df.loc[df["me_jun_dollars"] >= cutoff].copy()


def winsorize_per_year(s: pd.Series, year: pd.Series, p: float = 0.01) -> pd.Series:
    """Winsorize at the 1%/99% level per (sort_year).

    Per the paper §2 L176: "I winsorize all variables at the 1% and 99% levels."
    This is applied per-year cross-section.
    """
    return s.groupby(year).transform(
        lambda x: x.clip(lower=x.quantile(p), upper=x.quantile(1 - p))
    )


def compute_ts_mean_std(df: pd.DataFrame, col: str) -> tuple[float, float]:
    """Compute time-series average of per-(sort_year) cross-sectional
    mean and standard deviation.

    For each sort_year, compute the cross-sectional mean and std of `col`,
    then take the time-series average (mean across years).
    """
    by_year = df.groupby("sort_year")[col].agg(["mean", "std"])
    return float(by_year["mean"].mean()), float(by_year["std"].mean())


# ---- Main ------------------------------------------------------------------
def main():
    t0 = time.time()
    print(f"[table1] SLUG: {SLUG}")
    print("[table1] Loading panel_annual.parquet...")
    df = load_panel()
    print(f"  -> {len(df):,} rows; {df['sort_year'].min()}..{df['sort_year'].max()}")

    # Filter to IOR-restricted sample
    df = df.loc[
        (df["sort_year"] >= SAMPLE_START) & (df["sort_year"] <= SAMPLE_END)
    ].copy()
    print(f"  -> After year filter (1981..2013): {len(df):,} rows")

    # Filter to above the 20th size percentile
    df = filter_above_size_pct(df, pct=20)
    print(f"  -> After 20th size percentile filter: {len(df):,} rows")

    # IOR: zero where missing
    df["ior"] = df["ior"].fillna(0.0)

    # ME in millions
    df["me_mil"] = df["me_jun_dollars"] / 1e6

    # Variable list (per Table 1)
    variables = {
        "dur": "Dur",
        "bm": "BM",
        "ior": "IOR",
        "pr": "PR",
        "roe": "ROE",
        "sales_g": "Sales_g",
        "me_mil": "ME ($M)",
        "age": "Age",
    }

    # Winsorize each variable per sort_year before computing stats.
    # Iter-4 fix (audit3 M1): restore the paper's 1%/99% winsorization on
    # dur (paper §2 L176: "I winsorize all variables at the 1% and 99%
    # levels"). The dur column arriving here has ALREADY been winsorized
    # per-fyear in main.py (the panel-level dur clip), so re-winsorizing
    # here is a no-op on the central dur distribution — it only matters
    # if dur was re-introduced as a raw value somewhere. The per-sort_year
    # winsorize is kept for dur for consistency with the paper's rule
    # and to handle any dur values that arrived unclipped.
    print("[table1] Winsorizing all variables at 1%/99% per sort_year (incl. dur)...")
    for col in variables.keys():
        df[col] = winsorize_per_year(df[col], df["sort_year"], p=0.01)

    # Compute summary statistics
    print("[table1] Computing summary statistics...")
    rows = []
    summary = {}
    for col, label in variables.items():
        mean_ts, std_ts = compute_ts_mean_std(df, col)
        # The mean in the paper is the cross-sectional MEAN (we use ts-avg of
        # cross-sectional means — same since the cross-sectional mean is the
        # first moment by sort_year).
        rows.append((label, mean_ts, std_ts))
        summary[col] = {
            "mean": float(mean_ts),
            "std": float(std_ts),
        }
        print(f"  {label}: mean={mean_ts:.3f}, std={std_ts:.3f}, "
              f"n_years={df['sort_year'].nunique()}")

    # Format markdown
    md_lines = []
    md_lines.append("# Weber (2018) — Table 1: Summary Statistics")
    md_lines.append("")
    md_lines.append(
        f"Sample: {SAMPLE_START}-{SAMPLE_END} (IOR-restricted sample).  "
        "Universe: above 20th size percentile."
    )
    md_lines.append("")
    md_lines.append("All variables winsorized at the 1%/99% level per sort_year before computing stats.")
    md_lines.append("Statistics: time-series average of per-(sort_year) cross-sectional mean / std.")
    md_lines.append("ME in millions. IOR set to 0 where missing (paper §2 L110).")
    md_lines.append("")
    md_lines.append("| Variable | Mean | Std |")
    md_lines.append("|---|---|---|")
    for label, m, s in rows:
        md_lines.append(f"| {label} | {m:.3f} | {s:.3f} |")

    md_lines.append("")
    md_lines.append("## Comparison to paper values")
    md_lines.append("")
    md_lines.append("| Variable | Our Mean | Paper Mean | Our Std | Paper Std |")
    md_lines.append("|---|---|---|---|---|")
    paper_values = {
        "Dur": (18.77, 5.37),
        "BM": (0.67, 0.53),
        "IOR": (0.44, 0.23),
        "PR": (-0.01, 2.10),
        "ROE": (0.05, 0.54),
        "Sales_g": (0.22, 0.59),
        "ME ($M)": (2125, 6197),
        "Age": (17.59, 11.46),
    }
    for label, m, s in rows:
        pm, ps = paper_values[label]
        md_lines.append(f"| {label} | {m:.3f} | {pm:.3f} | {s:.3f} | {ps:.3f} |")

    md = "\n".join(md_lines)

    out_md = RESULTS_DIR / "table_1.md"
    out_md.write_text(md)
    print(f"\n[table1] Wrote {out_md}")
    print(f"[table1] Total elapsed: {time.time() - t0:.1f}s")
    return summary


if __name__ == "__main__":
    main()
