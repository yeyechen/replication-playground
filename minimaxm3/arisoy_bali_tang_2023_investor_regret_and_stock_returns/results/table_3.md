# Table 3 — Dependent Bivariate Sorts: REG Premium Across 12 Controls

Sample: NYSE/AMEX/NASDAQ common stocks (shrcd 10,11), $5-$1000 price screen.
Sort month = June 1963 to November 2020 (689 months).
Each month: sort into control quintiles (NYSE breakpoints), then within each
control quintile sort into REG quintiles (NYSE breakpoints). Compute next-month
VW (me_lag1-weighted) excess returns. Then time-series regression of each
(control_q, reg_q) cell's monthly VW return on FF5 factors (NW-6 t-stats).

Each cell below is the FF5 alpha (in %/month) of the AVERAGE across the 5
control-quintile alphas for that REG quintile. The HL column is the average
across control quintiles of the (Q5 - Q1) spread.

Note: paper uses FF6PS alphas; per Assumption 3 we substitute FF5 (LIQ missing).
For audit major [M3], we also compute FF5+MOM (proxy for FF6 minus LIQ) and
record the |FF5 - FF5+MOM| shift per control.

| Control | Q1 (Low REG) | Q2 | Q3 | Q4 | Q5 (High REG) | High-Low |
|---|---:|---:|---:|---:|---:|---:|
| BETA | -0.32% | -0.27% | -0.13% | 0.02% | 0.29% | 0.61% |
| SIZE | -0.16% | -0.03% | 0.12% | 0.35% | 0.90% | 1.06% |
| BM | -0.31% | -0.17% | -0.03% | 0.02% | 0.33% | 0.64% |
| MOM | -0.32% | -0.24% | -0.11% | 0.06% | 0.35% | 0.68% |
| STR | -0.29% | -0.20% | -0.06% | 0.06% | 0.37% | 0.66% |
| COSKEW | -0.24% | -0.21% | -0.10% | 0.10% | 0.36% | 0.60% |
| ILLIQ | -0.34% | -0.15% | 0.02% | 0.23% | 0.76% | 1.11% |
| IVOL | -0.31% | -0.22% | -0.09% | 0.02% | 0.40% | 0.71% |
| MAX | -0.31% | -0.20% | -0.12% | 0.03% | 0.32% | 0.63% |
| OP | -0.24% | -0.22% | -0.06% | 0.10% | 0.45% | 0.70% |
| IA | -0.25% | -0.19% | -0.06% | 0.10% | 0.38% | 0.63% |
| SUE | -0.11% | -0.15% | -0.10% | 0.04% | 0.33% | 0.44% |

## Comparison with paper Table 3

Ours vs paper for each cell. Format: ours vs paper. Highlight: > 50% divergence.

| Control | Cell | Ours | Paper | Diff (%) | Note |
|---|---|---:|---:|---:|---|
| BETA | Q1 | -0.3204 | -0.3600 | 11.0% | |
| BETA | Q2 | -0.2743 | -0.3000 | 8.6% | |
| BETA | Q3 | -0.1294 | -0.2100 | 38.4% | |
| BETA | Q4 | 0.0238 | 0.0000 | inf%  **DIVERGENCE** | |
| BETA | Q5 | 0.2920 | 0.2100 | 39.1% | |
| BETA | HL | 0.6125 | 0.5600 | 9.4% | |
| SIZE | Q1 | -0.1553 | -0.4600 | 66.2%  **DIVERGENCE** | |
| SIZE | Q2 | -0.0333 | -0.2500 | 86.7%  **DIVERGENCE** | |
| SIZE | Q3 | 0.1202 | -0.1500 | 180.2%  **DIVERGENCE** | |
| SIZE | Q4 | 0.3541 | 0.0000 | inf%  **DIVERGENCE** | |
| SIZE | Q5 | 0.9012 | 0.3500 | 157.5%  **DIVERGENCE** | |
| SIZE | HL | 1.0565 | 0.8100 | 30.4% | |
| BM | Q1 | -0.3107 | -0.4000 | 22.3% | |
| BM | Q2 | -0.1675 | -0.2300 | 27.2% | |
| BM | Q3 | -0.0259 | -0.1400 | 81.5%  **DIVERGENCE** | |
| BM | Q4 | 0.0242 | 0.0400 | 39.5% | |
| BM | Q5 | 0.3324 | 0.2300 | 44.5% | |
| BM | HL | 0.6431 | 0.6300 | 2.1% | |
| MOM | Q1 | -0.3237 | -0.4200 | 22.9% | |
| MOM | Q2 | -0.2397 | -0.2900 | 17.3% | |
| MOM | Q3 | -0.1077 | -0.1700 | 36.6% | |
| MOM | Q4 | 0.0633 | -0.0600 | 205.4%  **DIVERGENCE** | |
| MOM | Q5 | 0.3547 | 0.1800 | 97.1%  **DIVERGENCE** | |
| MOM | HL | 0.6785 | 0.6000 | 13.1% | |
| STR | Q1 | -0.2908 | -0.3000 | 3.1% | |
| STR | Q2 | -0.2046 | -0.2200 | 7.0% | |
| STR | Q3 | -0.0649 | -0.1000 | 35.1% | |
| STR | Q4 | 0.0625 | -0.0300 | 308.5%  **DIVERGENCE** | |
| STR | Q5 | 0.3700 | 0.2200 | 68.2%  **DIVERGENCE** | |
| STR | HL | 0.6608 | 0.5200 | 27.1% | |
| COSKEW | Q1 | -0.2418 | -0.3000 | 19.4% | |
| COSKEW | Q2 | -0.2073 | -0.2400 | 13.6% | |
| COSKEW | Q3 | -0.0965 | -0.1500 | 35.6% | |
| COSKEW | Q4 | 0.1041 | 0.0600 | 73.5%  **DIVERGENCE** | |
| COSKEW | Q5 | 0.3584 | 0.2700 | 32.8% | |
| COSKEW | HL | 0.6002 | 0.5700 | 5.3% | |
| ILLIQ | Q1 | -0.3415 | -0.5100 | 33.0% | |
| ILLIQ | Q2 | -0.1467 | -0.2500 | 41.3% | |
| ILLIQ | Q3 | 0.0249 | -0.1700 | 114.7%  **DIVERGENCE** | |
| ILLIQ | Q4 | 0.2328 | 0.0000 | inf%  **DIVERGENCE** | |
| ILLIQ | Q5 | 0.7650 | 0.3300 | 131.8%  **DIVERGENCE** | |
| ILLIQ | HL | 1.1065 | 0.8400 | 31.7% | |
| IVOL | Q1 | -0.3150 | -0.3800 | 17.1% | |
| IVOL | Q2 | -0.2173 | -0.2300 | 5.5% | |
| IVOL | Q3 | -0.0948 | -0.2400 | 60.5%  **DIVERGENCE** | |
| IVOL | Q4 | 0.0241 | -0.0200 | 220.5%  **DIVERGENCE** | |
| IVOL | Q5 | 0.3971 | 0.2300 | 72.6%  **DIVERGENCE** | |
| IVOL | HL | 0.7121 | 0.6100 | 16.7% | |
| MAX | Q1 | -0.3111 | -0.3400 | 8.5% | |
| MAX | Q2 | -0.2018 | -0.2000 | 0.9% | |
| MAX | Q3 | -0.1200 | -0.2300 | 47.8% | |
| MAX | Q4 | 0.0255 | 0.0100 | 155.4%  **DIVERGENCE** | |
| MAX | Q5 | 0.3166 | 0.1700 | 86.2%  **DIVERGENCE** | |
| MAX | HL | 0.6276 | 0.5100 | 23.1% | |
| OP | Q1 | -0.2432 | -0.3800 | 36.0% | |
| OP | Q2 | -0.2153 | -0.2300 | 6.4% | |
| OP | Q3 | -0.0558 | -0.2000 | 72.1%  **DIVERGENCE** | |
| OP | Q4 | 0.0971 | -0.1000 | 197.1%  **DIVERGENCE** | |
| OP | Q5 | 0.4524 | 0.2400 | 88.5%  **DIVERGENCE** | |
| OP | HL | 0.6956 | 0.6200 | 12.2% | |
| IA | Q1 | -0.2533 | -0.3100 | 18.3% | |
| IA | Q2 | -0.1882 | -0.2000 | 5.9% | |
| IA | Q3 | -0.0575 | -0.1600 | 64.1%  **DIVERGENCE** | |
| IA | Q4 | 0.1019 | -0.0300 | 439.8%  **DIVERGENCE** | |
| IA | Q5 | 0.3752 | 0.2500 | 50.1%  **DIVERGENCE** | |
| IA | HL | 0.6285 | 0.5600 | 12.2% | |
| SUE | Q1 | -0.1086 | -0.2800 | 61.2%  **DIVERGENCE** | |
| SUE | Q2 | -0.1457 | -0.1500 | 2.8% | |
| SUE | Q3 | -0.1037 | -0.1600 | 35.2% | |
| SUE | Q4 | 0.0380 | -0.0600 | 163.3%  **DIVERGENCE** | |
| SUE | Q5 | 0.3285 | 0.2700 | 21.7% | |
| SUE | HL | 0.4371 | 0.5500 | 20.5% | |

## M3 — FF5 vs FF5+MOM shift per control (HL spread)

FF5 = Mkt-RF + SMB + HML + RMW + CMA. FF5+MOM adds MOM (proxy for FF6 minus LIQ).
The shift = FF5 - FF5+MOM approximates the marginal impact of MOM on the alpha.
Paper's HL column uses FF6PS = FF5 + MOM + LIQ. Our FF5+MOM HL is a partial
substitute for FF6PS (LIQ missing).

| Control | Ours FF5 HL | Ours FF5+MOM HL | Shift | Paper FF6PS HL | Ours-FF5 vs Paper |
|---|---:|---:|---:|---:|---:|
| BETA | 0.6125% | 0.6390% | -0.0265% | 0.56% | 9.4% |
| SIZE | 1.0565% | 1.0327% | +0.0238% | 0.81% | 30.4% |
| BM | 0.6431% | 0.6421% | +0.0010% | 0.63% | 2.1% |
| MOM | 0.6785% | 0.7173% | -0.0388% | 0.60% | 13.1% |
| STR | 0.6608% | 0.6716% | -0.0108% | 0.52% | 27.1% |
| COSKEW | 0.6002% | 0.6030% | -0.0028% | 0.57% | 5.3% |
| ILLIQ | 1.1065% | 1.0928% | +0.0136% | 0.84% | 31.7% |
| IVOL | 0.7121% | 0.7166% | -0.0045% | 0.61% | 16.7% |
| MAX | 0.6276% | 0.6460% | -0.0184% | 0.51% | 23.1% |
| OP | 0.6956% | 0.6952% | +0.0003% | 0.62% | 12.2% |
| IA | 0.6285% | 0.6309% | -0.0024% | 0.56% | 12.2% |
| SUE | 0.4371% | 0.4475% | -0.0104% | 0.55% | 20.5% |
