import type { Bar } from "./types.ts";

// Deterministic so both renderers draw the identical session.
function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export const BAR_SECONDS = 60;
const START = Date.UTC(2026, 0, 5, 3, 45) / 1000; // 09:15 IST

/** Ticks per wall second at a replay speed: 60x plays one bar-minute per second. */
export const ticksPerSecond = (ticksPerBar: number, speed: number) => (ticksPerBar * speed) / BAR_SECONDS;

/**
 * Synthetic 1-minute session for one symbol.
 * shortcut: random walk, not recorded vendor ticks; swap in U6 replay files once G1 sample data exists.
 */
export class Replay {
  readonly history: Bar[] = [];
  private rnd: () => number;
  private last: Bar;
  private ticksInBar = 0;
  private ticksPerBar: number;

  constructor(seed: number, historyBars: number, ticksPerBar: number) {
    this.ticksPerBar = ticksPerBar;
    this.rnd = mulberry32(seed);
    let price = 1000 + seed * 37;
    for (let i = 0; i < historyBars; i++) {
      const bar = this.walkBar(START + i * BAR_SECONDS, price);
      this.history.push(bar);
      price = bar.close;
    }
    this.last = { ...this.history[this.history.length - 1]! };
  }

  private walkBar(time: number, open: number): Bar {
    let high = open;
    let low = open;
    let p = open;
    for (let t = 0; t < 8; t++) {
      p += (this.rnd() - 0.5) * open * 0.002;
      high = Math.max(high, p);
      low = Math.min(low, p);
    }
    return { time, open, high, low, close: p };
  }

  /** Next tick: the updated (or new) last bar. */
  next(): { bar: Bar; isNew: boolean } {
    if (++this.ticksInBar >= this.ticksPerBar) {
      this.ticksInBar = 0;
      const o = this.last.close;
      this.last = { time: this.last.time + BAR_SECONDS, open: o, high: o, low: o, close: o };
      return { bar: { ...this.last }, isNew: true };
    }
    const p = this.last.close + (this.rnd() - 0.5) * this.last.close * 0.0008;
    this.last.close = p;
    this.last.high = Math.max(this.last.high, p);
    this.last.low = Math.min(this.last.low, p);
    return { bar: { ...this.last }, isNew: false };
  }
}
