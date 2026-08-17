# Page 1

# What Lies Beneath Zero: Censoring, Demand Estimation, and Hidden Beliefs*

Daniel Graves $^\dagger$

August 11, 2025

## Abstract

This paper proposes a novel approach to institution-level asset demand estimation and then applies it to obtain estimates of investor beliefs. Across institutions, I divide investors’ idiosyncratic beliefs about a given stock into two categories: “overt beliefs,” the beliefs of institutions that elected to own the stock, and “hidden beliefs,” the beliefs of institutions that elected not to own the stock. The demand estimation approach allows for recovery of overt beliefs and identifies strong upper bounds on hidden beliefs despite two forms of data censoring: (a) many participants are short sale constrained and (b) 13F filings do not report short sales. I aggregate these bounds and estimates across institutions to create a Hidden Beliefs Index (HBI) and Overt Beliefs Index (OBI). The OBI displays minimal ability to forecast returns. Contrary to standard rational frameworks, however, the HBI strongly predicts returns in the cross section. These results suggest that markets largely incorporate overt beliefs, which can be more easily recovered from public data, but fail to fully account for the informational value of hidden beliefs. I show empirically and theoretically that this paper’s results are consistent with a form of bounded rationality but inconsistent with a pure disagreement and short sale constraint mechanism. Markets asymmetrically embed the informational content of agents’ holdings and non-holdings, with beliefs about returns improperly updated when faced with the news that a given agent chose not to own a specific stock.

**JEL Codes**: G12, G11, G40, G23, G14, C34, C36, C60

---

*I thank my advisors Nicholas Barberis, Eduardo Dávila, John Geanakoplos, and Stefano Giglio for their continued support and guidance. I also thank Xiaohong Chen, Paul Fontanier, Paul Goldsmith-Pinkham, Philip Haile, Ralph Koijen, Stavros Panageas, Cecilia Parlatore, Kelly Shue, Alp Simsek, Kaushik Vasudevan, and Annette Vissing-Jorgensen, as well as seminar participants at Yale SOM, Northwestern Kellogg, University of Michigan Ross, HBS, NYU Stern, Stanford GSB, Berkeley Haas, Harvard, MIT Sloan, Wharton, and UCLA Anderson for helpful conversations and comments. I would also like to thank the Yale Center for Research Computing for the use of computing infrastructure, and special thanks to Aya Nawano for help with the Gurobi optimizer. I gratefully acknowledge support of the NSF GRFP; this material is based upon work supported by the National Science Foundation Graduate Research Fellowship under Grant No. DGE-1752134.*

$^\dagger$ Harvard University, 1805 Cambridge St, Cambridge, MA 02138. Email: danielgraves@fas.harvard.edu

---

# Page 2

# 1 Introduction

Agents’ beliefs are a central object of interest to economists, with investors’ expected returns a major focus of financial economics. As proper inference from available information is a primary tenet of most rational models in economics, financial economists have long debated whether investors account for the beliefs and information of other investors, who are potentially informed. SEC-mandated quarterly 13F filings can provide insight into large investors’ idiosyncratic beliefs about stocks. This information, however, is partly obscured by the fact that 13Fs detail institutional stock holdings but not the short positions that show which investors have bet against a particular stock. Because the long positions are publicly revealed, we might conjecture that investors will make approximately correct inferences regarding a given institution’s belief about a stock that it owns and therefore reports, which I call an “overt belief.” Yet some investors are short sale constrained and are unable to express more negative beliefs through action, and even for non-short sale constrained investors, short sales are unreported. I call these beliefs about stocks that an investor chooses not to own “hidden beliefs.” For example, if we see an investor that almost exclusively owns “value” stocks (with cheap-looking valuation metrics) refrain from owning a particular value stock, then we might infer that the investor has a negative hidden belief about the stock. But inference about these hidden beliefs is challenging because of two forms of censoring: the censoring at zero of short sale constraints, and the censoring at zero (non-reporting of short sales) of 13F data.

This paper studies the hidden and overt beliefs of investors and whether investors fully account for the hidden and overt beliefs of others. To accomplish this, I first develop a novel demand estimation method that allows us to estimate how institutional asset demands change as a function of observable and unobservable characteristics when only long positions are observed. Using the estimated parameters from this approach, I can fully recover estimates of overt beliefs and put strong bounds on each institution’s hidden beliefs. These bounds represent the highest possible stock-specific belief an institution could have held before it would have switched from being a non-owner to being an owner. I aggregate these bounds on hidden beliefs across institutions to form a Hidden Beliefs Index (HBI), a measure of the intensity of beliefs that lie beneath the data’s censoring point of zero. The HBI enables us to study whether investors, in aggregate, fully update their prior idiosyncratic return expectations to account for hidden beliefs. I find that, in stark contrast to standard models, hidden beliefs strongly and persistently predict returns in the cross section, even predicting returns over a multi-year time horizon. When I aggregate overt beliefs into an Overt Beliefs Index (OBI), however, the index displays at best a weak ability to predict future returns. I therefore find that hidden beliefs, as opposed to overt beliefs, are only incorporated into prices gradually and in a manner inconsistent with rational expectations. The empirical findings are consistent with participants engaging in a form of boundedly rational inference, with agents forming posterior beliefs about idiosyncratic returns that are a combination of (a) the standard Bayesian posterior and (b) a default value. Given the high financial stakes and strong incentives of institutional investing, these results point to a potential fundamental difference between how

1

---

# Page 3

agents account for the informational content of action and inaction.

A simple example provides the intuition for this paper’s strategy. Suppose there is a stock with a very high book-to-market ratio: it is a classic “value” stock with its assets net of liabilities large relative to its price. Now suppose we observe an institution that is a classic value investor. In fact, it bases its portfolio decisions only on (1) book-to-market ratios, the higher the better, and (2) research about a company’s idiosyncratic return prospects. If the investor fails to invest in this seemingly perfect value stock despite having researched it, then we can infer that the investor harbors a strongly negative idiosyncratic belief about the company. If, however, we observe the investor fail to hold a position in a “growth” stock, we would not be able to reach such a firm conclusion. Instead, we could only surmise that the investor’s idiosyncratic belief about the stock must not be extremely high, or else it would hold a position regardless of its dislike of growth stocks. The bound on a hidden belief is thus a form of measurement: how strong is our evidence that this specific non-owner uncovered adverse information?

Generalizing this intuition, consider a censored linear model where volatility-scaled demand $y_n$ , which is just the product of a stock $n$ ’s portfolio weight $w_n$ with its idiosyncratic variance of returns $\sigma_n^2$ , is given by $y_n = w_n \sigma_n^2 = \max \{0, x_n' \beta_0 + u_n\}$ , with $\beta_0 \in \mathbb{R}^{K+1}$ the true demand parameters of an institution, $x_n' \in \mathbb{R}^{K+1}$ the vector of observable characteristics of asset $n$ , and $u_n$ the unobservable idiosyncratic return expectation of the institution for stock $n$ . $^1$ If $\hat{\beta}$ is our estimate of demand parameters, then $\hat{u}_n \leq -x_n' \hat{\beta}$ if asset $n$ is missing from the portfolio or else $x_n' \hat{\beta} + \hat{u}_n > 0$ and the asset would have been purchased; $-x_n' \hat{\beta}$ is therefore an upper bound on the unobservable hidden belief $\hat{u}_n$ . I define the Hidden Beliefs Index (HBI) to be the assets-under-management-weighted value of such bounds taken over all dynamic institutions that had a stock within their consideration sets but chose not to hold it. Similarly, overt beliefs are defined as the residual $\hat{u}_n = y_n - x_n' \hat{\beta}$ whenever stock $n$ is held in the portfolio, with the OBI formed analogously to the HBI but using $\hat{u}_n$ instead of $-x_n' \hat{\beta}$ .

In trying to infer hidden beliefs, we are faced with two major complications in quantifying this approach. First, we do not know a given investor’s demand parameters $\beta_0$ and do not know the precise risk model of investors. Second, we are not provided with the lists of stocks that investors considered when selecting portfolios. Inferring a belief only makes sense if the investor formed a belief.

This paper’s methodological contribution is a new approach to institutional asset demand estimation that proposes solutions to both of these issues. I begin by showing that observed institutional demand can be expressed as the censored linear model just described, with $y_n = w_n \sigma_n^2 = \max \{0, x_n' \beta_0 + u_n\}$ . Obtaining this censored linear model requires only two standard assumptions: (a) mean-variance preferences with a multi-factor covariance matrix decomposition and (b) return expectations that are linear in asset characteristics. The censored linear model can be derived regardless of leverage constraints, short sale constraints, or number of portfolio

---

$^1$ As we will later see, this volatility scaling and censored linear model come from a mean-variance portfolio framework with beliefs that are linear in characteristics, where risk factors are included as characteristics.

2

---

# Page 4

risk factors, thus permitting us to apply the method to institutions without knowing their specific portfolio restrictions.

With a censored linear model in hand, I next proceed to estimation. Estimation is challenging due to censoring, the presence of an endogenous variable, and likely heteroskedasticity: the distribution of unobservable private beliefs might be a function of characteristics. To solve these issues, I adapt the Sequential Censored Quantile Regression (SCQR) of Chen (2018) with a control function approach to endogeneity, using a conditional median zero restriction instead of the conditional mean zero restriction commonly used in financial economics. The median zero restriction is not merely a modeling choice but a necessity: demand parameters, as well as the desired bounds on hidden beliefs and estimates of overt beliefs, are only identified under a quantile-type restriction on unobservables (see e.g. Newey (2001)).

The favorable computational properties of this paper’s estimation routine are pivotal in enabling the study of hidden and overt beliefs, as conducting censored regressions on approximately 250,000 quarterly institutional portfolios is intractable for estimators such as the CLAD estimator of Powell (1984) that require high-dimensional non-convex optimization. To the best of my knowledge, this paper is the first to devise a microdata demand estimation approach for censored data with endogeneity that is computationally tractable at scale and avoids strong distributional assumptions.

I apply this methodology to quarterly data from 1984 to 2021, estimating institutional demand for common stocks in each quarter. Using price data from CRSP, accounting data from Compustat, and quarterly 13F institutional portfolio holding data from Thomson Reuters, I compute quarterly asset characteristics and institutional portfolio weights for common stocks. This paper’s main specification uses the characteristics of Kojien and Yogo (2019), which consist of the dividend-to-book ratio along with five based on the five-factor model of Fama and French (2015): log market cap, log book value, operating profitability, investment, and market beta. Results are robust to using alternate sets of characteristics.

Two critical estimation details are defining institutional zero holdings and forming an instrument for asset prices, with the instrument dependent on defining the zeros. Zero holdings are derived from consideration sets, the sets of assets that each manager selects from during the portfolio formation process. In their ideal form, consideration sets or “choice sets,” which have a long tradition in the IO literature (see e.g. Goeree (2008)), are the sets of assets that managers are allowed by mandate to trade and have researched sufficiently to form a return expectation.

To better determine consideration sets, I first devise a taxonomy of “rigid” and “dynamic” managers. Rigid managers have approximately static portfolio weights and stock holdings, while dynamic managers hold changing sets of assets and alter their portfolio weights over time. For rigid managers, such as a passive mutual fund, I take the consideration set during quarter $t$ to be exclusively those stocks that are held at time $t$; we will not estimate demand for rigid managers, as they do not form beliefs.

Dynamic manager consideration sets are broader, and this paper’s approach combines (i) all stocks that share a 4-digit North American Industry Classification System (NAICS) code with two

3

---

# Page 5

or more portfolio holdings from the past three years and (ii) all holdings from the last three years. The premise is that if an investment manager currently holds PepsiCo stock and once owned shares in a different soft drink company but has never owned Coca Cola, then we include Coca Cola in the consideration set. As shown by Abaluck and Adams-Prassl (2021) in the context of demand for health insurance, how consideration sets are constructed, and how much they differ from full consideration, can have significant effects on both the sign and magnitude of economic effects when estimating demand. I therefore consider alternative definitions of consideration sets and show that the strongest empirical results are obtained by using the definition that hews closest to common intuition about how managers research and trade.

With consideration sets defined as above and the “zeros” established, I devise an instrument for log price inspired by the IV construction approach of Kojien and Yogo (2019): I take the log of the sum of the counterfactual market equities that would arise from institutions holding (1) equal-weighted portfolios within their consideration sets and (2) book-equity-weighted portfolios within their consideration sets. Unlike the IV of Kojien and Yogo (2019), which is based on institutions’ current and previous holdings, this paper’s instrument is based on just the current portfolio holdings for rigid institutions (no zero holdings) and broad industry-code-based consideration sets for dynamic institutions (many zero holdings). The dynamic consideration sets are largely static over time and are plausibly unrelated to a manager’s idiosyncratic beliefs. Using this instrument, we can construct a control variable that “controls” for the endogeneity of price.$^{2}$ Relevance of the IV comes from the basic idea that a company on more investors’ radars will carry a higher valuation, particularly when most investors are short sale constrained.

Next, using institutional holdings data, consideration sets, stock characteristics, and the control variable, I estimate institutional demands for each quarter from 1984Q4 through 2021Q4.$^{3}$ As a proof of concept illustrating the power of this paper’s approach, I conduct a large-scale simulation exercise and show that this paper’s methodology accurately recovers the generated demand coefficients, whereas other widely used methods fail to recover institutional demands.

If markets incorporate information and beliefs into prices in a manner consistent with rational expectations, then the HBI and OBI will be unable to predict returns; past quarters’ inferable private information should be priced, as investors can use this paper’s approach or a similar censored regression to recover it from public data. To test this null hypothesis, I divide stocks into size (market capitalization) deciles each quarter and sort by the two indices respectively to form size × HBI and size × OBI quintile equal-weighted quarterly portfolios. I conduct these quintile sorts using the HBI and OBI from one quarter ago, two quarters ago, and three quarters ago, computing a given size × HBI or size × OBI portfolio’s daily returns by averaging the results from the three lags. Abnormal returns (alphas) are computed using the four factors of Carhart

---

$^{2}$Kojien and Yogo (2019) propose similar instruments but use the “investment universe” of just past and current holdings in computing their instrumental variables instead of this paper’s “consideration sets.” Their approach implicitly assumes no censoring: all zero holdings are stocks that were previously held but currently are not. This paper’s approach defines broad universes for dynamic managers, with past holdings a small fraction of zeros.

$^{3}$Any managers with fewer than twenty-five portfolio holdings are dropped from the analysis due to insufficient data for estimation.

4

---

# Page 6

(1997). The OBI portfolio alphas have no discernible pattern, consistent with rational expectations. A modestly informative OBI, however, can be generated from a different institutional dataset that captures disaggregated portfolios of mutual fund managers.$^{4}$

By contrast, the HBI portfolios reveal a monotonically increasing pattern of abnormal returns in nearly every size decile as we progress from low HBI quintiles to high HBI quintiles: negative aggregate hidden beliefs predict poor returns, while positive hidden beliefs predict positive abnormal returns. A simple zero-cost long/short strategy that purchases the top HBI quintile portfolios and sells short the lowest HBI quintile portfolios, with equal weighting among the top eight size deciles, has an annualized four-factor alpha of 8.50% (t-statistic of 9.27 with Newey-West standard errors). The strategy’s anomalous performance is statistically significant across all size deciles and is not driven by arbitrage asymmetry; the long legs feature the strongest abnormal returns, which also stands in contrast to the predictions of standard behavioral disagreement models. The predictive power of the HBI is strongly robust, with HBI subindices derived exclusively from the non-holdings of banks, insurance companies, investment advisors, mutual funds, or pension funds all possessing strong predictive power; additionally, a highly predictive HBI is derived from estimations that use (a) alternative definitions of consideration sets, (b) an entirely different dataset of mutual funds, or (c) different included asset characteristics. Moreover, markets only gradually incorporate hidden beliefs over a multi-year time horizon, with the HBI predicting returns for at least 14 quarters.

I show that the strong and pervasive asymmetry between hidden and overt beliefs is inconsistent with traditional rational models and behavioral disagreement models along the lines of Miller (1977). The results are, however, consistent with a bounded rationality framework wherein institutions do not fully account for the fact that each institution’s inferable beliefs about asset characteristics provide us with insight into their stock-specific beliefs (recall the “value manager” example). This mechanism can be viewed as a close relative of the anchoring and adjustment heuristic described by Tversky and Kahneman (1974): when faced with the information that a given institution does not own a stock, agents form a posterior that is “shrunk” toward a default value such as the unconditional expected belief of a non-owner.$^{5}$

I consider a basic conceptual framework wherein agents face two types of information, “good news” and “bad news,” with good news readily observable but the processing of “bad news” requiring a significant cognitive or financial cost that results in shrinkage toward a default value. In this context, I show that the HBI will strongly predict returns whereas the OBI will not. Moreover, the framework does not include a disagreement channel, illustrating how the standard disagreement plus short sale constraint mechanism is not required to generate the patterns in hidden and overt beliefs. I also develop an equilibrium disagreement model and show that combining short sale constraints, disagreement, and bounded rationality creates the empirical patterns observed with

---

$^{4}$13F filings contain portfolios at the filing institution level: Vanguard, for example, is a single set of holdings as opposed to a separate filing for each of its products. Product-level data is available for mutual funds in the s12 database. I later discuss in detail what we should expect to find when comparing the results from these two different datasets.

$^{5}$Other recent theoretical and empirical contributions to this literature include Gabaix (2014), Khaw, Li and Woodford (2021), and Enke and Graeber (2023).

5

---

# Page 7

the HBI and OBI, but imposing Bayesian updating of idiosyncratic beliefs in the same framework creates a negatively predictive HBI, the opposite sign from what we observe empirically.

This paper’s findings suggest that asset demand estimation can serve as a powerful tool to extract investor beliefs from institutional holdings data, with those beliefs serving as the basis for empirical tests of hypotheses regarding belief formation and asset pricing. Most critically, the non-holdings of institutions must be carefully accounted for to conduct this analysis. When we account for censoring and the choice set that a given institution faces, we gain insight into the institution’s full set of beliefs. Institutional beliefs about the stocks they elect not to hold, which is to say hidden beliefs, robustly and persistently predict returns, whereas overt beliefs do not.

**Related Literature** I review this paper’s contributions in the context of three strands of the financial economics literature: (1) demand estimation, (2) disagreement models, and (3) rational expectations and information models.

*Demand Estimation* The primary methodological contribution of this paper is a novel approach to censored demand estimation with applications beyond financial economics. Kojien and Yogo (2019) spurred a new literature by directly estimating demand parameters from institutional holdings. This paper also estimates asset demands but focuses on leveraging the consistent estimation of institution-level demand parameters to extract investor beliefs in the context of censored data as opposed to the construction of a “demand system” under the assumption that data is not censored. I offer an econometric framework and portfolio model for demand estimation that accounts for both censoring and unobserved heterogeneous portfolio constraints among institutions. In solving these outstanding problems, this paper also proposes a microdata demand estimation approach that is new to the Industrial Organization literature and has the potential for applications outside of finance.$^{6}$

*Disagreement Models and Breadth* Miller (1977) has argued that disagreement in the presence of short sale constraints leads to overpricing because negative beliefs and information are suppressed while optimists express their beliefs through asset purchases. Hong and Stein (2007) also emphasize the disagreement and short sale constraint combination, suggesting that both are necessary to explain high trading volumes across financial markets and overvaluation of the most actively traded stocks (see also Scheinkman and Xiong (2003)). Chen, Hong and Stein (2002) confirm the conceptual underpinnings of Miller (1977) and show that stocks with greater breadth of mutual fund ownership outperform those with only limited mutual fund breadth. Unlike Chen, Hong and Stein (2002), this paper focuses not on the number of managers with suppressed negative opinions, but rather the strength of hidden beliefs, which can be positive or negative. The Hidden Beliefs

$^{6}$Hendel (1999) devises a multiple discrete choice model for PCs using microdata and notes that an alternative approach would be a linear demand model but that an implicit censoring problem arises because demand for a given brand is only observed when profitability from use of that brand exceeds that of other brands; otherwise, demand is zero. This paper, through its use of mean-variance preferences and a risk factor decomposition of the covariance matrix, turns a standard portfolio optimization problem into a censored linear form that permits the use of recent breakthroughs in econometrics to conduct estimation, thus solving a related microdata censoring problem to the one noted by Hendel (1999).

6

---

# Page 8

Index is a function of the beliefs of both short sale constrained and non-short sale constrained institutional investors and not just mutual funds, and its strong ability to predict returns is most consistent with a bounded rationality mechanism as opposed to a disagreement channel. Readily computed metrics such as the *Breadth* measure of Chen, Hong and Stein (2002) do not embed the predictive power of the HBI, with the HBI-based strategy featuring abnormal returns uncorrelated with those based on Chen, Hong and Stein (2002) as well as those based on institutional ownership, short interest, or idiosyncratic volatility. This paper’s analysis suggests that the existence of a large number of non-purchasers is not as informative about mispricing as the beliefs of the “hidden” investor population.

The primary empirical contribution of this paper is an analysis of hidden and overt beliefs that argues for the importance of bounded rationality as a separate channel from the disagreement model of Miller (1977); both mechanisms can generate large asset price distortions. Daniel, Klos and Rottke (2023) produce a new test of disagreement and find that stocks that have experienced a large price increase but are costly to borrow subsequently have poor stock performance, yielding approximately $-40\%$ in cumulative abnormal returns versus the market over a five year period. This paper’s Hidden Beliefs Index is also a statistically powerful sorting variable but does not focus on hard to borrow stocks; the basic HBI strategy tested in this paper holds 20% of stocks long and 20% short at each point in time. Moreover, the HBI predicts both overvaluation in stocks with low index values and undervaluation in stocks with high index values, with the undervaluation at least as large as the overvaluation. This symmetry argues for the importance of boundedly rational inference, not just disagreement combined with short sale constraints, in understanding deviations from rational expectations models.

*Rational Expectations and Information* Hidden beliefs lie in the background within heterogeneous agent models with private information. Although standard Rational Expectations Equilibrium (REE) models (see e.g. Admati (1985)) have agents who rationally infer private information from prices, Grossman and Stiglitz (1980) have argued that there is a fundamental tension between costly information acquisition and informational efficiency, with markets therefore incorporating private information into a public signal — equilibrium prices — that still leaves room for agents to profit from their private information. Real markets feature several major departures from the model of Grossman and Stiglitz (1980), among them the facts that many investors are short sale constrained and that positions of informed investors are publicly revealed with a lag. In this setting, if information is costly to acquire and would-be short sellers are prevented from acting on their beliefs, then the rational inference problem becomes significantly more challenging. This paper provides evidence that the informational structure of markets is complex and asymmetric, with boundedly rational inference about hidden beliefs.

**Outline** This paper proceeds as follows. Section 2 derives a censored linear model of asset demand. Section 3 provides the estimation method for this censored linear model. Section 4 reviews the data and also discusses how to impute the set of assets from which a given institution

7

---

# Page 9

selected its holdings. Section 5 briefly reviews the estimation results. Section 6 applies the estimates to study hidden and overt beliefs. Section 7 details the paper’s conceptual framework. Section 8 provides additional empirical results. Section 9 concludes.

## 2 A Model of Institutional Asset Demand

Our first step is to construct a parsimonious model of asset demand that uses only standard assumptions and can be estimated with institution-level 13F data, which only contains long positions and is therefore implicitly censored at zero. In this paper’s model, institutions possess heterogeneous beliefs about the implied future returns from observable asset characteristics such as market beta as well as an unobservable characteristic that embeds private information, institution-specific sentiment, or research. I derive optimal portfolios for both short sale constrained and non-short sale constrained institutions and show that with two standard assumptions and censored data, all optimal demands lead to a censored linear model that we can then estimate. This model builds on the asset demand estimation literature started by Kojien and Yogo (2019), but whereas Kojien and Yogo (2019) focus on constructing a “demand system” in the absence of censoring, this paper focuses on studying investors’ hidden and overt beliefs in the presence of censoring.

### 2.1 Environment

Time is discrete, $t = \{0, 1, ..., T\}$ , and $N + 1$ assets are traded each period, including a risk-free asset in perfectly elastic supply ( $n = 0$ ) and $N$ risky assets ( $n = 1, ..., N$ ) with the set of assets given by $\mathcal{N}$ . Each risky asset $n$ is in fixed finite supply of 1 with appropriate share normalization in the empirical analysis, as market capitalization is the only relevant variable in the model, not price per share. $^7$ Gross returns between $t - 1$ and $t$ are expressed as $R_t(n)$ , with the price of asset $n$ given by $P_t(n)$ . The prices and returns of all risky assets are given by vectors $P_t, R_t \in \mathbb{R}^N$ . Each asset $n$ has observable characteristics $x_{k,t}(n)$ , $k = 0, ..., K$ , where the last characteristic $x_{K,t}(n) = 1$ is a constant and the first characteristic is log market equity, $x_{0,t}(n) = \log(P_t(n))$ . $^8$ The risk-free rate is normalized to zero so that all returns are excess returns; this is without loss of generality, as the assumptions lead to static mean-variance optimization.

Institutions are indexed by $i \in \mathcal{I} = \{1, 2, ..., |\mathcal{I}|\}$ with wealth $A_{i,t}$ and portfolio weights $w_{i,t}$ for institution $i$ in period $t$ . Some institutions are subject to short sale constraints (henceforth “short sale constrained institutions” or “SSC institutions”), while others are not (“NSSC” institutions). I

---

$^7$ Market equity equals price throughout, with agents able to purchase and sell short fractional shares. Behavioral and institutional finance issues related to per share price normalizations (splits, reverse splits, “penny stock” categorization), while interesting and empirically relevant to price determination, are beyond the scope of this paper.

$^8$ In earlier versions of the paper’s theory section, as well as unreported theory results pertaining to conditions for existence of a unique equilibrium once household investors are introduced to the economy, characteristic 0 is the log of one dollar plus market equity, which is merely a technical device to avoid having to bound prices above a positive threshold. Prices are generally of the order of billions or millions in the empirical applications, so this distinction is irrelevant to the empirical sections. The constant characteristic $x_{K,t}$ is included to ensure that our identifying moment condition is without loss of generality and to serve as an intercept term.

8

---

# Page 10

follow the canonical CRRA-lognormal portfolio choice problem detailed in Campbell and Viceira (2002) and applied in Kojien and Yogo (2019); I adopt much of the notation of the latter for the reader’s convenience, though this paper’s framework features many significant modeling differences. Short sale constrained investors select a time $t$ optimal portfolio weight vector $w_{i,t} \in \mathbb{R}^N$ by solving the optimization problem

$$
\sum_{w_{i,t}(n) \leq L_{i,t}^L; \sum_{w_{i,t}(n) \geq L_{i,t}^S; w_{i,t} \geq 0} \mathbb{E}_{i,t} \left[ \log \left( A_{i,T} \right) \right]}
\quad (1)
$$

subject to the standard asset budget constraint $A_{i,t+1} = A_{i,t} w_{i,t}' R_{t+1}$ , the portfolio leverage constraints $\sum_{n>0} w_{i,t}(n) \leq L_{long}$ and $\sum_{n>0} w_{i,t}(n) \geq L_{short}$ , and the short sale constraint $w_{i,t} \geq 0$ . NSSC institutions face the same problem but without the last constraint. I abuse notation and redefine the set of assets to be $\mathcal{H}_{i,t}$ , institution $i$ ’s “habitat” or “consideration set” at time $t$ , the set of stocks that $i$ is allowed to trade and has sufficiently researched to develop a stock-specific return belief.

As shown in Campbell and Viceira (2002) and elsewhere, because of the log utility, in the case of NSSC institutions with no leverage restrictions we can use a second order Taylor series approximation of the optimal solution to find $w_{i,t} \approx \Sigma_{i,t}^{-1} \mu_{i,t}$ where $\Sigma_{i,t}$ is the covariance matrix of log returns and $\mu_{i,t} = \mathbb{E}_{i,t} \left[ \log \left( R_{t+1} \right) \right] + \frac{1}{2} \text{diag} \left( \Sigma_{i,t} \right)$ is the $N$ -dimensional vector of log expected returns since returns are lognormally distributed. As is well known in the literature, this mean-variance approximation becomes exact as the length of the discrete time intervals tends to zero. As shown in Appendix A, we can adapt this approach and find the two equations

$$
\underbrace{w_{i,t}^{NSSC} \approx \Sigma_{i,t}^{-1} \left( \mu_{i,t} - \eta_{i,t} \mathbf{1} \right)}_{\text{Non-SSC Weights}} \quad \quad \quad \underbrace{w_{i,t}^{SSC} \approx \Sigma_{i,t}^{-1} \left( \mu_{i,t} - \eta_{i,t} \mathbf{1} + \lambda_{i,t} \right)}_{\text{SSC Weights}}
\quad (2)
$$

where $\eta_{i,t}$ is the sum of the shadow values of relaxing each of the two leverage constraints and $\lambda_{i,t} \in \mathbb{R}_N^+$ is the vector of Lagrange multipliers for the short sale constraints. $^9$ When an institution has a partial set of short sale constraints, the same equation applies but with the $n$ th component of $\lambda_{i,t}$ redefined to be 0 for all $n$ such that the institution does not face a short sale constraint.

## 2.2 Portfolio Weights as a Censored Function

Two crucial assumptions allow for this paper’s estimation procedure: (1) beliefs about returns are linear in asset characteristics and (2) the log return covariance matrix has a factor structure with the factors belonging to the space spanned by the belief-relevant characteristics. This subsection develops the censored model under these two assumptions.

---

$^9 \eta_{i,t} = \eta_{i,t}^{Long} - \eta_{i,t}^{Short}$ since only one of the two constraints can bind when $L_{long} > L_{short}$ . Stocks have positive expected returns over most time horizons and therefore for 13F filing institutions we should generally expect that $\eta_{i,t}^{Short} = 0$ for each manager studied, but allowing for both upper and lower constraints increases the generality of the framework.

9

---

# Page 11

**Linear Belief Structure** Each asset has $K + 1$ observable characteristics, which are functions of market capitalization (price), return history, and accounting data. Each investor has linear beliefs: return expectations are a linear combination of observable characteristics and a private unobservable asset characteristic that constitutes each agent’s idiosyncratic belief about returns for assets, as specified in Assumption 1. $^{10}$

**Assumption 1.** *(Linear Beliefs)* The log expected return vector capturing agent $i$ ’s beliefs is given by the equation

$$
\mu_{i,t} = \sum_{k=0}^{K} \beta_{k,i,t} x_{k,t} + \epsilon_{i,t}
\quad \text{(3)}
$$

where $x_{k,t}$ is the $N$ -tuple of characteristic $k$ for each asset, $\beta_{k,i,t}$ is agent $i$ ’s belief about returns to characteristic $k$ , and $\epsilon_{i,t}$ is $i$ ’s vector of expected returns driven by private beliefs; $x_{0,t} = \log(P_t)$ , with the logarithm taken elementwise, is the first characteristic (“size”).

I define $x_{K,t} = \mathbf{1}$ throughout so that a constant is always included in the linear structure. All prior research that uses linear factor structures as well as many REE models feature similarly structured return beliefs.

**Covariance Matrix Decomposition via a Single Common Risk Factor** I begin with a single common risk factor assumption for the covariance matrix for ease of exposition, then I generalize to the arbitrary multifactor case. I drop time subscripts for legibility.

**Assumption 2.** *(Single Risk Factor)* The covariance matrix $\Sigma$ for log returns is given by $\Sigma = \Gamma \Gamma' + D$ where $D$ is a positive definite diagonal matrix and $\Gamma \in \mathbb{R}^N$ is the common risk factor.

Following standard terminology, the common factor $\Gamma$ will be called “market risk” throughout the paper, while $D$ will be referred to as “idiosyncratic risk.” The most widely used decomposition features $\Gamma$ as the product of stocks’ market betas with the standard deviation of stock market returns. Although I also use the Woodbury matrix identity for matrix inversion in my proof, this representation and the subsequent derivation differ from that of Kojien and Yogo (2019) because whereas they assume each asset has the same idiosyncratic volatility, here each asset possesses an arbitrary level of idiosyncratic volatility, captured by the diagonal of the matrix $D$ . Most importantly, this paper derives a censored linear functional form under minimal assumptions in lieu of an exponential linear form under substantial parameter restrictions; see Appendix V for a detailed set of similarities and differences with respect to Kojien and Yogo (2019).

**Optimal Portfolios under a Single Risk Factor** In Appendix A I use matrix algebra to show that the optimal portfolios for NSSC and SSC institutions from equation (2) can be rewritten as

---

$^{10}$ Assumption 1 is effectively a separability condition over any given hypercube B because of Stone-Weierstrass: we can always add polynomial functions of characteristics, but we will require that the idiosyncratic belief component $\epsilon_{i,t}$ be additively separable and linear.

10

---

# Page 12

$$
w^{NSSC*} = D^{-1} \left( \mu - \eta \mathbf{1} - \kappa^{NSSC} \Gamma \right); \; w^{SSC} = D^{-1} \left( \mu - \eta \mathbf{1} + \lambda - \kappa^{SSC} \Gamma \right)
\quad (4)
$$

respectively, where $\kappa^{NSSC} = \theta \Gamma' D^{-1} (\mu - \eta \mathbf{1})$ , $\kappa^{SSC} = \theta \Gamma' D^{-1} (\mu - \eta \mathbf{1} + \lambda)$ , and $\theta = (1 + \Gamma' D^{-1} \Gamma)^{-1}$ , a positive scalar. Recall that $\lambda$ is the vector of Lagrange multipliers that captures the shadow value of relaxing each of the short sale constraints. Institutional portfolios are therefore equal to log expected return minus a shrinkage factor that adjusts portfolios downward (in the typical case where $\Gamma' D^{-1} (\mu - \eta \mathbf{1})$ is positive) to account for variable exposure to the common risk factor, with that sum scaled by the inverse of idiosyncratic risk. Stocks with lower idiosyncratic variance are upweighted, as are stocks with low or negative exposure to the common risk factor.

Although the short sale constrained investor weights in equation (4) include $\lambda$ , a complicated implicit function of return beliefs and the covariance matrix, we can simplify this expression and eliminate the $\lambda$ . $D^{-1}$ is a positive definite diagonal matrix, so we must have that $\left( \mu - \eta \mathbf{1} - \kappa^{SSC} \Gamma \right)_n > 0$ whenever $w_n^{SSC} > 0$ because $\lambda_n = 0$ by complementary slackness. Likewise, when $\lambda_n > 0$ we must have $w_n^{SSC} = 0$ . I have now shown that if we add the data censoring where the observed $w$ is actually $\max \{0, w^*\}$ , then we have found

$$
w = \max \left\{ 0, D^{-1} (\mu - \eta \mathbf{1} - \kappa \Gamma) \right\}
\quad (5)
$$

where the max operator is taken elementwise and $\kappa$ is either $\kappa^{SSC}$ or $\kappa^{NSSC}$ depending on whether the investor is short sale constrained. Under censoring all of these portfolio weights have the same functional form: the inverse of idiosyncratic variance multiplied by a linear combination of the return belief vector $\mu$ , a constant vector $\mathbf{1}$ , and the common risk factor $\Gamma$ . All that differs is the computation of the risk factor shrinkage parameters $\kappa^{NSSC}$ and $\kappa^{SSC}$ . In the appendix, I show that the same functional form applies under partial short sale constraints.

**A Censored Linear Model via Linear Beliefs** Combining equation (5) with the linear belief specification of Assumption 1 and regrouping terms gives us the following theorem (suppressing subscripts $i$ and $t$ for clarity):

**Theorem 1.** Suppose assumptions (1) and (2) hold true and that the observed portfolios are $w = \max (0, w^*)$ where $w^*$ is the true vector of uncensored portfolio weights. Then regardless of leverage constraints and short sale constraints, variance-scaled observed weights $y = Dw$ can be expressed as

$$
y = Dw = \max \left\{ 0, \sum_{k=0}^{K} \tilde{\beta}_k x_k + \epsilon \right\},
\quad (6)
$$

where $\tilde{\beta}_1 = \beta_1 - \kappa$ , $\tilde{\beta}_K = \beta_K - \eta^{Long} + \eta^{Short}$ , and $\tilde{\beta}_k = \beta_k$ for $k \notin \{1, K\}$ .

Note here that we have gone from $\beta$ , the belief parameters, to $\tilde{\beta}$ , the demand parameters. For all characteristics $k$ except for the coefficient $\beta_1$ on the risk factor $\Gamma = x_1$ and the coefficient $\beta_K$

11

---

# Page 13

on the constant $x_K = 1$ , $\tilde{\beta}_k$ and $\beta_k$ are the same. The belief ( $\beta$ ) and demand ( $\tilde{\beta}$ ) terms differ for the risk factor and constant because (1) for the risk factor term, demand contributions from return expectations and risk aversion are collinear and (2) for the constant term, optimism or pessimism about risky assets (the belief coefficient $\beta_K$ ) is collinear to the desire to relax leverage (the shadow values $\eta^{Long}$ or $\eta^{Short}$ ). Appendix D contains a more elaborate discussion of belief parameter recovery versus local demand parameter recovery and its implications for other topics in the literature.

We therefore have a censored linear functional form that we can estimate. Our dependent variable is not portfolio weights but rather portfolio weights multiplied by idiosyncratic variance, while the right-hand side is linear in characteristics but left censored at zero.

**A General Multifactor Model** Here I assume a more general factor structure and derive the same censored linear model.

**Assumption 3.** *(Multiple Factor Structure)* The covariance matrix $\Sigma$ is given by $\Sigma = \sum_{j=1}^r \Gamma_j \Gamma_j' + D$ with $D$ an arbitrary diagonal positive definite matrix and $r$ non-collinear risk factors $\Gamma_1, ..., \Gamma_r$ , with $r \geq 2$ .

In Appendix C I show that the weight vector $w$ can be expressed as $w = D^{-1}(\mu + \lambda) - \sum_{j=1}^r \kappa_j D^{-1} \Gamma_j$ where $\kappa_j = a_j' D^{-1} (\mu + \lambda)$ for a vector $a_j'$ that is solely a function of the known risk factors $\Gamma_j$ and $D$ . Moreover, using similar logic to that above, I show that

$$
w = \max \left\{ 0, D^{-1} \left( \mu - \sum_{j=1}^r \kappa_j \Gamma_j - \eta \mathbf{1} \right) \right\}
\quad (7)
$$

after data censoring. As before, when each of the $\Gamma_j$ are included in the linear belief specification for $\mu$ so that $\mu = \beta_0 \log(1 + P_t) + \sum_{k=1}^r \beta_k \Gamma_k + \sum_{k=r+1}^K \beta_k x_k + \epsilon$ , we are left with equation (6) from Theorem 1 again, just with different constants $\kappa$ that map demand coefficients to belief coefficients. Proposition 3 in Appendix C provides the correction constants for the multifactor model if we wish to obtain estimates of short sale constrained institutions’ belief parameters as opposed to demand parameters.

The expression in Theorem 1 is unintuitive because it shows that the idiosyncratic variance-scaled weight vector $Dw$ lies in the censored span of asset characteristics, shifted by idiosyncratic beliefs $\epsilon$ . Yet the demand parameters $\tilde{\beta}_k$ that capture this linear-seeming relationship are themselves functions of characteristics, risk factors, Lagrange multipliers, and idiosyncratic beliefs. What the theorem then reveals is a censored linear relationship that applies to a specific snapshot observation of a portfolio: once we observe weights $w$ , idiosyncratic variance $D$ , and characteristics $x$ at a given point in time, the relationship is $y = Dw = \max \left\{ 0, \sum_{k=0}^K \tilde{\beta}_k x_k + \epsilon \right\}$ for some scalars $\tilde{\beta}_k$ . With enough observations of stocks held ( $w_n > 0$ ) and stocks not held ( $w_n = 0$ ), we can therefore estimate the $\tilde{\beta}_k$ and learn about $\epsilon$ under the right moment conditions, which are detailed in the next section.

12

---

# Page 14

# 3 Institutional Demand Estimation

The last section derived a censored linear functional form for portfolio weights, so we now turn our focus to estimating the model. One critical point of emphasis throughout is that we can only identify institutions’ demand parameters when zero holdings are accounted for and a conditional median zero restriction — not a mean zero restriction — is used as the identifying assumption. The median zero restriction is not commonly used in financial economics but here is vital to identification.

## 3.1 Estimation Problem

Let $\sigma_n^2$ be the idiosyncratic variance of stock $n$ , the $n$ th diagonal element of the matrix $D$ from the last section. Writing out equation (6), our initial estimation problem takes the form

$$
y_{i,t}(n) = \sigma_n^2 w_{i,t}(n) = \max \left\{ 0, \tilde{\beta}_{0,i,t} \log(P_t(n)) + \sum_{k=1}^K \tilde{\beta}_{k,i,t} x_{k,t}(n) + \epsilon_{i,t} \right\}
\quad (8)
$$

because all short positions are censored or investors are short sale constrained. I have made explicit the fact that the right-hand side contains a censored function of an endogenous variable. Furthermore, the estimation task is complicated by the limited number of observations for some institutions, as well as common challenges such as convergence of numerical optimizers and potentially undesirable small sample properties. This paper’s estimation procedure aims to circumvent these issues.

## 3.2 Identifying Moment Conditions and Instrumental Variables

Here I review the choice of estimation method, the control function approach to endogeneity, and the identifying moment condition.

### Choice of Estimation Approach

Conducting estimation in the presence of a censored variable is a standard econometric problem, with the Tobit maximum likelihood approach being one of the most canonical. In this paper’s setting, however, we cannot apply the Tobit because (a) one of the variables is endogenous and (b) the Tobit is notoriously sensitive to heteroskedasticity and non-normality of the error terms (see e.g. Lee and Maddala (1985)). The Tobit and other non-quantile-based methods can still be adapted to accommodate endogeneity, but the Tobit’s point identification of parameters relies on assuming that the idiosyncratic beliefs are independent of characteristics. This homoskedasticity assumption is extraordinarily restrictive and limits the interaction between censoring and the unobservables. Because we do not know the distribution of a given investor’s beliefs across stocks (e.g. consider a manager with just two idiosyncratic stock assessments corresponding to “good” and “bad,” with the expected return spread between these varying with operating profitability), allowing heteroskedasticity and a flexible distribution of investor beliefs is vital to this paper’s

13

---

# Page 15

setting. The Censored Least Absolute Deviations (CLAD) estimator of Powell (1984) is a more robust approach to censored regression that does not impose the Tobit’s strict distributional assumptions on investors’ idiosyncratic beliefs but still cannot handle endogeneity. Moreover, the CLAD approach is computationally challenging due to the estimator being computed via non-convex optimization. Other approaches, some of which are reviewed in Appendix E, have been proposed to handle censoring and endogeneity, but many are computationally challenging and generally involve nonparametric estimation and various tuning parameters. For most standard economic questions, these computational challenges would be surmountable, but this paper’s setting requires the estimation of 250,000 censored regressions, one for every quarterly portfolio of each institution over a 37-year period. Computational tractability and scalability are therefore paramount in proposing an approach in the context of demand estimation.

I use the Sequential Censored Quantile Regression (SCQR) approach of Chen (2018) because it is uniquely computationally tractable, scalable, and consistent. Most importantly, it avoids strong distributional assumptions on institutions’ idiosyncratic beliefs, which are the paper’s main objects of interest. The primary issue in applying SCQR directly, however, is that although Chen (2018) develops an approach to SCQR with an endogenous variable, the SCQR-IV method, this approach will often fail to converge when data is heavily censored. Indeed, the data censoring problem in asset demand estimation is extreme: when a manager selects 100 stocks from a consideration set of 1,000 stocks, this implies that 90% of our observations are censored.

I therefore adapt the SCQR approach to a control function approach to endogeneity with a linear functional form assumption on the relationship between the unobservables and the control variable. In essence, we will use an IV to build a control variable that controls for the endogeneity issue when added to the regression. This approach allows us to directly use the computationally favorable SCQR approach under a median zero restriction: investors’ idiosyncratic beliefs have a zero median conditional on the included regressors and the control variable. To the best of the author’s knowledge, this paper is the first to propose a computationally tractable and scalable approach to censored demand estimation in the presence of endogeneity.

## Control Function Approach to Endogeneity

We start by accounting for the endogenous variable, the log of market cap. This variable is endogenous because institution $i$ can influence the contemporaneous prices of assets it holds. Moreover, I do not place any restriction on the private beliefs of investors, which can be arbitrarily correlated across institutions. This correlated unobservables issue is especially relevant in the investment management industry, where similar data sets and research methodologies can result in a strong relationship between an institution’s idiosyncratic return expectations and price because other institutions possess correlated beliefs. We must therefore be concerned that $\epsilon_{i,t}$ is strongly related to price. Non-price characteristics are considered exogenous and labeled $X_t^{-0}(j) = \left(x_{1,t}(j) \quad x_{2,t}(j) \quad \cdots \quad x_{K,t}(j)\right)' \in \mathbb{R}^K$ .

Following one standard approach in the econometrics literature, I form a control function $v_t$

14

---

# Page 16

that when added to the regression will “control for” the endogeneity of $ x_{0,t} = \log(P_t) $ . First, let us suppose we have a scalar instrument for log price $ z_t(j) \in \mathbb{R} $ (this will be detailed in the next section) and that the instrument vector $ Z_t(j) = \begin{pmatrix} z_t(j) & X_t^{-0}(j)' \end{pmatrix}' \in \mathbb{R}^{K+1} $ for stock $ j $ satisfies the standard relevance, non-redundancy, and exogeneity conditions. $^{11}$ Second, I assume that private unobservable beliefs are a linear combination of two components: (1) a “control function” $ v_t $ that embeds how aggregate sentiment among institutions impacts price and (2) an “idiosyncratic unobservable belief” $ u_{i,t} $ that has a zero median conditional on $ v_t $ and all characteristics $ X_t $ , including price. Specifically, we assume $ \epsilon_{i,t} = \pi_{i,t}v_t + u_{i,t} $ where $ \pi_{i,t} $ is just a scalar coefficient.

We find this “control function” $ v_t $ by using our exogenous characteristics and the excluded instrument for log price $ z_t $ and estimating the equation $ \log(P_t) = Z_t\Upsilon_t + v_t $ via OLS under the moment condition $ \mathbb{E}[v_t(j)|Z_t(j)] = 0 $ ; we compute control variables $ v_t $ for each time period $ t $ , with $ \Upsilon_t \in \mathbb{R}^{K+1} $ representing the parameters in the relationship between log price and the instruments (our “first stage”) and $ Z_t \in \mathbb{R}^{N \times K+1} $ representing the instrument matrix.

The control variable $ v_t $ is analogous to the inferred aggregated beliefs obtained from REE models like those of Admati (1985) and Hellwig (1980), only here the coefficient is estimated as opposed to computed via Bayesian updating. We can readily imagine $ v_t $ as another signal received by agent $ i $ that is given weight $ \pi_{i,t} $ . Although $ v_t $ is estimated, we deem $ v_t $ to be “known to the econometrician” because we possess the entire universe of equities and compute $ v_t $ from the full universe of stocks. For the purposes of control variable computation, our sample is the entire population.

# Identifying Moment Restriction: Conditional Median Zero

Our identifying conditional median restriction, which exploits $ v_t $ as a (known to the econometrician) control variable, is that

$$
\mathbb{E}[m(u_{i,t}(j))|X_t(j),v_t(j)] = 0
$$

where $ m(\epsilon) = 1 (\epsilon < 0) - 0.5 $ , and we can write the censored linear model as

$$
y_{i,t}(j) = \max \left\{ 0, \tilde{\beta}_{0,i,t} \log(P_t(j)) + \sum_{k=1}^K \tilde{\beta}_{k,i,t} x_{k,t}(j) + \tilde{\pi}_{i,t} v_t(j) + u_{i,t}(j) \right\}.
$$

Thus the private beliefs $ u_{i,t} $ of agent $ i $ have a zero median conditional on the control variable and observable characteristics, but using zero is without loss of generality because of the inclusion of the constant $ x_{K,t} = 1 $ in the estimation. $^{12}$

[^1]: $^{11}$ Specifically, $ rank \left( \mathbb{E}[Z_{i,t}(j)X_t(j)'] \right) = K + 1 $ , $ \mathbb{E}[Z_{i,t}(j)Z_{i,t}(j)'] \succ 0 $ , and $ \mathbb{E}[Z_{i,t}(j)\epsilon_{i,t}] = 0 $ .

$^{12}$ This assumption is strong in that I specify the form taken by the endogeneity and require that the unobservable term $ \epsilon $ be a linear function of the control variable $ v $ and a median independent component $ u_{i,t} $ . Instead of requiring that the $ \epsilon $ terms have a zero median, I require that the $ u $ terms have a zero median; in essence, we are forcing the control variable to account for the endogeneity and serve as a publicly observed variable that absorbs any equilibrium relationship between log price and private beliefs. Again, this is very similar in spirit to the derived equilibrium beliefs of agents in REE models such as Hellwig (1980), but the assumption is still strong. In Appendix E I briefly review other methods, many of which do not require this form of assumption. Ultimately, however, we must sacrifice a degree of generality in exchange for significant gains in computational tractability, all while avoiding more restrictive assumptions (e.g. symmetry) on the distribution of unobservables.

---

# Page 17

# Why a Conditional Median Restriction?

The median zero restriction, as opposed to a mean zero restriction, is vital because we do not observe $y_{i,t}^*(j)$ and instead observe $y_{i,t}(j) = \max\left(0, y_{i,t}^*(j)\right)$ due to censoring. If we attempt to apply a mean zero restriction to point identify the demand parameters, then we also need to make strong assumptions about the independence of idiosyncratic beliefs and the other characteristics (as well as the control variable); these assumptions preclude heteroskedasticity, for example, but homoskedasticity is unjustifiable in this paper’s context. If we assume homoskedasticity but errors are heteroskedastic, then estimators based on a mean zero restriction will be inconsistent. A conditional median zero restriction is similar in spirit to a conditional mean zero restriction: instead of requiring the mean of $u$ conditional on $\{X, v\}$ to be constantly zero, we require that its conditional median be constantly zero. Estimators based on this conditional median zero restriction, a quantile restriction, are consistent even if the $u$ are heteroskedastic. This attractive property of quantile-based estimators in the presence of censoring comes from the equivariance property of quantiles to monotone transformations (censoring is a monotone transformation): if we take the median of data that has been censored at zero, that is the same as taking the median of the uncensored data and then censoring the median at zero. $^{13}$

## 3.3 Estimation via SCQR

I use the robust three-step version of SCQR to estimate institutional asset demand. I begin with the basic intuition for two-step estimation and then fill in important details that make the procedure robust. This paper primarily hews closely to the approach of Chen (2018), but I adapt it to a control variable approach to improve the computational properties for this paper’s setting.

### SCQR Intuition: A Descending Grid of LP Problems by Oracle Approximation

We are interested in the median regression, $\tau = 0.5$ , but traditional censored quantile regression approaches such as the Censored Least Absolute Deviation (CLAD) estimator of Powell (1984) are complicated, non-convex problems. Standard quantile regression, however, is straightforward to estimate via linear programming techniques. In fact, the concept of median regression predates least squares and minimizes the sum of the absolute value of residuals. Quantile regression minimizes an asymmetric linear loss function that looks like a check mark instead of the absolute value function used in median regression.

---

$^{13}$ As shown in Newey (2001), in censored regression models identification is dependent on the moment condition function $m(\epsilon)$ such that $\mathbb{E}[m(\epsilon)|X] = 0$ being constant below some value. When $m(\epsilon) = 1(\epsilon < 0) - 0.5$ as in this paper, which leads to a conditional median restriction, then this condition is satisfied. The SCQR method uses this moment restriction to devise an estimator for $\tilde{\beta}_{i,t}$ by noting that $\mathbb{E}^*(m(u)|z) = 0 \implies \mathbb{E}(1(z'\beta > 0)m(u)|z) = 0$ : we take a moment condition for the uncensored (latent) data, namely that the median belief is zero conditional on $z$ , and convert it into a moment condition for the censored data that selects out points $\{j : z_j'\beta > 0\}$ where the median of $y^*|z$ rises above zero, the censoring point. The SCQR method employed in this paper and described in the next subsection simultaneously estimates $\beta$ and the set of points $\{j : z_j'\beta > 0\}$ . All censored quantile regressions are essentially performing the same step: they attempt to isolate the points $\{j : z_j'\beta > 0\}$ that contain the information we need to determine $\beta$ . Other quantiles $\tau \neq 0.5$ can also be used instead of the median.

---

# Page 18

SCQR converts a normally computationally complex problem into a sequence of computationally easy quantile regressions (QR); it exploits the fact that if we slightly tilt the “check loss” function that penalizes residuals, the estimated parameters will smoothly vary. $^{14}$ We will therefore arrive at censored median regression via a series of descending quantile regressions. The goal of these quantile regressions is to isolate the subset of observations $\{x : x'\beta > 0\}$ , which is to say the set of data points where the median value of $y$ conditional on $x$ rises above the censoring point. These points are what we require to find $\beta$ ; in fact, the traditional CLAD estimator can be found by minimizing the absolute value of the residuals $|y - x'\beta|$ over just these points. But this relies on an oracle in that $\beta$ is precisely the parameter we wish to estimate. The key innovation of the SCQR method is that it conducts iterated subsample selection to find an approximation to this oracle set, then conducts the desired median regression.

Let $\beta(\tau)$ be the parameters from the regression where we require the $\tau$ th quantile of $y|x$ to be $x'\beta(\tau)$ . Extreme upper quantiles do not suffer from a censoring problem, so the subsample selection $\{x : x'\beta(\tau_u) > 0\}$ for $\tau_u = 0.99$ can be accurately approximated by traditional QR. We can then use the subsample $\left\{x : x'\hat{\beta}(\tau_u) > 0\right\}$ from QR with $\tau_u$ to conduct QR for $\tau = 0.98$ and find a new subsample $\{x : x'\beta(0.98) > 0\}$ , then use that subsample for QR with $\tau = 0.97$ , continuing down the grid of values until we arrive at a subsample for $\tau = 0.5$ along with the desired estimate $\hat{\beta}(0.5)$ .

## Three-Step Estimation Procedure in Detail

To make the process explicit and fill in important details that contribute to the method’s robustness, let $\beta = \left(\tilde{\beta}, \pi\right)$ be the vector of demand parameters and control function parameter, let $y_j^*$ be the latent dependent variable in Equation (10), and let $\tilde{z}_j = \left(x_0(j), x_1(j), ..., x_K(j), v(j)\right)$ where I have dropped time subscripts for legibility. Then we will use the model

$$
Q_{y^*|z}(\tau) = \tilde{z}'\beta(\tau)
$$

where $\tau \in (0, 1)$ is the quantile: the $\tau$ th quantile of the latent $y^*$ conditional on $\tilde{z}$ is a linear function of the characteristics and control variable, with $\beta(\tau)$ the vector of parameters. Because of short sale constraints or data censoring, $y^*$ is left censored, but if it were observed we could solve the problem by

$$
\beta(\tau) = \arg\min_{\hat{\beta} \in B} \sum_j \left[\rho_\tau\left(y_j^* - \tilde{z}_j'\hat{\beta}\right)\right]
$$

where $\rho_\tau(\epsilon) = (\tau - 1(\epsilon < 0))\epsilon$ is the usual Koenker and Bassett (1978) “check” loss function and $B$ is a hypercube that puts outer bounds on the parameters. When $\tau \approx 1$ the solution to the censored problem should be identical to that of the uncensored problem because only values below zero are censored.

Now let us form a grid of values $S_{L_n} = \{0.99 = \tau_u = \tau_0 > \tau_1 > ... > \tau_{L_n} = \tau_l = 0.5\}$ where

---

$^{14}$ More precisely, we are assuming that if $\beta(\tau)$ is defined as the $\tau$ th conditional quantile of $y^*$ given $x$ , $Q_{y^*|x} = x'\beta(\tau)$ , then $\beta(\tau)$ is Lipschitz in $\tau$ . This is Assumption 4 of Chen (2018).

17

---

# Page 19

$\tau_j - \tau_{j+1}$ is always small, thus exploiting the continuity of quantile regression coefficients. Choose $L_n = \max\left(40, n^{1/2}\right)$ or $L_n = \max\left(20, \frac{1}{2}n^{1/2}\right)$ so that $L_n \to \infty$ as $n \to \infty$ . We define

$$
\hat{\beta}\left(\tau_0\right) = \arg\min_{\hat{\beta} \in B} \sum_{l=1}^n \rho_{\tau_0}\left(y_l - \tilde{z}_l'\hat{\beta}\right)
$$

so that $\hat{\beta}\left(\tau_0\right)$ is merely the coefficient vector for standard (uncensored) quantile regression at quantile $\tau_0$ . Now for each of $j = 0, ..., L_n - 1$ we do the following steps:

1. Let $Q_{0.01}\left(\tilde{z}_r'\hat{\beta}\left(\tau_j\right) : \tilde{z}_r'\hat{\beta}\left(\tau_j\right) > 0\right)$ denote the 0.01 quantile of positive values of $\tilde{z}_r'\hat{\beta}\left(\tau_j\right)$ . Select the subsample

$$
J_0 = \left\{h : \tilde{z}_h'\hat{\beta}\left(\tau_j\right) > Q_{0.01}\left(\tilde{z}_r'\hat{\beta}\left(\tau_j\right) : \tilde{z}_r'\hat{\beta}\left(\tau_j\right) > 0\right)\right\}.
$$

2. Define an initial estimator

$$
\hat{\beta}_0\left(\tau_{j+1}\right) = \arg\min_{\hat{\beta} \in B} \sum_{h \in J_0} \rho_{\tau_{j+1}}\left(y_h - \tilde{z}_h'\hat{\beta}\right).
$$

3. Select the subsample

$$
J_1 = \left\{h : \tilde{z}_h'\hat{\beta}_0\left(\tau_{j+1}\right) > Q_{0.005}\left(\tilde{z}_r'\hat{\beta}_0\left(\tau_{j+1}\right) : \tilde{z}_r'\hat{\beta}_0\left(\tau_{j+1}\right) > 0\right)\right\}.
$$

4. Given $J_1$ , estimate $\beta\left(\tau_{j+1}\right)$ via

$$
\hat{\beta}\left(\tau_{j+1}\right) = \arg\min_{\hat{\beta} \in B} \sum_{h \in J_1} \rho_{\tau_{j+1}}\left(y_h - \tilde{z}_h'\hat{\beta}\right).
$$

We have now arrived at the desired estimate $\hat{\beta}\left(\tau_l\right) = \hat{\beta}\left(0.5\right)$ . When the sets $J_0$ or $J_1$ become empty at any stage, the estimation procedure will fail to converge, but we have gained important information: the rank condition required to learn the demand parameters with censored data is violated or nearly violated, therefore we cannot successfully estimate this institution's demand in this sample and will exclude it from our analysis.

When we converge to a solution, this method has given us an estimate, $\hat{\beta}\left(0.5\right)$ , of how an investor's demand changes as a function of the observable characteristics and control function. Most critically, we have obtained this estimate by solving approximately 100 linear programming problems instead of one non-convex problem, and we have done so without a strict distributional assumption. We can now move to defining the included characteristics and IV used in the empirical approach.

---

# Page 20

# 4 Empirical Approach: Data, Characteristics, and Instrument Construction

In this section I provide details on the data sources, asset characteristics, classification scheme for rigid versus dynamic managers, consideration set construction methodology, and finally the creation of an instrument for the log of price.

## 4.1 Data Description

All stock price, return, and market capitalization (via shares outstanding) data are from the CRSP Daily Stock Database. I use the CRSP/Compustat Merged - Fundamentals Quarterly Database from WRDS for accounting data. I use quarterly accounting data and exclude from estimation all stock/time period combinations where corresponding accounting data is unavailable. I use a one quarter lag for accounting data to counterbalance the two competing sources of bias from excessively lagged versus nonpublic data. The study of hidden beliefs and return predictability in Section 6 exclusively uses estimates from prior quarters’ 13F filings, making all accounting data used in the HBI calculations lagged by more than a quarter.

Institutional holdings data are obtained from the Thomson Reuters Institutional Holdings Database (via WRDS), which aggregates all data filed with the U.S. Securities and Exchange Commission (SEC) on a quarterly basis into a single database (s34 Database). Any investment manager with more than $100M in qualifying securities is obligated to file a 13F report within 45 days after the close of a calendar quarter. Each report contains the manager’s name, CUSIP numbers, total shares held at quarter end, total market values, and the names of the equities. Additional details on share code restrictions, computation of assets under management, and ownership dataset construction are contained in Appendix P.

## 4.2 Linear Characteristics-Based Model of Beliefs and Covariance

The main empirical sections use the factors of Fama and French (2015) to create a linear belief specification; the characteristics are the same set as Kojien and Yogo (2019), while Appendix G uses an alternate set based on the value and momentum characteristics of Asness, Moskowitz and Pedersen (2013).$ ^{15} $ Formally, define $ x_0(n) $ to be the log of market capitalization, $ x_1(n) $ to be stock $ n $’s beta computed using a half year of daily data, $ x_2(n) $ to be annual dividends divided by last quarter’s book equity, $ x_3(n) $ and $ x_4(n) $ to be operating profitability and investment according to the definitions of Fama and French (2015), $ x_5(n) $ to be the log of last quarter’s book equity, $ x_6(n) $ to be the control variable, and $ x_7 $ to just be the constant term 1. Profitability, investment, and six-

$ ^{15}$The 2-12 momentum variable of Asness, Moskowitz and Pedersen (2013) raises the question of endogeneity since shifts in private beliefs can be correlated with levels. Nonetheless, the predictive power of hidden beliefs is approximately the same regardless of specification used, with highly consistent results across the two different models. Other sets of characteristics can be used as well; the main requirement for generating a predictive HBI is that the included exogenous variables explain a sufficient amount of variation in investors’ portfolios.

19

---

# Page 21

month daily betas are all winsorized at their respective 1% and 99% levels, while dividend-to-book is winsorized at the 99% level.

To complete the specifications of characteristics and variance, the $n$ th diagonal element of the idiosyncratic variance matrix $D_{i,t}$ is obtained from the data in the standard way: we compute stock $n$ ’s log excess return variance over the past 126 trading days and subtract the market factor’s variance times the square of stock $n$ ’s market beta. $^{16}$ While this model of idiosyncratic risk is simple, it follows a long tradition in the asset pricing literature that emphasizes the importance of both a common risk factor and idiosyncratic risk. Goyal and Santa-Clara (2003) show that the average idiosyncratic variance of stocks predicts returns positively whereas total market variance does not. Meanwhile, Campbell, Lettau, Malkiel and Xu (2001) find that idiosyncratic risk has increased over time and that larger numbers of equities are required to diversify away such risks, making idiosyncratic risk heterogeneity crucial in models such as that of this paper.

## 4.3 The Manager Menagerie: Rigid Institutions, Dynamic Institutions, and Consideration Sets

Consideration sets are vital to estimation: they determine which stocks an investor selects from and therefore which non-holdings are true choices. These zeros are important contributors to the censored quantile regressions that allow us to estimate demand. Past approaches such as Kojien and Yogo (2019) have relied on “universes” comprised of past and current holdings. Yet investors regularly consider a given stock, formulate a persistent negative belief, and subsequently fail to invest in the stock (or hold a short position) for many quarters or even years. Moreover, investors might consider 1,000 stocks but only select 100 or 200 for their portfolios. In this paper I impute consideration sets by first determining whether an investor is actively forming beliefs. These dynamic, non-passive investors consider a set of industries (defined by four-digit NAICS codes), with every stock in the considered industries added to our imputed consideration sets. In this subsection I fully characterize the process of separating “dynamic” and “rigid” managers and determining the industries within each investor’s consideration set.

This paper’s empirical approach divides managers into two broad categories: those with rigid mandates and those with dynamic mandates. Rigid mandates require explicit portfolio weights (e.g. index funds with market capitalization or equal-weighted schemes) or nonzero weights over a pre-defined universe of equities that must always be held regardless of market conditions. Most such investment vehicles can be considered “passive investment” products, although a limited number of non-passive managers may be classified as rigid if they routinely hold almost the same set of equities with changing weights. $^{17}$

---

$^{16}$ I compute beta as $\text{Cov}(\log(1+R_i), M)/\text{Var}(M)$ because $M$ is more commonly used by investors than $\log(1+M)$ , though using $\text{Cov}(\log(1+R_i), \log(1+M))/\text{Var}(\log(1+M))$ with $\log(1+M)$ as the market risk factor provides functionally identical results since the returns are daily. The paper’s main empirical results are robust to simplistically approximating idiosyncratic variance with a stock’s total variance in the estimations; for most stocks the majority of the volatility is idiosyncratic.

$^{17}$ By way of illustration, a biotechnology mutual fund manager who holds the same 30 equities every period but

20

---

# Page 22

**Definition 1.** *(Rigid Institution)* A manager is “rigid” or has a “rigid mandate” at time $t$ if it satisfies either of the following two criteria:

1. The sets of stocks held over each of the past twelve quarters and current quarter overlap by an average of 95% or more with the previous quarter’s holdings.

2. The sets of stocks held over each of the past twelve quarters and current quarter overlap by at least 90% or more with the previous quarter’s holdings AND EITHER

   (a) $\|\hat{w}_{j,t-k} - w_{j,t-k-1}\|_1 < 0.1 \ \forall k \in \{0, ..., 12\}$ , where $\hat{w}_{j,t}$ is $w_{j,t}$ restricted to those assets with nonzero holdings at time $t-1$ OR

   (b) $\|\tilde{w}_{j,t-k} - w_{j,t-k-1}\|_1 < 0.1 \ \forall k \in \{0, ..., 12\}$ , where $\tilde{w}_{j,t}$ is equal to the weights at time $t$ for those stocks with nonzero holdings at time $t-1$ , adjusted for the changes in the cross sectional distribution of fractional market equity between the two periods.

Criterion 2(a) captures fixed-weight schemes while 2(b) captures capitalization-weighted or fixed-share schemes that allow for the portfolio weights to change with price fluctuations. For any rigid institution $i$ , we take the consideration set at time $t$ , $\mathcal{H}_{i,t}$ , to consist solely of those stocks for which it has positive weights at time $t$ . As these managers display behavior inconsistent with belief and information-driven optimization (Vanguard and Blackrock are two prominent “rigid managers”), estimating demand equations for these institutions is uninformative about asset demand. Dynamic managers have time-varying holding sets and weights, with “dynamic” managers defined as below.

**Definition 2.** *(Dynamic Institution)* A manager is “dynamic” or has a “dynamic mandate” at time $t$ if it does not have a rigid mandate at time $t$ .

Dynamic managers have consideration sets that resemble an iceberg: only a small fraction of the universe is directly visible through 13F filing data, while the zero holdings and short positions of the manager are not directly reported. Long/short hedge funds and active mutual funds are typical of this subset of managers: they regularly eliminate certain long positions, add new stocks to the portfolio, and constantly shift industry concentrations. Equity hedge funds will typically hold concentrated positions in a small set of stocks while holding short positions or no position in large numbers of equities that are still in the institution’s consideration set. The set definition must be expansive enough to capture the full set over which such institutions optimize while still accounting for limited mandates such as sector-specific products. I therefore define consideration sets as follows:

**Definition 3.** *(Consideration Sets)* Dynamic institution $j$ ’s consideration set $\mathcal{H}_{j,t}$ is the union of (1) all assets held by $j$ in the past twelve quarters or current quarter (“recent holdings”) and (2) all stocks that share a NAICS code with two or more recent holdings.

dynamically changes weights over time in a manner inconsistent with market-weighting or equal weighting would be said to be an “active” manager with a rigid mandate.

21

---

# Page 23

This methodology’s premise is that if an institution has held two or more stocks within an industry, then it has conducted sufficient research on the industry to purchase several securities and has refrained from purchasing other securities in the same industry. On the other hand, if a mutual fund has invested in one stock within an industry with 100 companies, we assume that the other 99 companies were not researched and that the one stock was researched for idiosyncratic reasons. While the cutoff is arbitrary and future research might improve upon the manager consideration set definitions, this heuristic approach based on industry classification captures the learning process of a firm that studies contextual information and like-company comparisons within an industry when formulating idiosyncratic return beliefs about stocks. The ubiquity of sector-specific and industry-specific analysts among finance practitioners and the gains to specialization suggest that these assumptions are grounded in the informational organization of asset managers. In Section 7 I explore an enhancement to this approach by trimming the consideration set’s range of market cap and book value to match the corresponding ranges within the manager’s holdings. Results are robust to using alternative definitions of consideration sets, as shown in Appendix S. This completes the taxonomy of managers, which will be critical in both defining the censored data as well as constructing instruments.

## 4.4 Instrument Construction, Strength, and Exogeneity

The creation of a valid instrument for log price is important for conducting consistent estimation of the demand parameters, as price is directly impacted by the private beliefs of institutions (captured by $\epsilon_{i,t}(n)$ ), which can be arbitrarily correlated across institutions. I create an instrument that uses the exogenous variation in consideration sets as a price shifter unrelated to the beliefs of institutions; this instrument is inspired by Kojien and Yogo (2019), who consider the counterfactual market capitalization that would result from each institution holding equal-weighted or book-value-weighted portfolios across their currently and previously held stocks.

I construct a related but different instrument for log market equity using the consideration sets for all managers derived according to the methodology of the last subsection via the taxonomy of rigid and dynamic managers. We consider the total institutional dollar demand for each stock under scenarios where institutions just form $1/N$ portfolios within their consideration sets (this demand is $\hat{P}_t^{EQ}(n)$ ) as well as total institutional dollar demand for each stock if institutions formed book-weighted portfolios within their consideration sets ( $\hat{P}_t^{BE}(n)$ ). The log price instrument for stock $n$ is therefore

$$
z_n = \log\left(1 + \hat{P}_t^{EQ}(n) + \hat{P}_t^{BE}(n)\right),
$$

although we can alternatively use $z_n = \log\left(\hat{P}_t^{EQ}(n) + \hat{P}_t^{BE}(n)\right)$ and define $z_n = 0$ whenever a stock is absent from all institutions’ consideration sets. $^{18}$ Using both equal weighting and book value

$^{18}$ Adding one dollar to this specification is irrelevant except in the case where $\hat{P}_t^{EQ}(n)$ and $\hat{P}_t^{BE}(n)$ are both zero, which only occurs when a stock $n$ cannot be found in the consideration set of any dynamic or rigid institution; $\hat{P}_t^{EQ}(n)$ and $\hat{P}_t^{BE}(n)$ are generally $>> 10^6$ . The one dollar simply normalizes the instrument to zero when a stock cannot be found in consideration sets. Alternatively, we could avoid using the single dollar and define $z_n$ to be

22

---

# Page 24

weighting serves to strengthen the instrument by accounting for multiple exogenous determinants of price. A company with greater book equity and wider presence in the consideration sets of institutions should have a higher market capitalization, with variation in this instrument orthogonal to variation in private beliefs about returns.

In the following three remarks, I conclude this section by contrasting this instrument with previous instruments from the literature and discussing consideration set exogeneity and instrument strength.

*Remark 1. (Instrument Comparison)* This instrument differs in four substantive ways from the log market equity instrument of Kojien and Yogo (2019): (1) most critically, the instrument is based on consideration sets instead of “investment universes” comprised of current and recent holdings; (2) both equal and book-equity weighted proposed counterfactual allocation schemes of Kojien and Yogo (2019) are integrated into a single instrument; (3) I use the assets and consideration sets of all managers; and (4) the instrument does not differ across managers because dynamic consideration sets are determined by industry codes.

*Remark 2. (Primary Threat to Identification)* The main threat to identification comes from a data limitation: because the data is heavily censored and we must infer consideration sets, we will occasionally miss an industry group $r$ that a manager $i$ has considered. If $i$ chooses to either sell short or avoid ownership in the entire industry group, then we will not include $r$ in $i$ ’s consideration set. This will introduce a relationship between the instrument and private beliefs. I mitigate this risk by using an expansive definition of consideration sets: this threat will only be relevant if an institution has refrained from owning two or more stocks within an industry group over a multi-year period.

*Remark 3. (Instrument Strength)* In Appendix K I show that the null of weak instruments can be rejected in all quarters, employing the effective F-statistic of Olea and Pflueger (2013) to account for heteroskedasticity. $^{19}$ Additionally, the relationship between the instrument and log price strengthens over time as the AUM of rigid institutions grows. Appendix K contains details on the analysis of instrument strength as well as how this paper’s taxonomy of managers relates to the growth of passive investing.

## 5 Estimations and Simulations

I use the method and data approach of the last two sections to estimate demand parameters for dynamic institutions in each quarter from 1984Q4 to 2021Q4, excluding institutions with fewer

$\log \left( \hat{P}_{t}^{EQ}(n) + \hat{P}_{t}^{BE}(n) \right)$ when $\hat{P}_{t}^{EQ}(n) + \hat{P}_{t}^{BE}(n) > 1$ and zero otherwise. The addition of one dollar does not impact the empirical results of this paper versus taking the log directly and defining $z_{n}$ to be zero when the stock is absent from every consideration set; see Chen and Roth (2024) for a fuller discussion of the theoretical issues associated with taking the $\log(1 + x)$ transformation.

$^{19}$ As discussed in Appendix K, no developed theory of instrument strength in this paper’s econometric context exists, leading to the choice of this robust methodology for studying standard 2SLS.

23

---

# Page 25

Table 1: Institutional Demand Estimation Summary Statistics

<table>
  <thead>
    <tr>
      <th></th>
      <th>Num Inst</th>
      <th>Tot Inst AUM</th>
      <th>Rigid AUM</th>
      <th>Dynamic AUM</th>
      <th>AUM SCQR</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1984-1988</td>
      <td>793</td>
      <td> $525B</td>
      <td>$ 17B</td>
      <td> $508B</td>
      <td>$ 348B</td>
    </tr>
    <tr>
      <td>1989-1992</td>
      <td>958</td>
      <td> $867B</td>
      <td>$ 74B</td>
      <td> $793B</td>
      <td>$ 544B</td>
    </tr>
    <tr>
      <td>1993-1996</td>
      <td>1156</td>
      <td> $1666B</td>
      <td>$ 118B</td>
      <td> $1549B</td>
      <td>$ 1184B</td>
    </tr>
    <tr>
      <td>1997-2000</td>
      <td>1540</td>
      <td> $4363B</td>
      <td>$ 248B</td>
      <td> $4115B</td>
      <td>$ 3462B</td>
    </tr>
    <tr>
      <td>2001-2004</td>
      <td>1921</td>
      <td> $5227B</td>
      <td>$ 542B</td>
      <td> $4686B</td>
      <td>$ 3979B</td>
    </tr>
    <tr>
      <td>2005-2008</td>
      <td>2574</td>
      <td> $7774B</td>
      <td>$ 1650B</td>
      <td> $6124B</td>
      <td>$ 4874B</td>
    </tr>
    <tr>
      <td>2009-2012</td>
      <td>2915</td>
      <td> $7974B</td>
      <td>$ 1732B</td>
      <td> $6242B</td>
      <td>$ 5257B</td>
    </tr>
    <tr>
      <td>2013-2016</td>
      <td>3733</td>
      <td> $14000B</td>
      <td>$ 5111B</td>
      <td> $8888B</td>
      <td>$ 7401B</td>
    </tr>
    <tr>
      <td>2017-2020</td>
      <td>4752</td>
      <td> $20587B</td>
      <td>$ 8399B</td>
      <td> $12188B</td>
      <td>$ 10495B</td>
    </tr>
    <tr>
      <td>2021</td>
      <td>5970</td>
      <td> $31962B</td>
      <td>$ 14298B</td>
      <td> $17664B</td>
      <td>$ 14965B</td>
    </tr>
  </tbody>
</table>

Note: Table 1 contains summary statistics for the demand estimation, including number of institutions, total institutional AUM, the AUM of rigid institutions, the AUM of dynamic institutions, and the AUM of institutions for which the SCQR estimation converges. Each variable is averaged over all quarters within the designated four-year window or, in the case of 2021, one-year window.

than twenty-five positive holdings in a given quarterly filing period. The main empirical results in Section 6 require the SCQR method to be applied to 247,997 institution × date pairs.

## 5.1 Summary Statistics: Managers, Consideration Sets, and Assets under Management (AUM)

In Table 1 I summarize the average quarterly number of estimations by time period as well as the aggregate assets under management (AUM) of different categories of managers. Rigid managers, whose preferences are not estimated, comprise a progressively larger fraction of aggregate AUM, as shown in both Figure 13a of Appendix K and Table 1. Dynamic AUM also increases rapidly over time in correspondence with a well-documented trend toward lower direct household ownership and greater institutional ownership of the stock market.

The most important number in Table 1 is the AUM of dynamic institutions whose assets are successfully estimated by the SCQR-based methodology of Section 3 (“AUM SCQR”). Institutions with fewer than twenty-five positive holdings are not estimated due to insufficient data, but even institutions with many positive holdings can be infeasible to estimate depending on the severity of the data censoring problem, which I take to be the ratio of positive holdings to the size of the consideration set. When the set of assets whose observable characteristics contribute positively to return expectations is almost empty, estimation will fail because we lack sufficient information about $\beta$ from the observations. $^{20}$

This limitation of all consistent estimation approaches for censored institutional demand does

$^{20}$ When the measure of the set $\{j : x_j'\beta > 0\}$ is zero, the rank condition of SCQR or CLAD is violated, leading to inconsistency or non-convergence.

24

---

# Page 26

Table 2: Institutional Demand Estimation Consideration Sets and Holdings

<table>
  <thead>
    <tr>
      <th></th>
      <th>Avg Pos Hold</th>
      <th>Med Pos Hold</th>
      <th>Med C.S. Size</th>
      <th>5th Prctl C.S. Size</th>
      <th>95th Prctl C.S. Size</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1984-1988</td>
      <td>119</td>
      <td>72</td>
      <td>1264</td>
      <td>372</td>
      <td>2885</td>
    </tr>
    <tr>
      <td>1989-1992</td>
      <td>138</td>
      <td>74</td>
      <td>1361</td>
      <td>416</td>
      <td>3148</td>
    </tr>
    <tr>
      <td>1993-1996</td>
      <td>157</td>
      <td>73</td>
      <td>1623</td>
      <td>550</td>
      <td>3865</td>
    </tr>
    <tr>
      <td>1997-2000</td>
      <td>176</td>
      <td>73</td>
      <td>1826</td>
      <td>676</td>
      <td>4409</td>
    </tr>
    <tr>
      <td>2001-2004</td>
      <td>187</td>
      <td>72</td>
      <td>1678</td>
      <td>639</td>
      <td>3645</td>
    </tr>
    <tr>
      <td>2005-2008</td>
      <td>190</td>
      <td>74</td>
      <td>1510</td>
      <td>589</td>
      <td>3258</td>
    </tr>
    <tr>
      <td>2009-2012</td>
      <td>189</td>
      <td>77</td>
      <td>1311</td>
      <td>520</td>
      <td>2876</td>
    </tr>
    <tr>
      <td>2013-2016</td>
      <td>203</td>
      <td>86</td>
      <td>1260</td>
      <td>498</td>
      <td>2647</td>
    </tr>
    <tr>
      <td>2017-2020</td>
      <td>209</td>
      <td>87</td>
      <td>1347</td>
      <td>590</td>
      <td>2582</td>
    </tr>
    <tr>
      <td>2021</td>
      <td>205</td>
      <td>90</td>
      <td>1438</td>
      <td>669</td>
      <td>2636</td>
    </tr>
  </tbody>
</table>

**Note**: Table 2 contains summary statistics on the consideration sets (CS) and holdings of institutional investors that have twenty-five or more positive holdings in their portfolio. The censoring issue is illustrated by the ratio of positive holdings to consideration set size, with an order of magnitude difference in median sizes. The right skewness of the distribution of portfolio sizes is apparent from the large gap between median and mean number of positions.

not impede this paper’s primary empirical objectives. First, as is visible in Table 1 by comparing the AUM of institutions with successful SCQR estimations (“AUM SCQR”) to the AUM of dynamic institutions in aggregate, between 69% and 86% of dynamic AUM have a corresponding demand parameter vector successfully estimated in each time period. Table 2 succinctly captures the underlying reason for non-convergence of the estimators in the remaining 14% to 31%: consideration sets are an order of magnitude larger than positive holdings on average, with a typical institution holding under 100 stocks with a consideration set approximately $15 - 20$ times larger. When the censoring problem is extreme, as with an institution holding only 50 long positions despite considering 3,000 stocks, we will generally find that unobservable characteristics are responsible for this pattern, barring an extraordinary clustering of those 50 positions among assets whose characteristics have extremal values. Yet our inability to obtain accurate parameter estimates for such institutions is then moot: the parameters are largely irrelevant to such an institution’s decision problem and the “road not taken” (the set of unpurchased stocks) is wide enough to be rendered meaningless.

## 5.2 Simulation: Recovering Demand Parameters

In Appendices H and I, I conduct two large-scale simulations using CRSP, Compustat, and consideration set data from 2021Q4. The objective of these simulations is to test this paper’s methodology by applying it to an artificially constructed set of institutions with randomly chosen beliefs about characteristics. I use the characteristics and randomly drawn beliefs to compute the corresponding institutional asset demands via numerical mean-variance optimization. After computing these portfolio weights, I censor any short holdings to zero. I simulate both short sale constrained and non-short sale constrained institutions, with this paper’s estimation routine

25

---

# Page 27

only provided with the asset characteristics, censored demands, and volatility parameters. I show that this paper’s methodology accurately recovers the demand parameters for most simulated institutions, while existing methodologies fail to do so. Figure 4 in Appendix H illustrates the power of this paper’s modeling approach, plotting recovered parameters versus simulated parameters, while Appendix I introduces beliefs with heteroskedasticity and contrasts the SCQR-based estimation results with those of other methodologies.

Figure 7 in Appendix I plots the estimated parameters using the exponential-linear model of Kojien and Yogo (2019), which does not recover the demand parameters. The remainder of Appendix I demonstrates that the issue with applying the method of Kojien and Yogo (2019) is not the misspecification of the functional form, nor the lack of a correction for heterogeneous idiosyncratic volatility, but rather the moment condition itself. Even when a linear model is applied with correct idiosyncratic volatility scaling, and even if we exclude the censored data and just estimate parameters from uncensored data, the estimators are inconsistent. Note that Kojien and Yogo (2019) make assumptions regarding non-holdings that are entirely different from those made here, so this contrast in parameter recovery is natural and derives from the different modeling assumptions. The two primary takeaways from the simulation results are that (a) SCQR works as intended to recover demand and belief parameters and (b) using a median zero restriction, not a mean zero restriction, is vital for consistent estimation when the assumptions of this paper hold. Moreover, I also show that the risk correction constant $\kappa$ that maps the demand parameter for the market risk factor $\tilde{\beta}_1$ to the belief parameter for market risk $\beta_1$ follows the equations derived in Section 2: for short sale constrained institutions, we can recover the belief parameter $\beta_1$ whereas $\beta_1$ is unrecoverable for non-short sale constrained institutions. $^{21}$

## 6 The Informational Value of Hidden and Overt Beliefs

In this section I study the information content of hidden and overt beliefs. Overt beliefs are straightforward: they are the regression residuals from the last section’s estimates and correspond to the idiosyncratic component of a stock owner’s return expectations that is not attributable to observable characteristics. Hidden beliefs correspond to the same stock-specific component of return expectations, but their determination is more subtle: each non-owner of a given stock has a threshold level of idiosyncratic (unobservable) return expectations above which they would have switched to being an owner. If our censored demand model says that institution $i$ ’s demand for a stock would switch to being positive when its idiosyncratic belief $u > -5\%$ , then we have an estimate of the hidden belief: it lies somewhere in the interval $(-\infty, -0.05]$ . In this section I aggregate these bounds across non-owners to form a “Hidden Beliefs Index.” Low values of this index indicate

$^{21}$ This paper’s theory section and simulations underscore why I do not study how the estimated constants $\tilde{\beta}_k$ change over time, as well as why I study neither elasticities nor cross-price elasticities; under this paper’s assumptions, the elasticities are unidentified due to the censoring problem, and the $\tilde{\beta}_k$ are non-structural objects that do not map directly to beliefs, information, or risk. The objects studied here are those that are either able to be point identified (overt beliefs) or set identified (hidden beliefs) after accounting for censoring.

26

---

# Page 28

that non-owners harbored negative beliefs about the stock; this suggests that non-owners possess adverse private information. High values of this index indicate that we have no evidence of such adverse private information, even though high index values do not preclude this possibility.

I find that the aggregation of hidden beliefs strongly predicts future returns whereas overt beliefs only weakly predict returns. This result is consistent with a bounded rationality mechanism: institutions fail to fully incorporate the informational content of institutions choosing not to own a stock, even while they account for the informational content of other institutions owning a stock.

## The Hidden Beliefs Index (HBI) and Overt Beliefs Index (OBI)

The HBI for a given stock $ n $ is the weighted average of each non-owner's threshold return expectation beyond which they would have become an owner instead. In this paper's model, we can use each institution's estimated demand parameters $ \tilde{\beta}_{i,t} $ and the characteristics for a stock $ z_n $ to compute this: since weights are positive when $ z_n' \tilde{\beta}_{i,t} + u_{i,t}(n) > 0 $ , non-ownership implies that $ u_{i,t}(n) \leq -z_n' \tilde{\beta}_{i,t} $ . In other words, we have set identification of the hidden belief.

The HBI for stock $ n $ in period $ t $ is therefore computed by taking the AUM-weighted average of the hidden belief bounds $ -z_n' \tilde{\beta}_{i,t} $ across all institutions $ i $ that have stock $ n $ in their consideration sets but did not hold the stock during the last three years, including the current period. $^{22}$ The HBI is a measure of hidden beliefs and information: it captures the weighted average of beliefs that would have pushed non-owners into becoming owners. When the non-owners of a stock include many institutions for which it is “surprising” that they do not hold the stock, this index value will be low. Recall the example from the introduction: if an institution $ i $ 's estimated demand parameters $ \tilde{\beta}_{i,t} $ imply that $ i $ will own the stock except when its idiosyncratic unobservable belief $ u_{i,t}(n) $ is very low, then this institution will contribute negatively to the HBI. On the other hand, if the non-owners largely contain the “usual suspects” such as growth investors who avoid ownership in a value stock, then we have less compelling evidence that the non-owners have negative stock-specific information.

The OBI aggregates overt beliefs, the idiosyncratic return expectations of stock owners. Recall that $ \sigma^2(n) w_{i,t}(n) $ is just our variable $ y_{i,t}(n) $ from the regression, so the overt belief captures the difference between the predicted level of the variance-scaled portfolio weight, $ z_n' \tilde{\beta}_{i,t} $ , and the actual level, $ \sigma^2(n) w_{i,t}(n) $ . The OBI for stock $ n $ in period $ t $ is thus computed by taking the AUM-weighted average of the residuals $ \hat{u}_{i,t} = \sigma^2(n) w_{i,t}(n) - z_n' \tilde{\beta}_{i,t} $ across all institutions $ i $ that currently hold a position in stock $ n $ .

## Hidden Beliefs and Return Predictability

I compute the HBI for every time period and stock included in the estimations of Section 5 and analyze how the HBI predicts returns via portfolio sorts. Because of how the HBI is generated, these

[^1]: $^{22}$ Results are robust to including past holdings, but the results of Akepanidtaworn, Mascio, Imas and Schmidt (2023) suggest that even certain sophisticated institutions with a clear demonstration of skill in stock purchasing patterns sell stocks in a suboptimal and heuristic way. This indicates that hidden beliefs for previously owned stocks might fail to capture the intended belief.

---

# Page 29

Table 3: The HBI and Portfolio Returns: Size × HBI Sorts

<table>
  <thead>
    <tr>
      <th></th>
      <th>HBI Q1</th>
      <th>HBI Q2</th>
      <th>HBI Q3</th>
      <th>HBI Q4</th>
      <th>HBI Q5</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>-0.94% (-1.32)</td>
      <td>0.16% (0.23)</td>
      <td>1.53% (2.02)</td>
      <td>2.55% (3.45)</td>
      <td>3.75% (4.93)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>-0.6% (-0.53)</td>
      <td>-0.96% (-1)</td>
      <td>1.64% (1.93)</td>
      <td>2.94% (3.39)</td>
      <td>3.56% (3.71)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>-3.56% (-3.35)</td>
      <td>-1.49% (-1.64)</td>
      <td>1.23% (1.5)</td>
      <td>3.35% (3.93)</td>
      <td>3.26% (3.32)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>-4.19% (-4.17)</td>
      <td>-1.23% (-1.31)</td>
      <td>0.55% (0.6)</td>
      <td>1.99% (2.25)</td>
      <td>3.24% (3.01)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>-3.95% (-3.49)</td>
      <td>-2.54% (-2.45)</td>
      <td>-0.19% (-0.19)</td>
      <td>1.64% (1.54)</td>
      <td>4% (3.18)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>-4.85% (-3.53)</td>
      <td>-1.97% (-1.49)</td>
      <td>0.09% (0.07)</td>
      <td>2% (1.47)</td>
      <td>6.76% (4.44)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>-5.14% (-2.97)</td>
      <td>-1.76% (-1.05)</td>
      <td>2.23% (1.34)</td>
      <td>2.33% (1.31)</td>
      <td>7.65% (4.07)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>-3.21% (-1.49)</td>
      <td>-0.11% (-0.05)</td>
      <td>1.81% (0.83)</td>
      <td>5.06% (2.22)</td>
      <td>9.35% (3.85)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>0.93% (0.37)</td>
      <td>3.66% (1.46)</td>
      <td>6.01% (2.33)</td>
      <td>7.73% (2.54)</td>
      <td>13.87% (4.72)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>10.31% (3)</td>
      <td>12.93% (4.17)</td>
      <td>14.17% (4.45)</td>
      <td>16.8% (4.6)</td>
      <td>23.06% (5.82)</td>
    </tr>
  </tbody>
</table>

Note: Table 3 contains the results for portfolios formed via sorts on the Hidden Beliefs Index (HBI) from 1986 to 2021. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on the HBI, which is generated from bounds on hidden beliefs weighted by the AUM of each institution. Stocks are divided into HBI quintiles within each size decile, resulting in 50 equal-weighted portfolios. This process is repeated three times, using the HBI as of the last day of the previous quarter, the second prior quarter, and the third prior quarter, with the simple average of the returns of these three portfolios used as the size × HBI quintile return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

return prediction exercises test semi-strong market efficiency: is available information from public data fully and rationally incorporated into prices? I divide all stocks into size deciles at the end of every calendar quarter, discard all stocks that are missing an HBI value for the time period, and sort the remaining stocks within each size decile into five equal-weighted quintile portfolios based on the HBI from lowest (Q1) to highest (Q5). To avoid using data that was not contemporaneously available to the public, I take the returns for a given size × quintile combination to be the average returns of the three corresponding size × quintile portfolios formed at the end of the previous quarter, second prior quarter, and third prior quarter.$^{23}$ By way of illustration, portfolio holdings for January-March 2021 are determined by HBIs derived from 13F filing data from September 2020, June 2020, and March 2020. I regress the daily excess returns (daily returns for all long/short zero cost strategies) against the excess market return factor, the HML and SMB factors of Fama and French (1993), and the momentum (UMD) factor of Carhart (1997), then compute the residual abnormal returns.

The annualized results and corresponding t-statistics, computed with Newey-West standard errors, are given in Table 3, which shows the strong predictive power of the HBI. In virtually every size decile, alpha is monotonically increasing as we go from the low HBI quintile to the high HBI quintile, with an extreme difference between the first and fifth quintiles. Unlike with many other documented anomalies in the cross section of stocks, the strongest results are not confined to lower

$^{23}$Recall that although 13F filings contain data for the end of each calendar quarter, they are not required to be submitted until 45 days after quarter end.

28

---

# Page 30

Table 4: HBI Long Short Strategy Results by Size Decile

<table>
  <thead>
    <tr>
      <th></th>
      <th>Annualized Alpha</th>
      <th>MKT</th>
      <th>SMB</th>
      <th>HML</th>
      <th>UMD</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>4.69% (4.57)</td>
      <td>-0.14 (-17.3)</td>
      <td>0.01 (0.63)</td>
      <td>0.22 (9.31)</td>
      <td>0.08 (4.67)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>4.16% (3.5)</td>
      <td>-0.1 (-9.92)</td>
      <td>-0.02 (-1.47)</td>
      <td>0 (0.17)</td>
      <td>-0.05 (-3.15)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>6.82% (5.33)</td>
      <td>-0.09 (-11.48)</td>
      <td>-0.03 (-1.95)</td>
      <td>-0.12 (-6.38)</td>
      <td>-0.03 (-2.2)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>7.43% (5.49)</td>
      <td>-0.05 (-5.88)</td>
      <td>-0.03 (-2.31)</td>
      <td>-0.22 (-12.07)</td>
      <td>-0.04 (-2.67)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>7.94% (5.42)</td>
      <td>-0.04 (-5.1)</td>
      <td>-0.03 (-2.25)</td>
      <td>-0.23 (-13.11)</td>
      <td>-0.05 (-4.06)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>11.61% (7.06)</td>
      <td>-0.01 (-1.55)</td>
      <td>0.02 (1.06)</td>
      <td>-0.22 (-12.36)</td>
      <td>-0.05 (-3.88)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>12.8% (7.13)</td>
      <td>0 (-0.03)</td>
      <td>0.04 (2.7)</td>
      <td>-0.16 (-8.2)</td>
      <td>-0.03 (-2.11)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>12.57% (6.16)</td>
      <td>0.03 (2.13)</td>
      <td>0.08 (4.3)</td>
      <td>-0.14 (-5.53)</td>
      <td>-0.04 (-2.59)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>12.94% (5.64)</td>
      <td>0.03 (2.55)</td>
      <td>0.08 (4.07)</td>
      <td>-0.12 (-5.28)</td>
      <td>-0.02 (-1.36)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>12.75% (3.7)</td>
      <td>0 (-0.21)</td>
      <td>0.05 (1.74)</td>
      <td>-0.12 (-2.85)</td>
      <td>-0.01 (-0.34)</td>
    </tr>
  </tbody>
</table>

Note: Table 4 contains the results for a strategy that uses portfolios generated from the Hidden Beliefs Index (HBI) from 1986 to 2021. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on the HBI, which is generated from bounds on hidden beliefs weighted by the AUM of each institution. Stocks are divided into HBI quintiles within each size decile, with the strategy going long the top quintile and short the bottom quintile, with an equal-weighted portfolio within each size decile’s long and short legs. This process is repeated three times, using the HBI as of the last day of the second to last quarter, the third to last quarter, and the fourth to last quarter, with the simple average of the returns of these three portfolios used as the strategy return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

size deciles. Moreover, the HBI results are largely symmetric; the top HBI quintile has anomalously positive performance, while the bottom HBI quintile portfolios perform poorly.$^{24}$ In Appendix R I compute value-weighted results within each size decile and find the same patterns.

Table 4 gives the results of a simple long-short strategy that purchases each of the top HBI quintile portfolios and sells short each of the bottom HBI quintile portfolios, with daily returns computed as the simple average of the three long-short portfolios formed via data lagged by one quarter, two quarter, and three quarters. Four-factor alpha is statistically significant in every size decile, with the strategy achieving positive returns in almost every year for which we have results. Deciles seven and eight, which contain stocks conventionally deemed to be “mid-cap,” have annualized alphas of 7.43% and 6.82% respectively, making the fact that these phenomena are not arbitraged away difficult to explain by transaction costs.

The HBI-based return predictability is not only large in magnitude, but also highly persistent,

$^{24}$The results for the bottom two CRSP size deciles, D1 and D2, are reported for completeness despite the fact that (a) much of the literature dispenses with these stocks entirely and (b) all “composite” results in this paper similarly exclude them. Despite the fact that this paper uses CRSP delisting returns to account for delisting events, these returns are nonetheless subject to the “delisting bias” in CRSP documented by, among others, Shumway (1997). Many methods for handling this bias have been documented, most of which involve ad-hoc imputation of delisting returns based on delisting codes (e.g. a particular delisting code corresponds to a -30% or -40% return); this paper maintains the CRSP delisting returns when reporting bottom deciles. The high average returns for ultra-microcap stocks in the tables (D1 and D2) are attributable to a combination of equal weighing, poor pricing of such stocks by Fama and French (1993) factors, subset selection (e.g. stocks that have a defined HBI or OBI), and delisting bias, none of which impact the paper’s main results or robustness analyses.

29

---

# Page 31

Table 5: HBI Long Short Strategy Quarterly Results by time after Formation

<table>
  <thead>
    <tr>
      <th></th>
      <th>Annualized Alpha</th>
      <th>MKT</th>
      <th>SMB</th>
      <th>HML</th>
      <th>UMD</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Lag 0</td>
      <td>7.85% (5.77)</td>
      <td>-0.03 (-3.05)</td>
      <td>-0.04 (-2.17)</td>
      <td>-0.16 (-6.56)</td>
      <td>-0.09 (-6.36)</td>
    </tr>
    <tr>
      <td>Lag 1</td>
      <td>8.67% (6.92)</td>
      <td>-0.04 (-4.3)</td>
      <td>-0.01 (-0.58)</td>
      <td>-0.11 (-3.42)</td>
      <td>-0.1 (-4.09)</td>
    </tr>
    <tr>
      <td>Lag 2</td>
      <td>9.56% (8.01)</td>
      <td>-0.05 (-6.62)</td>
      <td>0.01 (0.46)</td>
      <td>-0.13 (-5.65)</td>
      <td>-0.01 (-0.88)</td>
    </tr>
    <tr>
      <td>Lag 3</td>
      <td>8.7% (7.15)</td>
      <td>-0.05 (-6.2)</td>
      <td>0.01 (0.53)</td>
      <td>-0.09 (-3.93)</td>
      <td>0.03 (1.54)</td>
    </tr>
    <tr>
      <td>Lag 4</td>
      <td>8.93% (7)</td>
      <td>-0.04 (-5.58)</td>
      <td>0 (0.21)</td>
      <td>-0.08 (-3.24)</td>
      <td>0.07 (4.79)</td>
    </tr>
    <tr>
      <td>Lag 5</td>
      <td>8% (5.79)</td>
      <td>-0.04 (-4.27)</td>
      <td>-0.05 (-2.3)</td>
      <td>-0.11 (-4.58)</td>
      <td>0.08 (4.47)</td>
    </tr>
    <tr>
      <td>Lag 6</td>
      <td>8.93% (7.19)</td>
      <td>-0.05 (-4.3)</td>
      <td>-0.04 (-1.77)</td>
      <td>-0.15 (-7.4)</td>
      <td>0.06 (3.14)</td>
    </tr>
    <tr>
      <td>Lag 7</td>
      <td>8.11% (7.11)</td>
      <td>-0.03 (-5.39)</td>
      <td>0 (-0.46)</td>
      <td>-0.14 (-8.5)</td>
      <td>0.06 (5.84)</td>
    </tr>
    <tr>
      <td>Lag 8</td>
      <td>7.89% (6.59)</td>
      <td>-0.04 (-4.14)</td>
      <td>-0.01 (-0.63)</td>
      <td>-0.14 (-6.35)</td>
      <td>0.07 (5.3)</td>
    </tr>
    <tr>
      <td>Lag 9</td>
      <td>8.37% (6.5)</td>
      <td>-0.03 (-3.84)</td>
      <td>-0.02 (-1.03)</td>
      <td>-0.14 (-5.14)</td>
      <td>0.08 (4.47)</td>
    </tr>
    <tr>
      <td>Lag 10</td>
      <td>6.76% (5.65)</td>
      <td>-0.03 (-3.38)</td>
      <td>-0.02 (-1.35)</td>
      <td>-0.13 (-5.24)</td>
      <td>0.08 (4.24)</td>
    </tr>
    <tr>
      <td>Lag 11</td>
      <td>7.07% (6.15)</td>
      <td>-0.03 (-3.96)</td>
      <td>0 (0.01)</td>
      <td>-0.14 (-7.57)</td>
      <td>0.07 (5.96)</td>
    </tr>
    <tr>
      <td>Lag 12</td>
      <td>5.62% (4.74)</td>
      <td>-0.02 (-3.11)</td>
      <td>-0.01 (-0.6)</td>
      <td>-0.15 (-6.99)</td>
      <td>0.08 (5.95)</td>
    </tr>
    <tr>
      <td>Lag 13</td>
      <td>5.73% (4.9)</td>
      <td>-0.02 (-2.7)</td>
      <td>-0.01 (-1.3)</td>
      <td>-0.14 (-7.54)</td>
      <td>0.07 (4.89)</td>
    </tr>
    <tr>
      <td>Lag 14</td>
      <td>4.82% (4.39)</td>
      <td>-0.01 (-1.94)</td>
      <td>-0.01 (-1.28)</td>
      <td>-0.13 (-7.27)</td>
      <td>0.05 (4.6)</td>
    </tr>
  </tbody>
</table>

**Note**: Table 5 contains the results for a strategy that uses portfolios generated from the Hidden Beliefs Index (HBI) using CRSP, Compustat, and Thomson Reuters 13F filing data from 1984Q4 through 2021Q4, with strategy results from December 1988 through December 2021. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on the HBI, which is generated from bounds on hidden beliefs weighted by the AUM of each institution. Stocks are divided into HBI quintiles within each size decile, with the strategy going long the top quintile portfolio and short the bottom quintile portfolio, with equal weightings within each constituent portfolio. Results are averaged across the eight largest size decile long portfolios and the eight largest size decile short portfolios. I calculate results separately for portfolios formed 0 quarters ago (using contemporaneous information from 13F filings that is not available to participants until 45 days later) through 14 quarters ago. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997), with a clear descending pattern but strong persistence.

with a clear time decay pattern but continued statistical significance for a multi-year period. Table 5 shows the returns to quarterly long/short portfolios formed at each of a series of lags ranging from 0 to 14 quarters. The Lag 0 portfolio uses contemporaneously unavailable information, namely it forms the long and short legs at the end of each quarter from an HBI calculated with institutional holdings from the same day as the formation day.$^{25}$ The Lag 1 through Lag 14 portfolios are a function of contemporaneously available information, with portfolios formed based on current size deciles and HBI data from 1 through 14 quarters ago. Although the first two years after HBI calculation have the strongest positive performance, returns remain statistically significant at all lags, with annualized alpha decaying from 8.67% for the Lag 1 portfolio to 4.82% for the Lag 14 portfolio.

$^{25}$13F filings are only required to be filed within 45 days after the end of a quarter.

30

---

# Page 32

Table 6: The OBI and Portfolio Returns: Size × OBI Sorts

<table>
  <thead>
    <tr>
      <th></th>
      <th>Annualized Alpha</th>
      <th>MKT</th>
      <th>SMB</th>
      <th>HML</th>
      <th>UMD</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>0.85% (0.71)</td>
      <td>0.13 (11.76)</td>
      <td>0.09 (6.22)</td>
      <td>-0.08 (-3.57)</td>
      <td>-0.05 (-3.13)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>-0.59% (-0.38)</td>
      <td>-0.05 (-4.37)</td>
      <td>0.01 (0.44)</td>
      <td>0.23 (8.16)</td>
      <td>0.04 (1.64)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>1.63% (1.06)</td>
      <td>-0.15 (-14.01)</td>
      <td>-0.14 (-8.74)</td>
      <td>0.23 (11.27)</td>
      <td>0.03 (1.52)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>2.59% (1.66)</td>
      <td>-0.18 (-21.95)</td>
      <td>-0.18 (-12.06)</td>
      <td>0.16 (10.28)</td>
      <td>-0.01 (-0.71)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>-0.23% (-0.14)</td>
      <td>-0.17 (-13.92)</td>
      <td>-0.17 (-10.21)</td>
      <td>0.14 (7.59)</td>
      <td>-0.04 (-2.48)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>0.48% (0.31)</td>
      <td>-0.18 (-15.68)</td>
      <td>-0.2 (-10.36)</td>
      <td>0.05 (2.91)</td>
      <td>-0.05 (-3.77)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>1.93% (1.04)</td>
      <td>-0.19 (-7.98)</td>
      <td>-0.21 (-11.58)</td>
      <td>0.03 (1.01)</td>
      <td>-0.02 (-1.17)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>3% (1.53)</td>
      <td>-0.14 (-14.62)</td>
      <td>-0.22 (-10.34)</td>
      <td>-0.06 (-3.02)</td>
      <td>0 (-0.07)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>0.26% (0.11)</td>
      <td>-0.14 (-7.36)</td>
      <td>-0.19 (-7.94)</td>
      <td>-0.07 (-2.82)</td>
      <td>-0.01 (-0.44)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>3.75% (0.95)</td>
      <td>-0.03 (-1.01)</td>
      <td>-0.15 (-4.4)</td>
      <td>-0.03 (-0.56)</td>
      <td>0.02 (0.69)</td>
    </tr>
  </tbody>
</table>

**Note**: Table 6 contains the results for portfolios formed via sorts on the Overt Beliefs Index (OBI) from 1986 to 2021. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on the OBI. Stocks are divided into OBI quintiles within each size decile, with the strategy holding long an equal-weighted portfolio of the top OBI quintile within each size decile and selling short an equal-weighted bottom quintile portfolio. This process is repeated three times, using the OBI as of the last day of the second to last quarter, the third to last quarter, and the fourth to last quarter, with the simple average of the returns of these three portfolios used as the size × OBI quintile return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

## 6.3 Overt Beliefs and (the Lack of) Return Predictability

I compute returns for size × OBI portfolios in the same manner as for size × HBI portfolios, excluding stocks with a missing OBI instead of HBI, then analyze the abnormal returns. The four-factor alphas from forming size decile long-short portfolios in the same way as the HBI portfolios are given in Table 6. Unlike the HBI, the OBI has limited predictive power, with high and low index values yielding approximately equal performance.

This asymmetry between the OBI’s ability and the HBI’s ability to predict returns shows that overt and hidden beliefs are not equivalently impounded in prices. Recall that overt beliefs are just the regression residual $\hat{u}_{i,t} = \sigma^2(n) w_{i,t}(n) - z_n' \tilde{\beta}_{i,t}$ , the difference between the idiosyncratic variance-scaled portfolio weight $\sigma^2(n) w_{i,t}(n)$ and the estimated variance-scaled demand $z_n' \tilde{\beta}_{i,t}$ based on $i$ ’s demand parameters $\tilde{\beta}_{i,t}$ and stock $n$ ’s characteristics $z_n$ . The main driver of this residual is the first component, $\sigma^2(n) w_{i,t}(n)$ , which is easily computed by market participants. The proliferation of websites and news articles focused on the large holdings of various institutional investors suggests that at least the first component of the residual is in the information set of most sophisticated market observers. In Section 8 I show that overt beliefs modestly predict returns when we use disaggregated mutual fund data, but the asymmetry with hidden beliefs remains.

31

---

# Page 33

# A Conceptual Framework for Bounded Rationality and Hidden Beliefs

We have now seen that the HBI strongly predicts returns, whereas the OBI only weakly predicts returns. In this subsection I propose a bounded rationality mechanism for this pattern that differs both from standard behavioral disagreement models such as Miller (1977) as well as from models with rational expectations. I start by proposing a straightforward model of inference without disagreement that illustrates how we can obtain predictive hidden beliefs and uninformative overt beliefs. I then compare three conceptual frameworks that we might consider to explain the results and argue that only bounded rationality is consistent with this paper’s empirical results. Finally, I provide results for a two-agent equilibrium model that shows how a disagreement model with short sale constraints and standard Bayesian inference yields counterfactual predictions about the HBI’s predictive power, whereas replacing Bayesian inference with boundedly rational inference yields patterns consistent with this paper’s main empirical results. The primary finding is that the paper’s empirical evidence is most consistent with bounded rationality: even sophisticated agents in financial markets facing high-stakes allocation decisions struggle to infer from other agents’ non-holdings, even while they are able to extract much of the informational content of holdings.

## 7.1 A Model of Boundedly Rational Inference from Censored Data

Before moving to the 13F filing setting, I provide an illustrative model for this paper’s core mechanism. Consider an environment with a continuum of identical risk neutral agents who are presented with $N$ different investment opportunities, with each asset $n$ having unknown payoff $F_n$ , quantity $Q > 0$ , and equilibrium price $P_n$ . At time 0 they first receive information about the opportunities and then invest; at time 1 they receive the payoffs. The payoff for asset $n$ is given by $F_n = \sum_{k=1}^K \epsilon_k^n + \sum_{k=1}^K \eta_k^n$ where $\epsilon_k^n \sim U[-1, 0]$ is a uniformly distributed negative payoff component with $K$ total components, while $\eta_k^n \sim U[0, 1]$ are the positive payoff components. In this model, the positive components $\eta_k^n$ are comparable to the inferable overt beliefs of investors and are directly observed by all agents. For the negative components $\epsilon_k^n$ , however, the only information available is an upper bound $O_k^n \sim U[\epsilon_k^n, 0]$ ; these are analogous to bounds on hidden beliefs. Suppose that the agents possess cognitive uncertainty in the sense of Enke and Graeber (2023); in particular, agents display “Bayesian cognitive noise” wherein the Bayesian evaluation of the expected payoff is distorted toward a default value. $^{26}$

The standard solution requires agents to invoke Bayes’ theorem to compute the conditional distribution of $\epsilon_k^n | O_k^n$ and find the expected value, which is given by

$$
\mathbb{E}[\epsilon_k^n | O_k^n] = \frac{1 + O_k^n}{\log(-O_k^n)}.
$$

$^{26}$ Enke and Graeber (2023) consider distortions of actions and do not take a stance on the origin of the noise; in this setting, however, it is simpler to discuss noisy perception of the expected payoffs.

---

# Page 34

With cognitive noise, the perceived expected unit profit $ R_n = F_n - P_n $ conditional on the signal set $ \mathcal{I} $ is

$$
\mathbb{E}^{CN}[R_n|\mathcal{I}] = \underbrace{\lambda}_{\text{Signal Weight}} \sum_{k=1}^K \underbrace{\left( \frac{1 + O_k^n}{\log(-O_k^n)} \right)}_{\mathbb{E}[\epsilon_k^n|O_k^n]} + \underbrace{(1-\lambda)}_{\text{Default Weight}} \underbrace{\left( -\frac{K}{2} \right)}_{\text{Default}} + \underbrace{\left( \sum_{k=1}^K \eta_k^n - P_n \right)}_{\text{Known with Certainty}}.
$$

Examining the breakpoints where $ \mathbb{E}[\epsilon_k^n|O_k^n] $ equals the default value, we have the following proposition.

**Proposition 1.** Consider the case of one signal, $ K = 1 $ . When $ -0.2032 < O_1^n \leq 0 $ , $ \mathbb{E}^{CN}[R_n] < \mathbb{E}[R_n] $ and the asset is underpriced. When $ -1 \leq O_1^n < -0.2032 $ , $ \mathbb{E}^{CN}[R_n] > \mathbb{E}[R_n] $ and the asset is overpriced. For $ K > 1 $ , when $ \{O_k^n\}_{k=1}^K $ satisfies $ \frac{1}{K} \sum_{k=1}^K \left( \frac{1+O_k^n}{\log(-O_k^n)} \right) > -\frac{1}{2} $ , risky asset $ n $ will be underpriced, while it will be overpriced when the inequality is reversed.

Because the median value of the signal is $ \approx -0.1867 $ , marginally more assets will be underpriced than overpriced, while assets with signals close to the median signal value will be valued approximately the same as in the fully rational case. Note that this model's minimal environment does not include a disagreement mechanism; only cognitive noise in perception of negative signals is necessary to generate a predictive HBI.

## A Comparison of Three Frameworks: Quasi-Rational, Disagreement, and Bounded Rationality

**Environment: Institutions, Information, and Beliefs** Consider an environment where each period, investment institutions receive private information about the average future returns of stocks over a many-period horizon, and assume that this information's precision varies linearly with assets under management. This persistent private information is valuable but can be partially exposed through trading because every period, every market participant receives a full accounting of last period's portfolio holdings for every agent, just as with quarterly 13F filings. Agents are mean-variance optimizers and behave like the agents previously described in Section 2: they form beliefs that are linear in observable asset characteristics and use a simple backward-looking factor model to estimate the covariance matrix. Let us now consider three different frameworks and review their implications for hidden beliefs and overt beliefs.

**Quasi-Rational Framework** In a quasi-rational framework, we will find that neither the HBI nor OBI predicts returns. The primary principle of a rational framework is that agents incorporate all available information, updating their beliefs like a Bayesian. Each institution will update its signals using three sources of information: (1) any new private information; (2) other institutions' overt beliefs from last period, recovered from public filings; and (3) other institutions' censored hidden beliefs for all institutions that did not own the stock but could have. While

---

# Page 35

this belief updating process might appear to resemble the information acquisition literature (see e.g. Van Nieuwerburgh and Veldkamp (2010) and Kacperczyk, Van Nieuwerburgh and Veldkamp (2016)), it is analytically intractable even with normally distributed signals, as agents combine their own signals with the censored signals of all other agents.$^{27}$

In this framework overt beliefs and bounds on hidden beliefs are just different forms of information that are fully incorporated into every other agent’s beliefs. While the most recent period’s hidden and overt beliefs might be valuable in the current quarter because they are only revealed with a lag, all past quarters’ hidden beliefs will already be accounted for in prices. Given the HBI results and the lack of a plausible risk-based explanation, these predictions are counterfactual.

**Traditional Disagreement Framework** In a disagreement framework such as Miller (1977), short sale constraints will cause stocks with high levels of disagreement to become overpriced. Among those with extreme views, only the extreme optimists can act on their beliefs. Overpricing will increase monotonically as we increase the variance of beliefs, holding all else constant.

The disagreement framework has strong implications for return predictability. One implication explored by Chen, Hong and Stein (2002) is that stocks with low breadth of institutional ownership will underperform because limited ownership implies more pessimists with beliefs suppressed by short sale constraints. If the Miller (1977) framework explains the HBI, then high disagreement stocks will have more negative hidden beliefs and mispricing will concentrate in these “low hidden belief” stocks, with the HBI and $Breadth$ measure of Chen, Hong and Stein (2002) sorting stocks into similar groups. A second implication is that if we introduce non-short sale constrained agents who possess the same belief distribution as the short sale constrained investors, then the low HBI stocks will have much larger short interest than other stocks. The framework of Miller (1977) therefore makes three predictions if the HBI results are a reflection of the disagreement mechanism: (1) stocks with very low HBI values will underperform the market, while above-average HBI stocks will not have significant abnormal returns; (2) alpha from sorting on $Breadth$ will be strongly correlated with alpha from sorting on the HBI; and (3) stocks with a low HBI value will have high short interest, while stocks with a high HBI value will have low short interest. We have already seen that the Miller (1977) model’s exclusive prediction of overvaluation is inconsistent with the HBI results. As we will soon see, the latter two predictions also do not hold in the data.

**Bounded Rationality Framework with Inference Error** In this paper’s bounded rationality framework, institutions treat positive positions approximately correctly.$^{28}$ When analyzing the non-holdings of other institutions, however, the boundedly rational agents make what I will call an

---

$^{27}$If information is normally distributed, this combination involves (a) a Gaussian distribution and (b) a series of rectified Gaussians with an accumulation of mass at zero. Rational agents must therefore combine a signal with a standard distribution with a large number of censored signals in forming their posteriors, with the censoring point varying for every institution. Computing such posteriors is non-trivial and requires numerical techniques.

$^{28}$To the extent that institutions fail to fully separate other agents’ beliefs about observables (e.g. how market risk factors into their portfolio) from stock-specific idiosyncratic beliefs, properly computed overt beliefs can modestly predict future returns.

34

---

# Page 36

“inference error”: instead of fully adjusting their posterior belief about idiosyncratic returns, they shade it toward the unconditional expected belief of a non-holding institution. This mechanism could be viewed as a variant of the “cognitive uncertainty” studied by Enke and Graeber (2023): complexity and uncertainty about inference lead to investors possessing posterior idiosyncratic return expectations that are a convex combination of the Bayesian posterior and a default value.

Under this framework, the HBI will be strongly predictive; through its AUM-based weighting scheme, the HBI weights each institution by a proxy for the precision of its private information and captures the differing informational value of each institution not holding an asset. If a large institution has an extreme positive belief about profitability but fails to invest in a company with high levels of profitability, then this a far more negative signal than the observation that a different institution fails to invest but dislikes companies with high profitability. With inference errors, these two zero positions are treated insufficiently differently by agents, resulting in return predictability. Bounded rationality generates several predictions: (1) stocks with low HBI values will have negative abnormal returns while stocks with high HBI values will have high abnormal returns, with a monotonically increasing pattern as we progress from low to high; (2) the HBI will be predictive when computed using a censored quantile regression but not when using an improper moment condition that fails to properly identify hidden beliefs; and (3) enhancing the consideration set definition will lead to a more predictive HBI. We have already seen the clear monotonic pattern from (1) and will soon see that (2) and (3) also hold true. We now proceed to further test the disagreement and bounded rationality predictions.

## 7.3 Testing Disagreement as an Explanation for the HBI

I test the relationship between the HBI and the $Breadth$ measure of Chen, Hong and Stein (2002). Stocks with larger numbers of institutional holders (greater $Breadth$ ) experience superior risk-adjusted returns versus institutions that have limited or declining institutional ownership. $^{29}$ Because this paper’s analysis excludes rigid institutions (who are not subject to disagreement mechanisms, as they do not possess beliefs), a $Breadth$ measure formed exclusively from the subgroup of dynamic institutional 13F filers presents a new opportunity to both test the conclusions of Chen, Hong and Stein (2002) and contrast their approach with that of this paper’s.

Despite using all 13F dynamic institutions instead of just mutual funds, using $Breadth$ instead of $\Delta Breadth$ , and using a different data set that includes 1986-2021 instead of 1979-1998, I confirm the main premise of Chen, Hong and Stein (2002): firms with greater breadth outperform those with limited breadth. I repeat again the analysis of the previous sections, dividing stocks into size deciles every quarter and forming equal-weighted quintile portfolios based on the sorting variable, with the strategy holding long the three most recent highest quintile portfolios and selling short the three most recent lowest quintile portfolios. Such a strategy formed on $Breadth$ has an annualized

$^{29}$ Although Chen, Hong and Stein (2002) use changes in $Breadth$ ( $\Delta Breadth$ ) instead of levels, the closest proxy to their model of disagreement under short sale constraints is $Breadth$ , with controlling for market cap an important factor in separating mechanical contributions to $Breadth$ such as index inclusion from disagreement-based contributions.

35

---

# Page 37

four-factor alpha of 4.11% (t-statistic of 3.47 with Newey-West standard errors); see Appendix L for detailed tables.

Contrary to the disagreement model’s prediction, however, the daily abnormal returns from $Breadth$ are uncorrelated to those generated by the HBI-based strategy. Moreover, short interest is lower in bottom quintile HBI stocks versus top quintile HBI stocks, the opposite direction from what one would expect if the HBI were a vehicle for detecting latent short interest as a disagreement proxy. We therefore see that while the disagreement mechanism of Miller (1977) provides important intuition for asset pricing and is apparent in this section’s analysis of $Breadth$ , the evidence is inconsistent with the HBI and OBI results being driven by a disagreement channel.

## 7.4 Testing Bounded Rationality: an OLS Placebo Test

At the core of this section’s bounded rationality framework is the “inference error” that agents make when trying to incorporate institutions’ zero holdings into their beliefs. They form a posterior idiosyncratic return expectation that is a convex combination of (1) the Bayesian posterior from conditioning on the institution’s demand for observable characteristics and (2) a default value. Correctly measuring the degree of shrinkage toward the default value is therefore entirely dependent on correctly estimating institutional beliefs. This estimation depends on taking into account both holdings and non-holdings. If the HBI’s ability to predict returns is driven by some other phenomenon, however, we might expect more ad hoc estimations of demand to establish the same relationship.

To test the relevance of this paper’s SCQR-based methodology, I run a placebo test and repeat all institutional demand estimations but using OLS. As in this paper’s main estimation procedure, the dependent variable is portfolio weights scaled by idiosyncratic variance. The only difference is therefore the identifying assumption: OLS uses a mean zero restriction instead of a median zero restriction. Ignoring censoring entirely in conducting the OLS-based analysis will result in transparently useless results, as the consideration sets are an order of magnitude larger than the holdings. To give OLS the opportunity to achieve more reasonable estimates, I conduct estimation exclusively on the sets of assets with positive weights; this ad hoc correction is occasionally seen in the literature when the censoring problem is not treated carefully. Furthermore, I eliminate outlier estimates to avoid the OLS-HBI results being skewed by extreme OLS estimates based on very small sample sizes. $^{30}$

The results, contained in Table 11 of Appendix J, show that an HBI formed from OLS estimates yields no return predictability, with every size decile of the long-short strategy seeing statistically insignificant abnormal returns and multiple deciles delivering negative abnormal returns. While the HBI and OBI results are robust to independent variable selection, misestimation of idiosyncratic volatility, and consideration set definitions, they can only be obtained through careful econometric treatment of the censoring problem. Our ability to predict returns therefore

$^{30}$ Outliers are any institution $\times$ quarter pair where $\|\tilde{\beta}_{i,t}\|_1 > 5 \times 10^{-4}$ .

36

---

# Page 38

hinges on conducting econometrically sound demand estimation, which is consistent with this section’s bounded rationality mechanism.

## 7.5 Testing Bounded Rationality: Sharper Consideration Sets

Recall the main prediction of the bounded rationality framework: the degree of inference error is a function of how much an institution would like a stock based solely on its observables. The gap between Bayesian and boundedly rational inference is therefore dependent on defining which stocks the institution could have held but did not. If we improve the definition of consideration sets, the sets from which institutions select their portfolios, then we should expect the HBI’s ability to predict returns to strengthen, which is precisely what I show here.

Consideration sets are often based on industries (e.g. sector-specific products, sector exclusions, an industry-based research process or analyst hiring process) as well as size (large, middle, small-cap) and valuation (“value,” “growth,” or “blend”). We are faced with the challenge of defining a universal consideration set construction algorithm that favorably treats all types of firms, from small cap growth funds to quantitative hedge funds.

I repeat the paper’s entire main analysis by creating “style boxes” in the spirit of the $3 \times 3$ grids frequently used by Morningstar to situate mutual fund mandates in the space of size (large, mid, small) and type (value, blend, growth). For each manager, I take the enlarged range of smallest log market cap times 0.95 to largest log market cap times 1.05, specifically, $[0.95 \times \log(P_{min}), 1.05 \times \log(P_{max})]$ , and exclude from the consideration set all stocks outside this range. I repeat the same process with $\log(\text{Book Equity})$ . $^{31}$ The newly formed consideration sets are therefore the intersection of the main NAICS-based approach with “style boxes” constructed in this manner.

In Table 7 I provide the results of the same long-short HBI-based strategy as subsection 6.2, but with consideration sets redefined using this subsection’s combined “style box” approach. The composite strategy comprised of an equal-weighted portfolio of all size deciles, excluding the bottom two microcap deciles for which return data is less reliable, yields annualized four-factor alpha of 9.93% (11.74). The OBI, meanwhile, remains uninformative about future prices, with statistically insignificant four-factor alpha of 1.28% (1.44). The gain in return predictability from improving the definition of consideration sets underscores two points: (a) the precision of measuring the gap between Bayesian and boundedly rational inference is dependent on the precision of the consideration sets and (b) future research into institutional consideration sets is of first order importance for asset pricing and demand estimation.

---

$^{31}$ Results are nearly identical if we use size and book to market ratio and create bands accordingly, expanding the range of permissible log valuation ratios by 5% symmetrically, 2.5% on each end, and leaving the market cap band unchanged. Most funds have positions with a wide range of book values and $BE/ME$ ratios because whereas market cap is a transparent “style” limitation of many funds, definitions of “value” vary from manager to manager and even across the equity universe for a given manager.

37

---

# Page 39

Table 7: HBI Long Short Strategy Results by Size Decile, “Style Box” Version

<table>
  <thead>
    <tr>
      <th></th>
      <th>Annualized Alpha</th>
      <th>MKT</th>
      <th>SMB</th>
      <th>HML</th>
      <th>UMD</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>4.77% (5.05)</td>
      <td>-0.13 (-23.75)</td>
      <td>0 (-0.19)</td>
      <td>0.2 (14.92)</td>
      <td>0.07 (7.18)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>4.66% (4.1)</td>
      <td>-0.11 (-10.6)</td>
      <td>-0.05 (-3.86)</td>
      <td>0.01 (0.38)</td>
      <td>0 (-0.24)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>7.7% (6.27)</td>
      <td>-0.13 (-15.19)</td>
      <td>-0.07 (-5.84)</td>
      <td>-0.1 (-5.55)</td>
      <td>0.02 (1.42)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>9.28% (6.86)</td>
      <td>-0.09 (-10.37)</td>
      <td>-0.1 (-7.16)</td>
      <td>-0.19 (-8.85)</td>
      <td>0.01 (0.96)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>9.2% (6.65)</td>
      <td>-0.1 (-9.9)</td>
      <td>-0.12 (-8.21)</td>
      <td>-0.18 (-8.48)</td>
      <td>0 (0.25)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>13.49% (8.22)</td>
      <td>-0.09 (-8.72)</td>
      <td>-0.09 (-5.21)</td>
      <td>-0.16 (-7.44)</td>
      <td>-0.04 (-2.59)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>14.83% (8.36)</td>
      <td>-0.05 (-5.9)</td>
      <td>-0.04 (-2.35)</td>
      <td>-0.06 (-3.28)</td>
      <td>-0.01 (-0.52)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>15.48% (7.5)</td>
      <td>-0.03 (-2.31)</td>
      <td>-0.02 (-1.2)</td>
      <td>-0.06 (-2.54)</td>
      <td>-0.04 (-2.39)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>12.89% (5.61)</td>
      <td>-0.04 (-2.68)</td>
      <td>-0.06 (-2.95)</td>
      <td>-0.03 (-1.68)</td>
      <td>-0.04 (-2.82)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>8.12% (2.66)</td>
      <td>-0.02 (-0.77)</td>
      <td>-0.04 (-1.35)</td>
      <td>0.03 (0.95)</td>
      <td>-0.06 (-2.44)</td>
    </tr>
  </tbody>
</table>

Note: Table 7 contains the results for a strategy that uses portfolios generated from the Hidden Beliefs Index (HBI) from 1986 to 2021, with the HBI derived from estimates formed via this section’s “style box” approach to consideration set construction. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on the HBI, which is generated from bounds on hidden beliefs weighted by the AUM of each institution. Stocks are divided into HBI quintiles within each size decile, with the strategy going long the top quintile and short the bottom quintile, with an equal-weighted portfolio within each size decile’s long and short legs. This process is repeated three times, using the HBI as of the last day of the second to last quarter, the third to last quarter, and the fourth to last quarter, with the simple average of the returns of these three portfolios used as the strategy return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

## 7.6 A Two-Agent Model of Disagreement and Bounded Rationality

In Appendix U I create a model that studies the interaction of the disagreement and bounded rationality mechanisms previously described. The environment features many risky assets and one riskless asset, three periods, and two informed agents. Payoffs are dependent on common risk factors as well as idiosyncratic risk factors specific to each asset. Short sale-constrained agents receive private signals about both common risk factors and idiosyncratic risk factors at time 0. Demands from time 0 are then revealed at time 1, with payoffs received at time 2. Each common and idiosyncratic risk factor has discrete outcomes, a “Good State” and a “Bad State.”

Each agent makes inferences about the payoffs from private signals as well as demand-based inference about the other agent’s signals from the revealed holdings. Each asset’s supply is stochastic and uncorrelated at times 0 and 1, and agents take prices as given; moreover, agents do not infer from price. All agents form demands based on mean-variance optimization with a fixed covariance matrix but with expected payoffs computed from proper Bayesian posteriors.

I explore how the institutions’ belief formation process impacts equilibrium prices and excess returns. The fundamental logic, detailed in Proposition 2, is that in this model the “winner’s curse” is active: the agent with higher beliefs about payoffs will hold the asset at time 1 whereas the pessimistic agent will not. At time 1, both agents will fully recover the other agent’s signals regarding common risk factors but only recover a subset of beliefs about idiosyncratic shocks. This

38

---

# Page 40

leads to both agents having identical posteriors about common factors but differing posteriors for idiosyncratic shocks: the winner’s curse is solely determined by beliefs about idiosyncratic stock risk. When agents use standard Bayesian updating of beliefs about idiosyncratic payoffs, stocks with low HBI values have symmetrically informed agents and no winner’s curse, while stocks with high HBI values still feature a winner’s curse. Low HBI stocks therefore counterfactually outperform high HBI stocks under standard Bayesian inference. If agents fail to make inferences regarding hidden beliefs, then the winner’s curse for stocks with high bounds on hidden beliefs diminishes while the winner’s curse becomes active in stocks with low bounds on hidden beliefs. Under bounded rationality, the HBI will positively predict returns, whereas under a pure disagreement framework with full inference, the HBI will negatively predict returns, as given in the following proposition.

**Proposition 2.** *With investor disagreement, short sale constraints, and non-inference from price, the overvaluation mechanism of Miller (1977) becomes active in high HBI stocks and the HBI negatively predicts excess factor-adjusted returns. If agents make an inference error, however, and only incorporate overt beliefs but not hidden beliefs into their posteriors, then the “winner’s curse” for high hidden beliefs index stocks diminishes and shifts to stocks with low hidden beliefs. Under parameter restrictions that allow for hidden beliefs to be positive with sufficiently high probability, the factor-adjusted excess returns of stocks with high bounds on hidden beliefs exceed the factor-adjusted excess returns of stocks with low bounds on hidden beliefs when agents fail to properly infer hidden beliefs.*

## 8 Additional Empirical Results

In this section I study the HBI’s connection (or lack thereof) to various sorting variables from the literature and explore how the HBI and OBI’s ability to predict returns varies across institution types and institution sizes. I also apply the paper’s methodology to disaggregated mutual fund data and find similar results to the main analysis. Finally, I establish a relationship between institutions’ overt beliefs and the results of Antón, Cohen and Polk (2021), who show that the most abnormally concentrated positions of managers outperform other stocks.

### 8.1 The HBI, Idiosyncratic Volatility, Short Interest, and Institutional Ownership

We have seen that the HBI’s ability to predict returns is most consistent with bounded rationality as opposed to a traditional disagreement framework, but we must also exclude the possibility that this ability is driven by a simpler phenomenon: a connection between the HBI and the raw inputs to the estimation process. Given extensive evidence that highly shorted stocks perform poorly (see e.g. Jones and Lamont (2002), Asquith, Pathak and Ritter (2005), and Boehmer, Jones and Zhang (2008)) and stocks with high idiosyncratic volatility substantially underperform (Ang, Hodrick, Xing and Zhang (2006)), the HBI-based strategy’s implicit use of idiosyncratic volatility through

39

---

# Page 41

the estimation method and the extensive use of 13F data raises the question of whether the HBI is capturing some element of the idiosyncratic volatility or short interest anomalies previously documented in the literature. Additionally, to the extent that the HBI forecasts high institutional ownership, its predictive power might be related to simple sorts on institutional ownership. To test these hypotheses, in Appendices M, N, and O I create size × idiosyncratic volatility, size × short interest, and size × institutional ownership portfolios with the same methodology as the HBI: I divide each size decile into quintiles by each sorting variable. Unsurprisingly given the aforementioned literatures, stocks with high idiosyncratic volatility, high short interest, or low institutional ownership underperform their low idiosyncratic volatility, low short interest, and high institutional ownership peers, respectively. I compute the daily four-factor alphas for each of the three corresponding composite (equal weight each of the top eight size deciles) long/short strategies, finding annualized four-factor alphas of 8.48%, 5.03%, and 4.77%, respectively.

I regress the daily returns of the HBI-based composite strategy on the four factors of Carhart (1997) as well as the daily alphas from each of the idiosyncratic volatility, short interest, and institutional ownership strategies as well as the *Breadth*-based strategy. Annualized alpha actually increases to 8.95% from 8.50% once the additional variables are included because of statistically significant coefficients (t-statistics of −2.42 and -2.47) on the idiosyncratic volatility and short sale anomalies. The HBI results are made more puzzling for a traditional rational framework, not less, in light of several of the literature’s well-documented anomalies.

The HBI quintile portfolios display a clear pattern in institutional ownership despite the fact that strategies formed from ownership and the HBI have uncorrelated alphas. Stocks with a high HBI have substantially greater institutional ownership than stocks with low HBI values. Table 8 details the average institutional ownership across time for each of the size × HBI quintile portfolios, with a monotonically increasing relationship as we progress from the lowest quintile to the highest quintile. The pattern in Table 8 illustrates the power of both the estimation methodology and the HBI. Despite the fact that the HBI is derived solely from the SCQR-based estimates of institutions that chose *not to own a stock*, the HBI is strongly related to the extent to which institutions *own the stock*. Yet the HBI is a far more predictive sorting variable than institutional ownership, as already shown in the above analysis. If a stock possesses a high HBI, then few non-owning institutions (weighted by AUM) have adverse information about the stock. The stock owners therefore likely received limited negative idiosyncratic signals and will hold larger positions than if the signals were more mixed. When the HBI is low, the opposite holds. Inverting the pattern to study household ownership, which is to say the complement of institutional ownership, these patterns provide suggestive evidence that households are left holding a disproportionate fraction of common stocks about which institutional investors have gleaned adverse private information.

### 8.2 The HBI’s Informational Content and Institution Size

Given the HBI’s strong informational content, another natural question is whether its power derives from the beliefs of large or small institutions. Many Bayesian models of information acquisition

40

---

# Page 42

Table 8: The HBI and Institutional Ownership

<table>
  <thead>
    <tr>
      <th></th>
      <th>HBI Q1</th>
      <th>HBI Q2</th>
      <th>HBI Q3</th>
      <th>HBI Q4</th>
      <th>HBI Q5</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>35.43%</td>
      <td>43.34%</td>
      <td>53.57%</td>
      <td>62.31%</td>
      <td>70.61%</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>38.28%</td>
      <td>40.78%</td>
      <td>53.51%</td>
      <td>60.59%</td>
      <td>67.63%</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>36.4%</td>
      <td>40.92%</td>
      <td>49.91%</td>
      <td>57.04%</td>
      <td>64.19%</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>33.81%</td>
      <td>37.7%</td>
      <td>45.69%</td>
      <td>50.98%</td>
      <td>58.3%</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>29.46%</td>
      <td>33.18%</td>
      <td>39.37%</td>
      <td>43.8%</td>
      <td>51.19%</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>25.78%</td>
      <td>28.26%</td>
      <td>30.72%</td>
      <td>35.94%</td>
      <td>44.73%</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>20.2%</td>
      <td>22.07%</td>
      <td>23.03%</td>
      <td>26.41%</td>
      <td>35.8%</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>16.16%</td>
      <td>16.98%</td>
      <td>17.37%</td>
      <td>18.31%</td>
      <td>26.49%</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>10.17%</td>
      <td>10.97%</td>
      <td>10.61%</td>
      <td>10.47%</td>
      <td>16.38%</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>5.48%</td>
      <td>5.5%</td>
      <td>4.84%</td>
      <td>4.77%</td>
      <td>6.38%</td>
    </tr>
  </tbody>
</table>

**Note**: Table 8 gives the across-time average institutional ownership of each of the size × HBI portfolios. Ownership follows a nearly monotonic increasing pattern, with low HBI stocks possessing low institutional ownership and high HBI stocks possessing high institutional ownership.

have proposed i.i.d. draws of a noisy signal, which implicitly suggests that the aggregation of a large number of hidden beliefs or overt beliefs is necessary to distill an informative signal. By contrast, if we use a heterogeneous skill model where the precision of an institution’s information varies linearly with assets under management, then aggregating hidden beliefs only across highly skilled (large) institutions will still provide strong return predictability because their collective information precision will vastly outweigh that of smaller managers.

Figure 1 provides a heatmap that compares the relative performance of long/short HBI strategies formed from (a) all institutional hidden beliefs, (b) a subindex comprised of the top 10% of 13F institutions by AUM in each period, and (c) a subindex comprised of the bottom 90% of 13F institutions by AUM. Whereas the results for the large institutions are at least as strong as the “all-institution” HBI results, the return predictability of the small AUM HBI index is markedly weaker despite it possessing an order of magnitude more institutions than the large AUM group. When the HBI construction method is revised to use equal weighting of beliefs instead of AUM-weighting, the contrast is more severe. These findings are inconsistent with i.i.d. models of information acquisition but consistent with models of heterogeneous skill; the hidden beliefs of large institutions strongly predict future returns whereas the hidden beliefs of small institutions weakly (though still statistically significantly) predict future returns.

## 8.3 HBI and OBI-based Return Predictability by Institution Type

A natural question is whether the HBI derives its power from a specific institution type, and similarly whether the OBI can predict returns if only certain institutions are included. By creating HBI and OBI subindices that aggregate the hidden and overt beliefs of different institution types, we

41

---

# Page 43

![image](image_1.png)

Figure 1: HBI Predictive Power by Institutional AUM

**Note**: This heatmap details the t-statistics for the long/short HBI strategy across size deciles D1 to D10, with D10 the largest cap, for HBI subindices based on the hidden beliefs of all institutions, institutions in the top decile of dynamic institutions by AUM, and institutions with AUM less than the 90th percentile of all dynamic managers. I sort equities into size deciles each quarter, then sort into equal weight quintile portfolios based on a given HBI subindex within each size decile. The long/short strategy holds long the three most recent past top quintile portfolios and sells short the three most recent bottom quintile portfolios. Daily returns are computed for the time period 1986Q1-2017Q4 (for ready comparison with the heatmaps in the next subsection), with four-factor alpha and corresponding Newey-West standard errors computed. The derived t-statistics from this analysis are plotted in the heatmap.

can study the informational content of aggregate hidden and overt beliefs of different institutional investor populations. I use the 13F institution type code reclassification scheme of Kojien and Yogo (2019) from 1986-2017 and create HBI and OBI subindices that are restricted to banks, insurance companies, investment advisors, mutual funds, or pension funds (type codes 1, 2, 3, 4, and 5, respectively). I conduct the same analysis as subsections 6.2 and 6.3 for each subindex and aggregate the results into a heatmap that shows levels of statistical significance for each size decile $\times$ type code combination.

As seen in the heatmap in Figure 2, each HBI subindex displays meaningful return predictability, with the HBI subindex derived from banks the most informative across all deciles overall and the index derived from mutual funds most informative about the top decile of largest stocks, which is to say the bulk of equities by market cap. The daily performance of the five HBI subindex-derived strategies reveals that “investment advisor” and “mutual fund” sub-strategies have minimally correlated performance ( $R^2 = 5.94\%$ ) whereas “mutual fund” and “pension fund” sub-strategies have a high level of correlation ( $R^2 = 37.99\%$ ). $^{32}$

If we aggregate the sub-strategies instead of using the composite HBI-derived strategy, the informational power of hidden beliefs remains exceedingly strong, with a t-statistic of 11.57, an annualized four-factor alpha of 7.22% over 1986-2017, and an annualized Sharpe ratio of 2.17 for

$^{32}$ These are “composite” strategies from an equal weighting of the top eight size decile portfolios, which excludes microcap stocks from D1 and D2.

42

---

# Page 44

![image](image_1.png)

**Figure 2: HBI Predictive Power by Institution Type and Size Decile**

*Note:* This heatmap details the t-statistics for the long/short HBI strategy across size deciles D1 to D10, with D10 the largest cap, for HBI subindices based on the hidden beliefs of five different institution types: banks, insurance companies, investment advisors, mutual funds, and pension funds. I sort equities into size deciles each quarter, then sort into equal weight quintile portfolios based on a given HBI subindex within each size decile. The long/short strategy holds long the three most recent past top quintile portfolios and sells short the three most recent bottom quintile portfolios. Daily returns are computed for the time period 1986Q1-2017Q4, with four-factor alpha and corresponding Newey-West standard errors computed. The derived t-statistics from this analysis are plotted in the heatmap.

the factor-neutral portfolio; the composite HBI strategy over the same time period has a t-statistic of 9.94, annualized four-factor alpha of 9.02%, and an annualized Sharpe ratio of 1.93 for the factor-neutral portfolio. These results are consistent with all institutional investor types possessing informative hidden beliefs. Turning to the OBI, we yet again see a lack of predictive power across institution types, as illustrated by the heatmap in Figure 3. The overt beliefs derived from 13F filings of different investor types fail to predict returns in the cross section.

*Remark 4.* The contrast between the HBI and OBI when decomposed by institution type is not surprising because it parallels the contrast in the aggregate indices, but the predictive power of hidden beliefs across institution subtypes is somewhat surprising. Several caveats in interpreting these results are necessary: (1) miscoding of institution types is a common and challenging issue as noted by the data sources; (2) investment advisors (which include hedge funds) are the most likely to use complex hedging strategies, derivatives, or non-stock instruments such as convertible debt in building their portfolios and therefore we should expect that demand estimation will be most challenging for such institutions; and (3) the fact that all institutions possess informative hidden beliefs does not imply equal skill levels, with banks displaying stronger evidence of informative hidden beliefs than insurance companies in every single size decile.

*Remark 5.* The HBI subindex results are important for understanding the relationship between short sales and the HBI. Mutual funds, insurance companies, and pension funds are largely short sale constrained, indicating that the HBI’s predictive power at least partially derives from the

43

---

# Page 45

<table>
  <thead>
    <tr>
      <th rowspan="2">D10</th>
      <td>0.23</td>
      <td>0.76</td>
      <td>0.9</td>
      <td>-0.17</td>
      <td>0.33</td>
      <td rowspan="10" style="background: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet); text-align: center; vertical-align: middle;">8<br>-6<br>-4<br>-2<br>0<br>-2<br>-4<br>-6<br>-8</td>
    </tr>
    <tr>
      <th>D9</th>
      <td>0.44</td>
      <td>0.16</td>
      <td>-0.17</td>
      <td>-1.26</td>
      <td>0.17</td>
    </tr>
    <tr>
      <th>D8</th>
      <td>1.1</td>
      <td>1.05</td>
      <td>0.61</td>
      <td>0.97</td>
      <td>0.51</td>
    </tr>
    <tr>
      <th>D7</th>
      <td>1.5</td>
      <td>0.73</td>
      <td>0.28</td>
      <td>0.87</td>
      <td>0.61</td>
    </tr>
    <tr>
      <th>D6</th>
      <td>-0.78</td>
      <td>-0.98</td>
      <td>-0.93</td>
      <td>-0.93</td>
      <td>-0.03</td>
    </tr>
    <tr>
      <th>D5</th>
      <td>-0.43</td>
      <td>-0.72</td>
      <td>-0.72</td>
      <td>-0.23</td>
      <td>-0.08</td>
    </tr>
    <tr>
      <th>D4</th>
      <td>0.43</td>
      <td>-0</td>
      <td>1.16</td>
      <td>0.01</td>
      <td>1.47</td>
    </tr>
    <tr>
      <th>D3</th>
      <td>0.55</td>
      <td>0.92</td>
      <td>-0.76</td>
      <td>0.03</td>
      <td>0.36</td>
    </tr>
    <tr>
      <th>D2</th>
      <td>1.33</td>
      <td>1.32</td>
      <td>1.79</td>
      <td>0.93</td>
      <td>1.2</td>
    </tr>
    <tr>
      <th>D1</th>
      <td>0.74</td>
      <td>0.38</td>
      <td>1.22</td>
      <td>0.03</td>
      <td>0.9</td>
    </tr>
    <tr>
      <th></th>
      <th>Banks</th>
      <th>Insurance</th>
      <th>Inv Comp</th>
      <th>Mut Funds</th>
      <th>Pen Funds</th>
      <th></th>
    </tr>
  </thead>
</table>

Figure 3: OBI Predictive Power by Institution Type and Size Decile

**Note**: This heatmap details the t-statistics for the long/short OBI strategy across size deciles D1 to D10, with D10 the largest cap, for OBI subindices based on the hidden beliefs of five different institution types: banks, insurance companies, investment advisors, mutual funds, and pension funds. I sort equities into size deciles each quarter, then sort into equal weight quintile portfolios based on a given OBI subindex within each size decile. The long/short strategy holds long the three most recent past top quintile portfolios and sells short the three most recent bottom quintile portfolios. Daily returns are computed for the time period 1986Q1-2017Q4, with four-factor alpha and corresponding Newey-West standard errors computed. The derived t-statistics from this analysis are plotted in the heatmap.

hidden beliefs of short sale constrained institutions. Banks and investment advisors do indeed hold short positions as industry groups, yet many institutions within those categories are also short sale constrained; therefore we have suggestive evidence that even the beliefs of non-short sale constrained institutions are informative, but we cannot reach the same firm conclusion as we can with short sale constrained institutions. Aggregate short interest can in principle be connected with the hidden beliefs of institutions, yet it provides minimal information about them. First, although aggregate short interest is generally small as a fraction of market cap, it is sufficiently large that it is unable to meaningfully bound a given institution’s short demand. Second, short interest can be driven by negative institutional beliefs about a given stock’s blend of observable characteristics.

## 8.4 Parallel Patterns in Disaggregated Mutual Fund Data

The pattern of strongly predictive hidden beliefs and minimally informative overt beliefs is not only visible in the 13F filings of the Thomson Reuters s34 database, but also the mutual fund filings of the Thomson Reuters s12 database. 13F filings implicitly contain a level of aggregation, as 13F reporting institutions such as large mutual fund families might only file one report each quarter despite offering hundreds of different funds to investors. Disaggregated mutual fund holdings thus offer an opportunity to explore the degree to which this paper’s empirical approach is robust to

44

---

# Page 46

modest aggregation.$^{33}$

I repeat the “NAICS + style box” analysis of Section 7 using the s12 database, including only end of quarter filings to align with the 13F data.$^{34}$ I estimate demand for dynamic institutions in each quarter, again excluding institutions with rigid mandates that lead to static portfolios. Table 21 in Appendix Q provides the summary statistics for this analysis, with a lower fraction of institutional assets under management covered by the estimations due to the s12’s implicit restriction to mutual funds. On the other hand, the s12’s disaggregation versus 13F filings can result in institutions that are rigid at the 13F level having products included as “dynamic” when they are separated from other products. The s12 estimations thus cover a distinct but partially overlapping set of portfolios versus the s34 estimations.

In Tables 23 and 24 of Appendix Q, I report the results for the s12-based HBI and OBI.$^{35}$ Once again, the HBI displays strong predictive power. A composite long/short strategy using an equal weighting of the top eight size decile portfolios yields annualized four-factor alpha of 5.01% (6.90) for the HBI-based strategy. Disaggregation therefore yields comparably strong results, though the lack of disaggregated data for banks, insurance companies, hedge funds, and non-mutual fund investment advisors and the semiannual reporting frequency of much of the s12 data does not enable a one-to-one comparison. Comparing the “Type 4” (mutual fund) HBI daily abnormal returns using the 13F data and “style box” analysis with the HBI abnormal returns based on the above s12 mutual fund database analysis, we obtain an $R^2$ of 0.36, whereas the corresponding $R^2$ values for the HBIs generated from 13F filings of banks, insurance companies, investment advisors, and pensions funds are 0.05, 0.09, 0.02, and 0.19 respectively, consistent with the earlier finding of a stronger connection between pension fund and mutual fund HBI performance. These results illustrate the robustness of the methodology to the choice of data set and level of aggregation, but do not clarify the optimal level of disaggregation, which will vary based on managers’ internal decision making and research processes.

The results for the OBI become statistically significant with disaggregated data. A composite strategy of the top eight deciles yields annualized four-factor alpha of 2.76% (2.14), but these results severely understate the strength of the disaggregated OBI’s power, as the daily abnormal returns possess a correlation of $-0.55$ with the previously mentioned long/short idiosyncratic volatility strategy. In other words, the s12-based OBI strategy is an excellent hedge against the idiosyncratic

---

$^{33}$This paper’s model is designed to estimate belief parameters for a single decision maker, not the aggregation of multiple independent decision makers. On the other hand, large institutions have strong incentives to facilitate the sharing of idiosyncratic stock information across products and managers; many top institutions have a centralized research department that is responsible for generating company-specific analysis even if different products and strategies are offered. For such institutions, the parent institution’s 13F filing offers greater insight into hidden beliefs than the latent data for individual products.

$^{34}$I use this NAICS + “style box” methodology because it is most consistent with the mandates of mutual funds, which generally include restrictions on the market capitalization of holdings.

$^{35}$I include only institutions with at least 100 holdings in a given period in the index calculations. I exclude the portfolios with limited positive observations because they largely contribute noise to the indices, a minor issue with 13F filing data that is magnified by the significantly smaller portfolios found in disaggregated holdings. Similar portfolio size exclusion rules applied to the main specification with 13F data do not alter any of the previous analysis; results are virtually identical.

45

---

# Page 47

risks of a simple long/short strategy that capitalizes on one of the most extreme known anomalies, the underperformance of high volatility stocks versus their low volatility counterparts (see e.g. Ang, Hodrick, Xing and Zhang (2006) and Ang, Hodrick, Xing and Zhang (2009)); the lack of hedges for this idiosyncratic volatility strategy is one of the leading explanations for the idiosyncratic volatility puzzle (Stambaugh, Yu and Yuan (2015)). If we orthogonalize the OBI strategy returns to the returns of the idiosyncratic volatility strategy by including the daily abnormal returns of the long/short idiosyncratic volatility strategy as a fifth factor in the regression, we obtain strongly statistically significant annualized alpha of 4.98% (5.42); six-factor alpha (the five factors of Fama and French (2015), abbreviated “FF5,” with the “UMD” momentum factor of Carhart (1997) added) is similarly 4.14% (4.03). I also find larger abnormal performance when the universe of stocks is restricted to “high disagreement” stocks for which recent idiosyncratic volatility is above the median for their respective size deciles; the OBI-based strategy for such stocks in the s12 database yields four-factor alpha of 3.78% (2.84). Moreover, these abnormal returns are uncorrelated with the HBI’s abnormal returns, implying different mechanisms. However, this correlation pattern with idiosyncratic volatility is only visible in the OBI derived from disaggregated portfolio data, not the OBIs derived from 13F filings. The disaggregated data, though only available for mutual funds and at a lower frequency, nonetheless offers us a window into a potential underreaction mechanism for markets wherein managers’ overt beliefs are only partially incorporated into prices.

## 8.5 Manager Skill and the Informational Value of Overt Beliefs

Not all beliefs are created equal, yielding another application of this paper’s demand estimation methodology. In Appendix T, I revisit the analysis of Antón, Cohen and Polk (2021), who find that the “best ideas” of a subset of “highly active” mutual funds and a subsample of hedge funds outperform the stock market. In their analysis “best ideas” are those most overweighted versus the market portfolio. They use the Thomson Reuters s12 mutual fund database for their primary analysis, finding that a portfolio that holds long stocks that are in the top five “overweights” of at least one manager and short sells investments in each manager’s portfolio that are not in the top five has a six-factor alpha (FF5 + UMD) of approximately 0.14% per month, with stronger results of 0.26% per month when only going long each manager’s single top investment. I use a normalized version of this paper’s overt beliefs as a sorting variable and similarly find that a portfolio comprised of “top overt belief stocks” that are in the top few normalized overt beliefs of at least one manager generate statistically significant alpha. This provides further evidence that markets only gradually incorporate information.

## 8.6 Robustness

In Appendix S I conduct additional robustness tests and show that the HBI results are robust to alternative consideration set definitions, sorts based only on high volatility stocks, and alternate sets of characteristics.

46

---

# Page 48

## 8.7 The HBI, OBI, and Return Predictability: Putting it all Together

Taken together, the predictive power of the HBI and limited predictive power of the OBI paint a picture consistent with institutions displaying bounded rationality in forming stock-specific beliefs when faced with a complex information set. When offered data on the position of an investor, such as “Warren Buffet owns a million shares of Company X,” investors appear to account for most of the informational value of this investment, updating their beliefs in the correct direction on average, but not fully separating Warren Buffet’s preferences for value stocks in general from his preference for Company X in particular. We therefore see a weak amount of return predictability from the OBI, which estimates demand for observable characteristics and differences out this characteristic-based demand to leave behind stock-specific beliefs about returns.

On the other hand, when faced with the information “Warren Buffet does not own any shares in Company Y,” investors display behavior consistent with making an “inference error”: they fail to fully incorporate the informational value of a non-holding conditional on Warren Buffet’s preferences. Warren Buffet failing to own Tesla, GameStop, and a large cap value stock with significant cash flow are then taken to be insufficiently different for each of the three stocks when only the non-holding of the value stock provides meaningful information. When measures of these potential failures to correct beliefs are aggregated together, they provide us with an informative HBI. As evidenced by the HBI’s persistence in explaining returns over a multi-year time horizon, market participants’ stock-specific beliefs are only gradually updated over time to incorporate hidden beliefs, potentially when the information embedded in these beliefs becomes public.

## 9 Conclusion

This paper has developed a new approach to institution-level demand estimation in the presence of censoring and applied it to study the hidden and overt beliefs of institutions. Whereas aggregate institutional beliefs about the stocks they choose to purchase display little predictive power, aggregate bounds on institutional beliefs about assets they choose *not* to purchase strongly predict returns in the cross section. This asymmetric informational value of the Overt Beliefs Index (OBI) and the Hidden Beliefs Index (HBI) suggests that markets incorporate information about investors’ asset holdings into prices in a manner almost consistent with rational expectations but fail to fully account for the informational content of an institution not holding an asset. The HBI’s strong predictive power raises questions about canonical models of disagreement, short sale constraints, and equilibrium expectations. Past research has focused on the asymmetry induced by short sale constraints, but this paper presents evidence that informational asymmetries can generate strong return predictability when investors display boundedly rational inference. One might surmise that the public disclosure of short sale positions in 13F filings would alter these dynamics and reduce or eliminate the HBI’s ability to predict returns, yet the HBI is mostly a function of the decisions of short sale constrained institutions whose positions are already fully embedded in public filings, and the HBI predicts not only overvaluation of stock portfolios, but also undervaluation.

47

---

# Page 49

The study of hidden and overt beliefs is uniquely facilitated by this paper’s main methodological contribution: an approach to agent-level censored demand estimation with broad applicability to contexts where demand can be reduced to a censored linear model. When unobservable tastes or beliefs are not assumed to be drawn from a standard distribution but rather are central objects of economic interest, the econometrician can use this paper’s demand estimation approach to recover bounds on these hidden preferences. In markets that feature oligopsony or near oligopsony, such hidden beliefs represent a rich and unstudied vein for future analysis of institutional demand for products.

48

---

# Page 50

# References

Abaluck, Jason, and Abi Adams-Prassl. 2021. “What do Consumers Consider Before They Choose? Identification from Asymmetric Demand Responses.” *The Quarterly Journal of Economics*, 136(3): 1611–1663.

Admati, A.R. 1985. “A noisy rational expectations equilibrium for multi-asset securities markets.” *Econometrica: Journal of the Econometric Society*, 629–657.

Akepanidtaworn, Klakow, Rick Di Mascio, Alex Imas, and Lawrence D.W. Schmidt. 2023. “Selling Fast and Buying Slow: Heuristics and Trading Performance of Institutional Investors.” *The Journal of Finance*, 78(6): 3055–3098.

Andrews, Isaiah, James H. Stock, and Liyang Sun. 2019. “Weak Instruments in Instrumental Variables Regression: Theory and Practice.” *Annual Review of Economics*, 11(1): 727–753.

Ang, Andrew, Robert J Hodrick, Yuhang Xing, and Xiaoyan Zhang. 2006. “The cross-section of volatility and expected returns.” *The Journal of Finance*, 61(1): 259–299.

Ang, Andrew, Robert J Hodrick, Yuhang Xing, and Xiaoyan Zhang. 2009. “High idiosyncratic volatility and low returns: International and further US evidence.” *Journal of Financial Economics*, 91(1): 1–23.

Angrist, Joshua, Victor Chernozhukov, and Iván Fernández-Val. 2006. “Quantile Regression under Misspecification, with an Application to the U.S. Wage Structure.” *Econometrica*, 74(2): 539–563.

Antón, Miguel, Randolph B Cohen, and Christopher Polk. 2021. “Best ideas.” *Available at SSRN 1364827*.

Asness, Clifford S., Tobias J. Moskowitz, and Lasse Pedersen. 2013. “Value and Momentum Everywhere.” *Journal of Finance*, 68(3): 929–985.

Asquith, Paul, Parag A. Pathak, and Jay R. Ritter. 2005. “Short interest, institutional ownership, and stock returns.” *Journal of Financial Economics*, 78(2): 243–276.

Bilias, Yannis, Kostas Florios, and Spyros Skouras. 2019. “Exact computation of Censored Least Absolute Deviations estimator.” *Journal of Econometrics*, 212(2): 584–606.

Blundell, Richard, and James L Powell. 2007. “Censored regression quantiles with endogenous regressors.” *Journal of Econometrics*, 141(1): 65–83.

Boehmer, Ekkehart, Charles M. Jones, and Xiaoyan Zhang. 2008. “Which Shorts Are Informed?” *The Journal of Finance*, 63(2): 491–527.

Campbell, John Y, Martin Lettau, Burton G Malkiel, and Yexiao Xu. 2001. “Have individual stocks become more volatile? An empirical exploration of idiosyncratic risk.” *The Journal of Finance*, 56(1): 1–43.

Campbell, J.Y., and L.M. Viceira. 2002. *Strategic asset allocation: portfolio choice for long-term investors*. Oxford University Press, USA.

Carhart, Mark M. 1997. “On persistence in mutual fund performance.” *The Journal of Finance*, 52(1): 57–82.

49

---

# Page 51

Chen, Jiafeng, and Jonathan Roth. 2024. “Logs with Zeros? Some Problems and Solutions.” *The Quarterly Journal of Economics*, 139(2): 891–936.

Chen, Joseph, Harrison Hong, and Jeremy C Stein. 2002. “Breadth of ownership and stock returns.” *Journal of Financial Economics*, 66(2): 171–205.

Chen, Songnian. 2018. “Sequential estimation of censored quantile regression models.” *Journal of Econometrics*, 207(1): 30–52.

Chen, Xiaohong, Timothy M. Christensen, and Elie Tamer. 2018. “Monte Carlo Confidence Sets for Identified Sets.” *Econometrica*, 86(6): 1965–2018.

Chernozhukov, Victor, Iván Fernández-Val, and Amanda E. Kowalski. 2015. “Quantile regression with censoring and endogeneity.” *Journal of Econometrics*, 186(1): 201–221.

Daniel, Kent, Alexander Klos, and Simon Rottke. 2023. “The dynamics of disagreement.” *The Review of Financial Studies*, 36(6): 2431–2467.

Enke, Benjamin, and Thomas Graeber. 2023. “Cognitive Uncertainty.” *The Quarterly Journal of Economics*, 138(4): 2021–2067.

Eyster, Erik, Matthew Rabin, and Dimitri Vayanos. 2019. “Financial Markets Where Traders Neglect the Informational Content of Prices.” *Journal of Finance*, 74(1): 371–399.

Fama, Eugene F, and Kenneth R French. 1993. “Common risk factors in the returns on stocks and bonds.” *Journal of financial economics*, 33(1): 3–56.

Fama, Eugene F., and Kenneth R. French. 2015. “A five-factor asset pricing model.” *Journal of Financial Economics*, 116(1): 1–22.

Gabaix, Xavier. 2014. “A Sparsity-Based Model of Bounded Rationality.” *The Quarterly Journal of Economics*, 129(4): 1661–1710.

Gabaix, Xavier, Parameswaran Gopikrishnan, Vasiliki Plerou, and H. Eugene Stanley. 2006. “Institutional Investors and Stock Market Volatility.” *The Quarterly Journal of Economics*, 121(2): 461–504.

Gârleanu, Nicolae, and Lasse Heje Pedersen. 2022. “Active and passive investing: Understanding Samuelson's dictum.” *The Review of Asset Pricing Studies*, 12(2): 389–446.

Goeree, Michelle Sovinsky. 2008. “Limited Information and Advertising in the U.S. Personal Computer Industry.” *Econometrica*, 76(5): 1017–1074.

Goyal, Amit, and Pedro Santa-Clara. 2003. “Idiosyncratic Risk Matters!” *Journal of Finance*, 58(3): 975–1007.

Grossman, S.J., and J.E. Stiglitz. 1980. “On the impossibility of informationally efficient markets.” *The American Economic Review*, 393–408.

Hellwig, M.F. 1980. “On the aggregation of information in competitive markets.” *Journal of Economic Theory*, 22(3): 477–498.

Hendel, Igal. 1999. “Estimating Multiple-Discrete Choice Models: An Application to Computerization Returns.” *The Review of Economic Studies*, 66(2): 423–446.

Hong, H., and J.C. Stein. 2007. “Disagreement and the stock market.” *The Journal of Economic Perspectives*, 21(2): 109–128.

---

# Page 52

Jones, Charles M, and Owen A Lamont. 2002. “Short-sale constraints and stock returns.” *Journal of Financial Economics*, 66(2): 207–239.

Kacperczyk, Marcin, Stijn Van Nieuwerburgh, and Laura Veldkamp. 2016. “A Rational Theory of Mutual Funds’ Attention Allocation.” *Econometrica*, 84: 571–626.

Khan, Shakeeb, and Elie Tamer. 2009. “Inference on endogenously censored regression models using conditional moment inequalities.” *Journal of Econometrics*, 152(2): 104–119.

Khaw, Mel Win, Ziang Li, and Michael Woodford. 2021. “Cognitive Imprecision and Small-Stakes Risk Aversion.” *The Review of Economic Studies*, 88(4): 1979–2013.

Koenker, Roger, and Gilbert Bassett. 1978. “Regression Quantiles.” *Econometrica*, 46(1): 33–50.

Koijen, Ralph S. J., and Motohiro Yogo. 2019. “A Demand System Approach to Asset Pricing.” *Journal of Political Economy*, 127(4): 1475 – 1515.

Lee, Lung-Fei, and GS Maddala. 1985. “The common structure of tests for selectivity bias, serial correlation, heteroscedasticity and non-normality in the Tobit model.” *International Economic Review*, 1–20.

Miller, E.M. 1977. “Risk, Uncertainty, and Divergence of Opinion.” *Journal of Finance*, 1151–1168.

Newey, Whitney K. 2001. “Conditional Moment Restrictions In Censored And Truncated Regression Models.” *Econometric Theory*, 17(5): 863–888.

Olea, José Luis Montiel, and Carolin Pflueger. 2013. “A robust test for weak instruments.” *Journal of Business & Economic Statistics*, 31(3): 358–369.

Powell, James L. 1984. “Least absolute deviations estimation for the censored regression model.” *Journal of econometrics*, 25(3): 303–325.

Powell, James L. 1986. “Censored regression quantiles.” *Journal of econometrics*, 32(1): 143–155.

Scheinkman, Jose A, and Wei Xiong. 2003. “Overconfidence and Speculative Bubbles.” *Journal of Political Economy*, 111(6).

Shumway, Tyler. 1997. “The Delisting Bias in CRSP Data.” *The Journal of Finance*, 52(1): 327–340.

Stambaugh, Robert F., Jianfeng Yu, and Yu Yuan. 2015. “Arbitrage Asymmetry and the Idiosyncratic Volatility Puzzle.” *The Journal of Finance*, 70(5): 1903–1948.

Stock, James H, and Motohiro Yogo. 2005. “Testing for Weak Instruments in Linear IV Regression.” *Identification and Inference for Econometric Models: Essays in Honor of Thomas Rothenberg*, 80.

Tversky, Amos, and Daniel Kahneman. 1974. “Judgment under Uncertainty: Heuristics and Biases.” *Science*, 185(4157): 1124–1131.

Van Nieuwerburgh, Stijn, and Laura Veldkamp. 2010. “Information acquisition and under-diversification.” *The Review of Economic Studies*, 77(2): 779–805.

51

---

# Page 53

# Online Appendix

A Optimal Institutional Portfolio Choice 54

B Single Factor Model with Arbitrary Idiosyncratic Volatility 56

C Two Factor and Arbitrary Multi-Factor Model with Arbitrary Idiosyncratic Volatility 57

D Recovery and Identification of Demand Parameters versus Belief Parameters 60

E SCQR and Alternate Approaches to Censored Regression and Confidence Sets 62

F Estimation: Confidence Sets and MIP-based CLAD Estimation 64

 F.1 Confidence Sets for Agent Demand Parameters 64

 F.2 Estimation via Bilias, Florios and Skouras (2019) 65

G Alternative Characteristics: Asness, Moskowitz and Pedersen (2013) 65

H Simulation Results: Recovering Demand Parameters 66

 H.1 Drawing Beliefs, Consideration Sets, and Constraints 67

 H.2 Optimization and Estimation 68

I Asset Demand Estimation Simulation 71

 I.1 Drawing Beliefs, Consideration Sets, and Constraints 71

 I.2 Optimization and SCQR Estimation 72

 I.3 Estimation via Kojien and Yogo (2019) 72

 I.4 Linear Model, Mean Zero Restriction 75

 I.5 Kojien and Yogo (2019) with Idiosyncratic Volatility Scaling 75

 I.6 Linear GMM with Idiosyncratic Volatility Scaling 75

 I.7 Linear GMM with Idiosyncratic Volatility Scaling, Positive Holdings Only 75

J Additional HBI and OBI Results 75

 J.1 OLS Placebo Test 75

 J.2 HBI Quintiles at Different Lags 75

K Instrumental Variable Strength and Rigid vs Dynamic Assets 80

L Breadth Portfolio Sorts 84

M Idiosyncratic Volatility Portfolio Sorts 84

N Short Sale Portfolio Sorts 86

52

---

# Page 54

O Institutional Ownership Portfolio Sorts 86

P Data Appendix and Computational Details 89
- P.1 Data Appendix 89
- P.2 Computational Details 89

Q Additional Tables for S12 Disaggregated Mutual Fund Data Analysis 90

R Value-Weighted HBI Results 92

S Additional Robustness Tests 94

T The Informational Content of Top Overt Beliefs 97

U Model of Hidden and Overt Beliefs 98

V Comparison with Kojien and Yogo (2019) 108

W HBI and Return Predictability over Time: Long/Short Performance 108

53

---

# Page 55

# A Optimal Institutional Portfolio Choice

I solve the optimization problem with full generality by using both short and long leverage constraints, with all leverage-related Lagrange multipliers vanishing as leverage is allowed to be arbitrarily large. We start with solving the problem

$$
\sum w_{i,t}(n) \leq L_{i,t}^L; \sum w_{i,t}(n) \geq L_{i,t}^S; w_{i,t} \geq 0 \quad \mathbb{E}_{i,t} \left[ \log \left( A_{i,T} \right) \right]
\quad \text{(17)}
$$

where the problem is implicitly taken to be over all assets $n : n \in \mathcal{H}_{i,t}$ .

We form the Lagrangian

$$
\mathcal{L}_{i,t} = \mathbb{E}_{i,t} \left[ \log \left( A_{i,T} \right) + \sum_{s=t}^{T-1} \left[ \lambda_{i,s}' w_{i,s} + \eta_{i,t}^{Long} \left( L_{i,t}^L - w_{i,s}' \mathbf{1} \right) + \eta_{i,t}^{Short} \left( -L_{i,t}^S + w_{i,s}' \mathbf{1} \right) \right] \right].
\quad \text{(18)}
$$

We can decompose the log of terminal assets as in Kojien and Yogo (2019) and much of the finance literature into

$$
\mathcal{L}_{i,t} = \log \left( A_{i,t} \right) + \mathbb{E}_{i,t} \left[ \sum_{s=t}^{T-1} \log \left( \frac{A_{i,s+1}}{A_{i,s}} \right) + \sum_{r=t}^{T-1} \left[ \lambda_{i,s}' w_{i,s} + \eta_{i,t}^{Long} \left( L_{i,t}^L - w_{i,s}' \mathbf{1} \right) + \eta_{i,t}^{Short} \left( -L_{i,t}^S + w_{i,s}' \mathbf{1} \right) \right] \right]
\quad \text{(19)}
$$

and then

$$
\mathcal{L}_{i,t} = \log \left( A_{i,t} \right) + \mathbb{E}_{i,t} \left[ \sum_{s=t}^{T-1} \log \left( w_{i,s}' R_{t+1} \right) + \sum_{r=t}^{T-1} \left[ \lambda_{i,s}' w_{i,s} + \eta_{i,t}^{Long} \left( L_{i,t}^L - w_{i,s}' \mathbf{1} \right) + \eta_{i,t}^{Short} \left( -L_{i,t}^S + w_{i,s}' \mathbf{1} \right) \right] \right].
\quad \text{(20)}
$$

We readily see that the optimal portfolio problem is myopic with the solution given by the first order condition

$$
\frac{\partial \mathcal{L}_{i,t}}{\partial w_{i,t}} = \mathbb{E}_{i,t} \left[ \frac{1}{w_{i,t}' R_{t+1}} R_{t+1} + \lambda_{i,t} - \left( \eta_{i,t}^{Long} - \eta_{i,t}^{Short} \right) \mathbf{1} \right] = 0.
\quad \text{(21)}
$$

$$
\mathbb{E}_{i,t} \left[ \frac{1}{w_{i,t}' R_{t+1}} R_{t+1} \right] = \left( \eta_{i,t}^{Long} - \eta_{i,t}^{Short} \right) \mathbf{1} - \lambda_{i,t}
\quad \text{(22)}
$$

as well as the complementary slackness conditions $\lambda_{i,t}' w_{i,t} = 0$ , $\eta_{i,t}^{Long} \left( L_{i,t}^L - w_{i,t}' \mathbf{1} \right) = 0$ , and $\eta_{i,t}^{Short} \left( -L_{i,t}^S + w_{i,s}' \mathbf{1} \right) = 0$ .

I follow the approximation of Kojien and Yogo (2019) (which is itself the commonly used derivation of approximate log portfolio returns from Campbell and Viceira (2002)) and use the Taylor series approximation

$$
\log \left( \frac{A_{i,t+1}}{A_{i,t}} \right) \approx w_{i,t}' \left( r_{t+1} + \frac{1}{2} \operatorname{diag} \left( \Sigma_{i,t} \right) \right) - \frac{1}{2} w_{i,t}' \Sigma_{i,t} w_{i,t}
$$

54

---

# Page 56

which leads to the first order condition

$$
\frac{\partial \mathcal{L}_{i,t}}{\partial w_{i,t}} = r_{t+1} + \frac{1}{2} \operatorname{diag}(\Sigma_{i,t}) - \Sigma_{i,t} w_{i,t} - \left( \eta_{i,t}^{Long} - \eta_{i,t}^{Short} \right) \mathbf{1} + \lambda_{i,t} = 0 \quad (23)
$$

and by rearrangement and setting $\mu_{i,t} = r_{t+1} + \frac{1}{2} \operatorname{diag}(\Sigma_{i,t})$ ,

$$
w_{i,t} = \Sigma_{i,t}^{-1} \left( \mu_{i,t} - \left( \eta_{i,t}^{Long} - \eta_{i,t}^{Short} \right) \mathbf{1} + \lambda_{i,t} \right). \quad (24)
$$

If $L_{i,t} = \infty$ and the managers are unconstrained then we are left with the simple expression

$$
w_{i,t} \approx \Sigma_{i,t}^{-1} \mu_{i,t} \quad (25)
$$

while if $0 < L_{i,t} < \infty$ and there are no short sale constraints, then we have

$$
w_{i,t} \approx \Sigma_{i,t}^{-1} \left( \mu_{i,t} - \eta_{i,t}^{Long} \mathbf{1} \right) \quad (26)
$$

where $\eta_{i,t}^{Long}$ captures the shadow value of relaxing the leverage constraint.

For the general case with short sale constraints, using the assumption that $\Sigma_t = \Gamma_{i,t} \Gamma_{i,t}' + D_{i,t}$ where $D_t$ is diagonal and $\Gamma$ is a vector of loadings on the market factor (beta), and dropping all of the subscripts for legibility, we have that

$$
\begin{aligned}
w &= (\Gamma \Gamma' + D)^{-1} \left( \mu - \left( \eta^{Long} - \eta^{Short} \right) \mathbf{1} + \lambda \right) \\
&= \left( D D^{-1} \Gamma \Gamma' + D \mathbf{I} \right)^{-1} \left( \mu - \left( \eta^{Long} - \eta^{Short} \right) \mathbf{1} + \lambda \right) \\
&= \left( D \left( D^{-1} \Gamma \Gamma' + \mathbf{I} \right) \right)^{-1} \left( \mu - \left( \eta^{Long} - \eta^{Short} \right) \mathbf{1} + \lambda \right) \\
&= \left( \left( D^{-1} \Gamma \right) \Gamma' + \mathbf{I} \right)^{-1} D^{-1} \left( \mu - \left( \eta^{Long} - \eta^{Short} \right) \mathbf{1} + \lambda \right) \\
&= \left( \mathbf{I} - \mathbf{I} D^{-1} \Gamma \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' \right) D^{-1} \left( \mu - \left( \eta^{Long} - \eta^{Short} \right) \mathbf{1} + \lambda \right) \\
&= D^{-1} \left( \mu - \left( \eta^{Long} - \eta^{Short} \right) \mathbf{1} + \lambda \right) - \left( D^{-1} \Gamma \right) \left[ \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \left( \mu - \left( \eta^{Long} - \eta^{Short} \right) \mathbf{1} + \lambda \right) \right] \\
&= D^{-1} \left( \mu - \left( \eta^{Long} - \eta^{Short} \right) \mathbf{1} + \lambda \right) - \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} D^{-1} \Gamma \Gamma' D^{-1} \left( \mu - \left( \eta^{Long} - \eta^{Short} \right) \mathbf{1} + \lambda \right) \\
&= D^{-1} \left( \mu - \left( \eta^{Long} - \eta^{Short} \right) \mathbf{1} + \lambda \right) - D^{-1} \Gamma \left\{ \Gamma' D^{-1} \left( \mu - \left( \eta^{Long} - \eta^{Short} \right) \mathbf{1} + \lambda \right) \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \right\} \\
&= D^{-1} \left( \mu - \left( \eta^{Long} - \eta^{Short} \right) \mathbf{1} + \lambda - \kappa^C \Gamma \right) \\
&= D^{-1} \left( \mu - \left( \eta^{Long} - \eta^{Short} \right) \mathbf{1} + \lambda \right) - \kappa^C D^{-1} \Gamma
\end{aligned}
$$

where the 5th line follows from the Sherman-Morrison formula (we have here explicitly used the Woodbury formula to show Sherman-Morrison) and

$$
\kappa^C = \Gamma' D^{-1} \left( \mu - \left( \eta^{Long} - \eta^{Short} \right) \mathbf{1} + \lambda \right) \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \quad (27)
$$

is a scalar.

55

---

# Page 57

But by complementary slackness we must have that either $\lambda_n = 0$ or

$$
\sigma_t^{-2}(n)\left(\mu(n) - \left(\eta^{Long} - \eta^{Short}\right) + \lambda_n\right) - \kappa^C \sigma_t^{-2}(n)\Gamma(n) = 0
$$

in which case

$$
\lambda_n = \kappa^C \Gamma(n) - \left(\mu(n) - \left(\eta^{Long} - \eta^{Short}\right)\right).
$$

This captures the fact that assets with higher beta (greater $\Gamma(n)$ ) and lower returns $\mu(n)$ have binding short sale constraints. We can therefore express the vector of Lagrange multipliers as

$$
\lambda = \max\left(0, \kappa^C \Gamma - \mu + \left(\eta^{Long} - \eta^{Short}\right)\mathbf{1}\right)
$$

where the max operator is taken elementwise.

Therefore we have that

$$
w = \max\left(D^{-1}\left(\mu - \left(\eta^{Long} - \eta^{Short}\right)\mathbf{1} - \kappa^C \Gamma\right), 0\right)
$$

where the max operator is likewise applied elementwise. In words, the optimal portfolio is equal to the greater of zero and the expected return weighted by the inverse of idiosyncratic variance, shrunk by a factor proportional to the ratio of factor exposure and the inverse of idiosyncratic variance.

When the manager faces no short sale constraints for a subset of stocks $\mathcal{S}_1$ and short sale constraints for a different subset $\mathcal{S}_2$ , let $\lambda \in \mathbb{R}_+^N$ be such that $\lambda_n = 0 \; \forall n \in \mathcal{S}_1$ and otherwise let $\lambda_n$ be the Lagrange multiplier representing the shadow value of relaxing the short sale constraint on asset $n \in \mathcal{S}_2$ . We then have that

$$
w_n = \begin{cases}
\sigma_n^{-2}\left(\mu_n - \left(\eta^{Long} - \eta^{Short}\right) - \kappa^C \Gamma_n\right) & n \in \mathcal{S}_1 \\
\max\left(\sigma_n^{-2}\left(\mu_n - \left(\eta^{Long} - \eta^{Short}\right) - \kappa^C \Gamma_n\right), 0\right) & n \in \mathcal{S}_2
\end{cases}
$$

by the exact same algebraic derivations applied with the new definition of $\lambda$ .

## B Single Factor Model with Arbitrary Idiosyncratic Volatility

Let us assume a single-factor model, linear in characteristics, as in Kojien and Yogo (2019), so that $\Sigma_{i,t} = \Gamma_{i,t} \Gamma_{i,t}' + D_{i,t}$ where $D_{i,t}$ is a positive definite diagonal idiosyncratic variance matrix. Then we have that

$$
w_{i,t} = \left(\Gamma_{i,t} \Gamma_{i,t}' + D_{i,t}\right)^{-1} (\mu_{i,t} - \lambda_{i,t} \mathbf{1})
$$

$$
= \left(D_{i,t} D_{i,t}^{-1} \Gamma_{i,t} \Gamma_{i,t}' + D_{i,t} \mathbf{I}\right)^{-1} (\mu_{i,t} - \lambda_{i,t} \mathbf{1})
$$

$$
= \left(D_{i,t} \left(D_{i,t}^{-1} \Gamma_{i,t} \Gamma_{i,t}' + \mathbf{I}\right)\right)^{-1} (\mu_{i,t} - \lambda_{i,t} \mathbf{1})
$$

56

---

# Page 58

$$
= \left( \left( D_{i,t}^{-1} \Gamma_{i,t} \right) \Gamma_{i,t}' + \mathbf{I} \right)^{-1} D_{i,t}^{-1} \left( \mu_{i,t} - \lambda_{i,t} \mathbf{1} \right)
$$

$$
= \left( \mathbf{I} - \mathbf{I} D_{i,t}^{-1} \Gamma_{i,t} \left( 1 + \Gamma_{i,t}' D_{i,t}^{-1} \Gamma_{i,t} \right)^{-1} \Gamma_{i,t}' \right) D_{i,t}^{-1} \left( \mu_{i,t} - \lambda_{i,t} \mathbf{1} \right)
$$

$$
= D_{i,t}^{-1} \left( \mathbf{x}_t' \beta_{i,t} + \epsilon_{i,t} - \lambda_{i,t} \mathbf{1} \right) - \left( D_{i,t}^{-1} \Gamma_{i,t} \right) \left[ \left( 1 + \Gamma_{i,t}' D_{i,t}^{-1} \Gamma_{i,t} \right)^{-1} \Gamma_{i,t}' D_{i,t}^{-1} \left( \mu_{i,t} - \lambda_{i,t} \mathbf{1} \right) \right]
$$

$$
= D_{i,t}^{-1} \left( \mathbf{x}_t' \beta_{i,t} + \epsilon_{i,t} - \lambda_{i,t} \mathbf{1} \right) - \left( 1 + \Gamma_{i,t}' D_{i,t}^{-1} \Gamma_{i,t} \right)^{-1} D_{i,t}^{-1} \Gamma_{i,t} \Gamma_{i,t}' D_{i,t}^{-1} \left( \mu_{i,t} - \lambda_{i,t} \mathbf{1} \right)
$$

$$
= D_{i,t}^{-1} \left( \mathbf{x}_t' \beta_{i,t} + \epsilon_{i,t} - \lambda_{i,t} \mathbf{1} \right) - D_{i,t}^{-1} \Gamma_{i,t} \left\{ \Gamma_{i,t}' D_{i,t}^{-1} \left( \mu_{i,t} - \lambda_{i,t} \mathbf{1} \right) \left( 1 + \Gamma_{i,t}' D_{i,t}^{-1} \Gamma_{i,t} \right)^{-1} \right\}
$$

$$
= D_{i,t}^{-1} \left( \mathbf{x}_t' \beta_{i,t} + \epsilon_{i,t} - \lambda_{i,t} \mathbf{1} - \kappa_{i,t} \Gamma_{i,t} \right)
$$

$$
= D_{i,t}^{-1} \left( \mathbf{x}_t' \beta_{i,t} - \kappa_{i,t} \Gamma_{i,t} - \lambda_{i,t} \mathbf{1} + \epsilon_{i,t} \right)
$$

where the 5th line follows from the Sherman-Morrison formula (we have here explicitly used the Woodbury formula to show Sherman-Morrison) and

$$
\kappa_{i,t} = \Gamma_{i,t}' D_{i,t}^{-1} \left( \mu_{i,t} - \lambda_{i,t} \mathbf{1} \right) \left( 1 + \Gamma_{i,t}' D_{i,t}^{-1} \Gamma_{i,t} \right)^{-1}.
\quad (28)
$$

We now see that with heterogeneous idiosyncratic volatility, we must express weights as a linear combination of characteristics that is invariant to the asset but weighted by the inverse of idiosyncratic volatility. This makes intuitive sense: if one asset possesses extreme idiosyncratic volatility but the same characteristics as another asset, then the one with higher volatility would have smaller weights.

## C Two Factor and Arbitrary Multi-Factor Model with Arbitrary Idiosyncratic Volatility

Let us assume a two-factor model so that $\Sigma_{i,t} = \Gamma_{i,t} \Gamma_{i,t}' + \Omega_{i,t} \Omega_{i,t}' + D_{i,t}$ where $D_{i,t}$ is a diagonal idiosyncratic variance matrix with strictly positive eigenvalues, $\Gamma$ is the “main” risk factor detailed in the last section and $\Omega$ is a second risk factor. We can group $\Sigma$ as $\Sigma = (\Gamma \Gamma' + D) + \Omega \Omega'$ and $\Sigma^{-1} = ((\Gamma \Gamma' + D) + \Omega \Omega')^{-1}$ .

We have already calculated $(\Gamma \Gamma' + D)^{-1}$ in the last subsection, so here we can exploit the Woodbury matrix identity again to obtain, letting $\theta = \left( 1 + \Omega' (\Gamma \Gamma' + D)^{-1} \Omega \right)^{-1}$

$$
\left( (\Gamma \Gamma' + D) + \Omega \Omega' \right)^{-1} = (\Gamma \Gamma' + D)^{-1} - (\Gamma \Gamma' + D)^{-1} \Omega \left( 1 + \Omega' (\Gamma \Gamma' + D)^{-1} \Omega \right)^{-1} \Omega' (\Gamma \Gamma' + D)^{-1}
$$

$$
= (\Gamma \Gamma' + D)^{-1} - \theta \left( D^{-1} - D^{-1} \Gamma \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \right) \Omega \Omega' \left( D^{-1} - D^{-1} \Gamma \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \right)
$$

$$
= (\Gamma \Gamma' + D)^{-1} - \theta \left( D^{-1} - D^{-1} \Gamma \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \right) \Omega \Omega' \left( D^{-1} - D^{-1} \Gamma \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \right)
$$

$$
= \left( D^{-1} - D^{-1} \Gamma \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \right)
$$

$$
- \theta \left( D^{-1} - D^{-1} \Gamma \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \right) \Omega \Omega' \left( D^{-1} - D^{-1} \Gamma \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \right)
$$

$$
= \left\{ D^{-1} \right\} - D^{-1} \Gamma \left\{ \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \right\}.
$$

57

---

# Page 59

$$
-D^{-1} \Omega \left\{ \theta \Omega' \left( D^{-1} - D^{-1} \Gamma \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \right) \right\}
$$

$$
+ D^{-1} \Gamma \left\{ \theta \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \Omega \Omega' \left( D^{-1} - D^{-1} \Gamma \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \right) \right\}
$$

This then implies that

$$
w = \left\{ D^{-1} (\mu + \lambda) \right\} - D^{-1} \Gamma \left\{ \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} (\mu + \lambda) \right\}
$$

$$
- D^{-1} \Omega \left\{ \theta \Omega' \left( D^{-1} - D^{-1} \Gamma \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \right) (\mu + \lambda) \right\}
$$

$$
+ D^{-1} \Gamma \left\{ \theta \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \Omega \Omega' \left( D^{-1} - D^{-1} \Gamma \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \right) (\mu + \lambda) \right\}
$$

$$
= D^{-1} (\mu + \lambda) - D^{-1} \kappa_1 \Gamma - D^{-1} \kappa_2 \Omega = D^{-1} \left[ \mu + \lambda - \kappa_1 \Gamma - \kappa_2 \Omega \right]
$$

where

$$
\kappa_1 = \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} (\mu + \lambda) -
$$

$$
\theta \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \Omega \Omega' \left( D^{-1} - D^{-1} \Gamma \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \right) (\mu + \lambda)
$$

and

$$
\kappa_2 = \theta \Omega' \left( D^{-1} - D^{-1} \Gamma \left( 1 + \Gamma' D^{-1} \Gamma \right)^{-1} \Gamma' D^{-1} \right) (\mu + \lambda).
$$

By complementary slackness, either $w_n = 0$ or $\lambda_n = 0$ so when $\lambda_n = 0$ we have $w_n = \left( D^{-1} \left[ \mu - \kappa_1 \Gamma - \kappa_2 \Omega \right] \right)_n \geq 0$ and when $\lambda_n > 0$ , $w_n = 0$ and since $D^{-1}$ is diagonal we have that $\left( D^{-1} \left[ \mu - \kappa_1 \Gamma - \kappa_2 \Omega \right] \right)_n < 0$ . Thus,

$$
w = D^{-1} \max \left( 0, \mu - \kappa_1 \Gamma - \kappa_2 \Omega \right).
$$

We can generalize to the arbitrary multifactor case via an inductive argument. Suppose we have already shown that for linearly independent risk factors $\Gamma_1, \Gamma_2, ..., \Gamma_{n-1}$ , with $n \geq 3$ , that $w = D^{-1} (\mu + \lambda) - \sum_{j=1}^{n-1} \kappa_j D^{-1} \Gamma_j$ and moreover that

$$
\left( \sum_{j=1}^{n-1} \Gamma_j \Gamma_j' + D \right)^{-1} = D^{-1} - \sum_{j=1}^{n-1} D^{-1} \left( \kappa_j \Gamma_j \Psi_j \right) = D^{-1} \left( I - \sum_{j=1}^{n-1} \kappa_j \Gamma_j \Psi_j \right)
$$

where $\Psi_j$ is $1 \times n$ and $\kappa_j$ is a constant. Then we have that for $n$ risk factors, by the Woodbury matrix identity,

$$
\left( \left( \sum_{j=1}^{n-1} \Gamma_j \Gamma_j' + D \right) + \Gamma_n \Gamma_n' \right)^{-1} (\mu + \lambda) =
$$

$$
\left( \sum_{j=1}^{n-1} \Gamma_j \Gamma_j' + D \right)^{-1} (\mu + \lambda)
$$

$$
- \left( \sum_{j=1}^{n-1} \Gamma_j \Gamma_j' + D \right)^{-1} \Gamma_n \left( 1 + \Gamma_n' \left( \sum_{j=1}^{n-1} \Gamma_j \Gamma_j' + D \right)^{-1} \Gamma_n \right)^{-1} \Gamma_n' \left( \sum_{j=1}^{n-1} \Gamma_j \Gamma_j' + D \right)^{-1} (\mu + \lambda)
$$

58

---

# Page 60

$$
= D^{-1}(\mu + \lambda) - \sum_{j=1}^{n-1} \kappa_j D^{-1} \Gamma_j
$$

$$
- D^{-1} \Gamma_n \left( 1 + \Gamma_n' \left( \sum_{j=1}^{n-1} \Gamma_j \Gamma_j' + D \right)^{-1} \Gamma_n \right)^{-1} \Gamma_n' \left( \sum_{j=1}^{n-1} \Gamma_j \Gamma_j' + D \right)^{-1} (\mu + \lambda)
$$

$$
+ \left( \sum_{j=1}^{n-1} D^{-1} (\kappa_j \Gamma_j \Psi_j) \right) \Gamma_n \left( 1 + \Gamma_n' \left( \sum_{j=1}^{n-1} \Gamma_j \Gamma_j' + D \right)^{-1} \Gamma_n \right)^{-1} \Gamma_n' \left( \sum_{j=1}^{n-1} \Gamma_j \Gamma_j' + D \right)^{-1} (\mu + \lambda).
$$

Now let $\theta_j = \Psi_j \Gamma_n \left( 1 + \Gamma_n' \left( \sum_{j=1}^{n-1} \Gamma_j \Gamma_j' + D \right)^{-1} \Gamma_n \right)^{-1} \Gamma_n' \left( \sum_{j=1}^{n-1} \Gamma_j \Gamma_j' + D \right)^{-1} (\mu + \lambda)$ , which is a scalar. We then have

$$
w = D^{-1}(\mu + \lambda) - \sum_{j=1}^{n-1} (\kappa_j - \kappa_j \theta_j) D^{-1} \Gamma_j - \tilde{\kappa}_n D^{-1} \Gamma_n
$$

or

$$
w = D^{-1}(\mu + \lambda) - \sum_{j=1}^{n-1} (1 - \theta_j) \kappa_j D^{-1} \Gamma_j - \tilde{\kappa}_n D^{-1} \Gamma_n \quad (29)
$$

where $\tilde{\kappa}_n = \left( 1 + \Gamma_n' \left( \sum_{j=1}^{n-1} \Gamma_j \Gamma_j' + D \right)^{-1} \Gamma_n \right)^{-1} \Gamma_n' \left( \sum_{j=1}^{n-1} \Gamma_j \Gamma_j' + D \right)^{-1} (\mu + \lambda)$ . Letting $\tilde{\kappa}_j = \kappa_j - \kappa_j \theta_j$ then we have $w = D^{-1}(\mu + \lambda) - \sum_{j=1}^{n} \tilde{\kappa}_j D^{-1} \Gamma_j$ and the inductive step is complete.

This proof is almost constructive for solving for the $\kappa$ values when the institution is short sale constrained, we merely need to establish that each $\kappa_j$ value is a function of $\mu + \lambda$ such that $\kappa_j$ takes the form $a_j' D^{-1} (\mu + \lambda)$ where $a_j \in \mathbb{R}^N$ is a function only of known risk factors and idiosyncratic volatility. But we have already shown this to be the case for $n = 1$ and $n = 2$ and that if it is this way for $n - 1$ then it also holds for $n$ , thus we are done with the inductive step.

For constrained institutions, the solution for the $\kappa$ values is generated by creating a system of $n$ equations in $n$ variables. The constrained weights are

$$
w^C = D^{-1}(\mu + \lambda) - \sum_{j=1}^{n} \kappa_j D^{-1} \Gamma_j \quad (30)
$$

First, we premultiply equation (30) by $a_1'$ to obtain $a_1' w^C = a_1' D^{-1} (\mu + \lambda) - \sum_{j=1}^{n} \kappa_j a_1' D^{-1} \Gamma_j = \kappa_1 - \sum_{j=1}^{n} \kappa_j a_1' D^{-1} \Gamma_j = (1 - a_1' D^{-1} \Gamma_1) \kappa_1 - \sum_{j=2}^{n} \kappa_j a_1' D^{-1} \Gamma_j$ . This is clearly a linear equation with $n$ unknowns, each of the $\kappa_j$ values. Proceeding to generate such equations by premultiplying

59

---

# Page 61

by $a_2', ..., a_n'$ , we obtain a system of $n$ equations in $n$ variables. The solution to this equation is

$$
\begin{bmatrix}
\kappa_1 \\
\kappa_2 \\
\vdots \\
\vdots \\
\kappa_n
\end{bmatrix}
=
\begin{bmatrix}
(1 - a_1'D^{-1}\Gamma_1) & -a_1'D^{-1}\Gamma_2 & \dots & \dots & -a_1'D^{-1}\Gamma_n \\
-a_2'D^{-1}\Gamma_1 & (1 - a_2'D^{-1}\Gamma_2) & \dots & \dots & -a_2'D^{-1}\Gamma_n \\
\vdots & \vdots & \ddots & \vdots & \vdots \\
\vdots & \vdots & \vdots & \ddots & \vdots \\
-a_n'D^{-1}\Gamma_1 & -a_n'D^{-1}\Gamma_2 & & & (1 - a_n'D^{-1}\Gamma_n)
\end{bmatrix}^{-1}
\begin{bmatrix}
a_1'w^C \\
a_2'w^C \\
\vdots \\
\vdots \\
a_n'w^C
\end{bmatrix}
= A^{-1}b
$$

provided that the matrix on the right-hand side is invertible, where $A = I - aD^{-1}\Gamma$ .

**Proposition 3.** *(Multifactor Correction Constants)* If an institution is short sale constrained, then given unique risk factors $\Gamma_1, ..., \Gamma_n$ , idiosyncratic volatility matrix $D$ , and knowledge of $\tilde{\beta}$ , the belief parameters $\beta_k$ are generically recoverable via $\beta_k = \kappa_k + \tilde{\beta}_k$ where the vector of $\kappa$ values is

$$
\begin{bmatrix}
\kappa_1 \\
\kappa_2 \\
\vdots \\
\vdots \\
\kappa_n
\end{bmatrix}
=
\begin{bmatrix}
(1 - a_1'D^{-1}\Gamma_1) & -a_1'D^{-1}\Gamma_2 & \dots & \dots & -a_1'D^{-1}\Gamma_n \\
-a_2'D^{-1}\Gamma_1 & (1 - a_2'D^{-1}\Gamma_2) & \dots & \dots & -a_2'D^{-1}\Gamma_n \\
\vdots & \vdots & \ddots & \vdots & \vdots \\
\vdots & \vdots & \vdots & \ddots & \vdots \\
-a_n'D^{-1}\Gamma_1 & -a_n'D^{-1}\Gamma_2 & \dots & \dots & (1 - a_n'D^{-1}\Gamma_n)
\end{bmatrix}^{-1}
\begin{bmatrix}
a_1'w^C \\
a_2'w^C \\
\vdots \\
\vdots \\
a_n'w^C
\end{bmatrix}.
$$

## D Recovery and Identification of Demand Parameters versus Belief Parameters

If an institution is short sale constrained and the econometrician is aware of this fact, then we can use the formulas derived above to compute $\kappa^C = \Gamma'w^C$ and thus recover $\beta_1 = \Gamma'w + \tilde{\beta}_1$ in the single common risk factor case (see Proposition 3 above for the multi-factor case). When an institution has short positions, however, we can still estimate $\tilde{\beta}_1 = \beta_1 - \kappa$ but $\kappa$ is an unrecoverable scalar function of all return beliefs, volatility, and Lagrange multipliers, and thus $\beta_1$ is unidentifiable without substantial and unconventional identifying assumptions.

Identifying the constant term $\beta_K$ , on the other hand, is not feasible given that (1) we do not know the leverage restrictions faced by the various institutions and (2) for unconstrained institutions, where the shadow value of relaxing the leverage constraint is also a function of beliefs about stocks held short, many idiosyncratic beliefs are again only set identified. In essence, we cannot distinguish between an institution that has a dim view of the stock market and one that has a rosier view but must refrain from desired purchases due to severe constraints on leverage, as only the sum of these two forces is identified without information like the specific leverage level.

The decomposition of portfolio weights raises an important limitation of demand estimation in this context, namely the fact that belief-based contributions to portfolio weights are collinear with several of the risk-based contributions to portfolio weights. The belief parameter $\beta_1$ , for example, which is to say the coefficient on the common risk factor $\Gamma$ , is not the coefficient in the regression

60

---

# Page 62

specification. Instead, we are left to estimate $\tilde{\beta}_1 = \beta_1 - \kappa$ but $\kappa$ is unknown and is a complicated function of all return beliefs, volatility, and Lagrange multipliers.

Although recovery of $\tilde{\beta}_1$ suffices for this paper’s study of hidden beliefs, we might wish to estimate $\beta_1$ . $\beta_1$ can still be recovered if we know that an institution is short sale constrained. Recall that the censoring problem is actually a double censoring problem: short sale constrained institutions cannot sell short and therefore none of the data is censored even though the optimization problem’s solution has a functional form similar to that of censored data. With unconstrained institutions we face a graver issue: observing a zero holding can mean a portfolio weight anywhere from $(-\infty, 0]$ , and as a result the data censoring destroys important information necessary to identify $\beta_1$ : the shrinkage constant $\kappa^U$ is a function of $\mu$ , but because many of the $\epsilon$ vector components are only set identified, we cannot recover $\kappa^U$ with beliefs $\mu$ that are themselves unrecoverable. On the other hand, if the institution is short sale constrained then we can use the formulas derived above to compute $\kappa^C = \Gamma' w^C$ and thus recover $\beta_1 = \Gamma' w + \tilde{\beta}_1$ because while $\mu$ is still not identified, $\mu + \lambda$ is.

On a practical level, use of 13F filing data always requires assumptions regarding outside assets and leverage, as only certain types of securities are required to be disclosed, and cash positions are not included. For all of these reasons, this paper adopts a conservative approach in its empirical analysis, clearly delineating when an additional assumption is required to identify a parameter (e.g. assuming the existence of short sale constraints to identify $\beta_1$ ) and avoiding analyses that require poorly supported assumptions.

One form of analysis that is of interest to the asset pricing literature but cannot be conducted without strong assumptions is counterfactual analysis, particularly with respect to idiosyncratic beliefs. These beliefs are a critical component of counterfactual analysis. In the model and analysis of Kojien and Yogo (2019), for instance, the idiosyncratic belief parameters $\epsilon$ are responsible for over 80% of stock market volatility versus a mere 4.7% attributable to changes in preferences for characteristics. Yet this paper’s model shows that the vast majority of components of a typical $\epsilon$ vector are only set identified: we can establish a bound on hidden beliefs but certainly cannot recover precise beliefs about stocks that are not held. Moreover, we lack knowledge of how the parameter $\kappa^U$ will shift and cannot establish counterfactual shadow values $\eta^*$ for relaxing the leverage constraints after preferences change. Local comparative statics are possible, but traditional IO counterfactual scenarios are non-local, merger analysis being one prominent such example.

In summary, while demand estimation enables recovery of institutional preferences for characteristics and bounds on hidden beliefs, it does not permit traditional counterfactual analysis. While this assertion may appear absurd in light of decades of significant progress on precisely such analysis within the IO literature, I want to underscore the two critical differences versus the traditional models of new empirical IO. First, IO models rarely take censored data as inputs and frequently make discrete choice assumptions that allow for censoring issues to implicitly vanish. Second, and more importantly, IO models generally view the demand side as a continuum of atomistic consumers whose idiosyncratic preferences take values drawn from a distribution. By

61

---

# Page 63

contrast, the finance literature has repeatedly established over decades of microstructure and asset pricing research, both theoretically and empirically, that individual institutions’ beliefs can impact prices. Institutions are non-atomistic and follow a Zipf’s law in size (see Gabaix, Gopikrishnan, Plerou and Stanley (2006)), making each institution’s beliefs vital to counterfactual analysis. Yet as I have already shown, censoring completely alters our knowledge of institutional beliefs. We can work around this problem by for instance assuming that stocks that are not held will never be held, but such assumptions have significant economic content and do not have a clear microfoundation. Innovating around these limitations is a significant topic for future research.

## E SCQR and Alternate Approaches to Censored Regression and Confidence Sets

SCQR can be understood as a form of iterated subsample selection, where we are invoking continuity on quantile regressions with respect to $\tau$ to select only observations $i$ such that $z_i'\hat{\beta} > 0$ because, as shown in Newey (2001), $\mathbb{E}^*(m(\epsilon)|z) = 0 \implies \mathbb{E}(1(z'\beta > 0)m(\epsilon)|z) = 0$ where $\mathbb{E}^*$ is the expectation operator with respect to the latent variables $y^*$ and $\mathbb{E}$ is the expectation operator with respect to the censored data $y$ . Convergence of the SCQR method is not guaranteed because if the sets $J_0$ or $J_1$ become empty at any stage, SCQR fails to converge. In the remainder of this appendix, I explore alternatives to SCQR, illustrating the multi-way trade-offs among computational tractability, distributional assumptions for unobservables, and treatment of endogeneity. $^{36}$

### CQIV, Khan and Tamer (2009), and Blundell and Powell (2007)

The Censored Quantile IV (CQIV) approach of Chernozhukov, Fernández-Val and Kowalski (2015) is one valid alternative approach that allows for arbitrary endogeneity as opposed to the linear functional form assumed in this paper. Like SCQR it involves subsample selection to approximate the approach of Powell (1986), but the subsample selection is dependent on a link function and various transformations of the data that seek to capture the probability of the data being censored given observables. The disadvantage of CQIV, despite the fact that it is implemented by the authors in STATA, is that it is computationally challenging when applied at scale because the appropriate choice of probability model might vary from problem to problem, leaving tuning parameters that prove important for obtaining accurate results.

Another approach to such problems is the endogenous censored regression estimation of Khan and Tamer (2009), an elegant method that allows for endogeneity as well as random censoring. Khan and Tamer (2009) use the median zero restriction to generate unconditional moment inequalities, deriving a minimum distance-type consistent estimator based on these inequalities. Unfortunately,

---

$^{36}$ This subsection is not a comprehensive survey, as the literature on censored quantile regression is vast and growing. Economic applications require challenging decisions about the optimal approach when the researcher faces small sample sizes, multidimensional data, or finite computational resources.

62

---

# Page 64

when the number of observations is large and the censoring problem extreme, as is the case in this paper and many other settings, computation of the estimator becomes intractable, as it involves a high dimensional grid search with each point on the grid requiring billions of computations. $^{37}$ Future advances in computing will likely render this inequality-based minimum distance estimator an attractive alternative given the lack of tuning parameters.

Many other estimators for censored regressions have been proposed over the years, with the main distinguishing features being the required assumptions on the data generating process as well as the computational complexity. The “Tobit” with its normally distributed errors is a classic example of a model with very strong distributional assumptions, while other models such as Blundell and Powell (2007) allow for far less stringent conditions and account for the endogeneity of one or multiple regressors. The necessity of avoiding both symmetry assumptions and nonparametric estimation of control functions and densities led to this paper’s approach, which combines SCQR with a functional form assumption on the unobservables with respect to the control variable.

### Estimation via CLAD with Mixed Integer Programming

In Appendix F I discuss how to use the mixed integer programming-based estimation technique of Bilias, Florios and Skouras (2019) to compute an alternative estimator when SCQR fails to converge. The approach of Bilias, Florios and Skouras (2019) transforms the CLAD estimator of Powell (1984) into a mixed integer programming problem. Unfortunately, when facing heavy censoring with large consideration sets, the estimator can require days or weeks to compute accurately for a single institution. Moreover, when the SCQR method fails to converge we should strongly suspect that the subset $\{i : x_i'\beta > 0\}$ might be close to null, in which case estimation is infeasible.

### Confidence Sets for This Paper’s Estimates

In Appendix F I also provide an alternative Markov Chain Monte Carlo-based methodology for computing demand estimates that generates confidence sets for individual institutions’ demand parameters, with these sets robust to weak instruments and partial identification. Computation of such individual confidence sets is beyond the scope of this paper given its irrelevance to the main empirical objects of interest, the HBI and OBI, but the methodology is provided for completeness as future research that adopts this paper’s approach might be interested in specific institutions’ confidence sets. $^{38}$

### Conditional Median Zero Restriction vs Mean Zero Restriction

Most economics and finance applications of GMM use a conditional mean zero restriction, not a conditional quantile restriction; as a result, I conclude this appendix with a brief explanation of the similarities and

---

$^{37}$ As noted by Khan and Tamer (2009), the objective function features a third order U-statistic and so when $n$ is large, we have $\mathcal{O}(n^3)$ computations at each point. They propose a split sample approach, but for problems with heavy censoring the loss of efficiency renders such an approach infeasible.

$^{38}$ Computation of such a set in isolation is tractable, but computation of hundreds of thousands of such sets would take millions or tens of millions of CPU hours.

63

---

# Page 65

differences between the approaches. Here we require that the median of the unobservables not shift as we vary the value of the instruments $Z$ , whereas a mean zero restriction accomplishes the same but for the average of the unobservables. If we make the additional assumption that the unobservables have a symmetric distribution conditional on $Z$ , then the two restrictions are the same.

But when we compute an estimator for a (often misspecified) linear model, we are interested in how the various observations contribute to the estimator. With OLS, that contribution is clear, with the estimate $\hat{\beta}$ just being the one that minimizes the mean-squared error (MSE). Angrist, Chernozhukov and Fernández-Val (2006) show that both quantile regression and OLS minimize a mean-squared error loss function, but with quantile regressions using importance weights that magnify the MSE integrand proportionately to the density of $Y|X$ near the $\tau$ th quantile of $Y|X$ . In plain words, this paper’s empirical approach minimizes MSE just like OLS but with upweighting of points $X$ where the $Y$ variable congregates near its conditional median $\text{med}(Y|X)$ while downweighting points $X$ such that the density of $Y$ is thin near the conditional median. The main takeaway from this discussion of MSE and moment conditions is that while the quantile regression approach is rarely used in financial economics versus mean restrictions, it both (1) is an equally valid approach in general and (2) is absolutely vital to studying the economic question.

## F Estimation: Confidence Sets and MIP-based CLAD Estimation

### F.1 Confidence Sets for Agent Demand Parameters

The empirical objective of this paper is to extract institutional beliefs and study whether agents rationally infer the beliefs of other agents when presented with holdings data. This empirical problem does not require a confidence set for a particular manager’s demand coefficients, though future research might require such sets, particularly if the research focuses on a small group of managers as opposed to the estimation of hundreds of thousands of sets of parameters, as in this paper’s setting. The asymptotic distribution of the CLAD estimator of Powell (1984) is challenging to compute because it requires the nonparametric estimation of the conditional density of $u$ at zero. Chen (2018) recommends using a multiplier bootstrap to compute confidence intervals with SCQR, which involves resampling a series of $n$ i.i.d. draws of $\xi$ , a variable such that $\xi > 0$ and $\mathbb{E}\xi = \text{Var}(\xi) = 1$ , and solving the last stage median regression (equation (12)) over the subset $\left\{i : z_i'\hat{\beta}(0.5) > 0\right\}$ with weight $\xi_{mj}$ applied to $\rho_{0.5}\left(y_j - z_j'\hat{\beta}\right)$ .

An alternative approach to both estimation and confidence set computation that is tractable, robust to weak identification, and partially robust to misspecification of the relationship between the control variable and instrument is now given. I do not use this method because it is only computationally feasible when the data has a sufficient number of positive observations and the degree of censoring is moderate (e.g. 60% of observations are censored as opposed to 95%), but it

64

---

# Page 66

has multiple attractive properties for future users of this methodology who apply the approach to different contexts.

The first step is to split the data randomly into two different subsamples, $ S_1 $ and $ S_2 $ . We compute the respective SCQR estimators $ \hat{\beta}_1 $ and $ \hat{\beta}_2 $ as in subsection 3.3, then use each of these SCQR estimators to select subsamples $ J^1 = \left\{ i \in S_1 : z_i' \hat{\beta}_2 > 0 \right\} $ and $ J^2 = \left\{ i \in S_2 : z_i' \hat{\beta}_1 > 0 \right\} $ , which take the place of the infeasible oracle subsamples. We now can use the median zero condition $ \mathbb{E} \left[ m \left( u \left( j \right) \right) | X \left( j \right), v \left( j \right) \right] = 0 $ where $ m \left( u \right) = 1 \left( u < 0 \right) - 0.5 $ to form unconditional moments and subsequently a continuously updated GMM criterion function. With this function in hand, we can use the Markov Chain Monte Carlo approach of Chen, Christensen and Tamer (2018) for both subsamples to compute confidence sets. These sets are robust to weak or partial identification and do not require tuning parameter adjustment, and both can be reported. $^{39}$

## F.2 Estimation via Bilias, Florios and Skouras (2019)

The original estimation method for censored median regression is the CLAD method of Powell (1984), where the estimator, based on a conditional median zero restriction for the error terms, is given by

$$
\beta = \arg \min_{\hat{\beta} \in B} \sum_j |y_j - \max \left\{ 0, z_j' \hat{\beta} \right\}|.
$$

This elegant estimator, while appealing in theory, has long proven challenging in empirical work because whereas LAD estimation is solved via straightforward linear programming, the CLAD objective function is highly non-convex. Empirical applications of CLAD often use numerical methods that resort to approximate optimization, which unfortunately can provide solutions far from the true CLAD estimator. Estimation in this paper uses the SCQR method for precisely these reasons. However, the recent innovations of Bilias, Florios and Skouras (2019) allow for precise CLAD estimation by recasting it as a mixed integer programming (MIP) problem. Usage of this approach as a default method, however, is infeasible because of the large sample sizes and number of estimates required; MIP becomes computationally burdensome for certain data sets due to time limitations when sample sizes are large and the number of required estimations is, as in this paper, in the hundreds of thousands.

# G Alternative Characteristics: Asness, Moskowitz and Pedersen (2013)

I use the 2-12 momentum characteristic of Asness, Moskowitz and Pedersen (2013) along with log price, log book equity, six month beta, a constant, and the control variable and repeat the estimations of the main text. Tables 9 and 10 provide summary statistics for this analysis.

Remark 6. (Exogeneity of Characteristics) I treat book value, the “12-2 month momentum” variable

[^1]: $^{39}$ Special thanks to Xiaohong Chen for suggesting a split-sample approach.

---

# Page 67

Table 9: Institutional Demand Estimation Summary Statistics

<table>
  <thead>
    <tr>
      <th></th>
      <th>Num Inst</th>
      <th>Tot Inst AUM</th>
      <th>Rigid AUM</th>
      <th>Dynamic AUM</th>
      <th>AUM SCQR</th>
      <th>AUM Low</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1984-1988</td>
      <td>793</td>
      <td> $525B</td>
      <td>$ 17B</td>
      <td> $508B</td>
      <td>$ 317B</td>
      <td> $9B</td>
    </tr>
    <tr>
      <td>1989-1992</td>
      <td>958</td>
      <td>$ 867B</td>
      <td> $74B</td>
      <td>$ 793B</td>
      <td> $495B</td>
      <td>$ 16B</td>
    </tr>
    <tr>
      <td>1993-1996</td>
      <td>1156</td>
      <td> $1666B</td>
      <td>$ 118B</td>
      <td> $1549B</td>
      <td>$ 1133B</td>
      <td> $22B</td>
    </tr>
    <tr>
      <td>1997-2000</td>
      <td>1540</td>
      <td>$ 4363B</td>
      <td> $248B</td>
      <td>$ 4115B</td>
      <td> $3316B</td>
      <td>$ 42B</td>
    </tr>
    <tr>
      <td>2001-2004</td>
      <td>1921</td>
      <td> $5227B</td>
      <td>$ 542B</td>
      <td> $4686B</td>
      <td>$ 3903B</td>
      <td> $59B</td>
    </tr>
    <tr>
      <td>2005-2008</td>
      <td>2574</td>
      <td>$ 7774B</td>
      <td> $1650B</td>
      <td>$ 6124B</td>
      <td> $4753B</td>
      <td>$ 106B</td>
    </tr>
    <tr>
      <td>2009-2012</td>
      <td>2915</td>
      <td> $7974B</td>
      <td>$ 1732B</td>
      <td> $6242B</td>
      <td>$ 5065B</td>
      <td> $181B</td>
    </tr>
    <tr>
      <td>2013-2016</td>
      <td>3733</td>
      <td>$ 14000B</td>
      <td> $5111B</td>
      <td>$ 8888B</td>
      <td> $7198B</td>
      <td>$ 374B</td>
    </tr>
    <tr>
      <td>2017-2020</td>
      <td>4752</td>
      <td> $20587B</td>
      <td>$ 8399B</td>
      <td> $12188B</td>
      <td>$ 10283B</td>
      <td> $549B</td>
    </tr>
    <tr>
      <td>2021</td>
      <td>5970</td>
      <td>$ 31962B</td>
      <td> $14298B</td>
      <td>$ 17664B</td>
      <td> $14652B</td>
      <td>$ 986B</td>
    </tr>
  </tbody>
</table>

**Note**: Table 9 contains summary statistics for the demand estimation, including number of institutions, total institutional AUM, the AUM of rigid institutions, the AUM of dynamic institutions, AUM of institutions for which the SCQR estimation converges, and the AUM of dynamic institutions with less than twenty-five holdings (“AUM Low”). Each variable is averaged over all quarters within the designated four-year window or, in the case of 2021, one-year window. The twenty-five-asset cutoff is used for generation of summary statistics because twenty-five is the cutoff used in the decision of whether to conduct estimation of a dynamic institution. The alternate characteristics based on the four-factor model are used.

of Asness, Moskowitz and Pedersen (2013), and beta as exogenous in the sense that $x_{k,t} \perp u_{i,t}, \forall i,t$ , $k = 1,2,3$ . Lagged book value is a publicly available accounting variable, and the identifying assumption merely requires that private return beliefs $u_{i,t}(n)$ have median zero conditional on $\log(BE(n))$ . Beta similarly is publicly observable and institution $i$ ’s current private beliefs about future idiosyncratic returns are plausibly median independent of past covariance with the market. Momentum is the variable that poses a modest threat to identification in that fluctuations in private beliefs of institutions, which themselves might be highly correlated, can cause momentum. Momentum is thus a function of many institutions’ $\Delta u_{i,t}$ but not a direct function of its level. Finally, I note that the momentum variable excludes the most recent month’s returns and therefore is not a function of the current log price which is itself already accounted for by the control variable. Future work that devises an instrument for momentum would prove useful in empirical analysis for research that focuses on the levels of the estimated characteristics, but to the best of my knowledge such an instrument has yet to be devised.

## H Simulation Results: Recovering Demand Parameters

This section conducts a large-scale simulation using CRSP data, Compustat data, control variables, and consideration set data from 2021Q4 but randomly drawn institutional demand parameters. Starting from mean-variance preferences and constructing portfolios by standard numerical optimization given beliefs about returns and covariance, I demonstrate that the model reliably recovers each institution’s demand parameters despite heavy censoring. The simulation

66

---

# Page 68

Table 10: Institutional Demand Estimation Consideration Sets and Holdings

<table>
  <thead>
    <tr>
      <th></th>
      <th>Avg Pos Hold</th>
      <th>Med Pos Hold</th>
      <th>Med CS Size</th>
      <th>5th Prctl CS Size</th>
      <th>95th Prctl CS Size</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1984-1988</td>
      <td>117</td>
      <td>68</td>
      <td>1346</td>
      <td>362</td>
      <td>3180</td>
    </tr>
    <tr>
      <td>1989-1992</td>
      <td>136</td>
      <td>69</td>
      <td>1454</td>
      <td>384</td>
      <td>3402</td>
    </tr>
    <tr>
      <td>1993-1996</td>
      <td>157</td>
      <td>69</td>
      <td>2082</td>
      <td>637</td>
      <td>4582</td>
    </tr>
    <tr>
      <td>1997-2000</td>
      <td>176</td>
      <td>72</td>
      <td>2356</td>
      <td>705</td>
      <td>5198</td>
    </tr>
    <tr>
      <td>2001-2004</td>
      <td>186</td>
      <td>70</td>
      <td>2181</td>
      <td>775</td>
      <td>4322</td>
    </tr>
    <tr>
      <td>2005-2008</td>
      <td>181</td>
      <td>68</td>
      <td>1902</td>
      <td>583</td>
      <td>3839</td>
    </tr>
    <tr>
      <td>2009-2012</td>
      <td>179</td>
      <td>69</td>
      <td>1643</td>
      <td>486</td>
      <td>3356</td>
    </tr>
    <tr>
      <td>2013-2016</td>
      <td>192</td>
      <td>76</td>
      <td>1554</td>
      <td>427</td>
      <td>3077</td>
    </tr>
    <tr>
      <td>2017-2020</td>
      <td>199</td>
      <td>78</td>
      <td>1625</td>
      <td>440</td>
      <td>2975</td>
    </tr>
    <tr>
      <td>2021</td>
      <td>197</td>
      <td>80</td>
      <td>1765</td>
      <td>488</td>
      <td>3070</td>
    </tr>
  </tbody>
</table>

**Note**: Table 10 contains summary statistics on the consideration sets of institutional investors. The censoring issue is illustrated by the ratio of positive holdings to consideration set size, with an order of magnitude difference in median sizes. The alternate characteristics based on the four-factor model are used.

results starkly illustrate the importance of correcting estimated coefficients by the $\kappa$ constant of Section 2 when belief parameters are desired as opposed to the linear reduced form. Furthermore, the results show how the interpretation of constrained and unconstrained institutions’ estimates must differ in precisely the way illustrated by the model, despite the fact that hidden beliefs can be studied for both with the same methodology.

## H.1 Drawing Beliefs, Consideration Sets, and Constraints

I start by randomly selecting 3,142 institutional consideration sets from the collection of derived dynamic institutional consideration sets, then I draw belief parameter vectors $\beta$ such that $\beta_k \in \left[-(5 \times 10^{-6})\sigma_k^{-1}, (5 \times 10^{-6})\sigma_k^{-1}\right]$ for each $k \in \{0, 1, ..., 5\}$ where $\sigma_k$ is the standard deviation of characteristic $k$ in the data except $\sigma_5 \equiv 1$ for the constant term. I also draw i.i.d. random idiosyncratic preferences $\epsilon$ for each institution and each asset from the interval $[-2.5 \times 10^{-7}, 2.5 \times 10^{-7}]$ . I use the six variable “alternative” characteristic analysis based on Asness, Moskowitz and Pedersen (2013) to keep the simulation simple. The covariance matrix is defined as $\Sigma = \Gamma\Gamma' + D$ where $D$ is the idiosyncratic variance of assets and $\Gamma = \sigma_M B$ where $B$ is the vector of market betas and $\sigma_M$ is the standard deviation of daily stock market returns. This covariance matrix corresponds to a single common risk factor model of the form covered in subsection 2.2. I also randomly select whether each institution is short sale constrained, with a 20% probability of being unconstrained and an 80% probability of being constrained. All institutions are subject to leverage constraints, with short sale constrained institutions restricted precisely to a leverage level of 1 and unconstrained required to be between $-1$ and $1$ .

67

---

# Page 69

## H.2 Optimization and Estimation

All institutions conduct mean-variance optimization with risk aversion parameter $\gamma = 1$ using covariance matrix $\Sigma$ and belief vector $\mu = X\beta + \epsilon$ for characteristic matrix $X$ subject to the institution-specific constraints and consideration set. I collect the results as weight vectors $w_i^*$ for each institution $i$ , then I censor all of the data via $w_i = \max\{0, w_i^*\}$ .

Using only the idiosyncratic volatility matrix $D$ , censored portfolio data $w_i$ , consideration sets $H_i$ , and characteristics $X$ , I estimate $\beta_i$ for each institution via the methodology of Section 3. Figure 4 plots the results visually, with the simulated coefficients on the x-axes versus the estimated coefficients on the y-axes. For all characteristics except for beta and the constant term, the parameters are recovered almost precisely, tracing out a near $45^\circ$ line. As noted in Section 3, the estimated $\tilde{\beta}_3$ term that captures demand for market beta should not correspond to the simulated belief parameter $\beta_3$ . Instead, we must first map the coefficient on beta ( $B$ ) to a coefficient on $\Gamma = \sigma_M B$ , the common risk factor. The correction term for constrained institutions is then $\kappa^C = \Gamma'w$ as previously discussed, whereas for unconstrained institutions the correction term is $\kappa^U = \Gamma'w^*$ , where $w^*$ is unfortunately lost to censoring.

In Figure 5 I show that the correction constants work precisely as predicted. Figure 5a plots the estimated $\beta_3$ against the true simulation value for constrained institutions, with the correction constant mapping to the belief parameter as in the model derivations. When the same correction is applied to unconstrained institutions, however, Figure 5b shows that we fail to recover the underlying belief parameter, which is not identified. Figure 5c plots the estimated coefficients corrected using $\kappa^U = \Gamma'w^*$ if we knew this constant term but did not know the weight vector. As expected, it recovers the underlying belief parameter with minimal error. Meanwhile, the constant belief term, plotted in Figure 4f, is not recovered, again just as the model predicts, because we are actually estimating a combination of the constant belief parameter $\beta_6$ with the shadow value of relaxing the leverage constraints. These simulation results provide a strong numerical illustration of the power of this paper’s modeling approach and estimation methodology while simultaneously underscoring the limitations of interpreting the beta coefficient and constant coefficient. In a multi-factor model, these limitations will extend to all risk-relevant characteristics.

In Appendix I I show that other standard approaches, including the estimation routine of Kojien and Yogo (2019), do not consistently recover the demand coefficients that the SCQR-based method recovers. I run an alternate simulation with heteroskedasticity and larger error terms, showing that even restriction to the set of uncensored data does not permit accurate recovery via linear GMM, with SCQR providing consistent and unbiased recovery. If the dispersion of private return beliefs varies strongly with observable characteristics such as momentum or book to market ratio, then the “errors” are heteroskedastic and properly adjusting for censoring becomes more critical.

---

# Page 70

<div style="display: flex; flex-wrap: wrap; justify-content: space-between;">

<div style="width: 48%; margin-bottom: 20px;">
    ![image](image_1.png)
    <p style="text-align: center;">(a) Log Mkt Equity</p>
</div>

<div style="width: 48%; margin-bottom: 20px;">
    ![image](image_2.png)
    <p style="text-align: center;">(b) Value</p>
</div>

<div style="width: 48%; margin-bottom: 20px;">
    ![image](image_3.png)
    <p style="text-align: center;">(c) Momentum</p>
</div>

<div style="width: 48%; margin-bottom: 20px;">
    ![image](image_4.png)
    <p style="text-align: center;">(d) Beta</p>
</div>

<div style="width: 48%; margin-bottom: 20px;">
    ![image](image_5.png)
    <p style="text-align: center;">(e) Control Variable</p>
</div>

<div style="width: 48%; margin-bottom: 20px;">
    ![image](image_6.png)
    <p style="text-align: center;">(f) Constant</p>
</div>

</div>

**Figure 4: Simulation Results: True Coefficients vs SCQR Estimates**

**Note:** This figure scatterplots the true simulation coefficients (x-axis) versus the coefficients estimated via this paper’s methodology (y-axis) for the institutions where the SCQR converges to a solution. The coefficient on beta (4d) is uncorrected for the risk component $\kappa$ - see Figure 5.

69

---

# Page 71

![image](image_1.png)

Figure 5: Coefficients on Gamma ( $\sigma_M^{-1}$ times Beta Coefficients)

**Note**: This figure scatterplots the true simulation $\Gamma = \sigma_M Beta$ coefficients (x-axis) versus the coefficients estimated via this paper’s methodology (y-axis) for the institutions where the SCQR converges to a solution. In subfigure (5a) I use the analytic formula from this paper’s model to compute $\kappa^C = \Gamma'w$ for short sale constraints, with the corrected estimated coefficients matching the demand parameters almost precisely, just as the theory predicts. In subfigure (5b) I use the same formula applied to unconstrained institutions and show that without knowledge of the censored data we cannot recover the true value. Subfigure 5c plots what we could have obtained if we were given the $\kappa^U$ value as given in Section 2. Again, as predicted by the theory, this would enable precise recovery of the belief parameters.

70

---

# Page 72

# I Asset Demand Estimation Simulation

This section conducts a large-scale simulation using CRSP data, Compustat data, control variables, and consideration set data from 2021Q4 but randomly drawn institutional demand parameters. Starting from mean-variance preferences and constructing portfolios by standard numerical optimization given beliefs about returns and covariance, I demonstrate that this paper’s estimation procedure reliably recovers each institution’s demand parameters despite heavy censoring, whereas other methodologies do not.

## I.1 Drawing Beliefs, Consideration Sets, and Constraints

I start by randomly selecting 3,142 institutional consideration sets from the collection of derived dynamic institutional consideration sets, then I draw belief parameter vectors $\beta$ such that the coefficient on market beta is $\beta_{3,i} = 0.01 + u_3 10^{-5}$ where $u_3 \sim U[-0.5, 0.5]$ , i.i.d. across institutions $i$ . The coefficient on book value is drawn as $\beta_{1,i} = 8 \times 10^{-5} u_1$ where $u_1 \sim U[-0.5, 0.5]$ and all other coefficients are independently drawn as $\beta_{k,i} = 2 \times 10^{-5} u_k$ where $u_k \sim U[-0.5, 0.5]$ . I normalize the data so that the standard deviation of each characteristic $k$ in the dataset is one, excepting the constant term. I use the six variable “alternative” characteristic analysis based on Asness, Moskowitz and Pedersen (2013) to keep the simulation simple; market beta is winsorized at the 5th and 95th percentiles. The covariance matrix is defined as $\Sigma = \Gamma \Gamma' + D$ where $D$ is the idiosyncratic variance of assets and $\Gamma = \sigma_M B$ where $B$ is the vector of market betas and $\sigma_M$ is the standard deviation of daily stock market log returns. This covariance matrix corresponds to a single common risk factor model of the form covered in subsection 2.2. I also randomly select whether each institution is short sale constrained, with a 20% probability of being unconstrained and an 80% probability of being constrained. All institutions are subject to leverage constraints, with short sale constrained institutions restricted precisely to a leverage level of 1 and unconstrained required to be between $-1$ and $1$ .

Meanwhile, the idiosyncratic preference of institution $i$ for asset $n$ with normalized log book value $x_n(2)$ is drawn as

$$
\epsilon_{i,n} = X_{i,n} \times 6 \times 10^{-6} \times (x_n(2))^2
$$

where $X_{i,n}$ is a Rademacher random variable. As is readily apparent from the construction, $\mathbb{E}[\epsilon_{i,n}|X] = 0$ and $\mathbb{E}[m(\epsilon_{i,n})|X] = 0$ because of the Rademacher term’s symmetry. Both types of moment condition are thus satisfied in the uncensored data, with both median and mean zero moment conditions appropriate in the full uncensored dataset.

I now restrict the focus to institutions that satisfy the “large holding set” criterion of Kojien and Yogo (2019), namely that the institution have at least 1000 positive holdings. This leaves only unconstrained institutions (328 of them, specifically) because of the simulation parameterization, so the censoring problem for these large institutions is in fact a data censoring issue, equivalent to 13F filings for hedge funds, as opposed to the implicit censoring of short sale constraints.

71

---

# Page 73

## I.2 Optimization and SCQR Estimation

All institutions conduct mean-variance optimization with risk aversion parameter $\gamma = 1$ using covariance matrix $\Sigma$ and belief vector $\mu = X\beta + \epsilon$ for characteristic matrix $X$ subject to the institution-specific constraints and consideration set. I collect the results as weight vectors $w_i^*$ for each institution $i$ , then I censor all of the data via $w_i = \max\{0, w_i^*\}$ .

Using only the idiosyncratic volatility matrix $D$ , censored portfolio data $w_i$ , consideration sets $H_i$ , and characteristics $X$ , I estimate $\beta_i$ for each institution via the methodology of Section 3. Figure 6 plots the results visually, with the simulated coefficients on the x-axes versus the estimated coefficients on the y-axes. For all characteristics except for beta and the constant term, the parameters are recovered almost precisely, tracing out a near $45^\circ$ line.

## I.3 Estimation via Kojien and Yogo (2019)

To illustrate this paper’s contribution to the existing asset demand literature, I rerun the simulation exercise but use the nonlinear GMM method of Kojien and Yogo (2019) for estimation. Their identifying restriction can be mimicked in this paper’s control function approach as $\mathbb{E}[\epsilon|X] = 1$ , where $X$ is as in the previous subsection, and $\epsilon$ is such that

$$
w_n = \exp\left\{x_n'\beta\right\} \epsilon_n
\quad \text{(32)}
$$

where I have removed the outside asset of Kojien and Yogo (2019) from the equation because this setting does not have outside assets.

I construct simple unconditional moment conditions $\mathbb{E}\left[x_j'w_j \exp\left\{-x_j'\beta\right\} - 1\right] = 0$ and apply standard two-step GMM, first constructing an efficient weight matrix by preliminary estimation via an identity weight matrix, then using the efficient weight matrix to conduct nonlinear GMM via numerical optimization over the sandwich criterion. The resulting estimates are plotted against the true simulation values in Figure 7. The estimation procedure delivers markedly weaker results than the SCQR-based method with frequently extreme error terms and limited correlation to the true parameters. The reasons for this difference are multiple, with the most prominent difference being that this paper’s methodology controls for censoring. Accounting for idiosyncratic volatility and the linear functional form matter, but not nearly as much, as shown in the subsequent subsections where I run analyses using a linear model but a mean zero restriction as well as the method of Kojien and Yogo (2019) but accounting for idiosyncratic volatility, and none of these methods yield comparable results to this paper’s SCQR-based method. If we wish to obtain bounds on hidden beliefs or study the cross section of beliefs about returns to characteristics, we must use a consistent estimator of $\beta$ and delineate between estimated coefficients that correspond to beliefs and those that do not (the constant term and coefficient on market risk). Despite the estimated institutions having over 1000 positive holdings, the approach of Kojien and Yogo (2019) does not recover accurate estimates because the mean-based moment condition does not hold in heavily censored data.

72

---

# Page 74

Log Mkt Cap

Estimated Coefficient

Simulated Demand Coefficient

(a) Log Mkt Equity

Log Book

Estimated Coefficient

Simulated Demand Coefficient

(b) Value

Momentum

Estimated Coefficient

Simulated Demand Coefficient

(c) Momentum

Beta

Estimated Coefficient

Simulated Demand Coefficient

(d) Beta

Control Variable

Estimated Coefficient

Simulated Demand Coefficient

(e) Control Variable

Constant

Estimated Coefficient

Simulated Demand Coefficient

(f) Constant

Figure 6: Simulation Results: True Coefficients vs SCQR Estimates

Note: This figure scatterplots the true simulation coefficients (x-axis) versus the coefficients estimated via this paper’s methodology (y-axis) for the institutions where the SCQR converges to a solution and the number of positive holdings exceeds 1000.

73

---

# Page 75

Log Mkt Cap

Log Book

(a) Log Mkt Equity

(b) Value

Momentum

Beta

(c) Momentum

(d) Beta

Control Variable

Constant

(e) Control Variable

(f) Constant

Figure 7: Simulation Results: Koijen and Yogo (2019) GMM Method

Note: This figure scatterplots the true simulation coefficients (x-axis) versus the coefficients estimated via the nonlinear GMM method of Koijen and Yogo (2019), but without their parameter restriction on the coefficient on log market equity, as here it is not restricted to be less than 1.

74

---

# Page 76

## I.4 Linear Model, Mean Zero Restriction

I now revisit moment conditions based on mean restrictions and modify the nonlinear GMM approach of Kojien and Yogo (2019) to a simple linear method of moments approach (this is just a numerical optimization version of an OLS estimator). In doing so I eliminate any estimation issues caused by the exponential linear model being misspecified. In the simulation $\mathbb{E}[\epsilon|X] = 0$ , the moment condition, is indeed satisfied, just as the conditional median zero condition is satisfied. As is readily visible from Figure 8, however, this estimation approach yields extraordinarily inaccurate results because the mean zero restriction only holds in the latent data, not the censored data. I have again only estimated parameters for institutions with over 1,000 positive holdings, a helpful restriction when using a moment condition that only holds in latent data, yet this is insufficient to produce accurate results. Figure 8 provides the results.

## I.5 Kojien and Yogo (2019) with Idiosyncratic Volatility Scaling

I rerun the analysis using the nonlinear GMM method of Kojien and Yogo (2019) but with weights rescaled by idiosyncratic variance. Figure 9 provides the results.

## I.6 Linear GMM with Idiosyncratic Volatility Scaling

I rerun the analysis using the linear GMM method from I.4 but with weights rescaled by idiosyncratic variance. Figure 10 provides the results.

## I.7 Linear GMM with Idiosyncratic Volatility Scaling, Positive Holdings Only

I rerun the analysis using the linear GMM method from I.4 but with weights rescaled by idiosyncratic variance and only positive holdings included in the analysis. Figure 11 provides the results.

# J Additional HBI and OBI Results

## J.1 OLS Placebo Test

Table 11 gives the results of the OLS placebo test detailed in subsection 7.4.

## J.2 HBI Quintiles at Different Lags

Table 12 provides quintile portfolio performance at different time lags. In addition to the clear gap between high and low HBI quintile portfolios, an additional pattern emerges: at longer lags, the mean alpha across all quintile portfolios is not zero but rather positive. While this might appear peculiar, it is what we should expect in light of the empirical literature on IPO underperformance: because a stock only has a defined HBI 3 years ago if it was in fact trading three years ago, this analysis implicitly removes all stocks that have had an IPO in the last three years as well

75

---

# Page 77

<div style="display: flex; flex-wrap: wrap; justify-content: space-between;">

<div style="width: 48%; margin-bottom: 20px;">
    ![image](image_1.png)
    <p style="text-align: center;">(a) Log Mkt Equity</p>
</div>

<div style="width: 48%; margin-bottom: 20px;">
    ![image](image_2.png)
    <p style="text-align: center;">(b) Value</p>
</div>

<div style="width: 48%; margin-bottom: 20px;">
    ![image](image_3.png)
    <p style="text-align: center;">(c) Momentum</p>
</div>

<div style="width: 48%; margin-bottom: 20px;">
    ![image](image_4.png)
    <p style="text-align: center;">(d) Beta</p>
</div>

<div style="width: 48%; margin-bottom: 20px;">
    ![image](image_5.png)
    <p style="text-align: center;">(e) Control Variable</p>
</div>

<div style="width: 48%; margin-bottom: 20px;">
    ![image](image_6.png)
    <p style="text-align: center;">(f) Constant</p>
</div>

</div>

**Figure 8: Simulation Results: Linear Method**

**Note:** This figure scatterplots the true simulation coefficients (x-axis) versus the coefficients estimated numerically via linear method of moments (i.e. OLS). The moment condition is a mean zero condition.

76

---

# Page 78

Log Mkt Cap

Estimated Coefficient

Simulated Demand Coefficient

-8 -6 -4 -2 0 2 4 6 8

-10$^{-6}$

(a) Log Mkt Equity

Log Book

Estimated Coefficient

Simulated Demand Coefficient

-3 -2 -1 0 1 2 3

-10$^{-5}$

(b) Value

Momentum

Estimated Coefficient

Simulated Demand Coefficient

-8 -6 -4 -2 0 2 4 6 8

-10$^{-6}$

(c) Momentum

Beta

Estimated Coefficient

Simulated Demand Coefficient

9.996 9.997 9.998 9.999 10 10.001 10.002 10.003 10.004

-10$^{-3}$

(d) Beta

Control Variable

Estimated Coefficient

Simulated Demand Coefficient

-8 -6 -4 -2 0 2 4 6 8

-10$^{-6}$

(e) Control Variable

Constant

Estimated Coefficient

Simulated Demand Coefficient

-8 -6 -4 -2 0 2 4 6 8

-10$^{-5}$

(f) Constant

Figure 9: Simulation Results: Kojien and Yogo (2019) Method, with Vol Scaling

Note: This figure scatterplots the true simulation coefficients (x-axis) versus the coefficients estimated numerically via the nonlinear GMM method of Kojien and Yogo (2019) but with weights rescaled by idiosyncratic variance.

77

---

# Page 79

![image](image_1.png)

Figure 10: Simulation Results: Linear GMM Method, with Vol Scaling

**Note**: This figure scatterplots the true simulation coefficients (x-axis) versus the coefficients estimated numerically via a linear GMM method (OLS) and weights rescaled by idiosyncratic variance. The moment condition is a mean zero condition.

78

---

# Page 80

![image](image_1.png)

Figure 11: Simulation Results: Linear GMM Method, with Vol Scaling, Uncensored Only

**Note**: This figure scatterplots the true simulation coefficients (x-axis) versus the coefficients estimated numerically via a linear GMM method (OLS) and weights rescaled by idiosyncratic variance and only uncensored data included (positive $y$ value). The moment condition is a mean zero condition.

79

---

# Page 81

Table 11: HBI Long Short Strategy Results: OLS Placebo

<table>
  <thead>
    <tr>
      <th></th>
      <th>Annualized Alpha</th>
      <th>MKT</th>
      <th>SMB</th>
      <th>HML</th>
      <th>UMD</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>0.67% (0.59)</td>
      <td>-0.05 (-4.09)</td>
      <td>0.35 (14.66)</td>
      <td>-0.16 (-7.67)</td>
      <td>0.07 (3.5)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>-2.58% (-1.43)</td>
      <td>-0.2 (-11.07)</td>
      <td>0.03 (0.73)</td>
      <td>-0.01 (-0.2)</td>
      <td>0.18 (5.21)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>-1.33% (-0.63)</td>
      <td>-0.27 (-12.2)</td>
      <td>-0.13 (-3.42)</td>
      <td>0.38 (9.87)</td>
      <td>0.23 (6.05)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>-0.18% (-0.08)</td>
      <td>-0.26 (-12.57)</td>
      <td>-0.22 (-6.4)</td>
      <td>0.51 (16.07)</td>
      <td>0.14 (4.49)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>0.71% (0.31)</td>
      <td>-0.25 (-14.75)</td>
      <td>-0.24 (-6.58)</td>
      <td>0.54 (19.11)</td>
      <td>0.07 (2.45)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>-2.81% (-1.24)</td>
      <td>-0.2 (-13.23)</td>
      <td>-0.18 (-5.88)</td>
      <td>0.48 (20.81)</td>
      <td>0 (0.17)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>-4.14% (-1.67)</td>
      <td>-0.22 (-11.31)</td>
      <td>-0.23 (-7.81)</td>
      <td>0.37 (11.26)</td>
      <td>0.02 (0.75)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>-3.55% (-1.52)</td>
      <td>-0.19 (-13.36)</td>
      <td>-0.24 (-10.15)</td>
      <td>0.24 (10.92)</td>
      <td>-0.01 (-0.65)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>-3.14% (-1.22)</td>
      <td>-0.15 (-11.66)</td>
      <td>-0.19 (-8.16)</td>
      <td>0.2 (7.73)</td>
      <td>0 (-0.14)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>2.81% (0.78)</td>
      <td>-0.03 (-1.61)</td>
      <td>-0.13 (-3.87)</td>
      <td>0.22 (5.31)</td>
      <td>-0.01 (-0.25)</td>
    </tr>
  </tbody>
</table>

Note: Table 11 contains the results for a strategy that uses portfolios generated from an alternative Hidden Beliefs Index (HBI) that uses estimates generated from applying a mean zero restriction and using OLS on positive observations instead of this paper’s median zero restriction with SCQR-based estimation. Otherwise, computations are identical to those of Table 4 in the main text.

as any stocks that had undefined accounting data three years ago. Furthermore, the portfolios use equal weighting as opposed to value weighting. Given the strong historical evidence of IPO underperformance and the historical outperformance of equal-weighted portfolios, these patterns in the alphas are not particularly noteworthy. The primary point remains the fact that the HBI continues to have statistically significant informational content even at longer lags; once we have excluded the recent IPOs from the past several years, the high HBI stocks outperform the low HBI stocks.

## K Instrumental Variable Strength and Rigid vs Dynamic Assets

The instrument for price is defined to be

$$
z_t = \log \left( 1 + \hat{P}_t^{EQ,R}(n) + \hat{P}_t^{EQ,D}(n) + \hat{P}_t^{BE,R}(n) + \hat{P}_t^{BE,D}(n) \right)
\quad \text{(33)}
$$

where

$$
\hat{P}_t^{EQ,R}(n) = \sum_{j \in \mathcal{R}} A_{j,t} \frac{1_{n \in \mathcal{H}_{j,t}}}{\sum_{m=1}^N 1_{m \in \mathcal{H}_{j,t}}},
\quad \text{(34)}
$$

$$
\hat{P}_t^{EQ,D}(n) = \sum_{j \in \mathcal{R}^C} A_{j,t} \frac{1_{n \in \mathcal{H}_{j,t}}}{\sum_{m=1}^N 1_{m \in \mathcal{H}_{j,t}}},
\quad \text{(35)}
$$

$$
\hat{P}_t^{BE,R}(n) = \sum_{j \in \mathcal{R}} A_{j,t} \frac{1_{n \in \mathcal{H}_{j,t}} BE_t(n)}{\sum_{m=1}^N 1_{m \in \mathcal{H}_{j,t}} BE_t(m)},
\quad \text{(36)}
$$

80

---

# Page 82

Table 12: Lagged HBI Sorted Returns: Size × HBI Sorts

<table>
  <thead>
    <tr>
      <th></th>
      <th>HBI Q1</th>
      <th>HBI Q2</th>
      <th>HBI Q3</th>
      <th>HBI Q4</th>
      <th>HBI Q5</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Lag 0</td>
      <td>-2.27% (-2.63)</td>
      <td>-0.79% (-0.99)</td>
      <td>0.59% (0.8)</td>
      <td>1.93% (2.17)</td>
      <td>5.58% (4.82)</td>
    </tr>
    <tr>
      <td>Lag 1</td>
      <td>-2.62% (-2.82)</td>
      <td>-1.15% (-1.5)</td>
      <td>1.09% (1.33)</td>
      <td>2.55% (2.62)</td>
      <td>6.05% (5.44)</td>
    </tr>
    <tr>
      <td>Lag 2</td>
      <td>-3.71% (-3.87)</td>
      <td>-1.05% (-1.11)</td>
      <td>1.88% (2.13)</td>
      <td>3.59% (3.97)</td>
      <td>5.85% (5.74)</td>
    </tr>
    <tr>
      <td>Lag 3</td>
      <td>-2.83% (-2.69)</td>
      <td>-0.55% (-0.58)</td>
      <td>1.54% (1.81)</td>
      <td>3.63% (4.23)</td>
      <td>5.87% (5.7)</td>
    </tr>
    <tr>
      <td>Lag 4</td>
      <td>-2.66% (-2.49)</td>
      <td>-0.24% (-0.22)</td>
      <td>1.76% (2.09)</td>
      <td>3.74% (4.33)</td>
      <td>6.27% (5.94)</td>
    </tr>
    <tr>
      <td>Lag 5</td>
      <td>-1.43% (-1.36)</td>
      <td>0.65% (0.68)</td>
      <td>2.01% (2.27)</td>
      <td>3.66% (3.85)</td>
      <td>6.56% (6.09)</td>
    </tr>
    <tr>
      <td>Lag 6</td>
      <td>-2.11% (-2.29)</td>
      <td>0.3% (0.32)</td>
      <td>3.02% (3.58)</td>
      <td>4.67% (4.6)</td>
      <td>6.82% (6.13)</td>
    </tr>
    <tr>
      <td>Lag 7</td>
      <td>-0.97% (-0.99)</td>
      <td>0.4% (0.39)</td>
      <td>2.82% (3.22)</td>
      <td>4.1% (4.54)</td>
      <td>7.14% (7.03)</td>
    </tr>
    <tr>
      <td>Lag 8</td>
      <td>-1.49% (-1.46)</td>
      <td>0.65% (0.64)</td>
      <td>2.68% (3.05)</td>
      <td>4.6% (5.2)</td>
      <td>6.41% (6.37)</td>
    </tr>
    <tr>
      <td>Lag 9</td>
      <td>-1.85% (-1.72)</td>
      <td>0.85% (0.87)</td>
      <td>3.83% (4.29)</td>
      <td>4.42% (5.01)</td>
      <td>6.51% (6.17)</td>
    </tr>
    <tr>
      <td>Lag 10</td>
      <td>-0.97% (-0.94)</td>
      <td>1.9% (1.95)</td>
      <td>3.38% (3.99)</td>
      <td>4.24% (4.67)</td>
      <td>5.79% (5.5)</td>
    </tr>
    <tr>
      <td>Lag 11</td>
      <td>-0.81% (-0.76)</td>
      <td>1.43% (1.46)</td>
      <td>3.53% (4.24)</td>
      <td>4.8% (5.09)</td>
      <td>6.26% (6.37)</td>
    </tr>
    <tr>
      <td>Lag 12</td>
      <td>-0.23% (-0.21)</td>
      <td>2.53% (2.62)</td>
      <td>3.43% (3.78)</td>
      <td>4.9% (5.63)</td>
      <td>5.39% (5.66)</td>
    </tr>
    <tr>
      <td>Lag 13</td>
      <td>-0.1% (-0.08)</td>
      <td>2.42% (2.49)</td>
      <td>3.29% (3.74)</td>
      <td>4.4% (5.05)</td>
      <td>5.64% (6.1)</td>
    </tr>
    <tr>
      <td>Lag 14</td>
      <td>-0.23% (-0.21)</td>
      <td>2.65% (2.8)</td>
      <td>3.51% (4.01)</td>
      <td>5.24% (5.69)</td>
      <td>4.58% (5.14)</td>
    </tr>
  </tbody>
</table>

**Note**: Table 5 contains the results for a strategy that uses portfolios generated from the Hidden Beliefs Index (HBI) using CRSP, Compustat, and Thomson Reuters 13F filing data from 1984Q4 through 2021Q4, with strategy results from December 1988 through December 2021. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on the HBI, which is generated from bounds on hidden beliefs weighted by the AUM of each institution. Stocks are divided into HBI quintiles within each size decile, with equal-weighted long/short (long high HBI stocks in Q5, short low HBI stocks in Q1) zero cost portfolios for each size decile averaged across the eight largest size deciles. I calculate results separately for portfolios formed 0 quarters ago (using contemporaneous information from 13F filings that is not available to participants until 45 days later) through 14 quarters ago. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997), with a clear descending pattern but strong persistence.

81

---

# Page 83

![image](image_1.png)

Figure 12: Instrument Strength and Stability

**Note**: This figure plots the first stage effective F-statistic in Sub-Figure 12a and the first stage coefficient for the instrument in 12b, where the regression is of $\log P_t(j)$ on the demeaned projection of $z_t(j)$ onto the space orthogonal to included exogenous variables. Coefficients are largely stable, with high effective F-statistics in all quarters.

$$
\hat{P}_t^{BE,D}(n) = \sum_{j \in \mathcal{R}^C} A_{j,t} \frac{1_{n \in \mathcal{H}_{j,t}} BE_t(n)}{\sum_{m=1}^N 1_{m \in \mathcal{H}_{j,t}} BE_t(m)},
\quad (37)
$$

and $BE_t(n)$ is the book equity at time $t$ for asset $n$ , computed using accounting data from Compustat from the previous quarter.

Andrews, Stock and Sun (2019), in their comprehensive review of the theoretical and empirical implications of weak instruments, argue for the use of the effective F-statistic of Olea and Pflueger (2013) to account for heteroskedasticity: ubiquitous violations of homoskedasticity assumptions render the traditional first stage F-statistic minimally informative about the presence of weak instruments. $^{40}$ The effective F-statistic is computed as

$$
F_{Eff} = \frac{\hat{\pi}' \hat{Q}_{ZZ} \hat{\pi}}{tr\left(\hat{\Sigma}_{\pi\pi} \hat{Q}_{ZZ}\right)}
$$

where $\hat{\pi}$ is the first stage regression coefficient, $\hat{\Sigma}_{\pi\pi}$ is the Eicker-White heteroskedasticity-robust covariance matrix from the first stage and $\hat{Q}_{ZZ} = \frac{1}{n} \sum_i Z_i Z_i'$ is the usual design matrix. I run a first stage regression and compute the effective F-statistic and coefficient of the linear regression of a demeaned $\log P_t$ on $z_t^\perp$ , where $z_t^\perp$ is the demeaned projection of $z_t$ onto the space orthogonal to non-constant characteristics. Figure 12a plots $F_{Eff}$ for each quarter while Figure 12b provides the first stage regression coefficients.

---

$^{40}$ Andrews, Stock and Sun (2019) argues for the use of Anderson-Rubin confidence intervals in cases with a single endogenous variable and one instrument, as is the case in this paper, but whereas they focus on traditional GMM and IV regression under a mean zero restriction, this paper uses a control variable derived from the instrument in the context of censored quantile regression. Unfortunately, to the best of the author’s knowledge, the econometric literature has yet to produce a well developed theory of weak instrumental variables in this context.

82

---

# Page 84

![image](image_1.png)

*Figure 13: Rigid and Dynamic Managers over Time*

Using the 5\% critical values from Stock and Yogo (2005), we can reject the null of weak instruments for all quarters, with the coefficient capturing the linear relationship between the endogenous variable and the instrument, plotted in 12b, consistently positive. A clear time trend exists, with the relationship between the instrument and price strengthening over time. A ready causal explanation of this time trend is the rapid increase in passive investing as a fraction of managed assets over the later years in the sample along with a general increase in institutional ownership of equities throughout the sample. Index funds have rigid mandates and therefore a precisely measured investment universe. In the earlier years of the sample, rigid mandates were uncommon whereas in later years they became ubiquitous.

Figure 13 plots the time dynamics of rigid versus dynamic asset managers. In 1985, fewer than 10 managers had rigid mandates according to this paper's taxonomy. Over time, the number of rigid and dynamic managers have both grown significantly, but with recent growth in the number of rigid managers far outpacing the growth in the number of dynamic managers on a percentage basis; despite this trend, dynamic managers outnumber rigid managers by more than 20 : 1 in recent years. The more important trend lies in AUM: rigid managers are on average far larger than dynamic managers and comprise nearly half of institutional assets under management. Recent work by Gârleanu and Pedersen (2022) on active versus passive investing aligns with these trends and numbers, suggesting that this paper's manager taxonomy, which is solely a function of 13F filing data, implicitly captures the investment mandates and styles of managers.

*Remark 7. (Consideration Sets and Exogeneity Assumption)* Consideration sets are crucial to the validity of the instrument: if they were to be defined as only stocks that have been recently held, then private return beliefs are embedded in the instrument. Indeed, if private beliefs are persistent, then a stock that has been recently held by institution $i$ likely has strong positive $u_{i,t}(n)$ whereas a stock that has not been held has low $u_{i,t}(n)$ . Correlated sentiment across institutions will increase

---

# Page 85

Table 13: Breadth and Portfolio Returns: Size × Breadth Sorts

<table>
  <thead>
    <tr>
      <th></th>
      <th>Q1</th>
      <th>Q2</th>
      <th>Q3</th>
      <th>Q4</th>
      <th>Q5</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>1.65% (1.57)</td>
      <td>3.08% (3.39)</td>
      <td>2.45% (2.79)</td>
      <td>1.55% (1.92)</td>
      <td>2.35% (3.64)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>1.24% (1.16)</td>
      <td>3.03% (3.05)</td>
      <td>2.33% (2.11)</td>
      <td>1.69% (1.43)</td>
      <td>3.18% (2.76)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>-0.38% (-0.35)</td>
      <td>2.02% (2.23)</td>
      <td>2.02% (2.29)</td>
      <td>3.53% (3.35)</td>
      <td>3.12% (2.58)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>-0.96% (-0.9)</td>
      <td>1.83% (1.97)</td>
      <td>1.85% (2.03)</td>
      <td>3.13% (2.97)</td>
      <td>3.41% (2.55)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>0.41% (0.29)</td>
      <td>1.2% (1.06)</td>
      <td>2.18% (2.09)</td>
      <td>3.26% (2.91)</td>
      <td>3.59% (2.5)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>-0.17% (-0.11)</td>
      <td>3.32% (2.48)</td>
      <td>3.63% (2.67)</td>
      <td>2.67% (2.01)</td>
      <td>5.8% (3.85)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>1.02% (0.53)</td>
      <td>2.96% (1.66)</td>
      <td>4.96% (2.98)</td>
      <td>6.22% (3.75)</td>
      <td>7.68% (3.9)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>3.15% (1.51)</td>
      <td>6.27% (2.62)</td>
      <td>7.91% (3.46)</td>
      <td>5.98% (2.69)</td>
      <td>9.72% (3.76)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>6.53% (2.67)</td>
      <td>8.75% (3.16)</td>
      <td>10.73% (3.74)</td>
      <td>10.9% (3.53)</td>
      <td>16.29% (4.87)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>19.41% (5.43)</td>
      <td>19.63% (4.73)</td>
      <td>12.99% (3.22)</td>
      <td>16.38% (4.12)</td>
      <td>16.27% (3.95)</td>
    </tr>
  </tbody>
</table>

Note: Table 13 contains the results for portfolios formed via sorts on $Breadth$ , the number of dynamic 13F institutions with long positions in a given stock. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on $Breadth$ . Stocks are divided into $Breadth$ quintiles within each size decile, resulting in 50 equal weight portfolios; stocks with a $Breadth$ of zero are excluded. This process is repeated three times, using the $Breadth$ as of the last day of the previous quarter, the second prior quarter, and the third prior quarter, with the simple average of the returns of these three portfolios used as the size × $Breadth$ quintile return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

this threat to identification. The recent work of Akepanidtaworn, Mascio, Imas and Schmidt (2023) demonstrates that even sophisticated institutional managers make systematic mistakes in selling, with buying driven by skill but selling swayed by attention. Recently held stocks, including those currently not held, are thus likely to be stocks with high unobservables. Including entire industry groupings, as is done throughout this paper, adds stocks with both high and low idiosyncratic beliefs $u_{i,t}(n)$ to the choice set.

# L Breadth Portfolio Sorts

Tables 13 and 14 provide the results from portfolio sorts into $Breadth$ quintiles within each size decile. I exclude all stocks with zero $Breadth$ , which are stocks where no dynamic institution holds a position. Zero $Breadth$ stocks have significantly negative abnormal returns, and their inclusion in the results does not alter the $Breadth$ -derived alpha’s lack of correlation with alpha derived from the HBI.

# M Idiosyncratic Volatility Portfolio Sorts

Tables 15 and 16 provide the results from portfolio sorts into idiosyncratic volatility quintiles within each size decile.

---

# Page 86

Table 14: Breadth Long Short Strategy Results by Size Decile

<table>
  <thead>
    <tr>
      <th></th>
      <th>Annualized Alpha</th>
      <th>MKT</th>
      <th>SMB</th>
      <th>HML</th>
      <th>UMD</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>0.7% (0.53)</td>
      <td>-0.15 (-8.95)</td>
      <td>-0.59 (-18.7)</td>
      <td>0.09 (2.41)</td>
      <td>0.12 (3.96)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>1.94% (1.26)</td>
      <td>-0.01 (-0.52)</td>
      <td>-0.37 (-19.23)</td>
      <td>0.29 (8.03)</td>
      <td>0.01 (0.63)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>3.51% (2.18)</td>
      <td>0.04 (2.28)</td>
      <td>-0.17 (-10.11)</td>
      <td>0.25 (7.77)</td>
      <td>-0.05 (-2.02)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>4.38% (2.44)</td>
      <td>0.03 (1.46)</td>
      <td>-0.07 (-3.01)</td>
      <td>0.25 (7.57)</td>
      <td>-0.08 (-3.41)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>3.18% (1.56)</td>
      <td>0.04 (2.07)</td>
      <td>-0.05 (-1.76)</td>
      <td>0.21 (6.24)</td>
      <td>-0.16 (-6.32)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>5.97% (2.99)</td>
      <td>0.12 (5.77)</td>
      <td>0.1 (4.31)</td>
      <td>0.2 (6.01)</td>
      <td>-0.19 (-7.95)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>6.66% (2.81)</td>
      <td>0.2 (5.45)</td>
      <td>0.28 (7.62)</td>
      <td>0.38 (7.29)</td>
      <td>-0.15 (-4.47)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>6.57% (2.81)</td>
      <td>0.28 (13.08)</td>
      <td>0.45 (14.78)</td>
      <td>0.35 (9.77)</td>
      <td>-0.11 (-4.74)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>9.76% (3.12)</td>
      <td>0.2 (13.4)</td>
      <td>0.29 (10.65)</td>
      <td>0.17 (5.78)</td>
      <td>-0.11 (-4.61)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>-3.14% (-0.72)</td>
      <td>0.14 (6.66)</td>
      <td>0.15 (4.14)</td>
      <td>0.09 (2.21)</td>
      <td>-0.06 (-2.29)</td>
    </tr>
  </tbody>
</table>

Note: Table 14 contains the results for a strategy that uses portfolios generated from *Breadth* data, where *Breadth* is the number of dynamic 13F institutions that hold a long position. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on *Breadth*. Stocks are divided into *Breadth* quintiles within each size decile, with the strategy going long the top quintile and short the bottom quintile, with an equal-weighted portfolio within each size decile’s long and short legs; stocks with a *Breadth* of zero are excluded. This process is repeated three times, using *Breadth* as of the last day of the previous quarter, the second prior quarter, and the third prior quarter, with the simple average of the returns of these three portfolios used as the strategy return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

Table 15: Idiosyncratic Volatility and Portfolio Returns: Size × Idiosyncratic Volatility Sorts

<table>
  <thead>
    <tr>
      <th></th>
      <th>Q1</th>
      <th>Q2</th>
      <th>Q3</th>
      <th>Q4</th>
      <th>Q5</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>1.94% (1.93)</td>
      <td>1.43% (1.76)</td>
      <td>1.35% (1.92)</td>
      <td>-0.28% (-0.34)</td>
      <td>-0.25% (-0.14)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>3.3% (3.2)</td>
      <td>2.92% (3.05)</td>
      <td>1.3% (1.39)</td>
      <td>-0.75% (-0.68)</td>
      <td>-3.6% (-1.88)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>2.66% (2.55)</td>
      <td>2.18% (2.15)</td>
      <td>0.57% (0.66)</td>
      <td>-1.31% (-1.27)</td>
      <td>-7.43% (-4.07)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>2.72% (2.62)</td>
      <td>1.76% (1.83)</td>
      <td>0.06% (0.07)</td>
      <td>-1.99% (-1.94)</td>
      <td>-8.38% (-4.49)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>1.58% (1.37)</td>
      <td>1.24% (1.33)</td>
      <td>-0.14% (-0.16)</td>
      <td>-3.44% (-2.84)</td>
      <td>-7.71% (-3.79)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>2.51% (2.1)</td>
      <td>1.84% (1.72)</td>
      <td>0.2% (0.18)</td>
      <td>-2.63% (-1.84)</td>
      <td>-6.81% (-2.85)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>3.68% (2.85)</td>
      <td>1.74% (1.35)</td>
      <td>1.36% (0.97)</td>
      <td>-1.2% (-0.64)</td>
      <td>-7.55% (-2.68)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>4.16% (2.76)</td>
      <td>2.82% (1.63)</td>
      <td>2.15% (1.11)</td>
      <td>0.03% (0.01)</td>
      <td>-3.6% (-1.14)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>7.28% (4.94)</td>
      <td>6.56% (3.29)</td>
      <td>6.66% (2.66)</td>
      <td>5.26% (1.78)</td>
      <td>-1.04% (-0.28)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>12.52% (6.39)</td>
      <td>16.01% (5.44)</td>
      <td>14.39% (4.12)</td>
      <td>11.53% (2.96)</td>
      <td>14.93% (3.04)</td>
    </tr>
  </tbody>
</table>

Note: Table 15 contains the results for portfolios formed via sorts on idiosyncratic volatility. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on idiosyncratic volatility. Stocks are divided into idiosyncratic volatility quintiles within each size decile, resulting in 50 equal weight portfolios. This process is repeated three times, using the idiosyncratic volatility as of the last day of the current quarter, the previous quarter, and the second prior quarter, with the simple average of the returns of these three portfolios used as the size × idiosyncratic volatility quintile return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

85

---

# Page 87

Table 16: Idiosyncratic Volatility Long Short Strategy Results by Size Decile

<table>
  <thead>
    <tr>
      <th></th>
      <th>Annualized Alpha</th>
      <th>MKT</th>
      <th>SMB</th>
      <th>HML</th>
      <th>UMD</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>-2.19% (-0.89)</td>
      <td>0.58 (15.99)</td>
      <td>0.6 (12.27)</td>
      <td>-0.66 (-8.65)</td>
      <td>-0.41 (-6.49)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>-6.9% (-2.68)</td>
      <td>0.6 (16.55)</td>
      <td>0.6 (11.95)</td>
      <td>-0.71 (-11.88)</td>
      <td>-0.32 (-6.65)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>-10.08% (-3.93)</td>
      <td>0.55 (17.46)</td>
      <td>0.55 (13.17)</td>
      <td>-0.65 (-13.62)</td>
      <td>-0.26 (-6.43)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>-11.1% (-4.37)</td>
      <td>0.52 (18.41)</td>
      <td>0.56 (15.28)</td>
      <td>-0.55 (-13.4)</td>
      <td>-0.23 (-6.29)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>-9.3% (-3.52)</td>
      <td>0.47 (19.55)</td>
      <td>0.56 (15.51)</td>
      <td>-0.53 (-13.22)</td>
      <td>-0.19 (-5.76)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>-9.32% (-3.22)</td>
      <td>0.44 (17.84)</td>
      <td>0.55 (12.36)</td>
      <td>-0.43 (-10.16)</td>
      <td>-0.17 (-4.91)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>-11.23% (-3.76)</td>
      <td>0.46 (24.96)</td>
      <td>0.63 (16.98)</td>
      <td>-0.3 (-9.18)</td>
      <td>-0.16 (-4.93)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>-7.76% (-2.48)</td>
      <td>0.43 (21.84)</td>
      <td>0.58 (15.94)</td>
      <td>-0.19 (-5.22)</td>
      <td>-0.08 (-2.78)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>-8.33% (-2.52)</td>
      <td>0.39 (24.07)</td>
      <td>0.55 (15.62)</td>
      <td>-0.11 (-3.54)</td>
      <td>-0.03 (-1.09)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>2.41% (0.6)</td>
      <td>0.18 (10)</td>
      <td>0.33 (10.71)</td>
      <td>-0.06 (-1.48)</td>
      <td>-0.05 (-1.72)</td>
    </tr>
  </tbody>
</table>

Note: Table 16 contains the results for a strategy that uses portfolios generated from idiosyncratic volatility data. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on idiosyncratic volatility. Stocks are divided into idiosyncratic volatility quintiles within each size decile, with the strategy going long the top quintile and short the bottom quintile, with an equal-weighted portfolio within each size decile’s long and short legs. This process is repeated three times, using idiosyncratic volatility as of the last day of the current quarter, the previous quarter, and the second prior quarter, with the simple average of the returns of these three portfolios used as the strategy return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

## N Short Sale Portfolio Sorts

Tables 17 and 18 provide the results from portfolio sorts into short interest quintiles within each size decile. Stocks with precisely zero short interest are excluded.

## O Institutional Ownership Portfolio Sorts

Tables 19 and 20 provide the results from portfolio sorts into ownership quintiles within each size decile. Stock with $\geq 100\%$ institutional ownership and stocks with $0\%$ institutional ownership are excluded. $^{41}$

$^{41}$ Greater than 100% institutional ownership is possible when short interest is high or when the underlying database has an error.

86

---

# Page 88

Table 17: Short Interest and Portfolio Returns: Size × Short Interest Sorts

<table>
  <thead>
    <tr>
      <th></th>
      <th>Q1</th>
      <th>Q2</th>
      <th>Q3</th>
      <th>Q4</th>
      <th>Q5</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>1.38% (1.68)</td>
      <td>1.72% (2.29)</td>
      <td>1.23% (1.64)</td>
      <td>1.26% (1.56)</td>
      <td>1.13% (1.09)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>2.83% (2.75)</td>
      <td>1.76% (1.66)</td>
      <td>1.74% (1.68)</td>
      <td>1.93% (1.71)</td>
      <td>-0.9% (-0.7)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>1.74% (1.64)</td>
      <td>0.66% (0.62)</td>
      <td>1.34% (1.24)</td>
      <td>0.62% (0.51)</td>
      <td>-2.42% (-1.73)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>1.22% (1.06)</td>
      <td>0.89% (0.79)</td>
      <td>1.62% (1.46)</td>
      <td>0.79% (0.63)</td>
      <td>-4.48% (-2.85)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>0.86% (0.65)</td>
      <td>-0.35% (-0.27)</td>
      <td>-1.89% (-1.35)</td>
      <td>-1.66% (-1.14)</td>
      <td>-2.15% (-1.22)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>1.44% (0.94)</td>
      <td>1.8% (1.19)</td>
      <td>0.7% (0.47)</td>
      <td>-1.97% (-1.14)</td>
      <td>-7.64% (-3.61)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>1.67% (0.93)</td>
      <td>2.64% (1.4)</td>
      <td>1.61% (0.87)</td>
      <td>-1.5% (-0.74)</td>
      <td>-5.43% (-2.08)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>4.48% (1.82)</td>
      <td>3.29% (1.42)</td>
      <td>0.78% (0.31)</td>
      <td>4.36% (1.57)</td>
      <td>-2.72% (-0.78)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>9.64% (3.07)</td>
      <td>11.07% (3.69)</td>
      <td>7.35% (2.34)</td>
      <td>7.49% (1.97)</td>
      <td>-3.62% (-0.82)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>28.44% (4.17)</td>
      <td>28.85% (4.62)</td>
      <td>22.48% (4.05)</td>
      <td>15.15% (2.8)</td>
      <td>4.6% (0.78)</td>
    </tr>
  </tbody>
</table>

**Note**: Table 17 contains the results for portfolios formed via sorts on short sales as a percentage of market cap (“short interest”). First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on short interest. Stocks are divided into short interest quintiles within each size decile, resulting in 50 portfolios. This process is repeated three times, using the short interest data as of the last day of the previous quarter, the second prior quarter, and the third prior quarter, with the simple average of the returns of these three portfolios used as the size × short interest quintile return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

Table 18: Short Interest Long Short Strategy Results by Size Decile

<table>
  <thead>
    <tr>
      <th></th>
      <th>Annualized Alpha</th>
      <th>MKT</th>
      <th>SMB</th>
      <th>HML</th>
      <th>UMD</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>-0.26% (-0.22)</td>
      <td>0.19 (13.82)</td>
      <td>0.21 (6.47)</td>
      <td>-0.11 (-4.45)</td>
      <td>-0.08 (-3.95)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>-3.73% (-2.88)</td>
      <td>0.22 (11.67)</td>
      <td>0.13 (5.21)</td>
      <td>-0.18 (-6.04)</td>
      <td>-0.07 (-3.41)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>-4.16% (-2.76)</td>
      <td>0.18 (11.34)</td>
      <td>0.1 (5.37)</td>
      <td>-0.22 (-8.32)</td>
      <td>-0.04 (-2.25)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>-5.7% (-3.15)</td>
      <td>0.15 (9.95)</td>
      <td>0.09 (4.91)</td>
      <td>-0.24 (-8.82)</td>
      <td>-0.1 (-5.25)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>-3.01% (-1.47)</td>
      <td>0.19 (11.67)</td>
      <td>0.15 (5.88)</td>
      <td>-0.21 (-7.54)</td>
      <td>-0.11 (-5.17)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>-9.08% (-3.88)</td>
      <td>0.24 (16.31)</td>
      <td>0.24 (9.58)</td>
      <td>-0.17 (-5.23)</td>
      <td>-0.16 (-6.67)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>-7.1% (-2.62)</td>
      <td>0.35 (14.2)</td>
      <td>0.35 (9.24)</td>
      <td>0 (0.06)</td>
      <td>-0.16 (-5.33)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>-7.19% (-2.12)</td>
      <td>0.4 (20.67)</td>
      <td>0.48 (13.16)</td>
      <td>0.12 (3.6)</td>
      <td>-0.05 (-2.06)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>-13.26% (-2.89)</td>
      <td>0.34 (18.4)</td>
      <td>0.39 (8.62)</td>
      <td>0.11 (3.1)</td>
      <td>-0.03 (-1.29)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>-25.41% (-3.17)</td>
      <td>0.21 (5.78)</td>
      <td>0.28 (4.7)</td>
      <td>0.07 (1.32)</td>
      <td>-0.04 (-0.94)</td>
    </tr>
  </tbody>
</table>

**Note**: Table 18 contains the results for a strategy that uses portfolios generated from short interest data. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on short interest. Stocks are divided into short interest quintiles within each size decile, with the strategy going long the top quintile and short the bottom quintile, with an equal-weighted portfolio within each size decile’s long and short legs. This process is repeated three times, using short interest data as of the last day of the second to last quarter, the third to last quarter, and the fourth to last quarter, with the simple average of the returns of these three portfolios used as the strategy return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

87

---

# Page 89

Table 19: Institutional Ownership and Portfolio Returns: Size × Fractional Ownership Sorts

<table>
  <thead>
    <tr>
      <th></th>
      <th>Q1</th>
      <th>Q2</th>
      <th>Q3</th>
      <th>Q4</th>
      <th>Q5</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>0.99% (1.17)</td>
      <td>2.45% (3.58)</td>
      <td>2.12% (2.83)</td>
      <td>2.43% (3.03)</td>
      <td>1.18% (1.37)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>0.48% (0.42)</td>
      <td>2.45% (2.89)</td>
      <td>3.05% (3.34)</td>
      <td>2.28% (2.21)</td>
      <td>1.88% (1.77)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>-2.35% (-1.87)</td>
      <td>0.73% (0.85)</td>
      <td>2.77% (3.31)</td>
      <td>3.15% (3.3)</td>
      <td>1.19% (1.31)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>-2.39% (-2.07)</td>
      <td>-0.2% (-0.21)</td>
      <td>3.06% (3.49)</td>
      <td>1.64% (1.76)</td>
      <td>2.35% (2.37)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>-2.28% (-1.58)</td>
      <td>0.84% (0.77)</td>
      <td>1.52% (1.48)</td>
      <td>2.32% (2.26)</td>
      <td>2.41% (2.27)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>-3.29% (-2.03)</td>
      <td>3.31% (2.57)</td>
      <td>3.28% (2.7)</td>
      <td>4.83% (4.08)</td>
      <td>2.5% (2.1)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>-2.16% (-1.13)</td>
      <td>1.99% (1.2)</td>
      <td>3.95% (2.36)</td>
      <td>5.37% (3.66)</td>
      <td>7.58% (4.85)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>-0.56% (-0.25)</td>
      <td>4.47% (2.27)</td>
      <td>5.89% (2.82)</td>
      <td>8.23% (4.25)</td>
      <td>7.48% (3.61)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>3.7% (1.42)</td>
      <td>8.99% (3.8)</td>
      <td>9.75% (4.16)</td>
      <td>12.29% (4.76)</td>
      <td>10.24% (4.15)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>16.77% (4.18)</td>
      <td>11.86% (3.37)</td>
      <td>16.35% (4.47)</td>
      <td>11.9% (3.72)</td>
      <td>14.38% (4.33)</td>
    </tr>
  </tbody>
</table>

**Note**: Table 19 contains the results for portfolios formed via sorts on fractional institutional ownership. Stocks with institutional ownership outside of (0, 1) are removed. Size deciles D1 to D10, with D10 the largest cap, are formed and within each decile, stocks are sorted based on institutional ownership. Stocks are divided into ownership quintiles within each size decile, resulting in 50 portfolios. This process is repeated three times, using the ownership as of the last day of the previous quarter, the second prior quarter, and the third prior quarter, with the simple average of the returns of these three portfolios used as the size × ownership quintile return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

Table 20: Institutional Ownership Long Short Strategy Results by Size Decile

<table>
  <thead>
    <tr>
      <th></th>
      <th>Annualized Alpha</th>
      <th>MKT</th>
      <th>SMB</th>
      <th>HML</th>
      <th>UMD</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>0.18% (0.15)</td>
      <td>0.08 (6.62)</td>
      <td>0.03 (1.54)</td>
      <td>-0.09 (-2.93)</td>
      <td>0.08 (3.91)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>1.4% (0.9)</td>
      <td>0.11 (11.41)</td>
      <td>-0.03 (-1.28)</td>
      <td>-0.07 (-3.05)</td>
      <td>-0.01 (-0.29)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>3.55% (2.17)</td>
      <td>0.06 (6.85)</td>
      <td>-0.05 (-2.98)</td>
      <td>-0.07 (-2.49)</td>
      <td>0.04 (2.07)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>4.74% (2.95)</td>
      <td>0.04 (2.72)</td>
      <td>-0.04 (-2.41)</td>
      <td>-0.01 (-0.5)</td>
      <td>-0.02 (-1.3)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>4.69% (2.58)</td>
      <td>0.03 (2.07)</td>
      <td>-0.05 (-2.12)</td>
      <td>0.1 (3.27)</td>
      <td>-0.09 (-3.83)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>5.79% (3.3)</td>
      <td>0.07 (5.19)</td>
      <td>0.05 (3.05)</td>
      <td>0.11 (4.05)</td>
      <td>-0.1 (-4.74)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>9.75% (5.04)</td>
      <td>0.12 (6.02)</td>
      <td>0.19 (8.85)</td>
      <td>0.24 (7.47)</td>
      <td>-0.08 (-3.59)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>8.05% (4.1)</td>
      <td>0.18 (12.66)</td>
      <td>0.27 (9.92)</td>
      <td>0.29 (12)</td>
      <td>-0.07 (-3.85)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>6.54% (2.83)</td>
      <td>0.1 (7.98)</td>
      <td>0.12 (5.17)</td>
      <td>0.17 (6.65)</td>
      <td>-0.08 (-3.83)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>-2.39% (-0.55)</td>
      <td>0.05 (2.14)</td>
      <td>0.01 (0.31)</td>
      <td>0.1 (2.17)</td>
      <td>-0.09 (-2.92)</td>
    </tr>
  </tbody>
</table>

**Note**: Table 20 contains the results for a strategy that uses portfolios generated from institutional ownership data. Stocks with institutional ownership outside of (0, 1) are removed. Size deciles D1 to D10, with D10 the largest cap, are formed and within each decile, stocks are sorted based on institutional ownership. Stocks are divided into ownership quintiles within each size decile, with the strategy going long the top quintile and short the bottom quintile, with an equal-weighted portfolio within each size decile’s long and short legs. This process is repeated three times, using ownership as of the last day of the second to last quarter, the third to last quarter, and the fourth to last quarter, with the simple average of the returns of these three portfolios used as the strategy return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

88

---

# Page 90

# P Data Appendix and Computational Details

## P.1 Data Appendix

Because 13F filings may contain data on positions in options, closed-end fund investments, convertible debt, and non-common equity, I eliminate all such products by filtering out all equities that do not have the common equity codes 10 and 11 obtained for the CUSIPs from the CRSP Database. Furthermore, to avoid issues associated with data revisions, splits, reverse splits, stale data, and non-contemporaneous data, I exclusively include dates where the s34 vintage date (“fdate”) is perfectly aligned with the s34 reporting date (“rdate”) that corresponds to the calendar date for which the report reflects institutional holdings.

This paper’s model of asset demand only takes as input data that are available to researchers and defines variables accordingly. Assets under management must be defined to mirror the optimization problems of Section 2, thus assets under management are defined to be the sum of the market value of each manager’s common equity holdings within the subset of equities with non-missing CRSP/Compustat data. This definition intentionally excludes obvious contributors to assets under management such as REITs, reportable options, convertible equity, foreign equities, and equities with missing data. The reason for this exclusion is that we are only interested in the portfolio allocation of assets under management across the cross-section of domestic stocks. $^{42}$ Missing data is a limitation of all studies such as this paper’s that make use of 13F or other publicly available filing data.

## P.2 Computational Details

All analysis was conducted using the Grace Cluster at the Yale Center for Research Computing, exploiting parallel processing over several hundred CPUs due to the computationally taxing methodology required as a result of the censoring problem. This paper’s results and the main specification in Section 6 require the SCQR method to be applied to 247,997 institution × date pairs, with each computation requiring the solution of approximately 100 linear programming problems with $n \approx 2500$ in a typical regression. Cluster-based parallel computing is ideal for this purpose given that estimation of each institution at each point in time is not dependent on the results of other estimations. I exploit the Gurobi optimizer package within Matlab to conduct all convex optimization, as it offers superior performance to Matlab’s internal convex optimization and LP methods. For comparison, a placebo test used in Section 6 to study the HBI employs OLS and requires under 250 seconds (1 CPU hour) on a desktop computer with an Intel Xeon E5-2687W v4 processor at 3.0GHz (12 cores), even with the OLS procedure generating an estimated covariance matrix; the problems induced by censoring require over three orders of magnitude more computing

$^{42}$ With no data on large fractions of institutional portfolios, the estimation task is less likely to result in biased estimates if we do not include asset classes that are only selectively reported by institutions or reported by institutions facing other decision problems that we cannot study, such as domestic versus foreign equity allocation by institutional asset managers.

89

---

# Page 91

resources than the matrix algebra of OLS.

I split the estimation task into four time periods, running each time period on a separate cluster node and using all available cores in Matlab to estimate different institutions in parallel on each node. Care must be taken to “slow down” the estimations by fractions of a second so as not to over-query the Gurobi license server because of the sheer number of optimizations required. A single run of estimations for a given consideration set construction methodology and set of explanatory characteristics requires of the order of 1,000 CPU hours.

## Q Additional Tables for S12 Disaggregated Mutual Fund Data Analysis

Table 21: Institutional Demand Estimation Summary Statistics: s12

<table>
  <thead>
    <tr>
      <th></th>
      <th>Num Inst</th>
      <th>Tot Inst AUM</th>
      <th>Rigid AUM</th>
      <th>Dynamic AUM</th>
      <th>AUM SCQR</th>
      <th>AUM Low</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1984-1988</td>
      <td>490</td>
      <td>$51B</td>
      <td>$1B</td>
      <td>$50B</td>
      <td>$25B</td>
      <td>$8B</td>
    </tr>
    <tr>
      <td>1989-1992</td>
      <td>645</td>
      <td>$88B</td>
      <td>$6B</td>
      <td>$82B</td>
      <td>$41B</td>
      <td>$10B</td>
    </tr>
    <tr>
      <td>1993-1996</td>
      <td>775</td>
      <td>$183B</td>
      <td>$10B</td>
      <td>$174B</td>
      <td>$113B</td>
      <td>$11B</td>
    </tr>
    <tr>
      <td>1997-2000</td>
      <td>2054</td>
      <td>$602B</td>
      <td>$19B</td>
      <td>$584B</td>
      <td>$420B</td>
      <td>$48B</td>
    </tr>
    <tr>
      <td>2001-2004</td>
      <td>2271</td>
      <td>$723B</td>
      <td>$57B</td>
      <td>$666B</td>
      <td>$481B</td>
      <td>$47B</td>
    </tr>
    <tr>
      <td>2005-2008</td>
      <td>1995</td>
      <td>$1222B</td>
      <td>$183B</td>
      <td>$1039B</td>
      <td>$687B</td>
      <td>$72B</td>
    </tr>
    <tr>
      <td>2009-2012</td>
      <td>4589</td>
      <td>$2360B</td>
      <td>$441B</td>
      <td>$1920B</td>
      <td>$1434B</td>
      <td>$131B</td>
    </tr>
    <tr>
      <td>2013-2016</td>
      <td>7476</td>
      <td>$5234B</td>
      <td>$1596B</td>
      <td>$3638B</td>
      <td>$2526B</td>
      <td>$253B</td>
    </tr>
    <tr>
      <td>2017-2020</td>
      <td>12224</td>
      <td>$9762B</td>
      <td>$3616B</td>
      <td>$6146B</td>
      <td>$4833B</td>
      <td>$362B</td>
    </tr>
    <tr>
      <td>2021</td>
      <td>15207</td>
      <td>$16351B</td>
      <td>$6395B</td>
      <td>$9956B</td>
      <td>$7671B</td>
      <td>$618B</td>
    </tr>
  </tbody>
</table>

**Note**: Table 21 contains summary statistics for the s12 database demand estimation, including number of institutions, total institutional AUM, the AUM of rigid institutions, the AUM of dynamic institutions, AUM of institutions for which the SCQR estimation converges, and the AUM of dynamic institutions with fewer than twenty-five holdings (“AUM Low”). Each variable is averaged over all quarters within the designated four-year window or, in the case of 2021, one-year window. The twenty-five-asset cutoff is used for generation of summary statistics because twenty-five is the cutoff used in the decision of whether to conduct estimation of a dynamic institution.

90

---

# Page 92

Table 22: Institutional Demand Estimation Consideration Sets and Holdings

<table>
  <thead>
    <tr>
      <th></th>
      <th>Avg Pos Hold</th>
      <th>Med Pos Hold</th>
      <th>Med Hab Size</th>
      <th>5th Prctl Hab Size</th>
      <th>95th Prctl Hab Size</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1984-1988</td>
      <td>37</td>
      <td>27</td>
      <td>307</td>
      <td>75</td>
      <td>992</td>
    </tr>
    <tr>
      <td>1989-1992</td>
      <td>44</td>
      <td>30</td>
      <td>305</td>
      <td>75</td>
      <td>1212</td>
    </tr>
    <tr>
      <td>1993-1996</td>
      <td>61</td>
      <td>35</td>
      <td>392</td>
      <td>80</td>
      <td>1764</td>
    </tr>
    <tr>
      <td>1997-2000</td>
      <td>63</td>
      <td>36</td>
      <td>373</td>
      <td>71</td>
      <td>1771</td>
    </tr>
    <tr>
      <td>2001-2004</td>
      <td>80</td>
      <td>42</td>
      <td>429</td>
      <td>84</td>
      <td>1749</td>
    </tr>
    <tr>
      <td>2005-2008</td>
      <td>90</td>
      <td>45</td>
      <td>433</td>
      <td>77</td>
      <td>1821</td>
    </tr>
    <tr>
      <td>2009-2012</td>
      <td>103</td>
      <td>50</td>
      <td>387</td>
      <td>69</td>
      <td>1794</td>
    </tr>
    <tr>
      <td>2013-2016</td>
      <td>109</td>
      <td>47</td>
      <td>388</td>
      <td>62</td>
      <td>1745</td>
    </tr>
    <tr>
      <td>2017-2020</td>
      <td>124</td>
      <td>50</td>
      <td>407</td>
      <td>63</td>
      <td>1751</td>
    </tr>
    <tr>
      <td>2021</td>
      <td>127</td>
      <td>48</td>
      <td>475</td>
      <td>73</td>
      <td>1941</td>
    </tr>
  </tbody>
</table>

Note: Table 22 contains summary statistics on the consideration sets (CS) and holdings of institutional investors that have at least twenty-five positive holdings in their portfolio. The censoring issue is illustrated by the ratio of positive holdings to consideration set size, with an order of magnitude difference in median sizes. The right skewness of the distribution of portfolio sizes is apparent from the large gap between median and mean number of positions.

Table 23: HBI Long Short Strategy Results by Size Decile, Mutual Fund Database

<table>
  <thead>
    <tr>
      <th></th>
      <th>Annualized Alpha</th>
      <th>MKT</th>
      <th>SMB</th>
      <th>HML</th>
      <th>UMD</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>2.53% (2.88)</td>
      <td>-0.1 (-15.08)</td>
      <td>0.03 (1.87)</td>
      <td>0.33 (20.07)</td>
      <td>0 (-0.22)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>1.88% (1.73)</td>
      <td>-0.07 (-9.48)</td>
      <td>-0.01 (-0.46)</td>
      <td>0.08 (5)</td>
      <td>-0.05 (-3.62)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>2.92% (2.77)</td>
      <td>-0.05 (-5.85)</td>
      <td>-0.04 (-3.07)</td>
      <td>0.01 (0.74)</td>
      <td>-0.04 (-3.34)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>3.14% (2.63)</td>
      <td>-0.04 (-5.06)</td>
      <td>-0.06 (-3.29)</td>
      <td>-0.13 (-8.24)</td>
      <td>-0.02 (-1.4)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>5.32% (4.1)</td>
      <td>-0.05 (-5.55)</td>
      <td>-0.03 (-1.79)</td>
      <td>-0.09 (-6.44)</td>
      <td>0.01 (0.87)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>8.14% (5.54)</td>
      <td>-0.05 (-5.77)</td>
      <td>-0.02 (-1.05)</td>
      <td>-0.07 (-4.94)</td>
      <td>0.01 (0.78)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>7.97% (5.18)</td>
      <td>-0.04 (-4.94)</td>
      <td>-0.04 (-2.52)</td>
      <td>-0.1 (-5.04)</td>
      <td>0 (0.16)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>8.14% (4.38)</td>
      <td>0 (0.04)</td>
      <td>0.03 (1.81)</td>
      <td>-0.07 (-3.38)</td>
      <td>-0.01 (-0.64)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>10.28% (4.85)</td>
      <td>-0.01 (-1)</td>
      <td>0.01 (0.71)</td>
      <td>-0.03 (-1.68)</td>
      <td>-0.03 (-1.99)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>3.81% (1.22)</td>
      <td>-0.02 (-1.3)</td>
      <td>-0.02 (-0.82)</td>
      <td>-0.11 (-3.62)</td>
      <td>-0.04 (-1.75)</td>
    </tr>
  </tbody>
</table>

Note: Table 23 contains the results for a strategy that uses portfolios generated from the Hidden Beliefs Index (HBI) from 1986 to 2021, with the index derived from Thomson Reuters s12 Mutual Fund database holdings. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on the HBI, which is generated from bounds on hidden beliefs weighted by the AUM of each institution. Stocks are divided into HBI quintiles within each size decile, with the strategy going long the top quintile and short the bottom quintile, with an equal-weighted portfolio within each size decile’s long and short legs. This process is repeated three times, using the HBI as of the last day of the second to last quarter, the third to last quarter, and the fourth to last quarter, with the simple average of the returns of these three portfolios used as the strategy return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

91

---

# Page 93

Table 24: OBI Long Short Strategy Results by Size Decile, Mutual Fund Database

<table>
  <thead>
    <tr>
      <th>Annualized Alpha</th>
      <th>MKT</th>
      <th>SMB</th>
      <th>HML</th>
      <th>UMD</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>2.39% (1.57)</td>
      <td>0.26 (15.69)</td>
      <td>0.29 (11.12)</td>
      <td>-0.31 (-11.37)</td>
      <td>-0.15 (-5.62)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>0.79% (0.57)</td>
      <td>0.2 (13.15)</td>
      <td>0.2 (12.43)</td>
      <td>-0.41 (-16.92)</td>
      <td>-0.16 (-8.37)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>1.42% (0.91)</td>
      <td>0.16 (11.73)</td>
      <td>0.13 (7.48)</td>
      <td>-0.32 (-15.34)</td>
      <td>-0.09 (-4.91)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>1.84% (1.14)</td>
      <td>0.13 (13.15)</td>
      <td>0.15 (8.9)</td>
      <td>-0.21 (-10.22)</td>
      <td>-0.05 (-3.62)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>2.56% (1.5)</td>
      <td>0.06 (3.97)</td>
      <td>0.1 (6.24)</td>
      <td>-0.21 (-8.36)</td>
      <td>-0.07 (-4.02)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>3.15% (1.55)</td>
      <td>0.04 (2.51)</td>
      <td>0.09 (4.34)</td>
      <td>-0.17 (-8.14)</td>
      <td>-0.07 (-3.83)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>4.27% (2.01)</td>
      <td>0.05 (3.01)</td>
      <td>0.08 (4.12)</td>
      <td>-0.07 (-3.79)</td>
      <td>-0.03 (-1.97)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>2.25% (0.63)</td>
      <td>0.09 (6.89)</td>
      <td>0.05 (1.97)</td>
      <td>0.03 (1.22)</td>
      <td>-0.06 (-2.89)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>3.12% (0.75)</td>
      <td>0.07 (4.81)</td>
      <td>0.1 (3.33)</td>
      <td>0.06 (2.18)</td>
      <td>-0.05 (-2.42)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>1.15% (0.21)</td>
      <td>0.04 (1.5)</td>
      <td>0.13 (2.3)</td>
      <td>0.06 (1.13)</td>
      <td>-0.07 (-2.07)</td>
    </tr>
  </tbody>
</table>


Note: Table 24 contains the results for a strategy that uses portfolios generated from the Overt Beliefs Index (OBI) from 1986 to 2021, with the index derived from Thomson Reuters s12 Mutual Fund database holdings. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on the OBI, which is generated from bounds on hidden beliefs weighted by the AUM of each institution. Stocks are divided into OBI quintiles within each size decile, with the strategy going long the top quintile and short the bottom quintile, with an equal-weighted portfolio within each size decile's long and short legs. This process is repeated three times, using the OBI as of the last day of the second to last quarter, the third to last quarter, and the fourth to last quarter, with the simple average of the returns of these three portfolios used as the strategy return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

# R Value-Weighted HBI Results

This section provides results for value-weighted HBI results within each size decile, as well as the value-weighted HBI long/short strategy results.

---

# Page 94

Table 25: The HBI and Portfolio Returns: Size × HBI Sorts

<table>
  <thead>
    <tr>
      <th></th>
      <th>HBI Q1</th>
      <th>HBI Q2</th>
      <th>HBI Q3</th>
      <th>HBI Q4</th>
      <th>HBI Q5</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>-0.37% (-0.72)</td>
      <td>0.82% (1.38)</td>
      <td>1.37% (2.3)</td>
      <td>1.83% (2.84)</td>
      <td>2.03% (3.01)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>-0.57% (-0.52)</td>
      <td>-1.37% (-1.51)</td>
      <td>1.13% (1.4)</td>
      <td>1.98% (2.42)</td>
      <td>2.7% (3.01)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>-3.54% (-3.4)</td>
      <td>-2.19% (-2.57)</td>
      <td>0.54% (0.69)</td>
      <td>2.15% (2.67)</td>
      <td>2.35% (2.49)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>-4.2% (-4.44)</td>
      <td>-1.65% (-1.89)</td>
      <td>-0.07% (-0.08)</td>
      <td>1.39% (1.68)</td>
      <td>2.46% (2.35)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>-3.36% (-3.32)</td>
      <td>-2.6% (-2.71)</td>
      <td>-0.25% (-0.25)</td>
      <td>0.9% (0.88)</td>
      <td>3.08% (2.63)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>-5.43% (-4.25)</td>
      <td>-2.71% (-2.33)</td>
      <td>-0.6% (-0.5)</td>
      <td>1.39% (1.1)</td>
      <td>5.51% (3.75)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>-5.25% (-3.26)</td>
      <td>-1.36% (-0.83)</td>
      <td>2.25% (1.3)</td>
      <td>2.07% (1.28)</td>
      <td>6.69% (3.68)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>-3.88% (-1.93)</td>
      <td>-0.74% (-0.38)</td>
      <td>1.85% (0.94)</td>
      <td>4.57% (2.13)</td>
      <td>8.41% (3.63)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>-1.27% (-0.53)</td>
      <td>2.45% (1.04)</td>
      <td>4.14% (1.69)</td>
      <td>5.29% (1.83)</td>
      <td>12.13% (4.25)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>0.07% (0.02)</td>
      <td>3.85% (1.33)</td>
      <td>4.66% (1.45)</td>
      <td>6.1% (1.79)</td>
      <td>13.31% (3.57)</td>
    </tr>
  </tbody>
</table>

Note: Table 25 contains the results for portfolios formed via sorts on the Hidden Beliefs Index (HBI) from 1986 to 2021. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on the HBI, which is generated from bounds on hidden beliefs weighted by the AUM of each institution. Stocks are divided into HBI quintiles within each size decile, resulting in 50 value-weighted portfolios. This process is repeated three times, using the HBI as of the last day of the previous quarter, the second prior quarter, and the third prior quarter, with the simple average of the returns of these three portfolios used as the size × HBI quintile return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

Table 26: HBI Long Short Strategy Results by Size Decile

<table>
  <thead>
    <tr>
      <th></th>
      <th>Annualized Alpha</th>
      <th>MKT</th>
      <th>SMB</th>
      <th>HML</th>
      <th>UMD</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>2.4% (2.54)</td>
      <td>-0.08 (-11.76)</td>
      <td>0.04 (2.42)</td>
      <td>0.13 (6.03)</td>
      <td>0.05 (3.39)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>3.27% (2.69)</td>
      <td>-0.11 (-10.07)</td>
      <td>-0.02 (-1.15)</td>
      <td>0.03 (1.26)</td>
      <td>-0.08 (-5.37)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>5.9% (4.53)</td>
      <td>-0.1 (-11.62)</td>
      <td>-0.01 (-0.82)</td>
      <td>-0.11 (-6.39)</td>
      <td>-0.06 (-4.34)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>6.66% (4.85)</td>
      <td>-0.05 (-5.31)</td>
      <td>-0.03 (-2.45)</td>
      <td>-0.22 (-12.01)</td>
      <td>-0.07 (-5.12)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>6.45% (4.4)</td>
      <td>-0.04 (-5.44)</td>
      <td>-0.05 (-3.53)</td>
      <td>-0.21 (-11.29)</td>
      <td>-0.07 (-5.52)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>10.94% (6.48)</td>
      <td>-0.01 (-1.6)</td>
      <td>0 (-0.16)</td>
      <td>-0.21 (-10.99)</td>
      <td>-0.05 (-3.74)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>11.94% (6.39)</td>
      <td>-0.01 (-1.31)</td>
      <td>0.03 (1.76)</td>
      <td>-0.14 (-6.87)</td>
      <td>-0.03 (-2.27)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>12.29% (5.71)</td>
      <td>0.02 (1.79)</td>
      <td>0.05 (2.71)</td>
      <td>-0.11 (-5.27)</td>
      <td>-0.02 (-1.42)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>13.4% (5.51)</td>
      <td>0.05 (4.67)</td>
      <td>0.09 (4.66)</td>
      <td>-0.11 (-5.62)</td>
      <td>-0.02 (-1.11)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>13.23% (4.01)</td>
      <td>0.03 (2.18)</td>
      <td>0.07 (2.11)</td>
      <td>-0.08 (-2.42)</td>
      <td>0 (-0.16)</td>
    </tr>
  </tbody>
</table>

Note: Table 26 contains the results for a strategy that uses portfolios generated from the Hidden Beliefs Index (HBI) from 1986 to 2021. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on the HBI, which is generated from bounds on hidden beliefs weighted by the AUM of each institution. Stocks are divided into HBI quintiles within each size decile, with the strategy going long the top quintile and short the bottom quintile, with a market equity-weighted portfolio within each size decile’s long and short legs. This process is repeated three times, using the HBI as of the last day of the second to last quarter, the third to last quarter, and the fourth to last quarter, with the simple average of the returns of these three portfolios used as the strategy return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

93

---

# Page 95

Table 27: The HBI and Portfolio Returns: Size × HBI Sorts

<table>
  <thead>
    <tr>
      <th></th>
      <th>HBI Q1</th>
      <th>HBI Q2</th>
      <th>HBI Q3</th>
      <th>HBI Q4</th>
      <th>HBI Q5</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>-0.87% (-1.32)</td>
      <td>-0.4% (-0.6)</td>
      <td>1.73% (2.64)</td>
      <td>2.03% (2.87)</td>
      <td>3.56% (4.48)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>-1.64% (-1.49)</td>
      <td>0.23% (0.26)</td>
      <td>1.5% (1.88)</td>
      <td>2.05% (2.42)</td>
      <td>4.44% (4.75)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>-4.48% (-4.11)</td>
      <td>-0.83% (-1.04)</td>
      <td>0.31% (0.38)</td>
      <td>2.15% (2.63)</td>
      <td>4.36% (4.79)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>-4.56% (-4.4)</td>
      <td>-1.69% (-1.86)</td>
      <td>0.54% (0.68)</td>
      <td>1.39% (1.56)</td>
      <td>3.51% (3.52)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>-4.85% (-4.25)</td>
      <td>-3.32% (-3.16)</td>
      <td>-0.56% (-0.57)</td>
      <td>2.52% (2.47)</td>
      <td>4.13% (3.66)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>-5.06% (-3.68)</td>
      <td>-1.92% (-1.56)</td>
      <td>-0.56% (-0.45)</td>
      <td>2.48% (2.04)</td>
      <td>6.07% (4.53)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>-5.51% (-3.29)</td>
      <td>-0.51% (-0.31)</td>
      <td>-0.47% (-0.28)</td>
      <td>3.9% (2.6)</td>
      <td>6.93% (4.25)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>-3.77% (-1.75)</td>
      <td>0.59% (0.28)</td>
      <td>2.25% (1.05)</td>
      <td>5.88% (3.02)</td>
      <td>8.35% (3.92)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>-0.11% (-0.04)</td>
      <td>3.88% (1.57)</td>
      <td>6.81% (2.52)</td>
      <td>8.88% (3.95)</td>
      <td>13.24% (4.9)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>11.61% (3.41)</td>
      <td>13.54% (4.12)</td>
      <td>11.9% (3.97)</td>
      <td>15.9% (4.63)</td>
      <td>23.23% (5.95)</td>
    </tr>
  </tbody>
</table>

Note: Table 27 contains the results for portfolios formed via sorts on the Hidden Beliefs Index (HBI) using the alternative characteristics (log size, log book value, momentum, beta, a constant). First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on the HBI, which is generated from bounds on hidden beliefs weighted by the AUM of each institution. Stocks are divided into HBI quintiles within each size decile, resulting in 50 portfolios. This process is repeated three times, using the HBI as of the last day of the previous quarter, the second prior quarter, and the third prior quarter, with the simple average of the returns of these three portfolios used as the size × HBI quintile return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

## S Additional Robustness Tests

I now test the sensitivity of the HBI results to alternative characteristic sets, a different consideration set definition, different HBI formulations, and strategy parameter changes. Results are qualitatively the same across all variations.

### Alternative Characteristics

I rerun the main HBI and OBI estimations and analysis using characteristics based on Asness, Moskowitz and Pedersen (2013) instead of the set of characteristics from Fama and French (2015). The results, given in Tables 27 and 28, show strong return predictability of the HBI, with t-statistics that on the whole are almost indiscernible in magnitude from the main specification. Yet the estimates of demand coefficients that both specifications share in common (e.g. beta) are often wildly different, with limited correlation in the cross section of managers. Carefully selected sets of explanatory characteristics can therefore provide us with an informative Hidden Beliefs Index, but caution must be employed when interpreting the meaning of specific coefficients due to the potential for omitted variables and endogeneity.

### Alternative Consideration Set Definitions

I rerun the analysis using an alternative definition of consideration sets that results in substantially fewer zero holdings. I once again use a NAICS-based definition but with a variable inclusion

94

---

# Page 96

Table 28: HBI Long Short Strategy Results by Size Decile

<table>
  <thead>
    <tr>
      <th>Annualized Alpha</th>
      <th>MKT</th>
      <th>SMB</th>
      <th>HML</th>
      <th>UMD</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>4.43% (4.27)</td>
      <td>-0.12 (-17.69)</td>
      <td>0.04 (2.89)</td>
      <td>0.28 (14.88)</td>
      <td>0.02 (1.63)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>6.08% (5.07)</td>
      <td>-0.13 (-10.44)</td>
      <td>-0.03 (-1.86)</td>
      <td>0.11 (5.93)</td>
      <td>-0.02 (-1.1)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>8.84% (6.62)</td>
      <td>-0.1 (-11.97)</td>
      <td>-0.05 (-3.49)</td>
      <td>0.03 (1.24)</td>
      <td>0 (0.01)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>8.06% (6.02)</td>
      <td>-0.07 (-7.79)</td>
      <td>-0.07 (-4.41)</td>
      <td>-0.1 (-4.32)</td>
      <td>0 (0.03)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>8.98% (6.31)</td>
      <td>-0.06 (-7.67)</td>
      <td>-0.06 (-3.64)</td>
      <td>-0.07 (-3.34)</td>
      <td>0.02 (1.02)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>11.13% (7.08)</td>
      <td>-0.06 (-6.63)</td>
      <td>-0.05 (-3.43)</td>
      <td>-0.07 (-3.1)</td>
      <td>0.01 (0.82)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>12.44% (7.73)</td>
      <td>-0.06 (-6.5)</td>
      <td>-0.05 (-3.32)</td>
      <td>-0.03 (-1.49)</td>
      <td>0.02 (1.4)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>12.13% (6.35)</td>
      <td>-0.07 (-5.22)</td>
      <td>-0.07 (-3.99)</td>
      <td>-0.09 (-4.34)</td>
      <td>0.04 (2.27)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>13.34% (6.24)</td>
      <td>-0.08 (-5.86)</td>
      <td>-0.05 (-2.41)</td>
      <td>-0.09 (-4.46)</td>
      <td>0 (0.27)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>11.62% (3.09)</td>
      <td>-0.06 (-2.14)</td>
      <td>0.06 (1.77)</td>
      <td>-0.15 (-3.05)</td>
      <td>0 (0.08)</td>
    </tr>
  </tbody>
</table>

Note: Table 28 contains the results for a strategy that uses portfolios generated from the Hidden Beliefs Index (HBI) using the alternative characteristics (log size, log book value, momentum, beta, a constant). First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on the HBI, which is generated from bounds on hidden beliefs weighted by the AUM of each institution. Stocks are divided into HBI quintiles within each size decile, with the strategy going long the top quintile and short the bottom quintile, with an equal-weighted portfolio within each size decile's long and short legs. This process is repeated three times, using the HBI as of the last day of the second to last quarter, the third to last quarter, and the fourth to last quarter, with the simple average of the returns of these three portfolios used as the strategy return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

criterion. Let $ K $ be the number of equities that share a given 4-digit NAICS code and let $ M $ be the number of equities with the same NAICS code that an institution has held at some point in the last three years. Then all remaining equities with the same NAICS code are added to the consideration set if and only if $ M > \lfloor \frac{K}{20} \rfloor $ ; this variable criterion is based on the concept that if fewer than 5\% of a NAICS code’s stocks are within a portfolio, then the other stocks in the industry have not been considered. The results, given in Tables 29 and 30, show that under this alternative definition the HBI remains strongly predictive of future returns with nearly identical results despite significantly different consideration set sizes (see Table 31).

# Varying Strategy Definition

The results of this section are highly robust to strategy variations such as restricting to a subset of stocks. If we sort into size deciles and only keep stocks with above median idiosyncratic volatility, results are comparably strong or stronger. These are the stocks most likely to be experiencing disagreement among investors, as noted by Daniel, Klos and Rottke (2023). When the HBI is constructed from this half-sized universe of idiosyncratically volatile “high disagreement” equities, the gap in four-factor alphas between the highest and lowest HBI quintile portfolios widens and the lowest HBI quintiles see substantially more negative abnormal returns.

---

# Page 97

Table 29: The HBI and Portfolio Returns: Size × HBI Sorts

<table>
  <thead>
    <tr>
      <th></th>
      <th>HBI Q1</th>
      <th>HBI Q2</th>
      <th>HBI Q3</th>
      <th>HBI Q4</th>
      <th>HBI Q5</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>-0.65% (-0.87)</td>
      <td>0.51% (0.71)</td>
      <td>1.45% (2.05)</td>
      <td>1.79% (2.4)</td>
      <td>3.92% (4.69)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>-1.75% (-1.51)</td>
      <td>0.57% (0.63)</td>
      <td>2.17% (2.56)</td>
      <td>2.45% (2.89)</td>
      <td>3.27% (3.45)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>-4.34% (-3.92)</td>
      <td>-0.71% (-0.8)</td>
      <td>1.83% (2.33)</td>
      <td>2.38% (2.78)</td>
      <td>3.57% (3.84)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>-5.4% (-4.72)</td>
      <td>-1.43% (-1.58)</td>
      <td>1.01% (1.17)</td>
      <td>2.91% (3.5)</td>
      <td>3.06% (3.24)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>-7.09% (-5.46)</td>
      <td>-0.98% (-0.89)</td>
      <td>1.09% (1.08)</td>
      <td>1.75% (1.88)</td>
      <td>3.76% (3.33)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>-8.51% (-5.13)</td>
      <td>-0.41% (-0.3)</td>
      <td>1.99% (1.6)</td>
      <td>3.42% (2.84)</td>
      <td>5.12% (4.04)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>-7.52% (-3.69)</td>
      <td>-1.42% (-0.78)</td>
      <td>3.03% (1.87)</td>
      <td>4.58% (3)</td>
      <td>6.35% (3.95)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>-6.36% (-2.55)</td>
      <td>0.22% (0.09)</td>
      <td>5.35% (2.53)</td>
      <td>5.71% (2.82)</td>
      <td>7.37% (3.57)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>-1.17% (-0.42)</td>
      <td>5.75% (1.97)</td>
      <td>5.78% (2.16)</td>
      <td>10.16% (3.99)</td>
      <td>11.15% (4.2)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>8.13% (2.34)</td>
      <td>10.68% (3.06)</td>
      <td>16.11% (4.74)</td>
      <td>18.53% (6.04)</td>
      <td>23.51% (6.79)</td>
    </tr>
  </tbody>
</table>

**Note**: Table 29 contains the results for portfolios formed via sorts on the Hidden Beliefs Index (HBI), with consideration sets constructed via the alternative approach of this appendix. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on the HBI, which is generated from bounds on hidden beliefs weighted by the AUM of each institution. Stocks are divided into HBI quintiles within each size decile, resulting in 50 equal-weight portfolios. This process is repeated three times, using the HBI as of the last day of the previous quarter, the second prior quarter, and the third prior quarter, with the simple average of the returns of these three portfolios used as the size × HBI quintile return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

Table 30: HBI Long Short Strategy Results by Size Decile

<table>
  <thead>
    <tr>
      <th></th>
      <th>Annualized Alpha</th>
      <th>MKT</th>
      <th>SMB</th>
      <th>HML</th>
      <th>UMD</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D10</td>
      <td>4.57% (3.85)</td>
      <td>-0.21 (-21.58)</td>
      <td>0.01 (0.43)</td>
      <td>0.38 (14.71)</td>
      <td>0.12 (6.34)</td>
    </tr>
    <tr>
      <td>D9</td>
      <td>5.02% (4.06)</td>
      <td>-0.2 (-17.75)</td>
      <td>-0.13 (-7.72)</td>
      <td>0.43 (24.6)</td>
      <td>0.07 (4.67)</td>
    </tr>
    <tr>
      <td>D8</td>
      <td>7.91% (5.94)</td>
      <td>-0.22 (-24.71)</td>
      <td>-0.2 (-13.52)</td>
      <td>0.32 (22.1)</td>
      <td>0.05 (3.86)</td>
    </tr>
    <tr>
      <td>D7</td>
      <td>8.45% (6.28)</td>
      <td>-0.18 (-15.47)</td>
      <td>-0.18 (-9.82)</td>
      <td>0.28 (17.66)</td>
      <td>0.03 (1.87)</td>
    </tr>
    <tr>
      <td>D6</td>
      <td>10.84% (6.84)</td>
      <td>-0.16 (-12.18)</td>
      <td>-0.19 (-7.95)</td>
      <td>0.25 (12.47)</td>
      <td>-0.05 (-3.04)</td>
    </tr>
    <tr>
      <td>D5</td>
      <td>13.63% (7.74)</td>
      <td>-0.13 (-11.05)</td>
      <td>-0.19 (-7.58)</td>
      <td>0.2 (9.5)</td>
      <td>-0.05 (-2.96)</td>
    </tr>
    <tr>
      <td>D4</td>
      <td>13.87% (7.23)</td>
      <td>-0.11 (-9.05)</td>
      <td>-0.15 (-5.89)</td>
      <td>0.21 (10.17)</td>
      <td>-0.02 (-1)</td>
    </tr>
    <tr>
      <td>D3</td>
      <td>13.73% (7.07)</td>
      <td>-0.06 (-4.71)</td>
      <td>-0.09 (-4.67)</td>
      <td>0.14 (7.17)</td>
      <td>-0.05 (-3.14)</td>
    </tr>
    <tr>
      <td>D2</td>
      <td>12.32% (5.59)</td>
      <td>-0.08 (-7.15)</td>
      <td>-0.1 (-4.44)</td>
      <td>0.02 (0.99)</td>
      <td>-0.02 (-1.64)</td>
    </tr>
    <tr>
      <td>D1</td>
      <td>15.38% (4.91)</td>
      <td>-0.04 (-2.67)</td>
      <td>-0.11 (-4.06)</td>
      <td>0.01 (0.2)</td>
      <td>0 (0.09)</td>
    </tr>
  </tbody>
</table>

**Note**: Table 30 contains the results for a strategy that uses portfolios generated from the Hidden Beliefs Index (HBI), with consideration sets constructed via the alternative approach of this appendix. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted within each decile based on the HBI, which is generated from bounds on hidden beliefs weighted by the AUM of each institution. Stocks are divided into HBI quintiles within each size decile, with the strategy going long the top quintile and short the bottom quintile, with an equal-weighted portfolio within each size decile’s long and short legs. This process is repeated three times, using the HBI as of the last day of the second to last quarter, the third to last quarter, and the fourth to last quarter, with the simple average of the returns of these three portfolios used as the strategy return. Reported results provide the annualized four-factor alpha and corresponding t-statistic using Fama and French (1993) factors plus the momentum factor of Carhart (1997).

96

---

# Page 98

Table 31: Institutional Demand Estimation Consideration Sets and Holdings

<table>
  <thead>
    <tr>
      <th></th>
      <th>Avg Pos Hold</th>
      <th>Med Pos Hold</th>
      <th>Med Hab Size</th>
      <th>5th Prctl Hab Size</th>
      <th>95th Prctl Hab Size</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1984-1988</td>
      <td>119</td>
      <td>72</td>
      <td>736</td>
      <td>184</td>
      <td>3032</td>
    </tr>
    <tr>
      <td>1989-1992</td>
      <td>138</td>
      <td>74</td>
      <td>741</td>
      <td>183</td>
      <td>3340</td>
    </tr>
    <tr>
      <td>1993-1996</td>
      <td>157</td>
      <td>73</td>
      <td>695</td>
      <td>166</td>
      <td>4048</td>
    </tr>
    <tr>
      <td>1997-2000</td>
      <td>176</td>
      <td>73</td>
      <td>661</td>
      <td>143</td>
      <td>4624</td>
    </tr>
    <tr>
      <td>2001-2004</td>
      <td>187</td>
      <td>72</td>
      <td>799</td>
      <td>172</td>
      <td>3822</td>
    </tr>
    <tr>
      <td>2005-2008</td>
      <td>190</td>
      <td>74</td>
      <td>906</td>
      <td>190</td>
      <td>3380</td>
    </tr>
    <tr>
      <td>2009-2012</td>
      <td>189</td>
      <td>77</td>
      <td>958</td>
      <td>206</td>
      <td>2993</td>
    </tr>
    <tr>
      <td>2013-2016</td>
      <td>203</td>
      <td>86</td>
      <td>934</td>
      <td>203</td>
      <td>2750</td>
    </tr>
    <tr>
      <td>2017-2020</td>
      <td>209</td>
      <td>87</td>
      <td>951</td>
      <td>197</td>
      <td>2660</td>
    </tr>
    <tr>
      <td>2021</td>
      <td>205</td>
      <td>90</td>
      <td>902</td>
      <td>177</td>
      <td>2717</td>
    </tr>
  </tbody>
</table>

Note: Table 31 contains summary statistics on the consideration sets of institutional investors, with consideration sets constructed via the alternative approach of this appendix. The censoring issue is illustrated by the ratio of positive holdings to consideration set size, with an order of magnitude difference in median sizes.

## T The Informational Content of Top Overt Beliefs

The OBI is by definition an average idiosyncratic belief across all holders of an asset, but the average will not capture the full informational value of institutions’ overt beliefs if some beliefs are more informative than others. Antón, Cohen and Polk (2021), for example, have found that the “best ideas” of a subset of “highly active” mutual funds and a subsample of hedge funds outperform the stock market. In their analysis “best ideas” are those most overweighted versus the market portfolio, and they use the Thomson Reuters s12 mutual fund database for their primary analysis, finding that a portfolio that holds long stocks that are in the top five “overweights” of at least one manager and short sells investments in each manager’s portfolio that are not in the top five has a six-factor alpha (FF5 + UMD) of approximately 0.14% per month, with stronger results of 0.26% per month when only going long each manager’s single top investment.

This paper’s model, taxonomy of rigid and dynamic managers, estimation of institution-level demand parameters, and recovery of overt beliefs allow us to formulate a new definition of managers’ highest return expectations: we look to isolate stocks that managers believe will have high idiosyncratic average returns going forward. In other words, we are looking for the stocks that managers most believe will outperform the market after the manager’s beliefs about returns to observable characteristics are differenced out. We should expect manager portfolio weights to on average be proportional to market capitalization due to liquidity considerations and market clearing, therefore in evaluating the highest overt belief $\hat{\mu}_{i,t}(n)$ over all stocks $n$ we must normalize to prevent stocks like Microsoft, Amazon, and Tesla from being the top selections of every manager. $^{43}$ I therefore take the variable for evaluating strongest ideas to be $\rho_{i,t}(n) = \hat{\mu}_{i,t}(n)/ME(n)$ , the expected idiosyncratic abnormal return normalized by market equity; in the cross section this is

$^{43}$ Equivalently, small cap stocks will never have high weights in a diversified portfolio despite them often being a high-conviction idea.

97

---

# Page 99

equivalent to taking the ratio of expected returns to the stock’s weighting in the market portfolio.[^1]

To evaluate manager stock selection ability as well as whether overt beliefs are fully incorporated into prices, I iterate over all institutions whose beliefs are successfully estimated via SCQR and that have at least 100 positions, using the enhanced “NAICS + style box” methodology of 7.5 that provides the strongest abnormal returns to sorting on hidden beliefs. For each investor and each time period, I sort by $\rho_{i,t}(n)$ and select the top 5 stocks within their portfolio. I then sort stocks into size deciles at the end of each quarter and create equal weight long portfolios holding each stock that has an institution with a corresponding position that ranks in the top five by $\rho_{i,t}(n)$ . Within a given size decile, the portfolio consists of all stocks that belong to the set of top 5 values of $\rho_{i,t}(n)$ for at least one manager. As with all past portfolio analyses in this paper, I calculate daily strategy performance by averaging the daily returns of quarterly buy-and-hold portfolios formed one, two, and three quarters ago to avoid using contemporaneously unavailable information.

Stocks that are in the top five values of $\rho_{i,t}(n)$ , the ratio of idiosyncratic return expectations to market cap, for at least one dynamic institution significantly outperform the market, with an equal weight average alpha across deciles of 3.47\% (5.16). The abnormal returns of these overt belief-based portfolios are highly persistent, just as with the HBI, with nearly constant quarterly performance and no obvious slope. The highly durable outperformance of belief-based portfolios strongly implies that markets fail to rationally incorporate aggregated hidden beliefs and fail to infer valuable information from the overt beliefs’ extreme value statistics, with the informational content slowly diffusing over many years. Daniel, Klos and Rottke (2023) find that short sale constrained stocks (low institutional ownership and high short interest) with strong price momentum subsequently perform poorly for five years, with consistently negative abnormal returns in each of the five years; they present evidence that optimistic agents overreact to news and only gradually adjust back toward the rational benchmark. This paper’s findings of persistent belief-based return predictability in a much broader set of stocks provides strong evidence that markets only gradually incorporate information, with both the average intensity of pessimistic beliefs and extreme optimistic beliefs imperfectly impounded in prices.

# Model of Hidden and Overt Beliefs

## Environment

We consider a model with two informed agents (“institutional investors,” $i = 1, 2$ ) who trade $N$ risky assets and a riskless asset that is numeraire and pays gross returns of $R$ dollars at time $t = 2$ . The model has three time periods, $t = 0, 1, 2$ , with agents trading at times $t = 0, 1$ and consuming at time $t = 2$ . Risky assets have stochastic supply $\tilde{Q}_0 > 0$ at time $t = 0$ and $\tilde{Q}_1 > 0$ at time $t = 1$ , while the two agents have demands given by $D_1(t)$ and $D_2(t)$ . As this model’s basic environment is inspired by the noisy REE model of Admati (1985), I adopt some of the same notation. The risky

[^1]: Results are robust to using alternative normalizations via proxies for liquidity and price impact such as dollar turnover and square root of market equity.

---

# Page 100

assets pay $\tilde{F} \in \mathbb{R}^N$ dollars at time $t = 2$ . Investor $i$ has initial wealth $W_{0i}$ and seeks to maximize the expected utility of consumption subject to the intertemporal budget constraints

$$
W_{2i} = W_{1i} R + D_1(t)' \left( \tilde{F} - R P_1 \right)
$$

and

$$
W_{1i} = W_{0i} + D_0(t)' \left( P_1 - P_0 \right).
$$

Investors $i$ are assumed to form mean-variance optimal portfolios with coefficient of risk aversion $\gamma = 1$ , maximizing $D_i(t)' \mathbb{E} \left[ \tilde{F} - R P \right] - \frac{1}{2} D_i(t)' \Sigma_{i,t} D_i(t)$ where $\Sigma_{i,t}$ is the covariance matrix of $\tilde{F}$ at time $t$ with respect to investor $i$ 's information set and $D$ is restricted so that $D_i(t) \geq 0$ (short sale constraint).

Each asset $n$ has $K$ observable characteristics given by $x_{k,n}$ for $k = 1, ..., K$ and there are $K$ corresponding independent common risk factors given by $f_1, ..., f_K$ . Realizations of the risk factors $f_k$ are binary (Rademacher, taking only the values $\{-1, 1\}$ ), while the $x_{k,n}$ are drawn from a continuous distribution with bounded and non-negative support and the random supplies $\tilde{Q}_0$ and $\tilde{Q}_1$ are drawn from a continuous distribution with strictly positive support and finite first and second moments. We also express characteristics as vectors $x_k$ . The payoff for asset $n$ is given by

$$
\tilde{F}_n = \sum_{k=1}^K x_{k,n} f_k + \epsilon_n
$$

where $\epsilon_n$ is Rademacher, taking only the values $\{-1, 1\}$ with $50 - 50$ probability, and the $\epsilon_n$ are all independent and identically distributed. Agents are aware of the payoff structure and form beliefs

$$
\hat{F}_{n,i} = \sum_{k=1}^K x_k \hat{f}_{k,i} + \hat{\epsilon}_{n,i}
$$

where $\hat{f}_{k,i}$ and $\hat{\epsilon}_{n,i}$ are agent $i$ 's posterior beliefs about factor $k$ and idiosyncratic value $n$ 's payoffs respectively.

## Information Structure, Trading Timeline, and Time 0 Inference

At time $t = 0$ and only time $t = 0$ , investors 1 and 2 independently receive distorted signals about the common risk factors and idiosyncratic risks, taking the form

$$
\hat{\rho}_{n,i} = \begin{cases}
\epsilon_n & \text{w.p. } \theta \\
-\epsilon_n & \text{w.p. } 1 - \theta
\end{cases}
$$

99

---

# Page 101

for the independent risks, where $\theta > 0.5$ is a “confusion parameter” that captures the probability of receiving the correct, undistorted signal. For the common risk factors,

$$
\hat{h}_{k,i} = \begin{cases}
f_k & \text{w.p. } \omega \\
-f_k & \text{w.p. } 1 - \omega
\end{cases},
$$

where $\omega > 0.5$ is the confusion parameter.

Agents are Bayesian and form posterior beliefs based on their priors and the received signals. However, we assume that agents use their prior covariance distribution when forming optimal portfolios; this assumption removes information precision as a source of price changes, as this model is designed to study how inference about other’s beliefs impacts demand, not how the accompanying resolution of uncertainty induced by inference about others alters demand. We can also view this assumption as being based in the backward-looking estimated covariance matrices commonly used by market participants, as real-world asset markets, and stocks in particular, rarely feature known distributions of payoffs.

We make a bounded rationality assumption similar to the cursedness concept of Eyster, Rabin and Vayanos (2019): agents at time $t = 0$ fail to infer information from prices. The non-inference can be interpreted as the stochastic noise rendering inference challenging or as a misunderstanding by the agents wherein they assume that no other informed agents exist because they do not observe others’ demands. This assumption might appear strong, yet as will soon become apparent, we still permit sophisticated inference about others’ beliefs by agents. Moreover, we maintain the standard assumption that agents take price as given and do not place orders strategically. This is critical because in this stylized two agent model, agents without insight into the other agent’s private information will suffer from the winner’s curse.

We additionally assume that agents myopically optimize each period as if the following period is $t = 2$ : this assumption is both for tractability and because we are not seeking to study the changes induced by initial receipt of private information, but rather the prices post-revelation under different assumptions about posterior formation. Finally, we assume that agents do not engage is strategic purchases at time 0 to deceive the other agent when their demands are publicly exposed.

At time $t = 1$ , agents do not receive new private information but the time $t = 0$ demands of the other investor are revealed to each of them. Agents at time $t = 1$ do not infer from price and instead directly make inferences from the observed demands of the other agent. Based on beliefs and the information structure, agents form mean-variance optimal portfolios with $\mu_i = \mathbb{E}\left[\tilde{F} - RP\right] = \sum_{k=1}^K x_k \hat{f}_{k,i} + \hat{\epsilon}^i - RP$ and covariance matrix $\Sigma_i = I_{N \times N} + \sum_{k=1}^K x_k x_k'$ where $I_{N \times N}$ is the $N \times N$ identity matrix, $x_k \in \mathbb{R}^N$ is the vector of characteristics for the $k$ th risk factor, and $\hat{\epsilon}^i$ is the vector of posterior expectations about idiosyncratic returns. The covariance matrix takes this form because each of the risk factors $f_k$ and idiosyncratic payoffs $\epsilon_n$ are independent, with 1 the variance of both the Rademacher random variable $f_k$ and $\epsilon_n$ . As is immediately clear, both beliefs about returns and the covariance matrix take on the required structure from Assumptions

100

---

# Page 102

(1) and (3). Optimal portfolios are therefore given by equation (7), with $K + 1$ characteristics $\left(\{x_k\}_{k=1}^K, P_t\right)$ , and $\eta = 0$ due to the lack of a leverage constraint.

The market clearing conditions are that $\tilde{Q}_0 = D_1(0) + D_2(0)$ and $\tilde{Q}_1 = D_1(1) + D_2(1)$ . Demands are given by

$$
D_i(0) = \max\left\{0, \sum_{k=1}^K \tilde{\beta}_k^i x_k - RP_0 + \hat{\epsilon}_i\right\}
$$

where $\tilde{\beta}_k = \hat{f}_{k,i} - \kappa_k^1$ is defined as in Section 2 and we have exploited the fact that the idiosyncratic volatility matrix is just the identity matrix. $^{45}$ We can rewrite the market clearing condition at time 0 as

$$
\tilde{Q}_0 = \max\left\{0, \sum_{k=1}^K \left(\hat{f}_{k,1} - \kappa_k^1\right) x_k - RP_0 + \hat{\epsilon}^1\right\} + \max\left\{0, \sum_{k=1}^K \left(\hat{f}_{k,2} - \kappa_k^2\right) x_k - RP_0 + \hat{\epsilon}^2\right\}
$$

where we allow for prices to be either positive or negative to ensure market clearing. Because all of the asset supply $\tilde{Q}_0$ must be held by one or both of the institutions (likewise at time $t = 1$ ), we must have that at (possibly negative) equilibrium price $P_{0,n}$ for stock $n$ , either both $\sum_{k=1}^K \left(\hat{f}_{k,1} - \kappa_k^1\right) x_k - RP_0 + \hat{\epsilon}^1$ and $\sum_{k=1}^K \left(\hat{f}_{k,2} - \kappa_k^2\right) x_k - RP_0 + \hat{\epsilon}^2$ are greater than zero or else one is greater than zero and one is less than zero since $\tilde{Q}_{0,n} > 0$ . Therefore either

$$
\tilde{Q}_{0,n} = \sum_{k=1}^K \left(\hat{f}_{k,i} - \kappa_k^i\right) x_{k.n} - RP_0 + \hat{\epsilon}_n^i
$$

for some $i \in \{1,2\}$ or

$$
\tilde{Q}_{0,n} = \sum_{k=1}^K \left(\hat{f}_{k,1} + \hat{f}_{k,2} - \kappa_k^1 - \kappa_k^2\right) x_{k.n} - 2RP_{0,n} + \hat{\epsilon}_n^1 + \hat{\epsilon}_n^2
$$

so that rearranging,

$$
P_{0,n} = \frac{1}{2R} \left[ -\tilde{Q}_{0,n} + \hat{\epsilon}_n^1 + \hat{\epsilon}_n^2 + \sum_{k=1}^K \left(\hat{f}_{k,1} + \hat{f}_{k,2} - \kappa_k^1 - \kappa_k^2\right) x_{k.n} \right].
$$

When only one institution purchases, we have

$$
P_{0,n} = \frac{1}{R} \left[ -\tilde{Q}_{0,n} + \hat{\epsilon}_n^i + \sum_{k=1}^K \left(\hat{f}_{k,i} - \kappa_k^i\right) x_{k.n} \right]
$$

where $\sum_{k=1}^K \left(\hat{f}_{k,i} - \kappa_k^i\right) x_k - RP_0 + \hat{\epsilon}^i > \sum_{k=1}^K \left(\hat{f}_{k,-i} - \kappa_k^{-i}\right) x_k - RP_0 + \hat{\epsilon}^{-i}$ .

$\hat{f}_{k,i}$ and $\hat{\epsilon}^i$ are computed via Bayes’ theorem. We consider the idiosyncratic risks, but the computation of both posteriors is identical with $\omega$ replacing $\theta$ . $\hat{\epsilon}_n^i$ is derived by noting that there is a $\left(\frac{1}{2}, \frac{1}{2}\right)$ prior and a probability of $\theta$ of receiving an accurate signal. Conditional on receiving a

$^{45}$ Proposition 3 gives the correction constants $\kappa_k$ as a function of primitives.

101

---

# Page 103

good signal, the probability of a good state $\epsilon_n = 1$ is given by

$$
P(\text{Good State}|\text{Good Signal}) = \frac{P(\text{Good Signal}|\text{Good State}) P(\text{Good State})}{P(\text{Good Signal})} = \frac{\theta \frac{1}{2}}{\frac{1}{2}} = \theta
$$

which is also clear from symmetry. Therefore conditional on receiving a good signal $\hat{\rho}_n = 1$ , the expected return is $\theta - (1 - \theta) = 2\theta - 1$ while conditional on a bad signal $\hat{\rho}_n = -1$ the expected return is $-\theta + (1 - \theta) = 1 - 2\theta$ .

## Time 1 Inference

At time 1 all holdings from time 0 are publicly revealed. Suppose that the number of assets $N$ is sufficiently large relative to $K$ that “sample error” becomes small. By the consistency and asymptotic normality of the SCQR estimator and the fact that institutions are short sale constrained without a leverage restriction, each investor $i$ will be able to recover the demand parameters $\tilde{\beta}$ and therefore recover all of the other institution’s posteriors $\hat{f}_{k,-i} = \tilde{\beta}_{-i} + \kappa_k^{-i}$ and in turn signals $\hat{h}_{k,-i}$ . The censoring problem, however, means that each institution can only set identify the other institution’s posterior expectation $\hat{\epsilon}_n^{-i}$ when last period’s demand was zero: demand is zero whenever

$$
\hat{\epsilon}_n^{-i} \leq -\left( \sum_{k=1}^K \tilde{\beta}_k x_{k,n} - RP_{0,n} \right),
$$

following this paper’s analysis of hidden beliefs. Conditional on observing that the other institution did not own a given asset $n$ , and using its knowledge that either $\hat{\epsilon}_n^{-i} = 2\theta - 1$ or $\hat{\epsilon}_n^{-i} = 1 - 2\theta$ , investor $i$ can either use the identified set to precisely recover $\hat{\epsilon}_n^{-i}$ or cannot recover any information, depending on the parameter values. Suppose that $1 - 2\theta \leq -\left( \sum_{k=1}^K \tilde{\beta}_k x_{k,n} - RP_{0,n} \right) < 2\theta - 1$ ; then $i$ learns that $\hat{\rho}_n^{-i} = -1$ . Suppose that $-\left( \sum_{k=1}^K \tilde{\beta}_k x_{k,n} - RP_{0,n} \right) \geq 2\theta - 1$ : then $i$ cannot know whether the other institution received a good or bad signal, but the probability of a good signal will be higher than the unconditional probability provided that the probability that $1 - 2\theta \leq -\left( \sum_{k=1}^K \tilde{\beta}_k x_{k,n} - RP_{0,n} \right) < 2\theta - 1$ occurs with positive measure.

Given the new information extracted from the public filings, each institution will now have a common posterior for the common risk factors, whereas agents will heterogeneously form posteriors about idiosyncratic risks conditional on whether they successfully recovered the other party’s belief. If investor $i$ possesses two signals, then if they are mixed it is trivial to see that their posterior resets to the base rate of $\left( \frac{1}{2}, \frac{1}{2} \right)$ . On the other hand, if both signals are identical then taking the two good signals case as representative by symmetry, we compute

$$
P(\text{Good State}|\text{2 Good Signals}) = \frac{P(\text{2 Good Signals}|\text{Good State}) P(\text{Good State})}{P(\text{2 Good Signals})} = \frac{\theta^2 \times \frac{1}{2}}{\frac{1}{2}\theta^2 + \frac{1}{2}(1 - \theta)^2} = \frac{\theta^2}{2\theta^2 - 2\theta + 1}
$$

102

---

# Page 104

with the posterior expectation given by

$$
\frac{2\theta - 1}{2\theta^2 - 2\theta + 1}.
$$

Let us put aside for a moment cases where both institutions own the stock in the first period. In such cases each institution will be able to learn the other institution’s overt belief and no beliefs are hidden. We must then distinguish four idiosyncratic signal cases in the one owner case:

1. One institution received a good signal and purchased the stock, while the other institution received a bad signal and did not purchase.

2. One institution received a bad signal and purchased the stock, while the other institution received a bad signal and did not purchase.

3. One institution received a good signal and purchased the stock, while the other institution received a good signal but did not purchase.

4. One institution received a bad signal and purchased the stock, while the other institution received a good signal but did not purchase.

In each of the four cases, the institution that purchased the stock has an inferable overt belief while the other institution has a hidden belief that is only inferable under certain circumstances, specifically when

$$
1 - 2\theta \leq -\left( \sum_{k=1}^{K} \tilde{\beta}_k^{-i} x_{k,n} - RP_{0,n} \right) < 2\theta - 1.
$$

If $-\left( \sum_{k=1}^{K} \tilde{\beta}_k^{-i} x_{k,n} - RP_{0,n} \right) \geq 2\theta - 1$ then the bound is inconclusive but informative: conditional on non-recovery, which is to say a bound $-\left( \sum_{k=1}^{K} \tilde{\beta}_k^{-i} x_{k,n} - RP_{0,n} \right) > 2\theta - 1$ , the expected hidden belief will exceed the unconditional average (unconditional with respect to equation (38) being satisfied) since recovery only occurs when the value is negative. For a data generating process $G$ that governs the distribution of the characteristics and random supply, there is a probability $1 - \phi_n$ that for a given stock’s characteristics $\{x_{k,n}\}_{k=1}^{K}$ , estimated coefficients $\left\{ \tilde{\beta}_k^{-i} \right\}_{k=1}^{K}$ , riskless return $R$ , and value of $\theta$ , the criterion $-\left( \sum_{k=1}^{K} \tilde{\beta}_k^{-i} x_{k,n} - RP_{0,n} \right) > 2\theta - 1$ will be satisfied by a non-owner’s demand coefficients in the first period, with corresponding probability $\phi_n$ that the non-owner’s demand coefficients will satisfy equation (38).

Let us first consider in turn the posterior beliefs of the non-owning institution, which possesses both signals:

1. $\hat{\epsilon}_n^{-i} = 0$ (mixed)

2. $\hat{\epsilon}_n^{-i} = \frac{1-2\theta}{2\theta^2-2\theta+1}$ (both bad)

3. $\hat{\epsilon}_n^{-i} = \frac{2\theta-1}{2\theta^2-2\theta+1}$ (both good)

103

---

# Page 105

4. $\hat{\epsilon}_n^{-i} = 0$ (mixed)

Now let us consider the posterior beliefs of the institution that owned the stock during the first period, starting with the case where equation (38) is satisfied. If that equation is satisfied, then the first period owner learns the other institution’s signal about $n$ and possesses the same beliefs as cases (1) and (2) above.

Suppose, however, that the institution can only bound the other institution’s signal. This will involve a mixture of all four cases and has probability $1 - \phi_n$ of occurring, with $\frac{1/2}{1-\phi_n}$ probability that the opposing institution received a good signal and $1 - \frac{1/2}{1-\phi_n}$ that the other institution received a bad signal. The posterior distribution is now a distribution over both the signal of the opposing institution and the underlying state, as both are uncertain. The expected value of $\epsilon_n$ is therefore

$$
\hat{\epsilon}_n^i = \frac{1/2}{1-\phi_n} \left( \frac{2\theta - 1}{2\theta^2 - 2\theta + 1} \right) + \left( 1 - \frac{1/2}{1-\phi_n} \right) (0) = \frac{1/2}{1-\phi_n} \left( \frac{2\theta - 1}{2\theta^2 - 2\theta + 1} \right) > 0
$$

in the case where the owner $i$ received a good signal and

$$
\hat{\epsilon}_n^i = \frac{1/2}{1-\phi_n} (0) + \left( 1 - \frac{1/2}{1-\phi_n} \right) \left( \frac{1 - 2\theta}{2\theta^2 - 2\theta + 1} \right) = \left( 1 - \frac{1/2}{1-\phi_n} \right) \left( \frac{1 - 2\theta}{2\theta^2 - 2\theta + 1} \right) < 0
$$

in the case where the owner $i$ received a bad signal.

At time $t = 1$ both institutions have the same posterior beliefs about factors in the limit because the delayed time $t = 0$ holdings data is completely revealing with respect to private factor information. Therefore, all disagreement about expected returns at time $t = 1$ centers on disagreement about idiosyncratic beliefs.

Let us assume for clarity that the risk shrinkage parameter $\kappa_k$ is shared by both institutions in the second period; this condition will hold true in the limit as $N \to \infty$ and the difference in risk shrinkage will be minimal based on this paper’s explicit formula for $\kappa$ , as both institutions share posterior beliefs about common risk factors and possess symmetric belief structures with respect to idiosyncratic risks.

In stocks where the institutions have an identical posterior belief, each will own an equal amount by symmetry. Prices are therefore given by

$$
P_{1,n} = \frac{1}{2R} \left[ -\tilde{Q}_{1,n} + 2\hat{\epsilon}_n^i + \sum_{k=1}^K \left( 2\hat{f}_{k,i} - 2\kappa_k \right) x_{k.n} \right]
$$

when both own the stock, where $i$ can be either 1 or 2.

On the other hand, when only one institution $i$ owns the stock, prices are given by

$$
P_{1,n} = \frac{1}{R} \left[ -\tilde{Q}_{1,n} + \hat{\epsilon}_n^i + \sum_{k=1}^K \left( \hat{f}_{k,i} - \kappa_k \right) x_{k.n} \right]
$$

where $i$ is the institution with the higher idiosyncratic belief: $\hat{\epsilon}_n^i > \hat{\epsilon}_n^{-i}$ . This creates a winner’s

104

---

# Page 106

curse like in auction theory, as the more optimistic agent determines the price yet both agents are equally well informed at time $t = 0$ .

When hidden beliefs can be inferred, prices will be at “fair value” in that they will be set by a common belief based on full information. When one agent has an uninferable hidden belief, then the winner’s curse will be active. We consider the four cases in turn, describing the expectation of the marginal buyer as well as their identity, assuming that $N$ is large enough that a pessimistic agent will not wish to own an asset about which it has strictly lower idiosyncratic return expectations than the other institution (recall that at time $t = 1$ they share identical perceptions of common risks):

1. The time 0 owner maintains ownership, with $\hat{e}_n^i = \frac{1/2}{1-\phi_n} \left( \frac{2\theta - 1}{2\theta^2 - 2\theta + 1} \right)$ determining prices.

2. The time 0 owner maintains ownership, with $\hat{e}_n^i = \left(1 - \frac{1/2}{1-\phi_n}\right) \left( \frac{1-2\theta}{2\theta^2 - 2\theta + 1} \right)$ determining prices.

3. The time 0 owner sells to the non-owner, with $\hat{e}_n^i = \frac{2\theta - 1}{2\theta^2 - 2\theta + 1}$ determining prices.

4. The time 0 owner sells to the non-owner with $\hat{e}_n^i = 0$ determining prices.

## Prices and Hidden Beliefs under Bounded Rationality with an Inference Error

Suppose that instead of updating beliefs according to the process detailed above, agents still conduct censored quantile regression and recover the factor signals and overt beliefs (idiosyncratic signals about purchased stocks) and share risk shrinkage constants $\kappa_k$ as we assumed before, but make an inference error and fail to distinguish between informative and uninformative non-holdings. This case will only be relevant when one institution owns a given stock and the other institution does not, as at least one institution must own the stock in equilibrium.

Let us consider the four cases above in turn. For ease of exposition, let us assume that institution 1 purchased the stock last period whereas institution 2 did not.

1. Institution 1 fails to update its belief, maintaining an expectation of $2\theta - 1$ ; institution 2 updates their belief to 0 by inferring the overt belief and noting the mixed signals.

2. Institution 1 fails to update its belief, maintaining an expectation of $1 - 2\theta$ ; institution 2 updates their belief to $\frac{1-2\theta}{2\theta^2 - 2\theta + 1}$ .

3. Institution 1 maintains an expectation of $2\theta - 1$ ; institution 2 updates their belief to $\frac{2\theta - 1}{2\theta^2 - 2\theta + 1}$ .

4. Institution 1 maintains an expectation of $1 - 2\theta$ ; institution 2 updates their belief to 0.

Cases 3 and 4 correspond to cases where the non-purchaser in the first period updates their beliefs and becomes the optimistic marginal buyer in period $t = 1$ , resulting in a marginal buyer with beliefs identical to the case with full Bayesian inference.

Cases 1 and 2, however, are more intriguing. Let us consider two possibilities. First, suppose equation (38) is satisfied so that the hidden belief is fully revealed to the econometrician but is not

105

---

# Page 107

used by the agent who owned at time $t = 0$ . Then instead of the agents sharing posteriors, the agent who failed to infer is left with more optimistic beliefs and the winner’s curse becomes active. In other words, with an inference failure, low HBI stocks become more expensive.

Second, suppose that the hidden belief was not revealed because equation (38) was not satisfied. Then something counterintuitive occurs: because the time $t = 0$ owner is only the owner at time $t = 1$ when being adversely selected against, the inability to infer hidden beliefs results in a lower expected return and therefore a lower price. In other words, high HBI stocks become less overpriced.

Let us examine the spread between a stock $n_1$ with an inferable hidden belief and a stock $n_2$ with a non-inferable (high) hidden belief when agents properly update beliefs and when the time 0 owner received a good signal but the time 0 non-owner received a bad signal, supposing identical levels of stochastic asset supply $\tilde{Q}_{1,n_2} = \tilde{Q}_{1,n_1}$ :

$$
\frac{1}{R} \left[ -\tilde{Q}_{1,n_2} + \frac{1/2}{1 - \phi_{n_2}} \left( \frac{2\theta - 1}{2\theta^2 - 2\theta + 1} \right) + \sum_{k=1}^{K} \left( \hat{f}_{k,i} - \kappa_k \right) x_{k.n_2} \right]
$$

$$
- \frac{1}{R} \left[ -\frac{1}{2} \tilde{Q}_{1,n_1} + \sum_{k=1}^{K} \left( \hat{f}_{k,i} - \kappa_k \right) x_{k.n_1} \right]
$$

$$
= \underbrace{\frac{1}{R} \frac{1/2}{1 - \phi_{n_2}} \left( \frac{2\theta - 1}{2\theta^2 - 2\theta + 1} \right)}_{\text{Winner's Curse Spread}} + \underbrace{\frac{1}{R} \left[ -\frac{1}{2} \tilde{Q}_{1,n_1} \right]}_{\text{Supply Term}} + \underbrace{\frac{1}{R} \left[ \sum_{k=1}^{K} \left( \hat{f}_k - \kappa_k \right) (x_{k.n_2} - x_{k.n_1}) \right]}_{\text{Risk Price Difference}}
$$

Counterfactually, we see that stocks with high hidden beliefs will be overpriced relative to risk due to a winner’s curse under full Bayesian updating.

Let us also examine the spread between a stock $n_1$ with an inferable hidden belief and a stock $n_2$ with a non-inferable (high) hidden belief when agents properly update beliefs and when the time 0 owner received a bad signal and the time 0 non-owner also received a bad signal, supposing identical levels of stochastic asset supply:

$$
\frac{1}{R} \left[ -\tilde{Q}_{1,n_2} + \left( 1 - \frac{1/2}{1 - \phi_{n_2}} \right) \left( \frac{1 - 2\theta}{2\theta^2 - 2\theta + 1} \right) + \sum_{k=1}^{K} \left( \hat{f}_{k,i} - \kappa_k \right) x_{k.n_2} \right]
$$

$$
- \frac{1}{R} \left[ -\frac{1}{2} \tilde{Q}_{1,n_1} + \frac{1 - 2\theta}{2\theta^2 - 2\theta + 1} + \sum_{k=1}^{K} \left( \hat{f}_{k,i} - \kappa_k \right) x_{k.n_1} \right]
$$

$$
= \underbrace{\frac{1}{R} \frac{1/2}{1 - \phi_{n_2}} \left( \frac{2\theta - 1}{2\theta^2 - 2\theta + 1} \right)}_{\text{Winner's Curse Spread}} + \underbrace{\frac{1}{R} \left[ -\frac{1}{2} \tilde{Q}_{1,n_1} \right]}_{\text{Supply Term}} + \underbrace{\frac{1}{R} \left[ \sum_{k=1}^{K} \left( \hat{f}_k - \kappa_k \right) (x_{k.n_2} - x_{k.n_1}) \right]}_{\text{Risk Price Difference}}
$$

Note that the spread induced by the winner’s curse is identical in each case, and can be viewed as a version of the disagreement plus short sale constraint mechanism of Miller (1977). Under bounded rationality, both of these winner’s curse spreads trivially collapse to zero since beliefs are not updated.

Our primary question is whether hidden beliefs will predict returns, and we have two different

106

---

# Page 108

answers. Because of the winner’s curse, hidden beliefs negatively predict returns in the Bayesian base case: a stock with high hidden beliefs will have a higher valuation conditional on signals due to disagreement despite an equivalent payoff next period, whereas stocks with low hidden beliefs that satisfy equation (38) will be priced based on properly updated Bayesian posteriors that represent common information.

On the other hand, hidden beliefs will positively predict returns under bounded rationality. First, let us define $N_{mix}$ to be the fraction of stocks with defined hidden beliefs (one owner, one non-owner at time $t = 0$ ). Further define $\phi_n^1$ , $\phi_n^2$ , $\phi_n^3$ , and $\phi_n^4$ to be the fraction of stocks with defined hidden beliefs that on average fall into each of the four cases, respectively. Finally, define $\phi_n^{1,L}$ and $\phi_n^{1,H}$ to be the fraction of case (1) stocks where equation (38) is satisfied and not satisfied, respectively (low and high hidden beliefs, respectively); $\phi_n^{2,L}$ and $\phi_n^{2,H}$ are defined equivalently for case (2).

For stocks in cases (1) and (2), we know that the winner’s curse is active and that institution 1 will be more optimistic and stuck holding all of the shares at time 1 because of an inference failure. In cases (1) and (2) above, the degrees to which institution 1’s expectations exceed the rational benchmark are $2\theta - 1$ for case (1) and $1 - 2\theta - \frac{1 - 2\theta}{2\theta^2 - 2\theta + 1} = (2\theta - 1) \frac{2\theta - 2\theta^2}{2\theta^2 - 2\theta + 1} > 0$ for case (2). In cases (3) and (4) where the non-owning institution from time 0 is more optimistic, prices are determined by the (accurate) beliefs of the non-owner. Therefore, conditional on low hidden beliefs, we have 0 occurrences of cases (3) and (4), with guaranteed overvaluation of the stock versus full information. High hidden beliefs, however, are always the case when we have (3) and (4) and sometimes occur with cases (1) and (2). Conditional on case (1) or conditional on case (2), high and low hidden belief bound scenarios have the same expected returns, but cases (3) and (4), which offer superior expected returns, only occur with high bounds on hidden beliefs. The expected risk factor-adjusted returns for each of the four cases are $1 - 2\theta$ , $-(2\theta - 1) \frac{2\theta - 2\theta^2}{2\theta^2 - 2\theta + 1}$ , 0, and 0 respectively. We therefore have that stocks with high bounds on hidden beliefs have average expected returns that exceed stocks with low expected returns whenever

$$
- \left[ \phi_n^1 \phi_n^{1,L} + \phi_n^2 \phi_n^{2,L} \frac{2\theta - 2\theta^2}{2\theta^2 - 2\theta + 1} \right] \frac{1}{\phi_n^1 \phi_n^{1,L} + \phi_n^2 \phi_n^{2,L}} <
$$

$$
- \left[ \phi_n^1 \phi_n^{1,H} + \phi_n^2 \phi_n^{2,H} \frac{2\theta - 2\theta^2}{2\theta^2 - 2\theta + 1} \right] \frac{1}{\phi_n^1 \phi_n^{1,H} + \phi_n^2 \phi_n^{2,H} + \phi_n^3 + \phi_n^4},
\quad (39)
$$

which can be shown to hold true under reasonable upper bounds on $\theta$ relative to $\phi_n^1$ and $\phi_n^2$ .

Therefore, under a plausible restriction on the distribution of stocks across the four cases, stocks with high hidden beliefs outperform stocks with low hidden beliefs under an inference error, the precise opposite of the Bayesian case. This outperformance will be greater when $\phi_3$ and $\phi_4$ are higher, which is to say there is a greater fraction of stocks where the hidden belief is a good signal.

107

---

# Page 109

V Comparison with Kojien and Yogo (2019)

Below is a table that compares and contrasts the paper’s approach and objectives with those of Kojien and Yogo (2019).

W HBI and Return Predictability over Time: Long/Short Performance

This appendix details the cumulative abnormal returns of the long/short strategy formed from three different HBIs: those of subsection 7.5, subsection 6.2, and Appendix S. Returns are largely smooth over time, with a brief period of stagnation following the start of the Covid-19 pandemic. Given that this period coincided with a time of significant shocks to companies and industries, this is unsurprising: private information that can be inferred from previous quarters’ 13F filings was no longer as relevant given the sudden macroeconomic and structural shifts in the economy. Moreover, this period coincided with the “meme stock” craze and widely recognized mispricing of stocks due to increased retail trading of common stocks.

Figures 14, 15, and 16 plot the cumulative abnormal returns over time. As is evidenced by this plot, the paper’s main empirical results are not confined to a particular time period and have not faded in the last decade. Stocks with high HBI values overwhelmingly and persistently outperform stocks with low HBI values.

108

---

# Page 110

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Kojien and Yogo</th>
      <th>This Paper</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Similarities</td>
      <td>1. Institutions engage in mean-variance optimization derived from canonical approximation via log utility with lognormal returns<br>2. Log return covariance matrix has a factor decomposition<br>3. Return expectations are a function of observable and unobservable characteristics<br>4. IV based on counterfactual market equities</td>
    </tr>
    <tr>
      <td>Differences</td>
      <td>1. Beliefs about returns are a function of an infinite dimensional polynomial expansion of characteristics with each term in the polynomial aligning precisely with the power series of the exponential function, giving an exponential linear model. The coefficient on log market equity in this expansion is restricted to be less than one.<br>2. The "universe" of an investor is anything they currently hold as well as anything held in the last three years. Zero holdings are only included when they were previously a positive holding.<br>3. No short sales are allowed; all investors are short sale constrained.<br>4. A stock is not held despite being within an investor’s universe only when $\epsilon = 0$ , which implies that the stock is expected to have a gross return of zero.<br>5. The IV is based on counterfactual market equities computed by having each institution that has highly overlapping quarterly portfolios hold equal amounts of every stock within their respective investment universes.<br>6. All institutions with over 1,000 holdings are estimated separately, and all institutions with fewer than 1,000 holdings are pooled together in groups of similar institutions until each group has at least 2,000 holdings.<br>7. All institutions are included in the estimations.<br>8. Builds a "demand system" from all institutions to study counterfactuals and conduct volatility attribution.</td>
    </tr>
    <tr>
      <td></td>
      <td>1. Institutions engage in mean-variance optimization derived from canonical approximation via log utility with lognormal returns<br>2. Log return covariance matrix has a factor decomposition<br>3. Return expectations are a function of observable and unobservable characteristics<br>4. IV based on counterfactual market equities<br>1. Beliefs about returns are a linear function of characteristics with no higher order terms and no parameter restrictions.<br>2. The "consideration set" of an investor is anything they currently hold as well as anything held in the last three years, PLUS any stock that shares a four digit NAICS code with two or more stocks currently or recently held. Zero holdings encompass all non-holdings that were in the same NAICS code as two or more other holdings as well as all formerly positive holdings.<br>3. Short sales are allowed; some institutions are short sale constrained, some are unconstrained, some are partially constrained.<br>4. A stock is not held despite being within an investor’s consideration set whenever the linear combination of the observables plus the unobservable is less than or equal to zero.<br>5. The IV is based on counterfactual market equities, but they are solely determined by consideration sets. Consideration sets are very large relative to holdings, with minimal relationship between recent holdings and the IV.<br>6. All institutions are estimated separately, and institutions with under 25 holdings are not estimated. Institutions for which the estimation does not converge are not included in the analysis.<br>7. Only "dynamic" institutions are included in estimations: "rigid" institutions such as passive investors do not form beliefs and are therefore not estimated.<br>8. Estimates parameters for "dynamic" institutions and uses these to study how beliefs are incorporated into asset prices.</td>
    </tr>
  </tbody>
</table>

109

---

# Page 111

Cumulative Abnormal Retuns: NAICS + Style Box

![image](image_1.png)

Figure 14: HBI Long/Short Abnormal Returns over Time: NAICS + Style Boxes

**Note**: This figure plots the cumulative abnormal returns (versus the four factors of Carhart (1997)) over time for a strategy based on the “NAICS + Style Box” analysis of subsection 7.5. The results are for a strategy that uses portfolios generated from the Hidden Beliefs Index (HBI) from 1986 to 2021, with the HBI derived from estimates formed via this paper’s “style box” approach to consideration set construction. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on the HBI, which is generated from bounds on hidden beliefs weighted by the AUM of each institution. Stocks are divided into HBI quintiles within each size decile, with the strategy going long the top quintile and short the bottom quintile, with an equal-weighted portfolio within each size decile’s long and short legs. This process is repeated three times, using the HBI as of the last day of the second to last quarter, the third to last quarter, and the fourth to last quarter, with the simple average of the returns of these three portfolios used as the strategy return. Only the top eight size deciles (microcaps are excluded) are averaged to form the strategy results.

110

---

# Page 112

Cumulative Abnormal Retuns: NAICS Main Specification

![image](image_1.png)

Figure 15: HBI Long/Short Abnormal Returns over Time: Main Specification

**Note**: This figure plots the cumulative abnormal returns (versus the four factors of Carhart (1997)) over time for a strategy based on the main HBI analysis in the body of the paper. The results are for a strategy that uses portfolios generated from the Hidden Beliefs Index (HBI) from 1986 to 2021, with the HBI derived from estimates formed via this paper’s “style box” approach to consideration set construction. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on the HBI, which is generated from bounds on hidden beliefs weighted by the AUM of each institution. Stocks are divided into HBI quintiles within each size decile, with the strategy going long the top quintile and short the bottom quintile, with an equal-weighted portfolio within each size decile’s long and short legs. This process is repeated three times, using the HBI as of the last day of the second to last quarter, the third to last quarter, and the fourth to last quarter, with the simple average of the returns of these three portfolios used as the strategy return. Only the top eight size deciles (microcaps are excluded) are averaged to form the strategy results.

111

---

# Page 113

Cumulative Abnormal Returns: NAICS, Alternative Characteristics

![image](image_1.png)

Figure 16: HBI Long/Short Abnormal Returns over Time: Main Specification, Alternative Characteristics

**Note**: This figure plots the cumulative abnormal returns (versus the four factors of Carhart (1997)) over time for a strategy based on the alternative characteristic analysis of Appendix S. The results are for a strategy that uses portfolios generated from the Hidden Beliefs Index (HBI) from 1986 to 2021, with the HBI derived from estimates formed via this paper’s “style box” approach to consideration set construction. First, size deciles D1 to D10, with D10 the largest cap, are formed and stocks are sorted based on the HBI, which is generated from bounds on hidden beliefs weighted by the AUM of each institution. Stocks are divided into HBI quintiles within each size decile, with the strategy going long the top quintile and short the bottom quintile, with an equal-weighted portfolio within each size decile’s long and short legs. This process is repeated three times, using the HBI as of the last day of the second to last quarter, the third to last quarter, and the fourth to last quarter, with the simple average of the returns of these three portfolios used as the strategy return. Only the top eight size deciles (microcaps are excluded) are averaged to form the strategy results.

112