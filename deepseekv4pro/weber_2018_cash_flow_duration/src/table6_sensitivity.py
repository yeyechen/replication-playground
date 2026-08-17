"""
Table 6 RV-series sensitivity grid (audit2 M2 diagnostic).

DOES NOT write metrics.json or touch table6.py/the committed pipeline.
Produces a comparison of six realized-variance (RV) constructions, holding the
monthly portfolio excess returns FIXED, to separate a fixable RV-construction
issue from an inherited tail effect. This is a diagnostic: the Replicator decides
whether to commit any variant.

Variants (monthly R_{i,t} fixed at the panel's ret_dl EW excess returns):
  T0  canonical:   RV_{i,t-1} = Sigma r^2 over prior-month trading days, daily EW
                   within sort-year membership.
  T1  VW:          daily VALUE-weighted portfolio returns (weights = me_jun constant).
  T2  stability:   prior-month daily returns including only members with >=15 valid
                   daily returns that month (membership stability screen).
  T3  market RV:   RV = dw^2 of crsp_202601.dsi.vwretd (SAME RV for every portfolio).
  T4  degenerate:  RV_{i,t-1} = (monthly R_{i,t-1})^2  (single monthly obs).
  T5  inverse-var: scale by 1/RV^2 (not 1/RV), c re-normalized for std equality.

Each variant scales: R_vm_{i,t} = (c_i / RV_{i,t-1}) * R_{i,t}, c_i = std(R) /
std(R/RV) so the scaled series matches the unscaled full-sample std (Moreira-Muir).
"""
from __future__ import annotations

import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from clickhouse_driver import Client

from utils.env import get_clickhouse_config
from utils.paths import paper_layout

SLUG = "weber_2018_attempt2_deepseek"
LAYOUT = paper_layout(SLUG)
SQL_DIR = LAYOUT.src_path("sql")

BIN_LABELS = [f"D{i}" for i in range(1, 11)]
SERIES = BIN_LABELS + ["D1D10"]
VARIANTS = ["T0", "T1", "T2", "T3", "T4", "T5"]
FACTS = {
    "capm": ["mkt_rf"],
    "ff3": ["mkt_rf", "smb", "hml"],
    "ff4": ["mkt_rf", "smb", "hml", "mom"],
    "ff5": ["mkt_rf", "smb", "hml", "rmw", "cma"],
}
TOL = 0.20  # T6 tolerance_pct = 20 (relative)


def _client() -> Client:
    cfg = get_clickhouse_config()
    return Client(host=cfg["host"], port=int(cfg["port"]), user=cfg["user"],
                  password=cfg["password"], database=cfg["database"],
                  settings={"max_execution_time": 600})


def _q(sql: str):
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


def load_paper_targets() -> dict:
    doc = json.loads(LAYOUT.preparations_path("tables_to_replicate.json").read_text())
    paper = {}
    for tbl in doc.get("tables", []):
        if tbl.get("id") != "T6":
            continue
        for m in tbl.get("metrics", []):
            paper[m["name"]] = m["value"]
    return paper


def load_factors() -> pd.DataFrame:
    f = _q((SQL_DIR / "ff_factors.sql").read_text())
    f["dt"] = pd.to_datetime(f["dt"])
    return f.set_index("dt")


def monthly_excess(panel: pd.DataFrame, factors: pd.DataFrame):
    """Monthly EW excess returns (ret_dl mean), long-short included — decimal."""
    p = panel[["month", "bin", "ret_dl"]].copy()
    ew = p.groupby(["month", "bin"])["ret_dl"].mean().unstack()
    ew = ew.reindex(columns=range(1, 11))
    ew.columns = BIN_LABELS
    rf = factors["rf"].groupby(factors.index.to_period("M")).last()
    rf.index = rf.index.to_timestamp()
    aligned = ew.join(rf.rename("rf"), how="left")
    for c in BIN_LABELS:
        aligned[c] = aligned[c] - aligned["rf"]
    out = aligned[BIN_LABELS].copy()
    out["D1D10"] = out["D1"] - out["D10"]
    return out  # month-indexed, decimal


def build_daily_returns(panel: pd.DataFrame, kind: str) -> pd.DataFrame:
    """Daily portfolio returns, wide (date x bin), columns D1..D10 (+D1D10).

    kind in {'ew','vw','stability'}:
      ew        -> mean( ret )          [T0]
      vw        -> sum(me_jun * ret)/sum(me_jun)   [T1]
      stability -> only members with >=15 valid daily returns in the month [T2]
    """
    members = panel[["permno", "sort_year", "bin", "me_jun"]].drop_duplicates()
    members = members[members["bin"].between(1, 10)].copy()
    members["permno"] = members["permno"].astype("int32")
    members["sort_year"] = members["sort_year"].astype("int32")
    members["bin"] = members["bin"].astype("uint8")
    members["me_jun"] = members["me_jun"].astype("float64")

    c = _client()
    try:
        c.execute("DROP TEMPORARY TABLE IF EXISTS t6_members")
        c.execute(
            "CREATE TEMPORARY TABLE t6_members "
            "(permno Int32, sort_year Int32, bin UInt8, me_jun Float64) "
            "ENGINE = Memory"
        )
        c.execute("INSERT INTO t6_members VALUES",
                  [tuple(r) for r in members.itertuples(index=False)])
        sql = (SQL_DIR / "table6_constituents.sql").read_text()
        data, cols = c.execute(sql, with_column_types=True)
        cons = pd.DataFrame(data, columns=[x[0] for x in cols])
    finally:
        try:
            c.execute("DROP TEMPORARY TABLE IF EXISTS t6_members")
        except Exception:
            pass
        c.disconnect()

    cons["date"] = pd.to_datetime(cons["date"])
    cons["month"] = cons["date"].dt.to_period("M").dt.to_timestamp()

    if kind == "stability":
        # stability: keep only (permno, bin, month) with >=15 valid daily returns
        n_valid = cons.groupby(["permno", "bin", "month"]).size()
        keep = n_valid[n_valid >= 15].reset_index()
        cons = cons.merge(keep, on=["permno", "bin", "month"], how="inner")

    # aggregation: EW (mean) or VW (sum of me_jun-weighted / sum of me_jun)
    if kind in ("ew", "stability"):
        d = cons.groupby(["date", "bin"], as_index=False)["ret"].mean()
    elif kind == "vw":
        cons["wret"] = cons["ret"] * cons["me_jun"]
        g = cons.groupby(["date", "bin"], as_index=False)
        num = g["wret"].sum().rename(columns={"wret": "wnum"})
        den = g["me_jun"].sum().rename(columns={"me_jun": "wden"})
        dd = num.merge(den, on=["date", "bin"])
        d = dd.assign(ret=dd["wnum"] / dd["wden"])[["date", "bin", "ret"]]
    else:
        raise ValueError(kind)

    w = d.pivot_table(index="date", columns="bin", values="ret")
    w = w.reindex(columns=range(1, 11))
    w.columns = BIN_LABELS
    w["D1D10"] = w["D1"] - w["D10"]
    return w


def market_daily() -> pd.DataFrame:
    d = _q((SQL_DIR / "table6_market_rv.sql").read_text())
    d["date"] = pd.to_datetime(d["date"])
    return d[["date", "vwretd"]].copy()


def rv_from_daily(daily_wide: pd.DataFrame) -> pd.DataFrame:
    """monthly RV = sum of squared daily returns, columns = SERIES."""
    rv = (daily_wide ** 2).reset_index()
    rv["month"] = rv["date"].dt.to_period("M").dt.to_timestamp()
    rv = rv.drop(columns=["date"]).groupby("month").sum()
    return rv.reindex(columns=SERIES)


def rv_market(market: pd.DataFrame) -> pd.DataFrame:
    m = market.copy()
    m["month"] = m["date"].dt.to_period("M").dt.to_timestamp()
    rv = (m["vwretd"] ** 2).groupby(m["month"]).sum().rename("rv")
    out = pd.DataFrame({s: rv for s in SERIES})
    return out


def rv_monthly_sq(monthly: pd.DataFrame) -> pd.DataFrame:
    """T4: RV_{i,t-1} = (lagged monthly portfolio excess return)^2."""
    sq = monthly[list(SERIES)] ** 2
    # RV for month t-1 (used to scale month t): shift the squared series
    # forward by one month so that rv.index == the month being scaled.
    return sq.shift(1)


def _ols(y: pd.Series, X: pd.DataFrame):
    y = y.dropna()
    Xa = X.reindex(y.index).dropna()
    y = y.reindex(Xa.index)
    Xc = sm.add_constant(Xa)
    m = sm.OLS(y, Xc).fit()
    return float(m.params["const"])


def scale_series(monthly, rv, series, power):
    """Scale R by c * (1/RV^power); return month-indexed series."""
    ri = monthly[series].reindex(rv.index)
    rvi = rv[series]
    valid = ri.notna() & rvi.notna() & (rvi > 0)
    ri = ri[valid]
    rvi = rvi[valid]
    if ri.empty:
        return pd.Series(dtype=float)
    basis = ri / (rvi ** power)
    sd_r = ri.std(ddof=1)
    sd_b = basis.std(ddof=1)
    if sd_r <= 0 or sd_b <= 0 or not np.isfinite(sd_b):
        return pd.Series(dtype=float)
    ci = sd_r / sd_b
    return ci * basis


def compute_variant(monthly, factors, rv, power=1.0) -> dict:
    scaled = {s: scale_series(monthly, rv, s, power) for s in SERIES}
    factories = {}
    for k, cols in FACTS.items():
        X = pd.DataFrame({c: factors[c] for c in cols})
        X.index = X.index.to_period("M").to_timestamp()
        factories[k] = X
    res = {}
    for s in SERIES:
        y = scaled[s]
        res[f"vm_mean_{s}"] = float(y.mean() * 100.0) if len(y) else float("nan")
        for tag, X in factories.items():
            a = _ols(y, X)
            res[f"vm_alpha_{tag}_{s}"] = float(a * 100.0) if np.isfinite(a) else float("nan")
    return res


def match_and_mae(variant: dict, paper: dict, level_cells: list):
    match = 0
    for name in paper:
        o = variant.get(name)
        pv = paper[name]
        if o is None or not np.isfinite(o) or not np.isfinite(pv):
            continue
        rel = abs(o - pv) / abs(pv) if pv != 0 else (abs(o) if o != 0 else 0)
        if rel <= TOL and (np.sign(o) == np.sign(pv) or pv == 0 or o == 0):
            match += 1
    # MAE across the 50 level cells (mean + 4 alphas, D1..D10)
    errs = []
    for name in level_cells:
        o = variant.get(name)
        pv = paper.get(name)
        if o is None or pv is None or not np.isfinite(o) or not np.isfinite(pv):
            continue
        errs.append(abs(o - pv))
    mae = float(np.mean(errs)) if errs else float("nan")
    return match, mae


def main():
    panel = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
    panel["month"] = pd.to_datetime(panel["month"])
    factors = load_factors()
    paper = load_paper_targets()

    monthly = monthly_excess(panel, factors)  # fix monthly returns throughout

    # ---- build RV inputs ----
    daily_ew = build_daily_returns(panel, "ew")
    daily_vw = build_daily_returns(panel, "vw")
    daily_stab = build_daily_returns(panel, "stability")
    market = market_daily()

    rv_ew = rv_from_daily(daily_ew)          # T0
    rv_vw = rv_from_daily(daily_vw)          # T1
    rv_stab = rv_from_daily(daily_stab)      # T2
    rv_mkt = rv_market(market)               # T3
    rv_msq = rv_monthly_sq(monthly)          # T4

    level_cells = []
    for prefix in ["vm_mean_", "vm_alpha_capm_", "vm_alpha_ff3_",
                   "vm_alpha_ff4_", "vm_alpha_ff5_"]:
        for d in range(1, 11):
            level_cells.append(f"{prefix}D{d}")

    rows = []
    for name, rv, power in [
        ("T0_canonical_ew", rv_ew, 1.0),
        ("T1_valueweighted", rv_vw, 1.0),
        ("T2_stability15", rv_stab, 1.0),
        ("T3_market_rv", rv_mkt, 1.0),
        ("T4_monthly_sq", rv_msq, 1.0),
        ("T5_inverse_var", rv_ew, 2.0),
    ]:
        v = compute_variant(monthly, factors, rv, power)
        match, mae = match_and_mae(v, paper, level_cells)
        rows.append({
            "variant": name,
            "match": match,
            "mae_level": mae,
            "vm_mean_D1": v.get("vm_mean_D1"),
            "vm_mean_D10": v.get("vm_mean_D10"),
            "vm_mean_D1D10": v.get("vm_mean_D1D10"),
            "vm_alpha_capm_D1": v.get("vm_alpha_capm_D1"),
            "vm_alpha_capm_D10": v.get("vm_alpha_capm_D10"),
            "vm_alpha_capm_D1D10": v.get("vm_alpha_capm_D1D10"),
            "vm_alpha_ff3_D1": v.get("vm_alpha_ff3_D1"),
            "vm_alpha_ff3_D10": v.get("vm_alpha_ff3_D10"),
            "vm_alpha_ff3_D1D10": v.get("vm_alpha_ff3_D1D10"),
            "vm_alpha_ff4_D1": v.get("vm_alpha_ff4_D1"),
            "vm_alpha_ff4_D10": v.get("vm_alpha_ff4_D10"),
            "vm_alpha_ff4_D1D10": v.get("vm_alpha_ff4_D1D10"),
            "vm_alpha_ff5_D1": v.get("vm_alpha_ff5_D1"),
            "vm_alpha_ff5_D10": v.get("vm_alpha_ff5_D10"),
            "vm_alpha_ff5_D1D10": v.get("vm_alpha_ff5_D1D10"),
        })

    table = pd.DataFrame(rows)
    print("\n=== T6 RV sensitivity grid ===\n")
    print(table.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    # ---- decomposition: inherited baseline + scaling-induced increment ----
    print("\n=== Level-error decomposition (D1 / D10) ===\n")
    # unscaled baseline = monthly excess return mean (no scaling), same metric names
    base = {}
    for s in SERIES:
        y = monthly[s].dropna()
        base[f"vm_mean_{s}"] = float(y.mean() * 100.0)
        for tag, cols in FACTS.items():
            X = pd.DataFrame({c: factors[c] for c in cols})
            X.index = X.index.to_period("M").to_timestamp()
            base[f"vm_alpha_{tag}_{s}"] = float(_ols(y, X) * 100.0)

    for d in ["D1", "D10"]:
        bmean = base[f"vm_mean_{d}"]
        pmean = paper[f"vm_mean_{d}"]
        print(f"{d}: baseline(unscaled) mean = {bmean:.3f} vs paper {pmean:.3f} "
              f"(inherited err {abs(bmean-pmean):.3f})")
        for name, rv, power in [
            ("T0", rv_ew, 1.0), ("T1", rv_vw, 1.0), ("T2", rv_stab, 1.0),
            ("T3", rv_mkt, 1.0), ("T4", rv_msq, 1.0), ("T5", rv_ew, 2.0),
        ]:
            v = compute_variant(monthly, factors, rv, power)
            vm = v[f"vm_mean_{d}"]
            incr = vm - bmean  # scaling-induced increment (signed)
            print(f"  {name}: vm_mean = {vm:.3f} | scaling increment = {incr:+.3f} "
                  f"| total err vs paper = {abs(vm-pmean):.3f}")

    # paper-level reference for spread cells
    print("\npaper spread refs:", {k: paper[f"vm_{k}_D1D10"]
          for k in ["mean", "alpha_capm", "alpha_ff3", "alpha_ff4", "alpha_ff5"]})


if __name__ == "__main__":
    main()
