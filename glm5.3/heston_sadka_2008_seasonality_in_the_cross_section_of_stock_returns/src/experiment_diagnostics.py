"""
Diagnostics experiment (Iteration 4 mandate, three parts). Standalone —
does NOT touch panel.parquet, metrics.json, or any committed output.

PART A — delisting-merge sensitivity of Table 1 short lags (1..8):
  Panel A simple gamma_k + NW(12) t, and Panel B spec1 coefficients + NW(12)
  t, computed on (i) the post-merge panel (data/panel.parquet) and (ii) a
  PRE-merge return matrix rebuilt from crsp_202601.msf via
  src/sql/universe_monthly.sql + the same PIT universe filter, with NO
  msedelist merge. Verifies: 555 combined cells differ, 3,642 inserted rows
  absent from the pre-merge matrix.

PART B — calendar-month decomposition of y1 (Table 7 row block L1680-1792):
  Rule A (complete formation window) 10-1 EW spreads by calendar month for
  y1 All / y1 Annual / y1 Nonannual / y2_5 Annual, plus the Feb-Dec pooled
  aggregate, 1965-01..2002-12.

PART C — Rule B (average-of-available) eligibility for long intervals
  (y6_10 / y11_15 / y16_20, All/Annual/Nonannual) vs Rule A vs paper.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SKILL_ROOT = Path("/home/ra_yeye/.claude/skills/rep-it-up")
sys.path.insert(0, str(SKILL_ROOT))
SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

from utils.paths import paper_layout  # noqa: E402
from utils.quantile import assign_quantiles  # noqa: E402
from utils.data import apply_universe_filter  # noqa: E402
from main import LAG_SETS, LAYOUT, fetch_data_cached, q_file  # noqa: E402
from table1 import _nw_tstat, _slope  # noqa: E402

HOLD_START = pd.Period("1965-01", freq="M")
HOLD_END = pd.Period("2002-12", freq="M")
N_BINS = 10
PCT = 100.0

SHORT_LAGS = list(range(1, 9))
SPEC1 = list(range(1, 13)) + [24, 36]

PAPER_PA = {  # lag -> (est, t)
    1: (-5.03, -9.03), 2: (-0.07, -0.16), 3: (1.36, 3.96), 4: (0.58, 1.42),
    5: (0.96, 2.42), 6: (0.98, 2.48), 7: (1.06, 3.18), 8: (0.58, 1.30)}
PAPER_SP1 = {
    1: (-6.80, -12.75), 2: (-1.23, -2.53), 3: (0.83, 1.91), 4: (0.49, 1.08),
    5: (1.03, 2.31), 6: (1.34, 3.28), 7: (1.08, 2.64), 8: (-0.05, -0.12)}

PAPER_T7 = {  # Table 7: Jan, Feb-Dec
    ("y1", "all"): (-4.49, 2.00), ("y1", "annual"): (3.33, 0.95),
    ("y1", "nonannual"): (-6.83, 1.90), ("y2_5", "annual"): (3.89, 0.38)}
PAPER_T7_MONTHS = {
    "y1_all": [-4.49, 1.01, 1.34, 2.17, 0.82, 3.07, 1.27, 1.26, 2.41,
               1.89, 2.56, 4.19],
    "y1_nonannual": [-6.83, 0.90, 0.91, 2.44, 0.75, 2.95, 1.38, 1.33,
                     2.24, 1.89, 2.14, 3.97]}

PAPER_LONG = {  # (interval, variant) -> (spread, spread_t) or None for t
    ("y6_10", "all"): (-0.39, None), ("y6_10", "annual"): (0.68, None),
    ("y6_10", "nonannual"): (-0.55, None),
    ("y11_15", "all"): (-0.02, None), ("y11_15", "annual"): (0.66, None),
    ("y11_15", "nonannual"): (-0.19, None),
    ("y16_20", "all"): (None, None), ("y16_20", "annual"): (0.52, None),
    ("y16_20", "nonannual"): (-0.39, None)}


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
    R[mi[mask].astype(int), pi[mask].astype(int)] = (
        panel["ret"].to_numpy()[mask])
    return R, months, permnos


def tstat(s):
    s = pd.Series(s).dropna()
    if len(s) < 2:
        return np.nan
    return float(s.mean() / (s.std(ddof=1) / np.sqrt(len(s))))


def t1_short(R, months):
    """Panel A (lags 1-8) + Panel B spec1 (lags 1-8) on a wide matrix."""
    hold_rows = [i for i, m in enumerate(months)
                 if HOLD_START <= m <= HOLD_END]
    gamma = {k: [] for k in SHORT_LAGS}
    for t in hold_rows:
        y = R[t, :]
        for k in SHORT_LAGS:
            g, _ = _slope(y, R[t - k, :])
            gamma[k].append(g)
    panA = {k: (float(np.nanmean(gamma[k])) * PCT,
                _nw_tstat(np.asarray(gamma[k], dtype=float))) for k in SHORT_LAGS}

    lags = np.asarray(SPEC1, dtype=int)
    coef = []
    for t in hold_rows:
        cols = np.concatenate(([t], t - lags))
        m = np.isfinite(R[cols, :]).all(axis=0)
        idx = np.where(m)[0]
        if len(idx) < len(lags) + 5:
            continue
        X = np.column_stack([np.ones(len(idx))] + [R[t - k, idx] for k in lags])
        beta, *_ = np.linalg.lstsq(X, R[t, idx], rcond=None)
        coef.append(beta)
    coef = np.asarray(coef)
    sp1 = {k: (float(np.nanmean(coef[:, i + 1])) * PCT,
               _nw_tstat(coef[:, i + 1]))
           for i, k in enumerate(lags) if k in SHORT_LAGS}
    return panA, sp1


def spread_series(R, months, lags, rule="A"):
    """Monthly 10-1 EW spread series (indexed by Period) + avg n/month."""
    lags = np.asarray(lags, dtype=int)
    n_lags = len(lags)
    min_avail = 1 if rule == "B" else n_lags  # A: complete window
    parts = []
    for t, m in enumerate(months):
        if not (HOLD_START <= m <= HOLD_END):
            continue
        cols = t - lags
        if cols.min() < 0:
            continue
        sub = R[cols, :]
        avail = (~np.isnan(sub)).sum(axis=0)
        ok = (avail >= min_avail) & ~np.isnan(R[t, :])
        if not ok.any():
            continue
        idx = np.where(ok)[0]
        parts.append(pd.DataFrame({"month": str(m), "sig":
                                   np.nanmean(sub[:, idx], axis=0),
                                   "ret": R[t, idx]}))
    long = pd.concat(parts, ignore_index=True)
    long["decile"] = assign_quantiles(long, date_col="month",
                                      signal_col="sig", n_bins=N_BINS,
                                      warn_fallback=False)
    piv = long.pivot_table(index="month", columns="decile", values="ret",
                           aggfunc="mean")
    spreads = (piv[N_BINS] - piv[1]).dropna()
    spreads.index = pd.PeriodIndex(spreads.index, freq="M")
    return spreads, float(long.groupby("month").size().mean())


def part_a():
    print("=" * 78)
    print("PART A — delisting-merge sensitivity of Table 1 short lags")
    print("=" * 78)
    post = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
    post["month"] = pd.PeriodIndex(post["month"], freq="M")

    raw = q_file("universe_monthly.sql")
    raw = apply_universe_filter(raw, fetch_data_cached,
                                shrcd_filter=[10, 11], exchcd_filter=[1, 2])
    raw["month"] = pd.to_datetime(raw["date"]).dt.to_period("M")
    raw["ret"] = pd.to_numeric(raw["ret"], errors="coerce")
    pre = (raw[["permno", "month", "ret"]]
           .drop_duplicates(subset=["permno", "month"], keep="first"))

    # verification: 555 combined cells differ; 3,642 inserted rows absent
    j = post.merge(pre, on=["permno", "month"], how="outer",
                   suffixes=("_post", "_pre"), indicator=True)
    both = j[j["_merge"] == "both"]
    n_differ = int(((both["ret_post"].notna()) &
                    ((both["ret_pre"].isna()) |
                     ((both["ret_post"] - both["ret_pre"]).abs() > 1e-9))
                    ).sum())
    n_combined = int(((both["ret_post"].notna()) &
                      (both["ret_pre"].notna()) &
                      ((both["ret_post"] - both["ret_pre"]).abs() > 1e-9)
                      ).sum())
    n_inserted = int((j["_merge"] == "left_only").sum())
    print(f"[verify] pre-merge rows: {len(pre):,}; post-merge: {len(post):,}; "
          f"overlapping cells with changed ret: {n_combined} (expect 555); "
          f"post-only rows: {n_inserted} (expect 3,642); "
          f"pre-missing/post-present ret: {n_differ}")

    Rpre, mpre, _ = wide_matrix(pre[["permno", "month", "ret"]])
    Rpost, mpost, _ = wide_matrix(post[["permno", "month", "ret"]])

    panA_pre, sp1_pre = t1_short(Rpre, mpre)
    panA_post, sp1_post = t1_short(Rpost, mpost)

    closer_pa = closer_sp = 0
    print("\nPanel A (simple gamma_k, lags 1-8), %/mo [NW(12) t]:")
    print(f"{'lag':>3} {'paper':>16} {'pre-merge':>16} {'post-merge':>16}")
    for k in SHORT_LAGS:
        p = PAPER_PA[k]
        print(f"{k:>3} {p[0]:7.2f} [{p[1]:6.2f}] "
              f"{panA_pre[k][0]:7.2f} [{panA_pre[k][1]:6.2f}] "
              f"{panA_post[k][0]:7.2f} [{panA_post[k][1]:6.2f}]")
        d_pre = abs(panA_pre[k][0] - p[0]) + abs(panA_pre[k][1] - p[1])
        d_post = abs(panA_post[k][0] - p[0]) + abs(panA_post[k][1] - p[1])
        closer_pa += d_pre < d_post
    print(f"cells closer to paper: pre-merge {8 - closer_pa} vs "
          f"post-merge {closer_pa} (of 8)")

    print("\nPanel B spec1 (multiple regression, lags 1-8), %/mo [NW(12) t]:")
    print(f"{'lag':>3} {'paper':>16} {'pre-merge':>16} {'post-merge':>16}")
    for k in SHORT_LAGS:
        p = PAPER_SP1[k]
        print(f"{k:>3} {p[0]:7.2f} [{p[1]:6.2f}] "
              f"{sp1_pre[k][0]:7.2f} [{sp1_pre[k][1]:6.2f}] "
              f"{sp1_post[k][0]:7.2f} [{sp1_post[k][1]:6.2f}]")
        d_pre = abs(sp1_pre[k][0] - p[0]) + abs(sp1_pre[k][1] - p[1])
        d_post = abs(sp1_post[k][0] - p[0]) + abs(sp1_post[k][1] - p[1])
        closer_sp += d_pre < d_post
    print(f"cells closer to paper: pre-merge {8 - closer_sp} vs "
          f"post-merge {closer_sp} (of 8)")
    return panA_pre, panA_post, sp1_pre, sp1_post


def part_b(R, months):
    print("\n" + "=" * 78)
    print("PART B — calendar-month decomposition of y1 (Rule A, current panel)")
    print("=" * 78)
    keys = [("y1", "all"), ("y1", "annual"), ("y1", "nonannual"),
            ("y2_5", "annual")]
    for key in keys:
        s, n = spread_series(R, months, LAG_SETS[key[0]][key[1]], rule="A")
        jan = s[[m.month == 1 for m in s.index]].mean() * PCT
        febdec = s[[m.month != 1 for m in s.index]].mean() * PCT
        pj, pf = PAPER_T7[key]
        print(f"{key[0]} {key[1]:<10} Jan {jan:6.2f} (paper {pj:6.2f}) | "
              f"Feb-Dec {febdec:5.2f} (paper {pf:5.2f}) | n/mo {n:,.0f}")

    for name, key in [("y1 All", ("y1", "all")),
                      ("y1 Nonannual", ("y1", "nonannual"))]:
        s, _ = spread_series(R, months, LAG_SETS[key[0]][key[1]], rule="A")
        by = pd.Series({mm: s[[m.month == mm for m in s.index]].mean() * PCT
                        for mm in range(1, 13)})
        pap = PAPER_T7_MONTHS["y1_all" if key[1] == "all" else "y1_nonannual"]
        print(f"\n{name} by calendar month (ours vs paper):")
        print("  " + " | ".join(
            f"{pd.Period('2000-%02d' % mm, 'M').strftime('%b')}" for mm in
            range(1, 13)))
        print("  " + " | ".join(f"{by[mm]:5.2f}" for mm in range(1, 13)))
        print("  " + " | ".join(f"{pap[mm-1]:5.2f}" for mm in range(1, 13)))


def part_c(R, months):
    print("\n" + "=" * 78)
    print("PART C — Rule B eligibility for long intervals (EW 10-1 spreads)")
    print("=" * 78
          )
    print(f"{'strategy':<18} {'rule':<5} {'spread':>7} {'t':>7} {'n/mo':>8} | "
          f"paper")
    for interval in ("y6_10", "y11_15", "y16_20"):
        for variant in ("all", "annual", "nonannual"):
            lags = LAG_SETS[interval][variant]
            psp = PAPER_LONG[(interval, variant)][0]
            for rule in ("A", "B"):
                s, n = spread_series(R, months, lags, rule=rule)
                print(f"{interval + ' ' + variant:<18} {rule:<5} "
                      f"{s.mean() * PCT:7.2f} {tstat(s):7.2f} {n:8,.0f} | "
                      f"{'' if psp is None else format(psp, '.2f')}")
        print()


def main():
    panel = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
    panel["month"] = pd.PeriodIndex(panel["month"], freq="M")
    R, months, permnos = wide_matrix(panel)
    print(f"panel: {len(panel):,} rows, {len(permnos):,} permnos, "
          f"{R.shape[0]} months")
    part_a()
    part_b(R, months)
    part_c(R, months)


if __name__ == "__main__":
    main()
