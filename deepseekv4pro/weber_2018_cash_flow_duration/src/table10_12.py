"""
Tables 10, 11, 12 for Weber (2018) — RIOR (residual institutional ownership)
double sorts (claim C5, "short-sale constraints").

Table 10: 25 portfolios = duration quintiles x residual institutional ownership
  quintiles (independent sorts), June t = 1981..2013, EW delisting-adjusted monthly
  excess returns July t..June t+1. Metrics: means + OLS SEs per cell.

Table 11: FF3 alphas of 9 portfolios (duration tertiles x RIOR tertiles), split
  first into SMALL/LARGE baskets (median June ME within the screened cross-section).

Table 12: FF3 alphas of 9 portfolios (duration tertiles x RIOR tertiles), split
  first into GROWTH/VALUE baskets (median BM = BE(FYE t-1)/ME(Dec t-1)).

Sample: stocks above the 20th size-percentile June-t screen (breakpoint variant
  selected in Part A2 — default = the data-favored variant), June 1981..2013.

RIOR (Eq. 7, paper L1991-1995): for each sort year t,
    logit(IOR) = a + b1 log(ME) + b2 log(ME)^2 + RIOR,
  with IOR floored at 0.0001 / capped at 0.9999 BEFORE the logit, IOR measured at
  December t-1 (most recent 13F quarter-end <= Dec 31 t-1, 8-quarter staleness ->
  zero), and ME = June-t market equity (the sorting-year size, dollars). RIOR is the
  OLS residual of this cross-sectional regression.

Baseline V0 pipeline (T2-T6) is UNTOUCHED. This module reuses the T1 machinery for
the June cross-section inputs and reuses panel.parquet for the delisting-adjusted
monthly returns (July t..June t+1), joining on (permno, sort_year=t).
"""
from __future__ import annotations

import json
import numpy as np
import pandas as pd

from utils.paths import paper_layout

SLUG = "weber_2018_attempt2_deepseek"
LAYOUT = paper_layout(SLUG)

T10_START = 1981   # first sort year (June)
T10_END = 2013     # last sort year (33 years)

SHORT_NAMES = {
    # T10 duration columns
    "D1": "D1", "D2": "D2", "D3": "D3", "D4": "D4", "D5": "D5", "D1D5": "D1D5",
}


def _latest_ior_by_dec(ior: pd.DataFrame):
    """Map each sort year t to the IOR at the most recent 13F quarter-end
    <= Dec 31 of year t-1 (six-month lag), 8-quarter staleness -> zero (absent from
    13F). Returns (permno, t, ior_dec)."""
    ior = ior.copy()
    ior["permno"] = ior["permno"].astype("float64")
    ior["y"] = ior["rdate"].dt.year
    frames = {}
    for t in range(T10_START, T10_END + 1):
        cutoff = pd.Timestamp(year=t - 1, month=12, day=31)
        cutoff_8q = cutoff - pd.DateOffset(months=24)
        sub = ior[(ior["rdate"] <= cutoff) & (ior["rdate"] >= cutoff_8q)]
        latest = sub.sort_values("rdate").groupby("permno")["ior"].last().rename("ior_dec")
        latest.index = latest.index.astype("float64")
        latest = latest.to_frame().assign(t=t).reset_index()
        frames[t] = latest
    return pd.concat(frames.values(), ignore_index=True)


def load_t10_cross_section(bp_variant: str = "nyse"):
    """Build the June-t 1981..2013 size-screened cross-section with Dur, BM, ME,
    IOR (Dec t-1), and RIOR."""
    import table1
    cs, bp_nyse, bp_all, _, ior_raw = table1._load_t1_inputs()

    # breakpoint variant
    bp = bp_nyse if bp_variant == "nyse" else bp_all
    cs = cs.merge(bp, on="t", how="left")
    cs = cs[cs["me_jun"] > cs["bp20"]].copy()

    # restrict to sort years 1981..2013 (T1 spans 1981..2014)
    cs = cs[cs["t"].between(T10_START, T10_END)].copy()

    # IOR at Dec t-1 (six-month lag) for the RIOR sort. Absent-from-13F -> IOR 0.
    ior_dec_by_t = _latest_ior_by_dec(ior_raw)
    cs = cs.merge(ior_dec_by_t, on=["permno", "t"], how="left")
    cs["ior_dec"] = cs["ior_dec"].fillna(0.0)

    # floor/cap IOR before logit (L1999)
    cs["ior_capped"] = cs["ior_dec"].clip(0.0001, 0.9999)
    cs["logit_ior"] = np.log(cs["ior_capped"] / (1.0 - cs["ior_capped"]))

    # cross-sectional RIOR regression per sort year t: logit(IOR) on log(ME) + log(ME)^2
    cs["log_me"] = np.log(cs["me_jun"].clip(lower=1e-9))
    cs["log_me2"] = cs["log_me"] ** 2
    rior_parts = []
    for t, g in cs.groupby("t"):
        g = g.dropna(subset=["logit_ior", "log_me", "log_me2"])
        if len(g) < 10:
            rior_parts.append(g.assign(rior=np.nan))
            continue
        X = np.column_stack([np.ones(len(g)), g["log_me"].to_numpy(),
                             g["log_me2"].to_numpy()])
        y = g["logit_ior"].to_numpy()
        beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ beta
        rior_parts.append(g.assign(rior=resid))
    cs = pd.concat(rior_parts, ignore_index=True)

    # winsorize Dur within the screened June-t cross-section (A4), and select columns
    def _clip_cs(s):
        lo, hi = s.quantile(0.01), s.quantile(0.99)
        return s.clip(lo, hi)
    cs["dur_q"] = cs.groupby("t")["dur"].transform(_clip_cs)

    # BM for T12 baskets is at Dec t-1 (already computed: bm = be / me_dec_m)
    return cs


def _load_return_panel():
    """The delisting-adjusted monthly returns by (permno, sort_year, month)."""
    p = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
    p["month"] = pd.to_datetime(p["month"])
    p["date"] = pd.to_datetime(p["date"])
    return p


def _load_factors():
    from clickhouse_driver import Client
    from utils.env import get_clickhouse_config
    cfg = get_clickhouse_config()
    c = Client(host=cfg["host"], port=int(cfg["port"]), user=cfg["user"],
               password=cfg["password"], database=cfg["database"],
               settings={"max_execution_time": 600})
    sql = (LAYOUT.src_path("sql") / "ff_factors.sql").read_text()
    data, colspec = c.execute(sql, with_column_types=True)
    df = pd.DataFrame(data, columns=[x[0] for x in colspec])
    df["dt"] = pd.to_datetime(df["dt"])
    return df.sort_values("dt").reset_index(drop=True)


def _assign_quintile(cs, col):
    """Independent quintiles (1..5) of `col` within each sort year t."""
    out = cs.copy()
    out["_q"] = out.groupby("t")[col].rank(method="first", pct=True)
    out["_q"] = np.ceil(out["_q"] * 5).astype(int).clip(1, 5)
    return out["_q"]


def _assign_tertile(cs, col):
    out = cs.copy()
    out["_q"] = out.groupby("t")[col].rank(method="first", pct=True)
    out["_q"] = np.ceil(out["_q"] * 3).astype(int).clip(1, 3)
    return out["_q"]


def _assign_tertile_within(cs, col, group_col):
    """Tertile of `col` formed WITHIN each `group_col` bin (paper's conditional
    double-sort: "within each bin I sort stocks into tertiles based on duration"),
    where quantiles are taken within each (group_col, sort-year t) cross-section."""
    out = cs.copy()
    out["_q"] = out.groupby([group_col, "t"])[col].rank(method="first", pct=True)
    out["_q"] = np.ceil(out["_q"] * 3).astype(int).clip(1, 3)
    return out["_q"]


def _medians(cs, col):
    """Median of `col` within each sort year t (for size/BM baskets)."""
    return cs.groupby("t")[col].median().rename("med")


def _join_returns(signals, panel):
    """Attach July t..June t+1 delisting-adjusted returns to each (permno, t) signal."""
    # signals keyed by (permno, t); panel by (permno, sort_year, month)
    p = panel[["permno", "sort_year", "month", "ret_dl"]].copy()
    p = p.rename(columns={"sort_year": "t"})
    # keep only July t .. June t+1 months
    p["yy"] = p["month"].dt.year
    p["mm"] = p["month"].dt.month
    # strictly: months in [July t, June t+1]
    keep = p[((p["yy"] == p["t"]) & (p["mm"] >= 7)) |
             ((p["yy"] == p["t"] + 1) & (p["mm"] <= 6))]
    return signals.merge(keep[["permno", "t", "month", "ret_dl"]],
                         on=["permno", "t"], how="inner")


def _add_rf(returns, factors):
    """Subtract the monthly rf (decimal) to get excess returns."""
    ff = factors.set_index("dt")["rf"]
    rf = ff.groupby(ff.index.to_period("M")).last()
    rf.index = rf.index.to_timestamp()
    r = returns.copy()
    r["month_m"] = r["month"].dt.to_period("M").dt.to_timestamp()
    r = r.merge(rf.rename("rf"), left_on="month_m", right_index=True, how="left")
    r["ret_ex"] = r["ret_dl"] - r["rf"]
    return r


def _ols_alpha_se(y, X):
    import statsmodels.api as sm
    y = y.dropna()
    Xa = X.reindex(y.index).dropna()
    y = y.reindex(Xa.index)
    Xc = sm.add_constant(Xa)
    model = sm.OLS(y, Xc).fit()
    return float(model.params["const"]), float(model.bse["const"])


def _ew_series(r):
    """EW mean (and OLS SE of the mean) of a monthly return series."""
    s = r.dropna()
    if len(s) < 2:
        return float("nan"), float("nan")
    mean = float(s.mean())
    se = float(s.std(ddof=1) / np.sqrt(len(s)))
    return mean, se


def compute_table10(cs, panel, factors, bp_variant="nyse"):
    """25 portfolios (5x5): duration quintiles x RIOR quintiles, EW excess returns."""
    d = cs.dropna(subset=["dur_q", "rior"]).copy()
    d["dq"] = _assign_quintile(d, "dur_q")
    d["rq"] = _assign_quintile(d, "rior")
    sig = d[["permno", "t", "dq", "rq"]].copy()
    ret = _join_returns(sig, panel)
    ret = _add_rf(ret, factors)

    # RIOR quintile labels: 1 = low RIOR, 5 = high RIOR
    rnames = {1: "lowrior", 2: "rior2", 3: "rior3", 4: "rior4", 5: "highrior"}
    dnames = {1: "D1", 2: "D2", 3: "D3", 4: "D4", 5: "D5"}

    # cell series
    ew = ret.groupby(["t", "rq", "dq"])["ret_ex"].mean().reset_index()

    # per-cell monthly series
    series = {}
    for (rq, dq), g in ret.groupby(["rq", "dq"]):
        series[(rq, dq)] = g.groupby("month")["ret_ex"].mean() * 100.0

    res = {}
    for rq, rn in rnames.items():
        for dq, dn in dnames.items():
            s = series.get((rq, dq), pd.Series(dtype=float))
            mean, se = _ew_series(s)
            res[f"t10_{rn}_{dn}"] = mean
            res[f"t10_{rn}_{dn}_se"] = se
        # D1-D5 spread (low - high duration)
        s1 = series.get((rq, 1), pd.Series(dtype=float))
        s5 = series.get((rq, 5), pd.Series(dtype=float))
        spread = s1 - s5
        mean, se = _ew_series(spread)
        res[f"t10_{rn}_D1D5"] = mean
        res[f"t10_{rn}_D1D5_se"] = se

    # RIOR long-short (RIOR1 - RIOR5) per duration quintile
    for dq, dn in dnames.items():
        s1 = series.get((1, dq), pd.Series(dtype=float))
        s5 = series.get((5, dq), pd.Series(dtype=float))
        spread = s1 - s5
        mean, se = _ew_series(spread)
        res[f"t10_r1r5_{dn}"] = mean
        res[f"t10_r1r5_{dn}_se"] = se
    s1_all = series.get((1, 1), pd.Series(dtype=float)) - series.get((5, 1), pd.Series(dtype=float))
    s5_all = series.get((1, 5), pd.Series(dtype=float)) - series.get((5, 5), pd.Series(dtype=float))
    spread = s1_all - s5_all
    mean, se = _ew_series(spread)
    res["t10_r1r5_D1D5"] = mean
    res["t10_r1r5_D1D5_se"] = se

    return res


def compute_table11(cs, panel, factors):
    """9 portfolios x 2 size panels: duration tertiles x RIOR tertiles, FF3 alphas."""
    d = cs.dropna(subset=["dur_q", "rior"]).copy()
    med = _medians(d, "me_jun")
    d = d.merge(med.rename("med_me"), on="t", how="left")
    d["basket"] = np.where(d["me_jun"] <= d["med_me"], "s", "l")  # s=small, l=large
    out = _double_tertile_alphas(d, panel, factors, "t11", mid_name="rior2")
    return out


def compute_table12(cs, panel, factors):
    """9 portfolios x 2 BM panels: duration tertiles x RIOR tertiles, FF3 alphas."""
    d = cs.dropna(subset=["dur_q", "rior", "bm"]).copy()
    med = _medians(d, "bm")
    d = d.merge(med.rename("med_bm"), on="t", how="left")
    d["basket"] = np.where(d["bm"] <= d["med_bm"], "s", "l")  # s=growth, l=value
    out = _double_tertile_alphas(d, panel, factors, "t12", mid_name="rior")
    return out


def _double_tertile_alphas(d, panel, factors, prefix, mid_name="rior2"):
    """FF3 alphas of 3x3 duration-tertile x RIOR-tertile portfolios, per basket."""
    import statsmodels.api as sm

    ff = factors.set_index("dt")
    F = pd.DataFrame({"mkt_rf": ff["mkt_rf"], "smb": ff["smb"], "hml": ff["hml"]})
    F.index = F.index.to_period("M").to_timestamp()

    # Duration tertiles are FORMED WITHIN each basket (paper: "within each bin I
    # sort stocks into tertiles based on duration"). Dur and BM / size are strongly
    # correlated, so global tertiles leave the high-duration bin of the value/large
    # basket nearly empty (26-38 firms/month), producing noise-only D3 alphas.
    # RIOR tertiles are an INDEPENDENT (global) sort (paper: "independent sort on
    # residual institutional ownership").
    d = d.copy()
    d["dq"] = _assign_tertile_within(d, "dur_q", "basket")
    d["rq"] = _assign_tertile(d, "rior")
    sig = d[["permno", "t", "basket", "dq", "rq"]].copy()
    ret = _join_returns(sig, panel)
    ret = _add_rf(ret, factors)

    rnames = {1: "lowrior", 2: mid_name, 3: "highrior"}
    dnames = {1: "D1", 2: "D2", 3: "D3"}
    res = {}
    # series dict keyed by (basket, rq, dq) -> monthly EW excess return (percent)
    series = {}
    for (basket, rq, dq), g in ret.groupby(["basket", "rq", "dq"]):
        series[(basket, rq, dq)] = g.groupby("month")["ret_ex"].mean() * 100.0

    for basket in ("s", "l"):
        for rq, rn in rnames.items():
            for dq, dn in dnames.items():
                s = series.get((basket, rq, dq), pd.Series(dtype=float))
                alpha, se = _ff3_alpha_se(s, F)
                res[f"{prefix}_{rn}_{basket}_{dn}"] = alpha
                res[f"{prefix}_{rn}_{basket}_{dn}_se"] = se
            # D1-D3 spread (alpha of D1 - D3)
            s1 = series.get((basket, rq, 1), pd.Series(dtype=float))
            s3 = series.get((basket, rq, 3), pd.Series(dtype=float))
            spread = s1 - s3
            alpha, se = _ff3_alpha_se(spread, F)
            res[f"{prefix}_{rn}_{basket}_D1D3"] = alpha
            res[f"{prefix}_{rn}_{basket}_D1D3_se"] = se
        # RIOR1 - RIOR3 long-short per duration tertile
        for dq, dn in dnames.items():
            s1 = series.get((basket, 1, dq), pd.Series(dtype=float))
            s3 = series.get((basket, 3, dq), pd.Series(dtype=float))
            spread = s1 - s3
            alpha, se = _ff3_alpha_se(spread, F)
            res[f"{prefix}_r1r3_{basket}_{dn}"] = alpha
            res[f"{prefix}_r1r3_{basket}_{dn}_se"] = se
        s1_all = (series.get((basket, 1, 1), pd.Series(dtype=float))
                  - series.get((basket, 3, 1), pd.Series(dtype=float)))
        s3_all = (series.get((basket, 1, 3), pd.Series(dtype=float))
                  - series.get((basket, 3, 3), pd.Series(dtype=float)))
        spread = s1_all - s3_all
        alpha, se = _ff3_alpha_se(spread, F)
        res[f"{prefix}_r1r3_{basket}_D1D3"] = alpha
        res[f"{prefix}_r1r3_{basket}_D1D3_se"] = se

    return res


def _ff3_alpha_se(series, F):
    import statsmodels.api as sm
    s = series.dropna()
    X = F.reindex(s.index).dropna()
    s = s.reindex(X.index)
    if len(s) < 10:
        return float("nan"), float("nan")
    Xc = sm.add_constant(X)
    model = sm.OLS(s, Xc).fit()
    return float(model.params["const"]), float(model.bse["const"])


def load_paper_targets() -> dict:
    doc = json.loads(LAYOUT.preparations_path("tables_to_replicate.json").read_text())
    paper = {}
    for tbl in doc.get("tables", []):
        if tbl.get("id") not in ("T10", "T11", "T12"):
            continue
        for m in tbl.get("metrics", []):
            paper[m["name"]] = m["value"]
    return paper


def write_tables_md(res10, res11, res12, paper) -> None:
    doc = json.loads(LAYOUT.preparations_path("tables_to_replicate.json").read_text())
    names = {}
    for tbl in doc.get("tables", []):
        if tbl.get("id") in ("T10", "T11", "T12"):
            names[tbl["id"]] = [m["name"] for m in tbl.get("metrics", [])]

    def _grid(title, source, committed_names):
        lines = [f"# {title}", "",
                 "| Cell | Ours | Paper |", "|---|---:|---:|"]
        for name in committed_names:
            o = source.get(name)
            p = paper.get(name)
            o_s = f"{o:.3f}" if (o is not None and pd.notna(o)) else "—"
            p_s = f"{p:.3f}" if p is not None else "—"
            lines.append(f"| {name} | {o_s} | {p_s} |")
        lines += [""]
        return "\n".join(lines) + "\n"

    LAYOUT.result_path("table_10.md").write_text(
        _grid("Table 10 — Dur x RIOR quintile means/SEs (ours vs paper)", res10,
              names.get("T10", [])))
    LAYOUT.result_path("table_11.md").write_text(
        _grid("Table 11 — FF3 alphas, size-conditional (ours vs paper)", res11,
              names.get("T11", [])))
    LAYOUT.result_path("table_12.md").write_text(
        _grid("Table 12 — FF3 alphas, BM-conditional (ours vs paper)", res12,
              names.get("T12", [])))


def main(bp_variant="nyse") -> dict:
    cs = load_t10_cross_section(bp_variant)
    panel = _load_return_panel()
    factors = _load_factors()

    res10 = compute_table10(cs, panel, factors, bp_variant)
    res11 = compute_table11(cs, panel, factors)
    res12 = compute_table12(cs, panel, factors)

    paper = load_paper_targets()
    write_tables_md(res10, res11, res12, paper)

    metrics = {}
    for d in (res10, res11, res12):
        for k, v in d.items():
            metrics[k] = {"value": float(v) if pd.notna(v) else float("nan"),
                          "unit": "percent_per_month"}
    return metrics


if __name__ == "__main__":
    m = main()
    print(json.dumps(m, indent=2, default=float))
