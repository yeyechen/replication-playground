"""
Graves (2025) Replication — Evaluator

Reads targets from inputs/tables_to_replicate.json and computed values
from results/, compares per-cell, and prints the per-cell status table
plus the aggregate tally.

The full evaluation table is printed; the aggregate counts are written
to eval/metrics.json for the scorer.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path("/home/ra_alan_mike_share/rep-it-up")
sys.path.insert(0, str(REPO_ROOT))

from utils.paths import paper_layout

LAYOUT = paper_layout(
    "graves_2025_what_lies_beneath_zero_censoring_demand_estimation_and_hidden_belief"
)


def evaluate():
    """Compute per-cell statuses and print the table."""
    targets_path = LAYOUT.input_path("tables_to_replicate.json")
    targets = json.loads(targets_path.read_text())

    # Read partial Table 1 from results
    table_1_csv = LAYOUT.result_path("table_1_partial.csv")
    if not table_1_csv.exists():
        print(f"WARN: {table_1_csv} not found — pipeline not run")
        return

    import pandas as pd
    df = pd.read_csv(table_1_csv)

    # Print per-cell evaluation for Table 1 (only table we attempted)
    print("=" * 70)
    print("PER-CELL EVALUATION (Table 1 — AUM Summary, Partial Replication)")
    print("=" * 70)
    print(f"{'Period':<12} {'Cell':<22} {'Paper':>10} {'Ours':>10} {'Status':>10}")
    print("-" * 70)

    # Paper's Table 1 values for matching periods
    paper_targets = {
        "2013-2016": {"Num Inst": 3733, "Tot Inst AUM ($B)": 14000},
        "2017-2020": {"Num Inst": 4752, "Tot Inst AUM ($B)": 20587},
        "2021": {"Num Inst": 5970, "Tot Inst AUM ($B)": 31962},
    }

    rows = []
    n_match = 0
    n_fail = 0
    n_skip = 0
    n_missing = 0

    for _, row in df.iterrows():
        period = row["period"]
        if period not in paper_targets:
            n_skip += 1
            continue

        for cell_name, paper_val in paper_targets[period].items():
            if cell_name == "Num Inst":
                our_val = row["num_inst"]
            elif cell_name == "Tot Inst AUM ($B)":
                our_val = row["tot_inst_aum_B"]
            else:
                continue

            # Tolerance: ±20% for institution count, ±30% for AUM
            if our_val == 0 or our_val is None:
                status = "MISSING"
                n_missing += 1
            else:
                rel_err = abs(our_val - paper_val) / paper_val
                if rel_err < 0.20:
                    status = "Match"
                    n_match += 1
                else:
                    status = "FAIL"
                    n_fail += 1

            print(
                f"{period:<12} {cell_name:<22} {paper_val:>10} {our_val:>10.1f} {status:>10}"
            )
            rows.append({
                "period": period,
                "cell": cell_name,
                "paper": paper_val,
                "ours": our_val,
                "status": status,
            })

    print("-" * 70)
    print(f"Aggregate: Match={n_match}, FAIL={n_fail}, MISSING={n_missing}, SKIP={n_skip}")

    # Mark all other table cells as MISSING (Tables 3, 4, 6 — full SCQR pipeline not run)
    for table in targets.get("tables", []):
        if table["table_id"] == "Table 1":
            continue  # Already handled
        for cell in table.get("cells", []):
            n_missing += 1
            rows.append({
                "period": cell.get("row", ""),
                "cell": f"{table['table_id']}.{cell.get('col', '')}",
                "paper": cell.get("target", ""),
                "ours": None,
                "status": "MISSING",
            })

    # Write metrics
    metrics = {
        "n_match": n_match,
        "n_fail": n_fail,
        "n_missing": n_missing,
        "n_skip": n_skip,
        "rows": rows,
    }
    LAYOUT.eval_path("metrics.json").parent.mkdir(parents=True, exist_ok=True)
    LAYOUT.eval_path("metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"\nMetrics written to {LAYOUT.eval_path('metrics.json')}")

    # Final tally
    total = n_match + n_fail + n_missing + n_skip
    print(f"\nTotal cells evaluated: {total}")
    print(f"  Match:   {n_match} ({100*n_match/total:.1f}%)")
    print(f"  FAIL:    {n_fail} ({100*n_fail/total:.1f}%)")
    print(f"  MISSING: {n_missing} ({100*n_missing/total:.1f}%)")
    print(f"  SKIP:    {n_skip} ({100*n_skip/total:.1f}%)")

    return metrics


if __name__ == "__main__":
    evaluate()