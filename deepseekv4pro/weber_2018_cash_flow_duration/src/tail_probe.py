"""
TAIL PROBE (outer iteration 3, inner iteration 1) — scratch module, does NOT
modify the canonical pipeline (main.py / panel.parquet / metrics.json).

Purpose
-------
Settle the open D9/D10 tail-construction question (audit2 M1) with a CONTROLLED
variant matrix over the loss-firm duration-construction reading. Rebuilds the
full duration measure from fundamentals_duration.parquet inputs under each
variant, re-forms the June decile sorts, recomputes T2/T3 tail metrics, and
compares against the committed baseline (V0).

Variants (per the Replicator's probe spec):
  V0  canonical (current committed): inputs winsorized within fyear @1/99;
      Dur winsorized per-sort-year @1/99; clean-surplus CF (no floor).
  V3  CF floor at zero in the recursion: CF_{t+s} = max(CF_{t+s}, 0).
      ("equityholders receive no negative distributions" reading.)
  V6  Dur winsorization POOLED across all sort years @1/99 (vs per-sort-year).
  V8  firms with BE < $1M excluded from duration sorts (DIAGNOSTIC only —
      quantifies how much of the D10 tail is tiny-BE; NOT committable).

Dropped per the spec (no DSS/paper citation, "soft knobs"):
  V3b (CF floor for first 5 years only), V7 (recursion inputs winsorized at
  0.5/99.5).

Reports, for each variant:
  mean_D9 / mean_D10 / mean_D1D10, nodl_mean_D9/D10, vw_mean_D10,
  alpha_capm_D9/D10, ff3/ff4/ff5_alpha_D9/D10, the COUNT of tail cells
  (18 D9/D10 cells across T2+T3) vs baseline within tolerance, and the spread
  deviation from 1.10. Also D10 composition: median me_jun, median BE, negative
  ROE share.

Writes only to results/ (iteration5_experiment_matrix.md append). No changes to
data/ or eval/.
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

# Duration parameters (identical to main.py / paper Eq 2/3/4)
R = 0.12
T_HORIZON = 15
AR_ROE = 0.4067
AR_SG = 0.2411
ROE_SS = 0.12
SG_SS = 0.06

BIN_LABELS = [f"D{i}" for i in range(1, 11)]

# The 18 D9/D10 tail cells (T2 + T3), spread cells excluded (tracked separately).
TAIL_CELLS = [
    "mean_D9", "mean_D10",
    "beta_capm_D9", "beta_capm_D10",
    "alpha_capm_D9", "alpha_capm_D10",
    "sharpe_D9", "sharpe_D10",
    "vw_mean_D9", "vw_mean_D10",
    "nodl_mean_D9", "nodl_mean_D10",
    "ff3_alpha_D9", "ff3_alpha_D10",
    "ff4_alpha_D9", "ff4_alpha_D10",
    "ff5_alpha_D9", "ff5_alpha_D10",
]
SPREAD_CELLS = [
    "mean_D1D10", "beta_capm_D1D10", "alpha_capm_D1D10", "sharpe_D1D10",
    "vw_mean_D1D10", "nodl_mean_D1D10",
    "ff3_alpha_D1D10", "ff4_alpha_D1D10", "ff5_alpha_D1D10",
]
ALL_CELLS = TAIL_CELLS + SPREAD_CELLS


def _client() -> Client:
    cfg = get_clickhouse_config()
    return Client(host=cfg["host"], port=int(cfg["port"]), user=cfg["user"],
                  password=cfg["password"], database=cfg["database"],
                  settings={"max_execution_time": 600})


def q(sql: str) -> pd.DataFrame:
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


def load_fund() -> pd.DataFrame:
    return pd.read_parquet(LAYOUT.data_path("fundamentals_duration.parquet"))


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
# duration recursion (parameterized over construction levers)
# --------------------------------------------------------------------------- #
def duration_recursion(roe, g, be, p, cf_floor_zero=False):
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


def _clip_cs(s):
    lo, hi = s.quantile(0.01), s.quantile(0.99)
    return s.clip(lo, hi)


# --------------------------------------------------------------------------- #
# build a variant's duration table -> (permno, sort_year, bin, dur, dur_raw)
# --------------------------------------------------------------------------- #
def build_dur_variant(funda, cf_floor_zero=False, dur_win_pooled=False,
                      be_floor_millions=None):
    f = funda.copy()
    # baseline winsorized inputs (roe/g winsorized within fyear @1/99 — A4)
    f["roe_in"] = f.groupby("fyear")["roe_raw"].transform(_clip_cs)
    f["g_in"] = f.groupby("fyear")["g_raw"].transform(_clip_cs)

    be = f["be"].to_numpy() * 1e6   # dollars, matching P
    p = f["p"].to_numpy()
    roe = f["roe_in"].to_numpy()
    g = f["g_in"].to_numpy()
    dur = duration_recursion(roe, g, be, p, cf_floor_zero)
    f["dur_raw_v"] = dur
    f["sort_year"] = f["fyear"] + 1

    if dur_win_pooled:
        # Dur winsorization POOLED across all sort years @1/99 (V6)
        f["dur_v"] = _clip_cs(f["dur_raw_v"])
    else:
        # per-sort-year @1/99 (V0/V3/V8 canonical)
        f["dur_v"] = f.groupby("sort_year")["dur_raw_v"].transform(_clip_cs)

    if be_floor_millions is not None:
        # V8: exclude tiny-BE firms (be < $1M == be < 1 in millions)
        f = f[f["be"] >= be_floor_millions].copy()

    return f[["permno", "fyear", "sort_year", "dur_raw_v", "dur_v",
              "be", "roe_in", "g_in", "p"]].copy()


def assign_bins(dur_df):
    d = dur_df.copy()
    d = d[d["sort_year"].between(1963, 2013)]
    d = d[d["dur_v"].notna() & d["p"].notna() & (d["p"] > 0)]
    d = d.sort_values("dur_v").drop_duplicates(subset=["permno", "sort_year"], keep="last")
    d["bin"] = d.groupby("sort_year")["dur_v"].rank(method="first", pct=True)
    d["bin"] = np.ceil(d["bin"] * 10).astype(int).clip(1, 10)
    return d


# --------------------------------------------------------------------------- #
# portfolio returns + alphas (mirrors compute_table2/3 in main.py)
# --------------------------------------------------------------------------- #
def portfolio_returns(panel, ret_col):
    p = panel[["month", "bin", ret_col, "me_jun"]].copy()
    # EW
    ew = p.groupby(["month", "bin"])[ret_col].mean().unstack().reindex(columns=range(1, 11))
    ew.columns = BIN_LABELS
    # VW
    has_me = p["me_jun"].notna() & (p["me_jun"] > 0)
    vw = p.loc[has_me].copy()
    vw["w"] = vw[ret_col] * vw["me_jun"]
    vwn = vw.groupby(["month", "bin"])[["w", "me_jun"]].sum()
    vw_ret = (vwn["w"] / vwn["me_jun"]).unstack().reindex(columns=range(1, 11))
    vw_ret.columns = BIN_LABELS
    # fill missing VW with EW
    vw_ret = vw_ret.where(vw_ret.notna(), ew)
    return ew, vw_ret


def align_excess(port_rets, factors):
    ff = factors.set_index("dt")["rf"]
    rf = ff.groupby(ff.index.to_period("M")).last()
    rf.index = rf.index.to_timestamp()
    aligned = port_rets.join(rf.rename("rf"), how="left")
    for c in port_rets.columns:
        aligned[c] = aligned[c] - aligned["rf"]
    return aligned.drop(columns=["rf"])


def _ols(y, X):
    import statsmodels.api as sm
    y = y.dropna()
    Xa = X.reindex(y.index).dropna()
    y = y.reindex(Xa.index)
    Xc = sm.add_constant(Xa)
    model = sm.OLS(y, Xc).fit()
    return float(model.params["const"]), float(model.params[X.columns[0]])


# --------------------------------------------------------------------------- #
# paper target + tolerance loader (for cell status)
# --------------------------------------------------------------------------- #
SIGN_EPS = 1e-9


def _sign(x):
    return 1 if x > SIGN_EPS else (-1 if x < -SIGN_EPS else 0)


def classify(paper, ours, tol_pct, zb=None):
    if paper is None or ours is None or (isinstance(ours, float) and np.isnan(ours)):
        return "missing"
    tol = tol_pct / 100.0
    if zb is not None:
        adev = abs(ours - paper)
        if adev <= zb:
            return "Match"
        mag_err = max(0.0, adev - zb) / max(zb, 1e-12)
        if _sign(paper) != _sign(ours) and _sign(paper) != 0 and _sign(ours) != 0:
            return "FAIL"
        return "Match" if mag_err <= tol else "FAIL"
    if paper == 0:
        rel = min(abs(ours) / max(tol, 1e-12), 100.0)
    else:
        rel = abs(ours - paper) / abs(paper)
    if _sign(paper) != _sign(ours) and _sign(paper) != 0 and _sign(ours) != 0:
        return "FAIL"
    return "Match" if rel <= tol else "FAIL"


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
# run one variant -> metrics dict + D10 composition
# --------------------------------------------------------------------------- #
def run_variant(name, funda, panel_binless, factors, paper, **kw):
    dur_df = build_dur_variant(funda, **kw)
    bins = assign_bins(dur_df)
    meta = bins[["permno", "sort_year", "bin", "dur_v", "dur_raw_v", "be",
                 "roe_in"]].drop_duplicates(["permno", "sort_year"])

    panel = panel_binless.merge(meta, on=["permno", "sort_year"], how="left")
    panel = panel[panel["bin"].notna()].copy()
    panel["bin"] = panel["bin"].astype(int)

    ew, vw = portfolio_returns(panel, "ret_dl")
    ew_nodl, _ = portfolio_returns(panel, "ret")
    ew_ex = align_excess(ew, factors)
    vw_ex = align_excess(vw, factors)
    nodl_ex = align_excess(ew_nodl, factors)

    res = {}
    means = ew_ex.mean() * 100.0
    for c in BIN_LABELS:
        res[f"mean_{c}"] = float(means[c])
    res["mean_D1D10"] = float(means["D1"] - means["D10"])

    nodl = nodl_ex.mean() * 100.0
    for c in BIN_LABELS:
        res[f"nodl_mean_{c}"] = float(nodl[c])
    res["nodl_mean_D1D10"] = float(nodl["D1"] - nodl["D10"])

    vwl = vw_ex.mean() * 100.0
    for c in BIN_LABELS:
        res[f"vw_mean_{c}"] = float(vwl[c])
    res["vw_mean_D1D10"] = float(vwl["D1"] - vwl["D10"])

    ff = factors.set_index("dt")
    mkt = pd.DataFrame({"mkt_rf": ff["mkt_rf"]})
    mkt.index = mkt.index.to_period("M").to_timestamp()
    for i in range(1, 11):
        c = f"D{i}"
        a, b = _ols(ew_ex[c], mkt)
        res[f"alpha_capm_{c}"] = a * 100.0
        res[f"beta_capm_{c}"] = b
    sp = (ew_ex["D1"] - ew_ex["D10"]).rename("sp")
    a_sp, b_sp = _ols(sp, mkt)
    res["alpha_capm_D1D10"] = a_sp * 100.0
    res["beta_capm_D1D10"] = b_sp

    for c in BIN_LABELS:
        s = ew_ex[c]
        res[f"sharpe_{c}"] = float(s.mean() / s.std(ddof=1)) if s.std(ddof=1) > 0 else float("nan")
    sp_s = ew_ex["D1"] - ew_ex["D10"]
    res["sharpe_D1D10"] = float(sp_s.mean() / sp_s.std(ddof=1)) if sp_s.std(ddof=1) > 0 else float("nan")

    fact_cols = {
        "ff3": ["mkt_rf", "smb", "hml"],
        "ff4": ["mkt_rf", "smb", "hml", "mom"],
        "ff5": ["mkt_rf", "smb", "hml", "rmw", "cma"],
    }
    for tag, cols in fact_cols.items():
        X = pd.DataFrame({c: ff[c] for c in cols})
        X.index = X.index.to_period("M").to_timestamp()
        for i in range(1, 11):
            res[f"{tag}_alpha_D{i}"], _ = _ols(ew_ex[f"D{i}"], X)
            res[f"{tag}_alpha_D{i}"] *= 100.0
        a, _ = _ols(sp, X)
        res[f"{tag}_alpha_D1D10"] = a * 100.0

    # D10 composition
    d10 = panel[panel["bin"] == 10]
    comp = {
        "median_me_jun": float(d10["me_jun"].median()),
        "median_be_millions": float(meta[meta["bin"] == 10]["be"].median()),
        "neg_roe_share": float((meta[meta["bin"] == 10]["roe_in"] < 0).mean()),
        "n_D10_rows": int(len(d10)),
        "n_D10_firms": int(meta[meta["bin"] == 10]["permno"].nunique()),
    }
    return res, comp


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def _status_counts(res, paper):
    n_tail_match = n_tail_fail = 0
    for cell in TAIL_CELLS:
        if cell not in paper:
            continue
        tol = paper[cell]["tolerance_pct"]
        zb = paper[cell].get("zero_band")
        st = classify(paper[cell].get("value"), res.get(cell), tol, zb)
        if st == "Match":
            n_tail_match += 1
        elif st == "FAIL":
            n_tail_fail += 1
    return n_tail_match, n_tail_fail


def main():
    funda = load_fund()
    panel = load_panel()
    factors = load_factors()
    paper = load_paper_targets()

    # strip the canonical bin/dur from panel (we re-merge variant bins)
    panel_binless = panel.drop(columns=["bin", "dur", "dur_raw"]).copy()

    variants = [
        ("V0 canonical", dict(cf_floor_zero=False, dur_win_pooled=False,
                              be_floor_millions=None)),
        ("V3 cf-floor", dict(cf_floor_zero=True, dur_win_pooled=False,
                             be_floor_millions=None)),
        ("V6 dur-pooled", dict(cf_floor_zero=False, dur_win_pooled=True,
                               be_floor_millions=None)),
        ("V8 be>=1M", dict(cf_floor_zero=False, dur_win_pooled=False,
                           be_floor_millions=1.0)),
    ]

    canonical = json.loads(LAYOUT.eval_path("metrics.json").read_text())["metrics"]
    canonical_vals = {k: (v["value"] if isinstance(v, dict) else v)
                      for k, v in canonical.items()}

    rows = []
    for name, kw in variants:
        res, comp = run_variant(name, funda, panel_binless, factors, paper, **kw)
        n_tm, n_tf = _status_counts(res, paper)
        spread_dev = res["mean_D1D10"] - 1.10
        rows.append((name, res, comp, n_tm, n_tf, spread_dev))
        print(f"[{name}] done: D9={res['mean_D9']:.3f} D10={res['mean_D10']:.3f} "
              f"spread={res['mean_D1D10']:.3f} tail Match={n_tm} FAIL={n_tf}")

    # baseline tail status (from committed metrics) for the "vs baseline" view
    base_res = canonical_vals
    base_tm, base_tf = _status_counts(base_res, paper)

    print("\n" + "=" * 120)
    print("TAIL PROBE MATRIX — D9/D10 construction variants (T2+T3 committed cells)")
    print("=" * 120)

    hdr = ["variant", "mean_D9", "mean_D10", "spread", "spread_dev",
           "nodl_D9", "nodl_D10", "vw_D10", "capm_a_D9", "capm_a_D10",
           "ff3_D9", "ff3_D10", "ff4_D9", "ff4_D10", "ff5_D9", "ff5_D10",
           "tailMatch", "tailFAIL"]
    print(" | ".join(f"{h:>11}" for h in hdr))
    for name, res, comp, n_tm, n_tf, sdev in rows:
        def g(k):
            v = res.get(k)
            return f"{v:11.3f}" if v is not None else f"{'nan':>11}"
        print(" | ".join([
            f"{name:<11}", g("mean_D9"), g("mean_D10"), g("mean_D1D10"),
            f"{sdev:11.3f}", g("nodl_mean_D9"), g("nodl_mean_D10"),
            g("vw_mean_D10"), g("alpha_capm_D9"), g("alpha_capm_D10"),
            g("ff3_alpha_D9"), g("ff3_alpha_D10"), g("ff4_alpha_D9"),
            g("ff4_alpha_D10"), g("ff5_alpha_D9"), g("ff5_alpha_D10"),
            f"{n_tm:>11d}", f"{n_tf:>11d}",
        ]))

    print("\nPaper targets: mean_D9=0.62  mean_D10=0.32  spread=1.10 "
          "ff4_alpha_D10=-0.07  ff5_alpha_D10=0.01")
    print(f"Baseline (V0 committed) tail: Match={base_tm} FAIL={base_tf}")

    # baseline (committed) values for the key tail cells, for reference
    print("\nBaseline (committed metrics.json) key tail cells:")
    for cell in ["mean_D9", "mean_D10", "mean_D1D10", "ff4_alpha_D10",
                 "ff5_alpha_D10", "ff3_alpha_D10", "alpha_capm_D10"]:
        print(f"  {cell}: {canonical_vals.get(cell):.3f}")

    # D10 composition per variant
    print("\n" + "=" * 120)
    print("D10 COMPOSITION per variant")
    print("=" * 120)
    for name, res, comp, *_ in rows:
        print(f"{name:<14} n_firms={comp['n_D10_firms']:>6d}  "
              f"median_me_jun=${comp['median_me_jun']/1e6:.1f}M  "
              f"median_BE=${comp['median_be_millions']:.1f}M  "
              f"neg_roe_share={comp['neg_roe_share']:.3f}")

    # net cell movement vs baseline for the two candidate variants (V3, V6)
    print("\n" + "=" * 120)
    print("NET CELL MOVEMENT vs V0 baseline (committed) over ALL T2+T3 cells")
    print("=" * 120)
    all_cells = [m["name"] for tbl in
                 [t for t in json.loads(
                     LAYOUT.preparations_path("tables_to_replicate.json").read_text()
                 ).get("tables", []) if t["id"] in ("T2", "T3")]
                 for m in tbl["metrics"]]
    for name, res, comp, *_ in rows:
        if name == "V0 canonical":
            continue
        gains = losses = 0
        for cell in all_cells:
            tol = paper[cell]["tolerance_pct"]
            zb = paper[cell].get("zero_band")
            st0 = classify(paper[cell].get("value"), base_res.get(cell), tol, zb)
            stv = classify(paper[cell].get("value"), res.get(cell), tol, zb)
            if st0 == stv:
                continue
            if stv == "Match" and st0 == "FAIL":
                gains += 1
            elif stv == "FAIL" and st0 == "Match":
                losses += 1
        print(f"{name:<14}: +{gains} Match-gains, -{losses} Match-losses "
              f"(net {gains - losses:+d})")

    return rows


if __name__ == "__main__":
    main()
