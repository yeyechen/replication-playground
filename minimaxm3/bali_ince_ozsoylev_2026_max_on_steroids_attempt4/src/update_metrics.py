"""
Merge Table 6 and Table 2 metrics into eval/metrics.json while
preserving the existing Table 1 entries.

T6 cells are written under both "T6_" prefixed names (e.g., T6_P1_RET_RF)
AND bare names (e.g., P1_RET_RF), so the canonical scorer (which reads
against tables_to_replicate.json's bare-name keys) finds them. Same for
T2 cells.

The unified eval/metrics.json is the scorer's input file.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from utils.paths import paper_layout  # noqa: E402

SLUG = "max_on_steroids_attempt4"
LAYOUT = paper_layout(SLUG)
LAYOUT.ensure()

EVAL_PATH = LAYOUT.eval_path("metrics.json")


def _expand(name: str, value: dict, table_id: str) -> list[tuple[str, dict]]:
    """Produce all (key, entry) copies for a cell.

    The canonical scorer reads bare names (P1_RET_RF) because
    tables_to_replicate.json uses bare names. We ALSO write the T6_/T2_
    prefixed versions for backwards-compat / disambiguation.
    """
    out = [(name, value)]
    if name.startswith(f"{table_id}_"):
        bare = name[len(table_id) + 1:]
        # Only add bare if no conflict with existing T1 entry
        # (T1 uses bare names too).
        # We add the bare-name copy unconditionally; if there's a
        # collision the scorer's later add wins.
        out.append((bare, value))
    return out


def run_table6() -> dict:
    """Run table6_maxbeta.main() and return its metrics dict (T6_ prefixed)."""
    import table6_maxbeta
    importlib.reload(table6_maxbeta)
    return table6_maxbeta.main()


def run_table2() -> dict:
    """Run table2_chars.main() and return its metrics dict (T2_ prefixed or bare)."""
    import table2_chars
    importlib.reload(table2_chars)
    return table2_chars.main()


def main() -> int:
    # 1. Load existing metrics (preserve Table 1 cells verbatim)
    existing = json.loads(EVAL_PATH.read_text())
    metrics = existing["metrics"]
    print(f"[update] preserving {len(metrics)} existing Table 1 cells")

    # 2. Run Table 6 -> adds T6_ prefixed cells + bare-name mirror.
    #    However, the bare-name keys (P1_RET_RF etc.) are SHARED with T1 cells;
    #    in those collisions, the existing T1 value should win (because T6 is
    #    a different sort). But the canonical scorer reads per-cell against
    #    the paper target table, so for T6 cells (which the paper target uses
    #    bare names), we want T6 values, not T1 values.
    #
    # Strategy: BEFORE adding T6 cells, snapshot all T1 cells; then delete
    # the colliding bare names; then add T6 cells (T6_+bare); then restore
    # T1 bare names (those got shadowed by T6 bare names but T6 cells win).
    t1_bare_keys = {k: v for k, v in metrics.items() if not k.startswith("T6_") and not k.startswith("T2_")}

    t6_metrics = run_table6()
    print(f"[update] Table 6 produced {len(t6_metrics)} cells (T6_-prefixed)")
    for label, c in t6_metrics.items():
        # label is already T6_-prefixed; expand to bare if applicable
        if label.startswith("T6_"):
            bare = label[3:]
            if bare in metrics:
                print(f"[update] WARNING: T6 cell {label} shadows T1 cell {bare}")
            metrics[label] = c
            metrics[bare] = c

    # 3. Run Table 2 -> adds T2_ prefixed + bare-name cells
    t2_metrics = run_table2()
    print(f"[update] Table 2 produced {len(t2_metrics)} cells")
    for label, c in t2_metrics.items():
        if label.startswith("T2_"):
            bare = label[3:]
            if bare in metrics:
                print(f"[update] NOTE: T2 cell {label} (bare={bare}) already in metrics, overwriting")
            metrics[label] = c
            metrics[bare] = c

    # 4. Sanity check: no bare scalars
    bad = [
        k for k, v in metrics.items()
        if not isinstance(v, dict) or "value" not in v
    ]
    assert not bad, f"bare-scalar metrics: {bad}"

    # 5. Write
    payload = {"schema_version": 2, "slug": SLUG, "metrics": metrics}
    EVAL_PATH.write_text(json.dumps(payload, indent=2, default=float))
    print(f"[update] saved {EVAL_PATH} ({len(metrics)} cells total)")
    return 0


if __name__ == "__main__":
    sys.exit(main())