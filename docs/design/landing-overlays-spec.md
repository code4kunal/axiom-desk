# Landing overlays spec (U5)

Theme menu, broker dialog, nav sheet. Tokens from `DESIGN.md` and `landing-palette-v2.md`; states in `docs/diagrams/landing-overlays.html`. Primitives from shadcn (Radix) per KTD9, restyled; none ship in the stock look.

## Shared

- No shadow, no blur, no alpha. DESIGN.md bans alpha tints, so there is **no scrim**: the dialog separates by a 1px `--ink` border on `--raised`; the sheet is full-screen on `--ground`. The page behind is inert (Radix modal).
- Radius 4px (`rounded-2`) on surfaces, 2px on cells. Hairline rules inside.
- Targets 48px. Focus ring 2px `--brass-line` (= ink), offset 2px, never removed.
- Motion: enter = opacity + rise, `--ease-reveal`; dialog and sheet 240ms with a 12px rise, menu 160ms with a 4px rise; exit = opacity, 200ms. Section reveals keep 480ms; overlays answer a click, so they enter faster. Reduced motion: opacity only, 0px rise.
- Focus: Radix traps it while open; Escape closes; focus returns to the trigger.

## Theme menu (R13, R14)

- Trigger in the header right slot at every width: after the section rail from 1024, left of INDEX below. 40px tall, `px-3`, hairline border, Martian Mono label type: `THEME · LIGHT`.
- Content: `DropdownMenuRadioGroup` (menuitemradio + aria-checked), aligned end, 4px below the trigger, min-width 200px, `--raised`, 1px `--ink` border. Items 48px, Anek Latin 500 `ui` size. Checked item: a 6px ink square at the left, colour never the only cue (aria-checked plus the square).
- Choosing an item applies and persists via `setTheme` (theme.ts), then closes.
- Replaces the footer's interim `ThemeButton`.

## Broker dialog (R10)

- Opens from "Talk to the desk" (section 08). Width `min(480px, 100vw - 32px)`, centred, padding 24px (16 at 375).
- Title: Eczar 700 `section-head` scaled down to 28px, "Talk to the desk". Description in `body`.
- Address: Martian Mono 500 20px, `select-all`, in a hairline-bordered cell, plain text.
- Actions row: **Copy** (primary: ink fill, ground text, 48px) and **Write an email** (ghost link with the `mailto:` and subject). Close is a text button "Close" top-right, 48px target.
- Copy feedback: the button label reads "Copied" for 2s and a polite live region announces "Address copied". Clipboard denied: the label reads "Select and copy" and the address text is selected for the visitor; no error colour.
- No form fields; nothing stored or sent.

## Nav sheet (R13, R19, below 1024)

- INDEX in the header opens a full-screen sheet (`side="top"`, inset 0) on `--ground`. Its first row repeats the header: wordmark left, "Close" right, 48px, hairline bottom rule, so the sheet reads as the header unfolding.
- List: the eight sections, rows 56px with hairline rules; Martian Mono ordinal `01` in `--ink-dim`, label in Anek Latin 500 20px. Current section (from the observer) gets `aria-current` and an ink 2px left bar inside the row.
- Choosing a row closes the sheet, then the browser follows the anchor; focus moves to the target section heading.
- From 1024 the sheet never renders; the rail lists sections.
