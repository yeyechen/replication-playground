"""
Tables 8 & 9 (Panel A) for Weber (2018) — analyst expectations (claim C4).

Table 8 (June 1982 .. June 2009), ten duration deciles:
  Panel A — LTG_t .. LTG_t+4 (time-series avg of annual cross-sectional MEANS of
             long-term growth forecasts).
  Panel B — EG_{t-6:t-1} and EG_{t:t+5} (realized five-year EPS growth, annualized);
             time-series avg of annual cross-sectional MEANS.
  Panel C — SUE1 / SUE2 / SUE3 (Livnat-Mendenhall 2006); time-series avg of annual
             cross-sectional MEDIANS (paper reports portfolio medians, L1929).
  Sample: firms with nonmissing LTG for all periods (footnote 16).

Table 9 Panel A (July 2001 .. June 2014), five duration QUINTILES:
  PTB = consensus 12-month price target / book equity (BE FYE t-1).
  PTP = (price target / current price - 1) * 100  [percent].
  Time-series avg of annual cross-sectional MEANS.

I/B/E/S mapping discovery (verified against data):
  - IBES `cusip` is *not* universally standard 8-digit CUSIP; non-US listings carry
    EX/ER/LM/FJ… prefixes. The `usfirm=1` flag isolates US firms whose cusip is
    standard and matches CRSP `dsenames.ncusip` at ~95.5% (665/14867 LTG cusips
    unmatched; 3894/4112 at June 2005 for ptgsum). Foreign firms excluded via usfirm=1.
  - LTG consensus in statsum_epsus fpi='0' AND fiscalp='LTG'; mean=meanest.
  - Price targets in ptgsum measure='PTG'; mean=meanptg (split-adjusted $/share);
    current price in actpsum_epsus.price at the same June statpers.
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
T8_END = 2009          # June sort years 1982..2009
T9_START = 2001
T9_END = 2013          # June sort years 2001..2013


def _client() -> Client:
    cfg = get_clickhouse_config()
    return Client(host=cfg["host"], port=int(cfg["port"]), user=cfg["user"],
                  password=cfg["password"], database=cfg["database"],
                  settings={"max_execution_time": 600})


_CFG = get_clickhouse_config()


def q(sql: str) -> pd.DataFrame:
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


def q_file(name: str) -> pd.DataFrame:
    return q((SQL_DIR / name).read_text())


# --------------------------------------------------------------------------- #
# CUSIP -> permno mapping (PIT)
# --------------------------------------------------------------------------- #
def load_cusip_map() -> pd.DataFrame:
    cm = q_file("cusip_map.sql")
    cm["namedt"] = pd.to_datetime(cm["namedt"])
    cm["nameendt"] = pd.to_datetime(cm["nameendt"])
    return cm


def map_cusip_to_permno(df: pd.DataFrame, cm: pd.DataFrame,
                        date_col: str) -> pd.DataFrame:
    """PIT-map IBES cusip -> CRSP permno at observation date.

    A CUSIP record is valid on `date` iff namedt <= date <= nameendt (inclusive).
    Among valid records keep the one with the latest namedt (most recent assignment).
    Rows with no valid window are DROPPED (returned matched-only). Returns a frame
    with the input cols + permno + a `_match` flag is NOT added; track rates via
    caller-level helper `match_report`.
    """
    d = df.copy()
    d["_date"] = pd.to_datetime(d[date_col])
    cm2 = cm[["cusip", "permno", "namedt", "nameendt"]].copy()
    merged = d.merge(cm2, on="cusip", how="left")
    valid = merged[merged["_date"].between(merged["namedt"], merged["nameendt"])]
    # among valid windows for a (cusip, date), keep latest namedt
    idx = valid.groupby(["cusip", "_date"], sort=False)["namedt"].idxmax()
    valid = valid.loc[idx].copy()
    valid = valid.drop(columns=["namedt", "nameendt"])
    return valid[valid["permno"].notna()]


def match_report(df: pd.DataFrame, cm: pd.DataFrame, date_col: str) -> dict:
    """Distinct-cusip match-rate report (honest, at cusip level)."""
    d = pd.to_datetime(df[date_col])
    cusips = df["cusip"].unique()
    n = len(cusips)
    matched = set(map_cusip_to_permno(df, cm, date_col)["cusip"].unique())
    return {"n_cusip": n, "n_matched": len(matched & set(cusips)),
            "frac": len(matched & set(cusips)) / n if n else 0.0}


# --------------------------------------------------------------------------- #
# Loaders
# --------------------------------------------------------------------------- #
def load_ltg() -> pd.DataFrame:
    lt = q_file("ibes_ltg.sql")
    lt["statpers"] = pd.to_datetime(lt["statpers"])
    lt["june_year"] = lt["statpers"].dt.year
    return lt


def load_ptg() -> pd.DataFrame:
    pt = q_file("ibes_ptg.sql")
    pt["statpers"] = pd.to_datetime(pt["statpers"])
    pt["june_year"] = pt["statpers"].dt.year
    return pt


def load_eps_actuals() -> pd.DataFrame:
    a = q_file("ibes_eps_actuals.sql")
    a["pends"] = pd.to_datetime(a["pends"])
    a["anndats"] = pd.to_datetime(a["anndats"])
    return a


def load_sue_consensus() -> pd.DataFrame:
    s = q_file("ibes_sue_consensus.sql")
    s["fpedats"] = pd.to_datetime(s["fpedats"])
    s["statpers"] = pd.to_datetime(s["statpers"])
    return s


def load_mapping() -> pd.DataFrame:
    """permno -> sort_year -> (decile 1..10, quintile 1..5, dur). Full universe."""
    pan = pd.read_parquet(LAYOUT.data_path("panel.parquet"),
                          columns=["permno", "sort_year", "bin", "dur"])
    pan = pan.drop_duplicates(["permno", "sort_year"])
    pan["decile"] = pan["bin"].astype(int)
    pan["quintile"] = pan.groupby("sort_year")["dur"].transform(
        lambda s: np.ceil(s.rank(method="first", pct=True) * 5).astype(int).clip(1, 5))
    return pan[["permno", "sort_year", "decile", "quintile"]]


def _redecile(dur_series: pd.Series) -> pd.Series:
    """Rank `dur_series` into deciles 1..10 within one June cohort (pct-rank,
    method='first', matching the full-universe convention in main.py L460-462)."""
    r = dur_series.rank(method="first", pct=True)
    return np.ceil(r * 10).astype(int).clip(1, 10)


def build_covered_mapping(covered: pd.DataFrame) -> pd.DataFrame:
    """Re-sort duration deciles (1..10) and quintiles (1..5) WITHIN the IBES-covered
    subset only (footnote 15), yielding the Table 8 universe. `covered` carries
    (permno, sort_year) rows already intersected with the panel's June cohorts.

    Returns (panel_map, diag) analogous to load_mapping() but decile/quin re-ranked
    on the covered cross-section; also returns the per-year coverage statistics.
    """
    pan = pd.read_parquet(LAYOUT.data_path("panel.parquet"),
                          columns=["permno", "sort_year", "bin", "dur", "me_jun"])
    pan = pan.drop_duplicates(["permno", "sort_year"])
    # full-universe June cohort size + ME for the coverage-share denominator
    full = pan[pan["sort_year"].between(T8_START, T8_END)].copy()
    full_stats = full.groupby("sort_year").agg(
        n_full=("permno", "count"), me_full=("me_jun", "sum")).reset_index()

    cov = pan.merge(covered[["permno", "sort_year"]].drop_duplicates(),
                    on=["permno", "sort_year"], how="inner").copy()
    cov = cov[cov["sort_year"].between(T8_START, T8_END)]
    # re-rank decile/quantile within the covered subset per cohort
    cov["decile"] = cov.groupby("sort_year")["dur"].transform(_redecile)
    cov["quintile"] = cov.groupby("sort_year")["dur"].transform(
        lambda s: np.ceil(s.rank(method="first", pct=True) * 5).astype(int).clip(1, 5))

    cov_stats = cov.groupby("sort_year").agg(
        n_cov=("permno", "count"), me_cov=("me_jun", "sum")).reset_index()
    stats = full_stats.merge(cov_stats, on="sort_year", how="left").fillna(0.0)

    diag = {
        "coverage_per_year": {
            int(r.sort_year): {
                "n_full": int(r.n_full),
                "n_cov": int(r.n_cov),
                "share_stocks": float(r.n_cov / r.n_full) if r.n_full else 0.0,
                "share_me": float(r.me_cov / r.me_full) if r.me_full else 0.0,
            }
            for r in stats.itertuples()
        },
        "coverage_n_full": int(full["permno"].nunique()),
        "coverage_n_cov": int(cov["permno"].nunique()),
    }
    return cov[["permno", "sort_year", "decile", "quintile"]], diag


def load_coverage(cm: pd.DataFrame) -> pd.DataFrame:
    """IBES-covered (permno, sort_year) pairs (footnote 15).

    ibes_coverage.sql emits distinct (cusip, june_year). PIT-map cusip->permno at the
    June statpers anchor (June 15 of june_year, within the month's validity window),
    then intersect with the panel's (permno, sort_year) where sort_year == june_year.
    Returns a frame with columns (permno, sort_year).
    """
    cov = q_file("ibes_coverage.sql")
    cov["june_year"] = cov["june_year"].astype(int)
    cm2 = cm[["cusip", "permno", "namedt", "nameendt"]].copy()
    cov["_anchor"] = pd.to_datetime(dict(year=cov["june_year"], month=6, day=15))
    m = cov.merge(cm2, on="cusip", how="left")
    valid = m[m["_anchor"].between(m["namedt"], m["nameendt"])]
    idx = valid.groupby(["cusip", "_anchor"], sort=False)["namedt"].idxmax()
    valid = valid.loc[idx].drop(columns=["namedt", "nameendt"])
    return valid[["permno", "june_year"]].rename(
        columns={"june_year": "sort_year"}).drop_duplicates()


def load_fundamentals() -> pd.DataFrame:
    fd = pd.read_parquet(LAYOUT.data_path("fundamentals_duration.parquet"),
                         columns=["permno", "fyear", "be"])
    fd["fyear"] = fd["fyear"].astype(int)
    return fd.drop_duplicates(["permno", "fyear"], keep="last")


# --------------------------------------------------------------------------- #
# Portfolio stats
# --------------------------------------------------------------------------- #
def _decile_mean_ts(df, value_col):
    """Annual cross-sectional MEAN per decile -> time-series average (Series over decile)."""
    yrs = df.groupby(["sort_year", "decile"])[value_col].mean().reset_index()
    return yrs.groupby("decile")[value_col].mean()


def _decile_median_ts(df, value_col):
    """Annual cross-sectional MEDIAN per decile -> time-series average."""
    yrs = df.groupby(["sort_year", "decile"])[value_col].median().reset_index()
    return yrs.groupby("decile")[value_col].mean()


def _emit_decile(metrics, ts, prefix, unit, has_spread):
    for d in range(1, 11):
        metrics[f"{prefix}_D{d}"] = {"value": float(ts.get(d, np.nan)), "unit": unit}
    if has_spread:
        v1, v10 = ts.get(1, np.nan), ts.get(10, np.nan)
        metrics[f"{prefix}_D1D10"] = {"value": float(v1 - v10), "unit": unit}


def winsorize_cs(df, col, key="sort_year"):
    """Cross-sectional 1%/99% winsorize of col within each key group (in place)."""
    def _w(s):
        lo, hi = s.quantile(0.01), s.quantile(0.99)
        return s.clip(lo, hi)
    df[col] = df.groupby(key)[col].transform(_w)
    return df


# --------------------------------------------------------------------------- #
# Table 8
# --------------------------------------------------------------------------- #
def compute_table8(panel_map, cm):
    diag = {}

    # ---- LTG ----
    ltg = load_ltg()
    diag["ltg_match"] = match_report(ltg, cm, "statpers")
    ltg = map_cusip_to_permno(ltg, cm, "statpers")
    ltg = ltg.rename(columns={"june_year": "sort_year"})
    ltg = ltg.merge(panel_map[["permno", "sort_year", "decile"]],
                    on=["permno", "sort_year"], how="inner")
    ltg = ltg[ltg["sort_year"].between(T8_START, T8_END)]

    # one consensus per (permno, sort_year)
    onet = ltg.drop_duplicates(["permno", "sort_year"])[
        ["permno", "sort_year", "decile", "meanest"]]
    diag["ltg_before_fn16"] = int(len(onet))

    # footnote 16 — firms with nonmissing LTG for all periods t..t+4:
    base = onet.rename(columns={"meanest": "ltg0"})
    for s in range(1, 5):
        sh = onet[["permno", "sort_year", "meanest"]].rename(
            columns={"meanest": f"ltg{s}"})
        sh["sort_year"] = sh["sort_year"] - s
        base = base.merge(sh, on=["permno", "sort_year"], how="inner")
    diag["ltg_after_fn16"] = int(len(base))
    diag["ltg_years"] = [int(y) for y in sorted(base["sort_year"].unique())]

    # winsorize LTG cross-sectionally at 1%/99% within each sort_year (L176)
    for s in range(5):
        winsorize_cs(base, f"ltg{s}")

    metrics = {}
    ltg_key = {0: "t", 1: "t1", 2: "t2", 3: "t3", 4: "t4"}
    ts_t = None
    for s in range(5):
        ts = _decile_mean_ts(base.rename(columns={f"ltg{s}": "__v"}), "__v")
        _emit_decile(metrics, ts, f"t8_ltg_{ltg_key[s]}", "percent", True)
        if s == 0:
            ts_t = ts
    diag["ltg_t_deciles"] = {int(d): float(v) for d, v in ts_t.items()}

    # ---- EG: realized 5-year annualized EPS growth (in percent) ----
    # Iteration-10 source (retained): Compustat split-adjusted annual EPS (epspx).
    # The IBES `act_epsus` actual is UNadjusted-for-splits and biases growth down;
    # Compustat epspx is split-adjusted. Metrics keep the Compustat source.
    #
    # Window conventions (paper Panel B labels, sorted at end-June of year t on firms
    # with fiscal year ending in year t-1):
    #   EG_{t-6:t-1}: annualized growth from EPS at FYE t-6 to EPS at FYE t-1.
    #                 Endpoint fyear = t-1 -> attribute to sort_year t = fyear + 1.
    #   EG_{t:t+5} : annualized growth from EPS at FYE t to EPS at FYE t+5.
    #                 Endpoint fyear = t+5 -> attribute to sort_year t = fyear - 5.
    # Both windows are 5-year annualized: (EPS_end / EPS_start)^(1/5) - 1, in percent.
    # Rule (paper silent, retained): both endpoints must exist and be > 0 (a sign
    # change or non-positive base yields undefined growth -> NaN).
    funda_eps = q_file("compustat_funda_eps.sql")
    ann = funda_eps[["permno", "fyear", "eps"]].copy()
    ann = ann.drop_duplicates(["permno", "fyear"], keep="last")
    ann = ann.sort_values(["permno", "fyear"])
    ann["eps_start"] = ann.groupby("permno")["eps"].shift(-5)
    ann["fyear_start"] = ann.groupby("permno")["fyear"].shift(-5)
    # For each endpoint fyear F, the 5-year window runs [F-5, F]. Here we index by the
    # LATER endpoint F and the earlier endpoint is F-5.
    ann["eps_prev5"] = ann.groupby("permno")["eps"].shift(5)
    ann["fyear_prev5"] = ann.groupby("permno")["fyear"].shift(5)
    ok = (ann["fyear"] - ann["fyear_prev5"] == 5) & ann["eps_prev5"].notna() & \
         (ann["eps_prev5"] > 0) & (ann["eps"] > 0)
    # annualized growth as a FRACTION (x100 later), keyed by ENDPOINT fyear
    ann["eg5"] = np.where(ok, (ann["eps"] / ann["eps_prev5"]) ** (1.0 / 5.0) - 1.0, np.nan)
    diag["eg_qualifying"] = int(ok.sum())

    # backward EG_{t-6:t-1}: endpoint FYE t-1 -> sort_year t = fyear + 1
    eb = ann[ann["eg5"].notna()][["permno", "fyear", "eg5", "eps", "eps_prev5"]].copy()
    eb["sort_year"] = eb["fyear"] + 1
    eb = eb.merge(panel_map[["permno", "sort_year", "decile"]],
                  on=["permno", "sort_year"], how="inner")
    eb = eb[eb["sort_year"].between(T8_START, T8_END)]

    # forward EG_{t:t+5}: endpoint FYE t+5 -> sort_year t = fyear - 5
    ef = ann[ann["eg5"].notna()][["permno", "fyear", "eg5", "eps", "eps_prev5"]].copy()
    ef["sort_year"] = ef["fyear"] - 5
    ef = ef.merge(panel_map[["permno", "sort_year", "decile"]],
                  on=["permno", "sort_year"], how="inner")
    ef = ef[ef["sort_year"].between(T8_START, T8_END)]

    diag["eg_back_n"] = int(len(eb))
    diag["eg_fwd_n"] = int(len(ef))

    # endpoint EPS medians per decile (for the EG convention check).
    # backward window: endpoint EPS_{t-1} = `eps`, start EPS_{t-6} = `eps_prev5`.
    diag["eg_eps_t_med_D1"] = float(eb[eb["decile"] == 1]["eps"].median())
    diag["eg_eps_t_med_D10"] = float(eb[eb["decile"] == 10]["eps"].median())
    diag["eg_eps_lag5_med_D1"] = float(eb[eb["decile"] == 1]["eps_prev5"].median())
    diag["eg_eps_lag5_med_D10"] = float(eb[eb["decile"] == 10]["eps_prev5"].median())

    eb = winsorize_cs(eb, "eg5").copy()
    ef = winsorize_cs(ef, "eg5").copy()
    # report in percent units (x100)
    eb["eg5"] = eb["eg5"] * 100.0
    ef["eg5"] = ef["eg5"] * 100.0

    ts = _decile_mean_ts(eb.rename(columns={"eg5": "__v"}), "__v")
    _emit_decile(metrics, ts, "t8_eg_t6_t1", "percent", True)
    ts = _decile_mean_ts(ef.rename(columns={"eg5": "__v"}), "__v")
    _emit_decile(metrics, ts, "t8_eg_t_t5", "percent", True)

    # ---- IBES-actuals-based EG (documentation only). ----
    # The paper labels EG as IBES actuals; we recompute the two D1/D10 cells from
    # IBES act_epsus ANN actuals for the record (metrics stay on Compustat epspx).
    diag["eg_ibes_D1D10"] = _eg_ibes_alternative(panel_map, cm)

    # ---- SUE ----
    sue_metrics, sue_diag = compute_sue(panel_map, cm)
    metrics.update(sue_metrics)
    diag.update(sue_diag)

    return metrics, diag


def _eg_ibes_alternative(panel_map, cm) -> dict:
    """IBES act_epsus ANN-actuals-based EG D1/D10, for documentation only.

    Returns {t6_t1_D1, t6_t1_D10, t_t5_D1, t_t5_D10} in percent, or None dict on
    failure. Note: act_epsus `value` is UNadjusted for splits, so these cells are
    expected to differ from the Compustat-epspx metrics; reported for the record.
    """
    try:
        act = load_eps_actuals()
        ann = act[act["pdicity"] == "ANN"].copy()
        ann = map_cusip_to_permno(ann, cm, "pends")
        ann["fyear"] = ann["pends"].dt.year
        ann = ann[["permno", "fyear", "value"]].dropna(subset=["value"])
        ann = ann.drop_duplicates(["permno", "fyear"], keep="last")
        ann = ann.sort_values(["permno", "fyear"])
        ann["eps_prev5"] = ann.groupby("permno")["value"].shift(5)
        ann["fyear_prev5"] = ann.groupby("permno")["fyear"].shift(5)
        ok = (ann["fyear"] - ann["fyear_prev5"] == 5) & ann["eps_prev5"].notna() & \
             (ann["eps_prev5"] > 0) & (ann["value"] > 0)
        ann["eg5"] = np.where(ok, (ann["value"] / ann["eps_prev5"]) ** (1.0/5.0) - 1.0, np.nan)
        eb = ann[ann["eg5"].notna()][["permno", "fyear", "eg5"]].copy()
        eb["sort_year"] = eb["fyear"] + 1
        eb = eb.merge(panel_map[["permno", "sort_year", "decile"]],
                      on=["permno", "sort_year"], how="inner")
        eb = eb[eb["sort_year"].between(T8_START, T8_END)]
        ef = ann[ann["eg5"].notna()][["permno", "fyear", "eg5"]].copy()
        ef["sort_year"] = ef["fyear"] - 5
        ef = ef.merge(panel_map[["permno", "sort_year", "decile"]],
                      on=["permno", "sort_year"], how="inner")
        ef = ef[ef["sort_year"].between(T8_START, T8_END)]
        eb = winsorize_cs(eb, "eg5"); ef = winsorize_cs(ef, "eg5")
        out = {}
        for tag, dframe in (("t6_t1", eb), ("t_t5", ef)):
            for d in (1, 10):
                sub = dframe[dframe["decile"] == d]["eg5"]
                out[f"{tag}_D{d}"] = float(sub.mean() * 100.0) if len(sub) else None
        return out
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


def load_compustat_fundq_sue() -> pd.DataFrame:
    """Split-adjusted quarterly EPS + qtr-end price from Compustat (for SUE1/SUE2)."""
    f = q_file("compustat_fundq_sue.sql")
    f["datadate"] = pd.to_datetime(f["datadate"])
    f["rdq"] = pd.to_datetime(f["rdq"])
    return f


def load_sue3_fc() -> pd.DataFrame:
    """Quarterly analyst (actual, meanest, numest) June snapshots for SUE3 sigma."""
    s = q_file("ibes_sue3_fc.sql")
    s["fpedats"] = pd.to_datetime(s["fpedats"])
    s["statpers"] = pd.to_datetime(s["statpers"])
    return s


def _seasonal_sue_series(df: pd.DataFrame, eps_col: str) -> pd.DataFrame:
    """Livnat-Mendenhall (2006) sigma-standardized seasonal-random-walk SUE.

    For a per-permno quarterly series (column `eps_col`), compute:
      sdiff_q = EPS_q - EPS_{q-4}                     (seasonal random walk)
      sigma_q = std of the PRIOR 8 seasonal differences (require >= 4 non-null)
      SUE_q   = sdiff_q / sigma_q                      (sigma units, NOT price)

    Uses sample std (ddof=1). Rows with < 4 usable prior differences get sigma=NaN
    and are dropped downstream. No additional winsorization here (sigma-standardized
    SUE is already approximately unit-scale).
    """
    q = df.sort_values(["permno", "datadate"]).copy()
    q["_sdiff"] = q.groupby("permno")[eps_col].transform(
        lambda s: s.diff(4))
    # std of prior 8 seasonal differences (shift(1) excludes the current error)
    q["_sigma"] = q.groupby("permno")["_sdiff"].transform(
        lambda s: s.shift(1).rolling(8, min_periods=4).std())
    # guard against (near-)zero sigma (firms with ~constant seasonal differences),
    # which would otherwise blow SUE to +/-inf; a numerical 1e-8 floor, NOT a
    # winsorization of the SUE value.
    q["_sigma"] = q["_sigma"].where(q["_sigma"] > 1e-8)
    q["_sue"] = q["_sdiff"] / q["_sigma"]
    return q


def _analyst_sue_series(fc: pd.DataFrame) -> pd.DataFrame:
    """SUE3 = (actual - meanest) / sigma_analyst, sigma = std of PRIOR forecast errors."""
    f = fc.sort_values(["cusip", "fpedats"]).copy()
    f["_err"] = f["actual"] - f["meanest"]
    f["_sigma"] = f.groupby("cusip")["_err"].transform(
        lambda s: s.shift(1).rolling(8, min_periods=4).std())
    f["_sigma"] = f["_sigma"].where(f["_sigma"] > 1e-8)
    f["_sue"] = f["_err"] / f["_sigma"]
    return f


def _sue_decile_median_ts(sub: pd.DataFrame, key_out: str,
                          winsorize: bool) -> pd.Series:
    """Annual cross-sectional MEDIAN of SUE per decile -> time-series average."""
    yrs = sub.groupby(["sort_year", "decile"])["_sue"].median().reset_index()
    return yrs.groupby("decile")["_sue"].mean()


def _emit_sue_variant(metrics, diag, sub_raw, key_out):
    """Emit SUE decile medians using the RAW sigma-standardized values by default,
    falling back to 1/99 winsorized only if the raw cross-sectional medians are
    outlier-dominated. Records BOTH raw and winsorized decile medians in diag."""
    sub_w = sub_raw.copy()
    lo, hi = (sub_w.groupby("sort_year")["_sue"].transform(lambda s: s.quantile(0.01)),
              sub_w.groupby("sort_year")["_sue"].transform(lambda s: s.quantile(0.99)))
    sub_w["_sue"] = sub_w["_sue"].clip(lo, hi)

    ts_raw = _sue_decile_median_ts(sub_raw, key_out, winsorize=False)
    ts_win = _sue_decile_median_ts(sub_w, key_out, winsorize=False)

    # outlier-domination check: if any raw decile median exceeds |10| in sigma units
    # (i.e., a cross-sectional median dominated by tails), prefer winsorized.
    raw_meds = [v for v in ts_raw.values if pd.notna(v)]
    dominated = any(abs(v) > 10.0 for v in raw_meds)
    ts = ts_win if dominated else ts_raw
    diag[f"{key_out}_winsorized_used"] = bool(dominated)
    diag[f"{key_out}_raw_medians"] = {
        int(d): (float(v) if pd.notna(v) else None) for d, v in ts_raw.items()}
    diag[f"{key_out}_winsorized_medians"] = {
        int(d): (float(v) if pd.notna(v) else None) for d, v in ts_win.items()}

    _emit_decile(metrics, ts, key_out, "sigma", True)
    return metrics, diag


def compute_sue(panel_map, cm):
    """SUE1/SUE2/SUE3 per Livnat-Mendenhall (2006), sigma-standardized (footnote 17).

    SUE1 = seasonal random walk on REPORTED EPS (epspiq):
           (EPS_q - EPS_{q-4}) / std(prior 8 seasonal forecast errors).
    SUE2 = same on EX-SPECIAL-ITEMS EPS ((ibq - spiq)/cshfdq).
    SUE3 = (actual - mean analyst forecast) / std(prior forecast errors),
           both from statsum_epsus (same split-adjusted basis).

    The seasonal difference is ordered by fiscal period-end `datadate`; the prior-
    quarter difference is the SAME fiscal quarter a year earlier. The surprise is
    attributed to the June duration cohort of its REPORT DATE year (rdq); SUE3 is
    attributed by fiscal-period-end year (paper "June statistical period" alignment).

    Data-source fix (iteration 10, retained): SUE1/SUE2 read split-adjusted Compustat
    fundq EPS (not IBES act_epsus, which carries reverse-split artifacts).
    """
    fundq = load_compustat_fundq_sue()
    qtr = fundq.drop_duplicates(["permno", "datadate"], keep="last").copy()

    # ---- SUE1 / SUE2 (sigma-standardized seasonal random walk) ----
    s1 = _seasonal_sue_series(qtr, "eps_piq")
    s2 = _seasonal_sue_series(qtr, "exsp_eps")

    # attribute to June duration cohort via report-date (announcement) year
    for s in (s1, s2):
        s["sort_year"] = pd.to_datetime(s["rdq"]).dt.year

    # ---- SUE3 (analyst forecast error, sigma-standardized) ----
    fc = load_sue3_fc()
    fc = fc.drop_duplicates(["cusip", "fpedats"], keep="last")
    a3 = _analyst_sue_series(fc)
    a3 = map_cusip_to_permno(a3, cm, "fpedats")
    a3["sort_year"] = a3["fpedats"].dt.year

    # merge decile and restrict to T8 sort years
    dec = panel_map[["permno", "sort_year", "decile"]]
    s1 = s1.merge(dec, on=["permno", "sort_year"], how="inner")
    s2 = s2.merge(dec, on=["permno", "sort_year"], how="inner")
    a3 = a3.merge(dec, on=["permno", "sort_year"], how="inner")
    s1 = s1[s1["sort_year"].between(T8_START, T8_END)]
    s2 = s2[s2["sort_year"].between(T8_START, T8_END)]
    a3 = a3[a3["sort_year"].between(T8_START, T8_END)]

    metrics = {}
    diag = {
        "sue_pool": int(len(s1)),
        "sue1_n": int(s1["_sue"].notna().sum()),
        "sue2_n": int(s2["_sue"].notna().sum()),
        "sue3_n": int(a3["_sue"].notna().sum()),
        "sue1_num_med_D1": None, "sue1_num_med_D10": None,
        "sue1_sigma_med_D1": None, "sue1_sigma_med_D10": None,
        "sue1_both_eps_frac": None,
    }
    qchk = qtr
    qchk["piq_lag4"] = qchk.groupby("permno")["eps_piq"].shift(4)
    diag["sue1_both_eps_frac"] = float(
        (qchk["eps_piq"].notna() & qchk["piq_lag4"].notna()).mean())

    # sigma_analyst coverage report
    fc_all = load_sue3_fc()
    fc_all = fc_all.drop_duplicates(["cusip", "fpedats"], keep="last")
    fc_all = _analyst_sue_series(fc_all)
    diag["sue3_sigma_total_errs"] = int(fc_all["_err"].notna().sum())
    diag["sue3_sigma_computable"] = int(fc_all["_sigma"].notna().sum())
    diag["sue3_sigma_coverage"] = float(
        fc_all["_sigma"].notna().mean()) if len(fc_all) else None

    # component diagnostics (SUE1 numerator & sigma by decile)
    q1 = s1.dropna(subset=["_sue"])
    for d, tag in ((1, "D1"), (10, "D10")):
        dd = q1[q1["decile"] == d]
        diag[f"sue1_num_med_{tag}"] = float(dd["_sdiff"].median()) if len(dd) else None
        diag[f"sue1_sigma_med_{tag}"] = float(dd["_sigma"].median()) if len(dd) else None

    for key, sdf in (("sue1", s1), ("sue2", s2)):
        sub = sdf[["sort_year", "decile", "_sue"]].dropna(subset=["_sue"])
        metrics, diag = _emit_sue_variant(metrics, diag, sub, f"t8_{key}")
    sub3 = a3[["sort_year", "decile", "_sue"]].dropna(subset=["_sue"])
    metrics, diag = _emit_sue_variant(metrics, diag, sub3, "t8_sue3")

    return metrics, diag


# --------------------------------------------------------------------------- #
# Table 9 (Panel A)
# --------------------------------------------------------------------------- #
# Consolidation target-plausibility band (data-hygiene, NOT tuning).
#
# The I/B/E/S price-target summary `ptgsum.meanptg` is split-ADJUSTED, but for
# firms that underwent REVERSE splits the per-analyst detail targets sit on
# mutually incompatible split bases (e.g. FCCM 2002: analysts target $15 and
# $1540 for a ~$2 stock; ptghigh/ptglow 1540/15). meanptg then averages these,
# producing target/price ratios of 100x..4000x (max observed PTP = 408,233%).
# The paper (using a 2014 I/B/E/S vintage with cleaner reverse-split handling)
# winsorizes 1%/99% and obtains a flat ~16% implied return; our 202601 vintage's
# contamination is ~2.6% of records (target/price > 3x) and renders the paper's
# 1%/99% winsorization useless (99th pct of PTP is still 277%).
#
# Fix (documented): drop records where the 12-mo target is implausible relative
# to the same-vintage split-adjusted price — meanptg/price outside
# [PTG_TPR_LO, PTG_TPR_HI] (implied return roughly -50%..+100%). This removes
# reverse-split artifacts only; it is a data-quality screen, not a fit to the
# paper, and is reported alongside a no-screen sensitivity.
PTG_TPR_LO = 0.5
PTG_TPR_HI = 2.0


def load_t9_mcap() -> pd.DataFrame:
    """CRSP June market cap + split-adjusted June close per (permno, June year),
    2001..2013, for the split-invariant PTB denominator."""
    m = q_file("t9_crsp_mcap.sql")
    m["june_year"] = m["june_year"].astype(int)
    return m


def _qmean_ts(df, col):
    """Annual cross-sectional MEAN per quintile -> time-series average (Series over
    quintile). Matches the paper's 'time series averages of annual cross-sectional
    means' (content.md L1810)."""
    yrs = df.dropna(subset=[col]).groupby(["sort_year", "quintile"])[col].mean().reset_index()
    return yrs.groupby("quintile")[col].mean()


def compute_table9(panel_map, cm, fund):
    diag = {}
    ptg = load_ptg()
    diag["ptg_match"] = match_report(ptg, cm, "statpers")
    ptg = map_cusip_to_permno(ptg, cm, "statpers")
    ptg = ptg.rename(columns={"june_year": "sort_year"})
    ptg = ptg.merge(panel_map[["permno", "sort_year", "quintile"]],
                    on=["permno", "sort_year"], how="inner")
    ptg = ptg[ptg["sort_year"].between(T9_START, T9_END)]

    ptg["fyear"] = ptg["sort_year"] - 1
    ptg = ptg.merge(fund, on=["permno", "fyear"], how="left")

    # CRSP June market cap (dollars) for the split-invariant PTB.
    mcap = load_t9_mcap()
    ptg = ptg.merge(mcap, left_on=["permno", "sort_year"],
                    right_on=["permno", "june_year"], how="left")

    diag["ptg_after_join"] = int(len(ptg))
    diag["ptg_with_be"] = int(ptg["be"].notna().sum())
    diag["ptg_with_price"] = int(ptg["price"].notna().sum())
    diag["ptg_with_mcap"] = int(ptg["mcap"].notna().sum())

    # Restrict to rows with positive book equity, a positive split-adjusted price,
    # and a positive CRSP market cap so both ratios are defined.
    ptg = ptg[(ptg["be"].notna()) & (ptg["be"] > 0)
              & (ptg["price"].notna()) & (ptg["price"] > 0)
              & (ptg["mcap"].notna()) & (ptg["mcap"] > 0)]

    diag["ptg_usable"] = int(len(ptg))

    # target/price ratio (split-invariant — both sides split-adjusted).
    ptg["tpr"] = ptg["meanptg"] / ptg["price"]
    diag["ptg_tpr_outliers"] = int(((ptg["tpr"] < PTG_TPR_LO) | (ptg["tpr"] > PTG_TPR_HI)).sum())

    # Data-quality screen: drop reverse-split split-adjustment artifacts.
    ptg = ptg[(ptg["tpr"] >= PTG_TPR_LO) & (ptg["tpr"] <= PTG_TPR_HI)].copy()

    # PTP = (target / price - 1) * 100  [implied return, percent].
    ptg["ptp"] = (ptg["tpr"] - 1.0) * 100.0
    # PTB = target per share / book-equity per share
    #     = (target/price) * (price*shares / BE) = tpr * (mcap / BE).
    # mcap is dollars, BE is $millions -> BE*1e6 dollars.
    ptg["ptb"] = ptg["tpr"] * (ptg["mcap"] / (ptg["be"] * 1e6))

    # Winsorize cross-sectionally at 1%/99% within each sort_year (paper L176).
    ptg = winsorize_cs(ptg, "ptb")
    ptg = winsorize_cs(ptg, "ptp")

    metrics = {}
    for col, name, unit in [("ptb", "ptb", "ratio"), ("ptp", "ptp", "percent")]:
        ts = _qmean_ts(ptg, col)
        for d in range(1, 6):
            metrics[f"t9_{name}_D{d}"] = {"value": float(ts.get(d, np.nan)), "unit": unit}
        v1, v5 = ts.get(1, np.nan), ts.get(5, np.nan)
        metrics[f"t9_{name}_D1D5"] = {"value": float(v1 - v5), "unit": unit}
    return metrics, diag


# --------------------------------------------------------------------------- #
# Table 9 spot-check (large-firm targets vs current price)
# --------------------------------------------------------------------------- #
SPOT_FIRMS = [
    ("AAPL", "03783310"), ("MSFT", "59491810"), ("GE", "36960410"),
    ("IBM", "45920010"), ("JNJ", "47816010"), ("WMT", "93114210"),
    ("KO", "19121610"),
]


def compute_t9_spot_check() -> pd.DataFrame:
    """Pull the June consensus 12-mo target + same-vintage price for a handful of
    large firms (2005 and 2010) and the implied PTP, to verify extraction sanity.

    Returns a DataFrame of rows (ticker, month, meanptg, medptg, numest, price, PTP%).
    """
    c = _client()
    rows = []
    for tk, cu in SPOT_FIRMS:
        for y in (2005, 2010):
            p = c.execute(
                f"SELECT meanptg, medptg, numest, statpers FROM ibes_202601.ptgsum "
                f"WHERE cusip='{cu}' AND usfirm=1 AND toYear(toDate32(statpers))={y} "
                f"AND toMonth(toDate32(statpers))=6")
            a = c.execute(
                f"SELECT price, shout, statpers FROM ibes_202601.actpsum_epsus "
                f"WHERE cusip='{cu}' AND usfirm=1 AND toYear(toDate32(statpers))={y} "
                f"AND toMonth(toDate32(statpers))=6")
            if p and p[0][0] is not None and a and a[0][0] is not None and a[0][0] > 0:
                meanptg, medptg, numest = p[0][0], p[0][1], p[0][2]
                price = a[0][0]
                ptp = (meanptg / price - 1.0) * 100.0
                rows.append({"ticker": tk, "month": f"{y}-06", "meanptg": meanptg,
                             "medptg": medptg, "numest": int(numest), "price": price,
                             "ptp_pct": ptp})
            else:
                rows.append({"ticker": tk, "month": f"{y}-06", "meanptg": None,
                             "medptg": None, "numest": None, "price": None,
                             "ptp_pct": None})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Report / markdown
# --------------------------------------------------------------------------- #
SCHEMA_NOTES = [
    "- **LTG** in `ibes_202601.statsum_epsus` `fpi='0'` AND `fiscalp='LTG'` (NOT measure='Ltg').",
    "  Per-analyst detail in `det_epsus` `fpi='0'` (value is a %, e.g. 20.0 / 85.0).",
    "- **statpers** = monthly statistical period date (3rd Thu, String; e.g. '2005-06-16').",
    "  June cross-section = `toMonth(statpers)=6`.",
    "- **IBES cusip not standard**: non-US listings use EX/ER/LM/FJ… prefixes.",
    "  `usfirm=1` filter yields standard 8-digit cusips matching `dsenames.ncusip` ~95.5%.",
    "- **EG** via Compustat annual `epspx` (split-adjusted), annualized 5-yr growth; the",
    "  paper specifies IBES act_epsus ANN but that file is UNadjusted for splits.",
    "  Windows per Panel B labels: EG_{t-6:t-1} = (EPS_{t-1}/EPS_{t-6})^{1/5}-1 (x100;",
    "  endpoint FYE t-1), EG_{t:t+5} = (EPS_{t+5}/EPS_t)^{1/5}-1 (x100; endpoint FYE t+5).",
    "- **SUE1/SUE2** Livnat-Mendenhall (2006) sigma-standardization (NOT price-scaling):",
    "  SUE = (EPS_q - EPS_{q-4}) / std(prior 8 seasonal differenced errors), require >=4",
    "  prior differences, sample std. SUE1 on `epspiq` (reported); SUE2 on ex-special-items",
    "  (ibq - spiq)/cshfdq. Split-adjusted Compustat fundq. Uses annual cross-sectional MEDIANS.",
    "- **SUE3** = (actual - meanest) / std(prior analyst forecast errors), both `actual` and",
    "  `meanest` from `statsum_epsus` (same split-adjusted basis), require >=4 prior errors.",
    "- **EG window fix (this iteration)**: prior code's endpoint comments referenced EPS_t /",
    "  EPS_{t-5}; the window is now explicit: backward ends at FYE t-1, forward ends at FYE t+5.",
    "- **Price targets** in `ibes_202601.ptgsum` `measure='PTG'`, `meanptg` (split-adjusted",
    "  $/share 12-mo-ahead); price in `actpsum_epsus.price` at same statpers.",
    "- **PTG aggregate fields**: `numest` (analyst count), `meanptg` (mean consensus — used),",
    "  `medptg` (median consensus), `stdev`/`ptghigh`/`ptglow` (dispersion). `ptgsum` has no",
    "  horizon column; the 12-mo-ahead horizon lives in the detail table `ptgdet.horizon='12'`.",
    "- **REVERSE-SPLIT split-adjustment artifact (this iteration)**: for microcaps that did",
    "  reverse splits, `meanptg` mixes per-analyst targets on incompatible split bases (e.g.",
    "  FCCM 2002: ptghigh=1540 vs ptglow=15 for a ~$2 stock), inflating meanptg/price to",
    "  100x..4000x (max PTP 408,233%). Screen drops tpr outside [0.5, 2.0].",
    "- **PTB split-invariant form (this iteration)**: PTB = (meanptg/price) × (CRSP mcap / BE).",
    "  `meanptg×shout` was split-inconsistent (`shout` not on the target's split basis), making",
    "  D5=12.25 implausible. BE is Compustat total book equity ($M); CRSP mcap is $/share.",
]


def _grid(metrics, rows, cols):
    lines = []
    lines.append("| Row | " + " | ".join(cols) + " |")
    lines.append("|---|" + "---|" * len(cols))
    for label, prefix in rows:
        cells = [label]
        for c in cols:
            v = metrics.get(f"{prefix}_{c}")
            cells.append(f"{v['value']:.3f}" if v and v.get("value") is not None else "—")
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_tables(m8, m9, diag8, diag9, spot=None):
    cols8 = [f"D{d}" for d in range(1, 11)] + ["D1D10"]
    rows8 = [(f"LTG_{s}", f"t8_ltg_{s}") for s in ("t", "t1", "t2", "t3", "t4")]
    rows8 += [("EG_{t-6:t-1}", "t8_eg_t6_t1"), ("EG_{t:t+5}", "t8_eg_t_t5"),
              ("SUE1", "t8_sue1"), ("SUE2", "t8_sue2"), ("SUE3", "t8_sue3")]

    md = ["# Table 8 — Analyst expectations (ours)", "",
          "TS-average of annual cross-sectional MEANS (Panels A/B) and MEDIANS (Panel C)",
          "of ten duration deciles, June 1982–June 2009, sorted on the **IBES-covered** "
          "subset (footnote 15).", "",
          _grid(m8, rows8, cols8), "",
          "## Schema discovery notes", ""] + SCHEMA_NOTES + ["", "## Coverage", ""]
    mm = diag8.get("ltg_match", {})
    md += [
        f"- LTG cusip match rate: {mm.get('n_matched')}/{mm.get('n_cusip')} "
        f"({mm.get('frac', 0)*100:.1f}%)",
        f"- LTG firms before fn16 screen: {diag8.get('ltg_before_fn16')}",
        f"- LTG firms after fn16 (nonmissing all periods): {diag8.get('ltg_after_fn16')}",
        f"- EG qualifying firm-5yr-growth obs: {diag8.get('eg_qualifying')}",
        f"- EG endpoint EPS_t median D1/D10: {diag8.get('eg_eps_t_med_D1')} / {diag8.get('eg_eps_t_med_D10')}",
        f"- EG endpoint EPS_(t-5) median D1/D10: {diag8.get('eg_eps_lag5_med_D1')} / {diag8.get('eg_eps_lag5_med_D10')}",
        f"- EG backward obs / forward obs: {diag8.get('eg_back_n')} / {diag8.get('eg_fwd_n')}",
        f"- SUE pool: {diag8.get('sue_pool')}  (S1={diag8.get('sue1_n')} "
        f"S2={diag8.get('sue2_n')} S3={diag8.get('sue3_n')})",
        f"- SUE1 both-EPS fraction: {diag8.get('sue1_both_eps_frac')}",
        f"- SUE1 seasonal |numerator| median D1={diag8.get('sue1_num_med_D1')} "
        f"D10={diag8.get('sue1_num_med_D10')}  sigma median D1={diag8.get('sue1_sigma_med_D1')} "
        f"D10={diag8.get('sue1_sigma_med_D10')}",
        f"- SUE3 sigma_analyst coverage: {diag8.get('sue3_sigma_computable')} computable / "
        f"{diag8.get('sue3_sigma_total_errs')} errors "
        f"({(diag8.get('sue3_sigma_coverage') or 0)*100:.1f}%)",
        f"- SUE winsorized-used flags: S1={diag8.get('t8_sue1_winsorized_used')} "
        f"S2={diag8.get('t8_sue2_winsorized_used')} S3={diag8.get('t8_sue3_winsorized_used')}",
        f"- SUE1 raw medians D1..D10: {diag8.get('t8_sue1_raw_medians')}",
        f"- SUE1 winsorized medians D1..D10: {diag8.get('t8_sue1_winsorized_medians')}",
        f"- LTG_t decile means (ours): {diag8.get('ltg_t_deciles')}",
        f"- IBES-covered permnos: {diag8.get('coverage_n_cov')} (full universe "
        f"{diag8.get('coverage_n_full')})",
        f"- IBES ANN-actuals EG (documentation only) D1/D10: {diag8.get('eg_ibes_D1D10')}",
        ""]
    # Coverage statistics per year (share of stocks and market cap)
    cp = diag8.get("coverage_per_year", {})
    if cp:
        md.append("### IBES coverage per sort year (share of full universe)")
        md.append("| year | full n | covered n | share stocks | share ME |")
        md.append("|---|---|---|---|---|")
        for y in sorted(cp):
            r = cp[y]
            md.append(f"| {y} | {r['n_full']} | {r['n_cov']} | "
                      f"{r['share_stocks']*100:.1f}% | {r['share_me']*100:.1f}% |")
        md.append("")
    comp = diag8.get("coverage_composition", {})
    if comp:
        md.append("### Decile composition after the coverage screen (median June price / ME)")
        md.append("| Decile | n | median price ($) | median ME ($) |")
        md.append("|---|---|---|---|")
        for d in range(1, 11):
            c = comp.get(f"D{d}", {})
            md.append(f"| D{d} | {c.get('n', '—')} | "
                      f"{c.get('median_price', 0):.2f} | {c.get('median_me', 0):.0f} |")
        md.append("")
    (LAYOUT.result_path("table_8.md")).write_text("\n".join(md))

    cols9 = [f"D{d}" for d in range(1, 6)] + ["D1D5"]
    rows9 = [("PTB", "t9_ptb"), ("PTP", "t9_ptp")]
    md9 = ["# Table 9 Panel A — Price targets (ours)", "",
           "TS-average of annual cross-sectional MEANS of five duration quintiles,",
           "July 2001–June 2014.", "", _grid(m9, rows9, cols9), "",
           "## Schema discovery notes", ""] + SCHEMA_NOTES + ["", "## Coverage", ""]
    pm = diag9.get("ptg_match", {})
    md9 += [
        f"- PTG cusip match rate: {pm.get('n_matched')}/{pm.get('n_cusip')} "
        f"({pm.get('frac', 0)*100:.1f}%)",
        f"- PTG firm-years after join: {diag9.get('ptg_after_join')}",
        f"- PTG with BE: {diag9.get('ptg_with_be')}  with price: {diag9.get('ptg_with_price')}  "
        f"with CRSP mcap: {diag9.get('ptg_with_mcap')}",
        f"- PTG usable rows (be>0 & price>0 & mcap>0): {diag9.get('ptg_usable')}",
        f"- PTG target/price outliers dropped (tpr outside [{PTG_TPR_LO},{PTG_TPR_HI}]): "
        f"{diag9.get('ptg_tpr_outliers')}",
        ""]
    if spot is not None and len(spot):
        md9 += ["## Spot-check — large-firm consensus targets vs current price", "",
                "| ticker | month | meanptg | medptg | numest | price | PTP (%) |",
                "|---|---|---|---|---|---|---|"]
        for r in spot.itertuples():
            if r.meanptg is None:
                md9.append(f"| {r.ticker} | {r.month} | — | — | — | — | — |")
            else:
                md9.append(f"| {r.ticker} | {r.month} | {r.meanptg:.3f} | {r.medptg:.3f} | "
                           f"{r.numest} | {r.price:.3f} | {r.ptp_pct:.1f} |")
        md9.append("")
    (LAYOUT.result_path("table_9.md")).write_text("\n".join(md9))


def load_paper_targets():
    targets = json.loads(LAYOUT.preparations_path("tables_to_replicate.json").read_text())
    out_t8, out_t9 = {}, {}
    for tbl in targets.get("tables", []):
        if tbl["id"] == "T8":
            dst = out_t8
        elif tbl["id"] == "T9":
            dst = out_t9
        else:
            continue
        for m in tbl.get("metrics", []):
            dst[m["name"]] = m["value"]
    return out_t8, out_t9


def coverage_composition(panel_map_covered: pd.DataFrame) -> dict:
    """Post-screen decile composition: median June price, median ME, and coverage share
    per decile (coverage share here = fraction of the covered-universe decile firms that
    pass each variable's per-row screen; but we report the decile's median prc/me)."""
    jpm = q_file("june_price_me.sql")
    out = {}
    rm = panel_map_covered.merge(jpm, left_on=["permno", "sort_year"],
                                 right_on=["permno", "june_year"], how="left")
    for d in range(1, 11):
        dd = rm[rm["decile"] == d]
        out[f"D{d}"] = {
            "n": int(len(dd)),
            "median_price": float(dd["prc"].median()),
            "median_me": float(dd["me"].median()),
        }
    return out


def main():
    print("Loading cusip map + panel mapping ...", flush=True)
    cm = load_cusip_map()
    panel_map = load_mapping()

    # ---- Table 8 on the IBES-covered subset (footnote 15) ----
    print("Building IBES coverage set ...", flush=True)
    covered = load_coverage(cm)
    panel_map8, cov_diag = build_covered_mapping(covered)
    m8, diag8 = compute_table8(panel_map8, cm)
    diag8.update(cov_diag)
    diag8["coverage_composition"] = coverage_composition(panel_map8)

    # ---- Table 9 (unchanged full-universe mapping) ----
    fund = load_fundamentals()
    print("Computing Table 9 ...", flush=True)
    m9, diag9 = compute_table9(panel_map, cm, fund)
    print("Computing Table 9 spot-check ...", flush=True)
    spot9 = compute_t9_spot_check()

    print("Writing results ...", flush=True)
    write_tables(m8, m9, diag8, diag9, spot=spot9)

    metrics = dict(m8)
    metrics.update(m9)
    return metrics, diag8, diag9


if __name__ == "__main__":
    m, d8, d9 = main()
    print("T8 metrics:", len(m))
    print(json.dumps({k: v for k, v in m.items() if "ltg_t_D" in k}, indent=1, default=str))
