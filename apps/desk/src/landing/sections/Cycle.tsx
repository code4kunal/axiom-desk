import { sectors } from "../content";

// The four seasons in the order a cycle runs; the hero shows the first two, this shows the whole loop.
// Colour by role: monsoon where sectors rise (risk-on, recovery), geru where they turn or fall.
export function Cycle() {
  return (
    <ol className="mt-8 grid grid-cols-2 border-t border-l border-hairline">
      {sectors.cycle.map((c, k) => (
        <li key={c.name} className="border-r border-b border-hairline p-3 lg:p-4">
          <p className="font-mono text-label text-ink-dim">
            {String(k + 1).padStart(2, "0")}{" "}
            <span className={k === 1 || k === 2 ? "text-geru" : "text-monsoon"}>{c.name.toUpperCase()}</span>
          </p>
          <p className="mt-1.5 text-body text-ink">{c.say}</p>
        </li>
      ))}
    </ol>
  );
}
