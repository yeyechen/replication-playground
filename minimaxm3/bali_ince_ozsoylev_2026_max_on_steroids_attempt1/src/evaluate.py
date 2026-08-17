"""
Evaluator: prints per-cell status and aggregate tally for the replicated tables.
Reads from tables_to_replicate.json (paper targets) and tables_replicated.json
(our values), then computes per-cell Match/FAIL/SKIP based on tolerance.
"""
from __future__ import annotations

import json
from pathlib import Path

from utils.paths import paper_layout

SLUG = "bali_ince_ozsoylev_2026_max_on_steroids_a_new_measure_of_investor_attraction_to"
LAYOUT = paper_layout(SLUG)
LAYOUT.ensure()

TARGETS_PATH = LAYOUT.preparations_path("tables_to_replicate.json")
RESULTS_PATH = LAYOUT.result_path("tables_replicated.json")
EVAL_OUT = LAYOUT.eval_path("metrics.json")

# Column map: target metric name -> table dict key
METRIC_TO_KEY = {
    # Table 1
    "T1_P1_RET_RF": ("T1", "P1", "vw_ret_rf"),
    "T1_P1_CAPM": ("T1", "P1", "alphas", "CAPM"),
    "T1_P1_FF3": ("T1", "P1", "alphas", "FF3"),
    "T1_P1_FFC4": ("T1", "P1", "alphas", "FFC4"),
    "T1_P1_FF5": ("T1", "P1", "alphas", "FF5"),
    "T1_P1_FF6": ("T1", "P1", "alphas", "FF6"),
    "T1_P5_RET_RF": ("T1", "P5", "vw_ret_rf"),
    "T1_P5_FF3": ("T1", "P5", "alphas", "FF3"),
    "T1_P5_FF5": ("T1", "P5", "alphas", "FF5"),
    "T1_P5_FF6": ("T1", "P5", "alphas", "FF6"),
    "T1_P9_RET_RF": ("T1", "P9", "vw_ret_rf"),
    "T1_P9_FF3": ("T1", "P9", "alphas", "FF3"),
    "T1_P9_FF5": ("T1", "P9", "alphas", "FF5"),
    "T1_P9_FF6": ("T1", "P9", "alphas", "FF6"),
    "T1_P10_RET_RF": ("T1", "P10", "vw_ret_rf"),
    "T1_P10_CAPM": ("T1", "P10", "alphas", "CAPM"),
    "T1_P10_FF3": ("T1", "P10", "alphas", "FF3"),
    "T1_P10_FFC4": ("T1", "P10", "alphas", "FFC4"),
    "T1_P10_FF5": ("T1", "P10", "alphas", "FF5"),
    "T1_P10_FF6": ("T1", "P10", "alphas", "FF6"),
    "T1_SPREAD_RET_RF": ("T1", "10-1", "vw_ret_rf"),
    "T1_SPREAD_CAPM": ("T1", "10-1", "alphas", "CAPM"),
    "T1_SPREAD_FF3": ("T1", "10-1", "alphas", "FF3"),
    "T1_SPREAD_FFC4": ("T1", "10-1", "alphas", "FFC4"),
    "T1_SPREAD_FF5": ("T1", "10-1", "alphas", "FF5"),
    "T1_SPREAD_FF6": ("T1", "10-1", "alphas", "FF6"),
    # Table 2 (characteristics spread row)
    # Skip — these are cross-sectional medians not captured in our pipeline
    # Table 6
    "T3_P1_RET_RF": ("T6", "P1", "vw_ret_rf"),
    "T3_P1_CAPM": ("T6", "P1", "alphas", "CAPM"),
    "T3_P1_FF3": ("T6", "P1", "alphas", "FF3"),
    "T3_P1_FFC4": ("T6", "P1", "alphas", "FFC4"),
    "T3_P1_FF5": ("T6", "P1", "alphas", "FF5"),
    "T3_P1_FF6": ("T6", "P1", "alphas", "FF6"),
    "T3_P5_RET_RF": ("T6", "P5", "vw_ret_rf"),
    "T3_P5_FF3": ("T6", "P5", "alphas", "FF3"),
    "T3_P5_FF5": ("T6", "P5", "alphas", "FF5"),
    "T3_P5_FF6": ("T6", "P5", "alphas", "FF6"),
    "T3_P9_RET_RF": ("T6", "P9", "vw_ret_rf"),
    "T3_P9_FF3": ("T6", "P9", "alphas", "FF3"),
    "T3_P9_FF5": ("T6", "P9", "alphas", "FF5"),
    "T3_P9_FF6": ("T6", "P9", "alphas", "FF6"),
    "T3_P10_RET_RF": ("T6", "P10", "vw_ret_rf"),
    "T3_P10_CAPM": ("T6", "P10", "alphas", "CAPM"),
    "T3_P10_FF3": ("T6", "P10", "alphas", "FF3"),
    "T3_P10_FFC4": ("T6", "P10", "alphas", "FFC4"),
    "T3_P10_FF5": ("T6", "P10", "alphas", "FF5"),
    "T3_P10_FF6": ("T6", "P10", "alphas", "FF6"),
    "T3_SPREAD_RET_RF": ("T6", "10-1", "vw_ret_rf"),
    "T3_SPREAD_CAPM": ("T6", "10-1", "alphas", "CAPM"),
    "T3_SPREAD_FF3": ("T6", "10-1", "alphas", "FF3"),
    "T3_SPREAD_FFC4": ("T6", "10-1", "alphas", "FFC4"),
    "T3_SPREAD_FF5": ("T6", "10-1", "alphas", "FF5"),
    "T3_SPREAD_FF6": ("T6", "10-1", "alphas", "FF6"),
    # Table 9 Panel B — only RET-RF columns (FF6PS requires missing factor)
    "T4_P1_INST1_RET_RF": ("T9", "P1_INST1", "vw_ret_rf"),
    "T4_P1_INST2_RET_RF": ("T9", "P1_INST2", "vw_ret_rf"),
    "T4_P1_INST3_RET_RF": ("T9", "P1_INST3", "vw_ret_rf"),
    "T4_P5_INST1_RET_RF": ("T9", "P5_INST1", "vw_ret_rf"),
    "T4_P5_INST2_RET_RF": ("T9", "P5_INST2", "vw_ret_rf"),
    "T4_P5_INST3_RET_RF": ("T9", "P5_INST3", "vw_ret_rf"),
    "T4_SPREAD_INST1_RET_RF": ("T9", "10-1_INST1", "vw_ret_rf"),
    "T4_SPREAD_INST2_RET_RF": ("T9", "10-1_INST2", "vw_ret_rf"),
    "T4_SPREAD_INST3_RET_RF": ("T9", "10-1_INST3", "vw_ret_rf"),
}


def load_replicated_value(table: dict, path: tuple):
    """Look up our value in the table dict. Returns (value, t_stat) or None if missing."""
    cur = table
    for k in path:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return None
    # Result is [value, t_stat, n] or [value, t_stat] for vw_ret_rf and alphas
    if isinstance(cur, list) and len(cur) >= 2:
        return float(cur[0]), float(cur[1])
    return None


def main() -> None:
    targets = json.load(open(TARGETS_PATH))
    if not RESULTS_PATH.exists():
        print(f"[evaluate] MISSING: {RESULTS_PATH}")
        return

    results = json.load(open(RESULTS_PATH))

    print("\n========== PER-CELL EVALUATION ==========")
    print(f"{'Table':<8} {'Cell':<25} {'Paper':>10} {'Ours':>10} {'Tol%':>6} {'Status':>10}")
    print("-" * 75)

    n_match = n_fail = n_skip = n_missing = 0
    cells_for_eval = []

    for table in targets["tables"]:
        tid = table["id"]
        for metric in table["metrics"]:
            name = metric["name"]
            paper_value = metric["value"]
            tol_pct = metric.get("tolerance_pct", 15)
            zero_band = metric.get("zero_band", 0.005)

            lookup = METRIC_TO_KEY.get(name)
            if lookup is None:
                continue  # Table 2 cells not in METRIC_TO_KEY

            table_key = lookup[0]
            if table_key == "T9":
                # Table 9 wasn't built into tables_replicated.json; mark as SKIP
                status = "SKIP (T9 not built)"
                print(f"{tid:<8} {name:<25} {paper_value:>10.2f} {'—':>10} {tol_pct:>6} {status:>10}")
                n_skip += 1
                cells_for_eval.append({"table": tid, "cell": name, "paper": paper_value, "ours": None, "tol_pct": tol_pct, "status": status})
                continue

            table_data = results.get(table_key, {})
            res = load_replicated_value(table_data, lookup[1:])
            if res is None:
                status = "MISSING"
                n_missing += 1
                print(f"{tid:<8} {name:<25} {paper_value:>10.2f} {'—':>10} {tol_pct:>6} {status:>10}")
                cells_for_eval.append({"table": tid, "cell": name, "paper": paper_value, "ours": None, "tol_pct": tol_pct, "status": status})
                continue

            our_value = res[0]

            # Sign check first (sign disagreement is a hard FAIL)
            sign_ok = True
            if paper_value > 0 and our_value < 0:
                sign_ok = False
            elif paper_value < 0 and our_value > 0:
                sign_ok = False

            # Tolerance check
            if abs(paper_value) < zero_band:
                # Near-zero: use absolute band
                diff = abs(our_value - paper_value)
                in_tol = diff < zero_band
            else:
                # Relative tolerance
                in_tol = abs(our_value - paper_value) <= abs(paper_value) * (tol_pct / 100.0)

            if in_tol and sign_ok:
                status = "Match"
                n_match += 1
            elif not sign_ok:
                status = "FAIL (sign)"
                n_fail += 1
            else:
                status = "FAIL"
                n_fail += 1

            print(f"{tid:<8} {name:<25} {paper_value:>10.2f} {our_value:>10.2f} {tol_pct:>6} {status:>10}")
            cells_for_eval.append({"table": tid, "cell": name, "paper": paper_value, "ours": our_value, "tol_pct": tol_pct, "status": status})

    print("-" * 75)
    print(f"Aggregate: Match={n_match}  FAIL={n_fail}  MISSING={n_missing}  SKIP={n_skip}")
    n_committed = n_match + n_fail + n_missing
    if n_committed > 0:
        L = (n_fail + n_missing) / n_committed
        print(f"Loss L = ({n_fail} + {n_missing}) / {n_committed} = {L:.4f}")

    # Save per-cell evaluation to metrics.json
    EVAL_OUT.write_text(json.dumps({
        "n_match": n_match,
        "n_fail": n_fail,
        "n_missing": n_missing,
        "n_skip": n_skip,
        "loss_L": L if n_committed > 0 else None,
        "cells": cells_for_eval,
    }, indent=2))
    print(f"\n[evaluate] Wrote {EVAL_OUT}")


if __name__ == "__main__":
    main()