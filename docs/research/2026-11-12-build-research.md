# Build research for the Axiom Desk plan

Date: 2026-11-12. This note backs the Key Technical Decisions in `docs/plans/2026-11-12-1110-feat-axiom-desk-platform-plan.md`. Most web findings come from search-result extracts of primary documents because a local hook blocked full page fetches. Claims not confirmed against a primary page carry UNVERIFIED.

## Market data licensing

NSE Data & Analytics publishes three separate tariffs, effective 1 Apr 2025. Real-time display goes through vendors. Non-display use (algorithms, analytics, anything derived from the feed) is licensed and paid directly to NSE D&A, even when the data arrives through a vendor. Analytical products include a real-time Greeks feed. The March 2026 pricing file suggests a non-display real-time fee of about INR 12.25 lakh a year for cash-market level 1 (UNVERIFIED: column layout read from an extract).

Consequence for Axiom: computing the surface, Greeks and screens is non-display use. That needs its own NSE licence per segment, on top of the vendor contract.

Delayed and end-of-day data needs written NSE consent before it is used for anything other than display.

Broker APIs are not usable as a data source. Zerodha states that Kite Connect data cannot be shown on other platforms. Other brokers are assumed to have similar terms (UNVERIFIED).

SEBI's circular of 24 May 2024 bars exchanges and registered intermediaries from sharing real-time prices with third parties, except for education. A revision dated 8 May 2026 takes effect on 1 Jul 2026 and adds a 30-day lag for educational use (UNVERIFIED: secondary sources only). A broker licensing Axiom cannot simply pass its own exchange feed to Axiom.

Vendors:
- **TrueData** streams live option chains and Greeks over WebSocket. Its historical API returns 1-minute, 5-minute and end-of-day bars, with no documented historical option-chain snapshot or tick endpoint.
- **Global Datafeeds** streams NSE and NFO tick by tick. Its historical depth is unconfirmed.
- **No feed found carries trade aggressor side.** Direction has to be inferred from trades against captured quotes.
- **NSE's tick-by-tick multicast** carries order and trade messages, but it is a colocation feed for members.
- **AMFI NAVs** are public, and their reuse terms are unconfirmed.
- **Fundamentals vendors** (CMOTS, Ace Equity, Capitaline) sell by contract only.

## Charting

- **TradingView Lightweight Charts:** Apache-2.0 with a mandatory attribution notice. Version 5 has panes and a plugin API but no drawing tools.
- **TradingView Advanced Charts:** proprietary. It is free only on public pages that are not behind a paywall. A private desk tool and a paid broker white-label both need a commercial licence, reported at about USD 144k a year (UNVERIFIED). Its indicators run in the browser, where the agent cannot reach them.
- **SciChart.js:** WebGL and WASM, with financial drawing tools since version 5.2 and a perpetual per-developer licence. Performance figures are vendor-published only.

## Running desk Python safely

Python cannot sandbox itself; libraries like RestrictedPython have been bypassed. Firecracker microVMs give a hardware-virtualisation boundary and are what AWS Lambda and Vercel Sandbox use. gVisor sits in the middle, and nsjail shares the host kernel. QuantConnect does not publish how it isolates user code. Managed sandboxes (E2B, Modal, Vercel) have unconfirmed India residency, so self-hosting in an Indian region is the safe default.

## Time-series storage

No published sizing exists at NSE scale. One forum figure puts a single Bank Nifty ATM strike on expiry day at 4 to 5 crore ticks, about 2 GB (UNVERIFIED). Full-universe raw ticks therefore run to terabytes a month, so chain snapshots and raw ticks should be stored separately. ClickHouse has ASOF joins and the largest install base. QuestDB claims faster ingest and supports ASOF joins with tolerance. TimescaleDB has no temporal join. Every published benchmark is vendor-run, so the choice needs a benchmark on our own schema.

## SEBI rules that touch the build

- **Retail algo framework:** SEBI circular of 4 Feb 2025 plus NSE implementation standards and FAQ of 3 Nov 2025.
  - Platforms that place orders through broker APIs must be empanelled with the exchange, and each strategy needs an exchange algo ID.
  - No source addresses a draft that a human confirms. An order the trader places in the broker's own order window is plausibly not an API order. An order Axiom sends through the API after a click likely is one (UNVERIFIED, needs legal review).
- **Cybersecurity framework (Aug 2024):** the regulated entity stays accountable for its vendors, needs back-to-back contracts and software bills of materials, and must use MeitY-empanelled cloud providers. The framework's own localisation clauses are suspended, but SEBI's 2023 cloud framework still requires a broker's data to be stored and processed in India.
- **Research analyst amendments (16 Dec 2024):** research now includes price targets, stop-losses, model portfolios and trading calls. Setups shown to retail clients could be treated as research, which R60 and R62 already route through the broker's RA team.

## Agent parity findings

- **Structural parity:** screen-agent parity (R4) holds only if both run off one capability registry, one engine API and one result envelope.
- **Numbers in the engine:** any judgment that yields a number, a probability or a hedge choice belongs in the engine, because the screen needs the same output.
- **Runs, not recomputes:** live-moving answers (regime, Radar, Command Center) should be published runs with ids. Then the agent and the screen agreeing is an identity check.
- **Drafts only:** the agent should be its own principal, allowed to create, revise and discard drafts and nothing more.
- **Model provider as a channel:** anything sent to the language model leaves our licence boundary, so the agent should receive computed results, not raw licensed data.

## Flow gaps found in the spec

- **No V1 order destination:** the confirm boundary had nowhere to land in V1, and no fill source existed for journals, exposure or the Edge Ledger.
- **No staleness model:** nothing said what screens, triggers, setups, drafts or the agent do when a feed goes stale, or when a surface fit fails.
- **Drafts needed rules:** they had no expiry or price band, and a multi-leg ticket confirmed leg by leg could leave a naked position.
- **Two separate setup states:** the state of each occurrence and the calibration status of the setup family are independent, and demotion must reach every watchlist, rank, trigger and draft that cites a family.
- **Ledger bias:** if the Edge Ledger scores only trades the desk took, desk selection decides what gets cut.
- **No book or role model:** the desk had no books and no roles inside it, so nobody owned confirming or signing off.

## Sources

- https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Non_Display_Policy.pdf
- https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Analytical_Products_Tariff_01042025_.pdf
- https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Real_Time_Tariff_Domestic_01042025_.pdf
- https://support.zerodha.com/category/trading-and-markets/kite-api/articles/can-i-use-historical-and-live-data-taken-from-kite-connect-api-on-other-platforms
- https://nsdl.co.in/downloadables/pdf/2024-0067-Policy-SEBI_Circular_on_Norms_for_sharing_of_real_time_price_data_to_third_parties.pdf
- https://www.truedata.in/market-data-apis
- https://www.tradingview.com/charting-library-docs/latest/introduction/
- https://unpkg.com/lightweight-charts@5.0.7/README.md
- https://www.scichart.com/scichart-pricing-licensing-guide/
- https://fly.io/learn/firecracker-vs-gvisor/
- https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail_Algo_03112025_NSE.pdf
- https://www.taxmann.com/post/blog/sebi-introduces-framework-for-adoption-of-cloud-services-by-regulated-entities/
- https://www.scconline.com/blog/post/2024/12/19/sebi-research-analyst-third-amendment-regulations-2024/
- https://algotest.in/vrp-analysis
