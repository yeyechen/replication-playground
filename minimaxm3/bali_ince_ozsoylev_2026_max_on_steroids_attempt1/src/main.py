"""
Replication of Bali, Ince, Ozsöylev (2026) "MAX on Steroids":
A New Measure of Investor Attraction to Maximum Daily Returns.

Stage 7 (data-pipeline-only): build the analysis-ready stock-month panel.
Downstream tables (MAX sorts, MAX^beta double-sorts, FM regressions,
factor-model alphas) are NOT built in this task — the Replicator decides
those in a follow-up task.

Panel columns produced (per task spec):
  permno, gvkey, month, ret, retx, prc, shrout, vol, me,
  max_5, beta_m, bm, mom, rev, illiq, ivol, roe
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from utils.env import get_clickhouse_config
from utils.paths import paper_layout

from clickhouse_driver import Client


# ---------------------------------------------------------------------------
# Paths / config
# ---------------------------------------------------------------------------

SLUG = "bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to"
LAYOUT = paper_layout(SLUG)
LAYOUT.ensure()

SQL_DIR = LAYOUT.src_path("sql")
PANEL_OUT = LAYOUT.data_path("panel.parquet")
SUMMARY_OUT = LAYOUT.data_path("panel_summary.json")


def _client() -> Client:
    cfg = get_clickhouse_config()
    return Client(
        host=cfg["host"],
        port=int(cfg["port"]),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        settings={"max_execution_time": 600},
    )


def q(sql: str) -> pd.DataFrame:
    """Run a SQL string against ClickHouse, return a DataFrame."""
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    c.disconnect()
    return pd.DataFrame(data, columns=[x[0] for x in cols])


def q_file(name: str) -> pd.DataFrame:
    """Read a SQL file under src/sql/ and execute it."""
    sql = (SQL_DIR / name).read_text()
    return q(sql)


# ---------------------------------------------------------------------------
# Build the panel
# ---------------------------------------------------------------------------

def build_panel() -> pd.DataFrame:
    """Build the analysis-ready stock-month panel from ClickHouse."""
    print(f"[main] Executing {SQL_DIR / '10_panel.sql'} …")
    panel = q_file("10_panel.sql")
    print(f"[main] Raw panel: {panel.shape[0]:,} rows × {panel.shape[1]} cols")

    # Cast types. ClickHouse Nullable returns Python None.
    if "month" in panel.columns:
        panel["month"] = pd.to_datetime(panel["month"])
    for c in panel.columns:
        if c in {"permno", "gvkey"}:
            panel[c] = panel[c].astype("string")
        elif c == "siccd":
            panel[c] = panel[c].astype("Int64")

    # Drop the siccd aux column (not part of the requested panel).
    if "siccd" in panel.columns:
        panel = panel.drop(columns=["siccd"])

    # Compute mom (cumulative return over t-12..t-2) in Python to avoid
    # ClickHouse "aggregate-inside-aggregate" errors.
    if {"permno", "month", "ret"}.issubset(panel.columns):
        panel = panel.sort_values(["permno", "month"]).reset_index(drop=True)
        # Use retx (= ret excl dividends) for momentum to match convention;
        # fall back to ret where retx missing.
        ret_for_mom = panel["retx"].fillna(panel["ret"])
        panel["mom"] = (
            ret_for_mom.groupby(panel["permno"])
            .transform(lambda s: (1 + s).rolling(11, min_periods=11).apply(np.prod, raw=True).shift(1) - 1)
        )

    return panel


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

KEY_COLS = ["max_5", "beta_m", "bm", "mom", "rev", "illiq", "ivol", "roe"]


def summarise(panel: pd.DataFrame) -> dict:
    """Compute panel-level diagnostics for the report."""
    out: dict = {}

    # Dimensions.
    out["n_rows"] = int(panel.shape[0])
    out["n_cols"] = int(panel.shape[1])
    out["n_months"] = int(panel["month"].nunique())
    out["n_permnos"] = int(panel["permno"].nunique())
    if "gvkey" in panel.columns:
        out["n_gvkeys"] = int(panel["gvkey"].dropna().nunique())

    # Per-column null counts and summary stats.
    per_col: dict = {}
    for c in panel.columns:
        s = panel[c]
        per_col[c] = {
            "n_non_null": int(s.notna().sum()),
            "n_null": int(s.isna().sum()),
            "dtype": str(s.dtype),
        }
        if pd.api.types.is_numeric_dtype(s):
            non_null = s.dropna()
            if len(non_null):
                per_col[c].update(
                    mean=float(non_null.mean()),
                    median=float(non_null.median()),
                    std=float(non_null.std()),
                    min=float(non_null.min()),
                    max=float(non_null.max()),
                )
    out["per_column"] = per_col

    # Obs per month.
    obs_per_month = panel.groupby("month").size()
    out["obs_per_month"] = {
        "mean": float(obs_per_month.mean()),
        "min": int(obs_per_month.min()),
        "max": int(obs_per_month.max()),
        "median": float(obs_per_month.median()),
    }

    # Stocks per month.
    stocks_per_month = panel.groupby("month")["permno"].nunique()
    out["stocks_per_month"] = {
        "mean": float(stocks_per_month.mean()),
        "min": int(stocks_per_month.min()),
        "max": int(stocks_per_month.max()),
        "median": float(stocks_per_month.median()),
    }

    # Summary stats for the key signal columns.
    key_stats: dict = {}
    for c in KEY_COLS:
        if c in panel.columns:
            non_null = panel[c].dropna()
            if len(non_null):
                key_stats[c] = {
                    "n": int(len(non_null)),
                    "mean": float(non_null.mean()),
                    "median": float(non_null.median()),
                    "std": float(non_null.std()),
                    "min": float(non_null.min()),
                    "max": float(non_null.max()),
                    "p1": float(non_null.quantile(0.01)),
                    "p99": float(non_null.quantile(0.99)),
                }
            else:
                key_stats[c] = {"n": 0}
    out["key_stats"] = key_stats

    return out


def print_report(stats: dict) -> None:
    print("\n========== PANEL REPORT ==========")
    print(f"Rows:           {stats['n_rows']:,}")
    print(f"Cols:           {stats['n_cols']}")
    print(f"Unique months:  {stats['n_months']:,}")
    print(f"Unique permnos: {stats['n_permnos']:,}")
    if "n_gvkeys" in stats:
        print(f"Unique gvkeys:  {stats['n_gvkeys']:,}")
    print()
    print("Obs per month:")
    for k, v in stats["obs_per_month"].items():
        print(f"  {k:>7}: {v}")
    print("Stocks per month:")
    for k, v in stats["stocks_per_month"].items():
        print(f"  {k:>7}: {v}")
    print()
    print("Per-column non-null counts and summary stats (key cols):")
    for c, info in stats["per_column"].items():
        line = f"  {c:>10}: non-null={info['n_non_null']:,}  null={info['n_null']:,}"
        if "mean" in info:
            line += (
                f"  mean={info['mean']:.4g}  median={info['median']:.4g}"
                f"  std={info['std']:.4g}  min={info['min']:.4g}  max={info['max']:.4g}"
            )
        print(line)
    print()
    print("Key-signal summary stats:")
    for c, info in stats["key_stats"].items():
        if info.get("n", 0) == 0:
            print(f"  {c:>10}: no non-null obs")
            continue
        print(
            f"  {c:>10}: n={info['n']:,}  mean={info['mean']:.4g}"
            f"  median={info['median']:.4g}  std={info['std']:.4g}"
            f"  min={info['min']:.4g}  max={info['max']:.4g}"
            f"  p1={info['p1']:.4g}  p99={info['p99']:.4g}"
        )
    print("==================================\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    panel = build_panel()
    panel.to_parquet(PANEL_OUT, index=False)
    print(f"[main] Wrote {PANEL_OUT} ({panel.shape[0]:,} rows × {panel.shape[1]} cols)")

    stats = summarise(panel)
    SUMMARY_OUT.write_text(json.dumps(stats, indent=2, default=float))
    print(f"[main] Wrote {SUMMARY_OUT}")

    print_report(stats)


if __name__ == "__main__":
    main()
