"""Table 3 — FF3 risk-adjusted returns (Heston & Sadka 2008, Table 3).

For each of the 15 Table 2 strategies (5 intervals x All/Annual/Nonannual):
time-series OLS of the monthly EW decile return (and the 10-1 spread) in
excess of rf on [MKT-RF, SMB, HML] over the 456 months 1965-01..2002-12.
alpha x 100 (percent/month) and OLS t-statistics (no HAC — the paper's
Table 3 note does not specify HAC; see report).

Additionally: value-weighted ANNUAL and NONANNUAL strategy spreads
(weights = mcap_lag1 within decile, Assumption 6), FF3 alpha of the
VW spread — backs the 4 prose cells t3_vw_<interval>_annual_alpha
(paper L1129: 0.98 / 0.91 / 0.77 / 0.48 percent per month).
"""
import json

import numpy as np
import pandas as pd

from main import q_file, LAYOUT, DECIMALS_RET, N_BINS

LABEL = {"all": "All", "annual": "Annual", "nonannual": "Nonannual"}


def load_ff() -> pd.DataFrame:
    ff = q_file("ff_factors.sql")
    ff["month"] = pd.PeriodIndex(pd.to_datetime(ff["month"]), freq="M")
    for c in ("mkt_rf", "smb", "hml", "rf"):
        ff[c] = pd.to_numeric(ff[c], errors="coerce")
    ff = ff.drop_duplicates(subset="month", keep="first")
    assert len(ff) == 456, f"expected 456 FF months, got {len(ff)}"
    return ff.set_index("month")


def ff3_alpha(ret: pd.Series, ff: pd.DataFrame,
              excess: bool = True) -> dict:
    """OLS of the return on [1, mkt_rf, smb, hml]; alpha, OLS t.

    excess=True  -> long-only decile convention: regress (ret - rf).
    excess=False -> zero-investment spread convention (10-1 column and
    VW spread alphas): regress the RAW spread. rf cancels in the paper's
    difference-of-decile-alphas construction, so subtracting it would
    shift the alpha down by the mean rf (~0.47%/mo) — iteration-6 bug.
    """
    df = pd.concat([ret.rename("ret"), ff], axis=1, join="inner").dropna()
    n = len(df)
    if n < 10:
        return {"alpha_pct": np.nan, "alpha_t": np.nan, "n_months": n}
    y = ((df["ret"] - df["rf"]) if excess else df["ret"]).to_numpy()
    X = np.column_stack([np.ones(n), df["mkt_rf"], df["smb"], df["hml"]])
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    resid = y - X @ beta
    dof = n - X.shape[1]
    s2 = resid @ resid / dof
    se = np.sqrt(np.diag(XtX_inv) * s2)
    return {"alpha_pct": beta[0] * DECIMALS_RET,
            "alpha_t": float(beta[0] / se[0]), "n_months": n}


def table3(t2_series: dict, metrics: dict) -> dict:
    """t2_series: {(interval, variant)} -> br frame (month, decile, EW, VW)."""
    ff = load_ff()
    out = {}
    vw_alphas = {}

    def put(name, value, unit):
        if value is not None and not (isinstance(value, float)
                                      and np.isnan(value)):
            metrics[name] = {"value": round(float(value), 4), "unit": unit}

    for (interval, variant), br in t2_series.items():
        br = br.copy()
        br["month"] = pd.PeriodIndex(pd.to_datetime(br["month"]), freq="M")
        cells = {}
        for wcol, tag in (("EW", ""), ("VW", "vw_")):
            piv = br.pivot(index="month", columns="decile", values=wcol)
            if wcol == "EW":
                for d in range(1, N_BINS + 1):
                    if d in piv.columns:
                        a = ff3_alpha(piv[d], ff)
                        cells[f"d{d}"] = a
                        put(f"t3_{interval}_{variant}_d{d}", a["alpha_pct"],
                            "percent_per_month")
                        put(f"t3_{interval}_{variant}_d{d}_t", a["alpha_t"],
                            "t_stat")
            spread = (piv[N_BINS] - piv[1]).dropna()
            # zero-investment convention: raw spread, no rf subtraction
            a = ff3_alpha(spread, ff, excess=False)
            if wcol == "EW":
                cells["spread"] = a
                put(f"t3_{interval}_{variant}_spread", a["alpha_pct"],
                    "percent_per_month")
                put(f"t3_{interval}_{variant}_spread_t", a["alpha_t"],
                    "t_stat")
            else:
                cells["vw_spread"] = a
                if variant in ("annual", "nonannual"):
                    put(f"t3_vw_{interval}_{variant}_alpha", a["alpha_pct"],
                        "percent_per_month")
        out[(interval, variant)] = cells
    return out


def write_table3_md(t3: dict) -> None:
    spec = json.loads(
        (LAYOUT.preparations_path("tables_to_replicate.json")).read_text())
    paper = {m["name"]: m for tb in spec["tables"] if tb["id"] == "T3"
             for m in tb["metrics"]}
    intervals = ["y1", "y2_5", "y6_10", "y11_15", "y16_20"]
    lines = [
        "# Table 3 — FF3 risk-adjusted returns (alpha, percent/month), "
        "1965-01 to 2002-12",
        "",
        "EW deciles: OLS of (ret - rf) on MKT-RF, SMB, HML; alpha x100 "
        "with OLS t-statistic in brackets. 10-1 spread cells and VW "
        "alphas: RAW spread on the factors (zero-investment; rf cancels). "
        "VW rows: FF3 alpha of the "
        "value-weighted annual/nonannual 10-1 spread (weights mcap_lag1, "
        "Assumption 6). OK/X = within/outside tables_to_replicate "
        "tolerance.",
        "",
        "| Strategy | Loser 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | "
        "Winner 10 | 10-1 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for interval in intervals:
        for variant in ("all", "annual", "nonannual"):
            cells = t3.get((interval, variant), {})
            name = f"{interval} {LABEL[variant]}"
            row = []
            for d in range(1, 11):
                a = cells.get(f"d{d}")
                if a is None:
                    row.append("—")
                else:
                    row.append(f"{a['alpha_pct']:.2f} [{a['alpha_t']:.2f}]"
                               f" (paper "
                               f"{paper.get(f't3_{interval}_{variant}_d{d}', {}).get('value', float('nan')):.2f})")
            a = cells.get("spread")
            if a is None:
                row.append("—")
            else:
                row.append(f"{a['alpha_pct']:.2f} [{a['alpha_t']:.2f}]"
                           f" (paper "
                           f"{paper.get(f't3_{interval}_{variant}_spread', {}).get('value', float('nan')):.2f})")
            lines.append(f"| {name} | " + " | ".join(row) + " |")

    lines += ["", "## Value-weighted FF3 alphas (annual / nonannual spreads)",
              "", "| Strategy | VW annual alpha | paper | VW nonannual "
              "alpha (replication-only) |", "|---|---|---|---|"]
    for interval in intervals:
        ca = t3.get((interval, "annual"), {}).get("vw_spread")
        cn = t3.get((interval, "nonannual"), {}).get("vw_spread")
        pa = paper.get(f"t3_vw_{interval}_annual_alpha", {}).get("value")
        lines.append(
            f"| {interval} | "
            + (f"{ca['alpha_pct']:.2f}" if ca else "—")
            + f" | {pa if pa is not None else '—'} | "
            + (f"{cn['alpha_pct']:.2f}" if cn else "—") + " |")

    (LAYOUT.result_path("table_3.md")).write_text("\n".join(lines) + "\n")
