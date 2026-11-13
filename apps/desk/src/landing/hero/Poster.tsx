import { Fragment } from "react";
import { hero } from "../content";

// The ring rendered offline at one state (scripts/render-posters.ts), one picture per theme, sitting on
// the ground with no frame. CSS shows the theme's picture; the other is display:none and lazy, so it is
// never fetched (KTD8). The regime word in the hole is live text, so the island can change it.
const THEMES = ["dark", "light"] as const;

export function Poster({ p }: { p: 0 | 40 | 70 | 100 }) {
  const hole = hero.hole[p === 0 ? 0 : 1]!;
  return (
    <div className="hero-plate relative aspect-square w-full">
      {THEMES.map((t) => (
        <picture key={t} data-poster={t}>
          <source type="image/avif" srcSet={`/hero/poster-${p}-${t}.avif`} />
          <img
            src={`/hero/poster-${p}-${t}.webp`}
            alt=""
            width={960}
            height={960}
            loading="lazy"
            decoding="async"
            className="block size-full"
          />
        </picture>
      ))}
      <div
        aria-hidden
        className="hero-hole pointer-events-none absolute inset-0 z-10 flex flex-col items-center justify-center gap-1.5 pt-[12%] text-center"
      >
        <b
          data-tone={hole.tone}
          className="max-w-[55%] font-display text-regime font-bold text-balance data-[tone=geru]:text-geru data-[tone=monsoon]:text-monsoon"
        >
          {hole.word}
        </b>
        <span className="max-w-[40%] font-mono max-sm:hidden text-label text-ink-dim tabular-nums">
          {/* Breaks only between "CONF 0.74" and "N 212". Hidden <640: the hole is too small and the caption repeats it. */}
          {hole.conf.split(" · ").map((part, i) => (
            <Fragment key={part}>
              {i > 0 && " · "}
              <span className="whitespace-nowrap">{part}</span>
            </Fragment>
          ))}
        </span>
      </div>
    </div>
  );
}

// Head script: preload the resolved theme's 0% poster (the LCP) at high priority, home page only.
export const posterPreloadScript = `if(location.pathname==="/"){var l=document.createElement("link");l.rel="preload";l.as="image";l.type="image/avif";l.fetchPriority="high";l.href="/hero/poster-0-"+document.documentElement.dataset.theme+".avif";document.head.appendChild(l)}`;
