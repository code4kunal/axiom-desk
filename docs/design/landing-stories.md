# Landing: eight stories (2026-11-13)

Supersedes the section list in `landing-sections-spec.md` (Problem, Hedge and Evidence sections are gone). User direction, 2026-11-13: the home page tells the story of every main V1 feature, each story is simple to explain, and no figures appear on screen.

## Order

| # | id | Story | Plan units |
|---|----|-------|------------|
| 01 | season | Hero: the season turns (Risk-on → Early warning), the basket moves, a hedge is drafted. Four steps, each with a plain sentence. | U22, U23, U24 |
| 02 | one-desk | One desk instead of four tools: a linked grid of every feature, plus the proof line. | all |
| 03 | sectors | Sector rotation, smart-money flows (R133), macro as context, morning view; the four-season cycle. | U22, U26 |
| 04 | charts | Synced charts, live signals with track records, screener with entry and exit, daily watchlist. | U14–U18 |
| 05 | options | Deep option chain, volatility lab ranking trades by premium (VRP), one pricing model. | U9–U11 |
| 06 | strategies | Strategy builder, backtests checked on unseen years, Python lab. | U19, U20 |
| 07 | baskets | Multi-asset baskets and hedge drafts; a person confirms every order. | U23, U24 |
| 08 | agent | Plain-word questions, cited answers, screens and option trades by chat. | U25 |
| — | brokers | White-label offer; outside the numbered nav. | — |

## Rules

- No figures in copy. `test/copy-rules.ts` still fails any unlabelled figure; the only figures left are the agent clip's citation markers and the `STEP n OF 4` counters (exempt).
- Season names follow the regime engine (R39): Risk-on, Early deterioration (said as "early warning"), Risk-off, Recovery.
- Colour roles: monsoon = rising / risk-on, geru = turning / falling, asset colours only for asset classes, ink for everything else.
- No superlatives or promised results ("best trade", "world's best"). The footer line stands: research tool, not investment advice, no performance promised.
- Clips are CSS-only sample screens (`src/landing/clips`), labelled ILLUSTRATIVE, final frame under reduced motion, started when their section is revealed.
