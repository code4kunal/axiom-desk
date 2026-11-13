# Axiom DESIGN.md

**Provisional: written from the approved direction before the build; rewritten from the shipped build at the end of the landing plan.**

Source of truth until then: `docs/design/landing-direction.md` ("Yantra", approved 2026-11-13). This file only names tokens and rules; it does not redesign. Scope: `apps/desk` landing page (U2–U7). Desk screens get their own pass after G5.

## 1. Colour tokens

CSS custom properties on `:root[data-theme]`. Dark is primary. Hex values are the direction's Colour table, verbatim.

| Token | Dark | Light | Role |
|---|---|---|---|
| `--ground` | `#14100D` | `#F5E6DC` | page background (basalt / pink paper) |
| `--raised` | `#1F1915` | `#FBF1EA` | cards, dialogs, sheets, specimen cells |
| `--hairline` | `#3A322B` | `#D9C8BB` | 1px rules, borders, cell dividers |
| `--ink` | `#EDE6DA` | `#1C1714` | primary text, wordmark |
| `--ink-dim` | `#A89E90` | `#5C524A` | secondary text, captions, nav items at rest |
| `--ink-faint` | `#6E655B` | `#B8A99B` | tick marks, inactive arcs, decorative rules only |
| `--brass` | `#E2B457` | `#8A5A14` | brass as **text**: links, active nav item, RAC label |
| `--brass-mark` | `#E2B457` | `#C8963E` | brass as **decorative mark**: i-tick, needle, scale ticks, button fill, current-nav underline |
| `--brass-line` | `#E2B457` | `#8A5A14` | brass as **functional line** that must meet 3:1: focus ring, RAC stamp outline |
| `--geru` | `#D9674A` | `#A63E26` | deterioration state, WL stamp; always with a word or glyph |
| `--monsoon` | `#5FB08A` | `#2E6B4F` | expansion state, CNF stamp; always with a word or glyph |
| `--on-brass` | `#14100D` | `#14100D` | text on a brass-mark button (dark ink in both themes) |

Why three brass tokens: in light mode brass marks (`#C8963E`) are 2.18:1 on pink paper, under the 4.5 text floor and under the 3:1 WCAG 2.2 floor for focus indicators. So `--brass` is text-safe, `--brass-line` is the same hex as `--brass` and carries only lines that must be perceivable (focus, stamp outlines), and `--brass-mark` is decorative only. In dark mode all three resolve to `#E2B457`.

**Contrast rules (direction figures, plus the three computed here with the WCAG relative-luminance formula).**
- May carry text: `--ink` (15.26 / 14.58), `--ink-dim` (7.17 dark on ground, 6.59 on raised; 6.24 light), `--brass` (9.82 / 4.85 on ground, 5.31 on light raised), `--geru` (5.40 / 5.16; 4.96 dark on raised), `--monsoon` (7.27 / 5.17), `--on-brass` on `--brass-mark` button fill (9.82 dark / 7.11 light).
- Never carry text: `--ink-faint` (3.31 dark), `--brass-mark` in light (2.18), `--hairline`.
- Non-text lines that must be perceived (focus ring, stamp outlines) use `--brass-line`, `--geru`, `--monsoon`: all ≥ 3:1 on both grounds. `--brass-mark` lines are decoration only.
- Minimum text size on `--geru` / `--monsoon` / light `--brass`: 14px Hind 500 or 12px Martian Mono 500 (ratios are above 4.5 but under 7).
- No colour outside this table anywhere in `apps/desk`. No alpha tints except `--hairline` at 100%; disabled = `--ink-dim`, not opacity.

## 2. Type

Self-hosted via `next/font/google`, latin subset (KTD10). `font-display: optional` for Martel, `swap` for Hind and Martian Mono.

| Token | Family | Weights | Use |
|---|---|---|---|
| `--font-display` | Martel | 700, 800 | statement, section heads, wordmark, 404 and legal h1 |
| `--font-body` | Hind | 400, 500, 600 | body, buttons, nav sheet labels, legal body |
| `--font-mono` | Martian Mono | 400, 500 | every number, caption rail, evidence cells, stamps, nav anchors, ordinals |

Scale (px / line-height / tracking). Fluid between 390 and 1440 via `clamp()`; the two columns are the clamp ends.

| Step | 390 | 1440 | Face |
|---|---|---|---|
| `statement` | 40 / 0.98 / -0.02em | 88 / 0.98 / -0.03em | Martel 800 |
| `section-head` | 30 / 1.05 / -0.015em | 52 / 1.02 / -0.02em | Martel 700 |
| `legal-h1` | 30 / 1.1 / -0.01em | 40 / 1.1 / -0.015em | Martel 700 |
| `subline` | 17 / 1.45 | 20 / 1.45 | Hind 400 |
| `body` | 16 / 1.55 | 18 / 1.55 | Hind 400 |
| `legal-body` | 16 / 1.65 | 17 / 1.65, measure 64ch | Hind 400 |
| `ui` | 16 / 1.2 | 16 / 1.2 | Hind 500 (buttons, sheet items) |
| `small` | 14 / 1.5 | 14 / 1.5 | Hind 400 (footer body, disclaimer, legal notice body) |
| `caption` | 12 / 1.4 / +0.06em | 13 / 1.4 / +0.06em | Martian Mono 400, uppercase |
| `label` | 12 / 1 / +0.10em | 12 / 1 / +0.10em | Martian Mono 500, uppercase (nav anchors, stamps, ordinals) |

- Wordmark: "Axiom", Martel 800, 20px at 390, 24px at 1440, tracking -0.03em; the i's dot is a 2×10px rectangle in `--brass-mark` (rotated 0°, sits on the x-height). Never animates.
- Numbers: Martian Mono only, `font-variant-numeric: tabular-nums`. They cut, never count up.
- Floor: nothing under 12px; 12px only in Martian Mono 500 uppercase.

## 3. Space, shape, surface

- Spacing scale (px): `4 8 12 16 24 32 48 64 96 128`. Tokens `--s-1 … --s-10` in that order.
- Section rhythm: 96 top/bottom at 390, 128 at 1440. Inside a card: 16 at 390, 24 at 1440.
- Gutters: 16 at 375, 32 at 768, 48 at 1280+. Content max 1280px, centred.
- Radius: `--r-1: 2px` (stamps, cells), `--r-2: 4px` (buttons, cards, dialogs, sheets). **Ceiling 4px.** No pills, no circles except the ring.
- Shadows: none. Elevation is `--raised` over `--ground` plus a `--hairline` border. No `box-shadow`, no `backdrop-filter`, no blur.
- Hairline rules: `1px solid var(--hairline)`; at DPR ≥ 2 keep 1px (never 0.5px, mid-range LCDs drop it). Section dividers run full content width; cell dividers inside specimen cards are hairline on all four sides, cells butt (`border-collapse`-style, no double rules).
- Buttons: 48px tall minimum (52px full-width on the hero at 390), padding 0 24px, radius 4px, Hind 500 16px. Primary: fill `--brass-mark`, text `--on-brass`. Ghost: 1px `--hairline` border, text `--ink`, hover border `--ink-dim` (colour only). No lift, no shadow, no scale.
- Links in body: `--brass` text, underline 1px offset 3px; hover switches underline colour to `--ink` (colour only).
- Targets: 48×48 minimum, 8px clear on every side. Icon-only controls carry a visible or `aria-label` word.
- Focus: `outline: 2px solid var(--brass-line); outline-offset: 2px; border-radius: inherit`. Never removed, never replaced by a box-shadow. The 2px offset puts the ring on `--ground`, so it stays visible on a brass button too.

## 4. Stamps (evidence grades)

Outline stamps, never filled. Martian Mono 500 12px uppercase, tracking 0.12em, padding 2px 6px, `border: 1.5px solid`, radius 2px, no rotation, no texture.

| Grade | Meaning | Outline | Text |
|---|---|---|---|
| `CNF` | out-of-sample confirmed | `--monsoon` | `--monsoon` |
| `RAC` | in-sample only | `--brass-line` | `--brass` |
| `WL` | insufficient evidence | `--geru` | `--geru` |

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

Both themes must keep the second voice or the build has drifted: `--geru` and `--monsoon` as real state colours on the page, the CNF / RAC / WL outline stamps, and pink paper (`#F5E6DC`) as the light ground. Brass alone on basalt is the "near-black with one glow" cluster; it is not this design.
