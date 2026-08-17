"""Surgical patch: rebuild `ce`/`cei` (log net-issuance residual) and
`betamax` (market-MAX regression) on the existing panel, plus the downstream
`rank_cei`, `mis`, `iss_idx` columns that feed on `cei`.

Composite equity issuance (Daniel-Titman 2006) is the LOG 12-month net-issuance
residual: ce = log(me_t / me_{t-12}) - log(1 + cumret12), computed with a
CALENDAR-month-aligned 12-month lookback (not a row-position shift) over the
panel's split-invariant me = abs(prc) * shrout * 1000. Firms with a data gap
have no t-12 row and get NaN. This is the correct DT construction: log(me
growth) tracks log(1 + 12-mo cumulative return) at corr ~0.92, so ce is a small
residual (std ~0.18) rather than the ~7.0 std produced by the prior
prc * shrout * cfacshr simple-growth construction (which double-counted the
split factor and blew up on share-record restatements).

Run from repo root (utils/ and src/ on sys.path).
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

    print("=== FIX: rebuild ce/cei (log net-issuance residual) ===")
    old_ce = panel["ce"].copy()
    # Composite equity issuance (Daniel-Titman 2006): ce = 12-month growth in
    # market equity minus the 12-month cumulative return, expressed in LOG terms
    # (the canonical DT form that makes ce a small net-issuance residual):
    #   ce = log(me_t / me_{t-12}) - log(1 + cumret12)
    # me is the panel's own split-invariant market equity abs(prc)*shrout*1000
    # (a split halves prc and doubles shrout on a within-date basis, leaving the
    # product unchanged). log(me_t/me_{t-12}) tracks log(1+cumret12) at corr ~0.92,
    # so ce is the small residual the paper reports (Table 2 CE median
    # -0.020..+0.013). The prior construction (prc*shrout*cfacshr in simple growth)
    # double-counted the split factor AND carried genuine share-restatement outliers
    # (e.g. permno 89134 shrout 119->476,871 thousands), giving ce std ~7 and a 30x-
    # inflated FM coefficient.
    # calendar 12-month lookback: join me at (permno, month-12)
    lag = panel[["permno", "month", "me"]].copy()
    lag["month"] = lag["month"] + 12
    lag = lag.rename(columns={"me": "me_l12"})
    panel = panel.merge(lag, on=["permno", "month"], how="left", suffixes=("", "_y"))
    # genuinely broken input rows (missing / non-positive lagged ME) -> NaN
    bad_lag = ~(panel["me_l12"] > 0) | ~np.isfinite(panel["me_l12"].astype(float))
    panel["_me_l12"] = panel["me_l12"].where(~bad_lag)
    panel["_me_gr12"] = np.log(panel["me"].astype(float) / panel["_me_l12"])
    panel["_cumlog12"] = np.log1p(panel["cumret12"].astype(float))
    panel["cei"] = panel["_me_gr12"] - panel["_cumlog12"]
    panel["ce"] = panel["cei"]
    panel["ce"] = panel["ce"].mask(~np.isfinite(panel["ce"].astype(float)))
    panel["cei"] = panel["cei"].mask(~np.isfinite(panel["cei"].astype(float)))
    panel = panel.drop(columns=["me_l12", "_me_l12", "_me_gr12", "_cumlog12"],
                       errors="ignore")

    # downstream: rank_cei (ascending), then mis + iss_idx
    panel["rank_cei"] = M._rank_asc(panel, "cei").astype(float)
    rank_cols = ["rank_nsi", "rank_cei", "rank_acc", "rank_noa", "rank_ag",
                 "rank_inv_at", "rank_distress", "rank_oscore", "rank_mom12_2",
                 "rank_gp", "rank_roa_q"]
    panel["mis"] = panel[rank_cols].mean(axis=1)
    panel["iss_idx"] = panel[["rank_nsi", "rank_cei", "rank_csi5"]].mean(axis=1)

    print(f"  ce before: max={old_ce.max():.1f} mean={old_ce.mean():.4f} std={old_ce.std():.3f}")
    print(f"  ce after : max={panel['ce'].max():.1f} mean={panel['ce'].mean():.4f} std={panel['ce'].std():.3f}")

    print("=== FIX 3: rebuild betamax (market-MAX dsi top-5) ===")
    old_bm = panel["betamax"].copy()
    panel["betamax"] = M._betamax(panel).values
    print(f"  betamax before: mean={old_bm.mean():.4f} std={old_bm.std():.4f}")
    print(f"  betamax after : mean={panel['betamax'].mean():.4f} std={panel['betamax'].std():.4f}")

    panel.drop(columns=["mkt_max"], errors="ignore", inplace=True)

    panel.to_parquet(LAYOUT.data_path("panel.parquet"), index=False)
    print(f"Wrote {LAYOUT.data_path('panel.parquet')}  {panel.shape}")


if __name__ == "__main__":
    main()
