"""
Replication of Heston & Sadka (2008) "Seasonality in the cross-section of
stock returns" (JFE).
Signal: average returns over lagged formation-month sets (All / Annual /
Nonannual, five lag intervals from year 1 to years 16-20).
Targets: Table 2 (EW decile winner-loser strategies + VW spreads), plus
universe diagnostics (Task A/B of iteration 1).

Paper parameters (preparations/preprocessing_rules.json):
  - universe: NYSE+AMEX common stocks, PIT (rules: universe_exchanges;
    Assumptions 1-2: shrcd 10/11, exchcd 1/2)
  - returns data from 1945-01 (sample_returns_from_1945)
  - strategy/holding period 1965-01..2002-12, 456 months
    (sample_strategy_period_456_months)
  - no $5 price screen (Assumption 3), msedelist delisting-return merge
    (Assumption 4 REVISED), complete formation-window availability
    (Assumption 5), VW by lagged ME (Assumption 6), equal-count deciles
    (Assumption 11), percent reporting (Assumption 12).
"""
# --- imports ---
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from clickhouse_driver import Client

SKILL_ROOT = Path("/home/ra_yeye/.claude/skills/rep-it-up")
sys.path.insert(0, str(SKILL_ROOT))

from utils.env import get_clickhouse_config  # noqa: E402
from utils.paths import paper_layout  # noqa: E402
from utils.data import apply_universe_filter  # noqa: E402
from utils.quantile import assign_quantiles  # noqa: E402
from utils.portfolio import bin_returns  # noqa: E402

# --- configuration (paper-derived; preprocessing_rules.json quotes) ---
SLUG = "heston_sadka_2008_seasonality_in_the_cross_section_of_stock_returns"
LAYOUT = paper_layout(SLUG)
LAYOUT.ensure()
SQL_DIR = LAYOUT.src_path("sql")

RET_START = "1945-01-01"   # sample_returns_from_1945 (L91)
HOLD_START = pd.Period("1965-01", freq="M")  # sample_strategy_period (L91)
HOLD_END = pd.Period("2002-12", freq="M")    # 456 months (L271)
N_BINS = 10                # ten equal-count portfolios (L271)
DECIMALS_RET = 100.0       # Assumption 12: report in percent

# Formation lag sets: lag k = months before holding month t (Task C spec).
LAG_SETS = {
    "y1": {
        "all": list(range(1, 13)),
        "annual": [12],
        "nonannual": list(range(1, 12)),
    },
    "y2_5": {
        "all": list(range(13, 61)),
        "annual": [24, 36, 48, 60],
        "nonannual": [k for k in range(13, 61) if k % 12 != 0],
    },
    "y6_10": {
        "all": list(range(61, 121)),
        "annual": [72, 84, 96, 108, 120],
        "nonannual": [k for k in range(61, 121) if k % 12 != 0],
    },
    "y11_15": {
        "all": list(range(121, 181)),
        "annual": [132, 144, 156, 168, 180],
        "nonannual": [k for k in range(121, 181) if k % 12 != 0],
    },
    "y16_20": {
        "all": list(range(181, 241)),
        "annual": [192, 204, 216, 228, 240],
        "nonannual": [k for k in range(181, 241) if k % 12 != 0],
    },
}

# --- ClickHouse connection ---
_CFG = get_clickhouse_config()


def _client() -> Client:
    return Client(host=_CFG["host"], port=int(_CFG["port"]),
                  user=_CFG["user"], password=_CFG["password"],
                  settings={"max_execution_time": 600})


def q(sql: str) -> pd.DataFrame:
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


def q_file(name: str) -> pd.DataFrame:
    return q((SQL_DIR / name).read_text())


def fetch_data_cached(table: str, columns: list, start: str, end: str,
                      date_col: str) -> pd.DataFrame:
    """fetch_fn for apply_universe_filter (wide-range header pull)."""
    col_list = ", ".join(columns)
    return q(
        f"SELECT {col_list} FROM {table} "
        f"WHERE {date_col} >= '{start}' AND {date_col} <= '{end}' "
        f"SETTINGS max_execution_time = 600, max_rows_to_read = 10000000000"
    )


# --- data loading ---
DLST_PERF_LO, DLST_PERF_HI = 500, 599   # performance-related dlstcd range
DLST_FALLBACK_RET = -0.30               # Assumption 4 (REVISED), NYSE/AMEX


def merge_delisting(raw: pd.DataFrame) -> pd.DataFrame:
    """Assumption 4 (REVISED): merge msedelist onto the msf panel.

    - msf row present in the delisting month and dlret present:
      ret = (1+ret)*(1+dlret)-1  (msf.ret EXCLUDES dlret in this vintage).
    - msf row absent: INSERT the row with ret = dlret.
    - dlret missing and dlstcd in 500-599: dlret_eff = -0.30.
    - dlret missing and not performance-related: drop (msf.ret as-is).
    The (permno, delisting month) pair gets the same dsfhdr PIT
    shrcd(10,11)/exchcd(1,2) filter as the msf rows.
    """
    dl = q_file("delist_merge.sql")
    n_dl_raw = len(dl)
    dl = apply_universe_filter(dl, fetch_data_cached, date_col="dmonth",
                               shrcd_filter=[10, 11],
                               exchcd_filter=[1, 2])
    dl["month"] = pd.to_datetime(dl["dmonth"]).dt.to_period("M")
    dl = (dl.sort_values("dlstcd")
            .drop_duplicates(subset=["permno", "month"], keep="last"))

    dl["dlret"] = pd.to_numeric(dl["dlret"], errors="coerce")
    perf = dl["dlstcd"].between(DLST_PERF_LO, DLST_PERF_HI)
    dl.loc[perf & dl["dlret"].isna(), "dlret"] = DLST_FALLBACK_RET
    dl_use = (dl[dl["dlret"].notna()]
              [["permno", "month", "dlret", "dl_hexcd", "dl_hsiccd"]])

    m = raw.merge(dl_use, on=["permno", "month"], how="outer",
                  indicator=True)
    both = m["_merge"] == "both"
    dl_only = m["_merge"] == "right_only"
    n_adjusted = int((both & m["ret"].notna() & m["dlret"].notna()).sum())
    n_replaced = int((both & m["ret"].isna() & m["dlret"].notna()).sum())

    # msf row present: combine (or dlret alone if msf.ret missing);
    # msf row absent: the inserted row carries dlret as its return
    comb = (1 + m["ret"]) * (1 + m["dlret"]) - 1
    m["ret"] = np.where(m["dlret"].notna(),
                        np.where(both & m["ret"].notna(), comb, m["dlret"]),
                        m["ret"])
    if dl_only.any():
        m.loc[dl_only, "prc"] = np.nan
        m.loc[dl_only, "shrout"] = np.nan
        m.loc[dl_only, "hexcd"] = m.loc[dl_only, "dl_hexcd"]
        m.loc[dl_only, "hsiccd"] = m.loc[dl_only, "dl_hsiccd"]
    n_inserted = int(dl_only.sum())
    m = m.drop(columns=["_merge", "dlret", "dl_hexcd", "dl_hsiccd"])

    print(f"[delist] msedelist rows: {n_dl_raw:,}; after PIT filter: "
          f"{len(dl):,}; combined ret: {n_adjusted:,}; msf.ret-missing "
          f"replaced by dlret: {n_replaced:,}; rows inserted: "
          f"{n_inserted:,}")
    return m


def build_panel() -> pd.DataFrame:
    """Task A: PIT-filtered monthly panel 1945-01..2002-12."""
    raw = q_file("universe_monthly.sql")
    n_raw = len(raw)
    raw = apply_universe_filter(raw, fetch_data_cached,
                                shrcd_filter=[10, 11],
                                exchcd_filter=[1, 2])  # paper rule, not default
    print(f"[panel] raw msf rows: {n_raw:,}; after PIT shrcd(10,11)/"
          f"exchcd(1,2) filter: {len(raw):,}")

    raw["month"] = pd.to_datetime(raw["date"]).dt.to_period("M")
    raw = merge_delisting(raw)
    raw["ret"] = pd.to_numeric(raw["ret"], errors="coerce")
    raw["mcap"] = (raw["prc"].abs() * raw["shrout"] * 1000.0)  # dollars
    raw.loc[raw["prc"].isna(), "mcap"] = np.nan

    panel = (raw[["permno", "month", "ret", "mcap", "hexcd", "hsiccd"]]
             .drop_duplicates(subset=["permno", "month"], keep="first")
             .sort_values(["permno", "month"])
             .reset_index(drop=True))
    panel["mcap_lag1"] = panel.groupby("permno")["mcap"].shift(1)
    return panel


# --- universe diagnostics (Task B) ---
def diagnostics(panel: pd.DataFrame, metrics: dict) -> dict:
    diag = {}
    eligible = panel[panel["ret"].notna()]

    # (a) eligible count Jan 1965 (paper: < 2,000, L91)
    diag["diag_eligible_jan1965"] = int(
        (eligible["month"] == pd.Period("1965-01", "M")).sum())

    # (b) mean/min/max eligible stocks per month, 1965-2002
    cnt = (eligible[(eligible["month"] >= HOLD_START)
                    & (eligible["month"] <= HOLD_END)]
           .groupby("month").size())
    diag["diag_eligible_mean_per_month"] = round(float(cnt.mean()), 1)
    diag["diag_eligible_min_per_month"] = int(cnt.min())
    diag["diag_eligible_max_per_month"] = int(cnt.max())

    # (c) complete-history firm counts (paper: >500 with 20-yr over all
    #     years; >1,000 with 10-yr by 1999, L91)
    R, m_idx, months, permnos, _ = _wide_matrix(panel)
    for anchor, K in [("1985-01", 240), ("1990-01", 240), ("1995-01", 240),
                      ("1999-01", 240), ("2002-01", 240), ("1999-01", 120)]:
        t = m_idx[pd.Period(anchor, freq="M")]
        if t - K + 1 < 0:
            continue
        win = ~np.isnan(R[t - K + 1: t + 1, :])       # True = ret present
        complete = int(win.all(axis=0).sum())
        key = (f"diag_complete_{K}m_{anchor.replace('-', '')}")
        diag[key] = complete

    # (d) delisting diagnostic (Assumption 4)
    diag.update(_delist_diagnostic())

    # (e) msf.hexcd vs dsfhdr PIT exchcd agreement
    diag["diag_hexcd_agreement"] = _hexcd_agreement(panel)

    for k, v in diag.items():
        metrics[k] = {"value": float(v)}
    return diag


def _wide_matrix(panel: pd.DataFrame):
    """month x permno float32 return matrix + {Period: row} index."""
    months = pd.period_range(panel["month"].min(), panel["month"].max(),
                             freq="M")
    permnos = np.sort(panel["permno"].unique())
    m_idx = {m: i for i, m in enumerate(months)}
    p_idx = {p: i for i, p in enumerate(permnos)}
    R = np.full((len(months), len(permnos)), np.nan, dtype=np.float32)
    mi = panel["month"].map(m_idx).to_numpy()
    pi = panel["permno"].map(p_idx).to_numpy()
    mask = ~np.isnan(mi) & ~np.isnan(pi)
    R[mi[mask].astype(int), pi[mask].astype(int)] = panel["ret"].to_numpy(
        )[mask]
    return R, m_idx, months, permnos, p_idx


def _delist_diagnostic() -> dict:
    all_rows = q_file("delist_diagnostic.sql")
    df = all_rows[all_rows["msf_ret"].notna()].copy()
    n = len(df)
    if n == 0:
        return {"diag_delist_n": 0,
                "diag_delist_n_sample": len(all_rows)}
    d = df["dlret"].astype(float)
    r = df["msf_ret"].astype(float)
    combined = (1 + r) * (1 + d) - 1     # total if msf.ret EXCLUDED dlret
    out = {
        "diag_delist_n": n,
        "diag_delist_n_sample": len(all_rows),
        # decisive test: when dlret is a total loss (<= -0.90), an
        # msf.ret that already embeds dlret would itself be near -1
        "diag_delist_n_dlret_le_-0.90": int((d <= -0.90).sum()),
        "diag_delist_frac_msret_gt_-0.99_when_dlret_le_-0.90": round(
            float((r[d <= -0.90] > -0.99).mean()), 3),
        # fraction where the delisting-month msf.ret equals dlret within 1pp
        # (expected if msf.ret already embeds the delisting return)
        "diag_delist_frac_ret_eq_dlret_1pp": round(
            float((r - d).abs().le(0.01).mean()), 3),
        # median |msf.ret - dlret|
        "diag_delist_med_absdiff": round(float((r - d).abs().median()), 4),
        # median msf.ret vs median dlret vs median combined
        "diag_delist_med_msret": round(float(r.median()), 4),
        "diag_delist_med_dlret": round(float(d.median()), 4),
        "diag_delist_med_combined": round(float(combined.median()), 4),
        # median absolute gap between msf.ret and the hypothetical combined
        # total: near 0 => msf.ret EXCLUDES dlret; large => msf.ret is
        # already the total
        "diag_delist_med_absdiff_combined": round(
            float((r - combined).abs().median()), 4),
    }
    # a small sample table for the report
    cols = ["permno", "dlstdt", "dlstcd", "dlret", "msf_date", "msf_ret"]
    print("[delist] sample of delisting-month rows (dlret vs msf.ret):")
    print(df[cols].head(20).to_string(index=False))
    return out


def _hexcd_agreement(panel: pd.DataFrame) -> float:
    hdr = fetch_data_cached(
        table="crsp_202601.dsfhdr",
        columns=["permno", "hexcd", "begdat", "enddat"],
        start="1900-01-01", end="2100-01-01", date_col="begdat")
    hdr["begdat"] = pd.to_datetime(hdr["begdat"])
    hdr["enddat"] = pd.to_datetime(hdr["enddat"])
    p = panel.copy()
    p["dt"] = p["month"].dt.to_timestamp(how="end")
    m = p.merge(hdr[["permno", "hexcd", "begdat", "enddat"]],
                on="permno", how="inner")
    m = m[(m["dt"] >= m["begdat"]) & (m["dt"] <= m["enddat"])]
    agree = (m["hexcd_x"] == m["hexcd_y"]).mean()
    return round(float(agree), 4)


# --- Table 2 (Task C) ---
def table2(panel: pd.DataFrame, metrics: dict,
           series_out: dict | None = None) -> pd.DataFrame:
    """15 strategies x (10 deciles + spread), EW; VW spreads.

    Eligibility (Assumption 5 REVISED, Rule B): a stock enters the
    month-t sort if its month-t return is non-missing AND at least ONE
    formation month in the lag set is available; the signal is the
    average over the AVAILABLE formation months only.

    Returns a tidy frame with columns:
    interval, variant, decile, mean_pct, t_stat, n_months, avg_n_firms.
    If `series_out` is given, fills it with {(interval, variant):
    monthly decile-return pivot (EW and VW columns)} for Table 3.
    """
    R, m_idx, months, permnos, p_idx = _wide_matrix(panel)
    nanmask = np.isnan(R)
    n_months, n_perm = R.shape

    # mcap_lag1 aligned to the wide matrix
    W = np.full_like(R, np.nan, dtype=np.float32)
    mc = panel[["permno", "month", "mcap_lag1"]].dropna(subset=["mcap_lag1"])
    mi = mc["month"].map(m_idx).to_numpy()
    pi = mc["permno"].map(p_idx).to_numpy()
    ok = ~np.isnan(mi) & ~np.isnan(pi)
    W[mi[ok].astype(int), pi[ok].astype(int)] = mc["mcap_lag1"].to_numpy()[ok]

    hold_rows = [i for i, m in enumerate(months)
                 if HOLD_START <= m <= HOLD_END]
    rows = []

    for interval, variants in LAG_SETS.items():
        for variant, lags in variants.items():
            lags = np.asarray(lags, dtype=int)
            # formation average + complete-availability mask, per holding row
            parts = []
            for t in hold_rows:
                cols = t - lags                       # formation row indices
                if cols.min() < 0:
                    continue
                sub = R[cols, :]                       # (n_lags, n_perm)
                avail = ~np.isnan(sub)
                # Rule B (Assumption 5 REVISED): >=1 available formation
                # month; signal = mean over available months only.
                ok_stocks = avail.any(axis=0) & ~nanmask[t, :]
                if not ok_stocks.any():
                    continue
                avg = np.nanmean(sub[:, ok_stocks].astype(np.float64),
                                 axis=0)
                idx = np.where(ok_stocks)[0]
                parts.append(pd.DataFrame({
                    "month": str(months[t]),
                    "permno": permnos[idx],
                    "sig": avg,
                    "ret": R[t, idx].astype(np.float64),
                    "mcap_lag1": W[t, idx].astype(np.float64),
                }))
            long = pd.concat(parts, ignore_index=True)
            long["decile"] = assign_quantiles(long, date_col="month",
                                              signal_col="sig",
                                              n_bins=N_BINS, warn_fallback=False)
            br = bin_returns(long, date_col="month", bin_col="decile",
                             ret_col="ret", mcap_col="mcap_lag1")
            if series_out is not None:
                series_out[(interval, variant)] = br  # monthly decile returns
            avg_n = long.groupby("month").size().mean()

            for d in range(1, N_BINS + 1):
                s = br.loc[br["decile"] == d, "EW"].dropna()
                rows.append(dict(interval=interval, variant=variant,
                                 decile=d, weight="EW",
                                 mean_pct=s.mean() * DECIMALS_RET,
                                 t_stat=_tstat(s), n_months=len(s),
                                 avg_n_firms=avg_n))
            for wcol in ("EW", "VW"):
                piv = br.pivot(index="month", columns="decile", values=wcol)
                spread = (piv[N_BINS] - piv[1]).dropna()
                rows.append(dict(interval=interval, variant=variant,
                                 decile="spread",
                                 mean_pct=spread.mean() * DECIMALS_RET,
                                 t_stat=_tstat(spread), n_months=len(spread),
                                 avg_n_firms=avg_n,
                                 weight=wcol))

            print(f"[t2] {interval} {variant}: avg eligible firms/month = "
                  f"{avg_n:,.0f}")

    res = pd.DataFrame(rows)
    _fill_metrics(res, metrics)
    return res


def _tstat(s: pd.Series) -> float:
    s = s.dropna()
    if len(s) < 2:
        return np.nan
    return float(s.mean() / (s.std(ddof=1) / np.sqrt(len(s))))


def _fill_metrics(res: pd.DataFrame, metrics: dict) -> None:
    """Write flat metric entries matching tables_to_replicate T2 names."""
    def put(name, value, unit):
        if value is not None and not (isinstance(value, float)
                                      and np.isnan(value)):
            metrics[name] = {"value": round(float(value), 4), "unit": unit}

    for _, r in res.iterrows():
        d, w = r["decile"], r.get("weight", "EW")
        if d == "spread":
            if w == "EW":
                name = f"t2_{r['interval']}_{r['variant']}_spread"
                put(name + "", r["mean_pct"], "percent_per_month")
                put(name + "_t", r["t_stat"], "t_stat")
            else:
                put(f"t2_vw_{r['interval']}_{r['variant']}_spread",
                    r["mean_pct"], "percent_per_month")
                put(f"t2_vw_{r['interval']}_{r['variant']}_spread_t",
                    r["t_stat"], "t_stat")
        elif isinstance(d, (int, np.integer)) and w == "EW":
            put(f"t2_{r['interval']}_{r['variant']}_d{int(d)}",
                r["mean_pct"], "percent_per_month")
            put(f"t2_{r['interval']}_{r['variant']}_d{int(d)}_t",
                r["t_stat"], "t_stat")


def write_table2_md(res: pd.DataFrame, diag: dict) -> None:
    lines = ["# Table 2 — Winner-loser strategies, mean monthly returns "
             "(percent), 1965-01 to 2002-12 (456 months)",
             "",
             "Equal-weighted deciles; decile 10 = winners (highest "
             "formation average). t-statistics in brackets "
             "(mean / (std/sqrt(n)), no HAC per Table 2 note).",
             "",
             "| Strategy | Loser 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | "
             "Winner 10 | 10-1 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    label = {"all": "All", "annual": "Annual", "nonannual": "Nonannual"}
    for interval in LAG_SETS:
        for variant in ("all", "annual", "nonannual"):
            sub = res[(res["interval"] == interval) & (res["variant"] == variant)]
            name = f"{interval} {label[variant]}"
            cells = []
            for d in range(1, 11):
                r = sub[(sub["decile"] == d) & (sub["weight"] == "EW")]
                if len(r) == 0:
                    cells.append("—")
                else:
                    r = r.iloc[0]
                    cells.append(f"{r['mean_pct']:.2f} [{r['t_stat']:.2f}]")
            sp = sub[(sub["decile"] == "spread") & (sub["weight"] == "EW")]
            if len(sp):
                r = sp.iloc[0]
                cells.append(f"{r['mean_pct']:.2f} [{r['t_stat']:.2f}]")
            else:
                cells.append("—")
            lines.append(f"| {name} | " + " | ".join(cells) + " |")
    lines += ["", "## Value-weighted 10-1 spreads (weights = mcap_lag1, "
              "Assumption 6)", "",
              "| Strategy | VW 10-1 spread | t |", "|---|---|---|"]
    for interval in LAG_SETS:
        for variant in ("all", "annual", "nonannual"):
            sp = res[(res["interval"] == interval) & (res["variant"] == variant)
                     & (res["decile"] == "spread")
                     & (res["weight"] == "VW")]
            if len(sp):
                r = sp.iloc[0]
                lines.append(f"| {interval} {label[variant]} | "
                             f"{r['mean_pct']:.2f} | {r['t_stat']:.2f} |")
    lines += [
        "",
        "## Note on absent paper cells",
        "The OCR source lost the Table 2 Years 16-20 rows at the page break "
        "(L697-702): only the All-strategy deciles 1-3 are printed; the "
        "Years 16-20 Annual/Nonannual EW decile rows and all decile rows "
        "beyond decile 3 have no committed paper targets. The Years 16-20 "
        "EW Annual/Nonannual spreads and all VW spreads are encoded from "
        "the prose at L253/L257. Values computed above for those cells are "
        "replication-only (no paper comparison).",
        "",
        "## Universe diagnostics (Task B)",
    ]
    for k, v in diag.items():
        lines.append(f"- {k}: {v}")
    (LAYOUT.result_path("table_2.md")).write_text("\n".join(lines) + "\n")


# --- main() ---
def main() -> None:
    metrics = {}
    t2_series = {}                      # (interval, variant) -> monthly br
    panel_path = LAYOUT.data_path("panel.parquet")
    if panel_path.exists():
        panel = pd.read_parquet(panel_path)
        panel["month"] = pd.PeriodIndex(panel["month"], freq="M")
        print(f"[panel] loaded cache: {len(panel):,} rows")
    else:
        panel = build_panel()
        panel.to_parquet(panel_path, index=False)
        print(f"[panel] wrote {panel_path}: {len(panel):,} rows")

    print(f"[panel] months {panel['month'].min()}..{panel['month'].max()}, "
          f"unique permnos {panel['permno'].nunique():,}, "
          f"eligible (ret) rows {panel['ret'].notna().sum():,}")

    diag = diagnostics(panel, metrics)
    print("[diag]", json.dumps(diag, indent=1, default=str))

    res = table2(panel, metrics, series_out=t2_series)
    from table1 import table1, write_table1_md
    t1 = table1(panel, metrics)
    write_table1_md(t1)
    print("[t1] Panel A gamma_1: "
          f"{t1['panA'][1]['est_pct']:.2f} [{t1['panA'][1]['t_nw']:.2f}] "
          f"(paper -5.03 [-9.03]); gamma_12: "
          f"{t1['panA'][12]['est_pct']:.2f} [{t1['panA'][12]['t_nw']:.2f}] "
          f"(paper 2.61 [7.40])")
    out = res.copy()
    out["decile"] = out["decile"].astype(str)   # mixed int/"spread" col
    out.to_parquet(LAYOUT.data_path("table2_results.parquet"), index=False)

    # Table 3: FF3 risk-adjusted returns on the Table 2 portfolios
    from table3 import table3, write_table3_md
    t3_res = table3(t2_series, metrics)
    write_table3_md(t3_res)
    print("[t3] y1 annual spread alpha "
          f"{t3_res[('y1', 'annual')]['spread']['alpha_pct']:.2f} "
          f"[{t3_res[('y1', 'annual')]['spread']['alpha_t']:.2f}] "
          "(paper 1.12 [7.33])")

    # Table 5: strategies within size groups (30/40/30 by mcap_lag1)
    from table5 import table5, write_table5_md
    t5_res, t5_diag = table5(panel, metrics)
    write_table5_md(t5_res, t5_diag)
    print("[t5] tally written to results/table_5.md")

    # Table 7: calendar-month decomposition of the EW 10-1 spreads
    from table7 import table7, write_table7_md
    t7_res = table7(t2_series, metrics)
    write_table7_md(t7_res)
    print("[t7] written to results/table_7.md")

    # Table 4: WRSS profits pi(k) and sigma^2_mu
    from table4 import table4, write_table4_md
    t4_out = table4(panel, metrics)
    write_table4_md(t4_out)
    print("[t4] written to results/table_4.md")

    # Table 6: industry decomposition of the 15 strategies
    from table6 import table6, write_table6_md
    t6_res = table6(panel, metrics)
    write_table6_md(t6_res)
    print("[t6] written to results/table_6.md")

    # Table 8: event-month conditioning (earnings/dividend/ex-div/fy-end)
    from table8 import table8, write_table8_md
    t8_out = table8(panel, metrics)
    write_table8_md(t8_out)
    print("[t8] written to results/table_8.md")

    # Figures (iteration 10): Fig. 2 Panel A replication + strategy PnL
    from plots import make_plots
    make_plots(panel, t2_series)

    LAYOUT.eval_path("metrics.json").parent.mkdir(parents=True, exist_ok=True)
    LAYOUT.eval_path("metrics.json").write_text(json.dumps(
        {"schema_version": 2, "slug": SLUG, "metrics": metrics},
        indent=2, default=float))

    # sanity: no bare scalars
    bad = [k for k, v in metrics.items()
           if not isinstance(v, dict) or "value" not in v]
    assert not bad, f"bare-scalar metrics: {bad}"

    write_table2_md(res, diag)
    print("[done] metrics:", len(metrics), "entries; table_2.md written")


if __name__ == "__main__":
    main()
