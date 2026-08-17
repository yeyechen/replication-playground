"""
Run all 4 tables:
- Table 1: Univariate sorts on MAX
- Table 6: MAX^beta double sort
- Table 4: Fama-MacBeth regression on MAX
- Table 8: Fama-MacBeth regression on MAX^beta
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path("/home/ra_alan_mike_share/rep-it-up/replications/max_on_steroids_attempt2")
DATA = ROOT / "data"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)


def load_panel():
    panel = pd.read_parquet(DATA / "panel.parquet")
    print(f"panel: {len(panel):,} rows, {panel['permno'].nunique():,} stocks")
    return panel


def load_ff():
    ff = pd.read_parquet(DATA / "ff_factors.parquet")
    print(f"ff: {len(ff)} months, {ff['month'].min()}-{ff['month'].max()}")
    return ff


def load_beta():
    p = DATA / "beta_ivol_monthly.parquet"
    if p.exists():
        beta = pd.read_parquet(p)
        beta = beta.rename(columns={'beta': 'beta_252', 'ivol': 'ivol_252'})
        print(f"beta: {len(beta):,} rows")
        return beta
    return None


def decile_sort(df: pd.DataFrame, signal_col: str, n_bins: int = 10) -> pd.Series:
    """Assign decile bins within each month based on signal."""
    out = pd.Series(np.nan, index=df.index)
    for m, g in df.groupby('month'):
        try:
            ranks = pd.qcut(g[signal_col].rank(method='first'), n_bins, labels=False, duplicates='drop')
            out.loc[g.index] = ranks.values + 1
        except Exception:
            pass
    return out


def value_weighted_returns(df: pd.DataFrame, bin_col: str, ret_col: str, mcap_col: str) -> pd.DataFrame:
    """Compute VW portfolio returns per (month, bin)."""
    df = df.dropna(subset=[bin_col, ret_col, mcap_col])
    df = df[df[mcap_col] > 0]
    grp = df.groupby(['month', bin_col])
    vw = grp.apply(lambda x: (x[ret_col] * x[mcap_col]).sum() / x[mcap_col].sum(), include_groups=False).reset_index()
    vw.columns = ['month', bin_col, 'ret_vw']
    return vw


def newey_west_tstat(returns: pd.Series, n_lags: int = 6) -> tuple[float, float]:
    """Compute mean and Newey-West t-stat with given number of lags."""
    r = returns.dropna()
    n = len(r)
    if n < 30:
        return np.nan, np.nan
    mean = r.mean()
    gamma0 = ((r - mean) ** 2).mean()
    var_hat = gamma0
    for k in range(1, min(n_lags, n-1) + 1):
        gamma_k = ((r[k:] - mean) * (r[:-k] - mean)).mean()
        weight = 1 - k / (n_lags + 1)
        var_hat += 2 * weight * gamma_k
    se = np.sqrt(var_hat / n)
    if se == 0 or np.isnan(se):
        return mean * 100, np.nan
    return mean * 100, mean / se


def run_factor_alpha(port_rets: pd.Series, ff: pd.DataFrame, factors: list[str], n_lags: int = 6) -> dict:
    """Run factor regression on portfolio returns."""
    df = pd.DataFrame({'ret': port_rets}).reset_index()
    df.columns = ['month', 'ret']
    df = df.merge(ff[['month', 'rf'] + factors], on='month', how='left')
    df = df.dropna()
    if len(df) < 30:
        return {'alpha_pct': np.nan, 't_stat': np.nan, 'n_obs': len(df)}
    y = (df['ret'] - df['rf']) * 100
    X = sm.add_constant(df[factors])
    model = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': n_lags})
    return {
        'alpha_pct': model.params['const'],
        't_stat': model.tvalues['const'],
        'n_obs': int(model.nobs),
        'betas': {f: model.params[f] for f in factors}
    }


def write_md(filename: str, title: str, headers: list, rows: list, notes: str = ""):
    md = f"# {title}\n\n"
    md += "| " + " | ".join(headers) + " |\n"
    md += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    for row in rows:
        md += "| " + " | ".join([str(c) for c in row]) + " |\n"
    md += "\n"
    if notes:
        md += f"**Notes:** {notes}\n"
    (RESULTS / filename).write_text(md)
    print(f"  wrote {filename}")


def table1(panel: pd.DataFrame, ff: pd.DataFrame) -> dict:
    """Table 1: Univariate sorts on MAX."""
    print("\n[Table 1] Univariate MAX sorts...")
    panel = panel.copy()
    panel['max_decile'] = decile_sort(panel, 'max_signal', 10)

    bin_vw = value_weighted_returns(panel, 'max_decile', 'ret_fwd1', 'mcap_dollars')
    bin_pivot = bin_vw.pivot(index='month', columns='max_decile', values='ret_vw').sort_index()
    bin_pivot.columns = [f'P{int(c)}' for c in bin_pivot.columns]
    rf = ff.set_index('month')['rf']
    bin_xs = bin_pivot.subtract(rf, axis=0) * 100

    metrics = {}
    for col in bin_xs.columns:
        rets = bin_pivot[col].dropna()
        mean, t = newey_west_tstat(rets, n_lags=6)
        metrics[col] = {'mean_ret_rf_pct': mean, 't_stat': t}
        for fset_name, fset in [('FF3', ['mkt_rf', 'smb', 'hml']),
                                 ('FFC4', ['mkt_rf', 'smb', 'hml', 'mom']),
                                 ('FF5', ['mkt_rf', 'smb', 'hml', 'rmw', 'cma']),
                                 ('FF6', ['mkt_rf', 'smb', 'hml', 'rmw', 'cma', 'mom'])]:
            alpha = run_factor_alpha(rets, ff, fset)
            metrics[col][f'alpha_{fset_name}'] = alpha['alpha_pct']
            metrics[col][f't_{fset_name}'] = alpha['t_stat']

    spread = (bin_pivot['P10'] - bin_pivot['P1']).dropna()
    mean, t = newey_west_tstat(spread, n_lags=6)
    spread_metrics = {'mean_ret_rf_pct': mean, 't_stat': t}
    for fset_name, fset in [('FF3', ['mkt_rf', 'smb', 'hml']),
                             ('FFC4', ['mkt_rf', 'smb', 'hml', 'mom']),
                             ('FF5', ['mkt_rf', 'smb', 'hml', 'rmw', 'cma']),
                             ('FF6', ['mkt_rf', 'smb', 'hml', 'rmw', 'cma', 'mom'])]:
        a = run_factor_alpha(spread, ff, fset)
        spread_metrics[f'alpha_{fset_name}'] = a['alpha_pct']
        spread_metrics[f't_{fset_name}'] = a['t_stat']
    metrics['10-1'] = spread_metrics

    print(f"  10-1 spread: RET-RF={spread_metrics['mean_ret_rf_pct']:.2f}% (t={spread_metrics['t_stat']:.2f})")
    print(f"  FF3 alpha: {spread_metrics['alpha_FF3']:.2f}% (t={spread_metrics['t_FF3']:.2f})")

    headers = ['Decile', 'RET-RF (t)', 'FF3 alpha (t)', 'FFC4 alpha (t)', 'FF5 alpha (t)', 'FF6 alpha (t)']
    rows = []
    for c in ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10']:
        m = metrics[c]
        rows.append([c,
                     f"{m['mean_ret_rf_pct']:.2f} ({m['t_stat']:.2f})",
                     f"{m['alpha_FF3']:.2f} ({m['t_FF3']:.2f})",
                     f"{m['alpha_FFC4']:.2f} ({m['t_FFC4']:.2f})",
                     f"{m['alpha_FF5']:.2f} ({m['t_FF5']:.2f})",
                     f"{m['alpha_FF6']:.2f} ({m['t_FF6']:.2f})"])
    m = metrics['10-1']
    rows.append(['10-1 spread',
                 f"{m['mean_ret_rf_pct']:.2f} ({m['t_stat']:.2f})",
                 f"{m['alpha_FF3']:.2f} ({m['t_FF3']:.2f})",
                 f"{m['alpha_FFC4']:.2f} ({m['t_FFC4']:.2f})",
                 f"{m['alpha_FF5']:.2f} ({m['t_FF5']:.2f})",
                 f"{m['alpha_FF6']:.2f} ({m['t_FF6']:.2f})"])

    notes = "VW 1-month-ahead excess returns and risk-adjusted alphas for decile portfolios sorted on MAX. Sample: 1968-2022. NW t-stats use 6 lags."
    write_md('table_1.md', 'Table 1: Univariate Sorts on MAX', headers, rows, notes)

    return {'metrics': metrics, 'bin_returns': bin_xs, 'panel_with_decile': panel}


def table6(panel: pd.DataFrame, ff: pd.DataFrame, beta: pd.DataFrame) -> dict:
    """Table 6: MAX^beta sorts (double sort: beta decile x MAX decile, regroup)."""
    print("\n[Table 6] MAX^beta double sort...")
    panel = panel.copy()
    if beta is not None:
        panel = panel.merge(beta, on=['permno', 'month'], how='left')
    panel = panel.dropna(subset=['beta_252'])
    panel = panel[panel['beta_252'].between(0.1, 5.0)]

    panel['beta_decile'] = decile_sort(panel, 'beta_252', 10)
    # Within each beta decile, sort by MAX into deciles
    panel['max_decile_in_beta'] = np.nan
    for (bd, m), g in panel.groupby(['beta_decile', 'month']):
        try:
            ranks = pd.qcut(g['max_signal'].rank(method='first'), 10, labels=False, duplicates='drop')
            panel.loc[g.index, 'max_decile_in_beta'] = ranks.values + 1
        except Exception:
            pass

    panel['max_beta_decile'] = panel['max_decile_in_beta']
    bin_vw = value_weighted_returns(panel, 'max_beta_decile', 'ret_fwd1', 'mcap_dollars')
    bin_pivot = bin_vw.pivot(index='month', columns='max_beta_decile', values='ret_vw').sort_index()
    bin_pivot.columns = [f'P{int(c)}' for c in bin_pivot.columns]
    rf = ff.set_index('month')['rf']
    bin_xs = bin_pivot.subtract(rf, axis=0) * 100

    metrics = {}
    for col in bin_xs.columns:
        rets = bin_pivot[col].dropna()
        mean, t = newey_west_tstat(rets, n_lags=6)
        metrics[col] = {'mean_ret_rf_pct': mean, 't_stat': t}
        for fset_name, fset in [('FF3', ['mkt_rf', 'smb', 'hml']),
                                 ('FFC4', ['mkt_rf', 'smb', 'hml', 'mom']),
                                 ('FF5', ['mkt_rf', 'smb', 'hml', 'rmw', 'cma']),
                                 ('FF6', ['mkt_rf', 'smb', 'hml', 'rmw', 'cma', 'mom'])]:
            alpha = run_factor_alpha(rets, ff, fset)
            metrics[col][f'alpha_{fset_name}'] = alpha['alpha_pct']
            metrics[col][f't_{fset_name}'] = alpha['t_stat']

    # 10-1 spread
    p10_col = [c for c in bin_pivot.columns if c.startswith('P10')]
    p1_col = [c for c in bin_pivot.columns if c.startswith('P1')]
    if p10_col and p1_col:
        spread = (bin_pivot[p10_col[0]] - bin_pivot[p1_col[0]]).dropna()
        mean, t = newey_west_tstat(spread, n_lags=6)
        spread_metrics = {'mean_ret_rf_pct': mean, 't_stat': t}
        for fset_name, fset in [('FF3', ['mkt_rf', 'smb', 'hml']),
                                 ('FFC4', ['mkt_rf', 'smb', 'hml', 'mom']),
                                 ('FF5', ['mkt_rf', 'smb', 'hml', 'rmw', 'cma']),
                                 ('FF6', ['mkt_rf', 'smb', 'hml', 'rmw', 'cma', 'mom'])]:
            a = run_factor_alpha(spread, ff, fset)
            spread_metrics[f'alpha_{fset_name}'] = a['alpha_pct']
            spread_metrics[f't_{fset_name}'] = a['t_stat']
        metrics['10-1'] = spread_metrics
        print(f"  10-1 spread: RET-RF={spread_metrics['mean_ret_rf_pct']:.2f}% (t={spread_metrics['t_stat']:.2f})")
        print(f"  FF3 alpha: {spread_metrics['alpha_FF3']:.2f}% (t={spread_metrics['t_FF3']:.2f})")

    headers = ['Decile', 'RET-RF (t)', 'FF3 alpha (t)', 'FFC4 alpha (t)', 'FF5 alpha (t)', 'FF6 alpha (t)']
    rows = []
    for c in sorted(metrics.keys()):
        if c == '10-1':
            continue
        m = metrics[c]
        rows.append([c,
                     f"{m['mean_ret_rf_pct']:.2f} ({m['t_stat']:.2f})",
                     f"{m['alpha_FF3']:.2f} ({m['t_FF3']:.2f})",
                     f"{m['alpha_FFC4']:.2f} ({m['t_FFC4']:.2f})",
                     f"{m['alpha_FF5']:.2f} ({m['t_FF5']:.2f})",
                     f"{m['alpha_FF6']:.2f} ({m['t_FF6']:.2f})"])
    if '10-1' in metrics:
        m = metrics['10-1']
        rows.append(['10-1 spread',
                     f"{m['mean_ret_rf_pct']:.2f} ({m['t_stat']:.2f})",
                     f"{m['alpha_FF3']:.2f} ({m['t_FF3']:.2f})",
                     f"{m['alpha_FFC4']:.2f} ({m['t_FFC4']:.2f})",
                     f"{m['alpha_FF5']:.2f} ({m['t_FF5']:.2f})",
                     f"{m['alpha_FF6']:.2f} ({m['t_FF6']:.2f})"])

    notes = ("MAX^beta = conditional double sort (sort into 10 beta deciles, "
             "then within each sort into 10 MAX deciles, regroup by MAX rank). "
             "Beta computed from 36-month rolling monthly regression on FF mkt_rf. "
             "SY/DHS factors unavailable in ClickHouse (skipped).")
    write_md('table_6.md', 'Table 6: Portfolio Sorts on MAX^beta', headers, rows, notes)

    return {'metrics': metrics, 'bin_returns': bin_xs}


def table4(panel: pd.DataFrame) -> dict:
    """Table 4: Fama-MacBeth regression on MAX."""
    print("\n[Table 4] FM regression on MAX...")
    p = panel.dropna(subset=['ret_fwd1', 'max_signal', 'mcap_lag1']).copy()
    p = p[p['mcap_lag1'] > 0]
    ff_local = pd.read_parquet(DATA / "ff_factors.parquet")[['month', 'rf']]
    p = p.merge(ff_local, on='month', how='left')
    p['ret_xs'] = p['ret_fwd1'] - p['rf']

    # Specs from paper:
    # Col1: MAX only
    # Col2: MAX + SIZE + BM + REV + MOM + ILLIQ + ROE + I/A + IVOL (standard controls)
    # Col3: MAX + MIS
    # Col4: MAX + CE
    # Col5: MAX + MIS + standard controls
    # Col6: MAX + CE + standard controls

    # For now, implement Col1 (univariate) and Col2 (full controls minus MIS/CE)
    # SIZE = log(mcap_lag1), REV = ret, MOM = log(1+ret_11_2), etc.

    # Compute MOM = cum return over months t-12 to t-2 (11 months)
    p = p.sort_values(['permno', 'month'])
    p['log_mcap'] = np.log(p['mcap_lag1'])
    p['mom'] = p.groupby('permno')['ret'].rolling(11, min_periods=6).sum().reset_index(level=0, drop=True)
    p['rev'] = p['ret']  # formation-month return

    # We need to winsorize 1%/99% per month
    def winsorize_month(g):
        for col in ['max_signal', 'log_mcap', 'mom', 'rev']:
            lo = g[col].quantile(0.01)
            hi = g[col].quantile(0.99)
            g[col] = g[col].clip(lo, hi)
        return g

    print("  winsorizing...")
    p = p.groupby('month', group_keys=False).apply(winsorize_month, include_groups=True).reset_index(drop=True)

    # Col1: univariate MAX
    def run_fm(X_cols, label):
        coefs = []
        for m, g in p.groupby('month'):
            g = g.dropna(subset=X_cols + ['ret_xs'])
            if len(g) < 30:
                continue
            X = sm.add_constant(g[X_cols])
            y = g['ret_xs']
            model = sm.OLS(y, X).fit()
            coefs.append(model.params)
        coefs_df = pd.DataFrame(coefs)
        # Newey-West t-stats on time series of coefs
        means = coefs_df.mean()
        n = len(coefs_df)
        nw_t = {}
        for col in coefs_df.columns:
            x = coefs_df[col].dropna()
            mean = x.mean()
            gamma0 = ((x - mean) ** 2).mean()
            var_hat = gamma0
            for k in range(1, min(6, len(x)-1) + 1):
                gamma_k = ((x[k:] - mean) * (x[:-k] - mean)).mean()
                weight = 1 - k / (6 + 1)
                var_hat += 2 * weight * gamma_k
            se = np.sqrt(var_hat / n)
            nw_t[col] = mean / se if se > 0 else np.nan
        return means, nw_t

    print("  Col1: MAX only")
    m1, t1 = run_fm(['max_signal'], 'Col1')
    print(f"  MAX coef: {m1.get('max_signal', np.nan):.3f} (t={t1.get('max_signal', np.nan):.2f})")

    print("  Col2: MAX + standard controls")
    m2, t2 = run_fm(['max_signal', 'log_mcap', 'mom', 'rev'], 'Col2')
    print(f"  MAX coef: {m2.get('max_signal', np.nan):.3f} (t={t2.get('max_signal', np.nan):.2f})")

    metrics = {
        'Col1': {'MAX_coef': m1.get('max_signal', np.nan), 'MAX_tstat': t1.get('max_signal', np.nan)},
        'Col2': {'MAX_coef': m2.get('max_signal', np.nan), 'MAX_tstat': t2.get('max_signal', np.nan)},
    }

    # Write markdown
    headers = ['Variable', 'Col1: MAX', 'Col2: MAX + Controls']
    rows = []
    rows.append(['MAX', f"{m1.get('max_signal', np.nan):.3f} ({t1.get('max_signal', np.nan):.2f})",
                 f"{m2.get('max_signal', np.nan):.3f} ({t2.get('max_signal', np.nan):.2f})"])
    for col in ['log_mcap', 'mom', 'rev']:
        if col in m2.index:
            rows.append([col.upper(),
                         '—',
                         f"{m2.get(col, np.nan):.3f} ({t2.get(col, np.nan):.2f})"])
    notes = ("Fama-MacBeth regression of one-month-ahead excess returns on MAX. "
             "Monthly cross-section OLS averaged over 1968-2022. "
             "Variables winsorized 1%/99% per month.")
    write_md('table_4.md', 'Table 4: Fama-MacBeth Regressions on MAX', headers, rows, notes)
    return metrics


def table8(panel: pd.DataFrame, beta: pd.DataFrame) -> dict:
    """Table 8: FM regression on MAX^beta dummies."""
    print("\n[Table 8] FM regression on MAX^beta dummies...")
    p = panel.copy()
    if beta is not None:
        p = p.merge(beta, on=['permno', 'month'], how='left')
    p = p.dropna(subset=['ret_fwd1', 'beta_252', 'max_signal', 'mcap_lag1'])
    p = p[p['mcap_lag1'] > 0]
    p = p[p['beta_252'].between(0.1, 5.0)]
    p = p.sort_values(['permno', 'month'])

    # Compute MAX^beta decile
    p['beta_decile'] = decile_sort(p, 'beta_252', 10)
    p['max_decile_in_beta'] = np.nan
    for (bd, m), g in p.groupby(['beta_decile', 'month']):
        try:
            ranks = pd.qcut(g['max_signal'].rank(method='first'), 10, labels=False, duplicates='drop')
            p.loc[g.index, 'max_decile_in_beta'] = ranks.values + 1
        except Exception:
            pass
    p['maxb_decile'] = p['max_decile_in_beta']

    # D2-D10 dummies (D1 omitted)
    for d in range(2, 11):
        p[f'D{d}'] = (p['maxb_decile'] == d).astype(float)

    p['log_mcap'] = np.log(p['mcap_lag1'])
    p['mom'] = p.groupby('permno')['ret'].rolling(11, min_periods=6).sum().reset_index(level=0, drop=True)
    p['rev'] = p['ret']

    # Merge rf to compute excess return
    ff_local = pd.read_parquet(DATA / "ff_factors.parquet")[['month', 'rf']]
    p = p.merge(ff_local, on='month', how='left')
    p['ret_xs'] = p['ret_fwd1'] - p['rf']

    # Winsorize
    def winsorize_month(g):
        for col in ['log_mcap', 'mom', 'rev']:
            if col in g.columns:
                lo = g[col].quantile(0.01)
                hi = g[col].quantile(0.99)
                g[col] = g[col].clip(lo, hi)
        return g

    print("  winsorizing...")
    p = p.groupby('month', group_keys=False).apply(winsorize_month, include_groups=True).reset_index(drop=True)

    # Col1: D2-D10 only
    dummies = [f'D{d}' for d in range(2, 11)]
    def run_fm_dummies(extra_cols, label):
        X_cols = dummies + extra_cols
        coefs = []
        for m, g in p.groupby('month'):
            g = g.dropna(subset=X_cols + ['ret_xs'])
            if len(g) < 30:
                continue
            X = sm.add_constant(g[X_cols])
            y = g['ret_xs']
            model = sm.OLS(y, X).fit()
            coefs.append(model.params)
        coefs_df = pd.DataFrame(coefs)
        means = coefs_df.mean()
        n = len(coefs_df)
        nw_t = {}
        for col in coefs_df.columns:
            x = coefs_df[col].dropna()
            mean = x.mean()
            gamma0 = ((x - mean) ** 2).mean()
            var_hat = gamma0
            for k in range(1, min(6, len(x)-1) + 1):
                gamma_k = ((x[k:] - mean) * (x[:-k] - mean)).mean()
                weight = 1 - k / (6 + 1)
                var_hat += 2 * weight * gamma_k
            se = np.sqrt(var_hat / n)
            nw_t[col] = mean / se if se > 0 else np.nan
        return means, nw_t

    print("  Col1: D2-D10 dummies only")
    m1, t1 = run_fm_dummies([], 'Col1')
    print(f"  D10 coef: {m1.get('D10', np.nan)*100:.3f}% (t={t1.get('D10', np.nan):.2f})")

    print("  Col2: D2-D10 + standard controls")
    m2, t2 = run_fm_dummies(['log_mcap', 'mom', 'rev'], 'Col2')
    print(f"  D10 coef: {m2.get('D10', np.nan)*100:.3f}% (t={t2.get('D10', np.nan):.2f})")

    metrics = {
        'Col1_D10_coef': m1.get('D10', np.nan) * 100,
        'Col1_D10_tstat': t1.get('D10', np.nan),
        'Col2_D10_coef': m2.get('D10', np.nan) * 100,
        'Col2_D10_tstat': t2.get('D10', np.nan),
    }

    # Write markdown
    headers = ['Decile dummy', 'Col1: D2-D10', 'Col2: + controls']
    rows = []
    for d in range(2, 11):
        m1c = m1.get(f'D{d}', np.nan) * 100
        t1c = t1.get(f'D{d}', np.nan)
        m2c = m2.get(f'D{d}', np.nan) * 100
        t2c = t2.get(f'D{d}', np.nan)
        rows.append([f'D{d}', f"{m1c:.3f} ({t1c:.2f})", f"{m2c:.3f} ({t2c:.2f})"])

    notes = ("Fama-MacBeth regression of one-month-ahead excess returns on MAX^beta "
             "decile dummies (D1 omitted). MAX^beta = conditional double sort on "
             "10 beta deciles x 10 MAX deciles. Beta computed from 36-month rolling "
             "monthly regression on FF mkt_rf.")
    write_md('table_8.md', 'Table 8: Fama-MacBeth Regressions on MAX^beta', headers, rows, notes)
    return metrics


def main():
    panel = load_panel()
    ff = load_ff()
    beta = load_beta()

    t1 = table1(panel, ff)
    print("\n[done] Table 1 written")

    if beta is not None:
        t6 = table6(panel, ff, beta)
        print("[done] Table 6 written")
        t8 = table8(panel, beta)
        print("[done] Table 8 written")
    else:
        print("Skipping Table 6, 8 (no beta)")
        t6 = None
        t8 = None

    t4 = table4(panel)
    print("[done] Table 4 written")

    # Save all metrics
    import json
    all_metrics = {
        'table1': {k: (v if not isinstance(v, pd.Series) else v.to_dict()) for k, v in t1['metrics'].items()},
        'table4': t4,
    }
    if t6 is not None:
        all_metrics['table6'] = {k: (v if not isinstance(v, pd.Series) else v.to_dict()) for k, v in t6['metrics'].items()}
    if t8 is not None:
        all_metrics['table8'] = t8
    with open(DATA / "metrics_all.json", "w") as f:
        json.dump(all_metrics, f, indent=2, default=str)
    print(f"\n[done] all metrics written")


if __name__ == "__main__":
    main()
