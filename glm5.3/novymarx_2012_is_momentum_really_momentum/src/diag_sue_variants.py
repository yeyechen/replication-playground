"""
DIAGNOSTIC ONLY (Iteration 5): SUE denominator disambiguation.

Tests four readings of the paper's ambiguous "scaled by assets" (L2587)
for SUE, holding everything else identical to the committed pipeline:
  BASE   : atq_q                      (current compustat_sue.sql)
  YEARGO : atq_{q-4}
  AVG5   : mean(atq_{q-4..q})
  ANNUAL : AT from the previous completed fiscal year (funda, as-of dd)

Runs Table 14 spec-4 FM (ret on [r127, SUE, r10, ln(me_lag1), log_bm],
monthly 1/99 winsorization, plain FM t, 1973-01..2010-12, slopes x10^2)
for each variant; for the variant closest to the paper's 22.5 [13.8],
also runs specs 2, 6, 8. Nothing is written to eval/metrics.json or the
committed panel; results print to stdout only.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from clickhouse_driver import Client

from utils.env import get_clickhouse_config
from utils.paths import paper_layout
from utils.regressions import fama_macbeth

SLUG = "novymarx_2012_is_momentum_really_momentum"
LAYOUT = paper_layout(SLUG)
SQL_DIR = LAYOUT.src_path("sql")

T8_START = pd.Timestamp("1973-01-31")
T8_END = pd.Timestamp("2010-12-31")
PAPER = {2: (21.9, 13.9), 4: (22.5, 13.8), 6: (23.7, 13.6), 8: (22.7, 13.5)}
SPECS = {  # spec id -> regressors (controls appended)
    2: ["r122", "sue"],
    4: ["r127", "sue"],
    6: ["r62", "sue"],
    8: ["r127", "r62", "sue"],
}
CONTROLS = ["r10", "lnme", "lnbm"]


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


def _winsorize_monthly(s: pd.DataFrame, var: str, pct: float = 0.01) -> pd.Series:
    return s.groupby("month")[var].transform(
        lambda x: x.clip(*x.quantile([pct, 1 - pct])))


def attach_sue(panel: pd.DataFrame, sue_ann: pd.DataFrame,
               var: str) -> pd.DataFrame:
    """Exact replica of main.add_sue, parameterized by the SUE column."""
    sue = sue_ann.dropna(subset=["permno", "avail", var]).copy()
    sue["avail"] = sue["avail"].astype("datetime64[ns]")
    sue = (sue.sort_values(["permno", "avail"])
              .drop_duplicates(["permno", "avail"], keep="last")
              .sort_values("avail"))
    p = panel.sort_values("month")
    m = pd.merge_asof(p[["permno", "month"]], sue[["permno", "avail", var]],
                      left_on="month", right_on="avail", by="permno",
                      direction="backward")
    staleness = ((m["month"].dt.year * 12 + m["month"].dt.month)
                 - (m["avail"].dt.year * 12 + m["avail"].dt.month))
    m[var] = m[var].where(staleness <= 6)
    out = panel.copy()
    out[var] = pd.Series(m[var].to_numpy(), index=p.index).reindex(panel.index)
    return out


def run_spec(d: pd.DataFrame, s_id: int) -> dict:
    cols = SPECS[s_id] + CONTROLS
    s = d[(d["month"] >= T8_START) & (d["month"] <= T8_END)][
        ["permno", "month", "ret"] + cols].copy()
    s = s.replace([np.inf, -np.inf], np.nan).dropna()
    for v in cols:
        s[v + "_w"] = _winsorize_monthly(s, v)
    wc = [v + "_w" for v in cols]
    fm = fama_macbeth(s, dependent_var="ret", independent_vars=wc,
                      time_col="month", winsorize_pct=0.0, n_lags=0)
    n_m = s.groupby("month").size()
    return {"mean": fm.summary["mean"], "t": fm.summary["t_stat"],
            "avg_firms": float(n_m.mean()), "n_months": int(len(n_m))}


def main():
    panel = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
    panel["lnme"] = np.log(panel["me_lag1"])
    panel["lnbm"] = panel["log_bm"]

    v = q_file("compustat_sue_variants.sql")
    v["avail"] = pd.PeriodIndex(v["month"], freq="M").to_timestamp(
        how="end").normalize()
    ann = q_file("compustat_sue_annual.sql")
    ann["avail"] = pd.PeriodIndex(ann["month"], freq="M").to_timestamp(
        how="end").normalize()

    frames = {"BASE": v[["permno", "avail", "sue_base"]].rename(
                  columns={"sue_base": "sue"}),
              "YEARGO": v[["permno", "avail", "sue_yeargo"]].rename(
                  columns={"sue_yeargo": "sue"}),
              "AVG5": v[["permno", "avail", "sue_avg5"]].rename(
                  columns={"sue_avg5": "sue"}),
              "ANNUAL": ann.assign(sue=ann["num"] / ann["den_annual"])[
                  ["permno", "avail", "sue"]]}
    for k, f in frames.items():
        print(f"{k}: {len(f):,} (permno, month) announcement rows")

    # ---- spec-4 under each variant ----
    results = {}
    merged = {}
    for k, f in frames.items():
        p = attach_sue(panel, f[["permno", "avail", "sue"]], "sue")
        merged[k] = p
        r = run_spec(p, 4)
        results[k] = r
        print(f"\n== {k} spec-4 == avg firms/mo {r['avg_firms']:.1f}, "
              f"{r['n_months']} months")
        print(f"  SUE  slope x10^2 = {r['mean']['sue_w']*100:7.2f}  "
              f"t = {r['t']['sue_w']:5.2f}   (paper 22.5 [13.8])")
        print(f"  r127 slope x10^2 = {r['mean']['r127_w']*100:7.2f}  "
              f"t = {r['t']['r127_w']:5.2f}")

    # ---- EXTRA: distributions + correlations (raw merged SUE, sample of
    # spec-4 listwise non-missing firm-months 1973-2010, pre-winsor) ----
    print("\n== SUE distributions (merged firm-month values, spec-4 "
          "listwise sample, pre-winsor) ==")
    sub = panel[(panel["month"] >= T8_START) & (panel["month"] <= T8_END)]
    sub = sub.dropna(subset=["ret", "r127", "r10", "lnme", "lnbm"])
    sue_mat = pd.DataFrame({
        k: m.loc[sub.index, "sue"] for k, m in merged.items()})
    stats = sue_mat.agg(["mean", "std", "count"]).T
    stats["p1"] = sue_mat.quantile(0.01)
    stats["p99"] = sue_mat.quantile(0.99)
    print(stats.round(4).to_string())
    print("\npairwise correlations:")
    print(sue_mat.corr().round(4).to_string())

    # ---- winner: other SUE specs ----
    def dist(k):
        r = results[k]
        return (abs(r["mean"]["sue_w"] * 100 - 22.5), r["avg_firms"])
    winner = min(results, key=dist)
    print(f"\n== winner (closest spec-4 SUE slope to 22.5): {winner} ==")
    p = merged[winner]
    for s_id in (2, 6, 8):
        r = run_spec(p, s_id)
        pp, pt = PAPER[s_id]
        print(f"spec-{s_id}: SUE slope x10^2 = {r['mean']['sue_w']*100:7.2f} "
              f"t = {r['t']['sue_w']:5.2f}  (paper {pp} [{pt}]); "
              f"avg firms/mo {r['avg_firms']:.1f}")


if __name__ == "__main__":
    main()
