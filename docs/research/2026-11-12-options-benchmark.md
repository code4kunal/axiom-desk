# Options module benchmark: best-in-class capabilities (research)

Date: 2026-11-12. Scope: inputs for the Axiom Desk options-module PRD (Indian multi-asset platform, first user a pro internal desk).
Method: web search only. WebFetch was blocked by a local hook, so most claims rest on search-result summaries of the cited pages, not full-page reads.
Tags: **[OFFICIAL]** = vendor, exchange or regulator page. **[3P]** = third-party review or news. **UNVERIFIED** = not confirmed from any source this session.
Caveat: several Indian "comparison" pages are written by competitors (AlgoTest writes about StockMock, FlashAlpha about SpotGamma and Unusual Whales). Treat their feature claims as marketing.

---

## 1. Indian platforms

| Platform | Best at | Evidence |
|---|---|---|
| **Sensibull** (Zerodha-partnered) | Retail-to-semi-pro **strategy builder** with payoff charts; basic and advanced option chain; OI charts, including multi-strike OI; FII/DII data page; live option charts; virtual (paper) trading; multi-leg basket execution through broker integration. | [OFFICIAL] https://sensibull.com/ ; [OFFICIAL] https://blog.sensibull.com/2023/03/10/new-feature-updates/ ; [OFFICIAL] https://zerodha.com/z-connect/tradezerodha/sensibull/introducing-sensibull-the-options-trading-platform ; [3P] https://www.strike.money/reviews/sensibull |
| **Opstra** (Definedge) | **IV tooling**: IV percentile against 252-day history, per-strike IV history, IV skew by expiry. Reportedly also a vol surface on the Pro tier. Plus a drag-and-drop strategy builder, a simulator, and a **backtester** for NSE and BSE indices. Weakness: dense UI, few scanners. | [3P] https://www.strike.money/reviews/definedge-opstra ; [3P] https://bankniftyoptions-com.pages.dev/artigos/opstra-banknifty-tools . Pro-tier contents and pricing conflict across sources: **UNVERIFIED** |
| **Quantsapp** | **OI analytics depth**: build-up by scrip, by breadth and by sector (long/short build-up, unwinding, covering). Participant data across cash, index and stock futures and options. Unusual Option Activity scanner. Real-time ATM IV tracking. | [OFFICIAL] https://new.quantsapp.com/ ; [OFFICIAL] https://web.quantsapp.com/participant-data ; [OFFICIAL] https://web.quantsapp.com/open-interest/ |
| **Tradl** | No product found under this name. Nearby Indian tools that did turn up: Samco Options B.R.O., InstaOptions, OptionAction (vol smile and vol **cone**), Trador. | **UNVERIFIED**. Get the exact name or URL from the requester. OptionAction: https://www.marketcalls.in/softwares/option-action-options-analysis-tool-indian-markets.html |
| **AlgoTest** | Leading Indian **rule-based options backtester** plus forward test and live algo. Uses 1-min OHLC bars. Re-entry modes: ASAP, ASAP-reverse, momentum, momentum-reverse, re-entering at the new ATM. Claims to include slippage and costs. EOD data reportedly from 2016. Covers stock options and NSE/BSE indices. **It documents its own fidelity gaps**: SL and entry inside the same 1-min candle can't be ordered; ATM is ambiguous when spot sits between strikes; timing within a minute matters. | [OFFICIAL] https://algotest.in/blog/why-is-there-is-difference-between-my-live-trade-vs-forward-test-vs-backtest-results/ ; https://algotest.in/blog/types-of-strategies-that-do-not-work.md ; https://algotest.in/blog/best-backtesting-software-for-options-trading-in-india/ . Slippage formula: **UNVERIFIED** |
| **StockMock** | **Option simulator**: step-by-step historical replay with manual adjustments, separate from batch backtest. Indices only (Nifty, BankNifty, FinNifty, Midcap Nifty, Sensex). Simulator data from Jan 2021. Slippage and brokerage settings. | [3P, competitor-authored] https://algotest.in/blog/stockmock-vs-algotest-option-simulator/ ; [3P] https://techjockey.com/detail/stockmock . Forward/paper-trading support conflicts across sources: **UNVERIFIED** |
| **FnOTrader** (fnotrader.com) | Broad Indian suite: options analytics (chain, OI build-up tags LB/SB/LU/SC per interval, straddle charts, F&O screener), footprint/order-flow charts, the QuikTrade 1-click multi-leg terminal, an Algo product (1-min backtests, paper or live deployment), and AI/MCP access for backtests. **"Setups" — how one is defined**: an algorithmic intraday setup is detected on 5-min bars by a "deterministic algorithm". A long candidate needs a new intraday high, a volume spike, and price above VWAP. The detector runs on a 1-min cron and waits for the 5-min bar close to confirm; a setup can disappear if it de-confirms. Each card shows entry, T1/T2 targets and a stop. **Evidence shown**: only a **same-day outcome label** (T1 HIT / SL HIT / OPEN), computed by walking forward through that day's bars. The site itself labels this "illustrative only". **No published aggregate win rate, sample size, base rate, out-of-sample result, or calibration for setups was found: UNVERIFIED / likely absent.** The Algo backtest report has a DTE summary with a win-rate column and an intrabar SL option that tests stops against each 1-min bar's high/low. The terminals show win rate and profit factor for the user's own trades. The site's calculator pages warn that win rate alone is meaningless without the payoff ratio. | [OFFICIAL] https://options.fnotrader.com/help.html ; https://www.fnotrader.com/options ; https://algo.fnotrader.com/ ; https://www.fnotrader.com/blog/options-strike-charts-buildup-tags ; https://www.fnotrader.com/blog/fnotrader-free-trading-calculators-position-sizing-kelly . Exact setup thresholds, short-side rules, and setup history page: **UNVERIFIED** |
| **Zerodha Kite** | Native option chain with Greeks (Delta, Gamma, Theta, Vega) per strike, order entry from the chain, and a **basket** showing initial and final margin including the hedge benefit. Payoff and strategy building go through Sensibull. | [OFFICIAL] https://support.zerodha.com/category/trading-and-markets/kite-web-and-mobile/articles/kite-option-chain ; https://zerodha.com/z-connect/business-updates/introducing-the-all-new-option-chain-on-kite |
| **Upstox** | Native Options Strategy Builder that places up to 4 orders at once. Chain Greeks and payoff details: **UNVERIFIED**. | [OFFICIAL] https://upstox.com/market-talk/up-your-trading-game-with-options-strategy-builder |

**Takeaway for India.** The Indian stack is retail-first. Its strengths are OI build-up, participant-OI dashboards, payoff builders, and 1-min-bar backtesting with re-entries. No Indian product found offers a pro-grade **vol surface with sticky-strike/sticky-delta dynamics**, **P&L attribution by Greek**, **portfolio scenario grids**, or **tick-level chain replay**. That gap is where Axiom Desk can differentiate.

---

## 2. Global platforms

### 2.1 Dealer positioning (GEX / vanna / charm)
- **SpotGamma**:
  - Key levels: Call Wall, Put Wall, Volatility Trigger, Hedge Wall (the strike with the largest change in gamma), Gamma Notional.
  - **HIRO**: real-time hedging-impact estimate per trade across the US market.
  - **TRACE**: intraday heatmap with Gamma, Delta Pressure and **Charm Pressure** lenses.
  - **Equity Hub**: covers 3,500+ names, with Total-OI and **Synthetic-OI** lenses, plus level alerts.
  - Sources: [OFFICIAL] https://spotgamma.com/equity-hub/ ; https://spotgamma.com/identifying-opportunities-with-hiro ; https://support.spotgamma.com/ ; https://spotgamma.com/vanna-and-charm-explained/
- **Volland (vol.land)**:
  - Breaks dealer exposure out by Greek (gamma, **vanna**, **charm**), with separate positioning-attribution methods. SPX focus.
  - Sources: [3P] https://benzinga.com/z/32822214 . 0DTE-specific Volland tools: **UNVERIFIED**.
- **Unusual Whales**: flow-first rather than exposure-first, but also shows GEX, DEX and vanna.
  - Sources: [3P] https://optionstradingiq.com/unusual-whales-review/ ; https://flashalpha.com/articles/spotgamma-vs-unusual-whales-comparison
- Shared caveat: dealer positioning is **inferred, not observed**.
  - Sources: https://convextrade.com/glossary/vanna-charm ; https://flashalpha.com/research/dealer-positioning

### 2.2 Flow / unusual activity
- **Unusual Whales**:
  - Real-time feed of sweeps, blocks, 0DTE flow and net premium.
  - Dark-pool prints from 50+ ATS venues.
  - Alerts and an API.
  - Sources: [OFFICIAL] https://unusualwhales.com/api_lander ; [3P] https://daytradingtoolkit.com/reviews/unusual-whales-review
- **LiveVol Pro (Cboe)**:
  - Options time & sales from **2011**, scrolling trades, alerts and scanners.
  - Sources: [OFFICIAL] https://datashop.cboe.com/livevol-pro
- **TrendSpider** comparison of UOA data vendors: https://trendspider.com/blog/unusual-options-activity-data-provider-comparison/

### 2.3 Volatility surface / term structure / skew / IV vs RV
- **ORATS**:
  - A smoothed IV curve fit between call and put bid/ask (SMV).
  - `unadjVol`: ATM term structure with the **earnings effect removed**. `earnEffect`: the market-implied earnings component.
  - ivHV-ratio indicators, for example "buy straddle when IV/HV < 0.85".
  - Sources: [OFFICIAL] https://orats.com/docs/definitions ; https://orats.com/blog/how-orats-removes-earnings-effect-from-implied-volatility ; https://orats.com/blog/trading-when-implied-is-a-specific-amount-over-realized-volatility
- **Market Chameleon**:
  - IV30 % Rank, term structure, IV vs HV, Volatility Compare.
  - Implied-move charts and "Implied Moves and IV Crush".
  - Sources: [OFFICIAL] https://marketchameleon.com/Learn/Volatility ; https://www.marketchameleon.com/volReports/VolatilityRankings
- **LiveVol**:
  - Historical skew, volatility charting, and historical IV and Greeks data.
  - Sources: [OFFICIAL] https://livevol.com/analytics-platforms ; https://www.cboe.com/solutions/options-analytics/historical-data
- **tastytrade**:
  - IV Rank (0–100 over a 1-year range), expected move (±1σ = S·IV·√(t/365)), POP on the ticket.
  - Sources: [OFFICIAL] https://tastylive.com/definitions/iv-rank ; https://tastyworks.freshdesk.com/support/solutions/articles/43000435395-platform-glossary

### 2.4 Earnings / event vol
- **ORATS** "Straddle Earn Move":
  - Implied post-earnings move, extracted from straddles with a proprietary post-event distribution.
  - Compared against the average realised move over the last 12 quarters.
  - Includes an earnings-strategy backtester.
  - Sources: [OFFICIAL] https://orats.com/docs/core-research ; https://orats.com/blog/earnings-options-strategies-backtest
- **LiveVol**: earnings event analysis.
  - Sources: https://datashop.cboe.com/livevol-pro

### 2.5 Backtesting fidelity
- **Option Omega**:
  - 1-min data from Jan 2013, good enough for 0DTE.
  - Entry filters on VIX level, delta and DTE.
  - Portfolio of backtests; CSV export.
  - It **documents that SL/PT fills can land "past" the trigger at bar granularity**.
  - Only end-of-day SPX expiries, no AM-settled ones.
  - Sources: [OFFICIAL] https://docs.optionomega.com/backtesting/backtesting-faq ; https://docs.optionomega.com/backtesting . Slippage and commission model: **UNVERIFIED**.
- **OptionNet Explorer**:
  - Manual **historical chain replay**: set the clock to any date and time in 5-min steps, then see prices, IV, Greeks, and intrinsic and extrinsic value.
  - Tracks adjustments and commissions across a position's life.
  - Windows desktop only.
  - Sources: [3P] https://optionstradingiq.com/optionnet-explorer-review/ ; https://steadyoptions.com/articles/optionnet-explorer-one-options-backtesting-software-r743 . Data start year: **UNVERIFIED**.
- **thinkorswim thinkBack**: historical chain lookup inside the Analyze tab.
  - Sources: [OFFICIAL] https://toslc.thinkorswim.com/center/howToTos/thinkManual/Analyze
- **ORATS backtester**: rule-based backtests on its historical data and proprietary indicators.
  - Sources: https://orats.com/backtester . History start year: **UNVERIFIED**.

### 2.6 Position risk / scenario
- **thinkorswim Analyze → Risk Profile**:
  - P&L curve by date.
  - **Price Slices** with Greeks per slice, set in %, $, σ or estimated range.
  - **Vol Adj** to shock IV, e.g. +10 pts.
  - Probability Analysis: the probable price range by date, and POP.
  - Sources: [OFFICIAL] https://toslc.thinkorswim.com/center/howToTos/thinkManual/Analyze ; [OFFICIAL] https://tickertape.tdameritrade.com/trading/analyze-tab-thinkorswim-platform-volatility-18793 ; https://www.schwab.com/learn/story/analyze-vertical-spreads-with-risk-profile-tool
- **tastytrade**:
  - **Curve Analysis**: drag legs to see Greeks, max P/L and breakevens update.
  - **Beta-weighted delta** to SPX, for portfolio-level directional risk.
  - Sources: [3P] https://curvedtrading.com/articles/en/brokers/tastytrade/ . Exact UI: **UNVERIFIED**.
- **P&L attribution by Greek** (delta/gamma/theta/vega/residual): no retail platform above was confirmed to offer it. It is standard desk practice and is implied by Sinclair, Taleb and Bennett (see §3). Treat it as a **gap to fill, UNVERIFIED in vendors**.

---

## 3. Canonical references → what each one requires the platform to have
These are standard texts. Chapter-level claims are confirmed only where a URL is given. The rest come from general knowledge of the books and were **not re-verified this session**.

| Book | What it requires the platform to have |
|---|---|
| **Natenberg, *Option Volatility & Pricing*** (2nd ed.) | Theoretical value vs market price, i.e. an **edge column** on the chain. Volatility types: historical, forecast, implied, future. **Volatility spreads** (backspreads, ratio spreads, calendars) and how they behave. Risk measurement through Greek-based position sheets. Skew and intermarket spreads. A chapter on how models break down in the real world. The platform needs a **theo-vs-market chain** with a user vol input, **Greek position sheets**, and **what-if grids over spot × vol × time**. Sources: https://valsec.barnesandnoble.com/w/option-volatility-pricing-sheldon-natenberg/1101371824 ; https://www.eyrolles.com/Loisirs/Livre/option-volatility-and-pricing-9781557384867 |
| **Sinclair, *Volatility Trading*** (2nd ed.) | Realised-vol estimators and forecasting. A chapter on the **variance premium**. **Volatility cones plus skew and kurtosis cones** (Appendix B). Vol mean reversion, clustering and long memory. **Hedging P&L** of delta-hedged options (hedging at implied vs at realised vol). Sizing. The platform needs **RV estimator choice** (close-to-close, Parkinson, Garman-Klass, Yang-Zhang: names **UNVERIFIED** against the book), **vol cones**, an **IV−RV (VRP) series**, and a **delta-hedge simulator**. Sources: https://www.schweitzer-online.de/en/buch/Sinclair/Volatility-Trading/9781118347133/B367298/ ; https://gmarti.gitlab.io/qfin/2023/04/30/book-volatility-trading-sinclair.html |
| **Sinclair, *Positional Option Trading*** (2020) | Edges to look for: variance premium, **term-structure premia**, earnings effects. Choosing the **structure** that best captures a given edge. Choosing a hedging strike. **Trade sizing for option portfolios** (Ch. 9). Robustness of BSM. The platform needs **edge scanners** (VRP, term-structure carry, event vol), a **structure comparator**, and **position sizing** that accounts for skewness. Sources: https://www.schweitzer-online.de/en/buch/Sinclair/Positional-Option-Trading/9781119583516/B490028/ |
| **Passarelli, *Trading Option Greeks*** | Second-order Greeks and how Greeks change with time and IV. Managing positions by their Greek profile, e.g. trading gamma against theta. The platform needs **Greeks through time** (time slider), **portfolio Greek aggregation**, and **Greek-target adjustment suggestions**. Contents **UNVERIFIED** (no source found). |
| **Taleb, *Dynamic Hedging*** | Shadow Greeks, meaning Greeks that include the change in vol along with the move in spot. Bucketed vega by expiry. **Pin risk** at expiry. Barrier and liquidity holes. **Stress tests** beyond local Greeks. The platform needs **vega by expiry bucket**, **shadow/scenario Greeks** (full revaluation under joint spot and vol shocks), and a **pin-risk monitor** on expiry day. Contents **UNVERIFIED** (no source found). |
| **Hull, *Options, Futures and Other Derivatives*** | The canonical BSM/Black-76, binomial and Greeks math. Futures-based pricing. The platform needs **correct pricing models**: Black-76 on futures for index options, a dividend-aware forward for stock options, and an IV solver. Contents **UNVERIFIED** (general knowledge). |
| **Bennett, *Trading Volatility*** | **Skew dynamics** (sticky-strike vs sticky-delta), skew theta and skew gamma, term structure, variance and vol swaps, dispersion and correlation. Hedging P&L is not path-dependent when you hedge at the realised vol. The platform needs a **surface model with a selectable sticky rule**, **skew metrics** (25Δ risk-reversal, butterfly), **term-structure slope**, and **implied correlation / dispersion** for index vs constituents. Sources: https://lr.sudovanilla.org/r/quant/comments/1cq04af/thinking_about_and_trading_volatility_skew ; sticky rules: https://moontowermeta.com/sticky-vs-floating-strike/ ; https://www.risk.net/derivatives/1506219/sticky-strike-and-sticky-delta-greeks-casualties-of-the-subprime-crisis |

---

## 4. India data reality

### 4.1 What NSE publishes
- **Participant-wise OI and volume** for Client, DII, FII and Pro:
  - Long and short contracts across index futures, index options (calls and puts split), stock futures and stock options.
  - Published **once a day after the close**, typically by about 19:00 IST. **There is no intraday version.**
  - BSE publishes an equivalent.
  - Sources: [3P] https://algotest.in/blog/participant-wise-open-interest/ ; [OFFICIAL BSE] https://bseindia.com/markets/Derivatives/DeriReports/DeriMarketDisclosures.aspx . The exact NSE archive URL was not fetched: **UNVERIFIED**. Back-history from 2012 is per a third party: https://tapetide.com/insight/participant-wise-open-interest
- **Real-time and historical feeds** from NSE Data & Analytics:
  - Level 1/2/3 and **tick-by-tick (TBT)** for CM and F&O.
  - F&O snapshot product (15-min-delayed, 1-min interval).
  - Historical trade data for F&O.
  - TBT is a licensed product, delivered via colo or authorised vendors.
  - Sources: [OFFICIAL] https://www.nseindia.com/market-data/real-time-data-subscription ; https://www.nseindia.com/nsedataandanalytics ; spec: https://nsearchives.nseindia.com//web/mediaattachment/2026-08/Snapshot_15_FAO_v1.8.pdf
  - Vendors: Global Datafeeds, TrueData. One source notes most vendors redistribute a **1-sec netted snapshot**, not true TBT.
  - Sources: https://www.marketcalls.in/softwares/data-vendors-and-quality-of-datafeeds.html ; https://www.truedata.in/
  - Price and date range of historical F&O TBT: **UNVERIFIED**.
- **Bhavcopy** (daily F&O settlement, OI and volume file), **security-wise delivery position**, **bulk/block deals**: published by NSE, but no page was fetched to confirm format or URL. **UNVERIFIED**.
- **MWPL / ban list**:
  - Daily notice. A stock enters the ban when OI exceeds 95% of MWPL. During the ban, positions can only be reduced.
  - Historically, the stock exits the ban once OI falls below 80%.
  - Sources: [3P] https://www.indiainfoline.com/knowledge-center/derivatives/why-are-stocks-banned-in-f-and-o
  - The May-2025 circular changed the **MWPL computation and ban rules** (based on FutEq OI) from 1 Oct 2025. The new thresholds were **not verified**; re-check before building.
  - Sources: https://www.businesstoday.in/markets/story/sebi-equity-fo-rules-futeq-method-mwpl-risk-management-478321-2025-05-29

### 4.2 Contract style and settlement
- **Exercise style**: both index options and single-stock options are **European**. NSE product page: https://www.nseindia.com/products-services/equity-derivatives-individual-securities
- **Settlement**:
  - **Index options are cash-settled.**
  - **Stock options (and stock futures) are physically settled.** NSE's product page says so, and the phase-in ran 2018–Oct 2019 per secondary sources.
  - Several third-party sites wrongly say stock options are cash-settled. Ignore them.
  - Settlement mechanism page: https://nseindia.com/products-services/equity-derivatives-settlement-mechanism
- **What this means for Axiom**:
  - Stock-option expiry risk includes a **delivery margin and obligation**, which needs an ITM-into-expiry physical-delivery alert.
  - Index options price off futures/forward, so use Black-76.

### 4.3 SEBI rule changes, 2024–25
- **Circular SEBI/HO/MRD/TPD-1/P/CIR/2024/132 (1 Oct 2024)**. Sources: https://zerodha.com/z-connect/business-updates/sebis-new-rules-for-index-derivatives-heres-whats-changing ; https://www.taxmann.com/post/blog/analysis-sebis-new-equity-index-derivatives-regulations
  - **Contract value**: minimum ₹15 lakh at introduction (previously ₹5–10 lakh). Lot sizes were reset to match, from 20 Nov 2024.
  - **One weekly-expiry benchmark per exchange**: NSE keeps Nifty 50; BankNifty, FinNifty and MidcapSelect weeklies were discontinued. BSE keeps Sensex.
  - **Upfront collection of option premium.**
  - **No calendar-spread margin benefit on expiry day** (from 1 Feb 2025).
  - **Extra 2% ELM on short options on expiry day.** Figure **UNVERIFIED**; sources only say "additional tail-risk margin".
  - **Intraday monitoring of position limits** (from 1 Apr 2025).
- **Expiry days**:
  - SEBI limited exchanges to **Tuesday or Thursday**, with one expiry day per exchange.
  - From **1 Sep 2025**, NSE moved to **Tuesday** and BSE to **Thursday**.
  - Sources: https://www.business-standard.com/markets/news/nse-bids-adieu-to-thursday-expiry-as-dates-swap-come-into-effect-explained-125082800635_1.html ; https://www.bajajbroking.in/blog/sebi-approves-nses-tuesday-expiry-shift
- **Circular SEBI/HO/MRD/TPD-1/P/CIR/2025/79 (29 May 2025)**. Sources: https://www.business-standard.com/amp/markets/news/sebi-fo-revamp-new-oi-metric-position-limits-july-december-rollout-125052901798_1.html ; https://www.bajajbroking.in/blog/sebi-notifies-new-f-and-o-rules-with-higher-index-limits-and-risk-measures
  - **Delta-based "FutEq" OI** at portfolio level.
  - **Index-option limits per PAN**: **₹1,500 cr net** FutEq (end of day) and **₹10,000 cr gross** per side.
  - Clearing corporations run **intraday FutEq monitoring at ≥4 random times** a session.
  - MWPL and ban rules revised from 1 Oct 2025.
  - Intraday MWPL monitoring from 3 Nov 2025.
  - Full index-option limit regime from 6 Dec 2025.
  - Not checked for amendments after Dec 2025: **UNVERIFIED**.
- **What this means for Axiom**: the risk engine must compute **FutEq (delta-weighted) OI per PAN intraday** and show headroom against the net and gross limits.

### 4.4 Jane Street interim order (SEBI, 3 Jul 2025)
This summarises SEBI's allegations, which are **interim and contested** by Jane Street.

- **Parties**: four JS-group entities: JSI Investments, JSI2 Investments, Jane Street Singapore, Jane Street Asia Trading.
- **Amount**: ₹4,843.57 cr impounded as alleged unlawful gains. JS deposited it on 14 Jul 2025 and disputes the findings.
- **Scope**: 18 BankNifty expiry days and 3 Nifty expiry days.
- **"Strategy A": intraday index manipulation**. The 17 Jan 2024 BankNifty expiry is the anchor example.
  - **Patch I (~09:15–11:46)**: bought BankNifty constituent stocks and stock futures (≈₹4,370 cr) to push the index up. At the same time, built very large **bearish index-options positions**. Options sold were ≈₹32,115 cr; peak short options exposure ≈₹46,620 cr.
  - **Patch II (~11:49–close)**: sold the cash and futures inventory and drove the index down. The bearish options book profited.
  - **Day result**: ≈₹735 cr options profit vs ≈₹61.6 cr cash/futures loss.
  - SEBI's core theory: **the thin cash/futures leg was used to move the index, while a far larger options book captured the move**. The volume imbalance between the two legs created the opportunity.
- **"Strategy B": extended marking the close**. Aggressive cash/futures trades near the close move the settlement VWAP in favour of the options book.
  - Example: 10 Jul 2024 and two other days. A ₹44,154 cr BankNifty options short carried into the close; a ≈₹225 cr gain is attributed to the soft close.
  - A bullish Nifty variant on 15 May 2025: large long options exposure, with heavy buying of Nifty and constituent futures in the last ~116 min.
- Sources: [3P] https://blogs.law.ox.ac.uk/oblb/blog-post/2025/07/jane-street-and-expiry-day-trap-unpacking-sebis-crackdown-algorithmic ; https://www.moneylife.in/article/jane-street-accused-of-massively-rigging-of-indias-derivatives-market-sebi-orders-ban-escrow-of-rs4843-crore-illegal-gains/77585.html ; https://www.businesstoday.in/markets/story/sebi-cracks-down-on-jane-street-in-landmark-derivatives-market-case-484348-2025-07-11 ; https://www.ecgi.global/publications/blog/expiry-day-and-the-governance-of-algorithmic-trading-the-jane-street-episode
- Primary order PDF not fetched. Exact call/put composition: **UNVERIFIED**.
- **What this means for Axiom**: it implies a surveillance and analytics view that **links a participant's cash/futures index-constituent flow to their options delta and gamma on expiry day**. It also implies a **settlement-window (VWAP) impact monitor** and **index-constituent weighted-flow attribution**. This is useful both for compliance (broker clients) and for a desk reading expiry-day tape.

---

## 5. Caveat: does US-style GEX hold in India?
- **The US convention**: customers are net long options and dealers are short and delta-hedged. GEX signs calls + and puts −, by option type. Every India GEX vendor found (stockmock-style, optionslens, stockmojo, tradejini) **applies the US convention unchanged**. None cites validation.
  - Sources: https://stockmojo.in/gamma-exposure ; https://www.tradejini.com/blogs/how-traders-can-use-gamma-exposure-to-understand-market-direction-part-1
- **No source found that tests the assumption for NSE.** The evidence below **contradicts the premise**:
  - **Proprietary traders account for about half of index-options premium turnover**, individuals about a third, FPIs single digits.
    - Sources: [FIA, NSE data] https://www.fia.org/marketvoice/articles/premium-turnover-indian-options-hits-150-billion ; NSE Market Pulse Nov 2024 (individuals 35%, prop 48% of equity-options premium turnover, FY25 YTD): https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Market%20Pulse_November%202024_FINAL_3.pdf
  - The SEBI FY22–24 study found prop and FPI profits (₹33k cr and ₹28k cr gross in FY24), **~96–97% of it from algo trading**, while 91.5% of individuals lost money in options.
    - Sources: https://theprint.in/economy/individual-traders-incurred-cumulative-net-loss-of-rs-1-8-lakh-crore-in-derivatives-market-in-3-yrs/2280936
    - This is consistent with prop/HFT/FPI acting as liquidity providers and option sellers. Inference: **UNVERIFIED** as a measured sign of net gamma.
  - The **Jane Street order** shows one large FPI-group player running **net short or net long options books of ₹40k cr+ notional and trading the underlying against them**, not delta-hedging passively.
- **The India advantage**: NSE participant-wise OI gives **long and short call and put contracts by Client/Pro/FII/DII each day**. So the **sign of each category's options position is observable** at category level, at end of day. That is better than the US, where it is assumed.
  - The data has no strike split and no intraday version. Strike-level GEX therefore still needs an assumption, e.g. distributing each category's net position across strikes in proportion to OI changes. That allocation is **UNVERIFIED / design choice**.
- **Recommendation**: label any GEX as "model, sign-convention X". Ship **participant-aware GEX**: the category sign comes from participant OI, the strike shape from the chain, and there is a toggle back to the US convention. Backtest which variant explains Nifty intraday realised-vol regimes before trusting it.

---

## 6. Capability checklist (deduplicated)
Source keys: FNO=FnOTrader, SB=Sensibull, OP=Opstra, QA=Quantsapp, AT=AlgoTest, SM=StockMock, KT=Kite, UP=Upstox, SG=SpotGamma, VL=Volland, UW=Unusual Whales, OR=ORATS, MC=Market Chameleon, LV=LiveVol, ONE=OptionNet Explorer, OO=Option Omega, TT=tastytrade, TOS=thinkorswim, NAT/SIN/SIN-P/PAS/TAL/HULL/BEN=books, NSE/SEBI=regulatory, JS=Jane Street order. **(gap)** = no vendor confirmed; derived from the books or regulation.

**A. Chain and pricing**
1. Live chain with bid/ask, OI, ΔOI, volume, IV, and full Greeks per strike; order entry from the chain. [KT, SB, QA]
2. Correct models: Black-76 on futures for index options, a dividend-aware forward for stock options, and a robust IV solver. [HULL, NSE settlement] (gap)
3. A theo vs market "edge" column driven by a user or desk vol surface. [NAT] (gap)
4. A smoothed IV curve fit inside bid/ask, plus an earnings- or event-stripped ATM vol. [OR]

**B. Volatility analytics**

5. IV rank and IV percentile (1-year/252-day), IV history per strike. [OP, MC, TT]
6. RV estimators, an IV−RV (VRP) series, and vol cones, including skew and kurtosis cones. [SIN, OR ivHV, MC IV-vs-HV, OptionAction cone]
7. A term-structure chart with slope/carry metrics, and IV skew by expiry; 25Δ RR/fly time series. [MC, OP, LV, BEN]
8. A full vol surface (strike/delta × expiry) with a selectable sticky-strike/sticky-delta rule for scenarios. [BEN, OP-Pro (UNVERIFIED)] (gap in India)
9. Event vol: implied move, comparison with historical realised event moves (12 quarters), and an IV-crush view. India events: results, RBI policy, Budget, elections. [OR, MC]
10. Expected move (±1σ) and probability cones on charts. [TT, TOS]
11. Implied correlation / dispersion, Nifty vs constituents. [BEN] (gap)

**C. OI, flow, positioning**

12. OI build-up classification by scrip, breadth and sector (long/short build-up, unwinding, covering); max-OI strikes; PCR. [QA, SB]
13. Participant-wise OI/volume dashboard (FII/DII/Pro/Client) with history and net call/put long/short. [QA, SB, NSE]
14. An unusual-activity scanner (volume vs OI, premium size, IV jump), plus large-trade/sweep detection from TBT. [QA, UW, LV]
15. Options time & sales with historical lookback. [LV]
16. Dealer/participant exposure: GEX, DEX, vanna, charm by strike and expiry, with key levels (call/put wall, flip/trigger) and intraday charm/delta-pressure views. [SG, VL, UW]
17. **Participant-aware sign convention** for exposure, with a toggle back to the US convention. [§5, NSE participant OI] (gap)
18. A hedging-impact (HIRO-style) real-time flow indicator. [SG]

**D. Strategy and position risk**

19. Multi-leg strategy builder: payoff by date, breakevens, max P/L, POP, drag-adjust (curve analysis), and basket execution with hedge-aware margin. [SB, OP, UP, KT, TT, TOS]
20. Scenario grid: spot slices (%, ₹, σ) × IV shock × date, with Greeks per slice; full revaluation (shadow Greeks). [TOS, TAL, NAT]
21. Portfolio Greeks aggregation, beta-weighted to Nifty, and vega bucketed by expiry. [TT, TAL, PAS]
22. **P&L attribution by Greek** (Δ, Γ, Θ, ν, residual) daily and intraday, plus gamma-scalping / delta-hedge P&L tracking. [SIN, BEN, TAL] (gap)
23. Trade sizing for option portfolios that accounts for skew, and an edge → structure comparator. [SIN-P] (gap)
24. Expiry-day monitors: pin risk, ITM stock options heading into **physical delivery**, expiry-day margin uplift, and loss of calendar-spread benefit. [TAL, NSE, SEBI 2024/132]

**E. Backtesting and replay**

25. Rule-based backtester: entry/exit by time, delta, DTE, VIX/IV filters; SL/PT; re-entry modes; adjustments; portfolio of backtests; CSV export. [AT, OO, OR]
26. Historical chain replay at the chosen resolution, with manual adjustments and cumulative P&L. [ONE, SM, TOS thinkBack]
27. Explicit fidelity model: fill at bid/ask or with a slippage function, ordering of SL and entry within a bar, ATM tie-break rule, costs (STT, exchange fees, stamp duty, GST), and a reconciliation report of backtest vs forward test vs live. [AT documents the gaps, OO documents SL overshoot] (gap: tick-level replay)
28a. **Signal/setup evidence card**. Every published setup or signal carries: N (sample size), base rate (unconditional hit rate for the same target and stop), hit rate with a CI, expectancy net of costs, an in-sample vs out-of-sample split, and a calibration plot (predicted vs realised). This goes beyond FnOTrader's same-day T1/SL label and AlgoTest/Option Omega raw backtests. [FNO shows outcome labels only; SIN-P sizing] (gap)
28. Regime-aware data: lot-size history, the Sept 2025 expiry-day change, and discontinued weeklies, so backtests use the contract specs in force on each date. [SEBI, NSE] (gap)

**F. Compliance and surveillance (broker-facing)**

29. Intraday FutEq (delta-based) OI per PAN vs the ₹1,500 cr net / ₹10,000 cr gross index limits; MWPL utilisation and ban-list alerts. [SEBI 2025/79, NSE]
30. Upfront premium and margin pre-check, including expiry-day ELM. [SEBI 2024/132]
31. Expiry-day cross-segment surveillance: the same entity's constituent cash/futures flow vs its options delta/gamma; settlement-window VWAP impact. [JS]

**G. Data plumbing**

32. TBT or at least 1-sec snapshot ingest; daily ingest of bhavcopy, participant OI, ban list, delivery, and bulk/block deals; point-in-time contract master. [NSE, vendors]
33. Alerts on any metric above: level, IV rank, OI spike, flow, limit headroom. [SG, LV, QA]

---
Not checked: primary SEBI order PDFs and NSE archive pages (WebFetch blocked by a local hook), current vendor pricing, Tradl's identity, and Passarelli/Taleb/Hull contents. Risk: the Indian competitive feature claims come mostly from third-party or competitor pages. Confirm before positioning against any named product.
