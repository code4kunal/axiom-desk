import { BAR_SECONDS, Replay } from "./replay.ts";
import type { ChartRenderer, RendererFactory, SyncBus } from "./types.ts";

const q = new URLSearchParams(location.search);
const name = q.get("renderer") ?? "custom";
const N = Number(q.get("charts") ?? 8);
const TICKS_PER_SEC = Number(q.get("tps") ?? 20); // per chart
const SECONDS = Number(q.get("seconds") ?? 20);
const WARMUP = 2;
const HISTORY = Number(q.get("history") ?? 20000);

const factories: Record<string, () => Promise<RendererFactory>> = {
  custom: async () => (await import("./custom.ts")).createCustom,
  scichart: async () => (await import("./scichart.ts")).createSciChart,
};

export interface BenchResult {
  renderer: string;
  charts: number;
  ticksPerSecPerChart: number;
  ticksPerSecDelivered: number; // chart 0, measured window: setInterval drops calls when drawing is late
  historyBars: number;
  frames: number;
  fps: number;
  frameMs: { p50: number; p95: number; p99: number; max: number };
  over20ms: number; // share of frames slower than a 50 fps budget
  longTasks: number;
  longTaskMs: number;
  userAgent: string;
}
declare global {
  interface Window {
    __bench?: BenchResult;
  }
}

const pct = (s: number[], p: number) => s[Math.min(s.length - 1, Math.floor(p * s.length))]!;

async function run() {
  const make = await factories[name]!();
  const grid = document.getElementById("grid")!;
  grid.style.gridTemplateColumns = `repeat(${Math.min(N, 4)}, 1fr)`;

  const charts: ChartRenderer[] = [];
  const bus: SyncBus = {
    crosshair: (src, t) => charts.forEach((c) => c !== src && c.setCrosshair(t)),
    range: (src, f, t) => charts.forEach((c) => c !== src && c.setRange(f, t)),
  };
  const replays: Replay[] = [];
  for (let i = 0; i < N; i++) {
    const cell = document.createElement("div");
    cell.className = "cell";
    grid.appendChild(cell);
    const r = new Replay(i + 1, HISTORY, 30);
    replays.push(r);
    const c = await make(cell, bus);
    c.setBars(r.history);
    charts.push(c);
  }

  // Ticks arrive on a timer like a socket would, independent of frames. Each new bar slides the
  // view so the live bar stays on screen, as on a desk; a fixed range lets new bars leave the
  // screen within seconds, after which a renderer that skips off-screen ticks does no tick redraws.
  let edge = replays[0]!.history[replays[0]!.history.length - 1]!.time;
  let measuring = false;
  let ticksMeasured = 0;
  const tickTimer = setInterval(() => {
    for (let i = 0; i < N; i++) {
      const { bar, isNew } = replays[i]!.next();
      charts[i]!.update(bar, isNew);
      if (isNew) charts[i]!.setRange(bar.time - 200 * BAR_SECONDS, bar.time + 10 * BAR_SECONDS);
      if (i === 0) {
        edge = bar.time;
        if (measuring) ticksMeasured++;
      }
    }
  }, 1000 / TICKS_PER_SEC);

  let longTasks = 0;
  let longTaskMs = 0;
  const po = new PerformanceObserver((l) =>
    l.getEntries().forEach((e) => {
      longTasks++;
      longTaskMs += e.duration;
    }),
  );
  try {
    po.observe({ type: "longtask", buffered: false });
  } catch {
    // longtask is Chromium-only; frame times still measure the other engines.
  }

  // A scripted user sweeps the crosshair across chart 0's visible bars every frame, so sync runs at full rate.
  const deltas: number[] = [];
  const t0 = performance.now();
  let prev = t0;
  await new Promise<void>((done) => {
    const loop = (now: number) => {
      const el = (now - t0) / 1000;
      const sweep = edge - 200 * BAR_SECONDS + ((el * 40) % 200) * BAR_SECONDS;
      measuring = el > WARMUP;
      charts[0]!.setCrosshair(sweep);
      bus.crosshair(charts[0]!, sweep);
      if (el > WARMUP) deltas.push(now - prev);
      prev = now;
      if (el < WARMUP + SECONDS) requestAnimationFrame(loop);
      else done();
    };
    requestAnimationFrame(loop);
  });
  clearInterval(tickTimer);
  po.disconnect();

  const s = deltas.slice().sort((a, b) => a - b);
  const round = (x: number) => Math.round(x * 100) / 100;
  const result: BenchResult = {
    renderer: name,
    charts: N,
    ticksPerSecPerChart: TICKS_PER_SEC,
    ticksPerSecDelivered: round(ticksMeasured / SECONDS),
    historyBars: HISTORY,
    frames: deltas.length,
    fps: round(deltas.length / SECONDS),
    frameMs: { p50: round(pct(s, 0.5)), p95: round(pct(s, 0.95)), p99: round(pct(s, 0.99)), max: round(s[s.length - 1]!) },
    over20ms: round(deltas.filter((d) => d > 20).length / deltas.length),
    longTasks,
    longTaskMs: round(longTaskMs),
    userAgent: navigator.userAgent,
  };
  window.__bench = result;
  document.getElementById("out")!.textContent = JSON.stringify(result, null, 2);
}

run().catch((e) => {
  document.getElementById("out")!.textContent = `ERROR ${e instanceof Error ? e.stack : String(e)}`;
  throw e;
});
