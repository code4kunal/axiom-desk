# Desk sign-in screens: `/sign-in` and `/desk`

Design spec, not build. Plan: `docs/plans/2026-11-13-1804-feat-desk-sign-in-plan.md` (R1, R3, R4, R6, R7, KTD8, KTD10, KTD11, U5). Tokens: `DESIGN.md` + `apps/desk/src/app/globals.css` (`@theme static`). Operate mode: precise, calm, no marketing voice. G5 start gate does not apply to these two shells (no new tokens, no new components beyond the ones named here); the full desk pass still waits on G5.

## Decisions

- Reuse: `Wordmark`, the landing rail (`sticky top-0 h-12 border-b border-hairline bg-ground` + `frame`), `frame`, `link` utility, the `not-found.tsx` primary-button recipe. No new tokens. No sections, cards or hero: one hairline-bounded column.
- Rail on both screens carries the wordmark only (no section nav, no ThemeMenu on `/sign-in`; `/desk` rail adds the Sign out form on the right). Wordmark is not a link on `/sign-in` (landing has no route from here; a signed-out user must not be bounced to a page whose purpose is a different audience). On `/desk` it is plain text too.
- One primary button per screen. Sign in is an `<a href="/auth/login">` (top-level GET, no JS). Sign out is `<form method="post" action="/auth/logout"><button type="submit">`.
- No JS needed anywhere. No client components required; theme follows the existing `data-theme` script / `prefers-color-scheme` fallback in `globals.css`.

## Tokens (classes only, no raw hex)

| Element | Font | Size token | Colour | Notes |
|---|---|---|---|---|
| Caption above h1 | `font-mono` Martian Mono 400 | `text-caption uppercase` | `text-ink-dim` | `AXIOM DESK`; `/desk`: `SIGNED IN` |
| h1 | `font-display` Eczar 700 | `text-legal-h1 font-bold text-balance` | `text-ink` | 30 -> 40px fluid; same as `not-found` |
| Body / helper | `font-body` Anek Latin 400 | `text-body` (18-20) | `text-ink-dim` | `max-w-[48ch]` |
| Error label | `font-mono` 500 | `text-label uppercase` | `text-geru` | 12px mono 500 uppercase = allowed floor |
| Error message | `font-body` 500 | `text-body` | `text-ink` | message in ink, not geru: contrast and calm; geru is the label + 2px `border-geru-mark` top rule only |
| Primary button | `font-body` 500 | `text-ui` (17) | `bg-brass-mark text-on-brass` | `h-12 rounded-2 px-6 inline-flex items-center` |
| Ghost button (Sign out, reload) | `font-body` 500 | `text-ui` | `text-ink border border-hairline hover:border-ink-dim` | `h-12 rounded-2 px-6`, colour-only hover |
| User name | `font-display` Eczar 700 | `text-legal-h1` | `text-ink` | the h1 on `/desk` |
| Tenant | `font-mono` 500 | `text-ui` | `text-ink` | label `BROKER` in `text-label uppercase text-ink-dim` above it |

- Focus: global `:focus-visible` (2px `brass-line`, 2px offset); do not override. On the rail, Sign out gets `focus-visible:outline-offset-[-2px]` like the landing nav links so the ring is not clipped by the 48px rail.
- Targets: all actions >= 48px tall; Sign in full-width below 768 (`w-full md:w-auto`); 8px+ clear around every control.
- Radius 4px max, no shadow, no gradient, no blur, no hover lift. Hover = colour only (existing recipe).

## `/sign-in` layout

```
375 (frame px-4)             768 (px-8)                     1280 (px-12, content max 1280)
+-------------------+       +-----------------------+      +-----------------------------------------------+
| Axiom  (rail 48)  |       | Axiom (rail 48)       |      | Axiom (rail 48)                               |
|-------------------|       |-----------------------|      |-----------------------------------------------|
|                   |       |                       |      |                                               |
| AXIOM DESK        |       |                       |      |   AXIOM DESK                                  |
| Sign in           |       | AXIOM DESK            |      |   Sign in                                     |
| [error block]     |       | Sign in               |      |   [error block, max 52ch]                     |
| Use your desk     |       | [error block]         |      |   Use your desk account. ...                  |
| account...        |       | body (48ch)           |      |   [ Sign in ]  (auto width)                   |
| [ Sign in ] 48 w  |       | [ Sign in ] auto      |      |                                               |
|                   |       |                       |      |   (right 5 cols empty: hairline column rule)  |
+-------------------+       +-----------------------+      +-----------------------------------------------+
```

- Column: `frame pt-16 pb-24 md:pt-24`; content `max-w-[48ch]`, left-aligned, not centred (centred card = stock auth page). At >= 1280 the content hangs on the first 5 of 12 columns and a single `border-l border-hairline` full-height rule sits at the column edge, and nothing else. Empty space is intentional.
- Vertical rhythm: caption -> 16 -> h1 -> 24 -> error block (if any) -> 24 -> body -> 32 -> button. Spacing scale tokens only (16/24/32/48).
- Body copy (no error): "Use your desk account to open the desk. You will be sent to your sign-in provider and brought back here." Button: **Sign in**. Under button, `text-small text-ink-dim`: "Trouble signing in? Ask your desk admin." (no mailto, no invented address).
- Provider-unavailable and `failed` states keep the Sign in button (retry = same action).

## Error presentation

- Position: between h1 and body, full column width, `border-t-2 border-geru-mark pt-4` (a top rule, not a left-border accent card; no fill, no card, no icon). Label word first (`SIGN-IN FAILED` etc. in geru mono) so colour is never the only signal, then the message in ink.
- Markup: `<div role="alert" class="...">` rendered server-side with `?error=` already resolved. Decision: `role="alert"` (not `status`): sign-in failed is blocking and the user must read it before acting. It is in DOM order before the Sign in button, so keyboard/AT users meet it first.
- Focus on load: none moved (no JS, no focus theft). Document `<title>` changes to the error title below, which AT announce on navigation. If a later enhancement adds focus, target the h1, never the button.
- Unknown / missing `error` value: generic copy, never echo the query value. No `error` param: no block.
- No provider text, no codes shown, no stack/reason ids. Code is in the URL only.

## Copy table (final)

| `?error=` | Label (mono) | Message | What to do (same paragraph, second sentence) |
|---|---|---|---|
| `mfa_required` | SECOND FACTOR NEEDED | Your sign-in did not use multi-factor authentication. | Sign in again and complete the second step at your provider. |
| `unknown_user` | NOT ON THIS DESK | Your account signed in, but it is not set up on this desk. | Ask your desk admin to add you, then sign in again. |
| `expired` | LINK EXPIRED | That sign-in expired or was already used. | Start again with Sign in. |
| `cancelled` | SIGN-IN CANCELLED | You cancelled sign-in at your provider. | Sign in again when you are ready. |
| `provider_unavailable` | PROVIDER UNREACHABLE | We could not reach your sign-in provider. | Wait a minute and try again. If it keeps failing, tell your desk admin. |
| `failed` | SIGN-IN FAILED | Sign-in did not complete. | Try again. If it keeps failing, tell your desk admin. |
| any other value | SIGN-IN FAILED | (same as `failed`) | (same as `failed`) |

Voice: second person, past tense for what happened, imperative for what to do, no apology, no exclamation, no "oops".

## `/desk` layout (signed-in placeholder shell)

```
375                          768                          1280
+-------------------+       +----------------------+     +------------------------------------------+
| Axiom   [Sign out]|       | Axiom      [Sign out]|     | Axiom                         [Sign out] |
|-------------------|       |----------------------|     |------------------------------------------|
| SIGNED IN         |       | SIGNED IN            |     | SIGNED IN                                |
| Priya Menon       |       | Priya Menon          |     | Priya Menon                              |
| ----------------- |       | -------------------- |     | ---------------------------------------- |
| BROKER            |       | BROKER   Demo Securities   |     | BROKER            Demo-Securities   |
| Demo Securities   |       | -------------------- |     | ---------------------------------------- |
| ----------------- |       | The desk is being    |     | The desk is being built. Nothing to      |
| The desk is being |       | built. ...           |     | open yet.                                |
| built. ...        |       +----------------------+     +------------------------------------------+
+-------------------+
```

- Rail: same 48px rail; Sign out is a ghost button in the rail, `h-12` (full rail height, hairline-free in the rail: text button `px-4 text-ui font-medium text-ink`, 48px target, colour hover `text-ink-dim`). Form is `class="flex h-full"`.
- Identity: h1 = display name (`text-legal-h1`, `text-balance`, `break-words`); a hairline definition list below: rows `border-t border-hairline py-4`, `BROKER` label left (`text-label uppercase text-ink-dim`), tenant right at >= 768 / stacked at 375 (`flex-col md:flex-row md:justify-between`). Name and tenant are rendered as text only (React-escaped); long values wrap, never truncate.
- Body: "The desk is being built. Nothing to open yet." in `text-body text-ink-dim`. No fake navigation, no empty widgets, no skeletons.
- Title: `Desk | Axiom`. Landmarks: rail `<header>`, `<main>` holds h1 + dl.

### Desk service unreachable (`/auth/me` non-401 failure)

Same rail (without Sign out: the session state is unknown), same column. Caption `DESK SERVICE`, h1 "The desk is not responding", error block as above with label `SERVICE UNREACHABLE` (geru label, top rule, `role="alert"`), message: "We could not reach the desk service." Then: "Reload to try again. If it keeps failing, tell your desk admin." Button: primary **Reload** = `<a href="/desk">` (full-page GET, no JS). Title: `Desk unavailable | Axiom`. No auto-refresh, no timer.

## Pending state

Sign in is a navigation: the browser shows its own load indicator and the page is left within ~one round trip. Decision: no custom pending state, no JS disabled-while-loading, no spinner (a spinner needs JS and would stick on bfcache back-navigation). Sign out and Reload: same. Buttons have no `:active` scale or shadow.

## Light / dark

- Both themes come from the existing token swap; no per-screen colour. Geru label: `text-geru` (4.5:1+ on `ground` in both themes per palette v2); 2px rule uses `border-geru-mark` (graphic, 3:1+). Primary button inverts automatically (`brass-mark`/`on-brass`).
- `/sign-in` and `/desk` render with the same no-JS `prefers-color-scheme` fallback as the landing. No theme control on `/sign-in`; `/desk` rail may mount `ThemeMenu` later, not in this unit.

## Reduced motion

No entrance animation, no reveal, no stagger on either screen (a utility screen must be readable instantly; the reveal observer is landing-only). Only motion is the global 160ms colour transition, already gated by `prefers-reduced-motion: no-preference`.

## Page titles

| Route / state | `<title>` | robots |
|---|---|---|
| `/sign-in` | `Sign in | Axiom Desk` | noindex |
| `/sign-in?error=<known>` | `Sign-in problem | Axiom Desk` | noindex |
| `/desk` | `Desk | Axiom` | noindex |
| `/desk` unreachable | `Desk unavailable | Axiom` | noindex |

Not in sitemap. Both are `dynamic`/no-store (KTD11).

## NOT stock-SaaS, per viewport

- 375: no centred card, no logo-over-form stack, no social/SSO button column, no "Welcome back!" greeting; left-aligned Eczar h1 at 30px over a full-width ink button, error is a labelled hairline rule instead of a red box with an icon.
- 768: still one 48ch column hung left on the frame grid, no two-pane split with a marketing panel or testimonial; `/desk` shows name and tenant as a hairline definition list, not a stat-card row or avatar chip.
- 1280: the empty right side is deliberate (single hairline column rule, nothing in it); no illustration, no gradient backdrop, no floating card with shadow. Tenant in Martian Mono reads as a ledger entry, not a profile badge.
- All: errors keep the word first (mono label) with geru only on label and rule; zero pills, shadows, gradients, purple, blur, hover lift.

## Verification (NOT RUN)

Spec only. Build unit must produce screenshots at 375/768/1280 in light and dark for: `/sign-in`, each error code, `/desk`, desk unreachable; keyboard-only pass (Tab reaches Sign in / Sign out with ring); no-JS pass (`javascript off`: Sign in navigates, Sign out POSTs); contrast check of `text-geru` on `ground` both themes.
