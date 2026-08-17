"""
Weber (2018) — Per-cell evaluator (DIAGNOSTIC-ONLY).

DIAGNOSTIC-ONLY evaluator. The canonical scorer is
`scripts/score_replication.py` (writes `eval/scoring.json`).
This file is for the agent's debugging; its tally is not
load-bearing. See rep/TOLERANCE_RULES.md § Per-slug evaluators
are diagnostic only.

Reads:
  - `inputs/tables_to_replicate.json`  -- target cells, paper values, tolerances
  - `results/table_1.md`               -- T1 means/std
  - `results/table_2.md`               -- T2 decile perf
  - `results/table_3.md`               -- T3 FF3/FF4/FF5 alphas
  - `results/table_5.md`               -- T5 subsample spreads
  - `results/table_10.md`              -- T10 dur x RIOR matrix

Writes:
  - `eval/metrics.json` -- per-cell replicated values, scorer input.

Computes per-cell status using:
  - Match   : sign matches AND |replicated - paper| / |paper| <= tolerance_pct/100
  - FAIL    : sign disagreement OR magnitude outside tolerance
  - MISSING : paper target exists but replicated value is absent
  - SKIP    : paper target is absent (no committed target)

The per-cell tally + aggregate is printed to stdout.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from utils.paths import paper_layout


# ---- Configuration ---------------------------------------------------------
SLUG = "weber_2018_cash_flow_duration_and_the_term_structure_of_equity_returns"
LAYOUT = paper_layout(SLUG)
LAYOUT.ensure()

EVAL_DIR = LAYOUT.eval_path("")  # eval/ folder
INPUTS_DIR = LAYOUT.input_path("")  # inputs/ folder
RESULTS_DIR = LAYOUT.result_path("")  # results/ folder

# Default near-zero band: paper's printing precision
DEFAULT_ZERO_BAND = 0.005  # paper Table 2/3 print 2-decimal; ±0.005


# ---- Helpers ---------------------------------------------------------------
def _classify(value: float | None, target: float, tolerance_pct: float,
              zero_band: float | None = None) -> str:
    """Compute per-cell status.

    Parameters
    ----------
    value         : replicated value, or None if missing
    target        : paper's value
    tolerance_pct : relative tolerance, in percent (e.g. 15 -> ±15%)
    zero_band     : optional absolute band for near-zero cells
    """
    if value is None:
        return "MISSING"
    # Sign check (sign agreement is required regardless of magnitude)
    sign_match = (value == 0 and target == 0) or (
        (value > 0 and target > 0) or (value < 0 and target < 0)
    )
    if not sign_match:
        return "FAIL"
    # Near-zero band: if paper's value is below zero_band, use absolute
    if abs(target) <= (zero_band or DEFAULT_ZERO_BAND):
        return "Match" if abs(value) <= (zero_band or DEFAULT_ZERO_BAND) else "FAIL"
    # Otherwise relative tolerance
    rel_err = abs(value - target) / abs(target)
    if rel_err <= tolerance_pct / 100.0:
        return "Match"
    return "FAIL"


def _fmt(x: float | None) -> str:
    if x is None:
        return "MISSING"
    if isinstance(x, float) and (x != x):  # NaN
        return "NaN"
    return f"{x:.3f}"


# ---- Markdown parsers ------------------------------------------------------
_NUM = r"-?\d+(?:\.\d+)?"

def _grep(pattern: str, text: str, group: int = 1) -> str | None:
    m = re.search(pattern, text)
    return m.group(group) if m else None


def parse_table_1(md_text: str) -> dict[str, dict[str, float]]:
    """Parse results/table_1.md for {variable: {mean, std}}.

    The 'Comparison to paper' section is NOT used (paper values live in
    tables_to_replicate.json). We parse the primary table.
    """
    out: dict[str, dict[str, float]] = {}
    # Variable labels are the canonical names; mapping handles formatting
    label_map = {
        "Dur": "dur",
        "BM": "bm",
        "IOR": "ior",
        "PR": "pr",
        "ROE": "roe",
        "Sales_g": "sales_g",
        "ME ($M)": "me_mil",
        "Age": "age",
    }
    for label, key in label_map.items():
        # The table is "| Dur | 19.433 | 4.441 |"
        pattern = rf"\|\s*{re.escape(label)}\s*\|\s*({_NUM})\s*\|\s*({_NUM})\s*\|"
        m = re.search(pattern, md_text)
        if m:
            mean_v = float(m.group(1))
            std_v = float(m.group(2))
            out[key] = {"mean": mean_v, "std": std_v}
    return out


def parse_table_2(md_text: str) -> dict[str, dict[str, float]]:
    """Parse results/table_2.md for decile-level {mean_excess, beta, alpha, sharpe}.

    The D1-D10 spread row is included as a "spread" key.
    """
    out: dict[str, dict[str, float]] = {}

    # ---- Panel A: Mean excess, Beta, Alpha ----
    # Header is | Decile | Mean excess (%, monthly) | SE mean | t_mean | Beta ...
    # We grab the Mean excess, Beta, Alpha columns. The Panel A table has
    # exactly 12 columns per row (Decile + 11 numeric), so we anchor on that.
    for decile in [f"D{i}" for i in range(1, 11)] + ["D1-D10"]:
        pattern = (
            rf"\|\s*{re.escape(decile)}\s*\|"
            rf"\s*({_NUM})\s*\|"  # Mean excess
            rf"\s*{_NUM}\s*\|"    # SE mean
            rf"\s*{_NUM}\s*\|"    # t_mean
            rf"\s*({_NUM})\s*\|"  # Beta
            rf"\s*{_NUM}\s*\|"    # SE beta
            rf"\s*{_NUM}\s*\|"    # t_beta
            rf"\s*({_NUM})\s*\|"  # Alpha
            rf"\s*{_NUM}\s*\|"    # SE alpha
            rf"\s*{_NUM}\s*\|"    # t_alpha
            rf"\s*{_NUM}\s*\|"    # R^2
            rf"\s*{_NUM}\s*\|"    # N months
        )
        m = re.search(pattern, md_text)
        if m:
            out[decile] = {
                "mean_excess_pct": float(m.group(1)),
                "beta": float(m.group(2)),
                "alpha_pct": float(m.group(3)),
            }

    # ---- Panel B: Sharpe ratios ----
    # Header: | Decile | Sharpe ratio (monthly) | N months |  (3 cols total)
    # We use a 3-column pattern to disambiguate from Panel A's 12-col row.
    # To avoid matching the Panel A row's first 3 cols (which would mis-read
    # mean_excess as Sharpe), we require the line to be a SHORT row by
    # searching for the Panel B header as an anchor and scanning lines after.
    panel_b_marker = "## Panel B:"
    idx = md_text.find(panel_b_marker)
    if idx >= 0:
        panel_b_text = md_text[idx:]
        for decile in [f"D{i}" for i in range(1, 11)] + ["D1-D10"]:
            pattern = (
                rf"\|\s*{re.escape(decile)}\s*\|"
                rf"\s*({_NUM})\s*\|"   # Sharpe
                rf"\s*{_NUM}\s*\|"     # N months
            )
            m = re.search(pattern, panel_b_text)
            if m:
                sharpe = float(m.group(1))
                if decile in out:
                    out[decile]["sharpe"] = sharpe
                else:
                    out[decile] = {"sharpe": sharpe}
    return out


def parse_table_3(md_text: str) -> dict[str, dict[str, float]]:
    """Parse results/table_3.md for decile-level FF3/FF4/FF5 alphas."""
    out: dict[str, dict[str, float]] = {}
    # Header: | Portfolio | FF3 alpha | FF3 SE | FF3 t | FF4 alpha | ... | FF5 alpha | ... | FF5 t |
    for decile in [f"D{i}" for i in range(1, 11)] + ["D1-D10"]:
        pattern = (
            rf"\|\s*{re.escape(decile)}\s*\|"
            rf"\s*({_NUM})\s*\|"   # FF3 alpha
            rf"\s*{_NUM}\s*\|"    # FF3 SE
            rf"\s*{_NUM}\s*\|"    # FF3 t
            rf"\s*({_NUM})\s*\|"  # FF4 alpha
            rf"\s*{_NUM}\s*\|"    # FF4 SE
            rf"\s*{_NUM}\s*\|"    # FF4 t
            rf"\s*({_NUM})\s*\|"  # FF5 alpha
            rf"\s*{_NUM}\s*\|"    # FF5 SE
            rf"\s*{_NUM}\s*\|"    # FF5 t
        )
        m = re.search(pattern, md_text)
        if m:
            out[decile] = {
                "ff3_alpha": float(m.group(1)),
                "ff4_alpha": float(m.group(2)),
                "ff5_alpha": float(m.group(3)),
            }
    return out


def parse_table_5(md_text: str) -> dict[str, float]:
    """Parse results/table_5.md for subsample mean excess D1-D10 spread
    AND per-decile D1/D10 means for selected subsamples.

    Returns a dict with both kinds of keys:
      - "1963-1973" -> D1-D10 spread (mean excess %, per month)
      - "Mean_D1_1963_1973" -> D1 mean excess (%, per month)
      - "Mean_D10_1963_1973" -> D10 mean excess (%, per month)
      - ... etc.
    """
    out: dict[str, float] = {}
    label_map = {
        "1963-1973": "1963-1973",
        "1973-1983": "1973-1983",
        "1983-1993": "1983-1993",
        "1993-2003": "1993-2003",
        "2003-2014": "2003-2014",
    }

    # ---- Spread rows: support two formats:
    #   (a) New: | Spread | <label> | Start | End | Mean Excess | SE | t-stat | N months |
    #   (b) Old: | <label> | Start | End | Mean Excess | SE | t-stat | N months |
    for label in label_map:
        if label in out:
            continue  # already matched
        pattern_new = (
            rf"\|\s*Spread\s*\|\s*{re.escape(label)}\s*\|"
            rf"\s*\d{{4}}-\d{{2}}-\d{{2}}\s*\|"
            rf"\s*\d{{4}}-\d{{2}}-\d{{2}}\s*\|"
            rf"\s*({_NUM})\s*\|"
        )
        pattern_old = (
            rf"\|\s*{re.escape(label)}\s*\|"
            rf"\s*\d{{4}}-\d{{2}}-\d{{2}}\s*\|"
            rf"\s*\d{{4}}-\d{{2}}-\d{{2}}\s*\|"
            rf"\s*({_NUM})\s*\|"
        )
        for pat in (pattern_new, pattern_old):
            m = re.search(pat, md_text)
            if m:
                out[label] = float(m.group(1))
                break

    # ---- Per-decile D1/D10 rows: | Decile | Subsample | Start | End | Mean Excess | SE | t-stat | N months |
    per_decile_subsamples = {
        "Mean_D1_1963_1973": ("D1", "1963-1973"),
        "Mean_D10_1963_1973": ("D10", "1963-1973"),
        "Mean_D1_1983_1993": ("D1", "1983-1993"),
        "Mean_D10_1983_1993": ("D10", "1983-1993"),
        "Mean_D1_2003_2014": ("D1", "2003-2014"),
        "Mean_D10_2003_2014": ("D10", "2003-2014"),
    }
    for metric_name, (decile, label) in per_decile_subsamples.items():
        pattern = (
            rf"\|\s*{re.escape(decile)}\s*\|"
            rf"\s*{re.escape(label)}\s*\|"
            rf"\s*\d{{4}}-\d{{2}}-\d{{2}}\s*\|"
            rf"\s*\d{{4}}-\d{{2}}-\d{{2}}\s*\|"
            rf"\s*({_NUM})\s*\|"
        )
        m = re.search(pattern, md_text)
        if m:
            out[metric_name] = float(m.group(1))
    return out


def parse_table_10(md_text: str) -> dict[str, float]:
    """Parse results/table_10.md for the dur x RIOR cell values + spreads."""
    out: dict[str, float] = {}

    # Main 5x5 matrix
    matrix: dict[tuple[int, int], float] = {}
    for dur_q in range(1, 6):
        for rior_q in range(1, 6):
            pattern = (
                rf"\|\s*Q{dur_q}\s*\|[^|\n]*\|[^|\n]*\|[^|\n]*\|[^|\n]*\|[^|\n]*\|"
            )
            # Match each cell by column. Use the row then columns.
            row_re = (
                rf"\|\s*Q{dur_q}\s*\|"
                rf"\s*({_NUM})\s*\|"   # Q1
                rf"\s*({_NUM})\s*\|"   # Q2
                rf"\s*({_NUM})\s*\|"   # Q3
                rf"\s*({_NUM})\s*\|"   # Q4
                rf"\s*({_NUM})\s*\|"   # Q5
                rf"\s*{_NUM}\s*\|"     # D1-D5
            )
            m = re.search(row_re, md_text)
            if m:
                matrix[(dur_q, 1)] = float(m.group(1))
                matrix[(dur_q, 2)] = float(m.group(2))
                matrix[(dur_q, 3)] = float(m.group(3))
                matrix[(dur_q, 4)] = float(m.group(4))
                matrix[(dur_q, 5)] = float(m.group(5))

    # Build named cell keys
    out["matrix"] = matrix  # type: ignore[assignment]

    # Spread cells. The metric names in tables_to_replicate.json use mixed
    # conventions: some have a "Mean_" prefix (Mean_LowRIOR_LowDur), others
    # do not (RIOR2_LowDur). Store both keys for full coverage.
    # - Low RIOR (Q1) LowDur (Q1) = matrix[(1, 1)]
    # - Low RIOR (Q1) HighDur (Q5) = matrix[(5, 1)]
    # - High RIOR (Q5) LowDur (Q1) = matrix[(1, 5)]
    # - High RIOR (Q5) HighDur (Q5) = matrix[(5, 5)]
    out["Mean_LowRIOR_LowDur"] = matrix[(1, 1)]
    out["Mean_LowRIOR_HighDur"] = matrix[(5, 1)]
    out["Mean_LowRIOR_D1_minus_D5"] = matrix[(1, 1)] - matrix[(5, 1)]
    out["Mean_HighRIOR_LowDur"] = matrix[(1, 5)]
    out["Mean_HighRIOR_HighDur"] = matrix[(5, 5)]
    out["Mean_HighRIOR_D1_minus_D5"] = matrix[(1, 5)] - matrix[(5, 5)]
    out["LowRIOR_RIOR1_minus_RIOR5_LowDur"] = matrix[(1, 1)] - matrix[(1, 5)]
    out["LowRIOR_RIOR1_minus_RIOR5_HighDur"] = matrix[(5, 1)] - matrix[(5, 5)]
    # RIOR2,3,4 D1-D5 spreads — target metric names omit the "Mean_" prefix
    for rior_q in [2, 3, 4]:
        out[f"RIOR{rior_q}_LowDur"] = matrix[(1, rior_q)]
        out[f"RIOR{rior_q}_HighDur"] = matrix[(5, rior_q)]
        out[f"RIOR{rior_q}_D1_minus_D5"] = matrix[(1, rior_q)] - matrix[(5, rior_q)]
    return out


# ---- Per-table metric evaluation -------------------------------------------
def eval_table_1(metrics_target: dict, parsed: dict) -> dict:
    """Return {metric_name: replicated_value} and per-cell statuses."""
    out_repl: dict[str, float | None] = {}
    statuses: list[dict] = []
    for m in metrics_target:
        name = m["name"]
        target = m["value"]
        tol = m["tolerance_pct"]
        var = name.split("_", 1)[1].lower()  # Mean_Dur -> dur; Mean_BM -> bm; Mean_ME -> me
        if var == "me":
            var = "me_mil"  # panel uses me_mil
        stat = name.split("_")[0].lower()  # Mean -> mean; Std -> std
        if var not in parsed:
            out_repl[name] = None
            statuses.append({
                "name": name, "target": target, "ours": None,
                "tolerance_pct": tol, "status": "MISSING",
                "abs_err": None, "rel_err_pct": None,
            })
            continue
        v = parsed[var].get(stat)
        out_repl[name] = v
        if v is None:
            statuses.append({
                "name": name, "target": target, "ours": None,
                "tolerance_pct": tol, "status": "MISSING",
                "abs_err": None, "rel_err_pct": None,
            })
            continue
        status = _classify(v, target, tol)
        statuses.append({
            "name": name, "target": target, "ours": v,
            "tolerance_pct": tol, "status": status,
            "abs_err": v - target,
            "rel_err_pct": abs(v - target) / abs(target) * 100.0 if target != 0 else None,
        })
    return {"replicated": out_repl, "statuses": statuses}


def eval_table_2(metrics_target: dict, parsed: dict) -> dict:
    """Mean_D1..Mean_D10, Mean_D1_minus_D10, Beta_D1, Beta_D10,
    Beta_D1_minus_D10, Alpha_D1, Alpha_D10, Alpha_D1_minus_D10,
    Sharpe_D1, Sharpe_D10, Sharpe_D1_minus_D10."""
    out_repl: dict[str, float | None] = {}
    statuses: list[dict] = []

    # Mapping from target metric name to (decile key, stat key) in parsed
    field_map = {
        "Mean_D1": ("D1", "mean_excess_pct"),
        "Mean_D2": ("D2", "mean_excess_pct"),
        "Mean_D3": ("D3", "mean_excess_pct"),
        "Mean_D4": ("D4", "mean_excess_pct"),
        "Mean_D5": ("D5", "mean_excess_pct"),
        "Mean_D6": ("D6", "mean_excess_pct"),
        "Mean_D7": ("D7", "mean_excess_pct"),
        "Mean_D8": ("D8", "mean_excess_pct"),
        "Mean_D9": ("D9", "mean_excess_pct"),
        "Mean_D10": ("D10", "mean_excess_pct"),
        "Mean_D1_minus_D10": ("D1-D10", "mean_excess_pct"),
        "Beta_D1": ("D1", "beta"),
        "Beta_D10": ("D10", "beta"),
        "Beta_D1_minus_D10": ("D1-D10", "beta"),
        "Alpha_D1": ("D1", "alpha_pct"),
        "Alpha_D10": ("D10", "alpha_pct"),
        "Alpha_D1_minus_D10": ("D1-D10", "alpha_pct"),
        "Sharpe_D1": ("D1", "sharpe"),
        "Sharpe_D10": ("D10", "sharpe"),
        "Sharpe_D1_minus_D10": ("D1-D10", "sharpe"),
    }

    for m in metrics_target:
        name = m["name"]
        target = m["value"]
        tol = m["tolerance_pct"]
        decile, stat = field_map[name]
        if decile not in parsed:
            out_repl[name] = None
            status_str = "MISSING"
            v = None
        else:
            v = parsed[decile].get(stat)
            out_repl[name] = v
            if v is None:
                status_str = "MISSING"
            else:
                status_str = _classify(v, target, tol)
        statuses.append({
            "name": name, "target": target, "ours": v,
            "tolerance_pct": tol, "status": status_str,
            "abs_err": (v - target) if v is not None else None,
            "rel_err_pct": (
                abs(v - target) / abs(target) * 100.0 if (v is not None and target != 0)
                else None
            ),
        })
    return {"replicated": out_repl, "statuses": statuses}


def eval_table_3(metrics_target: dict, parsed: dict) -> dict:
    """AlphaFF3_D1..D10, AlphaFF3_D1_minus_D10, AlphaFF4_D1_minus_D10, AlphaFF5_D1_minus_D10."""
    out_repl: dict[str, float | None] = {}
    statuses: list[dict] = []
    field_map = {
        "AlphaFF3_D1": ("D1", "ff3_alpha"),
        "AlphaFF3_D2": ("D2", "ff3_alpha"),
        "AlphaFF3_D3": ("D3", "ff3_alpha"),
        "AlphaFF3_D4": ("D4", "ff3_alpha"),
        "AlphaFF3_D5": ("D5", "ff3_alpha"),
        "AlphaFF3_D6": ("D6", "ff3_alpha"),
        "AlphaFF3_D7": ("D7", "ff3_alpha"),
        "AlphaFF3_D8": ("D8", "ff3_alpha"),
        "AlphaFF3_D9": ("D9", "ff3_alpha"),
        "AlphaFF3_D10": ("D10", "ff3_alpha"),
        "AlphaFF3_D1_minus_D10": ("D1-D10", "ff3_alpha"),
        "AlphaFF4_D1_minus_D10": ("D1-D10", "ff4_alpha"),
        "AlphaFF5_D1_minus_D10": ("D1-D10", "ff5_alpha"),
    }
    for m in metrics_target:
        name = m["name"]
        target = m["value"]
        tol = m["tolerance_pct"]
        decile, stat = field_map[name]
        if decile not in parsed:
            out_repl[name] = None
            status_str = "MISSING"
            v = None
        else:
            v = parsed[decile].get(stat)
            out_repl[name] = v
            if v is None:
                status_str = "MISSING"
            else:
                status_str = _classify(v, target, tol)
        statuses.append({
            "name": name, "target": target, "ours": v,
            "tolerance_pct": tol, "status": status_str,
            "abs_err": (v - target) if v is not None else None,
            "rel_err_pct": (
                abs(v - target) / abs(target) * 100.0 if (v is not None and target != 0)
                else None
            ),
        })
    return {"replicated": out_repl, "statuses": statuses}


def eval_table_5(metrics_target: dict, parsed: dict) -> dict:
    """Mean_D1_minus_D10_<period> spread for 5 subsamples + 6 D1/D10 means."""
    out_repl: dict[str, float | None] = {}
    statuses: list[dict] = []
    field_map = {
        "Mean_D1_minus_D10_1963_1973": "1963-1973",
        "Mean_D1_minus_D10_1973_1983": "1973-1983",
        "Mean_D1_minus_D10_1983_1993": "1983-1993",
        "Mean_D1_minus_D10_1993_2003": "1993-2003",
        "Mean_D1_minus_D10_2003_2014": "2003-2014",
        # Per-decile D1/D10 means for selected subsamples
        "Mean_D1_1963_1973": "Mean_D1_1963_1973",
        "Mean_D10_1963_1973": "Mean_D10_1963_1973",
        "Mean_D1_1983_1993": "Mean_D1_1983_1993",
        "Mean_D10_1983_1993": "Mean_D10_1983_1993",
        "Mean_D1_2003_2014": "Mean_D1_2003_2014",
        "Mean_D10_2003_2014": "Mean_D10_2003_2014",
    }
    for m in metrics_target:
        name = m["name"]
        target = m["value"]
        tol = m["tolerance_pct"]
        if name in field_map:
            v = parsed.get(field_map[name])
            out_repl[name] = v
            status_str = _classify(v, target, tol) if v is not None else "MISSING"
        else:
            v = None
            out_repl[name] = None
            status_str = "MISSING"
        statuses.append({
            "name": name, "target": target, "ours": v,
            "tolerance_pct": tol, "status": status_str,
            "abs_err": (v - target) if v is not None else None,
            "rel_err_pct": (
                abs(v - target) / abs(target) * 100.0 if (v is not None and target != 0)
                else None
            ),
        })
    return {"replicated": out_repl, "statuses": statuses}


def eval_table_10(metrics_target: dict, parsed: dict) -> dict:
    """17 cells from Table 10 (Dur x RIOR)."""
    out_repl: dict[str, float | None] = {}
    statuses: list[dict] = []
    for m in metrics_target:
        name = m["name"]
        target = m["value"]
        tol = m["tolerance_pct"]
        v = parsed.get(name)
        out_repl[name] = v
        if v is None:
            status_str = "MISSING"
        else:
            status_str = _classify(v, target, tol)
        statuses.append({
            "name": name, "target": target, "ours": v,
            "tolerance_pct": tol, "status": status_str,
            "abs_err": (v - target) if v is not None else None,
            "rel_err_pct": (
                abs(v - target) / abs(target) * 100.0 if (v is not None and target != 0)
                else None
            ),
        })
    return {"replicated": out_repl, "statuses": statuses}


# ---- Main ------------------------------------------------------------------
def main():
    print(f"[evaluate] SLUG: {SLUG}")
    targets_path = INPUTS_DIR / "tables_to_replicate.json"
    print(f"[evaluate] Loading targets: {targets_path}")
    raw = targets_path.read_text()
    # Fix known JSON syntax issue: unescaped double-quote inside a notes string.
    # The single offender is in T1 notes: ...paper's "restricted" sample...
    # Replace the literal quotes with escaped quotes to make it valid JSON.
    raw = raw.replace(
        'paper\'s "restricted" sample',
        "paper's \\\"restricted\\\" sample",
    )
    targets_doc = json.loads(raw)
    tables = targets_doc["tables"]

    # ---- Parse result tables ----
    table_paths = {
        "T1": RESULTS_DIR / "table_1.md",
        "T2": RESULTS_DIR / "table_2.md",
        "T3": RESULTS_DIR / "table_3.md",
        "T5": RESULTS_DIR / "table_5.md",
        "T10": RESULTS_DIR / "table_10.md",
    }
    table_text: dict[str, str] = {}
    for tid, p in table_paths.items():
        if not p.exists():
            print(f"[evaluate] WARNING: {p} not found")
            table_text[tid] = ""
        else:
            table_text[tid] = p.read_text()

    parsed = {
        "T1": parse_table_1(table_text["T1"]),
        "T2": parse_table_2(table_text["T2"]),
        "T3": parse_table_3(table_text["T3"]),
        "T5": parse_table_5(table_text["T5"]),
        "T10": parse_table_10(table_text["T10"]),
    }

    # ---- Evaluate each table ----
    evals = {
        "T1": eval_table_1(
            tables[0]["metrics"], parsed["T1"]),
        "T2": eval_table_2(
            tables[1]["metrics"], parsed["T2"]),
        "T3": eval_table_3(
            tables[2]["metrics"], parsed["T3"]),
        "T5": eval_table_5(
            tables[3]["metrics"], parsed["T5"]),
        "T10": eval_table_10(
            tables[4]["metrics"], parsed["T10"]),
    }

    # ---- Per-cell print ----
    all_statuses: list[dict] = []
    for tid in ["T1", "T2", "T3", "T5", "T10"]:
        ev = evals[tid]
        print()
        print(f"=== Table {tid[1:]} ===")
        print(f"{'Metric':<40s} {'Target':>10s} {'Ours':>10s} "
              f"{'Tol%':>6s} {'Status':<10s} {'RelErr%':>10s}")
        print("-" * 92)
        for st in ev["statuses"]:
            ours = _fmt(st["ours"])
            target = f"{st['target']:.3f}"
            rel = f"{st['rel_err_pct']:.1f}" if st["rel_err_pct"] is not None else "-"
            print(
                f"{st['name']:<40s} {target:>10s} {ours:>10s} "
                f"{st['tolerance_pct']:>6.0f} {st['status']:<10s} {rel:>10s}"
            )
        all_statuses.extend(ev["statuses"])

    # ---- Aggregate tally ----
    counts = {"Match": 0, "FAIL": 0, "MISSING": 0, "SKIP": 0}
    for st in all_statuses:
        counts[st["status"]] = counts.get(st["status"], 0) + 1
    n_total = len(all_statuses)
    n_scored = counts["Match"] + counts["FAIL"]
    hit_rate = (counts["Match"] / n_scored) if n_scored > 0 else float("nan")

    print()
    print("=" * 72)
    print(f"Total cells: {n_total}")
    print(f"  Match:    {counts['Match']}")
    print(f"  FAIL:     {counts['FAIL']}")
    print(f"  MISSING:  {counts['MISSING']}")
    print(f"  SKIP:     {counts['SKIP']}")
    print(f"  Hit rate (Match / (Match + FAIL)): "
          f"{hit_rate:.1%}" if not (hit_rate != hit_rate) else "  Hit rate: N/A")
    print("=" * 72)

    # ---- Headline metric ----
    headline_target = tables[1]["metrics"]  # T2
    headline_cell = next(m for m in headline_target if m["name"] == "Mean_D1_minus_D10")
    headline_ours = evals["T2"]["replicated"]["Mean_D1_minus_D10"]
    headline_status = next(
        s for s in evals["T2"]["statuses"] if s["name"] == "Mean_D1_minus_D10"
    )
    print()
    print("HEADLINE METRIC (T2 Mean_D1_minus_D10, %/month):")
    print(f"  Paper target: {headline_cell['value']:.3f} "
          f"(tolerance ±{headline_cell['tolerance_pct']}%)")
    print(f"  Our replication: {headline_ours:.3f} "
          f"(rel err {headline_status['rel_err_pct']:.1f}%)")
    print(f"  Status: {headline_status['status']}")
    print()

    # ---- Write eval/metrics.json ----
    # Scorer input format: {metric_name: {"value": X, "unit": ...}}.
    # Cells with `st["ours"] is None` are OMITTED from `metrics` (the
    # canonical scorer treats a missing key as MISSING — same effect
    # without emitting "value": null, which the validator rejects).
    metrics: dict[str, dict[str, Any]] = {}
    for st in all_statuses:
        if st["ours"] is None:
            continue  # OMIT; canonical scorer classifies missing key as MISSING
        # Find unit from targets
        unit = ""
        for tbl in tables:
            for m in tbl["metrics"]:
                if m["name"] == st["name"]:
                    unit = m.get("unit", "")
                    break
        metrics[st["name"]] = {
            "value": float(st["ours"]),
            "unit": unit,
            "status": st["status"],
            "target": st["target"],
            "tolerance_pct": st["tolerance_pct"],
        }

    out_metrics = {
        "schema_version": 2,
        "slug": SLUG,
        "tally": counts,
        "total_cells": n_total,
        "hit_rate": hit_rate if not (hit_rate != hit_rate) else None,
        "headline": {
            "metric": "Mean_D1_minus_D10",
            "paper": headline_cell["value"],
            "ours": headline_ours,
            "status": headline_status["status"],
            "tolerance_pct": headline_cell["tolerance_pct"],
        },
        "metrics": metrics,
    }
    out_path = EVAL_DIR / "metrics.json"
    out_path.write_text(json.dumps(out_metrics, indent=2, default=str))
    print(f"[evaluate] Wrote {out_path}")

    # Exit non-zero only if all targets are MISSING (a clear failure)
    if counts["Match"] == 0 and counts["FAIL"] == 0 and counts["MISSING"] > 0:
        print("[evaluate] All cells MISSING -- something is broken")
        sys.exit(2)


if __name__ == "__main__":
    main()
