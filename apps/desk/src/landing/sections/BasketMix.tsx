import type { CSSProperties } from "react";
import { hero } from "../content";
import { WEIGHTS_A, WEIGHTS_B } from "../hero/weights";

// The basket before and after the season turns, as two stacked bars in the asset colours. Lengths
// come from the ring's own weights, so the two never disagree; labels carry the meaning, not figures.
const MARKS = ["equity", "gilts", "gold", "cash", "intl"] as const;

function Bar({ label, weights }: { label: string; weights: readonly number[] }) {
  return (
    <div>
      <p className="font-mono text-label uppercase text-ink-dim">{label}</p>
      <div className="mt-2 flex h-6 gap-px overflow-hidden rounded-1">
        {weights.map((w, k) => (
          <span key={k} className="bg-(--c)" style={{ flexGrow: w, "--c": `var(--color-${MARKS[k]}-mark)` } as CSSProperties} />
        ))}
      </div>
    </div>
  );
}

export function BasketMix({ before, after }: { before: string; after: string }) {
  return (
    <div className="space-y-5 rounded-2 border border-hairline bg-raised p-4 lg:p-5">
      <Bar label={before} weights={WEIGHTS_A} />
      <Bar label={after} weights={WEIGHTS_B} />
      <ul className="flex flex-wrap gap-x-5 gap-y-2 border-t border-hairline pt-4 font-mono text-label uppercase text-ink-dim">
        {hero.legend.labels.map((l, k) => (
          <li key={l} className="flex items-center gap-2">
            <span className="size-2.5 rounded-1 bg-(--c)" style={{ "--c": `var(--color-${MARKS[k]}-mark)` } as CSSProperties} />
            {l}
          </li>
        ))}
      </ul>
    </div>
  );
}
