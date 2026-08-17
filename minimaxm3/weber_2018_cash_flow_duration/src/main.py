"""
Weber (2018) "Cash flow duration and the term structure of equity returns"
Replication data pipeline.

Pipeline overview
-----------------
1. ClickHouse SQL pulls (src/sql/*.sql):
   - universe_pit.sql:        monthly CRSP universe (PIT-filtered, excl financials/utilities)
   - panel_monthly.sql:       same as universe_pit + sort_year column
   - panel_annual.sql:        per-(permno, sort_year) annual features (excluding dur/ior)
   - compustat_funda.sql:     per-(gvkey, fyear) fundamentals + lags
   - duration_signal.sql:     per-(gvkey, fyear) seeds for the duration recursion
   - returns_with_delist.sql: monthly returns + delisting code/return for Shumway treatment
   - inst_ownership.sql:      per-(cusip, mgrno) first-appearance 13F holdings
   - ff_factors.sql:          FF3/FF4/FF5 monthly factors

2. Python (this file):
   - Compute cash-flow duration per (gvkey, fyear) using the Dechow et al. 2004 formula
   - Compute IOR per (permno, sort_year) from 13F (first-appearance) holdings
   - Apply Shumway (1997) delisting treatment to monthly returns
   - Assemble final panel_annual.parquet and panel_monthly.parquet

Outputs:
   data/panel_annual.parquet
   data/panel_monthly.parquet
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from clickhouse_driver import Client

from utils.env import get_clickhouse_config
from utils.paths import paper_layout


# ---- Configuration ---------------------------------------------------------
SLUG = "weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns"
LAYOUT = paper_layout(SLUG)
LAYOUT.ensure()

CFG = get_clickhouse_config()
SQL_DIR = LAYOUT.src_path("sql")
DATA_DIR = LAYOUT.data_path("")  # data/ folder

# Duration formula parameters (paper §2.1)
T_FORECAST = 15                  # T = detailed forecasting period (paper §2.1 L174)
R_DISCOUNT = 0.12                # r = discount rate (paper §2.1 L174)
ROE_SS    = 0.12                 # steady-state ROE (paper §2.1 L174)
PHI_ROE   = 0.41                 # AR(1) coefficient on ROE (paper §2.1 L174)
G_SS      = 0.06                 # steady-state sales growth (paper §2.1 L174)
PHI_G     = 0.24                 # AR(1) coefficient on sales growth (paper §2.1 L174)

# Shumway (1997) delisting treatment (paper §2 L104)
SHUMWAY_DLSTCD_RANGE = (400, 591)
SHUMWAY_SUBSTITUTE = -0.30       # -30%

# Sample period
SAMPLE_START = "1963-07-01"      # paper §2 L176
SAMPLE_END   = "2014-06-30"      # paper §2 L176
IOR_SAMPLE_START = "1981-01-01"  # Table 10 IOR-only sample


# ---- ClickHouse connection -------------------------------------------------
def client() -> Client:
    return Client(
        host=CFG["host"],
        port=int(CFG["port"]),
        user=CFG["user"],
        password=CFG["password"],
        database=CFG["database"],
        settings={"max_execution_time": 600, "max_rows_to_read": 5_000_000_000},
    )


def q(sql: str) -> pd.DataFrame:
    """Execute a SQL string and return DataFrame."""
    c = client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


def q_file(name: str) -> pd.DataFrame:
    """Execute a saved SQL file and return DataFrame."""
    return q((SQL_DIR / name).read_text())


# ---- Duration signal (Python, 15-step recursion) ----------------------------
def compute_duration(
    bv_0: np.ndarray,
    roe_seed: np.ndarray,
    g_seed: np.ndarray,
    p_t_0: np.ndarray | None = None,
    r: float = R_DISCOUNT,
    T: int = T_FORECAST,
    phi_roe: float = PHI_ROE,
    roe_ss: float = ROE_SS,
    phi_g: float = PHI_G,
    g_ss: float = G_SS,
) -> np.ndarray:
    """Vectorized 15-step AR(1) recursion on ROE and sales-growth.

    For each row, simulates the 15-year cash flow forecast implied by:
        ROE_{t+s} = ROE_ss + phi_roe * (ROE_{t+s-1} - ROE_ss)
        g_{t+s}   = g_ss   + phi_g   * (g_{t+s-1}   - g_ss)
        BV_{t+s}  = BV_{t+s-1} * (1 + g_{t+s})
        E_{t+s}   = BV_{t+s-1} * ROE_{t+s}
        CF_{t+s}  = BV_{t+s-1} * (ROE_{t+s} - g_{t+s})

    Then computes the Dechow et al. 2004 implied duration:
        Dur = ( sum_{s=1..T} s * CF_{t+s} / (1+r)^s ) / P_t
            + ( T + (1+r)/r ) * ( P_t - sum_{s=1..T} CF_{t+s} / (1+r)^s ) / P_t

    where P_t is the "current price" (paper §2 L108). Per the Dechow et al.
    (2004) formula as cited in Weber (2018), P_t is the CURRENT market price
    (not book equity). The BV recursion above generates the cash-flow path
    (which is a function of book-value dynamics), but the dur denominator
    uses P_t (market equity). Concretely:
        - BV recursion: BV_{t+s} = BV_{t+s-1} * (1 + g_{t+s})
        - CF_{t+s}    = BV_{t+s-1} * (ROE_{t+s} - g_{t+s})
        - P_t (denominator) = market equity (CRSP me_jun_dollars)
    If p_t_0 is None, the function falls back to bv_0 (legacy behavior).

    Parameters
    ----------
    bv_0 : ndarray, shape (n,)    -- book equity at time t (in dollars)
    roe_seed : ndarray, shape (n,) -- initial ROE (ib / lagged BE)
    g_seed : ndarray, shape (n,)   -- initial sales growth (5y preferred, 1y fallback)
    p_t_0 : ndarray or None, shape (n,) -- current market price (dollars).
                                         If None, falls back to bv_0.
    """
    bv_0 = np.asarray(bv_0, dtype=np.float64)
    roe_seed = np.asarray(roe_seed, dtype=np.float64)
    g_seed = np.asarray(g_seed, dtype=np.float64)
    if p_t_0 is None:
        p_t_0 = bv_0
    else:
        p_t_0 = np.asarray(p_t_0, dtype=np.float64)

    n = len(bv_0)
    out = np.full(n, np.nan)

    valid = (
        np.isfinite(bv_0) & (bv_0 > 0)
        & np.isfinite(p_t_0) & (p_t_0 > 0)
        & np.isfinite(roe_seed)
        & np.isfinite(g_seed)
    )
    if not np.any(valid):
        return out

    bv0 = bv_0[valid]
    roe0 = roe_seed[valid]
    g0 = g_seed[valid]
    p0 = p_t_0[valid]
    m = len(bv0)

    # Iterate T steps
    roe_prev = roe0.copy()
    g_prev = g0.copy()
    bv_prev = bv0.copy()

    # Accumulators: PV(CF) and s * PV(CF)
    pv_cf = np.zeros(m)
    s_pv_cf = np.zeros(m)
    discount = 1.0 / (1.0 + r)

    for s in range(1, T + 1):
        roe_curr = roe_ss + phi_roe * (roe_prev - roe_ss)
        g_curr   = g_ss   + phi_g   * (g_prev   - g_ss)
        bv_curr  = bv_prev * (1.0 + g_curr)

        # CF = E - (BV_s - BV_{s-1}) = BV_{s-1} * ROE_s - BV_{s-1} * g_s
        cf_curr = bv_prev * (roe_curr - g_curr)
        pv = discount ** s
        pv_cf   += cf_curr * pv
        s_pv_cf += s * cf_curr * pv

        # advance
        roe_prev = roe_curr
        g_prev   = g_curr
        bv_prev  = bv_curr

    # Duration formula — P_t is the market price (current price),
    # NOT book equity. This is what makes dur correlate NEGATIVELY with
    # B/M (growth firms have high dur; value firms have low dur) rather
    # than positively (which would happen if we used BV as the denominator).
    p_t = p0
    pv_factor = (T + (1.0 + r) / r)
    term1 = s_pv_cf / p_t
    term2 = pv_factor * (p_t - pv_cf) / p_t
    out[valid] = term1 + term2
    return out


# ---- Shumway (1997) delisting treatment ------------------------------------
def apply_shumway(panel: pd.DataFrame) -> pd.DataFrame:
    """Apply Shumway (1997) delisting treatment to monthly returns.

    For each row with a performance-related delisting code (dlstcd in 400-591)
    AND a missing dlret, substitute -0.30. The substituted delisting return is
    added to the delisting-month ret.
    """
    panel = panel.copy()
    shumway_mask = (
        panel["dlstcd"].between(SHUMWAY_DLSTCD_RANGE[0], SHUMWAY_DLSTCD_RANGE[1])
        & panel["dlret"].isna()
    )
    panel.loc[shumway_mask, "dlret"] = SHUMWAY_SUBSTITUTE
    # Delisting-adjusted return: ret + dlret (where dlret is in decimal, e.g. -0.30)
    panel["ret_adj"] = panel["ret"] + panel["dlret"].fillna(0.0)
    # Coerce invalid returns
    panel.loc[panel["ret_adj"] <= -1.0, "ret_adj"] = np.nan
    panel.loc[panel["ret"] <= -1.0, "ret"] = np.nan
    return panel


# ---- IOR computation (Python) ----------------------------------------------
def build_permno_cusip_map() -> pd.DataFrame:
    """Build a (cusip, permno) mapping with PIT validity.

    Uses crsp_202601.msenames (carries cusip, ncusip, permno, namedt, nameendt).
    The CUSIP of record at each point in time is the namedt<=t<nameendt row's cusip.

    To match s34 (which has one cusip per row), we keep only the row where
    namedt <= t and nameendt > t; or equivalently, we keep all rows so the
    downstream join can filter by the fdate.
    """
    sql = """
    SELECT permno, namedt, nameendt, cusip
    FROM crsp_202601.msenames
    WHERE permno IS NOT NULL AND cusip IS NOT NULL AND length(cusip) >= 8
    """
    df = q(sql)
    df["namedt"] = pd.to_datetime(df["namedt"])
    df["nameendt"] = pd.to_datetime(df["nameendt"])
    df["cusip8"] = df["cusip"].str.slice(0, 8)
    return df[["permno", "cusip8", "namedt", "nameendt"]]


def compute_ior(
    instown: pd.DataFrame,
    permno_cusip: pd.DataFrame,
    panel: pd.DataFrame,
) -> pd.DataFrame:
    """Compute IOR per (permno, sort_year) for the 1981-2014 sample.

    IOR_t = sum(shares_{mgrno, q}) / CRSP shrout at sort_year t

    We use the most recent 4 quarters of 13F data (TTM aggregation).

    Parameters
    ----------
    instown : per-(fdate_first, cusip, mgrno) first-appearance shares
    permno_cusip : per-(permno, cusip8) PIT mapping
    panel : monthly CRSP panel with permno, sort_year, year, month, shrout
    """
    print("[IOR] Linking s34 cusips to permnos (vectorized)...")
    instown = instown.copy()
    instown["cusip8"] = instown["cusip"].str.slice(0, 8)
    instown["fdate_first"] = pd.to_datetime(instown["fdate_first"])
    instown["fyear_q"] = instown["fdate_first"].dt.year

    # Join s34 to permno_cusip on cusip8, then filter by date overlap
    # (the CUSIP was valid at the fdate_first)
    merged = instown.merge(
        permno_cusip[["permno", "cusip8", "namedt", "nameendt"]],
        on="cusip8",
        how="inner",
    )
    mask = (merged["fdate_first"] >= merged["namedt"]) & (
        merged["fdate_first"] <= merged["nameendt"]
    )
    merged = merged.loc[mask].copy()

    # Sum shares by (permno, fyear_q) — first-appearance shares for each
    # (mgrno, cusip) pair, summed across all reporting institutions in each
    # calendar year.
    ior_qtr = (
        merged.groupby(["permno", "fyear_q"])["shares_first"].sum().reset_index()
    )
    ior_qtr = ior_qtr.rename(columns={"shares_first": "shares_qtr"})

    # Per-(permno, sort_year) CUMULATIVE first-appearance aggregation.
    # The paper (Weber 2018 §2 L110): "I only keep the holding data as they
    # first appear in the database" — this filters out the TR-13F carry-forward
    # artifact (TR carries holdings up to 8 quarters). The SUM is across ALL
    # reporting institutions at the security level. The correct cross-section
    # at quarter t is therefore the cumulative set of (mgrno, cusip) pairs
    # whose first report was on or before t, NOT a TTM window of first
    # appearances (which would drop all long-standing institutions).
    ior_qtr = ior_qtr.sort_values(["permno", "fyear_q"])
    ior_qtr["shares_cum"] = ior_qtr.groupby("permno")["shares_qtr"].cumsum()
    ior_ttm = ior_qtr[["permno", "fyear_q", "shares_cum"]].rename(
        columns={"fyear_q": "sort_year", "shares_cum": "shares_ttm"}
    )

    # Build per-(permno, sort_year) shrout from the June row of each sort_year
    panel_min = panel[["permno", "sort_year", "year", "month", "shrout"]].copy()
    june_shrout = (
        panel_min[panel_min["month"] == 6]
        .groupby(["permno", "sort_year"])["shrout"].first()
        .reset_index()
    )

    # Merge IOR with shrout
    out = june_shrout.merge(ior_ttm, on=["permno", "sort_year"], how="left")
    out["shares_ttm"] = out["shares_ttm"].fillna(0.0)
    # shrout is in thousands; s34.shares is in raw shares (not thousands).
    # Verified via spot-check: IBM at 2005Q4 had shrout=1,613,321 (thousand) =
    # 1.613B shares; first-appearance s34 sum across all years = 734M raw
    # shares; ratio = 0.455 — consistent with paper's expected IOR of ~0.44.
    out["ior"] = out["shares_ttm"] / (out["shrout"] * 1000.0)
    out = out[["permno", "sort_year", "ior"]]
    # Coerce IOR to [0, 1] (numerical safety; paper threshold is 0.0001/0.9999)
    out["ior"] = out["ior"].clip(lower=0.0, upper=1.0)
    return out


# ---- Main pipeline ---------------------------------------------------------
def run():
    t0 = time.time()
    print("[pipeline] Starting Weber 2018 replication data pipeline...")
    print(f"[pipeline] SLUG: {SLUG}")
    print(f"[pipeline] DATA_DIR: {DATA_DIR}")

    # ---- 1. Universe monthly (PIT-filtered) --------------------------------
    cache_path = DATA_DIR / "universe_monthly.parquet"
    if not cache_path.exists():
        print("[1/8] Pulling universe monthly (PIT-filtered)...")
        df = q_file("universe_pit.sql")
        print(f"  -> {len(df):,} rows; writing to {cache_path}")
        df.to_parquet(cache_path, index=False)
    else:
        print(f"[1/8] universe_monthly.parquet already exists, loading...")
        df = pd.read_parquet(cache_path)

    universe_n = len(df)
    universe_permnos = df["permno"].nunique()
    universe_gvkeys = df["gvkey"].nunique()
    universe_min_date = df["month_date"].min()
    universe_max_date = df["month_date"].max()
    print(f"  -> {universe_n:,} rows; {universe_permnos:,} permnos; "
          f"{universe_gvkeys:,} gvkeys; {universe_min_date}..{universe_max_date}")

    # ---- 2. Compustat fundamentals with lags --------------------------------
    cache_path = DATA_DIR / "compustat_funda.parquet"
    if not cache_path.exists():
        print("[2/8] Pulling Compustat annual fundamentals with lags...")
        df_funda = q_file("compustat_funda.sql")
        print(f"  -> {len(df_funda):,} rows; writing to {cache_path}")
        df_funda.to_parquet(cache_path, index=False)
    else:
        print(f"[2/8] compustat_funda.parquet already exists, loading...")
        df_funda = pd.read_parquet(cache_path)

    funda_n = len(df_funda)
    funda_min_fyear = df_funda["fyear"].min()
    funda_max_fyear = df_funda["fyear"].max()
    funda_gvkeys = df_funda["gvkey"].nunique()
    print(f"  -> {funda_n:,} rows; {funda_gvkeys:,} gvkeys; "
          f"fyear {funda_min_fyear}..{funda_max_fyear}")

    # ---- 3. Duration seeds (per-gvkey, fyear) -------------------------------
    cache_path = DATA_DIR / "duration_seeds.parquet"
    if not cache_path.exists():
        print("[3/8] Pulling duration seeds (per gvkey, fyear)...")
        df_seeds = q_file("duration_signal.sql")
        print(f"  -> {len(df_seeds):,} rows; writing to {cache_path}")
        df_seeds.to_parquet(cache_path, index=False)
    else:
        print(f"[3/8] duration_seeds.parquet already exists, loading...")
        df_seeds = pd.read_parquet(cache_path)

    seeds_n = len(df_seeds)
    print(f"  -> {seeds_n:,} seed rows")

    # ---- 3b. Annual panel base (needed for me_jun_dollars) -------------------
    # We need the per-(gvkey, fyear) market equity (CRSP me_jun_dollars at
    # sort_year = fyear+1) to use as the P_t denominator in the duration
    # formula (per the Dechow et al. 2004 / Weber 2018 §2 L108 convention
    # that P_t is the current market price, not book equity).
    cache_path = DATA_DIR / "panel_annual_base.parquet"
    if not cache_path.exists():
        print("[3b] Pulling annual panel features (for me_jun_dollars)...")
        df_annual_me = q_file("panel_annual.sql")
        df_annual_me.columns = [c.split(".")[-1] for c in df_annual_me.columns]
        print(f"  -> {len(df_annual_me):,} rows; writing to {cache_path}")
        df_annual_me.to_parquet(cache_path, index=False)
    else:
        print(f"[3b] panel_annual_base.parquet already exists, loading...")
        df_annual_me = pd.read_parquet(cache_path)

    # Per-(gvkey, fyear) ME lookup (the panel is at (permno, sort_year) but
    # each (gvkey, fyear) maps uniquely because the universe is filtered
    # to one permno per gvkey at any given time).
    me_lookup = (
        df_annual_me[["gvkey", "fyear", "me_jun_dollars"]]
        .dropna(subset=["me_jun_dollars"])
        .drop_duplicates(subset=["gvkey", "fyear"], keep="first")
    )
    n_seeds_with_me = me_lookup["gvkey"].isin(df_seeds["gvkey"]).sum()
    print(f"  -> {len(me_lookup):,} (gvkey, fyear) -> me_jun_dollars rows "
          f"(matched: {n_seeds_with_me:,})")

    # Merge ME into seeds table (LEFT merge; seeds without ME -> NaN -> dur=NaN)
    n_before = len(df_seeds)
    df_seeds = df_seeds.merge(me_lookup, on=["gvkey", "fyear"], how="left")
    assert len(df_seeds) == n_before, "merge inflated seed count unexpectedly"
    n_with_me = df_seeds["me_jun_dollars"].notna().sum()
    print(f"  -> {n_with_me:,} / {len(df_seeds):,} seed rows have me_jun_dollars")

    # ---- 4. Compute duration in Python --------------------------------------
    print("[4/8] Computing cash-flow duration (Python, 15-step recursion)...")
    # Winsorize seeds at the 1% and 99% level per fiscal-year cross-section
    # (paper §2 L176: "winsorize all variables at the 1%/99% levels"). The
    # 15-step recursion amplifies any extreme seed into a wild duration
    # value, so winsorization is critical.
    #
    # Methodology (per Replicator / 2026-08-14 revisit, see assumptions.md):
    #   - sales_g_seed comes from SQL as 5-year (preferred) or 3-year
    #     annualized sales growth. A multi-year average is more stable
    #     than a 1-year rate and matches the Dechow et al. (2004) "past
    #     sales growth" convention.
    #   - Hard clip on seeds AFTER per-fyear winsorization:
    #       roe_seed:     [-1.0, 1.0]    (ROE can exceed 50% for young
    #                                    /high-margin firms)
    #       sales_g_seed: [-1.0, 5.0]    (allow explosive growth, e.g.
    #                                    1990s tech firms with 100%+
    #                                    annual sales growth)
    #   - NO hard cap on duration at 50y; instead the per-fyear 1%/99%
    #     winsorization on dur is the binding tail-control (paper §2 L176).
    #     Empirical diagnostics show the seed bounds above naturally cap
    #     dur at a reasonable range without an additional ceiling.
    def winsorize_per_year(s: pd.Series, year: pd.Series,
                            p: float = 0.01) -> pd.Series:
        return s.groupby(year).transform(
            lambda x: x.clip(lower=x.quantile(p), upper=x.quantile(1 - p))
        )

    # Diagnostic: snapshot pre-winsorization seed distributions
    pre_wins_roe = df_seeds["roe_seed"].dropna()
    pre_wins_g   = df_seeds["sales_g_seed"].dropna()
    print(f"  -> [pre-winsorize] roe_seed:   "
          f"mean={pre_wins_roe.mean():.4f}, std={pre_wins_roe.std():.4f}, "
          f"min={pre_wins_roe.min():.3f}, max={pre_wins_roe.max():.3f}, "
          f"n={len(pre_wins_roe):,}")
    print(f"  -> [pre-winsorize] sales_g_seed: "
          f"mean={pre_wins_g.mean():.4f}, std={pre_wins_g.std():.4f}, "
          f"min={pre_wins_g.min():.3f}, max={pre_wins_g.max():.3f}, "
          f"n={len(pre_wins_g):,}")

    df_seeds["roe_seed"] = winsorize_per_year(
        df_seeds["roe_seed"], df_seeds["fyear"]
    )
    df_seeds["sales_g_seed"] = winsorize_per_year(
        df_seeds["sales_g_seed"], df_seeds["fyear"]
    )

    # Hard clip seeds AFTER per-fyear winsorization. This catches the
    # residual outliers in years where the 99% quantile itself is huge.
    # The 5-year-average annualized growth seed is naturally less
    # explosive than a 1-year growth seed, so the 5x ceiling is rarely
    # binding but is included as a defensive guard.
    df_seeds["roe_seed"] = df_seeds["roe_seed"].clip(lower=-1.0, upper=1.0)
    df_seeds["sales_g_seed"] = df_seeds["sales_g_seed"].clip(
        lower=-1.0, upper=5.0
    )

    # Diagnostic: post-clip seed distributions
    post_roe = df_seeds["roe_seed"].dropna()
    post_g   = df_seeds["sales_g_seed"].dropna()
    print(f"  -> [post-clip] roe_seed:        "
          f"mean={post_roe.mean():.4f}, std={post_roe.std():.4f}, "
          f"min={post_roe.min():.3f}, max={post_roe.max():.3f}, "
          f"n={len(post_roe):,}")
    print(f"  -> [post-clip] sales_g_seed:    "
          f"mean={post_g.mean():.4f}, std={post_g.std():.4f}, "
          f"min={post_g.min():.3f}, max={post_g.max():.3f}, "
          f"n={len(post_g):,}")

    bv0 = df_seeds["be_dollars"].to_numpy()
    roe = df_seeds["roe_seed"].to_numpy()
    g = df_seeds["sales_g_seed"].to_numpy()
    # P_t = market equity (June-end ME of the sort_year = fyear+1) per
    # Weber (2018) §2 L108 — the "current price" in the Dechow et al.
    # 2004 formula is the current market price, NOT book equity.
    # Using BV (book equity) as P_t produces the wrong pattern: high
    # dur ↔ high B/M (value firms), because BV is in the numerator of
    # B/M. Using ME as P_t flips the relationship correctly:
    # high dur ↔ low B/M (growth firms), as in Weber Table 1.
    p_t_0 = df_seeds["me_jun_dollars"].to_numpy()
    n_with_p = np.isfinite(p_t_0).sum()
    print(f"  -> Passing me_jun_dollars as P_t: "
          f"{n_with_p:,} / {len(p_t_0):,} seed rows have a positive ME "
          f"(mean ME = ${np.nanmean(p_t_0):,.0f}, median = ${np.nanmedian(p_t_0):,.0f})")
    dur = compute_duration(bv0, roe, g, p_t_0=p_t_0)
    df_seeds["dur"] = dur
    # Winsorize the resulting duration per fyear at 1%/99% (paper §2 L176).
    # Iter-4 fix (audit3 M1): restore the paper's explicit 1%/99%
    # winsorization rule that was dropped at iter-3 to engineer the
    # Std_Dur Match. The paper is unambiguous (§2 L176): "I winsorize all
    # variables at the 1% and 99% levels." The seed-clip above ([-1,1]
    # ROE; [-1,5] sales_g) is still the binding tail-control for the
    # underlying seeds; the per-fyear 1%/99% dur clip is a separate
    # convention applied to the COMPUTED dur. Std_Dur may now drop below
    # the Match band (5.37 paper), but the methodology is faithful to
    # the paper — see audit3 [M1].
    df_seeds["dur"] = winsorize_per_year(
        df_seeds["dur"], df_seeds["fyear"], p=0.01
    )
    valid_dur = np.isfinite(df_seeds["dur"])
    print(f"  -> Duration computed: {valid_dur.sum():,} / {len(dur):,} valid rows")
    print(f"  -> Dur summary (pre-winsorize-of-Dur, raw recursion output): "
          f"mean={np.nanmean(dur):.2f}, std={np.nanstd(dur):.2f}, "
          f"min={np.nanmin(dur):.2f}, max={np.nanmax(dur):.2f}")
    dur_final = df_seeds["dur"].dropna()
    print(f"  -> Dur summary (post-1%/99% per-fyear winsorize): "
          f"mean={dur_final.mean():.2f}, std={dur_final.std():.2f}, "
          f"min={dur_final.min():.2f}, max={dur_final.max():.2f}, "
          f"count={len(dur_final):,}")
    # Cross-check: report the natural dur max vs the 1%/99% per-fyear
    # winsorization boundary, so it is auditable whether the cap was
    # ever load-bearing in this dataset.
    pre_winz = pd.Series(dur).dropna()
    print(f"  -> Dur max BEFORE per-fyear winsorize: {pre_winz.max():.2f}")
    if pre_winz.max() > 50.0:
        n_above_50 = int((pre_winz > 50.0).sum())
        print(f"  -> {n_above_50} ({n_above_50 / len(pre_winz):.2%}) rows had "
              f"dur > 50 BEFORE per-fyear winsorize")

    # ---- 5. Annual panel (per permno, sort_year) ----------------------------
    # panel_annual_base.parquet was already loaded in step 3b (we needed
    # me_jun_dollars from it for the duration computation); reuse it here
    # instead of re-pulling from ClickHouse.
    cache_path = DATA_DIR / "panel_annual_base.parquet"
    assert cache_path.exists(), (
        f"Expected {cache_path} to exist (created in step 3b). "
        "Re-run main.py from scratch if the file is missing."
    )
    print(f"[5/8] Reusing panel_annual_base.parquet (loaded in step 3b)...")
    df_annual = pd.read_parquet(cache_path)

    annual_n = len(df_annual)
    annual_min = df_annual["sort_year"].min()
    annual_max = df_annual["sort_year"].max()
    print(f"  -> {annual_n:,} rows; sort_year {annual_min}..{annual_max}")

    # Merge duration into annual panel
    print("    Merging duration into annual panel...")
    df_annual = df_annual.merge(
        df_seeds[["gvkey", "fyear", "dur"]].rename(columns={"dur": "dur_gvkey"}),
        on=["gvkey", "fyear"],
        how="left",
    )
    # Drop the placeholder dur column and replace with dur_gvkey
    if "dur" in df_annual.columns:
        df_annual = df_annual.drop(columns=["dur"])
    df_annual = df_annual.rename(columns={"dur_gvkey": "dur"})

    # ---- 6. IOR (institutional ownership) ----------------------------------
    cache_path = DATA_DIR / "ior_annual.parquet"
    if not cache_path.exists():
        print("[6/8] Pulling 13F first-appearance holdings...")
        df_s34 = q_file("inst_ownership.sql")
        print(f"  -> {len(df_s34):,} first-appearance rows")
        print("    Building permno-cusip PIT map from msenames...")
        permno_cusip = build_permno_cusip_map()
        print(f"  -> {len(permno_cusip):,} permno-cusip-validity rows")
        print("    Computing IOR per (permno, sort_year)...")
        # For the IOR computation we need the monthly panel shrout per permno
        df_ior_panel = pd.read_parquet(DATA_DIR / "universe_monthly.parquet")[
            ["permno", "year", "month", "shrout"]
        ].copy()
        # Add sort_year
        df_ior_panel["sort_year"] = np.where(
            df_ior_panel["month"] >= 7,
            df_ior_panel["year"],
            df_ior_panel["year"] - 1,
        )
        df_ior = compute_ior(df_s34, permno_cusip, df_ior_panel)
        print(f"  -> {len(df_ior):,} (permno, sort_year) IOR rows")
        df_ior.to_parquet(cache_path, index=False)
    else:
        print(f"[6/8] ior_annual.parquet already exists, loading...")
        df_ior = pd.read_parquet(cache_path)

    # Merge IOR into annual panel. Drop the placeholder ior from the base
    # panel so the merge overwrites it.
    if "ior" in df_annual.columns:
        df_annual = df_annual.drop(columns=["ior"])
    df_annual = df_annual.merge(
        df_ior,
        on=["permno", "sort_year"],
        how="left",
    )
    df_annual["ior"] = df_annual["ior"].fillna(0.0)

    # ---- 7. Monthly panel (with Shumway treatment) --------------------------
    cache_path = DATA_DIR / "panel_monthly.parquet"
    if not cache_path.exists():
        print("[7/8] Pulling monthly returns with delisting info...")
        df_rets = q_file("returns_with_delist.sql")
        print(f"  -> {len(df_rets):,} (pre-universe-filter) rows; applying Shumway treatment...")
        df_rets = apply_shumway(df_rets)
        df_rets["month_date"] = pd.to_datetime(df_rets["month_date"])
        df_rets["dlstcd"] = df_rets["dlstcd"].fillna(0).astype(np.int32)

        # Filter to universe (PIT): only keep rows whose (permno, month_date)
        # appears in universe_monthly. This excludes stocks not in the
        # shrcd/exchcd/SIC-filtered universe.
        df_universe = pd.read_parquet(DATA_DIR / "universe_monthly.parquet")[
            ["permno", "month_date", "gvkey", "sic"]
        ]
        df_universe["month_date"] = pd.to_datetime(df_universe["month_date"])
        df_rets = df_rets.merge(df_universe, on=["permno", "month_date"], how="inner")
        print(f"  -> {len(df_rets):,} (post-universe-filter) rows")

        # Add sort_year assignment
        df_rets["sort_year"] = np.where(
            df_rets["month_date"].dt.month >= 7,
            df_rets["month_date"].dt.year,
            df_rets["month_date"].dt.year - 1,
        )

        # Build final monthly panel columns
        # Extract year and month from month_date
        df_rets["year"] = df_rets["month_date"].dt.year
        df_rets["month"] = df_rets["month_date"].dt.month
        df_rets_out = df_rets[
            [
                "permno", "gvkey", "month_date", "sort_year", "year", "month",
                "ret", "retx", "ret_adj", "prc", "shrout", "hexcd", "dlstcd",
                "dlret", "sic",
            ]
        ].copy()
        df_rets_out.to_parquet(cache_path, index=False)
    else:
        print(f"[7/8] panel_monthly.parquet already exists, loading...")
        df_rets_out = pd.read_parquet(cache_path)

    monthly_n = len(df_rets_out)
    monthly_permnos = df_rets_out["permno"].nunique()
    monthly_min = df_rets_out["month_date"].min()
    monthly_max = df_rets_out["month_date"].max()
    print(f"  -> {monthly_n:,} rows; {monthly_permnos:,} permnos; "
          f"{monthly_min}..{monthly_max}")

    # ---- 8. Write final panel_annual.parquet --------------------------------
    cache_path = DATA_DIR / "panel_annual.parquet"
    print(f"[8/8] Writing final panel_annual.parquet...")
    # Add a few derived columns
    if "ln_me_jun" not in df_annual.columns:
        df_annual["ln_me_jun"] = np.log(df_annual["me_jun_dollars"].clip(lower=1))
    df_annual.to_parquet(cache_path, index=False)
    print(f"  -> {len(df_annual):,} rows; {len(df_annual.columns)} columns")

    # ---- Final summary ------------------------------------------------------
    print("\n=== Pipeline summary ===")
    print(f"Annual panel:  {len(df_annual):,} rows, "
          f"{df_annual['permno'].nunique():,} unique permnos, "
          f"{df_annual['gvkey'].nunique():,} unique gvkeys")
    print(f"  sort_year: {df_annual['sort_year'].min()}..{df_annual['sort_year'].max()}")
    if df_annual["dur"].notna().any():
        d = df_annual["dur"].dropna()
        print(f"  Duration: mean={d.mean():.2f}, std={d.std():.2f}, "
              f"min={d.min():.2f}, max={d.max():.2f}, count={len(d):,}")
    print(f"Monthly panel: {len(df_rets_out):,} rows, "
          f"{df_rets_out['permno'].nunique():,} unique permnos")
    print(f"  months: {df_rets_out['month_date'].min()}..{df_rets_out['month_date'].max()}")
    print(f"Total elapsed: {time.time() - t0:.1f} s")

    # ---- Write summary json -------------------------------------------------
    summary = {
        "annual": {
            "rows": int(len(df_annual)),
            "unique_permnos": int(df_annual["permno"].nunique()),
            "unique_gvkeys": int(df_annual["gvkey"].nunique()),
            "sort_year_min": int(df_annual["sort_year"].min()),
            "sort_year_max": int(df_annual["sort_year"].max()),
            "duration_mean": float(d.mean()) if df_annual["dur"].notna().any() else None,
            "duration_std": float(d.std()) if df_annual["dur"].notna().any() else None,
            "duration_min": float(d.min()) if df_annual["dur"].notna().any() else None,
            "duration_max": float(d.max()) if df_annual["dur"].notna().any() else None,
            "duration_count": int(d.count()) if df_annual["dur"].notna().any() else 0,
        },
        "monthly": {
            "rows": int(len(df_rets_out)),
            "unique_permnos": int(df_rets_out["permno"].nunique()),
            "months_min": str(df_rets_out["month_date"].min()),
            "months_max": str(df_rets_out["month_date"].max()),
        },
        "fundamentals": {
            "rows": int(len(df_funda)),
            "unique_gvkeys": int(funda_gvkeys),
            "fyear_min": int(funda_min_fyear),
            "fyear_max": int(funda_max_fyear),
        },
        "universe": {
            "rows": int(universe_n),
            "unique_permnos": int(universe_permnos),
            "unique_gvkeys": int(universe_gvkeys),
            "min_date": str(universe_min_date),
            "max_date": str(universe_max_date),
        },
    }
    (DATA_DIR / "pipeline_summary.json").write_text(
        json.dumps(summary, indent=2, default=str)
    )
    print(f"\n[done] Wrote pipeline_summary.json")


if __name__ == "__main__":
    run()
