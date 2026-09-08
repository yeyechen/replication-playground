# T1 replication grid

| cell | paper | ours | status |
|---|---|---|---|
| r127_late | 0.93 | 0.7911 | Match |
| r127_late_t | 5.17 | 4.3920 | Match |
| r127_third | 1.24 | 1.1592 | Match |
| r127_third_t | 5.29 | 4.8603 | Match |
| r127_fourth | 0.61 | 0.4229 | Match |
| r127_fourth_t | 2.26 | 1.5754 | Match |
| r62_late | 0.36 | 0.2331 | no_effect |
| r62_late_t | 1.32 | 0.8611 | Match |
| r62_third | 0.37 | 0.3529 | no_effect |
| r62_third_t | 1.0 | 0.9976 | Match |
| r62_fourth | 0.36 | 0.1133 | no_effect |
| r62_fourth_t | 0.87 | 0.2761 | FAIL |
| r10_late | -6.1 | -6.3861 | Match |
| r10_late_t | -13.8 | -14.2169 | Match |
| r10_third | -8.18 | -8.4405 | Match |
| r10_third_t | -13.8 | -14.1772 | Match |
| r10_fourth | -4.02 | -4.3316 | Match |
| r10_fourth_t | -6.36 | -6.6790 | Match |
| logme_late | -0.09 | -0.1217 | Match |
| logme_late_t | -2.29 | -2.9100 | Match |
| logme_third | -0.04 | -0.0449 | no_effect |
| logme_third_t | -0.68 | -0.7828 | Match |
| logme_fourth | -0.15 | -0.1985 | Match |
| logme_fourth_t | -2.52 | -3.2733 | Match |
| logbm_late | 0.31 | 0.2791 | Match |
| logbm_late_t | 5.39 | 4.9972 | Match |
| logbm_third | 0.48 | 0.4443 | Match |
| logbm_third_t | 5.47 | 5.2260 | Match |
| logbm_fourth | 0.14 | 0.1138 | no_effect |
| logbm_fourth_t | 1.9 | 1.6010 | Match |
| diff_late | 0.57 | 0.5580 | Match |
| diff_late_t | 2.42 | 2.4014 | Match |
| diff_third | 0.88 | 0.8064 | Match |
| diff_third_t | 2.96 | 2.8234 | Match |
| diff_fourth | 0.25 | 0.3095 | no_effect |
| diff_fourth_t | 0.69 | 0.8446 | Match |

## FM sample counts (firm-months, listwise)

| sample | months | total obs | avg/month | min/month |
|---|---|---|---|---|
| late | 504 | 2,361,638 | 4685.8 | 1603 |
| third | 252 | 918,640 | 3645.4 | 1603 |
| fourth | 252 | 1,442,998 | 5726.2 | 4520 |

## Invariant: max |b(diff) - (b(r127)-b(r62))| per month (raw coefficient units)

| sample | diff row (b127-b62 series) | substitution regression (diff sole regressor) |
|---|---|---|
| late | 0.00e+00 | 0.2779 |
| third | 0.00e+00 | 0.1649 |
| fourth | 0.00e+00 | 0.2779 |

The substitution-regression deviation is the omitted-regressor effect (replacing [r127, r62] by [diff] alone removes r62 from the column space); the paper's diff row is the coefficient difference of the SAME regression, which is what the diff-row column reports (exact by construction).

log_bm coverage by decade (share of firm-months with ret/r127/r62/r10/log_me present): 1960s 0.811, 1970s 0.830, 1980s 0.840, 1990s 0.860, 2000s 0.850, 2010s 0.754
