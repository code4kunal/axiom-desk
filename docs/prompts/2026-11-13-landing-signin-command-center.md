# Build prompt: landing page, sign-in, Command Center

Groomed with prompt-coach on 2026-11-13. All choices are the user's, except TASTE, which is still open. Run one session per step and `/clear` between them. Use plan mode for each surface and wait for approval before editing.

## Decisions

| Topic | Choice |
|---|---|
| Order | Step 0 G5 design pass → 1 landing → 2 sign-in → 3 Command Center |
| Per-surface skills | `ce-brainstorm` → `ce-plan` → `ce-doc-review` → `archify` (docs/diagrams/) → `ui-ux-pro-max` design → `impeccable` review + fixes → `ce-work` |
| Framework | Next.js App Router, one app (`apps/desk`): static landing plus signed-in desk routes |
| Styling | Tailwind driven only by DESIGN.md tokens |
| Motion | Motion (framer-motion) for UI; GSAP ScrollTrigger for the hero scroll |
| 3D | three.js in the hero only, lazy-loaded, with a static poster fallback |
| HyperFrames | Pre-rendered product clips (agent answering, regime flip) as video loops on the landing page |
| 21st.dev | Primitives only (menus, dialogs), restyled to tokens |
| Audience | Brokers in discovery, plus the desk |
| Hero | Regime → basket → hedge loop |
| Brand | Typeset "Axiom" wordmark, designed in G5 |
| Tone | Quant-precise, evidence-first: numbers carry base rates |
| TASTE | **OPEN:** {{TASTE_LIKES}} / {{TASTE_HATES}}. Nothing starts without it |

## Prompt

```
Read first: @CLAUDE.md, @docs/plans/2026-11-12-1110-feat-axiom-desk-platform-plan.md (Goal Capsule and Product Contract l.1-110, R48 ~l.179, flow ~l.380, KTD20 ~l.631, G5 ~l.808, U2 ~l.891, U26 ~l.1311), and the UI rules in ~/.claude/CLAUDE.md.

Step 0: G5 design pass. It blocks everything else.
Run impeccable `context`. TASTE likes: {{TASTE_LIKES}}. Hates: {{TASTE_HATES}}.
Write DESIGN.md and references/TASTE.md: tokens, type (not Inter, Geist or DM Sans), colour (no purple or indigo), motion rules (durations, easing, reduced-motion), non-colour encoding for up/down and states, light and dark, and the typeset "Axiom" wordmark.
Wait for my approval.

Pipeline for each surface: ce-brainstorm -> ce-plan -> ce-doc-review -> archify (docs/diagrams/) -> ui-ux-pro-max design -> impeccable review and fixes -> ce-work.

Stack: Next.js App Router in apps/desk; Tailwind driven only by DESIGN.md tokens; Motion for UI; GSAP ScrollTrigger for the hero scroll; three.js in the hero only; HyperFrames for pre-rendered landing clips; 21st.dev primitives restyled to tokens. No other new dependencies. Pin exact versions at least two weeks old. Check every unfamiliar API against the installed source; mark anything unchecked UNVERIFIED.

1. Landing page (brokers in discovery, plus the desk)
   - Hero: the regime -> basket -> hedge loop as a three.js ring driven by scroll.
     0%: regime "Expansion". 40%: it turns to "Early deterioration, 68% confidence".
     70%: the basket reweights from equity to gilts and gold. 100%: a hedge card drafts, labelled "a human confirms every order".
   - Sections: the problem (equity-only tools fail in bear regimes); 4 modules (Charts, Options/Vol Lab, Hedge, cited Agent), each with a HyperFrames clip; the evidence standard (base rate, sample size, out-of-sample); a broker CTA.
   - Copy: quant-precise, 25 words or fewer per section. No performance promises and no buy, sell or advice wording. Add a test that fails on a banned-phrase list (returns, guaranteed, profit, buy, sell, tips, beat the market).
   - Performance: load three.js and the clips lazily; static poster when WebGL fails; a prefers-reduced-motion path; LCP under 2.5 s on throttled mobile.

2. Sign-in
   An Axiom-branded screen that hands off to the desk's OIDC identity provider with MFA (KTD20). No password field.
   States: idle, redirecting, IdP error, session expired, MFA required. Fully usable by keyboard and screen reader.

3. Command Center (R48), the first page after sign-in
   Shows regime and confidence, leading sectors and asset classes, top Radar opportunities and risk triggers. Any item opens into a chart. Agent prompt: "what changed since yesterday's close?".
   The engines are not built yet: use recorded fixtures and show a visible FIXTURE DATA label.
   No three.js or HyperFrames on chart panes (the spike's 120 fps budget). No stat-card row, no left-border cards, no hover lift.

Out of scope: a real auth backend, real engines, retail flows, pricing.

Done = lint, typecheck, tests and build all pass, with the output shown. Screenshots at 375, 768 and 1280 in light and dark for each surface, compared with DESIGN.md; differences listed and fixed. For each viewport, state what is not stock SaaS. Anything not run is marked NOT RUN.
Then have a subagent review the diff against the plan and DESIGN.md, reporting only gaps in correctness, requirements or compliance.
```

## Risks

- The landing page isn't in the plan of record. `ce-plan` should add it as a unit so the gates and the review cover it.
- Brokers may reuse landing copy under their own brand, which carries SEBI exposure. That's why the banned-phrase test exists.
- A heavy 3D hero on mid-tier Android hurts LCP and drains the battery. The poster and reduced-motion paths are required, not optional.
- The HyperFrames API is unchecked (UNVERIFIED).
