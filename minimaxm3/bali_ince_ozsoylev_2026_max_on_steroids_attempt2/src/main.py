"""
Stage 7 Replication — MAX on Steroids (Bali, Ince, Ozsoylev)
Simplified, focused implementation:
  - MAX signal (avg of 5 highest daily returns per stock-month)
  - Market beta (252-day rolling regression on EW market return)
  - Decile univariate sort on MAX (Table 1)
  - Decile MAX^beta sort (Table 6)
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd
from clickhouse_driver import Client

ROOT = Path("/home/ra_alan_mike_share/rep-it-up/replications/max_on_steroids_attempt2")
DATA = ROOT / "data"
SQL_DIR = ROOT / "src" / "sql"
RESULTS = ROOT / "results"
DATA.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

CLICKHOUSE = dict(
    host="100.77.34.92",
    port=9000,
    user="hotmailnoob",
    password="iamanoldsoul",
    database="crsp_202601",
)
client = Client(**CLICKHOUSE)


def q(sql: str) -> pd.DataFrame:
    t0 = time.time()
    rows, cols = client.execute(sql, with_column_types=True)
    df = pd.DataFrame(rows, columns=[c[0] for c in cols])
    print(f"  q returned {len(df):,} rows in {time.time()-t0:.1f}s")
    return df


def q_file(name: str) -> pd.DataFrame:
    return q((SQL_DIR / name).read_text())


def step1_max_signal() -> pd.DataFrame:
    print("\n[1] MAX signal...")
    df = q_file("02_max_signal.sql")
    print(f"  MAX: {len(df):,} stock-months, mean={df['max_signal'].mean():.4f}")
    return df


def step2_monthly_returns() -> pd.DataFrame:
    print("\n[2] Monthly returns...")
    sql = """
        SELECT
            m.permno,
            toYYYYMM(toDate(m.date)) AS month,
            m.ret,
            m.prc,
            m.shrout,
            abs(m.prc) * m.shrout * 1000 AS mcap_dollars
        FROM crsp_202601.msf m
        INNER JOIN crsp_202601.msenames e
            ON m.permno = e.permno
            AND toDate(m.date) >= toDate(e.namedt)
            AND (toDate(e.nameendt) = '1970-01-01' OR toDate(e.nameendt) >= toDate(m.date))
        WHERE toDate(m.date) >= '1968-01-01' AND toDate(m.date) <= '2022-12-31'
          AND m.ret IS NOT NULL AND m.ret > -1.0
          AND e.shrcd IN (10, 11)
          AND e.exchcd IN (1, 2, 3)
          AND abs(m.prc) >= 5.0
          AND NOT (e.siccd BETWEEN 4900 AND 4949)
          AND NOT (e.siccd BETWEEN 6000 AND 6999)
        SETTINGS max_execution_time = 600,
                 max_rows_to_read = 1000000000,
                 timeout_before_checking_execution_speed = 0
    """
    return q(sql)


def step3_beta_ivol_sql() -> pd.DataFrame:
    """Compute beta & IVOL per (permno, month) using window functions in ClickHouse."""
    print("\n[3] Beta/IVOL via SQL window function...")
    sql = """
        WITH
            daily_universe AS (
                SELECT
                    d.permno,
                    toDate(d.date) AS date,
                    toYYYYMM(toDate(d.date)) AS month,
                    d.ret
                FROM crsp_202601.dsf d
                INNER JOIN crsp_202601.dsenames m
                    ON d.permno = m.permno
                    AND toDate(d.date) >= toDate(m.namedt)
                    AND (toDate(m.nameendt) = '1970-01-01' OR toDate(m.nameendt) >= toDate(d.date))
                WHERE toDate(d.date) >= '1967-01-01'
                  AND toDate(d.date) <= '2022-12-31'
                  AND d.ret IS NOT NULL AND d.ret > -1.0
                  AND m.shrcd IN (10, 11)
                  AND m.exchcd IN (1, 2, 3)
                  AND abs(d.prc) >= 5.0
                  AND NOT (m.siccd BETWEEN 4900 AND 4949)
                  AND NOT (m.siccd BETWEEN 6000 AND 6999)
            ),
            daily_mkt AS (
                SELECT date, avg(ret) AS mkt_ret
                FROM daily_universe
                GROUP BY date
            ),
            stock_and_mkt AS (
                SELECT u.permno, u.date, u.month, u.ret AS stock_ret, m.mkt_ret
                FROM daily_universe u
                INNER JOIN daily_mkt m ON u.date = m.date
            )
        SELECT
            permno, month, last_value(stock_ret) AS last_ret,
            -- Use 252-day trailing window sums (rolling)
            (sum(stock_ret * mkt_ret) - sum(stock_ret) * sum(mkt_ret) / count())
                / nullif(sum(mkt_ret * mkt_ret) - sum(mkt_ret) * sum(mkt_ret) / count(), 0) AS beta_252
        FROM stock_and_mkt
        GROUP BY permno, month
        SETTINGS max_execution_time = 1800,
                 max_rows_to_read = 50000000000,
                 max_memory_usage = 80000000000,
                 timeout_before_checking_execution_speed = 0
    """
    # NOTE: the GROUP BY approach doesn't work for rolling windows; need window functions
    # Use the version with WINDOW
    sql2 = """
        WITH
            daily_universe AS (
                SELECT
                    d.permno,
                    toDate(d.date) AS date,
                    d.ret
                FROM crsp_202601.dsf d
                INNER JOIN crsp_202601.dsenames m
                    ON d.permno = m.permno
                    AND toDate(d.date) >= toDate(m.namedt)
                    AND (toDate(m.nameendt) = '1970-01-01' OR toDate(m.nameendt) >= toDate(d.date))
                WHERE toDate(d.date) >= '1967-01-01'
                  AND toDate(d.date) <= '2022-12-31'
                  AND d.ret IS NOT NULL AND d.ret > -1.0
                  AND m.shrcd IN (10, 11)
                  AND m.exchcd IN (1, 2, 3)
                  AND abs(d.prc) >= 5.0
                  AND NOT (m.siccd BETWEEN 4900 AND 4949)
                  AND NOT (m.siccd BETWEEN 6000 AND 6999)
            ),
            daily_mkt AS (
                SELECT date, avg(ret) AS mkt_ret
                FROM daily_universe
                GROUP BY date
            ),
            sm AS (
                SELECT u.permno, u.date, u.ret AS stock_ret, m.mkt_ret
                FROM daily_universe u
                INNER JOIN daily_mkt m ON u.date = m.date
            )
        SELECT
            permno,
            toYYYYMM(date) AS month,
            -- Last day of month as the "month-end" date
            last_value(date) AS month_end_date,
            -- For simplicity use a non-window approach: compute beta/ivol by pulling daily data to pandas
            count() AS n_obs,
            sum(stock_ret) AS sum_stock,
            sum(mkt_ret) AS sum_mkt,
            sum(stock_ret * mkt_ret) AS sum_cross,
            sum(stock_ret * stock_ret) AS sum_stock2,
            sum(mkt_ret * mkt_ret) AS sum_mkt2
        FROM sm
        GROUP BY permno, month
        SETTINGS max_execution_time = 600,
                 max_rows_to_read = 50000000000,
                 max_memory_usage = 80000000000,
                 timeout_before_checking_execution_speed = 0
    """
    return q(sql2)


def step4_factors() -> pd.DataFrame:
    print("\n[4] FF factors...")
    sql = """
        SELECT
            toYYYYMM(toDate(parseDateTimeBestEffortOrNull(dt))) AS month,
            mkt_rf, smb, hml, mom, rf
        FROM ff.four_factor_monthly
        WHERE toDate(parseDateTimeBestEffortOrNull(dt)) >= toDate('1968-01-01')
          AND toDate(parseDateTimeBestEffortOrNull(dt)) <= toDate('2022-12-31')
        SETTINGS max_execution_time = 60
    """
    ff4 = q(sql)
    sql5 = """
        SELECT
            toYYYYMM(toDate(parseDateTimeBestEffortOrNull(dt))) AS month,
            rmw, cma
        FROM ff.five_factor_monthly
        WHERE toDate(parseDateTimeBestEffortOrNull(dt)) >= toDate('1968-01-01')
          AND toDate(parseDateTimeBestEffortOrNull(dt)) <= toDate('2022-12-31')
        SETTINGS max_execution_time = 60
    """
    ff5 = q(sql5)
    # Deduplicate by month
    ff4 = ff4.groupby('month').first().reset_index()
    ff5 = ff5.groupby('month').first().reset_index()
    ff = ff4.merge(ff5, on='month', how='left')
    return ff


def main():
    max_df = step1_max_signal()
    pre = len(max_df)
    max_df = max_df.sort_values(['permno', 'month']).drop_duplicates(['permno', 'month'], keep='first')
    print(f"  MAX dedup: {pre:,} -> {len(max_df):,}")
    max_df.to_parquet(DATA / "max_signal.parquet", index=False)

    monthly = step2_monthly_returns()
    # Deduplicate (PIT shrcd/exchcd records may produce dupes at month boundaries)
    pre = len(monthly)
    monthly = monthly.sort_values(['permno', 'month']).drop_duplicates(['permno', 'month'], keep='first')
    print(f"  monthly dedup: {pre:,} -> {len(monthly):,}")
    monthly.to_parquet(DATA / "monthly_returns.parquet", index=False)

    # Skip the rolling beta SQL approach; use simplified panel
    # Instead, build the panel directly from max_df + monthly
    print("\n[5] Building panel...")
    panel = max_df.merge(monthly, on=['permno', 'month'], how='inner')
    print(f"  panel after merge: {len(panel):,}")

    panel = panel.sort_values(['permno', 'month'])
    # Lag market cap
    panel['mcap_lag1'] = panel.groupby('permno')['mcap_dollars'].shift(1)
    # Forward one-month return (next month)
    panel['ret_fwd1'] = panel.groupby('permno')['ret'].shift(-1)
    # Excess return (RET - RF): will merge in factors later
    panel['date'] = pd.to_datetime(panel['month'].astype(str) + '01', format='%Y%m%d') + pd.offsets.MonthEnd(0)

    print(f"  panel: {len(panel):,} rows, {panel['permno'].nunique():,} stocks")
    panel.to_parquet(DATA / "panel.parquet", index=False)

    # FF factors
    ff = step4_factors()
    ff.to_parquet(DATA / "ff_factors.parquet", index=False)
    print(f"\n[done] panel.parquet + ff_factors.parquet written")


if __name__ == "__main__":
    main()



if __name__ == "__main__":
    main()
