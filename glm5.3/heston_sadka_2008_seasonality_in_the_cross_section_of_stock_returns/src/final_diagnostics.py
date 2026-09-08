"""Iteration-10 diagnostics (no metric changes; report-only).

Task A — y1 January spread composition variants (Rule B base):
  (base)   current panel, all eligible stocks;
  (i)      exclude stocks with < 12 months of prior return history
           at the holding month (approximates Rule A completeness);
  (ii)     exclude bottom ME-tercile (mcap_lag1) stocks each month;
  (iii)    pre-delisting-merge returns (raw msf panel, no dlret
           combination, no inserted rows).
For each variant: Jan / Feb-Dec / full-sample EW 10-1 spread (percent)
for y1 All, Nonannual (and Annual to check the annual-lag cells).

Task B — T4 SE-construction readings:
  (1) SD over pair-level pi / sqrt(500)      (literal, current);
  (2) SD over LAG-level pi means / sqrt(500) (group members = lags);
  (3) SD over calendar-month-level pi means / sqrt(500).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))

from main import (LAG_SETS, N_BINS, DECIMALS_RET, HOLD_START, HOLD_END,
                  LAYOUT, _wide_matrix, _tstat, q_file, apply_universe_filter,
                  fetch_data_cached)
from utils.quantile import assign_quantiles
from utils.portfolio import bin_returns


# ---------------------------------------------------------------- Task A
def _spread_series_from_panel(panel: pd.DataFrame, lags: list,
                              min_prior: int | None = None,
                              drop_bottom_tercile: bool = False,
                              ) -> pd.Series:
    """EW 10-1 monthly spread series for one lag set, Rule B eligibility."""
    R, m_idx, months, permnos, p_idx = _wide_matrix(panel)
    nanmask = np.isnan(R)

    W = np.full_like(R, np.nan, dtype=np.float32)
    mc = panel[["permno", "month", "mcap_lag1"]].dropna(subset=["mcap_lag1"])
    mi = mc["month"].map(m_idx).to_numpy()
    pi_ = mc["permno"].map(p_idx).to_numpy()
    ok = ~np.isnan(mi) & ~np.isnan(pi_)
    W[mi[ok].astype(int), pi_[ok].astype(int)] = mc["mcap_lag1"].to_numpy()[ok]

    # prior non-missing return count per (month, stock) — cumulative
    if min_prior is not None:
        prior_cnt = np.cumsum(~nanmask, axis=0)   # inclusive of row t
    else:
        prior_cnt = None

    lags = np.asarray(lags, dtype=int)
    hold_rows = [i for i, m in enumerate(months) if HOLD_START <= m <= HOLD_END]
    parts = []
    for t in hold_rows:
        cols = t - lags
        if cols.min() < 0:
            continue
        sub = R[cols, :]
        avail = ~np.isnan(sub)
        elig = avail.any(axis=0) & ~nanmask[t, :]
        if min_prior is not None:
            # prior count strictly before t = prior_cnt[t-1] (inclusive cumsum)
            elig &= (prior_cnt[t - 1, :] >= min_prior) if t >= 1 else False
        if drop_bottom_tercile:
            w = W[t, :]
            elig &= np.isnan(w) | (w >= np.nanquantile(w[elig], 1.0 / 3.0))
        if not elig.any():
            continue
        idx = np.where(elig)[0]
        avg = np.nanmean(sub[:, idx].astype(np.float64), axis=0)
        parts.append(pd.DataFrame({
            "month": str(months[t]), "permno": permnos[idx], "sig": avg,
            "ret": R[t, idx].astype(np.float64),
            "mcap_lag1": W[t, idx].astype(np.float64)}))
    long = pd.concat(parts, ignore_index=True)
    long["decile"] = assign_quantiles(long, date_col="month", signal_col="sig",
                                      n_bins=N_BINS, warn_fallback=False)
    br = bin_returns(long, date_col="month", bin_col="decile",
                     ret_col="ret", mcap_col="mcap_lag1")
    piv = br.pivot(index="month", columns="decile", values="EW")
    s = (piv[N_BINS] - piv[1]).dropna()
    s.index = pd.PeriodIndex(pd.to_datetime(s.index), freq="M")
    return s


def _row(name, variant, s: pd.Series) -> dict:
    cm = s.index.month
    return {
        "panel": name, "variant": variant,
        "jan": s[cm == 1].mean() * DECIMALS_RET,
        "febdec": s[cm != 1].mean() * DECIMALS_RET,
        "full": s.mean() * DECIMALS_RET,
        "n_months": len(s),
    }


def task_a(panel: pd.DataFrame) -> pd.DataFrame:
    # (iii) pre-merge panel: raw msf, no delisting merge at all
    raw = q_file("universe_monthly.sql")
    raw = apply_universe_filter(raw, fetch_data_cached,
                                shrcd_filter=[10, 11], exchcd_filter=[1, 2])
    raw["month"] = pd.to_datetime(raw["date"]).dt.to_period("M")
    raw["ret"] = pd.to_numeric(raw["ret"], errors="coerce")
    raw["mcap"] = raw["prc"].abs() * raw["shrout"] * 1000.0
    raw.loc[raw["prc"].isna(), "mcap"] = np.nan
    pre = (raw[["permno", "month", "ret", "mcap", "hexcd", "hsiccd"]]
           .drop_duplicates(subset=["permno", "month"], keep="first")
           .sort_values(["permno", "month"]).reset_index(drop=True))
    pre["mcap_lag1"] = pre.groupby("permno")["mcap"].shift(1)
    print(f"[taskA-iii] pre-merge panel: {len(pre):,} rows "
          f"(merged panel: {len(panel):,})")

    rows = []
    configs = [
        ("base", panel, None, False),
        ("i_ge12prior", panel, 12, False),
        ("ii_ex_bottom_ME_tercile", panel, None, True),
        ("iii_premerge_returns", pre, None, False),
    ]
    y1 = LAG_SETS["y1"]
    for name, pnl, mp, terc in configs:
        for variant, lags in y1.items():
            s = _spread_series_from_panel(pnl, lags, min_prior=mp,
                                          drop_bottom_tercile=terc)
            rows.append(_row(name, variant, s))
            print(f"[taskA] {name:26s} {variant:10s} "
                  f"jan={rows[-1]['jan']:6.2f} febdec={rows[-1]['febdec']:5.2f} "
                  f"full={rows[-1]['full']:6.2f}")
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- Task B
T4_START = pd.Period("1963-01", freq="M")
T4_END = pd.Period("2002-12", freq="M")
SE_N = np.sqrt(500.0)


def task_b(panel: pd.DataFrame) -> pd.DataFrame:
    sub = panel[(panel["month"] >= T4_START) & (panel["month"] <= T4_END)]
    R, m_idx, months, permnos, _ = _wide_matrix(sub)
    Rf = R.astype(np.float64)
    nan = np.isnan(Rf)
    n_rows = Rf.shape[0]

    pi = []          # (k, t_index, value)
    for k in range(1, n_rows):
        A, B = Rf[:n_rows - k, :], Rf[k:, :]
        m = (~nan[:n_rows - k, :]) & (~nan[k:, :])
        n = m.sum(axis=1)
        valid = n >= 2
        if not valid.any():
            continue
        Av = np.where(m, A, 0.0); Bv = np.where(m, B, 0.0)
        mA = Av.sum(axis=1)[valid] / n[valid]
        mB = Bv.sum(axis=1)[valid] / n[valid]
        a = np.where(m[valid], A[valid] - mA[:, None], 0.0)
        b = np.where(m[valid], B[valid] - mB[:, None], 0.0)
        p = (a * b).sum(axis=1) / n[valid]
        pi.append((k, np.where(valid)[0], p))
        if k % 60 == 0:
            print(f"[taskB] k={k} done")

    lag_of_t = np.arange(n_rows)          # t index; k separate
    rows = []
    for g, pred in [("all", lambda k: True),
                    ("nonannual", lambda k: k % 12 != 0),
                    ("annual", lambda k: k % 12 == 0)]:
        vals, ks, ts = [], [], []
        for k, ti, p in pi:
            if pred(k):
                vals.append(p); ks.append(np.full(len(p), k))
                ts.append(ti)
        v = np.concatenate(vals); kv = np.concatenate(ks)
        tv = np.concatenate(ts)
        mean = v.mean() * 100.0
        # (1) pair-level
        t1 = mean / (v.std(ddof=0) / SE_N)
        # (2) lag-level means
        dfL = pd.DataFrame({"k": kv, "v": v})
        lag_means = dfL.groupby("k")["v"].mean().to_numpy()
        t2 = mean / (lag_means.std(ddof=0) / SE_N)
        # (3) calendar-month-level means (month of t)
        cal = months[tv].month if hasattr(months[0], "month") else \
            pd.PeriodIndex(months[tv]).month
        dfC = pd.DataFrame({"c": np.asarray(cal), "v": v})
        cal_means = dfC.groupby("c")["v"].mean().to_numpy()
        t3 = mean / (cal_means.std(ddof=0) / SE_N)
        rows.append(dict(group=g, mean=mean,
                         t1_pair=t1, t2_lagmean=t2, t3_calmonth=t3,
                         n_lags=len(lag_means), n_cal=len(cal_means)))
        print(f"[taskB] {g:10s} mean={mean:.4f} | t1(pair)={t1:8.2f} "
              f"t2(lagmean)={t2:7.2f} t3(calmonth)={t3:7.2f} "
              f"n_lags={len(lag_means)}")
    return pd.DataFrame(rows)


if __name__ == "__main__":
    panel = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
    panel["month"] = pd.PeriodIndex(panel["month"], freq="M")
    ta = task_a(panel)
    ta.to_csv(LAYOUT.result_path("y1_january_variants.csv"), index=False)
    tb = task_b(panel)
    tb.to_csv(LAYOUT.result_path("t4_se_readings.csv"), index=False)
    print("\n[taskA] table:\n", ta.round(2).to_string(index=False))
    print("\n[taskB] table:\n", tb.round(2).to_string(index=False))
