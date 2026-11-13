import type { CSSProperties, ReactNode } from "react";
import { sections } from "../content";

// Text and media column spans per section type at 1280 (12 columns).
const LAYOUT = {
  clip: { text: "lg:col-span-6", media: "lg:col-span-5 lg:col-start-8" },
  // Tall portrait clips: narrower plate, and the caption drops to the plate's bottom edge.
  portrait: { text: "lg:col-span-7 lg:flex lg:flex-col", media: "lg:col-span-4 lg:col-start-9" },
  card: { text: "lg:col-span-5", media: "lg:col-span-6 lg:col-start-7" },
  text: { text: "lg:col-span-8", media: "" },
  // The one-desk sheet: its feature grid runs the full measure.
  wide: { text: "lg:col-span-11", media: "" },
} as const;

type Props = {
  // brokers closes the page outside the numbered nav, so it has no folio.
  id: (typeof sections)[number]["id"] | "brokers";
  heading: string;
  lede?: string;
  caption?: string;
  media?: ReactNode;
  layout: keyof typeof LAYOUT;
  children?: ReactNode;
};

// Every numbered section 02–08, and brokers: full-width rule, folio ordinal in the margin (never above the heading),
// heading = the direction's first sentence, lede = the rest, mono caption on its own rule.
export function Sheet({ id, heading, lede, caption, media, layout, children }: Props) {
  const k = sections.findIndex((s) => s.id === id);
  const n = k < 0 ? "—" : String(k + 1).padStart(2, "0");
  const l = LAYOUT[layout];
  return (
    <section id={id} aria-labelledby={`${id}-h`} className="frame scroll-mt-16 pb-24 lg:pb-32">
      <div className="grid grid-cols-4 gap-x-4 border-t border-hairline pt-3 md:grid-cols-8 md:gap-x-6 lg:grid-cols-12">
        <p aria-hidden className="col-span-4 text-right font-mono text-label text-ink-dim md:col-span-1 md:col-start-1 md:row-start-1 md:text-left">
          {n}
        </p>
        <div className={`col-span-4 mt-12 md:col-span-7 md:col-start-2 md:row-start-1 ${l.text}`}>
          <h2 id={`${id}-h`} data-reveal style={{ "--i": 0 } as CSSProperties} className="font-display text-section-head font-bold text-balance">
            {heading}
          </h2>
          {lede && (
            <p data-reveal style={{ "--i": 1 } as CSSProperties} className="mt-4 max-w-[60ch] text-subline text-pretty text-ink">
              {lede}
            </p>
          )}
          {caption && (
            <p
              data-reveal
              style={{ "--i": 2 } as CSSProperties}
              className="mt-6 border-t border-hairline pt-3 font-mono text-caption uppercase text-ink-dim"
            >
              {caption}
            </p>
          )}
          {children}
        </div>
        {media && (
          <div
            {...(layout === "clip" || layout === "portrait" ? { "data-reveal": "", style: { "--i": 3 } as CSSProperties } : {})}
            className={`col-span-4 mt-8 md:col-span-7 md:col-start-2 lg:row-start-1 lg:mt-12 ${l.media}`}
          >
            {media}
          </div>
        )}
      </div>
    </section>
  );
}
