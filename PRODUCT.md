# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Next.js App Router in `apps/desk` (landing page, sign-in and the signed-in desk in one app), Tailwind driven only by DESIGN.md tokens, Motion for UI motion, GSAP ScrollTrigger for scroll-driven sequences, three.js for 3D (hero only on the landing page), HyperFrames for pre-rendered product clips, 21st.dev primitives restyled to tokens. Engines are Python behind a capability registry (KTD1). Chart renderer: decided by the U14 spike (`tools/benchmarks/renderer/RESULT.md`).

## Users

- **Primary, V1: the internal investment desk.** PMs, analysts, options traders and quants who today work across TradingView, Sensibull/Opstra/Tradl, Screener.in/Tijori and Excel/Python backtests. V1 is done when they stop using those four tools for daily work.
- **Paying customer: brokers (B2B2C).** They license Axiom white-labelled for their retail clients. Their SEBI-registered research analysts author baskets, Radar calls and ideas shown to clients.
- **V2 end users: the brokers' retail clients**, Indian investors and traders.

## Product Purpose

One multi-asset research and portfolio platform for India-investable assets. Users research, chart, diversify, trade options with statistically backed intelligence, and hedge before markets turn, driven by screen or by a cited AI agent. The agent drafts actions; a human confirms every order in the broker's own order flow.

## Positioning

**Evidence-graded intelligence.** Every setup, pattern and hedge trigger carries its base rate, sample size and out-of-sample proof, or says "insufficient evidence". Every options number derives from one arbitrage-free volatility surface. A daily archive of the desk's own computed surfaces, started on day one, is the calibration base competitors cannot buy.

## Operating Context

- Daily desk work: the pre-open console, the Command Center (regime and confidence, leading sectors and asset classes, top Radar opportunities, risk triggers), up to 8 synced charts, option chains and the Volatility Lab, strategy backtests, hedge drafts.
- Sign-in through the desk's OIDC identity provider with MFA. Roles: PM, analyst, trader, quant, admin.
- The landing page is for mass public use: Indian investors and traders, most of them first-time visitors on mid-range Android phones. It also serves brokers in discovery and the desk. The product behind it stays desk-first in V1, with retail clients reaching it through brokers in V2, so the landing page explains and invites but never offers sign-up for trading or advice.

## Capabilities and Constraints

- Plan of record: `docs/plans/2026-11-12-1110-feat-axiom-desk-platform-plan.md`.
- No autonomous trading. "Big player" activity is inferred and shown with its evidence, never attributed to an entity or called manipulation.
- Copy that brokers may reuse carries SEBI exposure: no performance promises and no buy, sell or advice wording.
- Engines behind U17, U18, U22 and U25 are not built yet. Screens that need them run on recorded fixtures labelled as such.
- Global markets are analysis only; the investable universe is what an Indian resident can directly buy.

## Brand Commitments

- Name: Axiom. Wordmark: typeset, no logo yet.
- Voice: quant-precise and evidence-first. Numbers carry base rates; short copy.

## Evidence on Hand

None. No customer or broker logos, testimonials, desk results, metrics or press exist. Do not fabricate any.

## Product Principles

1. Show the evidence or say there isn't enough.
2. The engine computes every number; screens and the agent show the same one.
3. Draft, never execute: a human confirms every order.
4. Diversify across what Indians can actually buy, and prepare before the turn.
