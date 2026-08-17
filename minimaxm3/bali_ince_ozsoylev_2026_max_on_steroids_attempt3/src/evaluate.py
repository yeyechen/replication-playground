"""
Per-cell tolerance check evaluator for the MAX on Steroids replication.

Reads `preparations/tables_to_replicate.json` (targets) and
`eval/metrics.json` (replicated values), then prints per-cell
(Paper | Ours | Status) tables and the aggregate tally.

This is a diagnostic tool per rep/TOLERANCE_RULES.md. The canonical
scorer is `scripts/score_replication.py`.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from utils.paths import paper_layout

LAYOUT = paper_layout("max_on_steroids_attempt3").ensure()


def status(paper: float, ours: float, tol_pct: float) -> str:
    """Return 'Match', 'FAIL', 'L' (sign mismatch), or 'MISSING'."""
    if ours is None or (isinstance(ours, float) and np.isnan(ours)):
        return "MISSING"
    if (np.sign(ours) != np.sign(paper)) and (abs(paper) > 1e-6) and (abs(ours) > 1e-6):
        return "L"
    rel_err = abs(ours - paper) / max(abs(paper), 1e-6)
    return "Match" if rel_err <= tol_pct / 100.0 else "FAIL"


def evaluate_table(tbl: dict, metrics_map: dict) -> tuple[list, dict]:
    """Run tolerance check for one table; return (rows, tally)."""
    tid = tbl["id"]
    rows = []
    tally = {"Match": 0, "FAIL": 0, "MISSING": 0, "L": 0}
    for m in tbl["metrics"]:
        name = m["name"]
        paper = m["value"]
        tol = m["tolerance_pct"]
        cell = metrics_map.get(name)
        ours = cell["value"] if cell is not None else None
        s = status(paper, ours, tol)
        tally[s] = tally.get(s, 0) + 1
        rows.append((tid, name, paper, ours, s, tol))
    return rows, tally


def render_table(rows: list) -> str:
    lines = []
    lines.append(f"{'Table':<6} {'Cell':<15} {'Paper':>10} {'Ours':>10} {'Tol%':>6} {'Status':<8}")
    lines.append("-" * 60)
    for r in rows:
        ours_str = f"{r[3]:>10.2f}" if r[3] is not None else "    —    "
        lines.append(f"{r[0]:<6} {r[1]:<15} {r[2]:>10.2f} {ours_str} {r[5]:>6} {r[4]:<8}")
    return "\n".join(lines)


def main():
    # Load spec
    with open(LAYOUT.preparations_path("tables_to_replicate.json")) as f:
        spec = json.load(f)
    # Load metrics
    metrics_path = LAYOUT.eval_path("metrics.json")
    if not metrics_path.exists():
        print(f"ERROR: {metrics_path} not found. Run main.py first.")
        return 1
    with open(metrics_path) as f:
        metrics_doc = json.load(f)
    metrics_map = metrics_doc.get("metrics", {})

    # Run per table
    grand_rows = []
    grand_tally = {"Match": 0, "FAIL": 0, "MISSING": 0, "L": 0}
    for tbl in spec["tables"]:
        rows, tally = evaluate_table(tbl, metrics_map)
        grand_rows.extend(rows)
        for k, v in tally.items():
            grand_tally[k] = grand_tally.get(k, 0) + v

    # Render
    print("=" * 80)
    print("PER-CELL TOLERANCE CHECK")
    print("=" * 80)
    # Per-table sections
    seen = set()
    output_rows = []
    for r in grand_rows:
        if r[0] not in seen:
            if seen:
                print()
            print(f"=== {r[0]} ===")
            seen.add(r[0])
        ours_str = f"{r[3]:>10.2f}" if r[3] is not None else "    —    "
        print(f"  {r[1]:<15} paper={r[2]:>8.2f}  ours={ours_str}  tol={r[5]:>3}%  {r[4]}")

    print()
    print("=" * 80)
    print("AGGREGATE TALLY")
    print("=" * 80)
    for k, v in grand_tally.items():
        print(f"  {k:<10}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
