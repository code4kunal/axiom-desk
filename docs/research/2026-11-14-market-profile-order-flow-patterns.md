# Market-structure pattern catalogue (Market Profile + order flow) for an NSE auction-state engine

Access date for every URL: 2026-11-14. Research mode: web search + recall. Book chapter/page cites are recalled, not checked against a copy: all marked UNVERIFIED unless noted.

## 0. Sources and keys

| Key | Source | Status |
|---|---|---|
| MOM | Dalton, Jones, Dalton, *Mind Over Markets* (1990/1993; updated ed. Wiley 2013). Day types, open types, OTF, value migration, 80% rule lineage | Book exists (Wikipedia refs). Chapter cites UNVERIFIED |
| MIP | Dalton, Bevan Dalton, Jones, *Markets in Profile* (Wiley 2007). Balance/imbalance, look-above/below-and-fail, long-term auction framing | Exists. Chapter cites UNVERIFIED |
| CBOT1/2 | CBOT *Market Profile* manuals 1985 (115 pp) and 1991 (335 pp); Steidlmayer, *Steidlmayer on Markets* (Wiley 1989) | Listed at https://en.wikipedia.org/wiki/Market_profile. Text not accessed |
| WIKI | https://en.wikipedia.org/wiki/Market_profile: Steidlmayer 3 day types (CBOTMP1 p12), later 4 (CBOTMP2 p4,12); MOM lists 9; VA approx. 70% (~1 sd) | Fetched |
| TASC | Drinka & Ptasienski, "Understanding Market Profile" series, TASC V.7:4 pp121-123, https://store.traders.com/-v07-c04-underst-pdf.html | Title verified, body not read |
| CQG | CQG MPVA docs: VA built outward from POC to 70% of TPOs, https://help.cqg.com/cqgic/25/Documents/marketprofilevalueareasmpva.htm | Search snippet |
| NFX80 | NexusFi 80% rule concept: figure traced to *The Profile Reports* (Dalton Capital Mgmt 1987-91), statistics "imperfect", https://nexusfi.com/a/concepts/80-percent-rule | Search snippet |
| CKS | Cont, Kukanov, Stoikov, "The Price Impact of Order Book Events", J. Fin. Econometrics 12(1):47-88, 2014, arXiv:1011.6402 | Verified (bibliographic + abstract) |
| OSL | Osler, "Currency Orders and Exchange Rate Dynamics…", J. Finance 58(5):1791-1819, 2003; NY Fed SR125 | Verified (abstract) |
| CRS | Chordia, Roll, Subrahmanyam, "Order imbalance, liquidity, and market returns", JFE 2002 | UNVERIFIED (recall) |
| NSE-EXP | NSE expiry moved Thu->Tue for contracts on/after 2025-09-01 (SEBI circ. 2025-05-26; NSE circ. 103/2025); monthly = last Tuesday, https://www.5paisa.com/news/nse-marks-historic-expiry-shift-as-tuesday-becomes-new-expiry-day | Verified (secondary) |
| NSE-PRE | F&O pre-open call auction 09:00-09:15 from 2025-12-08, current-month index+stock futures (next month in last 5 days before expiry); options excluded. Primary: https://nsearchives.nseindia.com//web/mediaattachment/2025-12/FAQs_for_PreOpen_Session_in_Equity_Derivatives_FO_Segment_20251202123640.pdf | Verified (secondary; PDF not opened) |
| OF-LORE | Order-flow vendor/practitioner material (footprint, stacked imbalance, absorption). Common sources: Jigsaw, Sierra Chart, ATAS, Trader Dale, Axia Futures | Practitioner lore, no single canonical text |

Evidence grade used below: **A** = peer-reviewed quantitative evidence for the mechanism (not necessarily for the trade); **B** = published practitioner statistics with stated method; **C** = source claim with no published test (lore). Nothing in Market Profile proper got above C in this search. No peer-reviewed study of VA/POC predictiveness was found.

## 1. Common primitives (engine definitions)

- Session S: 09:15-15:30 IST = 375 min. 30-min TPO periods -> 13 periods, last (P13 15:15-15:30) is a **15-min half period**. Normalise its TPO weight (x2) or merge into P12; recommend: keep separate, flag `half=true`, exclude from day-type thresholds.
- IB = P1+P2 (09:15-10:15). IBR = IBH-IBL.
- Tick bucket: TPO row size = k x tick (NIFTY fut tick 0.05 is far too fine; recommend row = max(tick, ATR20_daily/150) rounded to 0.05/5). Row size changes every VA number; pin it per instrument per day.
- POC = row with max TPO count (tie: closest to range mid). vPOC = row with max volume.
- VA: start at POC, add the larger of the next two rows above vs below (Dalton/Jones two-row method, UNVERIFIED as exact canonical form) until >=70% of TPOs (CQG). Compute both TPO-VA and volume-VA; store which.
- Single print: row with TPO count 1 inside a contiguous run (not at an extreme of a period's own range only).
- Tail (excess): >=2 single-print rows at session extreme, from one period. (MOM; 2-row min is common convention, UNVERIFIED as Dalton's number.)
- Poor high/low: >=2 periods share the extreme row (flat top/bottom, no tail). (MOM concept; rule is convention.)
- HVN/LVN: on volume-at-price smoothed (e.g., Gaussian sigma=2 rows) find local maxima/minima; LVN if vol < 0.3 x vPOC vol and local min; HVN if local max > 0.6 x vPOC vol. Thresholds = engineer convention (C).
- Delta per row/bar = aggressor buy vol - aggressor sell vol. **NSE caveat:** public feeds give LTP/LTQ + top-5 depth, not aggressor flag; aggressor must be inferred (tick rule / quote rule vs best bid/ask snapshot). Delta is therefore **estimated**; tag every order-flow pattern `delta_inferred=true`.
- Spot NIFTY/BANKNIFTY have no traded volume. Build TPO on spot or near-month future; volume/delta only from futures. Futures basis shifts at roll: build composites on a **basis-adjusted** continuous future or on spot for TPO, never splice raw contracts.

## 2. Day types (MOM; CBOT1/2; WIKI). All labels are final only at session close -> look-ahead risk.

| Pattern | Definition (source claim) | Detection rule (end of day unless noted) | TF | Implies (source claim) | Invalidates | HVN/LVN + OF confirm | Grade |
|---|---|---|---|---|---|---|---|
| Non-trend | Small IB that contains (almost) whole day; no OTF participation | range <= 1.15 x IBR, IBR < 0.6 x avg IBR20 | Day | No conviction; often precedes breakout/event (MOM) | Later RE > 15% IBR | Volume concentrated one HVN; delta near 0 | C |
| Normal | Wide IB set early by OTF, holds all day | no RE or RE <= 15% IBR; IBR >= ~80% day range (WIKI via TASC) | Day | Range set by large OTF entry early; rare in modern markets (MOM) | RE > 15% | Single vPOC mid IB | C |
| Normal variation | Moderate IB, RE in one direction up to ~2x IB | one-sided RE, range in (1.15, 2.0] x IBR | Day | OTF moved value moderately one way | Two-sided RE (->neutral) | RE leg on +delta (up) with LVN between IB and RE | C |
| Trend | Narrow IB, persistent one-sided RE, close near extreme | IBR < 25% day range (WIKI); one-sided RE; close in outer 10% of range; >=3 periods making new extreme; POC migrates >=2 times | Day | OTF in control all day; counter-trading dangerous; next day often continuation open (MOM) | Close back inside IB; tail at trend extreme | Thin profile (many LVN/single prints), cumulative delta monotone; absorption absent at extreme | C |
| Double distribution | Two separate value areas joined by single prints | 2 TPO-count modes separated by >=3 single-print rows; each mode >= 25% TPOs | Day | Late OTF entry; single-print zone = support/resistance next day (MOM) | Single prints filled within session | Single-print zone = LVN; second distribution builds on delta in break direction | C |
| Neutral | RE on both sides of IB, close near centre | RE above and below; close in middle 40% of range | Day | Both OTF sides active, balance; next day directional clue weak (MOM) | n/a | Two-sided absorption at extremes | C |
| Neutral extreme | Both-side RE, close at one extreme | both RE; close in outer 15% of range | Day | Side closing at extreme won; follow-through next open (MOM) | Next open back in middle third | Late-day delta aligned with close side | C |
| P profile | Long lower single-print/thin part, fat upper distribution | TPO-mass skew: >=60% TPOs in upper 40% of range; lower part single prints | Day | Short-covering (not new buying) -> weak follow-through (MOM/MIP common reading; UNVERIFIED wording) | Next day value higher and accepted | Rally leg low volume, then HVN at top; delta positive but fading | C |
| b profile | Mirror: long liquidation into fat lower distribution | >=60% TPOs in lower 40% | Day | Long liquidation, not fresh selling (same) | Next day value lower and accepted | Mirror | C |

Pitfall: the 9-type taxonomy (MOM) vs 3/4 types (CBOT) differ; thresholds (25%, 80%, 2x) are secondary-source numbers, not from the manuals read directly. Engine should emit a **probability over types** updated per period, not a hard label before close.

## 3. Open types (MOM). Evaluated on P1 (first 30 min) vs open; labelled by end of P1/P2.

| Pattern | Definition | Rule (o=open, P1 range) | Implies (source claim) | Invalidated by | Confirm | Grade |
|---|---|---|---|---|---|---|
| Open Drive (OD) | Aggressive move away from open, open never revisited | open within 10% of P1 extreme; P1 range >= 1.0 x avg P1 range; P2 does not trade back through o | Highest-conviction OTF; trend/NV day odds up (MOM) | Trade back through o in P2/P3 | Price leaves through LVN; delta strongly one-sided, no absorption at open | C |
| Open Test Drive (OTD) | Probe against intended direction to test a reference (prior H/L, VA edge), fail, then drive | P1 first moves >= 0.25 x P1range against, touches a reference within 1 row, then closes beyond o in other direction; o not revisited after | Confident after verifying no business on other side (MOM) | Return to test level | Absorption/exhaustion at test level; delta flip | C |
| Open Rejection Reverse (ORR) | Moves one way, meets opposite activity, reverses through open | P1 travels one way, then trades through o by >= 0.25 x P1range and sets other extreme | Less conviction; often rotational day (MOM) | Re-break of first extreme | Responsive absorption at first extreme, delta divergence | C |
| Open Auction in range (OA-in) | Rotates around open inside prior range | o inside prior day range; P1 trades both sides of o; |close_P1 - o| < 0.25 x P1range | Balance; lowest conviction; responsive trading (MOM) | IB break with acceptance (2 periods) | Volume builds HVN at open | C |
| Open Auction out of range (OA-out) | Opens outside prior range and auctions around | o outside prior H/L, same rotation test | Potential imbalance; watch whether market returns into prior range (MOM) | Acceptance back in prior range | Delta at return to prior range edge | C |

## 4. Open location vs prior value/range (MOM)

| Location | Rule | Source claim | Grade |
|---|---|---|---|
| In value | o in prior VA | Balance likely; responsive activity; 80% rule n/a (NFX80) | C |
| Out of value, in range | VAL > o >= prior L or VAH < o <= prior H | Moderate imbalance; acceptance test of prior VA edge | C |
| Out of range (gap) | o > prior H or < prior L | Strongest imbalance; gap fill vs go evaluated by first hour acceptance | C |
Combine: open location x open type gives a 5x3 matrix; engine stores it as `open_context`. NSE gaps are common because overnight global moves (SGX/GIFT Nifty) price in pre-open; since 2025-12-08 futures open from a call auction (NSE-PRE) so "o" for futures = auction price; for options there is no pre-open.

## 5. Core setups

| # | Pattern | Source | Definition | Detection rule | TF | Implies (claim) | Invalidates | HVN/LVN + OF | Grade |
|---|---|---|---|---|---|---|---|---|---|
| 5.1 | 80% rule (VA re-entry) | MOM lineage; NFX80; LuxAlgo/metrotrade write-ups | Open outside prior VA, re-enter and be accepted -> high odds of traversing to other VA edge | o outside prior VA; then 2 consecutive 30-min TPO periods with TPO inside prior VA (common modern variant; 1-period variants exist) | Day vs prior day VA; also composite VA | "80%" traverse (claim). NFX80 itself calls stats imperfect. No independent test found | Acceptance back outside entry edge (2 periods) | Path through VA: if prior-day LVN inside VA, faster; prior vPOC = midway magnet. Re-entry on delta in re-entry direction | C (the 80% figure is lore) |
| 5.2 | IB extension / range extension | CBOT2, MOM | Price beyond IB = OTF activity | RE up if high > IBH by >= 1 row after P2; record RE size/IBR, time of RE | Day | OTF initiating; large RE early -> trend/NV (claim) | Return inside IB and close inside | RE through LVN + initiative delta = valid; RE into HVN with absorption = likely fail | C |
| 5.3 | IB size regime | MOM | Narrow IB -> range extension likely; wide IB -> range held | IBR / median IBR20: <0.7 narrow, >1.3 wide | Day | (claim) | n/a | n/a | C (testable; compute own stats, Section 8) |
| 5.4 | Single prints | MOM | Fast one-way OTF move leaving no overlap | Section 1 rule; mid-profile, >=2 rows | Day; persist until filled | Act as support/resistance on retest (claim) | Revisited and filled (>=2 TPOs across) | = LVN; fill on low volume = weak, on HVN build = acceptance | C |
| 5.5 | Excess / tail | MOM, CBOT | Aggressive opposite response ends an auction | tail >= 2 rows at extreme | Day/wk/month extreme | Auction completed; extreme unlikely revisited soon (claim) | Price trades through tail | Tail on high volume + absorption + delta divergence = strong | C |
| 5.6 | Poor high/low (no excess) | MOM, MIP | Unfinished auction | >=2 TPO periods at exact extreme, tail < 1 row | Day, also weekly/monthly | Likely revisited ("repaired") (claim) | Revisited (then retire) | Low-delta flat top = weak; strong if extreme at HVN without rejection volume | C |
| 5.7 | Balance area | MIP | Multi-day overlapping value, rotational | >= 3 consecutive days VA overlap > 50% with the composite; composite range <= 1.5 x ADR | Multi-day | Balance precedes imbalance; trade edges responsively (claim) | Accepted break (5.8) | Composite HVN centre; edges at LVN | C |
| 5.8 | Balance breakout + acceptance | MIP | Leave balance and build value outside | close outside balance edge AND next session VA >= 50% outside | Multi-day | New directional auction to next reference (claim) | Return inside balance and close in | Break leaves through LVN with initiative delta, no absorption | C |
| 5.9 | Look above and fail (LAAF) / look below and fail (LBAF) | MIP | Probe beyond balance edge finds no follow-through, returns | trade > balance high by >= 1 row; within N=2 periods (intraday) or next session (multi-day) close back inside; no value built outside (<20% TPOs outside) | Multi-day edge, daily edge | Move to opposite side of balance (claim) | Re-break with acceptance | Absorption above edge, positive delta not lifting price (delta divergence), trapped buyers (5.20) | C |
| 5.10 | Value migration | MOM | Relationship of today's VA to prior: higher / overlapping-higher / overlapping / overlapping-lower / lower / inside / outside | compare VAH/VAL/POC vs prior; 7-state enum | Day; weekly | Higher/lower = OTF directional; overlapping = balance (claim) | n/a (descriptive) | vPOC migration agreeing with TPO-POC adds weight | C (descriptive, low risk) |
| 5.11 | Composite profile / nested value | MIP | Merge N sessions into one profile; daily value nested inside larger value | composite over rolling window or anchored (balance start, expiry start); flag `daily_VA within composite_VA` | Multi-day/weekly/monthly/expiry | Daily auctions inside composite value = longer TF balance; daily value outside composite = longer TF imbalance (claim) | Window choice changes answer -> store window | Composite HVN/LVN map is the main HVN/LVN source | C |
| 5.12 | Naked / virgin POC | practitioner (attributed to Dalton by some; UNVERIFIED) | Prior POC never retraded | prior POC not touched by any later session's range | Day POC, carried across days | Magnet; often retested (claim). One unverified secondary figure: ~75% within 30 sessions on ES (portfoliowebsite research summary, UNVERIFIED) | Touched -> retire | Higher weight if POC sits at composite HVN; touch on low volume = pass-through | C |
| 5.13 | HVN acceptance / magnet | vol-profile practice | High-volume node = prior acceptance; price slows, rotates | Section 1 | Composite | Price tends to rotate inside, slow down (claim) | Fast pass-through on high delta | Mechanism partly A: order clustering at levels documented (OSL, FX round numbers) | C (mechanism partial A) |
| 5.14 | LVN fast travel / rejection | vol-profile practice | Low-volume node = prior rejection; price travels fast through, or rejects at edge | Section 1 | Composite | Fast move across; LVN edges = reaction levels (claim) | Price builds volume (becomes HVN) | Stop clustering beyond levels -> fast moves (OSL, partial A for FX) | C |
| 5.15 | TPO count imbalance | MOM (UNVERIFIED cite) | Compare TPOs above vs below POC | count_above - count_below excluding POC row and single-print tails | Day, intraday | More TPOs below POC = buying-side pressure? (convention varies by author) UNVERIFIED direction | n/a | Combine with delta sign | C |
| 5.16 | Rotation factor | MOM (UNVERIFIED cite) | Per period: +1 higher high, +1 higher low, -1 lower high, -1 lower low; sum through day | sum over periods 2..n | Day, intraday | Sign = which side controls rotations (claim) | n/a | Cum delta should agree; disagreement = divergence | C |
| 5.17 | OTF control | MOM | Who is moving price: other-timeframe buyers/sellers vs day timeframe | OTF buyer control if RE up, value higher, buying tail at low, rot. factor > 0; mirror for sellers; else day-TF | Day; weekly | Controlling side sets direction (claim) | Opposite tail + value shift | Large block trades (if available from NSE bulk/block deals EOD) as OTF proxy | C |
| 5.18 | Inventory correction | MOM, MIP | Overnight/pre-open inventory imbalance corrected at open | NSE has no overnight session; proxy = gap vs prior close + pre-open futures auction price vs prior settle; "long inventory" if open > prior H and first 2 periods trade down >= 50% of gap | Day open | Inventory correction then resumption of direction (claim) | Correction exceeds gap fill and accepts | Delta during correction should be weak (responsive), resumption on initiative delta | C; NSE adaptation UNVERIFIED |

## 6. Order-flow patterns (OF-LORE unless noted). All need aggressor side; NSE delta is inferred.

| Pattern | Rule | Implies (claim) | Invalidates | Combine | Grade |
|---|---|---|---|---|---|
| Absorption | At a level, aggressive vol >= k x median (k=3) with price moving < 1 row over >= 2 min; passive side refreshes (depth snapshot) | Passive large player defends; reversal or stall | Level breaks by >=2 rows | Strongest at VA edge, balance edge, HVN edge, prior tail | C |
| Exhaustion | At move extreme, final bar(s) show falling aggressive vol and thin row volume at extreme | Initiative side out of fuel | New extreme on rising vol | Poor-high counterpart; pairs with LAAF | C |
| Stacked imbalances | >= 3 consecutive rows where ask vol >= 3 x diagonal bid vol (or mirror) | Initiative zone; acts as support on retest | Price trades back through whole stack | Valid only when leaving balance / through LVN | C |
| Delta divergence | New price extreme while bar/cum delta fails to make new extreme | Weakening initiative; reversal odds up | Delta confirms next bar | LAAF, P/b profiles, tails | C; mechanism (OFI drives price contemporaneously) A via CKS, predictive use C |
| Initiative vs responsive | MOM: initiative = buying above value / selling below value; responsive = buying below / selling above | Initiative outside value = OTF imbalance; responsive = balance | n/a | Tag each RE leg | C (definitional) |
| Trapped traders | Breakout bar with heavy aggressive vol in break direction, then close back inside within 1-2 bars | Trapped side covers -> fuel opposite move | Re-break | LAAF/LBAF confirmation | C |
| Order-flow imbalance (OFI) | CKS: signed changes in best bid/ask queue | Contemporaneous linear price impact, slope ~1/depth (A, US stocks) | n/a | Use as microstructure feature, not as a forecast | A (contemporaneous only) |
| Order imbalance (daily) | CRS | Imbalance relates to returns/liquidity (UNVERIFIED details) | n/a | Daily OTF proxy | A? UNVERIFIED |

## 7. Multi-timeframe clubbing conventions

| # | Convention | Practice | Notes |
|---|---|---|---|
| 1 | Fixed calendar composites: day / week / month | Most platforms, MOM-style weekly & monthly profiles | Simple; breaks balances at arbitrary boundaries |
| 2 | Rolling N-day composite (3/5/10/20) | "Three Day Balance Rule" (WIKI ref, 2007, UNVERIFIED content) | No boundary artefact; window choice arbitrary |
| 3 | Anchored/structure composite: from start of current balance (5.7) to now | MIP balance framing | Best for auction state; needs balance-start detector |
| 4 | Nested value: daily VA vs composite VA vs higher composite VA | MIP | Encodes TF agreement: all overlapping = balance; daily outside weekly outside monthly = trend |
| 5 | Event/contract cycle composite (expiry-to-expiry, roll-to-roll) | Futures/options desks; for NSE natural because positioning resets at expiry | Expiry week distorts (pinning, roll volume); NSE monthly = last Tuesday from 2025-09 (NSE-EXP) |

**Recommended NSE default (decision):** auction state per instrument = **nested triplet** {daily (13 periods, P13 half), anchored balance composite (#3, fallback rolling 5-day), expiry-cycle composite (#5, last-Tuesday to last-Tuesday)}, plus a monthly-calendar composite only for reference levels (naked POCs, tails, poor highs). Rationale: expiry cycle is where NSE F&O positioning actually resets; anchored balance avoids arbitrary week cuts. Weekly composite: drop as a state input for NIFTY since weekly Tuesday expiry already splits weeks; keep as display. Combination rule: state = `balance` if daily VA overlaps anchored VA >50% AND anchored VA within expiry-cycle VA; `imbalance_up/down` if daily value higher/lower than anchored for >=2 sessions with accepted break (5.8); `transition` otherwise. Contract roll: expiry-cycle composite on basis-adjusted continuous future; exclude expiry-day last 2 periods from VA (pinning) or flag them.

## 8. Evidence audit

(a) Published quantitative evidence vs lore
- **Quantitative, peer-reviewed (mechanism only):** order-flow imbalance -> contemporaneous price change (CKS, A); order clustering at round numbers explaining support/resistance and acceleration through levels (OSL, A, FX not equity index). Order imbalance vs returns (CRS, UNVERIFIED).
- **Practitioner statistics with some method:** none verified. 80% rule figure traced to Dalton's 1987-91 newsletter, unpublished method (NFX80). Naked POC ~75% retest (UNVERIFIED secondary).
- **Lore (C):** every day type and open type implication, IB thresholds, single prints as S/R, poor highs repair, LAAF/LBAF, P/b interpretation, rotation factor, TPO count, absorption/exhaustion/stacked imbalance/trapped traders, HVN magnet / LVN fast travel as trade signals.
- Consequence: engine must show suggestions as "source says X" + **own NSE base rates** computed walk-forward (hit rate, n, CI) per pattern before any grade above C. Suggested minimum: n >= 100 events per instrument class, out-of-sample year.

(b) Pitfalls
1. Day-type labels are subjective and only final at close; using them in a backtest at 10:15 is look-ahead. Emit provisional probabilities per period; freeze labels only at 15:30.
2. IB is known only at 10:15; RE before that does not exist. Open type known at earliest 09:45.
3. 70% VA is a convention (~1 sd analogy, WIKI); results change with 68/70/80% and with TPO vs volume VA, and with row size. Make all three parameters explicit and fixed per backtest.
4. VA algorithm variants (one-row vs two-row expansion, tie rules) give different VAH/VAL; pin one.
5. Half period P13 inflates/deflates late TPO counts; expiry-day close distorts (pinning, settlement).
6. NSE delta is inferred (no aggressor flag in common feeds); footprint patterns are noisier than in CME data. UNVERIFIED whether the desk's feed (e.g., tick-by-tick from a vendor) has trade-side.
7. Spot index has no volume; futures roll creates basis jumps in composites.
8. Pre-open auction (futures, from 2025-12-08) changes what "open" means vs pre-2025 history; backtest regime break.
9. Multiple-testing: 40+ patterns x thresholds -> spurious hits; control with holdout and FDR.
10. Survivorship in practitioner claims (books cite examples that worked).

(c) Clubbing default: Section 7.

## 9. Pattern record schema (for engine)

`{id, instrument, tf: day|anchored|expiry|month, ts_detected, ts_final|null, provisional: bool, inputs_hash, rule_version, params{row,va_pct,va_mode}, levels[], source_key, grade: A|B|C, own_base_rate{n,hit,ci}|null, invalidation{level|condition}, confirmations{hvn_lvn, delta_inferred, absorption}}`
