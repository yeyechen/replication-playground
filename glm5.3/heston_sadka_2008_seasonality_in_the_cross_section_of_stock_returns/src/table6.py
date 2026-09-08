"""Table 6 — industry decomposition of the 15 strategies (HS2008, T6).

Industry: hsiccd (historical SIC) -> 20 Moskowitz-Grinblatt (1999)
industries, reconstructed as a 2-digit-SIC partition under the priority
order fixed in the task spec (Assumption 8: MG 1999 Table 1's industry
list reconstructed from a priority-ordered 2-digit mapping; leftover
codes -> 'other').

Monthly industry return = EW mean of member returns (universe stocks with
ret that month). Intra-industry component of stock i in month t =
r_it - r_industry(i),t; inter-industry component = r_industry(i),t.

For each of the 15 Table 2 strategies (Rule B deciles): spread_intra =
mean(intra | D10) - mean(intra | D1) per month; likewise inter. Report
mean + simple t over the 456 holding months (percent/month).
"""
import json

import numpy as np
import pandas as pd

from main import (LAG_SETS, LAYOUT, HOLD_START, HOLD_END, N_BINS,
                  DECIMALS_RET, _wide_matrix, _tstat)
from utils.quantile import assign_quantiles

# priority-ordered partition of 2-digit SIC codes (first match wins)
IND_PRIORITY = [
    ("petroleum", (13, 29)),
    ("finance_real_estate", (61, 62, 63, 64, 65, 66, 67)),
    ("consumer_durables", (25, 30, 36, 37, 50, 55, 57)),
    ("basic_industry", (8, 10, 12, 14, 24, 26, 28, 33)),
    ("food_tobacco", (1, 20, 21, 54)),
    ("construction", (15, 16, 17, 32, 52)),
    ("capital_goods", (34, 35, 38)),
    ("transportation", (40, 41, 42, 44, 45, 46, 47)),
    ("unregulated_utilities", (48,)),
    ("textiles_trade", (22, 23, 31, 51, 53, 56, 59)),
    ("services", (72, 73, 75, 80, 82, 87, 89)),
    ("leisure", (27, 58, 70, 78, 79)),
    ("regulated_utilities", (49,)),
]
_OTHER = "other"

_SIC2IND = {}
for _i, (_name, _codes) in enumerate(IND_PRIORITY):
    for _c in _codes:
        _SIC2IND.setdefault(_c, _i)          # first match wins
IND_NAMES = [n for n, _ in IND_PRIORITY] + [_OTHER]


def industry_of(hsiccd) -> int:
    """2-digit SIC -> industry index (len(IND_PRIORITY) = 'other')."""
    n_other = len(IND_PRIORITY)
    if pd.isna(hsiccd):
        return n_other
    s2 = int(hsiccd) // 100
    if s2 < 0 or s2 > 99:
        return n_other
    return _SIC2IND.get(s2, n_other)


def table6(panel: pd.DataFrame, metrics: dict) -> pd.DataFrame:
    R, m_idx, months, permnos, p_idx = _wide_matrix(panel)
    nanmask = np.isnan(R)
    n_ind = len(IND_NAMES)

    # industry id per (month, permno) row of the wide matrix
    IND = np.full(R.shape, -1, dtype=np.int16)
    hs = panel[["permno", "month", "hsiccd"]]
    hs["ind"] = hs["hsiccd"].map(industry_of)
    mi = hs["month"].map(m_idx).to_numpy()
    pi = hs["permno"].map(p_idx).to_numpy()
    ok = ~np.isnan(mi) & ~np.isnan(pi)
    IND[mi[ok].astype(int), pi[ok].astype(int)] = hs["ind"].to_numpy()[ok]

    # 'other' share among stock-months (all panel rows)
    other_share = float((IND == n_ind - 1).mean())
    n_groups_observed = int(len(set(np.unique(IND)) - {-1}))
    print(f"[t6] industry groups observed: {n_groups_observed} "
          f"of {n_ind}; stock-month share in 'other': {other_share:.2%}")
    metrics["diag_t6_n_industry_groups"] = {"value": n_groups_observed,
                                            "unit": "count"}
    metrics["diag_t6_other_share"] = {"value": round(other_share, 4),
                                      "unit": "share"}

    hold_rows = [i for i, m in enumerate(months) if HOLD_START <= m <= HOLD_END]

    # per holding month: intra / inter component matrices (NaN where ret NaN)
    INTRA = np.full_like(R, np.nan, dtype=np.float32)
    INTER = np.full_like(R, np.nan, dtype=np.float32)
    for t in hold_rows:
        r = R[t, :]
        valid = ~np.isnan(r)
        if not valid.any():
            continue
        g = IND[t, valid].astype(np.int64)
        g = np.where(g < 0, n_ind - 1, g)     # unknown industry -> other
        s = np.bincount(g, weights=r[valid].astype(np.float64),
                        minlength=n_ind)
        c = np.bincount(g, minlength=n_ind)
        ind_ret = s / np.maximum(c, 1)
        INTRA[t, valid] = r[valid] - ind_ret[g].astype(np.float32)
        INTER[t, valid] = ind_ret[g].astype(np.float32)

    rows = []
    for interval, variants in LAG_SETS.items():
        for variant, lags in variants.items():
            lags = np.asarray(lags, dtype=int)
            parts = []
            for t in hold_rows:
                cols = t - lags
                if cols.min() < 0:
                    continue
                sub = R[cols, :]
                avail = ~np.isnan(sub)
                ok_stocks = avail.any(axis=0) & ~nanmask[t, :]
                if not ok_stocks.any():
                    continue
                avg = np.nanmean(sub[:, ok_stocks].astype(np.float64),
                                 axis=0)
                idx = np.where(ok_stocks)[0]
                parts.append(pd.DataFrame({
                    "month": str(months[t]),
                    "permno": permnos[idx],
                    "sig": avg,
                    "intra": INTRA[t, idx].astype(np.float64),
                    "inter": INTER[t, idx].astype(np.float64),
                }))
            long = pd.concat(parts, ignore_index=True)
            long["decile"] = assign_quantiles(long, date_col="month",
                                              signal_col="sig",
                                              n_bins=N_BINS,
                                              warn_fallback=False)
            for comp in ("intra", "inter"):
                piv = long.pivot_table(index="month", columns="decile",
                                       values=comp, aggfunc="mean")
                spread = (piv[N_BINS] - piv[1]).dropna()
                rows.append(dict(interval=interval, variant=variant,
                                 comp=comp,
                                 mean_pct=spread.mean() * DECIMALS_RET,
                                 t_stat=_tstat(spread),
                                 n_months=len(spread)))
            r_in = next(r for r in rows if r["interval"] == interval
                        and r["variant"] == variant and r["comp"] == "intra")
            r_it = next(r for r in rows if r["interval"] == interval
                        and r["variant"] == variant and r["comp"] == "inter")
            print(f"[t6] {interval} {variant}: intra "
                  f"{r_in['mean_pct']:.2f} [{r_in['t_stat']:.2f}] inter "
                  f"{r_it['mean_pct']:.2f} [{r_it['t_stat']:.2f}]")

    res = pd.DataFrame(rows)

    def put(name, value, unit):
        if value is not None and not (isinstance(value, float)
                                      and np.isnan(value)):
            metrics[name] = {"value": round(float(value), 4), "unit": unit}

    for _, r in res.iterrows():
        put(f"t6_{r['interval']}_{r['variant']}_{r['comp']}",
            r["mean_pct"], "percent_per_month")
        put(f"t6_{r['interval']}_{r['variant']}_{r['comp']}_t",
            r["t_stat"], "t_stat")
    return res


def write_table6_md(res: pd.DataFrame) -> None:
    spec = json.loads(
        (LAYOUT.preparations_path("tables_to_replicate.json")).read_text())
    paper = {m["name"]: m for tb in spec["tables"] if tb["id"] == "T6"
             for m in tb["metrics"]}
    from evaluate import classify
    intervals = ["y1", "y2_5", "y6_10", "y11_15", "y16_20"]
    label = {"all": "All", "annual": "Annual", "nonannual": "Nonannual"}
    lines = [
        "# Table 6 — Industry decomposition of strategy 10-1 spreads "
        "(percent/month), 1965-01 to 2002-12",
        "",
        "Intra-industry component: mean(r - r_industry | D10) - "
        "mean(r - r_industry | D1). Inter-industry component: "
        "mean(r_industry | D10) - mean(r_industry | D1). Industries: "
        "Moskowitz-Grinblatt (1999) 20-industry reconstruction from hsiccd "
        "2-digit codes (Assumption 8); Rule B deciles as in Table 2.",
        "",
        "| Strategy | Intra | paper | Inter | paper |",
        "|---|---|---|---|---|",
    ]

    def cell(r, comp):
        name = f"t6_{r['interval']}_{r['variant']}_{comp}"
        p = paper.get(name)
        pv = p.get("value") if p else None
        st = ("—" if pv is None else classify(
            float(r["mean_pct"]), pv, p.get("tolerance_pct", 0),
            p.get("absolute_band"), p.get("insignificant", False)))
        pt = paper.get(name + "_t", {}).get("value")
        return (f"{r['mean_pct']:.2f} [{r['t_stat']:.2f}]"
                + (f" vs {pv:.2f} [{pt:.2f}] ({st})" if pv is not None
                   else ""))

    for interval in intervals:
        for variant in ("all", "annual", "nonannual"):
            ci = res[(res["interval"] == interval)
                     & (res["variant"] == variant)
                     & (res["comp"] == "intra")]
            ce = res[(res["interval"] == interval)
                     & (res["variant"] == variant)
                     & (res["comp"] == "inter")]
            lines.append(
                f"| {interval} {label[variant]} | "
                + (cell(ci.iloc[0], "intra") if len(ci) else "—") + " | "
                + (cell(ce.iloc[0], "inter") if len(ce) else "—") + " |")
    lines += [
        "",
        "## Note on paper text vs table (L2386)",
        "The prose says the years 6-10 annual strategy's 'industry component "
        "is 12 basis points, but the inter-industry component is 58'. "
        "Against the table values (L1581-1595) the intra component is 0.56 "
        "(56bp) and the inter component is 0.12 (12bp). The text's '12 "
        "basis points' labeled 'industry component' equals the table's "
        "INTER cell, and its 'inter-industry component is 58' is "
        "approximately the table's INTRA cell (0.56 = 56bp; likely an OCR/"
        "rounding artifact). Conclusion: the prose SWAPS the two components "
        "relative to the table. Our y6_10 annual: see table above.",
    ]
    (LAYOUT.result_path("table_6.md")).write_text("\n".join(lines) + "\n")
