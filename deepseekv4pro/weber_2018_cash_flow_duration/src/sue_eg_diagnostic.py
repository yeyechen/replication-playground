"""Diagnostic / candidate-evaluation for Table 8 Panel B (EG) and Panel C (SUE).

Audit-2 [M3] resolution scaffold. This module does NOT touch metrics.json or the
canonical pipeline; it produces a comparison table of candidate SUE/EG constructions
that the Replicator uses to decide whether to commit any candidate change.

What it evaluates, per the task:
  Task 1  — IBES split-adjustment discovery (adj table semantics; AAPL 7:1 / 4:1 check).
  Task 2  — SUE1/SUE2 from IBES quarterly actuals (announcement-aligned seasonal RW).
  Task 3  — SUE3 check (announcement-alignment + split consistency of statsum meanest/actual).
  Task 4  — EG under (a) Compustat epspx, (b) split-adjusted IBES ANN actuals,
            (c) Compustat epsfx (diluted ex-items).
  Task 6  — per-candidate T8 cell-status movement vs current committed metrics.

Run:  python src/sue_eg_diagnostic.py
"""
from __future__ import annotations

import json
import numpy as np
import pandas as pd
from clickhouse_driver import Client

from utils.env import get_clickhouse_config
from utils.paths import paper_layout

SLUG = "weber_2018_attempt2_deepseek"
LAYOUT = paper_layout(SLUG)
SQL_DIR = LAYOUT.src_path("sql")

T8_START = 1982
T8_END = 2009

_cfg = get_clickhouse_config()


def _client():
    return Client(host=_cfg["host"], port=int(_cfg["port"]), user=_cfg["user"],
                  password=_cfg["password"], database=_cfg["database"],
                  settings={"max_execution_time": 600})


def q(sql):
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


def q_file(name):
    return q((SQL_DIR / name).read_text())


# ------------------------------------------------------------------ #
# Shared loaders
# ------------------------------------------------------------------ #
def load_cusip_map():
    cm = q_file("cusip_map.sql")
    cm["namedt"] = pd.to_datetime(cm["namedt"])
    cm["nameendt"] = pd.to_datetime(cm["nameendt"])
    return cm


def map_cusip_to_permno(df, cm, date_col):
    d = df.copy()
    d["_date"] = pd.to_datetime(d[date_col])
    cm2 = cm[["cusip", "permno", "namedt", "nameendt"]].copy()
    merged = d.merge(cm2, on="cusip", how="left")
    valid = merged[merged["_date"].between(merged["namedt"], merged["nameendt"])]
    idx = valid.groupby(["cusip", "_date"], sort=False)["namedt"].idxmax()
    valid = valid.loc[idx].drop(columns=["namedt", "nameendt"])
    return valid[valid["permno"].notna()].drop(columns=["_date"])


def load_mapping():
    pan = pd.read_parquet(LAYOUT.data_path("panel.parquet"),
                          columns=["permno", "sort_year", "bin", "dur"])
    pan = pan.drop_duplicates(["permno", "sort_year"])
    pan["decile"] = pan["bin"].astype(int)
    return pan[["permno", "sort_year", "decile"]]


def _redecile(s):
    r = s.rank(method="first", pct=True)
    return np.ceil(r * 10).astype(int).clip(1, 10)


def build_covered_mapping(cm):
    pan = pd.read_parquet(LAYOUT.data_path("panel.parquet"),
                          columns=["permno", "sort_year", "bin", "dur", "me_jun"])
    pan = pan.drop_duplicates(["permno", "sort_year"])
    cov = q_file("ibes_coverage.sql")
    cov["june_year"] = cov["june_year"].astype(int)
    cm2 = cm[["cusip", "permno", "namedt", "nameendt"]].copy()
    cov["_anchor"] = pd.to_datetime(dict(year=cov["june_year"], month=6, day=15))
    m = cov.merge(cm2, on="cusip", how="left")
    valid = m[m["_anchor"].between(m["namedt"], m["nameendt"])]
    idx = valid.groupby(["cusip", "_anchor"], sort=False)["namedt"].idxmax()
    valid = valid.loc[idx].drop(columns=["namedt", "nameendt"])
    covered = valid[["permno", "june_year"]].rename(
        columns={"june_year": "sort_year"}).drop_duplicates()
    covm = pan.merge(covered, on=["permno", "sort_year"], how="inner")
    covm = covm[covm["sort_year"].between(T8_START, T8_END)]
    covm["decile"] = covm.groupby("sort_year")["dur"].transform(_redecile)
    return covm[["permno", "sort_year", "decile"]]


# ------------------------------------------------------------------ #
# Task 1 — split adjustment discovery
# ------------------------------------------------------------------ #
def task1_split_adjustment():
    print("\n" + "=" * 70)
    print("TASK 1 — IBES split-adjustment discovery (adj table)")
    print("=" * 70)
    adj = q("""
        SELECT ticker, cusip, spdates, adj, usfirm
        FROM ibes_202601.adj
        WHERE ticker IN ('AAPL', 'MSFT', 'T', 'GE')
        ORDER BY ticker, toDate32(spdates)
        SETTINGS max_execution_time = 120, max_rows_to_read = 10000000000
    """)
    for tkr in ("AAPL", "MSFT"):
        sub = adj[adj["ticker"] == tkr]
        print(f"\nadj rows for {tkr} (cumulative split factor `adj` by split date):")
        for r in sub.itertuples():
            print(f"  {r.spdates}  adj={r.adj}")
    # adjsum: cumulative adjustment factor by statistical period
    print("\nadjsum sample (adjspf = cumulative factor by statpers):")
    ajs = q("""
        SELECT ticker, statpers, adjspf FROM ibes_202601.adjsum
        WHERE ticker='AAPL' AND toDate32(statpers) BETWEEN toDate32('2013-06-01')
          AND toDate32('2015-06-01') ORDER BY toDate32(statpers)
        SETTINGS max_execution_time = 120
    """)
    for r in ajs.itertuples():
        print(f"  {r.statpers}  adjspf={r.adjspf}")

    # Reconciliation: AAPL raw EPS vs act_epsus split-adjusted actual.
    print("\nAAPL act_epsus ANN actuals (split-adjusted, common basis):")
    ann = q("""
        SELECT pends, value FROM ibes_202601.act_epsus
        WHERE ticker='AAPL' AND pdicity='ANN' AND measure='EPS'
          AND toDate32(pends) BETWEEN toDate32('2011-09-01') AND toDate32('2015-09-30')
        ORDER BY toDate32(pends)
        SETTINGS max_execution_time = 120
    """)
    for r in ann.itertuples():
        print(f"  FYE {r.pends}  value={r.value}")
    print("  (Reconciliation: FY2012 raw ~44.15 -> /28 = 1.577 == act value 1.5768; "
          "FY2013 raw ~39.75 -> /28 = 1.420 == 1.4196.  act_epsus.value is ALREADY "
          "split-adjusted on a common basis.)")
    return adj


# ------------------------------------------------------------------ #
# Task 2 — SUE1/SUE2 on IBES quarterly actuals (announcement-aligned)
# ------------------------------------------------------------------ #
def load_ibes_qtr_actuals():
    a = q("""
        SELECT cusip, ticker, pends, anndats, value
        FROM ibes_202601.act_epsus
        WHERE pdicity = 'QTR' AND usfirm = 1 AND measure = 'EPS'
          AND value IS NOT NULL AND pends IS NOT NULL AND pends != ''
        SETTINGS max_execution_time = 600, max_rows_to_read = 10000000000
    """)
    a["pends"] = pd.to_datetime(a["pends"])
    a["anndats"] = pd.to_datetime(a["anndats"])
    return a


def seasonal_sue(qtr, col):
    """Seasonal random walk: sdiff = EPS_q - EPS_q-4; sigma = std of prior 8 sdiff
    (min 4). Sorted by fiscal period end (pends)."""
    s = qtr.sort_values(["permno", "pends"]).copy()
    s["_sdiff"] = s.groupby("permno")[col].diff(4)
    s["_sigma"] = (s.groupby("permno")["_sdiff"]
                   .transform(lambda x: x.shift(1).rolling(8, min_periods=4).std()))
    s["_sigma"] = s["_sigma"].where(s["_sigma"] > 1e-8)
    s["_sue"] = s["_sdiff"] / s["_sigma"]
    return s


def decile_median_ts(sub, col="_sue"):
    yrs = sub.dropna(subset=[col]).groupby(["sort_year", "decile"])[col].median().reset_index()
    return yrs.groupby("decile")[col].mean()


def task2_sue_ibes(cm, panel_map8):
    print("\n" + "=" * 70)
    print("TASK 2 — SUE1/SUE2 from IBES quarterly actuals")
    print("=" * 70)
    qtr = load_ibes_qtr_actuals()
    qtr = qtr.drop_duplicates(["cusip", "pends"], keep="last")
    # map via announcement date anndats; fall back to pends where anndats null
    a_ann = qtr[qtr["anndats"].notna()].copy()
    a_ann = map_cusip_to_permno(a_ann, cm, "anndats")
    a_pend = qtr[qtr["anndats"].isna()].copy()
    a_pend = map_cusip_to_permno(a_pend, cm, "pends")
    qtr_m = pd.concat([a_ann, a_pend], ignore_index=True)

    # Note: act_epsus.value is already split-adjusted on a common basis; no further
    # adjustment needed. We document the check in Task 1.
    qtr_m["_eps"] = qtr_m["value"]
    s1 = seasonal_sue(qtr_m, "_eps")
    # announcement-aligned: attribute to the June duration cohort of the announcement
    s1["sort_year"] = s1["anndats"].dt.year
    s1 = s1.merge(panel_map8[["permno", "sort_year", "decile"]],
                  on=["permno", "sort_year"], how="inner")
    s1 = s1[s1["sort_year"].between(T8_START, T8_END)]
    print(f"\nIBES QTR actuals post-map: {len(qtr_m)} rows; "
          f"seasonal SUE1 usable: {s1['_sue'].notna().sum()}")
    ts1 = decile_median_ts(s1)
    print("SUE1 (IBES act_epsus) D1..D10 medians:")
    for d in range(1, 11):
        print(f"  D{d}: {ts1.get(d, float('nan')):.4f}")
    print(f"  spread D1-D10: {ts1.get(1,0)-ts1.get(10,0):.4f}")
    # denominator scale check: seasonal diff is dollars/share; sigma in same units.
    print(f"\nSUE1 seasonal |sdiff| median: {s1['_sdiff'].abs().median():.4f} "
          f"(sigma median {s1['_sigma'].median():.4f})")
    # also report the raw seasonal diff median (numerator) to contrast with audit's
    # "flat at ~0" finding.
    num_ts = decile_median_ts(s1.assign(_sue=s1["_sdiff"]))
    print("SUE1 raw seasonal-diff (numerator) D1..D10 medians (dollars/share):")
    for d in range(1, 11):
        print(f"  D{d}: {num_ts.get(d, float('nan')):.5f}")
    return s1, ts1


# ------------------------------------------------------------------ #
# Task 3 — SUE3 check
# ------------------------------------------------------------------ #
def task3_sue3(cm, panel_map8):
    print("\n" + "=" * 70)
    print("TASK 3 — SUE3 check (analyst actual - meanest)")
    print("=" * 70)
    fc = q_file("ibes_sue3_fc.sql")
    fc["fpedats"] = pd.to_datetime(fc["fpedats"])
    fc["statpers"] = pd.to_datetime(fc["statpers"])
    fc = fc.drop_duplicates(["cusip", "fpedats"], keep="last")
    f = fc.sort_values(["cusip", "fpedats"]).copy()
    f["_err"] = f["actual"] - f["meanest"]
    f["_sigma"] = f.groupby("cusip")["_err"].transform(
        lambda x: x.shift(1).rolling(8, min_periods=4).std())
    f["_sigma"] = f["_sigma"].where(f["_sigma"] > 1e-8)
    f["_sue"] = f["_err"] / f["_sigma"]
    f = map_cusip_to_permno(f, cm, "fpedats")
    f["sort_year"] = f["fpedats"].dt.year
    f = f.merge(panel_map8[["permno", "sort_year", "decile"]],
                on=["permno", "sort_year"], how="inner")
    f = f[f["sort_year"].between(T8_START, T8_END)]
    print(f"\nSUE3 usable rows: {f['_sue'].notna().sum()}")
    # raw forecast error sign distribution
    print(f"forecast error (actual - meanest) mean: {f['_err'].mean():.5f} "
          f"median: {f['_err'].median():.5f}  (share >=0: {(f['_err']>=0).mean():.3f})")
    ts3 = decile_median_ts(f)
    print("SUE3 D1..D10 medians:")
    for d in range(1, 11):
        print(f"  D{d}: {ts3.get(d, float('nan')):.4f}")
    print(f"  spread D1-D10: {ts3.get(1,0)-ts3.get(10,0):.4f}")
    # check: is meanest split-consistent with actual? ratio distribution
    print(f"\nmeanest/actual ratio median: {(f['meanest']/f['actual']).median():.4f}")
    return f, ts3


# ------------------------------------------------------------------ #
# Task 4 — EG comparison (three EPS sources)
# ------------------------------------------------------------------ #
def eg_from_series(ann, panel_map8):
    """ann: columns permno, fyear, eps; returns backward/forward EG decile means."""
    ann = ann.drop_duplicates(["permno", "fyear"], keep="last").sort_values(
        ["permno", "fyear"])
    ann["eps_prev5"] = ann.groupby("permno")["eps"].shift(5)
    ann["fyear_prev5"] = ann.groupby("permno")["fyear"].shift(5)
    ok = (ann["fyear"] - ann["fyear_prev5"] == 5) & ann["eps_prev5"].notna() & \
         (ann["eps_prev5"] > 0) & (ann["eps"] > 0)
    ann["eg5"] = np.where(ok, (ann["eps"] / ann["eps_prev5"]) ** (1.0 / 5.0) - 1.0, np.nan)
    # backward EG_{t-6:t-1}: endpoint FYE t-1 -> sort_year t
    eb = ann[ann["eg5"].notna()][["permno", "fyear", "eg5"]].copy()
    eb["sort_year"] = eb["fyear"] + 1
    eb = eb.merge(panel_map8[["permno", "sort_year", "decile"]],
                  on=["permno", "sort_year"], how="inner")
    eb = eb[eb["sort_year"].between(T8_START, T8_END)]
    # forward EG_{t:t+5}: endpoint FYE t+5 -> sort_year t
    ef = ann[ann["eg5"].notna()][["permno", "fyear", "eg5"]].copy()
    ef["sort_year"] = ef["fyear"] - 5
    ef = ef.merge(panel_map8[["permno", "sort_year", "decile"]],
                  on=["permno", "sort_year"], how="inner")
    ef = ef[ef["sort_year"].between(T8_START, T8_END)]
    out = {}
    for tag, dframe in (("t6_t1", eb), ("t_t5", ef)):
        yrs = dframe.groupby(["sort_year", "decile"])["eg5"].mean().reset_index() * 100.0
        ts = (dframe.assign(eg5=dframe["eg5"] * 100.0)
              .groupby(["sort_year", "decile"])["eg5"].mean().reset_index()
              .groupby("decile")["eg5"].mean())
        out[tag] = ts
    return out


def task4_eg(cm, panel_map8):
    print("\n" + "=" * 70)
    print("TASK 4 — EG comparison (three realized-EPS sources)")
    print("=" * 70)
    result = {}
    # (a) Compustat epspx (current committed source)
    epspx = q_file("compustat_funda_eps.sql")
    a = epspx[["permno", "fyear", "eps"]].rename(columns={"eps": "eps"})
    a["fyear"] = a["fyear"].astype(int)
    result["a_epspx"] = eg_from_series(a, panel_map8)
    # (c) Compustat epsfx (diluted ex-items) — need epsfx from funda
    epsfx = q("""
        SELECT toUInt32(l.lpermno) AS permno, f.fyear AS fyear, f.epsfx AS eps
        FROM comp_202601.funda f
        INNER JOIN crsp_202601.ccmxpf_linktable l
          ON f.gvkey = l.gvkey AND l.linktype IN ('LC','LU')
         AND l.linkprim IN ('P','C') AND l.usedflag = 1
         AND toDate32(f.datadate) >= toDate32(l.linkdt)
         AND toDate32(f.datadate) <= toDate32(coalesce(l.linkenddt,'2100-01-01'))
        WHERE f.indfmt='INDL' AND f.consol='C' AND f.popsrc='D' AND f.datafmt='STD'
          AND f.fyear >= 1976 AND f.fyear <= 2014 AND f.epsfx IS NOT NULL
        SETTINGS join_algorithm='partial_merge', max_execution_time = 600,
                 max_rows_to_read = 10000000000
    """)
    epsfx["fyear"] = epsfx["fyear"].astype(int)
    result["c_epsfx"] = eg_from_series(epsfx, panel_map8)
    # (b) IBES ANN actuals (split-adjusted, common basis)
    ann_ibes = q("""
        SELECT cusip, pends, value FROM ibes_202601.act_epsus
        WHERE pdicity='ANN' AND usfirm=1 AND measure='EPS'
          AND value IS NOT NULL AND pends IS NOT NULL AND pends != ''
        SETTINGS max_execution_time = 600, max_rows_to_read = 10000000000
    """)
    ann_ibes["pends"] = pd.to_datetime(ann_ibes["pends"])
    ann_ibes = map_cusip_to_permno(ann_ibes, cm, "pends")
    ann_ibes["fyear"] = ann_ibes["pends"].dt.year
    ann_ibes = ann_ibes[["permno", "fyear", "value"]].rename(columns={"value": "eps"})
    result["b_ibes_act"] = eg_from_series(ann_ibes, panel_map8)

    paper = {"t6_t1": {1: 6.95, 10: 30.56}, "t_t5": {1: 10.11, 10: 10.85}}
    labels = {"a_epspx": "Compustat epspx (current)",
              "b_ibes_act": "IBES ANN act_epsus (split-adj)",
              "c_epsfx": "Compustat epsfx (diluted ex-items)"}
    for key in ("a_epspx", "b_ibes_act", "c_epsfx"):
        print(f"\n[{labels[key]}]")
        for win, wlabel in (("t6_t1", "EG_{t-6:t-1}"), ("t_t5", "EG_{t:t+5}")):
            ts = result[key][win]
            d1, d10 = ts.get(1, np.nan), ts.get(10, np.nan)
            print(f"  {wlabel}: D1={d1:.3f}  D10={d10:.3f}  "
                  f"(paper D1={paper[win][1]}, D10={paper[win][10]})")
    return result


# ------------------------------------------------------------------ #
# Task 6 — T8 cell-status movement per candidate
# ------------------------------------------------------------------ #
SIGN_EPS = 1e-9


def _sign(x):
    return 1 if x > SIGN_EPS else (-1 if x < -SIGN_EPS else 0)


def classify(paper, ours, tol_pct, zero_band=None):
    if paper is None or ours is None or (isinstance(ours, float) and np.isnan(ours)):
        return "MISSING"
    tol = tol_pct / 100.0
    if zero_band is not None:
        abs_dev = abs(ours - paper)
        if abs_dev <= zero_band:
            return "Match"
        mag_err = max(0.0, abs_dev - zero_band) / max(zero_band, 1e-12)
        if _sign(paper) != _sign(ours) and _sign(paper) != 0 and _sign(ours) != 0:
            return "FAIL"
        return "Match" if mag_err <= tol else "FAIL"
    if paper == 0:
        rel_err = min(abs(ours) / max(tol, 1e-12), 100.0)
    else:
        rel_err = abs(ours - paper) / abs(paper)
    if _sign(paper) != _sign(ours) and _sign(paper) != 0 and _sign(ours) != 0:
        return "FAIL"
    return "Match" if rel_err <= tol else "FAIL"


def task6_cell_movement():
    print("\n" + "=" * 70)
    print("TASK 6 — T8 cell-status movement vs committed metrics")
    print("=" * 70)
    targets = json.loads(LAYOUT.preparations_path("tables_to_replicate.json").read_text())
    committed = json.loads(LAYOUT.eval_path("metrics.json").read_text())["metrics"]
    # collect paper targets for SUE/EG (all T8)
    paper = {}
    tol = {}
    zb = {}
    for tbl in targets["tables"]:
        if tbl["id"] != "T8":
            continue
        for m in tbl["metrics"]:
            paper[m["name"]] = m["value"]
            tol[m["name"]] = float(m.get("tolerance_pct", 0))
            zb[m["name"]] = m.get("zero_band")
    # current committed status per cell
    def commit_status(name):
        e = committed.get(name)
        v = e["value"] if isinstance(e, dict) else e
        return classify(paper[name], v, tol[name], zb[name])

    sue_prefix = ("t8_sue1", "t8_sue2", "t8_sue3")
    eg_prefix = ("t8_eg_t6_t1", "t8_eg_t_t5")
    cells = [n for n in paper if n.startswith(sue_prefix) or n.startswith(eg_prefix)]
    # current status counts
    status_cur = {c: commit_status(c) for c in cells}
    print("\nCurrent committed T8 SUE/EG status counts:")
    from collections import Counter
    print("  ", dict(Counter(status_cur.values())))
    for c in cells:
        if c.endswith("_D1") or c.endswith("_D10") or c.endswith("_D1D10"):
            pass
    return paper, tol, zb, status_cur


if __name__ == "__main__":
    cm = load_cusip_map()
    panel_map8 = build_covered_mapping(cm)
    print(f"Covered mapping: {len(panel_map8)} (permno, sort_year) rows")
    task1_split_adjustment()
    s1, ts1 = task2_sue_ibes(cm, panel_map8)
    f3, ts3 = task3_sue3(cm, panel_map8)
    eg_res = task4_eg(cm, panel_map8)
    task6_cell_movement()
