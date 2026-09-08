# T5 replication grid

| cell | paper | ours | status |
|---|---|---|---|
| er_cond127_q1 | 1.07 | 1.1020 | Match |
| er_cond127_q1_t | 4.58 | 4.6606 | Match |
| er_cond127_q2 | 0.77 | 0.6840 | Match |
| er_cond127_q2_t | 3.67 | 3.2350 | Match |
| er_cond127_q3 | 0.95 | 0.9314 | Match |
| er_cond127_q3_t | 4.2 | 4.0353 | Match |
| er_cond127_q4 | 0.95 | 1.0099 | Match |
| er_cond127_q4_t | 4.69 | 5.0220 | Match |
| er_cond127_q5 | 1.3 | 1.3005 | Match |
| er_cond127_q5_t | 6.35 | 6.2477 | Match |
| er_cond62_q1 | 0.26 | 0.2624 | no_effect |
| er_cond62_q1_t | 0.97 | 0.9888 | Match |
| er_cond62_q2 | 0.26 | 0.1502 | no_effect |
| er_cond62_q2_t | 1.02 | 0.5956 | Match |
| er_cond62_q3 | 0.29 | 0.1374 | no_effect |
| er_cond62_q3_t | 1.17 | 0.5467 | FAIL |
| er_cond62_q4 | 0.39 | 0.4073 | no_effect |
| er_cond62_q4_t | 1.73 | 1.7831 | Match |
| er_cond62_q5 | 0.49 | 0.4609 | no_effect |
| er_cond62_q5_t | 1.93 | 1.7853 | Match |
| alpha_cond127_q1 | 0.15 | 0.2185 | no_effect |
| alpha_cond127_q1_t | 0.84 | 1.1766 | Match |
| alpha_cond127_q2 | -0.15 | -0.2399 | no_effect |
| alpha_cond127_q2_t | -0.93 | -1.5532 | FAIL |
| alpha_cond127_q3 | -0.03 | 0.0194 | no_effect |
| alpha_cond127_q3_t | -0.18 | 0.1162 | FAIL |
| alpha_cond127_q4 | 0.04 | 0.0887 | no_effect |
| alpha_cond127_q4_t | 0.29 | 0.6292 | Match |
| alpha_cond127_q5 | 0.39 | 0.4318 | Match |
| alpha_cond127_q5_t | 2.8 | 3.0694 | Match |
| alpha_cond62_q1 | -0.17 | -0.1557 | no_effect |
| alpha_cond62_q1_t | -0.65 | -0.6029 | Match |
| alpha_cond62_q2 | -0.05 | -0.1827 | no_effect |
| alpha_cond62_q2_t | -0.21 | -0.7432 | FAIL |
| alpha_cond62_q3 | -0.2 | -0.2956 | no_effect |
| alpha_cond62_q3_t | -0.82 | -1.1782 | Match |
| alpha_cond62_q4 | 0.01 | 0.0250 | no_effect |
| alpha_cond62_q4_t | 0.06 | 0.1077 | Match |
| alpha_cond62_q5 | 0.07 | 0.0576 | no_effect |
| alpha_cond62_q5_t | 0.28 | 0.2264 | Match |

## Inner-breakpoint convention (iteration 7 adoption): er_cond62

Base (committed): inner momentum quintile breakpoints from UNCONDITIONAL NYSE quintiles of r_6,2 applied within each IR (r_12,7) quintile (Assumption 9 as corrected in iteration 7; paper Table 7 note 'Portfolio break points based on NYSE stocks only', content.md L1701). Alternative (report-only): breakpoints computed WITHIN each IR quintile subsample (superseded reading of Assumption 9). %/mo [t].

| IR quintile | paper | base (uncond NYSE) | alternative (within) | alternative months |
|---|---|---|---|---|
| 1 | 0.26 [0.97] | 0.26 [0.99] | 0.75 [2.14] | 504 |
| 2 | 0.26 [1.02] | 0.15 [0.60] | 0.31 [1.22] | 504 |
| 3 | 0.29 [1.17] | 0.14 [0.55] | 0.05 [0.21] | 504 |
| 4 | 0.39 [1.73] | 0.41 [1.78] | 0.44 [1.90] | 504 |
| 5 | 0.49 [1.93] | 0.46 [1.79] | 0.69 [2.32] | 504 |
