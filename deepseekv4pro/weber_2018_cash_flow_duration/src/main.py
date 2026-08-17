"""
Replication of Weber (2018) "Cash flow duration and the term structure of equity
returns", JFE 128, 486-503.

Iteration 1: CORE data pipeline.
  - CRSP monthly universe (PIT common stocks, ex-finl/utilities, no price floor)
  - Compustat fundamentals + book-equity cascade
  - Dechow et al. (2004) implied cash-flow duration (Eq. 2, parameterized per Weber)
  - firm-year duration table + analysis-ready monthly panel

Iteration 2: portfolio returns + Table 2 (mean/CAPM/Sharpe/VW/no-delisting) and
  Table 3 (FF3/FF4/FF5 alphas), plus decile-spread plots and the diagnostic
  per-cell evaluator (src/evaluate.py).
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
from clickhouse_driver import Client

from utils.env import get_clickhouse_config
from utils.paths import paper_layout

# Make this file's own directory importable (table4_5.py lives here) regardless of
# how main.py is invoked (runpy, python src/main.py, or from the repo root).
import pathlib as _pl
if str(_pl.Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
SLUG = "weber_2018_attempt2_deepseek"
LAYOUT = paper_layout(SLUG)
LAYOUT.ensure()

_CFG = get_clickhouse_config()

# Module-level flag: price floor abs(prc) >= 5 (assumption A2). REVERSED (iteration 4):
# no price floor — the $5 floor inflates universe EW from 1.24% to 2.01%/mo by removing
# low-return penny stocks, incompatible with the paper's Table 2 means. PRICE_FILTER=False
# removes the price stage from the funnel counts (panel.sql has the predicate removed).
PRICE_FILTER = False

START_DATE = "1962-07-01"
END_DATE = "2014-06-30"

# Duration parameters (paper preprocessing_rules.json var_dur_parameters):
# r=0.12, T=15, ar_roe=0.4067 (paper "0.41"), ar_sg=0.2411 (paper "0.24"),
# roe_ss=0.12, sg_ss=0.06.
R = 0.12
T_HORIZON = 15
AR_ROE = 0.4067
AR_SG = 0.2411
ROE_SS = 0.12
SG_SS = 0.06


# --------------------------------------------------------------------------- #
# ClickHouse connection + helpers
# --------------------------------------------------------------------------- #
SQL_DIR = LAYOUT.src_path("sql")


def _client() -> Client:
    return Client(
        host=_CFG["host"],
        port=int(_CFG["port"]),
        user=_CFG["user"],
        password=_CFG["password"],
        database=_CFG["database"],
        settings={"max_execution_time": 600},
    )


def q(sql: str) -> pd.DataFrame:
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


def q_file(name: str) -> pd.DataFrame:
    return q((SQL_DIR / name).read_text())


# --------------------------------------------------------------------------- #
# Funnel counts (per stage, per decade)
# --------------------------------------------------------------------------- #
def _price_cond() -> str:
    # Used to template the price floor into a SQL predicate. When PRICE_FILTER is
    # False the predicate is a no-op (AND (1=1)).
    return "AND abs(prc) >= 5" if PRICE_FILTER else "AND (1 = 1)"


def funnel_counts() -> pd.DataFrame:
    """Count raw msf rows through each universe-filter stage, per decade."""
    valid_ret = "AND m.ret IS NOT NULL AND m.ret > -1.0"
    sql = f"""
    WITH base AS (
        SELECT m.permno, toDate32(m.date) AS date, m.prc, m.ret,
               h.hshrcd AS hshrcd, toUInt16(h.hexcd) AS hexcd, h.hsiccd AS hsiccd
        FROM crsp_202601.msf AS m
        INNER JOIN crsp_202601.msfhdr AS h
          ON m.permno = h.permno
         AND toDate32(m.date) >= toDate32(h.begdat)
         AND toDate32(m.date) <= toDate32(h.enddat)
        WHERE toDate32(m.date) >= toDate32('{START_DATE}')
          AND toDate32(m.date) <= toDate32('{END_DATE}')
    ),
    bucketed AS (
        SELECT *, concat(toString(intDiv(toYear(date), 10) * 10), 's') AS bucket
        FROM base
    )
    SELECT bucket AS decade,
        count() AS n_raw,
        countIf(hshrcd IN (10,11) AND hexcd IN (1,2,3)) AS n_pit,
        countIf(hshrcd IN (10,11) AND hexcd IN (1,2,3)
                AND (hsiccd < 4900 OR hsiccd >= 5000)
                AND (hsiccd < 6000 OR hsiccd >= 7000)) AS n_sic,
        countIf(hshrcd IN (10,11) AND hexcd IN (1,2,3)
                AND (hsiccd < 4900 OR hsiccd >= 5000)
                AND (hsiccd < 6000 OR hsiccd >= 7000)
                {_price_cond()}) AS n_price,
        countIf(hshrcd IN (10,11) AND hexcd IN (1,2,3)
                AND (hsiccd < 4900 OR hsiccd >= 5000)
                AND (hsiccd < 6000 OR hsiccd >= 7000)
                {_price_cond()}
                AND ret IS NOT NULL AND ret > -1.0) AS n_ret
    FROM bucketed
    GROUP BY bucket
    ORDER BY bucket
    SETTINGS join_algorithm = 'partial_merge',
             max_execution_time = 600,
             max_rows_to_read = 10000000000,
             timeout_before_checking_execution_speed = 0
    """
    return q(sql)


# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #
def load_universe() -> pd.DataFrame:
    df = q_file("universe_monthly.sql")
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df = df.sort_values(["permno", "date"]).reset_index(drop=True)
    return df


def load_funda() -> pd.DataFrame:
    df = q_file("compustat_funda.sql")
    df["datadate"] = pd.to_datetime(df["datadate"])
    df["lpermno"] = df["lpermno"].astype("Int64")
    return df.sort_values(["gvkey", "fyear", "datadate"]).reset_index(drop=True)


def load_delistings() -> pd.DataFrame:
    return q_file("delisting.sql")


def acquire_fundamentals_duration() -> pd.DataFrame:
    """Read the persisted fundamentals_duration parquet (built in build_panel)."""
    return pd.read_parquet(LAYOUT.data_path("fundamentals_duration.parquet"))


# --------------------------------------------------------------------------- #
# Book equity cascade (paper's order, assumption A5/A7)
# --------------------------------------------------------------------------- #
def book_equity(funda: pd.DataFrame) -> pd.DataFrame:
    """Per firm-year: shareholders_equity -> pstk_pref -> BE (Compustat-only)."""
    f = funda.copy()

    seq = f["seq"]
    ceq = f["ceq"]
    pstk = f["pstk"].fillna(0.0)

    # 1. shareholders equity: seq else (ceq + pstk) else (at - lt)
    shareholders = seq.where(seq.notna(),
                             ceq.where(ceq.notna(), f["at"] - f["lt"]).fillna(0.0) + pstk)

    # 2. preferred stock: pstkrv (if >0) -> pstkl (if >0) -> pstk
    pstkrv = f["pstkrv"].fillna(0.0)
    pstkl = f["pstkl"].fillna(0.0)
    pstk_pref = pstk
    pstk_pref = pstk_pref.where(~(pstkl > 0), pstkl)
    pstk_pref = pstk_pref.where(~(pstkrv > 0), pstkrv)

    # 3. BE = shareholders + txdb + itcb - pstk_pref  (Moody's supplement NOT available, A7)
    be = shareholders + f["txdb"].fillna(0.0) + f["itcb"].fillna(0.0) - pstk_pref

    f["be"] = be
    f["se"] = shareholders
    f["pstk_pref"] = pstk_pref
    return f


# --------------------------------------------------------------------------- #
# Duration (Dechow et al. 2004 / Weber eq. 2), fully vectorized
# --------------------------------------------------------------------------- #
def compute_duration(funda_be: pd.DataFrame, me_at_fye: pd.Series) -> pd.DataFrame:
    """
    Duration for each firm-year t. Inputs:
      funda_be : one row per (gvkey, fyear) with be, ib, sale.
      me_at_fye : market equity (dollars) at the fiscal-year-end month, indexed to
                  match funda_be rows (same order).
    """
    f = funda_be.reset_index(drop=True).copy()
    f["p"] = me_at_fye.reset_index(drop=True)

    # BE_{t-1}: lag BE within gvkey by fyear (fyear diff == 1 requirement in SQL spirit)
    f = f.sort_values(["gvkey", "fyear"]).reset_index(drop=True)
    f["be_lag"] = f.groupby("gvkey")["be"].shift(1)
    f["ib_lag"] = f.groupby("gvkey")["ib"].shift(1)
    f["sale_lag"] = f.groupby("gvkey")["sale"].shift(1)
    f["datadate_lag"] = f.groupby("gvkey")["datadate"].shift(1)
    f["fyear_lag"] = f.groupby("gvkey")["fyear"].shift(1)

    # fiscal-year adjacency (assumption A6): fyear diff = 1 AND datadate gap in [300,430] days
    f["fyear_diff"] = f["fyear"] - f["fyear_lag"]
    f["dd_gap"] = (f["datadate"] - f["datadate_lag"]).dt.days
    valid_adj = (f["fyear_diff"] == 1) & (f["dd_gap"].between(300, 430))

    # ROE = ib_t / BE_{t-1}; requires BE_{t-1} > 0 for a meaningful (finite) ROE.
    # Sales growth = sale_t/sale_{t-1} - 1; requires sale_{t-1} > 0.
    be_lag_ok = (f["be_lag"].notna()) & (f["be_lag"] > 0)
    sale_lag_ok = (f["sale_lag"].notna()) & (f["sale_lag"] > 0)
    f["roe"] = np.where(valid_adj & be_lag_ok, f["ib"] / f["be_lag"], np.nan)
    f["g"] = np.where(valid_adj & sale_lag_ok, f["sale"] / f["sale_lag"] - 1.0, np.nan)

    # Persist the RAW (un-winsorized) inputs before winsorization — the input-vs-output
    # winsorization lever test (iteration 4) needs these on disk to compare against the
    # winsorized versions that actually feed the duration recursion.
    f["roe_raw"] = f["roe"]
    f["g_raw"] = f["g"]

    # Paper winsorizes "all variables at 1%/99%" (L176), annually cross-sectionally
    # (A4). Winsorize the ROE and sales-growth INPUTS within each fyear before the
    # duration recursion, otherwise a handful of extreme roe/g blow the durations to
    # ~1e6 and dominate the cross-section (paper Table 1 mean 18.77 / std 5.37).
    def _clip_cs(s):
        lo, hi = s.quantile(0.01), s.quantile(0.99)
        return s.clip(lo, hi)
    f["roe"] = f.groupby("fyear")["roe"].transform(_clip_cs)
    f["g"] = f.groupby("fyear")["g"].transform(_clip_cs)

    # Book equity from Compustat is in MILLIONS of USD; market equity (P) from CRSP
    # is in DOLLARS. Duration Eq. (2) is a ratio CF/P so both must share units.
    # Convert BE to dollars (x1e6) so the cash-flow stream is dollar-consistency with P.
    dur = _duration_vectorized(f["roe"].to_numpy(), f["g"].to_numpy(),
                                f["be"].to_numpy() * 1e6, f["p"].to_numpy())
    f["dur"] = dur
    return f


def _duration_vectorized(roe: np.ndarray, g: np.ndarray,
                         be: np.ndarray, p: np.ndarray) -> np.ndarray:
    """Vectorized Dechow et al. (2004) duration over the (N, T) recursion.

    Forecasts for s=1..T:
      roe_s  = roe_ss + ar_roe^s   * (roe - roe_ss)
      g_s    = sg_ss  + ar_sg^s    * (g   - sg_ss)
      bv_s   = bv_{s-1} * (1 + g_s),  bv_0 = be
      cf_s   = bv_{s-1} * (roe_s - g_s)
      pv_s   = cf_s / (1+r)^s
    Dur = [ sum s*pv_s + (T + (1+r)/r) * (p - sum pv_s) ] / p
    """
    n = roe.shape[0]
    s = np.arange(1, T_HORIZON + 1, dtype=np.float64)  # (T,)

    ar_roe_s = np.power(AR_ROE, s)      # (T,)
    ar_sg_s = np.power(AR_SG, s)
    disc = np.power(1.0 + R, s)         # (1+r)^s

    roe = np.where(np.isfinite(roe), roe, ROE_SS)
    g = np.where(np.isfinite(g), g, SG_SS)
    be = np.where(np.isfinite(be) & (be > 0), be, 0.0)
    p = np.where(np.isfinite(p) & (p > 0), p, 0.0)

    # (N, T) arrays
    roe_dev = (roe[:, None] - ROE_SS)               # (N,1)
    g_dev = (g[:, None] - SG_SS)
    roe_all = ROE_SS + ar_roe_s[None, :] * roe_dev  # (N,T)
    g_all = SG_SS + ar_sg_s[None, :] * g_dev

    bv = np.empty((n, T_HORIZON + 1), dtype=np.float64)
    bv[:, 0] = be
    cf_pv = np.empty((n, T_HORIZON), dtype=np.float64)
    for k in range(T_HORIZON):
        bv_prev = bv[:, k]
        g_k = g_all[:, k]
        roe_k = roe_all[:, k]
        bv[:, k + 1] = bv_prev * (1.0 + g_k)
        cf_k = bv_prev * (roe_k - g_k)
        cf_pv[:, k] = cf_k / disc[k]

    pv_sum = cf_pv.sum(axis=1)                          # (N,)
    weighted = (cf_pv * s[None, :]).sum(axis=1)         # (N,)

    terminal = (T_HORIZON + (1.0 + R) / R) * (p - pv_sum)
    dur = (weighted + terminal) / p
    return dur


# --------------------------------------------------------------------------- #
# Self-checks
# --------------------------------------------------------------------------- #
def _macaulay_duration(roe: np.ndarray, g: np.ndarray, be: np.ndarray, p: np.ndarray,
                       sign_flip: int = 1, bv_one_minus_g: bool = False) -> np.ndarray:
    """Numeric Macaulay check of the same cash-flow stream (long tail to 2000).

    c is the level perpetuity whose PV equals p - sum_{s<=T} cf_s/(1+r)^s:
       c = r * (1+r)^T * (p - sum cf_s/(1+r)^s)
    Dur (numeric) = [ sum_{s=1..T} s*cf_s/(1+r)^s
                    + sum_{s=T+1..T+2000} s*c/(1+r)^s ] / p  (c constant for s>T).
    """
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
        bv[:, k + 1] = bv_prev * ((1.0 + sign_flip * g_k) if not bv_one_minus_g
                                  else (1.0 - g_k))
        cf_k = bv_prev * (roe_k - sign_flip * g_k)
        cf_pv[:, k] = cf_k / disc[k]

    pv_sum = cf_pv.sum(axis=1)
    weighted = (cf_pv * s[None, :]).sum(axis=1)

    c = R * np.power(1.0 + R, T_HORIZON) * (p - pv_sum)
    s_tail = np.arange(T_HORIZON + 1, T_HORIZON + 2000 + 1, dtype=np.float64)
    tail_w = np.sum(s_tail / np.power(1.0 + R, s_tail))  # scalar
    tail_term = c * tail_w

    dur = (weighted + tail_term) / p
    return dur


# --------------------------------------------------------------------------- #
# Delisting adjustment (Shumway + Cohen proration)
# --------------------------------------------------------------------------- #
def build_delist_adj(delisting: pd.DataFrame) -> pd.DataFrame:
    """Expand dsedelist rows into (permno, adj_month, adj_ret) rows.

    For each delisting event with an effective dlret, distribute the geometric
    factor (1+dlret)^(1/n)-1 across n panel months starting at last_trade_month
    (the last full month of trading) through the landing month.
    """
    rows = []
    for r in delisting.itertuples():
        dlret = r.dlret_eff
        if dlret is None or dlret <= -1.0:
            continue  # a -100% return is a genuine total loss; leave raw
        n = int(r.n_months)
        last = pd.Timestamp(r.last_trade_month)
        factor = (1.0 + dlret) ** (1.0 / n) - 1.0
        months = pd.date_range(last, periods=n, freq="MS")
        for m in months:
            rows.append((int(r.permno), m, factor))
    cols = ["permno", "adj_month", "adj_ret"]
    if not rows:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(rows, columns=cols)


# --------------------------------------------------------------------------- #
# Panel assembly
# --------------------------------------------------------------------------- #
def build_panel() -> tuple[pd.DataFrame, pd.DataFrame]:
    """return (panel, fundamentals_duration)."""
    print("Loading universe ...", flush=True)
    uni = load_universe()
    print(f"  universe rows: {len(uni)}", flush=True)

    print("Loading Compustat ...", flush=True)
    funda = load_funda()
    print(f"  funda rows (linked, >=2yr): {len(funda)}", flush=True)

    print("Computing book equity ...", flush=True)
    funda = book_equity(funda)

    # market equity at fiscal-year-end month: universe_monthly has me_dollars at CRSP
    # month-end; match funda datadate month -> join on (permno, month-start).
    # lpermno already links funda->CRSP permno (mapped in compustat_funda.sql).
    uni_month = uni[["permno", "month", "me_dollars"]].copy()
    uni_month = uni_month.groupby(["permno", "month"], as_index=False)["me_dollars"].last()

    funda = funda.rename(columns={"lpermno": "permno"})
    funda["month"] = funda["datadate"].dt.to_period("M").dt.to_timestamp()
    funda = funda.merge(uni_month.rename(columns={"me_dollars": "p"}),
                        on=["permno", "month"], how="left")

    print("Computing duration ...", flush=True)
    funda = compute_duration(funda, funda["p"])
    valid = (funda["be"].notna()) & (funda["be"] > 0) & (funda["p"].notna()) & (funda["p"] > 0)
    dur_table = funda[valid].copy()

    # Keep the later datadate if two fyear rows collide in a sort (per spec).
    dur_table = dur_table.sort_values("datadate").drop_duplicates(
        subset=["permno", "fyear"], keep="last")

    # self-checks
    _self_check_identity(dur_table)
    _self_check_distribution(dur_table)

    print("Building panel skeleton ...", flush=True)
    panel = q_file("panel.sql")
    panel["month"] = pd.to_datetime(panel["month"])
    panel["date"] = pd.to_datetime(panel["date"])

    # delisting-adjusted returns
    print("Applying delisting adjustment ...", flush=True)
    delist = load_delistings()
    dadj = build_delist_adj(delist)
    if len(dadj):
        panel = panel.merge(dadj, left_on=["permno", "month"],
                            right_on=["permno", "adj_month"], how="left")
        panel["ret_dl"] = np.where(
            panel["adj_ret"].notna(),
            (1.0 + panel["ret"]) * (1.0 + panel["adj_ret"]) - 1.0,
            panel["ret"],
        )
    else:
        panel["ret_dl"] = panel["ret"]

    # ---- duration sorts (annual end-of-June on Dur of fiscal year t-1) ----
    # sort_year t uses fyear = t-1 (any fiscal-end month). Dur table rows already
    # keyed by (permno, fyear). Map fyear -> sort_year = fyear + 1.
    dur = dur_table[["permno", "fyear", "dur", "p"]].copy()
    dur = dur.rename(columns={"dur": "dur_raw"})
    dur["sort_year"] = dur["fyear"] + 1
    dur = dur[dur["sort_year"].between(1963, 2013)]

    # winsorize Dur cross-sectionally at 1%/99% within each sort year (assumption A4)
    def ws(g):
        lo, hi = g["dur_raw"].quantile(0.01), g["dur_raw"].quantile(0.99)
        return g["dur_raw"].clip(lo, hi)
    dur["dur"] = dur.groupby("sort_year", group_keys=False).apply(ws)

    # deciles 1..10 by Dur over ALL universe stocks (no size screen for T2-T6)
    dur["bin"] = dur.groupby("sort_year")["dur"].rank(method="first", pct=True)
    dur["bin"] = np.ceil(dur["bin"] * 10).astype(int).clip(1, 10)

    # June formation ME (held constant across cohort) for VW weighting.
    # me_jun = me_dollars at end-of-June of sort_year (== June of calendar sort_year).
    june_me = uni.copy()
    june_me["month"] = june_me["month"].dt.to_period("M").dt.to_timestamp()
    june = june_me[(june_me["month"].dt.month == 6)]
    june["sort_year"] = june["month"].dt.year
    june = june[["permno", "sort_year", "me_dollars"]].rename(columns={"me_dollars": "me_jun"})
    june = june.drop_duplicates(["permno", "sort_year"], keep="last")

    dur = dur.merge(june, on=["permno", "sort_year"], how="left")

    # attach sort metadata to panel via (permno, sort_year)
    sort_cols = ["permno", "sort_year", "bin", "dur", "dur_raw", "me_jun"]
    panel = panel.merge(dur[sort_cols], on=["permno", "sort_year"], how="left")

    panel = panel.rename(columns={
        "ret": "ret", "ret_dl": "ret_dl",
    })
    out_cols = ["permno", "date", "month", "sort_year", "bin", "dur", "dur_raw",
                "ret", "ret_dl", "me_prev", "me_jun"]
    panel = panel[out_cols]
    panel = panel[panel["sort_year"].between(1963, 2013)]
    panel = panel[panel["dur"].notna()]  # only rows in a duration cohort

    # fundamentals_duration for downstream (T1 and T4 parameter variations).
    # Persist BOTH the winsorized inputs (roe, g) and the raw un-winsorized inputs
    # (roe_raw, g_raw) for the input-vs-output winsorization lever test.
    fundamentals_duration = dur_table[
        ["permno", "gvkey" if "gvkey" in dur_table.columns else "permno",
         "fyear", "fyr" if "fyr" in dur_table.columns else "fyear",
         "be", "roe", "g", "roe_raw", "g_raw", "p", "dur"]
    ]
    fundamentals_duration = fundamentals_duration.rename(columns={"dur": "dur_raw"})

    return panel, fundamentals_duration


# --------------------------------------------------------------------------- #
# Self-check implementations
# --------------------------------------------------------------------------- #
def _self_check_identity(dur_table: pd.DataFrame) -> None:
    roe = dur_table["roe"].to_numpy()
    g = dur_table["g"].to_numpy()
    be = dur_table["be"].to_numpy() * 1e6   # dollars, matching P units
    p = dur_table["p"].to_numpy()
    dur_closed = dur_table["dur"].to_numpy()

    macaulay = _macaulay_duration(roe, g, be, p)
    diff = np.abs(dur_closed - macaulay)
    # Relative tolerance: extreme durations (|dur| up to ~1e5 to ~1e6 from
    # un-winsorized ROE/g outliers) carry ~1e-9 relative float error; an absolute
    # 1e-6 bound would spuriously fail on those legitimately-finite rows. Assert
    # relative error < 1e-6 on finite durations and mask the non-finite ones.
    finite = np.isfinite(dur_closed) & np.isfinite(macaulay)
    rel = np.abs(dur_closed[finite] - macaulay[finite]) / np.maximum(
        np.abs(dur_closed[finite]), 1e-8)
    assert rel.max() < 1e-6, f"Identity check failed: max rel err = {rel.max():.3e}"

    # two wrong variants must break the assertion by a large margin
    v1 = _macaulay_duration(roe, g, be, p, sign_flip=-1)
    d1 = np.abs(dur_closed - v1).max()
    v2 = _macaulay_duration(roe, g, be, p, bv_one_minus_g=True)
    d2 = np.abs(dur_closed - v2).max()

    print("  [self-check] identity: correct max|diff| = %.3e (max rel err %.3e)"
          % (diff.max(), rel.max()), flush=True)
    print("  [self-check] identity: sign-flip variant max|diff| = %.3f" % d1, flush=True)
    print("  [self-check] identity: (1-g) BV variant max|diff| = %.3f" % d2, flush=True)
    for lbl, dd in (("sign-flip", d1), ("BV (1-g)", d2)):
        assert dd > 1.0 or (dd / (diff.max() + 1e-12)) > 1e6, \
            f"variant '{lbl}' failed to discriminate (max|diff|={dd:.3f})"


def _self_check_distribution(dur_table: pd.DataFrame) -> None:
    def _qs(x, label):
        print(f"  [self-check] {label}: mean={x.mean():.4f} std={x.std():.4f} "
              f"p1={x.quantile(.01):.4f} p50={x.quantile(.5):.4f} p99={x.quantile(.99):.4f} "
              f"n={len(x)}", flush=True)
        return x

    full = dur_table["dur"].dropna()
    _qs(full, "Dur full sample (raw)")

    # Cross-sectionally winsorized Dur within sort year (A4) -- the values that
    # actually feed the decile sort. Paper Table 1 mean 18.77 / std 5.37.
    d = dur_table[["dur", "fyear"]].copy()
    d["sort_year"] = d["fyear"] + 1
    def _clip_cs(s):
        lo, hi = s.quantile(0.01), s.quantile(0.99)
        return s.clip(lo, hi)
    d["dur_w"] = d.groupby("sort_year")["dur"].transform(_clip_cs)
    _qs(d["dur_w"].dropna(), "Dur full sample (cross-sectionally winsorized @1/99)")

    # June 1981+ sample above the 20th size percentile would require the 13F/size
    # linkage (iteration 2). Report the raw 1981+ full-cross-section here.
    sub = d[d["fyear"] >= 1980]["dur_w"].dropna()
    _qs(sub, "Dur fyear>=1980, winsorized (proxy for 1981+)")


# --------------------------------------------------------------------------- #
# Metrics output
# --------------------------------------------------------------------------- #
def write_metrics(panel: pd.DataFrame, dur_table: pd.DataFrame,
                  funnel: pd.DataFrame) -> None:
    metrics = {}

    n_sort = panel.groupby("sort_year")["permno"].nunique()
    metrics["panel_monthly_rows"] = {"value": int(len(panel)), "unit": "rows"}
    metrics["panel_n_sort_years"] = {"value": int(len(n_sort)), "unit": "count"}
    metrics["panel_n_firms_min"] = {"value": int(n_sort.min()), "unit": "count"}
    metrics["panel_n_firms_median"] = {"value": int(n_sort.median()), "unit": "count"}
    metrics["panel_n_firms_max"] = {"value": int(n_sort.max()), "unit": "count"}
    panel["y"] = panel["month"].dt.year
    obs = panel.groupby("month")["permno"].nunique()
    obs_decade = obs.groupby(obs.index.year // 10 * 10).mean()
    for dec, v in obs_decade.items():
        metrics[f"avg_obs_per_month_{int(dec)}s"] = {"value": float(v), "unit": "rows/month"}

    for row in funnel.itertuples():
        metrics[f"funnel_{row.decade}_raw"] = {"value": int(row.n_raw), "unit": "count"}
        metrics[f"funnel_{row.decade}_pit"] = {"value": int(row.n_pit), "unit": "count"}
        metrics[f"funnel_{row.decade}_sic"] = {"value": int(row.n_sic), "unit": "count"}
        metrics[f"funnel_{row.decade}_price"] = {"value": int(row.n_price), "unit": "count"}
        metrics[f"funnel_{row.decade}_ret"] = {"value": int(row.n_ret), "unit": "count"}

    dur_col = "dur" if "dur" in dur_table.columns else "dur_raw"
    full = dur_table[dur_col].dropna()
    metrics["dur_full_mean"] = {"value": float(full.mean()), "unit": "years"}
    metrics["dur_full_std"] = {"value": float(full.std()), "unit": "years"}

    bin_cells = panel.groupby(["sort_year", "bin"])["permno"].nunique()
    metrics["deciles_median_stocks"] = {
        "value": float(bin_cells.median()) if len(bin_cells) else float("nan"),
        "unit": "stocks/bin",
    }

    out = {"schema_version": 2, "slug": SLUG, "metrics": metrics}
    LAYOUT.eval_path("metrics.json").write_text(json.dumps(out, indent=2, default=str))


# --------------------------------------------------------------------------- #
# Iteration 2: portfolio returns, Tables 2 & 3, plots, metrics
# --------------------------------------------------------------------------- #
# matplotlib must import Agg before pyplot for headless PNG rendering.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


BIN_COLS = [f"D{i}" for i in range(1, 11)] + ["D1D10"]  # D1..D10, spread


def load_factors() -> pd.DataFrame:
    """FF factors + rf, aligned on year-month tuple (Calendar month-end index)."""
    df = q_file("ff_factors.sql")
    df["dt"] = pd.to_datetime(df["dt"])
    df = df.sort_values("dt").reset_index(drop=True)
    return df


def _portfolio_returns(panel: pd.DataFrame, ret_col: str) -> pd.DataFrame:
    """Monthly (bin x month) EW/VW returns.

    EW = mean(ret) within (bin, month).
    VW = sum(ret * me_jun) / sum(me_jun) within (bin, month); me_jun held
        constant across the cohort (A8). Stocks with missing me_jun fall back to
        EW (their contribution is the plain mean of the bin-month residual).
    Returns a DataFrame indexed by month with one value column per bin (D1..D10).
    """
    p = panel[["month", "bin", ret_col, "me_jun"]].copy()

    # EW return per (bin, month)
    ew = p.groupby(["month", "bin"])[ret_col].mean().rename("ew").reset_index()

    # VW return per (bin, month): me_jun-weighted. Missing me_jun -> EW fallback.
    has_me = p["me_jun"].notna() & (p["me_jun"] > 0)
    vw_num = p.loc[has_me].copy()
    vw_num["weighted"] = vw_num[ret_col] * vw_num["me_jun"]
    vw_num = vw_num.groupby(["month", "bin"]).agg(
        num=("weighted", "sum"), den=("me_jun", "sum")).reset_index()
    n_missing_me = int((~has_me).sum())

    out = ew.merge(vw_num, on=["month", "bin"], how="left")
    out["vw"] = np.where(out["den"].notna() & (out["den"] > 0),
                         out["num"] / out["den"], out["ew"])

    def _wide(key_col, val_col):
        w = out.pivot_table(index="month", columns="bin", values=val_col)
        w = w.reindex(columns=range(1, 11))
        w.columns = [f"D{i}" for i in range(1, 11)]
        return w

    ew_wide = _wide("ew", "ew")
    vw_wide = _wide("vw", "vw")
    return ew_wide, vw_wide, n_missing_me


def _align_excess(port_rets: pd.DataFrame, factors: pd.DataFrame) -> pd.DataFrame:
    """Subtract rf (monthly, decimal) from portfolio returns; returns excess returns.

    port_rets: month-indexed, columns D1..D10 (decimal returns).
    """
    ff = factors.set_index("dt")["rf"]
    rf = ff.groupby(ff.index.to_period("M")).last()
    rf.index = rf.index.to_timestamp()
    aligned = port_rets.join(rf.rename("rf"), how="left")
    for c in port_rets.columns:
        aligned[c] = aligned[c] - aligned["rf"]
    return aligned.drop(columns=["rf"])


def _ols(port_excess: pd.Series, X: pd.DataFrame) -> dict:
    """OLS (plain SEs) of a portfolio excess-return series on factor columns.

    Returns dict with alpha (intercept), beta(s), and coefficient names.
    """
    y = port_excess.dropna()
    Xa = X.reindex(y.index).dropna()
    y = y.reindex(Xa.index)
    Xc = sm.add_constant(Xa)
    model = sm.OLS(y, Xc).fit()
    return {"alpha": float(model.params["const"]),
            "betas": {c: float(model.params[c]) for c in X.columns}}


def compute_table2(panel: pd.DataFrame, factors: pd.DataFrame) -> dict:
    """Panel A mean/CAPM, Panel B Sharpe, Panel C VW, Panel D no-delisting.

    All values in percent per month (paper's unit), except beta (dimensionless)
    and Sharpe (dimensionless monthly).
    """
    res = {}

    # ---- delisting-adjusted EW (Panel A) and no-delisting EW (Panel D) ----
    ew_dl, vw_dl, n_miss_me = _portfolio_returns(panel, "ret_dl")
    ew_nodl, _, _ = _portfolio_returns(panel, "ret")

    ew_ex = _align_excess(ew_dl, factors)
    nodl_ex = _align_excess(ew_nodl, factors)
    vw_ex = _align_excess(vw_dl, factors)

    # Panel A: mean excess returns (%/mo)
    ewa_mean = ew_ex.mean() * 100.0
    ewa_mean["D1D10"] = ewa_mean["D1"] - ewa_mean["D10"]
    for c in BIN_COLS:
        res[f"mean_{c}"] = float(ewa_mean[c])

    # CAPM regression per portfolio (Panel A): R_i - rf = alpha + beta * mkt_rf
    mkt = factors.set_index("dt")["mkt_rf"]
    mkt.index = mkt.index.to_period("M").to_timestamp()
    X = pd.DataFrame({"mkt_rf": mkt})
    for i in range(1, 11):
        c = f"D{i}"
        fit = _ols(ew_ex[c], X)
        res[f"beta_capm_{c}"] = fit["betas"]["mkt_rf"]
        res[f"alpha_capm_{c}"] = fit["alpha"] * 100.0
    # spread CAPM
    spread = (ew_ex["D1"] - ew_ex["D10"]).rename("spread")
    fit_sp = _ols(spread, X)
    res["beta_capm_D1D10"] = fit_sp["betas"]["mkt_rf"]
    res["alpha_capm_D1D10"] = fit_sp["alpha"] * 100.0

    # Panel B: monthly Sharpe of excess returns (mean/std)
    def _sharpe(s):
        return float(s.mean() / s.std(ddof=1)) if s.std(ddof=1) > 0 else float("nan")
    for i in range(1, 11):
        res[f"sharpe_D{i}"] = _sharpe(ew_ex[f"D{i}"])
    res["sharpe_D1D10"] = _sharpe(spread)

    # Panel C: VW means (%/mo)
    vwa_mean = vw_ex.mean() * 100.0
    vwa_mean["D1D10"] = vwa_mean["D1"] - vwa_mean["D10"]
    for c in BIN_COLS:
        res[f"vw_mean_{c}"] = float(vwa_mean[c])

    # Panel D: no-delisting EW means (%/mo)
    nodl_mean = nodl_ex.mean() * 100.0
    nodl_mean["D1D10"] = nodl_mean["D1"] - nodl_mean["D10"]
    for c in BIN_COLS:
        res[f"nodl_mean_{c}"] = float(nodl_mean[c])

    res["_vw_n_missing_me"] = n_miss_me
    return res, ew_ex, spread, ew_dl


def compute_table3(ew_ex: pd.DataFrame, spread: pd.Series,
                   factors: pd.DataFrame) -> dict:
    """FF3 / FF4 / FF5 alphas (percent per month) for D1..D10 and the spread."""
    res = {}
    ff = factors.set_index("dt")
    fact_cols = {
        "ff3": ["mkt_rf", "smb", "hml"],
        "ff4": ["mkt_rf", "smb", "hml", "mom"],
        "ff5": ["mkt_rf", "smb", "hml", "rmw", "cma"],
    }
    factories = {k: pd.DataFrame({c: ff[c] for c in cols})
                 for k, cols in fact_cols.items()}
    for k in factories:  # year-month index
        factories[k].index = factories[k].index.to_period("M").to_timestamp()

    for tag, Xf in factories.items():
        for i in range(1, 11):
            c = f"D{i}"
            fit = _ols(ew_ex[c], Xf)
            res[f"{tag}_alpha_{c}"] = fit["alpha"] * 100.0
        fit_sp = _ols(spread, Xf)
        res[f"{tag}_alpha_D1D10"] = fit_sp["alpha"] * 100.0
    return res


def write_table2_md(metrics: dict, paper: dict, out) -> None:
    """Grid ours-vs-paper for Table 2's 6 committed rows x 11 columns."""
    rows = [
        ("Panel A: mean (%/mo)", "mean_"),
        ("Panel A: CAPM beta", "beta_capm_"),
        ("Panel A: CAPM alpha (%/mo)", "alpha_capm_"),
        ("Panel B: monthly Sharpe", "sharpe_"),
        ("Panel C: VW mean (%/mo)", "vw_mean_"),
        ("Panel D: no-delisting mean (%/mo)", "nodl_mean_"),
    ]
    lines = ["# Table 2 — Weber (2018) replication (ours vs paper)",
             "",
             "| Row | " + " | ".join(BIN_COLS) + " |",
             "|---|" + "|".join(["---"] * len(BIN_COLS)) + "|"]
    for label, prefix in rows:
        row_cells = []
        for c in BIN_COLS:
            key = f"{prefix}{c}"
            ours = metrics.get(key)
            pv = paper.get(key)
            ours_s = f"{ours:.3f}" if ours is not None else "—"
            pv_s = f"{pv:.3f}" if pv is not None else "—"
            row_cells.append(f"{ours_s} vs {pv_s}")
        lines.append(f"| {label} | " + " | ".join(row_cells) + " |")
    lines.append("")
    lines.append("Format: `ours vs paper` per cell.")
    out.write_text("\n".join(lines) + "\n")


def write_table3_md(metrics: dict, paper: dict, out) -> None:
    rows = [
        ("FF3 alpha (%/mo)", "ff3_alpha_"),
        ("FF4 alpha (%/mo)", "ff4_alpha_"),
        ("FF5 alpha (%/mo)", "ff5_alpha_"),
    ]
    lines = ["# Table 3 — Weber (2018) replication (ours vs paper)",
             "",
             "| Row | " + " | ".join(BIN_COLS) + " |",
             "|---|" + "|".join(["---"] * len(BIN_COLS)) + "|"]
    for label, prefix in rows:
        row_cells = []
        for c in BIN_COLS:
            key = f"{prefix}{c}"
            ours = metrics.get(key)
            pv = paper.get(key)
            ours_s = f"{ours:.3f}" if ours is not None else "—"
            pv_s = f"{pv:.3f}" if pv is not None else "—"
            row_cells.append(f"{ours_s} vs {pv_s}")
        lines.append(f"| {label} | " + " | ".join(row_cells) + " |")
    lines.append("")
    lines.append("Format: `ours vs paper` per cell.")
    out.write_text("\n".join(lines) + "\n")


def write_plots(ew_ex: pd.DataFrame, spread: pd.Series, paper_means: dict) -> None:
    """Decile-spread bar chart + cumulative D1-D10 long-short return."""
    # 1. Bar chart: EW (delisting-adj) mean excess returns vs paper Panel A means.
    ours_means = ew_ex.mean() * 100.0
    paper_vals = [paper_means.get(f"mean_D{i}", np.nan) for i in range(1, 11)]
    cols = [f"D{i}" for i in range(1, 11)]
    x = np.arange(1, 11)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - 0.2, [ours_means[c] for c in cols], width=0.4, label="ours (EW, dl-adj)")
    ax.bar(x + 0.2, paper_vals, width=0.4, label="paper Panel A")
    ax.set_xticks(x)
    ax.set_xticklabels(cols)
    ax.set_ylabel("Mean excess return (%/month)")
    ax.set_xlabel("Duration decile (D1 = low duration)")
    ax.set_title("Decile mean excess returns: ours vs paper")
    ax.legend()
    fig.tight_layout()
    fig.savefig(LAYOUT.result_path("decile_spread.png"), dpi=120)
    plt.close(fig)

    # 2. Cumulative D1-D10 long-short return over 1963-2014.
    cum = (1.0 + spread).cumprod()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(cum.index, cum.values)
    ax.set_ylabel("Cumulative return (D1 - D10)")
    ax.set_xlabel("Date")
    ax.set_title("Cumulative return of D1-D10 long-short spread (1963-2014)")
    fig.tight_layout()
    fig.savefig(LAYOUT.result_path("cumulative_d1d10.png"), dpi=120)
    plt.close(fig)


def load_paper_targets() -> dict:
    """Flat {metric_name: paper_value} across T2 and T3."""
    doc = json.loads(LAYOUT.preparations_path("tables_to_replicate.json").read_text())
    paper = {}
    for tbl in doc.get("tables", []):
        if tbl.get("id") not in ("T2", "T3"):
            continue
        for m in tbl.get("metrics", []):
            paper[m["name"]] = m["value"]
    return paper


def load_paper_targets_t4t5() -> dict:
    """Flat {metric_name: paper_value} across T4 and T5."""
    doc = json.loads(LAYOUT.preparations_path("tables_to_replicate.json").read_text())
    paper = {}
    for tbl in doc.get("tables", []):
        if tbl.get("id") not in ("T4", "T5"):
            continue
        for m in tbl.get("metrics", []):
            paper[m["name"]] = m["value"]
    return paper


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> None:
    print("=== Weber (2018) iteration 2: core pipeline + Tables 2/3 ===", flush=True)
    funnel = funnel_counts()
    print("\nFunnel counts (per stage, per decade, PRICE_FILTER=%s):" % PRICE_FILTER)
    print(funnel.to_string(index=False), flush=True)

    panel, fundamentals_duration = build_panel()

    print("\nSaving parquets ...", flush=True)
    panel.to_parquet(LAYOUT.data_path("panel.parquet"), index=False)
    fundamentals_duration.to_parquet(LAYOUT.data_path("fundamentals_duration.parquet"),
                                     index=False)

    print("\nPanel summary:", flush=True)
    print(f"  rows x cols: {panel.shape}", flush=True)
    print(f"  months: {panel['month'].nunique()}  sort_years: {panel['sort_year'].nunique()}  "
          f"permnos: {panel['permno'].nunique()}", flush=True)

    # ---- iteration 2: portfolio returns + tables ----
    print("\nLoading FF factors ...", flush=True)
    factors = load_factors()
    print(f"  ff rows: {len(factors)}  (dt {factors['dt'].min()} .. {factors['dt'].max()})",
          flush=True)

    print("Computing Table 2 ...", flush=True)
    t2, ew_ex, spread, _ = compute_table2(panel, factors)
    print(f"  VW stocks with missing me_jun (falling back to EW): {t2.pop('_vw_n_missing_me')}",
          flush=True)

    print("Computing Table 3 ...", flush=True)
    t3 = compute_table3(ew_ex, spread, factors)

    paper = load_paper_targets()

    write_table2_md(t2, paper, LAYOUT.result_path("table_2.md"))
    write_table3_md(t3, paper, LAYOUT.result_path("table_3.md"))
    write_plots(ew_ex, spread, paper)

    # ---- Tables 4 & 5 (robustness, claim C6) ----
    import table4_5
    from table4_5 import (
        compute_table4, compute_table5, build_metrics as build_t45_metrics,
        write_table4_md, write_table5_md,
    )

    print("\nComputing Table 4 (12 parameter variations) ...", flush=True)
    funds = acquire_fundamentals_duration()
    t4 = compute_table4(funds, panel, factors)
    print("Computing Table 5 (5 subsamples) ...", flush=True)
    t5 = compute_table5(panel, factors)
    paper_t45 = load_paper_targets_t4t5()
    write_table4_md(t4, paper_t45)
    write_table5_md(t5, paper_t45)
    t45_metrics = build_t45_metrics(t4, t5)

    # ---- Table 6 (volatility-managed portfolios, claim C6) ----
    import table6
    print("\nComputing Table 6 (volatility-managed portfolios) ...", flush=True)
    t6 = table6.compute_table6(panel, factors)
    table6._md_grid(t6, table6.load_paper_targets())

    # ---- Table 1 (summary statistics + correlations) ----
    import table1
    print("\nComputing Table 1 (summary statistics + correlations) ...", flush=True)
    t1_variants, t1_best_key, t1 = table1.compute_table1_variants(panel)
    t1_paper = table1.load_paper_targets()
    table1.write_table1_variants_md(t1_variants, t1_best_key, t1_paper, t1)
    print(f"  [T1] IOR cusip->permno match rate: {t1.get('_ior_match_rate'):.4f}",
          flush=True)

    # ---- Tables 10/11/12 (RIOR double sorts; claim C5) ----
    # bp variant follows the Table 1 choice (Part A2 canonical variant).
    import table10_12
    bp_variant = t1_best_key[0]  # "nyse" or "allstock"
    print(f"\nComputing Tables 10/11/12 (RIOR double sorts, bp={bp_variant}) ...",
          flush=True)
    t10_12 = table10_12.main(bp_variant)

    # ---- Tables 8 & 9 (analyst expectations; claim C4) ----
    import table8_9
    print("\nComputing Tables 8 & 9 (analyst expectations / price targets) ...",
          flush=True)
    t8_9, _d8, _d9 = table8_9.main()

    # ---- aggregate metrics into the flat dict the scorer reads ----
    metrics = dict(t2)
    metrics.update(t3)
    metrics.update(t45_metrics)
    metrics.update(t6)
    metrics.update(t1)
    metrics.update(t10_12)
    metrics.update(t8_9)
    # Fold in the pipeline diagnostics already present (non-target keys are ignored).
    # write_metrics writes the flat {name: {value}} format.

    out = {"schema_version": 2, "slug": SLUG, "metrics": {}}
    for k, v in metrics.items():
        if isinstance(v, dict):
            out["metrics"][k] = v
        else:
            out["metrics"][k] = {"value": float(v)}
    LAYOUT.eval_path("metrics.json").write_text(json.dumps(out, indent=2, default=str))

    print("\nWrote eval/metrics.json (%d target metric cells)" % len(metrics), flush=True)

    def _v(k):
        """Extract the numeric value from a metric that may be either a bare
        scalar (T2-T9) or a {"value": ..., "unit": ...} dict (T10-T12)."""
        v = metrics.get(k)
        if isinstance(v, dict):
            v = v.get("value")
        return float(v) if v is not None and pd.notna(v) else float("nan")

    print("\nKey results:")
    print(f"  EW spread (dl-adj): {_v('mean_D1D10'):.3f} %/mo")
    print(f"  VW spread:          {_v('vw_mean_D1D10'):.3f} %/mo")
    print(f"  no-delist spread:   {_v('nodl_mean_D1D10'):.3f} %/mo")
    print(f"  Sharpe spread:      {_v('sharpe_D1D10'):.3f}")
    print(f"  CAPM beta spread:   {_v('beta_capm_D1D10'):.3f}")
    print(f"  FF3 alpha spread:   {_v('ff3_alpha_D1D10'):.3f} %/mo")
    print(f"  FF5 alpha spread:   {_v('ff5_alpha_D1D10'):.3f} %/mo")
    if "vm_mean_D1D10" in metrics:
        print(f"  vm mean spread:     {_v('vm_mean_D1D10'):.3f} %/mo")
        print(f"  vm CAPM alpha spread: {_v('vm_alpha_capm_D1D10'):.3f} %/mo")
        print(f"  vm FF3 alpha spread:  {_v('vm_alpha_ff3_D1D10'):.3f} %/mo")
        print(f"  vm FF5 alpha spread:  {_v('vm_alpha_ff5_D1D10'):.3f} %/mo")
    if "mean_dur" in metrics:
        print(f"  T1 mean Dur: {_v('mean_dur'):.3f}  mean IOR: {_v('mean_ior'):.3f}"
              f"  mean ME: {_v('mean_me'):.1f}  mean Age: {_v('mean_age'):.3f}")
    if "t10_lowrior_D1D5" in metrics:
        print(f"  T10 low-RIOR D1-D5 spread:      {_v('t10_lowrior_D1D5'):.3f} %/mo")
        print(f"  T10 high-RIOR D1-D5 spread:     {_v('t10_highrior_D1D5'):.3f} %/mo")
        print(f"  T10 RIOR1-RIOR5 high-dur spread:{_v('t10_r1r5_D5'):.3f} %/mo")
    print("=== done ===", flush=True)


if __name__ == "__main__":
    main()
