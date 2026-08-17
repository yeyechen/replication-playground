"""
MAX on Steroids — Table 2 (Cross-sectional medians of MAX, BETA, IVOL).

Replicates paper Table 2 (page 57, L1169-L1357) for the diagnostic
characteristics only: MAX, BETA, IVOL (skipping MIS per Assumption 19).

Per `preparations/tables_to_replicate.json` T2 metrics and
`preparations/assumptions.md`:
  - Form 10 MAX deciles (NYSE-only breakpoints per Assumption 17).
  - For each (month, decile), compute cross-sectional median of MAX, BETA, IVOL.
  - Time-series-average the medians to get a single number per (decile, char).
  - Add a 10-1 difference row.
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

SLUG = "max_on_steroids_attempt4"
LAYOUT = paper_layout(SLUG)
LAYOUT.ensure()

PANEL_PATH = LAYOUT.data_path("panel.parquet")
RESULTS_DIR = LAYOUT.result_path
EVAL_PATH = LAYOUT.eval_path("metrics.json")

N_BINS = 10

# Reuse helpers from table1_max for: prepare_panel, _nyse_breakpoint_deciles
from table1_max import prepare_panel, _nyse_breakpoint_deciles  # noqa: E402


def assign_deciles(panel: pd.DataFrame) -> pd.DataFrame:
    """Form 10 MAX deciles using NYSE-only breakpoints (per Assumption 17).

    Returns panel with new int 'decile' column (1..10).
    """
    sub = panel.dropna(subset=["MAX", "BETA_w", "ME_lag1"]).copy()
    sub = sub[sub["ME_lag1"] > 0]
    decile_series, bp_stats = _nyse_breakpoint_deciles(sub)
    sub = sub.copy()
    sub["decile"] = pd.Series(decile_series.values, index=sub.index).astype("Int64")

    # Drop months with fewer than 30 NYSE stocks
    keep_months = bp_stats[bp_stats["n_nyse"] >= 30]["month"]
    sub = sub[sub["month"].isin(keep_months)].copy()
    sub = sub.dropna(subset=["decile"])
    sub["decile"] = sub["decile"].astype(int)
    return sub


def compute_median_table(panel_with_decile: pd.DataFrame) -> pd.DataFrame:
    """For each (month, decile), compute median of MAX, BETA, IVOL.

    Returns DataFrame with columns ['decile', 'MAX', 'BETA', 'IVOL']
    where each cell is the time-series mean of the cross-sectional medians.

    IVOL is reported in units of percent (x 100 of the panel's daily-residual
    stddev). The panel's IVOL column is a decimal (e.g. 0.0158); the paper
    reports IVOL as percent (e.g. 1.628). The scaling is internal to this
    function and the comparison-vs-paper metric.
    """
    sub = panel_with_decile.copy()

    # Drop rows with missing IVOL (IVOL is the diagnostic; can be NA in early years)
    sub = sub.dropna(subset=["MAX", "BETA_w", "IVOL"])

    # Scale IVOL to percent units (paper convention)
    sub["IVOL_pct"] = sub["IVOL"] * 100.0

    # Per-(month, decile) cross-sectional medians
    medians = (
        sub.groupby(["month", "decile"])
        [["MAX", "BETA_w", "IVOL_pct"]]
        .median()
        .reset_index()
    )

    # Time-series mean of medians per decile
    ts_means = (
        medians.groupby("decile")[["MAX", "BETA_w", "IVOL_pct"]]
        .mean()
        .reset_index()
    )

    # Rename BETA_w back to BETA, IVOL_pct back to IVOL
    ts_means = ts_means.rename(columns={"BETA_w": "BETA", "IVOL_pct": "IVOL"})

    # Append a 10-1 row at the bottom
    d10 = ts_means[ts_means["decile"] == 10].iloc[0]
    d1 = ts_means[ts_means["decile"] == 1].iloc[0]
    diff_row = pd.DataFrame([{
        "decile": "10-1",
        "MAX": d10["MAX"] - d1["MAX"],
        "BETA": d10["BETA"] - d1["BETA"],
        "IVOL": d10["IVOL"] - d1["IVOL"],
    }])
    out = pd.concat([ts_means, diff_row], ignore_index=True)

    # Diagnostic prints
    n_months = medians["month"].nunique()
    print(f"[table2] {n_months} months used")
    print(f"[table2] median of cross-sectional medians (TS mean):")
    print(out.to_string(index=False))

    # Monotonicity checks
    ts_only = ts_means.sort_values("decile")
    for col in ["MAX", "BETA", "IVOL"]:
        vals = ts_only[col].values
        monotonic_inc = all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))
        print(f"[table2] {col} monotonic-increasing across deciles: "
              f"{monotonic_inc}")

    return out


def table_to_markdown(t: pd.DataFrame) -> str:
    lines = []
    lines.append("# Table 2 — Cross-Sectional Medians across MAX Deciles")
    lines.append("")
    lines.append("Sample: 1968-01 to 2022-12. Independent decile sorts by MAX "
                 "(NYSE-only breakpoints). Cells report the time-series mean "
                 "of the cross-sectional median of each characteristic in "
                 "the (permno, month) panel.")
    lines.append("")
    lines.append("Skipped characteristics per Assumption 19: MIS "
                 "(requires 11-component mispricing composite).")
    lines.append("")
    lines.append("IVOL is reported in percent (panel's daily-residual stddev "
                 "scaled by 100; matches the paper's convention).")
    lines.append("")
    header = "| Decile | MAX (ratio) | BETA (ratio) | IVOL (% daily) |"
    sep = "|---|---|---|---|"
    lines.append(header)
    lines.append(sep)
    for _, row in t.iterrows():
        d = row["decile"]
        if isinstance(d, str):
            d_str = d
        else:
            d_str = f"P{int(d)}"
        lines.append(
            f"| {d_str} | {row['MAX']:.4f} | {row['BETA']:.4f} | {row['IVOL']:.4f} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("- P1 = lowest MAX decile, P10 = highest MAX decile.")
    lines.append("- 10-1 row = D10 minus D1.")
    lines.append("- Paper Table 2 reports these as cross-sectional medians; "
                 "we time-series-average the (month, decile) medians.")
    return "\n".join(lines)


def table_to_grid(t: pd.DataFrame) -> str:
    lines = []
    lines.append("=" * 80)
    lines.append("TABLE 2: CROSS-SECTIONAL MEDIANS BY MAX DECILE")
    lines.append("=" * 80)
    lines.append("(IVOL in % daily stddev; MAX and BETA are unit ratios)")
    header = f"{'Decile':<10} | {'MAX':>10} | {'BETA':>10} | {'IVOL':>10}"
    lines.append(header)
    lines.append("-" * len(header))
    for _, row in t.iterrows():
        d = row["decile"]
        d_str = d if isinstance(d, str) else f"P{int(d)}"
        lines.append(
            f"{d_str:<10} | {row['MAX']:>10.4f} | {row['BETA']:>10.4f} | "
            f"{row['IVOL']:>10.4f}"
        )
    lines.append("=" * 80)
    return "\n".join(lines)


def cells_to_metrics_json(t: pd.DataFrame) -> dict:
    """Build a metrics dict from the table.

    Keys are written with both "T2_" prefix AND bare names. The bare names
    are what the canonical scorer reads against tables_to_replicate.json
    (which uses bare names). The T2_-prefixed copies are kept for
    backwards-compat / disambiguation. Only MAX, BETA, IVOL are emitted
    (MIS is SKIP per Assumption 19).
    """
    metrics = {}

    # Look up D1, D10, and 10-1 rows
    d1 = t[t["decile"] == 1].iloc[0]
    d10 = t[t["decile"] == 10].iloc[0]
    diff = t[t["decile"] == "10-1"].iloc[0]

    char_cols = ["MAX", "BETA", "IVOL"]
    for ch in char_cols:
        e = {
            "value": float(d1[ch]),
            "unit": "ratio" if ch != "IVOL" else "% daily stddev",
            "n_obs": "n/a",
        }
        metrics[f"P1_{ch}"] = e
        metrics[f"T2_P1_{ch}"] = e
        e = {
            "value": float(d10[ch]),
            "unit": "ratio" if ch != "IVOL" else "% daily stddev",
            "n_obs": "n/a",
        }
        metrics[f"P10_{ch}"] = e
        metrics[f"T2_P10_{ch}"] = e
        e = {
            "value": float(diff[ch]),
            "unit": "ratio" if ch != "IVOL" else "% daily stddev",
            "n_obs": "n/a",
        }
        metrics[f"D10_D1_{ch}"] = e
        metrics[f"T2_D10_D1_{ch}"] = e

    # Mark MIS as SKIP per Assumption 19
    for d in ["P1", "P10", "D10_D1"]:
        e = {
            "value": None,
            "unit": "rank",
            "n_obs": 0,
            "status": "SKIP",
            "skip_reason": "MIS requires 11-component Stambaugh-Yuan composite (unavailable in ClickHouse)",
        }
        metrics[f"{d}_MIS"] = e
        metrics[f"T2_{d}_MIS"] = e

    return metrics


def compare_to_paper(t: pd.DataFrame, paper_target: dict) -> str:
    """Side-by-side comparison vs paper Table 2 values."""
    lines = []
    lines.append("=" * 100)
    lines.append("TABLE 2: REPLICATED vs PAPER")
    lines.append("=" * 100)
    lines.append(f"{'Cell':<14} | {'Replicated':>12} | {'Paper':>10} | {'%Diff':>10} | Status")

    d1 = t[t["decile"] == 1].iloc[0]
    d10 = t[t["decile"] == 10].iloc[0]
    diff = t[t["decile"] == "10-1"].iloc[0]

    cell_values = {
        "P1_MAX": float(d1["MAX"]),
        "P10_MAX": float(d10["MAX"]),
        "D10_D1_MAX": float(diff["MAX"]),
        "P1_BETA": float(d1["BETA"]),
        "P10_BETA": float(d10["BETA"]),
        "D10_D1_BETA": float(diff["BETA"]),
        "P1_IVOL": float(d1["IVOL"]),
        "P10_IVOL": float(d10["IVOL"]),
        "D10_D1_IVOL": float(diff["IVOL"]),
    }

    # Per-character tolerance from paper target list
    tol_lookup = {
        "MAX": 25,
        "BETA": 30,
        "IVOL": 30,
    }

    n_match = 0
    n_fail = 0
    n_skip = 0
    for cell, rep_v in cell_values.items():
        paper_v = paper_target.get(cell)
        if paper_v is None:
            if cell.endswith("_MIS"):
                n_skip += 1
                lines.append(f"{cell:<14} | {'':>12} | {'':>10} | {'':>10} | SKIP")
            else:
                lines.append(f"{cell:<14} | {rep_v:>10.3f} | {'(missing)':>10} | {'':>10} | N/A")
            continue

        if paper_v == 0:
            pct_diff = float("inf") if abs(rep_v) > 1e-6 else 0.0
        else:
            pct_diff = abs((rep_v - paper_v) / paper_v) * 100

        # Pick tolerance based on characteristic
        suffix = cell.split("_", 1)[1] if "_" in cell else ""
        char = suffix if suffix in tol_lookup else cell
        tol = tol_lookup.get(char, 30)
        within_tol = pct_diff <= tol
        status = "Match" if within_tol else "FAIL"
        if within_tol:
            n_match += 1
        else:
            n_fail += 1
        lines.append(
            f"{cell:<14} | {rep_v:>10.3f} | {paper_v:>8.2f} | {pct_diff:>8.1f}% | {status}"
        )

    # Mark MIS cells as SKIP
    for d in ["P1", "P10", "D10_D1"]:
        cell = f"{d}_MIS"
        if cell in paper_target:
            n_skip += 1
            lines.append(f"{cell:<14} | {'':>12} | {'':>10} | {'':>10} | SKIP")

    lines.append("=" * 100)
    lines.append(f"Match: {n_match}  FAIL: {n_fail}  SKIP: {n_skip}")
    return "\n".join(lines)


def main() -> int:
    print(f"[table2] loading panel from {PANEL_PATH}")
    panel = pd.read_parquet(PANEL_PATH)
    print(f"[table2] panel: {len(panel):,} rows x {panel.shape[1]} cols")

    panel = prepare_panel(panel)
    panel_with_decile = assign_deciles(panel)
    print(f"[table2] rows after decile assignment: {len(panel_with_decile):,}")

    table = compute_median_table(panel_with_decile)

    print()
    print(table_to_grid(table))

    paper_target_path = LAYOUT.input_path("tables_to_replicate.json")
    with open(paper_target_path) as f:
        paper_cfg = json.load(f)
    paper_target = {
        m["name"]: m["value"]
        for t in paper_cfg["tables"] if t["id"] == "T2"
        for m in t["metrics"]
    }
    print()
    print(compare_to_paper(table, paper_target))

    RESULTS_DIR("").mkdir(parents=True, exist_ok=True)
    md = table_to_markdown(table)
    (RESULTS_DIR("table_2.md")).write_text(md)
    print(f"\n[table2] saved {RESULTS_DIR('table_2.md')}")

    grid_text = table_to_grid(table) + "\n\n" + compare_to_paper(table, paper_target)
    (RESULTS_DIR("table_2_results.txt")).write_text(grid_text)
    print(f"[table2] saved {RESULTS_DIR('table_2_results.txt')}")

    return cells_to_metrics_json(table)


if __name__ == "__main__":
    metrics = main()
    print(f"\n[table2] {len(metrics)} cells")