# Options literature scan — differentiation ideas for Axiom Options

Date: 2026-11-12. Scope: academic + practitioner sources on options positioning, flow, vol surface, ML, manipulation, India. Research only.

Verification rule: every citation below was confirmed by web search against a bibliographic index (RePEc/EconPapers, IDEAS, arXiv, journal page, SSRN/NBER, regulator press release). Items not confirmed are tagged `UNVERIFIED`. Full texts were mostly paywalled: findings are from abstracts / working-paper versions, not tables. Numbers quoted are abstract-level.

India context assumed: NSE index options European, cash-settled; stock options European, physically settled since 2018-19 (`UNVERIFIED` here, check NSE circulars); one weekly-expiry benchmark per exchange since 20 Nov 2024 (SEBI circular below).

---

## 1. Information content of option order flow (options lead stocks)

**1.1 Easley, O'Hara, Srinivas (1998). "Option Volume and Stock Prices: Evidence on Where Informed Traders Trade." Journal of Finance 53(2):431–465.**
Link: https://www.econbiz.de/Record/option-volume-and-stock-prices-evidence-on-where-informed-traders-trade/10005691696
- Model: informed traders pick options vs stock venue (pooling equilibrium when option leverage/liquidity attractive). Empirics: *signed* ("positive" vs "negative") option volume carries information about future stock prices; stock usually leads options, but options lead under identifiable conditions.
- Capability: **signed option-flow imbalance per underlying** (buy-call + sell-put vs buy-put + sell-call), not raw volume.

**1.2 Pan, Poteshman (2006). "The Information in Option Volume for Future Stock Prices." RFS 19(3):871–908. NBER WP 10925.**
Link: https://www.nber.org/papers/w10925 ; https://econpapers.repec.org/RePEc:oup:rfinst:v:19:y:2006:i:3:p:871-908
- Put-call ratio from *buyer-initiated, open-position* volume: low-PCR stocks beat high-PCR by >40 bp next day, >1%/week. Stronger with more informed traders and higher-leverage (OTM) options. Driven by non-public info; public PCR (plain volume) has little power.
- Capability: **"opening-buy" PCR**, not the vanilla PCR every Indian terminal shows. Key point: the plain PCR is the weak version.

**1.3 Cremers, Weinbaum (2010). "Deviations from Put-Call Parity and Stock Return Predictability." JFQA 45(2):335–367.**
Link: https://ideas.repec.org/a/cup/jfinqa/v45y2010i02p335-367_00.html
- Volatility spread = IV(call) − IV(put) at matched strike/expiry. Expensive-call stocks beat expensive-put stocks by ~50 bp/week; stronger when option liquidity high, stock liquidity low. Mispricing decays over sample period.
- Capability: **call-put IV spread screener** across F&O stocks, ranked daily, with liquidity filter.

**1.4 Xing, Zhang, Zhao (2010). "What Does the Individual Option Volatility Smirk Tell Us About Future Equity Returns?" JFQA 45(3):641–662.**
Link: https://ideas.repec.org/a/cup/jfinqa/v45y2010i03p641-662_00.html
- SKEW = IV(OTM put) − IV(ATM call). Steepest-smirk stocks underperform (≈10.9%/yr in WP), persists ≥6 months, predicts next-quarter earnings shocks. Informed bearish traders buy OTM puts.
- Capability: **single-stock smirk-steepness rank + change**, pre-results alert.

**1.5 Johnson, So (2012). "The Option to Stock Volume Ratio and Future Returns." JFE 106(2):262–286.**
Link: https://econpapers.repec.org/RePEc:eee:jfinec:v:106:y:2012:i:2:p:262-286
- O/S (option volume / stock volume) negatively predicts returns: low-decile beats high-decile by 0.34%/week (19.3% ann.). Stronger with high short-sale costs. Predicts earnings news. Mechanism: short-sale constraints push negative info into options.
- Capability: **O/S ratio screener**. India relevance high: retail-short in cash is intraday-only and SLB is thin, so short-sale costs are effectively high → mechanism should be stronger, not weaker. Untested in India (no source found).

**1.6 Muravyev (2016). "Order Flow and Expected Option Returns." Journal of Finance 71(2):673–708.**
Link: https://zendy.io/title/10.1111/jofi.12380
- Price impact of option trades decomposes into inventory risk + asymmetric info; inventory component larger. Past option order imbalance is the strongest predictor of *option* returns. Extreme negative imbalances around expiry.
- Capability: **option-level order-imbalance → expected option return (richness/cheapness) signal** for the desk's execution.

---

## 2. Dealer gamma, hedging flow, pinning

**2.1 Avellaneda, Lipkin (2003). "A Market-Induced Mechanism for Stock Pinning." Quantitative Finance 3(6):417–425.**
Link: https://ideas.repec.org/a/taf/quantf/v3y2003i6p417-425.html ; author page https://math.nyu.edu/~avellane/stock_pinning.html
- SDE with singular drift from delta-hedging price impact; pin probability is an explicit function of vol, time-to-expiry, OI at strike, price elasticity.
- Capability: **closed-form pin-probability per strike on expiry day**, parameterised by OI and an impact constant calibrated on NSE history.

**2.2 Ni, Pearson, Poteshman (2005). "Stock Price Clustering on Option Expiration Dates." JFE 78(1):49–87.**
Link: https://econpapers.repec.org/RePEc:eee:jfinec:v:78:y:2005:i:1:p:49-87
- Optionable stocks close at strikes disproportionately on expiry. Two channels: market-maker hedge rebalancing (when MMs net long gamma) and manipulation by proprietary traders (when net short).
- Capability: **expiry-close clustering monitor** per stock/index, separating "long-gamma pin" from "short-gamma push".

**2.3 Golez, Jackwerth (2012). "Pinning in the S&P 500 Futures." JFE 106(3):566–585.**
Link: https://ideas.repec.org/a/eee/jfinec/v106y2012i3p566-585.html
- Futures settle near ATM strike on serial-option expiry; ≥$115m notional shift per expiry; driven by MM delta re-hedging from theta decay. Also "anti-pinning" away from ATM before index-option expiry.
- Capability: **index pin/anti-pin model** directly relevant to Nifty/Bank Nifty weekly expiries (index-level, cash-settled — closest analogue to NSE).

**2.4 Ni, Pearson, Poteshman, White (2021). "Does Option Trading Have a Pervasive Impact on Underlying Stock Prices?" RFS 34(4):1952–1986.**
Link: https://ideas.repec.org/a/oup/rfinst/v34y2021i4p1952-1986..html
- Non-informational channel: MM hedge rebalancing affects stock return volatility and probability of large moves on *all* days, not just expiry. Net MM gamma sign matters.
- Capability: **net-dealer-gamma → expected realised-vol / tail-move probability** for the underlying.

**2.5 Baltussen, Da, Lammers, Martens (2021). "Hedging Demand and Market Intraday Momentum." JFE 142(1):377–403.**
Link: https://econpapers.repec.org/RePEc:eee:jfinec:v:142:y:2021:i:1:p:377-403 ; WP https://www3.nd.edu/~zda/intramom.pdf
- 60+ futures, 1974–2020: rest-of-day return predicts last-30-min return; effect concentrated on negative-gamma days (gamma from options + leveraged ETFs); reverts over following days.
- Capability: **last-30-min continuation signal conditioned on estimated dealer gamma sign**. Note NSE index close is computed over the last 30 min (`UNVERIFIED` exact method), so this window *is* the settlement window on expiry.

**2.6 Barbon, Buraschi (WP, 2019–2021). "Gamma Fragility: Asset Pricing Implications of Delta-Hedging."**
Link: https://abarbon.com/papers/gamma-fragility ; https://www.alexandria.unisg.ch/261487 (SSRN ID not confirmed: `UNVERIFIED`)
- Aggregate dealer gamma imbalance × illiquidity explains intraday momentum (neg gamma) / reversal (pos gamma); linked to frequency and size of flash crashes; stronger for illiquid underlyings.
- Capability: **"gamma fragility" score = |net dealer gamma| / underlying depth**, per F&O stock — stock-level, not just index.

**2.7 Dim, Eraker, Vilkov (2024). "0DTEs: Trading, Gamma Risk and Volatility Propagation." SSRN 4692190.**
Link: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4692190 (ID from secondary source + Oxford seminar abstract)
- Counter-evidence: high 0DTE OI gamma does *not* propagate past volatility; intraday 0DTE volume shocks don't amplify index returns. 0DTEs carry the largest VRP.
- Capability: **honest gamma-regime backtest**: don't ship a GEX dashboard as gospel; show its realised hit-rate on NSE. Differentiator vs SpotGamma-style clones.

**2.8 Gârleanu, Pedersen, Poteshman (2009). "Demand-Based Option Pricing." RFS 22(10):4259–4299. NBER WP 11843.**
Link: https://www.nber.org/papers/w11843
- End-user demand raises option prices ∝ variance of unhedgeable part; cross-effects ∝ covariance. Index options: high end-user net long demand → expensive + skewed. Single-stock: small net short demand, not expensive.
- Capability: **demand-pressure attribution of skew** using participant-wise OI (client net vs pro/FII net).

---

## 3. Volatility risk premium, variance swaps, model-free IV

**3.1 Bakshi, Kapadia (2003). "Delta-Hedged Gains and the Negative Market Volatility Risk Premium." RFS 16(2):527–566.**
Link: https://ideas.repec.org/a/oup/rfinst/v16y2003i2p527-566.html
- Delta-hedged S&P option portfolios lose on average → negative vol risk premium; losses larger when vol high, smaller away from ATM.
- Capability: **delta-hedged P&L attribution per strike/expiry** (realised vs implied), the true measure of whether a seller earned VRP or just got lucky on direction.

**3.2 Carr, Wu (2009). "Variance Risk Premiums." RFS 22(3):1311–1341.**
Link: https://ideas.repec.org/a/oup/rfinst/v22y2009i3p1311-1341..html ; WP https://engineering.nyu.edu/sites/default/files/2019-01/CarrReviewofFinStudiesMarch2009-a.pdf
- Synthetic variance-swap rate from option strip (model-free); VRP = RV − SW. Strongly negative for indices, mostly an independent variance factor not explained by size/value/momentum.
- Capability: **synthetic variance-swap rate per underlying and tenor** (incl. single stocks, weekly Nifty) + realised-vs-implied VRP history.

**3.3 Bollerslev, Tauchen, Zhou (2009). "Expected Stock Returns and Variance Risk Premia." RFS 22(11):4463–4492.**
Link: https://scholars.duke.edu/publication/732839
- VRP = model-free IV² − realised variance (high-frequency) predicts aggregate equity returns, best at quarterly horizon, beats P/E, default spread, cay. Requires model-free IV + HF RV.
- Capability: **VRP regime gauge for Nifty** (India VIX² − 5-min RV) as a market-timing input.

**3.4 NSE. India VIX white paper / computation methodology.**
Link: https://nseindia.com/products/content/equities/indices/india_vix.htm (PDF linked from page; page text confirmed via secondary copies)
- CBOE methodology adapted: near/next-month Nifty OTM best bid/ask, cubic-spline, NSE MIBOR, rolls 3 trading days before expiry. Only one tenor (30d), only Nifty.
- Capability: **term structure of model-free vol (weekly → quarterly) for Nifty, Bank Nifty, Sensex and top F&O stocks** — India VIX covers one point; nobody publishes the rest.

---

## 4. Surface modelling, smile dynamics, rough vol

**4.1 Gatheral, Jacquier (2014). "Arbitrage-free SVI Volatility Surfaces." Quantitative Finance 14(1):59–71. arXiv:1204.0646.**
Link: https://arxiv.org/abs/1204.0646
- SSVI: closed-form family guaranteeing no calendar/butterfly static arbitrage; calibration recipe; tested on SPX.
- Capability: **arb-free SSVI surface as the single source of truth** for Greeks, probabilities, scenario P&L. Most Indian tools compute per-strike BS IV off LTP → noisy, arb-violating smiles, broken risk-neutral densities.

**4.2 Derman (1999). "Regimes of Volatility." Goldman Sachs QS Research Note (Jan 1999); Risk (Apr 1999).**
Link: https://emanuelderman.com/regimes-of-volatility/
- Sticky-strike vs sticky-delta vs sticky-implied-tree regimes; which regime holds changes hedge ratios (delta under sticky-delta ≥ sticky-strike).
- Capability: **live regime classifier** (regress ΔIV on Δspot per strike) and **smile-adjusted delta** displayed alongside BS delta.

**4.3 Bergomi (2004). "Smile Dynamics." Risk, Sept 2004.**
Link: https://www.risk.net/node/1500225 (part II page; part I exact Risk URL `UNVERIFIED`)
- Forward-skew / spot-vol correlation dynamics matter more than fitting today's smile; standard SV/jump models impose structural constraints on them.
- Capability: **skew-stickiness ratio** (realised ∂ATM-IV/∂ln S vs the smile's slope) — feeds hedge ratios and vega-of-skew risk.

**4.4 Gatheral, Jaisson, Rosenbaum (2018). "Volatility is Rough." Quantitative Finance 18(6):933–949. arXiv:1410.3394.**
Link: https://arxiv.org/abs/1410.3394
- Log-vol behaves like fBM with H≈0.1 (RFSV); gives strong RV forecasts and explains steep short-dated ATM skew term structure (~T^(H−½)).
- Capability: **rough-vol RV forecast** for weekly/0-1DTE horizons (where India volume is) → better "is weekly straddle rich?" call than GARCH/HV.

**4.5 Cao, Chen, Hull (2020). "A Neural Network Approach to Understanding Implied Volatility Movements." Quantitative Finance 20(9):1405–1413.**
Link: https://econpapers.repec.org/RePEc:taf:quantf:v:20:y:2020:i:9:p:1405-1413 ; WP https://www-2.rotman.utoronto.ca/~hull/downloadablepublications/VolSurfaces_NeuralNet.pdf
- NN models expected ΔIV as function of index return, moneyness, tenor (+ VIX level); ~10.7% improvement over analytic minimum-variance model; response differs sharply in high vs low vol regimes.
- Capability: **learned surface-response model** → "if Nifty −2%, expected surface" scenarios instead of flat-vol shocks.

---

## 5. ML for pricing/hedging and probability forecasts

**5.1 Buehler, Gonon, Teichmann, Wood (2019). "Deep Hedging." Quantitative Finance 19(8):1271–1291. arXiv:1802.03042.**
Link: https://arxiv.org/abs/1802.03042
- RL/NN hedging under transaction costs and frictions with convex risk measures; beats complete-market delta hedge under costs (Heston test). From JPM.
- Capability: **cost-aware hedge recommender** for the desk (hedge bands under STT/brokerage/impact) — STT on Indian options makes this more valuable than in the US.

**5.2 Ruf, Wang (2020). "Neural Networks for Option Pricing and Hedging: A Literature Review." J. Computational Finance. arXiv:1911.05620.**
Link: https://arxiv.org/abs/1911.05620
- Survey of >100 papers; flags data-leakage risk in ANN training on historical option data (companion paper).
- Capability: **leakage-safe backtest harness** (purged walk-forward) as a product feature, not only an internal tool.

**5.3 Bali, Beckmeyer, Mörke, Weigert (2023). "Option Return Predictability with Machine Learning and Big Data." RFS 36(9):3548–3602.**
Link: https://econpapers.repec.org/RePEc:oup:rfinst:v:36:y:2023:i:9:p:3548-3602.
- Nonlinear ML on 12M+ obs (1996–2020) gives long-short delta-hedged equity-option profits surviving costs; option characteristics strongest, stock characteristics add incremental power.
- Capability: **cross-sectional "rich/cheap" score per F&O stock option** (delta-hedged expected return), not direction calls.

**5.4 Breeden, Litzenberger (1978). "Prices of State-Contingent Claims Implicit in Option Prices." Journal of Business 51(4):621–651.**
Link: https://www.gsb.stanford.edu/faculty-research/working-papers/prices-state-contingent-claims-implicit-option-prices
- Risk-neutral density = second strike-derivative of call prices.
- Capability: **risk-neutral distribution per expiry** from the arb-free surface (prerequisite for 5.5/5.6).

**5.5 Jackwerth (2000). "Recovering Risk Aversion from Option Prices and Realized Returns." RFS 13(2):433–451.**
Link: https://ideas.repec.org/a/oup/rfinst/v13y2000i2p433-51.html
- Risk-neutral vs physical densities differ systematically (post-1987 "pricing kernel puzzle").
- Capability: **risk-neutral → real-world probability conversion**. Retail "probability of profit" in every Indian app uses risk-neutral (or lognormal HV) odds — systematically wrong for short-premium sellers.

**5.6 Gneiting, Raftery (2007). "Strictly Proper Scoring Rules, Prediction, and Estimation." JASA 102(477):359–378.**
Link: https://apps.dtic.mil/sti/html/tr/ADA459827/index.html
- Theory of proper scoring rules (log, CRPS, interval score); calibration + sharpness as the evaluation standard for probabilistic forecasts.
- Capability: **published calibration report card** for every probability the platform shows (reliability diagram, CRPS vs India VIX baseline). Trust differentiator for retail.

---

## 6. Manipulation / expiry-day behaviour

**6.1 Kumar, Seppi (1992). "Futures Manipulation with 'Cash Settlement'." Journal of Finance 47(4):1485–1502.**
Link: https://ideas.repec.org/a/bla/jfinan/v47y1992i4p1485-502.html
- Cash settlement removes corners/squeezes but enables a different manipulation: hold derivative position, trade the spot to move the settlement price. Manipulation ≈ endogenous noise trading.
- Capability: **cross-market footprint detector**: derivative delta exposure vs same-entity cash/futures trading in the settlement window. Exactly the SEBI–Jane Street pattern.

**6.2 SEBI (3 Jul 2025). Interim order in the matter of index manipulation by Jane Street group (JSI Investments, JSI2 Investments, Jane Street Singapore, Jane Street Asia Trading).**
Link: https://blogs.law.ox.ac.uk/oblb/blog-post/2025/07/jane-street-and-expiry-day-trap-unpacking-sebis-crackdown-algorithmic (summary) ; order on sebi.gov.in (exact URL `UNVERIFIED`)
- Alleged "Strategy A" (e.g., 17 Jan 2024 Bank Nifty expiry): aggressive morning buying of Bank Nifty constituents + stock futures while building large short-option/short-delta position, then selling into close ("marking the close"); ₹4,843.57 cr impounded; Jan 2023–Mar 2025. Jane Street disputes; appellate status pending (`UNVERIFIED` current status).
- Capability: **expiry-day "anomalous constituent flow vs option book" alert** using public data: constituent-weighted cash imbalance in morning vs afternoon, index-vs-futures basis dislocation, OI shift. Retail framing: "today is a high-manipulation-risk expiry".

**6.3 SEBI circular SEBI/HO/MRD/TPD-1/P/CIR/2024/132 (1 Oct 2024). "Measures to strengthen Equity Index Derivatives Framework for Increased Investor Protection and Market Stability."**
Link: https://www.scconline.com/blog/post/2024/10/03/measures-to-strengthen-equity-index-derivatives-framework-legal-news
- One weekly benchmark per exchange (from 20 Nov 2024); min contract ₹15 lakh; +2% ELM on short options on expiry; intraday monitoring of index position limits (from Apr 2025 per secondary sources).
- Capability: **regime-aware analytics** — all backtests/signals must split pre/post Nov-2024 and post expiry-day shifts (NSE expiry day moved in 2025; exact day `UNVERIFIED`, check NSE circular 33/2025 and later).

**6.4 Mahalwala (2016). Expiration-day effects in Indian index futures (CNX Nifty, ARMA-EGARCH). Metamorphosis 15(1):10–19.**
Link: https://econpapers.repec.org/RePEc:sae:metjou:v:15:y:2016:i:1:p:10-19 (exact title `UNVERIFIED`)
- Significant but non-disastrous expiry effects; attributed to arbitrage unwinding and cash settlement.
- Also: Singh & Shaik (2020), "Re-examining the Expiration Effects of Index Futures: Evidence from India," IJEFI — https://doaj.org/article/670623ed8fd148dca38ae9f134115cb3 (mixed results across Bank Nifty weekly introduction).
- Capability: baseline for **expiry-day abnormal volume/vol/return model**; the Indian academic literature is thin and pre-weekly-0DTE — gap to exploit.

**6.5 Muravyev (2016) and Ni-Pearson-Poteshman (2005)** (above) cover the MM-price-pressure and manipulation channels at expiry; combine with 6.1 for detection.

---

## 7. India-specific

**7.1 SEBI (23 Sep 2024). Study: "Analysis of Profit and Loss of Individual Traders dealing in Equity F&O Segment" (FY22–FY24). Press Release 22/2024.**
Link: https://taxguru.in/sebi/sebi-study-shows-93-percent-individual-fo-traders-incur-losses.html (summary; original on sebi.gov.in, exact title `UNVERIFIED`)
- 93% of ~1.13 cr individuals lost; net ₹1.81 lakh cr incl. costs; avg ≈₹2 lakh; only 7.2% profitable; >75% of loss-makers kept trading after two loss years. Follows Jan 2023 study (89% losers FY22).
- Capability: **behavioural guardrails as product** (loss-streak detection, cost drag display, "your edge after STT" report) — aligns with regulator intent, sells to brokers.

**7.2 SEBI (Jul 2025). FY25 follow-up study.**
Link: https://moneylife.in/article/91-percentage-of-retail-traders-lost-money-in-derivatives-losses-in-fo-surged-41-percentage-to-rs105-lakh-crore-in-fy25-sebi-study/77613.html
- ~91% individuals lost in FY25; net loss ≈₹1.06 lakh cr (+41% YoY); unique traders 61.4 lakh (Q1) → 42.7 lakh (Q4) after Nov-2024 measures. Top-13 brokers sample.
- Capability: same as 7.1; plus **pre/post-regulation participation dashboards**.

**7.3 Agarwal, Ghosh, Prabhala, Zhao (2025). "Animal Spirits on Steroids: Evidence from Retail Options Trading in India." CFR Working Paper 25-09 (Univ. of Cologne); AEA 2026.**
Link: https://www.cfr-cologne.de/download/workingpaper/cfr-25-09.pdf ; https://econpapers.repec.org/RePEc:zbw:cfrwps:327125
- All NSE options trades: retail concentrates in and dominates index options (index options ≈75% premium, 93% notional); exogenous increase in supply of short-maturity options *induces* retail trading.
- Capability: **retail-crowding index** per expiry/strike (OTM, short-dated, cheap premium concentration) — both a contrarian signal for the desk and a risk warning for retail.

**7.4 NSE participant-wise OI and volume (daily, FII/DII/Pro/Client × index/stock × futures/calls/puts × long/short).**
Link: https://www.nseindia.com (Reports → Derivatives → participant-wise OI; exact URL `UNVERIFIED`)
- Not a paper — the dataset. No peer-reviewed study found that tests FII *options* positioning as a Nifty return predictor; only blogs (e.g., marketcalls.in claims ~6% vs ~17% ann. after FII net short vs long, methodology absent → not evidence).
- Capability: **participant-positioning signal with proper test** (net FII long-call − long-put, client crowding) — genuine white space; also enables a crude "dealer = Pro" gamma proxy.

**7.5 Pathak, Bhattacharjee, Reddy (2015). Information content of S&P CNX Nifty index options under varying market conditions and moneyness. Global Business Review 16(2):281–302.**
Link: https://econpapers.repec.org/RePEc:sae:globus:v:16:y:2015:i:2:p:281-302 (exact title `UNVERIFIED`)
- ATM options are the preferred venue of informed traders in India across periods. Related: Debasish (2009), J. Risk Finance — Nifty options lead cash with feedback (https://ideas.repec.org/a/eme/jrfpps/15265940910980650.html, details `UNVERIFIED`).
- Capability: focus flow-signals on **ATM**, unlike US evidence favouring OTM (Pan-Poteshman leverage result) — localise, don't port.

---

## Under-implemented ideas — top 10 ranked by differentiation

Ranking = (evidence strength) × (absence in Indian retail/pro tools: Sensibull, Opstra, Quantsapp, broker terminals — absence based on general market knowledge, `NOT VERIFIED` against a feature audit; see sibling benchmark doc) × (India fit).

| # | Capability | Sources | Data sufficiency (NSE public / vendor) |
|---|---|---|---|
| 1 | **Arb-free SSVI surface as engine** → stable Greeks, risk-neutral densities, smile-adjusted delta, sticky-regime classifier | 4.1, 4.2, 4.3, 5.4 | **Sufficient.** Needs synchronised bid/ask snapshots (vendor tick or broker WebSocket). LTP-only EOD bhavcopy is insufficient (stale strikes). |
| 2 | **Real-world (not risk-neutral) probability of profit, with published calibration report card** | 5.5, 5.6, 3.1 | **Sufficient.** Surface + history of Nifty/stock returns. Calibration needs ≥2–3 yrs of stored surfaces → start archiving day 1. |
| 3 | **Expiry-day pin/anti-pin probability per strike** (Avellaneda-Lipkin calibrated on NSE; settlement-window aware) | 2.1, 2.2, 2.3 | **Mostly sufficient.** Needs intraday OI (NSE publishes OI snapshots intraday via feeds; granularity vendor-dependent) + tick. Dealer *sign* unknown → see #5 caveat. |
| 4 | **Expiry-day manipulation-risk / cross-market footprint monitor** (constituent cash imbalance vs index option book, basis dislocation, close-window pressure) | 6.1, 6.2, 2.2 | **Partial.** Aggregate footprint detectable from public tick of constituents + futures + options. Entity attribution impossible (needs exchange surveillance data); sell as "risk flag", never "accusation". |
| 5 | **Dealer-gamma regime with honest backtest** (GEX + gamma-fragility score per stock, tested for intraday momentum/reversal on NSE) | 2.4, 2.5, 2.6, 2.7, 2.8 | **Weak.** No MM/dealer identification; NSE participant OI is EOD and "Pro" ≠ dealer. Must assume sign (retail net short premium?—`UNVERIFIED`; Agarwal et al. suggest retail net *buys* short-dated OTM). Publish model uncertainty; this is where competitors overclaim. |
| 6 | **Signed / opening-buy flow metrics: PCR-buy, Easley-style signed imbalance, O/S ratio** | 1.1, 1.2, 1.5, 1.6 | **Partial.** No open/close or initiator flag publicly (unlike Cboe Open-Close used by Pan-Poteshman). Lee-Ready signing from tick+quotes feasible; open/close inferable only from ΔOI. O/S is fully buildable from public volume. |
| 7 | **Cross-sectional F&O-stock screeners: call-put IV spread, smirk steepness, ML rich/cheap delta-hedged score** | 1.3, 1.4, 5.3 | **Sufficient** for ~180–200 F&O stocks given bid/ask snapshots; single-stock option liquidity thin beyond near month → liquidity filter mandatory. |
| 8 | **Model-free variance-swap term structure + VRP gauge** for Nifty, Bank Nifty, Sensex, top stocks; delta-hedged P&L attribution | 3.1, 3.2, 3.3, 3.4 | **Sufficient** for index; stock strips sparse → interpolate via SSVI (#1). Needs 5-min RV from underlying tick. |
| 9 | **Participant-positioning signal (FII/Client/Pro net option exposure) with proper out-of-sample test + retail-crowding index** | 7.3, 7.4, 2.8 | **Sufficient (EOD).** NSE participant-wise OI public daily; no intraday. Untested academically → first-mover research credibility. |
| 10 | **Cost-aware deep-hedge / hedge-band recommender** under STT + impact; rough-vol RV forecast for 0-2DTE | 5.1, 4.4, 4.5 | **Sufficient** for desk (own positions + tick). Heavy compute; desk-only initially. |

### Cross-cutting conclusions
- Highest-leverage, lowest-data-risk wedge: **#1 → #2 → #8** (surface quality → honest probabilities → VRP). Every other signal depends on a clean surface; most Indian tools skip this.
- India-specific white space: **#4 and #9** — post-Jane-Street and post-Nov-2024 regime, no published academic tests; regulator-aligned narrative helps broker distribution.
- Biggest data gap: **trade direction and participant identity intraday**. No public initiator flag, no open/close flag, no MM identification. Ask NSE Data & Analytics / vendors whether tick feed carries aggressor side (`UNVERIFIED`); otherwise rely on Lee-Ready + ΔOI inference and state error bars.

### RISK
- Most US findings (PCR, O/S, smirk) decayed post-publication (Cremers-Weinbaum note decay) and are untested on NSE; treat as hypotheses, require NSE backtests before marketing.
- Signals implying "who is manipulating" carry legal/regulatory exposure for a broker-distributed product — frame as market-condition flags.
- Regime breaks (weekly expiry rationalisation Nov 2024, expiry-day changes 2025, lot-size changes) shorten usable history; pre-2024 data may mislead.
- Retail-facing probabilities without calibration evidence would replicate the problem SEBI studies document.

### Not verified / skipped
- Full texts not read (paywalled); numbers from abstracts/WPs.
- No search hit for an NSE/IIM paper on FII options positioning predictability; no RBI working paper on equity derivatives found in this pass.
- Cboe 0DTE / OCC white papers not included (time); Dim-Eraker-Vilkov covers the 0DTE gamma question.
- Exact sebi.gov.in URLs for the Jane Street order and 2024 study not captured.
