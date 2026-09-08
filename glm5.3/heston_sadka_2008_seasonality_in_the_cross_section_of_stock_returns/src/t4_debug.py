"""T4 debug (iteration 9): cross-validate pi(k) against table1-style cov.

Step 1: compute, on the identical 1963-01..2002-02 sub-panel:
  - buggy pi(k): table4.py current code (masked cells contribute mA*mB)
  - fixed  pi(k): mask applied AFTER demeaning (excludes missing stocks)
  - ref    pi(k): table1._slope-style cov per (t,k), mean over t
for k in (1, 2, 3, 12, 24).
"""
import numpy as np
import pandas as pd

from main import LAYOUT, _wide_matrix

T4_START = pd.Period("1963-01", freq="M")
T4_END = pd.Period("2002-12", freq="M")

panel = pd.read_parquet(LAYOUT.data_path("panel.parquet"))
panel["month"] = pd.PeriodIndex(panel["month"], freq="M")
sub = panel[(panel["month"] >= T4_START) & (panel["month"] <= T4_END)]
R, m_idx, months, permnos, _ = _wide_matrix(sub)
Rf = R.astype(np.float64)
nan = np.isnan(Rf)
n_rows = Rf.shape[0]
print(f"matrix {Rf.shape}, months {months[0]}..{months[-1]}")

for k in (1, 2, 3, 12, 24):
    A = Rf[:n_rows - k, :]
    B = Rf[k:, :]
    m = (~nan[:n_rows - k, :]) & (~nan[k:, :])
    n = m.sum(axis=1)
    valid = n >= 2
    Av = np.where(m, A, 0.0)
    Bv = np.where(m, B, 0.0)
    mA = Av.sum(axis=1)[valid] / n[valid]
    mB = Bv.sum(axis=1)[valid] / n[valid]
    # buggy: masked cells keep (-mA)*(-mB) inside the sum
    a_bug = np.where(m[valid], A[valid], 0.0) - mA[:, None]
    b_bug = np.where(m[valid], B[valid], 0.0) - mB[:, None]
    pi_bug = ((a_bug * b_bug).sum(axis=1) / n[valid]).mean()
    # fixed: zero the masked cells after demeaning
    a_fix = np.where(m[valid], A[valid] - mA[:, None], 0.0)
    b_fix = np.where(m[valid], B[valid] - mB[:, None], 0.0)
    pi_fix = ((a_fix * b_fix).sum(axis=1) / n[valid]).mean()
    # reference: per-(t,k) covariance, table1 _slope numerator logic
    covs = []
    for j in np.where(valid)[0]:
        x = A[j][m[j]]
        y = B[j][m[j]]
        covs.append(np.dot(x - x.mean(), y - y.mean()) / len(x))
    pi_ref = float(np.mean(covs))
    print(f"k={k:2d}  buggy={pi_bug*100:+.4f}  fixed={pi_fix*100:+.6f}  "
          f"ref={pi_ref*100:+.6f}  fixed-ref={pi_fix-pi_ref:.2e}  "
          f"avgN={n[valid].mean():,.0f} totalN={Rf.shape[1]}")
