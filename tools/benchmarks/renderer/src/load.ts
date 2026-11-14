// Synthetic desk load laid over the chart grid: what the renderer must carry besides candles.
// Page side only (DOM/canvas); the session presets are plain data and import cleanly in Node.
import { REPEATS } from "./metrics.ts";

export type LoadKind = "none" | "desk" | "footprint";

export interface Session {
  charts: number;
  seconds: number;
  repeats: number;
  speed: number;
  load: LoadKind;
}

export const SESSIONS = {
  // 16 F&O charts, rail, strategy overlay with payoff and cone, DOM control layer, 10 minutes, 60x replay.
  budget: { charts: 16, seconds: 600, repeats: REPEATS, speed: 60, load: "desk" },
  // Up to 4 footprint charts in a layout hold the same frame limits.
  footprint: { charts: 4, seconds: 600, repeats: REPEATS, speed: 60, load: "footprint" },
} satisfies Record<string, Session>;

// full ladder: a Nifty chain
const BASE_STRIKE = 22000;
const STRIKE_STEP = 50;
const LADDER_WIDTH = 5000;
const STRIKES = LADDER_WIDTH / STRIKE_STEP;
const LEGS = 4;
const RAIL_ITEMS = 20;
const FP_BARS = 40;
const FP_LEVELS = 30;
const WARMUP_MS = 2000;

declare global {
  interface Window {
    __frames?: number[];
  }
}

/** Deterministic cell value 0-899, so reruns draw the same load. */
const cellValue = (bar: number, level: number, side: number, t: number) =>
  Math.abs(Math.round(Math.sin(bar * 12.9898 + level * 78.233 + side * 3.1 + t) * 4375)) % 900;

function overlayCanvas(cell: HTMLElement): CanvasRenderingContext2D {
  const c = document.createElement("canvas");
  c.width = cell.clientWidth;
  c.height = cell.clientHeight;
  c.style.cssText = "position:absolute;inset:0;pointer-events:none";
  cell.appendChild(c);
  return c.getContext("2d")!;
}

function drawDesk(g: CanvasRenderingContext2D, t: number) {
  const { width: w, height: h } = g.canvas;
  g.clearRect(0, 0, w, h);
  const rowH = h / STRIKES;
  g.fillStyle = "#4a90d9";
  for (let i = 0; i < STRIKES; i++) g.fillRect(w - 80, i * rowH, cellValue(i, 0, 0, t) / 12, rowH - 0.5);
  g.strokeStyle = "#d9a441";
  g.beginPath();
  for (let x = 0; x <= 200; x++) {
    const px = (x / 200) * (w - 90);
    const y = h * (0.5 - 0.3 * Math.sin(x / 31 + t) * Math.tanh((x - 100) / 40));
    if (x === 0) g.moveTo(px, y);
    else g.lineTo(px, y);
  }
  g.stroke();
  g.fillStyle = "#4a90d933";
  g.beginPath();
  g.moveTo(w * 0.6, h * 0.5);
  g.lineTo(w - 90, h * (0.3 + 0.05 * Math.sin(t)));
  g.lineTo(w - 90, h * (0.7 - 0.05 * Math.sin(t)));
  g.fill();
}

function drawFootprint(g: CanvasRenderingContext2D, t: number) {
  const { width: w, height: h } = g.canvas;
  g.clearRect(0, 0, w, h);
  g.font = "9px monospace";
  const cw = w / FP_BARS;
  const rh = h / FP_LEVELS;
  for (let b = 0; b < FP_BARS; b++) {
    for (let l = 0; l < FP_LEVELS; l++) {
      const bid = cellValue(b, l, 0, t);
      const ask = cellValue(b, l, 1, t);
      g.fillStyle = bid > ask ? "#d9534f55" : "#3c9d5d55";
      g.fillRect(b * cw, l * rh, cw - 1, rh - 1);
      g.fillStyle = "#ddd";
      g.fillText(`${bid}x${ask}`, b * cw + 1, (l + 1) * rh - 3);
    }
  }
}

function mountControls(cell: HTMLElement): (t: number) => void {
  const layer = document.createElement("div");
  layer.style.cssText = "position:absolute;right:0;top:0;bottom:0;width:80px;overflow:hidden;display:flex;flex-direction:column";
  const ltps: HTMLElement[] = [];
  for (let i = 0; i < STRIKES; i++) {
    const row = document.createElement("div");
    row.style.cssText = "display:flex;flex:1;min-height:0;font-size:6px";
    for (const side of ["call", "put"]) {
      const b = document.createElement("button");
      b.setAttribute("aria-label", `${side} strike ${BASE_STRIKE + i * STRIKE_STEP}`);
      b.style.cssText = "flex:1;padding:0;border:0;background:transparent;color:#ddd";
      row.appendChild(b);
      ltps.push(b);
    }
    layer.appendChild(row);
  }
  const strip = document.createElement("div");
  strip.style.cssText = "position:absolute;left:4px;bottom:4px;display:flex;gap:4px";
  for (let i = 0; i < LEGS; i++) {
    const b = document.createElement("button");
    b.setAttribute("aria-label", `strategy leg ${i + 1}`);
    b.textContent = `leg ${i + 1}`;
    strip.appendChild(b);
  }
  cell.append(layer, strip);
  return (t) => ltps.forEach((b, i) => (b.textContent = String(cellValue(i, 0, 2, t))));
}

/** One rail for the layout: 20 cards, one of them rewritten every 500 ms like a new detector hit. */
function mountRail(): () => void {
  const rail = document.createElement("ol");
  rail.style.cssText = "position:fixed;right:0;top:0;width:220px;margin:0;padding:0;list-style:none;background:#000a;font-size:10px";
  const items: HTMLElement[] = [];
  for (let i = 0; i < RAIL_ITEMS; i++) {
    const li = document.createElement("li");
    li.tabIndex = 0;
    li.setAttribute("aria-label", `rail item ${i + 1}`);
    items.push(li);
    rail.appendChild(li);
  }
  document.body.appendChild(rail);
  let n = 0;
  return () => (items[n++ % RAIL_ITEMS]!.textContent = `signal ${n} ${cellValue(n, 0, 3, n)}`);
}

/**
 * Lay the load over every cell, redraw it at the tick rate, and log rAF deltas for the measured window.
 * The log (`window.__frames`) stops when the harness publishes `window.__bench`.
 */
export function mountLoad(kind: LoadKind, tps: number) {
  const frames: number[] = (window.__frames = []);
  const cells = kind === "none" ? [] : [...document.querySelectorAll<HTMLElement>(".cell")];
  const draw = kind === "footprint" ? drawFootprint : drawDesk;
  const gs = cells.map(overlayCanvas);
  const controls = kind === "desk" ? mountControls(cells[0]!) : () => {};
  const railStep = kind === "desk" ? mountRail() : () => {};
  let t = 0;
  let dirty = true;
  setInterval(() => ((dirty = true), (t += 0.05)), 1000 / tps);
  setInterval(railStep, 500);
  const start = performance.now();
  let prev = start;
  const loop = (now: number) => {
    if (window.__bench) return;
    if (now - start > WARMUP_MS) frames.push(now - prev);
    prev = now;
    if (dirty) {
      dirty = false;
      gs.forEach((g) => draw(g, t));
      controls(t);
    }
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);
}
