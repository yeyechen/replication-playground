# Page 1

# Investor Regret and Stock Returns

Y. Eser Arisoy $^{\dagger}$ Turan G. Bali $^{\ddagger}$ Yi Tang $^{\S}$

## Abstract

We introduce a measure of regret for stock market investors and investigate its cross-sectional asset pricing implications. According to our regret-based framework, investors experience regret due to not achieving the highest possible return from a similar set of stock investments, and equity portfolios with high regret generate 6.84% more annualized alpha than portfolios with low regret. Using investor-trading activity of 78,000 households at a large US-based brokerage firm, we develop an investor-based regret index and show that this household-level regret measure predicts stock returns in a similar way to our proposed regret measure. We also show that regret is not spanned by established risk or behavioral factors that have been documented to be robust predictors of equity returns.

*Key words:* Regret theory, equity returns, investor sophistication, household trading, informational frictions, limits-to-arbitrage, costly arbitrage.

*JEL classification:* G11, G12, G41.

---

$^{\dagger}$ Associate Professor of Finance, NEOMA Business School, Finance Department, 59 rue Pierre Taittinger, 51100 Reims, France. Phone: +33 (0)3 26 35 09 51, Email: eser.arisoy@neoma-bs.fr.

$^{\ddagger}$ Corresponding author. Robert Parker Chair Professor of Finance, McDonough School of Business, Georgetown University, Washington, D.C. 20057. Phone: +1 (202) 687-5388, Email: Turan.Bali@georgetown.edu.

$^{\S}$ Professor of Finance, Gabelli School of Business, Fordham University, New York, N.Y. 10023. Phone: +1 (646) 312-8292, Email: ytang@fordham.edu.

---

* We thank the editor, David Sraer, associate editor, and three anonymous referees for their constructive and insightful comments. We also benefited from discussions with Kevin Aretz, Yigit Atilgan, Justin Birru, David E. Bell, Michael J. Brennan, Zhi Da, Enrico Diecidue, Richard Engelbrecht-Wiggans, Umit Gurun, Fabian Hollstein, Graham Loomes, John Quiggin, Bruno Solnik, Raman Uppal, Quan Wen, Jianfeng Yu, and seminar participants at ESCP Europe, EDHEC Business School, Georgetown University, Manchester Business School, NEOMA Business School, Sabanci University, and TED University, 35 $^{\text{th}}$ Annual Conference of the French Finance Association, 8 $^{\text{th}}$ Financial Engineering and Banking Society International Conference, 3 $^{\text{rd}}$ Research in Behavioral Finance Conference, 2018 FMA Annual Meeting, 11 $^{\text{th}}$ Annual Meeting of Academy of Behavioral Finance and Economics, 5 $^{\text{th}}$ Inter-Business School Finance Seminar, 10 $^{\text{th}}$ Miami Behavioral Finance Conference, and 17 $^{\text{th}}$ Paris December Finance Meeting.

---

# Page 2

# 1 Introduction

Regret has a long-standing root in cognitive psychology and is defined as the negative emotion (a mixture of pain and anger) that people experience when realizing that their present situation would have been better had they decided or acted differently. Regret originates from a comparison between outcomes of a chosen action and the foregone alternatives in which the latter outperforms the former. From a financial perspective, the experience of regret is a widely encountered phenomenon among investors which can in turn affect their investment decisions by altering their demand for assets that generate high vs. low regret. $^{1}$

Being a powerful concept in psychology and decision sciences and having strong axiomatic foundations in addressing several violations of standard utility theory, regret theory and its implications for decision making have been studied in various settings. One major challenge with regret is that, besides limited experimental settings, it is not an easy task to measure investors' regret in financial markets. This paper contributes to the literature by proposing a framework to motivate a novel measure of regret for stock market investors and by investigating its cross-sectional pricing implications. In particular, we use the intuition behind the modified utility function of regret-averse investors à la Quiggin (1994) and examine the implications of regret that investors experience from holding a certain stock and at the same time not achieving the highest potential wealth level that could have been obtained by investing in alternative stocks. The key observation in our proposed framework is that the deviation of investors' wealth from the best possible foregone wealth level, hence regret, is an important factor that affects investors' utility, and it has significant implications for the cross-sectional pricing of individual equities. Thus, our regret-based setting implies that investors develop more regret, and hence experience a decrease in their modified utility, for holding stocks with large deviations between their realized returns and the highest foregone return that could have been otherwise obtained from the universe of benchmark stock investments during the same investment horizon. Obviously, one can think of various alternatives to define benchmark stock investments, i.e., the counterfactual that determines investors' regret. Motivated by studies on investor attention and familiarity bias, we consider return on stocks that are in the same industry with the stock held by the investor as counterfactuals determining investors' regret. In particular, we use stocks that have the same 3-digit SIC code with stock $i$ as counterfactuals and compare the return of stock $i$ over month $t$ to the maximum return that could have been obtained across these counterfactuals over the same period, that subsequently defines investors' regret. $^{2}$

${ }^{1}$ According to the results of a survey published by Consumer Affairs in October 2022, 67\% of Americans reported feeling regretful after a major financial decision. Source: <https://www.consumeraffairs.com/finance/learning-from-financial-hindsight.html>

${ }^{2}$ We further use different alternative benchmarks, such as the maximum return that could have been obtained across stocks: (i) with the same 2-digit code, (ii) in the same industry following Fama and French (1997) ten industry classification, (iii) headquartered in the same state, and (iv) headquartered in the same

---

# Page 3

Our regret-driven framework suggests that investors view stocks with large deviations between their realized return and the best possible foregone return in the same industry as stocks with high regret because these stocks generate the largest decline in investors’ utility as a result of the comparison of investors’ current wealth with the maximum foregone wealth level that could have been attained instead. Thus, regret-averse investors would demand extra compensation in the form of higher expected returns to hold such stocks. Likewise, due to their lower regret, investors would prefer to hold stocks with smaller deviations between their return and the maximum return that could have been achieved from alternative stock investments in the same industry, since these stocks minimize the impact of regret in investors’ utility. Accordingly, regret-averse investors would prefer stocks with low regret and accept lower future returns for such stocks in equilibrium. In line with investors’ aversion to stocks with high regret and investors’ preference for stocks with low regret, our framework predicts a positive relation between regret and future equity returns.

The contribution of our paper is fourfold. First, we extend the intuition behind the modified utility function of Quiggin (1994) to stock market investors in which regret from a stock investment impacts investors’ utility, and operationalize this regret-based framework by introducing a novel measure of regret based on the difference between a stock’s monthly return and the highest monthly return that could have been earned among stocks in the same industry. Second, we examine whether and how regret is priced in the cross-section of equity returns. Third, using household-level trading data and following the intuition behind our proposed regret framework for stock investments, we develop an investor-based regret index and examine its pricing implications. To the best of our knowledge, this is the first paper that constructs a real-life investor trading-based regret measure. Finally, we explore alternative economic underpinnings of the cross-sectional return predictability of regret.

We start our empirical analyses by investigating the cross-sectional pricing implications of regret ($REG$). First, we form quintile portfolios each month by sorting stocks according to their $REG$. Value-weighted univariate portfolio sorts indicate that stocks in the highest-$REG$ quintile outperform stocks in the lowest-$REG$ quintile by 0.40% per month (or 4.79% per annum). This result is robust to controlling for factors that are documented to be strong predictors of future returns, using equal-weighted portfolios, removing small and illiquid stocks, using only NYSE stocks, imposing price, size, and liquidity screens, across different business cycles and market conditions, and using risk-adjusted returns (alphas) with respect to alternative factor models.$^{3}$ The difference in risk-adjusted returns (alphas) of

metropolitan statistical area. The alternative counterfactuals and their corresponding results are discussed in Section 6.3.1. Our results are robust to the use of alternative counterfactuals.

$^{3}$ In particular, we use the CAPM, the 3-factor model (FF3) of Fama and French (1993), the 4-factor model (FFC) of Fama and French (1993) and Carhart (1997), the 5-factor model (FFCPS) of Fama and French (1993), Carhart (1997), and Pastor and Stambaugh (2003), the 5-factor model (FF5) of Fama and French (2015), the 6-factor model (FF6) of Fama and French (2018), the 7-factor model (FF6PS) of Fama and French (2018) and Pastor and Stambaugh (2003), the q-factor model (Q) of Hou et al. (2015), and the q-factor model (Q+) of Hou et al. (2015) augmented with FFC’s HML and UMD factors and Pastor and Stambaugh (2003) liquidity factor.

2

---

# Page 4

portfolios with the highest- and lowest-$REG$ stocks remains positive and highly significant across different stock samples, portfolio breakpoints, time periods, and factor models.

Our regret-based framework suggests that regret-averse investors dislike (prefer) high-$REG$ (low-$REG$) stocks because they represent large (small) deviations in investors’ utility and foregone wealth levels as a result of not achieving the highest return that could have been otherwise obtained by investing in more rewarding stocks. Thus, investors develop more (less) regret for holding high-$REG$ (low-$REG$) stocks in their portfolios. Because of their impact on investors’ utility, investors decrease (increase) their demand and pay low (high) prices for such stocks in order to minimize their regret, which leads to underpricing (overpricing) of high-$REG$ (low-$REG$) stocks and high (low) future returns in equilibrium.

To ensure that the significant premium of $REG$ does not simply capture the risk premia that have been identified by earlier studies, we conduct bivariate portfolio sorts based on a battery of stock characteristics that have been documented to be strong predictors of future returns. Bivariate portfolio sorts do not change the significantly positive relation between $REG$ and future stock returns. Consistent with the univariate and bivariate portfolio-level analyses, Fama and MacBeth (1973) cross-sectional regressions provide corroborating evidence that $REG$ commands a significantly positive premium after controlling for a large set of firm characteristics and risk factors.

Next, using household trading data we examine if our proposed measure of regret is linked to real-life individual investor trading behavior. Using investor trading activity and position statements of 78,000 households at a large US-based brokerage firm, we develop an investor-based regret index ($REGINDEX$) and show that $REGINDEX$ predicts sock returns in a similar way to our proposed regret measure. Furthermore, we investigate how investors’ demand and corresponding portfolio choices relate to regret. In particular, using changes in the average weights assigned to individual stocks held by individual investors for each $REGINDEX$-based portfolio over the six months including and following the portfolio formation period, we test whether there is a significant change in investors’ portfolio choices following regret. Our findings suggest that investors demand more (less) of low-regret (high-regret) stocks after observing their regret, leading to a regret-driven price pressure and the corresponding regret premium.$^4$

In addition, we construct alternative regret measures over longer-term estimation windows ranging from two to 12 months and document that regret premium is robust across different estimation periods. We also test the medium- to long-term persistence of regret and show that regret is a highly persistent phenomenon with cross-sectional predictability extending up to five months. Furthermore, following Fama and French (1993), we construct an investable strategy that mimicks the regret factor ($FREG$). The factor spanning regressions show that none of the existing rational or behavioral factor models

$^4$ We further compute portfolio weight changes holding the price constant, i.e., using beginning-of-the-month price, to compute portfolio weights at the end of the month and we obtain similar results over the six months including and following the portfolio formation period.

3

---

# Page 5

can subsume the significant alpha generated by $FREG$. The results indicate that regret is a distinctly priced investor characteristic in the cross-section of stock returns.

We conclude by investigating the economic mechanisms behind regret and the sources of its return predictability and offer important insights on the cross-sectional pricing of regret. We show that the regret premium is much more pronounced for stocks that are costlier to arbitrage and that have higher informational frictions. Using well-known proxies for arbitrage costs and informational frictions, we find that small, young, and illiquid stocks with low analyst coverage and low institutional holdings generate economically larger regret premium than large, mature, and liquid stocks with high analyst coverage and high institutional holdings. Small, young, and illiquid stocks with low institutional ownership and low analyst coverage are predominantly held by unsophisticated, uninformed retail investors. Due to informational frictions, informative signals about these stocks are not incorporated into stock prices quickly, thus their return predictability is high. These stocks are also associated with high regret. On the other hand, big, mature, and liquid stocks with high institutional ownership and high analyst coverage are largely held by sophisticated, informed institutional investors. Since informative signals about these stocks are incorporated into stock prices quickly, their return predictability is low. We also document that these stocks are associated with low regret.

Thus, our analyses suggest that regret can be induced by costly arbitrage and/or informational frictions in the equity market. Whether it is arbitrage risk or uninformed trading that may cause investors to hold unattractive stocks or miss the opportunity to hold attractive stocks, the results indicate that investors experience regret due to not achieving the highest possible return in the same industry with their stock investment. Consistent with investors’ aversion to stocks with high regret and investors’ preference for stocks with low regret, our empirical findings demonstrate a theoretically consistent, positive relation between regret and future equity returns.

The remainder of the paper is organized as follows. Section 2 presents an overview of the literature on regret theory and its applications in different settings. Section 3 provides a framework that links regret to stock returns and offers a novel measure of regret for stock market investors. Section 4 describes the data and variables. Sections 5 examines the cross-sectional relation between regret and future stock returns. Section 6 provides additional analyses and a battery of robustness checks. Section 7 investigates potential economic mechanisms behind regret and the sources of its cross-sectional predictive power. Section 8 concludes the paper.

## 2 Theoretical Motivation

Under subjective expected utility framework, if preferences satisfy certain axioms, there are numerical probabilities and utilities that represent agents’ decisions under uncertainty. The standard expected utility framework asserts that only the realized outcome matters

4

---

# Page 6

and agents choose the alternative with the highest utility in expectation. However, it is well-known that while making decisions, agents do not only care about the actual outcome of their decision, but they also account for the foregone alternatives by comparing what they could have gotten, had they chosen differently, to what they actually get. Expected utility theory has been challenged both theoretically and experimentally by studies showing significant violations of its axioms such as loss aversion, ambiguity aversion, and Allais and Ellsberg paradoxes. These challenges led to new alternative theories such as the cumulative prospect theory of Kahneman and Tversky (1979), the regret theory of Bell (1982) and Loomes and Sugden (1982), and the disappointment aversion model of Gul (1991).

Although the notion of regret in decision making goes back to Savage (1951) and to his minimax regret algorithm, it is Bell (1982) and Loomes and Sugden (1982) who formally derive a normative theory of choices under uncertainty that addresses many empirical violations of the expected utility framework. In their model, they introduce a modified utility function with a final payoff $x$ , where regret is measured by the distance between the payoff $x$ of the chosen act $X$ and the payoff $y$ that could have been obtained had another action $Y$ been selected:

$$
u(x, y) = v(x) + f(v(x) - v(y)),
$$

where $u(x, y)$ is the modified utility of having a final payoff of $x$ knowing that $y$ could have been achieved, $v(x)$ is the standard von Neumann-Morgenstern utility function which determines risk attitudes toward known outcomes (also known as choiceless utility), $v(x) - v(y)$ is utility loss/gain of having chosen act $X$ that delivers a payoff of $x$ rather than another choice $Y$ that could have paid off $y$ , and $f(v(x) - v(y))$ is the regret of having chosen $X$ when $Y$ could have been chosen. The regret function $f(\cdot)$ is monotonically increasing and concave with $f(0) = 0$ . The regret function implies that regret-averse agents differentiate between small and large regret, and large intensities of regret are weighted disproportionally heavier than small ones (Zeelenberg and Pieters, 2007). Another important characteristic of regret theory is that although the modified utility function is defined over ex post outcomes of investment choices, investors make choices ex ante by maximizing the expected value of the modified utility function.

Quiggin (1994) extends the above objective function that is defined for pairwise choices to general choice sets where investors could select from various investments, with outcomes $x_j$ , $j = 1, \ldots, n$ . For general choice problems, the modified utility function with outcome $x_i$ is defined as:

$$
u(x_i) = v(x_i) + f(v(x_i) - \max_j[v(x_j)]),
$$

where $\max_j[v(x_j)]$ is the best ex post utility that could have been obtained among all possible investments, i.e., the best foregone alternative. The distance between the two value

---

# Page 7

functions, $v(x_i) - \max_j[v(x_j)]$ , is the non-positive regret term.

Having strong axiomatic foundations in addressing several violations of expected utility theory, regret theory and its implications for decision making have been studied in various settings. $^5$ Regret is also found to be an important factor in shaping investor behavior and in financial decision making. Fogel and Berry (2006) examine the relation between regret and disposition effect, and find that investors experience more regret about holding on to a losing stock too long than about selling a winning stock too soon. Muermann et al. (2006) investigate how asset allocation decisions in a defined contribution pension plan vary with participants’ attitudes toward risk and regret, and show that investors who take regret into account hold more (less) equity in their optimal portfolios when the equity premium is low (high). Solnik and Zuo (2012) develop a global equilibrium asset pricing model using a utility formulation inspired by regret theory and provide a regret-aversion based explanation to home bias. Hazan and Kale (2015) introduce an optimal algorithm for investors’ portfolio selection problem under regret. Qin (2015) examines the effects of regret on investor behavior in which investors not only regret wrong actions but also regret inaction, and shows that regret aversion can cause investors to ride a bubble, exit and re-enter the market, or choose not to trade. Frydman and Camerer (2016) use neural data collected from an experimental asset market setting to measure regret preferences, while subjects trade stocks. Gollier (2020) shows that when presented with a one-risky-one-safe-lottery menu, regret-risk-averse agents are more willing to choose the risky act, implying a preference for positively skewed lotteries. Motivated by the above theoretical and empirical work, our paper contributes to the literature by offering a novel regret variable stemming from a stock investment and by examining the implications of this measure of regret for the cross-sectional pricing of individual equities and equity portfolios.

## 3 A Measure of Regret for Stock Market Investors

We extend Quiggin’s (1994) framework as outlined in Eq.(2) to stock market investors who develop regret by comparing their current wealth resulting from a stock investment to the highest foregone wealth level that could have been obtained across alternative stock investments:

$$
u(W_{i,t}) = v(W_{i,t}) + f\big(v(W_{i,t}) - \max_j[v(W_{j,t})]\big), \quad (3)
$$

$$
u(W_{i,t}) = v\big(W_{i,t-1}(1 + R_{i,t})\big) + f\big(v\big(W_{i,t-1}(1 + R_{i,t})\big) \\
- \max_j\big[v\big(W_{i,t-1}(1 + R_{j,t})\big)\big]\big), \quad (4)
$$

---

$^5$ See, e.g., Bell (1983), Engelbrecht-Wiggans (1989), Orphanides and Zervos (1995), Leland (1998), Camille et al. (2004), Coricelli et al. (2005), Hayashi (2008), Sarver (2008), Bleichrodt et al. (2010), Nasiry and Popescu (2012), Bikhchandani and Segal (2014), Buturak and Evren (2017), Jiang et al. (2017), Diecidue and Somasundaram (2017), Balseiro and Gur (2019), Zou et al. (2020), and Vera and Banerjee (2021) for different application areas of regret in decision making.

6

---

# Page 8

where $ W_{i,t} $ is investor's wealth at the end of month $ t $ obtained from investing in a risky stock $ i $ , $ \max_j[v(W_{j,t})] $ represents the maximum foregone wealth outcome that could have been obtained during the same month by investing in alternative stocks with $ j = 1, ..., n $ , and $ v(W_{i,t}) - \max_j[v(W_{j,t})] $ is the non-positive regret term, which captures the degree of regret, or the decrease in the value of the choiceless utility, $ f(\cdot) $ , stemming from not achieving the highest wealth outcome across all possible stock investments. Since investors' current wealth ( $ W_{i,t} $ ) is a one-to-one mapping of the return on the stock that they invest in the previous period ( $ R_{i,t} $ ), the modified utility function in Eq.(4) implies that investors care about not only the return on the stock they invest, $ R_{i,t} $ , which define their wealth next period, $ W_{i,t} $ , but also the highest possible return that could have been obtained across alternative stock investments, $ \max_j[R_{j,t}] $ , which defines their regret due to not attaining the highest possible wealth level over the same period, $ \max_j[v(W_{j,t})] $ .

An implication of Eq.(4) for regret-averse investors is that the higher the difference between a stock's monthly return and the maximum return that could have been accessed from alternative investments during the same month, the more negative (or the larger) their regret is. Hence, we define investors' regret, i.e., $ REG $ , as: $^6$

$$
REG_{i,t} = R_{i,t} - \max_j[R_{j,t}].
$$

One practical aspect of measuring regret as defined above is to choose the definition of alternative investment benchmarks (or counterfactuals), i.e., $ \max_j[R_{j,t}] $ , over which investors' regret is defined. One can think about various alternatives, however the investor attention literature suggests that investors are not able to process a large amount of information at the same time and they tend to focus on a limited number of stocks instead, while making investment decisions. Furthermore, the literature on familiarity bias suggests that investors have a tendency to invest in stocks that they are familiar with. Hence, a natural candidate for the alternative investments over which regret is evaluated is to consider stocks that are in the same industry with the stock that the investor has chosen to invest. In particular, we use stocks that have the same 3-digit SIC code with stock $ i $ as counterfactuals and compare the return of stock $ i $ over month $ t $ to the maximum return that could have been obtained across these counterfactuals over the same period, which develops investors' regret as outlined above. $^7$

$^6$ Note that we do not aim to propose a closed form solution to the maximization problem of the modified utility function in Eq. (4), or offer a formal derivation of the term inside the regret function, $ f(\cdot) $ . Our goal is to draw a link between regret theory and our proposed measure of regret stemming from a stock investment and test its pricing implications.

$^7$ To further establish the link between the modified utility function in Eq. (4) and our proposed regret measure in Eq. (5), take four stocks in the same industry with returns $-5\%$ , $10\%$ , $30\%$ , and $50\%$ , respectively. Also, assume an investor with an initial wealth of \ $10,000 and who evaluates the outcomes of her decision based on a logarithmic utility function, $ v(W) = ln(W) $ and a regret function of the form $ f(x) = -x^2 $, both of which are continuous, concave and increasing in investor's wealth, $ W $, and regret, $ x $. Eq. (4) implies that the investor achieves a modified utility of 8.95, 9.21, 9.45, and 9.62 from investing in stock A, B, C, or D, respectively. Furthermore, our proposed measure implies a regret of $ -0.55 $, $ -0.40 $,

---

# Page 9

Finally, to give an intuition of the relation between regret as defined in Eq.(5) and expected returns, suppose the returns on stock $A$ and $B$ are, respectively, 5% and 30% in month $t$ , and the maximum return that could have been attained across stocks with the same 3-digit SIC code in month $t$ is 40%. The regret measures for stock $A$ and $B$ are obtained from Eq.(5); $REG_A = -0.35$ and $REG_B = -0.10$ , indicating that regret-averse investors would develop a higher regret from investing in stock $A$ because of the larger difference between its return and the maximum return that could have otherwise been obtained from alternative investments in the same industry. Investors develop more regret for holding stock $A$ in their portfolio, or dislike stock $A$ , since it decreases investors’ utility more than stock $B$ . As a result, regret-averse investors undervalue high- $REG$ stock $A$ and demand extra compensation in the form of higher expected return to hold stock $A$ in their portfolio. Similarly, due to its lower regret, investors prefer to hold stock $B$ rather than stock $A$ in their portfolio, since stock $B$ curtails the decrease in investors’ utility. Accordingly, regret-averse investors overvalue low- $REG$ stock $B$ which generates less regret and hence they accept lower future return to hold stock $B$ in their portfolio.

Consistent with investors’ aversion to high regret and investors’ preference for low regret, our theoretical framework predicts a positive relation between regret and future returns. Thus, the future return on stock $A$ with high regret ( $REG_A = -0.35$ ) is expected to be higher than the future return on stock $B$ with low regret ( $REG_B = -0.10$ ). Since the original values of $REG$ obtained from Eq.(5) are always non-positive, we multiply the original values by $-1$ when conducting the key asset pricing tests so that higher values of $REG$ correspond to higher levels of regret.

## 4 Data and Variables

In this section, we first discuss the data sources and then provide a description of the control variables.

### 4.1 Data sources

Market variables are obtained from the Center for Research in Security Prices (CRSP) and accounting variables from COMPUSTAT. To ensure that the accounting data are available to investors in real time, we use accounting values from the fiscal year ending in calendar year $t-1$ to run out-of-sample asset pricing tests for the period from July of calendar year $t$ to June of calendar year $t+1$ . The monthly returns on the one-month Treasury bill (the risk-free rate), the equity market ( $MKT$ ), size ( $SMB$ ), book-to-market

$-0.20$ , and $0$ , respectively, for the same investments, suggesting that the higher (the more negative) the regret term is the higher the decrease in investor’s utility due to the impact of $f(x)$ in the modified utility function. Hence, there is a one-to-one link between our proposed measure, $REG$ , the term inside the regret function, $f(\cdot)$ , and the corresponding modified utility, $u(\cdot)$ , obtained from a stock investment following Quiggin’s (1994) framework.

8

---

# Page 10

$(HML)$, momentum $(MOM)$, profitability $(RMW)$, and investment $(CMA)$ factors are obtained from Kenneth French’s online data library.$^{8}$ The Pastor and Stambaugh (2003) liquidity factor $(LIQ)$ is obtained from Lubos Pastor’s website.$^{9}$ The monthly data on Q factors; size $(R_{ME})$, profitability $(R_{ROE})$, investment $(R_{I/A})$, and expected growth $(R_{EG})$ are obtained from q-factors data library.$^{10}$ Institutional holdings data come from Thomson Reuters Institutional Holding (13F) database. Analyst coverage data are obtained from IBES. Stambaugh, Yu, and Yuan (2012, 2014, 2015) mispricing measures for individual stocks (MISP) and Stambaugh and Yuan (2017) mispricing factors (MGMT and PERF) are obtained from Robert Stambaugh’s website.$^{11}$ Daniel, Hirshleifer and Sun (2020) short- and long-horizon behavioral factors (PEAD and FIN) are obtained from Kent Daniel’s website.$^{12}$ Text-based network industry classification (TNIC) data are obtained from Hoberg-Phillips data library.$^{13}$ Household trading activity and position statement data are obtained from Terrance Odean.$^{14}$

The sample period is from July 1963 to December 2020.$^{15}$ All tests are based on individual stocks trading on the New York Stock Exchange (NYSE), American Stock Exchange (AMEX), and NASDAQ with share codes 10 and 11. Furthermore, we exclude stocks with share prices less than $5 and more than $1,000 from our analysis to ensure that the results are not driven by small and illiquid stocks. The final sample contains an average of 3,036 equity observations per month. Our univariate tests investigating the relation between regret and future equity returns use a total of 2.10 million firm-month observations.

## 4.2 Control variables

We use as controls several firm-specific characteristics that have been shown to affect equity returns by earlier studies.$^{16}$ Following Fama and French (1992), we control for the market beta, size, and book-to-market equity ratio of a firm. We estimate the market beta $(BETA)$ of individual stocks using monthly returns over the past five years. We calculate the natural logarithm of each stock’s market capitalization $(SIZE)$ and its book-to-market equity $(BM)$ ratio at the end of each month. To control for the medium-term momentum effect of Jegadeesh and Titman (1993), we measure the momentum return $(MOM)$ of each

---

$^{8}$ http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html  
$^{9}$ https://faculty.chicagobooth.edu/faculty/lubos-pastor/data  
$^{10}$ http://global-q.org/factors.html  
$^{11}$ http://finance.wharton.upenn.edu/~stambaug/  
$^{12}$ http://www.kentdaniel.net/data.php  
$^{13}$ https://hobergphillips.tuck.dartmouth.edu/  
$^{14}$ We would like to thank Terrance Odean for kindly sharing his data.  
$^{15}$ The sample period for tests based on household trading activity data is from January 1991 to December 1996. The sample period for tests based on Hoberg and Phillips (2010, 2016) text-based network industry classification data is from July 1989 to December 2020.  
$^{16}$ Table A.1 in the Online Appendix provides a detailed description of the control variables used in our tests. We require that at least 15 (24) non-missing daily (monthly) return observations exist in a month (over the past five years) when we calculate variables with daily (monthly) data.

9

---

# Page 11

stock as its cumulative return during the past 12 months after skipping the most recent month. We also control for the short-term reversal ($STR$) effect of Jegadeesh (1990) using the one-month lagged stock return. Amihud (2002) shows that there exists a positive premium to more illiquid stocks, thus, we calculate the Amihud illiquidity measure ($ILLIQ$), defined as the absolute daily return divided by the daily dollar trading volume averaged over all trading days in each month for each stock. We calculate each stock’s co-skewness ($COSKEW$) following Harvey and Siddique (2000) using monthly return observations over the past five years. Following Ang, Hodrick, Xing and Zhang (2006) who uncover a negative relation between idiosyncratic volatility ($IVOL$) and future equity returns, we calculate idiosyncratic volatility as the standard deviation of the residuals from a regression of daily excess stock returns on the daily excess market return ($MKT$), size ($SMB$), and value ($HML$) factors in each month. Following Bali, Cakici, and Whitelaw (2011), we calculate lottery-like payoffs of a stock by the average of the stock’s five highest daily returns observed during the month ($MAX$). Following Fama and French (2015) and Hou et al. (2015), we control for the cross-sectional pricing effects of investment ($IA$) and profitability ($OP$). Finally, following Bernard and Thomas (1989, 1990), we control for the standardized unexpected earnings surprises ($SUE$).

## 5 Regret and the Cross-Section of Equity Returns

This paper is the first to investigate the cross-sectional relation between regret and future equity returns. First, we present results from univariate portfolio sorts. Second, we report average stock characteristics to have a clear picture of the composition of regret-sorted portfolios. Third, we conduct bivariate portfolio-level analyses to examine the predictive power of regret after controlling for well-known stock characteristics and risk factors. Finally, we present stock-level cross-sectional regression results.

### 5.1 Univariate portfolios of stocks sorted by $REG$

For each month from June 1963 to December 2020, stocks are sorted into quintile portfolios based on their regret measure, $REG$, where quintile 1 (quintile 5) contains stocks with the lowest (highest) $REG$. The breakpoints used to group the stocks are the 20th, 40th, 60th, and 80th percentile values of $REG$ among NYSE-listed stocks. Next, we calculate the one-month-ahead value-weighted average portfolio returns, and this procedure is repeated each month until the sample is exhausted.$^{17}$

---

$^{17}$ Our decision to use NYSE breakpoints and value-weighted portfolios follows earlier studies (e.g., Fama and French (1993, 2015, 2018), Hou, Xue, and Zhang (2015), Stambaugh and Yuan (2017), and Daniel, Hirshleifer, and Sun (2020)), showing that this methodology provides a more stringent test than using breakpoints based on all stocks or equal-weighted portfolios. In Tables A.2–A.4 of the Online Appendix, we show that our conclusions remain intact when we examine equal-weighted portfolios, value-weighted portfolios constructed using breakpoints calculated from CRSP breakpoints, and value-weighted portfolios using all stocks with no price screens, respectively.

10

---

# Page 12

Table 1 reports for each quintile the average $REG$, the next-month average excess return, and the risk-adjusted returns (alphas) based on the CAPM, FF3, FFC, FFCPS, FF5, FF6, FF6PS, Q, and Q+ models. The last row in Table 1 presents the 5–1 average return and alpha spreads for the hedge portfolio that is long in the quintile of stocks with the highest $REG$ and short in the quintile of stocks with the lowest $REG$.

Univariate portfolio sorts indicate a significantly positive relation between regret and next-month average returns. The value-weighted portfolio of stocks with the highest $REG$ earns an average excess return of 0.75% per month, whereas the average excess return on the value-weighted portfolio of stocks with the lowest $REG$ is 0.35% per month. The arbitrage portfolio with a long position in the highest $REG$ stocks and a short position in the lowest $REG$ stocks (High–Low $REG$) earns on average 0.40% per month (or 4.79% per annum) with a Newey-West (1987) $t$-statistic of 3.66.$^{18}$ The last row in Table 1 further presents the next month’s risk-adjusted returns for the High–Low $REG$ portfolio. The CAPM, FF3, FFC, FFCPS, FF5, FF6, FF6PS, Q, and Q+ alpha spreads for the long-short portfolio are all positive, economically large, ranging from 0.29% to 0.61% per month, and highly significant with $t$-statistics in the range of 2.59 and 6.52.$^{19}$

Next, we investigate the source of the economically large risk-adjusted return spreads between the high-$REG$ and low-$REG$ portfolios: Is it due to outperformance by high-$REG$ stocks, underperformance by low-$REG$ stocks, or both? For this, we focus on the economic and statistical significance of the risk-adjusted returns of quintile 1 versus quintile 5 of the value-weighted portfolios. As reported in Table 1, the CAPM, FF3, FFC, FFCPS, FF5, FF6, FF6PS, Q, and Q+ alphas of high-$REG$ stocks are all significantly positive, whereas the corresponding alphas of low-$REG$ stocks are all significantly negative. Thus, we conclude that the significantly positive alpha spread between the high-$REG$ and low-$REG$ stocks is due to both the outperformance by stocks in the highest $REG$ quintile and the underperformance by stocks in the lowest $REG$ quintile.

The results indicate that regret-averse investors dislike stocks with high-$REG$ because of the large differences between their returns and the maximum return that could have otherwise been obtained from alternative investments in the same industry. Hence, investors experience more regret for holding such stocks in their portfolios due to the decrease they cause in their utility as they compare their current wealth as a result of their chosen investment in these stocks with the maximum foregone wealth that could have been obtained instead. Thus, regret-averse investors undervalue high-$REG$ equities and demand extra compensation in the form of higher expected return to hold them in their portfolios, which is confirmed by the significantly positive alphas on high-$REG$ stocks in quintile 5. Accordingly, holding low-$REG$ stocks minimizes investors’ regret. Therefore, regret-averse

---

$^{18}$ Throughout the paper, we calculate $t$-statistics using the Newey-West (1987) procedure with six lags.

$^{19}$ Table A.5 of the Online Appendix documents similar results for the alpha spreads of the High–Low $REG$ arbitrage portfolio obtained from different factor models, ranging from 0.41% to 0.69% per month with $t$-statistics in the range of 3.49 and 6.74.

11

---

# Page 13

investors overvalue low-$REG$ equities whose returns are more appealing under regret theory and accept lower future returns, which is confirmed by the significantly negative alphas on low-$REG$ stocks in quintile 1.

Table 1 shows that the return predictability is driven by both the long and short legs of the arbitrage portfolio. Thus, one may think that the regret premium could potentially be explained by short-sale constraints. To test this conjecture, we focus on alternative subsamples of stocks that would be less prone to such limits to arbitrage. Following D’Avolio (2002), we perform univariate portfolio analysis using samples that exclude small and illiquid stocks. First, we replicate Table 1 using the NYSE stocks only, screening relatively small and illiquid stocks trading at AMEX and NASDAQ. Second, we apply an additional price screen by removing the low-priced NYSE stocks trading below \$5 per share. Third, we implement a size screen by removing the smaller NYSE stocks with market capitalizations that place them in the smallest NYSE size decile. Fourth, we perform a liquidity screen based on the illiquidity measure of Amihud (2002) by excluding the NYSE stocks that belong to the lowest NYSE liquidity decile. Finally, we impose the three screens simultaneously by removing the relatively low-priced, small, and illiquid NYSE stocks. The results are presented in Table A.6 of the Online Appendix.

Table A.6 presents the FF6PS alphas on the value-weighted quintile portfolios formed based on the aforementioned samples of NYSE stocks.$^{20}$ Similar to our earlier findings, the 5–1 alpha spread for the arbitrage portfolio that is long in the quintile of stocks with the highest $REG$ and short in the quintile of stocks with the lowest $REG$ is positive and statistically significant: 0.32% per month with a $t$-statistic of 3.08. For the individual price, size, and liquidity screened samples of NYSE stocks, the FF6PS alpha spreads between the high-$REG$ and low-$REG$ quintiles remain economically large and stable, in the range of 0.32% and 0.33% per month, and with significant $t$-statistics ranging from 3.14 to 3.18. Overall, these results suggest that the regret premium is not explained by liquidity or short-sale constraints.

## 5.2 Average stock characteristics of $REG$-sorted portfolios

Having documented significant return differences between the high-$REG$ and low-$REG$ portfolios, it is important to understand what kind of stocks have high vs. low regret characteristics. We are especially interested in the composition of both the high-$REG$ and low-$REG$ portfolios since the regret premium is driven by the outperformance (underperformance) of high-$REG$ (low-$REG$) stocks.

Table 2 demonstrates that there are significant differences in several firm characteristics

$^{20}$ As shown in Table 1, we use a total of nine different factor models in calculating the risk-adjusted returns (alphas) of $REG$-sorted portfolios. Starting with Table 3 in the paper and Table A.6 in the Online Appendix, we continue presenting the alphas from the 7-factor model (FF6PS) of Fama and French (2018) and Pastor and Stambaugh (2003) with the market (MKT), size (SMB), book-to-market (HML), momentum (MOM), profitability (RMW), investment (CMA), and the liquidity risk (LIQ) factors.

12

---

# Page 14

of high- $REG$ vs. low- $REG$ portfolios. In particular, compared to low- $REG$ stocks, high- $REG$ stocks with positive alpha have lower past month return, higher beta, and lower book-to-market ratio, are relatively larger and less liquid, with high momentum, with lower idiosyncratic volatility and lottery-like payoffs, have higher asset growth and negative unexpected earnings surprises. Earlier studies (e.g., Jegadeesh (1990), Amihud (2002), Ang, Hodrick, Xing, and Zhang (2006), Kumar (2009), and Bali, Cakici, and Whitelaw (2011)) find that the firm characteristics considered in Table 2 are instrumental in determining the cross-section of expected equity returns. Specifically, equities with lower one-month lagged return, lower liquidity, higher momentum, lower idiosyncratic volatility, and lower lottery demand tend to have higher expected returns. $^{21}$ Considering these prior findings in the literature and the patterns that the firm characteristics exhibit across the $REG$ quintiles, one may think that some of these return predictors drive the significantly positive relation between $REG$ and future stock returns. Thus, in the following two subsections, we test whether the predictive power of regret remains significant after controlling for all of these well-known, robust return predictors in the bivariate portfolios and multivariate Fama-MacBeth regressions.

### 5.3 Bivariate portfolios of $REG$ and the control variables

In this subsection, we conduct dependent bivariate portfolio sorts using 12 control variables. Specifically, we form value-weighted quintile portfolios at the end of each month by first sorting stocks into quintile portfolios based on one of the control variables. Next, we divide each quintile of stocks sorted by the control variable into quintiles based on $REG$ to generate $5 \times 5$ portfolios for each of the control variable and $REG$ . Subsequently, we average each of the $REG$ -sorted portfolios across the control variable quintiles, producing portfolios with dispersion in regret that are similar in terms of the control variable of interest. In addition, we form a portfolio that is long in the resulting high- $REG$ portfolio and short in the resulting low- $REG$ portfolio (High–Low $REG$ portfolio). $^{22}$

Table 3 reports the one-month-ahead FF6PS alphas for each of these five value-weighted portfolios averaged across the control quintiles. After controlling for 12 stock characteristics, the last column in Table 3 shows that all of the spread portfolios (High–Low $REG$ portfolio) command significantly positive next-month returns, with the FF6PS alpha spreads ranging from 0.51% to 0.84% per month with $t$ -statistics in the range of 5.40 and 9.53. A notable point in Table 3 is that even when controlling for size, momentum, liquidity, short-term reversal, idiosyncratic volatility, and lottery demand (potential drivers of the regret premium according to Table 2), the positive relation between regret and future returns remains highly

---

$^{21}$ We also note that $IVOL$ , $MAX$ , and $MOM$ characteristics are not monotonically increasing or decreasing across the $REG$ quintiles.

$^{22}$ We also perform independent bivariate portfolio sorts. The results from these independent bivariate sorts are reported in Table A.7 of the Online Appendix and they are similar to those obtained from dependent sorts presented in Table 3.

13

---

# Page 15

significant.

Harvey, Liu, and Zhu (2016) investigate 316 documented factors related to cross-sectional pricing effects and find that many of the documented predictors of stock returns capture the same underlying economic phenomena. Thus, the number of orthogonal drivers of expected stock returns is likely to be substantially lower. Harvey et al. (2016) indicate that due to data mining and the large amount of research examining the cross-section of expected returns, a five percent level of significance is too low a threshold, and emphasize that a new return predictor needs to clear a much higher hurdle, with a $t$ -statistic greater than 3.0. Besides the theoretical foundation of regret as described in Section 3, the $t$ -statistics of the alpha spreads on the value-weighted univariate and bivariate portfolios presented in Tables 1 and 3 are all above 3 (except the CAPM alpha spread in Table 1 with a $t$ -stat of 2.59) so that the newly proposed regret measure passes the more demanding significance thresholds arising from correlated multiple testing, data mining, and publication bias concerns highlighted by Harvey et al. (2016).

### 5.4 Firm-level cross-sectional regressions

We should note that the univariate and bivariate sort analyses are performed at the portfolio level and could suffer from the aggregation effect due to restraining individual stock-level information in the cross-section. To mitigate the aggregation effects and to control for the potential impact of other stock characteristics simultaneously, we run Fama and MacBeth (1973) regressions at the individual stock level while controlling for a large set of firm characteristics:

$$
r_{i,t+1} = \lambda_{0,t} + \lambda_{REG,t} REG_{i,t} + \lambda_{X,t} X_{i,t} + \epsilon_{i,t+1},
\quad (6)
$$

where $r_{i,t+1}$ is the excess return of stock $i$ in month $t+1$ , $REG_{i,t}$ is the regret arising from investing in stock $i$ in month $t$ as defined in Eq.(5), and $X_{i,t}$ denotes the set of controls representing the characteristics of stock $i$ in month $t$ , which are short-term return reversal ( $STR$ ), market beta ( $\beta^{MKT}$ ), log of market capitalization measured in millions of dollars ( $SIZE$ ), log of book-to-market ratio ( $BM$ ), momentum ( $MOM$ ), illiquidity ( $ILLIQ$ ), co-skewness ( $COSKEW$ ), idiosyncratic volatility ( $IVOL$ ), lottery-like payoffs ( $MAX$ ), operating profitability ( $OP$ ), annual growth rate of total assets ( $IA$ ), and standardized unexpected earnings surprise ( $SUE$ ). $^{23}$

Table 4 presents the time-series average of the cross-sectional intercepts and slope coefficients from the monthly cross-sectional regressions of one-month-ahead excess returns on $REG$ and different sets of stock characteristics for the period from July 1963 to December

---

$^{23}$ It is widely acknowledged that market beta is measured with substantial error for individual stocks. In order to make sure that measurement error in betas does not have an impact on our results, we repeat Fama-MacBeth regressions by removing market beta. Table A.8 of the Online Appendix show that our results remain robust to the removal of beta.

14

---

# Page 16

2020. The first specification examines the cross-sectional relation between regret and one-month-ahead stock returns without any controls. Consistent with our findings from the univariate portfolio sorts, Column 1 of Table 4 provides evidence of a positive and significant relation between $REG$ and one-month-ahead returns, with an average slope of 0.011 and a $t$-statistic of 6.44. The economic magnitude of the associated effect is greater than that documented in Table 1 for the value-weighted univariate portfolios of $REG$. The spread in average $REG$ between quintile 1 and 5 is 70.14 ($= 71.68 - 1.53$), and multiplying this spread by the average slope of 0.011 yields an estimated monthly return spread of 0.76%.$^{24,25}$

Having confirmed the significantly positive relation between REG and future returns at the individual stock level via univariate Fama and MacBeth (1973) regressions, we next control for a battery of stock characteristics. Following Fama and French (1992, 1993), Jegadeesh and Titman (1993), and Carhart (1997), we first control for the market beta, size, and book-to-market in Specification (2), and then add momentum in Specification (3). Finally, we sequentially add illiquidity, coskewness, idiosyncratic volatility, and MAX in Specification (4), operating profitability and asset growth rate in Specification (5), and unexpected earnings surprise (SUE) in Specification (6). Specifications (7) through (12) replicate the same set of regressions while including the short-term reversal as an additional control variable.$^{26}$ The last column in Table 4 presents results from the most comprehensive regression specification combining all of the 12 return predictors examined. After controlling for a wide range of stock characteristics, we still document a positive and robust relation between stocks’ regret prospects and their future returns. The positive average slope of 0.006 ($t$-stat. = 5.13) on $REG$ in the last column represents a sizable economic effect of 0.41% per month for the regret premium, controlling for everything else. Overall, these results show

---

$^{24}$ The ordinary least squares (OLS) methodology used in the Fama-MacBeth regressions gives an equal weight to each cross-sectional observation so that the regression results are more aligned with the equal-weighted portfolios. That is why the economic significance of $REG$ obtained from Fama-MacBeth regressions, 0.76% per month, is higher than the 0.40% per month obtained from the value-weighted portfolios (see Table 1), but very close to the 0.79% per month obtained from the equal-weighted portfolios (see Table A.2).

$^{25}$ A potential problem of using OLS methodology in Fama-MacBeth regressions is that assigning equal weight to each cross-sectional observation could result in overweighting the microcap stocks, which could in turn drive the significant regret premium. In order to rule out the potential impact of microcap stocks, we further conduct Fama-MacBeth regressions based on the market cap weighted least-squares (WLS) methodology. The results are presented in Table A.8 of the Online Appendix. The significantly positive regret premium in all specifications based on WLS Fama-MacBeth regressions indicates that our results are not driven by overweighting small stocks.

$^{26}$ Several observations are worth mentioning regarding the control variables. Consistent with earlier studies, the value effect is positive and significant and stocks exhibit intermediate-term momentum and short-term return reversals. The lottery demand (MAX) effect remains significantly negative in all specifications. In line with Fama and French (2015) and Hou, Xue, and Zhang (2015), stocks with high profitability (high asset growth) generate high (low) future returns. Furthermore, unexpected earnings surprise is significantly positively related to future stock returns, confirming the post-earnings-announcement-drift phenomenon. Size and illiquidity are negatively related to future stock returns, but they are not significant in all specifications. Idiosyncratic volatility changes sign from positive to negative when the short-term return reversal is controlled for and it is insignificant in some specifications. Consistent with Harvey and Siddique (2000), co-skewness is negatively related to future returns but statistically weak in some specifications. Finally, the market beta does not display a robust, significant relation with future returns.

15

---

# Page 17

that regret has distinct, significant information beyond established firm characteristics, and it is a strong and robust predictor of future equity returns, confirming our main finding that regret is priced in the cross-section of individual stocks.

# Additional Analyses and Robustness Checks

In this section, we conduct additional analyses to strengthen the link between regret and investors' trading behavior and perform a battery of robustness checks. First, using household-level data, we examine if our proposed measure of regret is linked to real-life individual investor trading behavior. Second, we examine the interaction between investor regret and loss aversion. Third, we test whether regret measures constructed with longer estimation windows behave in a similar way to our main measure of regret, and then investigate the relation between regret and the short-term reversal effect. Fourth, we examine if regret can be related to a potential mispricing effect. Fifth, we explore whether industry lead-lag effect and pairs-trading can explain the observed $REG$ premium. Sixth, we conduct subperiod analyses to examine whether the predictive power of regret is driven by good vs. bad states of the economy. Seventh, we test the cross-sectional persistence and longer-term predictability of regret. Finally, we construct an investable factor based on our regret measure ( $FREG$ ) and test whether $FREG$ is spanned by established factor models.

## Regret and household trading

It is likely that the regret measure that we introduce can be confounded with other factors that are not necessarily linked to investors' regret stemming from their investment in a particular stock. In order to provide a more direct link between our proposed measure of regret and investor trading behavior, we construct an investor-based regret measure that is tightly linked to our proposed regret-based framework and measure as outlined in Section 3 and Eq. (5). In particular, using investor trading activity and position statements of 78,000 households at a large US-based brokerage firm, we examine whether household trading activity reflects trading behavior that is consistent with regret theory and our proposed measure of regret.[^1] We proceed as follows.

For each month $t$ from January 1991 to December 1996, first we start by calculating return on a particular stock $i$ owned or disposed of by household $j$ , i.e., $ret_{j,i,t}$ , by solving:

$$
\sum_{n=0}^{N} \frac{CF_n}{(1 + ret_{j,i,t})^{\frac{n}{21}}} = 0,
$$

where $CF_n$ is the cash flow at time $n$ in the period from the date on which an initial position in the stock appeared on household $j$ 's brokerage account to month $t$ . $CF_n$ has

[^1]: For detailed information about household trading data, see Odean (1998, 1999) and Barber and Odean (2001, 2002).

---

# Page 18

a negative sign for stock buying and a positive sign for stock selling. As such, $ ret_{j,i,t} $ is a money-weighted return that considers the trading activity of individual households due to buying, holding, and selling stock $ i $ . Furthermore, it is a monthly measure assuming that there are 21 trading days in a month.

Next, we take the average of $ ret_{j,i,t} $ across all households' holding or trading stock $ i $ in month $ t $ , denoted $ ret_{i,t} $ , and use this aggregate investor-level return to measure investors' average degree of regret for investing in stock $ i $ in the month, i.e., $ REGINDEX_{i,t} $ . Specifically, $ REGINDEX_{i,t} $ is defined as:

$$
REGINDEX_{i,t} = -(ret_{i,t} - \max_k [ret_{k,t}]),
$$

where $ \max_k [ret_{k,t}] $ is the highest $ ret_t $ of stock $ i $ 's peer group $ k $ , which consists of stocks operating in: (i) the same 2-digit SIC industry (SIC2), (ii) the same 3-digit SIC industry (SIC3), (iii) the same Fama-French industry (FF10 Industry), (iv) the same state (STATE), or (v) the same metropolitan statistical area (MSA). $^{28}$

The advantage of using an investor trading-based aggregate regret index as described above is its ability to track investors' trading activity from the date on which an initial position in a stock appeared on a household brokerage account, which could be as early as January 1991 (the start of household trading data) to the end of month $ t $ (portfolio formation month). Hence, investors' regret depends on the timing of purchase and holding of the stock and how its return performs as opposed to the counterfactual return, which is what regret theory would predict. Since in a given month, different investors will have different levels of regret for different stocks depending on the timing of their purchase of the stocks, $ REGINDEX $ successfully captures and summarizes variations in regret from household to household.

We start our analysis first by investigating how investors' demand and corresponding portfolio choices relate to regret. In particular, using the changes in the average weights assigned to individual stocks held by individual investors for each regret-based portfolio in the portfolio formation month ( $ t $ ), i.e., the month when regret is experienced, as well as changes in the weights in the five months that follow ( $ t + 1 $ to $ t + 5 $ ), we test whether there is a significant change in investors' portfolio choices following regret. Table 5 reports the average weights assigned to individual stocks across the $ REGINDEX $ quintiles as well as the difference between the average weights allocated to stocks in the highest and lowest $ REGINDEX $ quintiles.

Table 5 shows that the average weight assigned to high-regret stocks decreases by 0.21\% and the average weight assigned to low-regret stocks increases by 0.43\% during portfolio formation month ( $ t $ ). Furthermore, the difference between the average weights allocated to

[^1]: $^{28}$ We further construct a value-weighted version of $ REGINDEX $ ( $ VW-REGINDEX $ ) with weights measured by individual households' initial costs of the position in a stock. The results of univariate portfolio sorts using $ VW-REGINDEX $ are presented in Section A.4 and Table A.10 of the Online Appendix.

---

# Page 19

stocks in the highest and lowest regret portfolios is $-0.60\%$ and highly significant ($t$-stat = $-12.10$). The findings suggest that investors demand more (less) of low-regret (high-regret) stocks after observing their regret, leading to a regret-driven price pressure and the corresponding regret premium. On the other hand, the differences in the monthly change in weights following the portfolio formation month ($t+1$ to $t+5$) are statistically insignificant, suggesting that the demand-related mechanism is mostly prominent in the month when regret is first experienced.$^{29}$

To conclude our analysis based on household-level regret, for each month from January 1991 to December 1996, we sort stocks into quintile portfolios based on $REGINDEX$ (following five different counterfactual returns), and examine their future value-weighted returns. Table 5 reports the next-month FF6PS alpha for each quintile, as well as the alpha spreads for the hedge portfolio that is long in the quintile of stocks with the highest $REGINDEX$ and short in the quintile of stocks with the lowest $REGINDEX$.

Regardless of the industry-based benchmark used to calculate counterfactual return that determine investors’ regret, second, third, and fourth columns of Table 5 show that stocks with high average regret accross investors earn higher returns than stocks with low average regret, with the portfolio that is long in the highest $REGINDEX$ quintile and short in the lowest $REGINDEX$ quintile earning statistically significant and positive returns ranging from $0.53\%$ to $0.63\%$.$^{30}$ Furthermore, the last two columns of the table report next-month FF6PS alphas of the value-weighted portfolios sorted by $REGINDEX$ calculated using alternative counterfactual returns based on geographical proximity to the invested stock, i.e., the maximum return on a stock that operates in the same state (STATE) or in the same metropolitan statistical area (MSA) with the invested stock. Columns 5 and 6 of Table 5 show that our main result extends beyond the use of industry benchmarks and remains robust to the use of alternative counterfactual returns that regret-averse and attention-limited (or familiarity bias driven) investors could take into account in determining their regret.

Overall, our analysis based on an individual investor-based regret index constructed following the intuition behind our proposed regret framework yields very similar results to our main analysis and offers household trading-level evidence on the implications of regret in the cross-sectional pricing of equities.

---

$^{29}$ An alternative explanation is that the observed regret premium arises due to mispricing of stocks in the highest- and lowest-regret quintiles that may cause their prices to deviate temporarily from their expected values. We explore this alternative mechanism in Section A.5 of the Online Appendix. Our results presented in Tables A.11 and A.12 of the Online Appendix suggest that mispricing of stocks in the highest- and lowest-regret portfolios during the portfolio formation month and a follow-up mean reversal cannot fully account for the observed regret premium.

$^{30}$ These magnitudes are very similar to the FF6PS alpha spread of $0.57\%$ reported in Table 1 based on the main measure of regret and obtained over the full sample period.

18

---

# Page 20

## 6.2 Regret and loss aversion

Although stemming from different theories (regret vs. prospect theory), it is possible that regret and loss aversion are related, and thus investors’ experience of regret might depend on a reference point. In this section, we investigate whether the regret effect depends on a reference point by testing if the regret premium is stronger (weaker) when investors are in their loss (gain) domain. Arguably, when investors are in gain (loss), they probably feel less (more) regret pain. Together with mental accounting (e.g., narrow framing), this argument could imply a stronger regret effect among stocks when their average investors are in their loss domain. To examine the impact of loss aversion on regret premium, we perform bivariate portfolio analysis by sorting stocks first based on the stock-level capital gain overhang ( $CGO$ ) measure of Grinblatt and Han (2005) and then on our regret measure ( $REG$ ). $^{31}$

Table A.13 of the Online Appendix reports the FF6PS alphas for $5 \times 5$ portfolios sorted by $CGO$ and $REG$ . Both dependent (Panel A) and independent (Panel B) bivariate portfolio sort results presented in Table A.13 suggest that the pricing effect of investor regret is indeed stronger for stocks in the low $CGO$ quintile (loss domain) than that in the high $CGO$ quintile (gain domain), i.e., 0.81% (0.83%) vs. 0.64% (0.62%) alpha spread in the loss vs. gain domains based on dependent (independent) sorts. However, the difference in the pricing effect is statistically insignificant.

## 6.3 Regret and short-term return reversal

The results in Tables 3 and 4 show that controlling for the short-term reversal ( $STR$ ) effect, regret premium remains highly significant. In this section, we present further evidence that our proposed regret measure is distinct from the $STR$ effect.

### 6.3.1 Alternative measures of regret from longer estimation windows

We first construct alternative measures of regret based on longer estimation windows ranging from two to 12 months:

$$
REG_{i,t-n:t} = -(ret_{i,t-n:t} - \max_k [ret_{k,t-n:t}]),
\quad \text{(9)}
$$

where $ret_{i,t-n:t}$ is stock $i$ ’s cumulative return over the past $t-n$ to $t$ months ( $n$ ranging from 2 to 12 months); and $\max_k [ret_{k,t-n:t}]$ is the maximum cumulative return of stocks within the same three-digit SIC industry.

Next, for each month from July 1963 to December 2020, we sort stocks into quintile portfolios based on alternative measures of $REG_{t-n:t}$ , and examine their future value-weighted returns. Panel A of Table 6 shows that even if our regret measure is constructed

---

$^{31}$ This refined test is similar in spirit with the recent findings of Wang et al. (2017) and An et al. (2020) showing that investors’ preference for lottery-like stocks is stronger when facing losses.

---

# Page 21

over longer-horizon returns (both for the stock return and the benchmark return), a portfolio that is long in high $REG_{t-n:t}$ stocks and short in low $REG_{t-n:t}$ stocks continue to earn positive and significant FF6PS alphas, ranging from 0.23% to 0.48% per month with $t$ -statistics in the range of 2.90 and 5.00. We also note that the predictive power of $REG$ becomes economically smaller (in relative terms) as estimation window, $n$ , increases.

Panel B of Table 6 presents the time-series average of the cross-sectional intercepts and slope coefficients from the monthly cross-sectional regressions of stocks’ $n$ -month-ahead excess returns on $REG_{i,t-n:t}$ and the same set of control variables. $^{32}$ The results of FM regressions presented in Panel B of Table 6 corroborate our univariate sort results, indicating that when it is constructed using longer-term estimation windows, the significant and positive risk premium associated with regret remains intact for periods up to 12 months. $^{33}$

### 6.3.2 Further robustness tests for the relation between regret and STR

In this section, we provide further robustness tests to distinguish our regret measure, $REG$ , from short-term reversal, $STR$ . We start our analyses by orthogonalizing (i) $REG$ with respect to $STR$ ( $REG\_Orth$ ), and (ii) $STR$ with respect to $REG$ ( $STR\_Orth$ ), to make sure that the orthogonalized component of $REG$ is independent of $STR$ and the orthogonalized component of $STR$ is independent of $REG$ . In particular, we regress (i) $REG$ on $STR$ , and (ii) $STR$ on $REG$ , respectively, and use the residuals from these monthly cross-sectional regressions as the orthogonalized measures of $REG$ and $STR$ $^{34}$

Panel A of Table A.9 of the Online Appendix shows that both $REG$ and $REG\_Orth$ have relatively low correlations with $STR$ and $STR\_Orth$ , respectively, suggesting that our proposed measure of regret as defined in Eq.(5) (or orthogonalized version of $REG$ with respect to $STR$ ) contains information well beyond the stock’s past one-month return. Next, we replicate Table 1 and form value-weighted quintile portfolios of $STR$ , $REG$ , $STR\_Orth$ , and $REG\_Orth$ with NYSE breakpoints for the period June 1963–December 2020. Panel B of Table A.9 reports the FF6PS alphas for the quintile portfolios as well as the FF6PS spreads for the hedge portfolio that is long in the quintile of stocks with the highest $STR$ , $REG$ , $STR\_Orth$ , or $REG\_Orth$ and short in the quintile of stocks with the lowest $STR$ , $REG$ , $STR\_Orth$ , or $REG\_Orth$ , respectively. One striking result is that neither $STR$ nor $STR\_Orth$ can predict next-month returns. On the other hand, regardless of using the raw or orthogonalized measure of regret, the positive relation between regret and future returns remains robust and highly significant.

Next, we construct $5 \times 5$ dependent bivariate portfolios of $STR\_Orth$ controlling for

---

$^{32}$ We further add the stock’s cumulative return over the past $n$ months as an additional control.

$^{33}$ To avoid potential measurement error in the estimation of market betas, we also run Fama-MacBeth regressions without market beta and our results remain robust to the removal of beta from the regression specifications.

$^{34}$ See Section A.4 of the Online Appendix and Eq. (10) and Eq. (11) for details about the construction of orthogonalized measures of $REG$ and $STR$ .

20

---

# Page 22

$REG$ and bivariate portfolios of $REG\_Orth$ controlling for $STR$ . Panel A of Table A.10 of the Online Appendix shows that, the FF6PS alpha spread between high- and low- $STR\_Orth$ quintiles is insignificant except for the stocks in the lowest- $REG$ quintile. On the other hand, Panel B of Table A.10 indicates that the FF6PS alpha spread between high- and low- $REG\_Orth$ quintiles is positive and significant for all $STR$ quintiles, regardless of the past one-month return of the stock, ranging from 0.25% to 0.58% per month with $t$ -statistics in the range of 1.99 and 3.54. $^{35}$ Finally, we average each of the $STR\_Orth$ ( $REG\_Orth$ ) sorted portfolios across the five $REG$ ( $STR$ ) quintiles, producing portfolios with dispersion in past one-month return (regret) that are similar in terms of regret (their past one-month return). The last column of Panel A (Panel B) of Table A.10 shows that while the FF6PS spread for high- and low- $STR\_Orth$ portfolio that is similar in terms of regret is insignificant ( $-0.13\%$ with $t$ -stat $=-0.93$ ), the FF6PS spread for high- and low- $REG\_Orth$ that is similar in terms of past one-month return remains highly significant ( $0.41\%$ with $t$ -stat $=5.58$ ). $^{36}$ Overall, the cross-sectional correlations, the univariate and bivariate portfolio analyses suggest that regret is a distinct measure of investor characteristic, which contains information well beyond the stock’s past month return. $^{37}$

## 6.4 $REG$ and industry-related explanations

This section provides additional tests to examine the robustness of our proposed regret measure to alternative industry-related explanations, such as industry short-term reversal, industry pairs-trading due to mispricing, and industry lead-lag effects.

### 6.4.1 $REG$ and industry-STR effect

At first sight, Eq. (5) might suggest that our proposed measure of regret could be very sensitive to loser and winner stocks in a certain industry, and thus, high- (low-) $REG$ stocks might be interpreted as tightly linked to short-term industry losers (winners). In that respect, a strategy that is long in high-regret-stocks and short in low-regret-stocks could be potentially capturing a within-industry short-term reversal (STR) strategy, which according to Hameed and Mian (2015), produces higher profits and survive the control of standard short-term return reversal.

However, by definition, $REG$ has two components and investors’ regret is determined not only by the stock’s own return but also as a result of its comparison with respect to the maximum return on the stock that operates in the same industry with the invested

---

$^{35}$ We obtain similar results with independent bivariate portfolio sorts.

$^{36}$ Furthermore, we show that our results based on bivariate sorts of orthogonalized versions of regret and $STR$ extend to raw measures of regret and $STR$ . The results are presented in Table A.11 of the Online Appendix. In particular, the table shows that, except for the stocks lowest- $REG$ quintile, $STR$ anomaly disappears when regret is controlled for in bivariate portfolio sorts.

$^{37}$ Table A.12 of the Online Appendix shows that the short-term reversal effect (tested with univariate portfolios) is not a strong, robust phenomenon as most of the alpha spreads are statistically insignificant. Table A.13 further shows that the $STR$ effect is driven by small and illiquid stocks.

21

---

# Page 23

stock, suggesting that a stock that might appear as short-term loser (winner) in a certain industry does not necessarily imply it being a high- (low-) regret stock.$^{38}$

Furthermore, our analyses in Section 6.1 based on household trading data and corresponding results reported in Table 5 suggest that our findings are not sensitive to the use of industry benchmark returns as counterfactuals in the definition of regret, and extend further to settings when regret is defined using alternative counterfactuals based on geographical proximity with the invested stock, i.e., the maximum return on a stock operating in the same state or metropolitan statistical area with the invested stock. Since the data and analyses in Section 6.1 are based on a limited number of stocks and investors and cover a relatively short sample period, we repeat a similar analysis in this section using alternative definitions of regret ($REG\_1$, $REG\_2$, $REG\_3$, and $REG\_4$) based on the counterfactuals as described in Section 6.1, but this time using all the stocks in our sample and over the full sample period.

In particular, for each month from July 1963 to December 2020, we sort stocks into quintile portfolios based on one of the four alternative proxies for regret and present the FF6PS alphas of $REG$-sorted quintile portfolios as well as the alpha spreads of the four High–Low $REG$ hedge portfolios. Table A.14 of the Online Appendix shows that using alternative benchmarks to evaluate regret based on different industry classifications or geographical locations of company headquarters still yield positive and significant FF6PS alphas for the spread portfolio, ranging from 0.35% to 0.55% with $t$-statistics in the range of 3.38 and 4.29.$^{39}$ Hence, even if we consider another plausible alternative, i.e., geographical proximity, that investors could potentially use to measure their regret, our main finding that stocks with high (low) regret earn higher (lower) future returns remains robust across alternative definitions of regret.

Finally, in order to make sure that our results are not driven by within-industry STR effect, we conduct both dependent and independent bivariate portfolio sorts controlling for the industry-adjusted STR effect as documented by Hameed and Mian (2015).$^{40}$ Table A.16

---

$^{38}$ To give an example, take two stocks A and B from two different industries earning -10% and 10% in a given month, respectively. The maximum return in the two industries that stocks A and B operate are recorded by stocks C and D earning 20% and 70%, respectively. Hence, according to Eq. (5) $REG_A = -(R_A - R_C) = 30$ and $REG_B = -(R_B - R_D) = 60$. Suppose also that stock A’s return was the lowest return in its industry whereas stock B’s return was the second highest return in its industry following stock D. So, although stock A is a short-term loser in its own industry (due to achieving the lowest return in its industry), it will be classified as a low-$REG$ stock according to our definition. Furthermore, stock B can be viewed as a short term winner in its own industry because it obtained the second highest return in its industry following stock D, however it will be classified as a high-$REG$ stock according to our definition. Thus, since regret-averse investors do not only judge a stock based on its return but also how the stock performs based on its industry benchmark (i.e., top performing stock in its industry), our example shows that an industry loser (winner) stock might well be classified as low- (high-) regret stock depending on how the stock performs with respect to its benchmark return.

$^{39}$ As an additional industry benchmark, we further use the text-based network industry classification (TNIC) of Hoberg and Phillips (2010, 2016) for robustness and our results remain robust to calculation of $REG$ based on TNIC. The results of this analysis is discussed in Section A.5.1 and Table A.15 of the Online Appendix.

$^{40}$ Following Hameed and Mian (2015), industry-adjusted STR is defined as the stock’s past month-return

22

---

# Page 24

of the Online Appendix suggest that High–Low $REG$ hedge portfolios continue to exhibit significant and positive returns even after controlling for industry-adjusted STR effect.

### 6.4.2 $REG$ and mispricing

In order to rule out the possibility that our results are driven by mispricing or costly arbitrage, we first perform bivariate portfolio sorts and then FM regressions controlling for the mispricing factor (MISP) of Stambaugh, Yu and Yuan (2015). As reported in Panel A of Table A.17, FF6PS alphas obtained from both dependent and independent bivariate portfolio sorts after controlling for MISP remain significantly positive for the High–Low $REG$ hedge portfolios. The average FF6PS spread across MISP quintiles is 0.63% (0.64%) with a $t$ -statistic of 5.98 (5.89) based on dependent (independent) bivariate sorts. Furthermore, Panel B of Table A.17 points towards a significant and positive risk premium for $REG$ even after controlling for a set of factors including size, idiosyncratic volatility, beta, MAX, and MISP that could be related to costly arbitrage and mispricing.

### 6.4.3 $REG$ , industry lead-lag effect, and industry pairs-trading

In this section, we start by examining if $REG$ picks up potential intra-industry lead-lag effects. In particular, we perform bivariate portfolio sorts controlling for the industry lead-lag effect. We construct two variables for the industry lead-lag effect: monthly value-weighted returns of the Fama-French 49 industries ( $IND49$ ) and monthly value-weighted returns of the 3-digit-SIC industries ( $SIC3$ ). Panel A (B) of Table A.18 of the Online Appendix presents the FF6PS alphas of $5 \times 5$ dependent (independent) bivariate portfolios of $REG$ controlling for monthly value-weighted industry returns using $IND49$ or $SIC3$ . $^{41}$ Regardless of the sorting methodology and the proxy used for the industry lead-lag effect, all of the spread (High–Low $REG$ ) portfolios command significantly positive FF6PS alpha spreads, confirming our previous results that high- $REG$ stocks continue to earn significantly higher returns than low- $REG$ stocks after controlling for industry lead-lag effects.

Next, we run Fama and MacBeth (1973) regressions at the individual stock level controlling for a large set of characteristics, the industry lead-lag effect, and the potential mispricing effect. Table A.19 of the Online Appendix presents the time-series average of the cross-sectional intercepts and slope coefficients from these monthly cross-sectional regressions. Consistent with our previous findings, we observe a positive and significant relation between $REG$ and one-month-ahead returns, even after controlling for potential mispricing and industry-related lead-lag effects as well as other well-known stock characteristics. Overall,

---

$^{41}$ Hou (2007) shows that the industry lead-lag effect is primarily driven by slow diffusion of information from big firms to small firms. Therefore, the industry lead-lag relation based on value-weighted industry returns is expected to be stronger. Hence, following Hou (2007), we focus on the value-weighted industry returns in the analysis. We further repeat the tests using equal-weighted industry returns and obtain qualitatively similar results.

23

---

# Page 25

the results presented in this section rule out the potential alternative explanation that regret can be driven by the previously documented industry lead-lag effects or industry pairs-trading due to potential mispricing.

## Subperiod analysis

This section explores whether the positive relation between regret and next-month stock returns is driven by different characteristics of the overall market. In particular, we divide our full sample period from July 1963 to December 2020 into two subperiods defined by different business cycles (expansions vs. recessions), economic activity (normal/high vs. low economic activity), economic uncertainty (high vs. low economic uncertainty), market volatility (high vs. low option implied market volatility), and time period (July 1963–December 1991 vs. January 1992–December 2020).[^1]

Table A.20 of the Online Appendix shows that the positive relation between $REG$ and future returns is significant across different sample periods.

## Cross-sectional persistence and longer-term predictability

In this section, we investigate the persistence of $REG$ by constructing a portfolio transition matrix that shows the percentage of stocks staying in the same quintile or moving from one $REG$ -sorted quintile in month $t$ to another $REG$ -sorted quintile in month $t + 1$ , $t + 3$ , $t + 6$ , $t + 9$ , and $t + 12$ , respectively. Table A.21 of the Online Appendix shows that the probability of a stock staying in the lowest (highest) $REG$ quintile is 40.42\% (57.32\%), 40.81\% (54.92\%), 39.28\% (52.08\%), 38.05\% (49.65\%), and 36.81\% (48.08\%) after one, three, six, nine, and 12 months, respectively. Given that the unconditional probability of a stock staying in the same $REG$ quintile is 20\%, the results imply that regret is a persistent phenomenon and stocks in the lowest and highest $REG$ quintiles have a strong likelihood of staying in the same portfolio even after 12 months.[^2]

The empirical results documented in Section 5 point at a positive and strong relation between regret and stocks’ one-month-ahead returns. We now test whether this positive relation holds for longer-term returns. To that end, each month over the period June

[^1]: We classify different cycles of the economy using the National Bureau of Economic Research’s (NBER) definition of US Business Cycle Expansions and Contractions. We denote with zero (one) months that correspond to NBER expansions (recessions). We classify different cycles of economic activity using the three-month moving average of the Chicago Fed National Activity Index (CFNAIMA3). We identify months with CFNAIMA3 index less than or equal to (greater than) –0.7 as months with low (high) economic activity. Our definition of economic uncertainty follows Jurado, Ludvigson, and Ng (2015) (hereafter JLN). We define months with high (low) economic uncertainty when the JLN economic uncertainty index is greater (lower) than its median over the full sample period. For market volatility, we use the end of month level of VIX index (S\&P 500 index option implied volatility) and define months with high (low) market uncertainty when the VIX index is greater (lower) than its median over the period of January 1990–December 2020.
[^2]: We further investigate whether the returns of stocks that are persistently in the high and low regret quintiles (persistent) are different from returns of stocks that become high or low regret for the first time (newcomer) and find that the abnormal returns of newcomer and persistent stocks exhibit similar patterns across lowest and highest regret quintiles.

---

# Page 26

1963–December 2020 we form value-weighted quintile portfolios of $ REG $ with NYSE breakpoints, and calculate 2- to 6-month-ahead FF6PS alphas for each quintile as well as for the hedge portfolio. The FF6PS alphas presented in Table A.22 of the Online Appendix indicate that the cross-sectional predictability of regret is not a one-month affair extending to medium-term returns. $ REG $ can predict risk-adjusted returns up to five months into the future. The predictive ability of $ REG $ diminishes after five months. Overall, our analyses in this subsection suggest that regret is not only a persistent phenomenon but it is also highly related to future stock returns beyond one month extending up to five months. This result further differentiates our regret measure from the short-term reversal effect, which is a one-week to one-month phenomenon (e.g., Lehmann (1990) and Jegadeesh (1990)).

## Regret factor mimicking portfolio (FREG)

Our main finding based on our newly proposed measure of regret is that stocks with high- $ REG $ outperform stocks with low- $ REG $ . Stambaugh and Yuan (2017) and Daniel, Hirshleifer and Sun (2020) contribute to the literature by introducing behavioral and mispricing factors, and our key variable $ REG $ also has a behavioral foundation related to investors’ behavioral and psychological biases. In Section A.7 of the Online Appendix, we propose a new factor ( $ FREG $ ) and test whether the existing factor models explain the newly proposed FREG factor. The results from the factor spanning regressions presented in Table A.23 of the Online Appendix indicate that $ FREG $ generates statistically significant raw and risk-adjusted returns that cannot be fully explained by established risk, mispricing, or behavioral factors.

# Regret and the sources of return predictability

We test whether costly arbitrage and informational frictions provide an explanation to the observed regret premium.

## Costly arbitrage

Our main result can be viewed as investors underprice (overprice) equities with higher (lower) regret, and therefore, stocks that generate high (low) regret experience abnormally high (low) future returns until the mispricing vanishes. The prior literature generally relies on firm size, illiquidity, and firm’s age to capture arbitrage costs (e.g., Shleifer and Vishny (1997), Amihud (2002), and Stambaugh, Yu, and Yuan (2015)). Thus, we test if costly arbitrage (or arbitrage risk) provides an explanation for the observed regret premium by investigating the interactions between $ REG $ and illiquidity, firm size and age.

We start our analysis by first sorting stocks into terciles every month based on the three proxies of arbitrage costs; illiquidity, size, and age. Next, we divide each liquidity, size, and age tercile into quintiles based on $ REG $ to generate $ 3 \times 5 $ portfolios of costly arbitrage

---

# Page 27

and $REG$. Subsequently, we average each of the $REG$-sorted portfolios across the three terciles, producing portfolios with dispersion in regret that are similar in terms of liquidity, size, and age. Finally, we form an arbitrage portfolio (High–Low $REG$ portfolio) and perform a differences in differences (diff-in-diff) analysis to test whether the regret premium generated by high vs. low illiquidity, small vs. big, and young vs. mature tercile of stocks are significantly different from each other.

Panel A of Table 7 shows that after controlling for illiquidity, size, and age in dependent sorts, the FF6PS alpha spreads between the high- and low-$REG$ portfolios remain economically large, in the range of 0.30% and 1.06% per month, and highly significant with $t$-statistics ranging from 2.55 to 8.78. Although the regret premium is significant across liquidity, size and age terciles, we observe that the FF6PS alpha spreads between high- and low-$REG$ portfolios are both economically larger and statistically more significant for illiquid, smaller, and younger stocks. To test the significance of this difference, we perform a diff-in-diff analysis, and report the difference in FF6PS spread of High–Low $REG$ portfolios between high vs. low illiquidity, small vs. big, and young vs. mature tercile of stocks, and present the coefficients and the corresponding $t$-statistics of the difference in the last column and the last row of each bivariate sort. The results indicate that the illiquid, small and young stocks generate much higher regret premium in the form of higher FF6PS spreads, compared to the liquid, large, and mature firms; i.e., 0.55%, 0.45%, and 0.42% higher FF6PS alpha spreads, respectively.

It is important to highlight the fact that, in all the stock samples that we examine, the significantly positive regret premium is driven by both the long and short legs of the arbitrage portfolio, i.e., by buying stocks with high regret and shorting stocks with low regret. Average stock characteristics of $REG$-sorted portfolios as reported in Table 2 suggest that the short leg of the portfolio (i.e., stocks with low regret) on average contain smaller and relatively illiquid stocks. Hence, shorting small/illiquid stocks might not be as easy due to arbitrage costs. Thus, costly arbitrage could be a partial explanation to the observed regret premium.

## 7.2 Informational frictions

Market reactions to large movements in individual stock returns can generate important insights on how the market processes information about positive vs. negative price shocks that may influence the information efficiency of the equity market. We conjecture that large positive vs. negative price shocks that generate low vs. high regret as defined in Eq.(5) are harder to interpret by average investors compared to the direct and well-defined information events studied in the previous literature. Thus, consistent with Hirshleifer, Hsu, and Li (2013), who emphasize that investors would have more difficulty in processing information that is less tangible, we conjecture that the elusive nature of regret thus makes

26

---

# Page 28

it harder for investors to follow stocks with high information uncertainty.$^{44}$

Following the literature, we use institutional holdings ($INST$) as the main proxy for information frictions. As we do in the previous subsection, we further use firm size ($SIZE$) and analyst coverage ($CVRG$) as alternative proxies for information frictions. Stocks with low (high) institutional holdings, and small (big) market cap, and low (high) analyst coverage are shown by earlier studies to be subject to more (less) information frictions. Thus, the information frictions hypothesis predicts that the return predictability should be more (less) pronounced for stocks that are largely held by more uninformed (informed) traders.

Panel B of Table 7 shows that the FF6PS alpha spreads between the high- and low-$REG$ quintiles are positive and highly significant in all the terciles that proxy for information frictions. However, stocks with low institutional ownership, smaller firms, and stocks with low analyst coverage have economically larger FF6PS alpha spreads than stocks with high institutional ownership, larger firms, and stocks with high analyst coverage, respectively. Although the diff-and-diff analysis of the FF6PS spreads of stocks with high vs. low institutional holdings does not generate a statistically significant difference ($t$-stat = $-1.11$), the economic magnitude is large; i.e., stocks with low institutional ownership generate 0.21% higher alpha than stocks with high institutional ownership. Furthermore, small firms and firms with low analyst coverage generate much higher FF6PS alpha spreads (i.e., 0.45%, and 0.33%, respectively) compared to large firms and firms with high analyst coverage. Hence, the regret premium is much stronger for stocks with high information frictions held by uninformed traders.

Overall, our findings from investigating the economic underpinnings of the return predictability of regret offer important insights. Small, young, and illiquid stocks with low institutional ownership and low analyst coverage are held by unsophisticated, uninformed retail investors, so due to informational frictions, information about these stocks is not incorporated into stock prices quickly, thus their return predictability is high. These stocks are also associated with high regret. On the other hand, big, mature, and liquid stocks with high institutional ownership and high analyst coverage are largely held by sophisticated, informed institutional investors, so information about these stocks is incorporated into stock prices quickly, thus their return predictability is low. We document that these stocks are associated with low regret.

Hence, our analyses suggest that regret can be induced by costly arbitrage and/or informational frictions in the equity market. Whether it is arbitrage risk or uninformed trading that may cause investors to hold unattractive stocks or miss the opportunity to hold

$^{44}$ There is also substantial empirical evidence that investor inattention can lead to underreaction to information. See, e.g. Huberman and Regev (2001), Hirshleifer and Teoh (2003), Hirshleifer, Hou, Teoh, and Zhang (2004), Hou and Moskowitz (2005), Barber and Odean (2008), Da, Engelberg, and Gao (2011), Da, Gurun and Warachka (2014), Bali, Peng, Shen, and Tang (2014), and Birru (2015). These studies show that, due to limited investor attention, stock prices underreact to public information about stock fundamentals and characteristics.

27

---

# Page 29

attractive stocks, the results indicate that investors experience regret due to not achieving the highest possible return in the same industry with their stock investment. In line with investors’ aversion to stocks with high regret and investors’ preference for stocks with low regret, our empirical findings demonstrate a theoretically consistent, positive relation between regret and future equity returns.

## 8 Conclusion

This paper introduces a measure of regret for stock market investors ($REG$) and examines its cross-sectional asset pricing implications. Following an extension of the modified expected utility function à la Bell (1982) and Loomes and Sugden (1982), we propose a novel regret measure for stock investments and show that the comparison of a stock’s realized return with the best foregone return that could have been obtained by investing in a similar stock is an important factor in determining investors’ modified utility as it captures the variation in investors’ current wealth with the foregone wealth opportunity. Using this key variable, we investigate whether $REG$ predicts the cross-sectional variation in future stock returns.

We first document that regret is positively related to the cross-section of future equity returns. Sorting individual stocks into value-weighted portfolios based on their $REG$, we show that stocks with high regret outperform stocks with low regret. The results indicate that regret-averse investors dislike (prefer) stocks which generate high (low) regret because investing in such stocks decrease investors’ utility more (less) than other stocks. As a result, stocks with high (low) regret earn higher (lower) future returns in equilibrium. Second, the positive relation between regret and expected returns is robust to using alternative factor models in the calculation of risk-adjusted returns (alphas), different portfolio weighting schemes, controlling for a number of stock characteristics, screening out small, illiquid, and low-priced stocks, and over different periods and stock samples. Multivariate Fama and MacBeth (1973) regressions that simultaneously control for individual stock characteristics further corroborate our main finding that regret is an important determinant of the cross-sectional dispersion in equity returns. Third, using household trading data and following the intuition behind our proposed regret framework for stock investments, we develop an investor-based regret index ($REGINDEX$) and show that $REGINDEX$ predicts stock returns in a similar way to our proposed regret measure. Fourth, we construct alternative regret measures using longer estimation windows ranging from two to 12 months and document that investor regret premium is robust across different estimation periods. Fifth, we document that regret is a highly persistent phenomenon and has cross-sectional predictive ability that goes beyond one month extending up to five months. Regret is also a distinct investor characteristic that is not spanned by established risk or behavioral factor models. Finally, we investigate the economic underpinnings of the observed regret premium, and find that investors do regret by holding unattractive stocks or missing the opportunity to hold attractive stocks due to costly arbitrage and informational frictions.

28

---

# Page 30

# References

Amihud, Y., 2002. “Illiquidity and stock returns: Cross-section and time-series effects.” *Journal of Financial Markets* 5, 31–56.

An, L., Wang, H., Wang, J., Yu, J., 2020. “Lottery-related anomalies: The role of reference-dependent preferences.” *Management Science* 66, 473–501.

Ang, A., Hodrick, R. J., Xing, Y., Zhang, X., 2006. “The cross-section of volatility and expected returns.” *Journal of Finance* 61, 259–299.

Bali, T. G., Cakici, N., Whitelaw, R. F., 2011. “Maxing out: Stocks as lotteries and the cross-section of stock returns.” *Journal of Financial Economics* 99, 427–446.

Bali, T. G., Peng, L., Shen, Y., Tang, Y., 2014. “Liquidity shocks and stock market reactions.” *Review of Financial Studies* 27, 1434–1485.

Ball, R., Brown, P., 1968. “An empirical evaluation of accounting numbers.” *Journal of Accounting Research* 6, 159–178.

Barber, B., Odean, T., 2000. “Trading is hazardous to your wealth: The common stock investment performance of individual investors.” *Journal of Finance* 55, 773–806.

Barber, B., Odean, T., 2001. “Boys will be boys: Gender, overconfidence, and common stock investment.” *Quarterly Journal of Economics* 21, 261–292.

Barber, B., Odean, T., 2008. “All that glitters: The effect of attention on the buying behavior of individual and institutional investors.” *Review of Financial Studies* 21, 785–818.

Balseiro, S. R., Gur, Y., 2019. “Learning in repeated auctions with budgets: Regret minimization and equilibrium.” *Management Science* 65, 3952–3968.

Bell, D. E., 1982. “Regret in decision making under uncertainty.” *Operations Research* 29, 1156–1166.

Bell, D. E., 1983. “Risk premiums for decision regret.” *Management Science* 56, 961–981.

Bernard, V., Thomas, J., 1989. “Post-earnings announcement drift: Delayed price response or risk premium?” *Journal of Accounting Research* 27, 1–36.

Bernard, V., Thomas, J., 1990. “Evidence that stock prices do not fully reflect the implications of current earnings for future earnings.” *Journal of Accounting and Economics* 13, 305–340.

Bikhchandani, S., Segal, U., 2014. “Transitive regret over statistically independent lotteries.” *Journal of Economic Theory* 152, 237–248.

Birru, J., 2015. “Confusion of confusions: A test of the disposition effect and momentum.” *Review of Financial Studies* 28, 1849–1873.

Bleichrodt, H., Cillo, A., Diecidue, E., 2010. “A quantitative measurement of regret theory.” *Management Science* 56, 161–175.

Buturak, G., Evren, O., 2017. “Choice overload and asymmetric regret.” *Theoretical Economics* 12, 1029–1056.

Camille, N., Coricelli, G., Sallet, J., Pradat-Diehl, P., Duhamel, J. R., Sirigu, A., 2004. “The involvement of orbitofrontal cortex in the experience of regret.” *Science* 304, 1167–1170.

Carhart, M., 1997. “On persistence in mutual fund performance.” *Journal of Finance* 52, 57–82.

29

---

# Page 31

Chen, Z., Liu, B., Wang, H., Wang, Z., Yu, J., 2020. “Characteristics-based factors.” *Working paper*.

Coricelli, G., Critchley, H. D., Joffily, M., Sirigu, A., Dolan, R. J., 2005. “Regret and its avoidance: A neuroimaging study of choice behavior.” *Nature Neuroscience* 8, 1255–1262.

Da, Z., Engelberg, J., Gao, P., 2011. “In search for attention.” *Journal of Finance* 66, 1461–1499.

Da, Z., Gurun, U. G., Warachka, M., 2014. “Frog in the pan: Continuous information and momentum.” *Review of Financial Studies* 27, 2171–2218.

Daniel, K., Hirshleifer, D., Sun, L., 2020. “Short- and long-horizon behavioral factors.” *Review of Financial Studies* 33, 1673–1736.

Diecidue, E., Somasundaram, J., 2017. “Regret theory: A new foundation.” *Journal of Economic Theory* 172, 88–119.

Engelbrecht-Wiggans, R., 1989. “The effects of regret on optimal bidding in auctions.” *Management Science* 35, 685–692.

Fama, E. F., MacBeth, J., 1973. “Risk, return and equilibrium: Empirical tests.” *Journal of Political Economy* 81, 607–636.

Fama, E. F., French, K. R., 1992. “The cross-section of expected stock returns.” *Journal of Finance* 46, 427–466.

Fama, E. F., French, K. R., 1993. “Common risk factors in the returns on stocks and bonds.” *Journal of Financial Economics* 33, 3–56.

Fama, E. F., French, K. R., 1997. “Industry costs of equity.” *Journal of Financial Economics* 43, 153–193.

Fama, E. F., French, K. R., 2015. “A five-factor asset pricing model.” *Journal of Financial Economics* 116, 1–22.

Fama, E. F., French, K. R., 2018. “Choosing factors.” *Journal of Financial Economics* 128, 234–252.

Fogel, S. O., Berry, T., 2006. “The disposition effect and individual investor decisions: The roles of regret and counterfactual alternatives.” *Journal of Behavioral Finance* 7, 107–116.

Frydman, C., Camerer, C., 2016. “Neural evidence of regret and its implications for investor behavior.” *Review of Financial Studies* 29, 3108–3139.

Gollier, C., 2020. “Aversion to risk of regret and preference for positively skewed risks.” *Economic Theory* 70, 913–941.

Grinblatt, M., Han, B., 2005. “Prospect theory, mental accounting, and momentum.” *Journal of Financial Economics* 78, 311–339

Gul, F., 1991. “A theory of disappointment aversion.” *Econometrica* 59, 667–686.

Hameed, A., Mian, G. M., 2015. “Industries and stock return reversals.” *Journal of Financial and Quantitative Analysis* 50, 89–117.

Harvey, C. R., Siddique, A., 2000. “Conditional skewness in asset pricing tests.” *Journal of Finance* 55, 1263–1295.

Harvey, C. R., Liu, Y., Zhu, H., 2016. “... and the cross-section of expected returns.” *Review of Financial Studies* 29, 5–68.

30

---

# Page 32

Hayashi, T., 2008. “Regret aversion and opportunity dependence.” *Journal of Economic Theory* 139, 242–268.

Hazan, E., Kale, S., 2015. “An online portfolio selection algorithm with regret logarithmic in price variation.” *Mathematical Finance* 25, 288–310.

Hirshleifer, D., Teoh, S. H., 2003. “Limited attention, information disclosure, and financial reporting” *Journal of Accounting and Economics* 36, 337–386.

Hirshleifer, D., Hou, K., Teoh, S. H., Zhang, Y., 2004. “Do investors overvalue firms with bloated balance sheets?” *Journal of Accounting and Economics* 38, 297–331.

Hirshleifer, D., Hsu, P.-H., Li, D., 2013. “Innovative efficiency and stock returns.” *Journal of Financial Economics* 107, 632–654.

Hoberg, G., Phillips, G., 2010. “Product market synergies and competition in mergers and acquisitions: A text-based analysis.” *Review of Financial Studies* 23, 3773–3811.

Hoberg, G., Phillips, G., 2010. “Text-based network industries and endogenous product differentiation.” *Journal of Political Economy* 124, 1423–1465.

Hou, K., 2007. “Industry information diffusion and the lead-lag effect in stock returns” *Review of Financial Studies* 20, 1113–1138.

Hou, K., Moskowitz, T., 2005. “Market frictions, price delay, and the cross-section of expected returns” *Review of Financial Studies* 18, 981–1020.

Hou, K., Xue, C., Zhang, L., 2015. “Digesting anomalies: An investment approach.” *Review of Financial Studies* 28, 650–705.

Hou, K., Xue, C., Zhang, L., 2020. “Replicating anomalies.” *Review of Financial Studies* 20, 2019–2133.

Hou, K., Mo, H., Xue, C., Zhang, L., 2021. “An augmented q-factor model with expected growth.” *Review of Finance* 25, 1–41.

Huberman, G., Regev, T., 2001. “Contagious speculation and a cure for cancer: A non-event that made stock prices soar.” *Journal of Finance* 56, 387–396.

Jegadeesh, N., 1990. “Evidence of predictable behavior of security returns.” *Journal of Finance* 45, 881–898.

Jegadeesh, N., Titman, S., 1993. “Returns to buying winners and selling losers: Implications for stock market efficiency.” *Journal of Finance* 48, 65–91.

Jiang, B., Narasimhan, C., Turut, O., 2017 “Anticipated regret and product innovation.” *Management Science* 63, 4308–4323.

Jurado, K., Ludvigson, S., Ng, S., 2015. “Measuring uncertainty.” *American Economic Review* 105, 1177–1216.

Kahneman, D., Tversky, A., 1979. “Prospect theory: An analysis of decision under risk.” *Econometrica* 47, 263–291.

Kumar, A., 2009. “Who gambles in the stock market?” *Journal of Finance* 64, 1889–1933.

Leland, J. W., 1998. “Similarity judgments in choice under uncertainty: A reinterpretation of the predictions of regret theory.” *Management Science* 44, 659–672.

Loomes, G., Sugden, R., 1982. “Regret theory: An alternative theory of rational choice under uncertainty.” *Economic Journal* 92, 805–824.

Muermann, A., Mitchell, O., Volkman, J., 2006. “Regret, portfolio choice, and guarantees in defined contribution schemes.” *Insurance: Mathematics and Economics* 39, 219–229.

31

---

# Page 33

Nasiry, J., Popescu, I., 2012. “Advance selling when consumers regret.” *Management Science* 58, 1160–1177.

Newey, W. K., West, K. D., 1987. “A simple, positive semi-definite, heteroscedasticity and autocorrelation consistent covariance matrix.” *Econometrica* 55, 703–708.

Odean ,T., 1998. “Are investors reluctant to realize their losses?” *Journal of Finance* 53, 1775–1798.

Odean ,T., 1999. “Do investors trade too much?” *American Economic Review* 89, 1279–1298.

Orphanides, A., Zervos, D., 1995. “Rational addiction with learning and regret.” *Journal of Political Economy* 103, 739–758.

Pastor, L., Stambaugh, R. F., 2003. “Liquidity risk and expected stock returns.” *Journal of Political Economy* 111, 642–685.

Qin, J., 2015. “A model of regret, investor behavior, and market turbulence.” *Journal of Economic Theory* 160, 150–174.

Quiggin, J., 1994. “Regret theory with general choices.” *Journal of Risk and Uncertainty* 8, 153–165.

Sarver, T., 2008. “Anticipating regret: Why fewer options may be better.” *Econometrica* 76, 263–305.

Savage, L. J., 1951. “The theory of statistical decision.” *Journal of the American Statistical Association* 46, 55–67.

Shleifer, A., Vishny, R. W., 1997. “The limits of arbitrage” *Journal of Finance* 52, 35–55.

Solnik, B., Zuo, L., 2012. “A global equilibrium asset pricing model with home preference.” *Management Science* 58, 273–292.

Stambaugh, R. F., Yu, J., Yuan, Y., 2012. “‘The short of it: Investor sentiment and anomalies.” *Journal of Financial Economics* 104, 288–302.

Stambaugh, R. F., Yu, J., Yuan, Y., 2014. “‘The long of it: Odds that investor sentiment spuriously predicts anomaly returns.” *Journal of Financial Economics* 114, 613–619.

Stambaugh, R. F., Yu, J., Yuan, Y., 2015. “Arbitrage asymmetry and the idiosyncratic volatility puzzle.” *Journal of Finance* 70, 1903–1948.

Stambaugh, R. F., Yuan, Y., 2017. “Mispricing factors.” *Review of Financial Studies* 30, 1270–1315.

Vera, A., Banerjee, S., 2021. “The Bayesian prophet: A low-regret framework for online decision making.” *Management Science* 67, 1368–1391.

Wang, H., Yan, J., Yu, J., 2017. “Reference-dependent preferences and the risk-return trade-off..” *Journal of Financial Economics* 123, 395–414.

Zeelenberg, M., Pieters, R., 2007. “A theory of regret regulation 1.0.” *Journal of Consumer Psychology* 17, 3–18.

Zou, T., Zhou, B., Jiang, B., 2020. “Product-line design in the presence of consumers’ anticipated regret.” *Management Science* 66, 5665–5682.

---

# Page 34

Table 1

**Univariate portfolios of stocks sorted by $REG$**

Each month from June 1963 to December 2020, stocks are sorted into quintile portfolios based on their $REG$ using NYSE breakpoints. This table reports, for each quintile, the average $REG$ values, the next-month value-weighted average excess returns (Mean), and the risk-adjusted returns (alphas) from the CAPM, FF3, FFC, FFCPS, FF5, FF6, FF6PS, Q, and Q+ models. The last row of in each panel presents the 5–1 average raw and risk-adjusted return spreads on the arbitrage portfolio with a long position in the portfolio of highest $REG$ stocks (quintile 5) and a short position in the portfolio of lowest $REG$ stocks (quintile 1). Newey-West adjusted $t$-statistics are given in square brackets.

<table>
  <thead>
    <tr>
      <th>Quintile</th>
      <th>REG</th>
      <th>Mean</th>
      <th>CAPM</th>
      <th>FF3</th>
      <th>FFC</th>
      <th>FFCPS</th>
      <th>FF5</th>
      <th>FF6</th>
      <th>FF6PS</th>
      <th>Q</th>
      <th>Q+</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1 (Low)</td>
      <td>1.53</td>
      <td>0.35</td>
      <td>−0.17</td>
      <td>−0.22</td>
      <td>−0.22</td>
      <td>−0.20</td>
      <td>−0.33</td>
      <td>−0.31</td>
      <td>−0.30</td>
      <td>−0.32</td>
      <td>−0.30</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>2.04</td>
      <td>−3.74</td>
      <td>−3.19</td>
      <td>−5.77</td>
      <td>−4.92</td>
      <td>−4.60</td>
    </tr>
    <tr>
      <td>2</td>
      <td>10.13</td>
      <td>0.42</td>
      <td>−0.05</td>
      <td>−0.10</td>
      <td>−0.10</td>
      <td>−0.08</td>
      <td>−0.19</td>
      <td>−0.18</td>
      <td>−0.17</td>
      <td>−0.20</td>
      <td>−0.18</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>2.69</td>
      <td>−2.04</td>
      <td>−1.65</td>
      <td>−4.15</td>
      <td>−3.90</td>
      <td>−3.59</td>
      <td>−3.35</td>
      <td>−3.37</td>
    </tr>
    <tr>
      <td>3</td>
      <td>18.04</td>
      <td>0.56</td>
      <td>0.03</td>
      <td>−0.02</td>
      <td>−0.04</td>
      <td>−0.04</td>
      <td>−0.14</td>
      <td>−0.14</td>
      <td>−0.16</td>
      <td>−0.16</td>
      <td>−0.16</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>3.28</td>
      <td>−0.37</td>
      <td>−0.82</td>
      <td>−2.86</td>
      <td>−2.88</td>
      <td>−2.95</td>
      <td>−2.78</td>
      <td>−2.89</td>
    </tr>
    <tr>
      <td>4</td>
      <td>28.73</td>
      <td>0.71</td>
      <td>0.12</td>
      <td>0.09</td>
      <td>0.08</td>
      <td>0.06</td>
      <td>0.04</td>
      <td>0.03</td>
      <td>0.02</td>
      <td>−0.03</td>
      <td>−0.04</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>3.71</td>
      <td>1.57</td>
      <td>1.03</td>
      <td>0.67</td>
      <td>0.63</td>
      <td>0.29</td>
      <td>−0.47</td>
    </tr>
    <tr>
      <td>5 (High)</td>
      <td>71.68</td>
      <td>0.75</td>
      <td>0.12</td>
      <td>0.17</td>
      <td>0.20</td>
      <td>0.17</td>
      <td>0.27</td>
      <td>0.29</td>
      <td>0.26</td>
      <td>0.28</td>
      <td>0.27</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>3.73</td>
      <td>3.34</td>
      <td>3.22</td>
      <td>5.28</td>
      <td>5.27</td>
      <td>4.65</td>
      <td>4.27</td>
    </tr>
    <tr>
      <td>High−Low</td>
      <td>70.14</td>
      <td>0.40</td>
      <td>0.29</td>
      <td>0.39</td>
      <td>0.41</td>
      <td>0.37</td>
      <td>0.60</td>
      <td>0.60</td>
      <td>0.57</td>
      <td>0.61</td>
      <td>0.58</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>3.66</td>
      <td>4.10</td>
      <td>3.79</td>
      <td>6.52</td>
      <td>6.30</td>
      <td>5.67</td>
      <td>4.95</td>
      <td>5.15</td>
    </tr>
  </tbody>
</table>

33

---

# Page 35

Table 2

**Average stock characteristics of $REG$-sorted portfolios**

This table reports the average stock characteristics of $REG$-sorted portfolios for the sample period from July 1963 to December 2020. The stock characteristics are the short-term return reversal (STR), the market beta (BETA), the market value of equity measured in billions of dollars (SIZE), the book-to-market ratio (BM), the return momentum (MOM), the illiquidity (ILLIQ), the co-skewness (COSKEW), the idiosyncratic volatility (IVOL), the lottery payoff (MAX), the operating profitability (OP), the asset growth (IA), and the standardized unexpected earnings surprise (SUE), respectively. The last two rows report the difference in average stock characteristics between portfolio of highest $REG$ stocks (quintile 5) and portfolio of lowest $REG$ stocks (quintile 1), and the corresponding Newey-West adjusted $t$-statistics in brackets, respectively.

<table>
  <thead>
    <tr>
      <th>Quintile</th>
      <th>REG</th>
      <th>STR</th>
      <th>BETA</th>
      <th>SIZE</th>
      <th>BM</th>
      <th>MOM</th>
      <th>ILLIQ</th>
      <th>COSKEW</th>
      <th>IVOL</th>
      <th>MAX</th>
      <th>OP</th>
      <th>IA</th>
      <th>SUE</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1 (Low)</td>
      <td>1.54</td>
      <td>10.69</td>
      <td>1.27</td>
      <td>2.07</td>
      <td>0.90</td>
      <td>20.06</td>
      <td>1.55</td>
      <td>−0.04</td>
      <td>2.33</td>
      <td>3.89</td>
      <td>0.06</td>
      <td>0.15</td>
      <td>0.04</td>
    </tr>
    <tr>
      <td>2</td>
      <td>10.15</td>
      <td>3.24</td>
      <td>1.13</td>
      <td>3.04</td>
      <td>0.89</td>
      <td>16.87</td>
      <td>1.26</td>
      <td>−0.03</td>
      <td>1.76</td>
      <td>2.79</td>
      <td>0.02</td>
      <td>0.14</td>
      <td>−0.01</td>
    </tr>
    <tr>
      <td>3</td>
      <td>18.05</td>
      <td>1.07</td>
      <td>1.19</td>
      <td>2.75</td>
      <td>0.88</td>
      <td>17.85</td>
      <td>1.52</td>
      <td>−0.04</td>
      <td>1.82</td>
      <td>2.74</td>
      <td>0.03</td>
      <td>0.15</td>
      <td>−0.04</td>
    </tr>
    <tr>
      <td>4</td>
      <td>28.76</td>
      <td>−0.58</td>
      <td>1.25</td>
      <td>2.44</td>
      <td>0.85</td>
      <td>19.21</td>
      <td>1.72</td>
      <td>−0.04</td>
      <td>1.95</td>
      <td>2.81</td>
      <td>0.02</td>
      <td>0.17</td>
      <td>−0.06</td>
    </tr>
    <tr>
      <td>5 (High)</td>
      <td>71.75</td>
      <td>−2.09</td>
      <td>1.39</td>
      <td>2.53</td>
      <td>0.77</td>
      <td>23.99</td>
      <td>1.84</td>
      <td>−0.03</td>
      <td>2.23</td>
      <td>3.06</td>
      <td>−0.03</td>
      <td>0.22</td>
      <td>−0.06</td>
    </tr>
    <tr>
      <td>High−Low</td>
      <td>70.21</td>
      <td>−12.77</td>
      <td>0.12</td>
      <td>0.46</td>
      <td>−0.13</td>
      <td>3.93</td>
      <td>0.29</td>
      <td>0.00</td>
      <td>−0.10</td>
      <td>−0.83</td>
      <td>−0.09</td>
      <td>0.07</td>
      <td>−0.10</td>
    </tr>
    <tr>
      <td></td>
      <td>[20.23]</td>
      <td>[−55.71]</td>
      <td>[5.93]</td>
      <td>[5.99]</td>
      <td>[−8.38]</td>
      <td>[3.20]</td>
      <td>[2.89]</td>
      <td>[1.22]</td>
      <td>[−4.53]</td>
      <td>[−21.96]</td>
      <td>[−1.81]</td>
      <td>[9.47]</td>
      <td>[−10.90]</td>
    </tr>
  </tbody>
</table>

---

# Page 36

Table 3

**Dependent bivariate portfolio sorts of $REG$ and the control variables**

Each month from June 1963 to December 2020, stocks are sorted into value-weighted quintile portfolios based on one of the control variables using NYSE breakpoints. Next, each quintile of stocks is sorted into quintiles based on $REG$ to generate $5 \times 5$ portfolios for each of the control variable and $REG$ . Control variables are the market beta (BETA), market value of equity (SIZE), book-to-market ratio (BM), momentum (MOM), short-term reversal (STR), co-skewness (COSKEW), illiquidity (ILLIQ), idiosyncratic volatility (IVOL), lottery payoff (MAX), operating profitability (OP), asset growth (IA), and standardized unexpected earnings surprise (SUE), respectively. Subsequently, we average each of the $REG$ -sorted portfolios across the five quintiles producing portfolios with dispersion in regret that are similar in terms of the control variables. In addition, we form an arbitrage portfolio (High–Low $REG$ portfolio) that is long in the resulting high- $REG$ portfolio and short in the resulting low- $REG$ portfolio. The table reports the one-month-ahead FF6PS alphas for each of these five portfolios and the last column presents the 5–1 (High–Low) FF6PS alpha spreads of $REG$ -sorted portfolios averaged across the control quintiles. Newey-West adjusted $t$ -statistics (with six lags) are given in square brackets.

<table>
  <thead>
    <tr>
      <th rowspan="2"> </th>
      <th colspan="6">Quintile</th>
    </tr>
    <tr>
      <th>1 (Low)</th>
      <th>2</th>
      <th>3</th>
      <th>4</th>
      <th>5 (High)</th>
      <th>High-Low</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>BETA</td>
      <td>−0.36</td>
      <td>−0.30</td>
      <td>−0.21</td>
      <td>0.00</td>
      <td>0.21</td>
      <td>0.56</td>
    </tr>
    <tr>
      <td> </td>
      <td>[−6.09]</td>
      <td>[−5.90]</td>
      <td>[−4.10]</td>
      <td>[−0.06]</td>
      <td>[3.59]</td>
      <td>[6.42]</td>
    </tr>
    <tr>
      <td>SIZE</td>
      <td>−0.46</td>
      <td>−0.25</td>
      <td>−0.15</td>
      <td>0.00</td>
      <td>0.35</td>
      <td>0.81</td>
    </tr>
    <tr>
      <td> </td>
      <td>[−8.98]</td>
      <td>[−5.32]</td>
      <td>[−3.36]</td>
      <td>[−0.06]</td>
      <td>[6.70]</td>
      <td>[9.34]</td>
    </tr>
    <tr>
      <td>BM</td>
      <td>−0.40</td>
      <td>−0.23</td>
      <td>−0.14</td>
      <td>0.04</td>
      <td>0.23</td>
      <td>0.63</td>
    </tr>
    <tr>
      <td> </td>
      <td>[−7.63]</td>
      <td>[−4.69]</td>
      <td>[−2.67]</td>
      <td>[0.84]</td>
      <td>[4.68]</td>
      <td>[7.70]</td>
    </tr>
    <tr>
      <td>MOM</td>
      <td>−0.42</td>
      <td>−0.29</td>
      <td>−0.17</td>
      <td>−0.06</td>
      <td>0.18</td>
      <td>0.60</td>
    </tr>
    <tr>
      <td> </td>
      <td>[−7.39]</td>
      <td>[−5.14]</td>
      <td>[−3.18]</td>
      <td>[−1.00]</td>
      <td>[3.36]</td>
      <td>[7.92]</td>
    </tr>
    <tr>
      <td>STR</td>
      <td>−0.30</td>
      <td>−0.22</td>
      <td>−0.10</td>
      <td>−0.03</td>
      <td>0.22</td>
      <td>0.52</td>
    </tr>
    <tr>
      <td> </td>
      <td>[−5.54]</td>
      <td>[−4.53]</td>
      <td>[−2.06]</td>
      <td>[−0.53]</td>
      <td>[4.64]</td>
      <td>[6.37]</td>
    </tr>
    <tr>
      <td>COSKEW</td>
      <td>−0.30</td>
      <td>−0.24</td>
      <td>−0.15</td>
      <td>0.06</td>
      <td>0.27</td>
      <td>0.57</td>
    </tr>
    <tr>
      <td> </td>
      <td>[−5.73]</td>
      <td>[−4.83]</td>
      <td>[−3.01]</td>
      <td>[1.26]</td>
      <td>[4.82]</td>
      <td>[6.46]</td>
    </tr>
    <tr>
      <td>ILLIQ</td>
      <td>−0.51</td>
      <td>−0.25</td>
      <td>−0.17</td>
      <td>0.00</td>
      <td>0.33</td>
      <td>0.84</td>
    </tr>
    <tr>
      <td> </td>
      <td>[−9.31]</td>
      <td>[−5.04]</td>
      <td>[−3.55]</td>
      <td>[−0.04]</td>
      <td>[6.75]</td>
      <td>[9.53]</td>
    </tr>
    <tr>
      <td>IVOL</td>
      <td>−0.38</td>
      <td>−0.23</td>
      <td>−0.24</td>
      <td>−0.02</td>
      <td>0.23</td>
      <td>0.61</td>
    </tr>
    <tr>
      <td> </td>
      <td>[−6.90]</td>
      <td>[−4.59]</td>
      <td>[−4.66]</td>
      <td>[−0.36]</td>
      <td>[3.93]</td>
      <td>[6.83]</td>
    </tr>
    <tr>
      <td>MAX</td>
      <td>−0.34</td>
      <td>−0.20</td>
      <td>−0.23</td>
      <td>0.01</td>
      <td>0.17</td>
      <td>0.51</td>
    </tr>
    <tr>
      <td> </td>
      <td>[−6.48]</td>
      <td>[−3.84]</td>
      <td>[−4.37]</td>
      <td>[0.22]</td>
      <td>[2.73]</td>
      <td>[5.85]</td>
    </tr>
    <tr>
      <td>OP</td>
      <td>−0.38</td>
      <td>−0.23</td>
      <td>−0.20</td>
      <td>−0.10</td>
      <td>0.24</td>
      <td>0.62</td>
    </tr>
    <tr>
      <td> </td>
      <td>[−6.17]</td>
      <td>[−4.28]</td>
      <td>[−3.43]</td>
      <td>[−1.63]</td>
      <td>[4.52]</td>
      <td>[6.41]</td>
    </tr>
    <tr>
      <td>IA</td>
      <td>−0.31</td>
      <td>−0.20</td>
      <td>−0.16</td>
      <td>−0.03</td>
      <td>0.25</td>
      <td>0.56</td>
    </tr>
    <tr>
      <td> </td>
      <td>[−5.22]</td>
      <td>[−3.87]</td>
      <td>[−2.95]</td>
      <td>[−0.57]</td>
      <td>[4.54]</td>
      <td>[5.76]</td>
    </tr>
    <tr>
      <td>SUE</td>
      <td>−0.28</td>
      <td>−0.15</td>
      <td>−0.16</td>
      <td>−0.06</td>
      <td>0.27</td>
      <td>0.55</td>
    </tr>
    <tr>
      <td> </td>
      <td>[−4.59]</td>
      <td>[−2.95]</td>
      <td>[−2.84]</td>
      <td>[−0.92]</td>
      <td>[4.43]</td>
      <td>[5.40]</td>
    </tr>
  </tbody>
</table>

35

---

# Page 37

Table 4

**Stock-level Fama-MacBeth regressions**

This table reports time-series averages of the intercepts and slope coefficients from the monthly cross-sectional regressions of one-month-ahead excess stock returns on $REG$ and a large set of stock characteristics as defined in Eq.(6) for the period of July 1963–December 2020. Newey-West adjusted $t$-statistics (with six lags) are given in square brackets.

<table>
  <thead>
    <tr>
      <th></th>
      <th>(1)</th>
      <th>(2)</th>
      <th>(3)</th>
      <th>(4)</th>
      <th>(5)</th>
      <th>(6)</th>
      <th>(7)</th>
      <th>(8)</th>
      <th>(9)</th>
      <th>(10)</th>
      <th>(11)</th>
      <th>(12)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>REG</td>
      <td>0.011</td>
      <td>0.014</td>
      <td>0.014</td>
      <td>0.011</td>
      <td>0.009</td>
      <td>0.008</td>
      <td>0.007</td>
      <td>0.007</td>
      <td>0.007</td>
      <td>0.008</td>
      <td>0.007</td>
      <td>0.006</td>
    </tr>
    <tr>
      <td></td>
      <td>[6.44]</td>
      <td>[8.23]</td>
      <td>[8.18]</td>
      <td>[7.15]</td>
      <td>[6.70]</td>
      <td>[6.60]</td>
      <td>[4.19]</td>
      <td>[4.94]</td>
      <td>[4.85]</td>
      <td>[5.62]</td>
      <td>[5.65]</td>
      <td>[5.13]</td>
    </tr>
    <tr>
      <td>STR</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>−0.023</td>
      <td>−0.037</td>
      <td>−0.038</td>
      <td>−0.024</td>
      <td>−0.024</td>
      <td>−0.028</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>[−6.76]</td>
      <td>[−9.53]</td>
      <td>[−10.05]</td>
      <td>[−5.11]</td>
      <td>[−4.59]</td>
      <td>[−4.91]</td>
    </tr>
    <tr>
      <td>BETA</td>
      <td>0.039</td>
      <td>−0.005</td>
      <td>0.166</td>
      <td>0.152</td>
      <td>0.173</td>
      <td></td>
      <td></td>
      <td>0.065</td>
      <td>0.026</td>
      <td>0.117</td>
      <td>0.098</td>
      <td>0.117</td>
    </tr>
    <tr>
      <td></td>
      <td>[0.45]</td>
      <td>[−0.07]</td>
      <td>[2.05]</td>
      <td>[1.70]</td>
      <td>[1.86]</td>
      <td></td>
      <td></td>
      <td>[0.69]</td>
      <td>[0.29]</td>
      <td>[1.45]</td>
      <td>[1.10]</td>
      <td>[1.29]</td>
    </tr>
    <tr>
      <td>SIZE</td>
      <td>−0.031</td>
      <td>−0.037</td>
      <td>−0.100</td>
      <td>−0.079</td>
      <td>−0.097</td>
      <td></td>
      <td></td>
      <td>−0.029</td>
      <td>−0.035</td>
      <td>−0.102</td>
      <td>−0.081</td>
      <td>−0.099</td>
    </tr>
    <tr>
      <td></td>
      <td>[−1.08]</td>
      <td>[−1.36]</td>
      <td>[−3.73]</td>
      <td>[−3.10]</td>
      <td>[−3.75]</td>
      <td></td>
      <td></td>
      <td>[−0.99]</td>
      <td>[−1.26]</td>
      <td>[−3.80]</td>
      <td>[−3.18]</td>
      <td>[−3.85]</td>
    </tr>
    <tr>
      <td>BM</td>
      <td>0.215</td>
      <td>0.209</td>
      <td>0.161</td>
      <td>0.201</td>
      <td>0.108</td>
      <td></td>
      <td></td>
      <td>0.222</td>
      <td>0.218</td>
      <td>0.171</td>
      <td>0.215</td>
      <td>0.122</td>
    </tr>
    <tr>
      <td></td>
      <td>[3.82]</td>
      <td>[3.85]</td>
      <td>[3.07]</td>
      <td>[3.36]</td>
      <td>[1.90]</td>
      <td></td>
      <td></td>
      <td>[3.85]</td>
      <td>[3.94]</td>
      <td>[3.19]</td>
      <td>[3.51]</td>
      <td>[2.10]</td>
    </tr>
    <tr>
      <td>MOM</td>
      <td></td>
      <td>0.007</td>
      <td>0.007</td>
      <td>0.005</td>
      <td>0.003</td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.007</td>
      <td>0.007</td>
      <td>0.005</td>
      <td>0.003</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td>[5.73]</td>
      <td>[5.71]</td>
      <td>[4.34]</td>
      <td>[2.92]</td>
      <td></td>
      <td></td>
      <td></td>
      <td>[5.68]</td>
      <td>[5.72]</td>
      <td>[4.29]</td>
      <td>[2.78]</td>
    </tr>
    <tr>
      <td>ILLIQ</td>
      <td></td>
      <td></td>
      <td>−0.016</td>
      <td>−0.020</td>
      <td>−0.018</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>−0.016</td>
      <td>−0.019</td>
      <td>−0.017</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td>[−1.32]</td>
      <td>[−2.98]</td>
      <td>[−2.46]</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>[−1.26]</td>
      <td>[−2.85]</td>
      <td>[−2.42]</td>
    </tr>
    <tr>
      <td>COSKEW</td>
      <td></td>
      <td></td>
      <td>−0.125</td>
      <td>−0.208</td>
      <td>−0.226</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>−0.074</td>
      <td>−0.170</td>
      <td>−0.188</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td>[−1.49]</td>
      <td>[−2.19]</td>
      <td>[−2.23]</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>[−0.86]</td>
      <td>[−1.76]</td>
      <td>[−1.82]</td>
    </tr>
    <tr>
      <td>IVOL</td>
      <td></td>
      <td></td>
      <td>0.101</td>
      <td>0.081</td>
      <td>0.116</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>−0.070</td>
      <td>−0.089</td>
      <td>−0.082</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td>[1.85]</td>
      <td>[1.90]</td>
      <td>[2.83]</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>[−1.39]</td>
      <td>[−1.91]</td>
      <td>[−1.67]</td>
    </tr>
    <tr>
      <td>MAX</td>
      <td></td>
      <td></td>
      <td>−0.289</td>
      <td>−0.270</td>
      <td>−0.284</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>−0.134</td>
      <td>−0.109</td>
      <td>−0.092</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td>[−8.03]</td>
      <td>[−8.35]</td>
      <td>[−9.03]</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>[−3.18]</td>
      <td>[−2.50]</td>
      <td>[−2.00]</td>
    </tr>
    <tr>
      <td>OP</td>
      <td></td>
      <td></td>
      <td></td>
      <td>3.336</td>
      <td>1.824</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>3.631</td>
      <td>2.020</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>[5.05]</td>
      <td>[4.45]</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>[5.07]</td>
      <td>[4.53]</td>
    </tr>
    <tr>
      <td>IA</td>
      <td></td>
      <td></td>
      <td></td>
      <td>−0.325</td>
      <td>−0.221</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>−0.341</td>
      <td>−0.238</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>[−5.35]</td>
      <td>[−3.64]</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>[−5.38]</td>
      <td>[−3.86]</td>
    </tr>
    <tr>
      <td>SUE</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.293</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>0.299</td>
    </tr>
    <tr>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>[12.98]</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>[12.99]</td>
    </tr>
    <tr>
      <td>Intercept</td>
      <td>0.491</td>
      <td>0.593</td>
      <td>0.550</td>
      <td>1.413</td>
      <td>1.312</td>
      <td>1.571</td>
      <td>0.607</td>
      <td>0.723</td>
      <td>0.684</td>
      <td>1.420</td>
      <td>1.323</td>
      <td>1.540</td>
    </tr>
    <tr>
      <td></td>
      <td>[2.28]</td>
      <td>[2.36]</td>
      <td>[2.27]</td>
      <td>[6.09]</td>
      <td>[5.54]</td>
      <td>[6.34]</td>
      <td>[2.77]</td>
      <td>[2.80]</td>
      <td>[2.74]</td>
      <td>[6.23]</td>
      <td>[5.59]</td>
      <td>[6.35]</td>
    </tr>
    <tr>
      <td>Adj. $R^2$</td>
      <td>0.56%</td>
      <td>4.25%</td>
      <td>5.16%</td>
      <td>6.51%</td>
      <td>6.14%</td>
      <td>6.25%</td>
      <td>1.31%</td>
      <td>4.92%</td>
      <td>5.77%</td>
      <td>7.00%</td>
      <td>6.67%</td>
      <td>6.80%</td>
    </tr>
  </tbody>
</table>

---

# Page 38

Table 5

Average monthly changes in the weights assigned to individual stocks across regret-sorted portfolios

Each month from January 1991 to December 1996, stocks are sorted into quintile portfolios based on $ REGINDEX $ constructed using household trading data as defined in Eq. (7) and Eq. (8). Next, using individual investors' stock holdings within each regret-based portfolio, we calculate average monthly changes in the weights assigned to individual stocks for each regret-based portfolio in the portfolio formation month ( $ t $ ), i.e., the month when regret is experienced, as well as changes in the weights in the five months that follow ( $ t + 1 $ to $ t + 5 $ ). The table presents the average monthly changes in the weights assigned to individual stocks across $ REGINDEX $ -sorted quintile portfolios as well as the difference between the average monthly changes assigned to stocks in the highest- $ REGINDEX $ portfolio and the lowest- $ REGINDEX $ portfolio. Newey-West adjusted $ t $ -statistics are given in square brackets.

<table>
  <thead>
    <tr>
      <th>Quintile</th>
      <th> $ t $ </th>
      <th> $ t + 1 $ </th>
      <th> $ t + 2 $ </th>
      <th> $ t + 3 $ </th>
      <th> $ t + 4 $ </th>
      <th> $ t + 5 $ </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1 (Low)</td>
      <td>0.0043</td>
      <td>0.0001</td>
      <td>0.0001</td>
      <td>0.0001</td>
      <td>0.0001</td>
      <td>0.0001</td>
    </tr>
    <tr>
      <td>2</td>
      <td>0.0012</td>
      <td>0.0000</td>
      <td>-0.0001</td>
      <td>-0.0001</td>
      <td>0.0000</td>
      <td>0.0000</td>
    </tr>
    <tr>
      <td>3</td>
      <td>0.0006</td>
      <td>0.0001</td>
      <td>0.0001</td>
      <td>0.0001</td>
      <td>0.0001</td>
      <td>0.0000</td>
    </tr>
    <tr>
      <td>4</td>
      <td>0.0006</td>
      <td>0.0000</td>
      <td>0.0002</td>
      <td>0.0002</td>
      <td>0.0000</td>
      <td>0.0001</td>
    </tr>
    <tr>
      <td>5 (High)</td>
      <td>-0.0021</td>
      <td>0.0003</td>
      <td>0.0001</td>
      <td>0.0001</td>
      <td>0.0001</td>
      <td>0.0001</td>
    </tr>
    <tr>
      <td>High-Low</td>
      <td>-0.0060</td>
      <td>0.0002</td>
      <td>0.0000</td>
      <td>0.0000</td>
      <td>0.0000</td>
      <td>0.0000</td>
    </tr>
    <tr>
      <td></td>
      <td>[-12.10]</td>
      <td>[0.91]</td>
      <td>[0.10]</td>
      <td>[0.10]</td>
      <td>[-0.04]</td>
      <td>[0.15]</td>
    </tr>
  </tbody>
</table>

37

---

# Page 39

Table 6

**Regret index based on household trading data**

Each month from January 1991 to December 1996, stocks are sorted into quintile portfolios based on regret index ($REGINDEX$) constructed using household trading data as defined in Eq. (7) and Eq. (8). We calculate five versions of $REGINDEX$ based on alternative counterfactual returns, i.e., the second term in Eq. (8), that investors could be using as benchmarks while determining their regret. In particular, the five counterfactuals that we consider are: i) the maximum return of the stock that has the same 2-digit SIC code with the invested stock (2-digit SIC), ii) the maximum return of the stock that has the same 3-digit SIC code with the invested stock (3-digit SIC), iii) the maximum return of the stock that belongs to the same industry as the invested stock where the industry definition follows Fama and French (1997) (FF10 industry), iv) the maximum return of the stock headquartered in the same state with the invested stock (State), and v) the maximum return of the stock headquartered in the same metropolitan statistical area with the invested stock (MSA). The table presents the next-month value-weighted FF6PS alphas of the corresponding five $REGINDEX$-sorted quintile portfolios based on each counterfactual, and the alpha spreads for the hedge portfolio that is long in the quintile of stocks with the highest $REGINDEX$ and short in the quintile of stocks with the lowest $REGINDEX$. Newey-West adjusted $t$-statistics are given in square brackets.

<table>
  <thead>
    <tr>
      <th rowspan="2">Quintile</th>
      <th colspan="5">Counterfactual</th>
    </tr>
    <tr>
      <th>2-digit SIC</th>
      <th>3-digit SIC</th>
      <th>FF10 industry</th>
      <th>State</th>
      <th>MSA</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1 (Low)</td>
      <td>−0.33<br>[−2.38]</td>
      <td>−0.25<br>[−2.07]</td>
      <td>−0.25<br>[−1.71]</td>
      <td>−0.01<br>[−0.08]</td>
      <td>−0.04<br>[−0.28]</td>
    </tr>
    <tr>
      <td>2</td>
      <td>0.03<br>[0.34]</td>
      <td>−0.26<br>[−1.96]</td>
      <td>0.01<br>[0.03]</td>
      <td>−0.29<br>[−1.74]</td>
      <td>0.00<br>[0.02]</td>
    </tr>
    <tr>
      <td>3</td>
      <td>−0.03<br>[−0.21]</td>
      <td>0.12<br>[0.81]</td>
      <td>0.08<br>[−0.05]</td>
      <td>−0.15<br>[0.06]</td>
      <td>−0.25<br>[−0.19]</td>
    </tr>
    <tr>
      <td>4</td>
      <td>0.07<br>[0.45]</td>
      <td>−0.01<br>[−0.05]</td>
      <td>−0.05<br>[−0.25]</td>
      <td>0.06<br>[0.49]</td>
      <td>−0.19<br>[−1.32]</td>
    </tr>
    <tr>
      <td>5 (High)</td>
      <td>0.29<br>[1.57]</td>
      <td>0.28<br>[2.17]</td>
      <td>0.34<br>[1.37]</td>
      <td>0.41<br>[3.67]</td>
      <td>0.49<br>[6.73]</td>
    </tr>
    <tr>
      <td>High−Low</td>
      <td>0.63<br>[2.29]</td>
      <td>0.53<br>[2.59]</td>
      <td>0.58<br>[2.03]</td>
      <td>0.42<br>[2.04]</td>
      <td>0.53<br>[3.00]</td>
    </tr>
  </tbody>
</table>

38

---

# Page 40

Table 7

**Regret over longer-term investment horizons**

This table presents the results from the analysis of longer-horizon regret measures constructed over two- to 12-month investment horizons and defined as:

$$
REG_{i,t-n:t} = -(ret_{i,t-n:t} - \max_k [ret_{k,t-n:t}]),
$$

where $ret_{i,t-n:t}$ is stock $i$ ’s cumulative return over the past $t-n$ to $t$ months ( $n$ ranging from 2 to 12 months); and $\max_k [ret_{k,t-n:t}]$ is the maximum cumulative return of stocks within the same three-digit SIC industry. Panel A reports the next-month value-weighted FF6PS alphas of portfolios sorted with respect to $REG$ , and Panel B reports the time-series averages of the intercepts and slope coefficients from the monthly cross-sectional regressions of two-month, three-month, four-month, five-month, six-month, seven-month, eight-month, nine-month, ten-month, eleven-month, and twelve-month-ahead excess stock returns on $REG$ constructed over the corresponding return horizon and a large set of stock characteristics as defined in Eq.(10) for the period of July 1963–December 2020. Newey-West adjusted $t$ -statistics (with six lags) are given in square brackets.

---

**Panel A: Univariate sorts**

*REG based on cumulative returns over the past n months*

<table>
  <thead>
    <tr>
      <th></th>
      <th>n=2</th>
      <th>n=3</th>
      <th>n=4</th>
      <th>n=5</th>
      <th>n=6</th>
      <th>n=7</th>
      <th>n=8</th>
      <th>n=9</th>
      <th>n=10</th>
      <th>n=11</th>
      <th>n=12</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1 (Low)</td>
      <td>-0.27</td>
      <td>-0.29</td>
      <td>-0.22</td>
      <td>-0.21</td>
      <td>-0.16</td>
      <td>-0.15</td>
      <td>-0.11</td>
      <td>-0.11</td>
      <td>-0.08</td>
      <td>-0.05</td>
      <td>-0.08</td>
    </tr>
    <tr>
      <td></td>
      <td>[-4.93]</td>
      <td>[-5.33]</td>
      <td>[-3.92]</td>
      <td>[-4.27]</td>
      <td>[-3.26]</td>
      <td>[-3.15]</td>
      <td>[-2.36]</td>
      <td>[-2.32]</td>
      <td>[-1.77]</td>
      <td>[-1.01]</td>
      <td>[-1.82]</td>
    </tr>
    <tr>
      <td>2</td>
      <td>-0.18</td>
      <td>-0.08</td>
      <td>-0.13</td>
      <td>-0.03</td>
      <td>-0.09</td>
      <td>-0.09</td>
      <td>-0.09</td>
      <td>-0.11</td>
      <td>-0.09</td>
      <td>-0.12</td>
      <td>-0.10</td>
    </tr>
    <tr>
      <td></td>
      <td>[-3.49]</td>
      <td>[-1.88]</td>
      <td>[-2.59]</td>
      <td>[-0.69]</td>
      <td>[-1.83]</td>
      <td>[-1.73]</td>
      <td>[-1.77]</td>
      <td>[-2.21]</td>
      <td>[-1.82]</td>
      <td>[-2.26]</td>
      <td>[-1.83]</td>
    </tr>
    <tr>
      <td>3</td>
      <td>-0.05</td>
      <td>-0.13</td>
      <td>-0.07</td>
      <td>-0.07</td>
      <td>-0.02</td>
      <td>-0.10</td>
      <td>-0.13</td>
      <td>0.00</td>
      <td>-0.07</td>
      <td>-0.10</td>
      <td>-0.12</td>
    </tr>
    <tr>
      <td></td>
      <td>[-0.85]</td>
      <td>[-2.51]</td>
      <td>[-1.42]</td>
      <td>[-1.23]</td>
      <td>[-0.40]</td>
      <td>[-1.79]</td>
      <td>[-2.41]</td>
      <td>[-0.03]</td>
      <td>[-1.35]</td>
      <td>[-1.67]</td>
      <td>[-2.21]</td>
    </tr>
    <tr>
      <td>4</td>
      <td>0.12</td>
      <td>0.09</td>
      <td>0.10</td>
      <td>-0.06</td>
      <td>-0.09</td>
      <td>-0.05</td>
      <td>-0.03</td>
      <td>-0.13</td>
      <td>-0.18</td>
      <td>-0.09</td>
      <td>-0.04</td>
    </tr>
    <tr>
      <td></td>
      <td>[2.31]</td>
      <td>[1.61]</td>
      <td>[1.81]</td>
      <td>[-1.31]</td>
      <td>[-1.81]</td>
      <td>[-1.06]</td>
      <td>[-0.61]</td>
      <td>[-2.27]</td>
      <td>[-2.71]</td>
      <td>[-1.50]</td>
      <td>[-0.71]</td>
    </tr>
    <tr>
      <td>5 (High)</td>
      <td>0.15</td>
      <td>0.19</td>
      <td>0.14</td>
      <td>0.18</td>
      <td>0.18</td>
      <td>0.21</td>
      <td>0.18</td>
      <td>0.17</td>
      <td>0.24</td>
      <td>0.21</td>
      <td>0.16</td>
    </tr>
    <tr>
      <td></td>
      <td>[2.49]</td>
      <td>[3.17]</td>
      <td>[2.64]</td>
      <td>[3.06]</td>
      <td>[3.08]</td>
      <td>[3.59]</td>
      <td>[3.15]</td>
      <td>[3.00]</td>
      <td>[3.41]</td>
      <td>[3.48]</td>
      <td>[2.87]</td>
    </tr>
    <tr>
      <td>High–Low</td>
      <td>0.42</td>
      <td>0.48</td>
      <td>0.36</td>
      <td>0.39</td>
      <td>0.34</td>
      <td>0.36</td>
      <td>0.29</td>
      <td>0.28</td>
      <td>0.32</td>
      <td>0.26</td>
      <td>0.23</td>
    </tr>
    <tr>
      <td></td>
      <td>[4.34]</td>
      <td>[5.00]</td>
      <td>[4.07]</td>
      <td>[4.35]</td>
      <td>[4.01]</td>
      <td>[4.39]</td>
      <td>[3.44]</td>
      <td>[3.36]</td>
      <td>[3.39]</td>
      <td>[2.90]</td>
      <td>[3.02]</td>
    </tr>
  </tbody>
</table>

*(continued on next page)*

---

# Page 41

<table>
  <thead>
    <tr>
      <th>Panel B: FM regressions</th>
      <th>n=2</th>
      <th>n=3</th>
      <th>n=4</th>
      <th>n=5</th>
      <th>n=6</th>
      <th>n=7</th>
      <th>n=8</th>
      <th>n=9</th>
      <th>n=10</th>
      <th>n=11</th>
      <th>n=12</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>REG$_{t-n:t}$</td>
      <td>0.004</td>
      <td>0.003</td>
      <td>0.002</td>
      <td>0.002</td>
      <td>0.001</td>
      <td>0.001</td>
      <td>0.001</td>
      <td>0.001</td>
      <td>0.001</td>
      <td>0.001</td>
      <td>0.001</td>
    </tr>
    <tr>
      <td></td>
      <td>[4.31]</td>
      <td>[4.23]</td>
      <td>[3.78]</td>
      <td>[3.79]</td>
      <td>[3.28]</td>
      <td>[3.06]</td>
      <td>[2.47]</td>
      <td>[2.71]</td>
      <td>[2.66]</td>
      <td>[3.20]</td>
      <td>[3.32]</td>
    </tr>
    <tr>
      <td>STR</td>
      <td>−0.027</td>
      <td>−0.032</td>
      <td>−0.031</td>
      <td>−0.031</td>
      <td>−0.033</td>
      <td>−0.032</td>
      <td>−0.031</td>
      <td>−0.033</td>
      <td>−0.034</td>
      <td>−0.034</td>
      <td>−0.037</td>
    </tr>
    <tr>
      <td></td>
      <td>[−5.33]</td>
      <td>[−6.34]</td>
      <td>[−5.80]</td>
      <td>[−6.06]</td>
      <td>[−6.39]</td>
      <td>[−6.26]</td>
      <td>[−6.11]</td>
      <td>[−6.36]</td>
      <td>[−6.44]</td>
      <td>[−6.45]</td>
      <td>[−6.67]</td>
    </tr>
    <tr>
      <td>BETA</td>
      <td>0.096</td>
      <td>0.102</td>
      <td>0.101</td>
      <td>0.114</td>
      <td>0.108</td>
      <td>0.115</td>
      <td>0.115</td>
      <td>0.113</td>
      <td>0.119</td>
      <td>0.111</td>
      <td>0.116</td>
    </tr>
    <tr>
      <td></td>
      <td>[1.07]</td>
      <td>[1.11]</td>
      <td>[1.12]</td>
      <td>[1.26]</td>
      <td>[1.22]</td>
      <td>[1.28]</td>
      <td>[1.28]</td>
      <td>[1.26]</td>
      <td>[1.32]</td>
      <td>[1.22]</td>
      <td>[1.26]</td>
    </tr>
    <tr>
      <td>SIZE</td>
      <td>−0.100</td>
      <td>−0.097</td>
      <td>−0.099</td>
      <td>−0.100</td>
      <td>−0.102</td>
      <td>−0.102</td>
      <td>−0.100</td>
      <td>−0.099</td>
      <td>−0.100</td>
      <td>−0.099</td>
      <td>−0.100</td>
    </tr>
    <tr>
      <td></td>
      <td>[−3.82]</td>
      <td>[−3.72]</td>
      <td>[−3.83]</td>
      <td>[−3.86]</td>
      <td>[−3.95]</td>
      <td>[−3.94]</td>
      <td>[−3.90]</td>
      <td>[−3.83]</td>
      <td>[−3.83]</td>
      <td>[−3.83]</td>
      <td>[−3.86]</td>
    </tr>
    <tr>
      <td>BM</td>
      <td>0.124</td>
      <td>0.124</td>
      <td>0.127</td>
      <td>0.121</td>
      <td>0.115</td>
      <td>0.115</td>
      <td>0.116</td>
      <td>0.112</td>
      <td>0.111</td>
      <td>0.110</td>
      <td>0.115</td>
    </tr>
    <tr>
      <td></td>
      <td>[2.13]</td>
      <td>[2.16]</td>
      <td>[2.23]</td>
      <td>[2.09]</td>
      <td>[1.96]</td>
      <td>[1.96]</td>
      <td>[1.98]</td>
      <td>[1.93]</td>
      <td>[1.90]</td>
      <td>[1.92]</td>
      <td>[1.99]</td>
    </tr>
    <tr>
      <td>MOM</td>
      <td>0.004</td>
      <td>0.003</td>
      <td>0.004</td>
      <td>0.004</td>
      <td>0.003</td>
      <td>0.004</td>
      <td>0.004</td>
      <td>0.002</td>
      <td>0.001</td>
      <td>0.000</td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>[3.33]</td>
      <td>[2.89]</td>
      <td>[3.09]</td>
      <td>[3.11]</td>
      <td>[2.79]</td>
      <td>[2.96]</td>
      <td>[3.17]</td>
      <td>[1.81]</td>
      <td>[0.68]</td>
      <td>[−0.08]</td>
      <td></td>
    </tr>
    <tr>
      <td>ILLIQ</td>
      <td>−0.019</td>
      <td>−0.018</td>
      <td>−0.017</td>
      <td>−0.019</td>
      <td>−0.018</td>
      <td>−0.018</td>
      <td>−0.018</td>
      <td>−0.017</td>
      <td>−0.018</td>
      <td>−0.017</td>
      <td>−0.018</td>
    </tr>
    <tr>
      <td></td>
      <td>[−2.61]</td>
      <td>[−2.47]</td>
      <td>[−2.45]</td>
      <td>[−2.58]</td>
      <td>[−2.45]</td>
      <td>[−2.41]</td>
      <td>[−2.49]</td>
      <td>[−2.40]</td>
      <td>[−2.43]</td>
      <td>[−2.43]</td>
      <td>[−2.46]</td>
    </tr>
    <tr>
      <td>COSKEW</td>
      <td>−0.160</td>
      <td>−0.180</td>
      <td>−0.202</td>
      <td>−0.189</td>
      <td>−0.183</td>
      <td>−0.192</td>
      <td>−0.195</td>
      <td>−0.203</td>
      <td>−0.196</td>
      <td>−0.187</td>
      <td>−0.189</td>
    </tr>
    <tr>
      <td></td>
      <td>[−1.54]</td>
      <td>[−1.78]</td>
      <td>[−1.96]</td>
      <td>[−1.84]</td>
      <td>[−1.80]</td>
      <td>[−1.86]</td>
      <td>[−1.86]</td>
      <td>[−1.97]</td>
      <td>[−1.91]</td>
      <td>[−1.83]</td>
      <td>[−1.84]</td>
    </tr>
    <tr>
      <td>IVOL</td>
      <td>−0.084</td>
      <td>−0.079</td>
      <td>−0.079</td>
      <td>−0.082</td>
      <td>−0.079</td>
      <td>−0.079</td>
      <td>−0.077</td>
      <td>−0.074</td>
      <td>−0.075</td>
      <td>−0.073</td>
      <td>−0.075</td>
    </tr>
    <tr>
      <td></td>
      <td>[−1.73]</td>
      <td>[−1.60]</td>
      <td>[−1.62]</td>
      <td>[−1.70]</td>
      <td>[−1.64]</td>
      <td>[−1.63]</td>
      <td>[−1.60]</td>
      <td>[−1.52]</td>
      <td>[−1.54]</td>
      <td>[−1.50]</td>
      <td>[−1.53]</td>
    </tr>
    <tr>
      <td>MAX</td>
      <td>−0.086</td>
      <td>−0.093</td>
      <td>−0.094</td>
      <td>−0.091</td>
      <td>−0.093</td>
      <td>−0.092</td>
      <td>−0.094</td>
      <td>−0.098</td>
      <td>−0.094</td>
      <td>−0.096</td>
      <td>−0.095</td>
    </tr>
    <tr>
      <td></td>
      <td>[−1.90]</td>
      <td>[−2.06]</td>
      <td>[−2.09]</td>
      <td>[−2.04]</td>
      <td>[−2.09]</td>
      <td>[−2.06]</td>
      <td>[−2.11]</td>
      <td>[−2.18]</td>
      <td>[−2.08]</td>
      <td>[−2.14]</td>
      <td>[−2.10]</td>
    </tr>
    <tr>
      <td>OP</td>
      <td>1.971</td>
      <td>2.009</td>
      <td>2.014</td>
      <td>2.055</td>
      <td>2.099</td>
      <td>2.107</td>
      <td>2.141</td>
      <td>2.131</td>
      <td>2.090</td>
      <td>2.112</td>
      <td>1.980</td>
    </tr>
    <tr>
      <td></td>
      <td>[4.55]</td>
      <td>[4.49]</td>
      <td>[4.44]</td>
      <td>[4.55]</td>
      <td>[4.45]</td>
      <td>[4.46]</td>
      <td>[4.43]</td>
      <td>[4.33]</td>
      <td>[4.38]</td>
      <td>[4.46]</td>
      <td>[4.44]</td>
    </tr>
    <tr>
      <td>IA</td>
      <td>−0.247</td>
      <td>−0.238</td>
      <td>−0.233</td>
      <td>−0.235</td>
      <td>−0.239</td>
      <td>−0.245</td>
      <td>−0.241</td>
      <td>−0.238</td>
      <td>−0.234</td>
      <td>−0.244</td>
      <td>−0.236</td>
    </tr>
    <tr>
      <td></td>
      <td>[−3.89]</td>
      <td>[−3.91]</td>
      <td>[−3.85]</td>
      <td>[−3.79]</td>
      <td>[−3.84]</td>
      <td>[−3.88]</td>
      <td>[−3.79]</td>
      <td>[−3.73]</td>
      <td>[−3.73]</td>
      <td>[−3.92]</td>
      <td>[−3.85]</td>
    </tr>
    <tr>
      <td>SUE</td>
      <td>0.301</td>
      <td>0.299</td>
      <td>0.299</td>
      <td>0.299</td>
      <td>0.297</td>
      <td>0.299</td>
      <td>0.300</td>
      <td>0.296</td>
      <td>0.296</td>
      <td>0.297</td>
      <td>0.298</td>
    </tr>
    <tr>
      <td></td>
      <td>[12.67]</td>
      <td>[12.61]</td>
      <td>[12.73]</td>
      <td>[12.74]</td>
      <td>[12.68]</td>
      <td>[12.68]</td>
      <td>[12.80]</td>
      <td>[12.78]</td>
      <td>[12.66]</td>
      <td>[12.82]</td>
      <td>[12.90]</td>
    </tr>
    <tr>
      <td>RET$_{t-n:t}$</td>
      <td>−0.395</td>
      <td>0.193</td>
      <td>−0.050</td>
      <td>−0.009</td>
      <td>0.081</td>
      <td>0.003</td>
      <td>−0.082</td>
      <td>0.174

---

# Page 42

Table 8

$3 \times 5$ sorts by $REG$ and proxies for limits-to-arbitrage and information frictions

Each month from June 1963 to December 2020, stocks are first sorted into three portfolios (Low, Medium, High) by control variables associated with limits-to-arbitrage and information frictions. The main control variables are illiquidity ( $ILLIQ$ ) and institutional holdings ( $INST$ ) for limits-to-arbitrage and information frictions, respectively. We further use firm size ( $SIZE$ ) and age ( $AGE$ ) as further proxies to limits-to-arbitrage, and size ( $SIZE$ ) and analyst coverage ( $CVRG$ ) as further proxies to information frictions. Then, stocks are further sorted into quintile portfolios by their regret $REG$ . Panels A and B present the next-month FF6PS alphas for each of the stock characteristic-sorted tercile portfolio and $REG$ -sorted quintile portfolio, and the alpha spreads for the hedge portfolio that is long in the quintile of stocks with the highest $REG$ and short in the quintile of stocks with the lowest $REG$ for each of the tercile portfolio sorted by the stock characteristic associated with limits-to-arbitrage and information frictions, respectively. In addition, the last wo columns for each bivariate sort report the average FF6PS alpha of the $REG$ -sorted quintile portfolios and the zero-cost arbitrage portfolio across the three terciles (Avg.) and the difference in difference in the regret premium associated with the low and high terciles of each characteristic (High-Low), respectively. Newey-West adjusted $t$ -statistics are given in square brackets.

Panel A: Limits-to-arbitrage

<table>
  <thead>
    <tr>
      <th rowspan="2">Quintile</th>
      <th colspan="3">ILLIQ</th>
      <th colspan="3">SIZE</th>
      <th colspan="3">AGE</th>
    </tr>
    <tr>
      <th>Low</th>
      <th>Medium</th>
      <th>High</th>
      <th>Avg.</th>
      <th>High-Low</th>
      <th>Low</th>
      <th>Medium</th>
      <th>High</th>
      <th>Avg.</th>
      <th>High-Low</th>
      <th>Low</th>
      <th>Medium</th>
      <th>High</th>
      <th>Avg.</th>
      <th>High-Low</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1 (Low)</td>
      <td>-0.27</td>
      <td>-0.41</td>
      <td>-0.66</td>
      <td>-0.45</td>
      <td></td>
      <td>-0.61</td>
      <td>-0.36</td>
      <td>-0.31</td>
      <td>-0.43</td>
      <td></td>
      <td>-0.33</td>
      <td>-0.39</td>
      <td>-0.27</td>
      <td>-0.33</td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>[-4.12]</td>
      <td>[-5.66]</td>
      <td>[-8.30]</td>
      <td>[-7.83]</td>
      <td></td>
      <td>[-8.34]</td>
      <td>[-5.56]</td>
      <td>[-4.65]</td>
      <td>[-7.89]</td>
      <td></td>
      <td>[-3.66]</td>
      <td>[-5.04]</td>
      <td>[-3.46]</td>
      <td>[-5.47]</td>
      <td></td>
    </tr>
    <tr>
      <td>2</td>
      <td>-0.15</td>
      <td>-0.16</td>
      <td>-0.21</td>
      <td>-0.17</td>
      <td></td>
      <td>-0.24</td>
      <td>-0.21</td>
      <td>-0.14</td>
      <td>-0.20</td>
      <td></td>
      <td>-0.18</td>
      <td>-0.21</td>
      <td>-0.19</td>
      <td>-0.19</td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>[-2.62]</td>
      <td>[-2.63]</td>
      <td>[-3.48]</td>
      <td>[-3.97]</td>
      <td></td>
      <td>[-4.21]</td>
      <td>[-3.23]</td>
      <td>[-2.80]</td>
      <td>[-4.81]</td>
      <td></td>
      <td>[-2.09]</td>
      <td>[-3.00]</td>
      <td>[-3.01]</td>
      <td>[-3.91]</td>
      <td></td>
    </tr>
    <tr>
      <td>3</td>
      <td>-0.15</td>
      <td>-0.12</td>
      <td>0.13</td>
      <td>-0.13</td>
      <td></td>
      <td>0.09</td>
      <td>-0.13</td>
      <td>-0.18</td>
      <td>-0.13</td>
      <td></td>
      <td>-0.14</td>
      <td>-0.09</td>
      <td>-0.09</td>
      <td>-0.11</td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>[-2.57]</td>
      <td>[-1.79]</td>
      <td>[-2.06]</td>
      <td>[-2.96]</td>
      <td></td>
      <td>[-1.47]</td>
      <td>[-1.85]</td>
      <td>[-3.06]</td>
      <td>[-3.02]</td>
      <td></td>
      <td>[-1.37]</td>
      <td>[-1.42]</td>
      <td>[-1.20]</td>
      <td>[-2.08]</td>
      <td></td>
    </tr>
    <tr>
      <td>4</td>
      <td>0.06</td>
      <td>-0.05</td>
      <td>0.04</td>
      <td>0.02</td>
      <td></td>
      <td>0.05</td>
      <td>-0.04</td>
      <td>0.07</td>
      <td>0.02</td>
      <td></td>
      <td>0.15</td>
      <td>0.03</td>
      <td>-0.15</td>
      <td>0.01</td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>[1.02]</td>
      <td>[-0.68]</td>
      <td>[0.58]</td>
      <td>[0.36]</td>
      <td></td>
      <td>[0.60]</td>
      <td>[-0.62]</td>
      <td>[1.20]</td>
      <td>[0.46]</td>
      <td></td>
      <td>[1.73]</td>
      <td>[0.34]</td>
      <td>[-1.99]</td>
      <td>[0.16]</td>
      <td></td>
    </tr>
    <tr>
      <td>5 (High)</td>
      <td>0.24</td>
      <td>0.35</td>
      <td>0.41</td>
      <td>0.33</td>
      <td></td>
      <td>0.40</td>
      <td>0.34</td>
      <td>0.26</td>
      <td>0.33</td>
      <td></td>
      <td>0.39</td>
      <td>0.31</td>
      <td>0.33</td>
      <td>0.25</td>
      <td></td>
    </tr>
    <tr>
      <td></td>
      <td>[3.74]</td>
      <td>[4.30]</td>
      <td>[5.62]</td>
      <td>[6.25]</td>
      <td></td>
      <td>[5.44]</td>
      <td>[4.68]</td>
      <td>[4.13]</td>
      <td>[6.08]</td>
      <td></td>
      <td>[4.79]</td>
      <td>[3.57]</td>
      <td>[0.43]</td>
      <td>[4.89]</td>
      <td></td>
    </tr>
    <tr>
      <td>High–Low</td>
      <td>0.61</td>
      <td>0.77</td>
      <td>1.06</td>
      <td>0.78</td>
      <td>0.55</td>
      <td>1.01</td>
      <td>0.69</td>
      <td>0.56</td>
      <td>0.76</td>
      <td>-0.45</td>
      <td>0.72</td>
      <td>0.71</td>
      <td>0.30</td>
      <td>0.58</td>
      <td>-0.42</td>
    </tr>
    <tr>
      <td></td>
      <td>[4.85]</td>
      <td>[6.80]</td>
      <td>[8.78]</td>
      <td>[8.16]</td>
      <td>[4.65]</td>
      <td>[8.45]</td>
      <td>[6.58]</td>
      <td>[5.35]</td>
      <td>[8.07]</td>
      <td>[-4.00]</td>
      <td>[5.50]</td>
      <td>[5.67]</td>
      <td>[2.55]</td>
      <td>[6.21]</td>
      <td>[-2.65]</td>
    </tr>
  </tbody>
</table>

(continued on next page)

---

# Page 43

Table 8  
$3 \times 5$ sorts by $REG$ and proxies for limits-to-arbitrage and information frictions (cont.)

Panel B: Information frictions

<table>
  <thead>
    <tr>
      <th rowspan="3">Quintile</th>
      <th colspan="4">INST</th>
      <th colspan="4">SIZE</th>
      <th colspan="4">CVRG</th>
    </tr>
    <tr>
      <th>Low</th>
      <th>Medium</th>
      <th>High</th>
      <th>Avg. High-Low</th>
      <th>Low</th>
      <th>Medium</th>
      <th>High</th>
      <th>Avg. High-Low</th>
      <th>Low</th>
      <th>Medium</th>
      <th>High</th>
      <th>Avg. High-Low</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1 (Low)</td>
      <td>−0.05</td>
      <td>−0.19</td>
      <td>−0.59</td>
      <td>−0.27</td>
      <td>−0.61</td>
      <td>−0.36</td>
      <td>−0.31</td>
      <td>−0.43</td>
      <td>−0.53</td>
      <td>−0.30</td>
      <td>−0.22</td>
      <td>−0.35</td>
    </tr>
    <tr>
      <td></td>
      <td>[−0.49]</td>
      <td>[−2.42]</td>
      <td>[−6.16]</td>
      <td>[−4.07]</td>
      <td>[−8.34]</td>
      <td>[−5.56]</td>
      <td>[−4.65]</td>
      <td>[−7.89]</td>
      <td>[−4.70]</td>
      <td>[−3.57]</td>
      <td>[−3.08]</td>
      <td>[−5.64]</td>
    </tr>
    <tr>
      <td>2</td>
      <td>0.14</td>
      <td>−0.21</td>
      <td>−0.43</td>
      <td>−0.17</td>
      <td>−0.24</td>
      <td>−0.21</td>
      <td>−0.14</td>
      <td>−0.20</td>
      <td>−0.26</td>
      <td>−0.16</td>
      <td>−0.11</td>
      <td>−0.18</td>
    </tr>
    <tr>
      <td></td>
      <td>[1.42]</td>
      <td>[−2.87]</td>
      <td>[−5.27]</td>
      <td>[−3.48]</td>
      <td>[−4.21]</td>
      <td>[−3.23]</td>
      <td>[−2.80]</td>
      <td>[−4.81]</td>
      <td>[−3.84]</td>
      <td>[−2.22]</td>
      <td>[−1.60]</td>
      <td>[−3.73]</td>
    </tr>
    <tr>
      <td>3</td>
      <td>0.02</td>
      <td>−0.18</td>
      <td>−0.46</td>
      <td>−0.21</td>
      <td>0.09</td>
      <td>−0.13</td>
      <td>−0.18</td>
      <td>−0.13</td>
      <td>−0.14</td>
      <td>−0.15</td>
      <td>0.18</td>
      <td>−0.16</td>
    </tr>
    <tr>
      <td></td>
      <td>[0.16]</td>
      <td>[−2.28]</td>
      <td>[−3.99]</td>
      <td>[−3.52]</td>
      <td>[−1.47]</td>
      <td>[−1.85]</td>
      <td>[−3.06]</td>
      <td>[−3.02]</td>
      <td>[−2.16]</td>
      <td>[−2.28]</td>
      <td>[−2.49]</td>
      <td>[−3.41]</td>
    </tr>
    <tr>
      <td>4</td>
      <td>0.20</td>
      <td>−0.11</td>
      <td>−0.38</td>
      <td>−0.09</td>
      <td>0.05</td>
      <td>−0.04</td>
      <td>0.07</td>
      <td>0.02</td>
      <td>−0.16</td>
      <td>−0.12</td>
      <td>0.00</td>
      <td>−0.09</td>
    </tr>
    <tr>
      <td></td>
      <td>[1.94]</td>
      <td>[−1.15]</td>
      <td>[−3.36]</td>
      <td>[−1.31]</td>
      <td>[0.60]</td>
      <td>[−0.62]</td>
      <td>[1.20]</td>
      <td>[0.46]</td>
      <td>[−1.99]</td>
      <td>[−1.47]</td>
      <td>[0.06]</td>
      <td>[−1.63]</td>
    </tr>
    <tr>
      <td>5 (High)</td>
      <td>0.68</td>
      <td>0.16</td>
      <td>−0.06</td>
      <td>0.26</td>
      <td>0.40</td>
      <td>0.34</td>
      <td>0.26</td>
      <td>0.33</td>
      <td>0.27</td>
      <td>0.26</td>
      <td>0.25</td>
      <td>0.26</td>
    </tr>
    <tr>
      <td></td>
      <td>[5.02]</td>
      <td>[2.35]</td>
      <td>[−0.61]</td>
      <td>[4.44]</td>
      <td>[5.44]</td>
      <td>[4.68]</td>
      <td>[4.13]</td>
      <td>[6.08]</td>
      <td>[3.30]</td>
      <td>[3.03]</td>
      <td>[2.82]</td>
      <td>[4.41]</td>
    </tr>
    <tr>
      <td>High−Low</td>
      <td>0.74</td>
      <td>0.35</td>
      <td>0.53</td>
      <td>0.54</td>
      <td>−0.21</td>
      <td>1.01</td>
      <td>0.69</td>
      <td>0.56</td>
      <td>0.76</td>
      <td>−0.45</td>
      <td>0.80</td>
      <td>0.55</td>
      <td>0.47</td>
      <td>0.61</td>
      <td>−0.33</td>
    </tr>
    <tr>
      <td></td>
      <td>[3.98]</td>
      <td>[2.98]</td>
      <td>[4.44]</td>
      <td>[4.99]</td>
      <td>[−1.11]</td>
      <td>[8.45]</td>
      <td>[6.58]</td>
      <td>[5.35]</td>
      <td>[8.07]</td>
      <td>[−4.00]</td>
      <td>[5.89]</td>
      <td>[4.18]</td>
      <td>[3.65]</td>
      <td>[5.82]</td>
      <td>[−2.48]</td>
    </tr>
  </tbody>
</table>

42