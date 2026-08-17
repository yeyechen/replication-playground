"""
Compute beta via rolling regression of monthly excess returns on FF mkt_rf.
This is a simplified approximation of the 252-day daily beta - uses monthly
data with a longer rolling window (36 or 60 months) to get enough observations.
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/home/ra_alan_mike_share/rep-it-up/replications/max_on_steroids_attempt2")
DATA = ROOT / "data"


def compute_rolling_beta_monthly(panel: pd.DataFrame, ff: pd.DataFrame, window: int = 36) -> pd.DataFrame:
    """For each stock, regress monthly excess returns on mkt_rf over rolling window."""
    df = panel.merge(ff[['month', 'mkt_rf', 'rf']], on='month', how='left')
    df['ret_xs'] = df['ret'] - df['rf']
    df = df.sort_values(['permno', 'month'])

    def roll(g):
        n = len(g)
        betas = np.full(n, np.nan)
        ivols = np.full(n, np.nan)
        x = g['mkt_rf'].values
        y = g['ret_xs'].values
        sx = np.cumsum(np.where(np.isnan(x), 0, x))
        sxx = np.cumsum(np.where(np.isnan(x), 0, x * x))
        sy = np.cumsum(np.where(np.isnan(y), 0, y))
        syy = np.cumsum(np.where(np.isnan(y), 0, y * y))
        sxy = np.cumsum(np.where(np.isnan(x) | np.isnan(y), 0, x * y))
        for i in range(window, n):
            s = i - window
            e = i + 1
            x_sum = sx[e-1] - (sx[s-1] if s > 0 else 0)
            x2_sum = sxx[e-1] - (sxx[s-1] if s > 0 else 0)
            y_sum = sy[e-1] - (sy[s-1] if s > 0 else 0)
            y2_sum = syy[e-1] - (syy[s-1] if s > 0 else 0)
            xy_sum = sxy[e-1] - (sxy[s-1] if s > 0 else 0)
            nw = window
            mx = x_sum / nw
            my = y_sum / nw
            var_x = x2_sum / nw - mx * mx
            if var_x > 1e-12:
                beta = (xy_sum / nw - mx * my) / var_x
                beta = max(-10, min(10, beta))
                betas[i] = beta
                var_y = y2_sum / nw - my * my
                resid_var = max(var_y - beta * beta * var_x, 0)
                ivols[i] = np.sqrt(resid_var)
        permno = g.name
        return pd.DataFrame({'permno': np.full(n, permno), 'month': g['month'].values, 'beta': betas, 'ivol': ivols})

    t0 = time.time()
    out = df.groupby('permno', group_keys=False).apply(roll, include_groups=False)
    out = out.reset_index(drop=True)
    print(f"  beta computation: {time.time()-t0:.1f}s")
    return out


def main():
    panel = pd.read_parquet(DATA / "panel.parquet")
    ff = pd.read_parquet(DATA / "ff_factors.parquet")

    print(f"panel: {len(panel):,} rows")
    print(f"computing 36-month rolling beta...")
    beta = compute_rolling_beta_monthly(panel, ff, window=36)
    print(f"beta: {len(beta):,} rows")
    print(beta.describe())

    beta = beta.reset_index(drop=True)
    beta.to_parquet(DATA / "beta_ivol_monthly.parquet", index=False)
    print(f"[done] beta_ivol_monthly.parquet written")


if __name__ == "__main__":
    main()
