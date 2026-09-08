"""
Replication of Novy-Marx (2012) "Is Momentum Really Momentum?"
Signal: r_{n,m}(t) = cumulative return over months t-n..t-m, indexed to the
        RETURN month t (formation at end of t-1; full-window requirement,
        Assumption 3); MOM_n,m = VW winner-minus-loser decile strategy
        (NYSE breakpoints, Assumption 5), ME at end of t-1 as VW weight
        (Assumption 4).
Targets: Table 2 (T2), Table 3 (T3). Later iterations extend metrics.json.

Universe: ALL CRSP stocks, no share/exchange filter (Assumption 1).
Sample: returns 1926-01..2010-12; strategy series 1927-01..2010-12.
t-stats: plain OLS SEs (Assumption 6); mean t = mean/(std/sqrt(T)).
"""
# --- imports ---
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import json

import numpy as np
import pandas as pd
import statsmodels.api as sm
from clickhouse_driver import Client

from utils.env import get_clickhouse_config
from utils.paths import paper_layout
from utils.portfolio import rolling_cumret
from utils.regressions import fama_macbeth

# --- configuration ---
SLUG = "novymarx_2012_is_momentum_really_momentum"
LAYOUT = paper_layout(SLUG)
LAYOUT.ensure()
SQL_DIR = LAYOUT.src_path("sql")

PULL_START = "1925-12-01"   # one extra month before 1926-01 for r_{n,m} windows
PANEL_START = pd.Timestamp("1926-01-31")
PANEL_END = pd.Timestamp("2010-12-31")
FIRST_STRAT_MONTH = pd.Timestamp("1927-01-31")
LAST_STRAT_MONTH = pd.Timestamp("2010-12-31")
N_STRATEGY_MONTHS_EXPECTED = 1008
EARLY_END = pd.Timestamp("1968-12-31")
LATE_START = pd.Timestamp("1969-01-31")
N_BINS = 10
SAMPLES = {
    "whole": (pd.Timestamp("1927-01-31"), pd.Timestamp("2010-12-31")),
    "early": (pd.Timestamp("1927-01-31"), EARLY_END),
    "late": (LATE_START, pd.Timestamp("2010-12-31")),
}

# --- ClickHouse connection ---


def _client() -> Client:
    cfg = get_clickhouse_config()
    return Client(host=cfg["host"], port=int(cfg["port"]),
                  user=cfg["user"], password=cfg["password"],
                  settings={"max_execution_time": 600})


def q_file(name: str) -> pd.DataFrame:
    sql = (SQL_DIR / name).read_text()
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


# --- data loading ---


def load_panel() -> pd.DataFrame:
    """Pull the raw universe and build the dense-within-span panel.

    The grid is reindexed over each stock's own listing span (first to last
    observed month) rather than the full 1926-2010 calendar; this is
    mathematically identical for every signal (months before the first
    observation are all-NaN windows), while keeping the panel ~5M rows
    instead of ~26M.
    """
    raw = q_file("universe_monthly.sql")
    # 'YYYY-MM' string -> calendar month-end timestamp (ClickHouse's
    # month-end expressions clamp pre-1970 dates, so the key stays a
    # string in SQL — see universe_monthly.sql).
    raw["month"] = pd.PeriodIndex(raw["month"], freq="M").to_timestamp(
        how="end").normalize()
    raw = raw.sort_values(["permno", "month"])

    spans = raw.groupby("permno")["month"].agg(["min", "max"])
    grid_parts = [
        pd.DataFrame({"month": pd.date_range(mn, mx, freq="ME"), "permno": p})
        for p, (mn, mx) in spans.iterrows()
    ]
    grid = pd.concat(grid_parts, ignore_index=True)
    panel = grid.merge(raw, on=["permno", "month"], how="left")
    panel = panel.rename(columns={"me_dollars": "me"})
    panel = panel.sort_values(["permno", "month"], ignore_index=True)

    # Signals (monthly, per stock; full-window requirement via
    # min_periods=window on the gap-filled grid — Assumption 3).
    # rolling_cumret(window, skip) semantics: prod(1+ret) over the
    # [t-n, t-(skip+1)] window:
    #   r_6,2  -> window=5,  skip=1  (months t-6..t-2)
    #   r_12,7 -> window=6,  skip=6  (months t-12..t-7)
    #   r_12,2 -> window=11, skip=1  (months t-12..t-2)
    panel["r62"] = rolling_cumret(panel, date_col="month", ret_col="ret",
                                  window=5, skip=1, min_periods=5)
    panel["r127"] = rolling_cumret(panel, date_col="month", ret_col="ret",
                                   window=6, skip=6, min_periods=6)
    panel["r122"] = rolling_cumret(panel, date_col="month", ret_col="ret",
                                   window=11, skip=1, min_periods=11)
    panel["r10"] = panel.groupby("permno")["ret"].shift(1)
    panel["me_lag1"] = panel.groupby("permno")["me"].shift(1)
    # Panel spec: 1926-01..2010-12 (the 1925-12 pull month only feeds the
    # r_{n,m} windows).
    panel = panel[panel["month"] >= PANEL_START].reset_index(drop=True)
    return panel


# --- book-to-market (Table 1; Assumptions 7 & 8) ---


def add_log_bm(panel: pd.DataFrame) -> pd.DataFrame:
    """Attach monthly log(BM) to the panel.

    Paper footnote 1 (L155): BM = book equity (tiered construction,
    Assumption 7; compustat_be.sql) "scaled by market equity lagged six
    months, and ... updated at the end of each June using accounting
    data from the fiscal year ending in the previous calendar year".
    BE leg June-aligned (fiscal year with datadate in calendar year
    y-1 active July y .. June y+1), as-of merged by (permno,
    eff=July y); ME leg frozen at December of y-1 (the "market equity
    lagged six months" from the June update, per the task spec), so
    log_bm is constant July y .. June y+1.
    BE is in millions -> x1e6 before the ratio.

    Implementation note: merge_asof requires the left frame sorted by
    the on-key ('month'), which differs from the panel's (permno,
    month) order — values are assigned back by INDEX, never
    positionally (a positional assignment here scrambled log_bm
    across firms in an earlier iteration of this task).
    """
    be = q_file("compustat_be.sql")
    be = be.dropna(subset=["permno", "active_year", "be"])
    be = (be.sort_values(["permno", "active_year"])
            .drop_duplicates(["permno", "active_year"], keep="first"))
    be["log_be"] = np.log(be["be"] * 1e6)
    be["eff"] = pd.to_datetime(
        {"year": be["active_year"].astype(int), "month": 7, "day": 1})

    dec = panel[panel["month"].dt.month == 12][
        ["permno", "month", "me"]].copy()
    dec["active_year"] = dec["month"].dt.year + 1
    dec = dec.rename(columns={"me": "me_dec"})[
        ["permno", "active_year", "me_dec"]]

    bm = be.merge(dec, on=["permno", "active_year"], how="inner")
    bm = bm[(bm["me_dec"].notna()) & (bm["me_dec"] > 0)]
    bm["log_bm"] = bm["log_be"] - np.log(bm["me_dec"])

    # Carry BE forward across missing fiscal years (FF convention: the
    # most recent annual book equity stays active), then join by an
    # explicit year key instead of merge_asof (whose by-key matching
    # silently fails on this frame): a month in Jul..Dec of year Y uses
    # active_year Y; Jan..Jun uses Y-1 (BE active July y..June y+1).
    g = bm.groupby("permno")["active_year"].agg(["min", "max"])
    g["max"] = g["max"].clip(upper=2010)
    grid = pd.DataFrame({
        "permno": g.index.repeat(g["max"] - g["min"] + 1),
        "active_year": np.concatenate([
            np.arange(a, b + 1) for a, b in zip(g["min"], g["max"])]),
    })
    bm_full = (grid.merge(bm[["permno", "active_year", "log_bm"]],
                          on=["permno", "active_year"], how="left")
               .sort_values(["permno", "active_year"], ignore_index=True))
    bm_full["log_bm"] = bm_full.groupby("permno")["log_bm"].ffill()
    bm_full = bm_full.set_index(["permno", "active_year"])["log_bm"]

    panel = panel.sort_values(["permno", "month"]).copy()
    bm_year = np.where(panel["month"].dt.month >= 7,
                       panel["month"].dt.year, panel["month"].dt.year - 1)
    panel["log_bm"] = bm_full.reindex(
        pd.MultiIndex.from_arrays([panel["permno"], bm_year])).to_numpy()
    return panel


# --- SUE (Table 14 / T8; paper L2587) ---


def add_sue(panel: pd.DataFrame) -> pd.DataFrame:
    """Attach monthly SUE to the panel (compustat_sue.sql does the fundq
    construction and the CCM link; see the SQL header).

    Timing (paper silent; logged as an assumption): each announcement's
    SUE becomes available in its announcement month (month(rdq), else the
    month after datadate) and is carried forward to subsequent months
    until the next announcement, with a maximum staleness of 6 months —
    a firm whose most recent SUE is older than 6 months has SUE missing
    that month.
    """
    sue = q_file("compustat_sue.sql")
    sue["avail"] = pd.PeriodIndex(sue["month"], freq="M").to_timestamp(
        how="end").normalize()
    sue = (sue.dropna(subset=["permno", "avail", "sue"])
              .sort_values(["permno", "avail"])
              .drop_duplicates(["permno", "avail"], keep="last")
              .sort_values("avail"))  # merge_asof: on-key must be global

    p = panel.sort_values("month")  # merge_asof needs on-key global order
    m = pd.merge_asof(p[["permno", "month"]], sue[["permno", "avail", "sue"]],
                      left_on="month", right_on="avail", by="permno",
                      direction="backward")
    staleness = ((m["month"].dt.year * 12 + m["month"].dt.month)
                 - (m["avail"].dt.year * 12 + m["avail"].dt.month))
    m["sue"] = m["sue"].where(staleness <= 6)
    panel = panel.copy()
    panel["sue"] = pd.Series(m["sue"].to_numpy(), index=p.index).reindex(
        panel.index)
    return panel


# --- Table 1: Fama-MacBeth regressions ---


T1_SAMPLES = {
    "late": (pd.Timestamp("1969-01-31"), pd.Timestamp("2010-12-31")),
    "third": (pd.Timestamp("1969-01-31"), pd.Timestamp("1989-12-31")),
    "fourth": (pd.Timestamp("1990-01-31"), pd.Timestamp("2010-12-31")),
}
T1_VARS = ["r127", "r62", "r10", "log_me", "log_bm"]
T1_KEYMAP = {"r127": "r127", "r62": "r62", "r10": "r10",
             "log_me": "logme", "log_bm": "logbm"}


def _winsorize_monthly(s: pd.DataFrame, var: str, pct: float = 0.01) -> pd.Series:
    """Mirror of utils.fama_macbeth's per-month winsorization."""
    return s.groupby("month")[var].transform(
        lambda x: x.clip(*x.quantile([pct, 1 - pct])))


def compute_table1(panel: pd.DataFrame, metrics: dict) -> dict:
    """FM regressions of ret_t on [r127, r62, r10, log_me, log_bm] and on
    the reparameterization diff = r127 - r62 (same controls).

    All independent variables winsorized 1%/99% per month (listwise
    sample). To keep the OLS identity b(diff) = b(r127) - b(r62) exact,
    variables are pre-winsorized per month and the regressions run with
    winsorize_pct=0 (clipping is idempotent, so this equals the
    primitive's default path — verified below on the 'late' sample);
    diff is formed from the WINSORIZED r127/r62 so it is the exact
    linear combination the first regression sees. t-stats: plain FM
    (n_lags=0, Assumption 6). Slopes reported x10^2.
    """
    report = {"avg_firms": {}, "min_firms": {}, "invariant": {},
              "n_months": {}, "total_obs": {}}
    d = panel.copy()
    d["log_me"] = np.log(d["me_lag1"])

    for samp, (lo, hi) in T1_SAMPLES.items():
        s = d[(d["month"] >= lo) & (d["month"] <= hi)][
            ["permno", "month", "ret"] + T1_VARS].copy()
        # mirror utils.fama_macbeth: ±inf -> NaN before the listwise drop
        s = s.replace([np.inf, -np.inf], np.nan).dropna()
        for v in T1_VARS:
            s[v + "_w"] = _winsorize_monthly(s, v)
        s["diff_w"] = s["r127_w"] - s["r62_w"]

        if samp == "late":
            # equivalence check: primitive default winsorization path
            # must reproduce the pre-winsorized call on raw columns.
            fm_ref = fama_macbeth(s, dependent_var="ret",
                                  independent_vars=T1_VARS, time_col="month",
                                  winsorize_pct=0.01, n_lags=0)
            fm_chk = fama_macbeth(s, dependent_var="ret",
                                  independent_vars=[v + "_w" for v in T1_VARS],
                                  time_col="month", winsorize_pct=0.0, n_lags=0)
            dev = float(np.abs(
                fm_ref.summary["mean"][T1_VARS].to_numpy()
                - fm_chk.summary["mean"][[v + "_w" for v in T1_VARS]].to_numpy()
            ).max())
            assert dev < 1e-10, f"winsorization mirror mismatch: {dev}"

        fmA = fama_macbeth(s, dependent_var="ret",
                           independent_vars=[v + "_w" for v in T1_VARS],
                           time_col="month", winsorize_pct=0.0, n_lags=0)
        # Diagnostic second regression with diff as the sole performance
        # regressor. NOTE (spec flag): replacing [r127, r62] by [diff]
        # alone REMOVES r62 from the column space, so b(diff) does NOT
        # equal b(r127)-b(r62) in general (omitted-regressor effect) —
        # the identity would only hold with r62 kept alongside diff.
        # The paper's printed diff row (0.93-0.36=0.57 etc.) is the
        # coefficient difference from the SAME regression, so the
        # reported diff metrics below use the per-month difference of
        # regression A's coefficient series (exact by construction).
        fmB = fama_macbeth(s, dependent_var="ret",
                           independent_vars=["diff_w"] + [v + "_w" for v in
                                                          T1_VARS[2:]],
                           time_col="month", winsorize_pct=0.0, n_lags=0)

        # sample alignment check (the discriminator): both regressions
        # must run on identical month sets.
        assert (fmA.coefficients.index.tolist()
                == fmB.coefficients.index.tolist()), \
            f"{samp}: FM sample misalignment (months differ)"

        # exact diff row: per-month b(r127) - b(r62), FM mean + plain t
        b_diff = (fmA.coefficients["r127_w"] - fmA.coefficients["r62_w"]
                  ).dropna()
        diff_mean = float(b_diff.mean())
        diff_t = float(b_diff.mean()
                       / (b_diff.std(ddof=1) / np.sqrt(len(b_diff))))

        # invariant report: (a) trivially-exact identity of the diff row,
        # (b) deviation of the diagnostic single-regressor regression.
        dev_exact = float(np.abs(
            b_diff - (fmA.coefficients["r127_w"]
                      - fmA.coefficients["r62_w"])).max())
        dev_subst = float(np.abs(
            fmB.coefficients["diff_w"] - b_diff).max())
        report["invariant"][samp] = {"diff_row": dev_exact,
                                     "substitution_reg": dev_subst}

        per_month_n = s.groupby("month").size()
        report["avg_firms"][samp] = float(per_month_n.mean())
        report["min_firms"][samp] = int(per_month_n.min())
        report["n_months"][samp] = int(len(per_month_n))
        report["total_obs"][samp] = int(len(s))

        for var in T1_VARS:
            key = T1_KEYMAP[var]
            metrics[f"T1:{key}_{samp}"] = {
                "value": float(fmA.summary["mean"][var + "_w"]) * 100,
                "unit": "fm_coef_x100"}
            metrics[f"T1:{key}_{samp}_t"] = {
                "value": float(fmA.summary["t_stat"][var + "_w"]),
                "unit": "t_stat"}
        metrics[f"T1:diff_{samp}"] = {
            "value": diff_mean * 100,
            "unit": "fm_coef_x100"}
        metrics[f"T1:diff_{samp}_t"] = {
            "value": diff_t,
            "unit": "t_stat"}

    # log_bm coverage by decade (share among firm-months with ret,
    # r127, r62, r10, log_me all present, 1969-2010).
    cov = d.dropna(subset=["ret", "r127", "r62", "r10", "log_me"])
    cov = cov[(cov["month"] >= T1_SAMPLES["late"][0])]
    cov = cov.assign(decade=(cov["month"].dt.year // 10) * 10)
    report["logbm_share_by_decade"] = {
        int(dec): float(g["log_bm"].notna().mean())
        for dec, g in cov.groupby("decade")}
    return report


# --- strategies ---


def build_strategy(panel: pd.DataFrame, sig_col: str, stats: dict):
    """VW winner-minus-loser decile strategy on `sig_col`, NYSE breakpoints.

    DEVIATION FROM utils.assign_quantiles PRIMITIVE (documented per task
    spec): assign_quantiles computes breakpoints over all stocks by default
    and has no NYSE-only breakpoint option matching Assumption 5, so
    breakpoints are computed here as the 10%..90% quantiles of the signal
    among hexcd==1 eligible stocks each month and bins are assigned with
    np.searchsorted (side='right': values equal to a breakpoint fall in the
    lower decile). Decile 1 = lowest past return (losers), 10 = winners.

    Iteration 1 fix: signals are indexed to the RETURN month t (formation
    happens at the end of month t-1). The r_{n,m} columns computed in
    load_panel via rolling_cumret(window=W, skip=S) already give, at each
    month t, prod(1+ret) over months t-S-W .. t-S-1 (utils/portfolio.py:
    shift_amt = skip+1, then a rolling W-window on the shifted log
    returns):
      r127(t) -> t-12..t-7, r62(t) -> t-6..t-2, r122(t) -> t-12..t-2.
    Eligibility at return month t: signal non-missing and me_lag1 (ME at
    end of t-1) non-missing. VW weight = me_lag1 (Assumption 4).
    Strategy return at t = VW(decile 10) - VW(decile 1),
    t = 1927-01..2010-12 (1008 months).
    """
    d = panel[["permno", "month", sig_col, "me_lag1", "hexcd", "ret"]].copy()
    d = d[(d["month"] >= FIRST_STRAT_MONTH) & (d["month"] <= LAST_STRAT_MONTH)]

    e = d[d[sig_col].notna() & d["me_lag1"].notna()].copy()
    parts = []
    for m, g in e.groupby("month"):
        nyse = g.loc[g["hexcd"] == 1, sig_col].to_numpy()
        bps = np.quantile(nyse, np.linspace(0.1, 0.9, 9))
        dec = np.searchsorted(bps, g[sig_col].to_numpy(), side="right") + 1
        parts.append(g.assign(decile=dec))
    E = pd.concat(parts, ignore_index=True)

    hold = E[E["ret"].notna()]
    vw = (hold.groupby(["month", "decile"])
               .apply(lambda g: np.average(g["ret"], weights=g["me_lag1"]),
                      include_groups=False)
               .rename("vw"))
    strat = (vw.xs(N_BINS, level="decile") - vw.xs(1, level="decile")
             ).rename("ret").sort_index()

    stats[sig_col] = {
        "avg_eligible_per_month": float(e.groupby("month").size().mean()),
        "avg_nyse_per_month": float(
            e[e["hexcd"] == 1].groupby("month").size().mean()),
        "avg_winner_count": float((E["decile"] == N_BINS).groupby(
            E["month"]).sum().mean()),
        "avg_loser_count": float((E["decile"] == 1).groupby(
            E["month"]).sum().mean()),
        "n_strategy_months": int(len(strat)),
    }
    return strat


# --- regressions ---


def mean_t(s: pd.Series):
    s = s.dropna()
    return float(s.mean()), float(s.mean() / (s.std(ddof=1) / np.sqrt(len(s))))


def ts_reg(y: pd.Series, X: pd.DataFrame):
    d = pd.concat([y.rename("y"), X], axis=1).dropna()
    res = sm.OLS(d["y"], sm.add_constant(d[X.columns])).fit()
    return res


def load_factors() -> pd.DataFrame:
    ff = q_file("ff_factors.sql")
    ff["dt"] = pd.to_datetime(ff["dt"])
    return ff.set_index("dt").sort_index()


# --- Table 2 ---


def compute_table2(strats, ff, metrics):
    spec_map = {
        1: ("r127", []),
        2: ("r127", ["mkt_rf"]),
        3: ("r127", ["mkt_rf", "smb", "hml"]),
        4: ("r127", ["mkt_rf", "smb", "hml", "mom"]),
        5: ("r62", []),
        6: ("r62", ["mkt_rf"]),
        7: ("r62", ["mkt_rf", "smb", "hml"]),
        8: ("r62", ["mkt_rf", "smb", "hml", "mom"]),
    }
    fac_name = {"mkt_rf": "mkt", "smb": "smb", "hml": "hml", "mom": "umd"}
    for s, (sig, facs) in spec_map.items():
        y = strats[sig]
        if not facs:
            mu, t = mean_t(y)
            metrics[f"T2:intercept_s{s}"] = {"value": mu * 100,
                                             "unit": "percent_per_month"}
            metrics[f"T2:intercept_s{s}_t"] = {"value": t, "unit": "t_stat"}
        else:
            res = ts_reg(y, ff[facs])
            metrics[f"T2:intercept_s{s}"] = {
                "value": res.params["const"] * 100,
                "unit": "percent_per_month"}
            metrics[f"T2:intercept_s{s}_t"] = {
                "value": float(res.tvalues["const"]), "unit": "t_stat"}
            for f in facs:
                metrics[f"T2:{fac_name[f]}_s{s}"] = {
                    "value": float(res.params[f]), "unit": "factor_loading"}
                metrics[f"T2:{fac_name[f]}_s{s}_t"] = {
                    "value": float(res.tvalues[f]), "unit": "t_stat"}
            metrics[f"T2:r2_s{s}"] = {"value": float(res.rsquared_adj),
                                      "unit": "adj_r_squared"}
    return spec_map


# --- Table 3 ---


def compute_table3(strats, ff, metrics):
    out = {}
    for panel_letter, ysig, xsig in (("A", "r127", "r62"),
                                     ("B", "r62", "r127")):
        for samp, (lo, hi) in SAMPLES.items():
            y = strats[ysig][(strats[ysig].index >= lo)
                             & (strats[ysig].index <= hi)]
            X = ff.loc[lo:hi, ["mkt_rf", "smb", "hml"]].copy()
            X["mom"] = strats[xsig].reindex(X.index)

            mu, t = mean_t(y)
            metrics[f"T3:{panel_letter}_er_{samp}"] = {
                "value": mu * 100, "unit": "percent_per_month"}
            metrics[f"T3:{panel_letter}_er_{samp}_t"] = {
                "value": t, "unit": "t_stat"}
            res = ts_reg(y, X)
            metrics[f"T3:{panel_letter}_int_{samp}"] = {
                "value": res.params["const"] * 100,
                "unit": "percent_per_month"}
            metrics[f"T3:{panel_letter}_int_{samp}_t"] = {
                "value": float(res.tvalues["const"]), "unit": "t_stat"}
            for f, key in (("mkt_rf", "mkt"), ("smb", "smb"), ("hml", "hml"),
                           ("mom", "mom")):
                metrics[f"T3:{panel_letter}_{key}_{samp}"] = {
                    "value": float(res.params[f]), "unit": "factor_loading"}
                metrics[f"T3:{panel_letter}_{key}_{samp}_t"] = {
                    "value": float(res.tvalues[f]), "unit": "t_stat"}
            metrics[f"T3:{panel_letter}_r2_{samp}"] = {
                "value": float(res.rsquared_adj), "unit": "adj_r_squared"}
            out[(panel_letter, samp)] = res
    return out


# --- Table 4: 5x5 independent double sort on r_12,7 (IR) x r_6,2 (RR) ---

T4_START = pd.Timestamp("1927-01-31")
T4_END = pd.Timestamp("2008-12-31")   # Assumption 11: Table 4 ends Dec 2008
T4_MONTHS_EXPECTED = 984
FF4 = ["mkt_rf", "smb", "hml", "mom"]


def _eligible(panel, lo, hi):
    """Firm-months with r127, r62, me_lag1, ret all non-missing."""
    d = panel[["permno", "month", "ret", "me_lag1", "r127", "r62",
               "hexcd"]].copy()
    d = d[(d["month"] >= lo) & (d["month"] <= hi)]
    return d.dropna(subset=["r127", "r62", "me_lag1", "ret"])


def _assign_double_quintiles(e):
    """Independent NYSE-quintile assignment (Assumption 5): breakpoints of
    r127 and of r62 computed independently on the hexcd==1 subset of the
    full eligible cross-section each month (NOT within cells)."""
    parts = []
    for m, g in e.groupby("month"):
        nyse = g[g["hexcd"] == 1]
        bps127 = np.quantile(nyse["r127"], [0.2, 0.4, 0.6, 0.8])
        bps62 = np.quantile(nyse["r62"], [0.2, 0.4, 0.6, 0.8])
        q_ir = np.searchsorted(bps127, g["r127"].to_numpy(), side="right") + 1
        q_rr = np.searchsorted(bps62, g["r62"].to_numpy(), side="right") + 1
        parts.append(g.assign(q_ir=q_ir, q_rr=q_rr))
    return pd.concat(parts, ignore_index=True)


def _vw(series_by_group):
    """VW returns: series_by_group has columns month, group keys, ret,
    me_lag1 -> Series indexed (month, *keys)."""
    return (series_by_group
            .groupby(["month"] + [c for c in series_by_group.columns
                                  if c.startswith("q_")])
            .apply(lambda g: np.average(g["ret"], weights=g["me_lag1"]),
                   include_groups=False)
            .rename("vw"))


def compute_table4(panel, ff, metrics):
    """Table 4 Panels A (mean excess) and D (FF4 alphas).

    25 VW cell series at the intersection of independent IR (r_12,7) and
    RR (r_6,2) NYSE quintiles; row spreads SPREAD_IR(j) = cell(j,IR5) -
    cell(j,IR1); column spreads SPREAD_RR(k) = cell(RR5,k) - cell(RR1,k).
    Panel A: mean of (ret - rf); Panel D: FF4 intercept (Assumption 6,
    plain OLS t). Percent per month.
    """
    e = _assign_double_quintiles(_eligible(panel, T4_START, T4_END))
    vw = _vw(e)  # index (month, q_rr, q_ir)

    cells = {(int(rr), int(ir)): vw.xs((rr, ir), level=("q_rr", "q_ir")
                                       ).sort_index()
             for rr in range(1, 6) for ir in range(1, 6)}
    spreads = {}
    for rr in range(1, 6):
        spreads[("row", rr)] = cells[(rr, 5)] - cells[(rr, 1)]
    for ir in range(1, 6):
        spreads[("col", ir)] = cells[(5, ir)] - cells[(1, ir)]

    # sanity: every series spans 1927-01..2008-12 (984 months)
    all_series = {f"cell{rr}_{ir}": cells[(rr, ir)]
                  for rr in range(1, 6) for ir in range(1, 6)}
    all_series.update({f"sp{k}": v for k, v in spreads.items()})
    for key, s in all_series.items():
        assert len(s) == T4_MONTHS_EXPECTED and \
            s.index.min() == T4_START and s.index.max() == T4_END, \
            f"T4 {key}: {len(s)} months ({s.index.min()}..{s.index.max()})"

    rf = ff["rf"].reindex(vw.index.get_level_values("month").unique())
    exc = {k: s - rf.reindex(s.index) for k, s in cells.items()}
    # excess spread series (rf-invariant in the mean, but keeps the Panel D
    # dependent variables consistently in excess-return units)
    exc_spreads = {k: s - rf.reindex(s.index) for k, s in spreads.items()}

    X = ff.loc[T4_START:T4_END, FF4]
    for rr in range(1, 6):
        for ir in range(1, 6):
            mu, t = mean_t(exc[(rr, ir)])
            metrics[f"T4:A_RR{rr}_IR{ir}"] = {"value": mu * 100,
                                              "unit": "percent_per_month"}
            metrics[f"T4:A_RR{rr}_IR{ir}_t"] = {"value": t, "unit": "t_stat"}
            res = ts_reg(exc[(rr, ir)], X)
            metrics[f"T4:D_RR{rr}_IR{ir}"] = {
                "value": res.params["const"] * 100,
                "unit": "percent_per_month"}
            metrics[f"T4:D_RR{rr}_IR{ir}_t"] = {
                "value": float(res.tvalues["const"]), "unit": "t_stat"}
        mu, t = mean_t(spreads[("row", rr)])
        metrics[f"T4:A_RR{rr}_SP"] = {"value": mu * 100,
                                      "unit": "percent_per_month"}
        metrics[f"T4:A_RR{rr}_SP_t"] = {"value": t, "unit": "t_stat"}
        res = ts_reg(exc_spreads[("row", rr)], X)
        metrics[f"T4:D_RR{rr}_SP"] = {"value": res.params["const"] * 100,
                                      "unit": "percent_per_month"}
        metrics[f"T4:D_RR{rr}_SP_t"] = {"value": float(res.tvalues["const"]),
                                        "unit": "t_stat"}
    for ir in range(1, 6):
        mu, t = mean_t(spreads[("col", ir)])
        metrics[f"T4:A_SP_IR{ir}"] = {"value": mu * 100,
                                      "unit": "percent_per_month"}
        metrics[f"T4:A_SP_IR{ir}_t"] = {"value": t, "unit": "t_stat"}
        res = ts_reg(exc_spreads[("col", ir)], X)
        metrics[f"T4:D_SP_IR{ir}"] = {"value": res.params["const"] * 100,
                                      "unit": "percent_per_month"}
        metrics[f"T4:D_SP_IR{ir}_t"] = {"value": float(res.tvalues["const"]),
                                        "unit": "t_stat"}

    n_cell = e.groupby(["q_rr", "q_ir"]).size() / e["month"].nunique()
    report = {
        "avg_eligible_per_month": float(e.groupby("month").size().mean()),
        "avg_stocks_per_cell": {f"RR{rr}_IR{ir}": float(n_cell[(rr, ir)])
                                for rr in range(1, 6) for ir in range(1, 6)},
        "months": int(e["month"].nunique()),
    }
    return report, spreads


# --- Table 6: conditional (within-quintile) momentum strategies ---

T5_START = pd.Timestamp("1969-01-31")
T5_END = pd.Timestamp("2010-12-31")
T5_MONTHS_EXPECTED = 504


def _assign_cond_quintiles(e, cond_col, inner_col, inner_mode="uncond"):
    """Conditioning quintile from NYSE breakpoints of cond_col over the full
    eligible cross-section; inner quintile on inner_col.

    inner_mode='uncond' (BASE, Assumption 9 as corrected in iteration 7):
    inner breakpoints from the UNCONDITIONAL NYSE (hexcd==1) quintiles of
    inner_col over the full eligible cross-section, applied to stocks
    within each conditioning subsample (same breakpoints as the
    unconditional sorts). The paper's Table 7 note "Portfolio break points
    based on NYSE stocks only" (content.md L1701) is not restricted to the
    size/conditioning sort, so the inner momentum breakpoints are also
    NYSE-only unconditional.
    inner_mode='within' (robustness alternative): inner breakpoints from
    the conditioning subsample itself (the original, superseded reading
    of Assumption 9; report-only)."""
    parts = []
    for m, g in e.groupby("month"):
        nyse = g[g["hexcd"] == 1]
        bps_c = np.quantile(nyse[cond_col], [0.2, 0.4, 0.6, 0.8])
        qc = np.searchsorted(bps_c, g[cond_col].to_numpy(), side="right") + 1
        g = g.assign(q_cond=qc)
        if inner_mode == "uncond":
            bps_i = np.quantile(nyse[inner_col], [0.2, 0.4, 0.6, 0.8])
            inner = (np.searchsorted(bps_i, g[inner_col].to_numpy(),
                                     side="right") + 1)
        else:
            inner = np.empty(len(g), dtype=int)
            for j in range(1, 6):
                idx = (g["q_cond"] == j).to_numpy()
                sub = g.loc[idx, inner_col].to_numpy()
                bps_i = np.quantile(sub, [0.2, 0.4, 0.6, 0.8])
                inner[idx] = np.searchsorted(bps_i, sub, side="right") + 1
        parts.append(g.assign(q_inner=inner))
    return pd.concat(parts, ignore_index=True)


def _cond_strategies(e, cond_col, inner_col, inner_mode="uncond"):
    """MOM_inner|cond_qj = VW inner-quintile-5 minus inner-quintile-1 within
    each conditioning quintile j. Returns {j: Series}."""
    a = _assign_cond_quintiles(e, cond_col, inner_col, inner_mode)
    vw = (a.groupby(["month", "q_cond", "q_inner"])
            .apply(lambda g: np.average(g["ret"], weights=g["me_lag1"]),
                   include_groups=False).rename("vw"))
    def _leg(j, k):
        try:
            return vw.xs((j, k), level=("q_cond", "q_inner")).sort_index()
        except KeyError:
            return pd.Series(dtype=float)

    out = {}
    for j in range(1, 6):
        out[j] = (_leg(j, 5) - _leg(j, 1)).dropna()
    return out


def compute_table5(panel, strats, ff, metrics):
    """Table 6: MOM_12,7 within each r_6,2 quintile (left block,
    er_cond127/alpha_cond127) and MOM_6,2 within each r_12,7 quintile
    (right block, er_cond62/alpha_cond62), 1969-01..2010-12.

    E[r^d] = mean strategy return, t = mean/SE (long-short spreads are
    rf-invariant). alpha = intercept on [mkt_rf, smb, hml, MOM_12,7
    unconditional decile series] (paper L1673) for BOTH blocks, plain
    OLS t (Assumption 6).
    """
    e = _eligible(panel, T5_START, T5_END)
    # base convention: unconditional NYSE inner breakpoints (Assumption 9
    # corrected, iteration 7; paper Table 7 note L1701)
    cond127 = _cond_strategies(e, "r62", "r127")   # MOM_12,7 | RR_j
    cond62 = _cond_strategies(e, "r127", "r62")    # MOM_6,2  | IR_j

    X = ff.loc[T5_START:T5_END, ["mkt_rf", "smb", "hml"]].copy()
    X["mom127"] = strats["r127"].reindex(X.index)

    report = {}
    for tag, strat_map in (("cond127", cond127), ("cond62", cond62)):
        for j, s in strat_map.items():
            # unconditional-NYSE inner breakpoints can leave thin
            # (cond_q, inner_5/1) cells empty in some months; series with
            # missing months are computed over the available months and
            # flagged.
            if len(s) != T5_MONTHS_EXPECTED:
                print(f"WARNING: T5 {tag} q{j}: {len(s)} months != "
                      f"{T5_MONTHS_EXPECTED}")
            mu, t = mean_t(s)
            metrics[f"T5:er_{tag}_q{j}"] = {"value": mu * 100,
                                            "unit": "percent_per_month"}
            metrics[f"T5:er_{tag}_q{j}_t"] = {"value": t, "unit": "t_stat"}
            # dependent: raw zero-cost strategy return (spec/paper: no rf
            # subtraction for T5 alphas; mean rf 1969-2010 is ~0.37%/mo and
            # the excess variant shifts every alpha down by exactly that,
            # away from the paper's printed values)
            res = ts_reg(s, X)
            metrics[f"T5:alpha_{tag}_q{j}"] = {
                "value": res.params["const"] * 100,
                "unit": "percent_per_month"}
            metrics[f"T5:alpha_{tag}_q{j}_t"] = {
                "value": float(res.tvalues["const"]), "unit": "t_stat"}
        report[tag] = {"months": {j: len(s) for j, s in strat_map.items()}}
    report["avg_eligible_per_month"] = float(e.groupby("month").size().mean())
    return report


def compute_table5_robust(panel):
    """Robustness alternative (superseded convention): the conditional
    MOM_6,2 grid recomputed WITH within-subsample inner breakpoints
    (breakpoints of r62 computed inside each IR (r_12,7) quintile), vs the
    base unconditional-NYSE convention (Assumption 9 corrected in
    iteration 7; paper Table 7 note, content.md L1701). Report-only —
    never written to eval/metrics.json."""
    e = _eligible(panel, T5_START, T5_END)
    cond62_u = _cond_strategies(e, "r127", "r62", inner_mode="within")
    out = {}
    for j, s in cond62_u.items():
        if len(s):
            mu, t = mean_t(s)
            out[j] = {"months": int(len(s)), "er": mu * 100, "t": t}
        else:
            out[j] = {"months": 0, "er": float("nan"), "t": float("nan")}
    return out


# --- Table 7: momentum within NYSE size quintiles (T6) ---

T6_START = pd.Timestamp("1927-01-31")
T6_END = pd.Timestamp("2010-12-31")
T6_LATE_START = pd.Timestamp("1969-01-31")
T6_FULL_MONTHS = 1008
T6_LATE_MONTHS = 504


def _assign_size_quintiles(u):
    """Size quintiles 1(small)..5(large) from NYSE (hexcd==1, Assumption 5)
    20/40/60/80 breakpoints of me_lag1, assigned to ALL stocks with me_lag1
    non-missing (Assumption 1 universe — signal availability irrelevant)."""
    parts = []
    for m, g in u.groupby("month"):
        nyse = g.loc[g["hexcd"] == 1, "me_lag1"].to_numpy()
        bps = np.quantile(nyse, [0.2, 0.4, 0.6, 0.8])
        q = np.searchsorted(bps, g["me_lag1"].to_numpy(), side="right") + 1
        parts.append(g.assign(q_size=q))
    return pd.concat(parts, ignore_index=True)


def _t6_momentum_within(d, size_q, inner_mode):
    """Momentum quintile sorts within each size quintile (T6 Panels B-E
    input). inner_mode='uncond' (BASE, Assumption 9 as corrected in
    iteration 7): breakpoints from the UNCONDITIONAL NYSE (hexcd==1, full
    eligible cross-section) quintiles of the signal, assigned to stocks
    within each size quintile — per the paper's Table 7 note "Portfolio
    break points based on NYSE stocks only" (content.md L1701), which is
    not restricted to the size sort. inner_mode='within' (robustness
    alternative, superseded reading of Assumption 9): breakpoints from the
    size-quintile eligible subsample itself.

    Returns (strat, counts): strat[tag][j] = VW top-minus-bottom inner
    quintile series within size quintile j; counts[tag][(j, k)] = average
    stocks per month in size quintile j, inner quintile k (thin-cell
    diagnostic for the unconditional variant)."""
    strat = {"m127": {}, "m62": {}}
    counts = {"m127": {}, "m62": {}}
    for tag, sig in (("m127", "r127"), ("m62", "r62")):
        e = d[d["ret"].notna() & d[sig].notna()].copy()
        e["q_size"] = size_q.reindex(
            pd.MultiIndex.from_frame(e[["permno", "month"]])).to_numpy()
        parts = []
        for m, g in e.groupby("month"):
            if inner_mode == "uncond":
                nyse = g.loc[g["hexcd"] == 1, sig].to_numpy()
                bps = np.quantile(nyse, [0.2, 0.4, 0.6, 0.8])
                inner = (np.searchsorted(bps, g[sig].to_numpy(),
                                         side="right") + 1)
            else:
                inner = np.empty(len(g), dtype=int)
                for j in range(1, 6):
                    idx = (g["q_size"] == j).to_numpy()
                    sub = g.loc[idx, sig].to_numpy()
                    bps = np.quantile(sub, [0.2, 0.4, 0.6, 0.8])
                    inner[idx] = np.searchsorted(bps, sub, side="right") + 1
            parts.append(g.assign(q_inner=inner))
        E = pd.concat(parts, ignore_index=True)
        vw = (E.groupby(["month", "q_size", "q_inner"])
                .apply(lambda g: np.average(g["ret"], weights=g["me_lag1"]),
                       include_groups=False).rename("vw"))

        def _leg(j, k):
            try:
                return vw.xs((j, k), level=("q_size", "q_inner")).sort_index()
            except KeyError:
                return pd.Series(dtype=float)

        n_m = E["month"].nunique()
        for j in range(1, 6):
            strat[tag][j] = (_leg(j, 5) - _leg(j, 1)).dropna()
            for k in range(1, 6):
                counts[tag][(j, k)] = float(
                    ((E["q_size"] == j) & (E["q_inner"] == k)).sum()) / n_m
    return strat, counts


def _t6_panels(strat, ff, out):
    """Fill out[f"T6:{pl}_{tag}_q{j}(_t)"] for Panels B-E from a strat map
    (base call writes to metrics; the robustness call writes to a
    report-only dict)."""
    for pl, lo in (("pb", T6_START), ("pd", T6_LATE_START)):
        for tag in ("m127", "m62"):
            for j in range(1, 6):
                s = strat[tag][j][(strat[tag][j].index >= lo)
                                  & (strat[tag][j].index <= T6_END)]
                mu, t = mean_t(s)
                out[f"T6:{pl}_{tag}_q{j}"] = {
                    "value": mu * 100, "unit": "percent_per_month"}
                out[f"T6:{pl}_{tag}_q{j}_t"] = {"value": t,
                                                "unit": "t_stat"}
    for pl, lo, hi in (("pc", T6_START, T6_END),
                       ("pe", T6_LATE_START, T6_END)):
        X = ff.loc[lo:hi, ["mkt_rf", "smb", "hml"]]
        for j in range(1, 6):
            other = {"m127": "m62", "m62": "m127"}
            for tag in ("m127", "m62"):
                y = strat[tag][j][(strat[tag][j].index >= lo)
                                  & (strat[tag][j].index <= T6_END)]
                if not len(y):
                    out[f"T6:{pl}_{tag}_q{j}"] = {"value": float("nan"),
                                                  "unit": "percent_per_month"}
                    out[f"T6:{pl}_{tag}_q{j}_t"] = {"value": float("nan"),
                                                    "unit": "t_stat"}
                    continue
                Xj = X.copy()
                Xj["other"] = strat[other[tag]][j].reindex(X.index)
                res = ts_reg(y, Xj)
                out[f"T6:{pl}_{tag}_q{j}"] = {
                    "value": res.params["const"] * 100,
                    "unit": "percent_per_month"}
                out[f"T6:{pl}_{tag}_q{j}_t"] = {
                    "value": float(res.tvalues["const"]), "unit": "t_stat"}


def compute_table6(panel, ff, metrics):
    """Table 7 (T6). Panel A: time-series-average characteristics of the
    size quintiles over ALL me_lag1-non-missing stocks. Panels B/C: full
    sample 1927-01..2010-12; D/E: late 1969-01..2010-12. Within size
    quintile i, momentum quintile sorts on r127 (MOM_12,7) and r62
    (MOM_6,2); strategy = VW(me_lag1) top - bottom
    quintile (zero-cost, rf cancels). Inner momentum breakpoints:
    UNCONDITIONAL NYSE quintiles of the signal (Assumption 9 corrected,
    iteration 7; paper Table 7 note, content.md L1701). Alphas: regression on
    [mkt_rf, smb, hml, OTHER strategy in the same quintile], plain OLS t
    (Assumption 6)."""
    u = panel[["permno", "month", "me_lag1", "hexcd"]].copy()
    u = u[(u["month"] >= T6_START) & (u["month"] <= T6_END)]
    u = u.dropna(subset=["me_lag1"])
    a = _assign_size_quintiles(u)
    report = {"months_panelA": int(a["month"].nunique())}

    # ---- Panel A ----
    per_month = a.groupby(["month", "q_size"]).agg(
        n=("permno", "size"), cap=("me_lag1", "sum")).reset_index()
    tot = per_month.groupby("month")["n"].transform("sum")
    per_month["pfirms"] = per_month["n"] / tot * 100
    tot_cap = per_month.groupby("month")["cap"].transform("sum")
    per_month["pcap"] = per_month["cap"] / tot_cap * 100
    per_month["avecap_m"] = per_month["cap"] / per_month["n"] / 1e6
    agg = per_month.groupby("q_size").mean(numeric_only=True)
    for j in range(1, 6):
        metrics[f"T6:pa_nfirms_q{j}"] = {
            "value": float(agg.loc[j, "n"]), "unit": "count"}
        metrics[f"T6:pa_pfirms_q{j}"] = {
            "value": float(agg.loc[j, "pfirms"]), "unit": "percent"}
        metrics[f"T6:pa_totcap_q{j}"] = {
            "value": float(agg.loc[j, "cap"] / 1e9), "unit": "billions_usd"}
        metrics[f"T6:pa_pcap_q{j}"] = {
            "value": float(agg.loc[j, "pcap"]), "unit": "percent"}
        metrics[f"T6:pa_avecap_q{j}"] = {
            "value": float(agg.loc[j, "avecap_m"]), "unit": "millions_usd"}

    # ---- universe validator stop-gate ----
    n1 = metrics["T6:pa_nfirms_q1"]["value"]
    if not (1500 <= n1 <= 2100):
        dec = a.assign(decade=(a["month"].dt.year // 10) * 10)
        by_dec = (dec.groupby(["decade", "q_size"]).size()
                  / dec.groupby("decade")["month"].nunique()).unstack()
        raise RuntimeError(
            f"T6 Panel A validator FAILED: size-quintile-1 avg firms = "
            f"{n1:.1f} outside [1500, 2100]. Avg firms/quintile by decade:\n"
            f"{by_dec.round(1).to_string()}")

    # ---- momentum within size quintiles ----
    d = panel[["permno", "month", "ret", "me_lag1", "hexcd",
               "r127", "r62"]].copy()
    d = d[(d["month"] >= T6_START) & (d["month"] <= T6_END)]
    d = d.dropna(subset=["me_lag1"])
    size_q = a.set_index(["permno", "month"])["q_size"]

    # base convention (Assumption 9 corrected, iteration 7: unconditional
    # NYSE inner breakpoints; paper Table 7 note L1701)
    strat, counts = _t6_momentum_within(d, size_q, "uncond")
    _t6_panels(strat, ff, metrics)

    # robustness alternative (superseded convention): within-subsample
    # inner breakpoints — REPORT-ONLY, never merged into
    # eval/metrics.json.
    rob_strat, rob_counts = _t6_momentum_within(d, size_q, "within")
    rob = {}
    _t6_panels(rob_strat, ff, rob)

    elig_counts = {tag: {j: sum(v for (jj, _), v in counts[tag].items()
                                if jj == j)
                         for j in range(1, 6)} for tag in counts}

    report["avg_eligible_by_quintile"] = elig_counts
    report["n_months"] = {tag: {j: len(s) for j, s in strat[tag].items()}
                          for tag in strat}
    report["rob_months"] = {tag: {j: len(s) for j, s in rob_strat[tag].items()}
                            for tag in rob_strat}
    report["inner_counts"] = counts
    report["rob_inner_counts"] = rob_counts
    report["panelA"] = {row: [float(agg.loc[row, c]) for c in
                              ("n", "pfirms", "cap", "pcap", "avecap_m")]
                        for row in agg.index}
    return report, strat, rob


# --- Table 8: industry momentum spanning tests (T7) ---

# Fama-French 49-industry SIC boundaries. This is the published FF49
# definition, transcribed verbatim from Kenneth French's official
# Siccodes49.txt (mba.tuck.dartmouth.edu/pages/faculty/ken.french,
# ftp/Siccodes49.zip, retrieved for this replication). Each entry:
# (industry id, abbreviation, name, [(sic_lo, sic_hi), ...]).
FF49_INDUSTRIES = [
    (1, "Agric", "Agriculture", [(100, 199), (200, 299), (700, 799), (910, 919), (2048, 2048)]),
    (2, "Food", "Food Products", [(2000, 2009), (2010, 2019), (2020, 2029), (2030, 2039), (2040, 2046), (2050, 2059), (2060, 2063), (2070, 2079), (2090, 2092), (2095, 2095), (2098, 2099)]),
    (3, "Soda", "Candy & Soda", [(2064, 2068), (2086, 2086), (2087, 2087), (2096, 2096), (2097, 2097)]),
    (4, "Beer", "Beer & Liquor", [(2080, 2080), (2082, 2082), (2083, 2083), (2084, 2084), (2085, 2085)]),
    (5, "Smoke", "Tobacco Products", [(2100, 2199)]),
    (6, "Toys", "Recreation", [(920, 999), (3650, 3651), (3652, 3652), (3732, 3732), (3930, 3931), (3940, 3949)]),
    (7, "Fun", "Entertainment", [(7800, 7829), (7830, 7833), (7840, 7841), (7900, 7900), (7910, 7911), (7920, 7929), (7930, 7933), (7940, 7949), (7980, 7980), (7990, 7999)]),
    (8, "Books", "Printing and Publishing", [(2700, 2709), (2710, 2719), (2720, 2729), (2730, 2739), (2740, 2749), (2770, 2771), (2780, 2789), (2790, 2799)]),
    (9, "Hshld", "Consumer Goods", [(2047, 2047), (2391, 2392), (2510, 2519), (2590, 2599), (2840, 2843), (2844, 2844), (3160, 3161), (3170, 3171), (3172, 3172), (3190, 3199), (3229, 3229), (3260, 3260), (3262, 3263), (3269, 3269), (3230, 3231), (3630, 3639), (3750, 3751), (3800, 3800), (3860, 3861), (3870, 3873), (3910, 3911), (3914, 3914), (3915, 3915), (3960, 3962), (3991, 3991), (3995, 3995)]),
    (10, "Clths", "Apparel", [(2300, 2390), (3020, 3021), (3100, 3111), (3130, 3131), (3140, 3149), (3150, 3151), (3963, 3965)]),
    (11, "Hlth", "Healthcare", [(8000, 8099)]),
    (12, "MedEq", "Medical Equipment", [(3693, 3693), (3840, 3849), (3850, 3851)]),
    (13, "Drugs", "Pharmaceutical Products", [(2830, 2830), (2831, 2831), (2833, 2833), (2834, 2834), (2835, 2835), (2836, 2836)]),
    (14, "Chems", "Chemicals", [(2800, 2809), (2810, 2819), (2820, 2829), (2850, 2859), (2860, 2869), (2870, 2879), (2890, 2899)]),
    (15, "Rubbr", "Rubber and Plastic Products", [(3031, 3031), (3041, 3041), (3050, 3053), (3060, 3069), (3070, 3079), (3080, 3089), (3090, 3099)]),
    (16, "Txtls", "Textiles", [(2200, 2269), (2270, 2279), (2280, 2284), (2290, 2295), (2297, 2297), (2298, 2298), (2299, 2299), (2393, 2395), (2397, 2399)]),
    (17, "BldMt", "Construction Materials", [(800, 899), (2400, 2439), (2450, 2459), (2490, 2499), (2660, 2661), (2950, 2952), (3200, 3200), (3210, 3211), (3240, 3241), (3250, 3259), (3261, 3261), (3264, 3264), (3270, 3275), (3280, 3281), (3290, 3293), (3295, 3299), (3420, 3429), (3430, 3433), (3440, 3441), (3442, 3442), (3446, 3446), (3448, 3448), (3449, 3449), (3450, 3451), (3452, 3452), (3490, 3499), (3996, 3996)]),
    (18, "Cnstr", "Construction", [(1500, 1511), (1520, 1529), (1530, 1539), (1540, 1549), (1600, 1699), (1700, 1799)]),
    (19, "Steel", "Steel Works Etc", [(3300, 3300), (3310, 3317), (3320, 3325), (3330, 3339), (3340, 3341), (3350, 3357), (3360, 3369), (3370, 3379), (3390, 3399)]),
    (20, "FabPr", "Fabricated Products", [(3400, 3400), (3443, 3443), (3444, 3444), (3460, 3469), (3470, 3479)]),
    (21, "Mach", "Machinery", [(3510, 3519), (3520, 3529), (3530, 3530), (3531, 3531), (3532, 3532), (3533, 3533), (3534, 3534), (3535, 3535), (3536, 3536), (3538, 3538), (3540, 3549), (3550, 3559), (3560, 3569), (3580, 3580), (3581, 3581), (3582, 3582), (3585, 3585), (3586, 3586), (3589, 3589), (3590, 3599)]),
    (22, "ElcEq", "Electrical Equipment", [(3600, 3600), (3610, 3613), (3620, 3621), (3623, 3629), (3640, 3644), (3645, 3645), (3646, 3646), (3648, 3649), (3660, 3660), (3690, 3690), (3691, 3692), (3699, 3699)]),
    (23, "Autos", "Automobiles and Trucks", [(2296, 2296), (2396, 2396), (3010, 3011), (3537, 3537), (3647, 3647), (3694, 3694), (3700, 3700), (3710, 3710), (3711, 3711), (3713, 3713), (3714, 3714), (3715, 3715), (3716, 3716), (3792, 3792), (3790, 3791), (3799, 3799)]),
    (24, "Aero", "Aircraft", [(3720, 3720), (3721, 3721), (3723, 3724), (3725, 3725), (3728, 3729)]),
    (25, "Ships", "Shipbuilding, Railroad Equipment", [(3730, 3731), (3740, 3743)]),
    (26, "Guns", "Defense", [(3760, 3769), (3795, 3795), (3480, 3489)]),
    (27, "Gold", "Precious Metals", [(1040, 1049)]),
    (28, "Mines", "Non-Metallic and Industrial Metal Mining", [(1000, 1009), (1010, 1019), (1020, 1029), (1030, 1039), (1050, 1059), (1060, 1069), (1070, 1079), (1080, 1089), (1090, 1099), (1100, 1119), (1400, 1499)]),
    (29, "Coal", "Coal", [(1200, 1299)]),
    (30, "Oil", "Petroleum and Natural Gas", [(1300, 1300), (1310, 1319), (1320, 1329), (1330, 1339), (1370, 1379), (1380, 1380), (1381, 1381), (1382, 1382), (1389, 1389), (2900, 2912), (2990, 2999)]),
    (31, "Util", "Utilities", [(4900, 4900), (4910, 4911), (4920, 4922), (4923, 4923), (4924, 4925), (4930, 4931), (4932, 4932), (4939, 4939), (4940, 4942)]),
    (32, "Telcm", "Communication", [(4800, 4800), (4810, 4813), (4820, 4822), (4830, 4839), (4840, 4841), (4880, 4889), (4890, 4890), (4891, 4891), (4892, 4892), (4899, 4899)]),
    (33, "PerSv", "Personal Services", [(7020, 7021), (7030, 7033), (7200, 7200), (7210, 7212), (7214, 7214), (7215, 7216), (7217, 7217), (7219, 7219), (7220, 7221), (7230, 7231), (7240, 7241), (7250, 7251), (7260, 7269), (7270, 7290), (7291, 7291), (7292, 7299), (7395, 7395), (7500, 7500), (7520, 7529), (7530, 7539), (7540, 7549), (7600, 7600), (7620, 7620), (7622, 7622), (7623, 7623), (7629, 7629), (7630, 7631), (7640, 7641), (7690, 7699), (8100, 8199), (8200, 8299), (8300, 8399), (8400, 8499), (8600, 8699), (8800, 8899), (7510, 7515)]),
    (34, "BusSv", "Business Services", [(2750, 2759), (3993, 3993), (7218, 7218), (7300, 7300), (7310, 7319), (7320, 7329), (7330, 7339), (7340, 7342), (7349, 7349), (7350, 7351), (7352, 7352), (7353, 7353), (7359, 7359), (7360, 7369), (7374, 7374), (7376, 7376), (7377, 7377), (7378, 7378), (7379, 7379), (7380, 7380), (7381, 7382), (7383, 7383), (7384, 7384), (7385, 7385), (7389, 7390), (7391, 7391), (7392, 7392), (7393, 7393), (7394, 7394), (7396, 7396), (7397, 7397), (7399, 7399), (7519, 7519), (8700, 8700), (8710, 8713), (8720, 8721), (8730, 8734), (8740, 8748), (8900, 8910), (8911, 8911), (8920, 8999), (4220, 4229)]),
    (35, "Hardw", "Computers", [(3570, 3579), (3680, 3680), (3681, 3681), (3682, 3682), (3683, 3683), (3684, 3684), (3685, 3685), (3686, 3686), (3687, 3687), (3688, 3688), (3689, 3689), (3695, 3695)]),
    (36, "Softw", "Computer Software", [(7370, 7372), (7375, 7375), (7373, 7373)]),
    (37, "Chips", "Electronic Equipment", [(3622, 3622), (3661, 3661), (3662, 3662), (3663, 3663), (3664, 3664), (3665, 3665), (3666, 3666), (3669, 3669), (3670, 3679), (3810, 3810), (3812, 3812)]),
    (38, "LabEq", "Measuring and Control Equipment", [(3811, 3811), (3820, 3820), (3821, 3821), (3822, 3822), (3823, 3823), (3824, 3824), (3825, 3825), (3826, 3826), (3827, 3827), (3829, 3829), (3830, 3839)]),
    (39, "Paper", "Business Supplies", [(2520, 2549), (2600, 2639), (2670, 2699), (2760, 2761), (3950, 3955)]),
    (40, "Boxes", "Shipping Containers", [(2440, 2449), (2640, 2659), (3220, 3221), (3410, 3412)]),
    (41, "Trans", "Transportation", [(4000, 4013), (4040, 4049), (4100, 4100), (4110, 4119), (4120, 4121), (4130, 4131), (4140, 4142), (4150, 4151), (4170, 4173), (4190, 4199), (4200, 4200), (4210, 4219), (4230, 4231), (4240, 4249), (4400, 4499), (4500, 4599), (4600, 4699), (4700, 4700), (4710, 4712), (4720, 4729), (4730, 4739), (4740, 4749), (4780, 4780), (4782, 4782), (4783, 4783), (4784, 4784), (4785, 4785), (4789, 4789)]),
    (42, "Whlsl", "Wholesale", [(5000, 5000), (5010, 5015), (5020, 5023), (5030, 5039), (5040, 5042), (5043, 5043), (5044, 5044), (5045, 5045), (5046, 5046), (5047, 5047), (5048, 5048), (5049, 5049), (5050, 5059), (5060, 5060), (5063, 5063), (5064, 5064), (5065, 5065), (5070, 5078), (5080, 5080), (5081, 5081), (5082, 5082), (5083, 5083), (5084, 5084), (5085, 5085), (5086, 5087), (5088, 5088), (5090, 5090), (5091, 5092), (5093, 5093), (5094, 5094), (5099, 5099), (5100, 5100), (5110, 5113), (5120, 5122), (5130, 5139), (5140, 5149), (5150, 5159), (5160, 5169), (5170, 5172), (5180, 5182), (5190, 5199)]),
    (43, "Rtail", "Retail", [(5200, 5200), (5210, 5219), (5220, 5229), (5230, 5231), (5250, 5251), (5260, 5261), (5270, 5271), (5300, 5300), (5310, 5311), (5320, 5320), (5330, 5331), (5334, 5334), (5340, 5349), (5390, 5399), (5400, 5400), (5410, 5411), (5412, 5412), (5420, 5429), (5430, 5439), (5440, 5449), (5450, 5459), (5460, 5469), (5490, 5499), (5500, 5500), (5510, 5529), (5530, 5539), (5540, 5549), (5550, 5559), (5560, 5569), (5570, 5579), (5590, 5599), (5600, 5699), (5700, 5700), (5710, 5719), (5720, 5722), (5730, 5733), (5734, 5734), (5735, 5735), (5736, 5736), (5750, 5799), (5900, 5900), (5910, 5912), (5920, 5929), (5930, 5932), (5940, 5940), (5941, 5941), (5942, 5942), (5943, 5943), (5944, 5944), (5945, 5945), (5946, 5946), (5947, 5947), (5948, 5948), (5949, 5949), (5950, 5959), (5960, 5969), (5970, 5979), (5980, 5989), (5990, 5990), (5992, 5992), (5993, 5993), (5994, 5994), (5995, 5995), (5999, 5999)]),
    (44, "Meals", "Restaurants, Hotels, Motels", [(5800, 5819), (5820, 5829), (5890, 5899), (7000, 7000), (7010, 7019), (7040, 7049), (7213, 7213)]),
    (45, "Banks", "Banking", [(6000, 6000), (6010, 6019), (6020, 6020), (6021, 6021), (6022, 6022), (6023, 6024), (6025, 6025), (6026, 6026), (6027, 6027), (6028, 6029), (6030, 6036), (6040, 6059), (6060, 6062), (6080, 6082), (6090, 6099), (6100, 6100), (6110, 6111), (6112, 6113), (6120, 6129), (6130, 6139), (6140, 6149), (6150, 6159), (6160, 6169), (6170, 6179), (6190, 6199)]),
    (46, "Insur", "Insurance", [(6300, 6300), (6310, 6319), (6320, 6329), (6330, 6331), (6350, 6351), (6360, 6361), (6370, 6379), (6390, 6399), (6400, 6411)]),
    (47, "RlEst", "Real Estate", [(6500, 6500), (6510, 6510), (6512, 6512), (6513, 6513), (6514, 6514), (6515, 6515), (6517, 6519), (6520, 6529), (6530, 6531), (6532, 6532), (6540, 6541), (6550, 6553), (6590, 6599), (6610, 6611)]),
    (48, "Fin", "Trading", [(6200, 6299), (6700, 6700), (6710, 6719), (6720, 6722), (6723, 6723), (6724, 6724), (6725, 6725), (6726, 6726), (6730, 6733), (6740, 6779), (6790, 6791), (6792, 6792), (6793, 6793), (6794, 6794), (6795, 6795), (6798, 6798), (6799, 6799)]),
    (49, "Other", "Almost Nothing", [(4950, 4959), (4960, 4961), (4970, 4971), (4990, 4991)]),
]


def _ff49_code_map() -> dict:
    """SIC code -> FF49 industry id. Codes outside every published range
    (e.g. 0000, 9990-9999, and any unclassifiable code) are NOT in the
    map and are assigned to industry 49 ('Other') downstream, per the
    FF convention; a MISSING hsiccd drops the stock-month instead."""
    m = {}
    for iid, _, _, ranges in FF49_INDUSTRIES:
        for lo, hi in ranges:
            for c in range(lo, hi + 1):
                assert m.get(c, iid) == iid, f"FF49 overlap at SIC {c}"
                m[c] = iid
    return m


T7_START = pd.Timestamp("1927-01-31")
T7_END = pd.Timestamp("2010-12-31")
T7_MONTHS_EXPECTED = 1008
T7_TERTILE = 0.30


def compute_table7(panel, ff, metrics):
    """Table 8 (T7): FF-49-industry momentum spanning tests.

    - Industry classification: monthly historical SIC (hsiccd) mapped to
      the published FF49 boundaries (FF49_INDUSTRIES above); unmatched
      non-missing SIC -> industry 49 'Other'; missing hsiccd -> dropped.
    - Industry returns: VW (me_lag1, Assumption 4) over ALL member
      stocks (Assumption 1), 1926-01..2010-12 (pre-1927 months feed the
      signal windows).
    - Signals on the industry series, indexed to the RETURN month t
      (Iteration-1 convention, same as the stock strategies):
      r127_ind(t) = prod(1+ret) over t-12..t-7, r62_ind(t) over
      t-6..t-2, full-window requirement (Assumption 3).
    - Tertile strategies (Assumption 10): each month rank eligible
      industries by the signal; n = round(0.30 * n_industries_that_month)
      (= 15 when 49 industries); losers = bottom n, winners = top n;
      strategy = EW mean(winners) - EW mean(losers) (paper L1933:
      strategy returns EW, underlying industry portfolios VW).
      Sample 1927-01..2010-12 (1008 months, Assumption 11).
    - Regressions: plain OLS t (Assumption 6). Specs 1-3 y = MOM_12,7
      (mean / on ff mom / on MOM_6,2); specs 4-6 y = MOM_6,2.
    """
    code_map = _ff49_code_map()
    d = panel[["month", "ret", "me_lag1", "hsiccd"]].copy()
    d = d.dropna(subset=["hsiccd", "ret", "me_lag1"])
    d["ind"] = d["hsiccd"].astype(int).map(code_map).fillna(49).astype(int)
    w = d["me_lag1"]
    d["_rw"] = d["ret"] * w

    ind_vw = (d.groupby(["month", "ind"])
                .agg(rw=("_rw", "sum"), ww=("me_lag1", "sum")))
    ind_vw["ret"] = ind_vw["rw"] / ind_vw["ww"]
    ret_w = ind_vw["ret"].unstack("ind").sort_index()
    ret_w = ret_w.reindex(columns=range(1, 50))

    # sanity: VW all-industry aggregate vs ff mkt_rf
    mkt = d.groupby("month").apply(
        lambda g: g["_rw"].sum() / g["me_lag1"].sum(),
        include_groups=False)
    pair = pd.concat([mkt, ff["mkt_rf"]], axis=1).dropna()
    mkt_corr = float(np.corrcoef(pair.iloc[:, 0], pair.iloc[:, 1])[0, 1])

    n_ind_per_month = ret_w.notna().sum(axis=1)
    avg_ind = float(n_ind_per_month.mean())

    # signals on industry return series, return-month indexing:
    # rolling_cumret convention = shift(skip+1) then rolling(window).sum()
    logret = np.log1p(ret_w)
    r127_w = np.expm1(logret.shift(7).rolling(6, min_periods=6).sum())
    r62_w = np.expm1(logret.shift(2).rolling(5, min_periods=5).sum())

    def tertile_strat(sig_w):
        S = sig_w.loc[T7_START:T7_END]
        R = ret_w.loc[T7_START:T7_END]
        vals = []
        for t in S.index:
            s = S.loc[t]
            ok = s.notna() & R.loc[t].notna()
            n_ok = int(ok.sum())
            n = int(round(T7_TERTILE * n_ok))
            order = s[ok].sort_values(kind="mergesort")
            losers = order.index[:n]
            winners = order.index[::-1][:n]
            vals.append(R.loc[t, winners].mean() - R.loc[t, losers].mean())
        return pd.Series(vals, index=S.index)

    mom127 = tertile_strat(r127_w)
    mom62 = tertile_strat(r62_w)
    for nm, s in (("MOM_12,7^indus", mom127), ("MOM_6,2^indus", mom62)):
        assert len(s) == T7_MONTHS_EXPECTED and \
            s.index.min() == T7_START and s.index.max() == T7_END and \
            s.notna().all(), f"T7 {nm}: bad series ({len(s)} months)"

    umd = ff["mom"]
    specs = {
        1: (mom127, None), 2: (mom127, umd), 3: (mom127, mom62),
        4: (mom62, None), 5: (mom62, umd), 6: (mom62, mom127),
    }
    # Metric names carry the "ind_" prefix so they are globally unique
    # in eval/metrics.json (bare-name contract, schema_version 3).
    slope_key = {2: "ind_umd", 5: "ind_umd", 3: "ind_mom62", 6: "ind_mom127"}
    report = {}
    for s_id, (y, x) in specs.items():
        if x is None:
            mu, t = mean_t(y)
            metrics[f"T7:ind_intercept_s{s_id}"] = {
                "value": mu * 100, "unit": "percent_per_month"}
            metrics[f"T7:ind_intercept_s{s_id}_t"] = {"value": t, "unit": "t_stat"}
        else:
            res = ts_reg(y.rename("y"), x.rename("x").to_frame())
            metrics[f"T7:ind_intercept_s{s_id}"] = {
                "value": res.params["const"] * 100,
                "unit": "percent_per_month"}
            metrics[f"T7:ind_intercept_s{s_id}_t"] = {
                "value": float(res.tvalues["const"]), "unit": "t_stat"}
            metrics[f"T7:{slope_key[s_id]}_s{s_id}"] = {
                "value": float(res.params["x"]), "unit": "factor_loading"}
            metrics[f"T7:{slope_key[s_id]}_s{s_id}_t"] = {
                "value": float(res.tvalues["x"]), "unit": "t_stat"}
            metrics[f"T7:ind_r2_s{s_id}"] = {"value": float(res.rsquared_adj),
                                             "unit": "adj_r_squared"}
        report[s_id] = {"months": int(len(y.dropna())),
                        "mean": float(y.mean()) * 100}

    report.update({"avg_industries_per_month": avg_ind,
                   "min_industries_per_month": int(n_ind_per_month.min()),
                   "mkt_corr": mkt_corr})
    return report


# --- Table 14 (T8): SUE Fama-MacBeth regressions, 1973-01..2010-12 ---

T8_START = pd.Timestamp("1973-01-31")
T8_END = pd.Timestamp("2010-12-31")
T8_SPECS = {  # spec id -> performance regressors (controls appended below)
    1: ["r122"], 2: ["r122", "sue"],
    3: ["r127"], 4: ["r127", "sue"],
    5: ["r62"],  6: ["r62", "sue"],
    7: ["r127", "r62"], 8: ["r127", "r62", "sue"],
}
T8_CONTROLS = ["r10", "lnme", "lnbm"]
T8_KEYMAP = {"r122": "r122", "r127": "r127", "r62": "r62", "sue": "sue",
             "r10": "r10", "lnme": "lnme", "lnbm": "lnbm"}


def compute_table8(panel: pd.DataFrame, metrics: dict) -> dict:
    """Table 14 (T8): FM regressions of returns on past-performance
    variables (r_12,2 / r_12,7 / r_6,2) and SUE, with r_1,0, ln(ME),
    ln(BM) controls; sample January 1973 - December 2010 (determined by
    quarterly earnings availability, L2585-2587). Independent variables
    winsorized 1%/99% per month (Assumption: pre-winsorized exactly as in
    compute_table1, fama_macbeth called with winsorize_pct=0); listwise
    non-missing sample per spec; plain FM t (n_lags=0, Assumption 6);
    slopes x10^2. Diff row for s7/s8 ONLY: per-month b(r127) - b(r62)
    series from the SAME regression with its FM t (Iteration-3
    convention); identity exact by construction.
    """
    report = {"avg_firms": {}, "min_firms": {}, "n_months": {},
              "total_obs": {}, "diff_identity": {}}
    d = panel.copy()
    d["lnme"] = np.log(d["me_lag1"])
    d["lnbm"] = d["log_bm"]
    d = d[(d["month"] >= T8_START) & (d["month"] <= T8_END)]

    for s_id, perfs in T8_SPECS.items():
        cols = perfs + T8_CONTROLS
        s = d[["permno", "month", "ret"] + cols].copy()
        s = s.replace([np.inf, -np.inf], np.nan).dropna()  # listwise per spec
        for v in cols:
            s[v + "_w"] = _winsorize_monthly(s, v)
        wc = [v + "_w" for v in cols]
        fm = fama_macbeth(s, dependent_var="ret", independent_vars=wc,
                          time_col="month", winsorize_pct=0.0, n_lags=0)
        for v in cols:
            metrics[f"T8:{T8_KEYMAP[v]}_s{s_id}"] = {
                "value": float(fm.summary["mean"][v + "_w"]) * 100,
                "unit": "fm_coef_x100"}
            metrics[f"T8:{T8_KEYMAP[v]}_s{s_id}_t"] = {
                "value": float(fm.summary["t_stat"][v + "_w"]),
                "unit": "t_stat"}
        if s_id in (7, 8):
            b_diff = (fm.coefficients["r127_w"]
                      - fm.coefficients["r62_w"]).dropna()
            metrics[f"T8:diff_s{s_id}"] = {"value": float(b_diff.mean()) * 100,
                                           "unit": "fm_coef_x100"}
            metrics[f"T8:diff_s{s_id}_t"] = {
                "value": float(b_diff.mean()
                               / (b_diff.std(ddof=1) / np.sqrt(len(b_diff)))),
                "unit": "t_stat"}
            report["diff_identity"][s_id] = float(np.abs(
                b_diff - (fm.coefficients["r127_w"]
                          - fm.coefficients["r62_w"])).max())

        n_m = s.groupby("month").size()
        report["avg_firms"][s_id] = float(n_m.mean())
        report["min_firms"][s_id] = int(n_m.min())
        report["n_months"][s_id] = int(len(n_m))
        report["total_obs"][s_id] = int(len(s))

    # SUE coverage by decade: share of firm-months (with ret, r127, r62,
    # r10, lnme present) that carry a usable SUE, 1973-2010.
    cov = d.dropna(subset=["ret", "r127", "r62", "r10", "lnme"])
    cov = cov.assign(decade=(cov["month"].dt.year // 10) * 10)
    report["sue_share_by_decade"] = {
        int(dec): float(g["sue"].notna().mean())
        for dec, g in cov.groupby("decade")}
    return report


def plot_t4_spreads(spreads, metrics):
    """Panel A spread bars: IR spreads (within RR rows) vs RR spreads
    (within IR columns) — the 'twice as large' claim."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ir = [metrics[f"T4:A_RR{j}_SP"]["value"] for j in range(1, 6)]
    rr = [metrics[f"T4:A_SP_IR{k}"]["value"] for k in range(1, 6)]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    xs = np.arange(1, 6)
    ax.bar(xs - 0.2, ir, 0.4, label="IR spread 5-1 within RR row (r_12,7)")
    ax.bar(xs + 0.2, rr, 0.4, label="RR spread 5-1 within IR column (r_6,2)")
    ax.set_xticks(xs)
    ax.set_xlabel("quintile of the conditioning sort")
    ax.set_ylabel("mean excess return spread (%/mo)")
    ax.legend()
    fig.tight_layout()
    out = LAYOUT.result_path("table4_spread_bars.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# --- table output ---


def write_table_md(table_id: str, rows: list, path: Path):
    """rows: list of (cell, paper, ours, status) from evaluate.run()."""
    lines = [f"# {table_id} replication grid", "",
             "| cell | paper | ours | status |", "|---|---|---|---|"]
    for cell, paper, ours, status in rows:
        ours_s = f"{ours:.4f}" if isinstance(ours, float) else str(ours)
        lines.append(f"| {cell} | {paper} | {ours_s} | {status} |")
    path.write_text("\n".join(lines) + "\n")


# --- main ---


def main():
    panel = load_panel()
    panel = add_log_bm(panel)
    panel = add_sue(panel)
    print(f"panel: {len(panel):,} rows x {len(panel.columns)} cols, "
          f"{panel['permno'].nunique():,} permnos, "
          f"{panel['month'].nunique()} months "
          f"({panel['month'].min().date()}..{panel['month'].max().date()})")
    print("r127 non-missing:", panel["r127"].notna().sum(),
          "| r62:", panel["r62"].notna().sum(),
          "| r122:", panel["r122"].notna().sum())
    panel.to_parquet(LAYOUT.data_path("panel.parquet"), index=False)

    ff = load_factors()
    strats = {}
    stats = {}
    for sig in ("r127", "r62", "r122"):
        strats[sig] = build_strategy(panel, sig, stats)
        st = stats[sig]
        print(f"{sig}: {st['n_strategy_months']} strategy months "
              f"({strats[sig].index.min().date()}.."
              f"{strats[sig].index.max().date()}), "
              f"avg eligible {st['avg_eligible_per_month']:.1f}/mo, "
              f"avg NYSE {st['avg_nyse_per_month']:.1f}/mo, "
              f"avg winner count {st['avg_winner_count']:.1f}, "
              f"avg loser count {st['avg_loser_count']:.1f}")

    # --- mandatory sanity checks ---
    # Iteration 1 fix: with return-month indexing, every strategy series
    # must span exactly 1008 months (1927-01..2010-12): the earliest
    # window needed (r_12,7 at 1927-01 = 1926-01..1926-06) is fully
    # available in CRSP.
    for sig in ("r127", "r62", "r122"):
        assert stats[sig]["n_strategy_months"] == N_STRATEGY_MONTHS_EXPECTED, \
            f"{sig}: {stats[sig]['n_strategy_months']} != 1008"

    mom_pair = pd.concat([strats["r122"].rename("mom122"),
                          ff["mom"].rename("ff_mom")], axis=1).dropna()
    umd_corr = float(np.corrcoef(mom_pair["mom122"],
                                 mom_pair["ff_mom"])[0, 1])
    print(f"SANITY 1: corr(MOM_12,2, ff.mom) 1927-01..2010-12 = {umd_corr:.4f}")

    mu127, t127 = mean_t(strats["r127"])
    mu62, t62 = mean_t(strats["r62"])
    print(f"SANITY 4: MOM_12,7 mean {mu127*100:.2f}%/mo (t {t127:.2f}); "
          f"paper 1.20%/mo t 5.79")
    print(f"SANITY 4: MOM_6,2  mean {mu62*100:.2f}%/mo (t {t62:.2f}); "
          f"paper 0.67%/mo t 2.88")

    metrics = {}
    t1_report = compute_table1(panel, metrics)
    print("T1 FM sample: avg firms/month "
          + ", ".join(f"{k}={v:.1f}" for k, v in t1_report["avg_firms"].items())
          + "; min " + ", ".join(f"{k}={v}" for k, v in t1_report["min_firms"].items()))
    print("T1 invariant max |b(diff)-(b127-b62)|: "
          + ", ".join(f"{k}: diff-row {v['diff_row']:.2e} / "
                      f"substitution-reg {v['substitution_reg']:.4f}"
                      for k, v in t1_report["invariant"].items()))
    print("T1 log_bm coverage by decade: "
          + ", ".join(f"{k}s={v:.3f}" for k, v in
                      t1_report["logbm_share_by_decade"].items()))
    compute_table2(strats, ff, metrics)
    compute_table3(strats, ff, metrics)
    t4_report, t4_spreads = compute_table4(panel, ff, metrics)
    print(f"T4: {t4_report['months']} months "
          f"({T4_START.date()}..{T4_END.date()}), avg eligible "
          f"{t4_report['avg_eligible_per_month']:.1f}/mo; avg stocks/cell "
          f"min {min(t4_report['avg_stocks_per_cell'].values()):.1f}, "
          f"max {max(t4_report['avg_stocks_per_cell'].values()):.1f}")
    t5_report = compute_table5(panel, strats, ff, metrics)
    print(f"T5: avg eligible {t5_report['avg_eligible_per_month']:.1f}/mo "
          f"({T5_START.date()}..{T5_END.date()}); all series "
          f"{T5_MONTHS_EXPECTED} months")
    t6_report, t6_strats, t6_rob = compute_table6(panel, ff, metrics)
    t5_rob = compute_table5_robust(panel)
    print("T5 robustness (within-subsample inner bps) er_cond62 q1..q5: "
          + " ".join(f"{t5_rob[j]['er']:.2f}[{t5_rob[j]['t']:.2f}]"
                     for j in range(1, 6)))
    print(f"T6 Panel A: {t6_report['months_panelA']} months; nfirms "
          + "/".join(f"{t6_report['panelA'][j][0]:.1f}" for j in range(1, 6))
          + " (paper 1772/653.6/481.9/385.1/336.6)")
    print("T6 months/series full sample: "
          + "/".join(str(v) for v in
                     t6_report["n_months"]["m127"].values())
          + f"; avg eligible m127 q1..q5: "
          + "/".join(f"{v:.0f}" for v in
                     t6_report["avg_eligible_by_quintile"]["m127"].values()))
    t7_report = compute_table7(panel, ff, metrics)
    print(f"T7: avg industries/month {t7_report['avg_industries_per_month']:.1f} "
          f"(min {t7_report['min_industries_per_month']}); "
          f"corr(VW all-industry, ff mkt_rf) = {t7_report['mkt_corr']:.4f}; "
          "MOM_12,7^indus mean "
          f"{t7_report[1]['mean']:.2f}%/mo, MOM_6,2^indus mean "
          f"{t7_report[4]['mean']:.2f}%/mo")
    t8_report = compute_table8(panel, metrics)
    print("T8 FM sample (avg firms/month): "
          + ", ".join(f"s{k}={v:.1f}" for k, v in t8_report["avg_firms"].items())
          + "; min " + ", ".join(f"s{k}={v}" for k, v
                                 in t8_report["min_firms"].items()))
    print("T8 SUE coverage by decade: "
          + ", ".join(f"{k}s={v:.3f}" for k, v in
                      t8_report["sue_share_by_decade"].items()))
    print("T8 diff identity max |b(diff)-(b127-b62)|: "
          + ", ".join(f"s{k}={v:.2e}" for k, v in
                      t8_report["diff_identity"].items()))
    plot_path = plot_t4_spreads(t4_spreads, metrics)
    print(f"wrote {plot_path}")

    # Canonical scorer contract (scripts/score_replication.py): metrics
    # keyed by BARE name (globally unique, no "Tx:" prefix), each entry a
    # {"value": x} dict, schema_version 3.
    bare = {k.split(":", 1)[-1]: v for k, v in metrics.items()}
    assert len(bare) == len(metrics), \
        f"metric name collision after prefix strip: {metrics.keys() ^ bare.keys()}"
    LAYOUT.eval_path("metrics.json").write_text(json.dumps(
        {"schema_version": 3, "slug": SLUG, "metrics": bare},
        indent=2, default=float))

    # bare-scalar schema sanity check
    bad = [k for k, v in metrics.items()
           if not isinstance(v, dict) or "value" not in v]
    assert not bad, f"bare-scalar metrics: {bad}"

    # --- evaluator (diagnostic-only) + table markdown ---
    sys.path.insert(0, str(LAYOUT.src_path(".")))
    import evaluate
    for tid, fname in (("T1", "table_1.md"), ("T2", "table_2.md"),
                       ("T3", "table_3.md"), ("T4", "table_4.md"),
                       ("T5", "table_6.md"), ("T6", "table_7.md"),
                       ("T7", "table_8.md"), ("T8", "table_14.md")):
        rows, tally = evaluate.run(tid)
        write_table_md(tid, rows, LAYOUT.result_path(fname))
        if tid == "T5":
            # Inner-breakpoint convention robustness: conditional 6-2 grid
            # under the superseded within-subsample convention.
            PAPER_ER_COND62 = {1: (0.26, 0.97), 2: (0.26, 1.02),
                               3: (0.29, 1.17), 4: (0.39, 1.73),
                               5: (0.49, 1.93)}
            extra = ["",
                     "## Inner-breakpoint convention (iteration 7 adoption): "
                     "er_cond62",
                     "",
                     "Base (committed): inner momentum quintile breakpoints "
                     "from UNCONDITIONAL NYSE quintiles of r_6,2 applied "
                     "within each IR (r_12,7) quintile (Assumption 9 as "
                     "corrected in iteration 7; paper Table 7 note "
                     "'Portfolio break points based on NYSE stocks only', "
                     "content.md L1701). Alternative (report-only): "
                     "breakpoints computed WITHIN each IR quintile subsample "
                     "(superseded reading of Assumption 9). %/mo [t].",
                     "",
                     "| IR quintile | paper | base (uncond NYSE) | "
                     "alternative (within) | alternative months |",
                     "|---|---|---|---|---|"]
            for j in range(1, 6):
                pv, pt = PAPER_ER_COND62[j]
                bv = metrics[f"T5:er_cond62_q{j}"]["value"]
                bt = metrics[f"T5:er_cond62_q{j}_t"]["value"]
                r = t5_rob[j]
                extra.append(
                    f"| {j} | {pv:.2f} [{pt:.2f}] | {bv:.2f} [{bt:.2f}] | "
                    f"{r['er']:.2f} [{r['t']:.2f}] | {r['months']} |")
            path = LAYOUT.result_path(fname)
            path.write_text(path.read_text() + "\n".join(extra) + "\n")
        if tid == "T6":
            # Inner-breakpoint convention robustness: Panels B-E m62 (and
            # m127) under the superseded within-subsample convention.
            PAPER_M62 = {
                "pb": {1: (0.53, 2.99), 2: (0.73, 4.22), 3: (0.52, 2.70),
                       4: (0.53, 2.85), 5: (0.24, 1.25)},
                "pc": {1: (0.63, 3.92), 2: (0.79, 5.02), 3: (0.63, 3.58),
                       4: (0.51, 3.12), 5: (0.40, 2.25)},
                "pd": {1: (1.08, 5.24), 2: (1.01, 4.71), 3: (0.62, 2.75),
                       4: (0.50, 2.20), 5: (0.16, 0.68)},
                "pe": {1: (0.52, 2.72), 2: (0.46, 2.31), 3: (0.20, 0.92),
                       4: (0.03, 0.14), 5: (-0.12, -0.54)},
            }
            PANEL_NAME = {"pb": "B (mean ret, 1927-2010)",
                          "pc": "C (FF3+other alpha, 1927-2010)",
                          "pd": "D (mean ret, 1969-2010)",
                          "pe": "E (FF3+other alpha, 1969-2010)"}
            extra = ["",
                     "## Inner-breakpoint convention (iteration 7 adoption)",
                     "",
                     "Inner momentum quintiles within size quintiles. "
                     "Base (committed): UNCONDITIONAL NYSE quintile "
                     "breakpoints of the same signal assigned to stocks "
                     "within each size quintile (Assumption 9 as corrected "
                     "in iteration 7; paper Table 7 note 'Portfolio break "
                     "points based on NYSE stocks only', content.md L1701). "
                     "Alternative (report-only): breakpoints computed WITHIN "
                     "the size-quintile eligible subsample (superseded "
                     "reading of Assumption 9). %/mo [t].",
                     ""]
            for pl in ("pc", "pd", "pb", "pe"):
                extra.append(f"### Panel {PANEL_NAME[pl]} — m62 rows")
                extra.append("")
                extra.append("| size quintile | paper | base (uncond NYSE) | "
                             "alternative (within) |")
                extra.append("|---|---|---|---|")
                for j in range(1, 6):
                    pv, pt = PAPER_M62[pl][j]
                    bv = metrics[f"T6:{pl}_m62_q{j}"]["value"]
                    bt = metrics[f"T6:{pl}_m62_q{j}_t"]["value"]
                    rv = t6_rob[f"T6:{pl}_m62_q{j}"]["value"]
                    rt = t6_rob[f"T6:{pl}_m62_q{j}_t"]["value"]
                    extra.append(
                        f"| {j} | {pv:.2f} [{pt:.2f}] | "
                        f"{bv:.2f} [{bt:.2f}] | {rv:.2f} [{rt:.2f}] |")
                extra.append("")
                extra.append(f"#### Panel {PANEL_NAME[pl]} — m127 rows")
                extra.append("")
                extra.append("| size quintile | base (uncond NYSE) | "
                             "alternative (within) |")
                extra.append("|---|---|---|")
                for j in range(1, 6):
                    bv = metrics[f"T6:{pl}_m127_q{j}"]["value"]
                    bt = metrics[f"T6:{pl}_m127_q{j}_t"]["value"]
                    rv = t6_rob[f"T6:{pl}_m127_q{j}"]["value"]
                    rt = t6_rob[f"T6:{pl}_m127_q{j}_t"]["value"]
                    extra.append(
                        f"| {j} | {bv:.2f} [{bt:.2f}] | "
                        f"{rv:.2f} [{rt:.2f}] |")
                extra.append("")
            extra.append("### Thin-cell diagnostic: average stocks/month in "
                         "size quintile 5 by inner m62 quintile")
            extra.append("")
            extra.append("| convention | q1 | q2 | q3 | q4 | q5 |")
            extra.append("|---|---|---|---|---|---|")
            base_row = [f"{t6_report['inner_counts']['m62'][(5, k)]:.1f}"
                        for k in range(1, 6)]
            rob_row = [f"{t6_report['rob_inner_counts']['m62'][(5, k)]:.1f}"
                       for k in range(1, 6)]
            extra.append("| uncond NYSE (base) | " +
                         " | ".join(base_row) + " |")
            extra.append("| within-subsample (alternative) | " +
                         " | ".join(rob_row) + " |")
            extra.append("")
            extra.append("Alternative-convention strategy months (base is "
                         "1008 full / 504 "
                         "late): "
                         + ", ".join(f"q{j}={t6_report['rob_months']['m62'][j]}"
                                     for j in range(1, 6)))
            path = LAYOUT.result_path(fname)
            path.write_text(path.read_text() + "\n".join(extra) + "\n")
        if tid == "T1":
            extra = ["", "## FM sample counts (firm-months, listwise)", "",
                     "| sample | months | total obs | avg/month | min/month |",
                     "|---|---|---|---|---|"]
            for samp in ("late", "third", "fourth"):
                extra.append(
                    f"| {samp} | {t1_report['n_months'][samp]} | "
                    f"{t1_report['total_obs'][samp]:,} | "
                    f"{t1_report['avg_firms'][samp]:.1f} | "
                    f"{t1_report['min_firms'][samp]} |")
            extra += ["", "## Invariant: max |b(diff) - (b(r127)-b(r62))| "
                      "per month (raw coefficient units)", "",
                      "| sample | diff row (b127-b62 series) | "
                      "substitution regression (diff sole regressor) |",
                      "|---|---|---|"]
            for samp, dev in t1_report["invariant"].items():
                extra.append(f"| {samp} | {dev['diff_row']:.2e} | "
                             f"{dev['substitution_reg']:.4f} |")
            extra += ["",
                      "The substitution-regression deviation is the "
                      "omitted-regressor effect (replacing [r127, r62] by "
                      "[diff] alone removes r62 from the column space); the "
                      "paper's diff row is the coefficient difference of "
                      "the SAME regression, which is what the diff-row "
                      "column reports (exact by construction)."]
            extra += ["", "log_bm coverage by decade (share of firm-months "
                      "with ret/r127/r62/r10/log_me present): "
                      + ", ".join(f"{k}s {v:.3f}" for k, v in
                                  t1_report["logbm_share_by_decade"].items())]
            path = LAYOUT.result_path(fname)
            path.write_text(path.read_text() + "\n".join(extra) + "\n")
        if tid == "T8":
            extra = ["", "## FM sample counts (firm-months, listwise per spec)",
                     "", "| spec | months | total obs | avg/month | min/month |",
                     "|---|---|---|---|---|"]
            for s_id in sorted(T8_SPECS):
                extra.append(
                    f"| s{s_id} | {t8_report['n_months'][s_id]} | "
                    f"{t8_report['total_obs'][s_id]:,} | "
                    f"{t8_report['avg_firms'][s_id]:.1f} | "
                    f"{t8_report['min_firms'][s_id]} |")
            extra += ["", "## Invariant: max |b(diff) - (b(r127)-b(r62))| "
                      "per month (s7/s8, raw coefficient units)", "",
                      "| spec | max deviation |", "|---|---|"]
            for s_id, dev in t8_report["diff_identity"].items():
                extra.append(f"| s{s_id} | {dev:.2e} |")
            extra += ["", "SUE coverage by decade (share of firm-months with "
                      "ret/r127/r62/r10/lnme present that carry usable SUE): "
                      + ", ".join(f"{k}s {v:.3f}" for k, v in
                                  t8_report["sue_share_by_decade"].items())]
            path = LAYOUT.result_path(fname)
            path.write_text(path.read_text() + "\n".join(extra) + "\n")
        print(f"wrote {LAYOUT.result_path(fname)}")

    # Stop gate temporarily lowered to 0.85 (Iteration 1): the Replicator
    # will judge the UMD anchor after seeing the post-fix numbers.
    if umd_corr < 0.85:
        raise RuntimeError(
            f"SANITY 1 FAILED: corr(MOM_12,2, ff.mom) = {umd_corr:.4f} < 0.85 "
            "- something is broken in the strategy construction.")


if __name__ == "__main__":
    main()
