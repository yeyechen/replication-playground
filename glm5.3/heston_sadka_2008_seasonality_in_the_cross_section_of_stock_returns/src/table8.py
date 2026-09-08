"""Table 8 — 10-1 spreads in event vs nonevent months (Heston & Sadka 2008).

Panels (event month = calendar month of the event date):
  pa: earnings announcements  (comp_202601.fundq.rdq, via CCM link)
  pb: dividend announcements  (msedist.dclrdt, distcd 1200-1299)
  pc: ex-dividend             (msedist.exdt, distcd 1200-1299)
  pd: fiscal year-end + subsequent month (funda.datadate, via CCM)

For each of the 15 strategies and each panel:
  covered firms = panel permnos with at least one event ever (in-sample).
  EVENT months: among covered firms with the event that month, form the
  10 Rule-B deciles on the strategy signal; EW decile returns; 10-1
  spread; mean + simple t over available holding months 1965-01..2002-12.
  NONEVENT months: same among covered firms WITHOUT the event that month.

rdq coverage starts ~1970 (Assumption 10), so Panel A event months begin
then — expected.
"""
import json

import numpy as np
import pandas as pd

from main import (DECIMALS_RET, HOLD_END, HOLD_START, LAG_SETS, LAYOUT, N_BINS,
                  _tstat, _wide_matrix)
from utils.quantile import assign_quantiles

PANEL_LABEL = {"pa": "A: earnings announcements", "pb": "B: dividend "
               "announcements", "pc": "C: ex-dividend",
               "pd": "D: fiscal year-end (+1)"}


def load_events(panel: pd.DataFrame) -> dict:
    """(panel_code, holding Period) -> set(permno); plus coverage counts."""
    frames = []
    from main import q_file
    frames.append(q_file("comp_events.sql"))       # pa, pd
    frames.append(q_file("dividend_events.sql"))   # pb, pc
    ev = pd.concat(frames, ignore_index=True)
    ev["event_month"] = pd.PeriodIndex(pd.to_datetime(ev["event_month"]),
                                       freq="M")
    ev = ev.drop_duplicates()
    ev = ev[(ev["event_month"] >= HOLD_START) & (ev["event_month"] <= HOLD_END)]
    # restrict to panel permnos and panel months
    panel_permnos = set(panel["permno"].unique())
    ev = ev[ev["permno"].isin(panel_permnos)]
    ev = ev[ev["permno"].notna()]
    ev["permno"] = ev["permno"].astype(int)

    events = {}
    for code, g in ev.groupby("panel"):
        events[code] = dict(g.groupby("event_month")["permno"].apply(set))
    return events, ev


def _strategy_frames(panel: pd.DataFrame) -> dict:
    """{(interval, variant)} -> tidy frame month/permno/sig/ret (Rule B).

    Same eligibility as Table 2 (Assumption 5 REVISED): ret at t
    non-missing and >= 1 available formation month; signal = mean over
    available formation months.
    """
    R, m_idx, months, permnos, _ = _wide_matrix(panel)
    nanmask = np.isnan(R)
    hold_rows = [i for i, m in enumerate(months) if HOLD_START <= m <= HOLD_END]
    frames = {}
    for interval, variants in LAG_SETS.items():
        for variant, lags in variants.items():
            lags = np.asarray(lags, dtype=int)
            parts = []
            for t in hold_rows:
                cols = t - lags
                if cols.min() < 0:
                    continue
                sub = R[cols, :]
                avail = ~np.isnan(sub)
                ok = avail.any(axis=0) & ~nanmask[t, :]
                if not ok.any():
                    continue
                avg = np.nanmean(sub[:, ok].astype(np.float64), axis=0)
                idx = np.where(ok)[0]
                parts.append(pd.DataFrame({
                    "month": str(months[t]), "permno": permnos[idx],
                    "sig": avg, "ret": R[t, idx].astype(np.float64)}))
            frames[(interval, variant)] = pd.concat(parts,
                                                    ignore_index=True)
    return frames


def table8(panel: pd.DataFrame, metrics: dict) -> dict:
    events, ev_raw = load_events(panel)
    frames = _strategy_frames(panel)

    # event-month counts per panel per decade (sanity, L2420)
    counts = {}
    ev_raw = ev_raw.copy()
    ev_raw["decade"] = (ev_raw["event_month"].dt.year // 10) * 10
    for code, g in ev_raw.groupby("panel"):
        counts[code] = (g.groupby("decade").size().to_dict()
                        | {"_months": len(set(g["event_month"])),
                           "_permnos": g["permno"].nunique()})

    rows = []
    for (interval, variant), long in frames.items():
        long = long.copy()
        long["month_p"] = pd.PeriodIndex(pd.to_datetime(long["month"]),
                                         freq="M")
        for code, ev_by_month in events.items():
            covered = set().union(*ev_by_month.values()) if ev_by_month else set()
            sub = long[long["permno"].isin(covered)]
            sub["is_event"] = [p in ev_by_month.get(m, ())
                               for p, m in zip(sub["permno"], sub["month_p"])]
            for which, sel in (("event", sub[sub["is_event"]]),
                               ("nonevent", sub[~sub["is_event"]])):
                sel = sel.drop(columns=["is_event"])
                if sel.empty:
                    continue
                sel["decile"] = assign_quantiles(
                    sel, date_col="month", signal_col="sig",
                    n_bins=N_BINS, warn_fallback=False)
                piv = sel.pivot_table(index="month", columns="decile",
                                      values="ret", aggfunc="mean")
                if N_BINS not in piv.columns or 1 not in piv.columns:
                    continue
                spread = (piv[N_BINS] - piv[1]).dropna()
                rows.append(dict(
                    interval=interval, variant=variant, panel=code,
                    which=which, mean_pct=spread.mean() * DECIMALS_RET,
                    t_stat=_tstat(spread), n_months=len(spread),
                    avg_n=sel.groupby("month").size().mean()))
        print(f"[t8] {interval} {variant} done")
    res = pd.DataFrame(rows)

    def put(name, value, unit):
        if value is not None and not (isinstance(value, float)
                                      and np.isnan(value)):
            metrics[name] = {"value": round(float(value), 4), "unit": unit}

    for _, r in res.iterrows():
        put(f"t8_{r['interval']}_{r['variant']}_{r['panel']}_{r['which']}",
            r["mean_pct"], "percent_per_month")
        put(f"t8_{r['interval']}_{r['variant']}_{r['panel']}_{r['which']}_t",
            r["t_stat"], "t_stat")
    return {"res": res, "counts": counts}


def write_table8_md(out: dict) -> None:
    res, counts = out["res"], out["counts"]
    spec = json.loads(
        (LAYOUT.preparations_path("tables_to_replicate.json")).read_text())
    paper = {m["name"]: m for tb in spec["tables"] if tb["id"] == "T8"
             for m in tb["metrics"]}
    from evaluate import classify

    lines = [
        "# Table 8 — 10-1 spreads in event vs nonevent months "
        "(percent/month), 1965-01 to 2002-12",
        "",
        "EW 10-1 spread mean [simple t], computed within the covered-firm "
        "subsample each month (event months = covered firms with the event "
        "that month; nonevent months = covered firms without). Rule B "
        "eligibility, as Table 2. Panel A event months start ~1971 "
        "(rdq coverage, Assumption 10).",
        "",
    ]
    tally = {}
    for code in ("pa", "pb", "pc", "pd"):
        lines.append(f"## Panel {PANEL_LABEL[code]}")
        lines.append("")
        lines.append("| Strategy | Event | Nonevent | Event months | "
                     "Nonevent months | avg firms (ev/nonev) |")
        lines.append("|---|---|---|---|---|---|")
        for interval in LAG_SETS:
            for variant in ("all", "annual", "nonannual"):
                cells = [f"{interval} {variant}"]
                for which in ("event", "nonevent"):
                    r = res[(res["interval"] == interval)
                            & (res["variant"] == variant)
                            & (res["panel"] == code)
                            & (res["which"] == which)]
                    if not len(r):
                        cells.append("—")
                        continue
                    r = r.iloc[0]
                    key = (f"t8_{interval}_{variant}_{code}_{which}")
                    p = paper.get(key)
                    st = ""
                    if p and p.get("value") is not None:
                        s = classify(float(r["mean_pct"]), p["value"],
                                     p.get("tolerance_pct", 0),
                                     p.get("absolute_band"),
                                     bool(p.get("insignificant", False)))
                        tally[s] = tally.get(s, 0) + 1
                        st = f" ({s})"
                    cells.append(f"{r['mean_pct']:.2f} [{r['t_stat']:.2f}]"
                                 f"{st}")
                ev = res[(res["interval"] == interval)
                         & (res["variant"] == variant)
                         & (res["panel"] == code)
                         & (res["which"] == "event")]
                ne = res[(res["interval"] == interval)
                         & (res["variant"] == variant)
                         & (res["panel"] == code)
                         & (res["which"] == "nonevent")]
                nm_e = int(ev.iloc[0]["n_months"]) if len(ev) else 0
                nm_n = int(ne.iloc[0]["n_months"]) if len(ne) else 0
                an = (f"{ev.iloc[0]['avg_n']:,.0f}/"
                      f"{ne.iloc[0]['avg_n']:,.0f}"
                      if len(ev) and len(ne) else "—")
                cells += [str(nm_e), str(nm_n), an]
                lines.append("| " + " | ".join(cells) + " |")
        lines.append("")

    lines.append("## Event firm-month counts by decade (sanity, L2420)")
    lines.append("")
    lines.append("| Panel | " + " | ".join(
        str(d) for d in range(1960, 2001, 10)) + " | distinct months | "
        "distinct permnos |")
    lines.append("|---|" + "---|" * 8)
    for code in ("pa", "pb", "pc", "pd"):
        c = counts[code]
        row = [PANEL_LABEL[code]]
        row += [f"{c.get(d, 0):,}" for d in range(1960, 2001, 10)]
        row += [f"{c['_months']:,}", f"{c['_permnos']:,}"]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    if tally:
        lines.append("Tally vs paper (spread cells): " + ", ".join(
            f"{k} {v}" for k, v in sorted(tally.items())))
    (LAYOUT.result_path("table_8.md")).write_text("\n".join(lines) + "\n")
