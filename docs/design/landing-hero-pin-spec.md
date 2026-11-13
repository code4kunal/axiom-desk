# Landing hero pin spec (U4, `html[data-hero=pin]`)

Scope: the pinned layout only. Copy, ring, posters, motion grammar and a11y are `landing-direction.md` § First viewport / § Hero 3D object / § Motion grammar / § Accessibility (authoritative). The stacked DOM in `Hero.tsx` and `landing-sections-spec.md` §2 stays the no-JS / reduced-motion / gate-fail layout. Method: ui-ux-pro-max (`gsap`: pinned scrub needs deterministic height, refresh after fonts; `ux`: no scroll hijack, keyboard skip) against KTD4/5/8, R6–R9, R15, R19 and impeccable's craft floor.

## 0. One mechanism: CSS sticky docks the captions, GSAP only paints the ring

- The box is `section#season` itself: `position: relative; height: var(--box)`; `--box: 300lvh` (`200lvh` below 768). `lvh` so the box never shrinks when a mobile address bar hides (no CLS at the section 02 edge); every sticky `top`/height uses `svh` so the pinned block fits the smallest viewport. `--d: calc(var(--box) - 100svh)` is the scroll distance of the pin; progress p = scrollY / `--d`.
- Nothing is pinned by GSAP. ScrollTrigger runs with `pin: false`, `start: top 48px`, `end: bottom bottom`, `scrub: 0.8`, and scrubs the ring states 0/40/70/100 only. No pin-spacer, no fixed elements, no transform on the section: native hash navigation and back/forward restoration keep working, so KTD5.4's manual scroll restoration is not needed. `ScrollTrigger.refresh()` on orientation change and after fonts load.
- The four captions (0, 40, 70, hedge card) are four sticky siblings in one grid column, all with the same `top: var(--rail-top)` and `background: var(--color-ground)`. Each later one, further down the document, docks into the same slot and covers the one before: a content **cut**, numbers never interpolate. Their approach is scroll-tied (the only motion the grammar allows for scroll). Identical in both paths; with WebGL the ring states are added on top, without WebGL (or after `webglcontextlost`) the poster plus docking captions is the whole experience. R7 costs nothing.
- `scroll.ts` reads each track's dock position (`track.offsetTop − rail-top`) and sets the canvas keyframes there, so the ring always changes state the instant its caption docks. At ≥768 those positions are exactly 0.4·d, 0.7·d, 1.0·d by construction; at 375 they follow the text (see §2).

## 1. DOM: one addition, two `display: contents` moves, rest is restyling

- **Added:** one `<div class="hero-text">` wrapping the `h1` and the subline/buttons `div`. `display: contents` everywhere except ≥768 pin, so stacked output is byte-identical in layout.
- **Moved (CSS only):** the plates `div` (`grid gap-y-10 …`) → `display: contents`, so its three figures become grid items of the ring column. Figure 1 → `display: contents` at every width (it already is below 768), so the poster box and `figcaption` 0 are separate sticky items.
- **Hidden:** the `Poster` of figures 2–4 (`display: none`; their imgs are `loading="lazy"`, so nothing is fetched). Their state is the canvas or, without WebGL, the caption alone over the 0% poster.
- **Restyled:** `section` (box, `padding-top` 16/40/64), `h1` (size at 768 and an svh cap at ≥1024), the poster wrapper (full column width, `background: var(--color-ground)`, the square centred inside at `--plate`), `figcaption` 0/40/70 (sticky rail: `margin-top: 12px → 0`, `border-top: 1px solid var(--color-hairline)`, `padding: 12px 0`, ground background), the hedge `figcaption` (sticky, card unchanged), `#reading` (`scroll-margin-top`).
- **Canvas:** inside figure 1's poster box (`position: relative`), `position: absolute; inset: 0`, `aria-hidden`, opacity 0 → 1 over `480ms var(--ease-reveal)` after the first rendered frame; on context loss opacity → 0 over 200ms and the canvas is removed. The poster `<img>` beneath never unmounts (R6).

Grid of the box (same `.frame` and 4/8/12 columns as stacked). Rows of the ring column, top to bottom: poster · caption 0 · track 40 · track 70 · hedge track. `--rail-top = 48px + padding-top + var(--plate) + 12px`; `--plate` is the ring column's width (768: `calc((100vw − 232px) / 2 + 72px)` = 340 at 768; ≥1024: `calc((min(100vw, 1280px) − 360px) * 5 / 12 + 96px)` = 479 at 1280).

| | 375 (content 343) | 768 (8 cols, 340 each half) | 1280 (12 cols, 76.7) |
|---|---|---|---|
| Box | `200lvh`, pt 16 | `300lvh`, pt 40 | `300lvh`, pt 64 |
| What sticks | poster box and rail only (`top: 64px`, z 2); text scrolls under them | left `hero-text` (cols 1–4) and poster (cols 5–8), both `top: 88px` | `hero-text` cols 1–7 and poster cols 8–12, both `top: 112px` |
| `--plate` | `min(300px, 32svh)` → 270 at 844; 300 only from 938svh up | 340 | 479 |
| `--rail-top` | 342 | 440 | 603 |
| Statement | `statement` step 40px, ~6 lines, in flow after the rail | `section-head` step (≈38px), Martel 800, cols 1–4, ~6 lines (the 57px/8-col stacked size cannot share a viewport with a 340 ring) | `min(var(--text-statement), 9svh)`: 72 at 800 tall (U4 measured 7 lines at 80px, buttons 22px under the fold; 9svh keeps them in) |
| Subline, buttons | subline 17px, 3 lines; primary 52px full width, bottom at ≈ 818 < 844; ghost link under it | subline 3 lines; primary 48 auto; ghost on its own 48 row (the pair is 379px, wider than the column) | as stacked: primary 48 + ghost inline, 24 gap |
| Ring-column rows below the rail | tracks start after the ghost link: `1fr 1fr` then hedge row `calc(100svh − var(--rail-top))` | `calc(.4 * var(--d))`, `calc(.3 * var(--d))`, `calc(.3 * var(--d))`, hedge row `calc(100svh − var(--rail-top))` | same as 768 |
| Caption 40 docks | when the last text line has passed under the rail (≈ p 0.6 at 844) | p 0.40 | p 0.40 (scrollY 640 at 800 tall) |
| Caption 70 / card dock | ≈ 0.8 / 1.0 | 0.70 / 1.00 (card holds 48px, then unpins) | 0.70 / 1.00 |

Row arithmetic: the hedge row equals the viewport space under the rail, so the card's natural top sits exactly `--d` below the rail and docks at p = 1 whatever the viewport. `--d` is in `lvh − svh` terms, so the address bar never moves a dock point.

## 2. Caption rail

- **With WebGL:** the rail shows exactly one caption: 0 until 40 docks, 40 until 70 docks, 70 until the card docks. Docking is a cut (coverage). Nothing fades, slides on its own timer or counts; `ILLUSTRATIVE` is in every caption so it never leaves the rail. The ring sweeps/tilts/reweights on the scrub between docks, its keyframes read from the tracks (§0).
- **Without WebGL / context lost:** the same captions dock over the sticky 0% poster in the same order; the poster never changes. Where they travel: at ≥768 up the ring column, beneath the rail, over empty ground (the text is in the other column, never touched); at 375 they are in flow after "For brokers", so the reading order is ring, rail, statement, subline, buttons, then caption 40 rises and docks under the ring, then 70, then the card. The statement is ahead of them in flow, so no overlap at any scroll position. z-order: poster and caption 0 at 2, tracks at 3 (they cover the rail, never the poster), flowing text at auto, nav rail `z-20` above all.
- Static ordered DOM text, no live region (R19); screen readers meet all four in order at any scroll position.

## 3. Hedge card

- Before p = 1 it is the hedge track's content: in the document at `--rail-top + --d` from the box top, i.e. ordinary offscreen content further down the page, fully opaque, server-rendered. Visible-but-dim is rejected: DESIGN.md allows no alpha, and dimmed Hind under 4.5:1 would fail. R9 holds because the card is DOM text in flow from first paint, not a hidden node.
- At p → 1 it rises from under the ring's bottom edge into the rail slot (the "slides from the ring's edge" of the direction, scrubbed, no easing) and covers caption 70. At ≥768 it holds 48px before the box ends; at 375 it docks at the box end and leaves with the ring as one unit.

## 4. Plates 40/70/100

Hidden in pin mode (§1). Their figures survive as the tracks, so `id="reading"` stays on figure 2 and the DOM order 0 → 40 → 70 → card is the reading order in both layouts.

## 5. End of the box and `#reading`

- The section ends at `--box`; sticky items are released by the box's bottom edge and the hero scrolls off as a block. Section 02 follows with its own padding and rule, untouched. Nothing collapses: the box exists from first paint (head script) and is never resized by JS.
- `#reading` = the caption-40 track. `html` already has `scroll-padding-top: 48px`, so in pin mode `#reading { scroll-margin-top: calc(var(--rail-top) − 48px) }`: the browser lands with the track's top at `--rail-top`, exactly the scroll position where EARLY DETERIORATION docks and the ring reads 40%, on both paths, at every width. The stacked layout keeps `scroll-mt-16`. The ScrollTrigger scrub (0.8) carries the ring to the state after the jump.

## 6. Keyboard, nav, performance

- Focus order: statement → primary → "For brokers" → section 02. The tracks hold no focusables; no `tabindex`, no `overflow: hidden`, no focus management. Tabbing out of the hero scrolls the page past the box natively.
- Below 768 the nav rail (`sticky top-0 z-20 h-12`) stays above the hero's z 2/3; the section creates no stacking context (no `isolation`, `transform`, `z-index` on it or on the box), so INDEX is visible and tappable at p 0/0.4/0.7/1. GSAP writes only to the canvas and the ring's uniforms.
- Layout is set by CSS before paint; the canvas is the only element added after load and it sits in a box that already exists (CLS 0 from the hero). Posters 40/70/100 are never fetched in pin mode, so the 3D path loads one poster plus the two chunks.

## 7. Not stock SaaS

- **375.** An instrument panel pinned at the top of the page while the statement, in a two-script serif, slides under it; three mono readings dock beneath the dial in turn, and the hedge draft arrives as a ruled card, not a toast. No full-screen video hero, no scroll-snap carousel, no dot indicators.
- **768.** A 340px dial pinned beside a six-line Martel column at the same top, one brass button under it; the ring column below the rail is empty ground that the readings climb, not a feature list. No split hero with a product screenshot, no "scroll to explore" chevron.
- **1280.** Statement block and 479px dial at equal top, each pinned for three viewports while the dial's rail cuts through regime → deterioration → reweight → draft; numbers cut, the only slide is the card from the ring's edge. No parallax layers, no counters, no sticky sidebar of bullet points; without WebGL the page reads the same, poster and rail, which no SaaS fallback does.

## 8. Risks

- Stacked and pin layouts differ at 768 (statement step) and 375 (plate ≤ 300). Safe because `data-hero` is set before first paint; only a reduced-motion or gate-fail visitor ever sees stacked, never a switch.
- Viewports under ~780 tall at ≥1024 shrink the statement via `10svh`; 1280×600 (gate minimum) still overflows the text block by ~27px while pinned: the ghost link sits below the fold until the unpin. Accepted; the gate's 600px floor is for phones.
- At 375 the states compress into the last ~40% of the pin (text passes first); the direction's 200vh cap is kept. If the desk wants 40/70 earlier, the only lever is the box height, not the layout.
- A docking caption travels visibly before it docks (scroll-tied). `@container scroll-state(stuck)` could hide the travel later; browser support UNVERIFIED, not required.
- Line counts (6 at 375 and 1280, 6 at 768) are estimates from Martel 800 metrics; measure in U4 screenshots at 375×844, 768×1024, 1280×800, light and dark. `NOT RUN` here.
