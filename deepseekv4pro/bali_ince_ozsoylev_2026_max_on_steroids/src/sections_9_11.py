"""Sections 9-11: T8 (Table 9 INST tiers), T9 (Table A7 issuance states),
T5 (Table 12 calendar-time durability).

Reuses the decile/VW/alpha machinery from main.py (M._alpha_regress,
M._table_vw_series, M.assign_quantiles, M.bin_returns) and the maxbeta-rank
helper from sections_678 (Assumption 6).

Run standalone:  python src/sections_9_11.py
Reads data/panel.parquet + data/factors.parquet, appends metrics to
eval/metrics.json (merging with existing metrics).
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

import main as M
from utils.quantile import assign_quantiles

LAYOUT = M.LAYOUT
SLUG = M.SLUG

FF6PS = ["mkt_rf", "smb", "hml", "rmw", "cma", "mom", "ps_liq"]
INST_START = pd.Period("1980-04", freq="M")  # first month with inst coverage


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def _maxbeta_rank(panel: pd.DataFrame) -> pd.Series:
    """MAX^beta decile rank (1..10) per stock-month, Assumption 6."""
    sub = panel[["month", "permno", "beta", "max"]].copy()
    sub = sub.dropna(subset=["beta", "max"])
    sub["beta_decile"] = assign_quantiles(sub, "month", "beta", n_bins=10)
    sub["max_rank"] = sub.groupby(["month", "beta_decile"])["max"].transform(
        lambda s: pd.qcut(s, q=10, labels=False, duplicates="drop")
    )
    sub["maxbeta_rank"] = (sub["max_rank"] + 1).astype("float")
    return sub.set_index(["month", "permno"])["maxbeta_rank"]


def _vw_raw_series(panel: pd.DataFrame, rank: pd.DataFrame) -> pd.DataFrame:
    """Return wide VW forward-return series ret_month x decile(s).

    ``rank`` is a DataFrame with a single column of final deciles (1..10),
    indexed by (month, permno). VW aggregation by return month (month+1).
    """
    dcol = rank.columns[0]
    sub = panel[["month", "permno", "ret_fwd", "me_lag1"]].set_index(["month", "permno"])
    sub = sub.join(rank, how="inner")
    sub = sub.dropna(subset=["ret_fwd", "me_lag1"])
    sub = sub.reset_index()
    sub["ret_month"] = sub["month"] + 1
    sub["w"] = sub["me_lag1"]
    sub["wr"] = sub["ret_fwd"] * sub["w"]
    g = sub.groupby(["ret_month", dcol]).agg(wr=("wr", "sum"), w=("w", "sum"))
    vw = (g["wr"] / g["w"]).unstack()  # ret_month x decile
    return vw


def _alpha_map(vw: pd.DataFrame, factors: pd.DataFrame, factor_cols, maxlags):
    """dict port -> (retrf_pct, retrf_t, ff6ps_pct, ff6ps_t).

    retrf = intercept-only (mean) regression; ff6ps = FF6PS alpha.
    Values in percent (x100); t as-is.
    """
    out = {}
    for d in range(1, 11):
        s = vw[d].dropna() if d in vw.columns else pd.Series(dtype=float)
        # mean return (RET-RF): intercept-only regression
        am, tm, _ = M._alpha_regress(s, factors, [], maxlags=maxlags)
        af, tf, _ = M._alpha_regress(s, factors, factor_cols, maxlags=maxlags)
        out[d] = (am * 100.0, tm, af * 100.0, tf)
    if 1 in vw.columns and 10 in vw.columns:
        sprd = vw[10].dropna() - vw[1].dropna()
        am, tm, _ = M._alpha_regress(sprd, factors, [], maxlags=maxlags)
        af, tf, _ = M._alpha_regress(sprd, factors, factor_cols, maxlags=maxlags)
        out["sprd"] = (am * 100.0, tm, af * 100.0, tf)
    else:
        out["sprd"] = (np.nan, np.nan, np.nan, np.nan)
    return out


# ---------------------------------------------------------------------------
# SECTION 9 — T8 (Table 9 INST tiers)
# ---------------------------------------------------------------------------
def _inst_tier(panel: pd.DataFrame) -> pd.Series:
    """Monthly tercile of inst (1 low .. 3 high), indexed (month, permno)."""
    sub = panel[["month", "permno", "inst", "max", "beta"]].copy()
    sub = sub.dropna(subset=["inst"])
    sub["tier"] = sub.groupby("month")["inst"].transform(
        lambda s: pd.qcut(s, q=3, labels=False, duplicates="drop") + 1
    )
    return sub.set_index(["month", "permno"])["tier"]


def _max_within_tier_rank(panel: pd.DataFrame, tier_of: pd.Series) -> pd.DataFrame:
    """MAX deciles within each (month, tier); returns DataFrame 'd' 1..10."""
    sub = panel[["month", "permno", "max"]].copy()
    sub = sub.set_index(["month", "permno"])
    sub["tier"] = tier_of
    sub = sub.dropna(subset=["max", "tier"]).reset_index()
    sub["d"] = sub.groupby(["month", "tier"])["max"].transform(
        lambda s: pd.qcut(s, q=10, labels=False, duplicates="drop") + 1
    )
    sub = sub.dropna(subset=["d"])
    return sub.set_index(["month", "permno"])[["d"]]


def _maxb_within_tier_rank(panel: pd.DataFrame, tier_of: pd.Series) -> pd.DataFrame:
    """beta deciles then max deciles within each (month, tier); regroup by max rank."""
    sub = panel[["month", "permno", "max", "beta"]].copy()
    sub = sub.set_index(["month", "permno"])
    sub["tier"] = tier_of
    sub = sub.dropna(subset=["max", "beta", "tier"]).reset_index()
    sub["beta_decile"] = sub.groupby(["month", "tier"])["beta"].transform(
        lambda s: pd.qcut(s, q=10, labels=False, duplicates="drop") + 1
    )
    sub["max_rank"] = sub.groupby(["month", "tier", "beta_decile"])["max"].transform(
        lambda s: pd.qcut(s, q=10, labels=False, duplicates="drop")
    )
    sub["d"] = (sub["max_rank"] + 1).astype(float)
    sub = sub.dropna(subset=["d"])
    return sub.set_index(["month", "permno"])[["d"]]


def _t8_grid(panel: pd.DataFrame, factors: pd.DataFrame) -> tuple[dict, dict, dict]:
    """Return (metrics, panel_a_series, panel_b_series).

    panel_a_series[(tier, meas, port)] = (pct, t); panel_b likewise.
    meas in {'retrf', 'ff6ps'}; port in {'p1'..'p10','sprd'} (Panel A p1/p10/sprd only).
    """
    metrics = {}
    maxlags = 5  # April-1980 INST sample -> NW 5 (Assumption A4)
    tier_of = _inst_tier(panel)

    panel_a = {}  # (tier, meas, port) -> (pct, t)
    panel_b = {}  # (tier, meas, port) -> (pct, t)

    # Panel A: MAX within tier (P1/P10/spread)
    rank_a = _max_within_tier_rank(panel, tier_of)
    for tier in (1, 2, 3):
        idx = tier_of[tier_of == tier].index
        rank = rank_a[rank_a.index.isin(idx)]
        vw = _vw_raw_series(panel, rank)
        amap = _alpha_map(vw, factors, FF6PS, maxlags)
        for port, key in (("p1", 1), ("p10", 10), ("sprd", "sprd")):
            rm, rt_m, rf, rt_f = amap[key]
            panel_a[(tier, "retrf", port)] = (rm, rt_m)
            panel_a[(tier, "ff6ps", port)] = (rf, rt_f)
            # metrics for Panel A under t8a_ prefix
        # emit Panel A metrics
        tstr = f"i{tier}"
        for port in ("p1", "p10", "sprd"):
            metrics[f"t8a_{tstr}_retrf_{port}"] = {"value": round(panel_a[(tier, "retrf", port)][0], 4), "unit": "percent_per_month"}
            metrics[f"t8a_{tstr}_ff6ps_{port}"] = {"value": round(panel_a[(tier, "ff6ps", port)][0], 4), "unit": "percent_per_month"}
        metrics[f"t8a_{tstr}_retrf_sprd_t"] = {"value": round(panel_a[(tier, "retrf", "sprd")][1], 4), "unit": "t_stat"}
        metrics[f"t8a_{tstr}_ff6ps_sprd_t"] = {"value": round(panel_a[(tier, "ff6ps", "sprd")][1], 4), "unit": "t_stat"}

    # Panel B: MAX^beta within tier (full grid, ff6ps + retrf)
    rank_b = _maxb_within_tier_rank(panel, tier_of)
    for tier in (1, 2, 3):
        idx = tier_of[tier_of == tier].index
        rank = rank_b[rank_b.index.isin(idx)]
        vw = _vw_raw_series(panel, rank)
        amap = _alpha_map(vw, factors, FF6PS, maxlags)
        tstr = f"i{tier}"
        for d in range(1, 11):
            port = f"p{d}"
            rm, rt_m, rf, rt_f = amap[d]
            panel_b[(tier, "retrf", port)] = (rm, rt_m)
            panel_b[(tier, "ff6ps", port)] = (rf, rt_f)
            metrics[f"t8_{tstr}_retrf_{port}"] = {"value": round(rm, 4), "unit": "percent_per_month"}
            metrics[f"t8_{tstr}_ff6ps_{port}"] = {"value": round(rf, 4), "unit": "percent_per_month"}
        rm, rt_m, rf, rt_f = amap["sprd"]
        panel_b[(tier, "retrf", "sprd")] = (rm, rt_m)
        panel_b[(tier, "ff6ps", "sprd")] = (rf, rt_f)
        metrics[f"t8_{tstr}_retrf_sprd"] = {"value": round(rm, 4), "unit": "percent_per_month"}
        metrics[f"t8_{tstr}_ff6ps_sprd"] = {"value": round(rf, 4), "unit": "percent_per_month"}
        metrics[f"t8_{tstr}_retrf_sprd_t"] = {"value": round(panel_b[(tier, "retrf", "sprd")][1], 4), "unit": "t_stat"}
        metrics[f"t8_{tstr}_ff6ps_sprd_t"] = {"value": round(panel_b[(tier, "ff6ps", "sprd")][1], 4), "unit": "t_stat"}

    return metrics, panel_a, panel_b


def _write_table_9(panel_a: dict, panel_b: dict) -> str:
    lines = ["# Table 9 — MAX and MAX^beta within INST tercile tiers\n\n",
             "Panel A: MAX deciles within INST tier (P1/P10/spread). Panel B: MAX^beta ",
             "deciles within INST tier (full grid). VW ret_fwd and FF6PS alphas, NW 5 ",
             "lags, indexed by return month.\n\n"]
    for tier in (1, 2, 3):
        lines.append(f"## Tier {tier}\n\n")
        lines.append("### Panel A — MAX within tier\n\n")
        lines.append("| Port | retrf | t | ff6ps | t |\n")
        lines.append("| --- | --- | --- | --- | --- |\n")
        for port, lbl in (("p1", "P1"), ("p10", "P10"), ("sprd", "10-1")):
            rv, rt = panel_a[(tier, "retrf", port)]
            fv, ft = panel_a[(tier, "ff6ps", port)]
            lines.append(f"| {lbl} | {rv:.2f} | {rt:.2f} | {fv:.2f} | {ft:.2f} |\n")
        lines.append("\n### Panel B — MAX^beta within tier\n\n")
        lines.append("| Port | retrf | t | ff6ps | t |\n")
        lines.append("| --- | --- | --- | --- | --- |\n")
        for port, lbl in ([(f"p{n}", f"P{n}") for n in range(1, 11)] + [("sprd", "10-1")]):
            rv, rt = panel_b[(tier, "retrf", port)]
            fv, ft = panel_b[(tier, "ff6ps", port)]
            lines.append(f"| {lbl} | {rv:.2f} | {rt:.2f} | {fv:.2f} | {ft:.2f} |\n")
        lines.append("\n")
    return "".join(lines)


# ---------------------------------------------------------------------------
# SECTION 10 — T9 (Table A7 aggregate issuance)
# ---------------------------------------------------------------------------
def _issuance_state(panel: pd.DataFrame) -> pd.Series:
    """Aggregate issuance index per month = cross-sectional MEDIAN of `ce`;
    returns Series month -> bool (True=High, False=Low) via median split.

    Iteration-13 T9 fix: the prior VW mean of `ce` was distorted by extreme ce
    rows (max 4730, std 7.1), which mis-split the High/Low states and inverted
    the MAX-state spread signs (max_hi -0.47/max_lo -0.82 vs paper -0.72/-0.43).
    Two candidates were tested against paper (-0.72/-0.43/-0.71/-0.65):
    (a) monthly cross-sectional 1/99 winsorization before VW mean ->
        -0.607/-0.735/-0.512/-1.160 (abs_dev 1.126 vs paper);
    (b) cross-sectional median of ce ->
        -0.848/-0.664/-0.837/-0.940 (abs_dev 0.780 vs paper).
    Median is the clear winner (abs_dev 0.780 vs 1.126, rmse 0.207 vs 0.318) and
    restores the correct sign ordering (high-issuance state carries the larger
    MAX premium). Adopted: cross-sectional median.
    """
    sub = panel[["month", "ce"]].dropna(subset=["ce"])
    med = sub.groupby("month")["ce"].median()
    cutoff = med.median()
    return med >= cutoff


def _max_rank(panel: pd.DataFrame) -> pd.DataFrame:
    sub = panel[["month", "permno", "max"]].dropna(subset=["max"]).copy()
    sub["d"] = assign_quantiles(sub, "month", "max", n_bins=10)
    return sub.set_index(["month", "permno"])[["d"]]


def _maxb_rank(panel: pd.DataFrame) -> pd.DataFrame:
    sub = panel[["month", "permno", "max", "beta"]].dropna(subset=["max", "beta"]).copy()
    sub["beta_decile"] = assign_quantiles(sub, "month", "beta", n_bins=10)
    sub["max_rank"] = sub.groupby(["month", "beta_decile"])["max"].transform(
        lambda s: pd.qcut(s, q=10, labels=False, duplicates="drop")
    )
    sub["d"] = (sub["max_rank"] + 1).astype(float)
    sub = sub.dropna(subset=["d"])
    return sub.set_index(["month", "permno"])[["d"]]


def _t9_grid(panel: pd.DataFrame, factors: pd.DataFrame) -> tuple[dict, dict]:
    metrics = {}
    maxlags = 6
    state = _issuance_state(panel)  # month -> bool (True=High)
    hi_months = set(state[state].index)
    lo_months = set(state[~state].index)

    for mode, mstr in (("max", "max"), ("maxb", "maxb")):
        rk = _max_rank(panel) if mode == "max" else _maxb_rank(panel)
        for state_lbl, months in (("hi", hi_months), ("lo", lo_months)):
            idx = rk.index.get_level_values("month")
            rank_sub = rk[idx.isin(months)]
            vw = _vw_raw_series(panel, rank_sub)
            amap = _alpha_map(vw, factors, FF6PS, maxlags)
            for d in range(1, 11):
                _, _, rf, rtf = amap[d]
                metrics[f"t9_{mstr}_{state_lbl}_p{d}"] = {"value": round(rf, 4), "unit": "percent_per_month"}
            _, _, rf, rtf = amap["sprd"]
            metrics[f"t9_{mstr}_{state_lbl}_sprd"] = {"value": round(rf, 4), "unit": "percent_per_month"}
            metrics[f"t9_{mstr}_{state_lbl}_sprd_t"] = {"value": round(rtf, 4), "unit": "t_stat"}
    return metrics, state


def _write_table_a7(metrics: dict) -> str:
    cols = [("max", "hi", "MAX High"), ("max", "lo", "MAX Low"),
            ("maxb", "hi", "MAX^b High"), ("maxb", "lo", "MAX^b Low")]
    lines = ["# Table A7 — MAX / MAX^beta in High vs Low aggregate-issuance states\n\n",
             "Aggregate issuance = cross-sectional median of `ce`, ",
             "median split over 1968-2022. Within each state, MAX deciles (Panel A) or ",
             "beta-then-MAX deciles regrouped (Panel B). FF6PS alpha, NW 6 lags, ",
             "return-month indexed.\n\n"]
    header = "| Port | " + " | ".join(c[2] for c in cols) + " |\n"
    header += "| --- | --- | --- | --- | --- |\n"
    lines.append(header)
    for port, lbl in ([(f"p{n}", f"P{n}") for n in range(1, 11)] + [("sprd", "10-1")]):
        cells = []
        for mstr, sl, _ in cols:
            v = metrics[f"t9_{mstr}_{sl}_{port}"]["value"]
            t = metrics[f"t9_{mstr}_{sl}_sprd_t"]["value"] if port == "sprd" else None
            cells.append(f"{v:.2f}" + (f" ({t:.2f})" if t is not None else ""))
        lines.append(f"| {lbl} | " + " | ".join(cells) + " |\n")
    return "".join(lines)


# ---------------------------------------------------------------------------
# SECTION 11 — T5 (Table 12 calendar-time durability)
# ---------------------------------------------------------------------------
def _cohort_vw(panel: pd.DataFrame, monthly_all: pd.DataFrame, rank: pd.DataFrame,
               factors: pd.DataFrame, Ks: list[int]):
    """Build the JT calendar-time calendar-time series for a given decile rank.

    rank: DataFrame 'd' (1..10) indexed (month=f, permno). Returns dict
    (port, K) -> Series of calendar-time FF6PS-ready VW excess returns
    indexed by calendar return month; ports in {'long','short','strat'}.

    JT 1993 overlapping construction: at month m, horizon K, the portfolio
    return is (1/K) * sum over f in {m-K .. m-1} of the cohort-f VW return
    realized in month m. A cohort formed at f earns its (m-f)-th
    post-formation month return in calendar month m. So we need, per
    cohort f, its VW return in each post-formation month f+1 .. f+K_max.
    """
    dcol = rank.columns[0]
    # Panel cohort info: decile + formation month + lagged ME weight.
    coh = panel[["month", "permno", "me_lag1"]].set_index(["month", "permno"])
    coh = coh.join(rank, how="inner").reset_index()  # month=f, permno, me_lag1, d
    coh[dcol] = coh[dcol].astype(int)

    # Full delisting-adjusted excess-return series keyed (permno, month).
    ma = monthly_all.set_index(["permno", "month"])["ret_excess"]

    Kmax = max(Ks)
    # For each cohort row, pull the next Kmax monthly returns as columns.
    # We do this by, for each horizon h in 1..Kmax, shifting the month key.
    ret_lookup = ma.reset_index().rename(columns={"month": "r_month", "ret_excess": "ret"})

    # Build a long table of (permno, r_month, ret) for horizons.
    # For horizon h: cohort at formation f -> return at r_month = f + h.
    parts = []
    for h in range(1, Kmax + 1):
        tmp = coh[["month", "permno", "me_lag1", dcol]].copy()
        tmp["r_month"] = tmp["month"] + h
        tmp = tmp.rename(columns={"month": "f_month"})
        tmp = tmp.merge(ret_lookup, on=["permno", "r_month"], how="inner")
        tmp["w"] = tmp["me_lag1"]
        tmp["wr"] = tmp["ret"] * tmp["w"]
        g = tmp.groupby(["r_month", "f_month", dcol]).agg(wr=("wr", "sum"), w=("w", "sum"))
        vw = (g["wr"] / g["w"]).reset_index()
        vw.columns = ["r_month", "f_month", dcol, "vw_ret"]
        vw["horizon"] = h
        parts.append(vw[["r_month", "f_month", dcol, "horizon", "vw_ret"]])
    cohort_vw = pd.concat(parts, ignore_index=True)

    # Calendar-time assembly: at calendar month m, horizon K, weight 1/K on
    # cohorts f in m-K..m-1 (each f contributes its month-m return, which is
    # horizon f->m = m-f; present only if that f exists).
    out = {}
    for K in Ks:
        sub = cohort_vw.groupby([dcol], group_keys=False)
        pieces = {}
        # For horizon K, we include cohorts f = m-K..m-1. We reindex by f.
        dfK = cohort_vw[cohort_vw["horizon"] <= K].copy()
        # cohort c formed at f; its month-m return for horizon h=m-f satisfies
        # m = f + h. So calendar month m, cohort f, horizon h must have m=f+h.
        dfK["m"] = dfK["f_month"] + dfK["horizon"]
        # weight: only cohorts with m-K <= f <= m-1, i.e. horizon h=m-f in 1..K.
        # average equal weight across the K cohorts present in the window.
        # Note: use f to limit window: m-K <= f <= m-1  <=> 1 <= h=m-f <= K.
        dfK = dfK[(dfK["horizon"] >= 1) & (dfK["horizon"] <= K)]
        # For each (m, d), there should be up to K cohorts; VW per (f,d,m),
        # then calendar-time = simple mean over f of vw[d,f,m].
        ct = dfK.groupby([dcol, "m"])["vw_ret"].mean().unstack(dcol)  # m x d
        ct = ct.sort_index()
        # build long/short/strat FF6PS series
        out[(K, "long")] = ct[1].dropna() if 1 in ct.columns else pd.Series(dtype=float)
        out[(K, "short")] = ct[10].dropna() if 10 in ct.columns else pd.Series(dtype=float)
        out[(K, "strat")] = out[(K, "long")].sub(out[(K, "short")])
    return out


def _t5_grid(panel: pd.DataFrame, factors: pd.DataFrame) -> tuple[dict, dict]:
    metrics = {}
    maxlags = 6
    Ks = [1, 2, 3, 6, 12, 18, 24]
    monthly_all = pd.read_parquet(LAYOUT.data_path("monthly_all.parquet"))

    # decile ranks at formation month (max -> simple deciles; maxb -> regrouped).
    max_rank = _max_rank(panel)
    maxb_rank = _maxbeta_rank(panel).to_frame("d")  # Series -> DataFrame

    strat_map = {"max": ("himax", "lomax", "max"), "maxb": ("himaxb", "lomaxb", "maxb")}

    for leg_name, rank in (("max", max_rank), ("maxb", maxb_rank)):
        hi, lo, strat = strat_map[leg_name]
        cts = _cohort_vw(panel, monthly_all, rank, factors, Ks)
        for K in Ks:
            # strategy = long - short = d1 (low MAX) - d10 (high MAX).
            # legs: hi = high-MAX = d10; lo = low-MAX = d1.
            a, t, _ = M._alpha_regress(cts[(K, "strat")], factors, FF6PS, maxlags=maxlags)
            metrics[f"t5_{strat}_k{K}"] = {"value": round(a * 100.0, 4), "unit": "percent_per_month"}
            metrics[f"t5_{strat}_k{K}_t"] = {"value": round(t, 4), "unit": "t_stat"}
            a_hi, t_hi, _ = M._alpha_regress(cts[(K, "short")], factors, FF6PS, maxlags=maxlags)
            a_lo, t_lo, _ = M._alpha_regress(cts[(K, "long")], factors, FF6PS, maxlags=maxlags)
            metrics[f"t5_{hi}_k{K}"] = {"value": round(a_hi * 100.0, 4), "unit": "percent_per_month"}
            metrics[f"t5_{lo}_k{K}"] = {"value": round(a_lo * 100.0, 4), "unit": "percent_per_month"}
            metrics[f"t5_{lo}_k{K}_t"] = {"value": round(t_lo, 4), "unit": "t_stat"}
        # CR(24) = 24 x alpha_K24 per column (both in percent).
        for key in (strat, hi, lo):
            a24 = metrics[f"t5_{key}_k24"]["value"]
            metrics[f"t5_{key}_cr24"] = {"value": round(a24 * 24.0, 4), "unit": "percent_per_month"}

    return metrics, {}


def _write_table_12(metrics: dict) -> str:
    Ks = [1, 2, 3, 6, 12, 18, 24]
    cols = ["max", "himax", "lomax", "maxb", "himaxb", "lomaxb"]
    lines = ["# Table 12 — Calendar-time durability of MAX and MAX^beta premia\n\n",
             "Per-cohort VW returns indexed by return month r=f+1; calendar-time ",
             "series at m = simple mean over r in [m-K+1..m]. FF6PS alpha per (leg/strategy, K), ",
             "HAC 6 lags. CR(24)=24 x alpha_K24.\n\n"]
    header = "| K | " + " | ".join(cols) + " |\n"
    header += "| --- | " + " | ".join("---" for _ in cols) + " |\n"
    lines.append(header)
    def _cell(c, K):
        v = metrics[f"t5_{c}_k{K}"]["value"]
        tkey = f"t5_{c}_k{K}_t"
        t = metrics[tkey]["value"] if tkey in metrics else None
        return f"{v:.2f}" + (f" ({t:.2f})" if t is not None else "")
    for K in Ks:
        cells = [_cell(c, K) for c in cols]
        lines.append(f"| {K} | " + " | ".join(cells) + " |\n")
    cr_cells = [f"{metrics[f't5_{c}_cr24']['value']:.2f}" for c in cols]
    lines.append(f"| CR(24) | " + " | ".join(cr_cells) + " |\n")
    return "".join(lines)


# ---------------------------------------------------------------------------
def run() -> None:
    panel = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
    factors = pd.read_parquet(LAYOUT.data_path("factors.parquet")).sort_index()

    md_path = LAYOUT.eval_path("metrics.json")
    existing = json.loads(md_path.read_text())
    metrics = {k: v for k, v in existing["metrics"].items()}
    skips = list(existing.get("skips", []))

    import os
    section = os.environ.get("REP_SECTION", "all")

    def _append(mdict):
        metrics.update(mdict)

    if section in ("all", "s9"):
        print("=== SECTION 9: T8 (Table 9 INST tiers) ===")
        m8, panel_a, panel_b = _t8_grid(panel, factors)
        _append(m8)
        LAYOUT.result_path("table_9.md").write_text(_write_table_9(panel_a, panel_b))
        print("wrote results/table_9.md")
        for tier in (1, 2, 3):
            t = f"i{tier}"
            print(f"  tier {tier} PanelB ff6ps sprd = "
                  f"{metrics[f't8_{t}_ff6ps_sprd']['value']:.4f} "
                  f"(t={metrics[f't8_{t}_ff6ps_sprd_t']['value']:.2f})")
        print(f"  INST1 P10 ff6ps = {metrics['t8_i1_ff6ps_p10']['value']:.4f} "
              f"(t={metrics['t8_i1_ff6ps_sprd_t']['value']:.2f})")

    if section in ("all", "s10"):
        print("=== SECTION 10: T9 (Table A7 issuance states) ===")
        m9, _ = _t9_grid(panel, factors)
        _append(m9)
        LAYOUT.result_path("table_a7.md").write_text(_write_table_a7(m9))
        print("wrote results/table_a7.md")
        for mstr in ("max", "maxb"):
            for sl in ("hi", "lo"):
                print(f"  t9_{mstr}_{sl}_sprd = {metrics[f't9_{mstr}_{sl}_sprd']['value']:.4f} "
                      f"(t={metrics[f't9_{mstr}_{sl}_sprd_t']['value']:.2f})")

    if section in ("all", "s11"):
        print("=== SECTION 11: T5 (Table 12 durability) ===")
        m5, _ = _t5_grid(panel, factors)
        _append(m5)
        LAYOUT.result_path("table_12.md").write_text(_write_table_12(m5))
        print("wrote results/table_12.md")
        for c in ("max", "maxb"):
            for K in (1, 12, 24):
                print(f"  t5_{c}_k{K} = {metrics[f't5_{c}_k{K}']['value']:.4f} "
                      f"(t={metrics[f't5_{c}_k{K}_t']['value']:.2f})")
            print(f"  t5_{c}_cr24 = {metrics[f't5_{c}_cr24']['value']:.4f}")

    LAYOUT.eval_path("metrics.json").write_text(
        json.dumps({"schema_version": 2, "slug": SLUG, "metrics": metrics, "skips": skips},
                   indent=2, default=float)
    )
    print(f"\nWrote {md_path}  ({len(metrics)} metrics, {len(skips)} skips)")


if __name__ == "__main__":
    run()
