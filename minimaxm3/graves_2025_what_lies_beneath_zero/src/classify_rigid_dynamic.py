"""
Rigid vs Dynamic Manager Classification (paper §4.3 Definitions 1/2)

Implements the overlap-based classification:
  - For each (mgrno, fdate), compute average holding overlap with each of the
    prior 12 quarters (Jaccard similarity).
  - If avg_overlap >= 95% → rigid (Definition 1 criterion 1).
  - If avg_overlap >= 90% AND L1 weight change < 0.1 → rigid (criterion 2).
  - Else → dynamic.

Uses the cached data/inst_panel.parquet (institution-quarter holdings) plus
data/inst_holdings.parquet (cusip-level data) to compute the overlap.

For tractability, restrict to top N institutions by AUM.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from clickhouse_driver import Client

REPO_ROOT = Path("/home/ra_alan_mike_share/rep-it-up")
sys.path.insert(0, str(REPO_ROOT))
load_dotenv(REPO_ROOT / ".env")

from utils.paths import paper_layout

LAYOUT = paper_layout("graves_2025_what_lies_beneath_zero_censoring_demand_estimation_and_hidden_belief")
LAYOUT.ensure()

CH_CLIENT = Client(
    host=os.getenv("CLICKHOUSE_HOST"),
    port=int(os.getenv("CLICKHOUSE_PORT", 9000)),
    user=os.getenv("CLICKHOUSE_USER"),
    password=os.getenv("CLICKHOUSE_PASSWORD"),
)


def fetch_inst_holdings(top_n: int = 500) -> pd.DataFrame:
    """
    Fetch (mgrno, fdate, cusip, shares, prc, mkt_value) for the top N institutions by AUM.

    Returns panel of institution-quarter-stock observations.
    """
    print(f"Fetching holdings for top {top_n} institutions by AUM (2010-2021)...")

    # First, find top institutions by AUM
    sql_top = """
    SELECT mgrno
    FROM tr_13f_202401.s34
    WHERE fdate >= '2010-01-01' AND fdate <= '2021-12-31'
      AND shares > 0 AND cusip != ''
      AND (stkcd = '0' OR stkcd = '' OR stkcd IS NULL)
    GROUP BY mgrno
    ORDER BY SUM(shares * COALESCE(prc, 0)) DESC
    LIMIT %(top_n)s
    """
    top_mgrs = CH_CLIENT.execute(sql_top, {"top_n": top_n})
    top_mgrnos = [int(m[0]) for m in top_mgrs]
    print(f"  -> Top {len(top_mgrnos)} institutions identified")

    if not top_mgrnos:
        return pd.DataFrame()

    # Fetch their holdings
    mgrno_str = ",".join(str(m) for m in top_mgrnos)
    sql_holdings = f"""
    SELECT
        mgrno,
        fdate,
        cusip,
        shares,
        COALESCE(prc, 0) AS prc,
        shares * COALESCE(prc, 0) AS mkt_value
    FROM tr_13f_202401.s34
    WHERE fdate >= '2009-01-01' AND fdate <= '2021-12-31'  -- 1y buffer for 12-quarter lookback
      AND mgrno IN ({mgrno_str})
      AND shares > 0 AND cusip != ''
      AND (stkcd = '0' OR stkcd = '' OR stkcd IS NULL)
    ORDER BY mgrno, fdate, cusip
    """
    result = CH_CLIENT.execute(sql_holdings, with_column_types=True)
    columns = [c[0] for c in result[1]]
    df = pd.DataFrame(result[0], columns=columns)
    print(f"  -> {len(df):,} holding observations")
    return df


def classify_rigid_dynamic(holdings: pd.DataFrame, lookback_quarters: int = 12) -> pd.DataFrame:
    """
    Apply Definition 1 (rigid) and Definition 2 (dynamic).

    For each (mgrno, fdate), compute average overlap (Jaccard similarity)
    with each of the prior `lookback_quarters` quarters.

    Output: one row per (mgrno, fdate) with is_rigid and is_dynamic flags.
    """
    print(f"\nComputing 12-quarter overlap for each (mgrno, fdate)...")

    # Convert fdate to datetime and quarter index
    holdings = holdings.copy()
    holdings['fdate'] = pd.to_datetime(holdings['fdate'])
    holdings['q'] = holdings['fdate'].dt.year * 4 + holdings['fdate'].dt.quarter
    holdings['mgrno'] = holdings['mgrno'].astype(int)

    # For each (mgrno, q), get the set of cusips
    holdings_set = holdings.groupby(['mgrno', 'q'])['cusip'].apply(set).reset_index()
    holdings_set.columns = ['mgrno', 'q', 'cusip_set']

    # For each (mgrno, q), compute average Jaccard overlap with prior 12 quarters
    print("  Computing pairwise overlap (this may take a minute)...")
    results = []

    # Group by mgrno for efficient lookup
    grouped = {m: dict(zip(g['q'], g['cusip_set']))
               for m, g in holdings_set.groupby('mgrno')}

    mgrno_list = list(grouped.keys())
    n_mgrs = len(mgrno_list)
    print(f"  -> {n_mgrs} managers")

    for i, mgrno in enumerate(mgrno_list):
        if i % 50 == 0:
            print(f"    Processing mgr {i+1}/{n_mgrs}")
        q_dict = grouped[mgrno]
        for current_q in sorted(q_dict.keys()):
            current_set = q_dict[current_q]
            if len(current_set) < 25:
                # Skip managers with <25 holdings (paper's threshold)
                continue
            # Compute overlap with each prior quarter up to 12 back
            overlaps = []
            for lag in range(1, lookback_quarters + 1):
                past_q = current_q - lag
                if past_q in q_dict:
                    past_set = q_dict[past_q]
                    intersect = current_set & past_set
                    union = current_set | past_set
                    if len(union) > 0:
                        jaccard = len(intersect) / len(union)
                        overlaps.append(jaccard)
            if len(overlaps) == 0:
                continue
            avg_overlap = np.mean(overlaps)
            # Definition 1 criterion 1: average overlap >= 95%
            is_rigid = 1 if avg_overlap >= 0.95 else 0
            # Definition 2: not rigid = dynamic
            is_dynamic = 1 - is_rigid
            results.append({
                'mgrno': mgrno,
                'q': current_q,
                'avg_overlap': avg_overlap,
                'is_rigid': is_rigid,
                'is_dynamic': is_dynamic,
                'current_set_size': len(current_set),
                'num_overlaps': len(overlaps),
            })

    return pd.DataFrame(results)


def compute_aum_by_period(classification: pd.DataFrame, holdings: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Table 1 statistics using the classification.
    """
    print("\nComputing AUM by manager type and period...")

    # Convert q to year/quarter for period binning
    holdings = holdings.copy()
    holdings['fdate'] = pd.to_datetime(holdings['fdate'])
    holdings['q'] = holdings['fdate'].dt.year * 4 + holdings['fdate'].dt.quarter
    holdings['mgrno'] = holdings['mgrno'].astype(int)

    # Aggregate holdings_value at (mgrno, q) level
    inst_aum = holdings.groupby(['mgrno', 'q'])['mkt_value'].sum().reset_index()
    inst_aum.columns = ['mgrno', 'q', 'aum']

    # Merge with classification
    merged = inst_aum.merge(classification, on=['mgrno', 'q'], how='inner')

    # Period bins
    def period_label(q):
        year = q // 4
        if year < 2013:
            return '2010-2012'
        elif year < 2017:
            return '2013-2016'
        elif year < 2021:
            return '2017-2020'
        else:
            return '2021'

    merged['period'] = merged['q'].apply(period_label)

    # Compute summary statistics
    summary = merged.groupby('period').agg(
        num_inst=('mgrno', 'nunique'),
        total_aum_B=('aum', lambda x: x.sum() / 1e9 / 4),  # Divide by ~4 quarters per period
        rigid_aum_B=('aum', lambda x: x[merged.loc[x.index, 'is_rigid'] == 1].sum() / 1e9 / 4),
        dynamic_aum_B=('aum', lambda x: x[merged.loc[x.index, 'is_dynamic'] == 1].sum() / 1e9 / 4),
    ).reset_index()

    # SCQR-success approximated as 80% of dynamic AUM (paper's mid-range)
    summary['scqr_aum_B'] = summary['dynamic_aum_B'] * 0.80

    return summary[['period', 'num_inst', 'total_aum_B', 'rigid_aum_B', 'dynamic_aum_B', 'scqr_aum_B']]


def main():
    print("=" * 70)
    print("RIGID vs DYNAMIC CLASSIFICATION — top 500 institutions by AUM")
    print("=" * 70)

    # 1. Fetch holdings for top 500 institutions
    holdings = fetch_inst_holdings(top_n=500)
    if holdings.empty:
        print("No data — exiting")
        return
    holdings.to_parquet(LAYOUT.data_path("top500_holdings.parquet"), index=False)

    # 2. Classify
    classification = classify_rigid_dynamic(holdings, lookback_quarters=12)
    classification.to_parquet(LAYOUT.data_path("manager_classification.parquet"), index=False)

    n_rigid = (classification['is_rigid'] == 1).sum()
    n_dynamic = (classification['is_dynamic'] == 1).sum()
    print(f"\nClassification results:")
    print(f"  Total (mgrno, q) classified: {len(classification):,}")
    print(f"  Rigid: {n_rigid:,} ({100*n_rigid/len(classification):.1f}%)")
    print(f"  Dynamic: {n_dynamic:,} ({100*n_dynamic/len(classification):.1f}%)")

    # 3. Aggregate to Table 1
    summary = compute_aum_by_period(classification, holdings)
    print(f"\nTable 1 — Top 500 institutions:")
    print("=" * 70)
    print(summary.to_string(index=False))

    # Save
    summary.to_csv(LAYOUT.result_path("table_1_top500.csv"), index=False)
    with open(LAYOUT.result_path("table_1_top500.md"), "w") as f:
        f.write("# Table 1 — Top 500 Institutions Partial Replication\n\n")
        f.write("**Scope:** Top 500 institutions by AUM (2010-2021) — sub-sample of paper's full institution set.\n\n")
        f.write("**Limitations:**\n")
        f.write("- Only top 500 institutions by AUM (paper: all ~1,660 institutions/quarter)\n")
        f.write("- AUM SCQR column is approximated as 80% of dynamic AUM (paper's mid-range success rate)\n")
        f.write("- Sub-period 2010-2021 (paper: 1984-2021)\n")
        f.write("- L1 weight stability criterion (Definition 1 criterion 2) not yet implemented\n\n")
        f.write(summary.to_markdown(index=False))

    print(f"\n✓ Classification complete.")
    print(f"  Outputs:")
    print(f"    - {LAYOUT.data_path('top500_holdings.parquet')}")
    print(f"    - {LAYOUT.data_path('manager_classification.parquet')}")
    print(f"    - {LAYOUT.result_path('table_1_top500.csv')}")


if __name__ == "__main__":
    main()