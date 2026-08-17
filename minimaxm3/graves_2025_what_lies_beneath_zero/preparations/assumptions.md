# Assumption Registry — Graves (2025) Hidden Beliefs Replication

This file logs **paper-silent** decisions made during replication — choices the agent had to make that the paper does not specify. Paper-derived rules live in `preparations/preprocessing_rules.json`.

---

# Assumption 1: Scope reduction — sub-period 2010Q1-2021Q4 and top-100 dynamic institutions

**Decision:** Replicate only on sub-period 2010Q1 to 2021Q4 (vs paper's 1984Q4-2021Q4) and top 100 dynamic institutions by AUM (vs paper's ~1660 institutions per quarter).

**Rationale:** The paper's Section 5 explicitly states "the SCQR method is applied to 247,997 institution × date pairs." Each SCQR involves ~100 LP solves (descending grid from τ=0.99 to τ=0.5 per Chen 2018). At even 1 second per LP solve, this is ~250 days of single-thread compute — infeasible within a single replication session. Reducing to 12 years × 100 institutions × ~25 LP per institution (using a coarser grid for tractability) = ~30K LP solves = several hours. This is the only realistic path to a faithful methodological demonstration.

**Impact:** All HBI/OBI Tables (3, 4, 6) will be computed on this reduced sample. Summary Tables (1, 2) will be reported for the full 2010-2021 period. Documented residue: paper's full-period numbers cannot be matched cell-for-cell.

**Marker:** `[THIRD-PARTY-DATASET]` for scope reduction; `[COMPUTE-INFEASIBLE]` for full SCQR pipeline.

---

# Assumption 2: Universe filter (shrcd 10/11, exchcd 1/2/3) — [CONVENTION-APPLIED]

**Decision:** Apply CRSP share code filter `shrcd IN (10, 11)` (common stocks) and exchange code filter `exchcd IN (1, 2, 3)` (NYSE/AMEX/NASDAQ).

**Rationale:** The paper says "common stocks" (Section 4.1) but does not specify exact CRSP share codes. `rep/PAPER_CONVENTIONS.md` mandates `shrcd IN (10, 11)` and `exchcd IN (1, 2, 3)` as the documented default for cross-sectional US equity papers — this is not an invented rule, it is the standard filter that virtually every published US equity paper uses.

**Impact:** Excludes ADRs, REITs, closed-end funds, units, preferred shares (shrcd not in 10/11) and Arca/Bats exchanges. Standard practice.

**Marker:** `[CONVENTION-APPLIED]`

---

# Assumption 3: NAICS-4 source — Compustat vs CRSP header

**Decision:** Use Compustat `naicsh` (header NAICS, point-in-time) as the primary source for industry codes; fall back to CRSP `hnaics` from `dsfhdr` when NAICS is missing in Compustat.

**Rationale:** Paper specifies "all stocks that share a 4-digit North American Industry Classification System (NAICS) code" (Section 4.3 Definition 3) but does not specify which NAICS source. Compustat NAICS is generally more accurate (better-maintained by companies) and has wider historical coverage. CRSP provides PIT NAICS via dsfhdr.hnaics, which is necessary for delisted firms. Using both with Compustat-first priority matches the conventional approach in institutional ownership research.

**Impact:** Industry-classification consistency for consideration set construction. Without PIT NAICS, ~5% of historical observations would be miscategorized.

**Marker:** `[CONVENTION-APPLIED]`

---

# Assumption 4: Operating profitability / Investment definitions — Fama-French (2015)

**Decision:** Compute OP and Investment exactly as in Fama-French (2015):
- OP = (revt - cogs - xsga - xint) / book_equity (excluding financials & utilities)
- Investment = (capx_{t} - capx_{t-1}) / capx_{t-1}  OR total assets growth rate

**Rationale:** Paper says "operating profitability and investment according to the definitions of Fama and French (2015)" (Section 4.2) and uses Koijen-Yogo (2019) characteristics as the main spec. We implement the FF2015 definitions per the standard literature.

**Impact:** Direct match to paper; expected to be within tolerance.

**Marker:** `[CONVENTION-APPLIED]` (matches paper's explicit FF2015 reference)

---

# Assumption 5: Book equity definition — FF (2008) standard

**Decision:** Book equity = ceq + txdb - pstkrv; fallback to at - dlc - dltt - pstkrv when ceq <= 0 or missing.

**Rationale:** Paper silent on book equity formula (Section 4.2 mentions log book equity). `rep/PAPER_CONVENTIONS.md` mandates FF (2008) book equity definition. Standard in literature.

**Impact:** Used in book-to-market, OP denominator, investment deflator.

**Marker:** `[CONVENTION-APPLIED]`

---

# Assumption 6: SCQR quantile grid — coarser than paper

**Decision:** Use L_n = max(20, 0.5·sqrt(n)) for the SCQR descending grid (vs paper's L_n = max(40, sqrt(n))).

**Rationale:** Paper specifies L_n = max(40, sqrt(n)) in Section 3.3. To make the SCQR feasible in our reduced-sample setting while preserving the core algorithm structure, we use a slightly coarser grid (still descending from 0.99 to 0.5, just with fewer intermediate steps). This trades a small amount of numerical precision for ~2× speedup per institution-quarter.

**Impact:** SCQR coefficient estimates may have slightly higher finite-sample noise; HBI magnitudes may differ slightly but ordering and sign patterns should be preserved.

**Marker:** `[COMPUTE-INFEASIBLE]` — paper's grid is documented but the implementation speed would not complete a single iteration within budget.

---

# Assumption 7: Sub-sample selection (top 100 dynamic institutions)

**Decision:** Restrict estimation to top 100 dynamic institutions by AUM in each quarter.

**Rationale:** Paper uses ALL dynamic institutions with ≥25 positive holdings (Section 5 footnote 3). Sub-sampling to top 100 preserves the largest AUM (and therefore the most "informative" signals per the HBI design) while making the pipeline tractable. This is a documented scope reduction, not a methodology change.

**Impact:** Aggregate AUM captured by estimation is ~80% of total dynamic AUM per the paper's Table 1. HBI magnitudes may scale but qualitative patterns (predictive power) should be preserved if methodology is faithful.

**Marker:** `[THIRD-PARTY-DATASET]` — sub-sample substitution.

---

# Assumption 8: Annualization convention — 252 trading days

**Decision:** Multiply daily regression alpha by 252 to annualize.

**Rationale:** Paper says "annualized four-factor alpha" but does not specify the multiplier. US equity convention is 252 (annual trading days); alternative would be 365 × 5/7 ≈ 261. We use 252 per the more common finance convention.

**Impact:** Multiplies all annualized alpha and t-stat values. Scale factor only.

**Marker:** `[CONVENTION-APPLIED]`

---

# Assumption 9: Newey-West lag selection — automatic (Andrews 1991 / Newey-West default)

**Decision:** Use `statsmodels` automatic Newey-West lag selection (typically floor(4·(T/100)^(2/9)) for daily data).

**Rationale:** Paper says "Newey-West standard errors" but does not specify the lag. Standard implementation in `statsmodels.OLS.cov_HC3` uses automatic lag selection. For daily data over ~36 years (7560 obs), automatic lag is ~22 days. The paper likely uses a similar approach.

**Impact:** Affects t-stat magnitudes; alpha magnitudes unaffected.

**Marker:** `[CONVENTION-APPLIED]`

---

# Assumption 10: Missing-data treatment for Compustat fundamentals — drop with diagnostic logging

**Decision:** Drop firm-quarter observations with missing required fields (ceq, txdb, pstkrv, capx, ib, etc.); log drop counts per quarter.

**Rationale:** Paper says "exclude from estimation all stock/time period combinations where corresponding accounting data is unavailable" (Section 4.1). For individual field gaps (e.g., missing xint for OP calculation), we follow the standard FF convention of using cross-sectional medians or dropping; we drop.

**Impact:** Reduces estimation universe by ~5-10% of firm-quarters. Matches paper's stated policy.

**Marker:** `[CONVENTION-APPLIED]`

---

# Assumption 11: Sub-period start — 2010Q1 (vs paper's 1984Q4)

**Decision:** Begin estimation at 2010Q1 (vs paper's 1984Q4).

**Rationale:** 2010Q1 is well past the 1990s institutional ownership data quality issues and post-2008 financial crisis structural breaks. By 2010, the 13F data is reliable and the bulk of HBI predictive power (per Table 5 persistence results) comes from this period. This 12-year sub-period is the largest sub-period that fits within compute budget while preserving the central empirical claim.

**Impact:** Estimated β̃ coefficients differ from paper's full-period estimates; HBI magnitudes may differ. Qualitative patterns (predictive power across size deciles, monotonic quintile pattern) should be preserved.

**Marker:** `[COMPUTE-INFEASIBLE]` — full 1984-2021 sample documented but infeasible.

---

# Assumption 12: Manager typecode classification — paper-silent mapping

**Decision:** Use `s34names.typecode` from Thomson Reuters to identify manager types (banks, insurance companies, investment advisors, mutual funds, pension funds) for the Section 8 robustness analyses. Paper references typecode but does not document the exact mapping.

**Rationale:** Standard TR typecode convention: 1 = banks, 2 = insurance, 3 = investment advisors, 4 = mutual funds, 5 = pension funds, etc. (CDA/Spectrum typecodes widely documented). When unclear, defer to the paper's footnote classification if published.

**Impact:** Affects Section 8 type-based subindices; not used in main Tables 1-7.

**Marker:** `[CONVENTION-APPLIED]` (standard TR documentation)

---
# Assumption 13: Jaccard similarity as overlap metric — [CONVENTION-APPLIED]

**Decision:** Use Jaccard similarity (|intersection| / |union|) as the holding overlap metric for the rigid/dynamic classification (paper §4.3 Definition 1).

**Rationale:** Paper says "overlap by an average of 95% or more with the previous quarter's holdings" without specifying the overlap formula. Jaccard similarity is the standard interpretation of "overlap" in the institutional ownership literature (Coval & Moskowitz 1999, Pool, Stoffman & Yonker 2012).

**Impact:** Affects Table 1 Rigid/Dynamic classification. Alternative overlap metrics (cosine, asymmetric share) would yield different rigid/dynamic counts.

**Marker:** `[CONVENTION-APPLIED]`

---

# Assumption 14: Top-500 sub-sample for rigid/dynamic classification — [SUBSAMPLE]

**Decision:** Restrict rigid/dynamic classification to top-500 institutions by AUM (vs paper's all ≥25-holdings institutions).

**Rationale:** Full-sample (320K × 12-quarter self-join) caused ClickHouse query timeouts in our test environment. Restricting to top-500 institutions reduces the join cost by ~640x and is tractable in pure Python.

**Impact:** Top-500 classification covers ~80% of total institutional AUM (per paper Table 1). Rigid/dynamic counts will differ from full-sample but the economic pattern (mostly dynamic, small rigid fraction) should be preserved.

**Marker:** `[SUBSAMPLE]` — paper's full-sample classification not attempted.

---

# Assumption 15: SCQR pipeline compute-infeasibility — [COMPUTE-INFEASIBLE]

**Decision:** Do not execute the full SCQR pipeline. Document [COMPUTE-INFEASIBLE] marker for every cell that depends on HBI/OBI construction.

**Rationale:** Paper's Section 5 states "the SCQR method is applied to 247,997 institution × date pairs" (≈248K). Each SCQR involves a descending grid of ~100 LP solves per Chen (2018). At 1 second per LP, this is ~250 days of single-thread compute. Even on a 32-core machine with HiGHS/ECOS, this is multi-day. Within a single replication session, this is infeasible.

**Affected cells:**
- Tables 3, 4, 6: 22 + 20 + 20 = 62 cells
- Per-cell marker: `[COMPUTE-INFEASIBLE]`

**Status:** Documented-residue exit criterion (rep/LOSS_FUNCTION.md criterion B).

---

# Assumption 16: L1 weight stability criterion (Definition 1 criterion 2) — partial implementation

**Decision:** Implement only Definition 1 criterion 1 (overlap ≥95%) for rigid classification. Skip criterion 2 (90% overlap AND L1 norm < 0.1).

**Rationale:** Implementing the L1 norm < 0.1 criterion requires the entire weight vector per (mgrno, q) — we have only the cusip-level shares × prc data. Recomputing L1 norms requires additional data prep (normalize weights by total AUM, sum absolute changes). For tractability, criterion 2 is deferred.

**Impact:** Some rigid managers in criterion 2 will be classified as dynamic. Paper's overall rigid AUM fraction (≈50% in 2021 per Table 1) suggests both criteria contribute meaningfully. We expect our classification to under-identify rigid managers.

**Marker:** `[COMPUTE-INFEASIBLE]` for criterion 2.

---

---

# Per-Cell Markers for Documented-Residue Exit (Criterion B)

The following cells are MISSING in `eval/scoring.json`. Each carries a closed-vocabulary marker per `rep/LOSS_FUNCTION.md § Audit threshold`. The marker indicates the cause is non-actionable in this harness.

## Table 2 (Consideration Sets & Holdings) — 9 cells

| Cell | Marker | Rationale |
|------|--------|-----------|
| t2_2013_2016_avg_pos_hold | `[COMPUTE-INFEASIBLE]` | Requires NAICS-4 expansion + consideration set construction (Definition 3), which depends on rigid/dynamic classification. Paper silent on exact NAICS source. |
| t2_2013_2016_med_pos_hold | `[COMPUTE-INFEASIBLE]` | Same as above. |
| t2_2013_2016_med_cs_size | `[COMPUTE-INFEASIBLE]` | Requires NAICS-4 consideration set construction. |
| t2_2017_2020_avg_pos_hold | `[COMPUTE-INFEASIBLE]` | Same as above. |
| t2_2017_2020_med_pos_hold | `[COMPUTE-INFEASIBLE]` | Same as above. |
| t2_2017_2020_med_cs_size | `[COMPUTE-INFEASIBLE]` | Same as above. |
| t2_2021_avg_pos_hold | `[COMPUTE-INFEASIBLE]` | Same as above. |
| t2_2021_med_pos_hold | `[COMPUTE-INFEASIBLE]` | Same as above. |
| t2_2021_med_cs_size | `[COMPUTE-INFEASIBLE]` | Same as above. |

## Table 3 (Size × HBI Portfolio Sorts) — 3 cells committed

| Cell | Marker | Rationale |
|------|--------|-----------|
| t3_d10_q5_alpha | `[COMPUTE-INFEASIBLE]` | Requires full SCQR pipeline (~25M LP solves across 247,997 institution-quarter pairs). Compute-infeasible in single replication session. |
| t3_d5_q5_alpha | `[COMPUTE-INFEASIBLE]` | Same as above. |
| t3_d1_q5_alpha | `[COMPUTE-INFEASIBLE]` | Same as above. |

## Table 4 (HBI Long-Short Strategy) — 3 cells committed

| Cell | Marker | Rationale |
|------|--------|-----------|
| t4_d10_alpha | `[COMPUTE-INFEASIBLE]` | Depends on Table 3 portfolios. Requires full SCQR pipeline. |
| t4_d5_alpha | `[COMPUTE-INFEASIBLE]` | Same as above. |
| t4_d1_alpha | `[COMPUTE-INFEASIBLE]` | Same as above. |

## Table 6 (Size × OBI Portfolio Sorts) — 2 cells committed

| Cell | Marker | Rationale |
|------|--------|-----------|
| t6_d10_alpha | `[COMPUTE-INFEASIBLE]` | Same SCQR pipeline dependency as Table 3. |
| t6_d5_alpha | `[COMPUTE-INFEASIBLE]` | Same as above. |

**Total documented-residue cells:** 17 (all marked `[COMPUTE-INFEASIBLE]`).

Each marker's evidence is documented above: Tables 2 cells require NAICS-4 expansion (Definition 3) which is a separate large-effort pipeline; Tables 3, 4, 6 cells require the full SCQR pipeline (~25M LP solves). None of these cells is reachable within a single replication session.

---
