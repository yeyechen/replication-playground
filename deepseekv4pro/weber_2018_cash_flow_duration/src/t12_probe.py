"""T12 BM-conditional probe (audit1 M6). Scratch diagnostic — reproducible,
does NOT touch panel.parquet / metrics.json.

Probes:
  1. BM construction = BE(FYE calendar t-1) / ME(Dec t-1).
  2. T12 basket breakpoint (median BM of screened cross-section) per year + sizes.
  3. D3 sign-flip cell composition + alpha sensitivity to the BM-split position.
"""
from __future__ import annotations
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, ".")
sys.path.insert(0, "replications/weber_2018_attempt2_deepseek/src")

import numpy as np
import pandas as pd
import table10_12 as t


def main():
    cs = t.load_t10_cross_section("allstock")
    panel = t._load_return_panel()
    factors = t._load_factors()

    print("=== 1. BM construction ===")
    print("cs has columns: me_dec_m (Dec t-1 ME, $M), be (book equity, $M), bm=be/me_dec_m")
    print("BM sample:", cs["bm"].notna().sum(), "of", len(cs))
    print()

    d = cs.dropna(subset=["dur_q", "rior", "bm"]).copy()
    med = d.groupby("t")["bm"].median().rename("med_bm")
    d = d.merge(med, on="t", how="left")
    d["basket"] = np.where(d["bm"] <= d["med_bm"], "s", "l")

    print("=== 2. Basket breakpoint (median BM, per year) ===")
    yearly = d.groupby("t")["bm"].median()
    print("median BM across years: mean=%.4f, min=%.4f, max=%.4f" % (
        yearly.mean(), yearly.min(), yearly.max()))
    sz = d.groupby("t")["basket"].value_counts().unstack()
    print("total growth(s) firms:", (d.basket == "s").sum(),
          " total value(l) firms:", (d.basket == "l").sum())
    print("median growth/year:", sz["s"].median(),
          " median value/year:", sz["l"].median())
    print("growth/value ratio (should be ~1):",
          round((d.basket == "s").sum() / max(1, (d.basket == "l").sum()), 3))
    print()

    print("=== 3. D3 cell composition ===")
    d["dq"] = t._assign_tertile(d, "dur_q")
    d["rq"] = t._assign_tertile(d, "rior")

    cells = [("s", 1, 3, "lowrior_GROWTH_D3"),
             ("l", 1, 3, "lowrior_VALUE_D3"),
             ("s", 2, 3, "midrior_GROWTH_D3"),
             ("l", 2, 3, "midrior_VALUE_D3"),
             ("s", 3, 3, "highrior_GROWTH_D3"),
             ("l", 3, 3, "highrior_VALUE_D3")]
    for basket, rq, dq, label in cells:
        sub = d[(d.basket == basket) & (d.rq == rq) & (d.dq == dq)]
        n = len(sub)
        ny = sub["t"].nunique()
        print("%-22s n=%5d  ny=%2d  n_per_month~%5.1f  medME=%7.1fM  "
              "medBM=%.3f  meanBM=%.3f" % (
                  label, n, ny, n / max(1, ny),
                  sub["me_jun"].median() / 1e6, sub["bm"].median(), sub["bm"].mean()))
    print()

    # Full 64-cell grid under current (median-of-screened-sample) split
    print("=== 4. T12 grid under CURRENT split (median of screened sample) ===")
    res12 = t.compute_table12(cs, panel, factors)
    print_t12(res12)


def print_t12(r):
    rows = [("lowrior", "D1"), ("lowrior", "D2"), ("lowrior", "D3"),
            ("rior", "D1"), ("rior", "D2"), ("rior", "D3"),
            ("highrior", "D1"), ("highrior", "D2"), ("highrior", "D3")]
    print("   cell                         s(growth)   l(value)")
    for rn, dn in rows:
        a = r.get(f"t12_{rn}_s_{dn}")
        b = r.get(f"t12_{rn}_l_{dn}")
        print("   t12_%-8s_%-3s        %8.3f   %8.3f" % (rn, dn,
              (a if pd.notna(a) else float("nan")),
              (b if pd.notna(b) else float("nan"))))
    print("   ---- D1-D3 spread (alpha of D1-D3) ----")
    for rn in ("lowrior", "rior", "highrior"):
        a = r.get(f"t12_{rn}_s_D1D3")
        b = r.get(f"t12_{rn}_l_D1D3")
        print("   t12_%-8s_D1D3        %8.3f   %8.3f" % (rn, a, b))


if __name__ == "__main__":
    main()
