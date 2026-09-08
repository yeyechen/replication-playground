"""Table 5 — strategies within size groups (Heston & Sadka 2008, Table 5).

Size groups (paper L1335): at each month t, among PIT-universe firms with
non-missing market cap at the end of month t-1 (= beginning of t,
mcap_lag1): Small = smallest 30% (by count), Large = top 30%, Medium =
middle 40%. Breakpoints use ALL NYSE/AMEX firms (paper explicit, not
NYSE-only).

Within EACH size group, form the 15 Table 2 strategies (Rule B
eligibility, Assumption 5 REVISED) among group members with a month-t
return; equal-count EW deciles; report the 10-1 spread mean and simple
t over 1965-01..2002-12. Units percent/month.
"""
import json

import numpy as np
import pandas as pd

from main import (LAG_SETS, LAYOUT, HOLD_START, HOLD_END, N_BINS,
                  DECIMALS_RET, _wide_matrix, _tstat)
from utils.quantile import assign_quantiles
from utils.portfolio import bin_returns

SIZES = ("small", "medium", "large")
MONTH_ABBR = {1: "jan", 2: "feb", 3: "mar", 4: "apr", 5: "may", 6: "jun",
              7: "jul", 8: "aug", 9: "sep", 10: "oct", 11: "nov", 12: "dec"}


def _size_groups(w: np.ndarray) -> np.ndarray:
    """Map one month's mcap_lag1 row to {-1,0,1,2} (2=small,1=med,0=large,
    -1 = missing mcap). Count-based 30/40/30 split over non-missing mcaps."""
    g = np.full(w.shape, -1, dtype=np.int8)
    ok = np.isfinite(w)
    n = int(ok.sum())
    if n == 0:
        return g
    n30 = max(1, int(np.floor(0.30 * n)))
    order = np.argsort(np.where(ok, w, np.inf), kind="stable")
    g[order[:n30]] = 2                    # smallest 30%
    g[order[n30:n - n30]] = 1             # middle 40%
    g[order[n - n30:]] = 0                # top 30%
    g[~ok] = -1
    return g


def table5(panel: pd.DataFrame, metrics: dict) -> pd.DataFrame:
    R, m_idx, months, permnos, p_idx = _wide_matrix(panel)
    nanmask = np.isnan(R)

    W = np.full_like(R, np.nan, dtype=np.float32)
    mc = panel[["permno", "month", "mcap_lag1"]].dropna(subset=["mcap_lag1"])
    mi = mc["month"].map(m_idx).to_numpy()
    pi = mc["permno"].map(p_idx).to_numpy()
    okm = ~np.isnan(mi) & ~np.isnan(pi)
    W[mi[okm].astype(int), pi[okm].astype(int)] = \
        mc["mcap_lag1"].to_numpy()[okm]

    hold_rows = [i for i, m in enumerate(months) if HOLD_START <= m <= HOLD_END]

    # group membership per holding row
    grp = {t: _size_groups(W[t, :]) for t in hold_rows}
    diag = {s: float(np.mean([(grp[t] == k).sum() for t in hold_rows]))
            for k, s in zip((2, 1, 0), SIZES)}
    print("[t5] avg firms/month by size group: "
          + ", ".join(f"{s}={diag[s]:,.0f}" for s in SIZES))
    for s in SIZES:
        metrics[f"diag_t5_avg_{s}_per_month"] = {
            "value": round(diag[s], 1), "unit": "count"}

    rows = []
    for interval, variants in LAG_SETS.items():
        for variant, lags in variants.items():
            lags = np.asarray(lags, dtype=int)
            for k, size in zip((2, 1, 0), SIZES):
                parts = []
                for t in hold_rows:
                    cols = t - lags
                    if cols.min() < 0:
                        continue
                    sub = R[cols, :]
                    avail = ~np.isnan(sub)
                    ok_stocks = (avail.any(axis=0) & ~nanmask[t, :]
                                 & (grp[t] == k))
                    if not ok_stocks.any():
                        continue
                    avg = np.nanmean(sub[:, ok_stocks].astype(np.float64),
                                     axis=0)
                    idx = np.where(ok_stocks)[0]
                    parts.append(pd.DataFrame({
                        # month+size key so deciles form within (month, size)
                        "month": f"{months[t]}_{size}",
                        "permno": permnos[idx],
                        "sig": avg,
                        "ret": R[t, idx].astype(np.float64),
                        "mcap_lag1": np.full(len(idx), np.nan),
                    }))
                long = pd.concat(parts, ignore_index=True)
                long["decile"] = assign_quantiles(
                    long, date_col="month", signal_col="sig",
                    n_bins=N_BINS, warn_fallback=False)
                br = bin_returns(long, date_col="month", bin_col="decile",
                                 ret_col="ret")
                piv = br.pivot(index="month", columns="decile", values="EW")
                spread = (piv[N_BINS] - piv[1]).dropna()
                rows.append(dict(interval=interval, variant=variant,
                                 size=size,
                                 mean_pct=spread.mean() * DECIMALS_RET,
                                 t_stat=_tstat(spread),
                                 n_months=len(spread)))
            print(f"[t5] {interval} {variant}: "
                  + ", ".join(f"{r['size']}={r['mean_pct']:.2f}"
                              f"[{r['t_stat']:.2f}]"
                              for r in rows[-3:]))

    res = pd.DataFrame(rows)

    def put(name, value, unit):
        if value is not None and not (isinstance(value, float)
                                      and np.isnan(value)):
            metrics[name] = {"value": round(float(value), 4), "unit": unit}

    for _, r in res.iterrows():
        put(f"t5_{r['interval']}_{r['variant']}_{r['size']}",
            r["mean_pct"], "percent_per_month")
        put(f"t5_{r['interval']}_{r['variant']}_{r['size']}_t",
            r["t_stat"], "t_stat")
    return res, diag


def write_table5_md(res: pd.DataFrame, diag: dict) -> None:
    spec = json.loads(
        (LAYOUT.preparations_path("tables_to_replicate.json")).read_text())
    paper = {m["name"]: m for tb in spec["tables"] if tb["id"] == "T5"
             for m in tb["metrics"]}
    intervals = ["y1", "y2_5", "y6_10", "y11_15", "y16_20"]
    label = {"all": "All", "annual": "Annual", "nonannual": "Nonannual"}
    lines = [
        "# Table 5 — Strategy 10-1 spreads within size groups "
        "(percent/month), 1965-01 to 2002-12",
        "",
        "Size groups: smallest 30% / middle 40% / top 30% by market cap at "
        "the end of month t-1, breakpoints from ALL NYSE/AMEX firms, "
        "re-ranked monthly (L1335). EW deciles within each group (Rule B "
        "eligibility). Paper value and Match/FAIL status (hybrid "
        "tolerance: tol_pct / absolute_band) shown per cell.",
        "",
        "| Strategy | Small | Medium | Large |",
        "|---|---|---|---|",
    ]
    from evaluate import classify

    def fmt(r):
        if r is None:
            return "—"
        p = paper.get(f"t5_{r['interval']}_{r['variant']}_{r['size']}")
        pv = p.get("value") if p else None
        st = ("—" if pv is None else classify(
            float(r["mean_pct"]), pv, p.get("tolerance_pct", 0),
            p.get("absolute_band"), False))
        return (f"{r['mean_pct']:.2f} [{r['t_stat']:.2f}]"
                + (f" (paper {pv:.2f}, {st})" if pv is not None else ""))

    for interval in intervals:
        for variant in ("all", "annual", "nonannual"):
            cells = [res[(res["interval"] == interval)
                         & (res["variant"] == variant)
                         & (res["size"] == s)] for s in SIZES]
            lines.append(f"| {interval} {label[variant]} | "
                         + " | ".join(fmt(c.iloc[0] if len(c) else None)
                                      for c in cells) + " |")
    lines += ["",
              "## Diagnostics",
              "- avg firms/month: " + ", ".join(
                  f"{s}={diag[s]:,.0f}" for s in SIZES)
              + " (paper: small 485-1,019, median 787, L1335)"]
    (LAYOUT.result_path("table_5.md")).write_text("\n".join(lines) + "\n")
