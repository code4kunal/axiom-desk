# Axiom DESIGN.md

**Provisional: written from the approved direction before the build; rewritten from the shipped build at the end of the landing plan.**

Source of truth until then: `docs/design/landing-direction.md` ("Yantra", approved 2026-11-13). This file only names tokens and rules; it does not redesign. Scope: `apps/desk` landing page (U2–U7), plus the Axiom Charts desk surface in §8 (charts plan U8, 2026-11-14). Mock: `docs/design/mocks/charts-desk.html`.

## 1. Colour tokens

**Superseded by palette v2 (user ruling 2026-11-13: no pink paper; white ground, colour as data, larger type).** The full token table with WCAG ratios is `docs/design/landing-palette-v2.md` §2; the values ship in `apps/desk/src/app/globals.css` (`@theme static` = light, `:root[data-theme="dark"]` = dark). Light is primary.

- Ground `#FFFFFF` / dark `#0E1114`; ink `#0E1319` / `#F1F3F5`. `--brass*` keeps its role (links, primary button, focus) and now resolves to ink.
- Asset colours, base for text (≥4.5:1), `-mark` for points, bars and outlines only (≥3:1): equity = ink, gilts `#0F7B7A`, gold `#956208`, cash `#636E7A`, intl `#B8206F`.
- Regime: `--monsoon` `#107A3A` (the word EXPANSION only), `--geru` `#BF3D12` (deterioration word; `--geru-mark` on the rim after the sweep and the wordmark i-tick). Never fills.
- `@theme static` is required: plain `@theme` drops tokens only read through `var()` (the ring reads `-mark` tokens from JS), which left the light band invisible.
- No purple, indigo or blue. No gradient. No colour outside the token set in `apps/desk`.

## 2. Type

**Superseded by palette v2** (`docs/design/landing-palette-v2.md` §3). Self-hosted via `next/font/google`, latin subset.

| Token | Family | Weights |
|---|---|---|
| `--font-display` | Eczar | 700, 800 |
| `--font-body` | Anek Latin | 400, 500, 600 |
| `--font-mono` | Martian Mono | 400, 500 |

Scale at 375 → 1280: statement 38 → 68 (capped at 9svh from 1024), regime word 22 → 34, section head 32 → 52, subline 18 → 21, body 18 → 20, ui 17, small 15, caption 13, label 12.

- Numbers: Martian Mono only, `tabular-nums`. They cut, never count up.
- Floor: nothing under 12px; 12px only in Martian Mono 500 uppercase.

## 3. Space, shape, surface

- Spacing scale (px): `4 8 12 16 24 32 48 64 96 128`. Tokens `--s-1 … --s-10` in that order.
- Section rhythm: 96 top/bottom at 390, 128 at 1440. Inside a card: 16 at 390, 24 at 1440.
- Gutters: 16 at 375, 32 at 768, 48 at 1280+. Content max 1280px, centred.
- Radius: `--r-1: 2px` (stamps, cells), `--r-2: 4px` (buttons, cards, dialogs, sheets). **Ceiling 4px.** No pills, no circles except the ring.
- Shadows: none. Elevation is `--raised` over `--ground` plus a `--hairline` border. No `box-shadow`, no `backdrop-filter`, no blur.
- Hairline rules: `1px solid var(--hairline)`; at DPR ≥ 2 keep 1px (never 0.5px, mid-range LCDs drop it). Section dividers run full content width; cell dividers inside specimen cards are hairline on all four sides, cells butt (`border-collapse`-style, no double rules).
- Buttons: 48px tall minimum (52px full-width on the hero at 390), padding 0 24px, radius 4px, Anek Latin 500 17px. Primary: fill `--brass-mark` (ink), text `--on-brass`. Ghost: 1px `--hairline` border, text `--ink`, hover border `--ink-dim` (colour only). No lift, no shadow, no scale.
- Links in body: `--brass` text, underline 1px offset 3px; hover switches underline colour to `--ink` (colour only).
- Targets: 48×48 minimum, 8px clear on every side. Icon-only controls carry a visible or `aria-label` word.
- Focus: `outline: 2px solid var(--brass-line); outline-offset: 2px; border-radius: inherit`. Never removed, never replaced by a box-shadow. The 2px offset puts the ring on `--ground`, so it stays visible on a brass button too.

## 4. Stamps (evidence grades)

Outline stamps, never filled. Martian Mono 500 12px uppercase, tracking 0.12em, padding 2px 6px, `border: 1.5px solid`, radius 2px, no rotation, no texture.

| Grade | Meaning | Outline | Text |
|---|---|---|---|
| `CNF` | out-of-sample confirmed | `--monsoon-mark` | `--monsoon` |
| `RAC` | in-sample only | `--gold-mark` | `--gold` |
| `WL` | insufficient evidence | `--cash-mark` | `--cash` |

Tokens: `--stamp-cnf`, `--stamp-rac`, `--stamp-wl` alias the outline colours above so a theme change cannot split them. Every stamp carries its three-letter word; colour is never the only signal.

## 5. Motion grammar

- `--ease-reveal: cubic-bezier(0.2, 0.7, 0.2, 1)`; `--t-reveal: 480ms`; `--t-exit: 200ms`; stagger 60ms, at most five items. Reveal = 16px rise + opacity, CSS transition toggled by one IntersectionObserver (KTD6).
- Scroll-tied: scrub, no easing. Needle and pointer tilt: 0.12s lerp, never spring.
- Theme switch: `--t-theme: 160ms`, `transition-property: color, background-color, border-color, outline-color` only.
- Never animates: body text, numbers, hairlines, wordmark, button labels, stamps, nav rail, footer.
- `prefers-reduced-motion: reduce`: reveals become opacity only; no pin, no scrub, no tilt; theme switch instant.

## 6. Banned

Gradients (fill, text, border); purple, indigo, violet, any blue-black ground; Inter, Geist, DM Sans, Fraunces, Space Grotesk; hover lift or scale; shadow growth; blur or glass; card rows of three; logo strips; testimonials or metrics (none exist); pills; count-up numbers; parallax beyond the ring; glow beyond 0.3 emissive on brass in the ring; emoji as icons; orange-on-black ticker density; any copy containing returns, guaranteed, profit, buy, sell, tips, beat the market.

## 7. Calibration guard (R21)

Both themes must keep the second voice or the build has drifted: `--geru` and `--monsoon` as real state colours on the page, the CNF / RAC / WL outline stamps, and the five asset colours carrying data on a white ground. Ink alone on white with one accent is the stock-fintech cluster; it is not this design.

## 8. Desk chart surface (Axiom Charts, plan U8)

Written 2026-11-14 from the charts plan, TASTE.md and the chart colour ruling (every chart element has a named colour role; colour is never the only cue). No new references were given. The landing tokens above still hold; this section adds the chart roles and the desk layout. Mock: `docs/design/mocks/charts-desk.html` (`?screen=workspace|auction|screener`, `?theme=dark`).

### 8.1 Direction

The chart is a specimen sheet, not a terminal. White pane, hairline grid, numbered panes (`01 NIFTY 5m`), Martian Mono on every number. Colour carries one of six jobs: direction, option side, magnet level, auction structure, uncertainty, and the evidence grade. No other colour appears on a pane. Panels never stack chrome on chrome: one hairline per edge, no boxes inside boxes.

### 8.2 Chart role tokens

Text tokens clear 4.5:1 on ground and raised; `-mark` tokens clear 3:1 and are for lines, bodies, bars and outlines only. Dark marks equal dark text. Ratios computed 2026-11-14 with the WCAG 2.x formula (`ground / raised`).

| Role | Token | Light text | Light mark | Dark | Light text ratio | Light mark ratio | Dark ratio |
|---|---|---|---|---|---|---|---|
| Up, buy, +delta, bid | `--c-up` | `#107A3A` | `#1E9A4A` | `#49C27A` | 5.43 / 4.93 | 3.64 / 3.30 | 8.37 / 7.64 |
| Down, sell, −delta, ask | `--c-down` | `#BF3D12` | `#E0501C` | `#F5805A` | 5.40 / 4.90 | 3.94 / 3.57 | 7.32 / 6.69 |
| Call OI, call wall | `--c-call` | `#0F7B7A` | `#149892` | `#3DBDB9` | 5.08 / 4.61 | 3.54 / 3.21 | 8.28 / 7.56 |
| Put OI, put wall | `--c-put` | `#B8206F` | `#D42E7E` | `#EE6CAB` | 6.04 / 5.49 | 4.68 / 4.24 | 6.64 / 6.07 |
| Magnet: POC, max pain, naked POC, value area | `--c-magnet` | `#956208` | `#B97D0C` | `#E3AC3C` | 5.21 / 4.73 | 3.50 / 3.18 | 9.23 / 8.43 |
| Auction structure: IB, HVN, LVN, single prints | `--c-auction` | `#5A6B0E` | `#738A12` | `#B3C94A` | 5.93 / 5.38 | 3.91 / 3.55 | 10.25 / 9.37 |
| Uncertainty: cone, VWAP bands, replay future | `--c-band` | `#636E7A` | `#808D9B` | `#98A2AE` | 5.20 / 4.72 | 3.39 / 3.07 | 7.32 / 6.68 |
| Price reference: VWAP, crosshair tag, last price | `--ink` | as §1 | | | | | |

The up, call, put and magnet values reuse the monsoon, gilts, intl and gold values, so the desk ships no new chromatic except `--c-auction` (moss). On a chart pane these names win: green means up there, not "expansion".

Liquidity heatmap ramp `--heat-1…6` (single hue, ochre, lightness carries the value):

| Step | Light | ratio on ground | Dark | ratio on ground |
|---|---|---|---|---|
| 1 | `#FBF1D9` | 1.12 | `#2A2210` | 1.20 |
| 2 | `#F0D58E` | 1.44 | `#4E3A12` | 1.75 |
| 3 | `#D9A73A` | 2.20 | `#80601A` | 3.25 |
| 4 | `#B0740F` | 3.92 | `#B88A28` | 6.05 |
| 5 | `#7A4708` | 7.69 | `#E3B84C` | 10.12 |
| 6 | `#3F2304` | 14.45 | `#FBE7A6` | 15.40 |

Steps 1–3 are below 3:1 on purpose: thin liquidity should recede. The heatmap always shows its numeric legend, and focus on a cell shows the size in lots.

### 8.3 The non-colour cue for every role

Tags shorten on narrow panes and never drop: a tag is the non-colour cue, so a pane without it fails this table. Every tag carries a plain-words definition on hover and focus. Text never uses `--ink-faint` (3.71:1 light, 4.22:1 dark); it is for ticks and rules only.

Up and down marks have almost equal luminance (1.08:1 light, 1.14:1 dark), so a red-green colour-blind reader cannot split them by hue. The shape cue is required, not decoration.

| Element | Colour | Cue that survives greyscale |
|---|---|---|
| Up candle | `--c-up` mark | hollow body, 1.5px outline |
| Down candle | `--c-down` mark | filled body |
| Volume bar | direction mark at 45% | sits under its candle, so it inherits the candle cue |
| Call OI bar on the price axis | `--c-call` mark | grows right from the strike; lane header `C` |
| Put OI bar | `--c-put` mark | grows left from the strike; lane header `P` |
| Call wall | `--c-call` mark, 3px solid line | tag `CALL WALL 24,450` (`CW` under 380px pane width) |
| Put wall | `--c-put` mark, double 1.5px line, 4px apart | tag `PUT WALL 24,100` (`PW` under 380px); the two walls differ in stroke, not only hue |
| Max pain | `--c-magnet` mark | dashed 6-4 line, tag `MAX PAIN` (`MP` under 380px) |
| POC | `--c-magnet` mark | solid 2px, tag `POC` |
| Naked POC | `--c-magnet` mark | dotted 2-3, runs right to the price axis, tag `nPOC` with its date |
| Value area | `--c-magnet` at 10% fill | VAH and VAL 1px edges, tags `VAH` `VAL` |
| Initial balance | `--c-auction` mark | 2px bracket left of the profile, tag `IB` |
| HVN / LVN | `--c-auction` | filled ◆ `HVN`, open ◇ `LVN` at the price axis |
| Single prints | `--c-auction` at 14% fill | 45° hatch behind the letters, tag `SP` |
| TPO letters | `--ink-dim`, IB letters `--c-auction` | the letter itself is the period |
| Implied range cone | `--c-band` 8% (1σ) and 4% (2σ) | dashed edges, tags `1σ 68%` `2σ 95%` |
| VWAP | `--ink` 1.5px | tag `VWAP`; bands `--c-band` dashed 1σ, dotted 2σ |
| Footprint cell | direction text | bid × ask numbers in the cell; imbalance cell gets 1.5px outline and 500 weight (Martian Mono ships 400 and 500) |
| Stacked imbalance (3+) | direction mark | bracket on the cell column, tag `STACK 3` |
| Delta, cumulative delta | direction text | sign always printed (`+1,240`, `−860`) |
| Payoff curve | `--ink` 2px | profit area `--c-up` 10%, loss area `--c-down` 10%, words `max gain` `max loss` at the extremes, `BE` ticks at breakevens |
| DOM bid / ask size | direction text | bid column left, ask column right, headers `BID` `ASK` |
| Staged order | `--ink` | dashed 1.5px row outline, word `STAGED`; confirmed rows are solid with the order id |
| Replay | `--c-band` hatch over the future, ink 2px frame | banner `REPLAY · 14 NOV 10:32 IST` and the clock in mono; live panes never show the hatch |
| Rail card type | role swatch 8×8 | type word (`POSITIONING`, `STRUCTURE`, `FLOW`, `REGIME`) and the evidence stamp |

### 8.4 Desk layout

- Grid: rail 64px left (keyboard-first dock, numbered), chart workspace, insight rail 360px right. Bottom: 40px timeline strip that becomes the replay scrubber.
- Workspace slots 1, 2, 4, 6, 9 or 16. Each pane head: index (`01`), symbol, interval, last price, change with sign, the pane's active overlays as text toggles. 32px tall, hairline below.
- Below 1024 the insight rail becomes a bottom sheet whose whole 56px head is the open button and shows the newest insight's title, so evidence never disappears; below 768 the workspace shows one pane, a 48px pane-switcher row (`01/04 NIFTY 50`) and an `/ Ask` button in the top bar. 375 shows one chart, the ladder collapses into the price-axis bars only, and the strategy builder opens full-screen.
- Order entry on the DOM is two steps: click a price to stage (dashed `STAGED` row), press `Enter` or the `Confirm order` button to send. `Esc` clears. Nothing sends on one click.
- Keyboard: `1–9` focus a pane, `R` rail, `/` command, `Space` replay play/pause, `[` `]` step a bar in replay. Desk screens are `⌥1–⌥4` in the dock, so dock numbers never collide with pane numbers. Replay shows its keys in the strip and a `Back to live` button.
- Controls: 32px tall on a fine pointer at ≥1024 (WCAG 2.5.8 asks for 24px); `pointer: coarse` restores 48px. This is the one desk exception to §3's 48px target.
- One fixture: every pane, wall, tag and rail fact reads the same engine numbers. A screen never shows two spot prices.
- Orders: the DOM head and the staged ticket name the contract, expiry, quantity and product (`NIFTY 27 NOV FUT · BUY 2 lots (150 qty) @ 24,311.00 LMT · NRML`) and the broker link state.

### 8.5 Not on a chart pane

three.js, HyperFrames, gradients, glow, shadow, animated numbers, tooltips that follow the cursor (the crosshair tag sits on the axis), legends inside the plot area, rounded candle bodies, red and green as the only up/down signal.
