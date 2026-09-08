"""DIAGNOSTIC-ONLY evaluator. The canonical scorer is
`scripts/score_replication.py` (writes `eval/scoring.json`).
This file is for the agent's debugging; its tally is not
load-bearing. See rep/TOLERANCE_RULES.md § Per-slug evaluators
are diagnostic only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SKILL_ROOT = Path("/home/ra_yeye/.claude/skills/rep-it-up")
sys.path.insert(0, str(SKILL_ROOT))

from utils.paths import paper_layout  # noqa: E402

SLUG = "heston_sadka_2008_seasonality_in_the_cross_section_of_stock_returns"
LAYOUT = paper_layout(SLUG)

# Tables implemented so far; all other tables' cells are reported MISSING.
IMPLEMENTED = {"T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"}


def classify(ours, paper, tol_pct, absolute_band, insignificant):
    """Hybrid tolerance rule (diagnostic mirror of the canonical scorer)."""
    if insignificant:
        return "no_effect"
    if ours is None:
        return "MISSING"
    if paper is None:
        return "SKIP"
    so = (ours > 0) - (ours < 0)
    sp = (paper > 0) - (paper < 0)
    if so != sp:
        return "FAIL"
    rel_err = abs(ours - paper) / abs(paper) if paper != 0 else float("inf")
    if rel_err <= tol_pct / 100.0:
        return "Match"
    if absolute_band is not None and abs(ours - paper) <= absolute_band:
        return "Match"
    return "FAIL"


def main() -> None:
    spec = json.loads(
        (LAYOUT.preparations_path("tables_to_replicate.json")).read_text())
    try:
        ours_all = json.loads(
            (LAYOUT.eval_path("metrics.json")).read_text())["metrics"]
    except FileNotFoundError:
        print("eval/metrics.json not found — run src/main.py first.")
        return

    tally = {}
    lines = []
    for table in spec["tables"]:
        tid = table["id"]
        for m in table["metrics"]:
            name = m["name"]
            paper = m.get("value")
            tol = m.get("tolerance_pct", 0)
            band = m.get("absolute_band")
            insig = bool(m.get("insignificant", False))
            entry = ours_all.get(name)
            ours = entry["value"] if isinstance(entry, dict) else entry
            if tid not in IMPLEMENTED:
                status = "MISSING" if paper is not None else "SKIP"
            else:
                status = classify(ours, paper, tol, band, insig)
            tally[status] = tally.get(status, 0) + 1
            ours_s = "—" if ours is None else f"{ours:.4g}"
            paper_s = "—" if paper is None else f"{paper:.4g}"
            lines.append(f"{tid:3s} {name:42s} ours={ours_s:>10s} "
                         f"paper={paper_s:>10s} -> {status}")

    print("\n".join(lines))
    total = sum(tally.values())
    print("\nTALLY (diagnostic only):")
    for k in ("Match", "FAIL", "MISSING", "SKIP", "no_effect"):
        if k in tally:
            print(f"  {k:10s} {tally[k]:4d}  ({tally[k] / total:.1%})")
    print(f"  {'total':10s} {total:4d}")


if __name__ == "__main__":
    main()
