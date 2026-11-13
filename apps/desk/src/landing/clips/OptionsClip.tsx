import type { CSSProperties } from "react";
import { options } from "../content";

// Five kinds of option trade, ranked by how much premium they carry. A bar per grade, no figures.
// Neutral ink: a rich premium is not "rising", so monsoon and geru stay out. Sized in container units.
const LENGTH: Record<string, number> = { Rich: 1, Fair: 0.6, Thin: 0.25 };
const at = (i: number): CSSProperties => ({ animationName: `clip-step-${Math.min(i, 5)}` });

export function OptionsClip() {
  const s = options.scene;
  return (
    <div data-scene aria-hidden className="absolute inset-0 flex flex-col p-[5.5cqw] pt-[11cqw]">
      <p className="font-mono text-[max(12px,3cqw)] font-medium text-ink">{s.title}</p>
      <ol className="mt-[5cqw] border-t border-hairline">
        {s.rows.map((r, k) => (
          <li key={r.trade} className="clip-step grid grid-cols-[3.5cqw_1fr_auto] items-center gap-x-[3cqw] gap-y-[1.6cqw] border-b border-hairline py-[3cqw]" style={at(k)}>
            <span className="font-mono text-[max(12px,3cqw)] text-ink-dim">{k + 1}</span>
            <span className="text-[max(14px,4cqw)] font-medium text-ink">{r.trade}</span>
            <span className="font-mono text-[max(12px,3cqw)] uppercase text-ink">{r.grade}</span>
            <span className="col-start-2 col-end-4 h-[1.4cqw] rounded-1 bg-ink-dim" style={{ width: `${(LENGTH[r.grade] ?? 0) * 100}%` }} />
          </li>
        ))}
      </ol>
      <p className="clip-step mt-[4cqw] text-[max(14px,3.6cqw)] leading-[1.4] text-ink-dim" style={at(5)}>
        {s.key}
      </p>
    </div>
  );
}
