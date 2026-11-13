export interface Bar {
  time: number; // unix seconds, bar open
  open: number;
  high: number;
  low: number;
  close: number;
}

/** What the harness needs from a candidate renderer. Both candidates implement exactly this. */
export interface ChartRenderer {
  /** Replace all data. */
  setBars(bars: Bar[]): void;
  /** Apply one tick: `isNew` appends a bar, otherwise the last bar is replaced. */
  update(bar: Bar, isNew: boolean): void;
  /** Show the crosshair at a time (from a sibling chart), or hide it. */
  setCrosshair(time: number | null): void;
  /** Show this time range (from a sibling chart). */
  setRange(from: number, to: number): void;
  destroy(): void;
}

/** Shared bus that keeps the layout synced by crosshair and time (R12). */
export interface SyncBus {
  crosshair(source: ChartRenderer, time: number | null): void;
  range(source: ChartRenderer, from: number, to: number): void;
}

export type RendererFactory = (el: HTMLElement, bus: SyncBus) => ChartRenderer | Promise<ChartRenderer>;
