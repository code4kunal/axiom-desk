---
title: Risk Appetite - HLD and LLD
type: feat
date: 2026-11-15
status: draft for review
execution: docs only, no code in this PR
---

# Risk Appetite: Profile, Suitability Labels and Evidence-Graded Ranges - HLD and LLD

## Goal Capsule

- **Objective:** add risk appetite to the platform so that what a user sees (ideas, ranges, sizes, basket labels) respects a stated risk level, every number carries its evidence grade, and the broker can show a regulator why.
- **Authority:** `docs/plans/2026-11-12-1110-feat-axiom-desk-platform-plan.md` governs. Specifically R52-R56, R60-R62, R137, KTD16, KTD17, KTD20 and the plan-delta decision D1 (`docs/research/2026-11-12-plan-deltas-from-ce-plan-session.md`). Where this file disagrees, the platform plan wins.
- **Status:** draft for Kunal and a desk quant. Every band number is a placeholder. Regulatory points are my reading of secondary sources, not legal advice, and go through gate G2 before build.
- **Stop conditions:** stop and ask if any requirement can only be met by the agent proposing its own allocation, instrument or ticket to a retail client (that breaks D1 and R55).
- **Companion:** research draft in Claude Docs, https://claude.ai/artifact/AtrNvKg1uvVTmV7jpugxE3 (its Sources list carries source numbers 1-10 used there).

## 1. What the plan already says, and a correction

An earlier draft of this work said the plan has no risk profile and proposed personalised size guidance for every user. Reading the plan in the repo shows both points were wrong or incomplete:

| Item | What the plan says | Consequence |
| --- | --- | --- |
| Risk profiling | R61 [V2]: retail clients complete risk profiling, and a basket is shown as suitable or unsuitable against that profile. | The feature exists as one requirement. It has no design, data model or unit. This document supplies those. |
| Retail agent limits | D1 and R55: for retail the agent drafts only what an RA authored, explains freely, and never proposes its own allocation, instrument or ticket. | Personalised size guidance for retail is out. Sizing follows an RA basket and the client holdings only. |
| Who authors for retail | R60 and A3: baskets, Radar calls and ideas reach retail only when the tenant RA team authored or approved them. A2: the broker owns client compliance. | The broker, not Axiom, is the party that holds the client relationship. |
| Output gate | R62 and U25: the SEBI gate classifies output as data, neutral analytics or research/advice; no-op in V1, blocking in V2. | Risk-appetite rules plug into this gate. |
| Portfolio risk | R137 and U23: each holding shows a risk cushion (distance to invalidation, drawdown-at-risk, crash flag). | The basket risk label can be computed from these, not typed by hand. |

Not found in the plan: a questionnaire, a band scheme, a profile data model, per-book risk limits for the desk (V1), or re-profiling rules. Those are new.

## 2. Evidence

Grades: Strong (regulator text or peer-reviewed), Moderate (professional or law-firm summary), Weak (blog, vendor, opinion).

| Claim | Source | Grade |
| --- | --- | --- |
| SEBI separates research from advice by whether a trading call is one-to-one after risk profiling and suitability assessment (advice) or one-to-many with neither (research). | Cyril Amarchand Mangaldas summary of SEBI consultation paper of 6 Aug 2024 [S1] | Moderate. Consultation paper, final rules not checked. |
| A basket of more than one security given to research clients falls within a research report (SEBI informal guidance to LGT Wealth, 5 Apr 2023). The 2024 paper proposes to codify model portfolios as research, subject to guidelines, reportedly with weightages assigned in the report. | [S1], [S2] | Moderate. |
| An RA running model portfolios without IA registration was treated as a violation and settled for Rs 28.6 lakh (Stallion Asset, 2022). | Vinod Kothari [S2] | Moderate. |
| Investment advisers must build a risk profile, assess suitability, advise appropriately to the profile, and keep records for at least 5 years. | SEBI (Investment Advisers) Regulations 2013, BCAS reference copy, partly locked [S3] | Moderate. Check the official text. |
| In the RA master circular (6 Feb 2026), pages 1-56 of 101, the phrase risk profile appears once, in a conflicts rule against incentives to sell products that do not suit client risk profile (16.4(xi)). Annexures B-J unread. | [S4] | Strong for what was read; half the document unread. |
| About 80% of 90,000 surveyed households put capital protection ahead of higher returns; 93% of F&O traders lost money in Apr 2021 - Mar 2024. | SEBI 2025 survey as reported by Business Standard [S5] | Moderate. Press report of the survey. |
| Free AMC risk profilers are about 10 questions and end in a product list. | freefincal review of about 8 tools [S6] | Weak. One author's opinion. |
| Assess need, ability and behavioural tolerance separately, reconcile, aim for questionnaire reliability 0.70 or higher. | CFA Institute Research and Policy Center guide [S7] | Moderate. |
| Scaling exposure down when volatility is high improved Sharpe out of sample, 1977-2020, net of costs: 1.062 against 0.940. Robustness is disputed. | DeMiguel et al., Journal of Finance 2024 [S8] | Strong, but US factor data, not Indian equities. |

Not found: any study showing that questionnaire scores predict how Indian investors behave in a drawdown. The design therefore treats the questionnaire as a record and a floor, and treats the label, ranges and gating as the product. Whether re-profiling after an actual drawdown improves outcomes is an untested idea (my hypothesis), to be measured through the Edge Ledger (U27).

## 3. HLD

### Principles

1. Risk appetite changes what is shown and how large, never what is true. Numbers stay the same; ranges, percentiles and gating change.
2. Two tracks, because the legal position differs. Desk users (A1) are the broker's own staff, so a risk mandate is internal risk control. Retail clients (A4) bring the advice question, so Axiom only labels what an RA authored.
3. The party that owns the client owns the profile: the broker (A2). Axiom stores it per tenant, versioned, and obeys it.
4. No profile, no personalised output. Without one, only general non-personalised views show.
5. Every output states its evidence grade (Tested, Candidate, Opinion) and the band rule that applied.

### Components

```mermaid
flowchart LR
  subgraph Capture
    Q[Questionnaire and capacity items] --> P[Risk profile record, versioned]
    M[Desk book risk mandate] --> P
  end
  P --> B[Band resolver: lower of willingness and capacity]
  B --> L[Limits: size cap, drawdown trigger, percentile, min grade]
  E[Evidence engine U12: grade, sample, base rate] --> S[Scenario range builder]
  S --> G
  L --> G[Output policy U25 and SEBI gate]
  C[Cushion and drawdown-at-risk U23] --> RL[Basket risk label, RA signs off]
  RL --> SU[Suitability match: label vs client band]
  B --> SU
  SU --> G
  G --> O[Screens, agent answers, drafts]
  G --> A[(Audit log U2: profile version, rule, output)]
```

### Track A: desk (V1)

A PM or admin sets a book risk mandate. It reuses the same band table and limits. Effect: the idea cards, Radar and agent answers for that book show the percentile, size range and minimum evidence grade of the mandate. Desk users keep full drafting (R55), so no suitability issue arises.

### Track B: retail via broker (V2)

1. The broker captures the client profile through Axiom white-labelled screens or imports its own (open decision).
2. The RA team authors a basket and signs its risk label. Axiom proposes the label from computed cushions (U23); the RA edits and approves it. Radar calls get the same.
3. Suitability match compares the basket label with the client band and shows suitable, caution or unsuitable with the reason. This is R61.
4. The agent explains and analyses. It drafts only follow or rebalance drafts toward an RA basket, sized to holdings (D1).
5. Scenario ranges follow the client band, but only for RA-authored items. Axiom never computes a personal allocation.

### Open legal question (blocks Track B build)

SEBI summaries draw the research/advice line at one-to-one output after risk profiling and suitability. R61 shows a per-client suitable or unsuitable label on an RA basket. That may be read as the suitability step that turns research into advice. Options for counsel: (a) the broker, who is registered, performs and owns the suitability judgement and Axiom only displays its result; (b) the broker or tenant holds IA registration; (c) show a non-personalised risk label only and let the client compare it themselves. Track B design below assumes (a) and degrades to (c) by turning off the match step. Gate G2 or a new suitability gate decides.

## 4. LLD

### 4.1 Data model (proposed, all point-in-time like U5)

| Table | Key fields | Notes |
| --- | --- | --- |
| `risk_profile` | tenant_id, subject_id (user or client), questionnaire_version, willingness_score, capacity_score, horizon, goals, band, band_reason, source (axiom or broker_import), effective_from, effective_to, recorded_at, recorded_by | Append-only. A change closes the old row. Past outputs replay against the profile in force. |
| `risk_override` | profile_id, direction, new_band, reason, recorded_at | Lower band always allowed. Higher band only for view-only scenarios, never size guidance. |
| `book_mandate` | tenant_id, book_id, band, limits_override, set_by, effective_from, effective_to | Track A. |
| `band_table` | version, band, equity_share_min, equity_share_max, single_idea_cap_pct, drawdown_trigger_pct, best_case_percentile, min_evidence_grade, signed_by, signed_at | Versioned. Signed by a quant (G4). Values are placeholders until signed. |
| `basket_risk_label` | basket_id, version, label, computed_inputs (cushion stats), proposed_by, approved_by_ra, approved_at | RA approval required before a retail client sees it (R60). |
| `suitability_result` | output_id, profile_id, label_id, result, reason, evaluated_at | Stored with every personalised output. |
| `evidence_grade` (field on U12 registry card) | grade, sample_size, independent_episodes, last_validated | Tested, Candidate or Opinion. |

### 4.2 Band resolution

- Willingness band and capacity band are scored separately. The band is the lower of the two. Horizon and need do not set the band; if the need exceeds capacity, the goal is flagged.
- Five bands as a starting point: Capital preservation, Cautious, Balanced, Growth, Aggressive. Whether to map names to SEBI risk-o-meter (six levels) is open.

Placeholder limits (quant to set; shape only):

| Band | Equity share | Single-idea cap | Drawdown trigger | Best case shown | Min grade to show |
| --- | --- | --- | --- | --- | --- |
| Capital preservation | 0-15% | 2% | -5% | 50th pct | Tested |
| Cautious | 15-35% | 3% | -10% | 75th pct | Tested |
| Balanced | 35-60% | 5% | -15% | 75th pct | Tested, Candidate flagged |
| Growth | 60-80% | 7% | -25% | 90th pct | Tested, Candidate flagged |
| Aggressive | 80-100% | 10% | -35% | 90th pct | All, Opinion marked, no size guidance |

### 4.3 Scenario range builder (extends U12)

- Input: the forward-return distribution after matching readings, and the matched-control distribution from the research brief's gate 3.
- Output: conservative (control median), base (pattern median), best case (the band percentile), plus the worst past drawdown beside the upside in the same type size.
- Grade rules: Tested shows the range. Candidate shows the lower end of the interval, with the independent episode count. Opinion shows no numbers.
- Size range = band single-idea cap times 100% (Tested) or 50% (Candidate, my proposal), none for Opinion. Applies to desk books and, for retail, only as context beside an RA item.
- Drawdown throttle: when a linked portfolio passes the band trigger, new-idea size ranges halve until recovery (needs quant sign-off).

### 4.4 Suitability match (Track B)

```
result = suitable   if label_level <= client_band_level
         caution    if label_level == client_band_level + 1
         unsuitable otherwise
```
The rule and the label, band and versions used are stored in `suitability_result`. Rule text is versioned and signed. If counsel chooses option (c), this step is switched off by tenant configuration and only the label shows.

### 4.5 Output policy additions (U25)

1. No current profile: general views only.
2. Evidence-grade gating as in 4.2 and 4.3.
3. Wording: historical frequencies and ranges only; no accuracy, assured or target returns (R53).
4. Disclosure on every output: as-of time, sources, method, sample size, grade, profile version.
5. Retail: block any agent-proposed allocation, instrument or ticket not authored by the RA (D1, R55).
6. No incentive coupling: ranking and revenue sharing must not favour higher-risk ideas for higher bands (conflicts rule 16.4(xi) in [S4]).

### 4.6 Capabilities and files (proposed)

| Capability | Purpose | Files |
| --- | --- | --- |
| `risk.profile.get / set` | read and record a profile, point-in-time | `packages/core/src/axiom_core/riskprofile.py`, migrations |
| `risk.band.resolve` | band and limits for a principal | `packages/core/src/axiom_core/riskband.py` |
| `risk.mandate.set` | desk book mandate (PM or admin; quant signs band table) | `packages/core/src/axiom_core/riskprofile.py`, `authz.py` |
| `risk.range.build` | scenario range by grade and band | `packages/evidence/src/axiom_evidence/ranges.py` |
| `risk.label.propose` | basket label from cushions, RA approves | `packages/portfolio/src/axiom_portfolio/risklabel.py` |
| `risk.suitability.check` | match label to client band | `packages/portfolio/src/axiom_portfolio/suitability.py` |
| policy rules | rules in 4.5 | `packages/agent/src/axiom_agent/policy.py`, `packages/core/src/axiom_core/sebi_gate.py` |
| UI | profile capture, band badge, range card, label chip | `apps/desk/src/risk/` (after G5 and the feature pipeline in CLAUDE.md) |

Every capability is registered in U3 so screen and agent return the same envelope (AE7).

### 4.7 Test scenarios

- A profile change closes the old row and an output from last week replays against the profile in force then.
- Willingness Aggressive with capacity Cautious resolves to Cautious, with the reason shown.
- A user override to a higher band is refused for size guidance and allowed for a view-only scenario, and is logged.
- No profile: personalised range requests return the general view and say why.
- A Candidate idea in the Cautious band is not shown; in Growth it shows the lower interval end, the episode count and a flag.
- An Opinion idea shows no numbers in any band; in Aggressive it shows as marked opinion with no size.
- A retail client asks the agent what to buy: the agent explains, lists RA-published baskets and drafts nothing not authored by an RA (D1).
- A basket label proposed from cushions cannot reach a client before RA approval.
- A forged tenant, subject or band in request parameters is refused; the session decides the principal (KTD20).
- Each suitability result writes one audit row with profile, label and rule versions.
- Band table edited without quant signature is rejected (G4).

## 5. Feasibility

| Piece | Reuse | New work (my estimate) | Risk |
| --- | --- | --- | --- |
| Profile, mandate, audit | U2 tenancy and audit; U5 point-in-time convention | Small to medium: tables, authz roles, capture API | Low |
| Band table and limits | Config plus quant sign-off (G4) | Small to build; the numbers are a quant task | Medium: numbers need backtesting |
| Evidence grade and ranges | U12 registry card, matched controls | Medium | History since 2019 gives few independent episodes, so many ideas will grade Candidate (my reasoning) |
| Basket label from cushions | U23 cushion and drawdown-at-risk | Medium; blocked until U23 exists | Label design is a quant call |
| Suitability match | Output policy U25 | Small | The legal question above |
| Questionnaire | None | Medium: 7-12 willingness items plus capacity items, a pilot | No Indian evidence on predictive power; reliability target 0.70 from [S7] |
| UI | Desk app after G5 | Medium | Premium design bar in CLAUDE.md |

Order: Track A first (V1, no regulatory dependency beyond the output wording), Track B design now and build after the legal read. The profile service needs no market data, so it can start before G1 clears (my reasoning).

## 6. Edges to sell

Competitor behaviour here is from one blog review of free AMC tools [S6] and the SEBI circulars; I did not trial any competitor product, so treat edge claims as hypotheses to be measured.

| Edge | Buyer | Why it is hard to copy | How we prove it |
| --- | --- | --- | --- |
| Risk label computed from drawdown-at-risk and cushion, not typed by hand | Broker RA team | Needs our U23 cushion and the evidence engine | Compare label to realised drawdown per basket in the Edge Ledger |
| Evidence grade on every range, with the control beside it | Broker, desk | Needs matched controls and point-in-time data (U5, U12) | Share of ideas shown at each grade; hit rate against control by grade |
| Replayable audit trail: any past output against the profile and rules in force | Broker compliance | Point-in-time convention on every table | Demo: replay a past day for an auditor in one query |
| Software-enforced research/advice line (RA-authored only) | Broker legal | U25 gate plus D1 | Gate log: blocked outputs by reason |
| Desk book mandates with the same grading | Prop and broker desks | Same engine as retail track, no extra build | Fewer limit breaches per book (needs desk pilot) |
| Re-profile prompted by an actual drawdown, not an annual form | Broker | Needs portfolio link (U23) | Untested hypothesis; measure panic-exit rate before and after in a pilot |
| Honest ranges for a market where 93% of F&O traders lost money and about 80% of households put capital protection first | Broker marketing and compliance | Positioning, not technology | Pilot feedback |

## 7. Decisions needed

1. Counsel: does the R61 suitable/unsuitable label on an RA basket stay research, or does it need IA registration (options a, b, c in section 3)? Also read the full RA master circular including Annexures B-J, and the final rules after the 2024 consultation paper.
2. Who captures and stores the retail profile: broker or Axiom?
3. Quant: band cut-offs, percentiles, caps, minimum sample for Candidate, volatility scaling versus fixed caps.
4. Kunal: should band names follow the SEBI risk-o-meter?
5. Is a suitability gate separate from G2 cleaner?

## 8. Implementation unit

### U29. Risk profile, bands and suitability labels (proposed)

- **Goal:** one profile and band service that every output obeys, with evidence-graded ranges and RA-signed basket labels.
- **Requirements:** R61 (design), R55, R60, R62, R137, AE7; KTD16, KTD17, KTD20; D1.
- **Dependencies:** U2, U3, U12, U23 (labels), U25.
- **Gates:** G2 (legal read of option a, b or c), G4 (band table and range method).
- **Files:** see 4.6.
- **Execution note:** build Track A and the profile service test-first; hold Track B label and match steps until the legal read.
- **Verification:** all scenarios in 4.7 pass; replay test reproduces a past output exactly.

## Sources

- [S1] Conventus Law, India: revamping the investment advisers and research analysts frameworks (CAM summary of SEBI consultation paper, 6 Aug 2024). https://conventuslaw.com/report/india-revamping-the-investment-advisers-and-research-analysts-frameworks-the-sebi-way/
- [S2] Vinod Kothari, Research Analysts v/s Investment Advisors, is the line blurring? (9 Aug 2024, updated 1 Oct 2024). https://vinodkothari.com/?p=50960
- [S3] SEBI (Investment Advisers) Regulations 2013, BCAS reference copy. https://www.bcasonline.org/Referencer2016-17/Other%20Laws/sebi_investment_advisers_regulations_2013.html
- [S4] SEBI Master Circular for Research Analysts, 6 Feb 2026 (mirror). https://www.cse-india.com/upload/upload/1770375507051.pdf
- [S5] Business Standard, Indian investors remain risk-averse, Sebi urges diversified portfolios. https://www.business-standard.com/amp/finance/personal-finance/sebi-2025-investment-survey-risk-appetite-diversification-portfolio-125101001108_1.html
- [S6] freefincal, Your risk profile is not a label, it is a behaviour you discover in a drawdown. https://freefincal.com/your-risk-profile-isnt-a-label-its-a-behaviour-you-discover-in-a-drawdown/
- [S7] CFA Institute Research and Policy Center, Investment Risk Profiling. https://rpc.cfainstitute.org/-/media/documents/survey/investment-risk-profiling.pdf
- [S8] DeMiguel et al., A Multifactor Perspective on Volatility-Managed Portfolios, Journal of Finance (2024). https://lbsresearch.london.edu/id/eprint/3716/1/The%20Journal%20of%20Finance%20-%202024%20-%20DeMIGUEL%20-%20A%20Multifactor%20Perspective%20on%20Volatility%E2%80%90Managed%20Portfolios.pdf

Not checked: final SEBI rules after the 2024 consultation paper; the full RA master circular; any competitor product; Indian evidence that questionnaires predict drawdown behaviour.
