# Landing direction: "Yantra"

**Status: APPROVED by the user on 2026-11-13, with all 6 fixes from `landing-direction-critique.md` applied below. Public CTA: "Ask your broker for Axiom" (no form).**

Direction only, no app code. Method: ui-ux-pro-max (design-system, typography, gsap, ux, threejs, google-fonts domains) checked against PRODUCT.md, references/TASTE.md, the 2026-11-13 build prompt and both CLAUDE.md files. The skill's default for "fintech" was navy + green + IBM Plex on an "Enterprise Gateway" pattern: that is the rut, rejected.

## 1. Mechanism, scene, rut

**Mechanism.** Axiom reads the market regime, reweights a basket across what an Indian resident can directly hold, and drafts a hedge before the turn; every number carries its base rate, sample size and out-of-sample proof, or says "insufficient evidence".

**Scene.** A 29-year-old in Indore, 9 pm, ceiling fan on, a Redmi at 40% brightness, 6.5-inch 1080p LCD, Jio 4G at three bars, thumb on the right edge. He came from a broker's WhatsApp link, has Zerodha and Groww installed, was burned once by a tip, and gives the page four seconds. Second reader: a broker's product head on a 1440 laptop in Lower Parel judging white-label fit. Third: the desk.

**The rut.** The category ships a dark terminal with green ticks, a white SaaS page with a gradient hero and three cards, or neon fintech with a floating coin. Its predictable opposite is pastel "calm wealth" with a serif and a plant. The gap: an instrument that measures and shows its working.

## 2. Seven candidate worlds

| # | World | Family | Why / how it looks |
|---|---|---|---|
| 1 | Jantar Mantar, Jaipur | Stone, brass marks | India's own precision instruments. Geru-red plaster, lime white, engraved graduations, hard shadows. Circular yantras map onto the hero ring. |
| 2 | The pink paper | Newsprint | Every investor's morning. Salmon ground, serif columns, hairline rules, small-caps datelines. Serious money without a terminal. |
| 3 | IMD monsoon onset map | Cartographic data graphic | Regimes are seasons; onset isochrones are India's most-read probabilistic chart. Thin contours, dated labels, one moving front. |
| 4 | Bahi-khata / Chopda | Cloth ledger | The honest account book. Red cloth cover, ruled cream pages, hand-set totals, a stamp. |
| 5 | Sarafa brass balance, tola weights | Metal, patina | Evidence is weighed. Dull brass, graduated weights, a needle settling. Gold as instrument, never coin. |
| 6 | Railway reservation chart | Paper, stamp | CNF / RAC / WL: statuses everyone reads instantly. Evidence grades borrow that literacy. Dot-matrix grid, stamp red. |
| 7 | BSE ticker and opening bell | Trading tool (the one allowed) | Familiar, and the Bloomberg rut's front door. Reference for what not to ship. |

## 3. Committed direction: "Yantra"

Worlds 1 + 3 + 6: a stone-and-brass instrument that reads market seasons and stamps each claim with its evidence grade.

**Thesis.** Axiom is an instrument, not a feed. The page shows one instrument reading one season and preparing one basket, then shows its working. Newcomers read the season; the desk reads the base rates underneath. One screen, two depths.

### Colour

Dark is primary (the phone at night). One luminous signal: brass, Fulgurite's role in Axiom's own material (scale marks, the needle). Two state hues, geru for deterioration and monsoon for expansion, always paired with a word or glyph. No purple, indigo or gradient fills. Ground is warm basalt, not blue-black.

| Token | Dark | Light |
|---|---|---|
| ground | `#14100D` basalt | `#F5E6DC` pink paper |
| raised | `#1F1915` | `#FBF1EA` |
| hairline | `#3A322B` | `#C9B3A2` (amended from `#D9C8BB`, 2026-11-13) |
| ink | `#EDE6DA` | `#1C1714` |
| ink-dim | `#A89E90` | `#5C524A` |
| ink-faint (rules only) | `#6E655B` | `#B8A99B` |
| brass | `#E2B457` | marks `#C8963E`, text `#8A5A14` |
| geru | `#D9674A` | `#A63E26` |
| monsoon | `#5FB08A` | `#2E6B4F` |

Contrast, computed: dark ink/ground 15.26, ink-dim/ground 7.17, ink-dim/raised 6.59, brass/ground 9.82, ground-on-brass button 9.82, geru/ground 5.40, monsoon/ground 7.27. Light ink/ground 14.58, ink-dim/ground 6.24, brass-text/ground 4.85, geru/ground 5.16, monsoon/ground 5.17. Light brass marks are 2.18 and dark ink-faint 3.31: marks and hairlines only, never text.

### Typefaces (Google Fonts, OFL)

- **Martel** 700/800 (Dan Reynolds): display. A two-script serif drawn for Devanagari and Latin together, so a Hindi toggle keeps the voice. Heavy weights have the cut of an engraved scale.
- **Hind** 400/500/600 (Indian Type Foundry): body and UI. Humanist sans built for Indian screens at 16px on low-DPR LCDs; Devanagari sibling exists.
- **Martian Mono** 400/500 (Evil Martians): every number, evidence cell and regime label. Tabular; subset to digits, punctuation and capitals.

Wordmark: "Axiom" in Martel 800, tracking -0.03em, the dot of the i replaced by a 2 px × 0.34 em brass tick (amended from 2 × 10 px on 2026-11-13: 10 px touched the stem).

### First viewport

**1440.** Left 55%: wordmark 24px; statement in Martel 800 at 88px, line-height 0.98, two lines (amended 2026-11-13: the approved statement runs about six lines at this size; the user kept the copy and the layout is sized for it); one Hind line at 20px; primary button "See how it reads a market" (ink on brass) with a ghost link "For brokers". Right 45%: the ring at 620px resting at Expansion, Martian Mono caption rail beneath: `REGIME EXPANSION · CONF 0.74 · N 212 · ILLUSTRATIVE`. Bottom: hairline with section index `01 Season 02 Basket 03 Hedge 04 Evidence`.

**390.** Wordmark 20px. Ring first, 300px, poster-first so it paints at once. Statement at 40px (amended 2026-11-13: runs about seven lines; copy kept, primary button still inside the first 844px). Hind line 17px. Primary button full-width, 52px, inside the first 844px. Caption rail in two 12px lines.

Statement: **"Markets have seasons. Axiom reads the season, reweights the basket, and shows its evidence."** Subline: **"A research instrument for Indian investors. It drafts; a human confirms every order."**

### Hero 3D object

- **Geometry.** Graduated ring, outer radius 1.0, tube 0.085, 96 segments; 360 tick marks as one `InstancedMesh`; inside, a 6-arc annulus (large-cap, mid/small-cap, gilts, gold, cash, international via LRS) from `RingGeometry`; one thin needle. Under 25k triangles.
- **Materials.** Ring `MeshStandardMaterial` `#2A221C`, roughness 0.7, metalness 0.15. Ticks and needle brass, roughness 0.35, metalness 0.8, emissive 0.3 so they read on dim LCDs. Arcs unlit ink-dim, active arc brass. One directional plus one hemisphere light. No environment map, bloom or post-processing.
- **Scroll** (GSAP ScrollTrigger, pinned 300vh, scrub 0.8). 0%: needle at Expansion, caption `EXPANSION · CONF 0.74`. 40%: needle sweeps 38°, ring tilts 12°, ticks near the needle turn geru, caption `EARLY DETERIORATION · CONF 0.68 · N 212`. 70%: arcs reweight in place, caption `EQUITY 61 → 42 · GILTS 18 → 29 · GOLD 9 → 17`. 100%: ring settles flat; a DOM hedge card slides from its edge: `HEDGE DRAFT · INDEX PROTECTION · ILLUSTRATIVE · a human confirms every order` (no named instrument in the hero; the structure appears only on the 05 evidence card). On screens under 768px the pin is capped at 200vh and the section index stays visible so the visitor can skip it. `ILLUSTRATIVE` stays in the rail at every frame.
- **Pointer.** Ring tilts up to 6° toward the pointer, lerp 0.12 s; ticks within 20° brighten. Touch ignored; scroll owns the object.
- **Poster.** AVIF with WebP fallback per theme, 1200 × 1200, the 0% state, the LCP element with `fetchpriority="high"`. The canvas fades over it and the poster never unmounts, so WebGL failure needs no second path.
- **Reduced motion.** No pin, no scrub: four static posters (0/40/70/100) as normal sections with the same captions.

### Scroll storyboard (copy, 25 words or fewer each)

01 **Hero.** Above.

Two depths in every section: a plain Hind line for the newcomer, then a Martian Mono caption for the desk.

02 **Problem.** "Equity-only tools go quiet when the season turns. By the time they flag the turn, prices have already fallen." A flat chart greys while the needle keeps reading.

03 **Charts.** "Every pattern on the chart tells you how often it has worked before, or says it can't tell yet." Caption: `BASE RATE · SAMPLE SIZE · UP TO 8 SYNCED CHARTS`. HyperFrames clip: a pattern stamping its evidence grade.

04 **Options and Vol Lab.** "Every options price comes from one consistent model, so the numbers agree everywhere." Caption: `ONE ARBITRAGE-FREE SURFACE · SSVI`. Clip: the surface turning once, a chain reading from it.

05 **Hedge.** "When regime confidence shifts, Axiom drafts the hedge. It never places an order; a human confirms each one." The hero's hedge card, now with its evidence grid.

06 **Cited agent.** "Ask what changed since yesterday's close. The agent answers with citations to the same numbers the screens show." Clip: the answer assembling with footnotes.

07 **Evidence standard.** "Every claim shows its base rate, sample size and out-of-sample result. When it can't show all three, it says so: insufficient evidence." A specimen card in hairline cells: `BASE RATE 0.58 · N 212 · OOS 0.54 · AS OF 2026-11-13 · ILLUSTRATIVE`. Grades as stamp outlines: **CNF** out-of-sample confirmed, **RAC** in-sample only, **WL** insufficient evidence.

08 **Brokers.** "White-label Axiom for your clients. Your SEBI-registered analysts author every basket and call. Talk to the desk." Brass button "Talk to the desk". For the public, a plain line under it: "Investing with a broker? Ask them for Axiom." No form, no trading sign-up, no pricing.

09 **Footer.** Wordmark, "Research tool. Not investment advice. No performance is promised.", section index, theme toggle.

### Motion grammar

- Scroll-tied: scrub, no easing.
- Reveals: `cubic-bezier(0.2, 0.7, 0.2, 1)`, 480 ms, 16px rise plus opacity; exits 200 ms; stagger 60 ms, max five items.
- Needle and tilt: 0.12 s lerp, never spring. Theme switch 160 ms, colour only.
- Never animates: body text, numbers (they cut, never count up), hairlines, wordmark, button labels; under reduced motion only opacity.
- Banned: hover lift, shadow growth, gradient sweeps, parallax beyond the ring.

### HyperFrames and 21st.dev

HyperFrames: three clips (03, 04, 06), 6 to 8 s, muted, `loop playsinline`, poster frame, play in view and pause off-screen, visible 48px pause control, captions as DOM text. Rendered 720 × 900 and 1200 × 760. None in the hero or on chart panes.

21st.dev: theme menu, broker dialog, mobile nav sheet only. Restyled to tokens: hairline borders, no shadow, radius 4px max, Hind labels.

### Performance budget

- LCP under 2.5 s on throttled 4G mid-tier Android: the poster AVIF (target 45 KB) is the LCP element, preloaded. Fonts: Martel 800 latin, Hind 400/500 latin, Martian Mono digits-only unicode-range; `font-display: optional` for display, `swap` for body. Critical CSS inline.
- First-paint JS under 90 KB gz (Next.js runtime + Motion). GSAP + ScrollTrigger (about 30 KB gz) via `next/dynamic` when the hero enters view. three.js plus ring module (target under 160 KB gz) only when WebGL2 is available, reduced motion is off, `deviceMemory` is 4 or more or unknown, and `saveData` is false; otherwise the poster path is final. Full-page ceiling 320 KB gz.
- Three.js: one canvas, `powerPreference: "low-power"`, DPR capped at 1.5, render only while in view and scroll changed, dispose on route change. CLS under 0.05 via fixed aspect boxes.

### Accessibility

Ratios above; ink-faint and brass marks never carry text. Ring is `aria-hidden`; a live region in the caption rail speaks the 40/70/100 copy. Section index is a real nav; the pin never traps focus. Targets 48px, 8px apart. States carry a word and a glyph (needle angle, stamp outline) beyond geru/monsoon. Focus ring 2px brass, 2px offset, never removed. `lang="en-IN"`, no idiom.

### Not stock SaaS, not Bloomberg, not crypto

- SaaS: no gradient, card row, logo strip, purple or Inter; a scroll-driven instrument over a numbered specimen sheet on hairlines.
- Bloomberg: under 20 numbers on the page, each ILLUSTRATIVE; warm basalt, no ticker, no orange, no quote grid; the newcomer path is one sentence about seasons.
- Crypto: no coin, no glow beyond 0.3 emissive on brass, no countdown, no rocket; "before" is the only urgency word.
- The likes: no violet, particles, cream-with-vermilion or agent cursors; only the pointer-aware object, telemetry grid and numbered sections are borrowed.

### Calibration guard

The second voice is what keeps basalt plus brass out of the "near-black with one glow" cluster: geru and monsoon as real state colours, railway stamp outlines, and pink paper in light mode. None of them may be dropped in the build.

### Risk

A pinned 300vh three.js hero can still drop frames and heat a Redmi; if the U2 build cannot hold 50 fps at DPR 1.5 on a mid-tier device, the ring goes four-poster on all phones and 3D stays desktop-only. Secondary: pink-paper light mode may read "newspaper" rather than "instrument"; test with three brokers first.

## Alternates

**A. Pink Paper.** World 2 alone. Salmon ground, Newsreader 700 display, columns and datelines; a folding broadsheet reveals the basket instead of the ring. No three.js, instantly Indian, weaker on "instrument"; brokers may read it as media.

**B. Chopda.** Worlds 4 + 5. Red-cloth ledger dark theme (`#2B0F0D`), a brass balance weighing equity against gilts and gold, evidence as stamped tallies. Strongest honesty story; risks festival kitsch and heavier materials.

## 4. Libraries named

- `three`: `MeshStandardMaterial`, `RingGeometry`, `InstancedMesh`, `HemisphereLight` from memory; version and APIs UNVERIFIED (nothing installed in this repo; skill dataset cites 0.185.1).
- `gsap` with `gsap/ScrollTrigger`: `scrub`, `pin`, `matchMedia` UNVERIFIED.
- `motion`: UNVERIFIED. `next`: `next/dynamic`, `next/image` UNVERIFIED (dataset cites 16.2).
- HyperFrames: package name and API UNVERIFIED. 21st.dev: component source UNVERIFIED.
- Martel, Hind, Martian Mono: present in the skill's google-fonts dataset as OFL; live availability not fetched.
