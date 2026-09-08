"""Replication figures (Task C, iteration 10). Headless matplotlib.

1. results/fig2_return_responses.png — Fig. 2 Panel A replication:
   average return-response gamma_k (percent) for ALL lags k = 1..240
   (simple monthly regressions r_it on r_i,t-k, cov/var slope,
   averaged 1965-01..2002-12), annual lags (k % 12 == 0) highlighted.
2. results/seasonal_strategy_pnl.png — cumulative (log scale) return
   of the y2_5 Annual EW 10-1 spread strategy, 1965-01..2002-12.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np              # noqa: E402
import pandas as pd             # noqa: E402

from main import (DECIMALS_RET, HOLD_END, HOLD_START, LAYOUT, N_BINS,
                  _wide_matrix)
from table1 import _slope


def fig2(panel: pd.DataFrame) -> None:
    R, m_idx, months, permnos, _ = _wide_matrix(panel)
    R = R.astype(np.float64)
    hold_rows = [i for i, m in enumerate(months)
                 if HOLD_START <= m <= HOLD_END]
    lags = np.arange(1, 241)
    gamma = {k: np.full(len(hold_rows), np.nan) for k in lags}
    for j, t in enumerate(hold_rows):
        y = R[t, :]
        for k in lags:
            g, _ = _slope(y, R[t - k, :])
            gamma[k][j] = g
    est = np.array([np.nanmean(gamma[k]) * DECIMALS_RET for k in lags])

    annual = lags % 12 == 0
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(lags[~annual], est[~annual], width=1.0, color="#7f8c8d",
           alpha=0.85, label="non-annual lags")
    ax.bar(lags[annual], est[annual], width=1.6, color="#c0392b",
           label="annual lags (k = 12, 24, ...)")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xlabel("Lag k (months)")
    ax.set_ylabel("Average return response $\\gamma_k$ (percent)")
    ax.set_title("Heston & Sadka (2008) Fig. 2 Panel A — return responses "
                 "by lag, 1965-01..2002-12 (replication)")
    ax.set_xlim(0, 241)
    ax.legend(loc="upper right", frameon=False)
    fig.tight_layout()
    fig.savefig(LAYOUT.result_path("fig2_return_responses.png"), dpi=150)
    plt.close(fig)
    print(f"[fig2] gamma_1={est[0]:.2f} gamma_12={est[11]:.2f} "
          f"gamma_240={est[-1]:.2f} (percent)")


def seasonal_pnl(t2_series: dict) -> None:
    br = t2_series[("y2_5", "annual")].copy()
    br["month"] = pd.PeriodIndex(pd.to_datetime(br["month"]), freq="M")
    piv = br.pivot(index="month", columns="decile", values="EW")
    s = (piv[N_BINS] - piv[1]).dropna()
    cum = (1.0 + s).cumprod()
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(s.index.to_timestamp(), cum, color="#c0392b", lw=1.6)
    ax.set_yscale("log")
    ax.set_xlabel("Month")
    ax.set_ylabel("Cumulative return (log scale)")
    ax.set_title("Seasonal strategy — y2_5 Annual EW 10-1 spread, "
                 f"{s.index[0]}..{s.index[-1]} "
                 f"(mean {s.mean()*DECIMALS_RET:.2f}%/month, "
                 f"{len(s)} months; replication)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(LAYOUT.result_path("seasonal_strategy_pnl.png"), dpi=150)
    plt.close(fig)
    print(f"[pnl] y2_5 annual 10-1: final cumulative {cum.iloc[-1]:.2f}x, "
          f"mean {s.mean()*DECIMALS_RET:.2f}%/mo over {len(s)} months")


def make_plots(panel: pd.DataFrame, t2_series: dict) -> None:
    fig2(panel)
    seasonal_pnl(t2_series)
