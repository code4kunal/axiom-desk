# Landing sections spec (U3, stacked default layout)

Scope: sections 01–08 in the server-rendered stacked layout (KTD5 step 1: no JS, no pin). U4 adds poster images, gate and scroll on top; U5 fills clip slots and the broker dialog. Copy is verbatim from `landing-direction.md` § First viewport and § Scroll storyboard; nothing here redesigns it. Tokens, steps and utilities are `DESIGN.md` / `globals.css` names (`frame`, `stamp`, `link`). Method: ui-ux-pro-max (`style` hit: editorial-grid-magazine, asymmetric grid, large plates, mobile reflow; `ux`: reserve media space with `aspect-ratio`, reduced motion) checked against the direction, the critique, TASTE.md and impeccable's craft floor.

## 1. Sheet grammar (every section 02–08)

- `<section id aria-labelledby>` inside `.frame`; `scroll-margin-top: 64px` (48px rail + 16px so the section's own rule never butts the rail hairline). Padding 96 top/bottom at 375, 128 at 1280. Each section opens with a full-content-width `1px solid var(--hairline)` rule.
- **Ordinal, not eyebrow.** Craft floor bans a label above a heading; the direction pins numbered sections and the rail shows `02 / 09`, so the number is position information the reader needs (skip the pin, deep-link). Resolution: the ordinal is a **folio**, never a kicker. At ≥ 768 it lives in a margin column (col 1) on the rule row, text starts at col 2; at 375 it sits on the rule row right-aligned, far corner, 48px of air before the h2. `label` step, `--ink-dim` 400, `aria-hidden="true"` (the nav already reads ordinals). No label word beside it.
- **h2 = the direction's first sentence**, Martel 700 `section-head`, `--ink`, `text-wrap: balance`. Remaining sentences of the line = **lede**, Hind 400 `subline` step, `--ink`, max 60ch, 16px under the h2. One-sentence lines (03, 04) are the whole h2 with no lede. No invented headlines.
- **Caption** (desk depth): `caption` step Martian Mono 400 uppercase `--ink-dim`, 24px under the lede, on its own hairline row (rule above, 12px padding). State words (`EXPANSION`, `EARLY DETERIORATION`) are weight 500 in `--monsoon` / `--geru` with a 12×12 inline-SVG scale-tick glyph (1.5px stroke, rotated to the needle angle: −30° expansion, +8° deterioration) so colour is never alone. `ILLUSTRATIVE` segments stay `--ink`.
- Grid at 1280 (12 col / 24 gap, col ≈ 76.7px): landscape clip (03) text cols 2–7, clip cols 8–12 (480px); portrait clips (04, 06) text cols 2–8, clip cols 9–12 (379px), caption pinned to the clip's bottom edge (build review: cut the void beside tall plates); card sections text cols 2–6, card cols 7–12 (580px); 02 and 08 text cols 2–9. Media top aligns to the h2 cap line. At 768 (8 col): ordinal col 1, text cols 2–8, media full 704px under the text, 32px gap. At 375: one column, media under the text, 24px gap. DOM order everywhere: ordinal, h2, lede, caption, media.
- Cards: `--raised`, `1px solid var(--hairline)`, radius 4px, no shadow; cells butt with single hairlines, padding 12px 12px at 375 and 16px at 1280, label row `label` step `--ink-dim`, value row Martian Mono 400 16px `--ink` (`tabular-nums`).

## 2. Section 01 hero (`id="season"`, h1 = statement, no ordinal, no reveal)

Strings: h1 **Markets have seasons. Axiom reads the season, reweights the basket, and shows its evidence.** · subline **A research instrument for Indian investors. It drafts; a human confirms every order.** · primary button **See how it reads a market** → `href="#reading"` (the 40% plate carries `id="reading"`; U4 keeps that id on the element whose scroll position maps to the 40% state, so on both paths the button lands where the reading begins instead of skipping the plates) · ghost link **For brokers** → `#brokers`.

Captions (`figcaption`, caption step; `ILLUSTRATIVE` in every one):
- 0: `REGIME EXPANSION · CONF 0.74 · N 212 · ILLUSTRATIVE` (EXPANSION monsoon)
- 40: `EARLY DETERIORATION · CONF 0.68 · N 212 · ILLUSTRATIVE` (EARLY DETERIORATION geru)
- 70: `EQUITY 61 → 42 · GILTS 18 → 29 · GOLD 9 → 17 · ILLUSTRATIVE`
- 100: the hedge card is plate 100's figcaption. One content string: `HEDGE DRAFT · INDEX PROTECTION · ILLUSTRATIVE · a human confirms every order`, rendered as a card: row 1 the three mono segments (caption step, `--ink-dim`, `ILLUSTRATIVE` in `--ink`); hairline; row 2 the last segment in Hind 500 16px `--ink`, lowercase exactly as written (R9 substring match). Server-rendered, so it is in the DOM from first paint.

| | 375 | 768 | 1280 |
|---|---|---|---|
| Statement | 40px, cols 1–4, runs 5–6 lines (see Risks) | 57px, cols 1–8, 4 lines | 80.7px, cols 1–7, 6 lines ≈ 475px |
| Subline + buttons | under statement; primary full-width 52px, ghost link 48px row beneath | cols 1–4 | cols 1–7; primary 48px auto-width + ghost 24px right |
| Plate 0 (LCP poster slot) | 300×300, first visually (`order: -1` below 768; DOM stays h1-first), caption 0 under it | cols 5–8, 341×341, beside subline row | cols 8–12, 480×480, rows 1–2 beside statement; caption 0 beneath |
| Plates 40/70/100 | 343×343 stacked, caption under each | 3-up, 218×218 | 3-up, cols 1–4 / 5–8 / 9–12, 379×379 |
| Hedge card | full width under plate 100 | cols 5–8 | cols 9–12 under plate 100 |

Poster slot (U3 stand-in, U4 swaps a 1200×1200 AVIF/WebP `<img alt="">` of identical box): `aspect-ratio: 1`, `--raised`, `1px solid var(--hairline)`, radius 4px, `aria-hidden`. Inside, one inline SVG so it is not a dead box: circle r = 44% stroke 1px `--hairline`; 24 ticks every 15°, 8px, `--ink-faint`; the four quadrant ticks 12px `--brass-mark`; one needle 1.5px `--brass-mark` from centre to 0.44r at −30° on plate 0 and +8° on plates 40/70/100 (the 38° sweep). Only plate 0 is `fetchpriority="high"`; 40/70/100 `loading="lazy"` (KTD5).

## 3. Sections 02–08

| § | id | h2 (Martel) | Lede (Hind) | Caption (Martian Mono) | Media |
|---|---|---|---|---|---|
| 02 | problem | Equity-only tools go quiet when the season turns. | By the time they flag the turn, prices have already fallen. | — | none in U3 (the "flat chart greys while the needle keeps reading" is scroll motion, U4; if U4 drops it, 02 stays type-only) |
| 03 | charts | Every pattern on the chart tells you how often it has worked before, or says it can't tell yet. | — | `BASE RATE · SAMPLE SIZE · UP TO 8 SYNCED CHARTS` | clip, landscape 1200×760 |
| 04 | options | Every options price comes from one consistent model, so the numbers agree everywhere. | — | `ONE ARBITRAGE-FREE SURFACE · SSVI` | clip, portrait 720×900 |
| 05 | hedge | When regime confidence shifts, Axiom drafts the hedge. | It never places an order; a human confirms each one. | — | evidence card (§5) |
| 06 | agent | Ask what changed since yesterday's close. | The agent answers with citations to the same numbers the screens show. | none given (see Proposed) | clip, portrait 720×900 |
| 07 | evidence | Every claim shows its base rate, sample size and out-of-sample result. | When it can't show all three, it says so: insufficient evidence. | — | specimen card + stamp legend (§5) |
| 08 | brokers | White-label Axiom for your clients. | Your SEBI-registered analysts author every basket and call. | — | button + public line (§6) |

08: the direction line's third sentence "Talk to the desk." is rendered once, as the button, not repeated in the lede.

## 4. Clip slots (03, 04, 06; U3 reserves, U5 fills)

Box = `width` + `aspect-ratio` (`1200/760` or `720/900`), never height from content, so the still, the placeholder and the real clip share one box (R12, CLS). Computed:

| Slot | 375 (w 343) | 768 (w 704 landscape / 432 portrait, cols 2–6) | 1280 (cols 8–12, w 480) |
|---|---|---|---|
| 03 landscape | 343×217 | 704×446 | 480×304 |
| 04 portrait | 343×429 | 432×540 | 379×474 |
| 06 portrait | 343×429 | 432×540 | 379×474 |

U3 placeholder: `--raised`, `1px solid var(--hairline)`, radius 4px, a second hairline frame inset 16px, label `CLIP PLACEHOLDER` (`label` step, `--ink-dim`) at top-left 24px inset. Server component, no `<video>`. Position: right of the text at 1280 (top edge on the h2 cap line), under the text at 768 and 375. Leave 48px clear at the slot's bottom-left for U5's pause control.

## 5. Cards

**05 evidence card** (cols 7–12 at 1280, full width below). Same `HedgeCard` component as the hero, with a grid between its two rows:
- Row 1: `HEDGE DRAFT · INDEX PROTECTION · ILLUSTRATIVE` (mono segments of the shared string).
- Grid, five cells, one row at ≥ 768, 2+2+1 (last spanning) at 375; labels/values need user approval, see Proposed: `TRIGGER` / `EARLY DETERIORATION` (geru 500 + tick glyph) · `BASE RATE` / `0.58` · `N` / `212` · `OOS` / `0.54` · `GRADE` / stamp `CNF`.
- Row 2: `a human confirms every order` (Hind 500). Without approval the card ships as the hero card alone (two rows), which still satisfies 05's copy.

**07 specimen card** (cols 7–12 at 1280): one string `BASE RATE 0.58 · N 212 · OOS 0.54 · AS OF 2026-11-13 · ILLUSTRATIVE` rendered as five butted cells: `BASE RATE`/`0.58`, `N`/`212`, `OOS`/`0.54`, `AS OF`/`2026-11-13`, and a fifth label-less cell `ILLUSTRATIVE` in `--ink`. Built as four figure cells (one row of four at ≥ 768, 2×2 at 375) plus a full-width closing `ILLUSTRATIVE` row at every width: five cells of 116px could not hold `ILLUSTRATIVE` or the date. The three numbers are the same figures the 05 grid shows: one example, one number everywhere (product principle 2).

**Stamp legend** under the card, 16px gap, same column: three 48px rows on hairlines, `stamp` utility left (72px column), meaning in Hind `body` `--ink` right. Exact text: `CNF` out-of-sample confirmed · `RAC` in-sample only · `WL` insufficient evidence. Colours per DESIGN.md §4 (monsoon / brass-line+brass / geru). Static, never revealed.

## 6. Section 08 action

- Brass primary 48px (auto width; full width at 375): label **Talk to the desk**. U3 renders it as `<a class="button" href="mailto:{contact}?subject={subject}">` with address and subject from `content.ts`, so the action works with JS off; U5 intercepts the click to open the dialog (R10) and the anchor remains the no-JS fallback. Subject string needs approval (Proposed).
- 16px under it, Hind `body` `--ink` (not dimmed, it is the public's only action): **Investing with a broker? Ask them for Axiom.**
- Nothing else: no form, pricing, sign-up.

## 7. Reveal motion (KTD6) and state colours

- One IntersectionObserver, threshold 0.2, once. Hidden state `opacity: 0; translate: 0 16px` is applied only under `html[data-js]` (set by the KTD8 head script), so no-JS renders everything visible. Transition `var(--t-reveal) var(--ease-reveal)`, 60ms stagger by `--i`. Reduced motion: opacity only.
- Hero: no reveal (LCP, already visible). Cards, grids, stamps, legend, hairlines, ordinals: never animate; a card that reveals does so as one block with nothing inside moving. Groups (≤ 5): 02 h2, lede · 03 h2, caption, clip · 04 h2, caption, clip · 05 h2, lede (card static) · 06 h2, lede, caption, clip · 07 h2, lede (card, legend static) · 08 h2, lede, button, public line.
- Calibration guard, no new copy: monsoon on `EXPANSION` (caption 0), the `CNF` stamp (05 grid if approved, 07 legend); geru on `EARLY DETERIORATION` (caption 40, 05 TRIGGER cell), the `WL` stamp (07 legend). Each carries its word and the tick or outline glyph. Pink paper is the light ground via tokens; nothing here adds colour.

## 8. Section ids

`season` (hero, h1), `problem`, `charts`, `options`, `hedge`, `agent`, `evidence`, `brokers`; `footer` exists (U2). Sub-anchor `reading` on the 40% plate. All with `scroll-margin-top: 64px`; `html` already has `scroll-padding-top: 48px`.

## 9. Proposed new copy (all three approved by the user, 2026-11-13; built)

1. 05 grid labels `TRIGGER`, `GRADE` and values `EARLY DETERIORATION`, `0.58`, `212`, `0.54`, `CNF` (all ILLUSTRATIVE, under the card's ILLUSTRATIVE segment). `BASE RATE`, `N`, `OOS` are direction vocabulary.
2. 06 caption: `CITATIONS · SAME NUMBERS AS THE SCREENS`.
3. 08 mailto subject: `Axiom for brokers`.

## 10. Data figures (R3, every instance)

0.74, 212 (caption 0) · 0.68, 212 (caption 40) · 61, 42, 18, 29, 9, 17 (caption 70) · 0.58, 212, 0.54 (05 grid, proposed) · 0.58, 212, 0.54, 2026-11-13 (07 card; the date counted to be safe). **17 with the proposed 05 grid, 14 without**; both under 20. Exempt: ordinals, `02 / 09` in the rail, `8` in `UP TO 8 SYNCED CHARTS`. Every figure sits in a group carrying `ILLUSTRATIVE`.

## 11. Not stock SaaS, per viewport

- **375.** A 300px instrument plate above a six-line serif statement, not a gradient hero with a centred H1; plates read as numbered specimen sheets with mono captions, not a carousel; cards are ruled cells on pink paper or basalt, no shadow, no icon-heading-text trio; the one brass button is ink-on-brass, no purple; geru and monsoon appear as state words with tick glyphs, not as badges.
- **768.** Folio ordinals in a margin column on a hairline rule, no eyebrow labels; clips are fixed plates set under the type with a second hairline frame, not screenshots in a browser chrome mock; the evidence card is five butted cells in Martian Mono, not stat tiles; the stamp legend is a ruled table of railway grades, not a feature list.
- **1280.** Asymmetric sheet, text cols 2–7 against plates cols 8–12, never a three-card row; statement block and poster of equal height on the first screen, no logo strip beneath; the only CTA below the fold is a brass link-button plus a plain public line, no pricing table, no testimonials; numbers never count up and nothing lifts on hover.

## 12. Risks

- The direction's "two lines at 88px" (1440) and "three lines max at 40px" (390) cannot hold the 91-character statement; it runs 5–6 lines at both ends. Composition above is sized for that. Decided 2026-11-13: the user kept the statement as written.
- At 375 the primary button lands near 830px of the first 844px with the poster-first order; measure in U3, and if it overflows drop caption 0 below the buttons rather than shrinking the poster.
- Banned-phrase check: every string above read against returns, guaranteed, guarantee, profit, profits, buy, buying, sell, selling, tips, beat the market (whole words); none appear. Screenshots at 375/768/1280 light and dark are the U3 exit: `NOT RUN` here.
