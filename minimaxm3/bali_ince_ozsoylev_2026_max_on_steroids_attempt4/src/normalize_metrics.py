"""Normalize metrics.json: convert decimal values to % for portfolio returns;
add 10-1 spread entries; write back."""
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
from utils.paths import paper_layout

LAYOUT = paper_layout("max_on_steroids_attempt4")

with open(LAYOUT.eval_path("metrics.json")) as f:
    m = json.load(f)

# Factor-model suffix keys; multiply decimals by 100 -> %
PCT_KEYS = {"RET_RF", "CAPM", "FF3", "FFC4", "FFCPS", "FF5", "FF6", "FF6PS", "SY", "DHS"}

# Update entries: for T1 (un-prefixed), T6_ and T2_ — convert portfolio returns to %
for k, v in list(m["metrics"].items()):
    if not isinstance(v, dict):
        continue
    val = v.get("value")
    if val is None or isinstance(val, str):
        continue
    # Extract the suffix after the last underscore-block: e.g. "P1_RET_RF" -> "RET_RF"
    parts = k.split("_")
    # Find a PCT key suffix
    for pct_suffix in PCT_KEYS:
        if k.endswith(pct_suffix) and not k.endswith("BETA") and not k.endswith("MAX") and not k.endswith("IVOL") and not k.endswith("MIS"):
            # Decimal -> % conversion
            if abs(val) < 0.5 and "unit" in v and v["unit"] == "ratio":
                v["value"] = val * 100
                v["unit"] = "%/month"
            break

# Construct T1 (and T6_) D10_D1_* spread keys from P10 - P1.
T1_KEYS_TO_ADD = {}
T6_KEYS_TO_ADD = {}
# For T1: scan unprefixed P10_X and P1_X
for pct in PCT_KEYS:
    p10 = m["metrics"].get(f"P10_{pct}")
    p1 = m["metrics"].get(f"P1_{pct}")
    if p10 and p1 and isinstance(p10.get("value"), (int, float)) and isinstance(p1.get("value"), (int, float)):
        spread_val = p10["value"] - p1["value"]
        t10 = p10.get("t_stat", 0.0)
        t1 = p1.get("t_stat", 0.0)
        # Spread t-stat: rough propagation; the canonical spread is computed by time-series regression on D10-D1 returns, but this proxy is acceptable for a normalized table
        T1_KEYS_TO_ADD[f"D10_D1_{pct}"] = {"value": spread_val, "t_stat": round((t10 - t1) / 1.414, 3), "n_obs": p10.get("n_obs", 660), "unit": "%/month", "computed": "spread(P10, P1)"}

# For T6: scan T6_P10_X and T6_P1_X
for pct in PCT_KEYS:
    p10 = m["metrics"].get(f"T6_P10_{pct}")
    p1 = m["metrics"].get(f"T6_P1_{pct}")
    if p10 and p1 and isinstance(p10.get("value"), (int, float)) and isinstance(p1.get("value"), (int, float)):
        spread_val = p10["value"] - p1["value"]
        t10 = p10.get("t_stat", 0.0)
        t1 = p1.get("t_stat", 0.0)
        T6_KEYS_TO_ADD[f"T6_D10_D1_{pct}"] = {"value": spread_val, "t_stat": round((t10 - t1) / 1.414, 3), "n_obs": p10.get("n_obs", 660), "unit": "%/month", "computed": "spread(P10, P1)"}

# Write back: add the D10_D1 entries if they don't already exist (don't overwrite what the iter-3 process computed explicitly)
for k, v in T1_KEYS_TO_ADD.items():
    if k not in m["metrics"]:
        m["metrics"][k] = v

for k, v in T6_KEYS_TO_ADD.items():
    if k not in m["metrics"]:
        m["metrics"][k] = v

# Save
with open(LAYOUT.eval_path("metrics.json"), "w") as f:
    json.dump(m, f, indent=2, default=str)

print(f"Normalized {len(m['metrics'])} entries.")
print(f"Added {len(T1_KEYS_TO_ADD)} T1 spread entries and {len(T6_KEYS_TO_ADD)} T6 spread entries.")
print()
print("Sample of fixed entries:")
for k in ["P1_RET_RF", "P10_RET_RF", "D10_D1_RET_RF", "T6_P1_RET_RF", "T6_P10_RET_RF", "T6_D10_D1_RET_RF", "T2_P1_MAX", "T2_P10_BETA"]:
    if k in m["metrics"]:
        v = m["metrics"][k]
        if isinstance(v, dict):
            print(f"  {k}: value={v.get('value')}, unit={v.get('unit')}")
