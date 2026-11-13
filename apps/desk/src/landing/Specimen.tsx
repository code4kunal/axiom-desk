import { evidence } from "./content";

const stampTone: Record<string, string> = { CNF: "text-stamp-cnf", RAC: "text-stamp-rac", WL: "text-stamp-wl" };

// "BASE RATE 0.58" → label "BASE RATE", value "0.58"; a segment without a figure is a label-less cell.
function cell(seg: string) {
  const m = seg.match(/^(.*\D) (\S*\d\S*)$/);
  return m ? { label: m[1]!, value: m[2]! } : { label: "", value: seg };
}

export function Specimen() {
  const cells = evidence.specimen.split(" · ").map(cell);
  const figures = cells.filter((c) => c.label);
  const marker = cells.filter((c) => !c.label).map((c) => c.value).join(" · ");
  return (
    <div>
      <div className="overflow-hidden rounded-2 border border-hairline bg-raised">
        <dl className="grid grid-cols-2 md:grid-cols-4">
          {figures.map((c) => (
            <div key={c.label} className="-mr-px -mb-px border-r border-b border-hairline p-3 lg:p-4">
              <dt className="font-mono text-label font-medium uppercase text-ink-dim">{c.label}</dt>
              <dd className="mt-3 font-mono text-[16px] leading-none text-ink">{c.value}</dd>
            </div>
          ))}
        </dl>
        <p className="p-3 font-mono text-[16px] leading-none text-ink lg:p-4">{marker}</p>
      </div>
      <ul className="mt-4">
        {evidence.grades.map((g) => (
          <li key={g.stamp} className="flex min-h-12 items-center gap-4 border-b border-hairline first:border-t">
            <span className="w-[72px] shrink-0">
              <span className={`stamp ${stampTone[g.stamp]}`}>{g.stamp}</span>
            </span>
            <span className="text-body text-ink">{g.meaning}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
