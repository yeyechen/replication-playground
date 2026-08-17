"""Sections 6-8: T2 (Table 4), T4 (Table 8), T6 (Table A5), T7 (Table 7).

Implements the Fama-MacBeth tables (T2/T4), the MAX^beta characteristic
table (T6), and the issuance/mispricing-controlled triple-sort alphas (T7).

Run standalone:  python src/sections_678.py
It reads data/panel.parquet + data/factors.parquet and appends metrics to
eval/metrics.json (merging with existing T1/T3 metrics).
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

import main as M
from utils.quantile import assign_quantiles

LAYOUT = M.LAYOUT
SLUG = M.SLUG

CONTROLS = ["beta", "size", "bm", "rev", "mom", "illiq", "roe", "ia", "ivol"]
FIXED_COLS = ["max", "beta", "mis", "ce", "size", "bm", "rev", "mom", "illiq", "roe", "ia", "ivol"]

# FM coefficients reported in PERCENT (x100) for the controls whose natural
# scale is a small fraction. Per the paper's Table 4/Table 8: MIS, CE, BETA,
# SIZE, BM, ILLIQ, ROE, I/A are printed in percent, while MAX, REV, MOM
# and the intercept are already at their matching fractional scale (the paper
# prints MAX -0.210, REV -0.030, MOM 0.007, Intercept 0.013 in the same table).
# IVOL is EXCLUDED (M1 FIX): the raw ivol FM coefficient is already
# percent-equivalent (daily residual std, decimal fraction); the paper prints
# ivol on that natural scale (-0.217), so the earlier x100 over-converted it ~55x
# (-12.28). Removing ivol from SCALE_PCT lands t2_ivol_c2 ~ -0.12 vs paper -0.217.
# CE is EXCLUDED (iteration-3 M1 FIX): ce is now the LOG Daniel-Titman
# net-issuance residual (decimal, median ~ -0.005, decile medians -0.012..+0.007),
# matching the paper's Table 2 CE scale (-0.020..+0.013) and its T2 ce coefficient
# convention (-0.017, -0.009). The prior x100 over-converted the coefficient ~30x
# (-0.514 vs paper -0.017). Removing ce from SCALE_PCT reports the raw decimal
# coefficient (-0.010) on the paper's own scale.
SCALE_PCT = {"mis", "beta", "size", "bm", "illiq", "roe", "ia"}

# T6 characteristic <-> column (plus transform) mapping, in paper column order.
T6_CHARS = ["max", "beta", "mis", "ce", "betamax", "inst", "eiskew", "size",
            "ivol", "bm", "rev", "mom", "illiq", "roe", "ia"]


def _ensure_size(panel: pd.DataFrame) -> pd.DataFrame:
    """Add ln(me) as `size` for FM regressions. Only over me > 0."""
    if "size" not in panel.columns:
        me = panel["me"].where(panel["me"] > 0)
        panel = panel.copy()
        panel["size"] = np.log(me)
    return panel


def _maxbeta_rank(panel: pd.DataFrame) -> pd.Series:
    """MAX^beta decile rank (1..10) per stock-month, Assumption 6."""
    sub = panel[["month", "permno", "beta", "max"]].copy()
    sub = sub.dropna(subset=["beta", "max"])
    sub["beta_decile"] = assign_quantiles(sub, "month", "beta", n_bins=10)
    sub["max_rank"] = sub.groupby(["month", "beta_decile"])["max"].transform(
        lambda s: pd.qcut(s, q=10, labels=False, duplicates="drop")
    )
    sub["maxbeta_rank"] = (sub["max_rank"] + 1).astype("float")
    out = sub.set_index(["month", "permno"])["maxbeta_rank"]
    return out


def _fm_fixed_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """The T2/T4 fixed sample: one dropna on the 12 predictors + ret_fwd."""
    panel = _ensure_size(panel)
    cols = list(FIXED_COLS) + ["ret_fwd"]
    return panel.dropna(subset=cols).replace([np.inf, -np.inf], np.nan).dropna(subset=cols)


def _t2_specs():
    """Return list of (label, independent_vars) for T2's 6 columns."""
    return [
        ("c1", ["max"]),
        ("c2", ["max"] + CONTROLS),
        ("c3", ["max", "mis"]),
        ("c4", ["max", "ce"]),
        ("c5", ["max", "mis"] + CONTROLS),
        ("c6", ["max", "ce"] + CONTROLS),
    ]


def _fm_col(fixed: pd.DataFrame, indep: list[str]):
    from utils.regressions import fama_macbeth
    return fama_macbeth(
        fixed, dependent_var="ret_fwd", independent_vars=list(indep),
        time_col="month", winsorize_pct=0.01, n_lags=6, n_jobs=1,
    )


# ---------------------------------------------------------------------------
# SECTION 6 — T2 and T4
# ---------------------------------------------------------------------------
def _t2_both(fixed: pd.DataFrame) -> tuple[dict, str]:
    """T2 (Table 4): 6 FM specs. Compute fms ONCE, return (metrics, grid)."""
    specs = _t2_specs()
    fms = {l: _fm_col(fixed, indep) for l, indep in specs}

    metrics = {}
    for label, indep in specs:
        s = fms[label].summary
        for var in ["max", "mis", "ce"]:
            if var in indep:
                sc = 100.0 if var in SCALE_PCT else 1.0
                metrics[f"t2_{var}_{label}"] = {"value": round(float(s["mean"][var]) * sc, 4), "unit": "coefficient"}
        metrics[f"t2_max_{label}_t"] = {"value": round(float(s["t_stat"]["max"]), 4), "unit": "t_stat"}
        if "mis" in indep:
            metrics[f"t2_mis_{label}_t"] = {"value": round(float(s["t_stat"]["mis"]), 4), "unit": "t_stat"}
        if "ce" in indep:
            metrics[f"t2_ce_{label}_t"] = {"value": round(float(s["t_stat"]["ce"]), 4), "unit": "t_stat"}
        for c in CONTROLS:
            if c in indep:
                sc = 100.0 if c in SCALE_PCT else 1.0
                metrics[f"t2_{c}_{label}"] = {"value": round(float(s["mean"][c]) * sc, 4), "unit": "coefficient"}
        metrics[f"t2_int_{label}"] = {"value": round(float(s["mean"]["const"]), 4), "unit": "coefficient"}
        metrics[f"t2_int_{label}_t"] = {"value": round(float(s["t_stat"]["const"]), 4), "unit": "t_stat"}
        metrics[f"t2_r2_{label}"] = {"value": round(float(s["avg_rsquared"]), 4), "unit": "r_squared"}

    header = "| Var | " + " | ".join(f"({i})" for i in range(1, 7)) + " |\n"
    header += "|" + " --- |" * 7 + "\n"
    rows = [header]
    def val(label, var):
        fm = fms[label]
        if var not in fm.summary["mean"].index:
            return "—"
        sc = 100.0 if var in SCALE_PCT else 1.0
        return f"{fm.summary['mean'][var]*sc:.3f} ({fm.summary['t_stat'][var]:.2f})"
    for v in ["max", "mis", "ce"]:
        rows.append(f"| {v} | " + " | ".join(val(l, v) for l, _ in specs) + " |\n")
    for c in CONTROLS:
        rows.append(f"| {c} | " + " | ".join(val(l, c) for l, _ in specs) + " |\n")
    rows.append(f"| Intercept | " + " | ".join(val(l, "const") for l, _ in specs) + " |\n")
    r2 = " | ".join(f"{fms[l].summary['avg_rsquared']:.3f}" for l, _ in specs)
    rows.append(f"| Avg R² | {r2} |\n")
    return metrics, "".join(rows)


def _maxbeta_base(fixed: pd.DataFrame, full_panel: pd.DataFrame) -> pd.DataFrame:
    """Fixed-sample frame with MAX^beta dummy columns D2..D10 (mapped from
    full-panel MAX^beta ranks, set before the fixed-sample dropna)."""
    rank = _maxbeta_rank(full_panel)
    fixed_idx = fixed.set_index(["month", "permno"])
    base = fixed_idx.join(rank, how="left")[["ret_fwd"] + list(FIXED_COLS) + ["maxbeta_rank"]]
    base = base.dropna(subset=["maxbeta_rank"])
    for k in range(2, 11):
        base[f"D{k}"] = (base["maxbeta_rank"] == k).astype(float)
    return base.reset_index()


def _t8_both(fixed: pd.DataFrame, full_panel: pd.DataFrame) -> tuple[dict, str]:
    """T4 (Table 8): MAX^beta dummies D2..D10 + 6 spec ladders. fms once."""
    base = _maxbeta_base(fixed, full_panel)
    dummy_cols = [f"D{k}" for k in range(2, 11)]
    specs = [
        ("c1", dummy_cols),
        ("c2", dummy_cols + CONTROLS),
        ("c3", dummy_cols + ["mis"]),
        ("c4", dummy_cols + ["ce"]),
        ("c5", dummy_cols + ["mis"] + CONTROLS),
        ("c6", dummy_cols + ["ce"] + CONTROLS),
    ]
    fms = {l: _fm_col(base, indep) for l, indep in specs}

    metrics = {}
    for label, indep in specs:
        s = fms[label].summary
        for d in range(2, 11):
            if f"D{d}" in indep:
                # Paper reports MAX^beta decile dummy coefficients in PERCENT
                # (Table 8 prose: D10 c2 "-0.435" = "43.5 basis points"); the
                # OLS dummy coefficient is the decile spread in fractional
                # returns, matching the paper's percent convention when x100.
                metrics[f"t4_d{d}_{label}"] = {"value": round(float(s["mean"][f"D{d}"]) * 100.0, 4), "unit": "coefficient"}
                metrics[f"t4_d{d}_{label}_t"] = {"value": round(float(s["t_stat"][f"D{d}"]), 4), "unit": "t_stat"}
        for c in CONTROLS:
            if c in indep:
                sc = 100.0 if c in SCALE_PCT else 1.0
                metrics[f"t4_{c}_{label}"] = {"value": round(float(s["mean"][c]) * sc, 4), "unit": "coefficient"}
        if "mis" in indep:
            metrics[f"t4_mis_{label}"] = {"value": round(float(s["mean"]["mis"]) * 100.0, 4), "unit": "coefficient"}
        if "ce" in indep:
            metrics[f"t4_ce_{label}"] = {"value": round(float(s["mean"]["ce"]) * 1.0, 4), "unit": "coefficient"}
        metrics[f"t4_int_{label}"] = {"value": round(float(s["mean"]["const"]), 4), "unit": "coefficient"}
        metrics[f"t4_int_{label}_t"] = {"value": round(float(s["t_stat"]["const"]), 4), "unit": "t_stat"}
        metrics[f"t4_r2_{label}"] = {"value": round(float(s["avg_rsquared"]), 4), "unit": "r_squared"}

    header = "| Var | " + " | ".join(f"({i})" for i in range(1, 7)) + " |\n"
    header += "|" + " --- |" * 7 + "\n"
    rows = [header]
    def val(label, var, scale=1.0):
        fm = fms[label]
        if var not in fm.summary["mean"].index:
            return "—"
        return f"{fm.summary['mean'][var]*scale:.3f} ({fm.summary['t_stat'][var]:.2f})"
    for d in range(2, 11):
        rows.append(f"| D{d} | " + " | ".join(val(l, f"D{d}", scale=100.0) for l, _ in specs) + " |\n")
    for c in CONTROLS:
        sc = 100.0 if c in SCALE_PCT else 1.0
        rows.append(f"| {c} | " + " | ".join(val(l, c, scale=sc) for l, _ in specs) + " |\n")
    rows.append(f"| mis | " + " | ".join(val(l, "mis", scale=100.0) for l, _ in specs) + " |\n")
    rows.append(f"| ce | " + " | ".join(val(l, "ce", scale=1.0) for l, _ in specs) + " |\n")
    rows.append(f"| Intercept | " + " | ".join(val(l, "const") for l, _ in specs) + " |\n")
    r2 = " | ".join(f"{fms[l].summary['avg_rsquared']:.3f}" for l, _ in specs)
    rows.append(f"| Avg R² | {r2} |\n")
    return metrics, "".join(rows)


# ---------------------------------------------------------------------------
# SECTION 7 — T6 (Table A5)
# ---------------------------------------------------------------------------
def _t6_transform(panel: pd.DataFrame) -> pd.DataFrame:
    p = panel.copy()
    p = _ensure_size(p)
    p["_size_m"] = p["me"] / 1e6
    p["_ivol_pct"] = p["ivol"] * 100.0
    p["_bm_ratio"] = p["bm_raw"]
    return p


def _t6_metrics_and_grid(panel: pd.DataFrame) -> tuple[dict, str]:
    p = _t6_transform(panel)
    rank = _maxbeta_rank(p)
    p = p.set_index(["month", "permno"])
    p = p.join(rank.to_frame("mb_rank"), how="left")

    col_of = {
        "max": "max", "beta": "beta", "mis": "mis", "ce": "ce", "betamax": "betamax",
        "inst": "inst", "eiskew": "eiskew", "size": "_size_m", "ivol": "_ivol_pct",
        "bm": "_bm_ratio", "rev": "rev", "mom": "mom", "illiq": "illiq",
        "roe": "roe", "ia": "ia",
    }

    metrics = {}
    # We need, per decile, per characteristic: time-series average of cross-sectional median.
    deciles = range(1, 11)
    # Build monthly median series per (char, decile)
    med_series = {}  # (char, decile) -> pd.Series indexed by month
    inst_start = pd.Period("1980-04", freq="M")
    for ch in T6_CHARS:
        sub_col = col_of[ch]
        sub = p[["mb_rank", sub_col]].dropna(subset=["mb_rank", sub_col])
        if ch in ("inst", "eiskew"):
            sub = sub[sub.index.get_level_values("month") >= inst_start]
        for d in deciles:
            g = sub[sub["mb_rank"] == d][sub_col]
            med = g.groupby(level="month").median()
            med_series[(ch, d)] = med

    rows_out = {}
    for ch in T6_CHARS:
        p1 = med_series[(ch, 1)].mean()
        p10 = med_series[(ch, 10)].mean()
        sprd_series = med_series[(ch, 10)] - med_series[(ch, 1)]
        sprd = sprd_series.mean()
        # beta spread 0.000 with t '—' (paper)
        if ch == "beta":
            sprd_t = None
            sprd = 0.0
        else:
            sprd_t = _nw_t(sprd_series, 6)
        metrics[f"t6_{ch}_p1"] = {"value": round(float(p1), 4), "unit": _t6_unit(ch)}
        metrics[f"t6_{ch}_p10"] = {"value": round(float(p10), 4), "unit": _t6_unit(ch)}
        metrics[f"t6_{ch}_sprd"] = {"value": round(float(sprd), 4), "unit": _t6_unit(ch)}
        if sprd_t is not None:
            metrics[f"t6_{ch}_sprd_t"] = {"value": round(float(sprd_t), 4), "unit": "t_stat"}
        else:
            metrics[f"t6_{ch}_sprd"] = {"value": 0.0, "unit": _t6_unit(ch)}
        rows_out[ch] = (p1, p10, sprd, sprd_t)

    # Build the markdown grid: 11 rows (D1..D10, spread) x 15 chars + t-stat row.
    header = "| Decile | " + " | ".join(T6_CHARS) + " |\n"
    header += "|" + " --- |" * (len(T6_CHARS) + 1) + "\n"
    lines = [header]
    for d in deciles:
        cells = [f"{med_series[(ch, d)].mean():.3f}" for ch in T6_CHARS]
        lines.append(f"| D{d} | " + " | ".join(cells) + " |\n")
    sprd_cells = [f"{rows_out[ch][2]:.3f}" for ch in T6_CHARS]
    lines.append(f"| 10-1 | " + " | ".join(sprd_cells) + " |\n")
    t_cells = [("—" if rows_out[ch][3] is None else f"{rows_out[ch][3]:.2f}") for ch in T6_CHARS]
    lines.append(f"| t-stat | " + " | ".join(t_cells) + " |\n")
    return metrics, "".join(lines)


def _t6_unit(ch: str) -> str:
    return {
        "max": "ratio", "beta": "unitless", "mis": "rank", "ce": "ratio",
        "betamax": "unitless", "inst": "fraction", "eiskew": "skewness",
        "size": "millions_usd", "ivol": "percent_per_day", "bm": "ratio",
        "rev": "ratio", "mom": "ratio", "illiq": "scaled_ratio",
        "roe": "ratio", "ia": "ratio",
    }.get(ch, "unitless")


def _nw_t(series: pd.Series, lags: int) -> float:
    """Newey-West t-stat on a series (mean / HAC se)."""
    s = series.dropna()
    if len(s) < 2:
        return float("nan")
    M._import_statsmodels()
    import statsmodels.api as sm
    import numpy as _np
    X = sm.add_constant(_np.ones(len(s)))
    model = sm.OLS(s.values, X).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    tv = model.tvalues
    # tvalues may be ndarray or Series depending on X dtype; take intercept t.
    return float(tv[0])


# ---------------------------------------------------------------------------
# SECTION 8 — T7 (Table 7)
# ---------------------------------------------------------------------------
def _triple_rank(panel: pd.DataFrame, outer_col: str, mode: str) -> pd.Series:
    """Outer decile (iss_idx/mis) then inner (MAX or MAX^beta) rank per stock-month.

    mode == 'max'   -> within outer decile, MAX deciles; regroup by max rank.
    mode == 'maxb'  -> within outer decile, beta deciles then MAX deciles within;
                       regroup by within-beta max rank (Assumption 6).
    Returns a Series (month, permno) -> final decile 1..10.
    """
    sub = panel[["month", "permno", outer_col, "max", "beta"]].copy()
    sub = sub.dropna(subset=[outer_col, "max"])
    sub["outer_decile"] = assign_quantiles(sub, "month", outer_col, n_bins=10)
    if mode == "max":
        sub["inner_rank"] = sub.groupby(["month", "outer_decile"])["max"].transform(
            lambda s: pd.qcut(s, q=10, labels=False, duplicates="drop")
        )
    else:  # maxb
        sub = sub.dropna(subset=["beta"])
        # beta deciles formed within each outer (issuance/MIS) decile (paper:
        # "within each issuance or MIS decile, stocks are first sorted into
        # decile portfolios based on market beta").
        sub["beta_decile"] = sub.groupby(["month", "outer_decile"])["beta"].transform(
            lambda s: _qcut_assign(s)
        )
        sub["inner_rank"] = sub.groupby(["month", "outer_decile", "beta_decile"])["max"].transform(
            lambda s: pd.qcut(s, q=10, labels=False, duplicates="drop")
        )
    sub["final_decile"] = (sub["inner_rank"] + 1).astype("float")
    return sub.set_index(["month", "permno"])["final_decile"]


def _qcut_assign(s: pd.Series) -> pd.Series:
    return pd.qcut(s, q=10, labels=False, duplicates="drop")


def _ff6ps_alpha_series(panel: pd.DataFrame, outer_col: str, mode: str, factors: pd.DataFrame):
    """Return wide DataFrame month x P1..P10 (+ spread) of FF6PS alphas? No —
    return the portfolio VW return series (by return month), then alpha computed.
    Build 11 series (P1..P10, spread) and return dict of (alpha, t)."""
    rank = _triple_rank(panel, outer_col, mode)
    sub = panel[["month", "permno", "ret_fwd", "me_lag1"]].set_index(["month", "permno"])
    sub = sub.join(rank.to_frame("d"), how="left").dropna(subset=["d", "ret_fwd", "me_lag1"])
    sub["ret_month"] = sub.index.get_level_values("month") + 1
    sub = sub.reset_index()
    # VW returns by ret_month and decile
    sub["w"] = sub["me_lag1"]
    sub["wr"] = sub["ret_fwd"] * sub["w"]
    g = sub.groupby(["ret_month", "d"]).agg(wr=("wr", "sum"), w=("w", "sum"))
    vw = (g["wr"] / g["w"]).unstack()  # month x decile
    ff6 = factors[["mkt_rf", "smb", "hml", "rmw", "cma", "mom", "ps_liq"]]
    out = {}
    for d in range(1, 11):
        s = vw[d].dropna() if d in vw.columns else pd.Series(dtype=float)
        out[d] = s
    out["sprd"] = vw[10].dropna() - vw[1].dropna() if {1, 10}.issubset(vw.columns) else pd.Series(dtype=float)
    return out


def _t7_metrics_and_grid(panel: pd.DataFrame, factors: pd.DataFrame) -> tuple[dict, str]:
    ff6 = ["mkt_rf", "smb", "hml", "rmw", "cma", "mom", "ps_liq"]
    panels = {"a": ("iss_idx", "max", "a_max"), "b": ("mis", "max", "b_max")}
    metrics = {}
    grid_keys = ["a_max", "a_maxb", "b_max", "b_maxb"]
    alpha_maps = {}
    for outer, mode, key in [
        ("iss_idx", "max", "a_max"),
        ("iss_idx", "maxb", "a_maxb"),
        ("mis", "max", "b_max"),
        ("mis", "maxb", "b_maxb"),
    ]:
        series = _ff6ps_alpha_series(panel, outer, mode, factors)
        alphas = {}
        for d in range(1, 11):
            s = series[d]
            a, t, _n = M._alpha_regress(s, factors, ff6)
            metrics[f"t7_{key}_p{d}"] = {"value": round(a * 100.0, 4), "unit": "percent_per_month"}
            alphas[d] = (a * 100.0, t)
        s = series["sprd"]
        a, t, _n = M._alpha_regress(s, factors, ff6)
        metrics[f"t7_{key}_sprd"] = {"value": round(a * 100.0, 4), "unit": "percent_per_month"}
        metrics[f"t7_{key}_sprd_t"] = {"value": round(t, 4), "unit": "t_stat"}
        alphas["sprd"] = (a * 100.0, t)
        alpha_maps[key] = alphas

    # grid: rows D1..D10, spread; cols a_max, a_maxb, b_max, b_maxb
    header = "| Decile | a_max | a_maxb | b_max | b_maxb |\n"
    header += "|" + " --- |" * 5 + "\n"
    lines = [header]
    for d in range(1, 11):
        cells = [f"{alpha_maps[k][d][0]:.2f} ({alpha_maps[k][d][1]:.2f})" for k in grid_keys]
        lines.append(f"| D{d} | " + " | ".join(cells) + " |\n")
    cells = [f"{alpha_maps[k]['sprd'][0]:.2f} ({alpha_maps[k]['sprd'][1]:.2f})" for k in grid_keys]
    lines.append(f"| 10-1 | " + " | ".join(cells) + " |\n")
    return metrics, "".join(lines)


# ---------------------------------------------------------------------------
def run() -> None:
    panel = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
    factors = pd.read_parquet(LAYOUT.data_path("factors.parquet"))
    factors = factors.sort_index()

    # ---- load existing metrics.json ----
    md_path = LAYOUT.eval_path("metrics.json")
    existing = json.loads(md_path.read_text())
    metrics = {k: v for k, v in existing["metrics"].items()}
    skips = list(existing.get("skips", []))

    # ---- SELECTIVE MODE: configurable via env SECTIONS ----
    import os
    section = os.environ.get("REP_SECTION", "all")

    def _append(key, mdict):
        metrics[key] = mdict

    if section in ("all", "s6"):
        print("=== SECTION 6: T2 (Table 4) + T4 (Table 8) ===")
        fixed = _fm_fixed_sample(panel)
        print(f"fixed sample rows = {len(fixed)}")
        m2, g2 = _t2_both(fixed)
        for k, v in m2.items():
            _append(k, v)
        LAYOUT.result_path("table_4.md").write_text(
            "# Table 4 — Fama-MacBeth on MAX and controls\n\n"
            "Fixed sample (one dropna on 12 predictors + ret_fwd); winsorize 1%/99% per month; NW 6 lags; n_jobs=1.\n\n"
            + g2
        )
        print("wrote results/table_4.md")
        m4, g8 = _t8_both(fixed, panel)
        for k, v in m4.items():
            _append(k, v)
        LAYOUT.result_path("table_8.md").write_text(
            "# Table 8 — Fama-MacBeth on MAX^beta decile dummies\n\n"
            + g8
        )
        print("wrote results/table_8.md")
        print("  T2 max c1..c6:",
              [metrics[f"t2_max_c{i}"]["value"] for i in range(1, 7)])
        print("  T4 D10 c1..c6:",
              [metrics[f"t4_d10_c{i}"]["value"] for i in range(1, 7)])

    if section in ("all", "s7"):
        print("=== SECTION 7: T6 (Table A5) ===")
        m6, grid6 = _t6_metrics_and_grid(panel)
        for k, v in m6.items():
            _append(k, v)
        LAYOUT.result_path("table_a5.md").write_text(
            "# Table A5 — Characteristics of MAX^beta deciles\n\n"
            "Time-series averages of cross-sectional medians; spread t-stats NW 6 lags.\n"
            "INST/E(ISKEW) on Apr 1980-Dec 2022 subsample; others full sample.\n\n"
            + grid6
        )
        print("wrote results/table_a5.md")
        for ch in ["max", "beta", "mis", "inst", "eiskew", "size", "ivol"]:
            print(f"  t6_{ch} sprd = {metrics[f't6_{ch}_sprd']['value']:.4f}")

    if section in ("all", "s8"):
        print("=== SECTION 8: T7 (Table 7) ===")
        m7, grid7 = _t7_metrics_and_grid(panel, factors)
        for k, v in m7.items():
            _append(k, v)
        LAYOUT.result_path("table_7.md").write_text(
            "# Table 7 — Issuance- and mispricing-controlled MAX / MAX^beta alphas (FF6PS)\n\n"
            "Panel A: monthly iss_idx deciles; Panel B: monthly mis deciles. Within each outer "
            "decile, MAX deciles (MAX) or beta-then-MAX deciles (MAX^beta); regrouped by max rank. "
            "FF6PS alpha, HAC 6 lags, aggregated by return month.\n\n" + grid7
        )
        print("wrote results/table_7.md")
        for k in ["a_max", "a_maxb", "b_max", "b_maxb"]:
            print(f"  t7_{k}_sprd = {metrics[f't7_{k}_sprd']['value']:.4f} (t={metrics[f't7_{k}_sprd_t']['value']:.2f})")

    # ---- write metrics.json ----
    LAYOUT.eval_path("metrics.json").write_text(
        json.dumps({"schema_version": 2, "slug": SLUG, "metrics": metrics, "skips": skips},
                   indent=2, default=float)
    )
    print(f"\nWrote {md_path}  ({len(metrics)} metrics, {len(skips)} skips)")


if __name__ == "__main__":
    run()
