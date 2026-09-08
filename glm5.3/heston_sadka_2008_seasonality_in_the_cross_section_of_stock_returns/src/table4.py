"""Table 4 — WRSS profits pi_t(k) and sigma^2_mu (Heston & Sadka 2008, T4).

Paper L1192: for each ordered pair (t, k), k >= 1, within 1963-01..2002-12
(480 months), take the common cross-section of stocks with non-missing
returns in BOTH month t and month t-k; demean each month's return over
that common cross-section (equal-weighted); pi_t(k) = (1/N) sum_i
(r_i,t-k - mean_t-k)(r_i,t - mean_t), in decimals.

Groups over ALL pairs: all (k != 0), nonannual (k % 12 != 0), annual
(k % 12 == 0; within sample max k = 468). Table 4 mean = mean of pi over
the group's pairs x 100 (Assumption 9). SE = population std (ddof=0) of
the group's pi values / sqrt(500) (paper's 480-month/500 normalization,
L1192); t = mean / SE.
"""
import json

import numpy as np
import pandas as pd

from main import LAYOUT, _wide_matrix

T4_START = pd.Period("1963-01", freq="M")     # 480-month window (L1192)
T4_END = pd.Period("2002-12", freq="M")
SE_N = np.sqrt(500.0)                          # paper's sqrt(500) (L1192)


def table4(panel: pd.DataFrame, metrics: dict) -> dict:
    sub = panel[(panel["month"] >= T4_START) & (panel["month"] <= T4_END)]
    R, m_idx, months, permnos, _ = _wide_matrix(sub)
    assert len(months) == 480, f"expected 480 months, got {len(months)}"
    Rf = R.astype(np.float64)
    nan = np.isnan(Rf)
    n_rows = Rf.shape[0]

    pi = {g: [] for g in ("all", "nonannual", "annual")}
    for k in range(1, n_rows):                 # max k = 479; annual max 468
        A = Rf[:n_rows - k, :]                 # month t-k
        B = Rf[k:, :]                          # month t
        m = (~nan[:n_rows - k, :]) & (~nan[k:, :])
        n = m.sum(axis=1)
        valid = n >= 2
        if not valid.any():
            continue
        Av = np.where(m, A, 0.0)
        Bv = np.where(m, B, 0.0)
        mA = Av.sum(axis=1)[valid] / n[valid]
        mB = Bv.sum(axis=1)[valid] / n[valid]
        # iteration-9 fix: mask AFTER demeaning — missing stocks are
        # excluded from the covariance, never zero-filled (a zero-filled
        # cell contributes mA*mB per missing stock, a positive offset
        # that grows as the pair-common set shrinks)
        a = np.where(m[valid], A[valid] - mA[:, None], 0.0)
        b = np.where(m[valid], B[valid] - mB[:, None], 0.0)
        p = (a * b).sum(axis=1) / n[valid]
        pi["all"].append(p)
        if k % 12:
            pi["nonannual"].append(p)
        else:
            pi["annual"].append(p)
        if k % 60 == 0:
            print(f"[t4] k={k} done")

    out = {"pair_counts": {}, "sqrt500": SE_N}
    for g in ("all", "nonannual", "annual"):
        v = np.concatenate(pi[g])
        # iteration-11 fix (audit 1 [M1]): mean and SE must share units in
        # the t calculation. SE is in decimal^2, so t uses the decimal^2
        # mean; the reported mean stays in table units (x100, Assumption 9).
        mean = v.mean() * 100.0                # decimals^2 x 100 (Assumption 9)
        se_dec = v.std(ddof=0) / SE_N          # decimal^2
        t = v.mean() / se_dec                  # both decimal^2
        assert abs(t - mean / (se_dec * 100.0)) < 1e-12, "unit mismatch in t"
        se = se_dec
        out[g] = dict(mean=mean, t=t, se=se, n_pairs=len(v),
                      mean_dec=v.mean(), sd=v.std(ddof=0))
        out["pair_counts"][g] = len(v)
        metrics[f"t4_mean_{g}"] = {"value": round(mean, 4),
                                   "unit": "decimal_sq_x100"}
        metrics[f"t4_mean_{g}_t"] = {"value": round(t, 4), "unit": "t_stat"}
        print(f"[t4] {g}: mean={mean:.4f} t={t:.2f} "
              f"n_pairs={len(v):,} sd(pi)={v.std(ddof=0):.5f}")

    # implied cross-sectional SD of the seasonal component (paper: 1.15%)
    sd_month = float(np.sqrt(out["annual"]["mean_dec"]))
    out["implied_sd_monthly_pct"] = sd_month * 100.0
    metrics["diag_t4_implied_sd_monthly_pct"] = {
        "value": round(sd_month * 100.0, 4), "unit": "percent"}
    print(f"[t4] implied cross-sectional SD = {sd_month*100:.2f}%/month "
          "(paper 1.15%)")
    return out


def write_table4_md(out: dict) -> None:
    spec = json.loads(
        (LAYOUT.preparations_path("tables_to_replicate.json")).read_text())
    paper = {m["name"]: m for tb in spec["tables"] if tb["id"] == "T4"
             for m in tb["metrics"]}
    from evaluate import classify
    lines = [
        "# Table 4 — WRSS profits pi(k) grouped by lag (x100), "
        "1963-01 to 2002-12",
        "",
        "pi_t(k) computed on the common cross-section of stocks with returns "
        "in both months, demeaned within that cross-section (L1192). "
        "Group mean of pi x100; t = mean / (population SD / sqrt(500)).",
        "",
        "| Group | mean (x100) | t | paper | status | pairs |",
        "|---|---|---|---|---|---|",
    ]
    paper_mean = {"all": -0.0006, "nonannual": -0.0019, "annual": 0.0133}
    paper_t = {"all": -0.26, "nonannual": -0.65, "annual": 3.57}
    for g in ("all", "nonannual", "annual"):
        st = classify(float(out[g]["mean"]), paper_mean[g], 50,
                      paper[f"t4_mean_{g}"].get("absolute_band")
                      if f"t4_mean_{g}" in paper else None,
                      paper.get(f"t4_mean_{g}", {}).get("insignificant", False))
        lines.append(f"| {g} | {out[g]['mean']:.4f} | {out[g]['t']:.2f} | "
                     f"{paper_mean[g]:.4f} [{paper_t[g]:.2f}] | {st} | "
                     f"{out['pair_counts'][g]:,} |")
    lines += [
        "",
        f"Implied cross-sectional SD of the seasonal component: "
        f"sqrt(mean_annual) = {out['implied_sd_monthly_pct']:.2f}%/month "
        "(paper: 1.15%/month, L1195).",
    ]
    (LAYOUT.result_path("table_4.md")).write_text("\n".join(lines) + "\n")
