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
- A scripted user moves the crosshair across chart 0 every frame; the sync bus forwards it to the other 7. Each new bar slides every chart's range so the live bar stays on screen (set per chart, not over the bus). Wheel zoom and drag pan use the bus but are not scripted, so bus range sync is untested under load.
- `ticksPerSecDelivered` records the tick rate chart 0 actually got in the measured window.
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

**Corrected 2026-11-13.** The first runs kept a fixed visible range. New bars left the screen within seconds (3 s at 100 ticks/s, 15 s at 20), and the custom renderer skips redraws for off-screen ticks, so most of those runs measured the crosshair alone. They are struck below. The harness now follows the live bar.

| Renderer | Ticks/s per chart (delivered) | Run | fps | p50 ms | p95 ms | p99 ms | max ms | frames > 20 ms (count) | long tasks |
|---|---|---|---|---|---|---|---|---|---|
| custom | 20 (20.05) | live edge | 119.95 | 8.3 | 9.2 | 9.3 | 33.6 | ≥1, count not recorded | 0 |
| custom | 100, 5× load (100) | live edge | 119.8 | 8.3 | 9.2 | 9.3 | 58.4 | ≥1, count not recorded | 2 (450 ms total) |
| ~~custom~~ | ~~20~~ | ~~fixed range, 3 runs~~ | ~~120~~ | ~~8.3~~ | ~~9.2~~ | ~~9.3–10.4~~ | ~~9.4–71.8~~ | | invalid: ticks off screen |
| ~~custom~~ | ~~100~~ | ~~fixed range~~ | ~~120.2~~ | ~~8.3~~ | ~~9.3~~ | ~~10.2~~ | ~~74.1~~ | | invalid: ticks off screen |
| scichart | 20 | — | NOT RUN: no licence key | | | | | | |

The harness now reports `framesOver20ms` as a count and counts only long tasks that start after warmup. The two custom rows above were recorded with the old harness, which reported a rounded share (one slow frame showed as 0%) and counted long tasks from page start, warmup included: their exact counts are unknown, and a max above 20 ms only proves at least one slow frame. Their long-task figures may include warmup (the 5× run's 450 ms did not show as a 450 ms frame). Rerun to replace them.

Visual check: a screenshot of `?renderer=custom` shows 8 candle charts drawing, with the synced crosshair at the same time on all of them.

Reading: with the live bar on screen, the custom renderer holds refresh rate with 8 charts at 5× the planned tick load, without WebGL (one run each; repeat before deciding). A rare single-frame stall remains (max 34–58 ms). GC is the likely cause; not yet profiled.

## Budget runs: 16 charts and 4 footprint charts

**NOT RUN.** The harness is built; no budget run has been made. Nothing below is measured.

What a run does (`bench.ts`, `src/load.ts`, `src/metrics.ts`):

- `--session=budget`: 16 charts, 600 s per run, 3 repeats, replay at 60x (30 ticks per bar, so 30 ticks/s per chart). Over the candles it lays a simulated rail (20 cards, one rewritten every 500 ms), a strategy overlay (payoff curve and cone) and a ladder of 100 strikes on every chart, redrawn at the tick rate, plus the DOM control layer (a labelled call and put button per strike, 4 strategy legs, 20 focusable rail items) on the focused chart only, as the desk virtualises it.
- `--session=footprint`: 4 charts, each drawing a 40-bar by 30-level footprint grid with bid-by-ask text, same duration, repeats and replay speed.
- Frame times are the `requestAnimationFrame` deltas of the measured window, taken from the whole run (`window.__frames`), not from the harness summary. Percentiles are nearest-rank.
- A run with fewer than 3 repeats reports `incomplete`. With 3, the status is `pass` only if every run has p95 at most 16.7 ms, p99.9 at most 33 ms and at most 3 frames over 50 ms; otherwise `fail`.
- The hardware profile (`--profile` name, CPU, cores, memory, OS, Chrome, GPU, device pixel ratio) is written into every result line.

Known gap: `src/main.ts` does not start the load itself. `bench.ts` injects it after the charts exist, so the load's 2 s warmup starts a little after the harness's own warmup.

```bash
pnpm --filter @axiom/renderer-spike dev        # serves http://localhost:5199
pnpm --filter @axiom/renderer-spike bench custom --session=budget --profile="<desk hardware name>" --out=budget.jsonl     # about 30 min
pnpm --filter @axiom/renderer-spike bench custom --session=footprint --profile="<desk hardware name>" --out=footprint.jsonl   # about 30 min
```

| Session | Renderer | Hardware profile | Repeats | p95 ms | p99.9 ms | frames > 50 ms | Status |
|---|---|---|---|---|---|---|---|
| budget (16 charts, rail, strategy overlay, DOM layer, 60x) | custom | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| footprint (4 charts, 60x) | custom | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| budget | scichart | NOT RUN: no licence key | | | | | |

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
