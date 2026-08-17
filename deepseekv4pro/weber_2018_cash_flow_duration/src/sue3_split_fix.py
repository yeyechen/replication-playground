"""Split-consistent SUE3 re-derivation (audit-3 [M1]).

Re-derive SUE3 = (actual - meanest) / sigma_analyst on a split-consistent basis.

Mechanism (diagnosed here): the 4.1% tail (|err|>5x|meanest|) in statsum_epsus June
snapshots is driven by REVERSE-SPLIT firms. statsum_epsus.actual is forward-persisted
from a pre-reverse-split per-share basis into the post-reverse-split row, while
meanest is written on the row's current basis. Since a reverse split collapses the
share count, a stale actual carries a wildly wrong magnitude (e.g. ACTC actual
-624M vs meanest -24M; GNTA -5.0M vs -35k). Per-share EPS is economically
meaningless across a reverse split, and the stale persistence is not cleanly
rebasable without the full split schedule.

Fix direction (minimises inconsistency + is defensible): standardise both `actual`
and `meanest` onto a common share basis using the cumulative split factor `adj`
(current-basis EPS = raw / adj, verified on AAPL FY2012: 44.15 / 28 = 1.5768), and
exclude rows where the firm underwent a reverse split (adj < 1 in effect at statpers)
— those are the 4% that dominate the surprise. This is a data-quality screen, not a
fit to the paper.

Run:  python src/sue3_split_fix.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from clickhouse_driver import Client

from utils.env import get_clickhouse_config
from utils.paths import paper_layout

SLUG = "weber_2018_attempt2_deepseek"
LAYOUT = paper_layout(SLUG)
SQL_DIR = LAYOUT.src_path("sql")

T8_START = 1982
T8_END = 2009

_cfg = get_clickhouse_config()

PAPER_SUE3 = {1: 0.038, 2: 0.022, 3: 0.030, 4: 0.018, 5: 0.028,
              6: 0.020, 7: 0.029, 8: 0.014, 9: 0.0, 10: 0.0}


def _client():
    return Client(host=_cfg["host"], port=int(_cfg["port"]), user=_cfg["user"],
                  password=_cfg["password"], database=_cfg["database"],
                  settings={"max_execution_time": 600})


def q(sql):
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


# ------------------------------------------------------------------ #
# Load June snapshots WITH the PIT split factor (adj) attached in SQL
# ------------------------------------------------------------------ #
def load_june_with_factor():
    """June statsum_epsus rows joined to the cumulative split factor `adj` in effect
    at statpers (latest spdates <= statpers for the same cusip). Brings `actual` and
    `meanest` onto the current share basis by dividing by `adj`."""
    return q("""
        WITH june AS (
            SELECT cusip, ticker, fpedats AS fp_str, statpers AS sp_str, fpi,
                   meanest, actual, numest
            FROM ibes_202601.statsum_epsus
            WHERE measure = 'EPS' AND usfirm = 1 AND fpi IN ('6','7','8','9')
              AND fpedats IS NOT NULL AND length(fpedats) >= 8
              AND meanest IS NOT NULL
              AND statpers IS NOT NULL AND length(statpers) >= 8
              AND toMonth(toDate32(statpers)) = 6
              AND toDate32(statpers) BETWEEN toDate32('1981-01-01') AND toDate32('2009-12-31')
        )
        SELECT june.cusip, june.ticker, toDate32(june.fp_str) AS fpedats,
               toDate32(june.sp_str) AS statpers, june.fpi,
               june.meanest, june.actual, june.numest,
               ab.adj
        FROM june
        LEFT JOIN (
            -- latest split factor in effect at statpers: max spdates <= statpers
            SELECT j2.cusip, j2.statpers, a.adj
            FROM (
                SELECT cusip, toDate32(s.statpers) AS statpers,
                       max(toDate32(a.spdates)) AS spd
                FROM ibes_202601.adj a
                CROSS JOIN (
                    SELECT DISTINCT cusip, toDate32(sp_str) AS statpers FROM june
                ) s
                WHERE a.cusip = s.cusip AND a.usfirm = 1
                  AND toDate32(a.spdates) <= s.statpers
                GROUP BY cusip, statpers
            ) j2
            LEFT JOIN ibes_202601.adj a
              ON a.cusip = j2.cusip AND a.usfirm = 1
             AND toDate32(a.spdates) = j2.spd
        ) ab ON ab.cusip = june.cusip AND ab.statpers = toDate32(june.sp_str)
        SETTINGS max_execution_time = 600, max_rows_to_read = 10000000000
    """)


def _analyst_sue(fc):
    f = fc.sort_values(["cusip", "fpedats"]).copy()
    f["_err"] = f["actual"] - f["meanest"]
    f["_sigma"] = f.groupby("cusip")["_err"].transform(
        lambda s: s.shift(1).rolling(8, min_periods=4).std())
    f["_sigma"] = f["_sigma"].where(f["_sigma"] > 1e-8)
    f["_sue"] = f["_err"] / f["_sigma"]
    return f


def _decile_median_ts(sub, mapping):
    sub = sub.merge(mapping[["permno", "sort_year", "decile"]],
                    on=["permno", "sort_year"], how="inner")
    yrs = sub.dropna(subset=["_sue"]).groupby(
        ["sort_year", "decile"])["_sue"].median().reset_index()
    return yrs.groupby("decile")["_sue"].mean()


def _pp(d):
    return {int(k): round(float(v), 4) if pd.notna(v) else None for k, v in d.items()}


def main():
    from sue_eg_diagnostic import load_cusip_map, build_covered_mapping, map_cusip_to_permno

    cm = load_cusip_map()
    panel_map8 = build_covered_mapping(cm)
    print(f"Covered mapping rows: {len(panel_map8)}")

    june = load_june_with_factor()
    june["fpedats"] = pd.to_datetime(june["fpedats"])
    june["statpers"] = pd.to_datetime(june["statpers"])
    june["err"] = june["actual"] - june["meanest"]

    print("=" * 70)
    print("DIAGNOSIS")
    print("=" * 70)
    print(f"June rows: {len(june)}")
    tail = june["err"].abs() > 5 * june["meanest"].abs()
    print(f"tail (|err|>5x|meanest|): {tail.sum()} ({tail.mean()*100:.2f}%)")
    ex = june[tail].sort_values("err").head(6)
    print("\nConcrete reverse-split examples (actual on stale basis):")
    print(ex[["ticker", "cusip", "fpedats", "statpers", "meanest", "actual"]]
          .to_string(index=False))

    # adj factor coverage & reverse-split share
    adjcov = june["adj"].notna().mean() * 100
    print(f"\nadj factor matched: {june['adj'].notna().sum()}/{len(june)} "
          f"({adjcov:.1f}%)")
    rs = june["adj"].notna() & (june["adj"] < 1.0)
    print(f"reverse-split rows (adj<1): {rs.sum()} ({rs.mean()*100:.2f}%)")
    tm = june[rs & tail]
    print(f"tail rows that are reverse-split: {len(tm)} / {tail.sum()} "
          f"({len(tm)/max(tail.sum(),1)*100:.1f}% of tail)")

    # split-consistent standardisation: current basis = raw / adj
    # (only meaningful for forward-split firms where adj >= 1; reverse-split firms
    #  are excluded from SUE3 as per-share EPS is economically meaningless there)
    for screen in ("none", "drop_revsplit"):
        fc = june.drop_duplicates(["cusip", "fpedats"], keep="last").copy()
        # standardise to current basis where adj factor available & >=1
        if screen == "drop_revsplit":
            fc = fc[fc["adj"].isna() | (fc["adj"] >= 1.0)]
            fc["actual"] = np.where(fc["adj"].notna(), fc["actual"] / fc["adj"], fc["actual"])
            fc["meanest"] = np.where(fc["adj"].notna(), fc["meanest"] / fc["adj"], fc["meanest"])
        f = _analyst_sue(fc)
        f = map_cusip_to_permno(f, cm, "fpedats")
        f["sort_year"] = f["fpedats"].dt.year
        f = f[f["sort_year"].between(T8_START, T8_END)]
        ts = _decile_median_ts(f, panel_map8)
        print(f"\nSUE3 [{screen}] D1..D10 (usable {f['_sue'].notna().sum()}):")
        print(f"  ours   {_pp(ts)}")
        print(f"  paper  {PAPER_SUE3}")
        print(f"  spread ours={ts.get(1,0)-ts.get(10,0):.4f} paper=0.038")


if __name__ == "__main__":
    main()
