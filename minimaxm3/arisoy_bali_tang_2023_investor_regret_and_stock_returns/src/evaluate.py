"""DIAGNOSTIC-ONLY evaluator. The canonical scorer is
`scripts/score_replication.py` (writes `eval/scoring.json`).
This file is for the agent's debugging; its tally is not
load-bearing. See rep/TOLERANCE_RULES.md § Per-slug evaluators
are diagnostic only.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SLUG_DIR = Path("/home/ra_alan_mike_share/rep-it-up/replications/arisoy_bali_tang_2023_investor_regret_and_stock_returns")


def main() -> None:
    targets = json.loads((SLUG_DIR / "preparations" / "tables_to_replicate.json").read_text())
    metrics = json.loads((SLUG_DIR / "eval" / "metrics.json").read_text())["metrics"]

    rows = []
    n_match = n_fail = n_missing = 0
    for tbl in targets["tables"]:
        for m in tbl["metrics"]:
            name = m["name"]
            paper = m["value"]
            tol = m["tolerance_pct"]
            if name not in metrics:
                status = "MISSING"
                ours = None
                rel = None
                n_missing += 1
            else:
                ours = metrics[name]["value"]
                if paper == 0:
                    rel = abs(ours)
                else:
                    rel = abs(ours - paper) / abs(paper)
                # Sign check
                signs_differ = (paper > 0 and ours < 0) or (paper < 0 and ours > 0)
                if signs_differ:
                    status = "FAIL"
                elif rel <= tol / 100:
                    status = "Match"
                else:
                    status = "FAIL"
                if status == "Match":
                    n_match += 1
                else:
                    n_fail += 1
            rows.append((tbl["id"], name, paper, ours, tol, rel, status))

    print(f"\n{'='*78}")
    print(f"Per-cell evaluation — {SLUG_DIR.name}")
    print(f"{'='*78}")
    print(f"{'Tbl':<4} {'Metric':<24} {'Paper':>10} {'Ours':>10} {'Tol%':>5} {'RelErr':>8} {'Status':<8}")
    print(f"{'-'*78}")
    for tid, name, paper, ours, tol, rel, status in rows:
        ours_str = f"{ours:>10.4f}" if ours is not None else f"{'-':>10}"
        rel_str = f"{rel:>8.4f}" if rel is not None else f"{'-':>8}"
        print(f"{tid:<4} {name:<24} {paper:>10.4f} {ours_str} {tol:>5.1f} {rel_str} {status:<8}")

    n = len(rows)
    print(f"{'-'*78}")
    print(f"Aggregate: {n} cells | Match: {n_match} | FAIL: {n_fail} | MISSING: {n_missing}")
    if (n_match + n_fail) > 0:
        loss = n_fail / (n_match + n_fail)
    else:
        loss = 1.0
    print(f"Loss (binary-match): {loss:.4f}")


if __name__ == "__main__":
    main()
