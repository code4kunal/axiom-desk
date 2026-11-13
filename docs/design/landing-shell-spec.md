# Landing shell spec (U2)

Scope: layout frame, the one `<nav>`, footer, 404, `/privacy`, `/terms`. Not the hero, not sections 01–09 (U3/U4), not the nav sheet or theme menu UI (U5). Tokens and type steps are `DESIGN.md` names. Requirements: R4, R15 (nav only), R17, R18, R19, R21.

## 1. Frame

| Viewport | Gutter | Columns / gap | Content width |
|---|---|---|---|
| 375 | 16 | 4 / 16 | 343 |
| 768 | 32 | 8 / 24 | 704 |
| 1280 | 48 | 12 / 24 | 1184 (max 1280 at ≥ 1376) |

- `body` background `--ground`, text `--ink`, `lang="en-IN"`, `scroll-padding-top: 48px` (rail height) so anchors land clear of the rail. No `scroll-behavior: smooth` globally: the hero pin owns scroll (KTD5); U4 adds smooth scroll for in-page anchors only when the pin is not active.
- `<a class="skip" href="#season">` first in `<body>`: visually hidden, on focus a 48px `--raised` bar at the top with `--hairline` border, label "Skip to content".
- Landmarks: one `<header>` (wordmark), one `<nav aria-label="Sections">`, `<main>`, one `<footer>`. The nav rail element wraps header + nav so both ride together.
- Nothing in the shell casts a shadow, blurs, or exceeds 4px radius.

## 2. The nav (single `<nav>`, R15)

One sticky top rail, `position: sticky; top: 0; height: 48px; background: var(--ground); border-bottom: 1px solid var(--hairline)`. Present on every route. Inside, left to right: wordmark (Martel 800, brass i-tick, links to `/`), then the anchor list. Ordinals in `label` step, labels in `label` step uppercase.

| # | id | Short label | Lands on |
|---|---|---|---|
| 01 | `season` | Season | hero (statement + ring) |
| 02 | `problem` | Problem | 02 "Equity-only tools go quiet…" |
| 03 | `charts` | Charts | 03 charts + base rates |
| 04 | `options` | Options | 04 one surface |
| 05 | `hedge` | Hedge | 05 hedge draft |
| 06 | `agent` | Agent | 06 cited agent |
| 07 | `evidence` | Evidence | 07 evidence standard |
| 08 | `brokers` | Brokers | 08 brokers + public line |
| 09 | `footer` | Footer | footer |

Anchor markup: `<a href="/#hedge">` (absolute, so the same nav works from `/privacy`, 404, `/terms`). Rendered as `05 HEDGE`: ordinal `--ink-dim` 400, label `--ink-dim` 500 (`--ink-faint` never carries text); the current section's label is `--brass` with a 2px `--brass-mark` underline flush to the rail's bottom hairline. Current section is set by one IntersectionObserver (`aria-current="location"`); until JS runs, nothing is current.

**Desktop (≥ 1024).** All nine anchors inline, right-aligned, 24px apart, each a 48px-tall hit area. The hero's "bottom hairline with section index" from the direction's 1440 first viewport is this rail, not a second list: the hero keeps only its caption rail on that bottom hairline.

**Tablet (768–1023).** Same rail; ordinals hidden, labels only, 16px apart; if the nine labels exceed the row they truncate to the first six plus the trigger below. Measure in U2 at 768 and pick one; do not wrap.

**Mobile (< 768).** The anchor list is hidden (`hidden` attribute until the sheet exists, not `display:none` on the `<nav>` itself, so the landmark stays). Rail shows: wordmark left; right, a 48×48 trigger labelled `INDEX` (Martian Mono 500 12px) preceded by the current ordinal as `02 / 09` in `--ink-dim`. The trigger is a `<button aria-expanded="false" aria-controls="index-sheet">`; U5 supplies the sheet. The rail stays fixed above the pinned hero (z-index above the pin box) so the visitor can always skip it (direction § Hero, KTD5). Trigger sits 16px from the right edge, thumb zone.

Not stock SaaS: no logo-left-links-right-button-right header; no "Sign in" or "Get started" (there is no public sign-up, R11); the index is numbered like a specimen sheet and set in mono; the rail is a hairline, not a blurred glass bar.

## 3. Footer (`id="footer"`, R4)

Full content width, `border-top: 1px solid var(--hairline)`, padding 64 top / 48 bottom at 375, 96 / 64 at 1280, background `--ground`.

Order in DOM (and reading order), stacked at 375, 12-col grid at 1280:
1. Wordmark, 24px, brass i-tick (cols 1–3).
2. Disclaimer, `small` step, `--ink`, exact text: **Research tool. Not investment advice. No performance is promised.** (cols 1–5, under the wordmark, max measure 40ch). Never dimmed, never smaller than 14px.
3. Section index (cols 7–9): `<ol>` of the nine anchors, same ordinals and labels as the nav, `label` step, `--ink-dim`, 48px rows, hairline between rows. It is a plain list, not a second `<nav>` landmark.
4. Theme menu slot (cols 10–12, top): a 48px ghost button `Theme · System` (Hind 500 16px; the second word shows the current choice: System / Dark / Light) with `aria-haspopup="menu"`. U2 ships this button wired to `theme.ts` cycling System → Dark → Light on click as the interim behaviour; U5 replaces the click with the 21st.dev menu, same button, same label.
5. Legal links (cols 10–12, under the theme button): `Privacy` → `/privacy`, `Terms` → `/terms`, `small` step, `--brass` underlined, 48px rows.
6. Bottom hairline, then one mono caption line, `caption` step, `--ink-dim`: `AXIOM · EN-IN · ILLUSTRATIVE FIGURES ONLY`. No copyright year (legal text is pending), no social icons, no newsletter.

At 375: wordmark, disclaimer, theme button (full width), index (full width, nine 48px rows), legal links row, caption. At 768: wordmark + disclaimer left (cols 1–4), index (5–6), theme + legal (7–8).

Not stock SaaS: no four-column link farm, no "Product / Company / Resources"; the index is the page's own table of contents; the disclaimer is the second thing on the footer, in ink not grey; no badges, no app-store buttons.

## 4. 404 (`not-found.tsx`, R17)

`<meta name="robots" content="noindex">`, status 404. Nav rail and footer present. `<main>` is one block, cols 1–7 at 1280, full width at 375, padding 128 top.

Copy, in order:
- `caption` step, `--ink-dim`: `STATUS 404 · NO PAGE AT THIS ADDRESS`
- h1, `legal-h1` step, Martel 700, `--ink`: **No reading at this address.**
- body, `body` step, `--ink-dim`, max 48ch: **The page you asked for is not on the instrument. The address may have changed, or it never existed.**
- Primary button (48px, `--brass-mark` fill): **Go to the start** → `/`.
- Beneath, `small` step: **Or pick a section from the index above.** ("above" is true on every viewport: the rail is sticky.)

No illustration, no ring, no search box, no "oops". The status line is set like a caption rail so even the error page reads as the instrument.

## 5. `/privacy` and `/terms` (R18)

Static pages, same layout: nav rail, `<main>` at cols 1–8 (1280), full width at 375, padding 96 top; footer. Both carry, directly under the h1, a notice box: `--raised` background, `border: 1px solid var(--hairline)`, radius 4px, padding 16, with a `RAC`-style outline stamp (`--brass-line` outline, `--brass` text) reading **PENDING** and, beside it, `small` step in `--ink`: **Text pending legal review.** The box is a `<p role="note">`. Nothing on these pages may be hidden behind a collapse.

**/privacy**
- `caption`: `PRIVACY NOTICE · DRAFT`
- h1: **Privacy notice**
- notice box (above)
- body, `legal-body` step: **This page will carry Axiom's privacy notice once counsel has reviewed it. Until then nothing here is a statement of practice.**
- body: **What this site does today: it keeps one setting in your browser, your theme choice. It has no forms and sends nothing you type.**
- link row: **Back to the start** → `/`

**/terms**
- `caption`: `TERMS OF USE · DRAFT`
- h1: **Terms of use**
- notice box
- body: **This page will carry the terms for using this site once counsel has reviewed them. Until then the footer line stands: research tool, not investment advice, no performance is promised.**
- link row: **Back to the start** → `/`

Titles: `Privacy notice · Axiom`, `Terms of use · Axiom`, `Page not found · Axiom`. All three pages `noindex` until legal text lands (404 by R17; legal pages because a draft notice should not be indexed, revisit in U7).

Banned-phrase check: every string above was read against returns, guaranteed, profit, buy, sell, tips, beat the market (whole words); none appear. Add these strings to the content module so the R2 test covers them.

## 6. Per-viewport: what is not stock SaaS

- **375.** A 48px hairline rail with a numbered mono `INDEX` trigger instead of a hamburger-and-logo bar; pink paper or basalt ground, no white; the footer is a ruled table of contents, not a stack of link columns; the disclaimer is in ink at 14px, not 11px grey.
- **768.** Labels-only rail still in Martian Mono uppercase, no centred pill nav; footer in three ruled columns on hairlines, no icons, no card; 404 and legal pages are a single column of type with a caption line, no illustration.
- **1280.** Nine numbered anchors across the rail, current one carried by a 2px brass rule flush to the hairline, no underline-on-hover animation; footer wordmark with the brass i-tick as the only mark on the page below the hero; notice boxes use an outline stamp, not a yellow warning banner.

Screenshots at 375/768/1280, light and dark, are the U2 exit, not this spec (`NOT RUN` here).
