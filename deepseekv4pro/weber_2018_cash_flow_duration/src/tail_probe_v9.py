"""
TAIL PROBE V9 — LOSS-FIRM-ONLY CF FLOOR (outer iteration 4, inner iteration 2).

Scratch module. Does NOT modify the canonical pipeline (main.py / panel.parquet /
metrics.json). Reuses tail_probe.py machinery; adds a GRADUATED loss-firm CF treatment.

V9 (loss-firm-only floor): in the duration recursion, floor CF_{t+s} at zero ONLY for
firms whose current (period-t) ROE_t < 0. Positive-ROE reinvesting firms keep their
legitimately-negative clean-surplus CFs (NOT floored). Cite: Weber footnote 6 terminal
value "paid out as a level perpetuity" presupposes non-negative payouts; loss firms
cannot distribute, so their clean-surplus CF = BV*(ROE - g) < 0 is economically a
negative distribution that equityholders never receive -> floored to zero.

Contrast with V3 (full CF floor at zero for ALL firms, overshoot D10 -> 0.225, spread
-> 1.343, net -6 cells). V9 is the "between no-floor and full-floor" calibration.

Reports: mean_D9/D10, spread, nodl_D9/D10, vw_mean_D10, alpha_capm_D9/D10,
ff3/ff4/ff5_alpha_D9/D10, tail-cell status vs baseline (18 D9/D10 cells), net cell
movement across all 99 T2+T3 cells, and D10 composition (median me/BE, neg-ROE share).

Writes only to results/ (appends to iteration5_experiment_matrix.md). No changes to
data/ or eval/.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

import tail_probe as tp

# --- a loss-firm-only floor variant of the recursion ----------------------- #
def duration_recursion_lossfloor(roe, g, be, p):
    """Same as tp.duration_recursion(roe,g,be,p, cf_floor_zero=False), but floors
    CF at zero ONLY for firms with current (period-t) ROE < 0.

    `roe` here is the winsorized ROE (roe_in) array; a firm is a "loss firm" if its
    entry (before the AR(1) mean reversion path) is negative.
    """
    n = roe.shape[0]
    s = np.arange(1, tp.T_HORIZON + 1, dtype=np.float64)
    ar_roe_s = np.power(tp.AR_ROE, s)
    ar_sg_s = np.power(tp.AR_SG, s)
    disc = np.power(1.0 + tp.R, s)

    roe = np.where(np.isfinite(roe), roe, tp.ROE_SS)
    g = np.where(np.isfinite(g), g, tp.SG_SS)
    be = np.where(np.isfinite(be) & (be > 0), be, 0.0)
    p = np.where(np.isfinite(p) & (p > 0), p, 0.0)

    # loss-firm mask from the CONTEMPORANEOUS roe (before mean-reversion)
    loss = roe < 0.0

    roe_all = tp.ROE_SS + ar_roe_s[None, :] * (roe[:, None] - tp.ROE_SS)
    g_all = tp.SG_SS + ar_sg_s[None, :] * (g[:, None] - tp.SG_SS)

    bv = np.empty((n, tp.T_HORIZON + 1), dtype=np.float64)
    bv[:, 0] = be
    cf_pv = np.empty((n, tp.T_HORIZON), dtype=np.float64)
    for k in range(tp.T_HORIZON):
        bv_prev = bv[:, k]
        g_k = g_all[:, k]
        roe_k = roe_all[:, k]
        bv[:, k + 1] = bv_prev * (1.0 + g_k)
        cf_k = bv_prev * (roe_k - g_k)
        cf_k = np.where(loss, np.maximum(cf_k, 0.0), cf_k)  # V9: floor only loss firms
        cf_pv[:, k] = cf_k / disc[k]

    pv_sum = cf_pv.sum(axis=1)
    weighted = (cf_pv * s[None, :]).sum(axis=1)
    terminal = (tp.T_HORIZON + (1.0 + tp.R) / tp.R) * (p - pv_sum)
    return (weighted + terminal) / p


def build_dur_v9(funda):
    """V9 duration table. Identical to tp.build_dur_variant(V0) except the recursion
    floors CF only for loss firms."""
    f = funda.copy()
    f["roe_in"] = f.groupby("fyear")["roe_raw"].transform(tp._clip_cs)
    f["g_in"] = f.groupby("fyear")["g_raw"].transform(tp._clip_cs)

    be = f["be"].to_numpy() * 1e6
    p = f["p"].to_numpy()
    roe = f["roe_in"].to_numpy()
    g = f["g_in"].to_numpy()
    dur = duration_recursion_lossfloor(roe, g, be, p)
    f["dur_raw_v"] = dur
    f["sort_year"] = f["fyear"] + 1
    f["dur_v"] = f.groupby("sort_year")["dur_raw_v"].transform(tp._clip_cs)

    return f[["permno", "fyear", "sort_year", "dur_raw_v", "dur_v",
              "be", "roe_in", "g_in", "p"]].copy()


def main():
    funda = tp.load_fund()
    panel = tp.load_panel()
    factors = tp.load_factors()
    paper = tp.load_paper_targets()

    panel_binless = panel.drop(columns=["bin", "dur", "dur_raw"]).copy()

    canonical = json.loads(tp.LAYOUT.eval_path("metrics.json").read_text())["metrics"]
    canonical_vals = {k: (v["value"] if isinstance(v, dict) else v)
                      for k, v in canonical.items()}

    # V0 baseline re-run (full reconstruction, identical to tail_probe.py)
    res0, comp0 = tp.run_variant("V0 canonical", funda, panel_binless, factors, paper,
                                 cf_floor_zero=False, dur_win_pooled=False,
                                 be_floor_millions=None)

    # V9: custom build (loss-firm-only floor), then re-use the rest of run_variant's
    # plumbing by assembling a dur_df and calling assign_bins + portfolio steps directly.
    dur_df = build_dur_v9(funda)
    bins = tp.assign_bins(dur_df)
    meta = bins[["permno", "sort_year", "bin", "dur_v", "dur_raw_v", "be",
                 "roe_in"]].drop_duplicates(["permno", "sort_year"])
    p9 = panel_binless.merge(meta, on=["permno", "sort_year"], how="left")
    p9 = p9[p9["bin"].notna()].copy()
    p9["bin"] = p9["bin"].astype(int)

    ew, vw = tp.portfolio_returns(p9, "ret_dl")
    ew_nodl, _ = tp.portfolio_returns(p9, "ret")
    ew_ex = tp.align_excess(ew, factors)
    vw_ex = tp.align_excess(vw, factors)
    nodl_ex = tp.align_excess(ew_nodl, factors)

    res9 = {}
    means = ew_ex.mean() * 100.0
    for c in tp.BIN_LABELS:
        res9[f"mean_{c}"] = float(means[c])
    res9["mean_D1D10"] = float(means["D1"] - means["D10"])

    nodl = nodl_ex.mean() * 100.0
    for c in tp.BIN_LABELS:
        res9[f"nodl_mean_{c}"] = float(nodl[c])
    res9["nodl_mean_D1D10"] = float(nodl["D1"] - nodl["D10"])

    vwl = vw_ex.mean() * 100.0
    for c in tp.BIN_LABELS:
        res9[f"vw_mean_{c}"] = float(vwl[c])
    res9["vw_mean_D1D10"] = float(vwl["D1"] - vwl["D10"])

    ff = factors.set_index("dt")
    mkt = pd.DataFrame({"mkt_rf": ff["mkt_rf"]})
    mkt.index = mkt.index.to_period("M").to_timestamp()
    for i in range(1, 11):
        c = f"D{i}"
        a, b = tp._ols(ew_ex[c], mkt)
        res9[f"alpha_capm_{c}"] = a * 100.0
        res9[f"beta_capm_{c}"] = b
    sp = (ew_ex["D1"] - ew_ex["D10"]).rename("sp")
    a_sp, b_sp = tp._ols(sp, mkt)
    res9["alpha_capm_D1D10"] = a_sp * 100.0
    res9["beta_capm_D1D10"] = b_sp

    for c in tp.BIN_LABELS:
        s = ew_ex[c]
        res9[f"sharpe_{c}"] = float(s.mean() / s.std(ddof=1)) if s.std(ddof=1) > 0 else float("nan")

    fact_cols = {
        "ff3": ["mkt_rf", "smb", "hml"],
        "ff4": ["mkt_rf", "smb", "hml", "mom"],
        "ff5": ["mkt_rf", "smb", "hml", "rmw", "cma"],
    }
    for tag, cols in fact_cols.items():
        X = pd.DataFrame({c: ff[c] for c in cols})
        X.index = X.index.to_period("M").to_timestamp()
        for i in range(1, 11):
            a, _ = tp._ols(ew_ex[f"D{i}"], X)
            res9[f"{tag}_alpha_D{i}"] = a * 100.0
        a, _ = tp._ols(sp, X)
        res9[f"{tag}_alpha_D1D10"] = a * 100.0

    d10 = p9[p9["bin"] == 10]
    comp9 = {
        "median_me_jun": float(d10["me_jun"].median()),
        "median_be_millions": float(meta[meta["bin"] == 10]["be"].median()),
        "neg_roe_share": float((meta[meta["bin"] == 10]["roe_in"] < 0).mean()),
        "n_D10_rows": int(len(d10)),
        "n_D10_firms": int(meta[meta["bin"] == 10]["permno"].nunique()),
    }

    # ---- tail status + net movement (reuse tp.classify / tp.TAIL_CELLS) ---- #
    ntm0, ntf0 = tp._status_counts(res0, paper)
    ntm9, ntf9 = tp._status_counts(res9, paper)

    all_cells = [m["name"] for tbl in
                 [t for t in json.loads(
                     tp.LAYOUT.preparations_path("tables_to_replicate.json").read_text()
                 ).get("tables", []) if t["id"] in ("T2", "T3")]
                 for m in tbl["metrics"]]

    # baseline net (V0 reconstruction vs committed — should be ~0; sanity)
    def net_mvt(base_res, res):
        gains = losses = 0
        for cell in all_cells:
            tol = paper[cell]["tolerance_pct"]
            zb = paper[cell].get("zero_band")
            st0 = tp.classify(paper[cell].get("value"), base_res.get(cell), tol, zb)
            stv = tp.classify(paper[cell].get("value"), res.get(cell), tol, zb)
            if st0 == stv:
                continue
            if stv == "Match" and st0 == "FAIL":
                gains += 1
            elif stv == "FAIL" and st0 == "Match":
                losses += 1
        return gains, losses

    g0, l0 = net_mvt(canonical_vals, res0)
    g9, l9 = net_mvt(canonical_vals, res9)

    print("=" * 118)
    print("V9 (loss-firm-only CF floor) probe")
    print("=" * 118)
    print(f"Baseline V0 reconstruction sanity: net movement vs committed = {g0 - l0:+d}")
    print()

    hdr = ["metric", "V0", "V9", "paper"]
    rows = [
        ("mean_D9", res0, res9, 0.62),
        ("mean_D10", res0, res9, 0.32),
        ("mean_D1D10", res0, res9, 1.10),
        ("nodl_mean_D9", res0, res9, 0.67),
        ("nodl_mean_D10", res0, res9, 0.47),
        ("vw_mean_D10", res0, res9, -0.04),
        ("alpha_capm_D9", res0, res9, -0.08),
        ("alpha_capm_D10", res0, res9, -0.39),
        ("ff3_alpha_D9", res0, res9, -0.08),
        ("ff3_alpha_D10", res0, res9, -0.38),
        ("ff4_alpha_D9", res0, res9, 0.18),
        ("ff4_alpha_D10", res0, res9, -0.07),
        ("ff5_alpha_D9", res0, res9, 0.14),
        ("ff5_alpha_D10", res0, res9, 0.01),
    ]
    print(" | ".join(f"{h:>20}" for h in hdr))
    for name, r0, r9, paperv in rows:
        print(" | ".join(f"{name:>20}" if h == "metric" else
                         f"{r9.get(name) if h == 'V9' else (r0.get(name) if h == 'V0' else paperv):>20.3f}"
                         for h in hdr))

    print()
    print(f"Tail-cell status (18 D9/D10 T2+T3 cells): V0 Match={ntm0} FAIL={ntf0} | "
          f"V9 Match={ntm9} FAIL={ntf9}")
    print(f"Net cell movement across all 99 T2+T3 cells (V9 vs committed): "
          f"+{g9} gains, -{l9} losses, net {g9 - l9:+d}")
    spread_dev = res9["mean_D1D10"] - 1.10
    print(f"Spread deviation V9: {res9['mean_D1D10']:.3f} vs 1.10 -> {spread_dev:+.3f} "
          f"(within +/-30% of 1.10 => band [0.77, 1.43])")

    print()
    print("D10 composition (V9):")
    print(f"  n_firms={comp9['n_D10_firms']}  median_me_jun=${comp9['median_me_jun']/1e6:.1f}M "
          f" median_BE=${comp9['median_be_millions']:.1f}M "
          f" neg_roe_share={comp9['neg_roe_share']:.3f}")

    # Determine commit bar verdict
    tail_improves = ntm9 > ntm0
    spread_ok = 0.77 <= res9["mean_D1D10"] <= 1.43
    net_ok = (g9 - l9) >= 2
    print()
    print("COMMIT BAR: ")
    print(f"  majority of tail cells improve ({ntm9}>{ntm0}): {tail_improves}")
    print(f"  spread within +/-30% of 1.10: {spread_ok} (spread={res9['mean_D1D10']:.3f})")
    print(f"  net movement >= +2: {net_ok} (net={g9 - l9:+d})")
    commit = tail_improves and spread_ok and net_ok
    print(f"  => V9 {'COMMITS' if commit else 'DOES NOT COMMIT'}")

    return res9, comp9


if __name__ == "__main__":
    main()
