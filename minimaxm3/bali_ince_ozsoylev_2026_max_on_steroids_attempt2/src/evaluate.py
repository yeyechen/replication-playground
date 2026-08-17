"""
Evaluator script: reads targets from tables_to_replicate.json and
replicated values from data/panel.parquet and results/, computes
per-cell status, prints the per-cell table, and writes eval/metrics.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/home/ra_alan_mike_share/rep-it-up/replications/max_on_steroids_attempt2")
DATA = ROOT / "data"
RESULTS = ROOT / "results"
EVAL = ROOT / "eval"


def load_metrics() -> dict:
    """Load replicated values from results/."""
    metrics = {}
    # Load table_1 (decile VW RET-RF and FF alphas)
    text = (RESULTS / 'table_1.md').read_text()
    lines = text.split('\n')
    for line in lines:
        if '|' in line and not line.startswith('|---') and not line.startswith('#'):
            parts = [p.strip() for p in line.split('|')]
            parts = [p for p in parts if p]
            if parts and (parts[0].startswith('P') or parts[0] == '10-1 spread'):
                decile = parts[0].replace(' spread', '').replace(' ', '_')
                for col_idx, col_name in enumerate(['RET-RF', 'FF3', 'FFC4', 'FF5', 'FF6'], start=1):
                    if col_idx < len(parts):
                        cell = parts[col_idx]
                        val_t = cell.split('(')
                        try:
                            val = float(val_t[0].strip())
                            t = float(val_t[1].rstrip(')').strip()) if len(val_t) > 1 else np.nan
                        except:
                            continue
                        key = f"table_1_{decile}_{col_name}"
                        metrics[key] = {'value': val, 't_stat': t}

    # Load table_6 similarly
    text = (RESULTS / 'table_6.md').read_text()
    lines = text.split('\n')
    for line in lines:
        if '|' in line and not line.startswith('|---') and not line.startswith('#'):
            parts = [p.strip() for p in line.split('|')]
            parts = [p for p in parts if p]
            if parts and (parts[0].startswith('P') or parts[0] == '10-1 spread'):
                decile = parts[0].replace(' spread', '').replace(' ', '_')
                for col_idx, col_name in enumerate(['RET-RF', 'FF3', 'FFC4', 'FF5', 'FF6'], start=1):
                    if col_idx < len(parts):
                        cell = parts[col_idx]
                        val_t = cell.split('(')
                        try:
                            val = float(val_t[0].strip())
                            t = float(val_t[1].rstrip(')').strip()) if len(val_t) > 1 else np.nan
                        except:
                            continue
                        key = f"table_6_{decile}_{col_name}"
                        metrics[key] = {'value': val, 't_stat': t}

    # Load table_4 (FM regression)
    text = (RESULTS / 'table_4.md').read_text()
    lines = text.split('\n')
    for line in lines:
        if '|' in line and not line.startswith('|---') and not line.startswith('#'):
            parts = [p.strip() for p in line.split('|')]
            parts = [p for p in parts if p]
            if parts:
                var_name = parts[0]
                for col_idx, col_label in enumerate(['Col1', 'Col2'], start=1):
                    if col_idx < len(parts) and parts[col_idx] != '—':
                        cell = parts[col_idx]
                        val_t = cell.split('(')
                        try:
                            val = float(val_t[0].strip())
                            t = float(val_t[1].rstrip(')').strip()) if len(val_t) > 1 else np.nan
                        except:
                            continue
                        key = f"table_4_{col_label}_{var_name}"
                        metrics[key] = {'value': val, 't_stat': t}

    # Load table_8 (FM dummies)
    text = (RESULTS / 'table_8.md').read_text()
    lines = text.split('\n')
    for line in lines:
        if '|' in line and not line.startswith('|---') and not line.startswith('#'):
            parts = [p.strip() for p in line.split('|')]
            parts = [p for p in parts if p]
            if parts and parts[0].startswith('D'):
                dummy = parts[0]
                for col_idx, col_label in enumerate(['Col1', 'Col2'], start=1):
                    if col_idx < len(parts) and parts[col_idx] != '—':
                        cell = parts[col_idx]
                        val_t = cell.split('(')
                        try:
                            val = float(val_t[0].strip())
                            t = float(val_t[1].rstrip(')').strip()) if len(val_t) > 1 else np.nan
                        except:
                            continue
                        key = f"table_8_{col_label}_{dummy}"
                        metrics[key] = {'value': val, 't_stat': t}

    return metrics


def load_paper_targets() -> list:
    """Load targets from tables_to_replicate.json."""
    with open(ROOT / "preparations" / "tables_to_replicate.json") as f:
        tables_doc = json.load(f)
    targets = []
    for table in tables_doc['tables']:
        for m in table['metrics']:
            targets.append({
                'table_id': table['id'],
                'name': m['name'],
                'value': m['value'],
                'unit': m['unit'],
                'tolerance_pct': m['tolerance_pct'],
                'paper_location': m['paper_location'],
            })
    return targets


def evaluate(targets: list, metrics: dict) -> tuple[list, dict]:
    """Compute per-cell status. Returns (rows, tally)."""
    rows = []
    counts = {'Match': 0, 'FAIL': 0, 'MISSING': 0, 'SKIP': 0}

    for t in targets:
        # Build expected key from target
        # Map T1 -> table_1; T6 -> table_6; T4 -> table_4; T8 -> table_8
        table_id_map = {'T1': 'table_1', 'T6': 'table_6', 'T4': 'table_4', 'T8': 'table_8'}
        prefix = table_id_map.get(t['table_id'], f"table_{t['table_id'].lstrip('T')}")
        # Target name like "P1_RET_RF" -> metric key "table_1_P1_RET-RF"
        target_name = t['name']
        # Look for matching key
        metric_key = None
        our_val = np.nan
        our_t = np.nan

        for k in metrics:
            if k.startswith(prefix + '_'):
                # Check if target_name matches the key's suffix
                suffix = k[len(prefix) + 1:]
                # Try direct match
                if target_name == suffix.replace('-', '_'):
                    metric_key = k
                    break
                # Try relaxed matching
                if target_name.startswith(suffix.split('_')[0]):
                    metric_key = k
                    break

        if metric_key is None:
            status = 'MISSING'
            counts['MISSING'] += 1
            rows.append([t['table_id'], t['name'], f"{t['value']:.3f}", 'N/A', status])
            continue

        m = metrics[metric_key]
        paper_val = t['value']
        our_val = m['value']
        tol = t['tolerance_pct']

        if our_val is None or np.isnan(our_val):
            status = 'MISSING'
            counts['MISSING'] += 1
        elif abs(our_val - paper_val) <= max(abs(paper_val * tol / 100), 0.05):
            status = 'Match'
            counts['Match'] += 1
        else:
            status = 'FAIL'
            counts['FAIL'] += 1

        rows.append([t['table_id'], t['name'], f"{paper_val:.3f}", f"{our_val:.3f}", status])

    return rows, counts


def main():
    metrics = load_metrics()
    targets = load_paper_targets()
    rows, counts = evaluate(targets, metrics)

    print("\n" + "=" * 80)
    print("Per-cell Evaluation")
    print("=" * 80)
    print(f"| {'Table':<6} | {'Cell':<25} | {'Paper':>10} | {'Ours':>10} | {'Status':<10} |")
    print("|" + "-" * 7 + "|" + "-" * 27 + "|" + "-" * 12 + "|" + "-" * 12 + "|" + "-" * 12 + "|")
    for r in rows:
        print(f"| {r[0]:<6} | {r[1]:<25} | {r[2]:>10} | {r[3]:>10} | {r[4]:<10} |")

    print("\n" + "=" * 80)
    print("Aggregate Tally")
    print("=" * 80)
    total = sum(counts.values())
    for k in ['Match', 'FAIL', 'MISSING', 'SKIP']:
        pct = counts[k] / total * 100 if total > 0 else 0
        print(f"  {k:<10} {counts[k]:>5} ({pct:.1f}%)")
    n_committed = counts['Match'] + counts['FAIL'] + counts['MISSING']
    L = (counts['FAIL'] + counts['MISSING']) / n_committed if n_committed > 0 else 0
    print(f"  Loss L = {L:.4f}")

    # Save eval/metrics.json
    EVAL.mkdir(exist_ok=True)
    out = {
        'metrics': {k: v for k, v in metrics.items()},
        'tally': counts,
        'loss': L,
        'n_committed': n_committed,
    }
    with open(EVAL / "metrics.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n[done] eval/metrics.json written")


if __name__ == "__main__":
    main()
