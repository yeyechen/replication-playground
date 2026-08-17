"""
Audit1 [M1] diagnosis: empirically test the [VINTAGE-DRIFT] story for the D9/D10
tail FAIL cluster.

The audit retired the D9/D10 fail cluster (ff4_alpha_D10 -0.070 vs +0.149,
ff5_alpha_D10 0.010 vs +0.222, mean_D10 0.462 vs 0.32) with a hedged
"[VINTAGE-DRIFT]" attribution and no demonstrated test. This module runs the
cheap, principled test:

  1. Rebuild the fundamentals/duration table with comp_202401.funda (Jan-2024
     vintage) + crsp_202401.ccmxpf_linktable, using the IDENTICAL filters and
     cascade as the canonical comp_202601 pipeline (indfmt='INDL', consol='C',
     popsrc='D', datafmt='STD', fyear 1960-2014, same BE cascade, same CCM link,
     same winsorization). Rebuild June decile sorts + monthly EW returns and
     compare D9/D10 means, D1-D10 spread, ff4/ff5 D10 alphas, and D10 composition
     across vintages.
  2. IBES-covered-subset diagnostic: recompute T2 decile means on the
     IBES-covered intersection (the coverage set from ibes_coverage.sql).

This module does NOT touch the canonical pipeline, data/panel.parquet, or
eval/metrics.json. It imports main.py's stateless math helpers (book_equity,
compute_duration, duration-recursion self-check, portfolio-return/alpha routines)
and re-runs them on a scratch duration table. Outputs go to data/ (scratch
parquets tagged 'vintage_probe_') and a diagnostic report to stdout.
"""
from __future__ import annotations

import sys
import pathlib as _pl

# Import main.py's machinery (stateless helpers only; main() is NOT run).
_THIS = _pl.Path(__file__).resolve().parent
if str(_THIS) not in sys.path:
    sys.path.insert(0, str(_THIS))
_REPO_ROOT = _THIS.parent.parent.parent  # .../rep-it-up (where utils/ lives)
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import main as M  # noqa: E402  (reuse book_equity, compute_duration, load_universe,
                 #  load_factors, compute_table2, compute_table3, q, LAYOUT, etc.)

SQL_DIR = _THIS / "sql"


def load_funda_vintage(funda_db: str, link_db: str) -> pd.DataFrame:
    """Load Compustat fundamentals from an arbitrary vintage, using the IDENTICAL
    filters/cascade as the canonical compustat_funda.sql (re-expressed in
    compustat_funda_vintage.sql with the two DB names templated)."""
    sql = (SQL_DIR / "compustat_funda_vintage.sql").read_text()
    sql = sql.replace("{funda_db}", funda_db).replace("{link_db}", link_db)
    df = M.q(sql)
    df["datadate"] = pd.to_datetime(df["datadate"])
    df["lpermno"] = df["lpermno"].astype("Int64")
    return df.sort_values(["gvkey", "fyear", "datadate"]).reset_index(drop=True)


def build_duration_table(funda: pd.DataFrame, uni: pd.DataFrame) -> pd.DataFrame:
    """Replicate build_panel()'s funda -> dur-table path EXACTLY (book_equity,
    FYE ME match, compute_duration, dedupe, valid-mask) for a given funda vintage.
    `uni` is the canonical crsp_202601 universe (CRSP is PIT and does not drift).
    dedupe keep=last matches main.py L419-420."""
    funda = M.book_equity(funda)

    uni_month = uni[["permno", "month", "me_dollars"]].copy()
    uni_month = uni_month.groupby(["permno", "month"], as_index=False)["me_dollars"].last()

    funda = funda.rename(columns={"lpermno": "permno"})
    funda["month"] = funda["datadate"].dt.to_period("M").dt.to_timestamp()
    funda = funda.merge(uni_month.rename(columns={"me_dollars": "p"}),
                        on=["permno", "month"], how="left")

    funda = M.compute_duration(funda, funda["p"])
    valid = (funda["be"].notna()) & (funda["be"] > 0) & \
            (funda["p"].notna()) & (funda["p"] > 0)
    dur_table = funda[valid].copy()
    dur_table = dur_table.sort_values("datadate").drop_duplicates(
        subset=["permno", "fyear"], keep="last")
    return dur_table


def build_panel_vintage(uni: pd.DataFrame, dur_table: pd.DataFrame) -> pd.DataFrame:
    """Replicate build_panel()'s panel-skeleton + duration-sort path, using a
    scratch duration table (dur_table). CRSP returns and June ME are the canonical
    crsp_202601 values; only the duration decile assignment differs by vintage."""
    panel = M.q_file("panel.sql")
    panel["month"] = pd.to_datetime(panel["month"])
    panel["date"] = pd.to_datetime(panel["date"])

    # delisting adjustment (canonical path)
    delist = M.load_delistings()
    dadj = M.build_delist_adj(delist)
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

    dur = dur_table[["permno", "fyear", "dur", "p"]].copy()
    dur = dur.rename(columns={"dur": "dur_raw"})
    dur["sort_year"] = dur["fyear"] + 1
    dur = dur[dur["sort_year"].between(1963, 2013)]

    def ws(g):
        lo, hi = g["dur_raw"].quantile(0.01), g["dur_raw"].quantile(0.99)
        return g["dur_raw"].clip(lo, hi)
    dur["dur"] = dur.groupby("sort_year", group_keys=False).apply(ws)

    dur["bin"] = dur.groupby("sort_year")["dur"].rank(method="first", pct=True)
    dur["bin"] = np.ceil(dur["bin"] * 10).astype(int).clip(1, 10)

    june_me = uni.copy()
    june_me["month"] = june_me["month"].dt.to_period("M").dt.to_timestamp()
    june = june_me[(june_me["month"].dt.month == 6)]
    june["sort_year"] = june["month"].dt.year
    june = june[["permno", "sort_year", "me_dollars"]].rename(
        columns={"me_dollars": "me_jun"})
    june = june.drop_duplicates(["permno", "sort_year"], keep="last")

    dur = dur.merge(june, on=["permno", "sort_year"], how="left")

    sort_cols = ["permno", "sort_year", "bin", "dur", "dur_raw", "me_jun"]
    panel = panel.merge(dur[sort_cols], on=["permno", "sort_year"], how="left")

    out_cols = ["permno", "date", "month", "sort_year", "bin", "dur", "dur_raw",
                "ret", "ret_dl", "me_prev", "me_jun"]
    panel = panel[out_cols]
    panel = panel[panel["sort_year"].between(1963, 2013)]
    panel = panel[panel["dur"].notna()]
    return panel, dur  # return dur too for composition (roe/g/be/gvkey keyed by permno+sort_year)


def d10_composition(dur_table: pd.DataFrame, panel: pd.DataFrame) -> dict:
    """D10 composition at the firm-year (formation) level across 1963-2013:
    median me_jun, median BE (millions), share with negative ROE, median age
    (Compustat fiscal-year count as of the sort, matching table1.py's definition)."""
    # dur_table has one row per (permno, sort_year) after dedup; map to its decile.
    d = dur_table[["permno", "fyear", "gvkey", "be", "roe", "p", "dur"]].copy()
    d = d.rename(columns={"dur": "dur_raw"})
    d["sort_year"] = d["fyear"] + 1
    d = d[d["sort_year"].between(1963, 2013)]
    # winsorized dur + decile (same 1%/99% then decile rank as build_panel_vintage)
    d["dur_w"] = d.groupby("sort_year")["dur_raw"].transform(
        lambda s: s.clip(s.quantile(0.01), s.quantile(0.99)))
    d["decile"] = d.groupby("sort_year")["dur_w"].rank(method="first", pct=True)
    d["decile"] = np.ceil(d["decile"] * 10).astype(int).clip(1, 10)

    # June ME (millions) for the formation cohort
    june_me = pd.read_parquet(M.LAYOUT.data_path("panel.parquet"),
                              columns=["permno", "sort_year", "me_jun"]) \
               .drop_duplicates(["permno", "sort_year"])
    d = d.merge(june_me, on=["permno", "sort_year"], how="left")

    # age = number of distinct fyear per gvkey up to this fyear (cumcount within gvkey)
    d = d.sort_values(["gvkey", "fyear"])
    d["age"] = d.groupby("gvkey")["fyear"].cumcount() + 1
    d10 = d[d["decile"] == 10]

    be_med = d10["be"].median()          # BE in $M (Compustat native)
    me_med = d10["me_jun"].median() / 1e6  # June ME in $M
    neg_roe = float((d10["roe"] < 0).mean())
    age_med = d10["age"].median()
    n = int(len(d10))
    return {"n": n, "median_me_jun_m": float(me_med), "median_be_m": float(be_med),
            "share_neg_roe": neg_roe, "median_age": float(age_med)}


def run_vintage(funda_db: str, link_db: str, factors: pd.DataFrame,
                uni: pd.DataFrame) -> dict:
    """Full probe for one Compustat vintage. Returns metrics + composition."""
    funda = load_funda_vintage(funda_db, link_db)
    dur_table = build_duration_table(funda, uni)
    panel, dur = build_panel_vintage(uni, dur_table)

    n_firmyrs = int(len(dur_table))
    n_permno = int(dur_table["permno"].nunique())

    t2, ew_ex, spread, _ = M.compute_table2(panel, factors)
    t3 = M.compute_table3(ew_ex, spread, factors)

    comp = d10_composition(dur_table, panel)
    out = {
        "n_firmyear": n_firmyrs, "n_permno": n_permno,
        "mean_D9": t2["mean_D9"], "mean_D10": t2["mean_D10"],
        "mean_D1D10": t2["mean_D1D10"],
        "ff3_alpha_D10": t3["ff3_alpha_D10"],
        "ff4_alpha_D9": t3["ff4_alpha_D9"], "ff4_alpha_D10": t3["ff4_alpha_D10"],
        "ff5_alpha_D9": t3["ff5_alpha_D9"], "ff5_alpha_D10": t3["ff5_alpha_D10"],
        "alpha_capm_D9": t2["alpha_capm_D9"],
        "comp": comp,
    }
    # store scratch parquets (diagnostic only, tagged)
    panel.to_parquet(M.LAYOUT.data_path(f"vintage_probe_panel_{funda_db}.parquet"),
                     index=False)
    dur_table.to_parquet(M.LAYOUT.data_path(f"vintage_probe_dur_{funda_db}.parquet"),
                         index=False)
    return out


def firmyear_added_by_2026(base_202401, base_202601):
    """(permno, fyear) added by the 2026 vintage relative to 2024, by decade."""
    a = set(zip(base_202401["permno"], base_202401["fyear"]))
    b = set(zip(base_202601["permno"], base_202601["fyear"]))
    added = b - a
    if not added:
        return pd.Series(dtype=float)
    s = pd.Series([p for p, _ in added])
    # decade from fyear requires pairing; rebuild a frame
    df = pd.DataFrame(list(added), columns=["permno", "fyear"])
    df["decade"] = (df["fyear"] // 10) * 10
    return df.groupby("decade")["permno"].count()


def ibes_covered_diagnostic(panel_202601, factors, dur_table_202601):
    """Recompute T2 decile means on the IBES-covered intersection.

    Uses ibes_coverage.sql + cusip_map.sql (PIT cusip->permno at June 15 anchor),
    exactly as table8_9.load_coverage does, then re-replicates load_mapping's
    documented approach: re-rank duration deciles WITHIN the covered subset and
    re-pull the covered sub-panel for EW returns. Returns the D9/D10/spread means
    on the covered subset.
    """
    import table8_9 as T
    cm = T.load_cusip_map()
    covered = T.load_coverage(cm)          # (permno, sort_year)
    panel_map, _diag = T.build_covered_mapping(covered)

    # build covered sub-panel: (permno, sort_year) -> covered decile, join panel returns
    cov_decile = panel_map[["permno", "sort_year", "decile"]].rename(
        columns={"decile": "bin"})
    p = panel_202601[["permno", "date", "month", "sort_year", "ret_dl", "me_jun"]].copy()
    p = p.merge(cov_decile, on=["permno", "sort_year"], how="inner")
    # drop sort_years outside the covered window (1982..2009)
    p = p[p["sort_year"].between(1982, 2009)]

    ew = p.groupby(["month", "bin"])["ret_dl"].mean().rename("ew").reset_index()
    w = ew.pivot_table(index="month", columns="bin", values="ew")
    w = w.reindex(columns=range(1, 11))
    w.columns = [f"D{i}" for i in range(1, 11)]

    ex = M._align_excess(w, factors)
    means = ex.mean() * 100.0
    spread = means["D1"] - means["D10"]
    return {
        "cov_mean_D9": float(means["D9"]), "cov_mean_D10": float(means["D10"]),
        "cov_mean_D1D10": float(spread),
        "n_months": int(len(w)),
        "n_covered_permno": int(p["permno"].nunique()),
    }


def main() -> None:
    print("=== vintage_probe.py — audit1 M1 D9/D10 vintage-drift test ===\n", flush=True)
    uni = M.load_universe()
    print(f"universe (crsp_202601): {len(uni)} rows, "
          f"{uni['permno'].nunique()} permnos", flush=True)
    factors = M.load_factors()
    print(f"factors: {len(factors)} rows\n", flush=True)

    base_202601 = None
    dur_202601 = None
    results = {}
    for funda_db, link_db in [("comp_202601", "crsp_202601"),
                              ("comp_202401", "crsp_202401")]:
        print(f"--- rebuilding duration table for {funda_db} + {link_db} ---",
              flush=True)
        r = run_vintage(funda_db, link_db, factors, uni)
        results[funda_db] = r
        print(f"  firm-years: {r['n_firmyear']}  permnos: {r['n_permno']}", flush=True)
        print(f"  D9 mean {r['mean_D9']:.3f}  D10 mean {r['mean_D10']:.3f}  "
              f"spread {r['mean_D1D10']:.3f}",
              flush=True)
        print(f"  ff4_alpha_D10 {r['ff4_alpha_D10']:.3f}  "
              f"ff5_alpha_D10 {r['ff5_alpha_D10']:.3f}",
              flush=True)
        print(f"  D10 comp: n={r['comp']['n']}  median_me_jun={r['comp']['median_me_jun_m']:.1f}M "
              f"median_be={r['comp']['median_be_m']:.1f}M  neg_roe_share={r['comp']['share_neg_roe']:.3f} "
              f"median_age={r['comp']['median_age']:.2f}\n", flush=True)
        # retain firmyear identity for the "added" count
        ft = build_duration_table(load_funda_vintage(funda_db, link_db), uni)
        if funda_db == "comp_202601":
            base_202601 = ft
            dur_202601 = ft
        else:
            added = firmyear_added_by_2026(ft, base_202601)
            print(f"  firm-years ADDED by comp_202601 relative to comp_202401, by decade:")
            if len(added):
                for dec, c in added.items():
                    print(f"    {dec}s: {c}")
            else:
                print("    (none)")
            print()

    # ---- evidence table ----
    print("=" * 70)
    print("EVIDENCE TABLE: canonical (comp_202601) vs old vintage (comp_202401)")
    print("=" * 70)
    hdr = f"{'metric':>24} {'comp_202601':>14} {'comp_202401':>14} {'paper':>10}"
    print(hdr)
    print("-" * len(hdr))
    rows = [
        ("mean_D9", "mean_D9", 0.62),
        ("mean_D10", "mean_D10", 0.32),
        ("mean_D1D10", "mean_D1D10", 1.10),
        ("ff3_alpha_D10", "ff3_alpha_D10", -0.38),
        ("ff4_alpha_D9", "ff4_alpha_D9", 0.18),
        ("ff4_alpha_D10", "ff4_alpha_D10", -0.07),
        ("ff5_alpha_D9", "ff5_alpha_D9", 0.14),
        ("ff5_alpha_D10", "ff5_alpha_D10", 0.01),
    ]
    for label, key, pv in rows:
        print(f"{label:>24} {results['comp_202601'][key]:>14.3f} "
              f"{results['comp_202401'][key]:>14.3f} {pv:>10.2f}")

    print("\n--- D10 composition ---")
    for db in ("comp_202601", "comp_202401"):
        c = results[db]["comp"]
        print(f"{db:>14}: n={c['n']:>5}  med_me_jun={c['median_me_jun_m']:>8.1f}M  "
              f"med_BE={c['median_be_m']:>7.1f}M  neg_roe={c['share_neg_roe']:.3f}  "
              f"med_age={c['median_age']:.2f}")

    print("\n--- IBES-covered-subset diagnostic (T2 means on covered intersection) ---")
    panel_202601 = pd.read_parquet(M.LAYOUT.data_path("panel.parquet"))
    diag = ibes_covered_diagnostic(panel_202601, factors, dur_202601)
    print(f"  covered permnos: {diag['n_covered_permno']}  months: {diag['n_months']}")
    print(f"  covered D9 mean   = {diag['cov_mean_D9']:.3f}   (paper 0.62)")
    print(f"  covered D10 mean  = {diag['cov_mean_D10']:.3f}   (paper 0.32)")
    print(f"  covered spread    = {diag['cov_mean_D1D10']:.3f} (paper 1.10)")

    print("\n=== done ===", flush=True)


if __name__ == "__main__":
    main()
