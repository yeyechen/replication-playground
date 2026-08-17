"""Iteration-13 surgical patch: rebuild `iskew` and `eiskew` on the existing
panel after fixing the M3b residual-moment intercept omission in
`main._rolling_iskew`.

The bug (main.py _rolling_iskew): the FF3 residual central moments Sr2/Sr3 were
expanded omitting the intercept beta b0 (expanding r = y - q.f instead of
r = y - b0 - q.f). The betas were correct (OLS solve used b0), but the 2nd and
3rd residual window moments were biased, collapsing the skewness (single-firm
spot check: g1 -0.0047 before vs -0.2436 hand-computed). Fixed in main.py; this
script regenerates the affected columns without re-running the full pipeline.

Run from repo root (utils/ and src/ on sys.path), or with
PYTHONPATH=<repo-root>:<src>.
"""
from __future__ import annotations

import sys

sys.path.insert(0, "replications/max_on_steroids_attempt5_deepseek/src")
sys.path.insert(0, ".")

import numpy as np
import pandas as pd

import main as M

LAYOUT = M.LAYOUT


def main() -> None:
    panel = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
    panel = panel.sort_values(["permno", "month"]).reset_index(drop=True)

    print("=== M3b: rebuild iskew (fixed residual-moment expansion) ===")
    old_iskew = panel["iskew"].copy()
    daily = M._load_daily_universe()
    ff3 = M.q_file("ff3_daily.sql")
    ff3["dt"] = pd.to_datetime(ff3["dt"])
    iskew = M._rolling_iskew(daily, ff3)
    panel = panel.drop(columns=["iskew"], errors="ignore")
    panel = panel.merge(iskew, on=["permno", "month"], how="left")
    print(f"  iskew before: mean={old_iskew.mean():.4f} std={old_iskew.std():.4f} "
          f"median={old_iskew.median():.4f}")
    print(f"  iskew after : mean={panel['iskew'].mean():.4f} std={panel['iskew'].std():.4f} "
          f"median={panel['iskew'].median():.4f}")

    print("=== rebuild eiskew (two-step on fixed iskew) ===")
    old_eiskew = panel["eiskew"].copy()
    # _eiskew needs the hexcd/hsiccd metadata (E(ISKEW) predictor set) that the
    # final panel drops; re-merge it here exactly as build_section4 does.
    meta = M.q_file("panel_meta.sql")
    meta["month"] = pd.to_datetime(meta["date"]).dt.to_period("M")
    meta = (meta[["permno", "month", "hexcd", "hsiccd"]]
            .drop_duplicates(subset=["permno", "month"], keep="last"))
    panel = panel.drop(columns=["hexcd", "hsiccd"], errors="ignore")
    panel = panel.merge(meta, on=["permno", "month"], how="left")
    panel = panel.sort_values(["permno", "month"]).reset_index(drop=True)
    panel["eiskew"] = M._eiskew(panel).values
    panel = panel.drop(columns=["hexcd", "hsiccd"], errors="ignore")
    print(f"  eiskew before: mean={old_eiskew.mean():.4f} std={old_eiskew.std():.4f} "
          f"median={old_eiskew.median():.4f}")
    print(f"  eiskew after : mean={panel['eiskew'].mean():.4f} std={panel['eiskew'].std():.4f} "
          f"median={panel['eiskew'].median():.4f}")

    panel.to_parquet(LAYOUT.data_path("panel.parquet"), index=False)
    print(f"Wrote {LAYOUT.data_path('panel.parquet')}  {panel.shape}")


if __name__ == "__main__":
    main()
