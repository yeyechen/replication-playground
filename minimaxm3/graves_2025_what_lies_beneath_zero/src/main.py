"""
Graves (2025) Hidden Beliefs Replication — Main Pipeline (Partial)

This implements a partial replication focused on:
  1. Summary statistics (Tables 1, 2) — universe + AUM aggregation
  2. Foundation for HBI/OBI computation (NOT executed due to computational
     constraints — see REPRODUCTION_NOTE below)

REPRODUCTION NOTE:
  The paper requires SCQR estimation across ~248,000 institution-quarter
  pairs (Section 5), each with ~100 LP solves. This is infeasible in a
  single replication session. We document this scope reduction in
  preparations/assumptions.md (Assumption 1).

  This script demonstrates:
    - The 13F data extraction pipeline (Thomson Reuters s34)
    - Quarterly AUM aggregation by paper's period windows
    - Validation that the data infrastructure works for the partial sample

  Full SCQR + HBI computation is OUT OF SCOPE for this partial replication.

Sub-period: 2010Q1-2021Q4
Universe: common stocks (TR stkcd = 0/blank/NULL)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from clickhouse_driver import Client

# Repo paths
REPO_ROOT = Path("/home/ra_alan_mike_share/rep-it-up")
sys.path.insert(0, str(REPO_ROOT))
load_dotenv(REPO_ROOT / ".env")

from utils.paths import paper_layout

LAYOUT = paper_layout("graves_2025_what_lies_beneath_zero_censoring_demand_estimation_and_hidden_belief")
LAYOUT.ensure()

# ClickHouse client
CH_CLIENT = Client(
    host=os.getenv("CLICKHOUSE_HOST"),
    port=int(os.getenv("CLICKHOUSE_PORT", 9000)),
    user=os.getenv("CLICKHOUSE_USER"),
    password=os.getenv("CLICKHOUSE_PASSWORD"),
)


def run_sql_file(path: Path) -> pd.DataFrame:
    """Execute a SQL file against ClickHouse and return a DataFrame."""
    sql = path.read_text()
    result = CH_CLIENT.execute(sql, with_column_types=True)
    columns = [c[0] for c in result[1]]
    data = result[0]
    return pd.DataFrame(data, columns=columns)


def build_quarterly_aum() -> pd.DataFrame:
    """Build institution-quarter panel from 13F."""
    print("Building institution-quarter universe from 13F...")
    sql_path = LAYOUT.src_path("sql") / "13f_quarterly_aum.sql"
    df = run_sql_file(sql_path)
    print(f"  -> {len(df):,} institution-quarter rows")
    return df


def build_table_1_summary(panel: pd.DataFrame) -> pd.DataFrame:
    """Aggregate institution-quarter panel to paper's period windows for Table 1."""
    print("\nBuilding Table 1 (AUM summary)...")

    # Save intermediate
    panel.to_parquet(LAYOUT.data_path("inst_quarter_panel.parquet"), index=False)

    # Aggregate by period using ClickHouse
    sql_path = LAYOUT.src_path("sql") / "aggregate_by_period.sql"
    summary = run_sql_file(sql_path)

    # Format
    summary.columns = [
        'period', 'num_inst', 'inst_quarters', 'avg_pos_hold',
        'total_aum_B', 'avg_quarterly_aum_B'
    ]

    # Paper's Table 1 reports 4 metrics: Num Inst, Tot Inst AUM, Rigid AUM, Dynamic AUM, AUM SCQR
    # We don't have Rigid/Dynamic classification yet (would need overlap computation)
    # So report what we have
    summary['tot_inst_aum_B'] = summary['avg_quarterly_aum_B']  # Use avg quarterly as proxy

    return summary[['period', 'num_inst', 'tot_inst_aum_B', 'avg_pos_hold']]


def main():
    print("="*70)
    print("GRAVES (2025) HIDDEN BELIEFS — PARTIAL REPLICATION")
    print("Sub-period: 2010Q1-2021Q4")
    print("="*70)

    # 1. Build universe panel
    panel = build_quarterly_aum()

    # 2. Aggregate Table 1
    table_1 = build_table_1_summary(panel)
    print("\nTable 1 (Partial Replication):")
    print("="*70)
    print(table_1.to_string(index=False))

    # Save
    table_1.to_csv(LAYOUT.result_path("table_1_partial.csv"), index=False)
    with open(LAYOUT.result_path("table_1_partial.md"), "w") as f:
        f.write("# Table 1 — Partial Replication (2010Q1-2021Q4)\n\n")
        f.write("**Note:** Sub-period 2010-2021; full SCQR pipeline not executed (see REPORT.md).\n")
        f.write("Period windows match the paper's 4-year / 1-year groupings.\n\n")
        f.write("**Paper's Table 1 (full 1984-2021) vs Our partial (2010-2021):**\n")
        f.write("- Paper's 2013-2016: 3,733 institutions, $14,000B total AUM\n")
        f.write("- Paper's 2017-2020: 4,752 institutions, $20,587B total AUM\n")
        f.write("- Paper's 2021: 5,970 institutions, $31,962B total AUM\n\n")
        f.write("**Limitations:**\n")
        f.write("- Rigid/Dynamic classification not implemented (requires 12-quarter overlap)\n")
        f.write("- AUM SCQR column not computed (requires full SCQR pipeline)\n")
        f.write("- 'Total Inst AUM' is per-quarter average (paper averages quarterly values)\n\n")
        f.write(table_1.to_markdown(index=False))

    print(f"\n✓ Pipeline complete.")
    print(f"  Outputs:")
    print(f"    - {LAYOUT.data_path('inst_quarter_panel.parquet')}")
    print(f"    - {LAYOUT.result_path('table_1_partial.csv')}")
    print(f"    - {LAYOUT.result_path('table_1_partial.md')}")


if __name__ == "__main__":
    main()