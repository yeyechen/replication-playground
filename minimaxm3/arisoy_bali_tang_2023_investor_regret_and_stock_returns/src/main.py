"""
Replication of Arisoy, Bali, Tang (2023) "Investor Regret and Stock Returns".

Task 1 — Data pipeline build:
  - PIT-filtered universe (1963-06 to 2020-12)
  - REG signal: -(R_{i,t} - max_j[R_{j,t}]) over 3-digit SIC peers
  - Monthly panel with REG, next-month excess return, ME_lag1, controls
  - Fama-French factor loads (FF3, FF4/FFC, FF5)

Universe: shrcd IN (10, 11), exchcd IN (1, 2, 3), $5 <= |prc| <= $1000.
Sample: July 1963 to December 2020 (sort month), ret t+1 in [1963-08, 2020-12].

Task 2 — Table 1 replication (see analysis_table1.py):
  - Winsorize REG at 1%/99% per month.
  - NYSE-only 20/40/60/80 percentiles of REG, assign quintiles 1..5.
  - VW excess returns (me_lag1-weighted) per (month, quintile).
  - Time-series regressions with Newey-West (1987) 6 lags.
  - Output: results/table_1.md + eval/metrics.json.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Repo paths
REPO_ROOT = Path("/home/ra_alan_mike_share/rep-it-up")
sys.path.insert(0, str(REPO_ROOT))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO_ROOT / ".env")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from clickhouse_driver import Client  # noqa: E402

from utils.paths import paper_layout  # noqa: E402

# ----------------------------------------------------------------------
# Layout / ClickHouse
# ----------------------------------------------------------------------

SLUG = "arisoy_bali_tang_2023_investor_regret_and_stock_returns"
LAYOUT = paper_layout(SLUG)
LAYOUT.ensure()
SQL_DIR = LAYOUT.src_path("sql")


def _client() -> Client:
    return Client(
        host=os.getenv("CLICKHOUSE_HOST"),
        port=int(os.getenv("CLICKHOUSE_PORT", 9000)),
        user=os.getenv("CLICKHOUSE_USER"),
        password=os.getenv("CLICKHOUSE_PASSWORD"),
        settings={"max_execution_time": 600},
    )


def q(sql: str) -> pd.DataFrame:
    """Execute a SQL string (or path to .sql file) and return a DataFrame."""
    if Path(sql).is_file() and sql.endswith(".sql"):
        sql = Path(sql).read_text()
    c = _client()
    data, cols = c.execute(sql, with_column_types=True)
    return pd.DataFrame(data, columns=[x[0] for x in cols])


def q_file(name: str) -> pd.DataFrame:
    """Execute a saved SQL file under src/sql/."""
    return q(str(SQL_DIR / name))


def run_ddl_file(name: str) -> None:
    """Execute a DDL .sql file (statements separated by ';') and ignore results."""
    sql = (SQL_DIR / name).read_text()
    # Strip line comments first (preserving semicolons inside comments).
    cleaned_lines = []
    for line in sql.split("\n"):
        idx = line.find("--")
        cleaned_lines.append(line[:idx] if idx >= 0 else line)
    cleaned = "\n".join(cleaned_lines)
    stmts = [s.strip() for s in cleaned.split(";") if s.strip()]
    c = _client()
    for stmt in stmts:
        c.execute(stmt)


# ----------------------------------------------------------------------
# Pipeline orchestration
# ----------------------------------------------------------------------


def build_universe() -> None:
    print("[1/4] Building PIT-filtered monthly universe (write_yeye.arb_universe)...")
    run_ddl_file("01_universe.sql")
    n = q("SELECT count(), uniqExact(permno), uniqExact(month) FROM write_yeye.arb_universe").iloc[0]
    print(f"      -> {n.iloc[0]:,} rows | {n.iloc[1]:,} permnos | {n.iloc[2]:,} months")


def build_reg() -> None:
    print("[2/4] Computing REG signal (write_yeye.arb_reg)...")
    run_ddl_file("02_reg_signal.sql")
    n = q("SELECT count(), uniqExact(permno) FROM write_yeye.arb_reg").iloc[0]
    print(f"      -> {n.iloc[0]:,} rows | {n.iloc[1]:,} permnos")


def build_panel() -> pd.DataFrame:
    print("[3/4] Assembling monthly panel (write_yeye.arb_panel)...")
    run_ddl_file("03_panel.sql")
    n = q("SELECT count(), uniqExact(permno), uniqExact(month) FROM write_yeye.arb_panel").iloc[0]
    print(f"      -> {n.iloc[0]:,} rows | {n.iloc[1]:,} permnos | {n.iloc[2]:,} months")
    return q("SELECT * FROM write_yeye.arb_panel ORDER BY month, permno")


def build_ff_factors() -> pd.DataFrame:
    print("[4/8] Pulling Fama-French factors (write_yeye.arb_ff)...")
    run_ddl_file("04_ff_factors.sql")
    n = q("SELECT count(), min(month), max(month) FROM write_yeye.arb_ff").iloc[0]
    print(f"      -> {n.iloc[0]:,} months | range {n.iloc[1]} to {n.iloc[2]}")
    return q("SELECT * FROM write_yeye.arb_ff ORDER BY month")


def build_daily_controls() -> None:
    print("[5/8] Building daily controls (ILLIQ, MAX)...")
    run_ddl_file("05_daily_controls.sql")
    n = q("SELECT count(), count(illiq), count(max5) FROM write_yeye.arb_daily_controls").iloc[0]
    print(f"      -> {n.iloc[0]:,} rows | illiq={n.iloc[1]:,} | max5={n.iloc[2]:,}")


def build_ivol() -> None:
    print("[6/8] Building IVOL (daily FF3 residual std)...")
    run_ddl_file("06_ivol.sql")
    n = q("SELECT count(), count(ivol) FROM write_yeye.arb_ivol").iloc[0]
    print(f"      -> {n.iloc[0]:,} rows | ivol={n.iloc[1]:,}")


def build_beta() -> None:
    print("[7/8] Building BETA (rolling 60m)...")
    run_ddl_file("07_beta.sql")
    n = q("SELECT count(), count(beta) FROM write_yeye.arb_beta").iloc[0]
    print(f"      -> {n.iloc[0]:,} rows | beta={n.iloc[1]:,}")


def build_coskew() -> None:
    print("[7/8] Building COSKEW (rolling 60m Harvey-Siddique)...")
    run_ddl_file("08_coskew.sql")
    n = q("SELECT count(), count(coskew) FROM write_yeye.arb_coskew").iloc[0]
    print(f"      -> {n.iloc[0]:,} rows | coskew={n.iloc[1]:,}")


def build_op_ia() -> None:
    print("[7/8] Building OP and IA (Compustat annual)...")
    run_ddl_file("09_op_ia.sql")
    n = q("SELECT count(), count(op), count(ia) FROM write_yeye.arb_op_ia").iloc[0]
    print(f"      -> {n.iloc[0]:,} rows | op={n.iloc[1]:,} | ia={n.iloc[2]:,}")


def build_sue() -> None:
    print("[7/8] Building SUE (IBES)...")
    run_ddl_file("10_sue.sql")
    n = q("SELECT count(), count(sue) FROM write_yeye.arb_sue").iloc[0]
    print(f"      -> {n.iloc[0]:,} rows | sue={n.iloc[1]:,}")


def build_panel_full() -> pd.DataFrame:
    """Build the panel with all 12 control variables attached."""
    print("[8/8] Joining all controls into enriched panel...")
    run_ddl_file("11_panel_with_controls.sql")
    full = q("SELECT * FROM write_yeye.arb_panel_full ORDER BY month, permno")
    full_path = LAYOUT.data_path("panel_full.parquet")
    full.to_parquet(full_path, index=False)
    print(f"      -> {full.shape[0]:,} rows x {full.shape[1]} cols | saved {full_path}")
    return full


# ----------------------------------------------------------------------
# Sanity checks & reporting
# ----------------------------------------------------------------------


def sanity_check_panel(panel: pd.DataFrame) -> dict:
    """Run all panel-level sanity checks; return a dict of summary stats."""
    out: dict = {}
    print("\n=== Panel sanity checks ===")

    n_rows = len(panel)
    n_permno = panel["permno"].nunique()
    n_months = panel["month"].nunique()
    out["n_rows"] = int(n_rows)
    out["n_permnos"] = int(n_permno)
    out["n_months"] = int(n_months)
    out["avg_obs_per_month"] = float(n_rows / n_months) if n_months else float("nan")
    print(f"Rows: {n_rows:,} | Permnos: {n_permno:,} | Months: {n_months:,}")
    print(f"Avg obs/month: {out['avg_obs_per_month']:.1f}")

    # Paper expects ~3,036 obs/month (paper text L186); we expect [2500, 4000].
    if not 2_500 <= out["avg_obs_per_month"] <= 4_000:
        print(f"   WARNING: avg obs/month = {out['avg_obs_per_month']:.1f}, "
              f"expected in [2,500, 4,000].")

    # Paper expects total 2.10 million firm-months.
    if not 1_900_000 <= n_rows <= 2_300_000:
        print(f"   WARNING: total rows = {n_rows:,}, expected ~2.10 million.")

    # REG signal invariants
    print("\n=== REG signal verification ===")
    reg_raw = panel["reg_raw"].dropna()
    reg = panel["reg"].dropna()
    out["reg_raw_min"] = float(reg_raw.min())
    out["reg_raw_max"] = float(reg_raw.max())
    out["reg_raw_mean"] = float(reg_raw.mean())
    out["reg_raw_std"] = float(reg_raw.std())
    print(f"reg_raw (before sign flip)  min={out['reg_raw_min']:.4f}, "
          f"max={out['reg_raw_max']:.4f}, mean={out['reg_raw_mean']:.4f}, "
          f"std={out['reg_raw_std']:.4f}")
    assert (reg_raw <= 0.001).all(), "reg_raw must be <= 0 (small tolerance)"

    out["reg_min"] = float(reg.min())
    out["reg_max"] = float(reg.max())
    out["reg_mean"] = float(reg.mean())
    out["reg_std"] = float(reg.std())
    out["reg_q01"] = float(reg.quantile(0.01))
    out["reg_q10"] = float(reg.quantile(0.10))
    out["reg_q50"] = float(reg.quantile(0.50))
    out["reg_q90"] = float(reg.quantile(0.90))
    out["reg_q99"] = float(reg.quantile(0.99))
    print(f"reg    (after  sign flip)  min={out['reg_min']:.4f}, "
          f"max={out['reg_max']:.4f}, mean={out['reg_mean']:.4f}, "
          f"std={out['reg_std']:.4f}")
    print(f"   quantiles: 1%={out['reg_q01']:.4f}, 10%={out['reg_q10']:.4f}, "
          f"50%={out['reg_q50']:.4f}, 90%={out['reg_q90']:.4f}, "
          f"99%={out['reg_q99']:.4f}")
    assert (reg >= -0.001).all(), "reg must be >= 0 (small tolerance)"
    # REG can be arbitrarily large when an industry has one stock with an extreme
    # return (e.g., a stock split adjustment error or unusual corporate action).
    # The paper's own data exhibits such outliers — see Section 4 / Robustness.
    # We just confirm the distribution is finite; the analysis pipeline will
    # winsorize as needed in Table 1.
    assert reg.max() < 100, "REG max is implausibly large (>100); sanity check"
    print("   PASS: reg_raw <= 0; reg >= 0 (sign flip correct)")

    # Critical invariant: REG == 0 iff R_i == max_j R_j.
    reg_zero_mask = panel["reg"].abs() < 1e-9
    out["frac_reg_eq_zero"] = float(reg_zero_mask.mean())
    out["reg_eq_zero_match_industry_max"] = bool(
        np.allclose(
            panel.loc[reg_zero_mask, "ret"],
            panel.loc[reg_zero_mask, "ret_max_industry"],
            atol=1e-9,
        )
    )
    print(f"   REG == 0 share: {out['frac_reg_eq_zero']:.4f}")
    print(f"   When REG == 0, ret == ret_max_industry: "
          f"{out['reg_eq_zero_match_industry_max']}")
    assert out["reg_eq_zero_match_industry_max"], (
        "When REG == 0, ret must equal the industry max"
    )

    # 3-digit SIC industry size distribution
    print("\n=== 3-digit SIC industry size (per industry-month) ===")
    industry_sizes = (
        panel.dropna(subset=["sic3"])
        .query("sic3 > 0")
        .groupby(["month", "sic3"])
        .size()
    )
    out["industry_n_groups"] = int(len(industry_sizes))
    out["industry_size_mean"] = float(industry_sizes.mean())
    out["industry_size_median"] = float(industry_sizes.median())
    out["industry_size_q25"] = float(industry_sizes.quantile(0.25))
    out["industry_size_q75"] = float(industry_sizes.quantile(0.75))
    out["industry_size_max"] = int(industry_sizes.max())
    print(f"  groups: {out['industry_n_groups']:,}")
    print(f"  avg size: {out['industry_size_mean']:.1f} | "
          f"median: {out['industry_size_median']:.1f} | "
          f"q25: {out['industry_size_q25']:.1f} | q75: {out['industry_size_q75']:.1f} | "
          f"max: {out['industry_size_max']}")

    # Excess return invariants
    print("\n=== RET_T+1 (next-month excess return) ===")
    ex = panel["ret_excess_lead1"].dropna()
    raw = panel["ret_lead1"].dropna()
    out["ret_lead1_count"] = int(len(raw))
    out["ret_excess_lead1_count"] = int(len(ex))
    out["ret_excess_lead1_mean"] = float(ex.mean()) if len(ex) else float("nan")
    out["ret_lead1_mean"] = float(raw.mean()) if len(raw) else float("nan")
    print(f"  ret_lead1 rows: {out['ret_lead1_count']:,} | "
          f"mean: {out['ret_lead1_mean']:.4f}")
    print(f"  ret_excess_lead1 rows: {out['ret_excess_lead1_count']:,} | "
          f"mean: {out['ret_excess_lead1_mean']:.4f}")
    # Excess return != raw return (should differ by ~rf = ~0.3% monthly)
    if abs(out["ret_lead1_mean"] - out["ret_excess_lead1_mean"]) < 1e-4:
        print("   WARNING: ret_excess_lead1 ≈ ret_lead1; rf may not be subtracted")

    return out


# ----------------------------------------------------------------------
# Main entry
# ----------------------------------------------------------------------


def main() -> None:
    build_universe()
    build_reg()
    panel = build_panel()
    ff = build_ff_factors()
    build_daily_controls()
    build_ivol()
    build_beta()
    build_coskew()
    build_op_ia()
    build_sue()
    full = build_panel_full()

    # Save panel.parquet
    panel_path = LAYOUT.data_path("panel.parquet")
    panel.to_parquet(panel_path, index=False)
    print(f"\nWrote panel: {panel_path} ({panel.shape[0]:,} rows x {panel.shape[1]} cols)")

    ff_path = LAYOUT.data_path("ff_factors.parquet")
    ff.to_parquet(ff_path, index=False)
    print(f"Wrote FF factors: {ff_path} ({ff.shape[0]:,} rows x {ff.shape[1]} cols)")

    stats = sanity_check_panel(panel)
    # Save stats
    stats_path = LAYOUT.data_path("panel_summary_stats.json")
    stats_path.write_text(json.dumps(stats, indent=2, default=float))
    print(f"\nWrote panel summary stats: {stats_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()

    # ------------------------------------------------------------------
    # Task 2 — Table 1 (univariate VW quintile portfolios sorted by REG)
    # ------------------------------------------------------------------
    print("\n\n=== Task 2: Table 1 analysis ===\n")
    from analysis_table1 import run_table_1
    metrics_t1 = run_table_1()

    # Update eval/metrics.json with Table 1 metrics (preserve any existing keys).
    eval_path = LAYOUT.eval_path("metrics.json")
    if eval_path.exists():
        existing = json.loads(eval_path.read_text())
        existing_metrics = existing.get("metrics", {})
    else:
        existing = {"schema_version": 2, "slug": SLUG, "metrics": {}}
        existing_metrics = {}
    existing_metrics.update(metrics_t1)
    existing["metrics"] = existing_metrics
    eval_path.parent.mkdir(parents=True, exist_ok=True)
    eval_path.write_text(json.dumps(existing, indent=2, default=float))
    print(f"\nUpdated {eval_path} with Table 1 metrics.")

    # ------------------------------------------------------------------
    # Task 3 — Table 3 (dependent bivariate sorts)
    # ------------------------------------------------------------------
    print("\n\n=== Task 3: Table 3 analysis ===\n")
    from analysis_table3 import run_table_3
    metrics_t3 = run_table_3()

    # Update eval/metrics.json with Table 3 metrics.
    eval_path = LAYOUT.eval_path("metrics.json")
    if eval_path.exists():
        existing = json.loads(eval_path.read_text())
        existing_metrics = existing.get("metrics", {})
    else:
        existing = {"schema_version": 2, "slug": SLUG, "metrics": {}}
        existing_metrics = {}
    existing_metrics.update(metrics_t3)
    existing["metrics"] = existing_metrics
    eval_path.parent.mkdir(parents=True, exist_ok=True)
    eval_path.write_text(json.dumps(existing, indent=2, default=float))
    print(f"\nUpdated {eval_path} with Table 3 metrics.")

    # ------------------------------------------------------------------
    # Task 4 — Table 4 (Fama-MacBeth cross-sectional regressions, 12 specs)
    # ------------------------------------------------------------------
    print("\n\n=== Task 4: Table 4 analysis (FM regressions) ===\n")
    from analysis_table4 import run_table_4
    metrics_t4 = run_table_4()

    # Update eval/metrics.json with Table 4 metrics (preserve Tables 1-3).
    eval_path = LAYOUT.eval_path("metrics.json")
    if eval_path.exists():
        existing = json.loads(eval_path.read_text())
        existing_metrics = existing.get("metrics", {})
    else:
        existing = {"schema_version": 2, "slug": SLUG, "metrics": {}}
        existing_metrics = {}
    existing_metrics.update(metrics_t4)
    existing["metrics"] = existing_metrics
    eval_path.parent.mkdir(parents=True, exist_ok=True)
    eval_path.write_text(json.dumps(existing, indent=2, default=float))
    print(f"\nUpdated {eval_path} with Table 4 metrics.")
