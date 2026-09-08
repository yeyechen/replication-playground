"""Table 1 — Fama-MacBeth return-response regressions (Heston & Sadka 2008).

Panel A: monthly simple regressions r_it = a + gamma_k r_i,t-k + e for
  k in LAGS_A (1..12, 24, 36, ..., 240), holding months 1965-01..2002-12.
  Eligible stocks: non-missing ret at t and t-k (Assumption 7).
  gamma_k computed as cov/var on the valid pair set (algebraically the
  OLS slope); time-averaged; NW(12) t-stat.

Panel B: monthly multiple regressions on three lag specifications
  (spec1: 1..12,24,36; spec2: ...120; spec3: ...240), listwise-available
  stocks only (Assumption 7). Rank-deficient months are solved with the
  min-norm least-squares solution (np.linalg.lstsq) and counted — never
  silently dropped.

Estimates reported in percent (x100; Assumption 12 / paper L180).
Formation data reaches back to 1945-01 (t-240 for t=1965-01): the wide
matrix spans the full panel.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from main import DECIMALS_RET, HOLD_END, HOLD_START, LAYOUT, _wide_matrix

NW_LAGS = 12
LAGS_A = list(range(1, 13)) + list(range(24, 241, 12))          # 31 lags
SPECS = {
    "spec1": list(range(1, 13)) + [24, 36],                     # 14 lags
    "spec2": list(range(1, 13)) + list(range(24, 121, 12)),     # 21 lags
    "spec3": LAGS_A,                                            # 31 lags
}


def _nw_tstat(x: np.ndarray, lags: int = NW_LAGS) -> float:
    """t-stat of mean(x) with Newey-West(lags) HAC standard error."""
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 2:
        return np.nan
    d = x - x.mean()
    s = np.dot(d, d) / n
    for l in range(1, min(lags, n - 1) + 1):
        w = 1.0 - l / (lags + 1.0)
        s += 2.0 * w * np.dot(d[l:], d[:-l]) / n
    se = np.sqrt(max(s, 0.0) / n)
    return float(x.mean() / se) if se > 0 else np.nan


def _slope(y: np.ndarray, x: np.ndarray) -> tuple:
    """OLS slope cov(x,y)/var(x) over jointly-finite pairs; (slope, n)."""
    m = np.isfinite(y) & np.isfinite(x)
    n = int(m.sum())
    if n < 3:
        return np.nan, n
    yc = y[m] - y[m].mean()
    xc = x[m] - x[m].mean()
    vx = np.dot(xc, xc)
    if vx == 0:
        return np.nan, n
    return float(np.dot(xc, yc) / vx), n


def table1(panel: pd.DataFrame, metrics: dict) -> dict:
    """Compute Panel A and Panel B; write T1 cells into metrics."""
    R, m_idx, months, permnos, _ = _wide_matrix(panel)
    R = R.astype(np.float64)
    hold_rows = np.array([i for i, m in enumerate(months)
                          if HOLD_START <= m <= HOLD_END])
    assert len(hold_rows) == 456, f"expected 456 holding months, got {len(hold_rows)}"

    out = {"panA": {}, "panB": {}, "avg_n": {}}

    # --- Panel A: simple regressions, per (t, lag) slope = cov/var ---
    gamma = {k: np.full(len(hold_rows), np.nan) for k in LAGS_A}
    ntot = {k: 0 for k in LAGS_A}
    for j, t in enumerate(hold_rows):
        y = R[t, :]
        for k in LAGS_A:
            g, n = _slope(y, R[t - k, :])
            gamma[k][j] = g
            ntot[k] += n
    for k in LAGS_A:
        g = gamma[k]
        out["panA"][k] = {
            "est_pct": float(np.nanmean(g)) * DECIMALS_RET,
            "t_nw": _nw_tstat(g),
            "avg_n": ntot[k] / len(hold_rows),
            "n_months": int(np.isfinite(g).sum()),
        }
        metrics[f"t1_pana_lag{k}"] = {
            "value": round(out["panA"][k]["est_pct"], 4),
            "unit": "percent_per_month"}
        metrics[f"t1_pana_lag{k}_t"] = {
            "value": round(out["panA"][k]["t_nw"], 4), "unit": "t_stat"}
    for k in (1, 12, 240):
        out["avg_n"][f"panA_lag{k}"] = out["panA"][k]["avg_n"]

    # --- Panel B: multiple regressions, listwise-available subset ---
    for spec, lags in SPECS.items():
        lags = np.asarray(lags, dtype=int)
        coef = np.full((len(hold_rows), len(lags) + 1), np.nan)  # [const, k...]
        n_used, rank_def = [], 0
        for j, t in enumerate(hold_rows):
            cols = np.concatenate(([t], t - lags))
            m = np.isfinite(R[cols, :]).all(axis=0)
            idx = np.where(m)[0]
            if len(idx) < len(lags) + 5:
                continue
            X = np.column_stack([np.ones(len(idx))]
                                + [R[t - k, idx] for k in lags])
            yv = R[t, idx]
            n_used.append(len(idx))
            try:
                if np.linalg.matrix_rank(X) < X.shape[1]:
                    rank_def += 1     # min-norm solution via lstsq (gelsd)
                beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
                coef[j, :] = beta
            except np.linalg.LinAlgError:
                beta = np.linalg.pinv(X) @ yv
                coef[j, :] = beta
                rank_def += 1
        out["panB"][spec] = {
            "rank_deficient_months": rank_def,
            "avg_n": float(np.mean(n_used)),
        }
        for i, k in enumerate(lags):
            c = coef[:, i + 1]
            est = float(np.nanmean(c))
            t = _nw_tstat(c)
            out["panB"][spec][int(k)] = {"est_pct": est * DECIMALS_RET,
                                         "t_nw": t}
            metrics[f"t1_{spec}_lag{int(k)}"] = {
                "value": round(est * DECIMALS_RET, 4),
                "unit": "percent_per_month"}
            metrics[f"t1_{spec}_lag{int(k)}_t"] = {
                "value": round(t, 4), "unit": "t_stat"}
        if spec == "spec3":
            out["avg_n"]["panB_spec3"] = out["panB"][spec]["avg_n"]
    return out


def write_table1_md(res: dict) -> None:
    spec = json.loads(
        (LAYOUT.preparations_path("tables_to_replicate.json")).read_text())
    paper = {m["name"]: m.get("value")
             for t in spec["tables"] if t["id"] == "T1"
             for m in t["metrics"]}

    lines = [
        "# Table 1 — Monthly return-response regressions, 1965-01..2002-12",
        "",
        "Cross-sectional OLS of r_it on lagged returns r_i,t-k; gamma_k "
        "averaged over 456 months; t-stats Newey-West(12). Estimates in "
        "percent (paper L180). Panel B includes only stocks with returns "
        "at t and at all lags of the specification (Assumption 7).",
        "",
        "## Panel A: simple regressions",
        "",
        "| Lag | Estimate [t] (ours) | Paper | | Lag | Estimate [t] (ours) "
        "| Paper |",
        "|---|---|---|---|---|---|---|",
    ]
    half = (len(LAGS_A) + 1) // 2
    for a in range(half):
        k1 = LAGS_A[a]
        k2 = LAGS_A[a + half] if a + half < len(LAGS_A) else None
        row = [str(k1)]
        row.append(f"{res['panA'][k1]['est_pct']:.2f} "
                   f"[{res['panA'][k1]['t_nw']:.2f}]")
        row.append(f"{paper.get('t1_pana_lag%d' % k1, float('nan')):.2f} "
                   f"[{paper.get('t1_pana_lag%d_t' % k1, float('nan')):.2f}]")
        if k2 is not None:
            row += [str(k2),
                    f"{res['panA'][k2]['est_pct']:.2f} "
                    f"[{res['panA'][k2]['t_nw']:.2f}]",
                    f"{paper.get('t1_pana_lag%d' % k2, float('nan')):.2f} "
                    f"[{paper.get('t1_pana_lag%d_t' % k2, float('nan')):.2f}]"]
        else:
            row += ["", "", ""]
        lines.append("| " + " | ".join(row) + " |")

    lines += ["", "## Panel B: multiple regressions", ""]
    for spec, lags in SPECS.items():
        lines += [f"### {spec} ({len(lags)} lags: "
                  f"{lags[0]}..{lags[-1]})", "",
                  "| Lag | Estimate [t] (ours) | Paper |",
                  "|---|---|---|"]
        for k in lags:
            c = res["panB"][spec][int(k)]
            p = paper.get(f"t1_{spec}_lag{k}")
            pt = paper.get(f"t1_{spec}_lag{k}_t")
            ps = "—" if p is None else f"{p:.2f} [{pt:.2f}]"
            lines.append(f"| {k} | {c['est_pct']:.2f} [{c['t_nw']:.2f}] "
                         f"| {ps} |")
        lines += [f"\navg cross-section: {res['panB'][spec]['avg_n']:,.0f} "
                  f"stocks/month; rank-deficient months (min-norm lstsq): "
                  f"{res['panB'][spec]['rank_deficient_months']}"]

    lines += ["", "## Avg Panel A cross-section size (stocks/month)",
              f"- lag 1: {res['avg_n']['panA_lag1']:,.0f}; "
              f"lag 12: {res['avg_n']['panA_lag12']:,.0f}; "
              f"lag 240: {res['avg_n']['panA_lag240']:,.0f}"]
    (LAYOUT.result_path("table_1.md")).write_text("\n".join(lines) + "\n")
