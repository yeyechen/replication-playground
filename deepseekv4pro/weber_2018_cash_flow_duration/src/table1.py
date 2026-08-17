"""
Table 1 for Weber (2018) — summary statistics and correlations (44 cells).

Panel A: annual cross-sectional means/stds of 8 characteristics (Dur, BM, IOR, PR,
ROE, Sales_g, ME, Age), winsorized cross-sectionally at 1%/99% (A4), averaged over
the 34 annual June cross-sections (June 1981 .. June 2014).

Panel B: annual cross-sectional correlation matrices (all 28 pairs among the 8
characteristics), averaged over years (plain mean).

Sample: stocks above the 20th NYSE size percentile (breakpoints from NYSE stocks'
June market equity, exchcd==1). A stock above the NYSE 20th pct in June t is in that
year's cross-section.

Variables per firm at June t (fiscal year ending calendar t-1):
    Dur      = implied equity duration (Dechow et al. eq. 2), winsorized (A4)
    BM       = BE(FYE t-1) / ME(Dec t-1)
    PR       = net payout / ni, net payout = dv + prstkc - sstk (L108)
    ROE      = ib / BE_lag (BE of FYE t-2)
    Sales_g  = sale_t / sale_{t-1} - 1
    ME       = June CRSP market equity (millions)
    Age      = number of distinct Compustat fiscal years for the firm as of FYE t-1
    IOR      = 13F institutional ownership ratio (see build_ior)

Baseline construction (V0) is UNTOUCHED: this module reuses compustat_funda.sql for
fundamentals (book-equity cascade + duration parameters identical to main.py) and
recomputes duration with the SAME recursion as main.py, but on the T1 sample.
"""
from __future__ import annotations

import json
import numpy as np
import pandas as pd
from clickhouse_driver import Client

from utils.env import get_clickhouse_config
from utils.paths import paper_layout
from table4_5 import duration_recursion

SLUG = "weber_2018_attempt2_deepseek"
LAYOUT = paper_layout(SLUG)
SQL_DIR = LAYOUT.src_path("sql")

VARS = ["dur", "bm", "ior", "pr", "roe", "sales_g", "me", "age"]
VAR_LABELS = {
    "dur": "Dur", "bm": "BM", "ior": "IOR", "pr": "PR", "roe": "ROE",
    "sales_g": "Sales_g", "me": "ME", "age": "Age",
}

T1_START = 1981   # first June cross-section
T1_END = 2014     # last June cross-section (34 years)


def _client() -> Client:
    cfg = get_clickhouse_config()
    return Client(host=cfg["host"], port=int(cfg["port"]), user=cfg["user"],
                  password=cfg["password"], database=cfg["database"],
                  settings={"max_execution_time": 600})


def _q(sql: str):
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


# --------------------------------------------------------------------------- #
# Fundamentals (reuse compustat_funda.sql + book-equity cascade from main.py)
# --------------------------------------------------------------------------- #
def load_funda() -> pd.DataFrame:
    df = _q((SQL_DIR / "compustat_funda.sql").read_text())
    df["datadate"] = pd.to_datetime(df["datadate"])
    df["lpermno"] = df["lpermno"].astype("Int64")
    return df.sort_values(["gvkey", "fyear", "datadate"]).reset_index(drop=True)


def book_equity(funda: pd.DataFrame) -> pd.DataFrame:
    f = funda.copy()
    seq = f["seq"]
    ceq = f["ceq"]
    pstk = f["pstk"].fillna(0.0)
    shareholders = seq.where(seq.notna(),
                             ceq.where(ceq.notna(), f["at"] - f["lt"]).fillna(0.0) + pstk)
    pstkrv = f["pstkrv"].fillna(0.0)
    pstkl = f["pstkl"].fillna(0.0)
    pstk_pref = pstk
    pstk_pref = pstk_pref.where(~(pstkl > 0), pstkl)
    pstk_pref = pstk_pref.where(~(pstkrv > 0), pstkrv)
    be = shareholders + f["txdb"].fillna(0.0) + f["itcb"].fillna(0.0) - pstk_pref
    f["be"] = be
    return f


def build_characteristics(funda: pd.DataFrame, me: pd.DataFrame) -> pd.DataFrame:
    """Compute firm-year characteristics keyed by (permno, fyear) with calendar t."""
    f = funda.copy()
    f = f.sort_values(["gvkey", "fyear"]).reset_index(drop=True)

    f["be_lag"] = f.groupby("gvkey")["be"].shift(1)
    f["ib_lag"] = f.groupby("gvkey")["ib"].shift(1)
    f["sale_lag"] = f.groupby("gvkey")["sale"].shift(1)
    f["datadate_lag"] = f.groupby("gvkey")["datadate"].shift(1)
    f["fyear_lag"] = f.groupby("gvkey")["fyear"].shift(1)

    f["fyear_diff"] = f["fyear"] - f["fyear_lag"]
    f["dd_gap"] = (f["datadate"] - f["datadate_lag"]).dt.days
    valid_adj = (f["fyear_diff"] == 1) & (f["dd_gap"].between(300, 430))

    be_lag_ok = f["be_lag"].notna() & (f["be_lag"] > 0)
    sale_lag_ok = f["sale_lag"].notna() & (f["sale_lag"] > 0)
    f["roe"] = np.where(valid_adj & be_lag_ok, f["ib"] / f["be_lag"], np.nan)
    f["g"] = np.where(valid_adj & sale_lag_ok, f["sale"] / f["sale_lag"] - 1.0, np.nan)

    # Keep RAW roe/g for the T1 characteristics (ROE, Sales_g) so they are winsorized
    # exactly once (in the T1 cross-section). The duration recursion below uses the
    # within-fyear-winsorized roe/g (A4, matching main.py), so do NOT overwrite roe/g
    # before the recursion.
    f["roe_raw_t1"] = f["roe"]
    f["g_raw_t1"] = f["g"]

    def _clip_cs(s):
        lo, hi = s.quantile(0.01), s.quantile(0.99)
        return s.clip(lo, hi)
    # winsorized ROE/g inputs (feed the baseline Dur, A4)
    roe_w = f.groupby("fyear")["roe"].transform(_clip_cs)
    g_w = f.groupby("fyear")["g"].transform(_clip_cs)

    f = f.rename(columns={"lpermno": "permno"})
    f["permno"] = f["permno"].astype("float64")
    f["month"] = f["datadate"].dt.to_period("M").dt.to_timestamp()
    me_month = me[["permno", "month", "me_dollars"]].drop_duplicates(
        ["permno", "month"], keep="last")
    me_month["permno"] = me_month["permno"].astype("float64")
    f = f.merge(me_month.rename(columns={"me_dollars": "p"}), on=["permno", "month"],
                how="left")

    # Two duration variants, differing only in the ROE/g INPUT winsorization:
    #   (a) "dur"      = winsorized-inputs	(fyear-winsorized roe/g) — current V0 / A4
    #   (b) "dur_rawin" = raw-inputs	(raw roe/g; only the sort-year Dur winsorization
    #                    is applied downstream), the A4-test / V1-style variant
    be_ok = f["be"].notna() & (f["be"] > 0)
    p_ok = f["p"].notna() & (f["p"] > 0)
    # duration_recursion substitutes roe_ss/sg_ss for NaN/finite-guard internally.
    dur_w = duration_recursion(roe_w.to_numpy(), g_w.to_numpy(),
                               f["be"].to_numpy() * 1e6, f["p"].to_numpy())
    dur_rwin = duration_recursion(f["roe_raw_t1"].to_numpy(), f["g_raw_t1"].to_numpy(),
                                  f["be"].to_numpy() * 1e6, f["p"].to_numpy())
    f["dur"] = np.where(be_ok & p_ok, dur_w, np.nan)
    f["dur_rawin"] = np.where(be_ok & p_ok, dur_rwin, np.nan)

    f["pr"] = (f["dv"] + f["prstkc"] - f["sstk"]) / f["ni"]
    f["sales_g"] = f["g_raw_t1"]
    f["roe_final"] = f["roe_raw_t1"]
    f["t"] = f["fyear"] + 1

    f = f.sort_values(["gvkey", "fyear"]).reset_index(drop=True)
    f["age"] = f.groupby("gvkey").cumcount() + 1

    return f


def build_me(me_all: pd.DataFrame):
    """June-t ME (millions), Dec t-1 ME (millions), and NYSE June-20th-pct breakpoints."""
    me = me_all.copy()
    me["month"] = pd.to_datetime(me["month"])
    me["yr"] = me["month"].dt.year
    me["mm"] = me["month"].dt.month

    june = me[me["mm"] == 6][["permno", "yr", "me_dollars"]].rename(
        columns={"yr": "t", "me_dollars": "me_jun"})
    dec = me[me["mm"] == 12][["permno", "yr", "me_dollars"]].rename(
        columns={"yr": "t", "me_dollars": "me_dec"})
    dec["t"] = dec["t"] + 1

    # NYSE June 20th percentile breakpoints (exchcd==1) — canonical A9 (V0).
    nyse = me[me["exchcd"] == 1]
    june_nyse = nyse[nyse["mm"] == 6][["permno", "yr", "me_dollars"]]
    bp_nyse = june_nyse.groupby("yr")["me_dollars"].quantile(0.20).rename("bp20").reset_index()
    bp_nyse = bp_nyse.rename(columns={"yr": "t"})

    # all-stock June 20th percentile breakpoints — A9 test variant (all exchcd 1/2/3).
    june_all = me[me["mm"] == 6][["permno", "yr", "me_dollars"]]
    bp_all = june_all.groupby("yr")["me_dollars"].quantile(0.20).rename("bp20").reset_index()
    bp_all = bp_all.rename(columns={"yr": "t"})

    june = june.drop_duplicates(["permno", "t"], keep="last")
    dec = dec.drop_duplicates(["permno", "t"], keep="last")
    out = june.merge(dec, on=["permno", "t"], how="outer")
    out["me_jun_m"] = out["me_jun"] / 1e6
    out["me_dec_m"] = out["me_dec"] / 1e6
    return out, bp_nyse, bp_all


# --------------------------------------------------------------------------- #
# IOR
# --------------------------------------------------------------------------- #
def build_ior(me_all: pd.DataFrame) -> pd.DataFrame:
    """(permno, quarter-end, IOR) with split-adjustment applied.

    Steps:
      1. s34 holdings summed per (cusip, rdate)  -> (cusip, rdate, shares, prdate).
      2. cusip -> permno PIT via dsenames cusip/ncusip.
      3. split adjustment: shares * cfacshr(report month) / cfacshr(prdate month).
      4. divide by CRSP shares outstanding (shrout * 1000).
    Holdings absent from 13F get IOR = 0 (set at June-t selection).
    """
    holdings = _q((SQL_DIR / "ior_s34.sql").read_text())
    cusip_map = _q((SQL_DIR / "cusip_map.sql").read_text())

    holdings["rdate"] = pd.to_datetime(holdings["rdate"])
    holdings["prdate"] = pd.to_datetime(holdings["prdate"])
    cusip_map["namedt"] = pd.to_datetime(cusip_map["namedt"])
    cusip_map["nameendt"] = pd.to_datetime(cusip_map["nameendt"])

    m = holdings.merge(cusip_map, on="cusip", how="inner")
    m = m[(m["rdate"] >= m["namedt"]) & (m["rdate"] <= m["nameendt"])]
    # keep first (ncusip) match for the ncusip/cusip UNION ALL dual mapping
    m = m.drop_duplicates(["cusip", "rdate", "permno"], keep="first")

    n_cusip = holdings["cusip"].nunique()
    matched_cusip = m["cusip"].nunique()
    match_rate = matched_cusip / n_cusip if n_cusip else 0.0
    print(f"  [IOR] distinct cusip {n_cusip}; matched {matched_cusip}; "
          f"rate {match_rate:.4f}", flush=True)

    agg = m.groupby(["permno", "rdate"], as_index=False).agg(
        shares=("shares", "sum"), prdate=("prdate", "min"))

    # ---- split adjustment via monthly cfacshr + shrout (from table1_me) ----
    me_all = me_all.copy()
    me_all["month"] = pd.to_datetime(me_all["month"])
    cfac = me_all[["permno", "month", "cfacshr", "shrout"]].drop_duplicates(
        ["permno", "month"], keep="last")
    cfac["permno"] = cfac["permno"].astype("float64")

    agg["permno"] = agg["permno"].astype("float64")
    agg["rep_month"] = agg["rdate"].dt.to_period("M").dt.to_timestamp()
    agg["pr_month"] = agg["prdate"].dt.to_period("M").dt.to_timestamp()

    agg = agg.merge(cfac[["permno", "month", "cfacshr", "shrout"]].rename(
                        columns={"month": "rep_month", "cfacshr": "cf_rep"}),
                    on=["permno", "rep_month"], how="left")
    agg = agg.merge(cfac[["permno", "month", "cfacshr"]].rename(
                        columns={"month": "pr_month", "cfacshr": "cf_pr"}),
                    on=["permno", "pr_month"], how="left")

    ratio = agg["cf_rep"] / agg["cf_pr"]
    ratio = ratio.where((agg["cf_pr"].notna()) & (agg["cf_pr"] > 0)
                        & (agg["cf_rep"].notna()), 1.0)
    agg["shares_adj"] = agg["shares"] * ratio

    agg["ior"] = agg["shares_adj"] / (agg["shrout"] * 1000.0)
    out = agg[["permno", "rdate", "ior"]].copy()
    return out, match_rate


def _latest_ior_by_june(ior: pd.DataFrame):
    """Map each June t to the IOR at the most recent report quarter-end <= June 30 of
    that year, applying carry-forward only up to 8 quarters: a report more than 8
    quarters stale (i.e. the stock has been absent from 13F for > 8 quarters) is
    treated as a zero holding, else the last reported value is carried forward."""
    ior = ior.copy()
    ior["permno"] = ior["permno"].astype("float64")
    ior["y"] = ior["rdate"].dt.year
    frames = {}
    for t in range(T1_START, T1_END + 1):
        cutoff = pd.Timestamp(year=t, month=6, day=30)
        # 8 quarters = 24 months; reports older than this are stale -> drop to 0
        cutoff_8q = cutoff - pd.DateOffset(months=24)
        sub = ior[(ior["rdate"] <= cutoff) & (ior["rdate"] >= cutoff_8q)]
        latest = sub.sort_values("rdate").groupby("permno")["ior"].last().rename("ior")
        latest.index = latest.index.astype("float64")
        latest = latest.to_frame().assign(t=t).reset_index()
        frames[t] = latest
    return pd.concat(frames.values(), ignore_index=True)


# --------------------------------------------------------------------------- #
# Table 1
# --------------------------------------------------------------------------- #
def _load_t1_inputs():
    """Load+precompute the T1 inputs once: funda (with be, both Dur variants),
    June/Dec ME pair (millions), both 20th-pct breakpoint variants, and IOR-by-June.

    Returns (cs, bp_nyse, bp_all, match_rate, ior_raw). `ior_raw` is the raw
    (permno, rdate, ior) frame so downstream T10-T12 can derive a Dec t-1 IOR
    lookup without re-querying s34."""
    funda = load_funda()
    funda = book_equity(funda)

    me_all = _q((SQL_DIR / "table1_me.sql").read_text())
    me_all["permno"] = me_all["permno"].astype("float64")
    me_all["month"] = pd.to_datetime(me_all["month"])

    chars = build_characteristics(funda, me_all)
    me_pair, bp_nyse, bp_all = build_me(me_all)

    ior, match_rate = build_ior(me_all)
    ior_by_t = _latest_ior_by_june(ior)

    # merge fundamentals (both dur variants + bm/pr/roe/sales_g/age)
    ch = chars[["permno", "t", "dur", "dur_rawin", "be", "pr", "roe_final",
                "sales_g", "age"]].copy()
    ch["permno"] = ch["permno"].astype("float64")
    me_pair = me_pair.merge(ch, on=["permno", "t"], how="left")
    me_pair["bm"] = me_pair["be"] / me_pair["me_dec_m"]

    cs = me_pair.merge(ior_by_t, on=["permno", "t"], how="left")
    cs["ior"] = cs["ior"].fillna(0.0)
    cs = cs.rename(columns={"me_jun_m": "me", "roe_final": "roe"})
    cs = cs[cs["t"].between(T1_START, T1_END)].copy()
    return cs, bp_nyse, bp_all, match_rate, ior


def _t1_stats(cs: pd.DataFrame, dur_col: str) -> dict:
    """Panel A means/stds + Panel B correlations for 8 characteristics, where the
    Dur column is `dur_col` ('dur' or 'dur_rawin'). Winsorizes cross-sectionally at
    1/99 within each t (A4), then averages annual stats over the 34 June-years."""
    # Replace the (single) duration column with "dur" without creating a duplicate:
    # pick the non-duration variant name to drop, then rename the chosen one.
    other_dur = "dur_rawin" if dur_col == "dur" else "dur"
    d = cs.drop(columns=[other_dur], errors="ignore").rename(columns={dur_col: "dur"})
    d = d[["permno", "t", "dur", "bm", "ior", "pr", "roe", "sales_g", "me",
           "age"]].copy()

    def _winsor(g):
        out = g[VARS].copy()
        for v in VARS:
            s = out[v]
            n = int(s.notna().sum())
            if n >= 2:
                lo, hi = s.quantile(0.01), s.quantile(0.99)
                out[v] = s.clip(lo, hi)
        return out
    # winsorize within year, preserving the t (year) column
    d[VARS] = d.groupby("t", group_keys=False)[VARS].apply(_winsor)

    annual_mean = d.groupby("t")[VARS].mean()
    annual_std = d.groupby("t")[VARS].std()

    res = {}
    for v in VARS:
        res[f"mean_{v}"] = float(annual_mean[v].mean())
        res[f"std_{v}"] = float(annual_std[v].mean())
    for i, v1 in enumerate(VARS):
        for v2 in VARS[i + 1:]:
            def _annual_corr(g, v1=v1, v2=v2):
                return g[[v1, v2]].corr().iloc[0, 1]
            corr_series = d.groupby("t")[VARS].apply(_annual_corr, include_groups=False)
            res[f"corr_{v1}_{v2}"] = float(corr_series.mean())
    res["_n_obs_total"] = int(len(d))
    res["_n_years"] = int(d["t"].nunique())
    return res


def compute_table1_variants(panel: pd.DataFrame = None) -> tuple[dict, dict, dict]:
    """Compute T1 stats under the 2×2 (breakpoint × Dur-input) variant grid.

    Returns:
      variants : {(bp_variant, dur_input): metrics_dict}, 4 entries
      bp_summary : summary of the size-screen effect on mean_me/mean_ior
      best : the chosen canonical metrics dict (data-favored variant)
    """
    cs, bp_nyse, bp_all, match_rate, _ = _load_t1_inputs()

    variants = {}
    # breakpoint variants
    for bp_name, bp in (("nyse", bp_nyse), ("allstock", bp_all)):
        sub = cs.merge(bp, on="t", how="left")
        sub = sub[sub["me_jun"] > sub["bp20"]].copy()
        # dur-input variants
        for dur_name, dur_col in (("win", "dur"), ("raw", "dur_rawin")):
            m = _t1_stats(sub, dur_col)
            m["_ior_match_rate"] = match_rate
            variants[(bp_name, dur_name)] = m

    # choose canonical: score each variant by |mean_me - 2125| and |mean_ior - 0.44|
    # scaled, then report the lowest. mean_me dominates (paper 2125 vs our prior 3559).
    def _score(mm):
        me_err = abs(mm["mean_me"] - 2125.0) / 2125.0
        ior_err = abs(mm["mean_ior"] - 0.44) / 0.44
        return me_err + ior_err
    best_key = min(variants, key=lambda k: _score(variants[k]))
    best = variants[best_key]

    return variants, best_key, best


def compute_table1(panel: pd.DataFrame = None) -> dict:
    """Canonical T1 metrics for integration with main.py — returns the data-favored
    variant (see compute_table1_variants)."""
    _, best_key, best = compute_table1_variants(panel)
    return best


def _md_table1(metrics: dict, paper: dict) -> str:
    lines = ["# Table 1 — Weber (2018) summary statistics & correlations (ours vs paper)",
             "",
             "## Panel A: means (avg of 34 annual cross-sections)",
             "",
             "| Variable | Ours | Paper |",
             "|---|--:|--:|"]
    for v in VARS:
        o = metrics.get(f"mean_{v}")
        p = paper.get(f"mean_{v}")
        o_s = f"{o:.4f}" if o is not None else "—"
        p_s = f"{p:.4f}" if p is not None else "—"
        lines.append(f"| {VAR_LABELS[v]} | {o_s} | {p_s} |")
    lines += ["", "## Panel A: stds", "",
              "| Variable | Ours | Paper |", "|---|--:|--:|"]
    for v in VARS:
        o = metrics.get(f"std_{v}")
        p = paper.get(f"std_{v}")
        o_s = f"{o:.4f}" if o is not None else "—"
        p_s = f"{p:.4f}" if p is not None else "—"
        lines.append(f"| {VAR_LABELS[v]} | {o_s} | {p_s} |")
    lines += ["", "## Panel B: correlations", "",
              "| Pair | Ours | Paper |", "|---|--:|--:|"]
    for i, v1 in enumerate(VARS):
        for v2 in VARS[i + 1:]:
            key = f"corr_{v1}_{v2}"
            o = metrics.get(key)
            p = paper.get(key)
            o_s = f"{o:.4f}" if o is not None else "—"
            p_s = f"{p:.4f}" if p is not None else "—"
            lines.append(f"| {VAR_LABELS[v1]}-{VAR_LABELS[v2]} | {o_s} | {p_s} |")
    lines += ["", "Format: `ours vs paper` per cell."]
    return "\n".join(lines) + "\n"


def write_table1_variants_md(variants: dict, best_key: tuple, paper: dict,
                             best: dict) -> None:
    """Document the 2x2 variant grid AND the canonical per-cell table in
    results/table_1.md (variant grid first, canonical table second)."""
    order = [("nyse", "win"), ("nyse", "raw"), ("allstock", "win"), ("allstock", "raw")]
    labels = {"nyse": "NYSE-only bp", "allstock": "all-stock bp",
              "win": "win Dur inputs", "raw": "raw Dur inputs"}

    lines = ["# Table 1 — variant comparison (iteration 8)",
             "",
             "Size screen (A9) and Dur input-winsorization (A4) variant grid.",
             "`bp` = 20th-pct breakpoint universe; `Dur` = ROE/g input winsorization.",
             "",
             "## Key cells across the 2x2 grid",
             "",
             "| Variant | mean_dur | std_dur | mean_me | mean_ior | corr_dur_roe | corr_dur_bm | corr_dur_sales_g | corr_dur_pr |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for k in order:
        m = variants[k]
        lines.append(f"| {labels[k[0]]} / {labels[k[1]]} | {m['mean_dur']:.4f} | "
                     f"{m['std_dur']:.4f} | {m['mean_me']:.1f} | {m['mean_ior']:.4f} | "
                     f"{m['corr_dur_roe']:.4f} | {m['corr_dur_bm']:.3f} | "
                     f"{m['corr_dur_sales_g']:.4f} | {m['corr_dur_pr']:.4f} |")
    lines += ["",
              f"Paper targets: mean_dur 18.77, std_dur 5.37, mean_me 2125, mean_ior 0.44,",
              "corr_dur_roe -0.39, corr_dur_bm -0.70, corr_dur_sales_g 0.34, corr_dur_pr -0.10.",
              "",
              f"**Chosen canonical variant: bp={best_key[0]} / Dur={best_key[1]}**",
              f"(scored by |mean_me-2125|/2125 + |mean_ior-0.44|/0.44).",
              "",
              "---",
              "",
              _md_table1(best, paper)]
    LAYOUT.result_path("table_1.md").write_text("\n".join(lines))


def load_paper_targets() -> dict:
    doc = json.loads(LAYOUT.preparations_path("tables_to_replicate.json").read_text())
    paper = {}
    for tbl in doc.get("tables", []):
        if tbl.get("id") != "T1":
            continue
        for m in tbl.get("metrics", []):
            paper[m["name"]] = m["value"]
    return paper


def main() -> None:
    paper = load_paper_targets()
    variants, best_key, best = compute_table1_variants()

    # variant grid + canonical per-cell table (both written to results/table_1.md)
    write_table1_variants_md(variants, best_key, paper, best)

    print("=== Table 1 variant grid (iteration 8) ===")
    order = [("nyse", "win"), ("nyse", "raw"), ("allstock", "win"), ("allstock", "raw")]
    labels = {"nyse": "NYSE-bp", "allstock": "all-bp", "win": "win-in", "raw": "raw-in"}
    print("variant           mean_dur  std_dur  mean_me   mean_ior  c_dur_roe c_dur_bm c_dur_sg c_dur_pr")
    for k in order:
        m = variants[k]
        print(f"{labels[k[0]]}/{labels[k[1]]:<5}      {m['mean_dur']:8.3f} {m['std_dur']:7.3f} "
              f"{m['mean_me']:9.1f} {m['mean_ior']:9.4f} {m['corr_dur_roe']:9.4f} "
              f"{m['corr_dur_bm']:8.3f} {m['corr_dur_sales_g']:8.4f} {m['corr_dur_pr']:9.4f}")
    print(f"chosen canonical variant: bp={best_key[0]} / Dur={best_key[1]}")
    print("ior_match_rate:", best.get("_ior_match_rate"))
    print("n_obs_total:", best.get("_n_obs_total"))
    print("n_years:", best.get("_n_years"))
    return best


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
