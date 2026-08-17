"""
EXPERIMENT HARNESS (iteration 5) — scratch module, does NOT touch main.py.

Diagnosis + controlled experiment matrix over duration-construction variants for
the long-duration-tail mismatch (D9 too LOW, D10 too HIGH vs the paper).

Step 1 (bug check): verify D10's extreme months against raw crsp_202601.msf.
Step 2 (matrix):  V0..V5 duration → decile assignment variants, rebuild bin EW
                  returns, report D1..D10 means / spread, per-cell status flips
                  vs baseline, D10 top-3 months, and |ROE|/g/me_jun composition.
Step 3: D9-vs-D10 boundary composition (V0 vs best variant).

Writes only to results/ (a scratch .md) and prints the matrix to stdout. Reads
data/fundamentals_duration.parquet + data/panel.parquet. No changes to data/ or
eval/ canonical outputs.

The duration recursion (Dechow-Sloan-Soliman 2004 / Weber 2018 Eq. 2) is
reproduced from main.py's _duration_vectorized and parameterized:

  roe_s = roe_ss + ar_roe^s * (roe - roe_ss)
  g_s   = sg_ss  + ar_sg^s  * (g   - sg_ss)
  bv_s  = bv_{s-1} * (1 + g_s),  bv_0 = be
  cf_s  = bv_{s-1} * (roe_s - g_s)
  pv_s  = cf_s / (1+r)^s
  Dur   = [ sum s*pv_s + (T + (1+r)/r) * (p - sum pv_s) ] / p

Variants:
  V0 baseline : inputs winsorized within fyear @1/99; Dur winsorized per sort-year @1/99.
  V1 dur-only  : roe_raw/g_raw in recursion; Dur winsorized per sort-year @1/99; no input win.
  V2 no win    : roe_raw/g_raw in recursion; raw Dur sort (no Dur winsorization).
  V3 cf floor  : CF_{t+s} = max(CF_{t+s}, 0) in recursion; baseline win otherwise.
  V4 roe trunc : ROE_{t+s} = max(ROE_{t+s}, -1.0) in recursion; baseline win otherwise.
  V5 ret win   : baseline duration; monthly cross-sectional 1%/99% winsorization of
                 ret_dl before computing portfolio means.
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

R = 0.12
T_HORIZON = 15
AR_ROE = 0.4067
AR_SG = 0.2411
ROE_SS = 0.12
SG_SS = 0.06

BIN_LABELS = [f"D{i}" for i in range(1, 11)]
MEAN_CELLS = ["mean_D1", "mean_D2", "mean_D3", "mean_D4", "mean_D5",
              "mean_D6", "mean_D7", "mean_D8", "mean_D9", "mean_D10", "mean_D1D10"]
ALPHA_CELLS = {
    "ff3": [f"ff3_alpha_D{i}" for i in range(1, 11)] + ["ff3_alpha_D1D10"],
    "ff4": [f"ff4_alpha_D{i}" for i in range(1, 10)] + ["ff4_alpha_D10", "ff4_alpha_D1D10"],
    "ff5": [f"ff5_alpha_D{i}" for i in range(1, 10)] + ["ff5_alpha_D10", "ff5_alpha_D1D10"],
}


def _client() -> Client:
    cfg = get_clickhouse_config()
    return Client(host=cfg["host"], port=int(cfg["port"]), user=cfg["user"],
                  password=cfg["password"], database=cfg["database"],
                  settings={"max_execution_time": 600})


def q(sql: str) -> pd.DataFrame:
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


# --------------------------------------------------------------------------- #
# data loading
# --------------------------------------------------------------------------- #
def load_fund() -> pd.DataFrame:
    f = pd.read_parquet(LAYOUT.data_path("fundamentals_duration.parquet"))
    return f


def load_panel() -> pd.DataFrame:
    p = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
    p["month"] = pd.to_datetime(p["month"])
    p["date"] = pd.to_datetime(p["date"])
    return p


def load_factors() -> pd.DataFrame:
    df = q((LAYOUT.src_path("sql") / "ff_factors.sql").read_text())
    df["dt"] = pd.to_datetime(df["dt"])
    return df.sort_values("dt").reset_index(drop=True)


# --------------------------------------------------------------------------- #
# duration recursion (parameterized)
# --------------------------------------------------------------------------- #
def duration_recursion(roe: np.ndarray, g: np.ndarray, be: np.ndarray, p: np.ndarray,
                       cf_floor_zero: bool = False, roe_truncate: bool = False) -> np.ndarray:
    n = roe.shape[0]
    s = np.arange(1, T_HORIZON + 1, dtype=np.float64)
    ar_roe_s = np.power(AR_ROE, s)
    ar_sg_s = np.power(AR_SG, s)
    disc = np.power(1.0 + R, s)

    roe = np.where(np.isfinite(roe), roe, ROE_SS)
    g = np.where(np.isfinite(g), g, SG_SS)
    be = np.where(np.isfinite(be) & (be > 0), be, 0.0)
    p = np.where(np.isfinite(p) & (p > 0), p, 0.0)

    roe_all = ROE_SS + ar_roe_s[None, :] * (roe[:, None] - ROE_SS)
    g_all = SG_SS + ar_sg_s[None, :] * (g[:, None] - SG_SS)

    if roe_truncate:
        roe_all = np.maximum(roe_all, -1.0)
    if cf_floor_zero:
        # CF_t = bv_{t-1} * (roe_t - g_t); floor at zero requires bv>0.
        pass  # handled below after cf computed

    bv = np.empty((n, T_HORIZON + 1), dtype=np.float64)
    bv[:, 0] = be
    cf_pv = np.empty((n, T_HORIZON), dtype=np.float64)
    for k in range(T_HORIZON):
        bv_prev = bv[:, k]
        g_k = g_all[:, k]
        roe_k = roe_all[:, k]
        bv[:, k + 1] = bv_prev * (1.0 + g_k)
        cf_k = bv_prev * (roe_k - g_k)
        if cf_floor_zero:
            cf_k = np.maximum(cf_k, 0.0)
        cf_pv[:, k] = cf_k / disc[k]

    pv_sum = cf_pv.sum(axis=1)
    weighted = (cf_pv * s[None, :]).sum(axis=1)
    terminal = (T_HORIZON + (1.0 + R) / R) * (p - pv_sum)
    dur = (weighted + terminal) / p
    return dur


# --------------------------------------------------------------------------- #
# winsorization helpers
# --------------------------------------------------------------------------- #
def _clip_cs(s):
    lo, hi = s.quantile(0.01), s.quantile(0.99)
    return s.clip(lo, hi)


def _winsorize_inputs(funda: pd.DataFrame, use_raw: bool) -> pd.DataFrame:
    """Return a copy with roe/g chosen (winsorized vs raw), winsorized only if use_raw=False."""
    f = funda.copy()
    if use_raw:
        f["roe_in"] = f["roe_raw"]
        f["g_in"] = f["g_raw"]
    else:
        # baseline: winsoize within fyear @1/99 (matches main.py _clip_cs on roe/g)
        f["roe_w"] = f.groupby("fyear")["roe_raw"].transform(_clip_cs)
        f["g_w"] = f.groupby("fyear")["g_raw"].transform(_clip_cs)
        f["roe_in"] = f["roe_w"]
        f["g_in"] = f["g_w"]
    return f


def build_dur_variant(funda: pd.DataFrame, use_raw: bool, dur_winsorize: bool,
                      cf_floor_zero: bool, roe_truncate: bool) -> pd.DataFrame:
    """Rebuild dur for a variant and return (permno, sort_year, dur_raw_v, dur_v)."""
    f = _winsorize_inputs(funda, use_raw)
    # BE in dollars (matching P): funda['be'] is millions
    be = f["be"].to_numpy() * 1e6
    p = f["p"].to_numpy()
    roe = f["roe_in"].to_numpy()
    g = f["g_in"].to_numpy()
    dur = duration_recursion(roe, g, be, p, cf_floor_zero, roe_truncate)
    f["dur_v_raw"] = dur

    # sort_year = fyear + 1
    f["sort_year"] = f["fyear"] + 1
    if dur_winsorize:
        f["dur_v"] = f.groupby("sort_year")["dur_v_raw"].transform(_clip_cs)
    else:
        f["dur_v"] = f["dur_v_raw"]
    return f[["permno", "fyear", "sort_year", "dur_v_raw", "dur_v",
              "be", "roe_in", "g_in", "p"]].copy()


def assign_bins(dur_df: pd.DataFrame) -> pd.DataFrame:
    """Decile 1..10 by dur_v over ALL universe stocks within sort_year."""
    d = dur_df.copy()
    d = d[d["sort_year"].between(1963, 2013)]
    d = d[d["dur_v"].notna() & d["p"].notna() & (d["p"] > 0)]
    d = d.sort_values("dur_v").drop_duplicates(subset=["permno", "sort_year"], keep="last")
    d["bin"] = d.groupby("sort_year")["dur_v"].rank(method="first", pct=True)
    d["bin"] = np.ceil(d["bin"] * 10).astype(int).clip(1, 10)
    return d


# --------------------------------------------------------------------------- #
# portfolio returns
# --------------------------------------------------------------------------- #
def portfolio_returns(panel: pd.DataFrame, ret_col: str, ret_winsorize: bool):
    """EW (delisting-adj) per (bin, month). Returns month-indexed wide with D1..D10."""
    p = panel[["month", "bin", ret_col]].copy()
    if ret_winsorize:
        p[ret_col] = p.groupby("month")[ret_col].transform(_clip_cs)
    ew = p.groupby(["month", "bin"])[ret_col].mean().unstack()
    ew = ew.reindex(columns=range(1, 11))
    ew.columns = BIN_LABELS
    return ew


def align_excess(port_rets: pd.DataFrame, factors: pd.DataFrame) -> pd.DataFrame:
    ff = factors.set_index("dt")["rf"]
    rf = ff.groupby(ff.index.to_period("M")).last()
    rf.index = rf.index.to_timestamp()
    aligned = port_rets.join(rf.rename("rf"), how="left")
    for c in port_rets.columns:
        aligned[c] = aligned[c] - aligned["rf"]
    return aligned.drop(columns=["rf"])


def ols_alpha(port_excess: pd.Series, X: pd.DataFrame) -> float:
    import statsmodels.api as sm
    y = port_excess.dropna()
    Xa = X.reindex(y.index).dropna()
    y = y.reindex(Xa.index)
    Xc = sm.add_constant(Xa)
    model = sm.OLS(y, Xc).fit()
    return float(model.params["const"])


# --------------------------------------------------------------------------- #
# classify (mirrors evaluate.py for cell status)
# --------------------------------------------------------------------------- #
SIGN_EPS = 1e-9


def _sign(x):
    if x > SIGN_EPS:
        return 1
    if x < -SIGN_EPS:
        return -1
    return 0


def classify(paper, ours, tolerance_pct, zero_band=None):
    if paper is None or ours is None:
        return None
    tol = tolerance_pct / 100.0
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


def load_paper_targets():
    doc = json.loads(LAYOUT.preparations_path("tables_to_replicate.json").read_text())
    paper = {}
    for tbl in doc.get("tables", []):
        if tbl.get("id") not in ("T2", "T3"):
            continue
        for m in tbl.get("metrics", []):
            paper[m["name"]] = m
    return paper


# --------------------------------------------------------------------------- #
# run one variant -> full T2+T3 metrics dict (all 99 committed cells)
# --------------------------------------------------------------------------- #
def run_variant(name, funda, panel, factors, paper,
                use_raw=False, dur_winsorize=True, cf_floor_zero=False,
                roe_truncate=False, ret_winsorize=False):
    dur_df = build_dur_variant(funda, use_raw, dur_winsorize, cf_floor_zero, roe_truncate)
    bins = assign_bins(dur_df)

    meta = bins[["permno", "sort_year", "bin", "dur_v", "dur_v_raw"]].drop_duplicates(
        ["permno", "sort_year"])
    panel = panel.merge(meta, on=["permno", "sort_year"], how="left")
    panel["bin"] = panel["bin_y"]
    panel = panel[panel["bin"].notna()].copy()

    ew = portfolio_returns(panel, "ret_dl", ret_winsorize)
    ew_nodl = portfolio_returns(panel, "ret", ret_winsorize)
    ew_ex = align_excess(ew, factors)
    nodl_ex = align_excess(ew_nodl, factors)

    # VW returns (me_jun-weighted)
    vw_wide = vw_portfolio_returns(panel, "ret_dl", ret_winsorize)
    vw_ex = align_excess(vw_wide, factors)

    means = ew_ex.mean() * 100.0
    spread = means["D1"] - means["D10"]
    res = {f"mean_{c}": float(means[c]) for c in BIN_LABELS}
    res["mean_D1D10"] = float(spread)

    # Panel C VW means
    vw_means = vw_ex.mean() * 100.0
    vw_means["D1D10"] = vw_means["D1"] - vw_means["D10"]
    for c in BIN_LABELS + ["D1D10"]:
        res[f"vw_mean_{c}"] = float(vw_means[c])

    # Panel D no-delisting means
    nodl_means = nodl_ex.mean() * 100.0
    nodl_means["D1D10"] = nodl_means["D1"] - nodl_means["D10"]
    for c in BIN_LABELS + ["D1D10"]:
        res[f"nodl_mean_{c}"] = float(nodl_means[c])

    ff = factors.set_index("dt")
    mkt = pd.DataFrame({"mkt_rf": ff["mkt_rf"]})
    mkt.index = mkt.index.to_period("M").to_timestamp()

    # CAPM beta/alpha (Panel A)
    for i in range(1, 11):
        c = f"D{i}"
        b, a = ols_beta_alpha(ew_ex[c], mkt)
        res[f"beta_capm_{c}"] = b
        res[f"alpha_capm_{c}"] = float(a) * 100.0
    sp = (ew_ex["D1"] - ew_ex["D10"]).rename("sp")
    b_sp, a_sp = ols_beta_alpha(sp, mkt)
    res["beta_capm_D1D10"] = b_sp
    res["alpha_capm_D1D10"] = float(a_sp) * 100.0

    # Sharpe (Panel B)
    for c in BIN_LABELS:
        s = ew_ex[c]
        res[f"sharpe_{c}"] = float(s.mean() / s.std(ddof=1)) if s.std(ddof=1) > 0 else float("nan")
    sp_s = spread_s = ew_ex["D1"] - ew_ex["D10"]
    res["sharpe_D1D10"] = float(sp_s.mean() / sp_s.std(ddof=1)) if sp_s.std(ddof=1) > 0 else float("nan")

    # alphas for T3
    fact_cols = {
        "ff3": ["mkt_rf", "smb", "hml"],
        "ff4": ["mkt_rf", "smb", "hml", "mom"],
        "ff5": ["mkt_rf", "smb", "hml", "rmw", "cma"],
    }
    for tag, cols in fact_cols.items():
        X = pd.DataFrame({c: ff[c] for c in cols})
        X.index = X.index.to_period("M").to_timestamp()
        for i in range(1, 11):
            res[f"{tag}_alpha_D{i}"] = ols_alpha(ew_ex[f"D{i}"], X) * 100.0
        sp = (ew_ex["D1"] - ew_ex["D10"]).rename("sp")
        res[f"{tag}_alpha_D1D10"] = ols_alpha(sp, X) * 100.0

    # D10 top-3 months + composition
    d10 = panel[panel["bin"] == 10]
    top = d10.groupby("month")["ret_dl"].mean().sort_values(ascending=False).head(3)
    fund_d10 = bins[bins["bin"] == 10].copy()
    comp = {
        "mean_abs_roe": float(fund_d10["roe_in"].abs().mean()),
        "mean_g": float(fund_d10["g_in"].mean()),
        "median_me_jun": float(panel[panel["bin"] == 10]["me_jun"].median()),
    }
    return res, top, comp, None


def vw_portfolio_returns(panel, ret_col, ret_winsorize):
    p = panel[["month", "bin", ret_col, "me_jun"]].copy()
    if ret_winsorize:
        p[ret_col] = p.groupby("month")[ret_col].transform(_clip_cs)
    has_me = p["me_jun"].notna() & (p["me_jun"] > 0)
    vw_num = p.loc[has_me].copy()
    vw_num["weighted"] = vw_num[ret_col] * vw_num["me_jun"]
    vw_num = vw_num.groupby(["month", "bin"]).agg(num=("weighted", "sum"),
                                                  den=("me_jun", "sum")).reset_index()
    ew = p.groupby(["month", "bin"])[ret_col].mean().rename("ew").reset_index()
    out = ew.merge(vw_num, on=["month", "bin"], how="left")
    out["vw"] = np.where(out["den"].notna() & (out["den"] > 0), out["num"] / out["den"], out["ew"])
    w = out.pivot_table(index="month", columns="bin", values="vw")
    w = w.reindex(columns=range(1, 11))
    w.columns = BIN_LABELS
    return w


def ols_beta_alpha(port_excess, X):
    import statsmodels.api as sm
    y = port_excess.dropna()
    Xa = X.reindex(y.index).dropna()
    y = y.reindex(Xa.index)
    Xc = sm.add_constant(Xa)
    model = sm.OLS(y, Xc).fit()
    return float(model.params[X.columns[0]]), float(model.params["const"])


def paper_get(pm, k):
    e = pm.get(k)
    return e.get("value") if isinstance(e, dict) else e


# --------------------------------------------------------------------------- #
# main experiment runner
# --------------------------------------------------------------------------- #
def _baseline_metrics():
    """Recompute the canonical V0 baseline from data (should reproduce metrics.json)."""
    funda = load_fund()
    panel = load_panel()
    factors = load_factors()
    paper_meta = load_paper_targets()
    paper = {k: (v.get("value") if isinstance(v, dict) else v) for k, v in paper_meta.items()}
    return funda, panel, factors, paper_meta, paper


def main():
    funda, panel, factors, paper_meta, paper = _baseline_metrics()

    # canonical baseline from eval/metrics.json (the CURRENT pipeline V0, committed)
    canonical = json.loads(LAYOUT.eval_path("metrics.json").read_text())["metrics"]
    canonical_vals = {}
    for k, v in canonical.items():
        canonical_vals[k] = v["value"] if isinstance(v, dict) and "value" in v else v

    variants = [
        ("V0 baseline", dict(use_raw=False, dur_winsorize=True, cf_floor_zero=False,
                             roe_truncate=False, ret_winsorize=False)),
        ("V1 dur-only", dict(use_raw=True, dur_winsorize=True, cf_floor_zero=False,
                             roe_truncate=False, ret_winsorize=False)),
        ("V2 no-win", dict(use_raw=True, dur_winsorize=False, cf_floor_zero=False,
                           roe_truncate=False, ret_winsorize=False)),
        ("V3 cf-floor", dict(use_raw=False, dur_winsorize=True, cf_floor_zero=True,
                             roe_truncate=False, ret_winsorize=False)),
        ("V4 roe-trunc", dict(use_raw=False, dur_winsorize=True, cf_floor_zero=False,
                              roe_truncate=True, ret_winsorize=False)),
        ("V5 ret-win", dict(use_raw=False, dur_winsorize=True, cf_floor_zero=False,
                            roe_truncate=False, ret_winsorize=True)),
    ]

    # baseline statuses (from canonical metrics.json) for flip comparison
    results = {}
    for name, kw in variants:
        res, top, comp, _ = run_variant(name, funda, panel.copy(), factors, paper, **kw)
        results[name] = (res, top, comp)

    # Report matrix
    print("=" * 110)
    print("EXPERIMENT MATRIX: duration-construction variants (D9/D10/spread + status flips)")
    print("=" * 110)
    header = ["variant", "D7", "D8", "D9", "D10", "D1-D10",
              "mean_flips", "alpha_flips", "T2D9delta", "T2D10delta"]
    print(" | ".join(f"{h:>12}" for h in header))

    canonical_flat = ["mean_" + c for c in ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D1D10"]]
    alpha_flat = []
    for tag, cells in ALPHA_CELLS.items():
        alpha_flat += cells

    # baseline status per cell (canonical metrics.json = V0)
    def v0_status(cell):
        if cell not in paper_meta:
            return None
        tol = paper_meta[cell]["tolerance_pct"]
        zb = paper_meta[cell].get("zero_band")
        return classify(paper_get(paper_meta, cell), canonical_vals.get(cell), tol, zb)

    rows_out = []
    for name, kw in variants:
        res, top, comp = results[name]
        d7, d8, d9, d10, spread = res["mean_D7"], res["mean_D8"], res["mean_D9"], res["mean_D10"], res["mean_D1D10"]
        # flip counts
        mean_flips, alpha_flips = 0, 0
        flip_details = []
        for cell in canonical_flat:
            st_v0 = v0_status(cell)
            tol = paper_meta[cell]["tolerance_pct"]
            zb = paper_meta[cell].get("zero_band")
            st_v = classify(paper_get(paper_meta, cell), res.get(cell), tol, zb)
            if st_v0 is not None and st_v0 != st_v:
                mean_flips += 1
                flip_details.append((cell, st_v0, st_v))
        for cell in alpha_flat:
            st_v0 = v0_status(cell)
            tol = paper_meta[cell]["tolerance_pct"]
            zb = paper_meta[cell].get("zero_band")
            st_v = classify(paper_get(paper_meta, cell), res.get(cell), tol, zb)
            if st_v0 is not None and st_v0 != st_v:
                alpha_flips += 1
                flip_details.append((cell, st_v0, st_v))
        rows_out.append((name, d7, d8, d9, d10, spread, mean_flips, alpha_flips,
                         res.get("mean_D9"), res.get("mean_D10")))
        print(f"{name:<12} | {d7:>12.3f} | {d8:>12.3f} | {d9:>12.3f} | {d10:>12.3f} | "
              f"{spread:>12.3f} | {mean_flips:>10d} | {alpha_flips:>11d} | "
              f"{(res.get('mean_D9')-paper_get(paper_meta,'mean_D9')):>12.3f} | "
              f"{(res.get('mean_D10')-paper_get(paper_meta,'mean_D10')):>12.3f}")

    print()
    print("Paper targets (mean D7/D8/D9/D10/spread): 0.81 / 0.68 / 0.62 / 0.32 / 1.10")
    print()
    print("=" * 110)
    print("PER-VARIANT D10 top-3 months (%/mo) and composition")
    print("=" * 110)
    for name, kw in variants:
        res, top, comp = results[name]
        top_str = ", ".join(f"{pd.Timestamp(m).strftime('%Y-%m')}:{v*100:.1f}" for m, v in top.items())
        print(f"{name:<12} | top3: {top_str}")
        print(f"{'':>12} | mean|ROE|={comp['mean_abs_roe']:.4f}  mean g={comp['mean_g']:.4f}  "
              f"median me_jun={comp['median_me_jun']:.3e}")

    print()
    print("=" * 110)
    print("FAIL cell count per variant (full T2+T3 committed cells, 99 total)")
    print("=" * 110)
    # Build the full committed cell key list from paper_meta (T2 + T3)
    all_committed = [m["name"] for tbl in [t for t in
                     json.loads(LAYOUT.preparations_path("tables_to_replicate.json").read_text()).get("tables", [])
                     if t["id"] in ("T2", "T3")] for m in tbl["metrics"]]

    for name, kw in variants:
        if name == "V0 baseline":
            res = canonical_vals  # canonical current pipeline = V0, use committed values directly
        else:
            res = results[name][0]
        n_fail, n_match, n_missing = 0, 0, 0
        for cell in all_committed:
            tol = paper_meta[cell]["tolerance_pct"]
            zb = paper_meta[cell].get("zero_band")
            st = classify(paper_get(paper_meta, cell), res.get(cell), tol, zb)
            if st == "FAIL":
                n_fail += 1
            elif st == "Match":
                n_match += 1
            else:
                n_missing += 1
        L = (n_fail + n_missing) / (n_fail + n_match + n_missing) if (n_fail + n_match + n_missing) else float("nan")
        print(f"{name:<12} -> FAIL={n_fail}  Match={n_match}  missing={n_missing}  L={L:.4f}")

    # per-variant flip details (Match<->FAIL) vs V0 baseline
    print()
    print("=" * 110)
    print("FLIP DETAILS vs V0 baseline (cells changing Match<->FAIL)")
    print("=" * 110)
    for name, kw in variants:
        if name == "V0 baseline":
            continue
        res = results[name][0]
        flips = []
        for cell in all_committed:
            tol = paper_meta[cell]["tolerance_pct"]
            zb = paper_meta[cell].get("zero_band")
            st_v0 = classify(paper_get(paper_meta, cell), canonical_vals.get(cell), tol, zb)
            st_v = classify(paper_get(paper_meta, cell), res.get(cell), tol, zb)
            if st_v0 is not None and st_v0 != st_v:
                flips.append((cell, st_v0, st_v))
        if flips:
            for cell, st0, stv in flips:
                print(f"  {name:<12} {cell:<22} {st0} -> {stv}  "
                      f"(paper={paper_get(paper_meta,cell):.3f} v0={canonical_vals.get(cell):.3f} new={res.get(cell):.3f})")
        else:
            print(f"  {name}: no flips")
    # summarize T2 mean flips and T3 alpha flips separately
    print()
    for name, kw in variants:
        if name == "V0 baseline":
            continue
        res = results[name][0]
        t2mean_flips = sum(1 for cell in canonical_flat
                          if classify(paper_get(paper_meta, cell), canonical_vals.get(cell),
                                      paper_meta[cell]["tolerance_pct"], paper_meta[cell].get("zero_band"))
                          != classify(paper_get(paper_meta, cell), res.get(cell),
                                      paper_meta[cell]["tolerance_pct"], paper_meta[cell].get("zero_band")))
        t3alpha_flips = sum(1 for cell in alpha_flat
                           if classify(paper_get(paper_meta, cell), canonical_vals.get(cell),
                                       paper_meta[cell]["tolerance_pct"], paper_meta[cell].get("zero_band"))
                           != classify(paper_get(paper_meta, cell), res.get(cell),
                                       paper_meta[cell]["tolerance_pct"], paper_meta[cell].get("zero_band")))
        print(f"{name:<12}: T2 mean flips={t2mean_flips}, T3 alpha flips={t3alpha_flips}")

    # Step 3: boundary composition V0 vs best
    print()
    print("=" * 110)
    print("STEP 3: D9 vs D10 boundary composition (V0 vs V3)")
    print("=" * 110)
    boundary_report(results, funda, panel, paper_meta)

    return results


def boundary_report(results, funda, panel, paper_meta):
    # rebuild bins for V0 (baseline) and V3 (cf-floor) and report D9/D10 composition
    for name, kw in [("V0 baseline", dict(use_raw=False, dur_winsorize=True, cf_floor_zero=False,
                                          roe_truncate=False, ret_winsorize=False)),
                     ("V3 cf-floor", dict(use_raw=False, dur_winsorize=True, cf_floor_zero=True,
                                          roe_truncate=False, ret_winsorize=False))]:
        dur_df = build_dur_variant(funda, kw["use_raw"], kw["dur_winsorize"],
                                   kw["cf_floor_zero"], kw["roe_truncate"])
        bins = assign_bins(dur_df)
        # merge me_jun from panel
        me = panel[["permno", "sort_year", "me_jun"]].drop_duplicates(["permno", "sort_year"])
        bins = bins.merge(me, on=["permno", "sort_year"], how="left")
        # median dur, be, me_jun, share neg roe_raw, share be<10M
        for bname in ("D9", "D10"):
            b = bins[bins["bin"] == (9 if bname == "D9" else 10)]
            # negative ROE_raw: use the raw (un-winsorized) roe if available
            neg_roe = (b["roe_in"] < 0).mean()
            be_lt10 = ((b["be"]) < 10).mean()  # be in millions; $10M = 10 million
            print(f"{name} {bname} (n={len(b)}): "
                  f"median dur={b['dur_v'].median():.3f} "
                  f"median BE(M)={b['be'].median():.3f} "
                  f"median me_jun={b['me_jun'].median():.3e} "
                  f"share neg ROE={neg_roe:.3f} "
                  f"share BE<$10M={be_lt10:.3f}")


if __name__ == "__main__":
    main()
