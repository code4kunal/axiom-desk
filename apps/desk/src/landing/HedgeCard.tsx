import { Caption, Tick } from "./Caption";

type Cell = { label: string; value: string };

// The 05 card adds an evidence grid between its two rows: the trigger spans the first row.
function Grid({ cells }: { cells: readonly Cell[] }) {
  return (
    <dl className="grid grid-cols-2 border-t border-hairline md:grid-cols-4">
      {cells.map((c, i) => (
        <div key={c.label} className={`-mr-px -mb-px border-r border-b border-hairline p-3 lg:p-4 ${i === 0 ? "col-span-full" : ""}`}>
          <dt className="font-mono text-label font-medium uppercase text-ink-dim">{c.label}</dt>
          <dd className="mt-3 font-mono text-[16px] leading-none">
            {c.value === "EARLY DETERIORATION" ? (
              <span className="font-medium text-geru">
                <Tick tone="geru" />
                {c.value}
              </span>
            ) : c.value === "CNF" ? (
              <span className="stamp text-stamp-cnf">{c.value}</span>
            ) : (
              <span className="text-ink">{c.value}</span>
            )}
          </dd>
        </div>
      ))}
    </dl>
  );
}

// One content string: mono segments, then the human-confirms line (split at the last " · ").
export function HedgeCard({ text, grid }: { text: string; grid?: readonly Cell[] }) {
  const cut = text.lastIndexOf(" · ");
  return (
    <div className="overflow-hidden rounded-2 border border-hairline bg-raised">
      <p className="px-3 py-3 font-mono text-caption uppercase text-ink-dim lg:px-4">
        <Caption text={text.slice(0, cut)} />
      </p>
      {grid && <Grid cells={grid} />}
      <p className={`${grid ? "" : "border-t border-hairline"} px-3 py-3 font-body text-ui font-medium text-ink lg:px-4`}>
        {text.slice(cut + 3)}
      </p>
    </div>
  );
}
