# U14 renderer spike: result

Status: **partial, no decision yet.** The custom renderer is measured. SciChart is built and typechecks but has not run (no licence key). The five R126 timed tasks have not run (no desk testers yet). Per the plan, no chart feature work starts until this file records a decision.

## Candidates

| | A: custom | B: SciChart.js as renderer |
|---|---|---|
| Code | `src/custom.ts`, Canvas2D, ~200 lines | `src/scichart.ts`, `scichart@6.0.15` |
| Drawing | Canvas2D: one base layer redrawn on data/range change, one overlay for the crosshair; draws visible bars only | WebGL, or WebGPU on Apple Silicon (per the package README, UNVERIFIED here) |
| Licence | ours | Commercial EULA. The free community licence is personal and non-commercial only, so the desk needs a trial or paid key |
| Data, replay, sync | shared harness: `src/replay.ts`, `src/main.ts` | same harness |

Both implement the same `ChartRenderer` interface in `src/types.ts`, so either can sit behind `packages/chart-ts`.

## Method

- `src/main.ts` lays out N charts (default 8, 4×2), each fed by a seeded 1-minute random-walk replay (20,000 history bars, 30 ticks per bar) on a timer, independent of frames.
- A scripted user moves the crosshair across chart 0 every frame; the sync bus forwards it to the other 7. Range changes (wheel zoom, drag pan) also go over the bus.
- After a 2 s warmup it records every `requestAnimationFrame` delta for the run, plus Chromium long tasks.
- `bench.ts` opens each renderer in headed Google Chrome (real GPU) at 1920×1080 through Playwright and prints one JSON line per run.

```bash
pnpm --filter @axiom/renderer-spike dev        # serves http://localhost:5199
pnpm --filter @axiom/renderer-spike bench custom --seconds=20
pnpm --filter @axiom/renderer-spike bench scichart --seconds=20   # needs VITE_SCICHART_LICENSE_KEY in .env.local
```

Machine: darwin-arm64 (Apple Silicon), 120 Hz display, Chrome 157, Node 24.22.3, 2026-11-13.

## Results: frame time, 8 synced charts

A 120 Hz display gives an 8.33 ms frame budget, so p50 = 8.3 ms means locked at refresh rate.

| Renderer | Ticks/s per chart | Run | fps | p50 ms | p95 ms | p99 ms | max ms | frames > 20 ms | long tasks |
|---|---|---|---|---|---|---|---|---|---|
| custom | 20 | 1 | 120.1 | 8.3 | 9.2 | 9.3 | 9.4 | 0% | 1 (54 ms) |
| custom | 20 | 2 | 120.6 | 8.3 | 9.2 | 10.0 | 33.1 | 0% | 0 |
| custom | 20 | 3 | 119.9 | 8.3 | 9.2 | 10.4 | 71.8 | 0% | 0 |
| custom | 100 (5× load) | 1 | 120.2 | 8.3 | 9.3 | 10.2 | 74.1 | 0% | 0 |
| scichart | 20 | — | NOT RUN: no licence key | | | | | | |

Visual check: a screenshot of `?renderer=custom` shows 8 candle charts drawing, with the synced crosshair at the same time on all of them.

Reading: the custom renderer holds refresh rate with 8 charts at 5× the planned tick load, without WebGL. There is a rare single-frame stall (max 33–74 ms in 3 of 4 runs, under 0.05% of frames) with no long task logged. GC is the likely cause; not yet profiled.

## R126 timed tasks (two desk users)

The five spike tasks: open a symbol, change interval, add an indicator, draw a trendline, switch layout.

| Tester | Renderer | Task times | Notes |
|---|---|---|---|
| — | — | NOT RUN | needs two named desk testers |

These tasks also need UI the spike does not have yet (a symbol picker, interval menu, indicator add, trendline tool, layout switch). Build it once on the shared interface so both renderers get the same UI.

## Decision

Open. Decide after the SciChart run and the timed tasks. The custom renderer meets the frame-time bar on its own, so the decision turns on:

1. Whether SciChart is clearly faster at higher data density (many more bars on screen, 1-second bars).
2. Licence cost: per-developer and white-label terms for broker tenants. UNVERIFIED; get a quote.
3. Build cost of the R10 chart types and drawing tools that SciChart ships and we would write ourselves.
