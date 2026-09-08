"""DIAGNOSTIC-ONLY evaluator. The canonical scorer is
`scripts/score_replication.py` (writes `eval/scoring.json`).
This file is for the agent's debugging; its tally is not
load-bearing. See rep/TOLERANCE_RULES.md § Per-slug evaluators
are diagnostic only.
"""

import json
from pathlib import Path

LAYOUT = Path(__file__).resolve().parents[1]

# Tables with computed cells so far. Later iterations extend this list.
TABLES = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"]


def classify(metric: dict, ours):
    """Hybrid rule per rep/TOLERANCE_RULES.md:
    Match iff sign matches AND (relative within tolerance_pct
    OR absolute gap within absolute_band). insignificant:true cells ->
    no_effect when the paired inference t-cell is present, else flagged."""
    if ours is None:
        return "MISSING"
    paper = metric["value"]
    tol = metric.get("tolerance_pct", 0) / 100.0
    band = metric.get("absolute_band")
    if metric.get("insignificant"):
        inf = metric.get("inference_cell")
        return "no_effect" if inf is not None else "FLAG_no_inference_cell"
    if (paper >= 0) != (ours >= 0):
        return "FAIL"
    if abs(ours - paper) / abs(paper) <= tol:
        return "Match"
    if band is not None and abs(ours - paper) <= band:
        return "Match"
    return "FAIL"


def run(table_id: str):
    spec = json.loads(
        (LAYOUT / "preparations" / "tables_to_replicate.json").read_text())
    metrics = json.loads(
        (LAYOUT / "eval" / "metrics.json").read_text())["metrics"]
    tbl = next(t for t in spec["tables"] if t["id"] == table_id)

    rows = []
    counts = {"Match": 0, "FAIL": 0, "MISSING": 0, "no_effect": 0,
              "FLAG_no_inference_cell": 0}
    for m in tbl["metrics"]:
        # metrics.json uses bare, globally-unique names (schema_version 3);
        # table membership comes from this targets file, not from prefixes.
        entry = metrics.get(m["name"])
        ours = float(entry["value"]) if entry else None
        status = classify(m, ours)
        if status not in counts:
            counts[status] = 0
        counts[status] += 1
        rows.append((m["name"], m["value"], ours, status))

    print(f"\n=== {table_id} ({tbl['table_ref']}) — DIAGNOSTIC tally ===")
    print(f"{'cell':28s} {'paper':>10s} {'ours':>10s}  status")
    for cell, paper, ours, status in rows:
        ours_s = f"{ours:.4f}" if ours is not None else "—"
        print(f"{cell:28s} {paper:>10.4f} {ours_s:>10s}  {status}")
    n = counts["Match"] + counts["FAIL"] + counts["MISSING"]
    loss = (counts["FAIL"] + counts["MISSING"]) / n if n else float("nan")
    print(f"tally: {counts} | loss L = (FAIL+MISSING)/(Match+FAIL+MISSING)"
          f" = {loss:.3f}")
    return rows, counts


if __name__ == "__main__":
    for tid in TABLES:
        run(tid)
