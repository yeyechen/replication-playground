"""DIAGNOSTIC-ONLY evaluator. The canonical scorer is
`scripts/score_replication.py` (writes `eval/scoring.json`).
This file is for the agent's debugging; its tally is not
load-bearing. See rep/TOLERANCE_RULES.md § Per-slug evaluators
are diagnostic only.
"""
from __future__ import annotations

import json
import sys

from utils.paths import paper_layout

SLUG = "weber_2018_attempt2_deepseek"
LAYOUT = paper_layout(SLUG)
SIGN_EPS = 1e-9


def _sign(x):
    if x > SIGN_EPS:
        return 1
    if x < -SIGN_EPS:
        return -1
    return 0


def classify(paper, ours, tolerance_pct, zero_band=None, insignificant=False):
    """Return (status, rel_err). Mirrors scripts/score_replication.py."""
    if insignificant:
        return ("no_effect", None)
    if paper is None:
        return ("SKIP", None)
    if ours is None:
        return ("MISSING", None)
    tol = tolerance_pct / 100.0

    if zero_band is not None:
        abs_dev = abs(ours - paper)
        if abs_dev <= zero_band:
            return ("Match", 0.0)
        mag_err = max(0.0, abs_dev - zero_band) / max(zero_band, 1e-12)
        if _sign(paper) != _sign(ours) and _sign(paper) != 0 and _sign(ours) != 0:
            return ("FAIL", mag_err)
        return ("Match", mag_err) if mag_err <= tol else ("FAIL", mag_err)

    if paper == 0:
        rel_err = min(abs(ours) / max(tol, 1e-12), 100.0)
    else:
        rel_err = abs(ours - paper) / abs(paper)

    if _sign(paper) != _sign(ours) and _sign(paper) != 0 and _sign(ours) != 0:
        return ("FAIL", rel_err)
    return ("Match", rel_err) if rel_err <= tol else ("FAIL", rel_err)


def main():
    targets = json.loads(LAYOUT.preparations_path("tables_to_replicate.json").read_text())
    metrics_doc = json.loads(LAYOUT.eval_path("metrics.json").read_text())
    ours_map = metrics_doc.get("metrics", {})

    # Build a tables map for the report (all committed tables in the JSON).
    tables = {}
    table_ids = []
    for tbl in targets.get("tables", []):
        tid = tbl.get("id")
        tables[tid] = tbl
        table_ids.append(tid)

    rows = []
    counts = {"Match": 0, "FAIL": 0, "MISSING": 0, "no_effect": 0, "SKIP": 0}
    for tid in table_ids:
        for m in tables[tid].get("metrics", []):
            name = m["name"]
            paper = m.get("value")
            tol = float(m.get("tolerance_pct", 0))
            zb = m.get("zero_band")
            insig = bool(m.get("insignificant", False))
            entry = ours_map.get(name)
            ours = entry["value"] if isinstance(entry, dict) and "value" in entry else None
            status, rel_err = classify(paper, ours, tol, zb, insig)
            counts[status] = counts.get(status, 0) + 1
            rows.append((tid, name, paper, ours, status, rel_err))

    # Full per-cell table
    print("Table | Cell | Paper | Ours | Status")
    print("------|------|-------|------|--------")
    for tid, name, paper, ours, status, rel_err in rows:
        ps = f"{paper:.4f}" if paper is not None else "—"
        os = f"{ours:.4f}" if ours is not None else "—"
        suffix = f" (err={rel_err:.3f})" if rel_err is not None else ""
        print(f"{tid} | {name} | {ps} | {os} | {status}{suffix}")

    match = counts["Match"]
    fail = counts["FAIL"]
    missing = counts["MISSING"]
    no_effect = counts["no_effect"]
    denom = match + fail + missing
    loss = (fail + missing) / denom if denom else float("nan")
    print("\nAggregate tally:")
    print(f"  Match     = {match}")
    print(f"  FAIL      = {fail}")
    print(f"  MISSING   = {missing}")
    print(f"  no_effect = {no_effect}")
    print(f"  SKIP      = {counts.get('SKIP', 0)}")
    print(f"  L = (FAIL+MISSING)/(Match+FAIL+MISSING) = {loss:.4f}")

    # per-table tally
    print("\nPer-table tally:")
    for tid in table_ids:
        sub = [r for r in rows if r[0] == tid]
        if not sub:
            continue
        m = sum(1 for r in sub if r[4] == "Match")
        f = sum(1 for r in sub if r[4] == "FAIL")
        miss = sum(1 for r in sub if r[4] == "MISSING")
        den = m + f + miss
        print(f"  {tid}: Match={m} FAIL={f} MISSING={miss}  "
              f"L={(f+miss)/den if den else float('nan'):.4f}")


if __name__ == "__main__":
    main()
