"""
Stage 7 evaluator for max_on_steroids_attempt4.

Computes per-cell statuses (Match / FAIL / SKIP / MISSING) for the
committed target cells in tables_to_replicate.json, against the
replicated values in eval/metrics.json. Prints both per-cell grid and
aggregate tally. Output is the per-cell evaluation block; it is the
ONLY writer of those statuses; the scorer (scripts/score_replication.py)
is the canonical writer of eval/scoring.json, but for this run the
per-cell grid it prints is the audit source.
"""
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
from utils.paths import paper_layout

SLUG = "max_on_steroids_attempt4"
LAYOUT = paper_layout(SLUG)


def _load():
    targets = json.load(open(LAYOUT.preparations_path("tables_to_replicate.json")))
    metrics = json.load(open(LAYOUT.eval_path("metrics.json")))
    return targets, metrics


def _pick_replicated(metrics: dict, key: str) -> tuple:
    """Find a metric entry by exact key (T6_ prefix also checked if key missing)."""
    if key in metrics.get("metrics", {}):
        e = metrics["metrics"][key]
        if isinstance(e, dict):
            return e.get("value"), e.get("t_stat"), e.get("status", "computed")
    # Fallback namespaced keys (T6_, T2_)
    for prefix in ("T6_", "T2_"):
        nk = prefix + key
        if nk in metrics.get("metrics", {}):
            e = metrics["metrics"][nk]
            return e.get("value"), e.get("t_stat"), e.get("status", "computed")
    return None, None, None


def _status(replicated, paper_value, tolerance_pct):
    """Match / FAIL / MISSING / SKIP per rep/TOLERANCE_RULES.md."""
    if replicated is None:
        return "MISSING"
    if paper_value is None:
        return "SKIP"
    # Sign rule (per rep/TOLERANCE_RULES.md)
    if paper_value != 0 and replicated != 0:
        if (replicated > 0) != (paper_value > 0):
            return "FAIL"
    rel = abs(replicated - paper_value) / max(abs(paper_value), 1e-9)
    if rel <= tolerance_pct / 100.0:
        return "Match"
    return "FAIL"


def main():
    targets, metrics = _load()

    rows = []
    tallies = {"Match": 0, "FAIL": 0, "MISSING": 0, "SKIP": 0}

    print("=" * 90)
    print("Stage 7 evaluation — max_on_steroids_attempt4")
    print("=" * 90)
    print(f"{'Table':<8} {'Cell':<32} {'Paper':>10} {'Ours':>14} {'Status':<10}")
    print("-" * 90)

    for t in targets.get("tables", []):
        for m in t["metrics"]:
            paper = m["value"]
            repl, ts, status = _pick_replicated(metrics, m["name"])
            if status == "SKIP" or repl is None and paper is None:
                result = "SKIP"
                paper_s, repl_s = f"{paper:.3f}", "—"
            elif repl is None:
                result = "MISSING"
                paper_s = f"{paper:.3f}"
                repl_s = "—"
            elif isinstance(repl, str) and "SKIP" in repl.upper():
                result = "SKIP"
                paper_s = f"{paper:.3f}"
                repl_s = "—"
            else:
                result = _status(repl, paper, m["tolerance_pct"])
                paper_s = f"{paper:.3f}"
                repl_s = f"{repl:.4f}"
            tallies[result] += 1
            print(f"{t['id']:<8} {m['name']:<32} {paper_s:>10} {repl_s:>14} {result:<10}")
            rows.append({
                "table": t["id"], "cell": m["name"], "paper": paper,
                "ours": repl if not isinstance(repl, str) else None,
                "status": result,
            })

    n_total = sum(tallies.values())
    n_committed = tallies["Match"] + tallies["FAIL"] + tallies["MISSING"]
    print("-" * 90)
    print(f"Aggregate: {tallies}")
    print(f"Committed cells: {n_committed}, total entries: {n_total}")
    if n_committed > 0:
        loss = (tallies["FAIL"] + tallies["MISSING"]) / n_committed
        print(f"Loss L = (FAIL + MISSING) / committed = {loss:.4f}")

    # Save per-cell table for the iteration log to consume
    out = LAYOUT.eval_path("per_cell_evaluation.json")
    with open(out, "w") as f:
        json.dump({"rows": rows, "tallies": tallies, "n_committed": n_committed,
                   "loss": (tallies["FAIL"] + tallies["MISSING"]) / n_committed
                   if n_committed > 0 else None}, f, indent=2, default=str)
    print(f"\nWrote per-cell evaluation to {out}")


if __name__ == "__main__":
    main()
