// A mono caption split on " · ": the state word carries its tone plus a needle glyph (colour is never
// the only signal), ILLUSTRATIVE stays in ink, and lines only break after a separator dot.
type Tone = "monsoon" | "geru";

const toneClass: Record<Tone, string> = { monsoon: "text-monsoon", geru: "text-geru" };
const tickAngle: Record<Tone, number> = { monsoon: -30, geru: 8 };

// A pivoted needle, like the poster's, so it can't be read as a typed slash.
export function Tick({ tone }: { tone: Tone }) {
  return (
    <svg aria-hidden viewBox="0 0 12 12" className="mr-1 inline-block size-3 align-[-1px]">
      <g transform={`rotate(${tickAngle[tone]} 6 10)`}>
        <line x1="6" y1="10" x2="6" y2="2.5" stroke="currentColor" strokeWidth="1.5" />
        <circle cx="6" cy="10" r="1.5" fill="currentColor" />
      </g>
    </svg>
  );
}

function Segment({ seg, state, tone }: { seg: string; state?: string; tone?: string }) {
  if (seg === "ILLUSTRATIVE") return <span className="text-ink">{seg}</span>;
  if (state && tone && seg.includes(state)) {
    const [before, after] = seg.split(state);
    return (
      <>
        {before}
        <span className={`font-medium ${toneClass[tone as Tone]}`}>
          <Tick tone={tone as Tone} />
          {state}
        </span>
        {after}
      </>
    );
  }
  return <>{seg}</>;
}

export function Caption({ text, state, tone }: { text: string; state?: string; tone?: string }) {
  const segments = text.split(" · ");
  return (
    <>
      {segments.map((seg, i) => (
        <span key={i}>
          <span className="whitespace-nowrap">
            <Segment seg={seg} state={state} tone={tone} />
            {i < segments.length - 1 && " ·"}
          </span>
          {i < segments.length - 1 && " "}
        </span>
      ))}
    </>
  );
}
