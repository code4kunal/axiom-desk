import type { CSSProperties } from "react";
import { charts } from "../content";

// Small panes on one clock: the crosshair moves in all of them at once, then two tags land.
// Below 1024 the slot is narrow (~340–720px), so it shows four panes at twice the scale, keeping tags readable.
const N = 64;
const CROSS = 0.68; // where the crosshair rests: inside the tagged pattern

// Deterministic random walk per pane (mulberry32), so server and every visit draw the same lines.
function walk(seed: number, pw: number, ph: number): string {
  let a = seed;
  const rnd = () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const ys: number[] = [];
  let y = 0;
  for (let i = 0; i < N; i++) ys.push((y += rnd() - 0.48));
  const lo = Math.min(...ys);
  const span = Math.max(...ys) - lo || 1;
  const top = ph * 0.12;
  const bottom = ph * 0.82;
  return ys
    .map((v, i) => `${i ? "L" : "M"}${((i / (N - 1)) * (pw - 32) + 16).toFixed(1)} ${(bottom - ((v - lo) / span) * (bottom - top)).toFixed(1)}`)
    .join("");
}

type Layout = { w: number; h: number; cols: number; rows: number; y0: number; title: number; tag: number; seeds: number[]; known: number; unknown: number };

const WIDE: Layout = { w: 1200, h: 760, cols: 4, rows: 2, y0: 100, title: 24, tag: 15, seeds: [0, 1, 2, 3, 4, 5, 6, 7], known: 0, unknown: 5 };
const NARROW: Layout = { w: 600, h: 380, cols: 2, rows: 2, y0: 64, title: 20, tag: 14, seeds: [0, 1, 4, 5], known: 0, unknown: 3 };

function Tag({ x, y, text, size, tone }: { x: number; y: number; text: string; size: number; tone: "known" | "unknown" }) {
  // Martian Mono advances ~0.72em per character.
  const w = text.length * size * 0.72 + 20;
  return (
    <g className={`clip-tag clip-tag-${tone}`} transform={`translate(${x} ${y})`}>
      <rect width={w} height={size * 2.2} rx="2" className={tone === "known" ? "fill-ground stroke-monsoon" : "fill-ground stroke-hairline"} />
      <text x="10" y={size * 1.45} style={{ fontSize: size }} className={`font-mono font-medium ${tone === "known" ? "fill-monsoon" : "fill-ink-dim"}`}>
        {text}
      </text>
    </g>
  );
}

function Scene({ l, className }: { l: Layout; className: string }) {
  const gap = 16;
  const x0 = 40;
  const pw = (l.w - 2 * x0 - gap * (l.cols - 1)) / l.cols;
  const ph = (l.h - l.y0 - 40 - gap * (l.rows - 1)) / l.rows;
  const panes = l.seeds.map((seed, i) => ({
    x: x0 + (i % l.cols) * (pw + gap),
    y: l.y0 + Math.floor(i / l.cols) * (ph + gap),
    d: walk(11 + seed * 7, pw, ph),
  }));
  const band = (pw - 32) * 0.16;
  const bandX = 16 + (pw - 32) * CROSS - band / 2;
  const tagY = (p: { y: number }) => p.y + ph - l.tag * 2.2 - 10;
  return (
    <svg data-scene viewBox={`0 0 ${l.w} ${l.h}`} className={`absolute inset-0 size-full ${className}`} aria-hidden>
      <text x={x0} y={l.y0 * 0.58} style={{ fontSize: l.title }} className="fill-ink font-mono font-medium">
        {charts.scene.title}
      </text>
      {panes.map((p, i) => (
        <g key={i} transform={`translate(${p.x} ${p.y})`}>
          <rect width={pw} height={ph} rx="2" className="fill-ground stroke-hairline" />
          {i === l.known && <rect x={bandX} y="12" width={band} height={ph - 24} className="clip-band fill-monsoon/10" />}
          {i === l.unknown && <rect x={bandX} y="12" width={band} height={ph - 24} className="clip-band fill-ink/5 stroke-hairline [stroke-dasharray:4_4]" />}
          <path d={p.d} pathLength={1} className="clip-line fill-none stroke-ink" strokeWidth="2" style={{ animationDelay: `${i * 60}ms` }} />
          <line
            x1="0"
            x2="0"
            y1="8"
            y2={ph - 8}
            className="clip-cross stroke-ink-dim [stroke-dasharray:6_4]"
            strokeWidth="1.5"
            style={{ "--to": `${16 + (pw - 32) * CROSS}px` } as CSSProperties}
          />
        </g>
      ))}
      <Tag x={panes[l.known]!.x + 10} y={tagY(panes[l.known]!)} text={charts.scene.known} size={l.tag} tone="known" />
      <Tag x={panes[l.unknown]!.x + 10} y={tagY(panes[l.unknown]!)} text={charts.scene.unknown} size={l.tag} tone="unknown" />
    </svg>
  );
}

export function ChartsClip() {
  return (
    <>
      <Scene l={NARROW} className="lg:hidden" />
      <Scene l={WIDE} className="max-lg:hidden" />
    </>
  );
}
