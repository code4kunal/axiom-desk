# Landing palette v2: white ground, colour as data

Status: approved 2026-11-13 ("Approve, build it"), after the ruling: white ground, different colours on white, best fonts, maybe larger; no pink paper. Replaces the colour, type and hero-object sections of `DESIGN.md`. Pin mechanics (`landing-hero-pin-spec.md`: CSS sticky, 4 caption docks, states 0/40/70/100) are kept unchanged. Mock: `docs/design/mocks/landing-v2-hero.html`. Screenshots: `docs/design/mocks/{375,768,1280}-{light,dark}-{0,40}.png` plus `1280-light-70.png`. Revised 2026-11-13 after the impeccable critique (eight fixes applied).

## 1. Direction

White ground, black ink, black primary button. Every chromatic colour on the page is data and means one thing: a regime, a diversifying asset class, or an evidence grade. Equity is ink: colour marks only what diversifies the basket, so the ring visibly gains colour as it reweights. The hero object is the basket itself, drawn as 6,500 points on the white, the regime word in its hole and the regime reading on its rim. Nothing is framed, nothing glows, nothing is a gradient. The page looks like a well-set broadsheet with one live instrument on it.

Counter-proposal, one paragraph: white is right for this audience and for sharing cards, so the mock is white first. If anything, the page sections 02 to 08 should alternate between `--ground` and `--raised` (white and `#F2F4F7`) so specimen cards sit on a plane without hairlines doing all the work; the hero stays on pure white. I do not recommend a dark default: dark reads as terminal cosplay to the mass public and halves the legibility of coloured text on mid-range LCDs.

## 2. Tokens

Same names as `DESIGN.md`; `--brass*` keeps its role (action and link colour) and now resolves to ink, so the swap is mechanical. New names for basket, grades and graphic marks.

Rule: the base token is for text (4.5:1 or better on ground and raised). The `-mark` token is for graphics only (points, swatches, 3px legend bars, stamp outlines; 3:1 or better). Dark theme needs no separate marks: its data colours already clear 6:1, so each `-mark` equals its base.

| Token | Light | on ground / raised | Dark | on ground / raised | Job |
|---|---|---|---|---|---|
| `--ground` | `#FFFFFF` | | `#0E1114` | | page |
| `--raised` | `#F2F4F7` | | `#171B20` | | cards, hedge card, sections that alternate |
| `--hairline` | `#D7DCE2` | 1.38 / 1.25 | `#2B313A` | 1.45 / 1.32 | 1px rules only, never a control border that must be seen |
| `--ink` | `#0E1319` | 18.65 / 16.93 | `#F1F3F5` | 17.02 / 15.55 | text, wordmark, needle |
| `--ink-dim` | `#4E5966` | 7.13 / 6.47 | `#A7AFB9` | 8.54 / 7.80 | subline, captions, nav at rest |
| `--ink-faint` | `#7B8692` | 3.71 / 3.36 | `#6E7884` | 4.22 / 3.86 | rim at rest, ticks, inactive marks; never text |
| `--brass` | `#0E1319` | 18.65 / 16.93 | `#F1F3F5` | 17.02 / 15.55 | links (underlined), active nav |
| `--brass-mark` | `#0E1319` | 18.65 | `#F1F3F5` | 17.02 | primary button fill, nav underline |
| `--brass-line` | `#0E1319` | 18.65 / 16.93 | `#F1F3F5` | 17.02 / 15.55 | focus ring: `outline:2px solid var(--ink); outline-offset:2px; box-shadow:0 0 0 4px var(--ground)` |
| `--on-brass` | `#FFFFFF` | 18.65 on button | `#0E1114` | 17.02 on button | button text |
| `--monsoon` | `#107A3A` | 5.43 / 4.93 | `#49C27A` | 8.37 / 7.64 | the word EXPANSION only (hole and rail), CNF stamp text |
| `--monsoon-mark` | `#1E9A4A` | 3.64 / 3.30 | `#49C27A` | 8.37 | CNF outline only; never on the ring |
| `--geru` | `#BF3D12` | 5.40 / 4.90 | `#F5805A` | 7.32 / 6.69 | regime DETERIORATION text, WL text when a word is present |
| `--geru-mark` | `#E0501C` | 3.94 / 3.57 | `#F5805A` | 7.32 | rim points after the sweep, the i-tick in the wordmark |
| `--equity` | `#0E1319` (= ink) | 18.65 / 16.93 | `#F1F3F5` (= ink) | 17.02 / 15.55 | equity text |
| `--equity-mark` | `#0E1319` | 18.65 | `#F1F3F5` | 17.02 | equity points, legend bar |
| `--gilts` | `#0F7B7A` | 5.08 / 4.61 | `#3DBDB9` | 8.28 / 7.56 | gilts text |
| `--gilts-mark` | `#149892` | 3.54 / 3.21 | `#3DBDB9` | 8.28 | gilts points |
| `--gold` | `#956208` | 5.21 / 4.73 | `#E3AC3C` | 9.23 / 8.43 | gold text, RAC stamp text |
| `--gold-mark` | `#B97D0C` | 3.50 / 3.18 | `#E3AC3C` | 9.23 | gold points, RAC outline |
| `--cash` | `#636E7A` | 5.20 / 4.72 | `#98A2AE` | 7.32 / 6.68 | cash text, WL stamp text |
| `--cash-mark` | `#808D9B` | 3.39 / 3.07 | `#98A2AE` | 7.32 | cash points, WL outline |
| `--intl` | `#B8206F` | 6.04 / 5.49 | `#EE6CAB` | 6.64 / 6.07 | international text |
| `--intl-mark` | `#D42E7E` | 4.68 / 4.24 | `#EE6CAB` | 6.64 | international points |
| `--cnf` / `--rac` / `--wl` | alias `--monsoon` / `--gold` / `--cash` | | same | | evidence grades, always with the word |

Ratios computed with the WCAG 2.x relative-luminance formula (script run 2026-11-13; equity and brass-line now share ink's ratios). Every text token clears 4.5:1 on both ground and raised in both themes; every `-mark` clears 3:1. Purple, indigo and blue absent. No gradient anywhere. Colour-blind safety: the regime change shows in shape (the rim frays, the needle sweeps, the word changes) as well as hue.

Why these hues: ink for equity (the base of every Indian portfolio, so it carries no signal), teal for gilts (sovereign, cooler than equity, never confused with green), ochre-gold for gold (literal), grey for cash (no signal), rose for international (the only warm chromatic that is neither geru nor gold). Regime stays monsoon green and geru red-ochre from the Yantra direction: monsoon appears only in the word EXPANSION; geru appears in the word, on the rim after the sweep, and as the wordmark's i-tick. Never as fills.

## 3. Type

All three on Google Fonts under OFL. Still banned: Inter, Geist, DM Sans, Fraunces, Space Grotesk.

| Role | Face | Weights | Why |
|---|---|---|---|
| `--font-display` | Eczar (Rosetta, Vaibhav Singh) | 700, 800 | Devanagari and Latin drawn together; sharp, high-contrast, unmistakably Indian at 68px without being a wedding card. |
| `--font-body` | Anek Latin, with Anek Devanagari for Hindi | 400, 500, 600 | Ek Type's variable grotesk, large x-height, wide counters: reads at 18px on a 6.1" 1080p Android. The two Aneks are one family, so Hindi UI needs no second pairing. |
| `--font-mono` | Martian Mono | 400, 500 | kept: numbers, rail, stamps; `tabular-nums`. Latin only (numbers do not need Devanagari). |

Scale (px / line-height / tracking), fluid via `clamp()`; columns are the values at 375 and 1280.

| Step | 375 | 1280 | Face |
|---|---|---|---|
| `statement` | 38 / 1.0 / -0.02em | 68 / 1.0 / -0.02em | Eczar 700 |
| `regime-word` (in the hole) | 22 / 1.0 / -0.01em | 34 / 1.0 / -0.01em | Eczar 700, `clamp(22px,3vw,34px)` |
| `section-head` | 32 / 1.05 / -0.015em | 52 / 1.02 / -0.02em | Eczar 700 |
| `wordmark` | 22 / 1 / -0.03em | 24 / 1 / -0.03em | Eczar 800 |
| `subline` | 18 / 1.45 | 21 / 1.45 | Anek Latin 400 |
| `body` | 18 / 1.55 | 20 / 1.55 | Anek Latin 400 |
| `ui` | 17 / 1.2 | 17 / 1.2 | Anek Latin 500 (buttons 52px tall) |
| `small` | 15 / 1.5 | 15 / 1.5 | Anek Latin 400 |
| `legend-number` | 20 / 1 | 22 / 1 | Martian Mono 500, tabular |
| `caption` (rail) | 13 / 1.4 / +0.06em | 13 / 1.4 / +0.06em | Martian Mono 400, uppercase |
| `label` | 12 / 1 / +0.10em | 12 / 1 / +0.10em | Martian Mono 500, uppercase |

Floor stays 12px, Martian Mono only. Body goes up two steps from the current 16/18 because the audience reads on a phone at arm's length in daylight.

## 4. Hero object v2: the basket as points

What three.js draws: one `THREE.Points` object (band and rim) plus a needle of two quads and two discs, **five draw calls**. No torus, no tile, no lights. The ring sits directly on the ground. The regime word sits in the hole as DOM over the canvas: Eczar 700 `clamp(22px,3vw,34px)` in `--monsoon` (EXPANSION) or `--geru` (EARLY DETERIORATION), with `CONF 0.74 · N 212` under it in Martian Mono 12px `--ink-dim`.

Populations, one buffer:
- **Band, 6,500 points** (3,800 under 768px): an annulus r 0.62 to 1.0. Each point owns a fixed angle; its class at state A (61/18/9/7/5) and at state B (42/29/17/7/5) are attributes, so the geometry never changes, only colour and a radial lift. Equity points are ink.
- **Rim, 1,000 points** (700 on phones): r 1.075 to 1.10, the regime reading. `--ink-faint` at rest.
- **Needle:** a solid 2px ink line from r 0.30 to 0.60 with a 3.5px hub disc at 0.30, each drawn over a ground-coloured keyline 2px wider, so it never crosses the band and separates from the ink equity points. Its angle is the same uniform the rim sweep uses.

Idle: every point breathes on a sine of `uTime` and its seed (±0.006 world units, about 2px); the group yaws ±2° on a 18-second sine. Nothing is computed on the CPU per point, so idle costs one uniform upload and one draw. Under `prefers-reduced-motion` `uTime` is frozen and the yaw is off; the pointer still answers (not vestibular), and the page still gets the posters per the pin spec.

The hand (verified in the mock with a real pointer): the pointer is unprojected onto the ring's plane each move; the shader pushes points out of a crater of radius 0.30 around it, and the sector under it comes forward (points ×1.55, every other sector drops to 30% alpha); a DOM tag follows the pointer reading `EQUITY · 61%`, and the matching legend cell lights. The whole group tilts up to 9° toward the pointer, lerped at 0.08. Point size 4.2px under 420px wide, 4.8px above; resting alpha 1.0 in light (`uLight`), 0.86 in dark.

Four states, driven by one `progress` uniform set from scroll:
- **0:** needle at rest, rim ink-faint, band at weights A, the word EXPANSION in monsoon. Caption dock 0.
- **40:** needle sweeps 38°; the rim turns geru outward from the needle (`uSweep`) and frays (radial jitter 0.04 to 0.22, doubled from the first draft) within 1.6 rad of it (`uFray`); the word becomes EARLY DETERIORATION in geru; tilt ×1.6. Dock 1.
- **70:** `uMix` 0→1 over scroll 44 to 74: points whose class changes lift 0.14 out of the band, swing 0.08 rad and settle in their new colour, staggered by seed. Legend numbers cut to 42/29/17 at 58. Dock 2.
- **100:** tilt returns to 0, fray calms, rim stays geru. The DOM hedge card (CNF stamp, `HEDGE DRAFT · INDEX PROTECTION · ILLUSTRATIVE`) rises 24px into view at 92. Dock 3.

Budget: 7,500 points × 13 floats = 390 KB of GPU buffers, uploaded once, plus four tiny needle meshes; fragment cost is a disc discard; measured in the mock at DPR 1 under SwiftShader without dropped frames (desktop GPU numbers NOT RUN). Bundle: three.js core for `Points` + `ShaderMaterial` + `WebGLRenderer` tree-shakes below the current torus build because `MeshStandardMaterial`, lights and `TorusGeometry` go; the whole unshaken `three.module.js` is 131 KB gz (`gzip -c | wc -c`, 2026-11-13), already under the 160 KB hero ceiling; the shaken chunk plus ring code is UNVERIFIED until U7 measures it in the browser. The shader is 70 lines. Posters: render states 0/40/70/100 headlessly as before, white and dark.

## 5. Motion

GSAP does exactly one thing: `ScrollTrigger` scrubs the pinned hero (300vh, 200vh under 768px, scrub 0.8) into a single `progress` number that the ring maps onto `uNeedle`, `uSweep`, `uFray`, `uMix` and tilt scale, and toggles the hedge card class at 92. It loads with the hero chunk after `load`, never on first paint, never under reduced motion. Section reveals stay CSS transitions on one IntersectionObserver (KTD6). HyperFrames clips (HTML-rendered, shipped as short MP4/WebM loops with a still poster, never on a chart pane): **03 Charts**, landscape, 6 s: a pattern label appears on one chart pane and its base rate and sample size cells fill in, then a crosshair moves in sync across two panes. **04 Options**, portrait, 6 s: an SSVI surface draws as a hairline mesh and settles arbitrage-free, then one price cell agrees across three screens. **05 Hedge**, no clip: the DOM card is live, the 05 evidence card carries the structure. **06 Agent**, portrait, 8 s: a labelled Axiom cursor works through the desk, each action logging a citation line; the confirm button is never pressed. framer-motion: **no**, every motion on the page is CSS, GSAP or a shader uniform, and 30 KB gz for a reveal we already have fails R20. Remotion: **no**, HyperFrames already renders the clips and the 1200×630 OG still comes from the headless ring render; a second video renderer is a second pipeline to maintain for zero new frames.

## 6. Not stock SaaS, per viewport

- **375:** ring at 280px with the regime word in its hole, then the statement in Eczar at 38px, subline, and the black CTA all inside the first screen (CTA bottom measured at 741px of 844 by Playwright); legend as five hairline cells with 3px colour bars and the rail follow as one block, no stat-card row, no gradient, no pill, no glow.
- **768:** ring capped at 52svh so statement, subline and CTA show on the first screen (CTA bottom 975px of 1024); same order as 375; no three-card grid, no centred hero text, no illustration.
- **1280:** broadsheet split, Eczar statement left at 68px, instrument right with no frame or shadow, legend and rail under it; a black 52px button and an underlined text link; nav is numbered mono anchors, not pills; wordmark without underline, its i-tick in geru.

## 7. Mock and verification

- `docs/design/mocks/landing-v2-hero.html`: self-contained, three@0.186.1 via importmap, theme toggle, scrub slider plus dock buttons (keys 1 to 4), `?theme=dark&state=40` for screenshots, `window.__dbg()` exposes pointer state.
- Screenshots (Playwright, chromium, SwiftShader, DPR 1): `docs/design/mocks/{375,768,1280}-{light,dark}-{0,40}.png` and `docs/design/mocks/1280-light-70.png`. Pointer answer verified with a real `page.mouse.move` at 1280 light (`focus: 0`, equity tag shown) and 1280 dark state 70 (`focus: 1`, gilts). CTA bottom edge measured with `getBoundingClientRect()`: 740.9px at 375×844, 974.5px at 768×1024.
- Layout below 1024: ring, statement, subline, CTA, then legend and rail together; `.scene{width:min(100%,280px)}` under 480px, `min(100%,640px,52svh)` from 480 to 1023, `min(100%,640px)` at 1024 and up.
- UNVERIFIED: Google Fonts shipping of Eczar 700/800, Anek Latin and Anek Devanagari through `next/font/google` (the mock loads them from the Google CSS endpoint and they rendered); tree-shaken three.js chunk size; frame rate on a real mid-range Android.
