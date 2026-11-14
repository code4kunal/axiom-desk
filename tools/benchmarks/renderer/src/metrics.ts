export interface FrameStats {
  frames: number;
  p50: number;
  p95: number;
  p99: number;
  p999: number;
  max: number;
  over50ms: number;
}

// Nearest rank on integer permille, so 999 of 1000 frames is rank 999 with no float rounding.
const rank = (sorted: number[], permille: number) => sorted[Math.ceil((permille * sorted.length) / 1000) - 1]!;
const round = (x: number) => Math.round(x * 100) / 100;

export function frameStats(frameMs: number[]): FrameStats {
  const s = frameMs.slice().sort((a, b) => a - b);
  return {
    frames: s.length,
    p50: round(rank(s, 500)),
    p95: round(rank(s, 950)),
    p99: round(rank(s, 990)),
    p999: round(rank(s, 999)),
    max: round(s[s.length - 1]!),
    over50ms: s.filter((d) => d > 50).length,
  };
}

export const REPEATS = 3;
export const LIMITS = { p95: 16.7, p999: 33, over50ms: 3 }; // per run, 10-minute session

export function summarise(runs: Pick<FrameStats, "p95" | "p999" | "over50ms">[]): { status: "incomplete" | "pass" | "fail" } {
  if (runs.length < REPEATS) return { status: "incomplete" };
  const ok = runs.every((r) => r.p95 <= LIMITS.p95 && r.p999 <= LIMITS.p999 && r.over50ms <= LIMITS.over50ms);
  return { status: ok ? "pass" : "fail" };
}

// shortcut: 95% is a guess at setInterval jitter on a healthy run, tune it from the first real budget runs.
export const TICK_FLOOR = 0.95;

export type Run = Pick<FrameStats, "p95" | "p999" | "over50ms"> & { pageErrors: string[]; ticksPerSecDelivered: number };

/** One renderer's verdict. A page error or a tick shortfall voids the run, and only an unmodified preset session can pass. */
export function runStatus(runs: (Run | { error: unknown })[], tps: number, atPreset: boolean): "error" | "incomplete" | "pass" | "fail" {
  const broken = (r: Run | { error: unknown }) =>
    "error" in r || r.pageErrors.length > 0 || r.ticksPerSecDelivered < TICK_FLOOR * tps;
  if (runs.some(broken)) return "error";
  const { status } = summarise(runs as Run[]);
  return status === "pass" && !atPreset ? "incomplete" : status;
}
