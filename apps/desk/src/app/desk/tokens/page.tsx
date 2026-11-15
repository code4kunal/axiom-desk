import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";
import { lanes, payoff, tags } from "@/chart/content";

// Dev-only specimen of the chart role tokens (DESIGN.md §8.2–8.3), for U8's screenshot check.
export const metadata: Metadata = { title: "Chart tokens", robots: { index: false } };

const Svg = ({ children }: { children: ReactNode }) => (
  <svg width="96" height="32" viewBox="0 0 96 32" aria-hidden="true" className="shrink-0">
    {children}
  </svg>
);

const ROLES: { token: string; text: string; role: string; sample: string; cue: string; mark: ReactNode }[] = [
  {
    token: "c-up",
    text: "text-c-up",
    role: "Up, +delta, bid",
    sample: "+1,240",
    cue: "hollow body, 1.5px outline",
    mark: <rect x="40" y="6" width="14" height="20" fill="none" strokeWidth="1.5" className="stroke-c-up-mark" />,
  },
  {
    token: "c-down",
    text: "text-c-down",
    role: "Down, −delta, ask",
    sample: "−860",
    cue: "filled body",
    mark: <rect x="40" y="6" width="14" height="20" className="fill-c-down-mark" />,
  },
  {
    token: "c-call",
    text: "text-c-call",
    role: "Call OI, call wall",
    sample: tags.callWall.full,
    cue: `3px solid line, lane ${lanes.call}`,
    mark: <line x1="0" y1="16" x2="96" y2="16" strokeWidth="3" className="stroke-c-call-mark" />,
  },
  {
    token: "c-put",
    text: "text-c-put",
    role: "Put OI, put wall",
    sample: tags.putWall.full,
    cue: `double 1.5px line, lane ${lanes.put}`,
    mark: (
      <g strokeWidth="1.5" className="stroke-c-put-mark">
        <line x1="0" y1="14" x2="96" y2="14" />
        <line x1="0" y1="18" x2="96" y2="18" />
      </g>
    ),
  },
  {
    token: "c-magnet",
    text: "text-c-magnet",
    role: "POC, max pain, value area",
    sample: tags.maxPain.full,
    cue: "dashed 6-4 line, tag",
    mark: <line x1="0" y1="16" x2="96" y2="16" strokeWidth="2" strokeDasharray="6 4" className="stroke-c-magnet-mark" />,
  },
  {
    token: "c-auction",
    text: "text-c-auction",
    role: "IB, HVN, LVN, single prints",
    sample: `${tags.hvn.full} ${tags.lvn.full}`,
    cue: "filled ◆ HVN, open ◇ LVN",
    mark: (
      <g strokeWidth="1.5" className="stroke-c-auction-mark">
        <path d="M30 8 L38 16 L30 24 L22 16 Z" className="fill-c-auction-mark" />
        <path d="M66 8 L74 16 L66 24 L58 16 Z" fill="none" />
      </g>
    ),
  },
  {
    token: "c-band",
    text: "text-c-band",
    role: "Cone, VWAP bands, replay future",
    sample: tags.cone1.full,
    cue: "dashed edges, tag",
    mark: (
      <g className="stroke-c-band-mark" strokeDasharray="4 3" strokeWidth="1.5">
        <rect x="0" y="8" width="96" height="16" className="fill-c-band-mark" fillOpacity="0.08" />
        <line x1="0" y1="8" x2="96" y2="8" />
        <line x1="0" y1="24" x2="96" y2="24" />
      </g>
    ),
  },
];

// Literal class names: Tailwind only emits utilities it can read in source.
const HEAT = ["bg-heat-1", "bg-heat-2", "bg-heat-3", "bg-heat-4", "bg-heat-5", "bg-heat-6"];

export default function Tokens() {
  if (process.env.NODE_ENV === "production") notFound();
  return (
    <main className="frame py-10">
      <p className="font-mono text-caption uppercase text-ink-dim">DESIGN.md §8.2 · §8.3</p>
      <h1 className="mt-3 font-display text-legal-h1 font-bold">Chart tokens</h1>

      <ul className="mt-8 border-t border-hairline">
        {ROLES.map((r) => (
          <li key={r.token} className="grid grid-cols-[1fr_auto] items-center gap-x-4 gap-y-2 border-b border-hairline py-4 md:grid-cols-[14rem_10rem_6rem_1fr]">
            <div>
              <p className="font-mono text-label">--{r.token}</p>
              <p className="mt-1 text-small text-ink-dim">{r.role}</p>
            </div>
            <p className={`font-mono text-ui ${r.text}`}>{r.sample}</p>
            <Svg>{r.mark}</Svg>
            <p className="text-small text-ink-dim">{r.cue}</p>
          </li>
        ))}
      </ul>

      <h2 className="mt-10 font-mono text-label">Liquidity heatmap, --heat-1…6</h2>
      <ol className="mt-4 grid grid-cols-6 border border-hairline">
        {HEAT.map((bg, i) => (
          <li key={bg} className="border-r border-hairline last:border-r-0">
            <div className={`h-12 ${bg}`} />
            <p className="px-2 py-1 font-mono text-label">{i + 1}</p>
          </li>
        ))}
      </ol>

      <h2 className="mt-10 font-mono text-label uppercase">Payoff words</h2>
      <p className="mt-3 font-mono text-ui">
        <span className="text-c-up">{payoff.maxGain}</span> · <span className="text-c-down">{payoff.maxLoss}</span> ·{" "}
        {tags.breakeven.full}
      </p>
    </main>
  );
}
