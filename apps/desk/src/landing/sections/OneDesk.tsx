import type { CSSProperties } from "react";
import { oneDesk } from "../content";

// 02: every feature as one ruled contents list. Each row links down to the story that shows it.
export function OneDesk() {
  return (
    <>
      <ul className="mt-10 border-t border-hairline">
        {oneDesk.items.map((item, k) => (
          <li key={item.name} data-reveal style={{ "--i": 2 + Math.min(k, 3) } as CSSProperties} className="border-b border-hairline">
            <a
              href={item.href}
              className="group grid gap-1 py-3 hover:bg-raised focus-visible:outline-offset-[-2px] sm:grid-cols-[minmax(0,16rem)_1fr] sm:items-baseline sm:gap-6 lg:py-3.5"
            >
              <span className="font-mono text-label font-medium uppercase text-ink">{item.name}</span>
              <span className="text-body text-ink-dim group-hover:text-ink">{item.say}</span>
            </a>
          </li>
        ))}
      </ul>
      <p data-reveal style={{ "--i": 5 } as CSSProperties} className="mt-6 max-w-[60ch] text-body font-medium text-ink">
        {oneDesk.proof}
      </p>
    </>
  );
}
