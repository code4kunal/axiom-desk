import type { CSSProperties } from "react";
import { sectors } from "../content";

// Six sectors re-rank as the season turns: rows slide from the risk-on order to the early-warning
// order. Bar length is relative strength in the after order; no figures. Rows share whatever height
// the labels leave, so phone-size minimum text cannot push the last row out of the slot. A row's
// translate is a percentage of its own height, so rank k sits at k * 100%.
const strength = [0.92, 0.8, 0.66, 0.5, 0.36, 0.24]; // bar length by rank, top to bottom

export function SectorsClip() {
  const s = sectors.scene;
  return (
    <div data-scene aria-hidden className="absolute inset-0 flex flex-col p-[4cqw] pt-[3.4cqw]">
      <p className="font-mono text-[max(12px,2.2cqw)] font-medium text-ink">{s.title}</p>
      <p className="mt-[2.4cqw] text-right font-mono text-[max(12px,1.8cqw)] text-monsoon">↑ {s.leading}</p>
      <div className="relative mt-[0.8cqw] min-h-0 flex-1 border-t border-hairline">
        {s.after.map((name, to) => {
          const from = s.before.indexOf(name);
          const up = to < from;
          return (
            <div
              key={name}
              className="clip-rank absolute inset-x-0 top-0 flex items-center gap-[2.5cqw] border-b border-hairline"
              style={{ height: `${100 / s.after.length}%`, "--from": `${from * 100}%`, "--to": `${to * 100}%` } as CSSProperties}
            >
              <span className="w-[16cqw] text-[max(13px,2.6cqw)] font-medium text-ink">{name}</span>
              <span className="relative h-[1.6cqw] flex-1">
                <span
                  className={`clip-bar absolute inset-y-0 left-0 w-full origin-left rounded-1 bg-ink-dim`}
                  style={{ "--s0": strength[from], "--s1": strength[to] } as CSSProperties}
                />
              </span>
              <span className={`w-[3cqw] text-center font-mono text-[2.4cqw] ${up ? "text-monsoon" : "text-geru"}`}>{up ? "↑" : "↓"}</span>
            </div>
          );
        })}
      </div>
      <p className="mt-[0.8cqw] text-right font-mono text-[max(12px,1.8cqw)] text-geru">↓ {s.fading}</p>
    </div>
  );
}
