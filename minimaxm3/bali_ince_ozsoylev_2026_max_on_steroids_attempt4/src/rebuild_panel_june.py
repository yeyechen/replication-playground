"""
rebuild_panel_june.py — adds me_june_t column to data/panel.parquet.

Convention (FF 1993 / Bali-Cakici-Whitelaw 2011 carry-forward):
  For each (permno, month), me_june_t = ME at calendar-June-of-year(y-1)
  if month is July-Dec of year y, else ME at calendar-June-of-year(y-1)
  if month is Jan-June of year y (i.e. always the June just BEFORE the
  12-month holding window that begins in month).

  Equivalently, for any month m in year y:
      - If month(m) >= 7:  june_key = y . 06
      - If month(m) <= 6:  june_key = (y-1) . 06
  where "june_key" identifies the calendar June that supplies ME.

Outputs: data/panel.parquet now has additional column `me_june_t`
(plus ME_lag1 backup is preserved).
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from clickhouse_driver import Client

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from utils.env import get_clickhouse_config  # noqa: E402
from utils.paths import paper_layout  # noqa: E402

SLUG = "max_on_steroids_attempt4"
LAYOUT = paper_layout(SLUG)
LAYOUT.ensure()

PANEL_PATH = LAYOUT.data_path("panel.parquet")
SQL_DIR = LAYOUT.src_path("sql")
SQL_FILE = SQL_DIR / "08_me_june.sql"

_CFG = get_clickhouse_config()


def _client() -> Client:
    return Client(
        host=_CFG["host"],
        port=int(_CFG["port"]),
        user=_CFG["user"],
        password=_CFG["password"],
        database=_CFG.get("database", "default"),
        settings={"max_execution_time": 600},
    )


def q(sql: str) -> pd.DataFrame:
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


def main() -> int:
    t0 = time.time()
    print(f"[rebuild_june] loading panel from {PANEL_PATH}")
    panel = pd.read_parquet(PANEL_PATH)
    print(f"[rebuild_june] panel: {len(panel):,} rows x {panel.shape[1]} cols")

    panel["month"] = pd.to_datetime(panel["month"])
    panel["year"] = panel["month"].dt.year.astype(int)
    panel["mon"] = panel["month"].dt.month.astype(int)
    # june_key per row: year(y - 1) . 06 if month <= 6; else year(y) . 06
    panel["june_year"] = np.where(panel["mon"] <= 6,
                                  panel["year"] - 1,
                                  panel["year"])
    # Same year-month key shape as 08_me_june.sql emits.
    panel["ym_key"] = panel["june_year"] * 100 + 6

    print(f"[rebuild_june] loading June ME snapshots from ClickHouse")
    sql = SQL_FILE.read_text()
    june_df = q(sql)
    print(f"[rebuild_june] June ME snapshot rows: {len(june_df):,}")

    june_df["ym_key"] = june_df["ym_key"].astype(int)
    june_df["permno"] = june_df["permno"].astype(int)
    june_df = june_df.rename(columns={"ME_june": "me_june_t"})

    # Drop the temp columns to avoid lingering duplicate keys
    panel2 = panel.merge(
        june_df[["permno", "ym_key", "me_june_t"]],
        on=["permno", "ym_key"],
        how="left",
    )
    print(f"[rebuild_june] merge done. me_june_t null count: "
          f"{panel2['me_june_t'].isna().sum():,} "
          f"of {len(panel2):,}")

    # Diagnostic: distribution of me_june_t and ratio vs ME
    sub = panel2[panel2["me_june_t"] > 0].copy()
    sub["ratio"] = sub["me_june_t"] / sub["ME"]
    print(f"[rebuild_june] me_june_t vs ME — ratios: mean={sub['ratio'].mean():.3f}"
          f" median={sub['ratio'].median():.3f}")

    # Drop helper columns; keep ME_lag1 backup (compute it here too)
    panel2 = panel2.drop(columns=["year", "mon", "june_year", "ym_key"])
    # ME_lag1: prior-month ME per permno (backup column, kept for diagnostics)
    panel2 = panel2.sort_values(["permno", "month"]).reset_index(drop=True)
    panel2["ME_lag1"] = panel2.groupby("permno")["ME"].shift(1)

    # Reorder columns: keep original panel columns first, then
    # me_june_t and ME_lag1 at the end (without reusing the
    # dropped helper names).
    orig_cols = [c for c in panel.columns if c in panel2.columns]
    extra_cols = [c for c in ["me_june_t", "ME_lag1"] if c in panel2.columns]
    panel2 = panel2[orig_cols + extra_cols]

    # Save back
    panel2.to_parquet(PANEL_PATH, index=False)
    print(f"[rebuild_june] saved {PANEL_PATH} "
          f"({PANEL_PATH.stat().st_size / 1e6:.1f} MB)"
          f" — {panel2.shape[0]:,} rows x {panel2.shape[1]} cols"
          f" in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
