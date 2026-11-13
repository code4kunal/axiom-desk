import { strategies } from "../content";

// A backtest: one strategy line, with the last third shaded as years the strategy never saw while it
// was built. The line falls inside that band on purpose: a test on unseen years shows losses too.
// No market line, so nothing reads as "beats the market". Shapes only, no axis figures.
// The chart, note and checks stack in normal flow so phone-size text cannot overlap the chart.
const W = 640;
const H = 340;
const X0 = 8;
const X1 = 632;
const Y0 = 20;
const Y1 = 320;
const N = 90;
const SPLIT = 0.66;

// Deterministic path: a steady drift with one fall placed inside the unseen years.
function line(drift: number, fall: number, seed: number): string {
  let a = seed;
  const rnd = () => ((a = (a * 16807) % 2147483647) / 2147483647) - 0.5;
  const ys: number[] = [];
  let y = 0;
  for (let i = 0; i < N; i++) {
    const t = i / (N - 1);
    const drop = t > 0.74 && t < 0.84 ? -fall : 0;
    ys.push((y += drift + drop + rnd() * 0.9));
  }
  const top = Math.max(...ys);
  const bottom = Math.min(...ys);
  const py = (v: number) => Y1 - 24 - ((v - bottom) / (top - bottom)) * (Y1 - Y0 - 90);
  return ys.map((v, i) => `${i ? "L" : "M"}${(X0 + (i / (N - 1)) * (X1 - X0)).toFixed(1)} ${py(v).toFixed(1)}`).join("");
}

const strategy = line(0.24, 1.1, 11);
const split = X0 + SPLIT * (X1 - X0);

export function StrategyClip() {
  const s = strategies.scene;
  return (
    <div data-scene aria-hidden className="absolute inset-0 flex flex-col p-[5.5cqw] pt-[11cqw]">
      <p className="font-mono text-[max(12px,3cqw)] font-medium text-ink">{s.title}</p>
      <svg viewBox={`0 0 ${W} ${H}`} className="mt-[4cqw] w-full">
        <rect x={split} y={Y0} width={X1 - split} height={Y1 - Y0} className="clip-band fill-ink/5" />
        <line x1={split} x2={split} y1={Y0} y2={Y1} className="stroke-ink-dim [stroke-dasharray:6_6]" />
        <text x={split + 12} y={Y0 + 30} className="clip-band fill-ink-dim font-mono text-[22px]">{s.unseen}</text>
        <line x1={X0} x2={X1} y1={Y1} y2={Y1} className="stroke-ink-dim" />
        <path d={strategy} pathLength={1} className="clip-line fill-none stroke-ink" strokeWidth="3" />
      </svg>
      <p className="clip-step mt-[3cqw] text-[max(14px,3.6cqw)] leading-[1.4] text-ink-dim" style={{ animationName: "clip-step-1" }}>
        {s.note}
      </p>
      <ul className="mt-auto border-t border-hairline">
        {s.checks.map((c, k) => (
          <li key={c} className="clip-step flex items-center gap-[2.5cqw] border-b border-hairline py-[2cqw] text-[max(14px,3.6cqw)] text-ink" style={{ animationName: `clip-step-${k + 2}` }}>
            <span className="font-mono text-monsoon">✓</span>
            {c}
          </li>
        ))}
      </ul>
    </div>
  );
}
