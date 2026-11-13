# Axiom DESIGN.md

**Provisional: written from the approved direction before the build; rewritten from the shipped build at the end of the landing plan.**

Source of truth until then: `docs/design/landing-direction.md` ("Yantra", approved 2026-11-13). This file only names tokens and rules; it does not redesign. Scope: `apps/desk` landing page (U2–U7). Desk screens get their own pass after G5.

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
