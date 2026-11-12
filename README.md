# Axiom Desk

Research, charting, options and hedging platform for the Indian market, built agent-native: every capability is reachable from its screen, the command bar and the agent through one registry.

The plan is `docs/plans/2026-11-12-1110-feat-axiom-desk-platform-plan.md`.

## Layout

- `packages/<name>/src/<module>`: Python packages (uv workspace). Every number is computed here.
- `apps/desk`: the desk app (Next.js, pnpm workspace).
- `services/`: API, workers, stream gateway, sandbox.
- `tools/`: benchmarks, hooks and repo checks.

## Commands

```bash
uv sync --python 3.12
uv run ruff check . && uv run pyright && uv run pytest
pnpm install && pnpm -r typecheck && pnpm -r lint && pnpm -r test
git config core.hooksPath tools/hooks   # secret scan before each commit
```
