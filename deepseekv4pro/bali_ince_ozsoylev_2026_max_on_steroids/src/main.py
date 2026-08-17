"""
Replication of Bali, Ince & Ozsoylev (2026) "MAX on Steroids: A New
Measure of Investor Attraction to Lottery-Like Payoffs".

Signal: MAX (average of top-5 daily returns) and MAX^beta.
Targets: factor/portfolio/regression tables.

This file currently implements ONLY the factor dataset build
(data/factors.parquet). Later table sections (portfolio sorts, alphas,
Fama-MacBeth) will be added in subsequent tasks.
"""

# --- imports ---
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from clickhouse_driver import Client
from utils.env import get_clickhouse_config
from utils.paths import paper_layout
from utils.portfolio import rolling_cumret, bin_returns
from utils.quantile import assign_quantiles

SLUG = "max_on_steroids_attempt5_deepseek"
LAYOUT = paper_layout(SLUG)

# --- configuration (read from preprocessing_rules.json) ---
_RULES = json.loads(LAYOUT.preparations_path("preprocessing_rules.json").read_text())
# Derive sample range from the paper-derived rules (Jan 1968 -> Dec 2022).
START = pd.Period("1968-01", freq="M")
END = pd.Period("2022-12", freq="M")

# --- ClickHouse connection ---
_CFG = get_clickhouse_config()
SQL_DIR = LAYOUT.src_path("sql")


def _client() -> Client:
    return Client(
        host=_CFG["host"],
        port=int(_CFG["port"]),
        user=_CFG["user"],
        password=_CFG["password"],
        settings={"max_execution_time": 600},
    )


def q(sql: str) -> pd.DataFrame:
    """Execute a SQL query and return a DataFrame."""
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


def q_file(name: str) -> pd.DataFrame:
    """Execute a saved SQL file and return a DataFrame."""
    return q((SQL_DIR / name).read_text())


# =========================================================================
# SECTION 1 — Factor dataset (data/factors.parquet)
# =========================================================================
def _parse_ps_liquidity(path: Path) -> pd.DataFrame:
    """Parse Pastor-Stambaugh liquidity factor file.

    Header line: "Month\\tAgg Liq.\\tInnov Liq (eq8)\\tTraded Liq (LIQ_V)".
    Month is YYYYMM integer; the 4th column (LIQ_V) is the traded
    10-1 portfolio return used by the FF6PS model. -99 = missing.
    """
    lines = path.read_text().splitlines()
    # skip comment lines (start with %) and the header row
    rows = [
        ln.split()
        for ln in lines
        if ln.strip() and not ln.startswith("%") and not ln.startswith("Month")
    ]
    df = pd.DataFrame(
        [
            (int(r[0]), float(r[3]))
            for r in rows
            if len(r) >= 4
        ],
        columns=["yyyymm", "ps_liq"],
    )
    # drop the -99 missing sentinel
    df = df[df["ps_liq"] != -99.0]
    df["month"] = pd.PeriodIndex(
        df["yyyymm"].astype(str).str[:4] + "-" + df["yyyymm"].astype(str).str[4:],
        freq="M",
    )
    return df[["month", "ps_liq"]]


def _parse_sy4(path: Path) -> pd.DataFrame:
    """Parse Stambaugh-Yuan mispricing factors (M4.csv).

    Columns: YYYYMM, MKTRF, SMB, MGMT, PERF, RF. File ends 2016-12.
    """
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns={"yyyymm": "_ym"})
    df["month"] = pd.PeriodIndex(
        df["_ym"].astype(str).str[:4] + "-" + df["_ym"].astype(str).str[4:],
        freq="M",
    )
    df = df.rename(
        columns={
            "mktrf": "sy_mktrf",
            "smb": "sy_smb",
            "mgmt": "sy_mgmt",
            "perf": "sy_perf",
            "rf": "sy_rf",
        }
    )
    return df[["month", "sy_mktrf", "sy_smb", "sy_mgmt", "sy_perf", "sy_rf"]]


def build_factors() -> pd.DataFrame:
    """Assemble the single monthly factor panel, 1968-01 .. 2022-12."""
    # 1. FF factors from ClickHouse
    ff = q_file("factors.sql")
    ff["dt"] = pd.to_datetime(ff["dt"])
    ff["month"] = ff["dt"].dt.to_period("M")
    ff = ff.drop(columns=["dt"])

    # 2. Pastor-Stambaugh liquidity
    ps = _parse_ps_liquidity(LAYOUT.input_path("liq_data_1962_2024.txt"))

    # 3. Stambaugh-Yuan mispricing
    sy = _parse_sy4(LAYOUT.input_path("M4.csv"))

    # merge everything on month
    df = ff.merge(ps, on="month", how="left").merge(sy, on="month", how="left")

    # restrict to the sample window
    df = df[(df["month"] >= START) & (df["month"] <= END)]

    # index by month (YYYY-MM-01 period)
    df = df.set_index("month").sort_index()
    df.index.name = "month"

    # canonical column order
    cols = [
        "mkt_rf", "smb", "hml", "mom", "rmw", "cma", "rf",
        "ps_liq", "sy_mktrf", "sy_smb", "sy_mgmt", "sy_perf", "sy_rf",
    ]
    df = df[[c for c in cols if c in df.columns]]
    return df


# =========================================================================
# SECTION 2 — Monthly stock-month analysis panel (data/panel.parquet)
# =========================================================================
# Build the panel with all CRSP-derived signal variables (MAX, BETA, IVOL,
# ILLIQ, REV, MOM, SIZE, turnover, CE inputs) per the paper's universe and
# variable definitions. This is the foundation for every committed table.
# =========================================================================


def _load_daily_universe() -> pd.DataFrame:
    """PIT-filtered daily data (universe filters applied in SQL via dsfhdr).

    Caches to data/daily_universe.parquet (Assumption 16) and short-circuits
    on the cache to avoid re-pulling the 53M-row daily relation every run.
    """
    cache = LAYOUT.data_path("daily_universe.parquet")
    if cache.exists():
        df = pd.read_parquet(cache)
        df["date"] = pd.to_datetime(df["date"])
        return df
    df = q_file("daily_universe.sql")
    df["date"] = pd.to_datetime(df["date"])
    # dsfhdr columns come back as floats; coerce to int where meaningful
    for c in ("hshrcd", "hexcd", "hsiccd"):
        if c in df.columns:
            df[c] = df[c].astype("Int64")
    df.to_parquet(cache, index=False)
    print(f"  cached {cache} ({len(df)} rows)")
    return df


def _load_daily_signals() -> pd.DataFrame:
    """Monthly aggregation of daily signals (MAX, ILLIQ numerator, turnover,
    obs count, month-end price) — done in ClickHouse SQL."""
    df = q_file("daily_signals.sql")
    df["month"] = pd.to_datetime(df["month"]).dt.to_period("M")
    # max computed as mean of top-5; requiring >=15 obs is applied downstream
    return df


def _rolling_beta_ivol(
    daily: pd.DataFrame,
    mkt_daily: pd.DataFrame,
    rf_daily: pd.Series,
) -> pd.DataFrame:
    """252-trading-day rolling beta/IVOL per stock, vectorized per permno.

    Regression: daily excess return (ret - rf) on market excess return
    (vwretd - rf). Slope = BETA; std of residuals = IVOL. Requires >=200
    non-missing obs in the window (Assumption 17).

    Vectorized across all permnos using pandas' C-implemented groupby-rolling
    sums (no Python loop over stocks). Returns a DataFrame with columns
    permno, month (end-of-month), beta, ivol.
    """
    d = daily[["permno", "date", "ret"]].copy()
    d = d.merge(mkt_daily, on="date", how="left")
    d["rf"] = rf_daily.reindex(d["date"]).values
    d = d.dropna(subset=["ret", "vwretd", "rf"])
    d["y"] = d["ret"] - d["rf"]
    d["x"] = d["vwretd"] - d["rf"]
    d = d.sort_values(["permno", "date"])

    window = 252
    min_obs = 200

    # Fully vectorized rolling OLS via groupby + rolling (C-implemented).
    d["_xy"] = d["x"] * d["y"]
    d["_x2"] = d["x"] * d["x"]
    d["_y2"] = d["y"] * d["y"]
    d["_x"] = d["x"]
    d["_y"] = d["y"]
    d["_one"] = 1.0

    grp = d.groupby("permno", sort=False)
    sx = grp["_x"].rolling(window, min_periods=min_obs).sum().droplevel(0)
    sy = grp["_y"].rolling(window, min_periods=min_obs).sum().droplevel(0)
    n = grp["_one"].rolling(window, min_periods=min_obs).sum().droplevel(0)
    sxy = grp["_xy"].rolling(window, min_periods=min_obs).sum().droplevel(0)
    sxx = grp["_x2"].rolling(window, min_periods=min_obs).sum().droplevel(0)
    syy = grp["_y2"].rolling(window, min_periods=min_obs).sum().droplevel(0)

    denom = n * sxx - sx * sx
    beta = (n * sxy - sx * sy) / denom
    ssr = (syy - sy * sy / n) - (sxy - sx * sy / n) ** 2 / denom
    ssr = np.where(ssr >= 0, ssr, 0.0)
    ivol = np.sqrt(ssr / n)

    out = pd.DataFrame({
        "permno": d["permno"].values,
        "month": d["date"].dt.to_period("M").values,
        "beta": beta.values,
        "ivol": ivol.values,
    })
    out = out.sort_values(["permno", "month"]).dropna(subset=["beta"])
    # keep last (month-end) value per (permno, month)
    out = out.groupby(["permno", "month"], as_index=False).last()
    return out[["permno", "month", "beta", "ivol"]]


def build_panel() -> pd.DataFrame:
    """Assemble the monthly stock-month panel with all CRSP-derived signals.

    Rows: one per (permno, month) for 1968-01 .. 2022-12.
    """
    print("Loading daily universe ...")
    daily = _load_daily_universe()

    print("Loading daily signals (MAX, ILLIQ, turnover) ...")
    daily_sig = _load_daily_signals()

    print("Loading monthly universe ...")
    monthly = q_file("monthly_universe.sql")
    monthly["date"] = pd.to_datetime(monthly["date"])
    monthly["month"] = monthly["date"].dt.to_period("M")

    print("Loading delisting events ...")
    delist = q_file("delisting.sql")
    delist["dlstdt"] = pd.to_datetime(delist["dlstdt"])
    delist["month"] = delist["dlstdt"].dt.to_period("M")

    print("Loading risk-free + market ...")
    rf_all = q_file("risk_free.sql")
    rf_monthly = rf_all[rf_all["dt_kind"] == "monthly"].copy()
    rf_monthly["month"] = pd.to_datetime(rf_monthly["dt"]).dt.to_period("M")
    rf_monthly = rf_monthly[["month", "rf"]].drop_duplicates("month")
    rf_daily_full = rf_all[rf_all["dt_kind"] == "daily"].copy()
    rf_daily_full["date"] = pd.to_datetime(rf_daily_full["dt"])
    rf_daily = rf_daily_full.set_index("date")["rf"].sort_index()

    mkt_daily = q_file("market_daily.sql")
    mkt_daily["date"] = pd.to_datetime(mkt_daily["date"])

    # --- Delisting-adjusted monthly return ---
    # For each permno's LAST month in the panel, if it matches a delisting
    # month with a valid dlret, substitute; else -0.30 for performance
    # delistings (dlstcd in 500-599). Standard convention (paper silent).
    delist = delist[delist["dlret"] > -0.40]  # drop missing-return sentinels
    monthly = monthly.sort_values(["permno", "date"])
    # identify last observation per permno
    monthly["_last"] = monthly.groupby("permno")["date"].transform("max")

    # Map delisting info onto the last month of each permno
    dl = delist.groupby(["permno", "month"], as_index=False).agg(
        dlret=("dlret", "last"), dlstcd=("dlstcd", "max"),
    )
    monthly = monthly.merge(dl, on=["permno", "month"], how="left")
    # Performance delisting fallback: dlstcd >= 500
    perf = monthly["dlstcd"] >= 500
    monthly["ret_adj"] = monthly["ret"]
    # apply dlret where the stock's last month coincides with a delisting and dlret exists
    has_dl = monthly["dlret"].notna()
    monthly.loc[has_dl, "ret_adj"] = monthly.loc[has_dl, "dlret"]
    # fallback -0.30 for performance delistings with missing dlret
    fallback = perf & monthly["dlret"].isna()
    monthly.loc[fallback, "ret_adj"] = -0.30
    monthly = monthly.drop(columns=["dlret", "dlstcd"])
    monthly = monthly.sort_values(["permno", "month"]).reset_index(drop=True)

    # --- MOM (12-2 cumulative return, skip 1) ---
    mom_ser = rolling_cumret(
        monthly, date_col="month", ret_col="ret_adj", window=11, skip=1,
    )
    monthly["mom"] = mom_ser.values

    # --- me growth / cumret12 (CE inputs) ---
    # me_gr12 = me_t / me_{t-12} - 1  (12-month market-cap growth)
    # cumret12 = cumulative return over months t-11 .. t (12 months, includes t)
    monthly = monthly.sort_values(["permno", "month"]).reset_index(drop=True)
    g = monthly.groupby("permno")
    monthly["me_lag12"] = g["me"].shift(12)
    monthly["me_gr12"] = monthly["me"] / monthly["me_lag12"] - 1
    monthly["logret"] = np.log1p(monthly["ret_adj"])
    monthly["_cumlog12"] = g["logret"].rolling(12, min_periods=12).sum().reset_index(level=0, drop=True)
    monthly["cumret12"] = np.expm1(monthly["_cumlog12"])
    monthly = monthly.drop(columns=["logret", "_cumlog12"])

    # --- final assembly ---
    # Start from the monthly panel (PIT + price + SIC already applied in SQL).
    # Merge daily_sig (MAX/ILLIQ/turnover/nobs), then apply >=15 obs rule.
    panel = monthly.merge(
        daily_sig[["permno", "month", "max", "illiq_num", "nvol_obs",
                   "turnover", "nobs", "prc_end"]],
        on=["permno", "month"], how="left",
    )

    # ILLIQ = mean over positive-volume days of |ret|/dollarvol, scaled by 1e6
    # (paper: "scaled by 10^6"). illiq_num already sums |ret|/dollarvol over
    # positive-volume days; divide by the count of such days (nvol_obs).
    panel["illiq"] = (panel["illiq_num"] / panel["nvol_obs"]) * 1e6

    # >=15 daily obs rule: null out the daily-derived signals (MAX, ILLIQ,
    # turnover) where fewer than 15 non-missing daily returns are available
    # in month t (paper L169). The row (monthly ret/me/beta from the 252-day
    # window) is retained.
    low_obs = panel["nobs"] < 15
    panel.loc[low_obs, ["max", "illiq", "turnover"]] = np.nan

    # BETA / IVOL (month is Period on both sides)
    beta_ivol = _rolling_beta_ivol(daily, mkt_daily, rf_daily)
    panel = panel.merge(beta_ivol, on=["permno", "month"], how="left")
    panel = panel.drop(columns=["_last"], errors="ignore")

    # Excess monthly return (REV) + rf merge
    panel = panel.merge(rf_monthly, on="month", how="left")
    panel["ret_excess"] = panel["ret_adj"] - panel["rf"]

    # Restrict to sample window and apply >=15-obs rule for daily-derived signals
    panel = panel[(panel["month"] >= START) & (panel["month"] <= END)]
    panel = panel.reset_index(drop=True)

    # month-end date column; me_lag1 for VW weights
    panel["date"] = pd.to_datetime(panel["date"])
    panel["me_lag1"] = panel.groupby("permno")["me"].shift(1)

    # Replace the raw monthly return with the delisting-adjusted return.
    panel = panel.drop(columns=["ret"]).rename(columns={"ret_adj": "ret"})
    panel["rev"] = panel["ret_excess"]

    # --- ret_fwd (one-month-ahead UNFILTERED excess return) ---
    # month-aligned merge from the unfiltered monthly-all series; ret_excess
    # (month-t) is preserved for REV and contemporaneous diagnostics.
    panel = _merge_ret_fwd(panel)

    final_cols = [
        "month", "permno", "date", "ret", "ret_excess", "ret_fwd", "rf",
        "max", "beta", "ivol", "illiq", "rev", "mom",
        "me", "me_lag1", "turnover", "me_gr12", "cumret12",
        "nobs",
    ]
    panel = panel[[c for c in final_cols if c in panel.columns]]
    return panel


# =========================================================================
# SECTION 2b — Unfiltered monthly-all series (data/monthly_all.parquet)
# =========================================================================
# The one-month-ahead (t+1) return for every forward-looking table (T1-T9,
# via the panel's `ret_fwd` column) must come from the UNFILTERED CRSP
# monthly file, not the formation-filtered panel. The paper's price/universe
# filters apply only at formation month t; at t+1 a crash below $5 or an
# exchange-drop still realizes its (delisting-adjusted) return. Pulling from
# the filtered panel would (a) drop those t+1 rows and (b) let a groupby-shift
# silently grab the t+2 recovery return. This parquet is therefore a
# genuinely-separate, different-universe artifact (all CRSP stocks, 1968-01
# .. 2023-01 — one extra month for the last formation month's t+1), consumed
# by the ret_fwd column of every forward-looking metric. It cannot fold into
# the filtered panel CTE because it is a disjoint universe at a different
# (unfiltered) filter level.
# =========================================================================


def build_monthly_all() -> pd.DataFrame:
    """Unfiltered monthly-all returns, delisting-adjusted, merged with rf.

    Keyed (permno, month). ret_excess = ret - rf. Month is a Period[M].
    Window extends one month past END (to 2023-01) so the last formation
    month 2022-12 has a valid t+1 return.
    """
    raw = q_file("monthly_all.sql")
    raw["date"] = pd.to_datetime(raw["date"])
    raw["month"] = raw["date"].dt.to_period("M")

    # monthly rf, pulled directly from the FF monthly table (not the
    # already-truncated factors.parquet) so the extra 2023-01 month — needed
    # for the last formation month 2022-12's t+1 excess return — has an rf.
    rf = q(
        "SELECT dt AS dt, rf AS rf FROM ff.four_factor_monthly "
        "WHERE dt >= '1968-01-01' AND dt <= '2023-01-31' "
        "SETTINGS max_execution_time = 300, max_rows_to_read = 10000000, "
        "timeout_before_checking_execution_speed = 0"
    )
    rf["month"] = pd.PeriodIndex(pd.to_datetime(rf["dt"]), freq="M")
    rf = rf[["month", "rf"]].drop_duplicates("month")

    df = raw.merge(rf, on="month", how="left")
    df["ret_excess"] = df["ret"] - df["rf"]
    df = df[["permno", "month", "ret", "ret_excess"]]
    # Drop any month where rf is missing (outside the factor window).
    df = df.dropna(subset=["ret_excess"])
    df = df.drop_duplicates(subset=["permno", "month"], keep="last")
    df = df.sort_values(["permno", "month"]).reset_index(drop=True)
    return df


# =========================================================================
# SECTION 3 — Compustat-derived variables + mispricing (data/panel.parquet)
# =========================================================================
# Extends the Section-2 panel (1,743,269 rows x 18 cols, keyed (permno, month))
# with the Compustat-derived fundamentals and the 11-anomaly mispricing
# machinery. See src/sql/compustat_annual.sql, compustat_quarterly.sql,
# issuance_shares.sql, market_totval.sql. All merges are LEFT, preserving every
# existing row/column.
# =========================================================================

# Quarterly lag (months): most recent fundq quarter-end with datadate >= this
# many months before month t (ROE, ROA, CHS distress inputs). Paper says
# "6-mo-ish"/">=4 months" — 4 months used (documented ambiguity).
QTR_LAG_MONTHS = 4
# Annual lag (months): most recent funda FYE with datadate >= this many months
# before month t (BE/BM, accruals, NOA, AG, INV/AT, GP, O-score). Assumption 19.
ANN_LAG_MONTHS = 6
# CHS (2008) exponential-weight decay for NIMTAAVG over last 4 quarters.
CHS_RHO = 2.0 / 3.0
# CHS PRICE floor (log price floored at log(15)).
CHS_PRICE_FLOOR = 15.0


CHS_BETA = [-9.164, -20.264, 1.416, -7.129, 1.411, -0.045, -2.132, 0.075, -0.058]


def _merge_asof_lag(panel, facts, fact_date_col, lag_months, required_cols=()):
    """merge_asof fiscal facts onto a monthly panel with a fixed lag.

    `facts` has `permno`, a date column, and value columns. For each panel row
    at month t, match the most recent fact with date <= t - lag_months. Returns
    a DataFrame (aligned to `panel`, same length) of just the required value cols.

    pandas 2.x `merge_asof(..., by=)` requires the on-key globally sorted (not
    per-group), so it errors on panels with multiple permnos interleaving. We do
    the asof per permno via groupby-apply, which restores the within-group
    semantics.
    """
    keep = [c for c in facts.columns if c == "permno" or c == fact_date_col
            or c in required_cols]
    facts = facts[keep].copy()
    facts[fact_date_col] = pd.to_datetime(facts[fact_date_col])
    facts = facts.sort_values(["permno", fact_date_col]).drop_duplicates(
        subset=["permno", fact_date_col], keep="last")

    left = panel[["month", "permno"]].copy()
    left["_ref"] = (left["month"].dt.to_timestamp(freq="M")
                    - pd.DateOffset(months=lag_months))

    # Vectorized asof: for each permno, facts dates are ordered; use searchsorted
    # to find the last fact date <= ref. Build per-permno numpy date arrays and
    # value arrays once, then grab by index.
    fact_dates = facts[fact_date_col].values.astype("datetime64[ns]")
    fact_perm  = facts["permno"].values
    order = np.lexsort((fact_dates, fact_perm))
    fact_dates = fact_dates[order]
    fact_perm  = fact_perm[order]
    value_cols = [c for c in required_cols]
    fact_vals  = {c: facts[c].values[order].astype(np.float64)
                  for c in required_cols}

    # unique permnos (sorted) and their date-array boundaries
    uniq, first_idx, counts = np.unique(fact_perm, return_index=True,
                                        return_counts=True)

    ref_ns = left["_ref"].values.astype("datetime64[ns]").astype("int64")
    perm_left = left["permno"].values

    # Map each left permno to its block start
    perm_to_pos = {p: i for i, p in enumerate(uniq)}
    left_pos = np.array([perm_to_pos.get(p, -1) for p in perm_left])

    out_idx = np.full(len(left), -1, dtype=np.int64)
    # Loop over permnos (<= ~20k) — vectorized searchsorted within each block.
    for bi, p in enumerate(uniq):
        s, e = first_idx[bi], first_idx[bi] + counts[bi]
        rows = np.where(left_pos == bi)[0]
        if rows.size == 0:
            continue
        block_dates = fact_dates[s:e]
        r = ref_ns[rows]
        pos = np.searchsorted(block_dates, r, side="right") - 1
        pos[pos < 0] = -1
        # valid positions get the global index s + pos; -1 stays -1
        out_idx[rows] = np.where(pos >= 0, s + pos, -1)

    result = {}
    for c in required_cols:
        col = np.full(len(left), np.nan, dtype=np.float64)
        fill = out_idx >= 0
        col[fill] = fact_vals[c][out_idx[fill]]
        result[c] = col
    out = pd.DataFrame(result)
    return out


def _monthly_rank(s: pd.Series, month: pd.Series):
    """Cross-sectional percentile rank (0-100) per month. Higher value -> higher
    rank; orientation reversal is the caller's job."""
    df = pd.DataFrame({"month": month, "v": s})
    r = df.groupby("month")["v"].rank(pct=True, method="average",
                                      na_option="keep") * 100.0
    return r


def _rank_asc(df, col):
    """ascending rank (higher value -> higher rank)."""
    return _monthly_rank(df[col], df["month"])


def _rank_desc(df, col):
    """descending rank (higher value -> lower rank): 100 - ascending rank."""
    return 100.0 - _monthly_rank(df[col], df["month"])


def _load_monthly_all() -> pd.DataFrame:
    """Load (or build + cache) the unfiltered monthly-all excess-return series.

    Caches to data/monthly_all.parquet (Section 2b). Short-circuits on cache.
    """
    cache = LAYOUT.data_path("monthly_all.parquet")
    if cache.exists():
        df = pd.read_parquet(cache)
        df["month"] = pd.PeriodIndex(df["month"], freq="M")
        return df
    df = build_monthly_all()
    df.to_parquet(cache, index=False)
    print(f"  cached {cache} ({len(df)} rows)")
    return df


def _merge_ret_fwd(panel: pd.DataFrame) -> pd.DataFrame:
    """Add ret_fwd: month-ALIGNED one-month-ahead excess return from the
    unfiltered monthly-all series (no gap skipping). ret_fwd at (permno, t)
    = monthly_all.ret_excess at (permno, t+1). Implemented by shifting the
    monthly-all month back by 1 (month <- month - 1) then inner/left merge on
    (permno, month); a formation row without a t+1 return stays NaN (never
    pulls the t+2 recovery return). Verified no duplicate (permno, month)."""
    all_ = _load_monthly_all()
    shifted = all_[["permno", "month", "ret_excess"]].copy()
    shifted["month"] = shifted["month"] - 1  # month t now holds t+1's return
    shifted = shifted.rename(columns={"ret_excess": "ret_fwd"})
    assert shifted.duplicated(subset=["permno", "month"]).sum() == 0, (
        "ret_fwd merge key (permno, month) not unique")
    panel = panel.merge(shifted, on=["permno", "month"], how="left")
    assert panel.duplicated(subset=["permno", "month"]).sum() == 0, (
        "panel has duplicate (permno, month) after ret_fwd merge")
    return panel


def build_section3(panel: pd.DataFrame) -> pd.DataFrame:
    """Merge Compustat-derived fundamentals + mispricing ranks onto the panel.

    Returns `panel` with the new columns added (existing rows/cols preserved).
    """
    panel = panel.copy()

    # ---- load source facts ----
    print("Loading annual Compustat (funda + CCM) ...")
    funda = q_file("compustat_annual.sql")
    print("Loading quarterly Compustat (fundq + CCM) ...")
    fundq = q_file("compustat_quarterly.sql")
    print("Loading issuance shares (NSI / CSI-5) ...")
    shares = q_file("issuance_shares.sql")
    print("Loading market aggregates (vwretd_m, totval) ...")
    mkt = q_file("market_totval.sql")

    for df in (funda, fundq, shares):
        df["permno"] = df["permno"].astype("int64")

    funda["datadate"] = pd.to_datetime(funda["datadate"])
    fundq["datadate"] = pd.to_datetime(fundq["datadate"])
    shares["month"] = pd.to_datetime(shares["month"]).dt.to_period("M")
    mkt["month"] = pd.to_datetime(mkt["month"]).dt.to_period("M")

    # =========================================================================
    # Annual signals (6-month lag). Build the per-permno annual time series,
    # compute year-over-year lags, then merge_asof once onto the panel.
    # =========================================================================
    funda = funda.sort_values(["permno", "datadate"]).reset_index(drop=True)
    g = funda.groupby("permno", sort=False)
    funda["at_lag1"] = g["at"].shift(1)
    funda["ppent_lag1"] = g["ppent"].shift(1)
    funda["invt_lag1"] = g["invt"].shift(1)
    funda["ni_lag1"] = g["ni"].shift(1)
    funda["act_che"] = funda["act"] - funda["che"]
    funda["lct_dlc"] = funda["lct"] - funda["dlc"]
    funda["d_wc"] = funda["act_che"] - g["act_che"].shift(1)
    funda["d_ncl"] = funda["lct_dlc"] - g["lct_dlc"].shift(1)
    funda["avg_at"] = (funda["at"] + funda["at_lag1"]) / 2.0
    funda["acc"] = (funda["d_wc"] - funda["d_ncl"] - funda["dp"]) / funda["avg_at"]
    # NOA: (DLC + DLTT - CHE) / lagged AT (operating assets = AT-CHE; operating
    #   liabilities = AT-DLC-DLTT-PSTK-CEQ; netting to DLC+DLTT-CHE net of the
    #   PSTK+CEQ terms, which are small for most firms).
    funda["noa"] = (funda["dlc"] + funda["dltt"] - funda["che"]) / funda["at_lag1"]

    ann_req = ("be", "at", "lt", "act", "che", "lct", "dlc", "dltt", "ppent",
               "invt", "ib", "ni", "revt", "cogs", "dp", "oancf", "txt", "itcb",
               "at_lag1", "ppent_lag1", "invt_lag1", "ni_lag1", "acc", "noa")
    ann = _merge_asof_lag(panel, funda, "datadate", ANN_LAG_MONTHS, ann_req)
    for c in ann_req:
        panel[c] = ann[c].values

    # -------- BM = ln(BE / me); nonpositive BE/ME -> NaN --------
    # BE in millions USD, me in dollars -> BE * 1e6 / me (COMPUSTAT.md units).
    be_me = panel["be"] * 1e6 / panel["me"]
    panel["bm"] = np.where(be_me > 0, np.log(be_me), np.nan)

    # -------- asset growth (I/A; CGS 2008) --------
    panel["ag"] = (panel["at"] - panel["at_lag1"]) / panel["at_lag1"]
    panel["ia"] = panel["ag"]

    # -------- investment-to-assets (Titman-Wei-Xie / Xing) --------
    panel["inv_at"] = ((panel["ppent"] - panel["ppent_lag1"])
                       + (panel["invt"] - panel["invt_lag1"])) / panel["at_lag1"]

    # -------- gross profitability (Novy-Marx) --------
    panel["gp"] = (panel["revt"] - panel["cogs"]) / panel["at"]

    # -------- Ohlson (1980) O-score (annual, 6-mo lag, TA undeflated Assumption 20) ---
    ta = panel["at"]            # millions USD
    lt = panel["lt"]
    log_ta = np.log(np.where(ta > 0, ta, np.nan))
    tlta = lt / ta
    wcta = (panel["act"] - panel["lct"]) / ta
    clca = panel["lct"] / panel["act"]
    oeneg = np.where(ta < lt, 1.0, 0.0)
    nita = panel["ni"] / ta
    futl = panel["oancf"] / lt
    intwo = np.where((panel["ni"] < 0) & (panel["ni_lag1"] < 0), 1.0, 0.0)
    denom_chin = np.abs(panel["ni"]) + np.abs(panel["ni_lag1"])
    chin = (panel["ni"] - panel["ni_lag1"]) / np.where(denom_chin > 0, denom_chin, np.nan)
    panel["oscore"] = (
        -1.32 - 0.407 * log_ta + 6.03 * tlta - 1.43 * wcta + 0.0757 * clca
        - 1.72 * oeneg - 2.37 * nita - 1.83 * futl + 0.285 * intwo - 0.521 * chin
    )

    # =========================================================================
    # Quarterly signals: ROE, ROA, CHS distress (4-month lag).
    # =========================================================================
    fundq = fundq.sort_values(["permno", "datadate"]).reset_index(drop=True)
    # quarterly book equity: seqq + txdbq + itcb(annual) - pref
    # fundq lacks itcbq -> use annual itcb merged on (permno, fyear), else 0
    # (documented in Assumption 13/19). pref = pstkq, else pstkrq, else 0.
    itcb_a = funda[["permno", "fyear", "itcb"]].drop_duplicates(
        subset=["permno", "fyear"], keep="last")
    fundq = fundq.merge(itcb_a, left_on=["permno", "fyearq"],
                        right_on=["permno", "fyear"], how="left", suffixes=("", "_a"))
    fundq["itcb_use"] = fundq["itcb"].fillna(0.0)
    prefq = fundq["pstkq"].combine_first(fundq["pstkrq"]).fillna(0.0)
    fundq["be_q"] = (fundq["seqq"] + fundq["txdbq"].fillna(0.0)
                     + fundq["itcb_use"] - prefq)
    gq = fundq.groupby("permno", sort=False)
    fundq["be_q_lag1"] = gq["be_q"].shift(1)
    fundq["atq_lag1"] = gq["atq"].shift(1)

    qtr_req = ("atq", "ltq", "be_q", "be_q_lag1", "atq_lag1", "ibq", "niq",
               "cheq", "cshoq", "prccq", "seqq", "ceqq")
    qtr = _merge_asof_lag(panel, fundq, "datadate", QTR_LAG_MONTHS, qtr_req)
    for c in qtr_req:
        panel[c] = qtr[c].values

    # -------- ROE = ibq / one-quarter-lagged book equity --------
    panel["roe"] = panel["ibq"] / panel["be_q_lag1"]
    # -------- ROA = ibq / prior-quarter total assets (Chen-Novy-Marx-Zhang) ---
    panel["roa_q"] = panel["ibq"] / panel["atq_lag1"]

    # -------- CHS (2008) distress (published coefficients) --------
    be_q_dollars = panel["be_q"] * 1e6
    mta_q = panel["atq"] * 1e6 + 0.1 * (panel["me"] - be_q_dollars)
    tlmta = panel["ltq"] * 1e6 / mta_q
    cashmta = panel["cheq"] * 1e6 / mta_q
    mta_book = be_q_dollars + 0.1 * (panel["me"] - be_q_dollars)
    mb = panel["me"] / mta_book

    # NIMTAAVG: EW average of NIMTA over last 4 quarters (rho=2/3). The quarterly
    # NIMTA depends on month-t market equity, so compute per panel row: carry the
    # current + 3 lagged quarters of niq/atq/be_q into the panel and average.
    for k in range(3):
        fundq[f"niq_l{k+1}"] = gq["niq"].shift(k + 1)
        fundq[f"atq_l{k+1}"] = gq["atq"].shift(k + 1)
        fundq[f"be_q_l{k+1}"] = gq["be_q"].shift(k + 1)
    qtr2_req = ("niq", "atq", "be_q", "ltq", "cheq",
                "niq_l1", "atq_l1", "be_q_l1",
                "niq_l2", "atq_l2", "be_q_l2",
                "niq_l3", "atq_l3", "be_q_l3")
    qtr2 = _merge_asof_lag(panel, fundq, "datadate", QTR_LAG_MONTHS, qtr2_req)

    def _nimta_of(niq_s, atq_s, beq_s):
        beq_d = beq_s * 1e6
        mta = atq_s * 1e6 + 0.1 * (panel["me"].values - beq_d)
        return niq_s * 1e6 / mta

    nims = [_nimta_of(qtr2["niq"], qtr2["atq"], qtr2["be_q"]),
            _nimta_of(qtr2["niq_l1"], qtr2["atq_l1"], qtr2["be_q_l1"]),
            _nimta_of(qtr2["niq_l2"], qtr2["atq_l2"], qtr2["be_q_l2"]),
            _nimta_of(qtr2["niq_l3"], qtr2["atq_l3"], qtr2["be_q_l3"])]
    w = np.array([CHS_RHO ** 0, CHS_RHO ** 1, CHS_RHO ** 2, CHS_RHO ** 3])
    nimtaavg = (w[0] * nims[0] + w[1] * nims[1] + w[2] * nims[2] + w[3] * nims[3]) / w.sum()

    # EXRET = log(1+ret) - log(1+vwretd_m) over t-12..t-1; EXRETAVG = mean.
    mkt_map = mkt.set_index("month")
    panel = panel.sort_values(["permno", "month"]).reset_index(drop=True)
    panel["_vwretd_m"] = panel["month"].map(mkt_map["vwretd_m"])
    panel["_exret"] = np.log1p(panel["ret"]) - np.log1p(panel["_vwretd_m"])
    gp_ = panel.groupby("permno", sort=False)
    panel["_exretavg"] = gp_["_exret"].shift(1).rolling(12, min_periods=1).mean().reset_index(
        level=0, drop=True)

    # RSIZE = log(me / total CRSP market cap)  [S&P500 proxy = dsi.totval]
    panel["_totval"] = panel["month"].map(mkt_map["totval"])
    panel["_rsize"] = np.log(panel["me"] / panel["_totval"])

    # Net stock issuance (NSI), CSI-5, and month-end prc (for CHS PRICE).
    shares = (shares.drop_duplicates(subset=["permno", "month"], keep="last")
              .sort_values(["permno", "month"]))
    sh_g = shares.groupby("permno", sort=False)
    shares["nsi"] = np.log(shares["adjshrout"]) - np.log(sh_g["adjshrout"].shift(12))
    shares["csi5"] = np.log(shares["adjshrout"]) - np.log(sh_g["adjshrout"].shift(60))
    panel = panel.merge(shares[["permno", "month", "nsi", "csi5", "adjshrout", "prc"]],
                        on=["permno", "month"], how="left")

    # CEI = 12-month growth in SPLIT-INVARIANT ME minus cumret12 (iteration-3
    # M1 fix). The prior Iteration-9 construction used me_adj = |prc| * shrout
    # * cfacshr (the cfacshr-adjusted "current-basis" shares from the
    # issuance_shares relation). This carried two defects:
    #   1. cfacshr changes only at stock splits/dividends, but shrout itself is
    #      ALREADY restated at the same event, so prc*shrout*cfacshr double-counts
    #      the split factor across a 12-month window (lagged denominator at a
    #      different cfacshr level) and inflates the growth ratio.
    #   2. The 12-mo-lagged denominator is near-zero/stale for genuine share
    #      restatements (e.g. permno 89134: shrout 119 -> 476,871 thousands in one
    #      month), blowing up me_gr12 to ~4730 and std to ~7 (40x the 12-mo return
    #      std ~0.83), so ce = me_gr12 - cumret12 becomes pure ME noise instead of
    #      the small Daniel-Titman net-issuance residual.
    # The fix (construction "split-invariant + log"): use me = abs(prc) * shrout
    # * 1000, which is ALREADY split-invariant (a 2:1 split halves prc and doubles
    # shrout, leaving the product unchanged on a within-date basis). ce is the LOG
    # Daniel-Titman net-issuance residual:
    #   cei = log(me / me_{t-12}) - log(1 + cumret12)
    # Growth is a calendar-month-aligned 12-month lookback (merge on month-12), NOT
    # a row-position shift, so firms with a data gap get NaN rather than a spurious
    # ratio across a multi-year gap. Rows with a missing/non-positive lagged ME
    # (genuinely broken input: shrout<=0 at t-12) are set to NaN.
    #   me is the panel's own split-invariant me column; cumret12 is the t-11..t
    #   cumulative return.
    me_lag = panel[["permno", "month", "me"]].copy()
    me_lag["month"] = me_lag["month"] + 12
    me_lag = me_lag.rename(columns={"me": "me_l12"})
    panel = panel.merge(me_lag, on=["permno", "month"], how="left")
    # genuinely broken input rows (stale/near-zero lagged ME denominator) -> NaN
    bad_lag = ~(panel["me_l12"] > 0) | ~np.isfinite(panel["me_l12"].astype(float))
    panel["_me_l12"] = panel["me_l12"].where(~bad_lag)
    panel["me_gr12"] = np.log(panel["me"] / panel["_me_l12"])
    panel["cei"] = panel["me_gr12"] - np.log1p(panel["cumret12"])
    panel["ce"] = panel["cei"]
    panel = panel.drop(columns=["me_l12", "_me_l12"])

    # SIGMA = std of daily returns over last 3 months, annualized (*sqrt(252)).
    #   Source: daily_universe.parquet (already PIT-filtered).
    daily = _load_daily_universe()
    daily = daily[["permno", "date", "ret"]].copy()
    daily["month"] = daily["date"].dt.to_period("M")
    # monthly daily-return std over a 3-month trailing window per permno
    daily = daily.sort_values(["permno", "date"])
    dg = daily.groupby("permno", sort=False)
    # combine a 3-month window: use rolling std of daily ret over ~63 days
    daily["_rollstd"] = dg["ret"].rolling(63, min_periods=15).std().reset_index(
        level=0, drop=True)
    dmon = daily.groupby(["permno", "month"])["_rollstd"].last().reset_index()
    dmon["sigma"] = dmon["_rollstd"] * np.sqrt(252)
    panel = panel.merge(dmon[["permno", "month", "sigma"]],
                        on=["permno", "month"], how="left")

    # PRICE = log(prc), floored at log(15) (CHS). prc = month-end |prc| from CRSP
    # (merged from the shares relation above).
    log_prc = np.log(np.maximum(panel["prc"], CHS_PRICE_FLOOR))

    # CHS logit
    z = (CHS_BETA[0] + CHS_BETA[1] * nimtaavg + CHS_BETA[2] * tlmta
         + CHS_BETA[3] * panel["_exretavg"] + CHS_BETA[4] * panel["sigma"]
         + CHS_BETA[5] * panel["_rsize"] + CHS_BETA[6] * cashmta
         + CHS_BETA[7] * mb + CHS_BETA[8] * log_prc)
    panel["distress"] = 1.0 / (1.0 + np.exp(-z))

    # =========================================================================
    # Sanitize ratio signals: replace non-finite values (inf/-inf) with NaN so
    # they do not tie at the extreme of the percentile ranks. Division by a
    # near-zero lagged denominator produces genuine infinities (broken obs).
    # =========================================================================
    for col in ("nsi", "cei", "acc", "noa", "ag", "inv_at", "gp", "roe",
                "roa_q", "csi5", "oscore", "distress"):
        if col in panel.columns:
            panel.loc[~np.isfinite(panel[col].astype(float)), col] = np.nan

    # =========================================================================
    # The 11 SY mispricing anomalies -> monthly percentile ranks (0-100).
    #   orientation: higher rank -> lower expected next-month return.
    # Ascending ranks: nsi, cei, acc, noa, ag, inv_at, distress, oscore.
    # Descending ranks: mom12_2, gp, roa_q.
    # =========================================================================
    for col in ("nsi", "cei", "acc", "noa", "ag", "inv_at", "distress", "oscore"):
        panel[f"rank_{col}"] = _rank_asc(panel, col)
    panel["rank_mom12_2"] = _rank_desc(panel, "mom")
    panel["rank_gp"] = _rank_desc(panel, "gp")
    panel["rank_roa_q"] = _rank_desc(panel, "roa_q")

    rank_cols = ["rank_nsi", "rank_cei", "rank_acc", "rank_noa", "rank_ag",
                 "rank_inv_at", "rank_distress", "rank_oscore", "rank_mom12_2",
                 "rank_gp", "rank_roa_q"]
    panel["mis"] = panel[rank_cols].mean(axis=1)

    # Issuance index: mean of ascending ranks of nsi, cei (ce), csi5.
    panel["rank_csi5"] = _rank_asc(panel, "csi5")
    panel["iss_idx"] = panel[["rank_nsi", "rank_cei", "rank_csi5"]].mean(axis=1)

    # drop helper columns
    drop_cols = ["_vwretd_m", "_exret", "_exretavg", "_totval",
                 "_rsize", "_prc"]
    panel = panel.drop(columns=[c for c in drop_cols if c in panel.columns])

    return panel


# =========================================================================
# SECTION 4 — Institutional holdings (INST/ΔINST) + skewness (ISKEW/E(ISKEW))
#             + beta^MAX, plus the ROE/bm_raw fixes (Section 3 review).
# =========================================================================
# Extends the Section-3 panel (key (permno, month)) but is IDEMPOTENT: it
# loads data/panel.parquet, mutates/overwrites only the affected columns
# (bm_raw new, roe overwritten), and adds inst, dinst, iskew, eiskew, betamax.
# =========================================================================

# ---- annualized-ROE fix (Assumption 23) and raw BM (Assumption 22) ----
_ANNUAL_ROE = 4.0


def _apply_roe_bm_fixes(panel: pd.DataFrame) -> pd.DataFrame:
    """Rebuild roe (annualized) and add bm_raw. Idempotent: overwrites roe,
    assigns bm_raw fresh, and preserves every other existing column."""
    panel = panel.copy()
    # Raw BE/ME ratio (Assumption 22). be in $M, me in $ -> be*1e6 / me.
    be_me = panel["be"] * 1e6 / panel["me"]
    panel["bm_raw"] = np.where(np.isfinite(be_me) & (be_me > 0), be_me, np.nan)
    # Annualized ROE (Assumption 23): 4 * ibq / one-quarter-lagged book equity.
    panel["roe"] = _ANNUAL_ROE * panel["ibq"] / panel["be_q_lag1"]
    panel.loc[~np.isfinite(panel["roe"]), "roe"] = np.nan
    return panel


# ---- FF-17 industry mapping (SIC -> industry id) ----
# Standard Ken French 17-industry portfolio classification from 4-digit SIC,
# applied on CRSP hsiccd. Unclassified -> industry 17 ("Other"). Exact SIC
# boundaries follow French's "17 Industry Portfolios" file (fixed-effect
# controls only -- medians are insensitive to small boundary imprecisions).
_FF17_SIC = [
    (1,   "Food",  [(100, 999), (2000, 2399), (2700, 2749), (2770, 2799),
                    (3100, 3199), (3940, 3989)]),
    (2,   "Mines", [(1000, 1499)]),
    (3,   "Oil",   [(1300, 1399), (2900, 2999), (4600, 4699)]),
    (4,   "Clths", [(2200, 2399), (3100, 3199), (5600, 5699)]),
    (5,   "Durbl", [(2400, 2499), (3000, 3099), (3400, 3499), (3600, 3699),
                    (3700, 3799), (3900, 3999)]),
    (6,   "Chems", [(2800, 2899)]),
    (7,   "Cnsum", [(2500, 2599), (2600, 2699), (3270, 3299), (3500, 3599),
                    (3700, 3729), (3800, 3879), (4000, 4099), (5000, 5099),
                    (5700, 5799), (7000, 7099)]),
    (8,   "Cnstr", [(1500, 1799), (2400, 2499), (3200, 3299), (5200, 5299)]),
    (9,   "Steel", [(3300, 3399), (3440, 3489), (3620, 3699)]),
    (10,  "FabPr", [(3000, 3099), (3400, 3439), (3490, 3499), (3500, 3599),
                    (3900, 3999)]),
    (11,  "Machn", [(3510, 3599), (3650, 3669), (3710, 3719), (3750, 3759),
                    (3800, 3899)]),
    (12,  "Autos", [(3710, 3719), (3720, 3739), (3740, 3799)]),
    (13,  "Trans", [(3720, 3749), (3750, 3799), (4000, 4099), (4100, 4179),
                    (4200, 4299), (4400, 4499), (4500, 4599), (4700, 4799)]),
    (14,  "Utils", [(4800, 4899), (4900, 4949)]),
    (15,  "Rtail", [(5000, 5099), (5100, 5199), (5200, 5299), (5300, 5399),
                    (5400, 5499), (5500, 5599), (5700, 5799), (5900, 5999)]),
    (16,  "Money", [(6000, 6999)]),
]
_FF17_DEFAULT = 17


def _ff17_ind(sic: np.ndarray) -> np.ndarray:
    """Map 4-digit SIC codes to FF-17 industry ids (1..17). Vectorized."""
    sic = np.asarray(sic, dtype=np.float64)
    out = np.full(sic.shape, _FF17_DEFAULT, dtype=np.int64)
    valid = np.isfinite(sic)
    if not valid.any():
        return out
    s = sic[valid].astype(np.int64)
    ids = np.full(s.shape, _FF17_DEFAULT, dtype=np.int64)
    for ind_id, _name, ranges in _FF17_SIC:
        mask = np.zeros(s.shape, dtype=bool)
        for lo, hi in ranges:
            mask |= (s >= lo) & (s <= hi)
        ids[mask] = ind_id
    out[valid] = ids
    return out


def _load_inst() -> pd.DataFrame:
    """Quarterly INST from 13F (src/sql/inst_13f.sql). Returns (permno,
    fquarter, inst, shrout_src) with inst = min(sum_shares/shrout, 1.0)."""
    raw = q_file("inst_13f.sql")
    raw["permno"] = raw["permno"].astype("int64")
    raw["fquarter"] = pd.to_datetime(raw["fquarter"])
    raw = raw.sort_values(["permno", "fquarter"])
    raw = raw.drop_duplicates(subset=["permno", "fquarter"], keep="last")
    denom = raw["shrout"].astype(float)
    inst = np.where(denom > 0, raw["inst_shares"].astype(float) / denom, np.nan)
    inst = np.where(np.isfinite(inst), np.minimum(inst, 1.0), np.nan)
    raw["inst"] = inst
    return raw[["permno", "fquarter", "inst", "shrout_src", "n_managers"]]


def _merge_inst_monthly(panel: pd.DataFrame) -> pd.DataFrame:
    """Merge quarterly INST onto the monthly panel via merge_asof (forward
    fill from the most recent quarter-end); months before 1980-04 NaN; then
    dinst = INST_t - INST_{t-1}, NaN at first INST obs. Returns panel."""
    inst_q = _load_inst()[["permno", "fquarter", "inst"]]
    panel = panel.copy()

    # align on a permno-sorted key; merge_asof needs global sort on `on`.
    panel = panel.sort_values("date").reset_index(drop=True)
    inst_q = (inst_q.rename(columns={"fquarter": "date"})
              .sort_values("date"))
    # align datetime64 resolutions before merge_asof (ClickHouse Date
    # parses to [s]; panel `date` may be [us])
    inst_q["date"] = inst_q["date"].astype(panel["date"].dtype)
    merged = pd.merge_asof(
        panel, inst_q, on="date", by="permno", direction="backward",
        allow_exact_matches=True,
    )
    panel["inst"] = merged["inst"].values

    # months before the first quarter-end (1980-03-31) stay NaN; the first
    # forward-filled month is 1980-04.
    first_q = inst_q["date"].min()
    panel.loc[panel["date"] < first_q, "inst"] = np.nan

    # dinst = change through most recent quarter-end, per permno. Forward-fill
    # produces no look-ahead (each month uses only quarter-ends <= that month).
    panel = panel.sort_values(["permno", "date"]).reset_index(drop=True)
    inst_ff = panel.groupby("permno")["inst"].ffill()
    inst_shift = inst_ff.groupby(panel["permno"]).shift(1)
    dinst = inst_ff - inst_shift
    first_flag = inst_ff.notna() & inst_shift.isna()
    dinst = dinst.where(~first_flag, np.nan)
    panel["inst"] = inst_ff.values
    panel["dinst"] = dinst.values
    return panel


def _rolling_iskew(daily: pd.DataFrame, ff3: pd.DataFrame) -> pd.DataFrame:
    """60-month (1260 trading day) rolling FF3-residual skewness per permno.

    Endpoint-beta residuals: for each month-end t, estimate the OLS beta of
    daily excess return on [1, mkt_rf, smb, hml] over the trailing 1260 days,
    then take the Fisher-Pearson (bias=False) skewness of those residuals.

    Fully vectorized via a pure-numpy N x K monomial matrix + segmented cumsum
    (no per-stock/day Python loop and no per-column groupby). The window sums
    of r, r^2, r^3 at each month-end are expanded polynomially in beta. The
    >=500 non-missing residual day requirement (Assumption 17) is enforced via
    the running day-count n. Returns (permno, month, iskew).
    """
    window = 1260
    min_obs = 500
    from itertools import product as _prod

    d = daily[["permno", "date", "ret"]].copy()
    ff = ff3[["dt", "mkt_rf", "smb", "hml", "rf"]].rename(columns={"dt": "date"})
    d = d.merge(ff, on="date", how="left")
    d = d.dropna(subset=["ret", "mkt_rf", "smb", "hml", "rf"])
    d["y"] = (d["ret"] - d["rf"]).astype(np.float64)
    d = d.sort_values(["permno", "date"])

    permno = d["permno"].to_numpy(np.int64)
    n = len(d)
    # base columns (x0=1 implicit); variables y, f1=mkt_rf, f2=smb, f3=hml
    cols = [d["y"].to_numpy(np.float64),
            d["mkt_rf"].to_numpy(np.float64),
            d["smb"].to_numpy(np.float64),
            d["hml"].to_numpy(np.float64)]
    # month-end mask (last trading day of each permno-month) via pandas (cheap,
    # computed once on the sorted frame).
    month_arr = d["date"].dt.to_period("M").values
    d["_month"] = month_arr
    d["_is_last"] = d.groupby(["permno", "_month"])["date"].transform("max") == d["date"]
    me = d["_is_last"].values

    # group running count (position within permno) via cumulative count
    boundaries = np.r_[0, np.flatnonzero(permno[1:] != permno[:-1]) + 1, n]
    pos = np.arange(n) - np.repeat(boundaries[:-1], np.diff(boundaries)) + 1
    n_per_row = np.minimum(pos, window).astype(np.float64)

    # ---- monomial matrix M (N, K): all y^ey * f1^e1 * f2^e2 * f3^e3 of degree
    # 1..3. Exponent tuples listed and kept in a dict for O(1) lookup.
    mono_exps = []
    for deg in (1, 2, 3):
        for exps in _prod(range(4), repeat=4):
            if sum(exps) == deg and any(x > 0 for x in exps):
                mono_exps.append(exps)
    exp_idx = {e: i for i, e in enumerate(mono_exps)}
    K = len(mono_exps)
    M = np.empty((n, K), dtype=np.float64)
    for i, exps in enumerate(mono_exps):
        col = np.ones(n)
        for v in range(4):
            if exps[v]:
                col = col * (cols[v] ** exps[v])
        M[:, i] = col

    # ---- segmented cumsum along columns (reset per permno) ----
    C = np.cumsum(M, axis=0)                       # global cumsum
    # subtract group-start offset to reset cumsum per permno
    group_start = boundaries[:-1]                   # start index of each permno
    starts = M[group_start]                         # (G, K) row values at group starts
    # For each row, subtract the cumsum value PREVIOUS to its group start.
    # cumsum value at group_start-1 (0 if group start == 0). Build offsets.
    C_prev = np.vstack([np.zeros((1, K)), C[group_start[1:] - 1]])
    # map each row to its group index
    gidx = np.repeat(np.arange(len(boundaries) - 1), np.diff(boundaries))
    offset = C_prev[gidx]                           # (N, K) cumsum value before group start
    Cseg = C - offset                               # per-permno cumsum

    # ---- window sums: W[k] = Cseg[k] - Cseg[k-window] (clamped within group) ----
    # lag-by-window value = Cseg at position (k - window) if >=0 within group.
    k_minus_w = np.arange(n) - window
    # position of k-window within group = pos - window; valid if pos > window
    valid_lag = pos > window
    lag_pos = np.where(valid_lag, np.arange(n) - window, -1)
    # Cseg at lag_pos: use fancy indexing with -1 -> 0 (before window)
    W = Cseg - np.where((lag_pos >= 0)[:, None],
                        Cseg[np.clip(lag_pos, 0, None)][:, :], 0.0)

    # window count n (capped) and running sum of ones handled separately
    Nme = n_per_row

    def _sum(exps):
        return W[:, exp_idx[tuple(exps)]][me] if me.any() else np.array([])
    def _n_me():
        return Nme[me]

    # ---- assemble X'X, X'y, and monomial window sums at month-end ----
    nm = int(me.sum())
    Nme2 = _n_me()
    # helper exponent tuples
    yvec = (1, 0, 0, 0)
    Sy = _sum(yvec)
    Sy2 = _sum((2, 0, 0, 0))
    Sy3 = _sum((3, 0, 0, 0))

    XX = np.zeros((nm, 4, 4))
    Xyy = np.zeros((nm, 4))
    Xyy[:, 0] = Sy                       # sum 1*y = sum y
    for i in range(1, 4):
        ei = [1, 0, 0, 0]                # sum y*f_i
        ei[i] += 1
        Xyy[:, i] = _sum(tuple(ei))
    for i in range(4):
        for j in range(i, 4):
            if i == 0 and j == 0:
                v = Nme2                  # sum 1*1 = n
            elif i == 0:
                e = [0, 0, 0, 0]; e[j] = 1
                v = _sum(tuple(e))        # sum 1*f_j = sum f_j
            elif j == 0:
                e = [0, 0, 0, 0]; e[i] = 1
                v = _sum(tuple(e))        # sum f_i
            else:
                e = [0, 0, 0, 0]; e[i] += 1; e[j] += 1
                v = _sum(tuple(e))        # sum f_i*f_j
            XX[:, i, j] = v
            XX[:, j, i] = v

    ok = (Nme2 >= min_obs) & np.all(np.isfinite(XX), axis=(1, 2))
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        det = np.linalg.det(XX)
    ok &= np.isfinite(det) & (np.abs(det) > 1e-20)
    beta = np.zeros((nm, 4))
    beta[ok] = np.linalg.solve(XX[ok], Xyy[ok][:, :, None])[..., 0]

    # ---- residual raw window sums (r = y - b0 - b1 f1 - b2 f2 - b3 f3) ----
    b = beta
    Sx = np.zeros((nm, 3)); Syx = np.zeros((nm, 3)); Sy2x = np.zeros((nm, 3))
    for i in range(3):
        ei = [0, 0, 0, 0]; ei[i + 1] = 1
        Sx[:, i] = _sum(tuple(ei))
        eye = [1, 0, 0, 0]; eye[i + 1] = 1
        Syx[:, i] = _sum(tuple(eye))
        eye2 = [2, 0, 0, 0]; eye2[i + 1] = 1
        Sy2x[:, i] = _sum(tuple(eye2))

    # Residual raw window moments. r = y - b0 - q.f with q = b[:,1:], so the
    # 2nd/3rd moments MUST include the intercept b0 cross-terms. The previous
    # expansion dropped b0 (expanding r = y - q.f), which biased Sr2/Sr3 and
    # collapsed the skewness (Iteration-13 M3b fix — spot-checked against a
    # hand-computed window: g1 -0.2436 vs -0.0047 before the fix).
    b0 = b[:, 0]
    q = b[:, 1:]
    Sr = Sy - b0 * Nme2 - (q * Sx).sum(1)
    Sxx = np.zeros((nm, 3, 3))
    for i in range(3):
        for j in range(3):
            e = [0, 0, 0, 0]; e[i + 1] += 1; e[j + 1] += 1
            Sxx[:, i, j] = _sum(tuple(e))
    qSx = (q * Sx).sum(1)
    qSyx = (q * Syx).sum(1)
    Sr2 = (Sy2
           - 2 * b0 * Sy
           - 2 * qSyx
           + b0 * b0 * Nme2
           + 2 * b0 * qSx
           + np.einsum("mi,mij,mj->m", q, Sxx, q))
    Syxx = np.zeros((nm, 3, 3))
    for i in range(3):
        for j in range(3):
            e = [1, 0, 0, 0]; e[i + 1] += 1; e[j + 1] += 1
            Syxx[:, i, j] = _sum(tuple(e))
    Sxxx = np.zeros((nm, 3, 3, 3))
    for i in range(3):
        for j in range(3):
            for k in range(3):
                e = [0, 0, 0, 0]; e[i + 1] += 1; e[j + 1] += 1; e[k + 1] += 1
                Sxxx[:, i, j, k] = _sum(tuple(e))
    qSy2x = (q * Sy2x).sum(1)
    qSxxq = np.einsum("mi,mij,mj->m", q, Sxx, q)
    Sr3 = (Sy3
           - 3 * b0 * Sy2
           - 3 * qSy2x
           + 3 * b0 * b0 * Sy
           + 6 * b0 * qSyx
           + 3 * np.einsum("mi,mij,mj->m", q, Syxx, q)
           - b0 * b0 * b0 * Nme2
           - 3 * b0 * b0 * qSx
           - 3 * b0 * qSxxq
           - np.einsum("mi,mj,mk,mijk->m", q, q, q, Sxxx))

    n_eff = Nme2
    with np.errstate(divide="ignore", invalid="ignore"):
        mean = Sr / n_eff
        var = (Sr2 / n_eff) - mean * mean
        var = np.where(var > 0, var, 0.0)
        sd = np.sqrt(var)
        c3 = (Sr3 / n_eff) - 3 * mean * (Sr2 / n_eff) + 2 * mean ** 3
        adj = np.where(n_eff > 2,
                       np.sqrt(n_eff * (n_eff - 1)) / (n_eff - 2), np.nan)
        g1 = adj * c3 / np.where(sd > 1e-20, sd ** 3, np.nan)

    out = pd.DataFrame({
        "permno": permno[me],
        "month": month_arr[me],
        "iskew": g1,
    })
    out["permno"] = out["permno"].astype("int64")
    out = out[np.isfinite(out["iskew"])]
    return out[["permno", "month", "iskew"]].reset_index(drop=True)


def _eiskew(panel: pd.DataFrame) -> pd.Series:
    """Two-step expected idiosyncratic skewness (Boyer-Mitton-Vorkink 2010).

    Step 1 (per month t): cross-sectional OLS of iskew_t on predictors dated
    t-1: iskew, ivol, mom, turnover, nasdaq dummy (exchcd==3), bottom & middle
    size-tercile dummies, and 16 of 17 FF-17 industry dummies.
    Step 2: E(ISKEW)_t = month-t characteristics x month-t coefficients
    (contemporaneous characteristics, predictive coefficients -- paper L201).
    Returns a pd.Series aligned to the panel's (permno, month) sorted order.
    """
    panel = panel.sort_values(["permno", "month"]).reset_index(drop=True)
    p = panel

    terc = p.groupby("month")["me"].transform(
        lambda s: pd.qcut(s, 3, labels=False, duplicates="drop"))
    sz_bot = (terc == 0).astype(float)
    sz_mid = (terc == 1).astype(float)
    nasdaq = (p["hexcd"] == 3).astype(float)
    ind = _ff17_ind(p["hsiccd"].values)

    cont = pd.DataFrame({
        "iskew": p["iskew"].values,
        "ivol": p["ivol"].values,
        "mom": p["mom"].values,
        "turnover": p["turnover"].values,
        "nasdaq": nasdaq.values,
        "sz_bot": sz_bot.values,
        "sz_mid": sz_mid.values,
    })
    # 16 industry dummies (drop base industry id=2, i.e. keep others via
    # get_dummies on 1..17 then drop the first present column = id 1).
    ind_d = pd.get_dummies(ind.astype(int)).reindex(columns=range(1, 18),
                                                    fill_value=0)
    # drop base category: use the first industry column (id 1) as base
    ind_d = ind_d.iloc[:, 1:]
    cont = pd.concat([cont, ind_d.astype(float).set_axis(cont.index)], axis=1)
    cont.columns = list(cont.columns[:7]) + [f"ind_{k}" for k in range(2, 18)]

    pred_cols = list(cont.columns)

    # lag within permno by one month
    cont["_permno"] = p["permno"].values
    cont["_month"] = p["month"].values
    lag = cont.groupby("_permno", sort=False)[pred_cols].shift(1)
    lag = lag.to_numpy(float)

    y = p["iskew"].to_numpy(float)
    months = p["month"].values
    uniq = np.unique(months)

    X_cont = cont[pred_cols].to_numpy(float)
    X_lag_int = np.column_stack([np.ones(len(y)), lag])

    eiskew = np.full(len(y), np.nan)
    for m in uniq:
        mask = months == m
        yy = y[mask]
        xx = X_lag_int[mask]
        valid = np.isfinite(yy) & np.all(np.isfinite(xx), axis=1)
        if valid.sum() < 20:
            continue
        coef, *_ = np.linalg.lstsq(xx[valid], yy[valid], rcond=None)
        xc = np.column_stack([np.ones(mask.sum()), X_cont[mask]])
        eiskew[mask] = xc @ coef

    # reindex back to original order
    out = pd.Series(eiskew, index=panel.index)
    return out


def _betamax(panel: pd.DataFrame) -> pd.Series:
    """beta^MAX: per-stock 12-month rolling slope of stock MAX on the MARKET's
    MAX. Market MAX in month t = mean of the 5 highest daily market-index
    (crsp_202601.dsi.vwretd) returns in month t (Iteration-9 fix — the prior
    VW cross-sectional mean of stock MAX was replaced). Requires >=10 months
    of overlapping history. Returns a Series aligned to the panel's
    (permno, month) sorted order."""
    panel = panel.sort_values(["permno", "month"]).reset_index(drop=True)
    mkt = q_file("market_max.sql")
    mkt["month"] = pd.to_datetime(mkt["month"]).dt.to_period("M")
    mkt_max = mkt.drop_duplicates("month").set_index("month")["mkt_max"]
    panel["mkt_max"] = panel["month"].map(mkt_max).astype(float)

    g = panel.groupby("permno", sort=False)
    panel["_mkt_max"] = panel["mkt_max"].astype(float)
    panel["_max"] = panel["max"].astype(float)
    n = g["_max"].rolling(12, min_periods=10).count().droplevel(0)
    sx = g["_mkt_max"].rolling(12, min_periods=10).sum().droplevel(0)
    sy = g["_max"].rolling(12, min_periods=10).sum().droplevel(0)
    sxx = (panel["_mkt_max"] ** 2).groupby(panel["permno"], sort=False).rolling(
        12, min_periods=10).sum().droplevel(0)
    sxy = (panel["_mkt_max"] * panel["_max"]).groupby(
        panel["permno"], sort=False).rolling(12, min_periods=10).sum().droplevel(0)
    denom = n * sxx - sx * sx
    bmax = np.where(np.abs(denom) > 1e-12, (n * sxy - sx * sy) / denom, np.nan)
    bmax = np.where(n >= 10, bmax, np.nan)
    return pd.Series(bmax, index=panel.index)


def build_section4(panel: pd.DataFrame) -> pd.DataFrame:
    """Idempotent Section 4 extension (roe/bm_raw fixes + INST/ΔINST + ISKEW/
    E(ISKEW) + beta^MAX). Returns the full panel with new columns added."""
    panel = panel.copy()
    # canonical (permno, month) order for deterministic alignment of the
    # .values-driven column assignments below (eiskew / betamax return arrays
    # in this same order).
    panel = panel.sort_values(["permno", "month"]).reset_index(drop=True)

    # --- fixes (Section 3 review) ---
    panel = _apply_roe_bm_fixes(panel)

    # --- exchange/SIC metadata for the E(ISKEW) predictor set ---
    meta = q_file("panel_meta.sql")
    meta["month"] = pd.to_datetime(meta["date"]).dt.to_period("M")
    meta = (meta[["permno", "month", "hexcd", "hsiccd"]]
            .drop_duplicates(subset=["permno", "month"], keep="last"))
    panel = panel.merge(meta, on=["permno", "month"], how="left")

    # --- INST + ΔINST ---
    print("Building INST / ΔINST (13F) ...")
    panel = _merge_inst_monthly(panel)

    # --- ISKEW ---
    print("Building ISKEW (60-mo FF3 rolling skewness) ...")
    daily = _load_daily_universe()
    ff3 = q_file("ff3_daily.sql")
    ff3["dt"] = pd.to_datetime(ff3["dt"])
    iskew = _rolling_iskew(daily, ff3)
    panel = panel.merge(iskew, on=["permno", "month"], how="left")

    # --- E(ISKEW) ---
    print("Building E(ISKEW) (two-step) ...")
    panel["eiskew"] = _eiskew(panel).values

    # --- beta^MAX ---
    print("Building beta^MAX (12-mo rolling) ...")
    panel["betamax"] = _betamax(panel).values

    # drop transient helper cols
    panel = panel.drop(columns=["hexcd", "hsiccd", "mkt_max"], errors="ignore")
    return panel


def _section4_sanity(panel: pd.DataFrame) -> None:
    """Sanity checks + paper Table 2 comparison for the Section 4 extension."""
    print("\n=== Section 4 sanity checks ===")
    print(f"Shape: {panel.shape}")
    dup = panel.duplicated(subset=["permno", "month"]).sum()
    print(f"(d) duplicate (permno, month): {dup}")

    new_cols = ["inst", "dinst", "iskew", "eiskew", "betamax", "bm_raw"]
    print("\nNull-rate per new column:")
    for c in new_cols:
        if c in panel.columns:
            print(f"  {c:10s}  {panel[c].isna().mean():.4f}")

    roe = panel["roe"].dropna()
    print(f"\nROE (annualized) median={roe.median():.4f} mean={roe.mean():.4f}")

    inst = panel["inst"].dropna()
    print(f"(a) inst range [{inst.min():.4f}, {inst.max():.4f}] "
          f"median={inst.median():.4f}")

    first = panel.loc[panel["inst"].notna(), "month"].min()
    print(f"(b) first non-null INST month: {first} (expect >= 1980-04)")

    s = panel.dropna(subset=["inst", "me"])
    if len(s):
        log_me = np.log(s["me"].clip(lower=1.0))
        c = np.corrcoef(s["inst"], log_me)[0, 1]
        print(f"(c) corr(inst, log_me) = {c:.4f}")

    eisk = panel["eiskew"].dropna()
    print(f"(e) eiskew median={eisk.median():.4f} range "
          f"[{eisk.min():.4f}, {eisk.max():.4f}]")

    print("\nTime-series means of cross-sectional medians:")
    for c in ["inst", "eiskew", "iskew", "betamax", "bm_raw", "roe"]:
        if c in panel.columns:
            med_ts = panel.groupby("month")[c].median().mean()
            print(f"  {c:8s}  median_ts={med_ts:.6f}")



def _panel_sanity(panel: pd.DataFrame) -> None:
    """Print panel summary stats and run the auditable sanity checks."""
    print("=== Panel sanity checks ===")
    print(f"Shape: {panel.shape}")
    print(f"n unique permnos: {panel['permno'].nunique()}")
    print(f"n months: {panel['month'].nunique()}")
    print(f"Date range: {panel['month'].min()} .. {panel['month'].max()}")

    obs_by_year = panel.groupby(panel["month"].dt.year).size()
    print(f"obs per year: min={obs_by_year.min()}, mean={obs_by_year.mean():.1f}, "
          f"max={obs_by_year.max()}")

    print("\nNull-rate per column:")
    for c in panel.columns:
        nr = panel[c].isna().mean()
        print(f"  {c:14s}  {nr:.4f}")

    # Sanity (a): MAX in [0,2] for >99.9% of non-null MAX rows
    maxnn = panel["max"].dropna()
    frac = ((maxnn >= 0) & (maxnn <= 2)).mean()
    print(f"\n(a) MAX in [0,2]: {frac:.5f} of non-null MAX rows "
          f"({(panel['max'].isna().mean()):.4f} MAX null-rate)")

    # Sanity (b): mean ret_excess (equal-weight) vs market; also VW with lagged ME
    vw = (panel["ret_excess"] * panel["me_lag1"]).sum() / panel["me_lag1"].sum()
    print(f"\n(b) mean ret_excess (EW) = {panel['ret_excess'].mean():.6f}")
    print(f"    mean ret_excess (VW, lagged me) = {vw:.6f}")

    # Sanity (c): duplicate check
    dup = panel.duplicated(subset=["permno", "month"]).sum()
    print(f"(c) duplicate (permno, month) rows: {dup}")

    # Cross-sectional means/medians time-series (paper Table 2 comparison)
    print("\nTime-series means of cross-sectional mean/median:")
    for col in ["max", "beta", "ivol", "illiq", "mom", "rev"]:
        cs = panel.groupby("month")[col].agg(["mean", "median"])
        print(f"  {col:8s}  mean_ts={cs['mean'].mean():.6f}  median_ts={cs['median'].mean():.6f}")
    log_me = np.log(panel["me"].clip(lower=1.0))
    csme = panel.assign(log_me=log_me).groupby("month")["log_me"].agg(["mean", "median"])
    print(f"  log(me)   mean_ts={csme['mean'].mean():.4f}  median_ts={csme['median'].mean():.4f}")


def _section3_sanity(panel: pd.DataFrame) -> None:
    """Sanity checks + paper Table 2 comparison for the Section 3 extension."""
    print("\n=== Section 3 sanity checks ===")
    print(f"Shape: {panel.shape}")
    dup = panel.duplicated(subset=["permno", "month"]).sum()
    print(f"(d) duplicate (permno, month): {dup}")

    new_cols = ["bm", "roe", "ia", "mis", "ce", "nsi", "acc", "noa", "ag",
                "inv_at", "gp", "roa_q", "distress", "oscore", "iss_idx",
                "csi5", "cei", "be"]
    print("\nNull-rate per new column:")
    for c in new_cols:
        if c in panel.columns:
            print(f"  {c:12s}  {panel[c].isna().mean():.4f}")

    # (a) mis bounds
    mis = panel["mis"].dropna()
    print(f"\n(a) mis range [{mis.min():.2f}, {mis.max():.2f}] "
          f"mean={mis.mean():.3f} std={mis.std():.3f}")

    # (b) rank(mis) cross-correlated with rank(ce): monotone direction check
    tmp = panel.copy()
    tmp["_rank_mis"] = tmp.groupby("month")["mis"].rank(pct=True)
    s = tmp.dropna(subset=["_rank_mis", "rank_cei"])
    if len(s):
        c = np.corrcoef(s["_rank_mis"], s["rank_cei"])[0, 1]
        print(f"(b) corr(rank_mis, rank_cei) = {c:.4f}")

    # (c) monotone sign checks (rank vs raw signal)
    for a, b in [("rank_nsi", "nsi"), ("rank_cei", "cei"), ("rank_acc", "acc"),
                 ("rank_ag", "ag"), ("rank_gp", "gp"), ("rank_roa_q", "roa_q")]:
        s = panel.dropna(subset=[a, b])
        if len(s):
            cc = np.corrcoef(s[a], s[b])[0, 1]
            print(f"(c) corr({a}, {b}) = {cc:.4f}")

    # (e) BM coverage (% of panel rows with BM)
    n_bm = panel["bm"].notna().sum()
    print(f"(e) BM coverage: {n_bm} rows ({n_bm/len(panel):.1%} of panel)")

    # Time-series means of cross-sectional medians (paper Table 2)
    print("\nTime-series means of cross-sectional medians:")
    for c in new_cols:
        if c in panel.columns:
            med_ts = panel.groupby("month")[c].median().mean()
            print(f"  {c:12s}  median_ts={med_ts:.6f}")


def _sanity_checks(factors: pd.DataFrame) -> None:
    """Print per-column coverage + smoke-test means, and assert invariants."""
    print("=== Factor panel sanity checks ===")
    print(f"Shape: {factors.shape}")
    print(f"Index type: {type(factors.index)}  freq={factors.index.freqstr if hasattr(factors.index, 'freqstr') else None}")
    print(f"Date range: {factors.index.min()} .. {factors.index.max()}")

    print("\nPer-column coverage (first valid, last valid, count non-null):")
    for col in factors.columns:
        s = factors[col].dropna()
        if len(s) == 0:
            print(f"  {col:10s}  (no valid obs)")
            continue
        first = s.index.min()
        last = s.index.max()
        print(f"  {col:10s}  {first} .. {last}  n={len(s)}")

    print("\nSmoke-test means over common 1968-2022 window:")
    for col in factors.columns:
        print(f"  {col:10s}  mean={factors[col].mean():.6f}")

    # --- asserts ---
    ps = factors["ps_liq"].dropna()
    assert ps.index.min() == START, f"ps_liq first valid = {ps.index.min()}, expected {START}"

    sy_mgmt = factors["sy_mgmt"].dropna()
    assert sy_mgmt.index.max() == pd.Period("2016-12", freq="M"), (
        f"sy_mgmt max = {sy_mgmt.index.max()}, expected 2016-12"
    )

    full = factors[(factors.index >= START) & (factors.index <= END)]
    for col in ["mkt_rf", "smb", "hml", "mom", "rmw", "cma", "rf"]:
        assert full[col].notna().all(), f"NaN found in {col} over 1968-2022"

    assert full.index.min() == START and full.index.max() == END, "FF coverage mismatch"

    print("\nAll sanity-check asserts passed.")


def _pipeline_funnel() -> None:
    """Audit the universe-filter funnel row counts at each stage."""
    print("\n=== Universe funnel (row counts) ===")
    # raw dsf monthly-row-equivalent: count daily rows in range that will
    # become monthly rows (report daily + monthly as separate milestones).
    c = _client()
    def cnt(sql: str):
        return int(c.execute(sql)[0][0])

    r_raw = cnt("SELECT count() FROM crsp_202601.msf WHERE date >= '1968-01-01' AND date <= '2022-12-31' AND ret IS NOT NULL AND ret > -50")
    r_pit = cnt(
        "SELECT count() FROM crsp_202601.msf m "
        "INNER JOIN crsp_202601.dsfhdr h ON m.permno = h.permno AND m.date >= h.begdat AND m.date <= h.enddat "
        "WHERE m.date >= '1968-01-01' AND m.date <= '2022-12-31' AND m.ret IS NOT NULL AND m.ret > -50 "
        "AND h.hshrcd IN (10,11) AND h.hexcd IN (1,2,3)"
    )
    r_sic = cnt(
        "SELECT count() FROM crsp_202601.msf m "
        "INNER JOIN crsp_202601.dsfhdr h ON m.permno = h.permno AND m.date >= h.begdat AND m.date <= h.enddat "
        "WHERE m.date >= '1968-01-01' AND m.date <= '2022-12-31' AND m.ret IS NOT NULL AND m.ret > -50 "
        "AND h.hshrcd IN (10,11) AND h.hexcd IN (1,2,3) "
        "AND NOT (h.hsiccd >= 4900 AND h.hsiccd <= 4949) AND NOT (h.hsiccd >= 6000 AND h.hsiccd <= 6999)"
    )
    r_price = cnt(
        "SELECT count() FROM crsp_202601.msf m "
        "INNER JOIN crsp_202601.dsfhdr h ON m.permno = h.permno AND m.date >= h.begdat AND m.date <= h.enddat "
        "WHERE m.date >= '1968-01-01' AND m.date <= '2022-12-31' AND m.ret IS NOT NULL AND m.ret > -50 "
        "AND h.hshrcd IN (10,11) AND h.hexcd IN (1,2,3) "
        "AND NOT (h.hsiccd >= 4900 AND h.hsiccd <= 4949) AND NOT (h.hsiccd >= 6000 AND h.hsiccd <= 6999) "
        "AND abs(m.prc) >= 5"
    )
    # >=15 daily obs in month t (measured on the daily PIT-filtered relation)
    r_obs15 = cnt(
        "SELECT count() FROM ("
        "  SELECT d.permno, toStartOfMonth(toDate32(d.date)) AS mo, count() AS nobs "
        "  FROM crsp_202601.dsf d "
        "  INNER JOIN crsp_202601.dsfhdr h ON d.permno = h.permno AND d.date >= h.begdat AND d.date <= h.enddat "
        "  WHERE d.date >= '1968-01-01' AND d.date <= '2022-12-31' AND d.ret IS NOT NULL AND d.ret > -50 "
        "  AND h.hshrcd IN (10,11) AND h.hexcd IN (1,2,3) "
        "  AND NOT (h.hsiccd >= 4900 AND h.hsiccd <= 4949) AND NOT (h.hsiccd >= 6000 AND h.hsiccd <= 6999) "
        "  GROUP BY d.permno, toStartOfMonth(toDate32(d.date)) HAVING count() >= 15"
        ")"
    )
    print(f"  raw msf (1968-2022, valid ret):            {r_raw}")
    print(f"  after PIT shrcd/exchcd filter:             {r_pit}")
    print(f"  after SIC exclusion:                      {r_sic}")
    print(f"  after price >= $5:                        {r_price}")
    print(f"  daily (permno,month) cells with >=15 obs: {r_obs15}  (daily-granularity,\n"
          f"      NOT the panel row count — panel keeps rows and nulls out\n"
          f"      daily-derived signals where nobs < 15)")


# =========================================================================
# SECTION 5 — T1 (MAX deciles) + T3 (MAX^beta deciles) portfolio sorts and
# factor-model alphas. Produces eval/metrics.json per SKILL rule 7.
#
# FORWARD-RETURN SERIES MUST BE INDEXED BY THE RETURN MONTH (formation month
# + 1) IN EVERY TABLE SECTION — see assumptions.md Iteration 6. The signal/
# bin is assigned at formation month t, but the realized forward return is
# in month t+1; aggregating by formation month misaligns the y-series with
# the factor series by one month (betas attenuated toward 0).
# =========================================================================

# Factor-model wiring. Metric-name prefix -> factor columns.
_MODELS: dict[str, list[str]] = {
    "capm": ["mkt_rf"],
    "ff3": ["mkt_rf", "smb", "hml"],
    "ffc4": ["mkt_rf", "smb", "hml", "mom"],
    "ffcps": ["mkt_rf", "smb", "hml", "mom", "ps_liq"],
    "ff5": ["mkt_rf", "smb", "hml", "rmw", "cma"],
    "ff6": ["mkt_rf", "smb", "hml", "rmw", "cma", "mom"],
    "ff6ps": ["mkt_rf", "smb", "hml", "rmw", "cma", "mom", "ps_liq"],
    "sy": ["sy_mktrf", "sy_smb", "sy_mgmt", "sy_perf"],
}

# Column-order used in the results markdown tables.
_COL_ORDER = ["RET-RF", "CAPM", "FF3", "FFC4", "FFCPS", "FF5", "FF6", "FF6PS", "SY", "DHS"]

_IMPORTED_STATSMODELS = False
def _import_statsmodels():
    global _IMPORTED_STATSMODELS
    if not _IMPORTED_STATSMODELS:
        import statsmodels.api as sm  # noqa: F401
        global sm_mod
        sm_mod = sm
        _IMPORTED_STATSMODELS = True


def _alpha_regress(
    series: pd.Series, factors: pd.DataFrame, factor_cols: list[str], maxlags: int = 6
) -> tuple[float, float, int]:
    """Regress an excess-return series on factor columns; return (alpha, t, nobs).

    alpha is the OLS intercept (in the input's units); t is its HAC
    (Newey-West, Bartlett kernel, ``maxlags`` lags) t-statistic via
    statsmodels cov_type='HAC'. ``factor_cols`` empty => intercept-only
    (mean-return) regression.
    """
    _import_statsmodels()
    X = sm_mod.add_constant(factors[factor_cols]) if factor_cols else pd.DataFrame(
        {"const": 1.0}, index=factors.index
    )
    y = series.reindex(factors.index).dropna()
    X = X.reindex(y.index)
    if len(y) < 2 or X.isna().any().any():
        return float("nan"), float("nan"), int(len(y))
    model = sm_mod.OLS(y, X, missing="drop").fit(
        cov_type="HAC", cov_kwds={"maxlags": maxlags}
    )
    alpha = model.params["const"]
    t = model.tvalues["const"]
    return float(alpha), float(t), int(model.nobs)


def _bin_vw_series(
    panel: pd.DataFrame,
    signal_col: str,
    date_col: str,
    ret_col: str,
    mcap_col: str,
    n_bins: int = 10,
) -> pd.DataFrame:
    """Bin signal@t and return VW bin_rets on the already-paired forward
    return column (``ret_col`` = the panel's ``ret_fwd``, i.e. the t+1
    unfiltered excess return). No groupby-shift is applied here — the t+1
    pairing is done once, month-aligned, on the unfiltered monthly-all
    series when the panel's ret_fwd column is built.

    The returned series are indexed by the RETURN MONTH (formation month
    + 1, column ``ret_month``) rather than the formation ``date_col``, so
    that factor regressions align y(t+1) with factors(t+1). See
    assumptions.md Iteration 6.

    Returns the ``bin_returns`` DataFrame pivoted to wide (month x bin)
    with columns 1..n_bins holding VW returns, indexed by ret_month.
    """
    sub = panel[[date_col, "permno", signal_col, ret_col, mcap_col]].copy()
    sub = sub.dropna(subset=[signal_col, ret_col, mcap_col])
    sub["bin"] = assign_quantiles(sub, date_col, signal_col, n_bins=n_bins)
    sub["ret_month"] = sub[date_col] + 1
    bin_rets = bin_returns(sub, "ret_month", "bin", ret_col, mcap_col=mcap_col)
    wide = bin_rets.pivot(index="ret_month", columns="bin", values="VW")
    return wide


def _table_vw_series(panel: pd.DataFrame, signal_col: str) -> pd.DataFrame:
    """Decile VW series (wide month x P1..P10) for one table."""
    wide = _bin_vw_series(panel, signal_col, "month", "ret_fwd", "me_lag1")
    return wide


def _t3_bin_vw_series(panel: pd.DataFrame) -> pd.DataFrame:
    """MAX^beta grouped deciles: sort beta deciles, within each sort MAX
    deciles, then regroup all within-beta MAX-rank n across beta deciles
    (Assumption 6). Forward return is the panel's ret_fwd (pre-paired t+1)."""
    sub = panel[["month", "permno", "beta", "max", "ret_fwd", "me_lag1"]].copy()
    sub = sub.dropna(subset=["beta", "max", "ret_fwd", "me_lag1"])
    sub["beta_decile"] = assign_quantiles(sub, "month", "beta", n_bins=10)
    # Within each (month, beta_decile), MAX decile rank.
    sub["max_rank"] = sub.groupby(["month", "beta_decile"])["max"].transform(
        lambda s: pd.qcut(s, q=10, labels=False, duplicates="drop")
    )
    # Only months where every beta-decile produced a full 10 ranks (9 here).
    sub = sub.dropna(subset=["max_rank"])
    sub["bin"] = (sub["max_rank"] + 1).astype(int)
    sub["ret_month"] = sub["month"] + 1
    bin_rets = bin_returns(sub, "ret_month", "bin", "ret_fwd", mcap_col="me_lag1")
    wide = bin_rets.pivot(index="ret_month", columns="bin", values="VW")
    return wide


def _table_metrics(
    prefix: str, wide: pd.DataFrame, factors: pd.DataFrame
) -> tuple[dict, dict]:
    """Compute all metrics for one table (10 deciles + spread, per model).

    Returns (metrics dict, series-dict keyed by '{model}:{port}' for the
    markdown table builder). Values in percent (x100); t-stats as-is.
    """
    metrics: dict = {}
    # Build the 11 series: P1..P10 (VW excess) + spread (P10 - P1).
    series = {f"p{n}": wide[n] for n in range(1, 11)}
    series["sprd"] = wide[10] - wide[1]

    # SY window: restrict to months <= 2016-12 (Assumption 7).
    sy_factors = factors[factors.index <= pd.Period("2016-12", freq="M")]

    series_chart: dict = {}  # {port: {model_prefix: (value_pct, t)}}
    for port, s in series.items():
        s = s.dropna()
        # RET-RF: mean excess return (intercept-only), value + HAC t.
        a, t, _n = _alpha_regress(s, factors, [])
        mean_pct = s.mean() * 100.0
        metrics[f"{prefix}_retrf_{port}"] = {"value": round(mean_pct, 4), "unit": "percent_per_month"}
        if port == "sprd":
            metrics[f"{prefix}_retrf_sprd_t"] = {"value": round(t, 4), "unit": "t_stat"}
        series_chart.setdefault("retrf", {})[port] = (mean_pct, t)
        # Factor models.
        for mname, fcols in _MODELS.items():
            fac = sy_factors if mname == "sy" else factors
            if len(fcols) == 0:
                continue
            a, t, _n = _alpha_regress(s, fac, fcols)
            ap = a * 100.0
            metrics[f"{prefix}_{mname}_{port}"] = {"value": round(ap, 4), "unit": "percent_per_month"}
            if port == "sprd":
                metrics[f"{prefix}_{mname}_sprd_t"] = {"value": round(t, 4), "unit": "t_stat"}
            series_chart.setdefault(mname, {})[port] = (ap, t)
    return metrics, series_chart


def _markdown_grid(series_chart: dict) -> str:
    """Render an 11x10 value(t) grid."""
    ports = [f"p{n}" for n in range(1, 11)] + ["sprd"]
    header = "| Port | " + " | ".join(_COL_ORDER) + " |\n"
    header += "|" + " --- |" * (len(_COL_ORDER) + 1) + "\n"
    lines = [header]
    for p in ports:
        label = "10-1" if p == "sprd" else p[1:]
        cells = []
        for c in _COL_ORDER:
            if c == "DHS":
                cells.append("SKIP")
                continue
            key = "retrf" if c == "RET-RF" else _MODEL_KEY[c]
            vt = series_chart.get(key, {}).get(p)
            if vt is None:
                cells.append("—")
            else:
                cells.append(f"{vt[0]:.2f} ({vt[1]:.2f})")
        lines.append(f"| {label} | " + " | ".join(cells) + " |\n")
    return "".join(lines)


_MODEL_KEY = {
    "RET-RF": "retrf", "CAPM": "capm", "FF3": "ff3", "FFC4": "ffc4",
    "FFCPS": "ffcps", "FF5": "ff5", "FF6": "ff6", "FF6PS": "ff6ps",
    "SY": "sy",
}

def build_section5() -> tuple[dict, list[str]]:
    """Build T1 + T3 metrics; also write results/table_1.md + table_6.md."""
    import re

    panel = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
    factors = pd.read_parquet(LAYOUT.data_path("factors.parquet"))

    # Identify committed metric names so we know the DHS cells to skip.
    tables = json.loads(LAYOUT.preparations_path("tables_to_replicate.json").read_text())
    t1 = next(t for t in tables["tables"] if t["id"] == "T1")
    t3 = next(t for t in tables["tables"] if t["id"] == "T3")
    t1_names = {m["name"] for m in t1["metrics"]}
    t3_names = {m["name"] for m in t3["metrics"]}

    metrics: dict = {}

    # ---- T1: MAX deciles ----
    wide1 = _table_vw_series(panel, "max")
    m1, chart1 = _table_metrics("t1", wide1, factors)
    metrics.update(m1)

    # ---- T3: MAX^beta deciles ----
    wide3 = _t3_bin_vw_series(panel)
    m3, chart3 = _table_metrics("t3", wide3, factors)
    metrics.update(m3)

    # ---- DHS skips: every t1_dhs_* and t3_dhs_* committed name ----
    skips = sorted(
        [n for n in list(t1_names) + list(t3_names) if "_dhs_" in n]
    )

    # Write the results markdown tables (grids only; evaluator output appended later).
    LAYOUT.result_path("table_1.md").write_text(
        "# Table 1 — MAX deciles (VW one-month-ahead excess returns and alphas)\n\n"
        "SY window: 1968-2016 (M4.csv ends 2016-12); DHS column SKIP.\n\n"
        + _markdown_grid(chart1)
    )
    LAYOUT.result_path("table_6.md").write_text(
        "# Table 6 — MAX^beta deciles (VW one-month-ahead excess returns and alphas)\n\n"
        "SY window: 1968-2016 (M4.csv ends 2016-12); DHS column SKIP.\n\n"
        + _markdown_grid(chart3)
    )

    return metrics, skips


def main() -> None:
    factors = build_factors()

    out = LAYOUT.data_path("factors.parquet")
    factors.to_parquet(out, index=True)
    print(f"Wrote {out}")

    _sanity_checks(factors)

    # ---- SECTION 2: panel build ----
    _pipeline_funnel()
    panel = build_panel()
    panel_out = LAYOUT.data_path("panel.parquet")
    panel.to_parquet(panel_out, index=False)
    print(f"\nWrote {panel_out}  ({panel.shape[0]} rows x {panel.shape[1]} cols)")

    _panel_sanity(panel)

    # ---- SECTION 3: Compustat + mispricing extension ----
    print("\n=== SECTION 3: Compustat-derived variables + mispricing ===")
    panel = build_section3(panel)
    panel.to_parquet(panel_out, index=False)
    print(f"\nWrote {panel_out}  ({panel.shape[0]} rows x {panel.shape[1]} cols)")

    _section3_sanity(panel)

    # ---- SECTION 4: INST/ΔINST + ISKEW/E(ISKEW) + beta^MAX + fixes ----
    print("\n=== SECTION 4: INST + skewness (ISKEW/E(ISKEW)) + beta^MAX ===")
    panel = build_section4(panel)
    panel.to_parquet(panel_out, index=False)
    print(f"\nWrote {panel_out}  ({panel.shape[0]} rows x {panel.shape[1]} cols)")

    _section4_sanity(panel)

    # ---- SECTION 5: T1/T3 portfolio sorts + alphas + metrics.json ----
    print("\n=== SECTION 5: T1 (MAX deciles) + T3 (MAX^beta deciles) + alphas ===")
    metrics, skips = build_section5()
    LAYOUT.eval_path("metrics.json").write_text(
        json.dumps(
            {"schema_version": 2, "slug": SLUG, "metrics": metrics, "skips": skips},
            indent=2,
            default=float,
        )
    )
    print(f"\nWrote {LAYOUT.eval_path('metrics.json')}  ({len(metrics)} metrics, {len(skips)} skips)")


if __name__ == "__main__":
    main()
