# Axiom Desk

Plan of record: `docs/plans/2026-11-12-1110-feat-axiom-desk-platform-plan.md`. Units U1–U27, phase PRs, merge gates G1–G5.

## Feature pipeline (mandatory, every feature, in order)

1. **Groom** with compound-engineering: `ce-brainstorm` when scope is unclear, then `ce-plan` to turn the unit into an implementation plan; `ce-doc-review` on that plan before build.
2. **Diagram** before implementation with `archify`: architecture, data flow, sequence or state for the feature. Diagrams go in `docs/diagrams/`.
3. **UI**: design with `ui-ux-pro-max:ui-ux-pro-max`, then review with `impeccable` and apply its fixes. Target: the most premium desk UI, not stock SaaS.
4. **Backend**: implement with `ce-work` or `ship`.

Skip a step only when the feature has no part for it (no UI, no backend), and say which step was skipped.

## UI constraints

- G5 is a start gate: no `apps/desk` screen work before `DESIGN.md` and the TASTE file (3 likes + 3 hates from the desk) exist. The U14 renderer spike is exempt.
- The global UI rules still apply: no stock default stack, screenshots at 375/768/1280 in light and dark before "done".
