"""
Experiment: eligibility A/B (Iteration 3 mandate).

Standalone diagnostic — does NOT touch panel.parquet, metrics.json, or any
committed pipeline output. Only prints a comparison report.

Rules:
  A (current, Assumption 5): ret at holding month t AND ret in EVERY
    formation month of the lag set; signal = mean over all lag months.
  B (average-of-available): ret at t AND ret in >= 1 formation month;
    signal = mean over AVAILABLE formation months only.
  C (diagnostic): ret at t AND ret in >= (n_lags - 2) formation months
    (at most 2 missing); signal = mean over available months.

Strategies: y1 and y2_5 x (All / Annual / Nonannual), deciles D1..D10,
EW, 10-1 spread, simple t-stats, holding months 1965-01..2002-12.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SKILL_ROOT = Path("/home/ra_yeye/.claude/skills/rep-it-up")
sys.path.insert(0, str(SKILL_ROOT))

from utils.paths import paper_layout  # noqa: E402
from utils.quantile import assign_quantiles  # noqa: E402

SLUG = "heston_sadka_2008_seasonality_in_the_cross_section_of_stock_returns"
LAYOUT = paper_layout(SLUG)

HOLD_START = pd.Period("1965-01", freq="M")
HOLD_END = pd.Period("2002-12", freq="M")
N_BINS = 10
PCT = 100.0

LAG_SETS = {
    ("y1", "all"): list(range(1, 13)),
    ("y1", "annual"): [12],
    ("y1", "nonannual"): list(range(1, 12)),
    ("y2_5", "all"): list(range(13, 61)),
    ("y2_5", "annual"): [24, 36, 48, 60],
    ("y2_5", "nonannual"): [k for k in range(13, 61) if k % 12 != 0],
}

PAPER = {  # (d1, d10, spread, spread_t); None = not quoted
    ("y1", "all"): (0.64, 2.10, 1.46, 5.58),
    ("y1", "annual"): (None, None, 1.15, 7.60),
    ("y1", "nonannual"): (0.80, 1.97, 1.17, 4.20),
    ("y2_5", "all"): (1.91, 0.84, -1.07, -5.02),
    ("y2_5", "annual"): (None, None, 0.67, 5.35),
    ("y2_5", "nonannual"): (1.99, 0.74, -1.25, -5.60),
}

RULES = {"A": 0, "B": None, "C": 2}  # max missing formation months


def wide_matrix(panel):
    months = pd.period_range(panel["month"].min(), panel["month"].max(),
                             freq="M")
    permnos = np.sort(panel["permno"].unique())
    m_idx = {m: i for i, m in enumerate(months)}
    p_idx = {p: i for i, p in enumerate(permnos)}
    R = np.full((len(months), len(permnos)), np.nan, dtype=np.float64)
    mi = panel["month"].map(m_idx).to_numpy()
    pi = panel["permno"].map(p_idx).to_numpy()
    mask = ~np.isnan(mi) & ~np.isnan(pi)
    R[mi[mask].astype(int), pi[mask].astype(int)] = panel["ret"].to_numpy()[mask]
    return R, months, permnos


def tstat(s):
    s = pd.Series(s).dropna()
    if len(s) < 2:
        return np.nan
    return float(s.mean() / (s.std(ddof=1) / np.sqrt(len(s))))


def run_rule(R, months, lags, max_missing):
    """Decile means + spread for one lag set under one eligibility rule."""
    lags = np.asarray(lags, dtype=int)
    n_lags = len(lags)
    min_avail = 1 if max_missing is None else n_lags - max_missing
    parts = []
    for t, m in enumerate(months):
        if not (HOLD_START <= m <= HOLD_END):
            continue
        cols = t - lags
        if cols.min() < 0:
            continue
        sub = R[cols, :]                              # (n_lags, n_perm)
        avail = (~np.isnan(sub)).sum(axis=0)          # available count
        ok = (avail >= min_avail) & ~np.isnan(R[t, :])
        if not ok.any():
            continue
        idx = np.where(ok)[0]
        avg = np.nanmean(sub[:, idx], axis=0)
        parts.append(pd.DataFrame({"month": str(m), "permno": permnos[idx],
                                   "sig": avg, "ret": R[t, idx]}))
    long = pd.concat(parts, ignore_index=True)
    long["decile"] = assign_quantiles(long, date_col="month", signal_col="sig",
                                      n_bins=N_BINS, warn_fallback=False)
    means = long.groupby("decile")["ret"].mean() * PCT
    piv = long.pivot_table(index="month", columns="decile", values="ret",
                           aggfunc="mean")
    spread = (piv[N_BINS] - piv[1]).dropna()
    avg_n = long.groupby("month").size().mean()
    return (float(means.get(1, np.nan)), float(means.get(N_BINS, np.nan)),
            float(spread.mean() * PCT), tstat(spread), float(avg_n))


if __name__ == "__main__":
    panel = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
    panel["month"] = pd.PeriodIndex(panel["month"], freq="M")
    R, months, permnos = wide_matrix(panel)
    print(f"panel: {len(panel):,} rows, {len(permnos):,} permnos, "
          f"{R.shape[0]} months\n")

    results = {}   # (rule, key) -> (d1, d10, spread, t, avg_n)
    for rule, mm in RULES.items():
        for key, lags in LAG_SETS.items():
            results[(rule, key)] = run_rule(R, months, lags, mm)

    label = {("y1", "all"): "y1 All", ("y1", "annual"): "y1 Annual",
             ("y1", "nonannual"): "y1 Nonannual",
             ("y2_5", "all"): "y2_5 All", ("y2_5", "annual"): "y2_5 Annual",
             ("y2_5", "nonannual"): "y2_5 Nonannual"}

    print(f"{'Strategy':<16} {'Rule':<5} {'D1':>6} {'D10':>6} {'Spread':>7} "
          f"{'t':>7} {'N/mo':>8} | paper spread [t]")
    for key in LAG_SETS:
        pd1, pd10, psp, pt = PAPER[key]
        for rule in "ABC":
            d1, d10, sp, t, n = results[(rule, key)]
            print(f"{label[key]:<16} {rule:<5} {d1:6.2f} {d10:6.2f} "
                  f"{sp:7.2f} {t:7.2f} {n:8,.0f} | "
                  f"{psp if psp else '':>5} [{pt}]")
        print()

    # eligible counts A vs B per strategy
    print("Eligible firms/month (avg), Rule A vs Rule B:")
    for key in LAG_SETS:
        na = results[("A", key)][4]
        nb = results[("B", key)][4]
        print(f"  {label[key]:<16} A {na:8,.0f}  B {nb:8,.0f}  "
              f"(B/A = {nb / na:.2f})")

    # RMSE vs paper across the six spreads, per rule
    print("\nSpread RMSE vs paper (all six strategies, %/mo):")
    for rule in "ABC":
        errs = [(results[(rule, k)][2] - PAPER[k][2]) for k in LAG_SETS]
        rmse = float(np.sqrt(np.mean(np.square(errs))))
        y1_err = np.sqrt(np.mean([e**2 for e, k in zip(errs, LAG_SETS)
                                  if k[0] == "y1"]))
        y25_err = np.sqrt(np.mean([e**2 for e, k in zip(errs, LAG_SETS)
                                   if k[0] == "y2_5"]))
        print(f"  Rule {rule}: total {rmse:.3f} | y1 {y1_err:.3f} | "
              f"y2_5 {y25_err:.3f}")
