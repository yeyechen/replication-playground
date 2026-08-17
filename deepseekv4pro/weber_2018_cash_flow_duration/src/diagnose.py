"""
DIAGNOSIS ONLY (iteration 3) — do NOT modify computation logic.
Diagnostic checks A-D for the Weber (2018) EW decile-mean level-shift problem.

Reads the existing data/panel.parquet (+ fundamentals_duration.parquet) and, where
needed, raw ClickHouse. Does NOT write anything to data/ or results/. Purely reports
numbers to stdout for the Replicator.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from clickhouse_driver import Client

from utils.env import get_clickhouse_config
from utils.paths import paper_layout

SLUG = "weber_2018_attempt2_deepseek"
LAYOUT = paper_layout(SLUG)

_CFG = get_clickhouse_config()


def _client() -> Client:
    return Client(
        host=_CFG["host"], port=int(_CFG["port"]),
        user=_CFG["user"], password=_CFG["password"], database=_CFG["database"],
        settings={"max_execution_time": 600},
    )


def q(sql: str) -> pd.DataFrame:
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


BIN_LABELS = [f"D{i}" for i in range(1, 11)]


def load_panel() -> pd.DataFrame:
    p = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
    p["month"] = pd.to_datetime(p["month"])
    p["date"] = pd.to_datetime(p["date"])
    return p


# --------------------------------------------------------------------------- #
# A. EW computation bug check
# --------------------------------------------------------------------------- #
def check_A_ew_bug(panel: pd.DataFrame):
    print("=" * 80)
    print("A. EW COMPUTATION BUG CHECK")
    print("=" * 80)

    # A1: mean(ret_dl) vs mean(1+ret_dl)-1 overall and per bin
    p = panel.copy()
    print("\n[A1] mean(ret_dl) vs mean(1+ret_dl)-1  (overall + per bin)")
    overall_mean = p["ret_dl"].mean()
    overall_compound = (1.0 + p["ret_dl"]).mean() - 1.0
    print(f"  overall: mean(ret_dl)={overall_mean:.6f}  mean(1+ret_dl)-1={overall_compound:.6f}  "
          f"delta={overall_mean - overall_compound:.2e}")
    rows = []
    for b in range(1, 11):
        sub = p[p["bin"] == b]["ret_dl"]
        m1 = sub.mean()
        m2 = (1.0 + sub).mean() - 1.0
        rows.append((b, m1, m2, m1 - m2))
    df = pd.DataFrame(rows, columns=["bin", "mean_ret", "mean_1p_ret-1", "delta"])
    print(df.to_string(index=False, float_format=lambda x: f"{x:.6f}"))

    # A2: panel-wide pooled EW vs dsi.ewretd / vwretd monthly mean
    print("\n[A2] panel pooled EW mean vs CRSP dsi index monthly means (1963-07..2014-06)")
    pooled = p.groupby("month")["ret_dl"].mean()
    pooled_mean = pooled.mean() * 100.0
    idx = q("""
        SELECT toDate32(date) AS dt, ewretd, vwretd
        FROM crsp_202601.dsi
        WHERE toDate32(date) >= toDate32('1963-07-01')
          AND toDate32(date) <= toDate32('2014-06-30')
    """)
    idx["ewretd"] = pd.to_numeric(idx["ewretd"], errors="coerce")
    idx["vwretd"] = pd.to_numeric(idx["vwretd"], errors="coerce")
    print(f"  panel pooled EW mean (dl-adj, %/mo): {pooled_mean:.4f}")
    print(f"  CRSP dsi.ewretd mean (%/mo):        {idx['ewretd'].mean()*100:.4f}")
    print(f"  CRSP dsi.vwretd mean (%/mo):        {idx['vwretd'].mean()*100:.4f}")
    print(f"  panel_POOLED - dsi.ewretd (bps):    {(pooled_mean - idx['ewretd'].mean()*100)*100:.2f}")

    # A3: EW bin-return matrix rows for specific months
    print("\n[A3] EW bin-return matrix rows (raw numbers, D1..D10)")
    for mm in ["1963-07-01", "1964-07-01", "2000-01-01"]:
        sub = p[p["month"] == pd.Timestamp(mm)]
        if sub.empty:
            print(f"  {mm}: (no rows)")
            continue
        ew = sub.groupby("bin")["ret_dl"].mean().reindex(range(1, 11))
        print(f"  {mm}: " + "  ".join(f"{ew.get(b, np.nan): .4f}" for b in range(1, 11)))

    # A4: spot-check 5 random (permno, month) rows vs raw msf.ret
    print("\n[A4] spot-check 5 random panel rows: ret_dl vs raw msf.ret")
    rng = np.random.default_rng(12345)
    sample = panel.sample(5, random_state=12345)
    for _, r in sample.iterrows():
        permno = int(r["permno"])
        d = r["date"]
        raw = q(f"""
            SELECT ret FROM crsp_202601.msf
            WHERE permno = {permno} AND toDate32(date) = toDate32('{d.strftime('%Y-%m-%d')}')
        """)
        raw_ret = raw["ret"].iloc[0] if len(raw) else None
        print(f"  permno={permno} date={d.date()} panel.ret={r['ret']:.6f} "
              f"panel.ret_dl={r['ret_dl']:.6f} raw_msf.ret={raw_ret}")


# --------------------------------------------------------------------------- #
# B. Small-cap anatomy
# --------------------------------------------------------------------------- #
def check_B_smallcap(panel: pd.DataFrame):
    print("=" * 80)
    print("B. SMALL-CAP ANATOMY")
    print("=" * 80)
    p = panel.copy()

    # me_jun is the June formation ME (held constant across cohort). Use it for size terciles.
    # Note: me_jun in dollars. $100M = 1e8.
    print("\n[B5] per-decade EW mean ret_dl by me_jun tercile (small/med/large) within cross-section")
    p["decade"] = p["sort_year"] // 10 * 10
    p["m_tc"] = np.nan
    # tercile within each sort_year cross-section
    def _tercile(g):
        g = g.copy()
        g["m_tc"] = pd.qcut(g["me_jun"].rank(method="first"), 3, labels=["S", "M", "L"])
        return g
    p = p.groupby("sort_year", group_keys=False).apply(_tercile)
    grp = p.groupby(["decade", "m_tc"])["ret_dl"].mean().unstack() * 100.0
    grp = grp[["S", "M", "L"]]
    print(grp.round(3).to_string())

    # B6: distribution of ret by size bucket
    print("\n[B6] ret distribution by me_jun bucket (<$100M vs >=$100M) per decade")
    p["small"] = p["me_jun"] < 1e8
    print("  dec decade: p50/p90/p95/p99/max, count(ret>1), count(ret>0.5)  [small vs big]")
    for dec in p["decade"].dropna().unique():
        dec = int(dec)
        for label, sub in (("small", p[(p["decade"] == dec) & p["small"]]),
                          ("big", p[(p["decade"] == dec) & ~p["small"]])):
            r = sub["ret_dl"].dropna()
            if r.empty:
                print(f"    {dec}s {label}: (no rows)")
                continue
            qs = r.quantile([0.5, 0.9, 0.95, 0.99]).to_dict()
            print(f"    {dec}s {label}: p50={qs[0.5]:.4f} p90={qs[0.9]:.4f} "
                  f"p95={qs[0.95]:.4f} p99={qs[0.99]:.4f} max={r.max():.4f} "
                  f"n_ret>1={(r>1).sum()} n_ret>0.5={(r>0.5).sum()} n={len(r)}")

    # B7: share of panel rows below size thresholds, per decade
    print("\n[B7] share of panel rows with me_jun < $100M / $50M / $25M per decade")
    share = p.groupby("decade").apply(
        lambda g: pd.Series({
            "n_rows": len(g),
            "frac_<100M": (g["me_jun"] < 1e8).mean(),
            "frac_<50M": (g["me_jun"] < 5e7).mean(),
            "frac_<25M": (g["me_jun"] < 2.5e7).mean(),
        }))
    print(share.round(4).to_string())

    # B7b: raw CRSP universe me shares for 1990 and 2000
    print("\n[B7b] raw crsp_202601.msf (all shrcd 10/11, any price) size shares, 1990 & 2000")
    for yr in (1990, 2000):
        raw = q(f"""
            SELECT abs(m.prc) * m.shrout * 1000 AS me_dollars
            FROM crsp_202601.msf AS m
            JOIN crsp_202601.msfhdr AS h ON m.permno = h.permno
             AND toDate32(m.date) >= toDate32(h.begdat)
             AND toDate32(m.date) <= toDate32(h.enddat)
            WHERE toDate32(m.date) >= toDate32('{yr}-01-01')
              AND toDate32(m.date) <= toDate32('{yr}-12-31')
              AND h.hshrcd IN (10,11)
              AND h.hexcd IN (1,2,3)
            SETTINGS join_algorithm='partial_merge', max_execution_time=600
        """)
        me = pd.to_numeric(raw["me_dollars"], errors="coerce").dropna()
        frac = {
            "n": len(me),
            "frac_<100M": (me < 1e8).mean(),
            "frac_<50M": (me < 5e7).mean(),
            "frac_<25M": (me < 2.5e7).mean(),
        }
        print(f"    {yr}: { {k: round(v,4) if isinstance(v,float) else v for k,v in frac.items()} }")


# --------------------------------------------------------------------------- #
# B8/B9 levers (lightweight recompute, no pipeline rebuild)
# --------------------------------------------------------------------------- #
def _ew_bin_returns(panel: pd.DataFrame) -> pd.DataFrame:
    """EW (delisting-adj) mean return per bin per month. Matches _portfolio_returns EW path."""
    ew = panel.groupby(["month", "bin"])["ret_dl"].mean().unstack()
    ew = ew.reindex(columns=range(1, 11))
    ew.columns = BIN_LABELS
    return ew


def check_B8_price_floor(panel: pd.DataFrame):
    print("=" * 80)
    print("B8 / B9. LEVERS (price floor, winsorization)")
    print("=" * 80)
    print("\n[B8] PRICE_FILTER effect on EW decile means + spread")

    # Current panel already has PRICE_FILTER=True ($5 floor). To get the off-floor
    # sample we re-pull the panel join path WITHOUT the $5 floor and recompute EW
    # decile means using the same bin assignment (bins are on Dur, independent of price).
    # Lightweight: re-filter the panel join path (same as panel.sql but no abs(prc)>=5).
    print("  (current panel = PRICE_FILTER ON, $5 floor)")
    ew_on = _ew_bin_returns(panel)
    means_on = ew_on.mean() * 100.0
    spread_on = means_on["D1"] - means_on["D10"]
    print(f"    D1={means_on['D1']:.3f}  D10={means_on['D10']:.3f}  spread={spread_on:.3f} %/mo")

    # Rebuild panel skeleton WITHOUT price floor, then re-merge bin assignment from the
    # existing panel's (permno, sort_year) -> bin/mdur mapping, then recompute EW.
    panel_nf = _load_panel_no_price_floor(panel)
    ew_off = _ew_bin_returns(panel_nf)
    means_off = ew_off.mean() * 100.0
    spread_off = means_off["D1"] - means_off["D10"]
    print(f"    (PRICE_FILTER OFF sample: D1={means_off['D1']:.3f}  D10={means_off['D10']:.3f}  "
          f"spread={spread_off:.3f} %/mo, n_rows={len(panel_nf)})")


def _load_panel_no_price_floor(panel: pd.DataFrame) -> pd.DataFrame:
    """Rebuild the panel skeleton WITHOUT the $5 floor, then attach the existing
    (permno, sort_year) -> bin/dur/dur_raw/me_jun mapping from the current panel, so
    the decile assignment is identical and only the universe screen changes."""
    raw = q("""
        SELECT
            permno,
            toDate32(date) AS date,
            toDate32(formatDateTime(toDate32(date), '%Y-%m-01')) AS month,
            if(toMonth(date) >= 7, toYear(date), toYear(date) - 1) AS sort_year,
            ret, prc, shrout, hsiccd,
            abs(prc) * shrout * 1000 AS me_dollars,
            lagInFrame(abs(prc) * shrout * 1000, 1) OVER w AS me_prev
        FROM (
            SELECT m.permno, toDate32(m.date) AS date, m.ret, m.prc, m.shrout, h.hsiccd AS hsiccd
            FROM crsp_202601.msf AS m
            INNER JOIN crsp_202601.msfhdr AS h
              ON m.permno = h.permno
             AND toDate32(m.date) >= toDate32(h.begdat)
             AND toDate32(m.date) <= toDate32(h.enddat)
            WHERE toDate32(m.date) >= toDate32('1962-07-01')
              AND toDate32(m.date) <= toDate32('2014-06-30')
              AND h.hshrcd IN (10,11)
              AND h.hexcd IN (1,2,3)
              AND (h.hsiccd < 4900 OR h.hsiccd >= 5000)
              AND (h.hsiccd < 6000 OR h.hsiccd >= 7000)
              AND m.ret IS NOT NULL
              AND m.ret > -1.0
        )
        WINDOW w AS (PARTITION BY permno ORDER BY date
                     ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
        SETTINGS join_algorithm='partial_merge', max_execution_time=600,
                 max_rows_to_read=10000000000, timeout_before_checking_execution_speed=0
    """)
    raw["month"] = pd.to_datetime(raw["month"])
    raw["date"] = pd.to_datetime(raw["date"])
    raw["sort_year"] = raw["sort_year"].astype(int)
    # attach existing bin mapping (permno, sort_year) -> bin/dur/dur_raw/me_jun
    meta = panel[["permno", "sort_year", "bin", "dur", "dur_raw", "me_jun"]].drop_duplicates(
        ["permno", "sort_year"])
    raw = raw.merge(meta, on=["permno", "sort_year"], how="left")
    raw = raw[raw["bin"].notna()]
    raw["ret_dl"] = raw["ret"]  # no delisting re-merge for this lightweight lever check
    return raw


def check_B9_winsorization():
    print("\n[B9] winsorization lever: Dur deciles under (a) inputs+Dur winsorized vs (b) Dur only")
    f = pd.read_parquet(LAYOUT.data_path("fundamentals_duration.parquet"))
    # fundamentals_duration stores roe/g AFTER input winsorization (computed in
    # compute_duration), and dur_raw (un-winsorized Dur). We can recompute:
    #  (a) current = input-winsorized roe/g + Dur winsorized  -> already the pipeline.
    #  (b) Dur only = recompute Dur from RAW inputs. But raw inputs aren't stored here
    #      (roe/g here are already winsorized). Report what we can and flag the gap.
    print("  roe stored in fundamentals_duration.parquet:")
    r = pd.to_numeric(f["roe"], errors="coerce")
    g = pd.to_numeric(f["g"], errors="coerce")
    print(f"    roe: n={r.notna().sum()} min={r.min():.4f} p1={r.quantile(.01):.4f} "
          f"p50={r.median():.4f} p99={r.quantile(.99):.4f} max={r.max():.4f}")
    print(f"    g:   n={g.notna().sum()} min={g.min():.4f} p1={g.quantile(.01):.4f} "
          f"p50={g.median():.4f} p99={g.quantile(.99):.4f} max={g.max():.4f}")
    print("  NOTE: roe/g here are ALREADY input-winsorized (main.py clamps before storing).")
    print("  Raw (pre-winsorization) ROE/g are NOT persisted; would need re-pull to run (b).")
    print("  dur_raw distribution (pre-Dur-winsorization):")
    du = pd.to_numeric(f["dur_raw"], errors="coerce").dropna()
    print(f"    dur_raw: n={len(du)} min={du.min():.4f} p1={du.quantile(.01):.4f} "
          f"p50={du.median():.4f} p99={du.quantile(.99):.4f} max={du.max():.4f}")


# --------------------------------------------------------------------------- #
# C. D10 anatomy
# --------------------------------------------------------------------------- #
def check_C_d10_anatomy(panel: pd.DataFrame):
    print("=" * 80)
    print("C. D10 ANATOMY (current pipeline)")
    print("=" * 80)
    p = panel.copy()

    # Need fundamentals (be, age proxy) + age. Panel has dur, me_jun, but not BE/ROE/g.
    # We can join fundamentals_duration.parquet (has be, roe, g) but NOT Age (years in
    # Compustat), and does have permno,fyear. We'll build the sort-year map.
    f = pd.read_parquet(LAYOUT.data_path("fundamentals_duration.parquet"))
    f = f.rename(columns={"dur_raw": "dur_raw_f"})
    f["sort_year"] = f["fyear"] + 1
    # Use fyear's be/roe/g as-of the sort year.
    f = f[["permno", "fyear", "sort_year", "be", "roe", "g"]].drop_duplicates(
        ["permno", "sort_year"], keep="last")

    # Age = number of years a firm has been in Compustat: proxy = (max fyear - min fyear + 1)
    age = f.groupby("permno")["fyear"].agg(["min", "max"])
    age["age"] = age["max"] - age["min"] + 1
    f = f.merge(age[["age"]].reset_index(), on=["permno"], how="left")
    f = f.rename(columns={"age": "age"})

    meta = p.merge(f, on=["permno", "sort_year"], how="left")
    # Dur winsorization cap: recompute p99 per sort_year on dur_raw
    def _p99_hi(g):
        hi = g["dur_raw"].quantile(0.99)
        # fraction at/near cap -> dur_raw >= hi - tiny eps
        near = (g["dur_raw"] >= hi - 1e-9).mean()
        g["dur_at_cap"] = near
        return g
    meta = meta.groupby("sort_year", group_keys=False).apply(_p99_hi)

    print("\n[C10] D1 vs D10 medians for latest sort year (2013) and 2000")
    for yr in (2000, 2013):
        sub = meta[meta["sort_year"] == yr]
        for bname, dset in (("D1", sub[sub["bin"] == 1]), ("D10", sub[sub["bin"] == 10])):
            def _md(x):
                x = pd.to_numeric(x, errors="coerce").dropna()
                return x.median() if len(x) else np.nan
            print(f"  {yr} {bname} (n={len(dset)}): "
                  f"me_jun={_md(dset['me_jun']):.3e} be_mio={_md(dset['be']):.3f} "
                  f"|roe|={_md(dset['roe'].abs()):.4f} sales_g={_md(dset['g']):.4f} "
                  f"age={_md(dset['age']):.1f} dur_at_cap_frac={dset['dur_at_cap'].mean():.3f} "
                  f"be<5M_frac={(dset['be'].dropna() < 5).mean():.3f}")

    # C11: D10 membership stability (churn) around 2000
    print("\n[C11] D10 membership stability (churn) around 2000")
    d10 = {}
    for yr in (1999, 2000, 2001):
        members = set(meta[(meta["sort_year"] == yr) & (meta["bin"] == 10)]["permno"])
        d10[yr] = members
        print(f"  D10 {yr}: n={len(members)}")
    if d10[2000]:
        in_99 = len(d10[2000] & d10[1999]) / len(d10[2000])
        in_01 = len(d10[2000] & d10[2001]) / len(d10[2000])
        print(f"  fraction of D10-2000 also in D10-1999: {in_99:.3f}")
        print(f"  fraction of D10-2000 also in D10-2001: {in_01:.3f}")


# --------------------------------------------------------------------------- #
# D. Delisting sanity
# --------------------------------------------------------------------------- #
def check_D_delisting():
    print("=" * 80)
    print("D. DELISTING SANITY")
    print("=" * 80)
    # D12a: delisting events 400-591 with missing dlret
    ev = q("""
        SELECT
            count() AS n_total,
            countIf(dlstcd >= 400 AND dlstcd <= 591) AS n_cause,
            countIf(dlstcd >= 400 AND dlstcd <= 591
                    AND (dlret IS NULL OR dlret <= -0.40)) AS n_cause_missing_dlret,
            countIf(dlret IS NULL OR dlret <= -0.40) AS n_missing_dlret_any
        FROM crsp_202601.dsedelist
        WHERE toDate32(dlstdt) >= toDate32('1962-07-01')
          AND toDate32(dlstdt) <= toDate32('2014-06-30')
    """)
    for row in ev.itertuples(index=False):
        print("  [D12a] total delistings=%d  cause(400-591)=%d  cause+missing_dlret=%d  "
              "missing_dlret_any=%d" % row)

    # D12b: how many panel permno-months received any delisting adjustment
    # (reconstruct: delisting.sql output -> build_delist_adj -> merge)
    delist = q("""
        SELECT permno, dlstcd, dlret AS dlret_raw,
               multiIf(
                   dlstcd >= 400 AND dlstcd <= 591 AND (dlret IS NULL OR dlret <= -0.40), -0.30,
                   dlret) AS dlret_eff,
               dlpdt, dlstdt, nextdt
        FROM crsp_202601.dsedelist
        WHERE toDate32(dlstdt) >= toDate32('1962-07-01')
          AND toDate32(dlstdt) <= toDate32('2014-06-30')
          AND multiIf(dlstcd >= 400 AND dlstcd <= 591 AND (dlret IS NULL OR dlret <= -0.40),
                      -0.30, dlret) IS NOT NULL
    """)
    print(f"\n  [D12b] delisting.sql-style rows: {len(delist)}")
    # count rows where dlret_eff is the -30% substitution (cause + missing)
    delist["dlret_eff"] = pd.to_numeric(delist["dlret_eff"], errors="coerce")
    substituted = delist[delist["dlret_eff"].round(6) == -0.30]
    print(f"    rows (approx) = -30%% substitution: {len(substituted)}")
    # trace month alignment: how many cause+missing events have dlstdt in MSF coverage
    # (i.e. a last msf row exists)
    sample = substituted.head(20)
    misaligned = 0
    for row in sample.itertuples(index=False):
        last_trade = q(f"""
            SELECT max(toDate32(date)) AS last_d FROM crsp_202601.msf WHERE permno = {int(row.permno)}
        """)
        last_d = last_trade["last_d"].iloc[0]
        dlstdt = pd.to_datetime(row.dlstdt)
        if last_d is None:
            continue
        gap = (dlstdt - last_d).days
        if abs(gap) > 90:
            misaligned += 1
    print(f"    sample of {len(sample)} substituted events: month-alignment check (dlstdt vs "
          f"last msf row), misaligned>{90}d count={misaligned}")


def main() -> None:
    panel = load_panel()
    print(f"Loaded panel: {panel.shape}")
    check_A_ew_bug(panel)
    check_B_smallcap(panel)
    check_B8_price_floor(panel)
    check_B9_winsorization()
    check_C_d10_anatomy(panel)
    check_D_delisting()
    print("\n=== diagnosis complete ===")


if __name__ == "__main__":
    main()
