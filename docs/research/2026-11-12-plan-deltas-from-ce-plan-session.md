# Plan deltas for 2026-11-12-1110-feat-axiom-desk-platform-plan.md

Seven changes the current plan (checked at its 13:02 save) does not yet carry. Items already covered were dropped: algo exposure of the V1 ticket path (KTD15, G2), licensing and the NSE non-display route (KTD7, G1), model-provider payloads (KTD17, G3), licence scope on derived outputs (KTD3), the agent cannot confirm (KTD16), Firecracker isolation (KTD18), store benchmark (U7).

Regulatory and vendor facts below are UNVERIFIED: the research agents could only read search snippets, because the context-mode hook (NODE_TOO_OLD) blocked page fetches.

## D1. V2 advice boundary — product decision by the user

**Decision (user-directed, 2026-11-12):** asked "For V2 retail clients, what may the Axiom agent draft as an order?", the user chose "Only RA-authored changes" over "Personalised drafts" (needs broker SEBI Investment Adviser registration and per-draft suitability records) and "Broker decides per tenant".

- Add a Key Decision: `(session-settled: user-directed — chosen over personalised agent drafts and per-tenant choice: agent-proposed allocations for retail clients are plausibly personalised investment advice needing IA registration)`.
- Requirement change: for retail clients, the agent drafts orders only to follow or rebalance toward a basket or change the tenant's RA published, sized to the client's holdings. It explains and analyses freely but never proposes its own allocation, instrument or ticket to a retail client. Desk users (V1) keep full drafting. Governs R55, R60.
- Acceptance example: given a retail client asks the agent "what should I buy to hedge?", the agent explains hedging approaches and shows RA-published baskets or hedges available to them, and drafts nothing that no RA authored.

## D2. Idea outcome needs a target

R28 has no target, so R29's "hit" has no definition. Add an optional target zone to desk and RA ideas. An idea is "hit" when price reaches the target zone before the invalidation level and before the horizon ends. Client ideas (R63) have no target, so they resolve only as invalidated or expired. An idea edited after publishing keeps its original levels for scoring and shows the edit history.

## D3. Regime flip-flop smoothing

The calibration hysteresis in the evidence engine covers model status, not regime calls. Near a threshold, R39's regime can flip daily, and R43 would draft a contradictory rebalance each time. Add a confirmation rule: a regime change triggers rebalance drafts only after it holds for a set confirmation window. Show the shift while unconfirmed as "Transition / Uncertain", which carries no asset tilt and drafts nothing. Planning sets the window from the evidence engine's backtests.

## D4. Survivorship and as-reported data

U5 gives point-in-time instrument truth, but nothing requires the history behind screens and backtests to include delisted and merged instruments, or fundamentals as originally reported. Without both, Strategy Lab and basket backtests overstate returns and the desk's quants will not trust them. Add a requirement and a G1 vendor-contract check: history includes delisted instruments and as-reported fundamentals with report dates.

## D5. Alert state rules

Missing behaviour, with defaults:
- A trigger never fires on data past its source's freshness threshold (U6). It shows "paused: stale data" and resumes when data recovers.
- After firing, a trigger is either one-shot (default) or re-arms only after its condition resets.
- Deleting a drawing that a trigger uses disables the trigger with a visible notice, never silently.

## D6. RA-authored ideas carry registration details

SEBI's 26 Feb 2026 circular (UNVERIFIED) requires a registered name and number on social content by regulated entities. Its Aug 2024 amendments also bar regulated entities from associating with unregistered people giving advice. Extend R63: RA-authored ideas show the RA's registered name and SEBI registration number, and client ideas never show performance claims next to a named instrument.

## D7. Stack signals (all UNVERIFIED) for U14, U20 and V1.5 voice

- TradingView Advanced Charts is free only for public-facing sites and needs approval, which a direct competitor is unlikely to get. Lightweight Charts v5 (Apache-2.0, multi-pane, plugins) is a candidate base for the U14 spike, with drawings, Renko/Kagi/point-and-figure, replay and overlays built in-house.
- TA-Lib and pandas-ta-classic detect candlestick patterns only; chart patterns and hit-rate statistics are custom (U15).
- vectorbt's licence is disputed (MIT vs Apache with Commons Clause): read its LICENSE before U20 depends on it. NautilusTrader is LGPL; backtrader and zipline-reloaded show low activity.
- TimescaleDB's TSL-licensed features restrict offering it as a service; this supports the U7 benchmark of ClickHouse vs QuestDB (both Apache-2.0).
- Sarvam Saaras v3 covers 22 Indian languages plus English with code-mixing: a candidate for R57's V1.5 voice.

## Source dossiers (machine-local)

`/private/tmp/claude-501/-Users-kunalsaxena-agentic-os/9ae53f0b-5ef7-4348-b9ff-a9d4b1ed35ab/scratchpad/ce-plan-research/`: `web-data-regulatory.md`, `web-charting-agent.md`, `agent-native.md`, `spec-flow.md`.
