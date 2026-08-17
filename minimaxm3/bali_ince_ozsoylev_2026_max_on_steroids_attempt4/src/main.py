"""
MAX on Steroids — Stage 7 panel builder.

This module builds the analysis-ready panel used by Tables 1, 6, and 2 of
"Bali, Ince, Ozsoylev — MAX on Steroids: A New Measure of Investor
Attraction to Lottery Stocks".

Pipeline (all pushed into a single ClickHouse SQL CTE chain in
src/sql/07_panel.sql):

  1. PIT-filtered daily universe (shrcd 10/11, exchcd 1/2/3, SIC exclusion,
     ret > -0.5).
  2. Monthly MAX signal = average of the top-5 daily returns in month.
     Requires ndays >= 15 and month-end |prc| >= $5.
  3. Daily market excess return (vwretd - rf/21).
  4. 252-day rolling BETA and IVOL per (permno, date), aggregated to
     month-end with argMax(date, ...).
  5. Monthly ME from crsp_202601.msf (|prc| * shrout * 1000).
  6. Monthly BM from Compustat annual fundamentals with FF (1992) lag:
     fiscal-year t -> monthly returns July (t+1) to June (t+2).
     Book equity = ceq + txdb + itcb - pstk, fallback at - dlc - dltt - pstk.
  7. Monthly MOM (12-2 cum return) and REV (formation-month return).
  8. Monthly ILLIQ (Amihud, *1e6) and IVOL.
  9. Next-month excess return (leadInFrame mret - rf).
 10. Save to data/panel.parquet; run sanity diagnostics; Table 1 spot check.

Sanity checks: panel dimensions, MAX / BETA / ME distributions, single-firm
IBM 2010 sample, and a 10-1 decile spread on raw excess returns.

The code reads credentials from .env (utils.env.get_clickhouse_config).
"""

import os
import sys
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from clickhouse_driver import Client

# --- repo plumbing ----------------------------------------------------------

# Repo root is three levels up from src/main.py:
#   src/ -> max_on_steroids_attempt4/ -> replications/ -> rep-it-up/
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from utils.env import get_clickhouse_config  # noqa: E402
from utils.paths import paper_layout  # noqa: E402

SLUG = "max_on_steroids_attempt4"
LAYOUT = paper_layout(SLUG)
LAYOUT.ensure()

SQL_DIR = LAYOUT.src_path("sql")
DATA_PATH = LAYOUT.data_path("panel.parquet")
PREP_DIR = LAYOUT.preparations_path("preprocessing_rules.json")

# --- parameters from preprocessing_rules.json -------------------------------

with open(PREP_DIR) as f:
    RULES = json.load(f)

SAMPLE_START = "1968-01-01"
SAMPLE_END = "2022-12-31"
N_BINS = 10


# --- ClickHouse connection --------------------------------------------------

_CFG = get_clickhouse_config()


def _client() -> Client:
    return Client(
        host=_CFG["host"],
        port=int(_CFG["port"]),
        user=_CFG["user"],
        password=_CFG["password"],
        database=_CFG.get("database", "default"),
        settings={"max_execution_time": 900},
    )


def q(sql: str) -> pd.DataFrame:
    """Execute a SQL query and return a DataFrame."""
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


# --- pipeline ---------------------------------------------------------------


def build_panel() -> pd.DataFrame:
    """Run the panel CTE chain and return the panel as a DataFrame."""
    sql_path = SQL_DIR / "07_panel.sql"
    sql = sql_path.read_text()
    print(f"[panel] running 07_panel.sql ({sql_path.stat().st_size} bytes)")
    t0 = time.time()
    df = q(sql)
    elapsed = time.time() - t0
    print(f"[panel] {len(df):,} rows x {df.shape[1]} cols, {elapsed:.1f}s")
    return df


# --- diagnostics ------------------------------------------------------------


def print_diagnostics(panel: pd.DataFrame) -> None:
    print("\n" + "=" * 72)
    print("PANEL DIAGNOSTICS")
    print("=" * 72)

    # Dimensions
    n_rows = len(panel)
    n_perm = panel["permno"].nunique()
    months = pd.to_datetime(panel["month"]).dt.to_period("M")
    n_months = months.nunique()
    first_month = str(months.min())
    last_month = str(months.max())
    print(f"rows            : {n_rows:,}")
    print(f"distinct permnos: {n_perm:,}")
    print(f"distinct months : {n_months}")
    print(f"date range      : {first_month} .. {last_month}")
    if n_months > 0:
        print(f"avg obs / month : {n_rows / n_months:,.0f}")

    # NA% of key columns
    print("\nNA% per column:")
    for col in panel.columns:
        na_pct = panel[col].isna().mean() * 100
        print(f"  {col:15s} {na_pct:6.2f}%")

    # MAX distribution (decimal -> percent)
    print("\nMAX distribution (decimal):")
    print(panel["MAX"].describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]))

    # BETA
    print("\nBETA distribution:")
    print(panel["BETA"].describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]))

    # ME
    print("\nME distribution (dollars):")
    print(panel["ME"].describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]))


def print_ibm_sanity(panel: pd.DataFrame) -> None:
    print("\n" + "=" * 72)
    print("SINGLE-FIRM SANITY CHECK: permno=14593 (IBM), 2010-01 .. 2010-06")
    print("=" * 72)
    sub = panel[(panel["permno"] == 14593)].copy()
    sub["month"] = pd.to_datetime(sub["month"])
    sub = sub[(sub["month"] >= "2010-01-01") & (sub["month"] <= "2010-06-30")]
    sub = sub.sort_values("month")
    if sub.empty:
        print("No rows for IBM in 2010 H1 — universe filter too tight?")
        return
    cols = ["month", "MAX", "BETA", "ME", "ret", "ret_excess_next"]
    print(sub[cols].to_string(index=False))


def quick_table1_spot_check(panel: pd.DataFrame) -> None:
    """Compute decile sort on MAX, then 10-1 VW excess-return spread."""
    print("\n" + "=" * 72)
    print("TABLE 1 SPOT CHECK: MAX deciles, 10-1 raw VW excess return spread")
    print("=" * 72)
    sub = panel.dropna(subset=["MAX", "ret_excess_next", "ME"]).copy()
    sub["month"] = pd.to_datetime(sub["month"])

    # Independent deciles per month (all-stocks breakpoints).
    # Avoid pandas groupby.apply quirks: just compute decile per month directly.
    sub["month"] = pd.to_datetime(sub["month"])
    sub = sub.sort_values(["month", "MAX"])
    sub["decile"] = (
        sub.groupby("month")["MAX"]
        .transform(
            lambda x: pd.qcut(x, q=N_BINS, labels=False, duplicates="drop") + 1
        )
    )
    sub = sub.dropna(subset=["decile"])
    sub["decile"] = sub["decile"].astype(int)

    # VW per decile per month: weight by ME
    def vw(g: pd.DataFrame) -> float:
        w = g["ME"].clip(lower=1.0)
        return float((g["ret_excess_next"] * w).sum() / w.sum())

    decile_ret = (
        sub.groupby(["month", "decile"])
        .apply(lambda g: pd.Series({"VW": vw(g)}), include_groups=False)
        .reset_index()
    )
    pivot = decile_ret.pivot(index="month", columns="decile", values="VW").sort_index()
    spread = (pivot[10] - pivot[1]).dropna()

    avg_spread = spread.mean()
    tstat = (
        avg_spread / (spread.std(ddof=1) / np.sqrt(len(spread)))
        if len(spread) > 1 else float("nan")
    )

    paper_value = -0.0095  # paper Table 1: -0.95%/month, raw RET-RF

    print(f"\nMAX decile counts (avg across months): "
          f"{sub.groupby('decile').size().mean():.0f}")
    print(f"\nDecile mean VW ret_excess_next (%/month):")
    means = pivot.mean() * 100
    print(means.round(3).to_string())

    print(f"\n10-1 spread (replicated, %/month): {avg_spread * 100:.3f}")
    print(f"10-1 t-stat (iid, no NW):            {tstat:.3f}")
    print(f"paper value (Table 1):                 {paper_value * 100:.2f}")
    print(f"months covered:                        {spread.shape[0]}")


# --- main -------------------------------------------------------------------


def main() -> int:
    t0 = time.time()
    panel = build_panel()
    if panel.empty:
        print("[panel] no rows produced; aborting")
        return 1

    # Persist to parquet
    panel.to_parquet(DATA_PATH, index=False)
    print(f"[panel] saved {DATA_PATH} ({DATA_PATH.stat().st_size / 1e6:.1f} MB)")

    print_diagnostics(panel)
    print_ibm_sanity(panel)
    quick_table1_spot_check(panel)

    print(f"\nTotal wall time: {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
