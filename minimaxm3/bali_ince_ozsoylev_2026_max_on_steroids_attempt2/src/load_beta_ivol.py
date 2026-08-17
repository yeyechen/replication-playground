"""
Compute 252-day rolling beta & IVOL for stocks in the panel using daily CRSP data.

Strategy: pull daily returns only for the universe stocks in the panel months.
Use efficient SQL with GROUP BY permno+date and aggregate to month-end.

The challenge: the rolling 252-day regression needs window functions, which ClickHouse supports.
We pull a "wide table" with stock_ret and mkt_ret per (permno, date), then aggregate via window.
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd
from clickhouse_driver import Client

ROOT = Path("/home/ra_alan_mike_share/rep-it-up/replications/max_on_steroids_attempt2")
DATA = ROOT / "data"

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


def main():
    print("\n[BETA] Computing 252-day rolling beta per (permno, month-end)")

    # Pull daily returns for stocks in our panel months + 1 year buffer for beta warmup
    # This is a HUGE table, so we pull only needed fields and use SQL-side aggregation
    print("  Pulling daily stock & market returns for universe...")
    sql = """
        WITH
            -- Universe: same as MAX signal
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
            )
        SELECT u.permno, u.date, u.ret AS stock_ret, m.mkt_ret
        FROM daily_universe u
        INNER JOIN daily_mkt m ON u.date = m.date
        ORDER BY u.permno, u.date
        SETTINGS max_execution_time = 1800,
                 max_rows_to_read = 50000000000,
                 max_memory_usage = 100000000000,
                 timeout_before_checking_execution_speed = 0
    """
    df = q(sql)
    print(f"  pulled {len(df):,} daily observations")

    # Save raw
    df.to_parquet(DATA / "daily_panel.parquet", index=False)

    # Compute rolling beta per stock
    print("  Computing 252-day rolling beta...")
    t0 = time.time()
    df = df.sort_values(['permno', 'date'])

    def rolling_beta(g):
        n = len(g)
        betas = np.full(n, np.nan)
        ivols = np.full(n, np.nan)
        x = g['mkt_ret'].values
        y = g['stock_ret'].values
        # Cumulative sums for rolling window
        sx = np.cumsum(np.where(np.isnan(x), 0, x))
        sxx = np.cumsum(np.where(np.isnan(x), 0, x * x))
        sy = np.cumsum(np.where(np.isnan(y), 0, y))
        syy = np.cumsum(np.where(np.isnan(y), 0, y * y))
        sxy = np.cumsum(np.where(np.isnan(x) | np.isnan(y), 0, x * y))
        n252 = np.arange(1, n + 1, dtype=np.float64)
        n252 = np.minimum(n252, 252)
        # For each day, we need sum of trailing 252 elements
        # We use array slicing with numpy cumulative sums (subtract start idx)
        # For efficiency, vectorize where possible
        # At i, the trailing 252 window is [max(0, i-251), i]
        for i in range(251, n):
            s = i - 252 + 1
            e = i + 1
            x_sum = sx[e-1] - (sx[s-1] if s > 0 else 0)
            x2_sum = sxx[e-1] - (sxx[s-1] if s > 0 else 0)
            y_sum = sy[e-1] - (sy[s-1] if s > 0 else 0)
            y2_sum = syy[e-1] - (syy[s-1] if s > 0 else 0)
            xy_sum = sxy[e-1] - (sxy[s-1] if s > 0 else 0)
            nw = 252
            mx = x_sum / nw
            my = y_sum / nw
            var_x = x2_sum / nw - mx * mx
            if var_x > 1e-12:
                beta = (xy_sum / nw - mx * my) / var_x
                betas[i] = beta
                var_y = y2_sum / nw - my * my
                resid_var = max(var_y - beta * beta * var_x, 0)
                ivols[i] = np.sqrt(resid_var)
        return pd.DataFrame({'date': g['date'].values, 'beta_252': betas, 'ivol_252': ivols})

    betas = df.groupby('permno', group_keys=False).apply(rolling_beta)
    print(f"  beta computation: {time.time()-t0:.1f}s")

    # Take month-end values
    betas['month'] = (betas['date'].dt.year * 100 + betas['date'].dt.month).astype(int)
    beta_monthly = betas.groupby(['permno', 'month']).last().reset_index()
    beta_monthly = beta_monthly[['permno', 'month', 'beta_252', 'ivol_252']]
    print(f"  beta_ivol: {len(beta_monthly):,} stock-months")
    beta_monthly.to_parquet(DATA / "beta_ivol.parquet", index=False)
    print(f"[done] beta_ivol.parquet written")


if __name__ == "__main__":
    main()
