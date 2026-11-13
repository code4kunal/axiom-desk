// Stand-in for the 1200×1200 ring poster: same square box, a drawn graduated ring so it isn't a dead
// box. The real AVIF/WebP posters replace the SVG inside the same frame, so nothing shifts.
const TICKS = Array.from({ length: 24 }, (_, i) => i * 15);

export function Poster({ needle }: { needle: number }) {
  return (
    <div aria-hidden className="aspect-square w-full rounded-2 border border-hairline bg-raised">
      <svg viewBox="0 0 100 100" className="size-full">
        <circle cx="50" cy="50" r="44" fill="none" className="stroke-hairline" strokeWidth="0.4" />
        {TICKS.map((a) => (
          <line
            key={a}
            x1="50" y1="6" x2="50" y2={a % 90 === 0 ? 11 : 9.4}
            className={a % 90 === 0 ? "stroke-brass-mark" : "stroke-ink-faint"}
            strokeWidth="0.5"
            transform={`rotate(${a} 50 50)`}
          />
        ))}
        <line
          x1="50" y1="50" x2="50" y2="30.6"
          className="stroke-brass-mark" strokeWidth="0.75"
          transform={`rotate(${needle} 50 50)`}
        />
        <circle cx="50" cy="50" r="1.2" className="fill-brass-mark" />
      </svg>
    </div>
  );
}
