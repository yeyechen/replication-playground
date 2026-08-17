"""
Weber (2018) "Cash flow duration and the term structure of equity returns"
Table 5 — Subsample analysis of the D1-D10 duration spread.

Methodology (per the paper / Replicator's spec):
  - 5 subsamples by month of return: 1963-1973, 1973-1983, 1983-1993,
    1993-2003, 2003-2014.
  - For each subsample, take the D1-D10 spread (low-dur minus high-dur)
    and compute the mean excess return over the subsample's months.

Outputs:
  results/table_5.md — markdown table with mean excess returns per subsample.
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

N_BINS = 10

# Subsample windows (calendar months — paper convention)
SUBSAMPLES = [
    ("1963-1973", pd.Timestamp("1963-07-01"), pd.Timestamp("1973-06-30")),
    ("1973-1983", pd.Timestamp("1973-07-01"), pd.Timestamp("1983-06-30")),
    ("1983-1993", pd.Timestamp("1983-07-01"), pd.Timestamp("1993-06-30")),
    ("1993-2003", pd.Timestamp("1993-07-01"), pd.Timestamp("2003-06-30")),
    ("2003-2014", pd.Timestamp("2003-07-01"), pd.Timestamp("2014-06-30")),
]


# ---- Loaders and helpers (same as Table 3) ---------------------------------
def load_panels():
    panel_annual = pd.read_parquet(DATA_DIR / "panel_annual.parquet")
    panel_monthly = pd.read_parquet(DATA_DIR / "panel_monthly.parquet")
    panel_monthly["month_date"] = pd.to_datetime(panel_monthly["month_date"])
    ff = pd.read_parquet(DATA_DIR / "ff_factors.parquet")
    ff["dt"] = pd.to_datetime(ff["dt"])
    return panel_annual, panel_monthly, ff


def assign_deciles(panel_annual: pd.DataFrame) -> pd.DataFrame:
    df = panel_annual.copy()
    df["decile"] = assign_quantiles(
        df, date_col="sort_year", signal_col="dur", n_bins=N_BINS,
        warn_fallback=False,
    )
    return df


def compute_decile_returns(panel_annual, panel_monthly, ff):
    sort_map = panel_annual[["permno", "sort_year", "decile"]].dropna(
        subset=["decile"]
    )
    sort_map["decile"] = sort_map["decile"].astype(int)
    df = panel_monthly.merge(sort_map, on=["permno", "sort_year"], how="inner")
    ff_join = ff[["year", "month", "rf"]].copy()
    df = df.merge(ff_join, on=["year", "month"], how="left")
    df["rf"] = df["rf"].astype(float)
    grp = df.groupby(["month_date", "year", "month", "decile"], as_index=False).agg(
        ret=("ret_adj", "mean"),
        rf=("rf", "first"),
        n_stocks=("ret_adj", "size"),
    )
    grp["ret_excess"] = grp["ret"] - grp["rf"]
    return grp


# ---- Build Table 5 ---------------------------------------------------------
def compute_d1d10_spread(decile_rets: pd.DataFrame) -> pd.Series:
    """Compute the D1-D10 EW spread (per month, decimal)."""
    d1 = decile_rets[decile_rets["decile"] == 1].set_index("month_date")
    d10 = decile_rets[decile_rets["decile"] == 10].set_index("month_date")
    common = d1.index.intersection(d10.index)
    spread = d1.loc[common, "ret"] - d10.loc[common, "ret"]
    spread = spread.sort_index()
    spread.name = "ret"
    return spread


def compute_decile_mean(decile_rets: pd.DataFrame, decile: int) -> pd.Series:
    """Compute the EW mean excess return (decimal) per month for a given decile."""
    sub = decile_rets[decile_rets["decile"] == decile].set_index("month_date")
    out = sub["ret_excess"].sort_index()
    out.name = "ret_excess"
    return out


def _summarise_series(s: pd.Series, label: str, start: pd.Timestamp,
                       end: pd.Timestamp) -> dict:
    """Apply HC0 OLS to a series over [start, end] and return summary dict."""
    sub = s.loc[(s.index >= start) & (s.index <= end)]
    if len(sub) > 1:
        y = sub.values
        X = np.ones((len(y), 1))
        model = sm.OLS(y, X).fit(cov_type="HC0")
        mean_pct = float(model.params[0] * 100.0)
        se_pct = float(model.bse[0] * 100.0)
        t_stat = float(model.tvalues[0])
        n_obs = int(len(sub))
    else:
        mean_pct = float(sub.mean() * 100.0)
        se_pct = float("nan")
        t_stat = float("nan")
        n_obs = int(len(sub))
    return {
        "label": label,
        "start": str(start.date()),
        "end": str(end.date()),
        "n_months": n_obs,
        "mean_pct": mean_pct,
        "se_pct": se_pct,
        "t_stat": t_stat,
    }


def build_table_5(decile_rets: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Compute mean D1-D10 spread per subsample, plus per-decile D1/D10 means
    for the subsamples committed in tables_to_replicate.json."""
    spread = compute_d1d10_spread(decile_rets)
    rows = []
    raw = {}
    for label, start, end in SUBSAMPLES:
        s = _summarise_series(spread, f"Spread {label}", start, end)
        raw[label] = s
        rows.append({
            "Decile": "Spread",
            "Subsample": label,
            "Start": s["start"],
            "End": s["end"],
            "Mean Excess (%)": s["mean_pct"],
            "SE": s["se_pct"],
            "t-stat": s["t_stat"],
            "N months": s["n_months"],
        })

    # Per-decile D1 and D10 means for the 3 committed subsamples (matches
    # tables_to_replicate.json: 1963-1973, 1983-1993, 2003-2014).
    per_decile_subsamples = [
        ("1963-1973", pd.Timestamp("1963-07-01"), pd.Timestamp("1973-06-30")),
        ("1983-1993", pd.Timestamp("1983-07-01"), pd.Timestamp("1993-06-30")),
        ("2003-2014", pd.Timestamp("2003-07-01"), pd.Timestamp("2014-06-30")),
    ]
    for decile in [1, 10]:
        d_series = compute_decile_mean(decile_rets, decile)
        for label, start, end in per_decile_subsamples:
            s = _summarise_series(d_series, f"D{decile} {label}", start, end)
            raw[f"D{decile}_{label}"] = s
            rows.append({
                "Decile": f"D{decile}",
                "Subsample": label,
                "Start": s["start"],
                "End": s["end"],
                "Mean Excess (%)": s["mean_pct"],
                "SE": s["se_pct"],
                "t-stat": s["t_stat"],
                "N months": s["n_months"],
            })
    return pd.DataFrame(rows), raw


# ---- Markdown output -------------------------------------------------------
def to_markdown(table: pd.DataFrame) -> str:
    md = []
    md.append("# Weber (2018) — Table 5: Subsample Analysis (D1-D10 Spread)")
    md.append("")
    md.append("Spread: equal-weight D1 (low dur) minus D10 (high dur).")
    md.append("Per-decile D1/D10 means: equal-weight mean excess return per "
              "subsample (selected periods; visual spectrum check).")
    md.append("Statistics: monthly mean (in %), HC0 standard error, t-statistic.")
    md.append("Subsample windows by month of return (10-year rolling windows).")
    md.append("")
    md.append("| Decile | Subsample | Start | End | Mean Excess (%) | SE | t-stat | N months |")
    md.append("|---|---|---|---|---|---|---|---|")
    for _, r in table.iterrows():
        md.append(
            f"| {r['Decile']} | {r['Subsample']} | {r['Start']} | {r['End']} | "
            f"{r['Mean Excess (%)']:.3f} | {r['SE']:.3f} | "
            f"{r['t-stat']:.2f} | {int(r['N months'])} |"
        )

    md.append("")
    md.append("## Comparison to paper")
    md.append("")
    md.append("### Spread (D1-D10)")
    md.append("")
    md.append("| Subsample | Our Mean | Paper Mean |")
    md.append("|---|---|---|")
    paper_vals = {
        "1963-1973": 0.69,
        "1973-1983": 1.34,
        "1983-1993": 1.37,
        "1993-2003": 1.10,
        "2003-2014": 1.04,
    }
    for _, r in table.iterrows():
        if r["Decile"] != "Spread":
            continue
        pm = paper_vals[r["Subsample"]]
        md.append(
            f"| {r['Subsample']} | {r['Mean Excess (%)']:.3f} | {pm:.3f} |"
        )

    md.append("")
    md.append("### Per-decile D1 / D10 means (selected subsamples)")
    md.append("")
    md.append("| Decile | Subsample | Our Mean | Paper Mean |")
    md.append("|---|---|---|---|")
    paper_per_decile = {
        ("D1", "1963-1973"): 0.91,
        ("D10", "1963-1973"): 0.23,
        ("D1", "1983-1993"): 0.96,
        ("D10", "1983-1993"): -0.41,
        ("D1", "2003-2014"): 1.68,
        ("D10", "2003-2014"): 0.64,
    }
    for _, r in table.iterrows():
        if r["Decile"] == "Spread":
            continue
        key = (r["Decile"], r["Subsample"])
        if key not in paper_per_decile:
            continue
        pm = paper_per_decile[key]
        md.append(
            f"| {r['Decile']} | {r['Subsample']} | {r['Mean Excess (%)']:.3f} | {pm:.3f} |"
        )

    return "\n".join(md)


# ---- Main ------------------------------------------------------------------
def main():
    t0 = time.time()
    print(f"[table5] SLUG: {SLUG}")
    panel_annual, panel_monthly, ff = load_panels()
    print(f"  -> panel_annual: {len(panel_annual):,} rows")
    print(f"  -> panel_monthly: {len(panel_monthly):,} rows")
    print(f"  -> ff_factors: {len(ff):,} rows")

    print("[table5] Assigning deciles within each sort_year...")
    panel_annual = assign_deciles(panel_annual)

    print("[table5] Computing per-decile EW returns...")
    decile_rets = compute_decile_returns(panel_annual, panel_monthly, ff)
    print(f"  -> {len(decile_rets):,} (month, decile) rows")

    print("[table5] Building Table 5 (subsample means)...")
    table, raw = build_table_5(decile_rets)
    print(table.to_string(index=False))

    md = to_markdown(table)
    out_md = RESULTS_DIR / "table_5.md"
    out_md.write_text(md)
    print(f"\n[table5] Wrote {out_md}")

    print(f"\n[table5] Total elapsed: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
