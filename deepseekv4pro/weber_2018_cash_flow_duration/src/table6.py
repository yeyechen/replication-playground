"""
Table 6 for Weber (2018) — volatility-managed duration portfolios (claim C6).

Implements Moreira & Muir (2017) volatility management applied to the ten
duration-decile portfolios plus the D1-D10 long-short series (11 series total).

Mechanics
---------
Daily portfolio returns (EW): for each sort year the portfolio membership is fixed
through its July-t..June-(t+1) cohort; the daily EW return is the equal-weighted mean
of the members' daily CRSP returns (dsf.ret, missing/sentinel returns skipped).

Realized variance of month t-1 for portfolio i:
    RV_{i,t-1} = sum over trading days d in month t-1 of r_{i,d}^2

Scaled monthly return (Moreira-Muir):
    R_vm_{i,t} = (c_i / RV_{i,t-1}) * R_{i,t}
where R_{i,t} is the delisting-adjusted EW excess return (from the existing panel)
and c_i is chosen so that the scaled series has the same full-sample standard
deviation as the unscaled series:  c_i = std(R_i) / std(R_i / RV_{i,t-1}).

The D1-D10 long-short daily series is (daily D1 - daily D10), and it is
volatility-managed SEPARATELY (its own RV and c), matching the paper's headline
spread values that are NOT the difference of two individually-managed portfolios.

Baseline construction (V0) is UNTOUCHED: this module reads the canonical
panel.parquet (bin/dur/ret_dl) and computes daily EW from the same membership.
"""
from __future__ import annotations

import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from clickhouse_driver import Client

from utils.env import get_clickhouse_config
from utils.paths import paper_layout

SLUG = "weber_2018_attempt2_deepseek"
LAYOUT = paper_layout(SLUG)
SQL_DIR = LAYOUT.src_path("sql")

BIN_LABELS = [f"D{i}" for i in range(1, 11)]
SERIES = BIN_LABELS + ["D1D10"]  # 11 series: 10 deciles + long-short

_CACHED_DAILY = None  # module cache: daily EW returns DataFrame


def _client() -> Client:
    cfg = get_clickhouse_config()
    return Client(host=cfg["host"], port=int(cfg["port"]), user=cfg["user"],
                  password=cfg["password"], database=cfg["database"],
                  settings={"max_execution_time": 600})


def _q(sql: str):
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


def build_daily_ew(panel: pd.DataFrame) -> pd.DataFrame:
    """Daily EW portfolio returns, long (date, bin, ew_ret), bins 1..10.

    Uses a session-scoped ClickHouse TEMPORARY table (t6_members) to carry the
    (permno, sort_year, bin) membership, joins to dsf inside SQL, and returns one
    row per (date, bin). Day labels use the same sort_year = if(month>=7,year,year-1)
    convention as panel.sql.
    """
    members = panel[["permno", "sort_year", "bin"]].drop_duplicates()
    members = members[members["bin"].between(1, 10)].copy()
    members["permno"] = members["permno"].astype("int32")
    members["sort_year"] = members["sort_year"].astype("int32")
    members["bin"] = members["bin"].astype("uint8")

    c = _client()
    try:
        c.execute("DROP TEMPORARY TABLE IF EXISTS t6_members")
        c.execute(
            "CREATE TEMPORARY TABLE t6_members "
            "(permno Int32, sort_year Int32, bin UInt8) ENGINE = Memory"
        )
        c.execute("INSERT INTO t6_members VALUES",
                  [tuple(r) for r in members.itertuples(index=False)])
        sql = (SQL_DIR / "table6_daily.sql").read_text()
        data, cols = c.execute(sql, with_column_types=True)
        daily = pd.DataFrame(data, columns=[x[0] for x in cols])
    finally:
        try:
            c.execute("DROP TEMPORARY TABLE IF EXISTS t6_members")
        except Exception:
            pass
        c.disconnect()

    daily["date"] = pd.to_datetime(daily["date"])
    return daily.sort_values(["date", "bin"]).reset_index(drop=True)


def build_scaled_series(panel: pd.DataFrame, factors: pd.DataFrame,
                        daily: pd.DataFrame) -> dict:
    """Return a dict of month-indexed Series: {'D1': R_vm, ..., 'D1D10': R_vm}."""
    # ---- monthly EW excess returns (from existing panel, ret_dl) ----
    p = panel[["month", "bin", "ret_dl"]].copy()
    ew = p.groupby(["month", "bin"])["ret_dl"].mean().unstack()
    ew = ew.reindex(columns=range(1, 11))
    ew.columns = BIN_LABELS

    ff = factors.set_index("dt")["rf"]
    rf = ff.groupby(ff.index.to_period("M")).last()
    rf.index = rf.index.to_timestamp()
    aligned = ew.join(rf.rename("rf"), how="left")
    for c in BIN_LABELS:
        aligned[c] = aligned[c] - aligned["rf"]
    monthly_excess = aligned[BIN_LABELS].copy()  # decimal, month-indexed
    # long-short raw excess
    monthly_excess["D1D10"] = monthly_excess["D1"] - monthly_excess["D10"]

    # ---- realized variance from daily ----
    daily = daily.copy()
    daily["month"] = daily["date"].dt.to_period("M").dt.to_timestamp()
    # wide daily returns: columns D1..D10 (D1D10 built from D1-D10)
    dw = daily.pivot_table(index="date", columns="bin", values="ew_ret")
    dw = dw.reindex(columns=range(1, 11))
    dw.columns = BIN_LABELS
    dw["D1D10"] = dw["D1"] - dw["D10"]

    # monthly realized variance = sum of squared daily returns within the month
    rv = (dw ** 2).reset_index()
    rv["month"] = rv["date"].dt.to_period("M").dt.to_timestamp()
    rv = rv.drop(columns=["date"]).groupby("month").sum()  # columns = SERIES
    rv = rv.reindex(columns=SERIES)

    # ---- scale each series ----
    out = {}
    for s in SERIES:
        ri = monthly_excess[s].reindex(rv.index)  # align months
        rvi = rv[s]
        valid = ri.notna() & rvi.notna() & (rvi > 0)
        ri = ri[valid]
        rvi = rvi[valid]

        basis = ri / rvi          # R_i / RV_{i,t-1}
        # Moreira-Muir: c selected so scaled series has same full-sample std.
        sd_r = ri.std(ddof=1)
        sd_b = basis.std(ddof=1)
        if sd_r <= 0 or sd_b <= 0 or not np.isfinite(sd_b):
            ci = np.nan
            out[s] = pd.Series(dtype=float)
            continue
        ci = sd_r / sd_b
        scaled = ci * basis
        out[s] = scaled
    return out


def _ols(y: pd.Series, X: pd.DataFrame):
    y = y.dropna()
    Xa = X.reindex(y.index).dropna()
    y = y.reindex(Xa.index)
    Xc = sm.add_constant(Xa)
    m = sm.OLS(y, Xc).fit()
    return float(m.params["const"]), {c: float(m.params[c]) for c in X.columns}


def compute_table6(panel: pd.DataFrame, factors: pd.DataFrame) -> dict:
    global _CACHED_DAILY
    if _CACHED_DAILY is None:
        _CACHED_DAILY = build_daily_ew(panel)
    daily = _CACHED_DAILY

    scaled = build_scaled_series(panel, factors, daily)

    ff = factors.set_index("dt")
    fact_cols = {
        "capm": ["mkt_rf"],
        "ff3": ["mkt_rf", "smb", "hml"],
        "ff4": ["mkt_rf", "smb", "hml", "mom"],
        "ff5": ["mkt_rf", "smb", "hml", "rmw", "cma"],
    }
    factories = {}
    for k, cols in fact_cols.items():
        X = pd.DataFrame({c: ff[c] for c in cols})
        X.index = X.index.to_period("M").to_timestamp()
        factories[k] = X

    res = {}
    for s in SERIES:
        y = scaled[s]
        res[f"vm_mean_{s}"] = float(y.mean() * 100.0) if len(y) else float("nan")
        for tag, X in factories.items():
            a, _ = _ols(y, X)
            key = f"vm_alpha_{tag}_{s}"
            res[key] = float(a * 100.0) if np.isfinite(a) else float("nan")
    return res


def _md_grid(metrics: dict, paper: dict) -> None:
    rows = [
        ("mean (%/mo)", "vm_mean_"),
        ("CAPM alpha (%/mo)", "vm_alpha_capm_"),
        ("FF3 alpha (%/mo)", "vm_alpha_ff3_"),
        ("FF4 alpha (%/mo)", "vm_alpha_ff4_"),
        ("FF5 alpha (%/mo)", "vm_alpha_ff5_"),
    ]
    lines = ["# Table 6 — Weber (2018) volatility-managed portfolios (ours vs paper)",
             "",
             "| Row | " + " | ".join(SERIES) + " |",
             "|---|" + "|".join(["---"] * len(SERIES)) + "|"]
    for label, prefix in rows:
        cells = []
        for c in SERIES:
            key = f"{prefix}{c}"
            o = metrics.get(key)
            pv = paper.get(key)
            o_s = f"{o:.3f}" if o is not None else "—"
            p_s = f"{pv:.3f}" if pv is not None else "—"
            cells.append(f"{o_s} vs {p_s}")
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("Format: `ours vs paper` per cell.")
    LAYOUT.result_path("table_6.md").write_text("\n".join(lines) + "\n")


def load_paper_targets() -> dict:
    doc = json.loads(LAYOUT.preparations_path("tables_to_replicate.json").read_text())
    paper = {}
    for tbl in doc.get("tables", []):
        if tbl.get("id") != "T6":
            continue
        for m in tbl.get("metrics", []):
            paper[m["name"]] = m["value"]
    return paper


def main() -> None:
    panel = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
    panel["month"] = pd.to_datetime(panel["month"])
    panel["date"] = pd.to_datetime(panel["date"])
    factors = _q((SQL_DIR / "ff_factors.sql").read_text())
    factors["dt"] = pd.to_datetime(factors["dt"])

    metrics = compute_table6(panel, factors)
    paper = load_paper_targets()
    _md_grid(metrics, paper)
    print(json.dumps(metrics, indent=2, default=float))
    return metrics


if __name__ == "__main__":
    main()
