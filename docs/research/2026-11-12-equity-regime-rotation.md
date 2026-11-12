# Equity intelligence: regime, rotation, hidden triggers, position management

Date: 2026-11-12 · Scope: research only, no code · Product: Axiom Desk equity module (internal desk first, broker white-label later)

## Method and evidence rules

- Sources found and checked via WebSearch (title, authors, venue, year, DOI/link from EconPapers/IDEAS/NBER/publisher/author pages). WebFetch was not used, so claims rest on abstracts, publisher metadata and author/working-paper copies, not full-text reads. Effect sizes quoted are from abstracts; treat as headline numbers, not replicated.
- `UNVERIFIED` = not confirmed by a search this session. Recalled-from-memory items are labelled so.
- Evidence grades: **strong** (top journal + replication across markets/periods), **moderate** (peer-reviewed, limited replication or India-only regional journals), **weak** (working paper / broker study / single sample), **folklore** (practitioner rule, no out-of-sample test found).
- Big caveat up front: **India-specific peer-reviewed evidence is thin** for almost every "hidden trigger". Most India positioning signals (FII L/S ratio, PCR, MTF) have only broker/media backing. The platform must backtest them on NSE data itself before shipping them as signals. That is a product requirement, not a footnote.

---

## 1. Sector / industry rotation

**What the evidence says**

| Claim | Source | Grade |
|---|---|---|
| Industry momentum explains a large part of stock momentum; industry momentum survives size/value/stock-momentum controls | Moskowitz & Grinblatt, "Do Industries Explain Momentum?", *J. Finance* 54(4), 1999, 1249–1290, doi:10.1111/0022-1082.00146 — https://ideas.repec.org/a/bla/jfinan/v54y1999i4p1249-1290.html | strong (contested: Grundy-Martin 2001, Lewellen 2002 dispute "explains") |
| Some industries' returns lead the market by up to ~2 months (retail, services, real estate, metals, petroleum); holds in 8 largest non-US markets; mechanism = slow information diffusion | Hong, Torous & Valkanov, "Do industries lead stock markets?", *JFE* 83(2), 2007, 367–396, doi:10.1016/j.jfineco.2005.09.010 — https://escholarship.org/content/qt6x49x543/qt6x49x543.pdf | strong-moderate |
| Classic business-cycle sector rotation adds only ~2.3%/yr gross **with perfect foresight** of NBER cycle; 1–2 months timing error erodes most of it | Stangl, Jacobsen & Visaltanachoti, "Sector Rotation over Business Cycles", working paper 2009 — https://www.cxoadvisory.com/economic-indicators/perfect-sector-rotation (summary; full text not retrieved) | moderate (WP) |
| No systematic sector performance where popular cycle-rotation belief expects it | Stangl & Molchanov, "The myth of business cycle sector rotation", *Int. J. Finance & Economics*, 2023 — https://mro.massey.ac.nz/handle/10179/69590 | moderate |
| Price momentum partly = slow reaction to earnings news; analyst forecast revisions predict drift independently of price | Chan, Jegadeesh & Lakonishok, "Momentum Strategies", *J. Finance* 51(5), 1996, 1681–1713 — https://ideas.repec.org/a/bla/jfinan/v51y1996i5p1681-1713.html | strong |
| Nearness to 52-week high predicts returns better than past return; no long-run reversal | George & Hwang, "The 52-Week High and Momentum Investing", *J. Finance* 59(5), 2004, 2145–2176, doi:10.1111/j.1540-6261.2004.00695.x | strong |
| Value & momentum premia exist across 8 markets/asset classes with a common factor structure | Asness, Moskowitz & Pedersen, "Value and Momentum Everywhere", *J. Finance* 68(3), 2013, 929–985 — https://pages.stern.nyu.edu/~lpederse/papers/ValMomEverywhere.pdf | strong |
| Cross-sectional dispersion: high dispersion → higher later value premium, lower later momentum premium (countercyclical state variable) | Stivers & Sun, *JFQA* 45(4), 2010, 987–1014, doi:10.1017/S0022109010000384 | moderate-strong |
| India: short-horizon continuation + weak long-horizon reversal (1989–99); 3m/3m momentum best | Sehgal & Balakrishnan (2002, cited secondarily); Ansari & Khan, "Momentum anomaly: evidence from India", *Managerial Finance*, 2012 — https://emerald.com/insight/content/doi/10.1108/03074351211193730/full/html ; "Short-term momentum patterns in stock and sectoral returns: evidence from India" (Emerald, doi:10.1108/09727981111129327) | moderate (regional; not full-text checked) |

**What actually leads rotation (ranked by evidence)**
1. **Earnings-revision momentum / breadth** (Chan-Jegadeesh-Lakonishok 1996) — fundamentals move before price finishes. Strongest "early" lever.
2. **Relative-strength persistence at the industry level** (Moskowitz-Grinblatt) — detects rotation *in progress* fast, but it's confirmation, not prediction.
3. **Leading-industry cross-signals** (Hong-Torous-Valkanov) — metals/energy/real-estate/retail returns carry macro info.
4. **Rates and credit** — via macro regime (see §3); sector mapping by cycle phase is weak on its own (Stangl et al.).
5. **Flows** — mostly *follow* returns (see §4, FII positive-feedback literature). Useful for crowding, not lead.

Implication: a "sector rotation clock" UI based on business-cycle phase is **folklore-grade**. Build rotation from measured relative strength + revision breadth + dispersion, not from a cycle diagram.

> **Platform capability:** Industry relative-strength engine (RS vs Nifty 500, 3/6/12m, skip-month), revision-breadth per sector, 52w-high proximity per stock, dispersion monitor; no static cycle-clock as a signal.

---

## 2. Adaptive / regime-aware modelling

| Concept | Source | Use |
|---|---|---|
| Markov-switching regimes; shifts are latent and inferred probabilistically | Hamilton, "A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle", *Econometrica* 57(2), 1989, 357–384, doi:10.2307/1912559 | Base regime model (bull/bear/crisis states with transition matrix) |
| Survey: regimes most reliably demarcated by volatility level; regimes materially change optimal portfolios | Ang & Timmermann, "Regime Changes and Financial Markets", *Annu. Rev. Fin. Econ.* 4, 2012, 313–337 — https://www.nber.org/papers/w17182 | Volatility is the primary regime axis |
| Online run-length posterior for most recent change-point | Adams & MacKay, "Bayesian Online Changepoint Detection", arXiv:0710.3742, 2007 — https://arxiv.org/abs/0710.3742 | Real-time break alerts on signal series |
| HMM with time-varying params + model-predictive control; two regimes suffice; trading penalty adds robustness; reduces drawdowns vs static weights | Nystrup, Madsen & Lindström, *Quantitative Finance* 18(1), 2018, 83–95 — https://econpapers.repec.org/RePEc:taf:quantf:v:18:y:2018:i:1:p:83-95 ; Nystrup et al., *JPM* 2017 (regime-based allocation profitable vs 60/40) | Regime → allocation with turnover penalty |
| Markets evolve; edges wax/wane as participants adapt | Lo, "The Adaptive Markets Hypothesis", *JPM* 30, 2004, 15–29 — https://web.mit.edu/Alo/www/Papers/JPM2004.html | Philosophy: every signal has a lifecycle |
| Anomaly returns −26% out-of-sample, −58% post-publication (97 predictors) | McLean & Pontiff, "Does Academic Research Destroy Stock Return Predictability?", *J. Finance* 71(1), 2016, 5–32, doi:10.1111/jofi.12365 | Haircut every published signal by ~half |
| Multiple-testing: new factors need t > 3.0; most published findings likely false | Harvey, Liu & Zhu, "…and the Cross-Section of Expected Returns", *RFS* 29(1), 2016, 5–68 — https://www.nber.org/papers/w20592 | Signal admission gate |
| Contrarian value-spread factor timing: no robust gain for diversified factor portfolios (Sharpe 0.55→0.54) | Asness, Chandra, Ilmanen & Israel, "Contrarian Factor Timing is Deceptively Difficult", *JPM* 43(5), 2017, 72–87 | Don't over-time factors; diversify |
| Momentum crashes occur in panic states (after declines, high vol, at rebounds) and are forecastable; dynamic scaling ~doubles Sharpe | Daniel & Moskowitz, "Momentum crashes", *JFE* 122(2), 2016, 221–247, doi:10.1016/j.jfineco.2015.12.002 | The one factor-timing rule with strong evidence: de-risk momentum after crashes + high vol |
| ML (trees, NNs) can double regression-strategy performance; dominant signals = momentum, liquidity, volatility | Gu, Kelly & Xiu, "Empirical Asset Pricing via Machine Learning", *RFS* 33(5), 2020, 2223–2273, doi:10.1093/rfs/hhaa009 | ML ranking layer OK, but feature set is mostly price/vol/liquidity |
| ML under regime change / concept drift: field early, no dominant technique; simple finance-specific drift detectors match sophisticated ones | Suárez-Cetrulo, Quintana & Cervantes, *IJIMAI* 2023 — https://www.ijimai.org/index.php/ijimai/article/view/281 ; "Domain Specific Concept Drift Detectors for Predicting Financial Time Series", arXiv:2103.14079 (UNVERIFIED beyond title listing) | Drift monitors + scheduled retrain, keep detectors simple |

**Design stance (recommended):** regime = small, interpretable state (2–3 states, volatility + trend + credit), inferred probabilistically, with change-point alerts. Signals are **conditioned on regime** (weights per regime estimated with shrinkage), not re-fit wholesale. Every signal carries a live decay monitor (rolling IC/hit-rate vs backtest; auto-demote when outside band). Avoid "one model per regime" overfitting — few regimes, few params.

> **Platform capability:** Regime service (HMM probability + BOCPD break alerts), regime-conditioned signal weights, per-signal decay/IC monitor with auto-demotion, admission gate (t>3, post-cost, OOS India backtest), McLean-Pontiff haircut on any literature-imported signal.

---

## 3. Early warning: bear markets and trend reversals

| Signal | Evidence | OOS quality | Source |
|---|---|---|---|
| Yield-curve slope | Best single recession predictor beyond 2 quarters; better alone than in combos | **strong** (US); India curve less studied — UNVERIFIED for India | Estrella & Mishkin, *REStat* 80(1), 1998, 45–61, doi:10.1162/003465398557320 |
| Credit spreads / excess bond premium | EBP shocks precede falling activity & asset prices; reflects intermediary risk capacity | **strong** (US) | Gilchrist & Zakrajšek, *AER* 102(4), 2012, 1692–1720, doi:10.1257/aer.102.4.1692 |
| Variance risk premium (implied − realized var) | Predicts market returns, strongest at quarterly horizon; beats P/E, default spread | **strong** (US) | Bollerslev, Tauchen & Zhou, *RFS* 22(11), 2009, 4463–4492, doi:10.1093/rfs/hhp008 |
| Average stock correlation (correlation spike) | Avg pairwise correlation predicts next-quarter excess market return | **moderate-strong** | Pollet & Wilson, *JFE* 96(3), 2010, 364–380, doi:10.1016/j.jfineco.2010.02.011 |
| Industry run-ups → crash probability | Run-ups don't predict lower *average* returns but sharply raise crash odds (50%→100% run-up lifts crash prob 20%→53%); vol, turnover, issuance, price-path convexity help | **strong** | Greenwood, Shleifer & You, "Bubbles for Fama", *JFE* 131(1), 2019, 20–43, doi:10.1016/j.jfineco.2018.09.002 |
| Time-series momentum / trend | Positive in extreme up and down years ("trend smile"); 1880–2016, 67 markets; did well in 8 of 10 largest 60/40 drawdowns | **strong** | Moskowitz, Ooi & Pedersen, "Time series momentum", *JFE* 104(2), 2012, 228–250 ; Hurst, Ooi & Pedersen, "A Century of Evidence on Trend-Following Investing", *JPM* Fall 2017 — https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing |
| 10-month SMA timing | Above-SMA months: much higher return / lower vol (1901–2008) | moderate (simple, widely replicated, in-sample-ish) | Faber, "A Quantitative Approach to Tactical Asset Allocation", *J. Wealth Mgmt* 2007 (venue per secondary sources; SSRN id 962461) |
| Investor sentiment (incl. IPO activity) | High sentiment → low later returns for small, young, volatile, unprofitable stocks | **strong** (cross-section) | Baker & Wurgler, *J. Finance* 61(4), 2006, 1645–1680 ; equity share in new issues: Baker & Wurgler, *J. Finance* 2000 |
| Retail fund flows ("dumb money") | High retail flows into funds predict low future returns of stocks they buy | **strong** (US 1980–2003) | Frazzini & Lamont, *JFE* 88(2), 2008, 299–322 |
| Margin credit | DKP "margin credit" measure: OOS R² ~7.5% monthly; raw margin-debt changes **lag** returns 1–2 months | mixed: DKP moderate, raw margin debt weak | Deuskar, Kumar & Poland, NYU Stern WP 2016/2017 — https://www.stern.nyu.edu/sites/default/files/assets/documents/DKP_Margin_Credit_20160901.pdf ; CXO tests |
| LPPLS bubble diagnostics | Real-time call of Shanghai 2015 by ETH FCO; but independent test fit post-hoc criteria for only 7 Hang Seng crashes, fits are "sloppy" | **weak / contested** | Sornette et al., *J. Investment Strategies* 4, 2015, 77–95 ; Brée & Joseph, *IRFA* 30, 2013, 287–297 ; Brée, Challet & Peirano, *Quant. Finance* 2013 |
| Breadth divergence, % above 200DMA, new-high/new-low, leadership narrowing | Widely used; no top-journal OOS test found this session. Related evidence: 52w-high anchoring (George-Hwang) | **folklore-to-weak** — UNVERIFIED | — |
| Dispersion collapse | Dispersion is a countercyclical state variable for factor premia, not a validated crash timer | moderate (as factor-conditioning), weak (as crash signal) | Stivers & Sun 2010 |
| Option skew / smirk (stock-level) | Steepest smirk underperforms by 10.9%/yr, persists 6m; precedes bad earnings | **strong** (US single-stock) | Xing, Zhang & Zhao, *JFQA* 45(3), 2010, 641–662 |

**Reality check:** the strongest crash-avoidance tool with century-long OOS evidence is **trend + volatility scaling**, not prediction. Macro (curve, credit, VRP) gives multi-month lead on *risk regime*, not crash dates. Breadth/new-high-low are useful dashboards but unproven as triggers — present them as context, never as signals with a hit-rate claim until India backtests exist.

> **Platform capability:** Bear-risk composite (trend state + realized/implied vol + VRP + avg correlation + credit/curve) feeding the regime service; industry run-up crash-probability flag (Greenwood-Shleifer-You features); breadth panel labelled "context, unvalidated".

---

## 4. Hidden / less-obvious India triggers (beyond volume)

User premise check: **"plain volume isn't the signal" is half-right.** Raw volume is public, but *volume conditioned on price state* is informative: high-volume winners reverse faster, low-volume winners persist (Lee & Swaminathan, "Price Momentum and Trading Volume", *J. Finance* 55(5), 2000, 2017–2069). And in India, **delivery % and volume rise significantly before bulk deals** — front-runners earn 5–7% within a week (Rajvanshi & Paul, "What's hidden behind bulk deals? A study on Indian stock market", *Managerial Finance* 48(4), 2022, 557–576, doi:10.1108/MF-08-2021-0374; IIM Calcutta WPS 863). So volume isn't useless; *unconditioned* volume is.

Second premise check: **flows mostly follow prices in India.** Multiple studies find FIIs are positive-feedback traders with bidirectional causality, and return shocks drive flows more than the reverse (Guru & Parikh 2009; Kumar 2011/2012 — regional journals, moderate). FII cash flows are a **crowding/confirmation** signal, not a lead. Derivatives positioning is where FPIs show edge: SEBI's FY22–24 study found FPIs and prop traders were profitable in F&O (97% of FPI profits from algo) while 93% of individuals lost (SEBI study, 23 Sep 2024 — https://www.business-standard.com/markets/capital-market-news/sebi-study-exposes-massive-losses-for-individual-f-o-traders-in-india-124092400948_1.html; full report on sebi.gov.in not retrieved).

| Trigger | What it signals | Lead time | Data / frequency (India) | Evidence |
|---|---|---|---|---|
| **FII index-futures long/short ratio + participant-wise OI** (FII/DII/Pro/Client) | Extremes are contrarian: very low FII L/S (e.g. 0.09, Aug 2025) historically preceded short-covering rallies; rising shorts into rally = distribution | days–weeks | NSE participant-wise OI, daily EOD, free | **weak** (HDFC Securities broker study via Business Standard, 2025 — https://www.business-standard.com/amp/markets/news/fiis-hold-10-short-bets-for-every-long-trade-in-index-futures-125080700077_1.html); no peer-reviewed India test found |
| **FII cash vs derivatives divergence** (buying cash, adding index shorts = hedged/neutral; selling cash + adding shorts = directional bear) | Separates hedging from conviction | days–weeks | NSE/NSDL FPI daily flows + participant OI | **folklore** (logic sound; untested) |
| **Option-implied skew / put-call parity deviation** (stock & index) | Informed traders use OTM puts; expensive puts → underperformance; low buyer-initiated put/call → outperformance | 1 day–6 months | NSE option chain (EOD free; tick paid). Buyer-initiated volume not public in India — must approximate | **strong** (US): Xing-Zhang-Zhao 2010; Cremers & Weinbaum, *JFQA* 45(2), 2010, 335–367 (expensive calls beat expensive puts ~50bp/wk, decaying over time); Pan & Poteshman, *RFS* 19(3), 2006, 871–908 (>1%/week, from non-public info). India replication UNVERIFIED |
| **OI build-up classification** (price × OI: long build-up / short build-up / short covering / long unwinding) | Positioning direction in stock futures | days | NSE F&O bhavcopy daily | **folklore** — standard broker heuristic, no study found |
| **India VIX level/changes & term structure** | Forecasts short-term *volatility* (good); Nifty returns negatively related to VIX changes; VIX switch large↔mid-cap helped | days–weeks (vol), weak for return level | NSE India VIX real-time; term structure must be built from option chain (no official VIX futures liquidity) | moderate for vol forecasting (Thenmozhi & Chandra, NSE WP 2013 — https://nsearchives.nseindia.com/research/content/res_WorkingPaper9.pdf); weak for return direction |
| **Delivery % (conditioned)** — delivery spike + price up + no news, esp. ahead of bulk/block deals | Genuine accumulation vs intraday churn | days–1 week | NSE security-wise delivery, daily | **moderate** (Rajvanshi & Paul 2022) |
| **Bulk/block deals** (named counterparties) | Institutional entry/exit; front-running pattern | event ±1 week | NSE/BSE daily disclosures | moderate (above); NSE-IGIDR block-trade paper: insider block purchases positive 3-day CAR (Ranganathan, NSE-IGIDR WP 2015-16 — https://nsearchives.nseindia.com/research/content/NSE-IGIDR_CG_RPaper_2015-16_WP4.pdf) |
| **Promoter/insider buying-selling** (SEBI PIT / SAST disclosures) | Insider purchases → positive abnormal returns, sales negative; signal is in *opportunistic* (non-routine) trades | weeks–months | BSE/NSE disclosures, within 2 trading days (PIT) | **strong** globally (Cohen, Malloy & Pomorski, "Decoding Inside Information", *J. Finance* 67(3), 2012, 1009–1043: 82bp/month for opportunistic); **moderate** India (Kumar, NITK PhD thesis 2018 — https://idr.nitk.ac.in/handle/123456789/14150) |
| **Promoter pledging** (level and change) | Higher crash risk, volatility, lower future performance | months | Quarterly shareholding + SAST event disclosures | **moderate** India: Kalia, *J. Adv. Mgmt Research* 2024 (BSE 500, 2011–20) — https://ideas.repec.org/a/eme/jamrpp/jamr-01-2023-0003.html ; Chauhan, Mishra & Spahr, *Financial Management* 50(1), 2021, 261–280 |
| **AMFI monthly MF flows / scheme portfolio changes** | Aggregate: domestic flows cushion FPI selling; cross-section: retail-driven flows = "dumb money" (crowding, lower later returns) | month+ (lagged disclosure) | AMFI monthly (~10th of month), scheme portfolios monthly | strong mechanism (Frazzini-Lamont US); India: media/AMC commentary only — weak |
| **SIP flows** | Structural bid; stability of domestic demand; a *drop* in SIP net adds (stoppages up) = retail capitulation | months | AMFI monthly | **folklore/weak** as timing signal |
| **MTF outstanding** (broker margin funding) | Retail leverage build-up; crowding | weeks–months | Exchange-published MTF data (aggregate; stock-wise availability UNVERIFIED) | weak: US analogue mixed (DKP margin credit moderate; raw margin debt lags) |
| **IPO / SME froth** (subscription multiples, listing gains, issuance volume) | Late-cycle sentiment; SME applicant-to-allottee ratio 245× in FY24 vs 4× FY22 | months | NSE/BSE/SEBI; Chittorgarh-type aggregators | strong mechanism (Baker-Wurgler); India data point: SEBI SME consultation paper, 19 Nov 2024; SEBI study: 54% of IPO shares (ex-anchor) sold within a week (2 Sep 2024) |
| **Retail F&O participation** (unique traders, option premium turnover share) | Speculative excess; regulator-driven regime breaks (SEBI F&O curbs) | months | SEBI/NSE reports, NSE monthly stats | weak as timing signal; SEBI study confirms retail is the loser cohort |
| **INR / crude / US 10y / DXY** | FPI flows to India driven primarily by global risk, liquidity, rates; DXY, oil and tight US conditions pressured INR/FPI in 2022 | weeks–months | Real-time | moderate (RBI: Acharya, Salvi & Kumar WP on global liquidity & FPI; RBI Bulletin on FX reserves — https://rbi.org.in/Scripts/PublicationsView.aspx?id=21791). RBI paper itself notes mixed support for rates driving surges |
| **Earnings-revision breadth** (sector-level up/down revisions) | Fundamental momentum ahead of price | 1–6 months | Paid (Bloomberg/LSEG/ACE Equity/Trendlyne consensus) — **data cost is the moat** | **strong** (Chan-Jegadeesh-Lakonishok 1996) |
| **GST / PMI / bank credit growth nowcasts** | Sector demand (GST collections, PMI new orders, RBI sectoral credit) | 1–3 months for sector fundamentals | GST monthly (PIB), PMI monthly, RBI sectoral deployment monthly (lag ~1 month) | weak-moderate as equity signal (no India equity-return study found; UNVERIFIED) |

> **Platform capability:** India positioning ingest (participant OI, FPI cash/deriv, delivery, bulk/block, PIT/SAST, pledges, AMFI, MTF, IPO stats, VIX + option chain) with point-in-time storage (as-published timestamps, no look-ahead); derived features: FII L/S percentile, cash-vs-deriv divergence, skew & PCP deviation, conditioned-delivery, opportunistic-insider classifier (Cohen-Malloy-Pomorski routine filter), pledge-change flag; every feature shipped with its own India backtest card.

---

## 5. Position management

| Topic | Evidence | Source |
|---|---|---|
| **Stop-losses** | If returns are random walk, stops only cut expected return. They help when returns have momentum or regime-switching; certain stop rules added 50–100 bp/month during stop-out periods (US equities 1950–2004, WP version) | Kaminski & Lo, "When do stop-loss rules stop losses?", *J. Financial Markets* 18, 2014, 234–254, doi:10.1016/j.finmar.2013.07.001 |
| Stops on momentum | 10% stop cut worst EW momentum month from −49.8% to −11.3% (1926–2011); gross of costs, critics haircut 300–600 bp | Han, Zhou & Zhu, "Taming Momentum Crashes: A Simple Stop-Loss Strategy", SSRN WP 2014 (journal version UNVERIFIED) |
| **Volatility targeting** | Reduces extreme returns and vol-of-vol across 60+ assets; US equity Sharpe 0.40 → 0.48–0.51; no Sharpe gain for non-risk assets | Harvey et al. (Man AHL), "The Impact of Volatility Targeting", *JPM* 45(1), 2018, 14–33, doi:10.3905/jpm.2018.45.1.014 |
| Volatility-managed factors | Scaling by inverse prior-month variance → higher Sharpe, large alphas, less risk in recessions | Moreira & Muir, "Volatility-Managed Portfolios", *J. Finance* 72(4), 2017, 1611–1644, doi:10.1111/jofi.12513 (later multifactor caveats: DeMiguel, Martín-Utrera & Uppal, *J. Finance* 2024) |
| **Adding to winners vs averaging down** | Investors sell winners too early and hold losers (disposition effect); hurts after-tax and subsequent performance. Momentum + 52w-high evidence supports adding to strength; no academic support for averaging down absent fundamental re-underwriting | Odean, "Are Investors Reluctant to Realize Their Losses?", *J. Finance* 53(5), 1998, 1775–1798 ; Shefrin & Statman 1985 (cited therein); George-Hwang 2004. SEBI IPO study also found a strong disposition effect among Indian IPO investors. Direct "pyramiding" studies: none found — **UNVERIFIED** |
| **Rebalancing frequency** | No optimal frequency/threshold; monthly/quarterly/annual similar risk-adjusted returns, costs rise with frequency; threshold (e.g. 5pp) or hybrid (check periodically, trade only past threshold) is efficient; use cash flows to rebalance | Vanguard, "Best practices for portfolio rebalancing" (Jaconetti, Kinniry, Zilbering), 2010 / updated 2015 — copy: https://www.aaii.com/files/journal/pdf/best-practices-for-portfolio-rebalancing.pdf (official Vanguard URL not confirmed) |
| **Position sizing — Kelly** | Kelly maximizes long-run growth but bets are large and short-run risky; fractional Kelly trades growth for safety | MacLean, Thorp & Ziemba, *Quantitative Finance* 10(7), 2010, doi:10.1080/14697688.2010.506108 |
| **Risk parity** | Equal risk contribution + leverage beat market ~4%/yr US 1926–2010 (AQR authors, conflict); result sensitive to backtest period per critics | Asness, Frazzini & Pedersen, *FAJ* 68(1), 2012, 47–59 ; Anderson, Bianchi & Goldberg, *FAJ* 2012 rebuttal |
| Momentum crash control | Scale momentum by forecast mean/variance; avoid full exposure after market crash + high vol | Daniel & Moskowitz 2016 |

**"Risk cushion" per holding (proposed definition — a synthesis, not a published metric):**

```
cushion_vol      = (price − invalidation_level) / ATR_20          # in ATRs; invalidation = structural low / trend line / 10m SMA
cushion_dd       = (price − invalidation_level) / (σ_daily · √h)  # horizon-scaled
dd_at_risk       = position_weight × (price − invalidation)/price # portfolio loss if invalidated
crash_flag       = industry run-up percentile + vol + turnover + issuance (Greenwood-Shleifer-You)
valuation_margin = (fair_value_range_low − price)/price            # MoS; only for investing sleeve
earnings_cushion = (consensus EPS − EPS implied by current P/E at sector-floor multiple)/consensus EPS
                 + revision trend (Chan-Jegadeesh-Lakonishok)
positioning_risk = pledge %, pledge Δ, MTF crowding, skew steepness, FII stock-futures short build-up
```

Action rules derived from evidence (recommended defaults, to be backtested on NSE):
- **Add** only when trend intact + revision breadth ≥ neutral + cushion_vol ≥ 2 ATR after the add; size via vol-target (risk per position = constant ₹ at invalidation), capped at fractional Kelly ≤ 0.25–0.5.
- **Partial profit booking** = vol-scaled trailing (chandelier-style ATR multiple) or when crash_flag fires (run-up >~100% + vol/turnover/issuance up) — book 1/3–1/2, trail the rest. Do not book merely because "it's up" (disposition effect).
- **Never average down** in the trading sleeve; in investing sleeve only after documented re-underwrite (thesis + earnings cushion still positive).
- **Rebalance** = threshold-on-calendar hybrid (monthly check, trade if drift > band); band widens in high-vol regime to cut churn.
- **Portfolio vol target** with regime-dependent cap; momentum sleeve scaled down in "panic" state (Daniel-Moskowitz).

> **Platform capability:** Per-holding cushion card (ATR/vol distance to invalidation, DaR, crash flag, valuation & earnings cushion, positioning risk); sizing engine (vol-target + fractional-Kelly cap + risk-parity option); trailing-stop and scale-out simulator; threshold/hybrid rebalancer with cost model; disposition-effect nudges.

---

## 6. Trading vs investing horizons

| Horizon | Dominant effect | Source |
|---|---|---|
| 1 week–1 month | **Reversal** (losers outperform winners); concentrated in low-turnover stocks, high-turnover stocks show short-term momentum | Jegadeesh 1990 (*J. Finance* 45(3), "Evidence of Predictable Behavior of Security Returns" — venue from memory, UNVERIFIED this session); Lehmann 1990; Medhat & Schmeling 2021 (cited secondarily) |
| 1 day–6 months | Options-informed flow (put/call, skew, PCP) | Pan-Poteshman 2006; Cremers-Weinbaum 2010; Xing-Zhang-Zhao 2010 |
| 3–12 months | **Momentum** (price, industry, earnings/revision, 52w-high) | Jegadeesh & Titman 1993 (*J. Finance* 48(1)); Moskowitz-Grinblatt 1999; Chan-Jegadeesh-Lakonishok 1996; George-Hwang 2004 |
| 1–12 months (macro) | Trend (TSMOM) for index/sector exposure | Moskowitz-Ooi-Pedersen 2012; Hurst-Ooi-Pedersen 2017 |
| 3–5 years | **Long-horizon reversal / value**; high-volume momentum reverses faster | Lee-Swaminathan 2000; Asness-Moskowitz-Pedersen 2013 |
| Sentiment-sensitive names | Small/young/unprofitable stocks mean-revert after high sentiment | Baker-Wurgler 2006 |

Value and momentum are negatively correlated (Asness-Moskowitz-Pedersen 2013), so one blended score hides opposing bets. Platform must keep **separate sleeves** with separate signals, sizing, stops and P&L attribution: (a) tactical/trading (days–weeks: options/positioning/reversal, tight vol-scaled stops), (b) swing/momentum (1–12m: RS + revisions + trend, ATR trailing), (c) investing (1–5y: quality/value + earnings cushion, thesis-based invalidation, rebalancing bands). A holding has one declared sleeve; signals from other horizons are shown as context only. Retail white-label default = investing + momentum sleeves; tactical sleeve gated (SEBI study: 91% of individual F&O traders lost money in FY24).

> **Platform capability:** Horizon-tagged signal registry; sleeve-scoped portfolios with declared intent per holding; horizon-mismatch warnings ("trading signal on investing holding"); retail gating of short-horizon tools.

---

## (a) Hidden triggers ranked — early sector rotation / early bear detection, India

| # | Signal | Use | Evidence | Lead time | India data availability |
|---|---|---|---|---|---|
| 1 | Earnings-revision breadth (sector & stock) | rotation | **strong** | 1–6 m | Paid consensus feeds; costly, point-in-time history scarce |
| 2 | Trend state + realized/implied vol regime (TSMOM, 10m SMA, vol scaling) | bear | **strong** | weeks (reactive, but robust) | Free (NSE prices, India VIX) |
| 3 | Industry relative strength / 52w-high proximity (skip-month) | rotation | **strong** | 1–3 m continuation | Free (NSE sector & stock prices) |
| 4 | Industry run-up crash flag (run-up + vol + turnover + issuance) | bear / profit-booking | **strong** | months | Free (prices, volumes, NSE/SEBI issuance) |
| 5 | Option skew & put-call parity deviation (stock & index) | bear / stock-level | **strong US, unvalidated India** | days–6 m | NSE option chain EOD free; intraday paid; liquid only for F&O stocks (~200) |
| 6 | Opportunistic insider/promoter buying (PIT, routine-filtered) | stock leaders / bottoms | **strong US, moderate India** | weeks–months | Free, exchange disclosures within 2 trading days |
| 7 | Global risk: credit spreads / US yields / DXY / crude → FPI flow pressure | bear | **moderate-strong** (RBI + US credit lit) | weeks–months | Free, real-time |
| 8 | Average correlation spike + dispersion state | bear / factor conditioning | **moderate-strong** | ~1 quarter | Derived from free price data |
| 9 | Promoter pledge level & change | stock crash risk | **moderate** (India peer-reviewed) | months | Free, quarterly + event |
| 10 | Conditioned delivery % + bulk/block deal flow | accumulation / distribution | **moderate** (India) | days–1 week | Free, daily |
| 11 | FII index-futures L/S ratio extremes + cash-vs-derivative divergence | bear / short-covering | **weak** (broker studies only) | days–weeks | Free, NSE participant OI daily |
| 12 | Froth composite: SME/main-board IPO subscription & listing gains, MTF growth, retail F&O share, MF flow surges | late-cycle / bear | **moderate mechanism (Baker-Wurgler, Frazzini-Lamont), weak India timing** | months | Mostly free monthly (AMFI, SEBI, exchanges); MTF stock-level UNVERIFIED |

Folklore (show as context, never as a scored signal until India backtest passes): breadth thrusts, % above 200DMA, new-high/new-low, OI build-up labels, business-cycle sector clock, PCR as a standalone, LPPLS crash dates.

## (b) Capability checklist (deduplicated)

1. **Point-in-time data lake** for India positioning/fundamentals (as-published timestamps, revisions kept) — prerequisite for every backtest; McLean-Pontiff, Harvey-Liu-Zhu.
2. **Signal admission gate**: India OOS backtest, post-cost, t>3, ~50% literature haircut, per-signal evidence card (source, grade, lead time) — Harvey-Liu-Zhu 2016; McLean-Pontiff 2016.
3. **Regime service**: 2–3 state HMM on vol/trend/credit + BOCPD break alerts; regime-conditioned weights with shrinkage and turnover penalty — Hamilton 1989; Ang-Timmermann 2012; Adams-MacKay 2007; Nystrup et al. 2017/2018.
4. **Signal decay monitor**: rolling IC/hit-rate vs backtest band, auto-demote, scheduled retrain, simple drift detectors — Lo 2004; Suárez-Cetrulo et al. 2023; Gu-Kelly-Xiu 2020.
5. **Rotation engine**: industry RS (3/6/12m, skip-month), 52w-high proximity, revision breadth, leading-industry cross-signals, dispersion — Moskowitz-Grinblatt 1999; Hong-Torous-Valkanov 2007; Chan-Jegadeesh-Lakonishok 1996; George-Hwang 2004; Stivers-Sun 2010. Explicitly no cycle-clock signal — Stangl et al. 2009/2023.
6. **Leader finder**: within-sector rank on RS + revisions + 52w-high + volume-conditioned momentum stage (low-volume winners preferred) + insider buying — Lee-Swaminathan 2000; Cohen-Malloy-Pomorski 2012.
7. **Bear-risk composite**: trend, vol, VRP, avg correlation, credit/curve, global (DXY/US10y/crude) — MOP 2012; HOP 2017; Bollerslev-Tauchen-Zhou 2009; Pollet-Wilson 2010; Gilchrist-Zakrajšek 2012; Estrella-Mishkin 1998; RBI.
8. **Crash-probability flag** on industries/stocks after run-ups — Greenwood-Shleifer-You 2019.
9. **Options intelligence**: skew, PCP deviation, India VIX term structure built from chain, FII participant OI analytics — Xing-Zhang-Zhao 2010; Cremers-Weinbaum 2010; Pan-Poteshman 2006; Thenmozhi-Chandra NSE WP.
10. **Ownership/insider module**: PIT/SAST parsing, routine-vs-opportunistic classifier, pledge tracker, bulk/block deal + conditioned-delivery detector — Cohen-Malloy-Pomorski 2012; Kalia 2024; Chauhan-Mishra-Spahr 2021; Rajvanshi-Paul 2022.
11. **Froth/sentiment gauge**: IPO/SME stats, MF/SIP flows, MTF, retail F&O share — Baker-Wurgler 2006; Frazzini-Lamont 2008; SEBI 2024 studies; DKP margin credit.
12. **Holding cushion card**: ATR/vol distance to invalidation, DaR, valuation & earnings cushion, positioning risk — synthesis of Kaminski-Lo 2014, Harvey et al. 2018, Chan-Jegadeesh-Lakonishok 1996.
13. **Sizing & risk engine**: vol targeting, fractional-Kelly cap, risk-parity option, momentum crash scaling — Moreira-Muir 2017; Harvey et al. 2018; MacLean-Thorp-Ziemba 2010; Asness-Frazzini-Pedersen 2012; Daniel-Moskowitz 2016.
14. **Exit/scale-out simulator**: vol-scaled trailing stops, partial booking rules, cost-aware — Kaminski-Lo 2014; Han-Zhou-Zhu 2014.
15. **Rebalancer**: threshold/hybrid bands, regime-widened in high vol, cash-flow-first — Vanguard 2010/2015.
16. **Horizon sleeves**: declared intent per holding, horizon-tagged signals, mismatch warnings, retail gating of tactical tools — Jegadeesh-Titman 1993; Lee-Swaminathan 2000; Asness-Moskowitz-Pedersen 2013; SEBI F&O study 2024.
17. **Behavioural guardrails**: disposition-effect nudges, no-average-down in trading sleeve — Odean 1998; SEBI IPO study 2024.

## Risks and open questions

- **India evidence gap**: FII L/S, PCR, OI build-up, MTF, SIP signals have no peer-reviewed India OOS tests found. Shipping them as "signals" to retail would be marketing, not evidence. Need an internal research backlog that backtests each on 2010–2026 NSE data.
- **Regulatory regime breaks**: SEBI F&O curbs (2024–25), PIT 2015 reform (insiders shifted trading to peer firms per a 2025 *Management Science* paper — UNVERIFIED title), SME rule changes — these break historical relationships. Regime service must include known-policy-date breakpoints.
- **Data cost/licensing**: revision breadth (rank #1) requires paid consensus with point-in-time history; white-label redistribution rights are a separate cost.
- **SEBI RA/IA regulation**: "guidance on adding/booking profit" to retail clients via brokers likely falls under SEBI Research Analyst / Investment Adviser regulations — legal review before white-label. Not researched here.
- **Crowding**: once broker clients act on the same public triggers (FII L/S, delivery), the edge decays faster (McLean-Pontiff).
- Not done: full-text reads (WebFetch not used), India replication of US options/credit results, official Vanguard URL, Jegadeesh 1990 venue, Han-Zhou-Zhu journal version, MTF stock-level data availability.
