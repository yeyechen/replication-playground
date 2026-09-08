"""
DIAGNOSTIC ONLY (Iteration 6): PIT (as-first-reported) SUE vintage test.

Question: does replacing the as-restated comp_202601.fundq SUE with a
point-in-time SUE (comp_pit.pithistdataus, each quarter's ibqh/atqh taken
at its own first report) move the spec-4 FM SUE slope toward the paper's
22.5 [13.8]?

Runs the Table-14 spec-4 FM (ret ~ r127 + SUE + r10 + ln(me_lag1) + log_bm,
monthly 1/99 winsorization, plain FM t, slopes x10^2) on the SAME window
1980-01..2010-12 for:
  (a) production as-restated SUE (panel.parquet 'sue', months restricted)
  (b) PIT SUE (src/sql/compustat_sue_pit.sql)
Also reports the 1/99-winsorized correlation between (a) and (b) on the
merged firm-month sample, and coverage shares. Nothing is written to
eval/metrics.json, the committed panel, or results/.
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

WIN_START = pd.Timestamp("1980-01-31")
WIN_END = pd.Timestamp("2010-12-31")
PAPER_SUE = (22.5, 13.8)
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


def attach_sue(panel: pd.DataFrame, sue: pd.DataFrame,
               var: str) -> pd.DataFrame:
    """Exact replica of diag_sue_variants.attach_sue (carry-forward, 6m)."""
    s = sue.dropna(subset=["permno", "avail", var]).copy()
    s["avail"] = s["avail"].astype("datetime64[ns]")
    s = (s.sort_values(["permno", "avail"])
          .drop_duplicates(["permno", "avail"], keep="last")
          .sort_values("avail"))
    p = panel.sort_values("month")
    m = pd.merge_asof(p[["permno", "month"]], s[["permno", "avail", var]],
                      left_on="month", right_on="avail", by="permno",
                      direction="backward")
    staleness = ((m["month"].dt.year * 12 + m["month"].dt.month)
                 - (m["avail"].dt.year * 12 + m["avail"].dt.month))
    m[var] = m[var].where(staleness <= 6)
    out = panel.copy()
    out[var] = pd.Series(m[var].to_numpy(), index=p.index).reindex(panel.index)
    return out


def run_spec4(d: pd.DataFrame, var: str) -> dict:
    cols = ["r127", var] + CONTROLS
    s = d[(d["month"] >= WIN_START) & (d["month"] <= WIN_END)][
        ["permno", "month", "ret"] + cols].copy()
    s = s.replace([np.inf, -np.inf], np.nan).dropna()
    for v in cols:
        s[v + "_w"] = _winsorize_monthly(s, v)
    wc = [v + "_w" for v in cols]
    fm = fama_macbeth(s, dependent_var="ret", independent_vars=wc,
                      time_col="month", winsorize_pct=0.0, n_lags=0)
    n_m = s.groupby("month").size()
    return {"mean": fm.summary["mean"], "t": fm.summary["t_stat"],
            "avg_firms": float(n_m.mean()), "n_months": int(len(n_m)),
            "sample_idx": s.index}


def main():
    panel = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
    panel["lnme"] = np.log(panel["me_lag1"])
    panel["lnbm"] = panel["log_bm"]

    pit = q_file("compustat_sue_pit.sql")
    print(f"PIT announcement rows: {len(pit):,} "
          f"({pit['permno'].nunique()} permnos, "
          f"{pit['month'].min()}..{pit['month'].max()})")

    # (a) production as-restated SUE already attached in panel
    res = {}
    samples = {}
    r = run_spec4(panel, "sue")
    res["(a) as-restated fundq"] = r
    samples["(a)"] = r.pop("sample_idx")

    # (b) PIT SUE
    pit["avail"] = pd.PeriodIndex(pit["month"], freq="M").to_timestamp(
        how="end").normalize()
    p_pit = attach_sue(panel, pit[["permno", "avail", "sue_pit"]], "sue_pit")
    r = run_spec4(p_pit, "sue_pit")
    res["(b) PIT first-report"] = r
    samples["(b)"] = r.pop("sample_idx")

    print(f"\n== spec-4 FM, window {WIN_START.date()}..{WIN_END.date()}, "
          f"slopes x10^2; paper SUE 22.5 [13.8] ==")
    for k, r in res.items():
        v = "sue" if k.startswith("(a)") else "sue_pit"
        print(f"\n{k}: avg firms/mo {r['avg_firms']:.1f}, "
              f"{r['n_months']} months")
        print(f"  SUE  slope x10^2 = {r['mean'][v + '_w'] * 100:7.2f}  "
              f"t = {r['t'][v + '_w']:5.2f}")
        print(f"  r127 slope x10^2 = {r['mean']['r127_w'] * 100:7.2f}  "
              f"t = {r['t']['r127_w']:5.2f}")

    # (a') as-restated SUE restricted to the months where (b) has data
    cols = ["r127", "sue"] + CONTROLS
    pit_months = set(pit["month"])
    s = panel[(panel["month"] >= WIN_START) & (panel["month"] <= WIN_END)]
    s = s[s["month"].dt.strftime("%Y-%m").isin(pit_months)][
        ["permno", "month", "ret"] + cols].copy()
    s = s.replace([np.inf, -np.inf], np.nan).dropna()
    for v in cols:
        s[v + "_w"] = _winsorize_monthly(s, v)
    fm = fama_macbeth(s, dependent_var="ret",
                      independent_vars=[v + "_w" for v in cols],
                      time_col="month", winsorize_pct=0.0, n_lags=0)
    print(f"\n(a') as-restated on (b)'s months "
          f"({s.groupby('month').size().shape[0]} months, "
          f"avg firms/mo {s.groupby('month').size().mean():.1f}):")
    print(f"  SUE  slope x10^2 = {fm.summary['mean']['sue_w'] * 100:7.2f}  "
          f"t = {fm.summary['t_stat']['sue_w']:5.2f}")
    print(f"  r127 slope x10^2 = {fm.summary['mean']['r127_w'] * 100:7.2f}  "
          f"t = {fm.summary['t_stat']['r127_w']:5.2f}")

    # coverage share: firm-months with each SUE among a common base sample
    base = panel[(panel["month"] >= WIN_START) & (panel["month"] <= WIN_END)]
    base = base.dropna(subset=["ret", "r127", "r10", "lnme", "lnbm"])
    print(f"\n== coverage on spec-4 base sample "
          f"({len(base):,} firm-months) ==")
    print(f"  (a) as-restated SUE non-missing: "
          f"{base['sue'].notna().mean():.3f}")
    print(f"  (b) PIT SUE non-missing:        "
          f"{p_pit.loc[base.index, 'sue_pit'].notna().mean():.3f}")

    # correlation of winsorized SUEs on merged (both non-missing) sample
    both = pd.DataFrame({
        "a": base["sue"], "b": p_pit.loc[base.index, "sue_pit"]}
    ).dropna()
    tmp = base.loc[both.index, ["month"]].copy()
    tmp["a"] = both["a"]
    tmp["b"] = both["b"]
    tmp["a_w"] = _winsorize_monthly(tmp, "a")
    tmp["b_w"] = _winsorize_monthly(tmp, "b")
    print(f"\n== merged both-present firm-months: {len(both):,} ==")
    print(f"  corr(raw)          = {tmp['a'].corr(tmp['b']):.4f}")
    print(f"  corr(winsor 1/99)  = {tmp['a_w'].corr(tmp['b_w']):.4f}")


if __name__ == "__main__":
    main()
