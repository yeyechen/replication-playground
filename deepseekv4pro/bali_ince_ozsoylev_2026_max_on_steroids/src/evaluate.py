"""DIAGNOSTIC-ONLY evaluator. The canonical scorer is
`scripts/score_replication.py` (writes `eval/scoring.json`).
This file is for the agent's debugging; its tally is not
load-bearing. See rep/TOLERANCE_RULES.md § Per-slug evaluators
are diagnostic only.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from utils.paths import paper_layout

SLUG = "max_on_steroids_attempt5_deepseek"
LAYOUT = paper_layout(SLUG)


_SIGN_EPS = 1e-12


def _sign(x: float) -> int:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return 0
    if x > _SIGN_EPS:
        return 1
    if x < -_SIGN_EPS:
        return -1
    return 0


def _classify(name: str, paper: dict, ours: float | None, skips: set[str]) -> str:
    # Iteration-13 alignment: mirror the canonical scorer's
    # scripts/score_replication.py::_classify_status exactly (binary ladder),
    # so the diagnostic tally's per-cell status matches the canonical scorer.
    # Prior divergence: (a) zero_band path required sign-match AND within-band,
    # while the canonical scorer returns Match on abs_dev<=band OR sign-match
    # with mag_err<=tol; (b) sign used >0/<0 instead of an |eps| threshold with
    # a paper_sign==0 / ours_sign==0 relaxation.
    if name in skips:
        return "MISSING"
    if ours is None or (isinstance(ours, float) and math.isnan(ours)):
        return "MISSING"
    pap = paper["value"]
    zero_band = paper.get("zero_band")
    insignificant = paper.get("insignificant", False)

    if insignificant:
        # Magnitude untestable; the paired inference_cell carries the
        # signal, scored normally. This cell itself -> no_effect.
        return "no_effect"

    tolerance_pct = paper.get("tolerance_pct", 50)

    if zero_band is not None:
        abs_dev = abs(ours - pap)
        if abs_dev <= zero_band:
            return "Match"
        tol = tolerance_pct / 100.0
        mag_err = max(0.0, abs_dev - zero_band) / max(zero_band, 1e-12)
        paper_sign = _sign(pap)
        ours_sign = _sign(ours)
        sign_match = paper_sign == ours_sign or paper_sign == 0 or ours_sign == 0
        if not sign_match:
            return "FAIL"
        if mag_err <= tol:
            return "Match"
        return "FAIL"

    tol = tolerance_pct / 100.0
    if pap == 0:
        rel_err = abs(ours) if tol == 0 else min(abs(ours) / max(tol, 1e-12), 100.0)
    else:
        rel_err = abs(ours - pap) / abs(pap)

    paper_sign = _sign(pap)
    ours_sign = _sign(ours)
    sign_match = paper_sign == ours_sign or paper_sign == 0 or ours_sign == 0
    if not sign_match:
        return "FAIL"
    if rel_err <= tol:
        return "Match"
    return "FAIL"


def main() -> None:
    tables = json.loads(LAYOUT.preparations_path("tables_to_replicate.json").read_text())
    metrics_doc = json.loads(LAYOUT.eval_path("metrics.json").read_text())
    ours_map = {
        k: v["value"] if isinstance(v, dict) else v
        for k, v in metrics_doc.get("metrics", {}).items()
    }
    skips = set(metrics_doc.get("skips", []))

    t1 = next(t for t in tables["tables"] if t["id"] == "T1")
    t3 = next(t for t in tables["tables"] if t["id"] == "T3")
    # Additional tables implemented in this task batch (T2/T4/T6/T7/T8/T9/T5).
    t_ids = {"T1", "T2", "T3", "T4", "T6", "T7", "T8", "T9", "T5"}
    extra = [t for t in tables["tables"] if t["id"] in t_ids and t["id"] not in ("T1", "T3")]

    cells = []
    for t in (t1, t3, *extra):
        for m in t["metrics"]:
            name = m["name"]
            ours = ours_map.get(name)
            status = _classify(name, m, ours, skips)
            cells.append((t["id"], name, m["value"], ours, status, m))

    misses = set(metrics_doc.get("skips", []))
    counts = {"Match": 0, "FAIL": 0, "MISSING": 0, "no_effect": 0}
    lines = []
    for tid, name, pap, ours, status, m in cells:
        counts[status] = counts.get(status, 0) + 1
        ov = "—" if ours is None else (f"{ours:.4f}" if isinstance(ours, (int, float)) else str(ours))
        pv = f"{pap:.4f}" if isinstance(pap, (int, float)) else str(pap)
        # Relabel the display status for documented third-party gaps so the
        # diagnostic tally's vocabulary matches the canonical scorer (MISSING),
        # while flagging the cause inline.
        disp = "MISSING (documented third-party gap)" if name in misses else status
        lines.append(f"{tid} | {name} | {pv} | {ov} | {disp}")

    header = "Table | Cell | Paper | Ours | Status"
    print(header)
    for ln in lines:
        print(ln)

    denom = counts["Match"] + counts["FAIL"] + counts["MISSING"]
    L = (counts["FAIL"] + counts["MISSING"]) / denom if denom else 0.0
    print()
    print("--- aggregate tally ---")
    print(f"Match={counts['Match']} FAIL={counts['FAIL']} MISSING={counts['MISSING']} "
          f"no_effect={counts['no_effect']}")
    print(f"(of the {counts['MISSING']} MISSING, {sum(1 for n in misses)} are documented third-party gaps)")
    print(f"L=(FAIL+MISSING)/(Match+FAIL+MISSING) = ({counts['FAIL']}+{counts['MISSING']})/{denom} = {L:.4f}")


if __name__ == "__main__":
    main()
