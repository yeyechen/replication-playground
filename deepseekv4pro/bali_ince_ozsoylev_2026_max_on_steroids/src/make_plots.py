"""Iteration-9 plots (headless Agg).

(a) results/plot_maxbeta_vs_max_spread.png — cumulative VW return of the
    MAX^beta 10-1 spread vs the MAX 10-1 spread, 1968-2022 (two lines).
(b) results/plot_maxbeta_decile_means.png — bar chart of the 10 MAX^beta
    decile mean VW forward returns (percent per month), with the paper's
    monotonic-decline pattern noted in the caption.

Reuses main._table_vw_series (MAX deciles) and main._t3_bin_vw_series
(MAX^beta regrouped deciles, Assumption 6). Both are indexed by return month.
"""
from __future__ import annotations

import sys

sys.path.insert(0, "replications/max_on_steroids_attempt5_deepseek/src")
sys.path.insert(0, ".")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import main as M

LAYOUT = M.LAYOUT


def main() -> None:
    panel = pd.read_parquet(LAYOUT.data_path("panel.parquet"))

    max_wide = M._table_vw_series(panel, "max")          # MAX deciles VW
    maxb_wide = M._t3_bin_vw_series(panel)               # MAX^beta deciles VW

    max_sprd = max_wide[10] - max_wide[1]
    maxb_sprd = maxb_wide[10] - maxb_wide[1]

    # ---- (a) cumulative VW spread returns ----
    df = pd.DataFrame({"max_sprd": max_sprd, "maxb_sprd": maxb_sprd}).dropna()
    df = df.reset_index()
    df = df.rename(columns={df.columns[0]: "month"})
    df["month"] = df["month"].dt.to_timestamp()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["month"], (1 + df["maxb_sprd"]).cumprod() - 1,
            label="MAX^beta 10-1 spread (VW)", color="#f31d36", linewidth=2)
    ax.plot(df["month"], (1 + df["max_sprd"]).cumprod() - 1,
            label="MAX 10-1 spread (VW)", color="#1e88e5", linewidth=2)
    ax.set_xlabel("Month")
    ax.set_ylabel("Cumulative Return")
    ax.set_title("Cumulative VW Return: MAX^beta 10-1 spread vs MAX 10-1 spread (1968-2022)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(LAYOUT.result_path("plot_maxbeta_vs_max_spread.png"), dpi=150)
    plt.close(fig)
    print("wrote results/plot_maxbeta_vs_max_spread.png")

    # ---- (b) MAX^beta decile mean VW forward returns (percent/mo) ----
    means = maxb_wide.mean() * 100.0  # percent per month, deciles 1..10
    means = means.reindex(range(1, 11))

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ["#f31d36" if d == 10 else "#1e88e5" for d in range(1, 11)]
    ax.bar([str(d) for d in range(1, 11)], means.values, color=colors)
    ax.set_xlabel("MAX^beta Decile")
    ax.set_ylabel("Mean VW Forward Return (% per month)")
    ax.set_title("MAX^beta Decile Mean VW Forward Returns (1968-2022)")
    ax.axhline(0, color="black", linewidth=0.8)
    fig.text(0.5, 0.01,
             "Paper pattern: mean forward returns decline monotonically from the "
             "low-MAX^beta (D1) to the high-MAX^beta (D10) decile, driving a "
             "negative 10-1 spread.",
             ha="center", fontsize=9)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(LAYOUT.result_path("plot_maxbeta_decile_means.png"), dpi=150)
    plt.close(fig)
    print("wrote results/plot_maxbeta_decile_means.png")

    print("decile means (%/mo):", dict(zip(range(1, 11), means.round(3))))


if __name__ == "__main__":
    main()
