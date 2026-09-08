"""Table 7 — calendar-month decomposition (Heston & Sadka 2008, Table 7).

For each of the 15 strategies, take the monthly EW 10-1 spread series
(from Table 2) and report mean + simple t separately for each calendar
month (Jan..Dec) and for the Feb-Dec aggregate. The Difference row =
Annual spread minus Nonannual spread computed month by month, then
averaged by calendar month (t of the difference series).
Units percent/month.
"""
import json

import numpy as np
import pandas as pd

from main import LAYOUT, LAG_SETS, N_BINS, DECIMALS_RET, _tstat

MONTH_ABBR = {1: "jan", 2: "feb", 3: "mar", 4: "apr", 5: "may", 6: "jun",
              7: "jul", 8: "aug", 9: "sep", 10: "oct", 11: "nov", 12: "dec"}
MONTHS = [MONTH_ABBR[m] for m in range(1, 13)]
GROUPS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep",
          "oct", "nov", "dec", "febdec"]
VARIANTS = ["all", "annual", "nonannual", "diff"]
LABEL = {"all": "All", "annual": "Annual", "nonannual": "Nonannual",
         "diff": "Difference"}


def _spread_series(br: pd.DataFrame) -> pd.Series:
    br = br.copy()
    br["month"] = pd.PeriodIndex(pd.to_datetime(br["month"]), freq="M")
    piv = br.pivot(index="month", columns="decile", values="EW")
    return (piv[N_BINS] - piv[1]).dropna()


def table7(t2_series: dict, metrics: dict) -> pd.DataFrame:
    spreads = {k: _spread_series(v) for k, v in t2_series.items()}
    rows = []
    for interval in LAG_SETS:
        series = {"all": spreads[(interval, "all")],
                  "annual": spreads[(interval, "annual")],
                  "nonannual": spreads[(interval, "nonannual")]}
        series["diff"] = (series["annual"] - series["nonannual"]).dropna()

        for variant, s in series.items():
            cm = s.index.month
            for g in GROUPS:
                sel = s[cm != 1] if g == "febdec" else s[cm == _month_num(g)]
                rows.append(dict(interval=interval, variant=variant,
                                 month=g, mean_pct=sel.mean() * DECIMALS_RET,
                                 t_stat=_tstat(sel), n_months=len(sel)))
    res = pd.DataFrame(rows)

    def put(name, value, unit):
        if value is not None and not (isinstance(value, float)
                                      and np.isnan(value)):
            metrics[name] = {"value": round(float(value), 4), "unit": unit}

    for _, r in res.iterrows():
        put(f"t7_{r['interval']}_{r['variant']}_{r['month']}",
            r["mean_pct"], "percent_per_month")
        put(f"t7_{r['interval']}_{r['variant']}_{r['month']}_t",
            r["t_stat"], "t_stat")
    return res


def _month_num(abbr: str) -> int:
    return {v: k for k, v in MONTH_ABBR.items()}[abbr]


def write_table7_md(res: pd.DataFrame) -> None:
    spec = json.loads(
        (LAYOUT.preparations_path("tables_to_replicate.json")).read_text())
    paper = {m["name"]: m for tb in spec["tables"] if tb["id"] == "T7"
             for m in tb["metrics"]}
    from evaluate import classify
    intervals = ["y1", "y2_5", "y6_10", "y11_15", "y16_20"]

    def cell(r):
        if r is None:
            return "—"
        key = f"t7_{r['interval']}_{r['variant']}_{r['month']}"
        p = paper.get(key)
        pv = p.get("value") if p else None
        if pv is None:
            return f"{r['mean_pct']:.2f} [{r['t_stat']:.2f}]"
        st = classify(float(r["mean_pct"]), pv, p.get("tolerance_pct", 0),
                      p.get("absolute_band"),
                      bool(p.get("insignificant", False)))
        return (f"{r['mean_pct']:.2f} [{r['t_stat']:.2f}] "
                f"(paper {pv:.2f}, {st})")

    lines = [
        "# Table 7 — 10-1 spreads by calendar month (percent/month), "
        "1965-01 to 2002-12",
        "",
        "EW 10-1 spread mean [simple t] per calendar month; Feb-Dec is the "
        "aggregate over months 2-12. Difference = Annual spread minus "
        "Nonannual spread, computed month by month.",
        "",
        "| Strategy | " + " | ".join(GROUPS) + " |",
        "|---|" + "---|" * len(GROUPS),
    ]
    for interval in intervals:
        for variant in VARIANTS:
            cells = []
            for g in GROUPS:
                r = res[(res["interval"] == interval)
                        & (res["variant"] == variant)
                        & (res["month"] == g)]
                cells.append(cell(r.iloc[0] if len(r) else None))
            lines.append(f"| {interval} {LABEL[variant]} | "
                         + " | ".join(cells) + " |")
    (LAYOUT.result_path("table_7.md")).write_text("\n".join(lines) + "\n")
