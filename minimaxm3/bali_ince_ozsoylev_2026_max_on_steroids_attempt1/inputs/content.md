# Page 1

# MAX on Steroids: A New Measure of Investor Attraction to Lottery Stocks*

Turan G. Bali $^{\dagger}$ Baris Ince $^{\ddagger\S}$ Han N. Ozsoylev $^{\P}$

## Abstract

We introduce MAX $^{\beta}$ , a refined lottery-stock measure that purges the systematic component of MAX to isolate lottery-seeking behavior. The value-weighted MAX $^{\beta}$ long-short portfolio earns significant abnormal returns, robust to risk and mispricing factors and independent of lottery-characteristic persistence. Its source differs by clientele: retail investors overpay for high-MAX $^{\beta}$ stocks, while institutions require a premium to hold the low-MAX $^{\beta}$ stocks retail avoids. This premium is concentrated where institutions are accumulating and continues to accrue over long holding periods, equilibrium compensation for bearing low skewness, not a transient correction. MAX $^{\beta}$ is thus a distinct anomaly rooted in heterogeneous skewness preferences.

**Keywords:** MAX anomaly, mispricing, lottery-like stocks, retail investors, institutional investors, skewness.

**JEL classification:** G11, G12, G41.

---

*We thank Yiğit Atılgan, Doruk Günaydın, Alexander Hillert, Oğuzhan Özbaş, Altan Pazarbaşı, Christian Schlag, Yi Tang, Rüdiger Weber, Kamil Yılmaz, Jianfeng Yu, and Yu Yuan for their helpful comments and sharing data/code. We also thank seminar participants at the Autonomous University of Barcelona, Bilkent University, Goethe University Frankfurt, Koç University, NEOMA Business School, Özyeğin University, and Sabancı University.

$^{\dagger}$ McDonough School of Business, Georgetown University. e-mail: Turan.Bali@georgetown.edu

$^{\ddagger}$ Goethe University Frankfurt. e-mail: ince@finance.uni-frankfurt.de

$^{\S}$ Bilkent University

$^{\P}$ Özyeğin University. e-mail: han.ozsoylev@ozyegin.edu.tr

---

# Page 2

# 1 Introduction

The demand for lottery-like payoffs is a pervasive behavioral phenomenon: in a meta-analysis spanning 68 countries, Tran et al. (2024) estimate that about 2% of adults engage specifically in financial-market gambling, a share large relative to stock-market participation rates that implies lottery-seeking traders form a sizeable part of the active retail base. This demand is grounded in cumulative prospect theory (Kahneman and Tversky, 1979; Tversky and Kahneman, 1992), under which investors overweight the tails and overvalue stocks offering a small chance of a large payoff, and is reinforced by the salience mechanism of Bordalo, Gennaioli, and Shleifer (2012, 2013); zero-commission, gamified trading has amplified but not altered it (Bali, Hirshleifer, Peng, Tang, and Wang, 2025). Lottery demand is thus a primary driver of structural mispricing, which motivates our focus on how it is priced in the cross-section.

Given that this gambling instinct drives structural mispricing, the effort to quantify such speculative demand fits squarely within the central theme of the asset pricing literature: the search for common risk or mispricing factors that predict the cross-section of stock returns. While early models focused on systematic risk, a vast body of literature has since uncovered numerous empirical regularities, or “anomalies,” that challenge the assumptions of perfectly rational investors and efficient markets. Among the most intriguing of these is the MAX anomaly, first documented by Bali, Cakici, and Whitelaw (2011) and preserving its strength since then. $^{1}$

Bali et al. (2011) find a robust and negative cross-sectional relationship between a stock’s maximum daily return in a given month (MAX) and its subsequent performance. This finding, which has been shown to hold not only in the U.S. but across a wide array of international equity markets (e.g., Walkshausl (2014) and Cheon and Lee (2018)), presents a puzzle: why do stocks exhibiting the most extreme positive daily returns tend to be

${ }^{1}$ McLean and Pontiff (2016) examine the post-publication return predictability of 97 firm characteristics and find that the predictive power of established stock market anomalies declines by an average of 58% after publication. Bali et al. (2025) show that the post-publication performance of the MAX effect remained economically large and statistically significant for the post-publication period of Bali, Cakici, and Whitelaw (2011), March 2011-December 2022.

---

# Page 3

such poor subsequent investments?

The prevailing explanation, proposed by Bali et al. (2011) and widely adopted since, interprets this anomaly as the direct asset-pricing consequence of the behavioral biases outlined above. Consistent with the theoretical framework of Barberis and Huang (2008), who model the asset pricing implications of skewness-loving preferences, high-MAX stocks serve as the quintessential target for the gambling-prone retail investors identified by Kumar (2009). This concentrated demand, amplified by the zero-commission, gamified trading noted earlier, leads to the overpricing of these lottery-like assets, which is inevitably followed by a period of negative returns as prices correct towards fundamental values. Because it effectively captures this behavioral mispricing, the MAX measure has proven to be one of the strongest predictors in machine learning models for forecasting stock returns (Gu, Kelly, and Xiu, 2020), cementing its status as the standard proxy in the literature for identifying stocks with these lottery-like features.

This paper re-examines the economic underpinnings of the MAX anomaly and challenges this conventional wisdom on both empirical and conceptual grounds. Our critique begins with a conceptual issue inherent in the MAX measure itself: since it is based on the highest daily returns in a month, it may contain a substantial systematic component, reflecting market-wide movements rather than purely idiosyncratic (firm-specific) spikes. For instance, during periods of high market returns, stocks with high market beta may exhibit high-MAX values simply due to their systematic risk exposure, driven by macroeconomic and geopolitical events that impact the market as a whole. This is problematic because the appeal of a lottery-like asset is undoubtedly its idiosyncrasy. If a stock’s extreme return is driven by common factors, it fails to capture the unique, firm-specific payoff that defines a lottery. Furthermore, this link to systematic effects becomes particularly problematic when we consider that market-wide movements are often driven by investor sentiment, which tends to be persistent. This creates a second conceptual inconsistency for the lottery-stock hypothesis. The theory rests on investors’ attraction to rare, unpredictable events, but if a stock’s high-MAX is simply a reflection of a persistent, sentiment-driven market trend, it is no longer an idiosyncratic lottery-like

2

---

# Page 4

event but rather a predictable outcome of market-wide optimism.$^{2}$ Our empirical findings lend strong support to this critique: the future negative returns associated with high-MAX are most pronounced among low-beta stocks, particularly during periods of low investor sentiment. This suggests that for high-beta stocks, the MAX effect is indeed confounded by systematic risk, weakening its power as a clean proxy for lottery-like preferences.

Our central thesis is that the original MAX measure is an imperfect and noisy proxy for lottery-like preferences, partly due to this contamination by systematic effects. We argue that its predictive power is largely a manifestation of previously documented mispricing phenomena, particularly those related to corporate financing decisions. Our investigation begins by subjecting the MAX anomaly to the scrutiny of recently developed factor models, namely those of Stambaugh and Yuan (2017) and Daniel, Hirshleifer, and Sun (2020). We find that the anomaly’s explanatory power for value-weighted portfolios is not robust, as the effect vanishes once we account for the mispricing/behavioral factors proposed in these studies.

Digging deeper, we find that the MAX anomaly is almost entirely explained by the management-related mispricing factors. In particular, equity issuance, a corporate action commonly linked to persistent mispricing (Baker and Wurgler, 2020; Daniel, Hirshleifer, and Sun, 2020), largely explains the MAX anomaly. This points towards an alternative economic mechanism: managers of overvalued firms, recognizing their stock’s elevated price, opportunistically issue new equity to raise capital on favorable terms. This is consistent with a long line of research showing that equity issuance is a strong negative predictor of future stock returns (Loughran and Ritter, 1995; Daniel and Titman, 2006). From this perspective, a high-MAX is not the cause of overpricing but rather a symptom, an indicator of the kind of speculative fervor that allows managers to time the market. Furthermore, these dynamics are amplified by market-wide optimism; we find that the link between high-MAX, mispricing, and equity issuance intensifies significantly during

$^{2}$While the behavioral bias toward lottery-like assets is expected to be persistent, the object of that preference must remain probabilistic. It is crucial to distinguish between the persistence of the *preference* and the persistence of the *payoff itself*; if a stock generates extreme returns persistently, the payoff becomes a predictable characteristic rather than a speculative anomaly, thereby violating the definition of a “lottery,” which inherently requires outcomes to be stochastic and rare.

3

---

# Page 5

periods of high investor sentiment, consistent with Baker and Wurgler (2006).

Crucially, this link to equity issuance introduces a temporal dimension that directly contradicts the lottery-stock hypothesis. Corporate financing decisions are not made impulsively; i.e., they involve significant planning, due diligence, and regulatory processes. For managers to identify mispricing and act upon it by issuing shares, the overvaluation must be reasonably persistent. A fleeting, one-day price spike is unlikely to trigger a seasoned equity offering. This insight leads to a sharp conceptual inconsistency: the allure of a lottery is its rare, unpredictable, and non-persistent nature. A stock that consistently produces extreme returns is not a lottery ticket; it is a predictably volatile asset. We test this implication directly and find compelling evidence that the MAX anomaly is concentrated almost entirely within stocks that exhibit persistence in extreme daily returns in the months preceding portfolio formation. This finding strongly supports the mispricing-driven issuance channel, but fundamentally undermines the skewness-preference explanation for the original MAX measure.

To resolve these inconsistencies and isolate a more refined proxy for lottery-like preferences, we propose a MAX-on-steroids measure, denoted by MAX $^\beta$ . The preference for lottery-like assets is conceptually a preference for high positive idiosyncratic skewness. By construction, an extreme positive idiosyncratic return is a primary driver of such skewness. Our methodology is therefore designed to purge the influence of market-wide movements from the MAX measure, isolating the idiosyncratic component of extreme returns. This makes MAX $^\beta$ a more direct and powerful proxy for the idiosyncratic skewness that lottery-seeking investors are theorized to value. The construction involves a two-stage portfolio sorting procedure: we first sort stocks into decile portfolios based on their market beta, and then within each beta-sorted portfolio, stocks are sorted again into decile portfolios based on their MAX. The resulting MAX $^\beta$ portfolios group stocks with similar idiosyncratic MAX characteristics, while maintaining neutrality to market beta.

The results of this alternative sorting procedure are striking. The long-short portfolios sorted on MAX $^\beta$ exhibit a large, statistically significant, and economically sizeable return spread. Crucially, this new anomaly cannot be explained by any of the standard asset

4

---

# Page 6

pricing models, including the Fama-French three-, five-, and six-factor models, and most importantly, the mispricing and behavioral factor models of Stambaugh and Yuan (2017) and Daniel, Hirshleifer, and Sun (2020). The alpha of the value-weighted long-short MAX $^{\beta}$ -sorted portfolio remains significant across all specifications. Furthermore, and in stark contrast to the original MAX measure, the predictive power of MAX $^{\beta}$ does not depend on the past persistence of extreme daily returns. The underperformance of high-MAX $^{\beta}$ stocks holds regardless of their prior return behavior. This consistency makes MAX $^{\beta}$ a far more compelling and conceptually sound proxy for capturing an underlying investor preference for lottery-like features.

Our key identification test links the MAX $^{\beta}$ effect directly to the behavior of retail investors. We find that the anomaly is significantly stronger and almost entirely concentrated among stocks with low institutional ownership, precisely the stocks where the trading of individual investors is most likely to impact prices. Consistent with this retail-investor-driven story, we also find that the MAX $^{\beta}$ effect is significantly stronger during periods of high investor sentiment, when speculative trading is more prevalent. While sentiment amplifies the mispricing and equity issuance channel for the original MAX anomaly, it amplifies the underlying speculative demand for lottery-like payoffs for the MAX $^{\beta}$ anomaly. Consistent with a preference-based rather than a mispricing-based premium, the MAX $^{\beta}$ spread is, moreover, approximately invariant to the aggregate equity issuance regime, whereas the original MAX spread concentrates in high-issuance states. The pattern of MAX $^{\beta}$ -sorted portfolio returns across institutional ownership tiers is also revealing, pointing to heterogeneous preferences for the idiosyncratic skewness that MAX $^{\beta}$ captures. Among stocks with low institutional ownership, the anomaly is driven by the underperformance of high-MAX $^{\beta}$ stocks, consistent with retail investors’ overpayment for lottery-like idiosyncratic skewness. However, among stocks with high institutional ownership, the return spread is driven by the outperformance of low-MAX $^{\beta}$ stocks.

The shifting source of the anomaly’s returns across investor clienteles is remarkably consistent with models of heterogeneous skewness preference, such as the one proposed by Mitton and Vorkink (2007). Their framework features two types of agents: “lotto investors”

5

---

# Page 7

(analogous to retail investors) and “traditional investors” (analogous to institutions). The key distinction is in their preference for (aversion to) positive (negative) skewness. “Lotto investors” have a strong desire for high positive skewness and are willing to overpay for it, which explains the subsequent underperformance of the high-MAX $^{\beta}$ stocks they concentrate in. In contrast, “traditional investors” exhibit no preference for skewness. Averse to holding underdiversified portfolios, which are not mean-variance efficient, institutional investors demand a premium in the form of higher expected returns as compensation to hold stocks with low idiosyncratic skewness. This dynamic explains why low-MAX $^{\beta}$ stocks, which are less appealing to lottery-seekers, deliver positive abnormal returns, particularly within the institution-dominated segment of the market.

These clientele patterns are consistent with a preference-based mechanism, but they are cross-sectional correlations, and a skeptical reader might still regard the low-MAX $^{\beta}$ premium as a slow-moving mispricing dressed in the language of preference. Two further results turn the correlation into an identified mechanism, and together they form a central contribution of this paper. First, and most decisively, the low-MAX $^{\beta}$ premium endures across holding horizons: it is earned in every month for as long as the position is held, declining only modestly over two years, whereas the original MAX effect corrects within a month or two. An abnormal return earned repeatedly for as long as the exposure is borne is the signature of an equilibrium compensation, not of a one-time correction, and it is the sharpest evidence that MAX $^{\beta}$ captures a priced preference rather than a transient mistake. Second, the premium is concentrated not merely among the low-MAX $^{\beta}$ stocks institutions hold but among those they are actively accumulating, while the high-MAX $^{\beta}$ underperformance concentrates among the stocks institutions are shedding to retail; this two-sided flow, institutions rewarded on the long leg and retail penalized on the short leg, is the most vivid expression of the arbitrage symmetry that sets MAX $^{\beta}$ apart from the one-sided MAX effect. That retail investors drive the original MAX anomaly is itself established (Han and Kumar, 2013; Bali et al., 2017); what is new here is the measure that separates preference from mispricing and the identification of the equilibrium that produces the long-leg premium.

6

---

# Page 8

To formally disentangle the joint contributions of mispricing, issuance, skewness, and investor heterogeneity, we employ Fama-MacBeth cross-sectional regressions that link the anomalies to specific firm characteristics. This analysis confirms that factors related to mispricing, particularly equity issuance, are the principal explanation for the original MAX anomaly. In contrast, while these factors also contribute to the MAX $^{\beta}$ anomaly, its behavior is more significantly shaped by skewness preference and investor heterogeneity. This evidence reinforces our central argument: the original MAX anomaly is primarily driven by mispricing, while the MAX $^{\beta}$ anomaly captures a distinct economic phenomenon rooted in the skewness preferences of different investor clienteles.

Finally, we subject the MAX $^{\beta}$ strategy to a battery of robustness tests and extensions. We show that the profitability of the strategy is not an artifact of micro-cap stocks or illiquidity; it generates significant abnormal returns across size, price, and liquidity subsamples, including the largest and most liquid segment of the market. The strategy also delivers superior risk-adjusted returns, as evidenced by high Sharpe ratios, and is not merely compensation for left-tail risk. We further demonstrate the generalizability of our beta-neutralization methodology using alternative proxies for lottery demand. To complement our portfolio-level evidence, we introduce a stock-level measure, MAX $^{\text{Treynor}}$ , and confirm via firm-level cross-sectional regressions that the anomaly remains robust to controls for mispricing and equity issuance.

The remainder of this paper proceeds as follows. Section 2 provides a literature review and summarizes our key contributions. Section 3 details the data and key variables used in our empirical analysis. Section 4 presents a comprehensive re-examination of the original MAX anomaly, demonstrating its weaknesses and dependence on persistent mispricing. In Section 5, we introduce and validate our newly proposed alternative, MAX $^{\beta}$ , establishing it as a new, robust anomaly that is distinct from known equity market factors. Section 6 delves into the economic drivers of the MAX $^{\beta}$ effect, providing evidence that links the anomaly to heterogeneous skewness preferences and the trading behaviors of retail and institutional investors. Section 7 presents robustness analyses, extensions using alternative lottery proxies, and firm-level evidence for the stock-level measure, MAX $^{\text{Treynor}}$ (with

7

---

# Page 9

detailed results reported in the Internet Appendix). Section 8 concludes.

## 2 Literature Review

The idea that the skewness of returns is an important consideration to investors when determining optimal investments is originally proposed by Arditti (1967), who provides theoretical and empirical evidence that investors demand a higher (lower) rate of return on investments whose return distributions are negatively (positively) skewed. Kraus and Litzenberger (1976) incorporate this notion into a three-moment asset pricing model in which expected returns on risky securities are determined not only by the amount of systematic (undiversifiable) variance associated with the security, but also by the security’s systematic skewness. According to the three-moment asset pricing model of Kraus and Litzenberger (1976), both idiosyncratic variance and idiosyncratic skewness are diversifiable and thus they do not play a role in determining expected returns. Harvey and Siddique (2000) introduce systematic skewness (co-skewness) into the pricing of securities via a stochastic discount factor that is quadratic in the market return, and show that this results in the cross-sectional pricing of conditional co-skewness.

Prior research has challenged the notion that idiosyncratic skewness is diversified away and hence cannot be priced. Simkowitz and Beedles (1978) and Conine and Tamarkin (1981) point out that when investors do not completely diversify, idiosyncratic skewness may be relevant to the pricing of securities. Mitton and Vorkink (2007) introduce a model in which heterogeneous skewness preference causes investors to underdiversify and demonstrate that idiosyncratic skewness has an impact on equilibrium prices. Boyer, Mitton, and Vorkink (2010) demonstrate that expected idiosyncratic skewness, estimated based on firm-specific characteristics, has a strong negative cross-sectional relationship with future stock returns.

To provide an explanation for investor attraction to lottery-like securities, Barberis and Huang (2008) propose a theoretical model in which investors have utility functions based on the cumulative prospect theory (CPT) of Tversky and Kahneman (1992), and

8

---

# Page 10

show that a security with positive idiosyncratic skewness can be overpriced and can earn a negative average excess return.$^{3}$ Brunnermeier and Parker (2005) and Brunnermeier, Gollier and Parker (2007) introduce a model in which investors optimally choose to distort their beliefs about future probabilities to maximize their current utility. In the optimal beliefs framework of Brunnermeier et al. (2005, 2007), optimistic investors overestimate their return and exhibit a preference for positive skewness.

Motivated by the theoretical findings of Barberis and Huang (2008) and Brunnermeier et al. (2005, 2007), Bali, Cakici, and Whitelaw (2011) introduce an empirical proxy for investor attraction to lottery-like securities and examine the effect of lottery demand on stock pricing.$^{4}$ Bali et al. (2011) argue that the maximum daily return in a given month (MAX) measures the attractiveness of the stock to lottery investors, or investors who want to own stocks that have a high probability of a large short-term price increase. Bali et al. (2011) investigate the significance of MAX in the cross-sectional pricing of individual stocks trading in the U.S equity market and find a strong negative relation with future stock returns. Several subsequent papers find that lottery-like stocks underperform in international equity markets as well; e.g., Annaert, De Ceuster, and Verstegen (2013), Walkshausl (2014), Barberis, Mukherjee, and Wang (2016), and Cheon and Lee (2018). The lottery demand effect is also identified in other asset classes, such as IPOs, equity options, and mutual funds; e.g., Green and Hwang (2012), Boyer and Vorkink (2014), and Agarwal, Jiang, and Wen (2022).$^{5}$

A widely accepted economic channel driving investor attraction to lottery stocks is that investors are perfectly aware of these lottery characteristics but nevertheless have inherent nontraditional preferences that induce demand for large positive skewness, as

---

$^{3}$Given their preference for upside potential and dislike of large losses, CPT investors would be willing to accept lower (demand higher) expected returns for assets with higher (lower) idiosyncratic skewness.

$^{4}$Kumar (2009) and Han and Kumar (2013) show that retail investors with high gambling propensity invest disproportionately in lottery stocks.

$^{5}$Green and Hwang (2012) show that initial public offerings (IPOs) with high expected skewness earn more negative abnormal returns in the following one to five years. Boyer and Vorkink (2014) investigate the cross-sectional relationship between ex-ante total skewness and holding period returns on individual equity options and find that options with lottery-like characteristics exhibit a strong and negative relationship with future option returns. Agarwal, Jiang, and Wen (2022) provide evidence for mutual funds’ motivation to hold lottery-like stocks. Although managers themselves do not prefer lottery stocks, they cater to fund investors’ preference for such stocks.

9

---

# Page 11

modeled by Barberis and Huang (2008) and Brunnermeier et al. (2005, 2007). Han, Hirshleifer, and Walden (2022) introduce an alternative economic mechanism in which investor attraction to lottery stocks can be stimulated by social interaction even if investors have no inherent preference for skewness. Bali, Hirshleifer, Peng, Tang, and Wang (2025) provide supporting empirical evidence for the theoretical model of Han et al. (2022) and show that social interactions are a key contributor to the overvaluation of lottery-like stocks.

This paper makes three contributions. First, we re-examine the economic content of the MAX anomaly and show that the skewness-preference interpretation of Bali et al. (2011) is incomplete: the anomaly is largely driven by management-related mispricing, particularly equity issuance, and is concentrated among stocks with persistent extreme returns, a pattern consistent with managerial market timing but inconsistent with a preference for rare, unpredictable payoffs. Second, we introduce MAX $^{\beta}$ , which purges the systematic component of MAX and more cleanly isolates firm-specific lottery-like skewness; the long-short MAX $^{\beta}$ portfolio earns abnormal returns that are robust to established risk and mispricing factors and, unlike the original MAX effect, do not depend on the persistence of past extreme returns. Third, we trace the anomaly to heterogeneous skewness preferences across investor clienteles (Mitton and Vorkink, 2007): among low-institutional-ownership stocks it is driven by the underperformance of high-MAX $^{\beta}$ stocks, whereas among high-institutional-ownership stocks it is driven by the outperformance of low-MAX $^{\beta}$ stocks.

# Data and Key Variables

## Sample Construction

Our stock sample includes all common stocks (CRSP share codes 10 and 11) traded on the New York Stock Exchange (NYSE), American Stock Exchange (Amex), and Nasdaq exchanges from January 1968 to December 2022. The daily and monthly return and volume data are from the Center for Research in Security Prices (CRSP). To be included

---

# Page 12

in our sample for a given month, we require that at least 15 daily stock return observations are available to calculate the key variables. We exclude stocks priced below $5 per share to ensure that our results are not driven by micro-cap or illiquid firms. We also exclude firms in the heavily regulated utility (SIC codes 4900–4949) and financial (SIC codes 6000–6999) sectors.

## 3.2 Main Variable of Interest

This paper first re-examines the cross-sectional predictive power of the maximum daily stock returns (MAX). Following Bali, Cakici, and Whitelaw (2011) and Bali, Brown, Murray, and Tang (2017), we define MAX as the average of the five highest daily returns generated by a stock in a given month.

We then propose a new portfolio-level measure, $ \text{MAX}^\beta $, designed to isolate the idiosyncratic component of MAX through a non-parametric approach. We construct $ \text{MAX}^\beta $ by first sorting stocks into decile portfolios based on their market beta,$ ^6 $ and then within each beta-sorted portfolio, we sort stocks into decile portfolios based on their MAX. We then group together all stocks with the same MAX portfolio ranking, $ n $, across the different beta portfolio ranks, and call the newly formed decile portfolio the $ \text{MAX}^\beta $ portfolio of rank $ n $. This procedure controls for the effect of market-wide movements on stock-level daily returns so that the resulting $ \text{MAX}^\beta $ portfolio is constrained to be neutral to the market beta. Thus, the $ \text{MAX}^\beta $ portfolio is designed to capture returns associated with investors’ demand for lottery-like characteristics of individual stocks, while maintaining neutrality to market beta.

## 3.3 Control Variables and Other Measures

Throughout our portfolio-level analyses and firm-level Fama-MacBeth (1973) regressions, we control for a battery of firm-level characteristics. We estimate the market beta of individual stocks using daily returns over a 252-day rolling window (see footnote 6).

$ ^6$A stock’s market beta at the end of each month is estimated as the slope coefficient from a regression of its daily excess returns on the market’s excess returns over a 252-day rolling window.

11

---

# Page 13

Market capitalization (SIZE) is a stock’s number of shares outstanding multiplied by its price per share. The book value of a firm is calculated as the sum of stockholders’ equity (SEQ), deferred taxes (TXDB), and investment tax credit (ITCB), minus the book value of preferred stock (PSTKRV, PSTKL, or PSTK). BM is the natural logarithm of the ratio of a firm’s book value to its market capitalization. Following Jegadeesh and Titman (1993), intermediate-term momentum (MOM) is measured as a stock’s cumulative return over the 11-month period prior to the portfolio formation month. Short-term reversal (REV) is the excess return generated over the portfolio formation month (Jegadeesh, 1990).

Following Amihud (2002), a stock’s monthly illiquidity (ILLIQ, scaled by $10^6$) is the ratio of the daily absolute stock return to the dollar trading volume averaged over the past one month. Following Hou, Xue, and Zhang (2015), we control for the annual growth of total assets (I/A) and return on equity (ROE). Asset growth is the change in the book value of assets scaled by lagged assets. Return-on-equity is income before extraordinary items (IBQ) divided by one-quarter-lagged book equity. Idiosyncratic volatility (IVOL) is computed as the standard deviation of the daily residuals from regressing a stock’s daily excess returns on the market’s excess returns over a 252-day rolling window, using the same specification employed to estimate market beta.

Institutional holdings (INST) data are from the Thomson Reuters Institutional Holdings (13F) database. INST measures the percentage of a firm’s shares held by institutional investors at each quarter-end. Idiosyncratic skewness for each stock and for each month is calculated as the skewness of the time-series regression residuals estimated over a 60-month rolling window based on the Fama and French (1993) three-factor model. Following Boyer, Mitton, and Vorkink (2010), expected idiosyncratic skewness, E(ISKEW), is estimated using predictive cross-sectional regressions of realized idiosyncratic skewness on lagged idiosyncratic skewness, lagged idiosyncratic volatility, past cumulative returns (momentum), turnover (sum of daily turnovers), dummy variable indicating firms listed on Nasdaq, firm size indicators (dummy variables indicating firms in the bottom tercile and middle tercile ranked by size), and industry fixed effects (dummy variables for 16 of the

12

---

# Page 14

17 industries defined by Ken French). The resulting coefficients are then combined with contemporaneous firm characteristics to produce forward-looking estimates of expected idiosyncratic skewness.

## 3.4 Factor Models and Mispricing Measures

### 3.4.1 Factor Models for Performance Evaluation

We test the significance of the return spreads on MAX- and MAX $^{\beta}$ -sorted portfolios using a comprehensive set of factor models: (i) CAPM with the excess market return (MKT); (ii) Fama-French (1993) three-factor (FF3) model with the MKT, size (SMB), and book-to-market (HML) factors; (iii) Fama-French-Carhart four-factor (FFC4) model with the MKT, size (SMB), book-to-market (HML), and Carhart’s (1997) momentum factor; (iv) FFCPS model that combines the FFC4 model with the liquidity factor of Pastor and Stambaugh (2003); (v) Fama-French (2015) five-factor (FF5) model with the MKT, size (SMB), book-to-market (HML), profitability (RMW), and investment (CMA) factors; (vi) Fama-French (2018) six-factor (FF6) model that combines the FF5 model with the momentum factor; and (vii) the 7-factor model (FF6PS) that combines the FF6 model with the liquidity factor of Pastor and Stambaugh (2003).

In addition to these standard risk factor models, we use two established behavioral models: (viii) the Stambaugh and Yuan (SY, 2017) four-factor mispricing model, which consists of the value-weighted excess market return (MKT), a size factor (SMB), and management (MGMT)- and performance (PERF)-related mispricing factors; and (ix) the Daniel, Hirshleifer, and Sun (DHS, 2020) three-factor behavioral model, which includes the value-weighted excess market return (MKT), long-horizon (FIN), and short-horizon (PEAD) behavioral factors.

The Fama and French (1993, 2015, 2018) factors and Carhart’s (1997) momentum factor are from Kenneth French’s data library. The Pastor and Stambaugh (2003) liquidity risk (LIQ) factor and the Stambaugh and Yuan (2017) mispricing factors (MGMT and PERF) are obtained from Robert Stambaugh’s website. The Daniel, Hirshleifer, and Sun (2020) behavioral factors (FIN and PEAD) are obtained from Lin Sun’s website.

13

---

# Page 15

The FIN and PEAD factors are available from July 1972 to December 2022, whereas the analyses involving the remaining factors cover the full sample period from January 1968 to December 2022.

### 3.4.2 Mispricing Scores and Constituent Anomalies

This paper examines the role of mispricing in explaining the cross-sectional predictive power of MAX and MAX $^{\beta}$ . We utilize the mispricing scores developed by Stambaugh, Yu, and Yuan (2012, 2014, 2015) and the mispricing factors of Stambaugh and Yuan (2017), both derived from 11 anomalous firm-level characteristics. These are grouped into two categories.

The management-related characteristics are: (i) net stock issuance, defined as annual logarithmic changes in split-adjusted shares outstanding (Ritter, 2008; Loughran and Ritter, 1995; Fama and French, 2008); (ii) composite equity issues, calculated as the one-year growth in market capitalization minus the one-year equity return (Daniel and Titman, 2006); (iii) accruals, computed as the annual change in non-cash working capital minus depreciation and amortization, divided by average total assets (Sloan, 1996); (iv) net operating assets, defined as operating assets minus operating liabilities, divided by lagged total assets (Hirshleifer et al., 2004); (v) asset growth, quantified with the one-year growth rate in total assets (Cooper, Gulen, and Schill, 2008); and (vi) investment-to-assets, measured as the change in gross property, plant, and equipment plus inventory changes, scaled by lagged total assets (Titman, Wei, and Xie, 2004; Xing, 2008).

The performance-related characteristics are: (vii) failure probability, estimated following Campbell, Hilscher, and Szilagyi (2008) using a logit model incorporating several equity market variables such as stock price, book-to-market ratio, stock volatility, size relative to the S&P 500 index, and the cumulative excess return; (viii) O-score, calculated following Ohlson (1980) using accounting variables to estimate bankruptcy probability; (ix) momentum, defined as a stock’s cumulative return from month $t - 12$ to $t - 2$ (Jegadeesh and Titman, 1993; Carhart, 1997); (x) gross profitability, calculated as total revenue minus the cost of goods sold, divided by total assets (Novy-Marx, 2013); and (xi) return-on-assets,

14

---

# Page 16

defined as income before extraordinary items scaled by the prior quarter’s total assets (Chen, Novy-Marx, and Zhang, 2010).

To construct a stock-level monthly composite mispricing index, we follow Stambaugh, Yu, and Yuan (2012, 2014, 2015). Specifically, stocks are ranked independently based on the aforementioned 11 return predictors in such an order that a higher rank is associated with lower one-month-ahead stock returns, as documented in earlier studies cited above. A stock’s composite mispricing measure (MIS) is defined as the arithmetic average of the ranks of the 11 anomalies.

The SY mispricing factors (MGMT and PERF) are calculated using a $2 \times 3$ double sorting method similar to Fama and French (2015), based on the value-weighted return differences between underpriced and overpriced stocks controlling for size. The DHS behavioral factors are constructed as follows: The long-horizon FIN factor is based on the 1-year net share issuance (NSI) of Pontiff and Woodgate (2008) and the 5-year composite share issuance (CSI) of Daniel and Titman (2006), where NSI uses a 1-year horizon and excludes cash dividends. The short-horizon PEAD factor is constructed following Chan, Jegadeesh, and Lakonishok (1996), where earnings surprise is measured as the 4-day cumulative abnormal return around the most recent quarterly earnings announcement date.

While examining the role of mispricing, we emphasize the role of equity issuance in the cross-sectional pricing of MAX and MAX $^{\beta}$ . We construct a stock-level issuance index using a methodology analogous to that employed for the composite mispricing index (MIS). Specifically, stocks are independently assigned percentile ranks based on (i) changes in split-adjusted shares outstanding (Ritter, 2008; Loughran and Ritter, 1995; Fama and French, 2008); (ii) composite equity issues, measured as the one-year growth in market capitalization minus the one-year equity return (Daniel and Titman, 2006); and (iii) the five-year composite share issuance (CSI) of Daniel and Titman (2006). A stock’s issuance index is then defined as the arithmetic average of its percentile ranks across these equity issuance-related variables.

15

---

# Page 17

## 3.5 Alternative Measures of Lottery-Like Payoffs

While our primary analysis focuses on the cross-sectional pricing of MAX and MAX $^\beta$ , we also examine several alternative proxies for lottery-like payoffs to ensure the robustness of our findings. These measures include the lottery index (LTRY) of Kumar (2009), the single highest daily return in a month (MAX(1)), the 95th and 99th percentiles of the daily return distribution (MAX(95%) and MAX(99%)), and a beta-scaled stock-level measure, MAX $^{\text{Treynor}}$ .

Following Kumar (2009), we construct the composite lottery index, LTRY, based on three stock characteristics: stock price (PRC), idiosyncratic volatility (IVOL), and idiosyncratic skewness (ISKEW). To construct the index, we sort stocks independently into 50 bins based on PRC in descending order, and into 50 bins based on IVOL and ISKEW in ascending order. We rely on the estimation of IVOL and ISKEW, utilizing the Fama and French (1993) three-factor model. For each stock, we sum the rankings of these three characteristics to obtain a composite score, SumRank, which ranges from 3 to 150. LTRY is defined as the decile rank of SumRank, where a higher value indicates a greater degree of lottery-like features.

We also consider alternative definitions of extreme positive returns. MAX(1) is defined as the maximum daily return generated by a stock within a given month. MAX(95%) and MAX(99%) capture the extreme upper end of the daily return distribution, corresponding to the 95th and 99th percentiles, respectively, of a stock estimated over the past 252 trading days. To facilitate a direct comparison with our main results, we also construct beta-neutralized versions of these variables, LTRY $^\beta$ , MAX(1) $^\beta$ , MAX(95%) $^\beta$ , and MAX(99%) $^\beta$ , following the same double-sorting methodology utilized for MAX $^\beta$ in Section 3.2.

Finally, we propose a stock-level measure of lottery payoffs, MAX $^{\text{Treynor}}$ , which serves as a firm-specific alternative to the portfolio-level MAX $^\beta$ and its beta-neutralized counterparts. MAX $^{\text{Treynor}}$ scales the magnitude of extreme returns by systematic risk and is calculated as the average of the five highest daily returns in a month (MAX) divided by the stock’s market beta.

---

# Page 18

# 4 Deconstructing the MAX Anomaly

This section presents the core empirical findings from our re-examination of the MAX anomaly. We begin by revisiting the original MAX anomaly, confirming its significance in our sample and testing its robustness against a comprehensive set of modern asset pricing models, including those designed to capture mispricing. We then dissect the characteristics of MAX-sorted portfolios to identify the economic drivers behind the anomaly, paying close attention to the confounding effects of market beta. Our subsequent analysis formally investigates the roles of persistent mispricing and equity issuance, demonstrating that these factors, rather than investors’ preference for lottery-like payoffs, are the primary sources of the MAX effect.

## 4.1 The MAX Anomaly and Modern Factor Models

We begin our empirical analysis by revisiting the cross-sectional predictive power of the MAX anomaly. Following the established literature, we sort stocks in ascending order based on their MAX values, defined as the average of the five highest daily returns in a given month, and form 10 decile portfolios. Table 1 presents the one-month-ahead value-weighted average excess returns and alphas for these portfolios.

– Table 1 around here –

Consistent with the findings of Bali et al. (2011), we document a significantly negative cross-sectional relationship between MAX and next-month returns. Portfolio 1, the low-MAX portfolio, yields an average one-month-ahead value-weighted excess return of 63 basis points. In contrast, Portfolio 10, the value-weighted high-MAX portfolio, loses 32 basis points per month. This results in a value-weighted average return spread of $-0.95\%$ per month, which is statistically significant with a Newey-West (1987) $t$ -statistic of $-3.08$ . $^{7}$

$^{7}$ Newey and West (1987) adjusted standard errors are computed using the optimal lag length selection procedure of Newey and West (1994). The optimal number of lags is defined as $4(T/100)^{\gamma}$ , where $T$ is the number of observations in the time series. The parameter $\gamma$ equals $2/9$ when using the Bartlett kernel and $4/25$ when using the quadratic spectral kernel to calculate heteroscedasticity- and autocorrelation-consistent standard errors. Following this procedure, we employ six lags for the sample periods spanning January 1968 to December 2022 and July 1972 to December 2022, and five lags for the period from April 1980 to December 2022. The specific lag length applied is reported in the caption of each table.

17

---

# Page 19

This baseline result confirms that stocks with extremely high daily returns in a month tend to generate lower next-month returns than stocks with low daily returns.

The subsequent columns of Table 1 assess whether this return differential can be explained by exposures to known risk factors. We report the alphas (abnormal returns) relative to several widely used factor models. The value-weighted risk-adjusted return spreads between the extreme portfolios are as follows: $\alpha_{CAPM}$ is $-1.41\%$ per month (t-stat. = $-5.17$ ), $\alpha_{FF3}$ is $-1.16\%$ per month (t-stat. = $-5.35$ ), $\alpha_{FFC4}$ is $-1.07\%$ per month (t-stat. = $-4.63$ ), $\alpha_{FFCPS}$ is $-1.11\%$ per month (t-stat. = $-4.81$ ), $\alpha_{FF5}$ is $-0.59\%$ per month (t-stat. = $-3.25$ ), $\alpha_{FF6}$ is $-0.57\%$ per month (t-stat. = $-2.80$ ), and $\alpha_{FF6PS}$ is $-0.61\%$ per month (t-stat. = $-3.00$ ). The results show that the risk-adjusted return spreads remain negative and highly statistically significant across all established risk factor models, indicating that these models fail to account for the MAX anomaly. Furthermore, the negative alpha spread is primarily driven by the significant underperformance of high-MAX stocks. Portfolio 10 produces economically large and statistically significant negative alphas (ranging from $-0.51\%$ to $-1.17\%$ per month with t-statistics between $-3.06$ and $-5.34$ ). In contrast, the alphas for Portfolio 1 are economically small and statistically insignificant under the more comprehensive FF5, FF6, and FF6PS models. This pattern aligns with the original interpretation of the anomaly, which attributes the effect to investors’ preference for lottery-like stocks, leading to their overpricing and subsequent poor performance.

The final two columns of Table 1 present the crucial test of our main hypothesis by reporting alphas relative to the Stambaugh and Yuan (2017) mispricing factor model (SY) and the Daniel, Hirshleifer, and Sun (2020) behavioral factor model (DHS). After accounting for these models, the MAX anomaly disappears. The $\alpha_{SY}$ and $\alpha_{DHS}$ differences between Portfolios 10 and 1 are, respectively, $-0.27\%$ and $-0.32\%$ per month with corresponding t-statistics of $-1.29$ and $-1.34$ , indicating statistical insignificance. Moreover, neither the long-leg nor the short-leg of the arbitrage portfolios generates significant alphas under these specifications. These results strongly suggest that once the value-weighted return spread is tested against recently proposed mispricing and behavioral factor models,

18

---

# Page 20

the MAX anomaly is largely explained, indicating a potential mispricing-based explanation for the original MAX effect.

## 4.2 Characteristics of MAX-Sorted Portfolios

To understand the economic underpinnings of the MAX anomaly, Table 2 presents the time-series averages of the cross-sectional medians for various firm characteristics across the 10 MAX-sorted decile portfolios. The characteristics of high-MAX stocks strongly align with a mispricing-based explanation, intertwined with systematic risk. By construction, MAX increases monotonically from 1% to 7.1% per day. More importantly, we find a strong positive correlation between MAX and several indicators of risk and overvaluation. Market beta (BETA) rises significantly from 0.581 to 1.043 across the deciles, and the market MAX beta (defined as the sensitivity of a stock’s MAX to the market-level MAX, estimated using 12-month rolling regressions) nearly doubles, indicating that the extreme returns of high-MAX stocks are highly sensitive to extreme market-wide movements. Critically, the mispricing score (MIS) increases monotonically from 44.07 to 55.11, and composite equity issuance (CE) moves from $-0.020$ to $0.013$. This pattern suggests high-MAX stocks are not only perceived as overvalued but are also associated with managerial actions, like equity issuance, that are typically linked to persistent mispricing (Daniel and Titman, 2006; Daniel, Hirshleifer, and Sun, 2020).

– Table 2 around here –

Several other characteristics are consistent with the traditional lottery-preference hypothesis. High-MAX stocks are significantly smaller and exhibit higher idiosyncratic volatility (IVOL). Furthermore, institutional ownership (INST) declines sharply in the top deciles, consistent with retail investors’ demand for lottery stocks (Han and Kumar, 2013; Bali et al., 2017). As expected, expected idiosyncratic skewness, $E(ISKEW)$, also increases monotonically with MAX. These patterns align with Kumar’s (2009) description of lottery-like assets.

Finally, high-MAX portfolios load on several other well-known return predictors. They exhibit significantly higher contemporaneous returns (REV), suggesting persistent

19

---

# Page 21

demand within the formation month. They also show lower past 12-month return (MOM) and higher illiquidity (ILLIQ). Consistent with a mispricing story, high-MAX stocks have significantly lower return-on-equity (ROE) and higher asset growth (I/A) — both characteristics associated with future underperformance (Stambaugh, Yu, and Yuan, 2015). In line with Bali et al. (2011), we find no significant pattern in the book-to-market ratio across the deciles.

## 4.3 The Conditional Role of Mispricing

The evidence from Table 1 and Table 2 strongly suggests that the MAX anomaly is linked to mispricing. To investigate this potential explanation more directly, we conduct bivariate portfolio sorts, first on mispricing and then on MAX. Table 3 presents the one-month-ahead value-weighted excess returns and seven-factor alphas for portfolios sorted first into five quintiles based on the composite mispricing (MIS) score, and then into 10 deciles based on MAX.$^{8}$

– Table 3 around here –

The results are stark: the MAX anomaly is exclusively a phenomenon of the most overvalued stocks. In the three lowest mispricing quintiles, the return and alpha spreads between the highest and lowest MAX deciles are statistically insignificant. For instance, the raw return spreads are 0.10% (t-stat. = 0.38), –0.30% (t-stat. = –1.08), and –0.45% (t-stat. = –1.56) in the first three quintiles, respectively. The corresponding alpha spreads are also insignificant, with only marginal significance appearing in the third and fourth quintiles.

In stark contrast, the effect materializes powerfully among the most overpriced firms. Within the highest MIS quintile, the strategy of shorting high-MAX stocks and buying low-MAX stocks yields a large and significant return spread of –1.65% per month (t-stat.

---

$^{8}$As shown in Table 1, we use a total of seven different risk factor models in calculating the risk-adjusted returns (alphas) on the long-short portfolios. Starting with Table 3, we continue presenting the alphas from the most comprehensive 7-factor model (FF6PS) of Fama and French (2018) and Pastor and Stambaugh (2003) with the market (MKT), size (SMB), book-to-market (HML), momentum (MOM), profitability (RMW), investment (CMA), and the liquidity risk (LIQ) factors.

20

---

# Page 22

= -4.42). The corresponding seven-factor FF6PS alpha is also highly significant at -1.17% per month (t-stat. = -4.20). This evidence demonstrates that the MAX anomaly is not a general market feature, but is instead confined to a subset of highly mispriced stocks, with the effect being driven primarily by the underperformance of high-MAX stocks in this overpriced segment.

## 4.4 Firm-Level Evidence

To complement our portfolio-level analysis, this section presents the firm-level cross-sectional regressions using the Fama-MacBeth (1973) methodology to evaluate the predictive power of MAX on future stock returns in a multivariate setting. It is worth noting that Fama-MacBeth regressions assign equal weight to each stock-month observation. Table 4 reports the time-series averages of the slope coefficients from the following stock-level predictive cross-sectional regressions of one-month-ahead excess returns on MAX and a set of control variables:

$$
RET_{i,t+1} = \lambda_{0,t} + \lambda_{1,t} \cdot \text{MAX}_{i,t} + \lambda_{2,t} \cdot X_{i,t} + \epsilon_{i,t+1},
\quad (1)
$$

where $RET_{i,t+1}$ is the excess return of stock $i$ in month $t+1$ and $X_{i,t}$ denotes the vector of control variables in month $t$ : MIS, CE, BETA, SIZE, BM, REV, MOM, ILLIQ, ROE, I/A, and IVOL defined in Section 3.3.

– Table 4 around here –

We restrict our Fama–MacBeth analyses to a fixed sample in which all observations have available data for every independent variable: MAX, BETA, MIS, CE, SIZE, BM, REV, MOM, ILLIQ, ROE, I/A, and IVOL. Thus, all regression specifications (Columns 1–6) are estimated using the same fixed sample, and the number of observations remains constant across specifications. To mitigate the effects of outliers in the regression tests, we winsorize all explanatory variables cross-sectionally at the 1st and 99th percentiles of their distribution. We apply winsorization to each variable on a month-to-month basis

21

---

# Page 23

using this fixed sample. $^{9}$

The first column of Table 4 presents the results from a univariate regression of one-month-ahead excess returns on MAX. The average slope on MAX turns out to be negative and statistically significant; $-0.210$ with a t-statistic of $-6.15$ . This result is consistent with the findings of Bali, Cakici, and Whitelaw (2011), and suggests that investors are willing to pay a high price to receive a small probability of a large payoff, or simply, investors overpay for stocks with high MAX.

The second column adds the standard set of control variables. While the magnitude of the MAX coefficient decreases, it remains negative and highly significant ( $-0.113$ with a t-statistic of $-5.40$ ), indicating that the pricing of MAX is robust beyond standard return predictors. The signs and significance of the control variables are generally in line with prior findings: smaller and value stocks tend to outperform, returns exhibit short-term reversal and medium-term momentum, and ROE is positively priced, while investment-to-assets ( $I/A$ ) and idiosyncratic volatility (IVOL) are negatively priced. The illiquidity premium is positive and statistically significant. It is worth noting that the reduction in the MAX coefficient is largely attributable to its significant correlation with IVOL (Hou and Loh, 2016); that is, in a specification that excludes IVOL, the coefficient on MAX remains almost unchanged.

The third column reports coefficients from a bivariate regression of returns on MAX and the mispricing score (MIS). The coefficient on MIS is negative and statistically significant ( $-0.026$ with a t-statistic of $-7.91$ ), supporting the idea of market correction where overvalued stocks experience downward price adjustments. The economic magnitude of the MAX coefficient in the bivariate regression declines by 22% (from $-0.210$ to $-0.163$ ) relative to the magnitude produced by the univariate regression, establishing mispricing as a potential economic driver of the lottery demand effect.

The fourth column presents a bivariate regression with MAX and composite equity issuance (CE). The coefficient on MAX again drops to $-0.187$ (t-stat. = $-5.80$ ), suggesting

$^{9}$ The winsorization procedure applied here would not affect the portfolio-level tests, which constitute the majority of the analyses carried out in the paper, as the portfolios are created according to their characteristics ranks (such as the ones for MAX and MAX $^{\beta}$ ) and their granularity is above a percentile.

22

---

# Page 24

that CE partly captures the information embedded in MAX. The CE variable is negatively and significantly priced ( $-0.017$ with a t-statistic of $-4.43$ ), consistent with the findings of Daniel and Titman (2006) and Stambaugh, Yu, and Yuan (2012, 2014, 2015), as firms tend to issue (repurchase) equity when shares are perceived to be overvalued (undervalued).

Columns 5 and 6 present the full multivariate specifications. In Column 5, after accounting for both MIS and the standard firm-level predictors, the average slope on MAX decreases to $-0.106$ (t-stat. = $-5.11$ ). In the final specification in Column 6, which includes CE and the other controls, the coefficient on MAX is $-0.110$ with a t-statistic of $-5.23$ . These results indicate that while a substantial portion of the predictive power of MAX is explained by mispricing, equity issuance, and other characteristics, MAX continues to carry a significant predictive power over future returns in an equal-weighted regression framework.

## 4.5 Dissecting the Anomaly: The Roles of Mispricing, Persistence, and Market Beta

Given that the MAX anomaly is concentrated in overpriced stocks and is explained by the mispricing factors, we now investigate which specific dimensions of mispricing are most important. Table 5 reports the one-month-ahead value-weighted seven-factor alphas ( $\alpha_{FF6PS}$ ) from bivariate sorts that condition the MAX-return relation on the underlying characteristics of the mispricing and behavioral factor models.

– Table 5 around here –

Panel A of Table 5 first sorts stocks into deciles based on the nine non-equity issuance mispricing characteristics from Stambaugh, Yu, and Yuan (2015) and the PEAD measure from Daniel, Hirshleifer, and Sun (2020). Within each of these deciles, stocks are then sorted into 10 portfolios based on MAX. The results show that even after controlling for these 10 mispricing and behavioral characteristics, the alpha spreads between the high- and low-MAX deciles remain economically sizeable and statistically significant.

23

---

# Page 25

Specifically, the monthly alpha spreads range from $-0.36\%$ to $-0.56\%$ per month, with t-statistics between $-1.97$ and $-3.11$.

Panel B isolates the impact of equity issuance on MAX. To do so, we construct a stock-level equity issuance index. Specifically, stocks are independently assigned percentile ranks based on (i) changes in split-adjusted shares outstanding (Ritter, 2008; Loughran and Ritter, 1995; Fama and French, 2008); (ii) composite equity issues, measured as the one-year growth in market capitalization minus the one-year equity return (Daniel and Titman, 2006); and (iii) the five-year composite share issuance (CSI) of Daniel and Titman (2006). A stock’s issuance index is then defined as the arithmetic average of its percentile ranks across these three equity issuance-related variables. We then perform a bivariate sort, first on this issuance index and then on MAX. The results are striking. Once we control for the equity issuance index, the value-weighted alpha spread between Portfolio 10 and Portfolio 1 declines to a statistically insignificant $-0.21\%$ per month (t-stat. = $-0.99$). Furthermore, the alpha of the high-MAX portfolio (Portfolio 10) becomes a negligible $-0.03\%$ per month (t-stat. = $-0.21$).

The finding that controlling for equity issuance eliminates the MAX anomaly has important implications for understanding its underlying source. Equity issuance is widely documented to be associated with persistent overvaluation and long-lasting mispricing (Baker and Wurgler, 2000; Daniel, Hirshleifer, and Sun, 2020). Unlike short-lived speculative demand, equity issuance decisions require mispricing that endures for months, as they involve considerable planning, due diligence, and regulatory procedures. Firms tend to issue equity when their shares are overpriced, capitalizing on predictable misvaluation rather than transitory pricing errors. Since the return predictability of MAX disappears after controlling for equity issuance, we hypothesize that the high-MAX stocks are primarily overpriced due to deeper, structural mispricing forces rather than transient investor attraction to lottery-like payoffs. This challenges the notion that the MAX anomaly is driven solely by short-term behavioral demand for positively skewed return distributions. Instead, the evidence points to a mispricing mechanism in which firms strategically time equity issuance to exploit persistent investor overreaction to stocks with extreme prior

24

---

# Page 26

returns. Overall, persistence is not a naturally expected characteristic of lottery-like stocks, as sustained outperformance would contradict the very notion of lottery-like payoffs. The finding that equity issuance factors largely account for the MAX anomaly therefore calls into question the view that it is driven by investors’ preference for lottery-like stocks.

The fact that the MAX anomaly is explained by factors associated with persistent mispricing raises a critical question: is the anomaly itself conditional on the persistence of high MAX? Table A1 in the Internet Appendix investigates this question directly. Panel A first establishes a strong contemporaneous link between MAX and stock returns, reporting a massive FF6PS alpha spread of 22.40% (t-stat. = 38.32) between the highest and lowest MAX deciles in the formation month. This magnitude motivates the inquiry into persistence. Panel B reveals that the predictive power of MAX is strictly conditional on its past performance. The results are stark: stocks with high MAX in both the current and prior month exhibit a significant one-month-ahead FF6PS alpha of $-0.91\%$ per month (t-stat. = $-3.47$). In contrast, stocks that experience a transient spike into the high-MAX decile show no significant subsequent underperformance. This dependence on persistence intensifies over longer horizons; the negative alpha deepens to $-1.32\%$ per month for four consecutive high-MAX months. This demonstrates that the MAX anomaly is not driven by one-off extreme returns, but by a small subset of stocks that consistently exhibit high MAX. Panel C shows that this persistence phenomenon is powerfully amplified by investor sentiment. During high-sentiment periods, as defined by Baker and Wurgler (2006), the underperformance of persistently high-MAX stocks becomes even more severe, with alphas reaching $-1.88\%$ for stocks with four consecutive months of high MAX. Conversely, during low-sentiment periods, the effect is muted and often statistically insignificant. This evidence strongly suggests that the MAX anomaly is a phenomenon of sustained overvaluation, exacerbated by market-wide optimism, rather than a typical preference for lottery-like payoffs.

Next, we examine the mispricing-related characteristics of the high-MAX portfolios, conditional on their prior performance and investor sentiment in Table A2 in the Appendix. This table complements the analysis in Table A1 by offering a deeper look into the

25

---

# Page 27

characteristics of persistently high-MAX stocks. It is important to note that for this analysis, we use the one-year firm-level composite equity issuance (CE) measure rather than the composite issuance index introduced in Table 5. The ranked index does not adequately reflect time-series variation, whereas the firm-level measure captures actual issuance behavior, making it more appropriate for examining dynamic responses to sentiment. This variation is critical for identifying the link between sentiment, mispricing, and managerial issuance decisions. Panel A of Table A2 reports the time-series average of the cross-sectional median for MIS, CE, and market MAX beta. The first three columns show that for stocks with high MAX in month $ t $ , those that also had high MAX in $ t - 1 $ exhibit markedly higher MIS and CE than those with transient MAX spikes. Relative to the summary statistics in Table 2, these results reinforce that persistent MAX behavior is closely associated with mispricing-related fundamentals; stocks with high-MAX over two consecutive periods exhibit substantially higher mispricing and issuance activity. This points to a speculative component driven by investor over-extrapolation and managerial timing, rather than one-off lottery-like payoffs. Columns 4 through 7 show that this pattern strengthens as the persistence horizon extends to three and four months. Panel B further conditions these characteristics on sentiment regimes. The results show that the differences in MIS and CE between persistently high-MAX portfolios and others widen significantly during high sentiment periods. Moreover, both MIS and CE are markedly higher in high-sentiment periods than in low-sentiment periods. These findings indicate that investor sentiment amplifies the mispricing dynamics underlying the MAX anomaly.

Given that MAX contains a significant systematic (or cross-sectionally persistent) component, we investigate how persistence and the market beta jointly affect its pricing. Table A3 in the Appendix examines this by sorting stocks into high and low market beta subgroups. Panel A shows that the strong contemporaneous link between MAX and stock returns holds within both beta groups. The core findings presented in Panel B reveal a crucial asymmetry in the predictive power of MAX. For high-beta stocks, the MAX anomaly—manifested as negative FF6PS alphas for decile 10 portfolios ranked on MAX in month $ t $ —requires persistence; significant underperformance only occurs for stocks

---

# Page 28

that had high- or mid-MAX in the prior month. In contrast, for low-beta stocks, the anomaly is unconditional on persistence; high-MAX stocks underperform significantly regardless of their prior month’s MAX. This suggests that for high-beta stocks, the MAX effect is entangled with systematic risk, whereas for low-beta stocks, it captures a cleaner pricing error. Panel C reinforces this by showing that during low-sentiment periods, the anomaly vanishes for high-beta stocks with non-persistent MAX (corresponding to the Low or Non-High subgroups) but remains relatively strong for non-persistent low-beta stocks, underscoring that the predictive power of MAX is most pronounced for stocks with limited systematic risk exposure.

Table A4 in the Appendix complements this by examining the characteristics of these portfolios. Panel A shows that high-beta, high-MAX stocks have higher mispricing (MIS) and substantially more equity issuance (CE) than their low-beta counterparts. Panels B and C confirm that these mispricing characteristics are strongest for stocks with persistent MAX performance and are amplified during high-sentiment periods, particularly within the high-beta group. Together, these results suggest that overvaluation and issuance are key drivers of the MAX anomaly, with these effects being most prominent among high-beta or persistently high-MAX stocks, and exacerbated by high investor sentiment.

## 5 Isolating the Lottery Preference: The MAX $^\beta$ Anomaly

The preceding section establishes that the MAX anomaly is concentrated in overpriced stocks and is largely explained by persistent mispricing, particularly equity issuance. Furthermore, its predictive power is strictly conditional on the persistence of past MAX performance and is confounded by market beta. These findings challenge the view that MAX serves as a clean proxy for investor preference for lottery-like payoffs, which should theoretically be idiosyncratic and not dependent on sustained performance or systematic risk.

This section introduces and validates an alternative measure, MAX $^\beta$ , designed to purge the systematic return component from MAX and better isolate the idiosyncratic

27

---

# Page 29

features that define a lottery-like asset. We first detail the construction of $\text{MAX}^{\beta}$ and demonstrate its significant, robust predictive power for future returns — a power that, unlike the original MAX, cannot be explained by the existing risk or mispricing factor models. We then analyze the characteristics of $\text{MAX}^{\beta}$ -sorted portfolios to confirm that our procedure successfully neutralizes systematic risk and sharpens the measure’s connection to idiosyncratic skewness and investor behavior. Finally, we provide extensive evidence from portfolio sorts and firm-level regressions showing that the $\text{MAX}^{\beta}$ anomaly is distinct from and robust to controls for the persistent mispricing channels that explain the original MAX anomaly, and that its abnormal performance, unlike that of the original MAX anomaly, does not concentrate in states of elevated aggregate overvaluation.

## 5.1 The Predictive Power of $\text{MAX}^{\beta}$

Since MAX may contain a substantial systematic component, we propose $\text{MAX}^{\beta}$ as a superior proxy for lottery-like payoffs. We construct this MAX-on-steroids measure using a non-parametric, double-sorting portfolio procedure. Each month, we first sort stocks into decile portfolios based on the market beta. Within each beta-sorted portfolio, we then sort stocks again into deciles based on MAX. Finally, we form the $\text{MAX}^{\beta}$ portfolios by regrouping all stocks that fall into the same MAX decile rank across all 10 beta deciles. This procedure ensures that each $\text{MAX}^{\beta}$ portfolio contains stocks with similar MAX rankings but varying market beta, effectively controlling for systematic return exposure and isolating the idiosyncratic component of extreme returns.

– Table 6 around here –

Table 6 presents the one-month-ahead value-weighted average returns for decile portfolios sorted on $\text{MAX}^{\beta}$ . The results demonstrate that $\text{MAX}^{\beta}$ has significant predictive power. The average return spread between the high- and low- $\text{MAX}^{\beta}$ portfolios is $-0.81\%$ per month and highly significant with a t-statistic of $-3.62$ . This spread remains economically large and statistically significant across all standard risk factor models. The alphas are: $\alpha_{CAPM} = -1.00\%$ , $\alpha_{FF3} = -0.90\%$ , $\alpha_{FFC4} = -0.95\%$ , $\alpha_{FFCPS} = -0.96\%$ ,

28

---

# Page 30

$\alpha_{FF5} = -0.67\%$ , $\alpha_{FF6} = -0.72\%$ , and $\alpha_{FF6PS} = -0.73\%$ , with t-statistics ranging from $-3.33$ to $-4.98$ . $^{10}$

Unlike the univariate MAX sorts, the alpha spreads for MAX $^{\beta}$ -sorted portfolios are driven by both legs of the arbitrage portfolio. Portfolio 10 earns significantly negative risk-adjusted returns, ranging from $-0.42\%$ to $-0.82\%$ per month (t-statistics ranging from $-3.14$ to $-4.33$ ), consistent with the overpricing of lottery-like stocks. In contrast, Portfolio 1 earns significantly positive alphas between $0.18\%$ and $0.25\%$ per month (all significant at the $1\%$ level). This outperformance of the low-MAX $^{\beta}$ portfolio may reflect compensation for low skewness.

Crucially, the last two columns of Table 6 show that the MAX $^{\beta}$ anomaly is robust to recently proposed mispricing factor models. The mispricing-adjusted alpha spreads remain large and significant: the $\alpha_{SY}$ and $\alpha_{DHS}$ spreads are $-0.62\%$ (t-stat. = $-3.33$ ) and $-0.46\%$ (t-stat. = $-2.10$ ), respectively. This is a key distinction from the original MAX anomaly, as pointed out by the insignificant $\alpha_{SY}$ and $\alpha_{DHS}$ spreads on MAX-sorted portfolios, presented in the last two columns of Table 1. By controlling for market-wide movements to isolate stock-specific lottery-like behavior, MAX $^{\beta}$ uncovers a return predictability that cannot be explained by the existing risk or mispricing factor models.

## 5.2 Characteristics of MAX $^{\beta}$ Portfolios

Table A5 in the Appendix examines the firm-level characteristics of the MAX $^{\beta}$ -sorted decile portfolios. The results confirm the effectiveness of our sorting procedure and highlight the key differences from the univariate MAX sorts. First, as shown in the second column, the market beta remains constant across the MAX $^{\beta}$ deciles, with a spread of zero between the extreme portfolios. This provides direct evidence that our methodology

---

$^{10}$ Bali, Brown, Murray, and Tang (2017) show that the betting-against-beta (BAB) anomaly originally proposed by Frazzini and Pedersen (2014) is concentrated in stocks with high retail ownership and it exists only when the price impact of lottery demand is concentrated in high-beta stocks. Given the high correlation Bali et al. (2017) note between these two effects, we test whether our proposed measure (MAX $^{\beta}$ ) is distinct from the BAB anomaly. To do so, we control for the BAB factor of Frazzini and Pedersen (2014) and re-estimate the long-short abnormal return spread on MAX $^{\beta}$ -sorted portfolios. The resulting FF6PS+BAB alpha spread remains negative, economically large and highly statistically significant at $-0.69\%$ per month with a t-statistic of $-3.47$ . This result demonstrates that the BAB factor does not explain the phenomenon captured by our new measure of investor attraction to lottery stocks.

29

---

# Page 31

successfully controls for systematic risk exposure while retaining a large and significant spread in MAX itself.

The next two columns show that controlling for market beta weakens the link between MAX and persistent mispricing. The spread in the mispricing score (MIS) between the extreme portfolios declines from 11.04 in the univariate MAX sort to 7.45 for MAX $^{\beta}$ -sorted portfolios. Similarly, the spread in composite equity issuance (CE) decreases from 0.033 to 0.019. This indicates that once portfolios are neutralized with respect to the market beta, the degree of overvaluation associated with the highest MAX portfolio diminishes.

Conversely, the link to idiosyncratic lottery-like features is sharpened. The market MAX beta spread plummets from 0.546 to 0.036, indicating that MAX $^{\beta}$ is far less sensitive to market-wide extreme returns. The spread in institutional ownership (INST) becomes more negative ( $-0.212$ vs. $-0.152$ ), and the spread in expected idiosyncratic skewness, E(ISKEW), increases from 0.390 to 0.451. This suggests that institutions are more inclined to hold low-MAX $^{\beta}$ stocks, and that MAX $^{\beta}$ provides a cleaner cross-sectional relationship with the idiosyncratic skewness that lottery-seeking investors prefer. Other characteristics such as SIZE, IVOL, BM, REV, MOM, ILLIQ, ROE, and I/A exhibit patterns similar to those in the univariate MAX sorts.

## 5.3 Is the MAX $^{\beta}$ Anomaly Distinct from Mispricing?

While MAX $^{\beta}$ appears less related to mispricing than the original MAX, we formally test its robustness to mispricing controls in Table 7. We conduct triple sorts to examine whether the predictive power of MAX $^{\beta}$ persists after controlling for equity issuance and the aggregate mispricing score.

– Table 7 around here –

Panel A of Table 7 controls for equity issuance. The first column replicates the earlier result, showing the original MAX alpha spread becomes an insignificant $-0.21\%$ per month (t-stat. = $-0.99$ ) after controlling for the stock-level equity issuance index. In stark contrast, the second column shows that the alpha spread on issuance-controlled MAX $^{\beta}$ -

30

---

# Page 32

sorted portfolios remains economically sizeable and statistically significant at $-0.48\%$ per month (t-stat. = $-2.32$ ).

Panel B conducts a similar analysis controlling for the aggregate mispricing score (MIS). Again, the value-weighted alpha spread on the original MAX-sorted portfolio becomes an insignificant $-0.29\%$ per month (t-stat. = $-1.53$ ). However, the predictive power of $\text{MAX}^{\beta}$ remains strong and statistically significant.

Taken together, the results in Table 7 highlight a key distinction: while the return predictability of MAX is largely absorbed by proxies for persistent mispricing, the alpha spread on $\text{MAX}^{\beta}$ -sorted portfolios remains strong. This suggests that $\text{MAX}^{\beta}$ isolates an idiosyncratic, short-horizon pricing component that is distinct from these broader mispricing channels and represents a novel cross-sectional return predictor.

## 5.4 Firm-Level Evidence for the $\text{MAX}^{\beta}$ Anomaly

To test the robustness of our portfolio-level findings, Table 8 presents firm-level Fama-MacBeth (1973) cross-sectional regressions of one-month-ahead excess returns on $\text{MAX}^{\beta}$ . Since $\text{MAX}^{\beta}$ is a portfolio-level measure, we use 10 dummy variables for the decile rankings, omitting the lowest decile.

– Table 8 around here –

We restrict our Fama–MacBeth analyses to a fixed sample in which all observations have available data for every independent variable: MAX, BETA, MIS, CE, SIZE, BM, REV, MOM, ILLIQ, ROE, I/A, and IVOL. Thus, all regression specifications (Columns 1–6) are estimated using the same fixed sample, and the number of observations remains constant across specifications. To mitigate the effects of outliers in the regression tests, we winsorize all explanatory variables cross-sectionally at the 1st and 99th percentiles of their own distribution. We apply winsorization to each variable on a month-to-month basis using this fixed sample.

Column 1 shows the results of a regression on only the $\text{MAX}^{\beta}$ dummies. The coefficients on the two highest decile dummies are large and highly significant; D10 and D9 have

31

---

# Page 33

coefficients of $-1.027$ (t-stat. = $-6.61$ ) and $-0.566$ (t-stat. = $-4.98$ ), respectively, indicating that stocks in the top two $\text{MAX}^\beta$ deciles significantly underperform the bottom decile.

Column 2 adds a comprehensive set of control variables. While the coefficients are attenuated, they remain significant; the underperformance of the highest $\text{MAX}^\beta$ portfolio relative to the lowest is 43.5 basis points per month. This reduction is largely driven by the inclusion of IVOL, which is highly correlated with MAX. Columns 3 and 4 show that adding MIS and CE individually only modestly decreases the $\text{MAX}^\beta$ coefficients. Finally, Columns 5 and 6 present the full regression specifications. Even after controlling for a comprehensive set of return predictors and mispricing characteristics, $\text{MAX}^\beta$ continues to exhibit a strong and statistically significant negative relationship with future stock returns.

## 5.5 The Role of Persistence in the $\text{MAX}^\beta$ Anomaly

Our final test addresses a key conceptual inconsistency of the original MAX measure: its dependence on persistence of past performance. Table A6 in the Appendix replicates the persistence analysis from Table A1 but uses $\text{MAX}^\beta$ -sorted portfolios.

Panel A of Table A6 first confirms that a strong contemporaneous relationship exists between $\text{MAX}^\beta$ and stock returns. Panel B then presents the central finding of this analysis. In stark contrast to the original MAX, high- $\text{MAX}^\beta$ stocks underperform in the subsequent month regardless of their prior $\text{MAX}^\beta$ levels. For instance, as shown in Columns 1-3, if a stock appears in the highest $\text{MAX}^\beta$ portfolio in month $t$ , its expected one-month-ahead risk-adjusted return is significantly negative whether it came from a high-, medium-, or low- $\text{MAX}^\beta$ portfolio in month $t-1$ , with alphas of $-0.78\%$ (t-stat. = $-3.25$ ), $-0.40\%$ (t-stat. = $-2.54$ ), and $-0.30\%$ (t-stat. = $-2.10$ ), respectively. The results in Columns 4-7, which examine longer horizons, confirm that this underperformance does not require consecutive months of high- $\text{MAX}^\beta$ rankings.

This lack of dependence on sustained past performance is a crucial distinction. While the predictive power of MAX is driven by persistently overvalued stocks, the $\text{MAX}^\beta$ effect

32

---

# Page 34

reflects a more transient pricing dynamic. This makes MAX $^{\beta}$ a more proper proxy for capturing investor preference for lottery-like payoffs, which should not be conditional on a stock’s longer-term past performance.

## 5.6 Aggregate Mispricing Conditioning of the MAX and MAX $^{\beta}$ Anomalies

This subsection examines whether the cross-sectional return predictability of MAX and MAX $^{\beta}$ is concentrated in states of the world in which aggregate overvaluation is elevated. The motivation is conceptual: a return predictor that reflects persistent mispricing should exhibit state-dependent abnormal performance, with the largest spreads realized when overvaluation is most pronounced; a return predictor that reflects a time-invariant preference for idiosyncratic skewness should not. Conditioning the cross-section on aggregate proxies for sentiment-driven and issuance-driven overvaluation, in the spirit of Baker and Wurgler (2006) and Stambaugh, Yu, and Yuan (2012, 2015), provides a direct test of this distinction.

A clarification about the design of the tests is in order. We do not infer the time-invariance of an underlying preference from the time-invariance of a return spread, nor the converse. A preference is a deep parameter of the agent, while its asset pricing footprint depends on the marginal trader (Shleifer and Vishny, 1997): even if retail investors’ preference for lottery-like idiosyncratic skewness is structurally stable, their marginal price impact in the larger, more liquid securities to which value-weighted spreads are most sensitive varies with their level of market participation. Crucially, our two conditioning variables capture this state-dependence through different channels. Investor sentiment proxies for the intensity of retail participation: when sentiment is high, the marginal price impact of lottery-seeking investors rises, so a spread driven by a stable retail preference widens even if the preference itself is fixed (Baker and Wurgler, 2006; Stambaugh, Yu, and Yuan, 2012). Aggregate issuance, in contrast, proxies for managers’ market-timing of overvaluation (Baker and Wurgler, 2000), and is therefore the cleaner signal of aggregate mispricing per se. It follows that a mispricing-driven predictor should concentrate in

33

---

# Page 35

high states of both variables, whereas a preference-driven predictor whose price impact merely scales with participation should strengthen with sentiment yet remain present across issuance regimes. The aggregate conditioning tests should therefore be read as evidence on the state-dependence of pricing, not on the state-dependence of preference.

We use the Baker and Wurgler (2006) sentiment index as the investor sentiment proxy and an aggregate issuance index, defined as the value-weighted cross-sectional average of firm-level twelve-month composite equity issuance following Daniel and Titman (2006), as the aggregate issuance proxy. High and Low states are defined, respectively, as months in which the conditioning variable lies above its in-sample median and months in which it lies at or below the median. All abnormal returns are seven-factor alphas (FF6PS), computed relative to the Fama and French (2018) six-factor model augmented with the Pastor and Stambaugh (2003) liquidity factor.

Table A7 in the Internet Appendix reports the value-weighted FF6PS alphas for MAX-sorted and MAX $^{\beta}$ -sorted decile portfolios across High and Low states of investor sentiment and aggregate issuance. We highlight two patterns.

First, the MAX 10−1 alpha spread is concentrated in high-sentiment and high-issuance regimes. The spread is $-0.82\%$ per month (t-stat. = $-2.85$ ) in high-sentiment months and shrinks to a statistically insignificant $-0.36\%$ (t-stat. = $-1.42$ ) in low-sentiment months. The pattern across aggregate issuance regimes is qualitatively similar but more attenuated: the spread is $-0.72\%$ (t-stat. = $-2.61$ ) in high-issuance months and an insignificant $-0.43\%$ (t-stat. = $-1.64$ ) in low-issuance months. This evidence is consistent with the interpretation of MAX as a mispricing-driven anomaly whose return predictability is amplified in regimes of elevated investor overvaluation, in line with Stambaugh, Yu, and Yuan (2012), who show that mispricing-driven anomalies are stronger following periods of high investor sentiment.

Second, the MAX $^{\beta}$ 10−1 alpha spread behaves very differently across the two conditioning variables, in a manner that maps onto the two channels distinguished above. Under investor sentiment conditioning, the spread is $-0.95\%$ (t-stat. = $-3.72$ ) in high-sentiment months and $-0.44\%$ (t-stat. = $-1.97$ ) in low-sentiment months. The spread thus declines

---

# Page 36

in magnitude by a proportion comparable to that of MAX, but, in contrast to MAX, it remains statistically significant in low-sentiment months. This residual significance, taken together with the amplification under high sentiment, is consistent with a stable retail preference whose price impact scales with participation, rather than with a spread that is switched on only by aggregate overvaluation. Under aggregate issuance conditioning, by contrast, the spread is essentially invariant: the $10-1$ alphas are $-0.71\%$ (t-stat. = $-2.92$ ) in high-issuance months and $-0.65\%$ (t-stat. = $-2.69$ ) in low-issuance months, both economically large and statistically significant. Because aggregate issuance is the proxy most directly tied to managerial market-timing of overvaluation, this invariance, rather than the behavior across sentiment states, is what most cleanly distinguishes MAX $^\beta$ from a mispricing-driven predictor: a preference-based premium should be present across high- and low-mispricing states, while a mispricing-based premium should not. Although the $10-1$ spread is stable across issuance states, its composition shifts. In high-issuance months it is driven mainly by the outperformance of the low-MAX $^\beta$ (long) leg (decile 1 alpha of $0.32\%$ , t-stat. = $3.13$ , with the high-MAX $^\beta$ leg insignificant at $-0.39\%$ , t-stat. = $-1.83$ ), whereas in low-issuance months it is driven by the underperformance of the high-MAX $^\beta$ (short) leg (decile 10 alpha of $-0.55\%$ , t-stat. = $-2.80$ , with the low-MAX $^\beta$ leg insignificant). This two-sided pattern is consistent with the skewness-premium interpretation developed in Section 6, in which institutions earn a premium for holding low-skewness stocks while retail investors overpay for high-skewness stocks.

In summary, the abnormal performance of MAX-sorted portfolios is concentrated in months of elevated investor sentiment and, to a lesser extent, elevated aggregate issuance, with the $10-1$ alpha spread becoming statistically insignificant in low-sentiment and low-issuance regimes. This state-dependence is consistent with the characterization of MAX as a mispricing-driven anomaly whose return predictability is amplified by aggregate overvaluation. The abnormal performance of MAX $^\beta$ -sorted portfolios is, by contrast, approximately invariant across aggregate issuance regimes, the cleanest signal of aggregate mispricing; across sentiment regimes it weakens by a margin comparable to that of MAX but, unlike MAX, remains statistically significant, consistent with a stable preference

35

---

# Page 37

whose price impact rises with retail participation. The evidence reinforces the central thesis: MAX is not a clean proxy for skewness preference; rather, it captures a composite of mispricing forces that are state-dependent in a manner consistent with the broader anomaly literature, while MAX $^{\beta}$ isolates a structural component of the cross-section that is stable across the aggregate mispricing states identified by managerial issuance.

## 6 Economic Mechanisms: Investor Heterogeneity and Skewness Preference

The preceding sections establish MAX $^{\beta}$ as a robust anomaly, distinct from the persistent mispricing that largely explains the original MAX effect. The two differ in the source of their return spread: the MAX anomaly is driven primarily by the underperformance of high-MAX stocks, whereas the MAX $^{\beta}$ anomaly is two-sided, arising from both the underperformance of high-MAX $^{\beta}$ stocks and the outperformance of low-MAX $^{\beta}$ ones. This “arbitrage symmetry,” in contrast to the “arbitrage asymmetry” of the MAX effect, points to a richer mechanism than simple overpricing: the short-leg underperformance is consistent with overpaying for lottery-like features, but the long-leg outperformance suggests a premium for an undesirable characteristic, low skewness. This section examines the economic mechanisms behind that pattern, showing that the original MAX anomaly is driven by mispricing, whereas MAX $^{\beta}$ reflects the pricing of skewness by heterogeneous retail and institutional clienteles.

### 6.1 Investor Heterogeneity and the Pricing of Skewness

To better understand the investor preferences that shape the pricing of MAX and MAX $^{\beta}$ , Table 9 examines the role of institutional ownership (INST). We use INST to proxy for the presence of sophisticated versus retail investors. Specifically, we divide the sample into three tiers based on the 33rd and 67th percentiles of INST. Within each tier, we form decile portfolios by sorting stocks on MAX (Panel A) and MAX $^{\beta}$ (Panel B) and report their one-month-ahead value-weighted average excess returns and seven-factor

36

---

# Page 38

(FF6PS) alphas.

– Table 9 around here –

Panel A of Table 9 confirms that the original MAX anomaly is a phenomenon concentrated among stocks with low institutional ownership. The effect is negatively and significantly priced only within the lowest INST tier (INST1), where the alpha spread between the high- and low-MAX deciles is $-0.85\%$ (t-stat. = $-2.36$ ) and is driven by the underperformance of the high-MAX portfolio. In contrast, the MAX anomaly is absent in the higher institutional ownership tiers (INST2 and INST3). This suggests that individual investors are the primary drivers of the overvaluation of high-MAX stocks, consistent with the findings of Han and Kumar (2013) and Bali et al. (2017).

Panel B of Table 9 reports the results for MAX $^\beta$ -sorted portfolios. The findings are more nuanced and powerful. Within the lowest INST tier (INST1), the MAX $^\beta$ effect is even stronger, with a return spread of $-1.54\%$ and an alpha spread of $-1.44\%$ per month with corresponding t-statistics of $-3.59$ and $-3.95$ . This alpha spread is primarily driven by the poor performance of the high-MAX $^\beta$ portfolio, which delivers an alpha of $-1.18\%$ (t-stat. = $-4.07$ ), indicating that the lottery demand effect is strongest among stocks dominated by retail investors. Notably, the MAX $^\beta$ anomaly persists into the middle tier (INST2), with a significant alpha spread of $-0.51\%$ (t-stat. = $-2.17$ ) driven by both the underperformance of the high-MAX $^\beta$ portfolio (alpha = $-0.35\%$ ) and the outperformance of the low-MAX $^\beta$ portfolio (alpha = $0.16\%$ ).

Most interestingly, in the highest institutional ownership tier (INST3), the alpha spread remains economically large at $-0.37\%$ per month and statistically significant at the 5% level (t-stat. = $-1.96$ ), but its source shifts to the long-leg of the arbitrage portfolio. The spread is now primarily driven by the strong performance of the low-MAX $^\beta$ portfolio, which earns a positive alpha of $0.23\%$ per month (t-stat. = $2.45$ ). This pattern is distinct from a conventional lottery-demand story and points towards a premium for low skewness. As shown in our earlier analysis, the low-MAX $^\beta$ stocks exhibit lower idiosyncratic skewness than the low-MAX stocks. The outperformance of these stocks among sophisticated investors suggests that these institutions may require extra compensation in the form of

37

---

# Page 39

higher expected return for holding assets that reduce portfolio skewness. The observed pricing dynamic, where the source of the anomaly shifts across investor clienteles, can be understood through the lens of heterogeneous preferences for skewness. This finding aligns well with the theoretical framework of Mitton and Vorkink (2007), which posits a market with two distinct investor clienteles: “lotto investors,” which can be viewed as retail investors, and “traditional investors,” which we consider as institutional investors. These groups are differentiated by the intensity of their preference for skewness. “Lotto investors” exhibit a strong demand for assets with extreme positive skewness, leading them to bid up the prices of high-MAX $^{\beta}$ securities and causing their subsequent underperformance, which is precisely what we observe in the low-INST tier. Conversely, “traditional investors” are skewness-neutral and averse to holding underdiversified, non-mean-variance efficient portfolios. To compensate for concentrating their holdings in low-skew assets, they require a return premium. This required premium explains the outperformance of low-MAX $^{\beta}$ stocks, an effect that is most pronounced in the segment of the market dominated by these sophisticated investors.

One potential concern with sorting by raw institutional ownership is its well-documented positive correlation with firm size. To ensure our findings are not inadvertently capturing a size effect, we conduct a robustness test using a size-orthogonalized measure of institutional ownership. Following the methodology of Nagel (2005), we construct this measure by estimating month-to-month cross-sectional regressions of the logit transformation of INST on the logarithm of market capitalization, and we use the resulting residuals as the orthogonalized INST proxy. To accommodate boundary conditions, the logit of INST is defined as $\log\left(\frac{INST}{1-INST}\right)$ , where values of INST below 0.0001 and above 0.9999 are replaced with 0.0001 and 0.9999, respectively. Table A8 in the Appendix reports the results for portfolios sorted within these size-orthogonalized INST tiers.

Notably, the findings for the $MAX^{\beta}$ anomaly, presented in Panel B of Table A8, demonstrate strong robustness to the size control. The alpha spreads remain economically large and statistically significant across the orthogonalized INST tiers. Crucially, the underlying drivers of these spreads remain consistent with our baseline observations.

38

---

# Page 40

Within the lowest INST tier (INST 1), the $MAX^\beta$ effect is primarily driven by the poor performance of the high- $MAX^\beta$ portfolio. In contrast, within the highest institutional ownership tier (INST 3), the alpha spread is primarily driven by the strong performance of the low- $MAX^\beta$ portfolio. This distinct shifting pattern once again aligns with the theoretical framework of Mitton and Vorkink (2007), confirming that lotto investors and traditional institutions exhibit heterogeneous preferences for skewness that are distinct from standard size effects.

## 6.2 Institutional Demand and the Compensation for Bearing Low Skewness

Section 6.1 establishes that the source of the $MAX^\beta$ spread shifts across investor clienteles: the short-leg (high- $MAX^\beta$ ) underperformance dominates among retail-dominated stocks, whereas the long-leg (low- $MAX^\beta$ ) outperformance emerges among institution-dominated stocks (Table 9, tier INST3). If, as the framework of Mitton and Vorkink (2007) implies, this long-leg premium is the compensation that institutions require for holding low-skewness assets, then it should accrue to the stocks that institutions hold and, more tellingly, to those they are actively accumulating. The premium arises not because institutions dislike skewness, since they are skewness-neutral, but because the aggressive demand of skewness-loving retail investors for high-skewness stocks leaves institutions holding a concentrated, non-mean-variance-efficient position in the low-skewness remainder; it is this underdiversification, not the low skewness itself, that they require compensation to bear (Section 6.1). This subsection provides that evidence by examining institutional ownership and its change within each leg of the $MAX^\beta$ strategy. For either strategy we call the low-decile (decile 1) portfolio the long leg and the high-decile (decile 10) portfolio the short leg, the long and short sides of the low-minus-high long-short strategy; thus the long leg of $MAX^\beta$ is the low- $MAX^\beta$ portfolio and its short leg is the high- $MAX^\beta$ portfolio, and likewise for MAX. We use these designations interchangeably.

– Table 10 around here –

39

---

# Page 41

We condition each leg on three variables, the level of institutional ownership (INST), its change through the most recent quarter-end ( $\Delta$ INST, measured prior to the return month so that the sort involves no look-ahead, and which proxies for institutional accumulation), and expected idiosyncratic skewness (E(ISKEW)) of Boyer, Mitton, and Vorkink (2010). $^{11}$ Table 10 reports one-month-ahead value-weighted FF6PS alphas for terciles formed within the long leg (Panel A) and the short leg (Panel B). On the long leg, the low-MAX $^{\beta}$ premium rises monotonically with the level of institutional ownership, from an insignificant 0.12% per month in the lowest INST tier to 0.23% (t-stat. = 2.56) in the highest; this last figure recovers a premium of the same magnitude as the one isolated among institution-dominated stocks in Section 6.1 (Table 9), reached there by sorting on MAX $^{\beta}$ within the top INST tier rather than, as here, on INST within the low-MAX $^{\beta}$ decile, so that the two conditionings run in opposite order yet agree, and the level sort establishes continuity rather than new content. The new dimension is the flow. The premium rises far more sharply with institutional accumulation than with the level of ownership: stocks in the top $\Delta$ INST tier earn an alpha of 0.70% per month (t-stat. = 6.31), whereas those that institutions have not been accumulating earn a negative and marginally significant $-0.19\%$ . The premium is thus concentrated among the low-MAX $^{\beta}$ stocks that institutions are buying, not merely among those they hold. Consistent with a skewness-based interpretation, the premium is also larger among the lowest-skewness stocks within the leg, at 0.34% (t-stat. = 3.16) in the bottom E(ISKEW) tier.

Panel B reveals the symmetric pattern on the short leg. The high-MAX $^{\beta}$ underperformance is a phenomenon of stocks that institutions avoid: the alpha is $-1.97\%$ per month (t-stat. = $-6.28$ ) in the lowest INST tier and a statistically indistinguishable 0.05% in the highest, and it is steepest among the highest-skewness stocks, at $-0.94\%$ (t-stat. = $-4.80$ ) in the top E(ISKEW) tier, while it is statistically insignificant in the bottom E(ISKEW) tier, at $-0.20\%$ (t-stat. = $-0.88$ ). Accumulation completes the

$^{11}$ On the long leg, high $\Delta$ INST marks institutional accumulation, the channel through which the compensation is earned. On the short leg the reading is the mirror image: institutional and retail ownership are approximately complementary, so net institutional selling, a low value of $\Delta$ INST, is an imperfect proxy for retail accumulation, informative in its direction though not exact, since $\Delta$ INST is a net institutional flow rather than gross retail buying.

40

---

# Page 42

picture from the retail side. The underperformance concentrates where institutions are selling, at $-1.51\%$ (t-stat. $= -5.66$ ) in the lowest $\Delta \text{INST}$ tier, the high-MAX $^\beta$ stocks that retail is accumulating, and turns positive, $0.94\%$ (t-stat. $= 4.19$ ), among the stocks institutions are buying. The overpricing is thus borne by the lottery stocks moving into retail hands, as the premium is borne by the low-skewness stocks moving into institutional hands; we read this as corroborating the retail-overpayment mechanism rather than as decisive, since institutional flow of this sign predicts returns in the broad cross-section as well. Taken together, the two panels trace both sides of the single skewness-preference mechanism developed in Section 6.1: retail overpayment for high-skewness stocks where institutions are absent, and an institutional premium for holding low-skewness stocks where institutions are present.

– Table 11 around here –

The role of institutional accumulation deserves closer scrutiny, because it speaks directly to the mechanism. Table 11 sharpens the evidence in two ways. Panel A reports an independent double sort that intersects the low-MAX $^\beta$ decile with INST terciles and, within each intersection, reports the average change in institutional ownership through the most recent quarter-end (again measured prior to the return month), expected idiosyncratic skewness, and the one-month-ahead FF6PS alpha. This double sort uses independent, full-sample INST breakpoints, in contrast to the within-leg terciles of Table 10, so the tier alphas here need not coincide with those in the INST panel of Table 10. The three quantities move together in a manner difficult to reconcile with anything other than the institutional demand for low-skewness assets that the mechanism of Section 6.1 predicts. As institutional ownership rises across the terciles, the change in institutional ownership rises from essentially zero ( $-0.01\%$ ) among low-INST stocks to a strongly positive $0.28\%$ among high-INST stocks, expected idiosyncratic skewness falls from $1.04$ to $0.60$ , and the alpha rises from an insignificant $0.05\%$ to a significant $0.24\%$ (t-stat. $= 2.52$ ). Institutions are accumulating precisely the lower-skewness low-MAX $^\beta$ stocks, and it is these stocks that earn the premium.

41

---

# Page 43

Panel B pushes the point to a triple sort. Among low-MAX $^{\beta}$ stocks that are both highly held and actively accumulated by institutions, that is, high-INST and high- $\Delta$ INST, the FF6PS alpha is 0.74% per month (t-stat. = 5.02) under a dependent sort and 0.78% (t-stat. = 4.63) under an independent sort. The magnitude is striking: the low-MAX $^{\beta}$ stocks that institutions are buying earn close to 80 basis points per month in abnormal returns. It is worth emphasizing what the change in institutional ownership captures here. Even if $\Delta$ INST does not perfectly proxy the timing of institutional trades, a portfolio of low-MAX $^{\beta}$ , high-INST stocks that have been gaining institutional ownership is, by construction, a portfolio moving further into institutional hands, and the fact that this portfolio earns a large and significant premium is exactly what our economic story predicts: institutions are compensated for the underdiversification that the low-skewness exposure they are accumulating entails.

The mirror portfolio completes the symmetry. High-MAX $^{\beta}$ stocks that are both retail-dominated and being accumulated by retail, that is, low-INST and low- $\Delta$ INST, earn $-1.09\%$ per month (t-stat. = $-2.79$ ) under a dependent sort and $-1.00\%$ (t-stat. = $-3.50$ ) under an independent sort. The two corners bracket the mechanism: the low-MAX $^{\beta}$ stocks institutions are buying earn close to $+0.8\%$ , while the high-MAX $^{\beta}$ stocks retail is buying lose close to $-1\%$ , the same complementary flow compensating one clientele and penalizing the other.

## 6.3 The Durability of the Skewness Premium

The evidence to this point is cross-sectional, identifying the investors who earn the low-MAX $^{\beta}$ premium and the circumstances under which they do so. It cannot, however, distinguish an equilibrium compensation from a one-time correction of underpricing, since a single cross-section is consistent with both. We therefore turn to the dynamics of the premium. If the low-MAX $^{\beta}$ premium is a compensation demanded for the underdiversification of holding low-skewness assets, investors are paid for as long as they hold the exposure, and the premium should endure; if the MAX effect is mispricing, by contrast, the overpricing of high-MAX stocks corrects once, and the associated abnormal return

42

---

# Page 44

should be a transient phenomenon of the first few months after portfolio formation. The question we pose is therefore whether the abnormal return continues to accrue over long holding periods, that is, whether it is earned repeatedly for as long as the position is held or only once at formation. This is distinct from the question examined in Section 5.5, which asks whether the $\text{MAX}^{\beta}$ effect depends on sustained past rankings; here the object of interest is the horizon profile of the return itself, not its dependence on the history of the sorting variable.

A direct test of durability must address a subtle feature of the sorting variable, and recognizing this feature is what gives the test its discriminating power. Both measures are built on the maximum daily return: MAX is the average of a stock’s five highest daily returns in the previous month, and $\text{MAX}^{\beta}$ is its beta-neutralized counterpart, ranked on MAX within beta deciles (Section 3.2). An extreme monthly maximum is close to the definition of a transient characteristic, since a month’s extreme daily returns are unlikely to recur, so a stock in the top MAX or $\text{MAX}^{\beta}$ decile this month is unlikely to remain there next month, and a buy-and-hold high-MAX or high- $\text{MAX}^{\beta}$ short leg sheds its lottery character within a month or two. The decay of either short-leg abnormal return is therefore over-determined, since a one-time mispricing correction and the mechanical staleness of the sorting variable predict the same decay and are observationally indistinguishable in the short-leg profile. For this reason we rest no part of the durability test on the short legs. The long legs are different in kind. A low maximum daily return, whether raw or beta-neutralized, is a property of stable, low-volatility stocks, and volatility clusters, so low-volatility firms remain low-volatility; low MAX and low $\text{MAX}^{\beta}$ are therefore persistent characteristics, not transient ones. A low-MAX or low- $\text{MAX}^{\beta}$ portfolio held without rebalancing accordingly retains its composition, and hence its exposure, far longer than the corresponding high-decile short leg retains its, so the staleness confound is largely absent. The long-leg profile is thus a clean test for either measure, and it poses a well-defined question: given that the exposure persists, does the abnormal return endure with it, or does it appear once and stop?

To measure the abnormal return as a function of holding horizon, we adopt the calendar-

43

---

# Page 45

time overlapping-portfolio methodology of Jegadeesh and Titman (1993), following the recommendation of Fama (1998) for long-horizon inference. Each leg is a value-weighted portfolio of its constituent stocks, as throughout the paper. For a holding horizon of $K$ months, we form the strategy anew each month and hold each cohort for $K$ months without rebalancing; in each calendar month we hold the $K$ most recently formed cohorts and take the average of their returns, each cohort receiving weight $1/K$ , which yields a single monthly return series for the $K$ -month strategy. We regress this series on the FF6PS factors to obtain a per-month alpha, $\alpha_K$ , with a single, well-specified Newey and West (1987) standard error at a fixed six-month lag, and we report the cumulative abnormal return over the holding period as $\text{CR}(K) = K \cdot \alpha_K$ . $^{12}$ We conduct the analysis for the MAX and MAX $^\beta$ long-short strategies and, separately, for each of their four legs.

– Table 12 and Figure 1 around here –

Table 12 reports the results. The two strategies decay very differently. The MAX strategy earns a significant alpha only at the shortest horizons, 0.61% per month at a one-month holding (t-stat. = 3.00) and 0.36% at two months (t-stat. = 2.19), after which it is statistically indistinguishable from zero and, by a two-year holding, slightly negative ( $-0.01\%$ , t-stat. = $-0.07$ ). The MAX effect is, in this precise sense, a one-to-two-month phenomenon: it corrects, and it is gone. The MAX $^\beta$ strategy behaves altogether differently, earning a positive and significant alpha out to a holding horizon of roughly one year (0.20% per month at twelve months, t-stat. = 2.05) and remaining economically large, though more weakly significant, thereafter. The cumulative abnormal returns make the contrast plain: over a two-year holding, the MAX $^\beta$ strategy accumulates 2.76%, against essentially nothing for MAX, whose cumulative abnormal return rises to roughly 0.8% within the first several months and then fades to essentially zero, marginally negative by

$^{12}$ Because the calendar-time portfolio collapses the overlapping cohorts into a single monthly return series, the mechanical autocorrelation induced by overlapping holding periods is absorbed into the portfolio rather than left in the time series, so a short, fixed Newey-West lag is appropriate at every horizon. This construction is preferable to compounding separately estimated monthly alphas, which produces a cumulative statistic whose standard error must account for the covariances across horizons and which inherits the poor properties of long-horizon buy-and-hold abnormal returns (Fama, 1998; Mitchell and Stafford, 2000).

44

---

# Page 46

two years, the hump-shaped profile of a correction rather than of an ongoing premium (Panel A of Figure 1).

The decomposition into legs locates the durability unambiguously in the long leg. As anticipated, the two short legs decay quickly: the high-MAX leg carries a significant negative alpha only at the one- and two-month horizons ( $-0.54\%$ and $-0.26\%$ , with t-statistics of $-3.29$ and $-2.03$ ), and the high-MAX $^\beta$ leg fades within a few months. The decisive quantity is the low-MAX $^\beta$ leg, which earns a positive and statistically significant alpha at every one of the twenty-four monthly horizons (Table 12 lists representative horizons and Figure 1 plots the full profile), declining only modestly from $0.23\%$ per month (t-stat. = 3.08) to $0.11\%$ (t-stat. = 2.21) and accumulating $2.68\%$ over two years. As Panel B of Figure 1 shows, the cumulative abnormal return of the low-MAX $^\beta$ leg rises steadily throughout the two-year window, whereas those of the short legs are flat or mean-reverting. The long-leg premium is not concentrated at formation; rather, it is earned in every month of the holding period, which is the signature of an ongoing compensation and not of a corrected mistake.

Two features of the evidence rule out the most natural alternative explanations. First, the durability of the low-MAX $^\beta$ premium cannot be a mechanical consequence of the portfolio remaining low-skew, because a corrected underpricing would earn nothing further once the price is fair, regardless of whether the characteristic persists: persistence of the characteristic is necessary for the abnormal return to endure, but it is not sufficient to produce it, and ongoing alpha conditional on a persistent exposure is exactly what distinguishes an equilibrium price from a corrected mistake. Second, and crucially, the durable long-leg premium is specific to the beta-neutralized measure. When we repeat the exercise for the long leg of the original MAX sort, the low-MAX (decile 1) portfolio earns an alpha that is statistically indistinguishable from zero at every horizon, for instance $0.07\%$ at one month (t-stat. = 0.87) and $0.04\%$ at two years (t-stat. = 0.80). It is not, therefore, that lottery sorts generically generate a durable long leg; rather, it is that neutralizing market beta, in the construction of Section 3.2, isolates a skewness exposure that earns an ongoing equilibrium premium, a premium that the original, beta-contaminated MAX

45

---

# Page 47

measure does not durably possess.

Taken together with the cross-sectional evidence of Section 6.2, these long-horizon results complete the economic account of the $\text{MAX}^{\beta}$ anomaly. The long-leg premium is earned by the institutions who accumulate low-skewness stocks, it scales with the intensity of their accumulation, and it endures for as long as the exposure is held. This is the empirical signature of the compensation that skewness-neutral, underdiversification-averse institutions demand in the equilibrium of Mitton and Vorkink (2007), and it stands in sharp contrast to the transient, retail-driven overpricing that constitutes the original MAX effect, whose abnormal performance concentrates in high-sentiment and high-issuance states (Section 5.6).

## 6.4 Disentangling the MAX and $\text{MAX}^{\beta}$ Anomalies through Firm Characteristics

Having traced the clientele mechanism through the portfolio sorts of Sections 6.1 and 6.2 and confirmed its durability across horizons in Section 6.3, we now disentangle it from the competing explanations of mispricing and equity issuance in a single multivariate framework. This section employs Fama and MacBeth (1973) cross-sectional regressions to examine the characteristics of portfolios sorted on MAX and $\text{MAX}^{\beta}$ .

Our methodology begins by sorting stocks into 25 portfolios based on their monthly MAX (Panel A) and $\text{MAX}^{\beta}$ (Panel B) values. $^{13}$ We use portfolios for the MAX sort to ensure comparability with $\text{MAX}^{\beta}$ , which is a portfolio-level measure. We then construct a categorical dependent variable, $Y_{p,t}$ , which equals 1 for portfolios in the top quintile (high $\text{MAX}/\text{MAX}^{\beta}$ ), $-1$ for portfolios in the bottom quintile (low $\text{MAX}/\text{MAX}^{\beta}$ ), and 0 for portfolios in the intermediate quintiles. This specification focuses on the extreme quintiles, which are the primary drivers of both anomalies. The MAX effect is concentrated in the underperformance of high-MAX stocks (as shown in Table 1), whereas the $\text{MAX}^{\beta}$

$^{13}$ While our preceding analyses rely on decile sorts, we employ 25 portfolios in this section to facilitate a more granular estimation of $\text{MAX}^{\beta}$ . This finer sorting is crucial for more effectively isolating the lottery preference component of MAX from its systematic risk exposure and for establishing a cleaner link with the portfolios’ underlying firm characteristics.

46

---

# Page 48

effect involves both the underperformance of high-MAX $^{\beta}$ stocks and the outperformance of low-MAX $^{\beta}$ stocks (as shown in Table 6).

For each of the 25 portfolios, we compute contemporaneous value-weighted averages of several key characteristics: mispricing score (MIS), composite equity issuance index (Issuance), expected idiosyncratic skewness (E(ISKEW)), and institutional ownership (INST). We also include a standard set of control variables: market capitalization (SIZE), book-to-market ratio (BM), return-on-equity (ROE), annual total asset growth (I/A), and intermediate-term momentum (MOM). We then estimate monthly cross-sectional regressions of the following form:

$$
Y_{p,t} = \lambda_{0,t} + \lambda_{1,t} \cdot X_{p,t} + \epsilon_{p,t},
$$

where $Y_{p,t}$ is the categorical variable for portfolio $p$ in month $t$ , and $X_{p,t}$ is the vector of its associated value-weighted characteristics. Table 13 reports the time-series averages of the estimated slope coefficients ( $\lambda_{1,t}$ ) for the sample period from April 1980 to December 2022. $^{14}$

– Table 13 around here –

Panel A of Table 13 shows that the MAX characteristic is significantly and positively related to the mispricing score (MIS) and equity issuance, but insignificantly related to expected idiosyncratic skewness, E(ISKEW). The relationship with institutional ownership (INST) is sensitive to the model specification, and the positive associations with mispricing and issuance are robust to the inclusion of standard control variables. In contrast, the analysis for MAX $^{\beta}$ presented in Panel B reveals crucial differences. In the MAX $^{\beta}$ regressions, the coefficient on E(ISKEW) becomes significantly positive, while the coefficient on INST is significantly negative. Furthermore, once the standard controls are included, the coefficients on MIS and Issuance are of diminished economic and statistical significance relative to the MAX regressions. This evidence provides the first layer of support for our central thesis that the original MAX effect is primarily a manifestation

$^{14}$ We select this sample period as it represents the broadest timeframe for which all firm characteristics used in our analysis are concurrently available.

47

---

# Page 49

of mispricing, whereas the newly proposed $\text{MAX}^{\beta}$ anomaly captures a distinct economic phenomenon rooted in the skewness preferences of heterogeneous investor clienteles.

The subsample analysis in Table A9 of the Appendix lends further support to this interpretation, directly linking these findings to the heterogeneous investor clienteles identified in Section 6.1. The table replicates the regressions from Table 13 separately for stocks with high (top tercile) and low (bottom tercile) institutional ownership. For the retail-dominated, low-INST subsample (Panel B), the link between MAX and skewness is statistically weak, whereas the association for $\text{MAX}^{\beta}$ is consistently positive and significant. This aligns with our earlier finding that the $\text{MAX}^{\beta}$ anomaly is strongest among “lotto investors,” whose demand for lottery-like payoffs creates a robust positive relationship between high- $\text{MAX}^{\beta}$ and skewness. Conversely, among stocks with high institutional ownership (Panel A), the relationship between MAX and skewness becomes negative in the multivariate specification, while the $\text{MAX}^{\beta}$ -skewness link remains positive. This divergence is consistent with the evidence from Table 9, which shows that institutions drive the $\text{MAX}^{\beta}$ anomaly through the outperformance of low-skew (low- $\text{MAX}^{\beta}$ ) stocks, for which they demand a return premium. Taken together, the contrasting results for MAX and $\text{MAX}^{\beta}$ across investor clienteles provide compelling evidence that $\text{MAX}^{\beta}$ , unlike MAX, is uniquely and robustly tied to the pricing of skewness preferences in a market with heterogeneous investors.

In sum, the cross-sectional regression analysis provides a clear distinction between the economic underpinnings of the MAX and $\text{MAX}^{\beta}$ anomalies. The MAX anomaly is consistently associated with firm-level characteristics related to mispricing. In contrast, the $\text{MAX}^{\beta}$ anomaly is robustly linked to characteristics that proxy for heterogeneous investor preferences for skewness, with its pricing dynamics varying predictably across different investor clienteles. This formal disentanglement solidifies our central thesis: MAX is predominantly a manifestation of mispricing, while $\text{MAX}^{\beta}$ represents a separate, skewness-based phenomenon.

48

---

# Page 50

# 7 Robustness Analyses and Extensions

Having identified the economic drivers of the $\text{MAX}^{\beta}$ phenomenon, we subject the strategy to a battery of robustness tests and extensions, which we summarize here and document in full in the Internet Appendix. First, the profitability of $\text{MAX}^{\beta}$ is not an artifact of small or illiquid stocks: the long-short strategy earns significant FF6PS alphas across subsamples screened by market capitalization, share price, and Amihud (2002) liquidity, including within the 500 most liquid stocks, and, consistent with Mitton and Vorkink (2007), the source of the spread shifts from the short (high- $\text{MAX}^{\beta}$ ) leg in retail-dominated segments to the long (low- $\text{MAX}^{\beta}$ ) leg in institution-dominated segments (Internet Appendix Table A10). Second, the strategy’s performance is not compensation for tail risk: its absolute Sharpe ratio exceeds that of the original MAX strategy and of every Fama-French characteristic other than momentum, and it delivers higher returns per unit of downside risk measured by Value-at-Risk and Expected Shortfall (Table A11). Third, the beta-neutralization is not specific to MAX: applying the same procedure to the lottery index of Kumar (2009), to MAX(1), and to the right-tail measures MAX(95%) and MAX(99%) produces beta-neutralized strategies that earn significant abnormal returns on both legs (Table A12).

Finally, we complement the portfolio-level evidence with a stock-level proxy, $\text{MAX}^{\text{Treynor}}$ , defined as MAX divided by the stock’s market beta. In firm-level Fama-MacBeth (1973) regressions, the average slope on $\text{MAX}^{\text{Treynor}}$ is negative and significant and, because the proxy is beta-neutralized, it is essentially unaffected by the mispricing score and composite equity issuance that absorb the original MAX effect (Tables A12 and A13). Taken together, these results confirm that $\text{MAX}^{\beta}$ is not a fragile, sample-specific regularity; rather, it captures a pricing phenomenon that is robust across market segments, risk-adjusted benchmarks, alternative lottery proxies, and construction methods.

49

---

# Page 51

# 8 Conclusion

The MAX anomaly, widely read as evidence of investor demand for lottery-like securities, has been a prominent finding in asset pricing. We provide a comprehensive re-examination and find that this interpretation is incomplete: the original MAX measure is a noisy proxy for lottery preferences, because its predictive power is intertwined with persistent mispricing, managerial issuance, and systematic risk.

Three results challenge the standard view. The MAX anomaly is fully explained by modern mispricing factor models, particularly those related to equity issuance; its predictive power is strictly conditional on the persistence of a stock’s prior extreme returns, a property at odds with the unpredictable nature of a lottery; and it is confounded by market beta, differing in strength and character between high- and low-beta stocks. The original MAX anomaly is therefore better understood as a manifestation of sustained overvaluation that managers exploit through equity issuance, and not as a direct consequence of transient, lottery-seeking behavior.

To isolate a cleaner proxy, we propose $\text{MAX}^{\beta}$ , which purges the systematic component of extreme daily returns. The resulting anomaly is robust to the risk and mispricing factors that explain the original effect, is invariant to the aggregate issuance regime, and, crucially, does not depend on the persistence of past performance. These properties establish $\text{MAX}^{\beta}$ as a conceptually sounder measure of the appetite for lottery-like payoffs. Its economic origin lies in heterogeneous skewness preferences. The anomaly is strongest among low-institutional-ownership stocks, and its source shifts across clienteles: in retail-dominated stocks it reflects the overpricing of high- $\text{MAX}^{\beta}$ names by skewness-loving retail investors, whereas in institution-dominated stocks it reflects the premium institutions require to hold low-skewness ones, as in Mitton and Vorkink (2007). We identify this equilibrium directly, through two findings. First, the low- $\text{MAX}^{\beta}$ premium is earned in every month for as long as the exposure is held, rather than corrected once; this is what an equilibrium compensation looks like and a mispricing does not. Second, the premium accrues to the low- $\text{MAX}^{\beta}$ stocks that institutions are actively accumulating, with its

50

---

# Page 52

mirror in the lottery stocks flowing to retail; this two-sided flow is what gives the anomaly its arbitrage symmetry. Finally, the beta-neutralization behind $\text{MAX}^{\beta}$ is a general device: applied to other lottery proxies, it isolates their idiosyncratic component in the same way, and is available for studying the pricing of skewness beyond MAX.

These findings imply that the demand for lottery-like stocks is real and priceable, but that the original MAX measure conflates it with mispricing. A predictor widely treated as the canonical proxy for lottery preferences, and among the strongest features in return-forecasting models, is therefore better understood as a manifestation of mispricing. Once the preference is isolated, it reveals a two-sided equilibrium in which idiosyncratic skewness is priced by heterogeneous clienteles. This is an equilibrium outcome of who holds and who accumulates which stocks, not a behavioral anomaly awaiting correction. $\text{MAX}^{\beta}$ offers a cleaner instrument for studying the preference and, as a new and unexplained anomaly, poses a fresh challenge for asset pricing models and for research on the pricing of idiosyncratic skewness.

51

---

# Page 53

# References

Agarwal, V., W. Jiang, and Q. Wen. 2022. Why do mutual funds hold lottery stocks? Journal of Financial Economics, 143, 352–375.

Amihud, Y. 2002. Illiquidity and stock returns: Cross-section and time-series effects. Journal of Financial Markets, 5, 31–56.

Annaert, J., M. De Ceuster, and K. Verstegen. 2013. Are extreme returns priced in the stock market? European evidence. Journal of Banking and Finance, 37, 3401–3411.

Arditti, F. 1967. Risk and the required return on equity. Journal of Finance, 22, 19–36.

Atilgan, Y., T. Bali, O. Demirtas, and D. Gunaydin. 2020. Left-tail momentum: Underreaction to bad news, costly arbitrage and equity returns. Journal of Financial Economics, 135, 725–775.

Baker, M., and J. Wurgler. 2000. The equity share in new issues and aggregate stock returns. Journal of Finance, 55, 2219–2257.

Baker, M., and J. Wurgler. 2006. Investor sentiment and the cross-section of stock returns. Journal of Finance, 61, 1645–1680.

Baker, M., and J. Wurgler. 2020. Market efficiency, market anomalies, and behavioral finance. Handbook of the Economics of Finance, Vol. 2, 577–652.

Bali, T., S. Brown, S. Murray, and Y. Tang. 2017. A lottery-demand-based explanation of the beta anomaly. Journal of Financial and Quantitative Analysis, 52, 2369–2397.

Bali, T., N. Cakici, and R. Whitelaw. 2011. Maxing out: Stocks as lotteries and the cross-section of expected returns. Journal of Financial Economics, 99, 427–446.

Bali, T., D. Hirshleifer, L. Peng, Y. Tang, and Q. Wang. 2025. Social interactions and lottery stock mania. Working Paper.

Barberis, N., and M. Huang. 2008. Stocks as lotteries: The implications of probability weighting for security prices. American Economic Review, 98, 2066–2100.

Barberis, N., A. Mukherjee, and B. Wang. 2016. Prospect theory and stock returns: An empirical test. Review of Financial Studies, 29, 3068–3107.

Bordalo, P., Gennaioli, N., and Shleifer, A. 2012. Salience theory of choice under risk. Quarterly Journal of Economics, 127, 1243–1285.

Bordalo, P., Gennaioli, N., and Shleifer, A. 2013. Salience and asset prices. American Economic Review 103, 623–628.

Boyer, B., T. Mitton, and K. Vorkink. 2010. Expected idiosyncratic skewness. Review of Financial Studies, 23, 169–202.

Boyer, B., and K. Vorkink. 2014. Stock options as lotteries. Journal of Finance, 69, 1485–1527.

Brunnermeier, M., C. Gollier, and J. Parker. 2007. Optimal beliefs, asset prices, and the preference for skewed returns. American Economic Review, 97, 159–165.

Brunnermeier, M., and J. Parker. 2005. Optimal expectations. American Economic Review, 95, 1092–1118.

Campbell, J., J. Hilscher, and J. Szilagyi. 2008. In search of distress risk. Journal of Finance, 63, 2899–2939.

52

---

# Page 54

Carhart, M. 1997. On persistence in mutual fund performance. Journal of Finance, 52, 57–82.

Chan, L., N. Jegadeesh, and J. Lakonishok. 1996. Momentum strategies. Journal of Finance, 51, 1681–1713.

Chen, L., R. Novy-Marx, and L. Zhang. 2010. An alternative three-factor model. Journal of Finance, 65, 927–971.

Cheon, Y., and Y. Lee. 2018. Lottery preference and stock returns: International evidence. Pacific-Basin Finance Journal, 51, 163–179.

Conine, T., and M. Tamarkin. 1981. On diversification given asymmetry in returns. Journal of Finance, 36, 1143–1155.

Cooper, M., H. Gulen, and M. Schill. 2008. Asset growth and the cross-section of stock returns. Journal of Finance, 63, 1609–1651.

Daniel, K., D. Hirshleifer, and L. Sun. 2020. Short- and long-horizon behavioral factors. Review of Financial Studies, 33, 1673–1736.

Daniel, K., and S. Titman. 2006. Market reactions to tangible and intangible information. Journal of Finance, 61, 1605–1643.

Fama, E. 1998. Market efficiency, long-term returns, and behavioral finance. Journal of Financial Economics, 49, 283–306.

Fama, E., and K. French. 1993. Common risk factors in the returns on stocks and bonds. Journal of Financial Economics, 33, 3–56.

Fama, E., and K. French. 2008. Dissecting anomalies. Journal of Finance, 63, 1653–1678.

Fama, E., and K. French. 2015. A five-factor asset pricing model. Journal of Financial Economics, 116, 1–22.

Fama, E., and K. French. 2018. Choosing factors. Journal of Financial Economics, 128, 234–252.

Fama, E., and J. MacBeth. 1973. Risk, return, and equilibrium: Empirical tests. Journal of Political Economy, 81, 607–636.

Frazzini, A., and L. Pedersen. 2014. Betting against beta. Journal of Financial Economics, 111, 1–25.

Green, T., and B. Hwang. 2012. IPOs as lotteries: Skewness preference and first-day returns. Management Science, 58, 432–444.

Gu, S., B. Kelly, and D. Xiu. 2020. Empirical asset pricing via machine learning. Review of Financial Studies, 33, 2223–2273.

Han, B., and A. Kumar. 2013. Speculative retail trading and asset prices. Journal of Financial and Quantitative Analysis, 48, 377–404.

Han, B., D. Hirshleifer, and J. Walden. 2022. Social transmission bias and investor behavior. Journal of Finance, 77, 1693–1735.

Harvey, C., and A. Siddique. 2000. Conditional skewness in asset pricing tests. Journal of Finance, 55, 1263–1295.

Hirshleifer, D., K. Hou, S. Teoh, and Y. Zhang. 2004. Do investors overvalue firms with bloated balance sheets? Journal of Accounting and Economics, 38, 297–331.

Hou, K., and R. Loh. 2016. Have we solved the idiosyncratic volatility puzzle? Journal of Financial Economics, 121, 167–194.

53

---

# Page 55

Hou, K., C. Xue, and L. Zhang. 2015. Digesting anomalies: An investment approach. Review of Financial Studies, 28, 650–705.

Jegadeesh, N. 1990. Evidence of predictable behavior of security returns. Journal of Finance, 45, 881–898.

Jegadeesh, N., and S. Titman. 1993. Returns to buying winners and selling losers. Journal of Finance, 48, 65–91.

Kahneman, D., and A. Tversky. 1979. Prospect theory: An analysis of decision under risk. Econometrica, 47, 263–292.

Kraus, A., and R. Litzenberger. 1976. Skewness preference and the valuation of risk assets. Journal of Finance, 31, 1085–1100.

Kumar, A. 2009. Who gambles in the stock market? Journal of Finance, 64, 1889–1933.

Lo, A. 2002. The statistics of Sharpe ratios, Financial Analysts Journal, 58, 36–52.

Loughran, T., and J. Ritter. 1995. The new issues puzzle. Journal of Finance, 50, 23–51.

McLean, R., and J. Pontiff. 2016. Does academic research destroy stock return predictability? Journal of Finance, 71, 5–32.

Mitchell, M., and E. Stafford. 2000. Managerial decisions and long-term stock price performance. Journal of Business, 73, 287–329.

Mitton, T., and K. Vorkink. 2007. Equilibrium underdiversification and the preference for skewness. Review of Financial Studies, 20, 1255–1288.

Nagel, S. 2005. Short sales, institutional investors and the cross-section of stock returns. Journal of Financial Economics, 78, 277–309.

Newey, W., and K. West. 1987. A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. Econometrica, 55, 703–708.

Newey, W., and K. West. 1994. Automatic lag length selection in covariance matrix estimation. Review of Economic Studies, 61, 631–653.

Novy-Marx, R. 2013. The other side of value: The gross profitability premium. Journal of Financial Economics, 108, 1–28.

Ohlson, J. 1980. Financial ratios and the probabilistic prediction of bankruptcy. Journal of Accounting Research, 18, 109–131.

Pastor, L., and R. Stambaugh. 2003. Liquidity risk and expected stock returns. Journal of Political Economy, 111, 642–685.

Pontiff, J., and A. Woodgate. 2008. Share issuance and cross-sectional stock returns. Journal of Finance, 63, 921–945.

Ritter, J. 2008. Forensic finance. Journal of Economic Perspectives, 22, 127–147.

Shleifer, A., and R. Vishny. 1997. The limits of arbitrage. Journal of Finance, 52, 35–55.

Simkowitz, M., and W. Beedles. 1978. Diversification in a three-moment world. Journal of Financial and Quantitative Analysis, 13, 927–941.

Sloan, R. 1996. Do stock prices fully reflect information in accruals and cash flows about future earnings? Accounting Review, 71, 289–315.

Stambaugh, R., and Y. Yuan. 2017. Mispricing factors. Review of Financial Studies, 30, 1270–1315.

54

---

# Page 56

Stambaugh, R., J. Yu, and Y. Yuan. 2012. The short of it: Investor sentiment and anomalies. Journal of Financial Economics, 104, 288–302.

Stambaugh, R., J. Yu, and Y. Yuan. 2014. The long of it: Investor sentiment and anomalies. Journal of Financial Economics, 114, 272–285.

Stambaugh, R., J. Yu, and Y. Yuan. 2015. Arbitrage asymmetry and the idiosyncratic volatility puzzle. Journal of Finance, 70, 1903–1948.

Titman, S., K. Wei, and F. Xie. 2004. Capital investments and stock returns. Journal of Financial and Quantitative Analysis, 39, 677–700.

Tran, L. T., Wardle, H., Colledge-Frisby, S., Taylor, S., Lynch, M., Rehm, J., Volberg, R., Marionneau, V., Saxena, S., Bunn, C., Farrell, M., and Degenhardt, L. 2024. The prevalence of gambling and problematic gambling: a systematic review and meta-analysis. Lancet Public Health, 9, 594-613.

Tversky, A., and D. Kahneman. 1992. Advances in prospect theory: Cumulative representation of uncertainty. Journal of Risk and Uncertainty, 5, 297–323.

Walkshausl, C. 2014. The lottery effect in international stock markets. Journal of Banking and Finance, 48, 51–71.

Xing, Y. 2008. Interpreting the value effect through the Q-theory: An empirical investigation. Review of Financial Studies, 21, 1767–1795.

55

---

# Page 57

Table 1

**Univariate sorts on MAX**: This table reports the performance of decile portfolios constructed monthly by sorting stocks based on MAX, defined as the average of the five highest daily returns within a month. Portfolio 1 contains stocks with the lowest MAX, while Portfolio 10 contains stocks with the highest MAX. The reported values are value-weighted average one-month-ahead excess returns (RET – RF), as well as alphas from risk-adjusted models (CAPM, FF3, FFC4, FFCPS, FF5, FF6, and FF6PS) and mispricing-adjusted models (SY and DHS). The final row displays the differences (spreads) in average monthly returns and alphas between Portfolio 10 and Portfolio 1. Newey and West (1987) $t$-statistics (adjusted with six lags) are reported in parentheses. The sample period spans January 1968 to December 2022, with the exception of the DHS analysis, which begins in July 1972.

<table>
  <thead>
    <tr>
      <th>Decile</th>
      <th>RET-RF</th>
      <th>CAPM</th>
      <th>FF3</th>
      <th>FFC4</th>
      <th>FFCPS</th>
      <th>FF5</th>
      <th>FF6</th>
      <th>FF6PS</th>
      <th>SY</th>
      <th>DHS</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 1</td>
      <td>0.63<br>(3.99)</td>
      <td>0.24<br>(3.22)</td>
      <td>0.19<br>(2.57)</td>
      <td>0.19<br>(2.26)</td>
      <td>0.20<br>(2.38)</td>
      <td>0.05<br>(0.71)</td>
      <td>0.06<br>(0.76)</td>
      <td>0.07<br>(0.87)</td>
      <td>-0.00<br>(-0.03)</td>
      <td>0.11<br>(1.20)</td>
    </tr>
    <tr>
      <td>2</td>
      <td>0.67<br>(4.04)</td>
      <td>0.21<br>(3.17)</td>
      <td>0.19<br>(2.94)</td>
      <td>0.17<br>(2.58)</td>
      <td>0.16<br>(2.51)</td>
      <td>0.04<br>(0.69)</td>
      <td>0.04<br>(0.63)</td>
      <td>0.03<br>(0.52)</td>
      <td>-0.01<br>(-0.24)</td>
      <td>0.08<br>(1.10)</td>
    </tr>
    <tr>
      <td>3</td>
      <td>0.60<br>(3.46)</td>
      <td>0.11<br>(1.79)</td>
      <td>0.11<br>(1.81)</td>
      <td>0.12<br>(1.95)</td>
      <td>0.11<br>(1.81)</td>
      <td>0.01<br>(0.05)</td>
      <td>0.02<br>(0.36)</td>
      <td>0.01<br>(0.22)</td>
      <td>0.00<br>(0.00)</td>
      <td>0.01<br>(0.16)</td>
    </tr>
    <tr>
      <td>4</td>
      <td>0.54<br>(2.75)</td>
      <td>0.01<br>(0.18)</td>
      <td>0.02<br>(0.32)</td>
      <td>0.05<br>(0.69)</td>
      <td>0.03<br>(0.46)</td>
      <td>-0.04<br>(-0.57)</td>
      <td>-0.01<br>(-0.21)</td>
      <td>-0.03<br>(-0.49)</td>
      <td>-0.04<br>(-0.60)</td>
      <td>0.01<br>(0.04)</td>
    </tr>
    <tr>
      <td>5</td>
      <td>0.60<br>(2.97)</td>
      <td>0.01<br>(0.20)</td>
      <td>0.02<br>(0.31)</td>
      <td>0.04<br>(0.51)</td>
      <td>0.02<br>(0.29)</td>
      <td>0.05<br>(0.69)</td>
      <td>0.07<br>(0.75)</td>
      <td>0.05<br>(0.55)</td>
      <td>0.07<br>(0.81)</td>
      <td>0.10<br>(1.03)</td>
    </tr>
    <tr>
      <td>6</td>
      <td>0.60<br>(2.62)</td>
      <td>-0.01<br>(-0.18)</td>
      <td>0.06<br>(0.80)</td>
      <td>0.06<br>(0.77)</td>
      <td>0.04<br>(0.53)</td>
      <td>0.13<br>(1.75)</td>
      <td>0.12<br>(1.59)</td>
      <td>0.11<br>(1.35)</td>
      <td>0.18<br>(2.14)</td>
      <td>0.20<br>(2.48)</td>
    </tr>
    <tr>
      <td>7</td>
      <td>0.53<br>(1.96)</td>
      <td>-0.16<br>(-1.31)</td>
      <td>-0.05<br>(-0.54)</td>
      <td>-0.06<br>(-0.68)</td>
      <td>-0.07<br>(-0.78)</td>
      <td>0.07<br>(0.74)</td>
      <td>0.05<br>(0.55)</td>
      <td>0.04<br>(0.39)</td>
      <td>0.16<br>(1.54)</td>
      <td>0.05<br>(0.50)</td>
    </tr>
    <tr>
      <td>8</td>
      <td>0.41<br>(1.43)</td>
      <td>-0.35<br>(-2.76)</td>
      <td>-0.25<br>(-2.03)</td>
      <td>-0.24<br>(-2.08)</td>
      <td>-0.25<br>(-2.15)</td>
      <td>-0.05<br>(-0.48)</td>
      <td>-0.05<br>(-0.56)</td>
      <td>-0.07<br>(-0.64)</td>
      <td>0.05<br>(0.50)</td>
      <td>0.07<br>(0.60)</td>
    </tr>
    <tr>
      <td>9</td>
      <td>0.22<br>(0.66)</td>
      <td>-0.59<br>(-3.25)</td>
      <td>-0.38<br>(-2.85)</td>
      <td>-0.34<br>(-2.68)</td>
      <td>-0.35<br>(-2.75)</td>
      <td>-0.08<br>(-0.74)</td>
      <td>-0.07<br>(-0.63)</td>
      <td>-0.08<br>(-0.71)</td>
      <td>0.09<br>(0.68)</td>
      <td>0.16<br>(1.06)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-0.32<br>(-0.85)</td>
      <td>-1.17<br>(-5.08)</td>
      <td>-0.97<br>(-5.34)</td>
      <td>-0.88<br>(-4.62)</td>
      <td>-0.91<br>(-4.85)</td>
      <td>-0.54<br>(-3.59)</td>
      <td>-0.51<br>(-3.06)</td>
      <td>-0.54<br>(-3.29)</td>
      <td>-0.27<br>(-1.56)</td>
      <td>-0.21<br>(-1.07)</td>
    </tr>
    <tr>
      <td>10-1 difference</td>
      <td>-0.95<br>(-3.08)</td>
      <td>-1.41<br>(-5.17)</td>
      <td>-1.16<br>(-5.35)</td>
      <td>-1.07<br>(-4.63)</td>
      <td>-1.11<br>(-4.81)</td>
      <td>-0.59<br>(-3.25)</td>
      <td>-0.57<br>(-2.80)</td>
      <td>-0.61<br>(-3.00)</td>
      <td>-0.27<br>(-1.29)</td>
      <td>-0.32<br>(-1.34)</td>
    </tr>
  </tbody>
</table>

---

# Page 58

Table 2

**Summary statistics for decile portfolios of stocks sorted by MAX**: This table reports summary statistics for decile portfolios constructed monthly by sorting stocks based on MAX, defined as the average of the five highest daily returns within a month. Portfolio 1 (10) contains stocks with the lowest (highest) MAX. The reported values represent the time-series averages of the cross-sectional median values for the following firm-specific characteristics: MAX; market beta (BETA); the firm-level mispricing index of Stambaugh, Yu, and Yuan (2015) (MIS); composite equity issuance (CE), defined as the 12-month growth in equity market capitalization minus the 12-month cumulative stock return; the sensitivity of stock-level MAX to the market MAX estimated via 12-month rolling regressions ( $\beta^{MAX}$ ); institutional holdings (INST); the expected idiosyncratic skewness measure of Boyer et al. (2010) (E(ISKEW)); market capitalization (SIZE); idiosyncratic volatility (IVOL); book-to-market ratio (BM); excess monthly return during the portfolio formation month (REV); intermediate-term momentum (MOM); Amihud (2002) illiquidity (ILLIQ); return on equity (ROE); and asset growth (I/A). The final row displays the differences in the reported values for firm-specific characteristics between the highest (Portfolio 10) and lowest (Portfolio 1) MAX deciles, along with Newey and West (1987) $t$ -statistics (adjusted with six lags) in parentheses. The sample period spans April 1980 to December 2022 for INST and E(ISKEW), and January 1968 to December 2022 for all other characteristics.

<table>
  <thead>
    <tr>
      <th>Decile</th>
      <th>MAX</th>
      <th>BETA</th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>INST</th>
      <th>E(ISKEW)</th>
      <th>SIZE</th>
      <th>IVOL</th>
      <th>BM</th>
      <th>REV</th>
      <th>MOM</th>
      <th>ILLIQ</th>
      <th>ROE</th>
      <th>I/A</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 1</td>
      <td>0.010</td>
      <td>0.581</td>
      <td>44.07</td>
      <td>-0.020</td>
      <td>0.654</td>
      <td>0.543</td>
      <td>0.897</td>
      <td>1655</td>
      <td>1.628</td>
      <td>0.528</td>
      <td>-0.032</td>
      <td>0.127</td>
      <td>0.112</td>
      <td>0.128</td>
      <td>0.071</td>
    </tr>
    <tr>
      <td>2</td>
      <td>0.016</td>
      <td>0.759</td>
      <td>44.26</td>
      <td>-0.019</td>
      <td>0.780</td>
      <td>0.609</td>
      <td>0.809</td>
      <td>1267</td>
      <td>1.728</td>
      <td>0.492</td>
      <td>-0.021</td>
      <td>0.122</td>
      <td>0.072</td>
      <td>0.127</td>
      <td>0.079</td>
    </tr>
    <tr>
      <td>3</td>
      <td>0.020</td>
      <td>0.826</td>
      <td>45.35</td>
      <td>-0.015</td>
      <td>0.851</td>
      <td>0.619</td>
      <td>0.824</td>
      <td>901</td>
      <td>1.889</td>
      <td>0.491</td>
      <td>-0.013</td>
      <td>0.118</td>
      <td>0.081</td>
      <td>0.121</td>
      <td>0.085</td>
    </tr>
    <tr>
      <td>4</td>
      <td>0.023</td>
      <td>0.871</td>
      <td>46.37</td>
      <td>-0.011</td>
      <td>0.915</td>
      <td>0.613</td>
      <td>0.861</td>
      <td>688</td>
      <td>2.065</td>
      <td>0.498</td>
      <td>-0.006</td>
      <td>0.113</td>
      <td>0.105</td>
      <td>0.117</td>
      <td>0.90</td>
    </tr>
    <tr>
      <td>5</td>
      <td>0.027</td>
      <td>0.915</td>
      <td>47.52</td>
      <td>-0.007</td>
      <td>0.969</td>
      <td>0.600</td>
      <td>0.898</td>
      <td>533</td>
      <td>2.263</td>
      <td>0.498</td>
      <td>0.001</td>
      <td>0.110</td>
      <td>0.131</td>
      <td>0.112</td>
      <td>0.095</td>
    </tr>
    <tr>
      <td>6</td>
      <td>0.031</td>
      <td>0.955</td>
      <td>48.62</td>
      <td>-0.003</td>
      <td>1.032</td>
      <td>0.580</td>
      <td>0.946</td>
      <td>430</td>
      <td>2.483</td>
      <td>0.500</td>
      <td>0.008</td>
      <td>0.109</td>
      <td>0.167</td>
      <td>0.105</td>
      <td>0.099</td>
    </tr>
    <tr>
      <td>7</td>
      <td>0.035</td>
      <td>0.995</td>
      <td>49.95</td>
      <td>0.001</td>
      <td>1.081</td>
      <td>0.555</td>
      <td>1.007</td>
      <td>354</td>
      <td>2.713</td>
      <td>0.497</td>
      <td>0.018</td>
      <td>0.105</td>
      <td>0.227</td>
      <td>0.097</td>
      <td>0.103</td>
    </tr>
    <tr>
      <td>8</td>
      <td>0.042</td>
      <td>1.031</td>
      <td>51.29</td>
      <td>0.003</td>
      <td>1.152</td>
      <td>0.523</td>
      <td>1.071</td>
      <td>286</td>
      <td>2.979</td>
      <td>0.498</td>
      <td>0.034</td>
      <td>0.100</td>
      <td>0.303</td>
      <td>0.086</td>
      <td>0.104</td>
    </tr>
    <tr>
      <td>9</td>
      <td>0.051</td>
      <td>1.068</td>
      <td>52.92</td>
      <td>0.008</td>
      <td>1.210</td>
      <td>0.480</td>
      <td>1.139</td>
      <td>233</td>
      <td>3.320</td>
      <td>0.492</td>
      <td>0.062</td>
      <td>0.097</td>
      <td>0.434</td>
      <td>0.072</td>
      <td>0.102</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>0.071</td>
      <td>1.043</td>
      <td>55.11</td>
      <td>0.013</td>
      <td>1.200</td>
      <td>0.391</td>
      <td>1.287</td>
      <td>162</td>
      <td>4.033</td>
      <td>0.500</td>
      <td>0.148</td>
      <td>0.075</td>
      <td>0.879</td>
      <td>0.033</td>
      <td>0.085</td>
    </tr>
    <tr>
      <td>10-1</td>
      <td>0.061</td>
      <td>0.462</td>
      <td>11.04</td>
      <td>0.033</td>
      <td>0.546</td>
      <td>-0.152</td>
      <td>0.390</td>
      <td>-1493</td>
      <td>2.405</td>
      <td>-0.028</td>
      <td>0.180</td>
      <td>-0.052</td>
      <td>0.767</td>
      <td>-0.094</td>
      <td>0.013</td>
    </tr>
    <tr>
      <td>difference</td>
      <td>(41.78)</td>
      <td>(14.40)</td>
      <td>(21.69)</td>
      <td>(20.08)</td>
      <td>(5.26)</td>
      <td>(-14.98)</td>
      <td>(8.09)</td>
      <td>(-6.82)</td>
      <td>(30.89)</td>
      <td>(-1.44)</td>
      <td>(31.33)</td>
      <td>(-2.02)</td>
      <td>(7.97)</td>
      <td>(-10.89)</td>
      <td>(2.97)</td>
    </tr>
  </tbody>
</table>

---

# Page 59

Table 3

**Returns to mispricing-dependent MAX sorts**: This table reports value-weighted average one-month-ahead excess returns (RET – RF) and alphas (FF6PS) for portfolios formed using bivariate dependent sorts. Each month, stocks are sorted into five quintiles based on the composite mispricing score (MIS) of Stambaugh, Yu, and Yuan (2015). Within each mispricing quintile, stocks are subsequently sorted into decile portfolios based on MAX, defined as the average of the five highest daily returns within a month. The final row reports the spreads in average monthly returns and alphas between the highest (Portfolio 10) and lowest (Portfolio 1) MAX deciles within each mispricing quintile. Newey and West (1987) $t$-statistics (adjusted with six lags) are reported in parentheses. The sample period spans January 1968 to December 2022.

<table>
  <thead>
    <tr>
      <th rowspan="3"> $\mathcal{S}$ </th>
      <th rowspan="3">Decile</th>
      <th colspan="2">MIS 1</th>
      <th colspan="2">MIS 2</th>
      <th colspan="2">MIS 3</th>
      <th colspan="2">MIS 4</th>
      <th colspan="2">MIS 5</th>
    </tr>
    <tr>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="10"> $\mathcal{S}$ </td>
      <td>Port 1</td>
      <td>0.91</td>
      <td>0.28</td>
      <td>0.75</td>
      <td>0.11</td>
      <td>0.71</td>
      <td>0.18</td>
      <td>0.82</td>
      <td>0.22</td>
      <td>0.50</td>
      <td>0.01</td>
    </tr>
    <tr>
      <td></td>
      <td>(5.53)</td>
      <td>(2.51)</td>
      <td>(4.19)</td>
      <td>(0.86)</td>
      <td>(3.66)</td>
      <td>(1.65)</td>
      <td>(4.05)</td>
      <td>(1.80)</td>
      <td>(2.09)</td>
      <td>(0.04)</td>
    </tr>
    <tr>
      <td>2</td>
      <td>0.81</td>
      <td>0.09</td>
      <td>0.77</td>
      <td>0.09</td>
      <td>0.75</td>
      <td>0.17</td>
      <td>0.51</td>
      <td>0.01</td>
      <td>0.38</td>
      <td>-0.20</td>
    </tr>
    <tr>
      <td></td>
      <td>(4.45)</td>
      <td>(0.77)</td>
      <td>(4.50)</td>
      <td>(1.11)</td>
      <td>(3.91)</td>
      <td>(1.54)</td>
      <td>(2.27)</td>
      <td>(0.11)</td>
      <td>(1.52)</td>
      <td>(-1.60)</td>
    </tr>
    <tr>
      <td>3</td>
      <td>0.69</td>
      <td>-0.02</td>
      <td>0.73</td>
      <td>0.10</td>
      <td>0.66</td>
      <td>0.10</td>
      <td>0.48</td>
      <td>-0.04</td>
      <td>-0.05</td>
      <td>-0.45</td>
    </tr>
    <tr>
      <td></td>
      <td>(4.27)</td>
      <td>(-0.24)</td>
      <td>(4.01)</td>
      <td>(1.05)</td>
      <td>(3.08)</td>
      <td>(0.90)</td>
      <td>(2.07)</td>
      <td>(-0.32)</td>
      <td>(-0.20)</td>
      <td>(-3.50)</td>
    </tr>
    <tr>
      <td>4</td>
      <td>0.73</td>
      <td>0.02</td>
      <td>0.71</td>
      <td>0.03</td>
      <td>0.53</td>
      <td>-0.13</td>
      <td>0.67</td>
      <td>0.07</td>
      <td>-0.14</td>
      <td>-0.57</td>
    </tr>
    <tr>
      <td></td>
      <td>(4.18)</td>
      <td>(0.22)</td>
      <td>(3.85)</td>
      <td>(0.37)</td>
      <td>(2.49)</td>
      <td>(-1.29)</td>
      <td>(2.67)</td>
      <td>(0.47)</td>
      <td>(-0.47)</td>
      <td>(-3.70)</td>
    </tr>
    <tr>
      <td>5</td>
      <td>0.65</td>
      <td>-0.04</td>
      <td>0.75</td>
      <td>0.00</td>
      <td>0.72</td>
      <td>0.18</td>
      <td>0.32</td>
      <td>-0.24</td>
      <td>0.12</td>
      <td>-0.33</td>
    </tr>
    <tr>
      <td></td>
      <td>(3.32)</td>
      <td>(-0.40)</td>
      <td>(3.74)</td>
      <td>(0.03)</td>
      <td>(2.99)</td>
      <td>(1.20)</td>
      <td>(1.23)</td>
      <td>(-1.53)</td>
      <td>(0.35)</td>
      <td>(-1.97)</td>
    </tr>
    <tr>
      <td rowspan="10"> $\mathcal{S}$ </td>
      <td>6</td>
      <td>0.87</td>
      <td>0.13</td>
      <td>0.35</td>
      <td>-0.31</td>
      <td>0.87</td>
      <td>0.18</td>
      <td>0.39</td>
      <td>-0.12</td>
      <td>-0.26</td>
      <td>-0.42</td>
    </tr>
    <tr>
      <td></td>
      <td>(4.34)</td>
      <td>(1.03)</td>
      <td>(1.54)</td>
      <td>(-2.62)</td>
      <td>(3.49)</td>
      <td>(1.23)</td>
      <td>(1.41)</td>
      <td>(-0.88)</td>
      <td>(-0.78)</td>
      <td>(-2.19)</td>
    </tr>
    <tr>
      <td>7</td>
      <td>0.86</td>
      <td>0.06</td>
      <td>0.84</td>
      <td>0.21</td>
      <td>0.65</td>
      <td>0.12</td>
      <td>0.76</td>
      <td>0.20</td>
      <td>-0.37</td>
      <td>-0.75</td>
    </tr>
    <tr>
      <td></td>
      <td>(3.95)</td>
      <td>(0.42)</td>
      <td>(3.63)</td>
      <td>(1.36)</td>
      <td>(2.30)</td>
      <td>(0.80)</td>
      <td>(2.44)</td>
      <td>(1.23)</td>
      <td>(-0.98)</td>
      <td>(-3.74)</td>
    </tr>
    <tr>
      <td>8</td>
      <td>0.96</td>
      <td>0.34</td>
      <td>0.64</td>
      <td>-0.09</td>
      <td>0.58</td>
      <td>-0.04</td>
      <td>0.37</td>
      <td>-0.14</td>
      <td>-0.48</td>
      <td>-0.70</td>
    </tr>
    <tr>
      <td></td>
      <td>(4.10)</td>
      <td>(2.35)</td>
      <td>(2.32)</td>
      <td>(-0.65)</td>
      <td>(2.04)</td>
      <td>(-0.24)</td>
      <td>(1.16)</td>
      <td>(-0.78)</td>
      <td>(-1.29)</td>
      <td>(-4.10)</td>
    </tr>
    <tr>
      <td>9</td>
      <td>0.87</td>
      <td>0.20</td>
      <td>0.61</td>
      <td>0.07</td>
      <td>0.69</td>
      <td>0.20</td>
      <td>-0.02</td>
      <td>-0.34</td>
      <td>-0.49</td>
      <td>-0.73</td>
    </tr>
    <tr>
      <td></td>
      <td>(3.19)</td>
      <td>(1.22)</td>
      <td>(1.87)</td>
      <td>(0.39)</td>
      <td>(2.08)</td>
      <td>(1.00)</td>
      <td>(-0.06)</td>
      <td>(-1.85)</td>
      <td>(-1.22)</td>
      <td>(-3.76)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>1.01</td>
      <td>0.35</td>
      <td>0.45</td>
      <td>-0.03</td>
      <td>0.26</td>
      <td>-0.28</td>
      <td>0.02</td>
      <td>-0.26</td>
      <td>-1.15</td>
      <td>-1.16</td>
    </tr>
    <tr>
      <td></td>
      <td>(3.34)</td>
      <td>(1.70)</td>
      <td>(1.35)</td>
      <td>(-0.19)</td>
      <td>(0.68)</td>
      <td>(-1.26)</td>
      <td>(0.07)</td>
      <td>(-1.16)</td>
      <td>(-2.52)</td>
      <td>(-5.42)</td>
    </tr>
    <tr>
      <td rowspan="2"> $\mathcal{S}$ </td>
      <td>10-1</td>
      <td>0.10</td>
      <td>0.06</td>
      <td>-0.30</td>
      <td>-0.14</td>
      <td>-0.45</td>
      <td>-0.46</td>
      <td>-0.80</td>
      <td>-0.48</td>
      <td>-1.65</td>
      <td>-1.17</td>
    </tr>
    <tr>
      <td>difference</td>
      <td>(0.38)</td>
      <td>(0.27)</td>
      <td>(-1.08)</td>
      <td>(-0.64)</td>
      <td>(-1.56)</td>
      <td>(-1.72)</td>
      <td>(-2.47)</td>
      <td>(-1.74)</td>
      <td>(-4.42)</td>
      <td>(-4.20)</td>
    </tr>
  </tbody>
</table>

---

# Page 60

Table 4

**Fama-MacBeth (1973) regressions on MAX**: This table reports the results of firm-level Fama-MacBeth (1973) cross-sectional regressions of one-month-ahead excess stock returns on MAX and a set of control variables. MAX is defined as the average of the five highest daily returns within a month. The control variables include: the firm-level mispricing index of Stambaugh, Yu, and Yuan (2015) (MIS); composite equity issuance (CE), defined as the 12-month growth in market capitalization minus the 12-month cumulative stock return; market beta (BETA); the natural logarithm of market capitalization (SIZE); the natural logarithm of the book-to-market ratio (BM); excess monthly return during the portfolio formation month (REV); intermediate-term momentum (MOM); Amihud (2002) illiquidity (ILLIQ); return on equity (ROE); asset growth (I/A); and idiosyncratic volatility (IVOL). Newey and West (1987) $t$-statistics (adjusted with six lags) are reported in parentheses. The last row reports the average adjusted $R^2$. The sample period spans January 1968 to December 2022.

<table>
  <thead>
    <tr>
      <th>Variable</th>
      <th>(1)</th>
      <th>(2)</th>
      <th>(3)</th>
      <th>(4)</th>
      <th>(5)</th>
      <th>(6)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>MAX</td>
      <td>-0.210<br>(-6.15)</td>
      <td>-0.113<br>(-5.40)</td>
      <td>-0.163<br>(-5.35)</td>
      <td>-0.187<br>(-5.80)</td>
      <td>-0.106<br>(-5.11)</td>
      <td>-0.110<br>(-5.23)</td>
    </tr>
    <tr>
      <td>MIS</td>
      <td></td>
      <td></td>
      <td>-0.026<br>(-7.91)</td>
      <td></td>
      <td>-0.018<br>(-6.92)</td>
      <td></td>
    </tr>
    <tr>
      <td>CE</td>
      <td></td>
      <td></td>
      <td></td>
      <td>-0.017<br>(-4.43)</td>
      <td></td>
      <td>-0.009<br>(-4.88)</td>
    </tr>
    <tr>
      <td>BETA</td>
      <td></td>
      <td>0.203<br>(1.58)</td>
      <td></td>
      <td></td>
      <td>0.224<br>(1.77)</td>
      <td>0.206<br>(1.64)</td>
    </tr>
    <tr>
      <td>SIZE</td>
      <td></td>
      <td>-0.117<br>(-3.67)</td>
      <td></td>
      <td></td>
      <td>-0.126<br>(-4.00)</td>
      <td>-0.116<br>(-3.64)</td>
    </tr>
    <tr>
      <td>BM</td>
      <td></td>
      <td>0.091<br>(1.86)</td>
      <td></td>
      <td></td>
      <td>0.094<br>(1.92)</td>
      <td>0.088<br>(1.80)</td>
    </tr>
    <tr>
      <td>REV</td>
      <td></td>
      <td>-0.030<br>(-6.37)</td>
      <td></td>
      <td></td>
      <td>-0.031<br>(-6.63)</td>
      <td>-0.030<br>(-6.41)</td>
    </tr>
    <tr>
      <td>MOM</td>
      <td></td>
      <td>0.007<br>(4.93)</td>
      <td></td>
      <td></td>
      <td>0.005<br>(3.72)</td>
      <td>0.007<br>(4.95)</td>
    </tr>
    <tr>
      <td>ILLIQ</td>
      <td></td>
      <td>0.020<br>(0.70)</td>
      <td></td>
      <td></td>
      <td>0.012<br>(0.42)</td>
      <td>0.016<br>(0.57)</td>
    </tr>
    <tr>
      <td>ROE</td>
      <td></td>
      <td>0.414<br>(1.99)</td>
      <td></td>
      <td></td>
      <td>0.095<br>(0.46)</td>
      <td>0.331<br>(1.59)</td>
    </tr>
    <tr>
      <td>I/A</td>
      <td></td>
      <td>-0.717<br>(-7.46)</td>
      <td></td>
      <td></td>
      <td>-0.272<br>(-3.01)</td>
      <td>-0.614<br>(-6.36)</td>
    </tr>
    <tr>
      <td>IVOL</td>
      <td></td>
      <td>-0.217<br>(-4.20)</td>
      <td></td>
      <td></td>
      <td>-0.170<br>(-3.36)</td>
      <td>-0.201<br>(-3.91)</td>
    </tr>
    <tr>
      <td>Intercept</td>
      <td>0.013<br>(7.25)</td>
      <td>0.027<br>(5.64)</td>
      <td>0.025<br>(13.94)</td>
      <td>0.013<br>(6.90)</td>
      <td>0.035<br>(7.47)</td>
      <td>0.026<br>(5.50)</td>
    </tr>
    <tr>
      <td>$R^2$</td>
      <td>0.015</td>
      <td>0.075</td>
      <td>0.023</td>
      <td>0.020</td>
      <td>0.077</td>
      <td>0.076</td>
    </tr>
  </tbody>
</table>

---

# Page 61

# Table 5

## Double sorts on mispricing characteristics and MAX:

This table reports one-month-ahead alphas (FF6PS) for the value-weighted portfolios formed using dependent double sorts. Panel A uses decile portfolios based on individual mispricing characteristics: the anomalous characteristics of Stambaugh, Yu, and Yuan (2015) (excluding equity issuance components) and the post-earnings announcement drift (PEAD) measure of Daniel, Hirshleifer, and Sun (2020). For the double sort on ROA, the RMW factor is excluded from the FF6PS model to avoid redundancy in controlling for profitability. Panel B uses a stock-level equity issuance index. Specifically, stocks are independently assigned percentile ranks based on (i) changes in split-adjusted shares outstanding (Ritter, 2008; Loughran and Ritter, 1995; Fama and French, 2008); (ii) composite equity issuance, measured as the one-year growth in market capitalization minus the one-year equity return (Daniel and Titman, 2006); and (iii) the five-year composite share issuance (CSI) of Daniel and Titman (2006). A stock’s issuance index is then defined as the arithmetic average of its percentile ranks across these three equity issuance-related variables. Within each characteristic decile (Panel A) or issuance index decile (Panel B), stocks are subsequently sorted into decile portfolios based on MAX, defined as the average of the five highest daily returns within a month. The final row reports the alpha spreads between the highest (Portfolio 10) and lowest (Portfolio 1) MAX deciles. Newey and West (1987) $t$-statistics (adjusted with six lags) are reported in parentheses. All sample periods end in December 2022, with start dates varying by characteristic: August 1971 for PEAD, January 1972 for ROA, January 1975 for Distress, and January 1968 for all others.

<table>
  <thead>
    <tr>
      <th rowspan="2">Decile</th>
      <th colspan="10">Panel A: Mispricing characteristics</th>
      <th rowspan="2">Panel B: Issuance index</th>
    </tr>
    <tr>
      <th>Accruals</th>
      <th>NOA</th>
      <th>Asset growth</th>
      <th>INV/AT</th>
      <th>Distress</th>
      <th>O-score</th>
      <th>MOM</th>
      <th>GP</th>
      <th>ROA</th>
      <th>PEAD</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 1</td>
      <td>0.11<br>(1.40)</td>
      <td>0.14<br>(1.67)</td>
      <td>0.16<br>(1.81)</td>
      <td>0.14<br>(1.76)</td>
      <td>0.18<br>(2.02)</td>
      <td>0.18<br>(2.05)</td>
      <td>0.24<br>(2.07)</td>
      <td>0.10<br>(1.39)</td>
      <td>0.21<br>(2.45)</td>
      <td>0.08<br>(1.05)</td>
      <td>0.18<br>(2.17)</td>
    </tr>
    <tr>
      <td>2</td>
      <td>-0.02<br>(-0.28)</td>
      <td>0.04<br>(0.67)</td>
      <td>0.09<br>(1.30)</td>
      <td>0.03<br>(0.48)</td>
      <td>0.04<br>(0.63)</td>
      <td>0.07<br>(0.91)</td>
      <td>0.15<br>(2.36)</td>
      <td>0.07<br>(1.12)</td>
      <td>0.15<br>(1.87)</td>
      <td>0.09<br>(1.16)</td>
      <td>0.05<br>(0.69)</td>
    </tr>
    <tr>
      <td>3</td>
      <td>-0.06<br>(-0.90)</td>
      <td>-0.01<br>(-0.11)</td>
      <td>-0.09<br>(-1.46)</td>
      <td>-0.12<br>(-1.98)</td>
      <td>0.02<br>(0.35)</td>
      <td>-0.03<br>(-0.57)</td>
      <td>-0.01<br>(-0.04)</td>
      <td>-0.01<br>(-0.23)</td>
      <td>0.05<br>(0.78)</td>
      <td>0.01<br>(0.30)</td>
      <td>0.01<br>(0.06)</td>
    </tr>
    <tr>
      <td>4</td>
      <td>0.05<br>(0.78)</td>
      <td>-0.01<br>(-0.27)</td>
      <td>0.04<br>(0.67)</td>
      <td>0.13<br>(2.07)</td>
      <td>0.03<br>(0.51)</td>
      <td>0.09<br>(1.06)</td>
      <td>0.06<br>(0.79)</td>
      <td>0.04<br>(0.72)</td>
      <td>0.07<br>(0.78)</td>
      <td>0.05<br>(0.82)</td>
      <td>-0.08<br>(-1.14)</td>
    </tr>
    <tr>
      <td>5</td>
      <td>-0.05<br>(-0.69)</td>
      <td>0.08<br>(0.92)</td>
      <td>0.01<br>(0.09)</td>
      <td>-0.13<br>(-1.74)</td>
      <td>-0.07<br>(-0.96)</td>
      <td>-0.01<br>(-0.14)</td>
      <td>0.05<br>(0.75)</td>
      <td>-0.10<br>(-1.22)</td>
      <td>0.05<br>(0.63)</td>
      <td>0.03<br>(0.42)</td>
      <td>0.02<br>(0.30)</td>
    </tr>
    <tr>
      <td>6</td>
      <td>0.04<br>(0.40)</td>
      <td>-0.12<br>(-1.56)</td>
      <td>-0.01<br>(-0.03)</td>
      <td>0.01<br>(0.04)</td>
      <td>-0.05<br>(-0.57)</td>
      <td>-0.01<br>(-0.05)</td>
      <td>-0.09<br>(-1.20)</td>
      <td>0.04<br>(0.54)</td>
      <td>-0.01<br>(-0.07)</td>
      <td>-0.01<br>(-0.22)</td>
      <td>-0.01<br>(-0.21)</td>
    </tr>
    <tr>
      <td>7</td>
      <td>0.10<br>(1.16)</td>
      <td>0.09<br>(0.98)</td>
      <td>0.01<br>(0.04)</td>
      <td>0.09<br>(1.00)</td>
      <td>0.09<br>(1.04)</td>
      <td>0.18<br>(2.01)</td>
      <td>-0.10<br>(-1.07)</td>
      <td>0.06<br>(0.66)</td>
      <td>0.03<br>(0.33)</td>
      <td>0.02<br>(0.22)</td>
      <td>-0.31<br>(-3.04)</td>
    </tr>
    <tr>
      <td>8</td>
      <td>0.01<br>(0.08)</td>
      <td>0.05<br>(0.47)</td>
      <td>0.07<br>(0.66)</td>
      <td>0.09<br>(0.85)</td>
      <td>-0.03<br>(-0.39)</td>
      <td>-0.05<br>(-0.53)</td>
      <td>-0.04<br>(-0.44)</td>
      <td>0.05<br>(0.56)</td>
      <td>-0.11<br>(-1.06)</td>
      <td>0.03<br>(0.31)</td>
      <td>0.17<br>(1.50)</td>
    </tr>
    <tr>
      <td>9</td>
      <td>-0.11<br>(-0.88)</td>
      <td>-0.18<br>(-1.57)</td>
      <td>-0.12<br>(-1.15)</td>
      <td>-0.04<br>(-0.37)</td>
      <td>-0.12<br>(-1.07)</td>
      <td>-0.08<br>(-0.67)</td>
      <td>-0.26<br>(-2.15)</td>
      <td>-0.29<br>(-2.50)</td>
      <td>-0.34<br>(-2.57)</td>
      <td>-0.07<br>(-0.58)</td>
      <td>0.10<br>(0.74)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-0.31<br>(-2.08)</td>
      <td>-0.36<br>(-2.46)</td>
      <td>-0.31<br>(-2.24)</td>
      <td>-0.24<br>(-1.67)</td>
      <td>-0.18<br>(-1.37)</td>
      <td>-0.20<br>(-1.38)</td>
      <td>-0.27<br>(-2.07)</td>
      <td>-0.26<br>(-1.71)</td>
      <td>-0.37<br>(-2.18)</td>
      <td>-0.48<br>(-2.90)</td>
      <td>-0.03<br>(-0.21)</td>
    </tr>
    <tr>
      <td>10-1 difference</td>
      <td>-0.42<br>(-2.34)</td>
      <td>-0.50<br>(-2.59)</td>
      <td>-0.47<br>(-2.62)</td>
      <td>-0.38<br>(-2.07)</td>
      <td>-0.36<br>(-1.97)</td>
      <td>-0.38<br>(-2.05)</td>
      <td>-0.51<br>(-3.11)</td>
      <td>-0.36<br>(-1.98)</td>
      <td>-0.58<br>(-2.65)</td>
      <td>-0.56<br>(-2.85)</td>
      <td>-0.21<br>(-0.99)</td>
    </tr>
  </tbody>
</table>

---

# Page 62

Table 6

**Portfolio sorts on MAX $^\beta$ **: This table reports the performance of market beta-neutralized MAX-sorted portfolios (MAX $^\beta$ ). The portfolios are constructed using a conditional sorting procedure. First, stocks are sorted into decile portfolios based on their market beta. Then, within each beta-sorted portfolio, stocks are further sorted into decile portfolios based on their MAX (defined as the average of the five highest daily returns within a month). To form the final deciles, we group together all stocks with the same MAX ranking, $n$ , across the different beta portfolios; this combined set is defined as the MAX $^\beta$ portfolio of rank $n$ . Portfolio 1 (10) contains stocks with the lowest (highest) MAX $^\beta$ rank. The reported values are value-weighted average one-month-ahead excess returns (RET – RF), as well as alphas from risk-adjusted models (CAPM, FF3, FFC4, FFCPS, FF5, FF6, and FF6PS) and mispricing-adjusted models (SY and DHS). The final row reports the differences (spreads) in average monthly returns and alphas between Portfolio 10 and Portfolio 1. Newey and West (1987) $t$ -statistics (adjusted with six lags) are reported in parentheses. The sample period spans January 1968 to December 2022, with the exception of the DHS analysis, which begins in July 1972.

<table>
  <thead>
    <tr>
      <th>Decile</th>
      <th>RET-RF</th>
      <th>CAPM</th>
      <th>FF3</th>
      <th>FFC4</th>
      <th>FFCPS</th>
      <th>FF5</th>
      <th>FF6</th>
      <th>FF6PS</th>
      <th>SY</th>
      <th>DHS</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 1</td>
      <td>0.71<br>(3.74)</td>
      <td>0.18<br>(2.59)</td>
      <td>0.22<br>(3.45)</td>
      <td>0.25<br>(3.38)</td>
      <td>0.24<br>(3.21)</td>
      <td>0.22<br>(3.36)</td>
      <td>0.24<br>(3.29)</td>
      <td>0.23<br>(3.08)</td>
      <td>0.23<br>(3.15)</td>
      <td>0.25<br>(2.96)</td>
    </tr>
    <tr>
      <td>2</td>
      <td>0.52<br>(2.82)</td>
      <td>0.01<br>(0.06)</td>
      <td>0.04<br>(0.82)</td>
      <td>0.04<br>(0.79)</td>
      <td>0.03<br>(0.71)</td>
      <td>-0.00<br>(-0.01)</td>
      <td>0.01<br>(0.04)</td>
      <td>-0.01<br>(-0.07)</td>
      <td>-0.02<br>(-0.43)</td>
      <td>-0.04<br>(-0.65)</td>
    </tr>
    <tr>
      <td>3</td>
      <td>0.64<br>(3.55)</td>
      <td>0.11<br>(2.09)</td>
      <td>0.14<br>(2.37)</td>
      <td>0.19<br>(3.18)</td>
      <td>0.19<br>(3.27)</td>
      <td>0.11<br>(1.76)</td>
      <td>0.15<br>(2.49)</td>
      <td>0.16<br>(2.61)</td>
      <td>0.12<br>(1.83)</td>
      <td>0.14<br>(1.81)</td>
    </tr>
    <tr>
      <td>4</td>
      <td>0.57<br>(3.02)</td>
      <td>0.02<br>(0.44)</td>
      <td>0.05<br>(0.91)</td>
      <td>0.07<br>(1.11)</td>
      <td>0.08<br>(1.25)</td>
      <td>0.01<br>(0.18)</td>
      <td>0.02<br>(0.42)</td>
      <td>0.03<br>(0.59)</td>
      <td>0.07<br>(1.03)</td>
      <td>0.03<br>(0.40)</td>
    </tr>
    <tr>
      <td>5</td>
      <td>0.62<br>(3.14)</td>
      <td>0.05<br>(0.96)</td>
      <td>0.06<br>(1.15)</td>
      <td>0.06<br>(1.07)</td>
      <td>0.06<br>(1.00)</td>
      <td>0.02<br>(0.46)</td>
      <td>0.03<br>(0.49)</td>
      <td>0.02<br>(0.39)</td>
      <td>0.02<br>(0.41)</td>
      <td>0.09<br>(1.31)</td>
    </tr>
    <tr>
      <td>6</td>
      <td>0.54<br>(2.60)</td>
      <td>-0.04<br>(-0.67)</td>
      <td>-0.02<br>(-0.40)</td>
      <td>-0.04<br>(-0.63)</td>
      <td>-0.04<br>(-0.66)</td>
      <td>-0.02<br>(-0.23)</td>
      <td>-0.03<br>(-0.42)</td>
      <td>-0.03<br>(-0.45)</td>
      <td>-0.02<br>(-0.32)</td>
      <td>0.03<br>(0.38)</td>
    </tr>
    <tr>
      <td>7</td>
      <td>0.56<br>(2.57)</td>
      <td>-0.03<br>(-0.37)</td>
      <td>-0.01<br>(-0.19)</td>
      <td>-0.01<br>(-0.13)</td>
      <td>-0.01<br>(-0.08)</td>
      <td>-0.02<br>(-0.19)</td>
      <td>-0.01<br>(-0.14)</td>
      <td>-0.01<br>(-0.08)</td>
      <td>0.01<br>(0.10)</td>
      <td>0.04<br>(0.44)</td>
    </tr>
    <tr>
      <td>8</td>
      <td>0.52<br>(2.10)</td>
      <td>-0.12<br>(-1.09)</td>
      <td>-0.03<br>(-0.32)</td>
      <td>-0.09<br>(-1.06)</td>
      <td>-0.10<br>(-1.08)</td>
      <td>0.04<br>(0.41)</td>
      <td>-0.01<br>(-0.11)</td>
      <td>-0.01<br>(-0.14)</td>
      <td>0.03<br>(0.37)</td>
      <td>0.08<br>(0.65)</td>
    </tr>
    <tr>
      <td>9</td>
      <td>0.29<br>(1.07)</td>
      <td>-0.40<br>(-3.16)</td>
      <td>-0.32<br>(-3.15)</td>
      <td>-0.36<br>(-3.56)</td>
      <td>-0.36<br>(-3.54)</td>
      <td>-0.17<br>(-1.90)</td>
      <td>-0.22<br>(-2.32)</td>
      <td>-0.22<br>(-2.28)</td>
      <td>-0.14<br>(-1.41)</td>
      <td>0.01<br>(0.04)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-0.10<br>(-0.33)</td>
      <td>-0.82<br>(-4.33)</td>
      <td>-0.68<br>(-4.19)</td>
      <td>-0.70<br>(-4.16)</td>
      <td>-0.72<br>(-4.28)</td>
      <td>-0.45<br>(-3.19)</td>
      <td>-0.48<br>(-3.14)</td>
      <td>-0.50<br>(-3.25)</td>
      <td>-0.39<br>(-2.37)</td>
      <td>-0.21<br>(-1.17)</td>
    </tr>
    <tr>
      <td>10-1 difference</td>
      <td>-0.81<br>(-3.62)</td>
      <td>-1.00<br>(-4.72)</td>
      <td>-0.90<br>(-4.98)</td>
      <td>-0.95<br>(-4.76)</td>
      <td>-0.96<br>(-4.74)</td>
      <td>-0.67<br>(-4.17)</td>
      <td>-0.72<br>(-3.95)</td>
      <td>-0.73<br>(-3.89)</td>
      <td>-0.62<br>(-3.33)</td>
      <td>-0.46<br>(-2.10)</td>
    </tr>
  </tbody>
</table>

---

# Page 63

Table 7

**Equity issuance- and mispricing-controlled MAX and MAX $^\beta$ portfolios**: This table reports one-month-ahead alphas (FF6PS) for the value-weighted decile portfolios sorted by MAX and MAX $^\beta$ , after controlling for equity issuance (Panel A) and the mispricing score (MIS) (Panel B). In Panel A, the control variable is the stock-level equity issuance index described in Table 5. In Panel B, the control variable is the aggregate mispricing score (MIS) of Stambaugh, Yu, and Yuan (2015). The portfolios are constructed using conditional dependent sorts. First, stocks are sorted into decile portfolios based on the issuance index (Panel A) or MIS (Panel B). For the controlled MAX portfolios, stocks are subsequently sorted into MAX deciles within each control portfolio. For the controlled MAX $^\beta$ portfolios, a three-step procedure is used: within each issuance or MIS decile, stocks are first sorted into decile portfolios based on market beta; then, within each of these portfolios, stocks are further sorted into deciles based on MAX. The final decile portfolios are formed by grouping together all stocks with the same MAX ranking across the control (and beta) portfolios. Portfolio 1 (10) consists of stocks with the lowest (highest) MAX. The final row reports the alpha spreads between decile portfolios 10 and 1. Newey and West (1987) $t$ -statistics (adjusted with six lags) are reported in parentheses. The sample period spans January 1968 to December 2022.

<table>
  <thead>
    <tr>
      <th rowspan="2">Decile</th>
      <th colspan="2">Panel A: Issuance controlled</th>
      <th colspan="2">Panel B: Mispricing controlled</th>
    </tr>
    <tr>
      <th>MAX</th>
      <th>MAX $^\beta$ </th>
      <th>MAX</th>
      <th>MAX $^\beta$ </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 1</td>
      <td>0.18<br>(2.17)</td>
      <td>0.20<br>(2.68)</td>
      <td>0.16<br>(2.07)</td>
      <td>0.21<br>(2.96)</td>
    </tr>
    <tr>
      <td>2</td>
      <td>0.05<br>(0.69)</td>
      <td>0.08<br>(1.13)</td>
      <td>0.03<br>(0.53)</td>
      <td>-0.01<br>(-0.21)</td>
    </tr>
    <tr>
      <td>3</td>
      <td>0.01<br>(0.06)</td>
      <td>0.09<br>(1.25)</td>
      <td>-0.00<br>(-0.03)</td>
      <td>0.06<br>(1.05)</td>
    </tr>
    <tr>
      <td>4</td>
      <td>-0.08<br>(-1.14)</td>
      <td>-0.06<br>(-0.65)</td>
      <td>0.05<br>(0.84)</td>
      <td>0.03<br>(0.47)</td>
    </tr>
    <tr>
      <td>5</td>
      <td>0.02<br>(0.30)</td>
      <td>-0.05<br>(-0.63)</td>
      <td>-0.03<br>(-0.45)</td>
      <td>0.13<br>(1.97)</td>
    </tr>
    <tr>
      <td>6</td>
      <td>-0.01<br>(-0.21)</td>
      <td>-0.08<br>(-0.95)</td>
      <td>-0.08<br>(-1.18)</td>
      <td>-0.01<br>(-0.19)</td>
    </tr>
    <tr>
      <td>7</td>
      <td>-0.31<br>(-3.04)</td>
      <td>-0.04<br>(-0.42)</td>
      <td>0.14<br>(1.41)</td>
      <td>0.10<br>(1.20)</td>
    </tr>
    <tr>
      <td>8</td>
      <td>0.17<br>(1.50)</td>
      <td>0.11<br>(0.98)</td>
      <td>-0.00<br>(-0.02)</td>
      <td>-0.07<br>(-0.80)</td>
    </tr>
    <tr>
      <td>9</td>
      <td>0.10<br>(0.74)</td>
      <td>-0.23<br>(-1.87)</td>
      <td>-0.05<br>(-0.50)</td>
      <td>-0.13<br>(-1.25)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-0.03<br>(-0.21)</td>
      <td>-0.28<br>(-1.82)</td>
      <td>-0.13<br>(-0.86)</td>
      <td>-0.25<br>(-1.79)</td>
    </tr>
    <tr>
      <td>10-1 difference</td>
      <td>-0.21<br>(-0.99)</td>
      <td>-0.48<br>(-2.32)</td>
      <td>-0.29<br>(-1.53)</td>
      <td>-0.46<br>(-2.52)</td>
    </tr>
  </tbody>
</table>

---

# Page 64

Table 8

**Fama-MacBeth (1973) regressions on MAX $^\beta$ **: This table reports the results of firm-level Fama-MacBeth (1973) cross-sectional regressions of one-month-ahead excess stock returns on dummy variables corresponding to MAX $^\beta$ portfolio rankings and a set of control variables. The MAX $^\beta$ rankings are determined using a conditional sorting procedure: stocks are first sorted into ten portfolios based on market beta, and then, within each beta portfolio, into ten deciles based on MAX. Stocks with the same MAX ranking ( $n$ ) across the beta portfolios are assigned to MAX $^\beta$ rank $n$ . The regression includes dummy variables for MAX $^\beta$ ranks 2 through 10 (Rank 1 serves as the benchmark to avoid multicollinearity). The control variables include: the firm-level mispricing score (MIS) of Stambaugh, Yu, and Yuan (2015); composite equity issuance (CE); market beta (BETA); the natural logarithm of market capitalization (SIZE); the natural logarithm of the book-to-market ratio (BM); excess monthly return during the portfolio formation month (REV); intermediate-term momentum (MOM); Amihud (2002) illiquidity (ILLIQ); return on equity (ROE); asset growth (I/A); and idiosyncratic volatility (IVOL). The final row indicates the control variables included in each specification and the average adjusted $R^2$ . Newey and West (1987) $t$ -statistics (adjusted with six lags) are reported in parentheses. The sample period spans January 1968 to December 2022.

<table>
  <thead>
    <tr>
      <th rowspan="2"></th>
      <th>(1)</th>
      <th>(2)</th>
      <th>(3)</th>
      <th>(4)</th>
      <th>(5)</th>
      <th>(6)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>-1.027<br>(-6.61)</td>
      <td>-0.435<br>(-3.98)</td>
      <td>-0.834<br>(-5.69)</td>
      <td>-0.937<br>(-6.27)</td>
      <td>-0.403<br>(-3.64)</td>
      <td>-0.421<br>(-3.79)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>-0.566<br>(-4.98)</td>
      <td>-0.179<br>(-2.30)</td>
      <td>-0.418<br>(-3.92)</td>
      <td>-0.501<br>(-4.61)</td>
      <td>-0.155<br>(-1.99)</td>
      <td>-0.170<br>(-2.17)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>-0.360<br>(-3.64)</td>
      <td>-0.064<br>(-0.83)</td>
      <td>-0.246<br>(-2.60)</td>
      <td>-0.306<br>(-3.21)</td>
      <td>-0.048<br>(-0.63)</td>
      <td>-0.056<br>(-0.73)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>-0.255<br>(-2.94)</td>
      <td>-0.013<br>(-0.20)</td>
      <td>-0.170<br>(-2.03)</td>
      <td>-0.218<br>(-2.61)</td>
      <td>-0.001<br>(-0.01)</td>
      <td>-0.009<br>(-0.14)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>-0.176<br>(-2.61)</td>
      <td>0.017<br>(0.28)</td>
      <td>-0.110<br>(-1.70)</td>
      <td>-0.147<br>(-2.23)</td>
      <td>0.028<br>(0.45)</td>
      <td>0.019<br>(0.31)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>-0.086<br>(-1.33)</td>
      <td>0.074<br>(1.27)</td>
      <td>-0.048<br>(-0.77)</td>
      <td>-0.067<br>(-1.06)</td>
      <td>0.079<br>(1.36)</td>
      <td>0.075<br>(1.29)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>-0.029<br>(-0.55)</td>
      <td>0.090<br>(1.84)</td>
      <td>-0.009<br>(-0.19)</td>
      <td>-0.020<br>(-0.39)</td>
      <td>0.092<br>(1.89)</td>
      <td>0.090<br>(1.82)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>-0.038<br>(-0.81)</td>
      <td>0.072<br>(1.64)</td>
      <td>-0.033<br>(-0.71)</td>
      <td>-0.038<br>(-0.82)</td>
      <td>0.075<br>(1.70)</td>
      <td>0.072<br>(1.67)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>-0.065<br>(-1.54)</td>
      <td>0.001<br>(0.04)</td>
      <td>-0.076<br>(-1.80)</td>
      <td>-0.069<br>(-1.62)</td>
      <td>-0.001<br>(-0.02)</td>
      <td>0.001<br>(0.00)</td>
    </tr>
    <tr>
      <td>Intercept</td>
      <td>0.009<br>(4.60)</td>
      <td>0.025<br>(5.24)</td>
      <td>0.023<br>(13.27)</td>
      <td>0.009<br>(4.61)</td>
      <td>0.033<br>(7.11)</td>
      <td>0.024<br>(5.10)</td>
    </tr>
    <tr>
      <td>Control variables</td>
      <td>No</td>
      <td>BETA, SIZE, BM, REV, MOM, ILLIQ, ROE, I/A, IVOL</td>
      <td>MIS</td>
      <td>CE</td>
      <td>MIS, BETA, SIZE, BM, REV, MOM, ILLIQ, ROE, I/A, IVOL</td>
      <td>CE, BETA, SIZE, BM, REV, MOM, ILLIQ, ROE, I/A, IVOL</td>
    </tr>
    <tr>
      <td> $R^2$ </td>
      <td>0.012</td>
      <td>0.079</td>
      <td>0.022</td>
      <td>0.019</td>
      <td>0.081</td>
      <td>0.080</td>
    </tr>
  </tbody>
</table>

---

# Page 65

Table 9

**Institutional holdings, MAX, and MAX $^\beta$ **: This table examines the role of institutional holdings (INST) in the cross-sectional pricing of MAX and MAX $^\beta$ . The sample is divided into three subgroups based on the 33rd and 67th percentiles of INST, labeled INST1 (lowest holdings) through INST3 (highest holdings). The portfolios are constructed using conditional dependent sorts. For the controlled MAX portfolios (Panel A), stocks are subsequently sorted into MAX deciles within each INST tier. For the controlled MAX $^\beta$ portfolios (Panel B), a two-step procedure is used: within each INST tier, stocks are first sorted into decile portfolios based on market beta; then, within each of these beta portfolios, stocks are further sorted into deciles based on MAX. The final MAX $^\beta$ decile portfolios are formed by grouping together all stocks with the same MAX ranking across the beta portfolios within that INST tier. Portfolio 1 (10) consists of stocks with the lowest (highest) MAX or MAX $^\beta$ . The table reports one-month-ahead value-weighted excess returns (RET − RF) and alphas (FF6PS). Newey and West (1987) $t$ -statistics (adjusted with five lags) are reported in parentheses. The sample period spans April 1980 to December 2022.

<table>
  <thead>
    <tr>
      <th rowspan="3">Decile</th>
      <th colspan="6">Panel A: MAX-sorted portfolios within INST tiers</th>
      <th colspan="6">Panel B: MAX $^\beta$ -sorted portfolios within INST tiers</th>
    </tr>
    <tr>
      <th colspan="2">INST 1</th>
      <th colspan="2">INST 2</th>
      <th colspan="2">INST 3</th>
      <th colspan="2">INST 1</th>
      <th colspan="2">INST 2</th>
      <th colspan="2">INST 3</th>
    </tr>
    <tr>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 1</td>
      <td>0.72</td>
      <td>0.07</td>
      <td>0.90</td>
      <td>0.27</td>
      <td>0.90</td>
      <td>0.07</td>
      <td>0.82</td>
      <td>0.26</td>
      <td>0.85</td>
      <td>0.16</td>
      <td>0.97</td>
      <td>0.23</td>
    </tr>
    <tr>
      <td></td>
      <td>(3.80)</td>
      <td>(0.49)</td>
      <td>(5.42)</td>
      <td>(2.41)</td>
      <td>(4.68)</td>
      <td>(0.65)</td>
      <td>(3.70)</td>
      <td>(1.79)</td>
      <td>(3.55)</td>
      <td>(1.33)</td>
      <td>(4.50)</td>
      <td>(2.45)</td>
    </tr>
    <tr>
      <td>2</td>
      <td>0.80</td>
      <td>0.09</td>
      <td>1.03</td>
      <td>0.22</td>
      <td>0.71</td>
      <td>-0.17</td>
      <td>0.71</td>
      <td>0.21</td>
      <td>0.89</td>
      <td>0.22</td>
      <td>0.76</td>
      <td>-0.08</td>
    </tr>
    <tr>
      <td></td>
      <td>(3.86)</td>
      <td>(0.73)</td>
      <td>(5.43)</td>
      <td>(2.06)</td>
      <td>(3.43)</td>
      <td>(-1.65)</td>
      <td>(2.40)</td>
      <td>(1.21)</td>
      <td>(4.20)</td>
      <td>(2.32)</td>
      <td>(3.13)</td>
      <td>(-0.84)</td>
    </tr>
    <tr>
      <td>3</td>
      <td>0.70</td>
      <td>-0.01</td>
      <td>0.83</td>
      <td>0.01</td>
      <td>0.75</td>
      <td>-0.10</td>
      <td>0.43</td>
      <td>-0.19</td>
      <td>0.73</td>
      <td>0.07</td>
      <td>0.75</td>
      <td>-0.06</td>
    </tr>
    <tr>
      <td></td>
      <td>(2.91)</td>
      <td>(-0.05)</td>
      <td>(4.01)</td>
      <td>(0.19)</td>
      <td>(3.35)</td>
      <td>(-1.17)</td>
      <td>(1.69)</td>
      <td>(-1.08)</td>
      <td>(3.46)</td>
      <td>(0.72)</td>
      <td>(3.25)</td>
      <td>(-0.82)</td>
    </tr>
    <tr>
      <td>4</td>
      <td>0.75</td>
      <td>0.04</td>
      <td>0.86</td>
      <td>0.19</td>
      <td>0.85</td>
      <td>-0.05</td>
      <td>0.54</td>
      <td>0.13</td>
      <td>0.90</td>
      <td>0.33</td>
      <td>0.79</td>
      <td>-0.01</td>
    </tr>
    <tr>
      <td></td>
      <td>(2.45)</td>
      <td>(0.21)</td>
      <td>(3.84)</td>
      <td>(1.62)</td>
      <td>(3.99)</td>
      <td>(-0.67)</td>
      <td>(1.82)</td>
      <td>(0.71)</td>
      <td>(4.16)</td>
      <td>(2.67)</td>
      <td>(3.44)</td>
      <td>(-0.20)</td>
    </tr>
    <tr>
      <td>5</td>
      <td>0.33</td>
      <td>-0.23</td>
      <td>0.84</td>
      <td>0.09</td>
      <td>0.82</td>
      <td>-0.09</td>
      <td>0.43</td>
      <td>-0.01</td>
      <td>1.08</td>
      <td>0.43</td>
      <td>0.54</td>
      <td>-0.30</td>
    </tr>
    <tr>
      <td></td>
      <td>(1.15)</td>
      <td>(-1.26)</td>
      <td>(3.19)</td>
      <td>(0.55)</td>
      <td>(3.50)</td>
      <td>(-0.85)</td>
      <td>(1.56)</td>
      <td>(-0.07)</td>
      <td>(3.77)</td>
      <td>(2.51)</td>
      <td>(2.22)</td>
      <td>(-2.89)</td>
    </tr>
    <tr>
      <td>6</td>
      <td>0.66</td>
      <td>0.12</td>
      <td>0.95</td>
      <td>0.26</td>
      <td>0.78</td>
      <td>-0.13</td>
      <td>0.74</td>
      <td>0.07</td>
      <td>0.66</td>
      <td>0.04</td>
      <td>0.79</td>
      <td>-0.04</td>
    </tr>
    <tr>
      <td></td>
      <td>(1.80)</td>
      <td>(0.61)</td>
      <td>(3.52)</td>
      <td>(1.78)</td>
      <td>(3.11)</td>
      <td>(-1.30)</td>
      <td>(2.32)</td>
      <td>(0.37)</td>
      <td>(2.90)</td>
      <td>(0.35)</td>
      <td>(3.37)</td>
      <td>(-0.41)</td>
    </tr>
    <tr>
      <td>7</td>
      <td>0.40</td>
      <td>-0.15</td>
      <td>0.78</td>
      <td>0.19</td>
      <td>0.64</td>
      <td>-0.18</td>
      <td>0.68</td>
      <td>0.12</td>
      <td>0.66</td>
      <td>-0.01</td>
      <td>0.75</td>
      <td>-0.17</td>
    </tr>
    <tr>
      <td></td>
      <td>(1.09)</td>
      <td>(-0.72)</td>
      <td>(2.55)</td>
      <td>(1.35)</td>
      <td>(2.38)</td>
      <td>(-1.59)</td>
      <td>(1.87)</td>
      <td>(0.52)</td>
      <td>(2.63)</td>
      <td>(-0.03)</td>
      <td>(3.02)</td>
      <td>(-1.82)</td>
    </tr>
    <tr>
      <td>8</td>
      <td>0.38</td>
      <td>-0.18</td>
      <td>0.54</td>
      <td>-0.06</td>
      <td>0.81</td>
      <td>0.10</td>
      <td>0.47</td>
      <td>-0.07</td>
      <td>0.64</td>
      <td>-0.00</td>
      <td>0.64</td>
      <td>-0.09</td>
    </tr>
    <tr>
      <td></td>
      <td>(0.88)</td>
      <td>(-0.80)</td>
      <td>(1.52)</td>
      <td>(-0.34)</td>
      <td>(2.69)</td>
      <td>(0.76)</td>
      <td>(1.11)</td>
      <td>(-0.28)</td>
      <td>(2.13)</td>
      <td>(-0.01)</td>
      <td>(2.68)</td>
      <td>(-0.83)</td>
    </tr>
    <tr>
      <td>9</td>
      <td>0.32</td>
      <td>0.13</td>
      <td>0.10</td>
      <td>-0.46</td>
      <td>0.53</td>
      <td>-0.10</td>
      <td>0.46</td>
      <td>0.21</td>
      <td>0.38</td>
      <td>-0.26</td>
      <td>0.49</td>
      <td>-0.29</td>
    </tr>
    <tr>
      <td></td>
      <td>(0.77)</td>
      <td>(0.55)</td>
      <td>(0.29)</td>
      <td>(-2.81)</td>
      <td>(1.54)</td>
      <td>(-0.61)</td>
      <td>(1.13)</td>
      <td>(0.88)</td>
      <td>(1.12)</td>
      <td>(-1.36)</td>
      <td>(1.74)</td>
      <td>(-1.96)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-0.54</td>
      <td>-0.78</td>
      <td>0.32</td>
      <td>-0.06</td>
      <td>0.47</td>
      <td>0.02</td>
      <td>-0.73</td>
      <td>-1.18</td>
      <td>0.16</td>
      <td>-0.35</td>
      <td>0.55</td>
      <td>-0.14</td>
    </tr>
    <tr>
      <td></td>
      <td>(-1.07)</td>
      <td>(-2.81)</td>
      <td>(0.71)</td>
      <td>(-0.27)</td>
      <td>(1.26)</td>
      <td>(0.09)</td>
      <td>(-1.39)</td>
      <td>(-4.07)</td>
      <td>(0.46)</td>
      <td>(-1.89)</td>
      <td>(1.79)</td>
      <td>(-0.86)</td>
    </tr>
    <tr>
      <td>10-1 difference</td>
      <td>-1.26</td>
      <td>-0.85</td>
      <td>-0.58</td>
      <td>-0.34</td>
      <td>-0.43</td>
      <td>-0.05</td>
      <td>-1.54</td>
      <td>-1.44</td>
      <td>-0.69</td>
      <td>-0.51</td>
      <td>-0.42</td>
      <td>-0.37</td>
    </tr>
    <tr>
      <td></td>
      <td>(-2.60)</td>
      <td>(-2.36)</td>
      <td>(-1.56)</td>
      <td>(-1.31)</td>
      <td>(-1.40)</td>
      <td>(-0.25)</td>
      <td>(-3.59)</td>
      <td>(-3.95)</td>
      <td>(-2.66)</td>
      <td>(-2.17)</td>
      <td>(-2.20)</td>
      <td>(-1.96)</td>
    </tr>
  </tbody>
</table>

---

# Page 66

Table 10

**Institutional ownership, accumulation, and the pricing of the MAX $^\beta$ legs**: This table reports one-month-ahead value-weighted FF6PS alphas for tercile portfolios formed within the long (low-MAX $^\beta$ , decile 1) and short (high-MAX $^\beta$ , decile 10) legs of the MAX $^\beta$ strategy. Within each leg, stocks are sorted into terciles, at the 33rd and 67th percentiles computed within the leg, by the level of institutional ownership (INST), by the change in institutional ownership realized through the most recent quarter-end ( $\Delta$ INST, measured prior to the return month so that the sort involves no look-ahead), and by the expected idiosyncratic skewness (E(ISKEW)) measure of Boyer, Mitton, and Vorkink (2010). Panel A reports the long leg and Panel B the short leg. Because the terciles are formed within the leg, this is a dependent sort, and the INST-tercile alphas here need not coincide with those from the independent double sort of Table 11. All alphas are in percent per month. Newey and West (1987) $t$ -statistics (adjusted with five lags) are reported in parentheses. The sample period spans April 1980 to December 2022.

<table>
  <thead>
    <tr>
      <th rowspan="2">Sort variable</th>
      <th rowspan="2">Tercile</th>
      <th colspan="2">Panel A: Long leg (low-MAX $^\beta$ )</th>
      <th colspan="2">Panel B: Short leg (high-MAX $^\beta$ )</th>
    </tr>
    <tr>
      <th>FF6PS</th>
      <th></th>
      <th>FF6PS</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="3">INST</td>
      <td>Low</td>
      <td>0.12</td>
      <td>(0.82)</td>
      <td>-1.97</td>
      <td>(-6.28)</td>
    </tr>
    <tr>
      <td>Mid</td>
      <td>0.20</td>
      <td>(2.10)</td>
      <td>-0.71</td>
      <td>(-2.65)</td>
    </tr>
    <tr>
      <td>High</td>
      <td>0.23</td>
      <td>(2.56)</td>
      <td>0.05</td>
      <td>(0.31)</td>
    </tr>
    <tr>
      <td rowspan="3"> $\Delta$ INST</td>
      <td>Low</td>
      <td>-0.19</td>
      <td>(-1.65)</td>
      <td>-1.51</td>
      <td>(-5.66)</td>
    </tr>
    <tr>
      <td>Mid</td>
      <td>0.17</td>
      <td>(1.56)</td>
      <td>-0.84</td>
      <td>(-3.39)</td>
    </tr>
    <tr>
      <td>High</td>
      <td>0.70</td>
      <td>(6.31)</td>
      <td>0.94</td>
      <td>(4.19)</td>
    </tr>
    <tr>
      <td rowspan="3">E(ISKEW)</td>
      <td>Low</td>
      <td>0.34</td>
      <td>(3.16)</td>
      <td>-0.20</td>
      <td>(-0.88)</td>
    </tr>
    <tr>
      <td>Mid</td>
      <td>0.19</td>
      <td>(1.55)</td>
      <td>-0.57</td>
      <td>(-2.74)</td>
    </tr>
    <tr>
      <td>High</td>
      <td>0.17</td>
      <td>(1.00)</td>
      <td>-0.94</td>
      <td>(-4.80)</td>
    </tr>
  </tbody>
</table>

65

---

# Page 67

Table 11

**Institutional accumulation and the low-MAX $^\beta$ premium**: Panel A reports an independent double sort in which stocks in the low-MAX $^\beta$ decile (decile 1) are intersected with terciles of institutional ownership (INST) formed on the full sample at the 33rd and 67th percentiles; because these breakpoints are independent of the MAX $^\beta$ sort, rather than computed within the leg as in Table 10, the INST-tier alphas need not coincide with those in the INST panel of Table 10. For each intersection, the table reports the time-series average of the cross-sectional mean change in institutional ownership through the most recent quarter-end ( $\Delta$ INST, in percent, measured prior to the return month) and expected idiosyncratic skewness (E(ISKEW)), together with the one-month-ahead value-weighted FF6PS alpha (in percent per month). Panel B reports one-month-ahead FF6PS alphas for triple-sorted portfolios of low-MAX $^\beta$ and high-MAX $^\beta$ stocks that are further sorted by INST and by $\Delta$ INST; results are shown for both dependent and independent sorts. Newey and West (1987) $t$ -statistics (adjusted with five lags) are reported in parentheses. The sample period spans April 1980 to December 2022.

<table>
  <thead>
    <tr>
      <th colspan="4">Panel A: Independent double sort within the low-MAX $^\beta$ decile</th>
    </tr>
    <tr>
      <th>INST tier</th>
      <th> $\Delta$ INST (%)</th>
      <th>E(ISKEW)</th>
      <th>FF6PS</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Low INST</td>
      <td>−0.01</td>
      <td>1.04</td>
      <td>0.05<br>(0.31)</td>
    </tr>
    <tr>
      <td>Mid INST</td>
      <td>0.10</td>
      <td>0.67</td>
      <td>0.23<br>(2.23)</td>
    </tr>
    <tr>
      <td>High INST</td>
      <td>0.28</td>
      <td>0.60</td>
      <td>0.24<br>(2.52)</td>
    </tr>
  </tbody>
</table>

<table>
  <thead>
    <tr>
      <th colspan="3">Panel B: Triple sort on MAX $^\beta$ , INST, and $\Delta$ INST (FF6PS alpha)</th>
    </tr>
    <tr>
      <th>Portfolio</th>
      <th>Dependent sort</th>
      <th>Independent sort</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Low-MAX $^\beta$ , high-INST, high- $\Delta$ INST</td>
      <td>0.74<br>(5.02)</td>
      <td>0.78<br>(4.63)</td>
    </tr>
    <tr>
      <td>High-MAX $^\beta$ , low-INST, low- $\Delta$ INST</td>
      <td>−1.09<br>(−2.79)</td>
      <td>−1.00<br>(−3.50)</td>
    </tr>
  </tbody>
</table>

66

---

# Page 68

Table 12

**Durability of the MAX and MAX $^\beta$ premia: calendar-time abnormal returns by holding horizon:** This table reports abnormal returns to holding the MAX and MAX $^\beta$ long-short strategies, and each of their four legs, for $K$ months after formation. Each leg is a value-weighted portfolio. For each horizon $K$ we form the strategy every month, hold each cohort for $K$ months without rebalancing, and in each calendar month average the $K$ most recently formed cohorts with weight $1/K$ each, yielding a single monthly return series (Jegadeesh and Titman, 1993; Fama, 1998). We report the per-month FF6PS alpha, $\alpha_K$ (in percent), with Newey and West (1987) $t$ -statistics (adjusted with six lags) in parentheses. The final rows report the cumulative abnormal return $\text{CR}(K) = K \cdot \alpha_K$ (in percent) at the two-year horizon, which carries the $t$ -statistic of $\alpha_{24}$ . “MAX” and “MAX $^\beta$ ” denote the low-minus-high long-short strategies; the leg columns report each decile portfolio’s own alpha. Representative horizons are reported; Figure 1 plots the cumulative abnormal return at all twenty-four horizons. The sample period spans January 1968 to December 2022.

<table>
  <thead>
    <tr>
      <th rowspan="2">Horizon $K$ </th>
      <th colspan="2">Strategies</th>
      <th colspan="4">Legs</th>
    </tr>
    <tr>
      <th>MAX</th>
      <th>MAX $^\beta$ </th>
      <th>high-MAX</th>
      <th>low-MAX</th>
      <th>high-MAX $^\beta$ </th>
      <th>low-MAX $^\beta$ </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>0.61</td>
      <td>0.73</td>
      <td>−0.54</td>
      <td>0.07</td>
      <td>−0.50</td>
      <td>0.23</td>
    </tr>
    <tr>
      <td></td>
      <td>(3.00)</td>
      <td>(3.89)</td>
      <td>(−3.29)</td>
      <td>(0.87)</td>
      <td>(−3.25)</td>
      <td>(3.08)</td>
    </tr>
    <tr>
      <td>2</td>
      <td>0.36</td>
      <td>0.59</td>
      <td>−0.26</td>
      <td>0.09</td>
      <td>−0.39</td>
      <td>0.21</td>
    </tr>
    <tr>
      <td></td>
      <td>(2.19)</td>
      <td>(4.36)</td>
      <td>(−2.03)</td>
      <td>(1.38)</td>
      <td>(−3.47)</td>
      <td>(3.48)</td>
    </tr>
    <tr>
      <td>3</td>
      <td>0.19</td>
      <td>0.38</td>
      <td>−0.10</td>
      <td>0.09</td>
      <td>−0.23</td>
      <td>0.15</td>
    </tr>
    <tr>
      <td></td>
      <td>(1.20)</td>
      <td>(2.98)</td>
      <td>(−0.82)</td>
      <td>(1.32)</td>
      <td>(−2.29)</td>
      <td>(2.71)</td>
    </tr>
    <tr>
      <td>6</td>
      <td>0.10</td>
      <td>0.30</td>
      <td>−0.04</td>
      <td>0.06</td>
      <td>−0.13</td>
      <td>0.16</td>
    </tr>
    <tr>
      <td></td>
      <td>(0.67)</td>
      <td>(2.75)</td>
      <td>(−0.32)</td>
      <td>(1.01)</td>
      <td>(−1.55)</td>
      <td>(3.15)</td>
    </tr>
    <tr>
      <td>12</td>
      <td>0.04</td>
      <td>0.20</td>
      <td>0.00</td>
      <td>0.04</td>
      <td>−0.06</td>
      <td>0.14</td>
    </tr>
    <tr>
      <td></td>
      <td>(0.29)</td>
      <td>(2.05)</td>
      <td>(0.01)</td>
      <td>(0.75)</td>
      <td>(−0.84)</td>
      <td>(2.57)</td>
    </tr>
    <tr>
      <td>18</td>
      <td>0.03</td>
      <td>0.17</td>
      <td>0.01</td>
      <td>0.04</td>
      <td>−0.05</td>
      <td>0.11</td>
    </tr>
    <tr>
      <td></td>
      <td>(0.20)</td>
      <td>(1.90)</td>
      <td>(0.13)</td>
      <td>(0.71)</td>
      <td>(−0.82)</td>
      <td>(2.17)</td>
    </tr>
    <tr>
      <td>24</td>
      <td>−0.01</td>
      <td>0.12</td>
      <td>0.05</td>
      <td>0.04</td>
      <td>−0.00</td>
      <td>0.11</td>
    </tr>
    <tr>
      <td></td>
      <td>(−0.07)</td>
      <td>(1.35)</td>
      <td>(0.55)</td>
      <td>(0.80)</td>
      <td>(−0.05)</td>
      <td>(2.21)</td>
    </tr>
    <tr>
      <td>CR(24)</td>
      <td>−0.21</td>
      <td>2.76</td>
      <td>1.26</td>
      <td>1.05</td>
      <td>−0.08</td>
      <td>2.68</td>
    </tr>
  </tbody>
</table>

67

---

# Page 69

Table 13

**Explaining MAX and MAX $^\beta$ **: This table examines the role of the aggregate mispricing score (MIS) of Stambaugh, Yu, and Yuan (2012, 2014, 2015), the stock-level equity issuance index, expected idiosyncratic skewness (E(ISKEW)), and institutional holdings (INST) in explaining the variation in MAX and MAX $^\beta$ . Panel A (B) sorts stocks in ascending order of MAX (MAX $^\beta$ ) to form 25 portfolios. The MAX $^\beta$ portfolios are constructed using a conditional dependent sort: stocks are first sorted into 25 portfolios based on market beta, and then within each beta portfolio, they are sorted into 25 portfolios based on MAX. The final MAX $^\beta$ portfolios are formed by aggregating portfolios with the same MAX ranking across the beta portfolios. The table reports results from portfolio-level cross-sectional Fama-MacBeth regressions. The dependent variable is a portfolio-level indicator that takes a value of one (minus one) if the portfolio belongs to the top (bottom) quintile of MAX or MAX $^\beta$ , and zero otherwise. The independent variables include the portfolio-level value-weighted averages of MIS, the stock-level equity issuance index (see Section 3.4.2 and Table 5 for definition), E(ISKEW), and INST. Additional control variables are portfolio-level value-weighted averages of SIZE, B/M, ROE, I/A, and MOM. Newey and West (1987) $t$ -statistics (adjusted with five lags) are reported in parentheses. The sample period spans April 1980 to December 2022.

<table>
  <thead>
    <tr>
      <th rowspan="2">68</th>
      <th colspan="12">Panel A: MAX</th>
    </tr>
    <tr>
      <th>(1a)</th>
      <th>(1b)</th>
      <th>(2a)</th>
      <th>(2b)</th>
      <th>(3a)</th>
      <th>(3b)</th>
      <th>(4a)</th>
      <th>(4b)</th>
      <th>(5a)</th>
      <th>(5b)</th>
      <th>(6a)</th>
      <th>(6b)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>MIS</td>
      <td>0.064<br>(48.48)</td>
      <td>0.024<br>(12.50)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.048<br>(23.67)</td>
      <td>0.021<br>(10.64)</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Issuance</td>
      <td></td>
      <td></td>
      <td>0.034<br>(32.86)</td>
      <td>0.009<br>(9.34)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.026<br>(20.83)</td>
      <td>0.008<br>(8.24)</td>
    </tr>
    <tr>
      <td>E(ISKEW)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.040<br>(0.21)</td>
      <td>0.059<br>(0.57)</td>
      <td></td>
      <td></td>
      <td>-0.309<br>(-1.97)</td>
      <td>-0.048<br>(-0.45)</td>
      <td>-0.210<br>(-1.32)</td>
      <td>-0.019<br>(-0.19)</td>
    </tr>
    <tr>
      <td>INST</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.507<br>(2.37)</td>
      <td>-0.376<br>(-3.43)</td>
      <td>0.023<br>(0.19)</td>
      <td>-0.348<br>(-3.37)</td>
      <td>-0.256<br>(-1.69)</td>
      <td>-0.448<br>(-4.03)</td>
    </tr>
    <tr>
      <td>Intercept</td>
      <td>-2.828<br>(-43.53)</td>
      <td>1.314<br>(4.13)</td>
      <td>-1.535<br>(-31.34)</td>
      <td>2.438<br>(9.10)</td>
      <td>0.032<br>(0.24)</td>
      <td>2.899<br>(10.51)</td>
      <td>-0.546<br>(-4.18)</td>
      <td>3.783<br>(12.13)</td>
      <td>-1.953<br>(-12.53)</td>
      <td>1.318<br>(3.58)</td>
      <td>-0.905<br>(-4.94)</td>
      <td>2.165<br>(6.43)</td>
    </tr>
    <tr>
      <td>Control variables</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
    </tr>
    <tr>
      <td> $R^2$ </td>
      <td>36.11%</td>
      <td>64.60%</td>
      <td>32.54%</td>
      <td>64.09%</td>
      <td>23.42%</td>
      <td>65.21%</td>
      <td>9.13%</td>
      <td>63.33%</td>
      <td>48.92%</td>
      <td>70.21%</td>
      <td>47.47%</td>
      <td>69.96%</td>
    </tr>
  </tbody>
</table>

<table>
  <thead>
    <tr>
      <th rowspan="2">69</th>
      <th colspan="12">Panel B: MAX $^\beta$ </th>
    </tr>
    <tr>
      <th>(1a)</th>
      <th>(1b)</th>
      <th>(2a)</th>
      <th>(2b)</th>
      <th>(3a)</th>
      <th>(3b)</th>
      <th>(4a)</th>
      <th>(4b)</th>
      <th>(5a)</th>
      <th>(5b)</th>
      <th>(6a)</th>
      <th>(6b)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>MIS</td>
      <td>0.064<br>(52.78)</td>
      <td>0.008<br>(4.12)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.045<br>(25.25)</td>
      <td>0.005<br>(2.33)</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Issuance</td>
      <td></td>
      <td></td>
      <td>0.033<br>(26.71)</td>
      <td>0.003<br>(0.34)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.024<br>(18.87)</td>
      <td>0.003<br>(3.25)</td>
    </tr>
    <tr>
      <td>E(ISKEW)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.851<br>(4.84)</td>
      <td>0.464<br>(4.93)</td>
      <td></td>
      <td></td>
      <td>0.233<br>(1.52)</td>
      <td>0.255<br>(2.61)</td>
      <td>0.297<br>(1.95)</td>
      <td>0.264<br>(2.68)</td>
    </tr>
    <tr>
      <td>INST</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>-0.408<br>(-1.43)</td>
      <td>-1.022<br>(-9.15)</td>
      <td>-0.513<br>(-2.88)</td>
      <td>-0.938<br>(-7.38)</td>
      <td>-0.700<br>(-3.35)</td>
      <td>-0.973<br>(-7.87)</td>
    </tr>
    <tr>
      <td>Intercept</td>
      <td>-2.803<br>(-47.44)</td>
      <td>5.143<br>(19.33)</td>
      <td>-1.451<br>(-25.96)</td>
      <td>5.579<br>(21.73)</td>
      <td>-0.616<br>(-4.72)</td>
      <td>4.878<br>(18.29)</td>
      <td>-0.104<br>(-0.63)</td>
      <td>6.671<br>(27.04)</td>
      <td>-2.006<br>(-11.88)</td>
      <td>5.226<br>(14.41)</td>
      <td>-1.050<br>(-5.07)</td>
      <td>5.372<br>(15.77)</td>
    </tr>
    <tr>
      <td>Control variables</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
    </tr>
    <tr>
      <td> $R^2$ </td>
      <td>29.27%</td>
      <td>62.86%</td>
      <td>27.50%</td>
      <td>62.72%</td>
      <td>20.98%</td>
      <td>64.14%</td>
      <td>12.24%</td>
      <td>63.27%</td>
      <td>44.02%</td>
      <td>69.37%</td>
      <td>44.68%</td>
      <td>69.33%</td>
    </tr>
  </tbody>
</table>

---

# Page 70

# Panel A: Long-short strategies

![image](image_1.png)

# Panel B: Individual legs

![image](image_2.png)

## Figure 1. Cumulative abnormal returns by holding horizon.

Panel A plots the cumulative FF6PS abnormal return $ CR(K) = K \cdot \alpha_K $ , in percent, for the MAX and MAX $^{\beta}$ long-short strategies as a function of the holding horizon $ K $ ; Panel B plots the same quantity for each of the four legs. The MAX $^{\beta}$ strategy cumulates steadily to roughly 2.8\% over two years, whereas the MAX strategy rises to about 0.8\% within the first several months and then fades to essentially zero and slightly negative, the hump-shaped profile of a correction. In Panel B the low-MAX $^{\beta}$ long leg accrues abnormal return steadily throughout the two-year window and is individually significant at every horizon, whereas the low-MAX long leg is insignificant throughout and the two short legs are flat or mean-reverting. The construction follows the calendar-time methodology of Table 12. The sample period spans January 1968 to December 2022.

---

# Page 71

# Internet Appendix

This Internet Appendix presents supplementary results and robustness checks that support the findings in the main paper. Section A reports the detailed robustness analyses and extensions summarized in Section 7 of the main paper. The appendix contains the following tables:

- **Table A1** examines the return performance of MAX-sorted portfolios conditional on prior MAX.
- **Table A2** presents the characteristics of high-MAX portfolios conditional on prior MAX, including mispricing scores, equity issuance, and $\beta^{MAX}$ .
- **Table A3** analyzes the return performance of MAX-sorted portfolios conditional on prior MAX, across subgroups of high vs. low market beta stocks and during periods of high vs. low investor sentiment.
- **Table A4** reports the characteristics of MAX-sorted portfolios conditional on prior MAX, across subgroups of high vs. low market beta stocks and during periods of high vs. low investor sentiment.
- **Table A5** reports the time-series averages of the cross-sectional median values of firm-specific characteristics of MAX $^\beta$ -sorted decile portfolios.
- **Table A6** investigates the return performance of MAX $^\beta$ -sorted portfolios conditional on prior MAX $^\beta$ .
- **Table A7** examines the cross-sectional pricing of MAX and MAX $^\beta$ across states of aggregate investor sentiment and aggregate equity issuance.
- **Table A8** examines the cross-sectional pricing of MAX and MAX $^\beta$ conditional on size-orthogonalized institutional ownership levels.
- **Table A9** investigates the roles of mispricing, equity issuance, and expected idiosyncratic skewness in driving MAX and MAX $^\beta$ conditional on institutional ownership levels.
- **Table A10** reports the robustness of the long-short MAX $^\beta$ strategy across subsamples formed on firm size, share price, and Amihud (2002) liquidity.
- **Table A11** reports absolute Sharpe ratios and downside risk-adjusted returns (Value-at-Risk and Expected Shortfall) for the long-short MAX and MAX $^\beta$ portfolios and for benchmark characteristics.
- **Table A12** examines alternative proxies for lottery-like payoffs (the lottery index of Kumar (2009), MAX(1), MAX(95%), and MAX(99%)) and their market beta-neutralized counterparts, together with the stock-level MAX $^{\text{Treynor}}$ measure.
- **Table A13** reports firm-level cross-sectional regressions of one-month-ahead excess stock returns on MAX $^{\text{Treynor}}$ , controlling for mispricing, equity issuance, and standard firm characteristics.

i

---

# Page 72

# Table A1

**MAX, persistence, and portfolio returns:** This table investigates the relationship between MAX and portfolio returns, conditional on stocks’ prior MAX performance. Panel A reports contemporaneous excess returns (RET-RF) and FF6PS alphas for value-weighted decile portfolios formed by sorting stocks on MAX. Panel B reports one-month-ahead excess returns and FF6PS alphas for value-weighted high MAX portfolios (deciles 9 and 10), conditional on the stocks’ past MAX performance. The analysis classifies stocks based on their MAX history over different horizons. The leftmost columns condition on MAX in month $t - 1$ , dividing stocks into High (top 30th percentile), Low (bottom 30th percentile), and Mid (the remaining stocks) subgroups. The middle and rightmost columns condition on persistence over months $t - 1$ and $t - 2$ , and $t - 1$ through $t - 3$ , respectively. For the longer-term persistence measures, stocks are classified as “High” if they are in the top 30th percentile of MAX. The subgroups compare stocks that were consistently High across all prior months (e.g., High in $t - 1$ , $t - 2$ , and $t - 3$ ) against those that were Non-High (bottom 70th percentile) in at least one prior month. Panel C reports one-month-ahead excess returns and FF6PS alphas for value-weighted high MAX portfolios (deciles 9 and 10), conditional on the interaction between past MAX performance and investor sentiment. High (low) sentiment regimes are defined as periods in which the Baker and Wurgler (2006) investor sentiment index remains strictly above (below) its full-sample time-series median in every month of the specified window. We examine three conditioning sets where the sentiment window spans the historical MAX performance period through the current month $t$ : (i) MAX performance in $t - 1$ conditional on sentiment in months $t$ and $t - 1$ ; (ii) MAX performance over $t - 1$ and $t - 2$ conditional on sentiment in months $t$ through $t - 2$ ; and (iii) MAX performance over $t - 1$ through $t - 3$ conditional on sentiment in months $t$ through $t - 3$ . Newey and West (1987) $t$ -statistics (adjusted with six lags) are reported in parentheses. The sample period spans January 1968 to December 2022.

## Panel A: Contemporaneous excess returns and alphas of MAX portfolios

<table>
  <thead>
    <tr>
      <th></th>
      <th>Port 1</th>
      <th>2</th>
      <th>3</th>
      <th>4</th>
      <th>5</th>
      <th>6</th>
      <th>7</th>
      <th>8</th>
      <th>9</th>
      <th>10</th>
      <th>10-1 diff.</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>RET-RF</td>
      <td>-3.01</td>
      <td>-1.00</td>
      <td>0.34</td>
      <td>1.43</td>
      <td>2.42</td>
      <td>3.41</td>
      <td>4.43</td>
      <td>5.98</td>
      <td>8.99</td>
      <td>19.46</td>
      <td>22.47</td>
    </tr>
    <tr>
      <td></td>
      <td>(-13.07)</td>
      <td>(-4.83)</td>
      <td>(1.64)</td>
      <td>(7.22)</td>
      <td>(10.44)</td>
      <td>(13.64)</td>
      <td>(14.66)</td>
      <td>(16.70)</td>
      <td>(20.16)</td>
      <td>(24.88)</td>
      <td>(29.24)</td>
    </tr>
    <tr>
      <td>FF6PS</td>
      <td>-3.51</td>
      <td>-1.57</td>
      <td>0.25</td>
      <td>0.80</td>
      <td>1.82</td>
      <td>2.89</td>
      <td>3.94</td>
      <td>5.50</td>
      <td>8.55</td>
      <td>18.88</td>
      <td>22.40</td>
    </tr>
    <tr>
      <td></td>
      <td>(-18.43)</td>
      <td>(-12.77)</td>
      <td>(-2.41)</td>
      <td>(10.64)</td>
      <td>(19.37)</td>
      <td>(23.36)</td>
      <td>(25.96)</td>
      <td>(28.87)</td>
      <td>(35.30)</td>
      <td>(38.44)</td>
      <td>(38.32)</td>
    </tr>
  </tbody>
</table>

## Panel B: One-month-ahead returns conditional on past MAX persistence

<table>
  <thead>
    <tr>
      <th></th>
      <th>MAX $_t$ conditional on MAX $_{t-1}$ </th>
      <th>MAX $_t$ conditional on MAX $_{t-1,t-2}$ </th>
      <th>MAX $_t$ conditional on MAX $_{t-1,t-2,t-3}$ </th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td></td>
      <td>High</td>
      <td>Mid</td>
      <td>Low</td>
      <td>High &amp; High</td>
      <td>Non-high</td>
      <td>High &amp; High &amp; High</td>
      <td>Non-high</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Port 9</td>
      <td>-0.25</td>
      <td>-0.49</td>
      <td>0.17</td>
      <td>-0.27</td>
      <td>0.58</td>
      <td>-0.06</td>
      <td>-0.49</td>
      <td>-0.71</td>
      <td>0.30</td>
      <td>-0.18</td>
      <td>-0.52</td>
      <td>-0.66</td>
      <td>0.24</td>
      <td>-0.23</td>
    </tr>
    <tr>
      <td></td>
      <td>(-0.61)</td>
      <td>(-2.30)</td>
      <td>(0.60)</td>
      <td>(-1.95)</td>
      <td>(2.54)</td>
      <td>(-0.57)</td>
      <td>(-1.08)</td>
      <td>(-2.68)</td>
      <td>(1.04)</td>
      <td>(-1.59)</td>
      <td>(-1.01)</td>
      <td>(-2.02)</td>
      <td>(0.82)</td>
      <td>(-2.07)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-0.74</td>
      <td>-0.91</td>
      <td>0.08</td>
      <td>-0.27</td>
      <td>0.62</td>
      <td>0.11</td>
      <td>-0.96</td>
      <td>-1.09</td>
      <td>0.09</td>
      <td>-0.20</td>
      <td>-1.24</td>
      <td>-1.32</td>
      <td>0.01</td>
      <td>-0.30</td>
    </tr>
    <tr>
      <td></td>
      <td>(-1.66)</td>
      <td>(-3.47)</td>
      <td>(0.22)</td>
      <td>(-1.52)</td>
      <td>(2.17)</td>
      <td>(0.74)</td>
      <td>(-2.13)</td>
      <td>(-3.89)</td>
      <td>(0.29)</td>
      <td>(-1.34)</td>
      <td>(-2.57)</td>
      <td>(-4.00)</td>
      <td>(0.02)</td>
      <td>(-2.05)</td>
    </tr>
  </tbody>
</table>

---

# Page 73

# Appendix Table A1 (continued): MAX, persistence, and portfolio returns

## Panel C: One-month-ahead returns conditional on past MAX persistence and investor sentiment

### High investor sentiment

<table>
  <thead>
    <tr>
      <th></th>
      <th>MAX_t conditional on MAX_{t-1}</th>
      <th>MAX_t conditional on MAX_{t-1,t-2}</th>
      <th>MAX_t conditional on MAX_{t-1,t-2,t-3}</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td></td>
      <td>High</td>
      <td>Mid</td>
      <td>Low</td>
      <td>High &amp; High</td>
      <td>Non-high</td>
      <td>High &amp; High &amp; High</td>
      <td>Non-high</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Port 9</td>
      <td>-1.27</td>
      <td>-0.52</td>
      <td>-0.31</td>
      <td>-0.21</td>
      <td>0.36</td>
      <td>-0.19</td>
      <td>-1.74</td>
      <td>-0.79</td>
      <td>-0.21</td>
      <td>-0.12</td>
      <td>-1.90</td>
      <td>-0.47</td>
      <td>-0.49</td>
      <td>-0.21</td>
    </tr>
    <tr>
      <td></td>
      <td>(-2.05)</td>
      <td>(-1.69)</td>
      <td>(-0.71)</td>
      <td>(-0.94)</td>
      <td>(1.07)</td>
      <td>(-1.19)</td>
      <td>(-2.66)</td>
      <td>(-2.16)</td>
      <td>(-0.49)</td>
      <td>(-0.65)</td>
      <td>(-2.30)</td>
      <td>(-0.96)</td>
      <td>(-1.05)</td>
      <td>(-1.12)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-2.30</td>
      <td>-1.50</td>
      <td>-0.81</td>
      <td>-0.54</td>
      <td>0.25</td>
      <td>0.04</td>
      <td>-2.70</td>
      <td>-1.60</td>
      <td>-0.99</td>
      <td>-0.55</td>
      <td>-3.37</td>
      <td>-1.88</td>
      <td>-1.24</td>
      <td>-0.65</td>
    </tr>
    <tr>
      <td></td>
      <td>(-3.99)</td>
      <td>(-3.64)</td>
      <td>(-1.64)</td>
      <td>(-1.90)</td>
      <td>(0.64)</td>
      <td>(0.18)</td>
      <td>(-4.32)</td>
      <td>(-3.85)</td>
      <td>(-2.10)</td>
      <td>(-2.40)</td>
      <td>(-5.10)</td>
      <td>(-4.03)</td>
      <td>(-2.44)</td>
      <td>(-2.75)</td>
    </tr>
  </tbody>
</table>


### Low investor sentiment

<table>
  <thead>
    <tr>
      <th></th>
      <th>MAX_t conditional on MAX_{t-1}</th>
      <th>MAX_t conditional on MAX_{t-1,t-2}</th>
      <th>MAX_t conditional on MAX_{t-1,t-2,t-3}</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td></td>
      <td>High</td>
      <td>Mid</td>
      <td>Low</td>
      <td>High &amp; High</td>
      <td>Non-high</td>
      <td>High &amp; High &amp; High</td>
      <td>Non-high</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Port 9</td>
      <td>0.61</td>
      <td>-0.50</td>
      <td>0.73</td>
      <td>-0.27</td>
      <td>0.88</td>
      <td>-0.02</td>
      <td>0.62</td>
      <td>-0.46</td>
      <td>0.73</td>
      <td>-0.30</td>
      <td>0.38</td>
      <td>-0.55</td>
      <td>0.65</td>
      <td>-0.32</td>
    </tr>
    <tr>
      <td></td>
      <td>(1.19)</td>
      <td>(-1.95)</td>
      <td>(1.92)</td>
      <td>(-1.76)</td>
      <td>(2.93)</td>
      <td>(-0.18)</td>
      <td>(1.03)</td>
      <td>(-1.38)</td>
      <td>(1.97)</td>
      <td>(-2.34)</td>
      <td>(0.59)</td>
      <td>(-1.33)</td>
      <td>(1.67)</td>
      <td>(-2.46)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>0.45</td>
      <td>-0.56</td>
      <td>0.95</td>
      <td>-0.01</td>
      <td>0.95</td>
      <td>0.02</td>
      <td>0.41</td>
      <td>-0.61</td>
      <td>0.93</td>
      <td>-0.01</td>
      <td>-0.16</td>
      <td>-1.03</td>
      <td>0.88</td>
      <td>0.01</td>
    </tr>
    <tr>
      <td></td>
      <td>(0.82)</td>
      <td>(-1.87)</td>
      <td>(2.24)</td>
      <td>(-0.03)</td>
      <td>(2.33)</td>
      <td>(0.13)</td>
      <td>(0.76)</td>
      <td>(-1.72)</td>
      <td>(2.29)</td>
      <td>(-0.08)</td>
      <td>(-0.27)</td>
      <td>(-2.53)</td>
      <td>(2.13)</td>
      <td>(0.12)</td>
    </tr>
  </tbody>
</table>

---

# Page 74

# Table A2

**MAX, persistence, and portfolio characteristics:** This table investigates the characteristics of high MAX portfolios (deciles 9 and 10), conditional on stocks’ prior MAX performance. The table reports the time-series averages of the cross-sectional medians for three characteristics: the aggregate mispricing score (MIS) of Stambaugh, Yu, and Yuan (2015); firm-level composite equity issuance (CE), defined as the 12-month growth in equity market capitalization minus the 12-month cumulative stock return; and $\beta^{MAX}$ , the sensitivity of stock-level MAX to the market MAX estimated via 12-month rolling regressions. Panel A reports characteristics for subgroups formed based on historical MAX performance in: (i) month $t-1$ ; (ii) months $t-1$ and $t-2$ ; and (iii) months $t-1$ through $t-3$ . The classification of stocks into High (top 30th percentile), Mid, and Low (bottom 30th percentile) subgroups follows the methodology described in Panel B of Table A1. Panel B reports portfolio characteristics conditional on investor sentiment. The definitions of high and low investor sentiment regimes, and their specific alignment with the historical MAX performance windows, are identical to those described in Panel C of Table A1. Newey and West (1987) $t$ -statistics (adjusted with six lags) are reported in parentheses. The sample period spans January 1968 to December 2022.

## Panel A: Characteristics of high MAX decile portfolios conditional on past MAX persistence

<table>
  <thead>
    <tr>
      <th rowspan="3">A1</th>
      <th colspan="3">MAX conditional on MAX $_{t-1}$ </th>
      <th colspan="3">MAX conditional on MAX $_{t-1,t-2}$ </th>
      <th colspan="3">MAX conditional on MAX $_{t-1,t-2,t-3}$ </th>
    </tr>
    <tr>
      <th colspan="2">High</th>
      <th colspan="2">Mid</th>
      <th colspan="2">Low</th>
      <th colspan="2">High & High</th>
      <th colspan="2">Non-high</th>
      <th colspan="2">High & High & High</th>
      <th colspan="2">Non-high</th>
    </tr>
    <tr>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 9</td>
      <td>56.27</td>
      <td>0.019</td>
      <td>1.302</td>
      <td>51.61</td>
      <td>0.004</td>
      <td>1.152</td>
      <td>48.00</td>
      <td>-0.009</td>
      <td>0.876</td>
      <td>56.53</td>
      <td>0.023</td>
      <td>1.352</td>
      <td>51.65</td>
      <td>0.004</td>
      <td>1.134</td>
      <td>56.87</td>
      <td>0.026</td>
      <td>1.356</td>
      <td>52.13</td>
      <td>0.005</td>
      <td>1.154</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>56.94</td>
      <td>0.021</td>
      <td>1.196</td>
      <td>53.53</td>
      <td>0.009</td>
      <td>1.190</td>
      <td>50.18</td>
      <td>-0.002</td>
      <td>0.912</td>
      <td>57.24</td>
      <td>0.026</td>
      <td>1.172</td>
      <td>53.69</td>
      <td>0.008</td>
      <td>1.165</td>
      <td>57.18</td>
      <td>0.031</td>
      <td>1.149</td>
      <td>54.24</td>
      <td>0.009</td>
      <td>1.181</td>
    </tr>
  </tbody>
</table>

---

# Page 75

# Appendix Table A2 — Continued: Panel B

## Panel B: Characteristics of high MAX decile portfolios conditional on past MAX persistence and investor sentiment

### High investor sentiment

<table>
  <thead>
    <tr>
      <th rowspan="3"></th>
      <th colspan="6">MAX conditional on MAX $_{t-1}$ </th>
      <th colspan="6">MAX conditional on MAX $_{t-1,t-2}$ </th>
      <th colspan="6">MAX conditional on MAX $_{t-1,t-2,t-3}$ </th>
    </tr>
    <tr>
      <th colspan="2">High</th>
      <th colspan="2">Mid</th>
      <th colspan="2">Low</th>
      <th colspan="2">High & High</th>
      <th colspan="2">Non-high</th>
      <th colspan="2">High & High & High</th>
      <th colspan="2">Non-high</th>
    </tr>
    <tr>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 9</td>
      <td>51.01</td>
      <td>0.007</td>
      <td>1.057</td>
      <td>52.15</td>
      <td>0.011</td>
      <td>1.118</td>
      <td>48.17</td>
      <td>-0.002</td>
      <td>0.871</td>
      <td>57.12</td>
      <td>0.030</td>
      <td>1.410</td>
      <td>52.20</td>
      <td>0.010</td>
      <td>1.099</td>
      <td>57.42</td>
      <td>0.033</td>
      <td>1.424</td>
      <td>52.72</td>
      <td>0.012</td>
      <td>1.133</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>53.39</td>
      <td>0.012</td>
      <td>1.132</td>
      <td>54.28</td>
      <td>0.016</td>
      <td>1.188</td>
      <td>50.73</td>
      <td>0.003</td>
      <td>0.957</td>
      <td>58.07</td>
      <td>0.032</td>
      <td>1.233</td>
      <td>54.47</td>
      <td>0.014</td>
      <td>1.166</td>
      <td>58.32</td>
      <td>0.038</td>
      <td>1.260</td>
      <td>55.09</td>
      <td>0.016</td>
      <td>1.196</td>
    </tr>
  </tbody>
</table>

### Low investor sentiment

<table>
  <thead>
    <tr>
      <th rowspan="3"></th>
      <th colspan="6">MAX conditional on MAX $_{t-1}$ </th>
      <th colspan="6">MAX conditional on MAX $_{t-1,t-2}$ </th>
      <th colspan="6">MAX conditional on MAX $_{t-1,t-2,t-3}$ </th>
    </tr>
    <tr>
      <th colspan="2">High</th>
      <th colspan="2">Mid</th>
      <th colspan="2">Low</th>
      <th colspan="2">High & High</th>
      <th colspan="2">Non-high</th>
      <th colspan="2">High & High & High</th>
      <th colspan="2">Non-high</th>
    </tr>
    <tr>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 9</td>
      <td>50.23</td>
      <td>-0.004</td>
      <td>1.144</td>
      <td>51.07</td>
      <td>-0.002</td>
      <td>1.198</td>
      <td>47.86</td>
      <td>-0.013</td>
      <td>0.990</td>
      <td>55.82</td>
      <td>0.016</td>
      <td>1.322</td>
      <td>51.09</td>
      <td>-0.002</td>
      <td>1.186</td>
      <td>56.28</td>
      <td>0.018</td>
      <td>1.335</td>
      <td>51.50</td>
      <td>-0.001</td>
      <td>1.216</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>52.06</td>
      <td>0.000</td>
      <td>1.167</td>
      <td>52.75</td>
      <td>0.001</td>
      <td>1.214</td>
      <td>49.89</td>
      <td>-0.006</td>
      <td>1.019</td>
      <td>56.33</td>
      <td>0.019</td>
      <td>1.132</td>
      <td>52.90</td>
      <td>0.001</td>
      <td>1.180</td>
      <td>55.99</td>
      <td>0.084</td>
      <td>1.149</td>
      <td>53.37</td>
      <td>0.002</td>
      <td>1.205</td>
    </tr>
  </tbody>
</table>

---

# Page 76

# Table A3

MAX, persistence, and portfolio returns conditional on market beta: This table investigates the relationship between MAX and portfolio returns for stocks with high and low market beta. The sample is divided into two subgroups—High and Low—based on whether a stock’s market beta in month $ t $ is above or below the cross-sectional median. Panel A reports contemporaneous excess returns (RET-RF) and FF6PS alphas for value-weighted decile portfolios formed by sorting stocks on MAX within each market beta subgroup. Panel B reports one-month-ahead excess returns and FF6PS alphas for value-weighted high MAX portfolios (deciles 9 and 10) within each market beta subgroup, conditional on the stocks’ past MAX performance. The classification of stocks based on their MAX history (High, Mid, and Low) follows the methodology described in Panel B of Table A1. Panel C reports one-month-ahead excess returns and FF6PS alphas for value-weighted high MAX portfolios (deciles 9 and 10) within each market beta subgroup, conditional on the interaction between past MAX performance and investor sentiment. The definitions of high and low investor sentiment regimes, and their specific alignment with the historical MAX performance windows, are identical to those described in Panel C of Table A1. Newey and West (1987) $ t $ -statistics (adjusted with six lags) are reported in parentheses. The sample period spans January 1968 to December 2022.

## Panel A: Contemporaneous excess returns and alphas of MAX portfolios

### High market beta stocks

<table>
  <thead>
    <tr>
      <th></th>
      <th>Port 1</th>
      <th>2</th>
      <th>3</th>
      <th>4</th>
      <th>5</th>
      <th>6</th>
      <th>7</th>
      <th>8</th>
      <th>9</th>
      <th>10</th>
      <th>10-1 diff.</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>RET-RF</td>
      <td>-2.81</td>
      <td>-0.62</td>
      <td>0.54</td>
      <td>1.86</td>
      <td>2.62</td>
      <td>3.58</td>
      <td>4.64</td>
      <td>6.47</td>
      <td>9.34</td>
      <td>19.83</td>
      <td>22.64</td>
    </tr>
    <tr>
      <td></td>
      <td>(-13.03)</td>
      <td>(-2.81)</td>
      <td>(2.35)</td>
      <td>(7.75)</td>
      <td>(9.45)</td>
      <td>(11.38)</td>
      <td>(13.50)</td>
      <td>(16.02)</td>
      <td>(18.49)</td>
      <td>(25.47)</td>
      <td>(31.20)</td>
    </tr>
    <tr>
      <td>FF6PS</td>
      <td>-3.36</td>
      <td>-1.15</td>
      <td>-0.07</td>
      <td>1.34</td>
      <td>2.12</td>
      <td>3.09</td>
      <td>4.08</td>
      <td>5.94</td>
      <td>8.92</td>
      <td>19.30</td>
      <td>22.66</td>
    </tr>
    <tr>
      <td></td>
      <td>(-24.50)</td>
      <td>(-10.67)</td>
      <td>(-0.62)</td>
      <td>(9.51)</td>
      <td>(13.62)</td>
      <td>(16.36)</td>
      <td>(21.45)</td>
      <td>(24.68)</td>
      <td>(27.26)</td>
      <td>(35.36)</td>
      <td>(37.94)</td>
    </tr>
  </tbody>
</table>

### Low market beta stocks

<table>
  <thead>
    <tr>
      <th></th>
      <th>Port 1</th>
      <th>2</th>
      <th>3</th>
      <th>4</th>
      <th>5</th>
      <th>6</th>
      <th>7</th>
      <th>8</th>
      <th>9</th>
      <th>10</th>
      <th>10-1 diff.</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>RET-RF</td>
      <td>-3.25</td>
      <td>-1.42</td>
      <td>-0.11</td>
      <td>1.07</td>
      <td>2.15</td>
      <td>3.28</td>
      <td>4.74</td>
      <td>6.33</td>
      <td>9.39</td>
      <td>20.42</td>
      <td>23.67</td>
    </tr>
    <tr>
      <td></td>
      <td>(-14.25)</td>
      <td>(-6.79)</td>
      <td>(-0.60)</td>
      <td>(5.52)</td>
      <td>(10.94)</td>
      <td>(16.20)</td>
      <td>(20.69)</td>
      <td>(24.24)</td>
      <td>(27.71)</td>
      <td>(23.79)</td>
      <td>(27.80)</td>
    </tr>
    <tr>
      <td>FF6PS</td>
      <td>-3.74</td>
      <td>-1.95</td>
      <td>-0.71</td>
      <td>0.43</td>
      <td>1.46</td>
      <td>2.58</td>
      <td>3.95</td>
      <td>5.60</td>
      <td>8.65</td>
      <td>19.42</td>
      <td>23.16</td>
    </tr>
    <tr>
      <td></td>
      <td>(-18.41)</td>
      <td>(-12.34)</td>
      <td>(-5.56)</td>
      <td>(3.72)</td>
      <td>(12.53)</td>
      <td>(23.43)</td>
      <td>(34.46)</td>
      <td>(36.44)</td>
      <td>(37.99)</td>
      <td>(30.27)</td>
      <td>(33.22)</td>
    </tr>
  </tbody>
</table>

---

# Page 77

# Appendix Table A3 – Continued: Panel B

## Panel B: One-month-ahead returns conditional on past MAX persistence

### High market beta stocks

<table>
  <thead>
    <tr>
      <th rowspan="3">Port</th>
      <th colspan="6">MAX$_{t-1}$</th>
      <th colspan="6">MAX$_{t-1,t-2}$</th>
      <th colspan="6">MAX$_{t-1,t-2,t-3}$</th>
    </tr>
    <tr>
      <th colspan="2">High</th>
      <th colspan="2">Mid</th>
      <th colspan="2">Low</th>
      <th colspan="2">High & High</th>
      <th colspan="2">Non-high</th>
      <th colspan="2">High & High & High</th>
      <th colspan="2">Non-high</th>
    </tr>
    <tr>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 9</td>
      <td>-0.32</td>
      <td>-0.58</td>
      <td>0.31</td>
      <td>-0.09</td>
      <td>1.02</td>
      <td>0.56</td>
      <td>-0.58</td>
      <td>-0.79</td>
      <td>0.35</td>
      <td>0.00</td>
      <td>-0.34</td>
      <td>-0.47</td>
      <td>0.30</td>
      <td>-0.03</td>
    </tr>
    <tr>
      <td></td>
      <td>(-0.75)</td>
      <td>(-2.44)</td>
      <td>(0.86)</td>
      <td>(-0.50)</td>
      <td>(3.52)</td>
      <td>(2.74)</td>
      <td>(-1.09)</td>
      <td>(-2.51)</td>
      <td>(1.05)</td>
      <td>(0.05)</td>
      <td>(-0.58)</td>
      <td>(-1.23)</td>
      <td>(0.87)</td>
      <td>(-0.21)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-0.41</td>
      <td>-0.58</td>
      <td>-0.18</td>
      <td>-0.58</td>
      <td>0.57</td>
      <td>0.12</td>
      <td>-0.55</td>
      <td>-0.50</td>
      <td>0.03</td>
      <td>-0.36</td>
      <td>-1.10</td>
      <td>-0.94</td>
      <td>-0.06</td>
      <td>-0.46</td>
    </tr>
    <tr>
      <td></td>
      <td>(-0.82)</td>
      <td>(-2.22)</td>
      <td>(-0.50)</td>
      <td>(-2.86)</td>
      <td>(1.73)</td>
      <td>(0.59)</td>
      <td>(-1.06)</td>
      <td>(-1.54)</td>
      <td>(0.09)</td>
      <td>(-2.06)</td>
      <td>(-2.06)</td>
      <td>(-2.49)</td>
      <td>(-0.17)</td>
      <td>(-2.59)</td>
    </tr>
  </tbody>
</table>

### Low market beta stocks

<table>
  <thead>
    <tr>
      <th rowspan="3">Port</th>
      <th colspan="6">MAX$_{t-1}$</th>
      <th colspan="6">MAX$_{t-1,t-2}$</th>
      <th colspan="6">MAX$_{t-1,t-2,t-3}$</th>
    </tr>
    <tr>
      <th colspan="2">High</th>
      <th colspan="2">Mid</th>
      <th colspan="2">Low</th>
      <th colspan="2">High & High</th>
      <th colspan="2">Non-high</th>
      <th colspan="2">High & High & High</th>
      <th colspan="2">Non-high</th>
    </tr>
    <tr>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 9</td>
      <td>0.15</td>
      <td>-0.60</td>
      <td>0.24</td>
      <td>-0.62</td>
      <td>0.72</td>
      <td>0.01</td>
      <td>-0.15</td>
      <td>-0.98</td>
      <td>0.36</td>
      <td>-0.43</td>
      <td>-0.09</td>
      <td>-1.02</td>
      <td>0.25</td>
      <td>-0.52</td>
    </tr>
    <tr>
      <td></td>
      <td>(0.45)</td>
      <td>(-2.04)</td>
      <td>(1.04)</td>
      <td>(-3.76)</td>
      <td>(3.55)</td>
      <td>(0.07)</td>
      <td>(-0.43)</td>
      <td>(-3.42)</td>
      <td>(1.68)</td>
      <td>(-3.49)</td>
      <td>(-0.22)</td>
      <td>(-2.62)</td>
      <td>(1.13)</td>
      <td>(-3.97)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-0.27</td>
      <td>-1.00</td>
      <td>0.16</td>
      <td>-0.52</td>
      <td>0.38</td>
      <td>-0.37</td>
      <td>-0.41</td>
      <td>-1.09</td>
      <td>0.15</td>
      <td>-0.53</td>
      <td>-0.97</td>
      <td>-1.73</td>
      <td>0.16</td>
      <td>-0.49</td>
    </tr>
    <tr>
      <td></td>
      <td>(-0.68)</td>
      <td>(-2.74)</td>
      <td>(0.63)</td>
      <td>(-2.82)</td>
      <td>(1.46)</td>
      <td>(-2.14)</td>
      <td>(-0.76)</td>
      <td>(-2.04)</td>
      <td>(0.63)</td>
      <td>(-2.97)</td>
      <td>(-1.75)</td>
      <td>(-3.59)</td>
      <td>(0.69)</td>
      <td>(-2.68)</td>
    </tr>
  </tbody>
</table>

---

# Page 78

# Appendix Table A3 – Continued: Panel C

## Panel C: One-month-ahead returns conditional on past MAX persistence and investor sentiment

### High market beta stocks during high investor sentiment regime

<table>
  <thead>
    <tr>
      <th></th>
      <th>MAX_{t-1}</th>
      <th>MAX_{t-1,t-2}</th>
      <th>MAX_{t-1,t-2,t-3}</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td></td>
      <td>High</td>
      <td>Mid</td>
      <td>Low</td>
      <td>High &amp; High</td>
      <td>Non-high</td>
      <td>High &amp; High &amp; High</td>
      <td>Non-high</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Port 9</td>
      <td>-1.25</td>
      <td>-0.53</td>
      <td>-0.38</td>
      <td>-0.09</td>
      <td>0.64</td>
      <td>0.48</td>
      <td>-1.58</td>
      <td>-0.55</td>
      <td>-0.36</td>
      <td>0.06</td>
      <td>-1.86</td>
      <td>-0.33</td>
      <td>-0.68</td>
      <td>-0.07</td>
    </tr>
    <tr>
      <td></td>
      <td>(-2.09)</td>
      <td>(-1.46)</td>
      <td>(-0.73)</td>
      <td>(-0.35)</td>
      <td>(1.48)</td>
      <td>(1.64)</td>
      <td>(-1.97)</td>
      <td>(-1.06)</td>
      <td>(-0.72)</td>
      <td>(0.27)</td>
      <td>(-1.85)</td>
      <td>(-0.45)</td>
      <td>(-1.33)</td>
      <td>(-0.35)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-1.84</td>
      <td>-0.97</td>
      <td>-1.02</td>
      <td>-0.72</td>
      <td>0.01</td>
      <td>-0.05</td>
      <td>-2.29</td>
      <td>-0.81</td>
      <td>-1.08</td>
      <td>-0.70</td>
      <td>-3.10</td>
      <td>-1.22</td>
      <td>-1.24</td>
      <td>-0.69</td>
    </tr>
    <tr>
      <td></td>
      <td>(-2.70)</td>
      <td>(-2.32)</td>
      <td>(-1.95)</td>
      <td>(-2.43)</td>
      <td>(0.03)</td>
      <td>(-0.16)</td>
      <td>(-2.90)</td>
      <td>(-1.42)</td>
      <td>(-2.01)</td>
      <td>(-2.46)</td>
      <td>(-4.05)</td>
      <td>(-2.05)</td>
      <td>(-2.17)</td>
      <td>(-2.27)</td>
    </tr>
  </tbody>
</table>


### Low market beta stocks during high investor sentiment regime

<table>
  <thead>
    <tr>
      <th></th>
      <th>MAX_{t-1}</th>
      <th>MAX_{t-1,t-2}</th>
      <th>MAX_{t-1,t-2,t-3}</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td></td>
      <td>High</td>
      <td>Mid</td>
      <td>Low</td>
      <td>High &amp; High</td>
      <td>Non-high</td>
      <td>High &amp; High &amp; High</td>
      <td>Non-high</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Port 9</td>
      <td>-0.44</td>
      <td>-0.76</td>
      <td>0.27</td>
      <td>-0.53</td>
      <td>0.59</td>
      <td>-0.15</td>
      <td>-0.90</td>
      <td>-1.19</td>
      <td>0.27</td>
      <td>-0.41</td>
      <td>-1.01</td>
      <td>-1.29</td>
      <td>0.06</td>
      <td>-0.54</td>
    </tr>
    <tr>
      <td></td>
      <td>(-0.96)</td>
      <td>(-1.89)</td>
      <td>(0.77)</td>
      <td>(-1.99)</td>
      <td>(2.09)</td>
      <td>(-0.76)</td>
      <td>(-1.81)</td>
      <td>(-2.51)</td>
      <td>(0.85)</td>
      <td>(-2.00)</td>
      <td>(-1.88)</td>
      <td>(-2.55)</td>
      <td>(0.18)</td>
      <td>(-2.57)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-1.28</td>
      <td>-1.57</td>
      <td>-0.14</td>
      <td>-0.66</td>
      <td>0.43</td>
      <td>-0.28</td>
      <td>-1.86</td>
      <td>-1.86</td>
      <td>-0.08</td>
      <td>-0.50</td>
      <td>-2.77</td>
      <td>-2.51</td>
      <td>-0.28</td>
      <td>-0.52</td>
    </tr>
    <tr>
      <td></td>
      <td>(-2.78)</td>
      <td>(-3.85)</td>
      <td>(-0.42)</td>
      <td>(-2.59)</td>
      <td>(1.23)</td>
      <td>(-1.27)</td>
      <td>(-3.39)</td>
      <td>(-3.41)</td>
      <td>(-0.25)</td>
      <td>(-1.88)</td>
      <td>(-4.16)</td>
      <td>(-3.92)</td>
      <td>(-0.80)</td>
      <td>(-1.88)</td>
    </tr>
  </tbody>
</table>


### High market beta stocks during low investor sentiment regime

<table>
  <thead>
    <tr>
      <th></th>
      <th>MAX_{t-1}</th>
      <th>MAX_{t-1,t-2}</th>
      <th>MAX_{t-1,t-2,t-3}</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td></td>
      <td>High</td>
      <td>Mid</td>
      <td>Low</td>
      <td>High &amp; High</td>
      <td>Non-high</td>
      <td>High &amp; High &amp; High</td>
      <td>Non-high</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Port 9</td>
      <td>0.53</td>
      <td>-0.59</td>
      <td>0.95</td>
      <td>-0.15</td>
      <td>1.44</td>
      <td>0.49</td>
      <td>0.22</td>
      <td>-0.89</td>
      <td>1.01</td>
      <td>-0.03</td>
      <td>0.50</td>
      <td>-0.49</td>
      <td>0.96</td>
      <td>0.01</td>
    </tr>
    <tr>
      <td></td>
      <td>(0.94)</td>
      <td>(-2.02)</td>
      <td>(2.05)</td>
      <td>(-0.74)</td>
      <td>(3.67)</td>
      <td>(1.94)</td>
      <td>(0.33)</td>
      <td>(-1.91)</td>
      <td>(2.32)</td>
      <td>(-0.22)</td>
      <td>(0.70)</td>
      <td>(-0.95)</td>
      <td>(2.09)</td>
      <td>(0.08)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>0.65</td>
      <td>-0.45</td>
      <td>0.70</td>
      <td>-0.35</td>
      <td>1.31</td>
      <td>0.34</td>
      <td>0.82</td>
      <td>-0.21</td>
      <td>0.82</td>
      <td>-0.25</td>
      <td>-0.42</td>
      <td>-1.18</td>
      <td>0.73</td>
      <td>-0.22</td>
    </tr>
    <tr>
      <td></td>
      <td>(1.11)</td>
      <td>(-1.40)</td>
      <td>(1.36)</td>
      <td>(-1.22)</td>
      <td>(2.95)</td>
      <td>(1.54)</td>
      <td>(1.41)</td>
      <td>(-0.54)</td>
      <td>(1.80)</td>
      <td>(-1.23)</td>
      <td>(-0.62)</td>
      <td>(-2.63)</td>
      <td>(1.56)</td>
      <td>(-1.07)</td>
    </tr>
  </tbody>
</table>


### Low market beta stocks during low investor sentiment regime

<table>
  <thead>
    <tr>
      <th></th>
      <th>MAX_{t-1}</th>
      <th>MAX_{t-1,t-2}</th>
      <th>MAX_{t-1,t-2,t-3}</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td></td>
      <td>High</td>
      <td>Mid</td>
      <td>Low</td>
      <td>High &amp; High</td>
      <td>Non-high</td>
      <td>High &amp; High &amp; High</td>
      <td>Non-high</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Port 9</td>
      <td>0.80</td>
      <td>-0.36</td>
      <td>0.38</td>
      <td>-0.60</td>
      <td>0.95</td>
      <td>0.09</td>
      <td>0.65</td>
      <td>-0.54</td>
      <td>0.57</td>
      <td>-0.37</td>
      <td>0.65</td>
      <td>-0.55</td>
      <td>0.52</td>
      <td>-0.37</td>
    </tr>
    <tr>
      <td></td>
      <td>(1.60)</td>
      <td>(-0.97)</td>
      <td>(1.20)</td>
      <td>(-2.95)</td>
      <td>(3.05)</td>
      <td>(0.46)</td>
      <td>(1.21)</td>
      <td>(-1.38)</td>
      <td>(1.90)</td>
      <td>(-

---

# Page 79

# Table A4

**MAX, persistence, and portfolio characteristics conditional on market beta:** This table investigates the characteristics of high MAX portfolios (deciles 9 and 10 formed within each market beta subgroup), conditional on stocks’ prior MAX performance. The sample is divided into two subgroups—High and Low—based on whether a stock’s market beta in month $t$ is above or below the cross-sectional median. The table reports the time-series averages of the cross-sectional medians for three characteristics: the aggregate mispricing score (MIS) of Stambaugh, Yu, and Yuan (2015); firm-level composite equity issuance (CE), defined as the 12-month growth in equity market capitalization minus the 12-month cumulative stock return; and $\beta^{MAX}$ , the sensitivity of stock-level MAX to the market MAX estimated via 12-month rolling regressions. Panel A reports the unconditional portfolio characteristics for these high MAX stocks within the high and low market beta subgroups. Panel B reports characteristics for subgroups within each market beta subset formed based on historical MAX performance in: (i) month $t-1$ ; (ii) months $t-1$ and $t-2$ ; and (iii) months $t-1$ through $t-3$ . The classification of stocks into High (top 30th percentile), Mid, and Low (bottom 30th percentile) subgroups follows the methodology described in Panel B of Table A1. Panel C reports portfolio characteristics conditional on investor sentiment. The definitions of high and low investor sentiment regimes, and their specific alignment with the historical MAX performance windows, are identical to those described in Panel C of Table A1. Newey and West (1987) $t$ -statistics (adjusted with six lags) are reported in parentheses. The sample period spans January 1968 to December 2022.

## Panel A: Characteristics of MAX sorted decile portfolios within high and low market beta subgroups

### High market beta stocks

<table>
  <thead>
    <tr>
      <th rowspan="2"></th>
      <th colspan="10">Port 1 2 3 4 5 6 7 8 9 10 10–1 diff.</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>MIS</td>
      <td>46.53</td>
      <td>46.87</td>
      <td>48.09</td>
      <td>49.16</td>
      <td>50.26</td>
      <td>51.26</td>
      <td>52.52</td>
      <td>53.78</td>
      <td>55.14</td>
      <td>57.21</td>
      <td>10.68</td>
    </tr>
    <tr>
      <td>CE</td>
      <td>-0.010</td>
      <td>-0.008</td>
      <td>-0.004</td>
      <td>-0.001</td>
      <td>0.002</td>
      <td>0.006</td>
      <td>0.009</td>
      <td>0.013</td>
      <td>0.017</td>
      <td>0.021</td>
      <td>0.031</td>
    </tr>
    <tr>
      <td> $\beta^{MAX}$ </td>
      <td>1.165</td>
      <td>1.174</td>
      <td>1.220</td>
      <td>1.264</td>
      <td>1.321</td>
      <td>1.352</td>
      <td>1.417</td>
      <td>1.459</td>
      <td>1.519</td>
      <td>1.555</td>
      <td>0.390</td>
    </tr>
  </tbody>
</table>

### Low market beta stocks

<table>
  <thead>
    <tr>
      <th rowspan="2"></th>
      <th colspan="10">Port 1 2 3 4 5 6 7 8 9 10 10–1 diff.</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>MIS</td>
      <td>43.93</td>
      <td>43.27</td>
      <td>43.90</td>
      <td>44.62</td>
      <td>45.47</td>
      <td>46.31</td>
      <td>47.24</td>
      <td>48.33</td>
      <td>49.49</td>
      <td>51.19</td>
      <td>7.26</td>
    </tr>
    <tr>
      <td>CE</td>
      <td>-0.022</td>
      <td>-0.023</td>
      <td>-0.021</td>
      <td>-0.018</td>
      <td>-0.015</td>
      <td>-0.013</td>
      <td>-0.010</td>
      <td>-0.007</td>
      <td>-0.004</td>
      <td>0.001</td>
      <td>0.023</td>
    </tr>
    <tr>
      <td> $\beta^{MAX}$ </td>
      <td>0.533</td>
      <td>0.593</td>
      <td>0.622</td>
      <td>0.631</td>
      <td>0.647</td>
      <td>0.656</td>
      <td>0.660</td>
      <td>0.662</td>
      <td>0.672</td>
      <td>0.622</td>
      <td>0.089</td>
    </tr>
  </tbody>
</table>

---

# Page 80

# Appendix Table A4 – Continued: Panel B

## Panel B: Characteristics of high MAX deciles within high and low market beta subgroups conditional on past MAX persistence

### High market beta stocks

<table>
  <thead>
    <tr>
      <th rowspan="3">×</th>
      <th colspan="3">MAX conditional on MAX $_{t-1}$ </th>
      <th colspan="3">MAX conditional on MAX $_{t-1,t-2}$ </th>
      <th colspan="3">MAX conditional on MAX $_{t-1,t-2,t-3}$ </th>
    </tr>
    <tr>
      <th colspan="2">High</th>
      <th colspan="2">Mid</th>
      <th colspan="2">Low</th>
      <th colspan="2">High & High</th>
      <th colspan="2">At least one period non-high</th>
      <th colspan="2">High & High & High</th>
      <th colspan="2">At least one period non-high</th>
    </tr>
    <tr>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 9</td>
      <td>57.69</td>
      <td>0.028</td>
      <td>1.623</td>
      <td>53.89</td>
      <td>0.014</td>
      <td>1.477</td>
      <td>50.97</td>
      <td>0.002</td>
      <td>1.337</td>
      <td>58.01</td>
      <td>0.035</td>
      <td>1.640</td>
      <td>53.87</td>
      <td>0.013</td>
      <td>1.468</td>
      <td>58.20</td>
      <td>0.045</td>
      <td>1.633</td>
      <td>54.27</td>
      <td>0.014</td>
      <td>1.487</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>58.50</td>
      <td>0.030</td>
      <td>1.590</td>
      <td>55.70</td>
      <td>0.018</td>
      <td>1.514</td>
      <td>53.42</td>
      <td>0.009</td>
      <td>1.419</td>
      <td>58.51</td>
      <td>0.038</td>
      <td>1.613</td>
      <td>55.99</td>
      <td>0.017</td>
      <td>1.520</td>
      <td>58.59</td>
      <td>0.048</td>
      <td>1.591</td>
      <td>56.49</td>
      <td>0.018</td>
      <td>1.535</td>
    </tr>
  </tbody>
</table>

### Low market beta stocks

<table>
  <thead>
    <tr>
      <th rowspan="3">×</th>
      <th colspan="3">MAX conditional on MAX $_{t-1}$ </th>
      <th colspan="3">MAX conditional on MAX $_{t-1,t-2}$ </th>
      <th colspan="3">MAX conditional on MAX $_{t-1,t-2,t-3}$ </th>
    </tr>
    <tr>
      <th colspan="2">High</th>
      <th colspan="2">Mid</th>
      <th colspan="2">Low</th>
      <th colspan="2">High & High</th>
      <th colspan="2">At least one period non-high</th>
      <th colspan="2">High & High & High</th>
      <th colspan="2">At least one period non-high</th>
    </tr>
    <tr>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 9</td>
      <td>51.46</td>
      <td>0.003</td>
      <td>0.681</td>
      <td>48.29</td>
      <td>-0.008</td>
      <td>0.687</td>
      <td>46.06</td>
      <td>-0.015</td>
      <td>0.643</td>
      <td>52.27</td>
      <td>0.007</td>
      <td>0.673</td>
      <td>48.29</td>
      <td>-0.008</td>
      <td>0.678</td>
      <td>52.67</td>
      <td>0.013</td>
      <td>0.686</td>
      <td>48.66</td>
      <td>-0.007</td>
      <td>0.682</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>52.76</td>
      <td>0.006</td>
      <td>0.562</td>
      <td>49.80</td>
      <td>-0.004</td>
      <td>0.665</td>
      <td>48.01</td>
      <td>-0.009</td>
      <td>0.631</td>
      <td>53.21</td>
      <td>0.013</td>
      <td>0.541</td>
      <td>50.12</td>
      <td>-0.004</td>
      <td>0.656</td>
      <td>53.14</td>
      <td>0.020</td>
      <td>0.543</td>
      <td>50.41</td>
      <td>-0.003</td>
      <td>0.659</td>
    </tr>
  </tbody>
</table>

---

# Page 81

# Appendix Table A4 – Continued: Panel C

## Panel C: Characteristics of high MAX deciles within high and low market beta subgroups conditional on past MAX persistence and investor sentiment

### High market beta stocks during high investor sentiment regime

<table>
  <thead>
    <tr>
      <th></th>
      <th>MAX conditional on MAX $_{t-1}$ </th>
      <th>MAX conditional on MAX $_{t-1,t-2}$ </th>
      <th>MAX conditional on MAX $_{t-1,t-2,t-3}$ </th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td></td>
      <td>High</td>
      <td>Mid</td>
      <td>Low</td>
      <td>High &amp; High</td>
      <td>At least one non-high</td>
      <td>High &amp; High &amp; High</td>
      <td>At least one non-high</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Port 9</td>
      <td>58.31</td>
      <td>0.036</td>
      <td>1.662</td>
      <td>54.48</td>
      <td>0.023</td>
      <td>1.472</td>
      <td>51.65</td>
      <td>0.009</td>
      <td>1.285</td>
      <td>59.21</td>
      <td>0.046</td>
      <td>1.723</td>
      <td>54.56</td>
      <td>0.022</td>
      <td>1.458</td>
      <td>59.77</td>
      <td>0.061</td>
      <td>1.709</td>
      <td>55.03</td>
      <td>0.023</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>59.32</td>
      <td>0.039</td>
      <td>1.701</td>
      <td>56.36</td>
      <td>0.027</td>
      <td>1.531</td>
      <td>54.21</td>
      <td>0.017</td>
      <td>1.427</td>
      <td>59.69</td>
      <td>0.051</td>
      <td>1.777</td>
      <td>56.73</td>
      <td>0.025</td>
      <td>1.552</td>
      <td>59.91</td>
      <td>0.063</td>
      <td>1.814</td>
      <td>57.39</td>
      <td>0.027</td>
    </tr>
  </tbody>
</table>

### Low market beta stocks during high investor sentiment regime

<table>
  <thead>
    <tr>
      <th></th>
      <th>MAX conditional on MAX $_{t-1}$ </th>
      <th>MAX conditional on MAX $_{t-1,t-2}$ </th>
      <th>MAX conditional on MAX $_{t-1,t-2,t-3}$ </th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td></td>
      <td>High</td>
      <td>Mid</td>
      <td>Low</td>
      <td>High &amp; High</td>
      <td>At least one non-high</td>
      <td>High &amp; High &amp; High</td>
      <td>At least one non-high</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Port 9</td>
      <td>51.69</td>
      <td>0.008</td>
      <td>0.656</td>
      <td>48.47</td>
      <td>-0.003</td>
      <td>0.640</td>
      <td>46.10</td>
      <td>-0.011</td>
      <td>0.584</td>
      <td>52.62</td>
      <td>0.012</td>
      <td>0.653</td>
      <td>48.43</td>
      <td>-0.002</td>
      <td>0.623</td>
      <td>53.02</td>
      <td>0.016</td>
      <td>0.674</td>
      <td>48.90</td>
      <td>-0.002</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>52.93</td>
      <td>0.007</td>
      <td>0.543</td>
      <td>50.11</td>
      <td>0.000</td>
      <td>0.610</td>
      <td>47.93</td>
      <td>-0.004</td>
      <td>0.578</td>
      <td>53.30</td>
      <td>0.010</td>
      <td>0.512</td>
      <td>50.51</td>
      <td>0.001</td>
      <td>0.620</td>
      <td>53.59</td>
      <td>0.014</td>
      <td>0.520</td>
      <td>50.85</td>
      <td>0.001</td>
    </tr>
  </tbody>
</table>

### High market beta stocks during low investor sentiment regime

<table>
  <thead>
    <tr>
      <th></th>
      <th>MAX conditional on MAX $_{t-1}$ </th>
      <th>MAX conditional on MAX $_{t-1,t-2}$ </th>
      <th>MAX conditional on MAX $_{t-1,t-2,t-3}$ </th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td></td>
      <td>High</td>
      <td>Mid</td>
      <td>Low</td>
      <td>High &amp; High</td>
      <td>At least one non-high</td>
      <td>High &amp; High &amp; High</td>
      <td>At least one non-high</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Port 9</td>
      <td>56.93</td>
      <td>0.018</td>
      <td>1.611</td>
      <td>53.28</td>
      <td>0.005</td>
      <td>1.506</td>
      <td>50.36</td>
      <td>-0.004</td>
      <td>1.394</td>
      <td>56.76</td>
      <td>0.024</td>
      <td>1.592</td>
      <td>53.17</td>
      <td>0.004</td>
      <td>1.512</td>
      <td>56.66</td>
      <td>0.028</td>
      <td>1.586</td>
      <td>53.48</td>
      <td>0.005</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>57.62</td>
      <td>0.020</td>
      <td>1.518</td>
      <td>55.04</td>
      <td>0.009</td>
      <td>1.532</td>
      <td>52.60</td>
      <td>0.002</td>
      <td>1.442</td>
      <td>57.43</td>
      <td>0.022</td>
      <td>1.491</td>
      <td>55.16</td>
      <td>0.008</td>
      <td>1.526</td>
      <td>57.48</td>
      <td>0.029</td>
      <td>1.426</td>
      <td>55.54</td>
      <td>0.009</td>
    </tr>
  </tbody>
</table>

### Low market beta stocks during low investor sentiment regime

<table>
  <thead>
    <tr>
      <th></th>
      <th>MAX conditional on MAX $_{t-1}$ </th>
      <th>MAX conditional on MAX $_{t-1,t-2}$ </th>
      <th>MAX conditional on MAX $_{t-1,t-2,t-3}$ </th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td></td>
      <td>High</td>
      <td>Mid</td>
      <td>Low</td>
      <td>High &amp; High</td>
      <td>At least one non-high</td>
      <td>High &amp; High &amp; High</td>
      <td>At least one non-high</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td>MIS</td>
      <td>CE</td>
      <td> $\beta^{MAX}$ </td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Port 9</td>
      <td>51.12</td>
      <td>-0.001</td>
      <td>0.706</td>
      <td>48.07</td>
      <td>-0.014</td>
      <td>0.745</td>
      <td>46.01</td>
      <td>-0.020</td>
      <td>0.710</td>
      <td>51.72</td>
      <td>0.001</td>
      <td>0.679</td>
      <td>48.10</td>
      <td>-0.014</td>
      <td>0.740</td>
      <td>52.13</td>
      <td>0.006</td>
      <td>0.734</td>
      <td>48.34</td>
      <td>-0.013</td>
    </tr>
    <tr>
      <td>Port 10</td>
     

---

# Page 82

Table A5

**Summary statistics for decile portfolios of stocks sorted by MAX $^{\beta}$ **: This table reports the time-series averages of the cross-sectional median values of firm-specific characteristics for decile portfolios sorted by $\beta^{\text{MAX}}$ . The characteristics include: MAX (the average of the five highest daily returns); market beta (BETA); the aggregate mispricing score (MIS) of Stambaugh, Yu, and Yuan (2015); composite equity issuance (CE), defined as the 12-month growth in equity market capitalization minus the 12-month cumulative stock return; $\beta^{\text{MAX}}$ , the sensitivity of stock-level MAX to the market MAX estimated via 12-month rolling regressions; institutional holdings (INST); the expected idiosyncratic skewness measure (E(ISKEW)) of Boyer, Mitton, and Vorkink (2010); market capitalization (SIZE); idiosyncratic volatility (IVOL); book-to-market ratio (BM); excess monthly return during the portfolio formation month (REV); intermediate-term momentum (MOM); Amihud (2002) illiquidity (ILLIQ); return on equity (ROE); and asset growth (I/A). The final row displays the average differences in characteristics between the highest (Decile 10) and lowest (Decile 1) $\beta^{\text{MAX}}$ portfolios. Newey and West (1987) $t$ -statistics (adjusted with six lags) are reported in parentheses. The sample period spans April 1980 to December 2022 for INST and E(ISKEW), and January 1968 to December 2022 for all other characteristics.

<table>
  <thead>
    <tr>
      <th>Decile</th>
      <th>MAX</th>
      <th>BETA</th>
      <th>MIS</th>
      <th>CE</th>
      <th> $\beta^{MAX}$ </th>
      <th>INST</th>
      <th>E(ISKEW)</th>
      <th>SIZE</th>
      <th>IVOL</th>
      <th>BM</th>
      <th>REV</th>
      <th>MOM</th>
      <th>ILLIQ</th>
      <th>ROE</th>
      <th>I/A</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 1</td>
      <td>0.011</td>
      <td>0.895</td>
      <td>45.95</td>
      <td>-0.012</td>
      <td>0.967</td>
      <td>0.587</td>
      <td>0.848</td>
      <td>1122</td>
      <td>1.886</td>
      <td>0.468</td>
      <td>-0.049</td>
      <td>0.123</td>
      <td>0.086</td>
      <td>0.121</td>
      <td>0.083</td>
    </tr>
    <tr>
      <td>2</td>
      <td>0.016</td>
      <td>0.895</td>
      <td>45.55</td>
      <td>-0.014</td>
      <td>0.923</td>
      <td>0.612</td>
      <td>0.806</td>
      <td>1096</td>
      <td>1.846</td>
      <td>0.470</td>
      <td>-0.027</td>
      <td>0.120</td>
      <td>0.069</td>
      <td>0.124</td>
      <td>0.086</td>
    </tr>
    <tr>
      <td>3</td>
      <td>0.020</td>
      <td>0.895</td>
      <td>46.10</td>
      <td>-0.012</td>
      <td>0.918</td>
      <td>0.609</td>
      <td>0.822</td>
      <td>887</td>
      <td>1.961</td>
      <td>0.477</td>
      <td>-0.015</td>
      <td>0.117</td>
      <td>0.081</td>
      <td>0.121</td>
      <td>0.087</td>
    </tr>
    <tr>
      <td>4</td>
      <td>0.023</td>
      <td>0.895</td>
      <td>46.68</td>
      <td>-0.010</td>
      <td>0.928</td>
      <td>0.600</td>
      <td>0.857</td>
      <td>708</td>
      <td>2.099</td>
      <td>0.488</td>
      <td>-0.006</td>
      <td>0.115</td>
      <td>0.100</td>
      <td>0.116</td>
      <td>0.089</td>
    </tr>
    <tr>
      <td>5</td>
      <td>0.026</td>
      <td>0.895</td>
      <td>47.52</td>
      <td>-0.007</td>
      <td>0.933</td>
      <td>0.586</td>
      <td>0.902</td>
      <td>570</td>
      <td>2.252</td>
      <td>0.496</td>
      <td>0.002</td>
      <td>0.110</td>
      <td>0.128</td>
      <td>0.112</td>
      <td>0.091</td>
    </tr>
    <tr>
      <td>6</td>
      <td>0.029</td>
      <td>0.895</td>
      <td>48.38</td>
      <td>-0.005</td>
      <td>0.939</td>
      <td>0.566</td>
      <td>0.957</td>
      <td>474</td>
      <td>2.420</td>
      <td>0.500</td>
      <td>0.011</td>
      <td>0.108</td>
      <td>0.160</td>
      <td>0.107</td>
      <td>0.095</td>
    </tr>
    <tr>
      <td>7</td>
      <td>0.034</td>
      <td>0.896</td>
      <td>49.18</td>
      <td>-0.002</td>
      <td>0.957</td>
      <td>0.540</td>
      <td>1.025</td>
      <td>379</td>
      <td>2.617</td>
      <td>0.507</td>
      <td>0.023</td>
      <td>0.106</td>
      <td>0.218</td>
      <td>0.100</td>
      <td>0.096</td>
    </tr>
    <tr>
      <td>8</td>
      <td>0.039</td>
      <td>0.896</td>
      <td>50.27</td>
      <td>-0.001</td>
      <td>0.969</td>
      <td>0.508</td>
      <td>1.086</td>
      <td>303</td>
      <td>2.849</td>
      <td>0.511</td>
      <td>0.039</td>
      <td>0.103</td>
      <td>0.304</td>
      <td>0.092</td>
      <td>0.097</td>
    </tr>
    <tr>
      <td>9</td>
      <td>0.048</td>
      <td>0.896</td>
      <td>51.51</td>
      <td>0.002</td>
      <td>0.995</td>
      <td>0.461</td>
      <td>1.166</td>
      <td>232</td>
      <td>3.171</td>
      <td>0.517</td>
      <td>0.066</td>
      <td>0.097</td>
      <td>0.454</td>
      <td>0.079</td>
      <td>0.095</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>0.069</td>
      <td>0.895</td>
      <td>53.40</td>
      <td>0.007</td>
      <td>1.003</td>
      <td>0.375</td>
      <td>1.299</td>
      <td>163</td>
      <td>3.872</td>
      <td>0.520</td>
      <td>0.150</td>
      <td>0.087</td>
      <td>0.835</td>
      <td>0.047</td>
      <td>0.079</td>
    </tr>
    <tr>
      <td>10–1 diff.</td>
      <td>0.058</td>
      <td>0.000</td>
      <td>7.45</td>
      <td>0.019</td>
      <td>0.036</td>
      <td>-0.212</td>
      <td>0.451</td>
      <td>-959</td>
      <td>1.986</td>
      <td>0.052</td>
      <td>0.199</td>
      <td>-0.036</td>
      <td>0.749</td>
      <td>-0.074</td>
      <td>-0.004</td>
    </tr>
    <tr>
      <td></td>
      <td>(44.99)</td>
      <td>(—)</td>
      <td>(18.52)</td>
      <td>(22.17)</td>
      <td>(0.39)</td>
      <td>(-24.77)</td>
      <td>(10.57)</td>
      <td>(-7.33)</td>
      <td>(28.02)</td>
      <td>(4.69)</td>
      <td>(36.73)</td>
      <td>(-1.84)</td>
      <td>(7.62)</td>
      <td>(-12.34)</td>
      <td>(-1.44)</td>
    </tr>
  </tbody>
</table>

---

# Page 83

# Table A6

**MAX $^\beta$ , persistence, and portfolio returns:** This table investigates the relationship between MAX $^\beta$ and portfolio returns, conditional on stocks' prior MAX $^\beta$ performance. Panel A reports contemporaneous excess returns (RET-RF) and FF6PS alphas for value-weighted decile portfolios formed by sorting stocks on MAX $^\beta$ . Panel B reports one-month-ahead excess returns and FF6PS alphas for value-weighted high MAX $^\beta$ portfolios (deciles 9 and 10), conditional on the stocks' past MAX $^\beta$ performance. The analysis classifies stocks based on their MAX $^\beta$ history over different horizons. The leftmost columns condition on MAX $^\beta$ in month $t-1$ , dividing stocks into High (top 30th percentile), Low (bottom 30th percentile), and Mid (the remaining stocks) subgroups. The middle and rightmost columns condition on persistence over months $t-1$ and $t-2$ , and $t-1$ through $t-3$ , respectively. For the longer-term persistence measures, stocks are classified as “High” if they are in the top 30th percentile of MAX $^\beta$ . The subgroups compare stocks that were consistently High across all prior months (e.g., High in $t-1$ , $t-2$ , and $t-3$ ) against those that were Non-High (bottom 70th percentile) in at least one prior month. Panel C reports one-month-ahead excess returns and FF6PS alphas for value-weighted high MAX $^\beta$ portfolios (deciles 9 and 10), conditional on the interaction between past MAX $^\beta$ performance and investor sentiment. High (low) sentiment regimes are defined as periods in which the Baker and Wurgler (2006) investor sentiment index remains strictly above (below) its full-sample time-series median in every month of the specified window. We examine three conditioning sets where the sentiment window spans the historical MAX $^\beta$ performance period through the current month $t$ : (i) MAX $^\beta$ performance in $t-1$ conditional on sentiment in months $t$ and $t-1$ ; (ii) MAX $^\beta$ performance over $t-1$ and $t-2$ conditional on sentiment in months $t$ through $t-2$ ; and (iii) MAX $^\beta$ performance over $t-1$ through $t-3$ conditional on sentiment in months $t$ through $t-3$ . Newey and West (1987) $t$ -statistics (adjusted with six lags) are reported in parentheses. The sample period spans January 1968 to December 2022.

## Panel A: Contemporaneous excess returns and alphas of MAX $^\beta$ portfolios

<table>
  <thead>
    <tr>
      <th></th>
      <th>Port 1</th>
      <th>2</th>
      <th>3</th>
      <th>4</th>
      <th>5</th>
      <th>6</th>
      <th>7</th>
      <th>8</th>
      <th>9</th>
      <th>10</th>
      <th>10-1 diff.</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>RET-RF</td>
      <td>-2.91</td>
      <td>-0.66</td>
      <td>0.70</td>
      <td>1.76</td>
      <td>2.85</td>
      <td>3.88</td>
      <td>5.35</td>
      <td>7.06</td>
      <td>9.92</td>
      <td>20.48</td>
      <td>23.41</td>
    </tr>
    <tr>
      <td></td>
      <td>(-13.51)</td>
      <td>(-3.22)</td>
      <td>(3.56)</td>
      <td>(8.23)</td>
      <td>(12.47)</td>
      <td>(15.09)</td>
      <td>(18.45)</td>
      <td>(20.42)</td>
      <td>(21.92)</td>
      <td>(26.34)</td>
      <td>(32.03)</td>
    </tr>
    <tr>
      <td>FF6PS</td>
      <td>-3.37</td>
      <td>-1.19</td>
      <td>0.15</td>
      <td>1.18</td>
      <td>2.25</td>
      <td>3.28</td>
      <td>4.72</td>
      <td>6.49</td>
      <td>9.41</td>
      <td>19.84</td>
      <td>23.21</td>
    </tr>
    <tr>
      <td></td>
      <td>(-30.92)</td>
      <td>(-14.59)</td>
      <td>(1.93)</td>
      <td>(12.32)</td>
      <td>(19.47)</td>
      <td>(23.67)</td>
      <td>(23.25)</td>
      <td>(28.81)</td>
      <td>(27.57)</td>
      <td>(33.00)</td>
      <td>(36.30)</td>
    </tr>
  </tbody>
</table>

## Panel B: One-month-ahead returns conditional on past MAX $^\beta$ persistence

<table>
  <thead>
    <tr>
      <th></th>
      <th>MAX $^\beta$ conditional on MAX $^\beta_{t-1}$ </th>
      <th>MAX $^\beta$ conditional on MAX $^\beta_{t-1,t-2}$ </th>
      <th>MAX $^\beta$ conditional on MAX $^\beta_{t-1,t-2,t-3}$ </th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td></td>
      <td>High</td>
      <td>Mid</td>
      <td>Low</td>
      <td>High &amp; High</td>
      <td>Non-high</td>
      <td>High &amp; High &amp; High</td>
      <td>Non-high</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td>RET-RF</td>
      <td>FF6PS</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Port 9</td>
      <td>-0.32</td>
      <td>-0.69</td>
      <td>0.46</td>
      <td>-0.04</td>
      <td>0.76</td>
      <td>0.22</td>
      <td>-0.01</td>
      <td>-0.40</td>
      <td>0.43</td>
      <td>-0.10</td>
      <td>-0.04</td>
      <td>-0.65</td>
      <td>0.37</td>
      <td>-0.15</td>
    </tr>
    <tr>
      <td></td>
      <td>(-0.91)</td>
      <td>(-3.28)</td>
      <td>(1.65)</td>
      <td>(-0.32)</td>
      <td>(3.54)</td>
      <td>(1.88)</td>
      <td>(-0.02)</td>
      <td>(-1.56)</td>
      <td>(1.69)</td>
      <td>(-0.91)</td>
      <td>(-0.08)</td>
      <td>(-1.98)</td>
      <td>(1.39)</td>
      <td>(-1.40)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-0.45</td>
      <td>-0.78</td>
      <td>0.05</td>
      <td>-0.40</td>
      <td>0.28</td>
      <td>-0.33</td>
      <td>-0.70</td>
      <td>-1.10</td>
      <td>0.10</td>
      <td>-0.41</td>
      <td>-1.09</td>
      <td>-1.50</td>
      <td>0.10</td>
      <td>-0.39</td>
    </tr>
    <tr>
      <td></td>
      <td>(-1.13)</td>
      <td>(-3.25)</td>
      <td>(0.20)</td>
      <td>(-2.54)</td>
      <td>(1.04)</td>
      <td>(-2.10)</td>
      <td>(-1.49)</td>
      <td>(-3.31)</td>
      <td>(0.36)</td>
      <td>(-2.85)</td>
      <td>(-2.14)</td>
      <td>(-3.81)</td>
      <td>(0.35)</td>
      <td>(-2.87)</td>
    </tr>
  </tbody>
</table>

---

# Page 84

# Appendix Table A6 – Continued: Panel C

## Panel C: One-month-ahead returns conditional on past MAX $^\beta$ persistence and investor sentiment

### High investor sentiment

<table>
  <thead>
    <tr>
      <th rowspan="3">AIX</th>
      <th colspan="6">MAX $^\beta$ conditional on MAX $_{t-1}^\beta$ </th>
      <th colspan="4">MAX $^\beta$ conditional on MAX $_{t-1,t-2}^\beta$ </th>
      <th colspan="4">MAX $^\beta$ conditional on MAX $_{t-1,t-2,t-3}^\beta$ </th>
    </tr>
    <tr>
      <th colspan="2">High</th>
      <th colspan="2">Mid</th>
      <th colspan="2">Low</th>
      <th colspan="2">High & High</th>
      <th colspan="2">Non-high</th>
      <th colspan="2">High & High & High</th>
      <th colspan="2">Non-high</th>
    </tr>
    <tr>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 9</td>
      <td>-1.12</td>
      <td>-0.69</td>
      <td>0.08</td>
      <td>0.04</td>
      <td>0.52</td>
      <td>0.16</td>
      <td>-0.74</td>
      <td>-0.07</td>
      <td>-0.04</td>
      <td>-0.10</td>
      <td>-1.04</td>
      <td>-0.38</td>
      <td>-0.20</td>
      <td>-0.10</td>
    </tr>
    <tr>
      <td></td>
      <td>(-2.25)</td>
      <td>(-2.43)</td>
      <td>(0.21)</td>
      <td>(0.21)</td>
      <td>(1.74)</td>
      <td>(1.01)</td>
      <td>(-1.18)</td>
      <td>(-0.20)</td>
      <td>(-0.12)</td>
      <td>(-0.62)</td>
      <td>(-1.34)</td>
      <td>(-0.71)</td>
      <td>(-0.52)</td>
      <td>(-0.62)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-1.59</td>
      <td>-1.10</td>
      <td>-0.52</td>
      <td>-0.50</td>
      <td>-0.13</td>
      <td>-0.53</td>
      <td>-2.19</td>
      <td>-1.59</td>
      <td>-0.68</td>
      <td>-0.66</td>
      <td>-2.94</td>
      <td>-2.12</td>
      <td>-0.89</td>
      <td>-0.69</td>
    </tr>
    <tr>
      <td></td>
      <td>(-3.04)</td>
      <td>(-2.99)</td>
      <td>(-1.35)</td>
      <td>(-2.02)</td>
      <td>(-0.34)</td>
      <td>(-2.11)</td>
      <td>(-3.63)</td>
      <td>(-3.31)</td>
      <td>(-1.74)</td>
      <td>(-3.14)</td>
      <td>(-3.86)</td>
      <td>(-3.57)</td>
      <td>(-2.10)</td>
      <td>(-3.12)</td>
    </tr>
  </tbody>
</table>

### Low investor sentiment

<table>
  <thead>
    <tr>
      <th rowspan="3">AIX</th>
      <th colspan="6">MAX $^\beta$ conditional on MAX $_{t-1}^\beta$ </th>
      <th colspan="4">MAX $^\beta$ conditional on MAX $_{t-1,t-2}^\beta$ </th>
      <th colspan="4">MAX $^\beta$ conditional on MAX $_{t-1,t-2,t-3}^\beta$ </th>
    </tr>
    <tr>
      <th colspan="2">High</th>
      <th colspan="2">Mid</th>
      <th colspan="2">Low</th>
      <th colspan="2">High & High</th>
      <th colspan="2">Non-high</th>
      <th colspan="2">High & High & High</th>
      <th colspan="2">Non-high</th>
    </tr>
    <tr>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 9</td>
      <td>0.47</td>
      <td>-0.58</td>
      <td>0.83</td>
      <td>-0.18</td>
      <td>1.04</td>
      <td>0.16</td>
      <td>0.81</td>
      <td>-0.35</td>
      <td>0.84</td>
      <td>-0.15</td>
      <td>0.51</td>
      <td>-0.71</td>
      <td>0.79</td>
      <td>-0.13</td>
    </tr>
    <tr>
      <td></td>
      <td>(1.03)</td>
      <td>(-2.21)</td>
      <td>(2.36)</td>
      <td>(-1.20)</td>
      <td>(3.32)</td>
      <td>(1.06)</td>
      <td>(1.56)</td>
      <td>(-0.97)</td>
      <td>(2.52)</td>
      <td>(-1.35)</td>
      <td>(0.81)</td>
      <td>(-1.48)</td>
      <td>(2.23)</td>
      <td>(-1.10)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>0.32</td>
      <td>-0.72</td>
      <td>0.69</td>
      <td>-0.24</td>
      <td>0.84</td>
      <td>-0.07</td>
      <td>0.57</td>
      <td>-0.54</td>
      <td>0.78</td>
      <td>-0.19</td>
      <td>0.11</td>
      <td>-0.81</td>
      <td>0.75</td>
      <td>-0.15</td>
    </tr>
    <tr>
      <td></td>
      <td>(0.70)</td>
      <td>(-2.36)</td>
      <td>(1.72)</td>
      <td>(-1.30)</td>
      <td>(2.44)</td>
      <td>(-0.41)</td>
      <td>(1.05)</td>
      <td>(-1.32)</td>
      <td>(2.02)</td>
      <td>(-1.18)</td>
      <td>(0.15)</td>
      <td>(-1.45)</td>
      <td>(1.92)</td>
      <td>(-0.96)</td>
    </tr>
  </tbody>
</table>

---

# Page 85

# Table A7

**Investor sentiment, aggregate issuance, MAX, and MAXβ**: This table examines whether the cross-sectional pricing of MAX and MAXβ varies across states of aggregate investor sentiment and aggregate equity issuance. The sample is divided into High and Low states based on the in-sample median of the Baker and Wurgler (2006) investor sentiment index and an aggregate issuance index constructed as the value-weighted cross-sectional average of firm-level twelve-month composite equity issuance following Daniel and Titman (2006). The portfolios are constructed using conditional dependent sorts. For the MAX portfolios (Panel A), stocks are sorted into MAX deciles separately within each aggregate state. For the controlled MAXβ portfolios (Panel B), a two-step procedure is used: within each aggregate state, stocks are first sorted into decile portfolios based on market beta; then, within each of these beta portfolios, stocks are further sorted into deciles based on MAX. The final MAXβ decile portfolios are formed by grouping together all stocks with the same MAX ranking across the beta portfolios within each aggregate state. Portfolio 1 (10) consists of stocks with the lowest (highest) MAX or MAXβ. The table reports one-month-ahead value-weighted FF6PS alphas. Newey and West (1987) t-statistics (adjusted with six lags) are reported in parentheses. The sample period spans January 1968 to December 2022.

<table>
  <thead>
    <tr>
      <th>Decile</th>
      <th>Panel A: MAX-sorted portfolios</th>
      <th>Panel B: MAXβ-sorted portfolios</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td></td>
      <td>Investor sentiment</td>
      <td>Aggregate issuance</td>
      <td>Investor sentiment</td>
      <td>Aggregate issuance</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>High</td>
      <td>Low</td>
      <td>High</td>
      <td>Low</td>
      <td>High</td>
      <td>Low</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>1</td>
      <td>0.03</td>
      <td>0.09</td>
      <td>0.09</td>
      <td>0.04</td>
      <td>0.27</td>
      <td>0.15</td>
      <td>0.32</td>
      <td>0.10</td>
    </tr>
    <tr>
      <td></td>
      <td>(0.31)</td>
      <td>(0.80)</td>
      <td>(0.80)</td>
      <td>(0.39)</td>
      <td>(2.75)</td>
      <td>(1.58)</td>
      <td>(3.13)</td>
      <td>(1.10)</td>
    </tr>
    <tr>
      <td>2</td>
      <td>0.14</td>
      <td>-0.07</td>
      <td>0.01</td>
      <td>0.06</td>
      <td>0.09</td>
      <td>-0.09</td>
      <td>-0.01</td>
      <td>-0.01</td>
    </tr>
    <tr>
      <td></td>
      <td>(1.39)</td>
      <td>(-0.83)</td>
      <td>(0.07)</td>
      <td>(0.61)</td>
      <td>(1.07)</td>
      <td>(-1.53)</td>
      <td>(-0.06)</td>
      <td>(-0.11)</td>
    </tr>
    <tr>
      <td>3</td>
      <td>0.06</td>
      <td>-0.03</td>
      <td>0.04</td>
      <td>-0.02</td>
      <td>0.20</td>
      <td>0.10</td>
      <td>0.14</td>
      <td>0.15</td>
    </tr>
    <tr>
      <td></td>
      <td>(0.74)</td>
      <td>(-0.40)</td>
      <td>(0.54)</td>
      <td>(-0.26)</td>
      <td>(1.97)</td>
      <td>(1.53)</td>
      <td>(1.51)</td>
      <td>(2.21)</td>
    </tr>
    <tr>
      <td>4</td>
      <td>-0.05</td>
      <td>-0.01</td>
      <td>-0.10</td>
      <td>0.03</td>
      <td>0.01</td>
      <td>0.05</td>
      <td>-0.01</td>
      <td>0.07</td>
    </tr>
    <tr>
      <td></td>
      <td>(-0.51)</td>
      <td>(-0.11)</td>
      <td>(-0.97)</td>
      <td>(0.39)</td>
      <td>(0.17)</td>
      <td>(0.61)</td>
      <td>(-0.09)</td>
      <td>(0.90)</td>
    </tr>
    <tr>
      <td>5</td>
      <td>0.04</td>
      <td>0.05</td>
      <td>0.05</td>
      <td>0.03</td>
      <td>0.01</td>
      <td>0.03</td>
      <td>-0.01</td>
      <td>0.04</td>
    </tr>
    <tr>
      <td></td>
      <td>(0.31)</td>
      <td>(0.50)</td>
      <td>(0.43)</td>
      <td>(0.36)</td>
      <td>(0.08)</td>
      <td>(0.44)</td>
      <td>(-0.03)</td>
      <td>(0.58)</td>
    </tr>
    <tr>
      <td>6</td>
      <td>0.21</td>
      <td>0.01</td>
      <td>0.05</td>
      <td>0.14</td>
      <td>-0.13</td>
      <td>0.05</td>
      <td>-0.04</td>
      <td>-0.02</td>
    </tr>
    <tr>
      <td></td>
      <td>(2.03)</td>
      <td>(0.06)</td>
      <td>(0.52)</td>
      <td>(1.46)</td>
      <td>(-1.19)</td>
      <td>(0.64)</td>
      <td>(-0.42)</td>
      <td>(-0.25)</td>
    </tr>
    <tr>
      <td>7</td>
      <td>-0.05</td>
      <td>0.10</td>
      <td>-0.01</td>
      <td>0.06</td>
      <td>0.02</td>
      <td>-0.03</td>
      <td>-0.08</td>
      <td>0.06</td>
    </tr>
    <tr>
      <td></td>
      <td>(-0.39)</td>
      <td>(0.74)</td>
      <td>(-0.06)</td>
      <td>(0.43)</td>
      <td>(0.17)</td>
      <td>(-0.31)</td>
      <td>(-0.60)</td>
      <td>(0.50)</td>
    </tr>
    <tr>
      <td>8</td>
      <td>0.01</td>
      <td>-0.13</td>
      <td>-0.04</td>
      <td>-0.09</td>
      <td>0.05</td>
      <td>-0.07</td>
      <td>0.06</td>
      <td>-0.08</td>
    </tr>
    <tr>
      <td></td>
      <td>(0.04)</td>
      <td>(-1.08)</td>
      <td>(-0.26)</td>
      <td>(-0.68)</td>
      <td>(0.34)</td>
      <td>(-0.61)</td>
      <td>(0.45)</td>
      <td>(-0.60)</td>
    </tr>
    <tr>
      <td>9</td>
      <td>-0.15</td>
      <td>-0.01</td>
      <td>-0.20</td>
      <td>0.04</td>
      <td>-0.23</td>
      <td>-0.20</td>
      <td>-0.19</td>
      <td>-0.23</td>
    </tr>
    <tr>
      <td></td>
      <td>(-0.84)</td>
      <td>(-0.12)</td>
      <td>(-1.54)</td>
      <td>(0.30)</td>
      <td>(-1.56)</td>
      <td>(-1.86)</td>
      <td>(-1.70)</td>
      <td>(-1.92)</td>
    </tr>
    <tr>
      <td>10</td>
      <td>-0.78</td>
      <td>-0.27</td>
      <td>-0.63</td>
      <td>-0.39</td>
      <td>-0.68</td>
      <td>-0.29</td>
      <td>-0.39</td>
      <td>-0.55</td>
    </tr>
    <tr>
      <td></td>
      <td>(-3.27)</td>
      <td>(-1.37)</td>
      <td>(-2.67)</td>
      <td>(-1.90)</td>
      <td>(-3.08)</td>
      <td>(-1.64)</td>
      <td>(-1.83)</td>
      <td>(-2.80)</td>
    </tr>
  </tbody>
</table>


| 10-1 difference | -0.82 | -0.36 | -0.72 | -0.43 | -0.95 | -0.44 | -0.71 | -0.65 |
|                | (-2.85) | (-1.42) | (-2.61) | (-1.64) | (-3.72) | (-1.97) | (-2.92) | (-2.69) |

---

# Page 86

# Table A8

**Size-orthogonalized institutional holdings, MAX, and MAX $^\beta$ **: This table examines the role of size-orthogonalized institutional holdings in the cross-sectional pricing of MAX and MAX $^\beta$ . We construct a size-orthogonalized measure of institutional ownership, INST $^\perp$ , by estimating month-to-month cross-sectional regressions of the logit transformation of INST on the logarithm of market capitalization and using the residuals as the orthogonalized INST measure. The logit of INST is defined as $\log\left(\frac{\text{INST}}{1-\text{INST}}\right)$ , where values of INST below 0.0001 and above 0.9999 are replaced with 0.0001 and 0.9999, respectively. The sample is divided into three subgroups based on the 33rd and 67th percentiles of the INST $^\perp$ measure, labeled INST $^\perp$ 1 (lowest) through INST $^\perp$ 3 (highest). The portfolios are constructed using conditional dependent sorts. For the MAX portfolios (Panel A), stocks are subsequently sorted into MAX deciles within each INST $^\perp$ tier. For the MAX $^\beta$ portfolios (Panel B), a two-step procedure is used: within each INST $^\perp$ tier, stocks are first sorted into decile portfolios based on market beta; then, within each of these beta portfolios, stocks are further sorted into deciles based on MAX. The final MAX $^\beta$ decile portfolios are formed by grouping together all stocks with the same MAX ranking across the beta portfolios within that INST $^\perp$ tier. Portfolio 1 (10) consists of stocks with the lowest (highest) MAX or MAX $^\beta$ . The table reports one-month-ahead value-weighted excess returns (RET–RF) and alphas (FF6PS). Newey and West (1987) $t$ -statistics (adjusted with five lags) are reported in parentheses. The sample period spans April 1980 to December 2022.

<table>
  <thead>
    <tr>
      <th rowspan="3">Decile</th>
      <th colspan="6">Panel A: MAX-sorted portfolios within INST $^\perp$ tiers</th>
      <th colspan="6">Panel B: MAX $^\beta$ -sorted portfolios within INST $^\perp$ tiers</th>
    </tr>
    <tr>
      <th colspan="2">INST $^\perp$ 1</th>
      <th colspan="2">INST $^\perp$ 2</th>
      <th colspan="2">INST $^\perp$ 3</th>
      <th colspan="2">INST $^\perp$ 1</th>
      <th colspan="2">INST $^\perp$ 2</th>
      <th colspan="2">INST $^\perp$ 3</th>
    </tr>
    <tr>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
      <th>RET-RF</th>
      <th>FF6PS</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 1</td>
      <td>0.77</td>
      <td>0.06</td>
      <td>1.03</td>
      <td>0.22</td>
      <td>1.14</td>
      <td>0.26</td>
      <td>0.78</td>
      <td>0.16</td>
      <td>1.01</td>
      <td>0.20</td>
      <td>1.04</td>
      <td>0.24</td>
    </tr>
    <tr>
      <td></td>
      <td>(4.68)</td>
      <td>(0.60)</td>
      <td>(5.33)</td>
      <td>(2.14)</td>
      <td>(5.10)</td>
      <td>(2.06)</td>
      <td>(3.50)</td>
      <td>(1.68)</td>
      <td>(4.75)</td>
      <td>(2.26)</td>
      <td>(3.97)</td>
      <td>(2.45)</td>
    </tr>
    <tr>
      <td>2</td>
      <td>0.86</td>
      <td>0.06</td>
      <td>0.92</td>
      <td>0.01</td>
      <td>0.96</td>
      <td>0.04</td>
      <td>0.73</td>
      <td>0.19</td>
      <td>0.81</td>
      <td>-0.03</td>
      <td>0.91</td>
      <td>-0.02</td>
    </tr>
    <tr>
      <td></td>
      <td>(4.75)</td>
      <td>(0.72)</td>
      <td>(4.52)</td>
      <td>(0.19)</td>
      <td>(4.01)</td>
      <td>(0.39)</td>
      <td>(3.63)</td>
      <td>(1.93)</td>
      <td>(3.54)</td>
      <td>(-0.42)</td>
      <td>(3.68)</td>
      <td>(-0.26)</td>
    </tr>
    <tr>
      <td>3</td>
      <td>0.72</td>
      <td>0.02</td>
      <td>0.85</td>
      <td>-0.06</td>
      <td>0.89</td>
      <td>-0.08</td>
      <td>0.62</td>
      <td>-0.02</td>
      <td>0.74</td>
      <td>-0.06</td>
      <td>0.92</td>
      <td>0.03</td>
    </tr>
    <tr>
      <td></td>
      <td>(3.69)</td>
      <td>(0.35)</td>
      <td>(3.86)</td>
      <td>(-0.72)</td>
      <td>(3.68)</td>
      <td>(-0.78)</td>
      <td>(3.08)</td>
      <td>(-0.30)</td>
      <td>(3.18)</td>
      <td>(-0.78)</td>
      <td>(3.65)</td>
      <td>(0.38)</td>
    </tr>
    <tr>
      <td>4</td>
      <td>0.71</td>
      <td>-0.02</td>
      <td>0.83</td>
      <td>-0.04</td>
      <td>0.82</td>
      <td>-0.13</td>
      <td>0.86</td>
      <td>0.12</td>
      <td>0.71</td>
      <td>-0.06</td>
      <td>0.89</td>
      <td>-0.01</td>
    </tr>
    <tr>
      <td></td>
      <td>(3.40)</td>
      <td>(-0.22)</td>
      <td>(3.69)</td>
      <td>(-0.47)</td>
      <td>(3.19)</td>
      <td>(-1.17)</td>
      <td>(4.07)</td>
      <td>(1.21)</td>
      <td>(3.08)</td>
      <td>(-0.78)</td>
      <td>(3.66)</td>
      <td>(-0.04)</td>
    </tr>
    <tr>
      <td>5</td>
      <td>0.80</td>
      <td>0.14</td>
      <td>0.80</td>
      <td>-0.12</td>
      <td>0.69</td>
      <td>-0.28</td>
      <td>0.73</td>
      <td>0.03</td>
      <td>0.83</td>
      <td>-0.05</td>
      <td>0.78</td>
      <td>-0.07</td>
    </tr>
    <tr>
      <td></td>
      <td>(3.34)</td>
      <td>(0.95)</td>
      <td>(3.33)</td>
      <td>(-1.11)</td>
      <td>(2.76)</td>
      <td>(-2.72)</td>
      <td>(3.44)</td>
      <td>(0.29)</td>
      <td>(3.43)</td>
      <td>(-0.56)</td>
      <td>(2.95)</td>
      <td>(-0.69)</td>
    </tr>
    <tr>
      <td>6</td>
      <td>0.73</td>
      <td>0.25</td>
      <td>0.64</td>
      <td>-0.26</td>
      <td>0.89</td>
      <td>-0.12</td>
      <td>0.63</td>
      <td>-0.06</td>
      <td>0.69</td>
      <td>-0.16</td>
      <td>0.64</td>
      <td>-0.21</td>
    </tr>
    <tr>
      <td></td>
      <td>(2.70)</td>
      <td>(1.93)</td>
      <td>(2.32)</td>
      <td>(-2.02)</td>
      <td>(3.22)</td>
      <td>(-1.29)</td>
      <td>(2.66)</td>
      <td>(-0.52)</td>
      <td>(2.90)</td>
      <td>(-1.42)</td>
      <td>(2.52)</td>
      <td>(-2.11)</td>
    </tr>
    <tr>
      <td>7</td>
      <td>0.53</td>
      <td>-0.06</td>
      <td>0.88</td>
      <td>0.07</td>
      <td>0.86</td>
      <td>-0.10</td>
      <td>0.59</td>
      <td>0.01</td>
      <td>0.82</td>
      <td>0.03</td>
      <td>0.70</td>
      <td>-0.17</td>
    </tr>
    <tr>
      <td></td>
      <td>(1.58)</td>
      <td>(-0.42)</td>
      <td>(2.97)</td>
      <td>(0.57)</td>
      <td>(2.92)</td>
      <td>(-0.91)</td>
      <td>(2.11)</td>
      <td>(0.09)</td>
      <td>(3.19)</td>
      <td>(0.28)</td>
      <td>(2.68)</td>
      <td>(-1.77)</td>
    </tr>
    <tr>
      <td>8</td>
      <td>0.56</td>
      <td>-0.07</td>
      <td>0.60</td>
      <td>-0.09</td>
      <td>0.70</td>
      <td>-0.06</td>
      <td>0.66</td>
      <td>0.05</td>
      <td>0.63</td>
      <td>-0.08</td>
      <td>0.52</td>
      <td>-0.33</td>
    </tr>
    <tr>
      <td></td>
      <td>(1.44)</td>
      <td>(-0.35)</td>
      <td>(2.05)</td>
      <td>(-0.69)</td>
      <td>(2.20)</td>
      <td>(-0.43)</td>
      <td>(1.98)</td>
      <td>(0.30)</td>
      <td>(2.16)</td>
      <td>(-0.50)</td>
      <td>(1.93)</td>
      <td>(-2.71)</td>
    </tr>
    <tr>
      <td>9</td>
      <td>0.53</td>
      <td>0.17</td>
      <td>0.50</td>
      <td>-0.01</td>
      <td>0.31</td>
      <td>-0.28</td>
      <td>0.44</td>
      <td>-0.15</td>
      <td>0.37</td>
      <td>-0.16</td>
      <td>0.41</td>
      <td>-0.44</td>
    </tr>
    <tr>
      <td></td>
      <td>(1.27)</td>
      <td>(0.79)</td>
      <td>(1.43)</td>
      <td>(-0.06)</td>
      <td>(0.93)</td>
      <td>(-2.62)</td>
      <td>(1.20)</td>
      <td>(-0.83)</td>
      <td>(1.10)</td>
      <td>(-1.01)</td>
      <td>(1.32)</td>
      <td>(-2.98)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-0.24</td>
      <td>-0.52</td>
      <td>0.28</td>
      <td>-0.08</td>
      <td>0.23</td>
      <td>-0.30</td>
      <td>-0.49</td>
      <td>-0.90</td>
      <td>0.29</td>
      <td>-0.24</td>
      <td>0.26</td>
      <td>-0.30</td>
    </tr>
    <tr>
      <td></td>
      <td>(-0.52)</td>
      <td>(-1.79)</td>
      <td>(0.67)</td>
      <td>(-0.42)</td>
      <td>(0.56)</td>
      <td>(-1.61)</td>
      <td>(-1.05)</td>
      <td>(-2.74)</td>
      <td>(0.82)</td>
      <td>(-1.21)</td>
      <td>(0.78)</td>
      <td>(-1.67)</td>
    </tr>
    <tr>
      <td>10–1 difference</td>
      <td>-1.01</td>
      <td>-0.58</td>
      <td>-0.75</td>
      <td>-0.30</td>
      <td>-0.91</td>
      <td>-0.56</td>
      <td>-1.27</td>
      <td>-1.06</td>
      <td>-0.72</td>
      <td>-0.44</td>
      <td>-0.78</td>
      <td>-0.54</td>
    </tr>
    <tr>
      <td></td>
      <td>(-2.44)</td>
      <td>(-1.79)</td>
      <td>(-2.11)</td>
      <td>(-1.26)</td>
      <td>(-2.87)</td>
      <td>(-2.42)</td>
      <td>(-3.47)</td>
      <td>(-3.01)</td>
      <td>(-2.69)</td>
      <td>(-1.97)</td>
      <td>(-3.75)</td>
      <td>(-2.58)</td>
    </tr>
  </tbody>
</table>

---

# Page 87

# Table A9

**Explaining MAX and MAX $^\beta$ within institutional ownership subgroups:** This table examines the role of the aggregate mispricing score (MIS), the stock-level equity issuance index, and expected idiosyncratic skewness (E(ISKEW)) in explaining the variation in MAX and MAX $^\beta$ within subgroups formed by institutional holdings (INST). The sample is divided into three groups based on INST using the 33rd and 67th percentiles as breakpoints. The table reports results from portfolio-level cross-sectional Fama-MacBeth regressions estimated separately within the high- (top tier) and low-INST (bottom tier) subgroups. Within each INST subgroup, stocks are sorted into 25 portfolios following the methodology described in Table 13. Panel A reports results for the high-INST subgroup, distinguishing between regressions where the dependent variable is based on MAX (Panel A.1) or MAX $^\beta$ (Panel A.2). Panel B presents analogous results for the low-INST subgroup (Panels B.1 and B.2). The dependent variable is a portfolio-level indicator as defined in Table 13. The independent variables include the portfolio-level value-weighted averages of MIS, the stock-level equity issuance index, and E(ISKEW); their definitions, along with those of the additional control variables, are provided in the caption of Table 13. Newey and West (1987) $t$ -statistics (adjusted with five lags) are reported in parentheses. The sample period spans April 1980 to December 2022.

## Panel A.1: High INST – MAX

<table>
  <thead>
    <tr>
      <th rowspan="2">MAX</th>
      <th colspan="10">Panel A.1: High INST – MAX</th>
    </tr>
    <tr>
      <th>(1a)</th>
      <th>(1b)</th>
      <th>(2a)</th>
      <th>(2b)</th>
      <th>(3a)</th>
      <th>(3b)</th>
      <th>(4a)</th>
      <th>(4b)</th>
      <th>(5a)</th>
      <th>(5b)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>MIS</td>
      <td>0.053<br>(30.34)</td>
      <td>0.029<br>(15.58)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.045<br>(24.72)</td>
      <td>0.028<br>(15.34)</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Issuance</td>
      <td></td>
      <td></td>
      <td>0.028<br>(25.43)</td>
      <td>0.011<br>(10.31)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.022<br>(20.30)</td>
      <td>0.009<br>(8.72)</td>
    </tr>
    <tr>
      <td>E(ISKEW)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>-0.337<br>(-1.70)</td>
      <td>-0.194<br>(-1.70)</td>
      <td>-0.527<br>(-3.28)</td>
      <td>-0.279<br>(-2.56)</td>
      <td>-0.294<br>(-1.95)</td>
      <td>-0.169<br>(-1.64)</td>
    </tr>
    <tr>
      <td>Intercept</td>
      <td>-2.362<br>(-29.75)</td>
      <td>1.257<br>(3.49)</td>
      <td>-1.349<br>(-25.73)</td>
      <td>2.347<br>(6.79)</td>
      <td>0.186<br>(1.36)</td>
      <td>3.299<br>(8.99)</td>
      <td>-1.717<br>(-12.05)</td>
      <td>1.080<br>(2.99)</td>
      <td>-0.946<br>(-8.54)</td>
      <td>2.224<br>(6.36)</td>
    </tr>
    <tr>
      <td>Control variables</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
    </tr>
    <tr>
      <td>R $^2$ </td>
      <td>25.25%</td>
      <td>56.70%</td>
      <td>23.17%</td>
      <td>56.39%</td>
      <td>19.39%</td>
      <td>57.25%</td>
      <td>36.84%</td>
      <td>61.20%</td>
      <td>34.18%</td>
      <td>60.78%</td>
    </tr>
  </tbody>
</table>

## Panel A.2: High INST – MAX $^\beta$

<table>
  <thead>
    <tr>
      <th rowspan="2">MAX</th>
      <th colspan="10">Panel A.2: High INST – MAX $^\beta$ </th>
    </tr>
    <tr>
      <th>(1a)</th>
      <th>(1b)</th>
      <th>(2a)</th>
      <th>(2b)</th>
      <th>(3a)</th>
      <th>(3b)</th>
      <th>(4a)</th>
      <th>(4b)</th>
      <th>(5a)</th>
      <th>(5b)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>MIS</td>
      <td>0.034<br>(22.87)</td>
      <td>0.013<br>(6.28)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.030<br>(18.50)</td>
      <td>0.013<br>(5.80)</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Issuance</td>
      <td></td>
      <td></td>
      <td>0.017<br>(16.06)</td>
      <td>0.004<br>(4.04)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.015<br>(13.59)</td>
      <td>0.003<br>(3.46)</td>
    </tr>
    <tr>
      <td>E(ISKEW)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.224<br>(1.72)</td>
      <td>0.297<br>(2.93)</td>
      <td>0.113<br>(0.95)</td>
      <td>0.275<br>(2.70)</td>
      <td>0.224<br>(1.94)</td>
      <td>0.312<br>(3.11)</td>
    </tr>
    <tr>
      <td>Intercept</td>
      <td>-1.580<br>(-23.52)</td>
      <td>4.571<br>(11.18)</td>
      <td>-0.851<br>(-17.14)</td>
      <td>5.247<br>(14.46)</td>
      <td>-0.307<br>(-3.19)</td>
      <td>4.900<br>(11.86)</td>
      <td>-1.589<br>(-16.15)</td>
      <td>4.008<br>(8.88)</td>
      <td>-0.994<br>(-11.54)</td>
      <td>4.674<br>(11.37)</td>
    </tr>
    <tr>
      <td>Control variables</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
    </tr>
    <tr>
      <td>R $^2$ </td>
      <td>12.67%</td>
      <td>47.36%</td>
      <td>12.11%</td>
      <td>47.18%</td>
      <td>11.04%</td>
      <td>48.21%</td>
      <td>21.17%</td>
      <td>52.36%</td>
      <td>20.62%</td>
      <td>52.32%</td>
    </tr>
  </tbody>
</table>

---

# Page 88

Table A9 - Continued: Panels B.1 and B.2

### Panel B.1: Low INST – MAX

<table>
  <thead>
    <tr>
      <th></th>
      <th>(1a)</th>
      <th>(1b)</th>
      <th>(2a)</th>
      <th>(2b)</th>
      <th>(3a)</th>
      <th>(3b)</th>
      <th>(4a)</th>
      <th>(4b)</th>
      <th>(5a)</th>
      <th>(5b)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>MIS</td>
      <td>0.039</td>
      <td>0.020</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.031</td>
      <td>0.017</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>(43.21)</td>
      <td>(13.96)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>(28.10)</td>
      <td>(12.67)</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Issuance</td>
      <td></td>
      <td></td>
      <td>0.024</td>
      <td>0.009</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.019</td>
      <td>0.008</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td>(36.16)</td>
      <td>(10.89)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>(21.80)</td>
      <td>(10.13)</td>
    </tr>
    <tr>
      <td>E(ISKEW)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.185</td>
      <td>-0.139</td>
      <td>-0.020</td>
      <td>-0.141</td>
      <td>-0.020</td>
      <td>-0.141</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>(1.59)</td>
      <td>(-1.54)</td>
      <td>(-0.23)</td>
      <td>(-1.71)</td>
      <td>(-0.22)</td>
      <td>(-1.71)</td>
    </tr>
    <tr>
      <td>Intercept</td>
      <td>-1.859</td>
      <td>0.568</td>
      <td>-1.173</td>
      <td>1.247</td>
      <td>-0.059</td>
      <td>2.217</td>
      <td>-1.405</td>
      <td>0.865</td>
      <td>-0.829</td>
      <td>1.454</td>
    </tr>
    <tr>
      <td></td>
      <td>(-39.54)</td>
      <td>(2.83)</td>
      <td>(-31.45)</td>
      <td>(6.54)</td>
      <td>(-0.52)</td>
      <td>(9.25)</td>
      <td>(-15.76)</td>
      <td>(3.65)</td>
      <td>(-9.36)</td>
      <td>(6.60)</td>
    </tr>
    <tr>
      <td>Control variables</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
    </tr>
    <tr>
      <td>R²</td>
      <td>26.63%</td>
      <td>56.18%</td>
      <td>25.25%</td>
      <td>55.43%</td>
      <td>20.19%</td>
      <td>56.20%</td>
      <td>36.06%</td>
      <td>60.45%</td>
      <td>35.42%</td>
      <td>59.80%</td>
    </tr>
  </tbody>
</table>


### Panel B.2: Low INST – MAX $^{\beta}$

<table>
  <thead>
    <tr>
      <th></th>
      <th>(1a)</th>
      <th>(1b)</th>
      <th>(2a)</th>
      <th>(2b)</th>
      <th>(3a)</th>
      <th>(3b)</th>
      <th>(4a)</th>
      <th>(4b)</th>
      <th>(5a)</th>
      <th>(5b)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>MIS</td>
      <td>0.028</td>
      <td>0.009</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.021</td>
      <td>0.007</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>(16.79)</td>
      <td>(6.35)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>(17.81)</td>
      <td>(4.81)</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Issuance</td>
      <td></td>
      <td></td>
      <td>0.017</td>
      <td>0.003</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.014</td>
      <td>0.002</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td>(23.39)</td>
      <td>(4.31)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>(15.68)</td>
      <td>(2.70)</td>
    </tr>
    <tr>
      <td>E(ISKEW)</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.535</td>
      <td>0.127</td>
      <td>0.368</td>
      <td>0.138</td>
      <td>0.361</td>
      <td>0.112</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>(7.07)</td>
      <td>(1.99)</td>
      <td>(5.67)</td>
      <td>(2.26)</td>
      <td>(5.31)</td>
      <td>(1.69)</td>
    </tr>
    <tr>
      <td>Intercept</td>
      <td>-1.348</td>
      <td>2.271</td>
      <td>-0.887</td>
      <td>2.635</td>
      <td>-0.462</td>
      <td>2.565</td>
      <td>-1.325</td>
      <td>2.000</td>
      <td>-0.989</td>
      <td>2.341</td>
    </tr>
    <tr>
      <td></td>
      <td>(-26.89)</td>
      <td>(12.87)</td>
      <td>(-22.26)</td>
      <td>(17.06)</td>
      <td>(-6.46)</td>
      <td>(13.33)</td>
      <td>(-18.74)</td>
      <td>(9.12)</td>
      <td>(-14.57)</td>
      <td>(11.10)</td>
    </tr>
    <tr>
      <td>Control variables</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
      <td>NO</td>
      <td>YES</td>
    </tr>
    <tr>
      <td>R²</td>
      <td>16.74%</td>
      <td>51.70%</td>
      <td>17.24%</td>
      <td>50.71%</td>
      <td>16.10%</td>
      <td>52.43%</td>
      <td>26.31%</td>
      <td>56.16%</td>
      <td>26.83%</td>
      <td>55.54%</td>
    </tr>
  </tbody>
</table>

---

# Page 89

# A Robustness Analyses and Extensions

Having identified the economic drivers of the $\text{MAX}^{\beta}$ phenomenon and its relation to investor heterogeneity, we now evaluate the robustness and generalizability of our findings. In this section, we subject the $\text{MAX}^{\beta}$ strategy to a battery of rigorous tests to ensure its profitability is not an artifact of specific market frictions or sample selection. We first examine the performance across subsamples sorted by size, price, and liquidity to verify that the effect persists in liquid, tradable segments of the market. Next, we analyze the risk-adjusted performance using Sharpe ratios and downside risk measures to rule out the possibility that the returns are merely compensation for tail risk. We also demonstrate the stability of the predictive power using alternative proxies for lottery demand. Finally, to complement our portfolio-level approach, we introduce a stock-level measure and provide firm-level evidence using cross-sectional regressions to confirm that the predictive power of the beta-neutralized proxy remains robust to controls for mispricing and equity issuance.

## A.1 Robustness of the $\text{MAX}^{\beta}$ Strategy

To ensure that the profitability of the $\text{MAX}^{\beta}$ strategy is not driven by micro-cap stocks, illiquid assets, or microstructure noise, we conduct comprehensive robustness checks across various subsamples. Table A10 reports the performance of the long-short $\text{MAX}^{\beta}$ portfolio within subsamples screened by market capitalization, share price, and Amihud (2002) liquidity. We report the alphas relative to the Fama-French (2018) six-factor model augmented with the Pastor and Stambaugh (2003) liquidity factor (FF6PS) to control for potential liquidity risk premiums.

The results indicate that the profitability of the $\text{MAX}^{\beta}$ strategy is economically and statistically robust regardless of the screening criteria employed. As reported in Table A10, the long-short strategy generates significantly negative abnormal returns across all size, price, and liquidity subsamples. For instance, even within the universe of the 500 most liquid stocks (a sample dominated by large-cap, efficiently priced firms) the strategy yields a highly significant alpha difference. This widespread persistence confirms that the $\text{MAX}^{\beta}$ effect is not a mechanical artifact of small or low-priced stocks but rather a pervasive pricing phenomenon.

Consistent with our main analyses, the abnormal returns in Table A10 are driven by both the long and the short legs of the strategy. However, we observe a distinct variation in the source of profitability as we move across subsamples. As the sample shifts toward larger market capitalization, higher share prices, and greater liquidity, the contribution of the long leg (low- $\text{MAX}^{\beta}$ stocks) to the overall alpha increases in statistical significance and economic magnitude. This variation aligns with the theoretical framework of Mitton and Vorkink (2007) regarding investor heterogeneity. In the retail-dominated segment (smaller, less liquid stocks), the effect is primarily driven by the overpricing of lottery-like assets (the short leg), consistent with “lotto investors” exerting price pressure. Conversely, in the institution-dominated segment (larger, more liquid stocks), the effect is increasingly driven by the premium demanded by “traditional investors” for holding assets with low idiosyncratic skewness (the long leg). Consequently, the persistence of the $\text{MAX}^{\beta}$ signal among the largest and most liquid stocks suggests that institutional constraints or preferences for skewness play a

xix

---

# Page 90

significant role in sustaining the effect even in the most efficient segments of the market.

## A.2 Sharpe Ratios and Downside Risk Performance

Beyond the robustness of alphas, we evaluate the risk-adjusted performance of the $\text{MAX}^{\beta}$ strategy relative to the original MAX measure and standard benchmark factors. Table A11 reports the absolute values of the Sharpe ratios and downside risk-adjusted returns for the long-short $\text{MAX}^{\beta}$ and MAX portfolios, alongside the Fama-French five factors (MKT, SIZE, B/M, INV, OP) and Momentum (MOM). As has been the case in our abnormal return analyses, the long-short portfolios for the characteristics are constructed using the extreme deciles of the sorting variables; i.e., market capitalization, book-to-market ratio, investment, profitability, and past 12-month return.

To assess the statistical significance of the Sharpe ratio differences, we utilize the methodology introduced in Lo (2002), which accounts for the statistical properties of Sharpe ratios when returns are not necessarily independent and identically distributed. Consistent with our earlier findings on abnormal return performances, the $\text{MAX}^{\beta}$ strategy exhibits superior risk-adjusted performance compared to the original MAX measure. The long-short $\text{MAX}^{\beta}$ portfolio delivers an absolute Sharpe ratio of 0.490 ( $t$ -stat. = 3.63), which is both economically and statistically larger than the absolute Sharpe ratio of 0.430 ( $t$ -stat. = 3.19) generated by the original MAX strategy. This improvement underscores the efficacy of purging systematic risk from the maximum daily return signal, allowing for a cleaner identification of the lottery-preference anomaly.

Furthermore, the $\text{MAX}^{\beta}$ strategy compares favorably to standard asset pricing factors. With the exception of Momentum (Sharpe = 0.674), $\text{MAX}^{\beta}$ produces a higher absolute Sharpe ratio than all other characteristics underlying the Fama-French factors, including the Market (0.404), Size (0.087), Value (0.283), Investment (0.412), and Operating Profitability (0.275).

Finally, given that lottery-like stocks are often associated with negative skewness and crash risk (e.g., Atilgan et al., 2020), we examine whether the strategy’s performance is merely compensation for left-tail risk. Table A11 presents the absolute values of downside risk-adjusted returns using Value-at-Risk (VaR) and Expected Shortfall (ES) at the 1% and 5% levels. The $\text{MAX}^{\beta}$ strategy consistently generates higher returns per unit of downside risk (e.g., $\text{RET}/\text{VaR}(5\%) = 0.098$ ) compared to the original MAX measure (0.096) and the majority of the benchmark factors. These results confirm that the abnormal returns associated with $\text{MAX}^{\beta}$ are not simply a premium for bearing extreme downside risk.

## A.3 Alternative Proxies for Lottery Demand

To ensure that our findings are not specific to the choice of the five maximum daily returns over a month (MAX) as the sole proxy for lottery demand, we extend our analysis to alternative measures of lotteryness. Specifically, we examine the robustness of our beta-neutralization procedure using the lottery index (LTRY) of Kumar (2009), the single highest daily return in a month (MAX(1)), and measures of extreme right-tail returns, specifically MAX(95%) and MAX(99%). MAX(95%) and MAX(99%) capture the extreme upper end of the daily return distribution, corresponding to the 95th and 99th percentiles over the past 252 trading days.

xx

---

# Page 91

Table A12 reports the performance of portfolios sorted on these alternative proxies, both in their raw form and after applying the same market-beta neutralization process used to construct $\text{MAX}^{\beta}$ . We report the alphas relative to the Fama-French (2018) six-factor model augmented with the Pastor and Stambaugh (2003) liquidity factor (FF6PS). The results confirm the generalizability of our methodological contribution. When the systematic component is purged from these alternative lottery proxies, the resulting beta-neutralized strategies [ $\text{LTRY}^{\beta}$ , $\text{MAX}(1)^{\beta}$ , $\text{MAX}(95\%)^{\beta}$ , and $\text{MAX}(99\%)^{\beta}$ ] generate economically and statistically significant abnormal returns. Importantly, consistent with the framework of Mitton and Vorkink (2007) and our earlier findings, the abnormal return performance of these alternative beta-neutralized measures is driven by both the long and the short legs of the strategy.

Finally, we introduce $\text{MAX}^{\text{Treynor}}$ as an alternative stock-level proxy for lottery demand. While $\text{MAX}^{\beta}$ is a portfolio-level measure constructed via double-sorting, $\text{MAX}^{\text{Treynor}}$ , defined as the average of the five highest daily returns divided by the market beta, provides a useful alternative with finer measurement availability at the individual stock level. The results in Panel C of Table A12 indicate that this stock-level adjustment effectively isolates the idiosyncratic lottery preference, yielding significant abnormal returns similar to the portfolio-based $\text{MAX}^{\beta}$ measure. This consistency across different definitions and construction methods highlights that the $\text{MAX}^{\beta}$ strategy captures a fundamental pricing phenomenon that persists across various proxies for lottery-like assets.

## A.4 Firm-Level Evidence for $\text{MAX}^{\text{Treynor}}$

Table A13 of the Appendix presents firm-level Fama-MacBeth (1973) cross-sectional regressions of one-month-ahead excess returns on $\text{MAX}^{\text{Treynor}}$ . The latter provides a stock-level alternative to the portfolio-level proxies for lottery demand.

We restrict our Fama–MacBeth analyses to a fixed sample in which all observations have available data for every independent variable: MAX, BETA, MIS, CE, SIZE, BM, REV, MOM, ILLIQ, ROE, I/A, and IVOL. Thus, all regression specifications (Columns 1–6) are estimated using the same fixed sample, and the number of observations remains constant across specifications. To mitigate the effects of outliers in the regression tests, we winsorize all explanatory variables cross-sectionally at the 1st and 99th percentiles of their own distribution. We apply winsorization to each variable on a month-to-month basis using this fixed sample.

The first column of Table A13 presents the results from a univariate regression. The average slope on $\text{MAX}^{\text{Treynor}}$ is negative and statistically significant; $-0.023$ with a t-statistic of $-3.63$ , indicating that stocks with high beta-adjusted maximum returns underperform in the subsequent month. Column 2 introduces the standard set of control variables. Although the coefficient decreases to $-0.013$ , it remains statistically significant (t-stat = $-2.91$ ), suggesting that the predictive power of $\text{MAX}^{\text{Treynor}}$ is not subsumed by standard firm characteristics or risk factors.

Columns 3 and 4 examine the robustness of the effect to mispricing and equity issuance. It is worth emphasizing that the performance of $\text{MAX}^{\text{Treynor}}$ is virtually unaffected by MIS or CE in the bivariate regression specifications (Columns 3 and 4). In the bivariate regression with the mispricing score (MIS) in

xxi

---

# Page 92

Column 3, the coefficient on $\text{MAX}^{\text{Treynor}}$ is $-0.026$ (t-stat. = $-4.04$ ), which is slightly larger in magnitude than the univariate estimate. Similarly, controlling for composite equity issuance (CE) in Column 4 yields a coefficient of $-0.025$ (t-stat. = $-4.03$ ). This robustness suggests that because $\text{MAX}^{\text{Treynor}}$ is beta-neutralized, it is less susceptible to the systematic mispricing components that drive the correlation between the original MAX measure and variables like MIS and CE.

Finally, Columns 5 and 6 present the full multivariate specifications. Even after accounting for MIS, CE, and the full set of control variables, the coefficients on $\text{MAX}^{\text{Treynor}}$ remain negative and significant at $-0.012$ (t-stat. = $-2.86$ ) and $-0.012$ (t-stat. = $-2.85$ ), respectively. These results confirm that the beta-adjusted lottery proxy captures a distinct pricing phenomenon that persists in firm-level cross-sectional regressions.

xxii

---

# Page 93

Table A10

**Robustness of MAX $^\beta$ across different subsamples**: This table reports robustness tests for market beta-neutralized MAX-sorted portfolios (MAX $^\beta$ ) across different subsamples based on firm size (Panel A), share price (Panel B), and liquidity (Panel C). In each panel, the portfolios are constructed using a conditional sorting procedure within the corresponding screened subsample. First, stocks are sorted into ten portfolios based on market beta. Then, within each beta-sorted portfolio, stocks are further sorted into decile portfolios based on MAX (defined as the average of the five highest daily returns within a month). The final decile portfolios are formed by grouping together all stocks with the same MAX ranking across the beta portfolios. Portfolio 1 (10) contains stocks with the lowest (highest) MAX $^\beta$ . Panel A restricts the sample based on market capitalization, including stocks above the NYSE 10th, 20th, and 50th percentiles, as well as the 1,000 and 500 largest stocks. Panel B restricts the sample based on share price, including stocks with prices above $1, $ 5 (benchmark), and $10. Panel C restricts the sample based on the liquidity measure of Amihud (2002), including stocks with liquidity above the NYSE 10th, 20th, and 50th percentiles, as well as the 1,000 and 500 most liquid stocks. The table reports one-month-ahead alphas (FF6PS) for the value-weighted decile portfolios. The final row reports the alpha spreads between decile portfolios 10 and 1. Newey and West (1987) $ t $-statistics (adjusted with six lags) are reported in parentheses. The sample period spans January 1968 to December 2022.

<table>
  <thead>
    <tr>
      <th rowspan="2">xxiii</th>
      <th colspan="5">Panel A: Size screen</th>
      <th colspan="3">Panel B: Price screen</th>
    </tr>
    <tr>
      <th>&gt;NYSE10</th>
      <th>&gt;NYSE20</th>
      <th>&gt;NYSE50</th>
      <th>1000 largest</th>
      <th>500 largest</th>
      <th>&gt; $ 1</th>
      <th>&gt; $5</th>
      <th>&gt; $ 10</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 1</td>
      <td>0.21<br>(2.73)</td>
      <td>0.17<br>(2.30)</td>
      <td>0.20<br>(2.58)</td>
      <td>0.19<br>(2.61)</td>
      <td>0.20<br>(2.48)</td>
      <td>0.19<br>(2.77)</td>
      <td>0.23<br>(3.08)</td>
      <td>0.21<br>(2.94)</td>
    </tr>
    <tr>
      <td>Port 2</td>
      <td>0.06<br>(1.05)</td>
      <td>0.12<br>(2.10)</td>
      <td>0.11<br>(1.84)</td>
      <td>0.15<br>(2.22)</td>
      <td>0.08<br>(1.20)</td>
      <td>0.03<br>(0.55)</td>
      <td>-0.01<br>(-0.07)</td>
      <td>0.06<br>(1.01)</td>
    </tr>
    <tr>
      <td>Port 3</td>
      <td>0.07<br>(1.41)</td>
      <td>0.03<br>(0.60)</td>
      <td>0.10<br>(1.50)</td>
      <td>0.09<br>(1.41)</td>
      <td>0.24<br>(3.24)</td>
      <td>0.10<br>(1.89)</td>
      <td>0.16<br>(2.61)</td>
      <td>0.13<br>(2.18)</td>
    </tr>
    <tr>
      <td>Port 4</td>
      <td>0.10<br>(1.33)</td>
      <td>0.14<br>(2.21)</td>
      <td>0.17<br>(2.31)</td>
      <td>0.15<br>(2.47)</td>
      <td>-0.00<br>(-0.03)</td>
      <td>0.03<br>(0.63)</td>
      <td>0.03<br>(0.59)</td>
      <td>0.04<br>(0.61)</td>
    </tr>
    <tr>
      <td>Port 5</td>
      <td>-0.08<br>(-1.35)</td>
      <td>-0.01<br>(-0.08)</td>
      <td>0.00<br>(0.01)</td>
      <td>-0.10<br>(-1.44)</td>
      <td>0.06<br>(1.02)</td>
      <td>0.03<br>(0.56)</td>
      <td>0.02<br>(0.39)</td>
      <td>-0.03<br>(-0.56)</td>
    </tr>
    <tr>
      <td>Port 6</td>
      <td>0.01<br>(0.21)</td>
      <td>-0.12<br>(-1.59)</td>
      <td>-0.06<br>(-0.86)</td>
      <td>-0.02<br>(-0.43)</td>
      <td>0.04<br>(0.53)</td>
      <td>0.04<br>(0.43)</td>
      <td>-0.03<br>(-0.45)</td>
      <td>-0.01<br>(-0.23)</td>
    </tr>
    <tr>
      <td>Port 7</td>
      <td>0.01<br>(0.04)</td>
      <td>-0.01<br>(-0.04)</td>
      <td>-0.15<br>(-2.02)</td>
      <td>-0.09<br>(-1.33)</td>
      <td>-0.14<br>(-1.80)</td>
      <td>0.12<br>(1.46)</td>
      <td>-0.01<br>(-0.08)</td>
      <td>-0.09<br>(-1.12)</td>
    </tr>
    <tr>
      <td>Port 8</td>
      <td>0.05<br>(0.65)</td>
      <td>-0.06<br>(-0.69)</td>
      <td>-0.03<br>(-0.36)</td>
      <td>-0.02<br>(-0.33)</td>
      <td>-0.07<br>(-0.93)</td>
      <td>-0.08<br>(-0.61)</td>
      <td>-0.01<br>(-0.14)</td>
      <td>0.02<br>(0.24)</td>
    </tr>
    <tr>
      <td>Port 9</td>
      <td>-0.19<br>(-1.93)</td>
      <td>-0.11<br>(-1.14)</td>
      <td>-0.06<br>(-0.66)</td>
      <td>-0.11<br>(-1.18)</td>
      <td>-0.01<br>(-0.21)</td>
      <td>-0.19<br>(-1.51)</td>
      <td>-0.22<br>(-2.28)</td>
      <td>-0.22<br>(-2.20)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-0.35<br>(-2.66)</td>
      <td>-0.22<br>(-1.59)</td>
      <td>-0.22<br>(-1.94)</td>
      <td>-0.26<br>(-2.09)</td>
      <td>-0.16<br>(-1.52)</td>
      <td>-0.63<br>(-3.39)</td>
      <td>-0.50<br>(-3.25)</td>
      <td>-0.34<br>(-2.35)</td>
    </tr>
    <tr>
      <td>10–1 difference</td>
      <td>-0.56<br>(-3.22)</td>
      <td>-0.39<br>(-2.25)</td>
      <td>-0.42<br>(-2.70)</td>
      <td>-0.45<br>(-2.72)</td>
      <td>-0.36<br>(-2.38)</td>
      <td>-0.82<br>(-3.90)</td>
      <td>-0.73<br>(-3.89)</td>
      <td>-0.55<br>(-2.97)</td>
    </tr>
  </tbody>
</table>

---

# Page 94

Table A10  
(continued)

<table>
  <thead>
    <tr>
      <th colspan="6">Panel C: Liquidity screen</th>
    </tr>
    <tr>
      <th></th>
      <th>&gt;NYSE10</th>
      <th>&gt;NYSE20</th>
      <th>&gt;NYSE50</th>
      <th>1000 liquid</th>
      <th>500 liquid</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 1</td>
      <td>0.20<br>(2.57)</td>
      <td>0.20<br>(2.65)</td>
      <td>0.23<br>(3.07)</td>
      <td>0.21<br>(2.86)</td>
      <td>0.28<br>(3.42)</td>
    </tr>
    <tr>
      <td>Port 2</td>
      <td>0.04<br>(0.75)</td>
      <td>0.11<br>(1.79)</td>
      <td>0.10<br>(1.37)</td>
      <td>0.14<br>(2.00)</td>
      <td>0.10<br>(1.27)</td>
    </tr>
    <tr>
      <td>Port 3</td>
      <td>0.14<br>(2.37)</td>
      <td>0.07<br>(0.99)</td>
      <td>0.09<br>(1.44)</td>
      <td>0.07<br>(1.09)</td>
      <td>0.06<br>(0.83)</td>
    </tr>
    <tr>
      <td>Port 4</td>
      <td>0.07<br>(0.97)</td>
      <td>0.08<br>(1.30)</td>
      <td>0.08<br>(1.06)</td>
      <td>0.11<br>(1.60)</td>
      <td>0.14<br>(1.81)</td>
    </tr>
    <tr>
      <td>Port 5</td>
      <td>-0.01<br>(-0.15)</td>
      <td>0.01<br>(0.06)</td>
      <td>0.11<br>(1.52)</td>
      <td>-0.01<br>(-0.18)</td>
      <td>0.06<br>(0.89)</td>
    </tr>
    <tr>
      <td>Port 6</td>
      <td>-0.02<br>(-0.37)</td>
      <td>-0.10<br>(-1.28)</td>
      <td>-0.07<br>(-1.19)</td>
      <td>-0.03<br>(-0.50)</td>
      <td>0.11<br>(1.53)</td>
    </tr>
    <tr>
      <td>Port 7</td>
      <td>-0.05<br>(-0.63)</td>
      <td>-0.01<br>(-0.16)</td>
      <td>-0.16<br>(-1.98)</td>
      <td>-0.08<br>(-1.10)</td>
      <td>-0.13<br>(-1.69)</td>
    </tr>
    <tr>
      <td>Port 8</td>
      <td>0.12<br>(1.23)</td>
      <td>0.04<br>(0.43)</td>
      <td>-0.01<br>(-0.03)</td>
      <td>-0.04<br>(-0.56)</td>
      <td>-0.11<br>(-1.28)</td>
    </tr>
    <tr>
      <td>Port 9</td>
      <td>-0.26<br>(-2.63)</td>
      <td>-0.20<br>(-2.02)</td>
      <td>-0.04<br>(-0.51)</td>
      <td>-0.19<br>(-2.05)</td>
      <td>-0.03<br>(-0.38)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-0.26<br>(-1.83)</td>
      <td>-0.25<br>(-1.81)</td>
      <td>-0.27<br>(-2.35)</td>
      <td>-0.24<br>(-1.89)</td>
      <td>-0.12<br>(-1.17)</td>
    </tr>
    <tr>
      <td>10–1 difference</td>
      <td>-0.46<br>(-2.47)</td>
      <td>-0.45<br>(-2.47)</td>
      <td>-0.50<br>(-3.21)</td>
      <td>-0.45<br>(-2.68)</td>
      <td>-0.40<br>(-2.62)</td>
    </tr>
  </tbody>
</table>

xxiv

---

# Page 95

Table A11

**Sharpe ratios and downside risk of MAX, MAX $^\beta$ , and benchmark characteristics:** This table reports absolute Sharpe ratios (with associated $t$ -statistics) and absolute downside risk-adjusted returns for value-weighted long-short portfolios formed on MAX and MAX $^\beta$ . For benchmarking purposes, the table also reports these metrics for the market portfolio (MKT) and long-short strategies based on size (SIZE), book-to-market ratio (BM), asset growth (INV), operating profitability (OP), and intermediate-term momentum (MOM). The analysis utilizes the benchmark sample, excluding stocks priced below $5 and firms in the utilities and financials industries. Downside risk is measured using Value-at-Risk (VaR) and Expected Shortfall (ES). VaR(1%) (VaR(5%)) is defined as the absolute value of the 1st (5th) percentile of the long-short portfolio’s return distribution. ES(1%) (ES(5%)) is the absolute value of the equal-weighted average of returns falling below the 1st (5th) percentile of the return distribution. Downside risk-adjusted returns are calculated as the absolute value of the long-short return spread divided by the corresponding downside risk measure. The sample period spans January 1968 to December 2022.

<table>
  <thead>
    <tr>
      <th rowspan="2"> </th>
      <th colspan="2">Sharpe</th>
      <th colspan="4">Downside risk</th>
    </tr>
    <tr>
      <th>Sharpe ratio</th>
      <th>t-statistic</th>
      <th>RET/VaR(1%)</th>
      <th>RET/VaR(5%)</th>
      <th>RET/ES(1%)</th>
      <th>RET/ES(5%)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>MKTRF</td>
      <td>0.404</td>
      <td>3.04</td>
      <td>0.045</td>
      <td>0.070</td>
      <td>0.034</td>
      <td>0.052</td>
    </tr>
    <tr>
      <td>SIZE</td>
      <td>0.087</td>
      <td>0.64</td>
      <td>0.010</td>
      <td>0.016</td>
      <td>0.009</td>
      <td>0.012</td>
    </tr>
    <tr>
      <td>B/M</td>
      <td>0.283</td>
      <td>2.09</td>
      <td>0.036</td>
      <td>0.055</td>
      <td>0.025</td>
      <td>0.039</td>
    </tr>
    <tr>
      <td>INV</td>
      <td>0.412</td>
      <td>3.05</td>
      <td>0.029</td>
      <td>0.047</td>
      <td>0.023</td>
      <td>0.034</td>
    </tr>
    <tr>
      <td>OP</td>
      <td>0.275</td>
      <td>2.04</td>
      <td>0.030</td>
      <td>0.057</td>
      <td>0.020</td>
      <td>0.037</td>
    </tr>
    <tr>
      <td>MOM</td>
      <td>0.674</td>
      <td>4.99</td>
      <td>0.076</td>
      <td>0.124</td>
      <td>0.056</td>
      <td>0.086</td>
    </tr>
    <tr>
      <td>MAX</td>
      <td>0.430</td>
      <td>3.19</td>
      <td>0.042</td>
      <td>0.096</td>
      <td>0.031</td>
      <td>0.055</td>
    </tr>
    <tr>
      <td>MAX $^\beta$ </td>
      <td>0.490</td>
      <td>3.63</td>
      <td>0.053</td>
      <td>0.098</td>
      <td>0.036</td>
      <td>0.063</td>
    </tr>
  </tbody>
</table>

---

# Page 96

Table A12

**Alternative measures of lottery-like payoffs**: This table examines alternative proxies for lottery-like payoffs and their cross-sectional pricing. The alternative measures include: the lottery index (LTRY) of Kumar (2009); the single highest daily return in a month (MAX(1)); and the extreme right-tail return measures, defined as the 95th and 99th percentiles of the daily return distribution over the past 252 trading days (MAX(95%) and MAX(99%)). To construct LTRY, stocks are independently sorted into 50 bins based on price per share (PRC) in descending order, and into 50 bins based on idiosyncratic volatility (IVOL) and idiosyncratic skewness (ISKEW) in ascending order. IVOL and ISKEW are estimated from monthly regressions of daily stock returns on the MKT, SMB, and HML factors. The three ranks are summed to form a composite score, and LTRY is defined as the decile rank of this sum. Panel A reports one-month-ahead FF6PS alphas for the value-weighted decile portfolios formed via univariate sorts on LTRY, MAX(1), MAX(95%), and MAX(99%). Panel B reports results for market beta-neutralized portfolios, constructed by first sorting stocks into ten portfolios based on market beta and then sorting into deciles within each beta portfolio on the lottery-payoff measure, analogous to the MAX $^\beta$ procedure. The final decile portfolios are formed by grouping together all stocks with the same lottery-payoff measure ranking across the beta portfolios. Panel C reports results for univariate sorts on MAX $^{\text{Treynor}}$ , a stock-level measure defined as MAX (the average of the five highest daily returns in a month) divided by market beta. The final row reports the alpha spreads between decile portfolios 10 and 1. Newey and West (1987) $t$ -statistics (adjusted with six lags) are reported in parentheses. The sample period spans January 1968 to December 2022.

<table>
  <thead>
    <tr>
      <th rowspan="2">Decile</th>
      <th colspan="4">Panel A: Lottery measures</th>
      <th colspan="4">Panel B: Lottery $^\beta$ measures</th>
      <th rowspan="2">Panel C: Treynor<br>MAX $^{\text{Treynor}}$ </th>
    </tr>
    <tr>
      <th>LTRY</th>
      <th>MAX(1)</th>
      <th>MAX(95%)</th>
      <th>MAX(99%)</th>
      <th>LTRY $^\beta$ </th>
      <th>MAX(1) $^\beta$ </th>
      <th>MAX(95%) $^\beta$ </th>
      <th>MAX(99%) $^\beta$ </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Port 1</td>
      <td>-0.00<br>(-0.03)</td>
      <td>0.05<br>(0.58)</td>
      <td>0.04<br>(0.78)</td>
      <td>-0.02<br>(-0.47)</td>
      <td>0.05<br>(1.38)</td>
      <td>0.14<br>(2.16)</td>
      <td>0.14<br>(2.16)</td>
      <td>0.13<br>(2.24)</td>
      <td>0.22<br>(2.55)</td>
    </tr>
    <tr>
      <td>2</td>
      <td>0.03<br>(0.71)</td>
      <td>-0.05<br>(-0.92)</td>
      <td>-0.06<br>(-1.17)</td>
      <td>0.01<br>(0.30)</td>
      <td>0.01<br>(0.03)</td>
      <td>0.01<br>(0.06)</td>
      <td>0.03<br>(0.65)</td>
      <td>0.01<br>(0.17)</td>
      <td>0.23<br>(2.05)</td>
    </tr>
    <tr>
      <td>3</td>
      <td>0.05<br>(0.78)</td>
      <td>0.01<br>(0.04)</td>
      <td>-0.03<br>(-0.62)</td>
      <td>-0.00<br>(-0.02)</td>
      <td>0.05<br>(0.91)</td>
      <td>-0.01<br>(-0.16)</td>
      <td>-0.02<br>(-0.31)</td>
      <td>0.01<br>(0.09)</td>
      <td>0.06<br>(1.11)</td>
    </tr>
    <tr>
      <td>4</td>
      <td>0.11<br>(1.68)</td>
      <td>0.05<br>(0.70)</td>
      <td>-0.01<br>(-0.17)</td>
      <td>-0.14<br>(-1.90)</td>
      <td>0.08<br>(1.24)</td>
      <td>0.05<br>(0.74)</td>
      <td>-0.10<br>(-1.24)</td>
      <td>-0.09<br>(-1.33)</td>
      <td>0.05<br>(0.77)</td>
    </tr>
    <tr>
      <td>5</td>
      <td>0.11<br>(1.50)</td>
      <td>0.09<br>(1.35)</td>
      <td>0.07<br>(0.89)</td>
      <td>-0.01<br>(-0.05)</td>
      <td>0.16<br>(2.27)</td>
      <td>0.07<br>(0.96)</td>
      <td>-0.09<br>(-1.19)</td>
      <td>-0.06<br>(-0.77)</td>
      <td>-0.03<br>(-0.44)</td>
    </tr>
    <tr>
      <td>6</td>
      <td>0.12<br>(1.55)</td>
      <td>0.03<br>(0.44)</td>
      <td>-0.01<br>(-0.09)</td>
      <td>-0.07<br>(-0.74)</td>
      <td>0.01<br>(0.08)</td>
      <td>0.01<br>(0.19)</td>
      <td>-0.02<br>(-0.26)</td>
      <td>-0.03<br>(-0.49)</td>
      <td>-0.09<br>(-1.25)</td>
    </tr>
    <tr>
      <td>7</td>
      <td>-0.08<br>(-0.92)</td>
      <td>0.06<br>(0.73)</td>
      <td>0.01<br>(0.06)</td>
      <td>0.18<br>(1.60)</td>
      <td>0.09<br>(1.07)</td>
      <td>0.05<br>(0.62)</td>
      <td>-0.01<br>(-0.07)</td>
      <td>0.01<br>(0.08)</td>
      <td>-0.15<br>(-1.74)</td>
    </tr>
    <tr>
      <td>8</td>
      <td>-0.00<br>(-0.02)</td>
      <td>0.08<br>(0.71)</td>
      <td>0.06<br>(0.53)</td>
      <td>-0.03<br>(-0.32)</td>
      <td>0.05<br>(0.59)</td>
      <td>-0.10<br>(-1.22)</td>
      <td>0.03<br>(0.30)</td>
      <td>-0.06<br>(-0.60)</td>
      <td>-0.30<br>(-2.99)</td>
    </tr>
    <tr>
      <td>9</td>
      <td>-0.06<br>(-0.62)</td>
      <td>-0.07<br>(-0.68)</td>
      <td>-0.04<br>(-0.38)</td>
      <td>-0.00<br>(-0.01)</td>
      <td>-0.21<br>(-2.22)</td>
      <td>0.04<br>(0.45)</td>
      <td>0.03<br>(0.24)</td>
      <td>0.01<br>(0.07)</td>
      <td>-0.24<br>(-1.85)</td>
    </tr>
    <tr>
      <td>Port 10</td>
      <td>-0.34<br>(-2.75)</td>
      <td>-0.31<br>(-2.20)</td>
      <td>-0.25<br>(-1.45)</td>
      <td>-0.31<br>(-2.00)</td>
      <td>-0.37<br>(-3.12)</td>
      <td>-0.38<br>(-3.01)</td>
      <td>-0.45<br>(-2.85)</td>
      <td>-0.42<br>(-3.33)</td>
      <td>-0.27<br>(-1.90)</td>
    </tr>
    <tr>
      <td>10–1 difference</td>
      <td>-0.34<br>(-2.63)</td>
      <td>-0.36<br>(-2.08)</td>
      <td>-0.29<br>(-1.50)</td>
      <td>-0.29<br>(-1.66)</td>
      <td>-0.42<br>(-3.53)</td>
      <td>-0.52<br>(-3.39)</td>
      <td>-0.59<br>(-3.23)</td>
      <td>-0.55<br>(-3.99)</td>
      <td>-0.49<br>(-2.82)</td>
    </tr>
  </tbody>
</table>

---

# Page 97

Table A13

**Fama-MacBeth (1973) regressions on MAX$^{Treynor}$**: This table reports the results of firm-level Fama-MacBeth (1973) cross-sectional regressions of one-month-ahead excess stock returns on MAX$^{Treynor}$ and a set of control variables. MAX$^{Treynor}$ is defined as the average of the five highest daily returns in a month divided by the market beta. The control variables include: the aggregate mispricing score (MIS) of Stambaugh, Yu, and Yuan (2015); composite equity issuance (CE); market beta (BETA); log market capitalization (SIZE); log book-to-market ratio (BM); return reversal (REV); intermediate-term momentum (MOM); Amihud (2002) illiquidity (ILLIQ); return on equity (ROE); asset growth (I/A); and idiosyncratic volatility (IVOL). The final row reports the average adjusted $R^2$. Newey and West (1987) $t$-statistics (adjusted with six lags) are reported in parentheses. The sample period spans January 1968 to December 2022.

<table>
  <thead>
    <tr>
      <th>Variable</th>
      <th>(1)</th>
      <th>(2)</th>
      <th>(3)</th>
      <th>(4)</th>
      <th>(5)</th>
      <th>(6)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>MAX$^{Treynor}$</td>
      <td>-0.023</td>
      <td>-0.013</td>
      <td>-0.026</td>
      <td>-0.025</td>
      <td>-0.012</td>
      <td>-0.012</td>
    </tr>
    <tr>
      <td></td>
      <td>(-3.63)</td>
      <td>(-2.91)</td>
      <td>(-4.04)</td>
      <td>(-4.03)</td>
      <td>(-2.86)</td>
      <td>(-2.85)</td>
    </tr>
    <tr>
      <td>MIS</td>
      <td></td>
      <td></td>
      <td>-0.031</td>
      <td></td>
      <td>-0.018</td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td>(-7.89)</td>
      <td></td>
      <td>(-6.97)</td>
      <td></td>
    </tr>
    <tr>
      <td>CE</td>
      <td></td>
      <td></td>
      <td></td>
      <td>-0.023</td>
      <td></td>
      <td>-0.009</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>(-5.33)</td>
      <td></td>
      <td>(-4.81)</td>
    </tr>
    <tr>
      <td>BETA</td>
      <td></td>
      <td>0.088</td>
      <td></td>
      <td></td>
      <td>0.115</td>
      <td>0.094</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>(0.65)</td>
      <td></td>
      <td></td>
      <td>(0.86)</td>
      <td>(0.70)</td>
    </tr>
    <tr>
      <td>SIZE</td>
      <td></td>
      <td>-0.116</td>
      <td></td>
      <td></td>
      <td>-0.125</td>
      <td>-0.114</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>(-3.62)</td>
      <td></td>
      <td></td>
      <td>(-3.95)</td>
      <td>(-3.59)</td>
    </tr>
    <tr>
      <td>BM</td>
      <td></td>
      <td>0.089</td>
      <td></td>
      <td></td>
      <td>0.092</td>
      <td>0.086</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>(1.80)</td>
      <td></td>
      <td></td>
      <td>(1.86)</td>
      <td>(1.75)</td>
    </tr>
    <tr>
      <td>REV</td>
      <td></td>
      <td>-0.037</td>
      <td></td>
      <td></td>
      <td>-0.038</td>
      <td>-0.037</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>(-8.73)</td>
      <td></td>
      <td></td>
      <td>(-8.94)</td>
      <td>(-8.75)</td>
    </tr>
    <tr>
      <td>MOM</td>
      <td></td>
      <td>0.007</td>
      <td></td>
      <td></td>
      <td>0.005</td>
      <td>0.007</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>(4.92)</td>
      <td></td>
      <td></td>
      <td>(3.71)</td>
      <td>(4.94)</td>
    </tr>
    <tr>
      <td>ILLIQ</td>
      <td></td>
      <td>0.030</td>
      <td></td>
      <td></td>
      <td>0.022</td>
      <td>0.026</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>(1.20)</td>
      <td></td>
      <td></td>
      <td>(0.89)</td>
      <td>(1.05)</td>
    </tr>
    <tr>
      <td>ROE</td>
      <td></td>
      <td>0.411</td>
      <td></td>
      <td></td>
      <td>0.089</td>
      <td>0.329</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>(1.98)</td>
      <td></td>
      <td></td>
      <td>(0.43)</td>
      <td>(1.58)</td>
    </tr>
    <tr>
      <td>I/A</td>
      <td></td>
      <td>-0.716</td>
      <td></td>
      <td></td>
      <td>-0.268</td>
      <td>-0.613</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>(-6.42)</td>
      <td></td>
      <td></td>
      <td>(-2.95)</td>
      <td>(-6.33)</td>
    </tr>
    <tr>
      <td>IVOL</td>
      <td></td>
      <td>-0.310</td>
      <td></td>
      <td></td>
      <td>-0.258</td>
      <td>-0.293</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>(-5.92)</td>
      <td></td>
      <td></td>
      <td>(-5.05)</td>
      <td>(-5.60)</td>
    </tr>
    <tr>
      <td>Intercept</td>
      <td>0.008</td>
      <td>0.027</td>
      <td>0.023</td>
      <td>0.008</td>
      <td>0.036</td>
      <td>0.026</td>
    </tr>
    <tr>
      <td></td>
      <td>(3.29)</td>
      <td>(5.63)</td>
      <td>(12.95)</td>
      <td>(3.52)</td>
      <td>(7.47)</td>
      <td>(5.50)</td>
    </tr>
    <tr>
      <td>R$^2$</td>
      <td>0.003</td>
      <td>0.074</td>
      <td>0.014</td>
      <td>0.010</td>
      <td>0.076</td>
      <td>0.075</td>
    </tr>
  </tbody>
</table>

xxvii