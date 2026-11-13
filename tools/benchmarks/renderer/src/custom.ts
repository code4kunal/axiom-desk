import { BAR_SECONDS } from "./replay.ts";
import type { Bar, ChartRenderer, SyncBus } from "./types.ts";

const AXIS_W = 56;
const UP = "#26a269";
const DOWN = "#c01c28";

/** Candidate A: hand-written Canvas2D candles. Base layer redraws on data/range change, overlay on crosshair. */
export function createCustom(el: HTMLElement, bus: SyncBus): ChartRenderer {
  const base = document.createElement("canvas");
  const over = document.createElement("canvas");
  for (const c of [base, over]) {
    c.style.cssText = "position:absolute;inset:0;width:100%;height:100%";
    el.appendChild(c);
  }
  el.style.position = "relative";
  const bctx = base.getContext("2d")!;
  const octx = over.getContext("2d")!;

  let bars: Bar[] = [];
  let from = 0;
  let to = 0;
  let cross: number | null = null;
  let baseDirty = true;
  let overDirty = true;
  let raf = 0;
  let w = 0;
  let h = 0;
  let dpr = 1;

  const resize = () => {
    dpr = window.devicePixelRatio || 1;
    w = el.clientWidth;
    h = el.clientHeight;
    for (const c of [base, over]) {
      c.width = Math.round(w * dpr);
      c.height = Math.round(h * dpr);
    }
    baseDirty = overDirty = true;
    schedule();
  };
  const ro = new ResizeObserver(resize);
  ro.observe(el);

  // Bars are sorted by time; binary search keeps per-frame work proportional to visible bars.
  const firstAtOrAfter = (t: number) => {
    let lo = 0;
    let hi = bars.length;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (bars[mid]!.time < t) lo = mid + 1;
      else hi = mid;
    }
    return lo;
  };

  const plotW = () => w - AXIS_W;
  const xOf = (t: number) => ((t - from) / (to - from)) * plotW();
  const tOf = (x: number) => from + (x / plotW()) * (to - from);

  let yMin = 0;
  let yMax = 1;
  const yOf = (p: number) => h - ((p - yMin) / (yMax - yMin)) * h;

  function drawBase() {
    bctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    bctx.clearRect(0, 0, w, h);
    const i0 = Math.max(0, firstAtOrAfter(from) - 1);
    const i1 = Math.min(bars.length, firstAtOrAfter(to) + 1);
    if (i1 <= i0) return;
    yMin = Infinity;
    yMax = -Infinity;
    for (let i = i0; i < i1; i++) {
      yMin = Math.min(yMin, bars[i]!.low);
      yMax = Math.max(yMax, bars[i]!.high);
    }
    const pad = (yMax - yMin) * 0.05 || 1;
    yMin -= pad;
    yMax += pad;
    const bw = Math.max(1, (BAR_SECONDS / (to - from)) * plotW() * 0.7);
    // Batch by colour: two fills and two strokes per frame instead of one per bar.
    for (const up of [true, false]) {
      bctx.fillStyle = bctx.strokeStyle = up ? UP : DOWN;
      bctx.beginPath();
      for (let i = i0; i < i1; i++) {
        const b = bars[i]!;
        if (b.close >= b.open !== up) continue;
        const x = Math.round(xOf(b.time + BAR_SECONDS / 2)) + 0.5;
        bctx.moveTo(x, yOf(b.high));
        bctx.lineTo(x, yOf(b.low));
      }
      bctx.stroke();
      for (let i = i0; i < i1; i++) {
        const b = bars[i]!;
        if (b.close >= b.open !== up) continue;
        const x = xOf(b.time + BAR_SECONDS / 2) - bw / 2;
        const y0 = yOf(Math.max(b.open, b.close));
        bctx.fillRect(x, y0, bw, Math.max(1, yOf(Math.min(b.open, b.close)) - y0));
      }
    }
    bctx.fillStyle = "#888";
    bctx.font = "11px system-ui";
    for (let k = 0; k <= 4; k++) {
      const p = yMin + ((yMax - yMin) * k) / 4;
      bctx.fillText(p.toFixed(2), plotW() + 4, yOf(p) - 2);
    }
  }

  function drawOver() {
    octx.setTransform(dpr, 0, 0, dpr, 0, 0);
    octx.clearRect(0, 0, w, h);
    if (cross === null) return;
    const x = Math.round(xOf(cross)) + 0.5;
    octx.strokeStyle = "#999";
    octx.setLineDash([4, 4]);
    octx.beginPath();
    octx.moveTo(x, 0);
    octx.lineTo(x, h);
    octx.stroke();
  }

  function frame() {
    raf = 0;
    if (baseDirty) drawBase();
    if (overDirty) drawOver();
    baseDirty = overDirty = false;
  }
  function schedule() {
    if (!raf) raf = requestAnimationFrame(frame);
  }

  // Interaction: wheel zooms around the cursor, drag pans; both broadcast the range.
  let dragX: number | null = null;
  over.addEventListener("wheel", (e) => {
    e.preventDefault();
    const t = tOf(e.offsetX);
    const k = e.deltaY > 0 ? 1.1 : 1 / 1.1;
    api.setRange(t - (t - from) * k, t + (to - t) * k);
    bus.range(api, from, to);
  });
  over.addEventListener("pointerdown", (e) => {
    dragX = e.offsetX;
    over.setPointerCapture(e.pointerId);
  });
  over.addEventListener("pointerup", () => (dragX = null));
  over.addEventListener("pointermove", (e) => {
    if (dragX !== null) {
      const dt = ((dragX - e.offsetX) / plotW()) * (to - from);
      dragX = e.offsetX;
      api.setRange(from + dt, to + dt);
      bus.range(api, from, to);
    }
    api.setCrosshair(tOf(e.offsetX));
    bus.crosshair(api, cross);
  });
  over.addEventListener("pointerleave", () => {
    api.setCrosshair(null);
    bus.crosshair(api, null);
  });

  const api: ChartRenderer = {
    setBars(b) {
      bars = b.slice();
      const last = bars[bars.length - 1]?.time ?? 0;
      from = last - 200 * BAR_SECONDS;
      to = last + 10 * BAR_SECONDS;
      baseDirty = true;
      schedule();
    },
    update(bar, isNew) {
      if (isNew) bars.push(bar);
      else bars[bars.length - 1] = bar;
      // Only redraw when the tick is on screen.
      if (bar.time + BAR_SECONDS >= from && bar.time <= to) {
        baseDirty = true;
        schedule();
      }
    },
    setCrosshair(t) {
      cross = t;
      overDirty = true;
      schedule();
    },
    setRange(f, t) {
      from = f;
      to = t;
      baseDirty = overDirty = true;
      schedule();
    },
    destroy() {
      cancelAnimationFrame(raf);
      ro.disconnect();
      el.replaceChildren();
    },
  };
  return api;
}
