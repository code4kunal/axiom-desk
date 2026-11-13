import { Fragment } from "react";
import { hero } from "../content";

// The ring rendered offline at one state (scripts/render-posters.ts), one picture per theme, sitting on
// the ground with no frame. CSS shows the theme's picture; the other is display:none and lazy, so it is
// never fetched (KTD8). The regime word in the hole is live text, so the island can change it.
const THEMES = ["dark", "light"] as const;

// Split by the breakpoint where the live ring changes density (RingIsland: narrow below 768), not by
// width descriptors, which would hand a 768-1023 tablet the phone-density file.
const PHONE = "(width < 48rem)";
const file = (p: number, t: string, ext: string, phone: boolean) => `/hero/poster-${p}-${t}${phone ? "-720" : ""}.${ext}`;

export function Poster({ p }: { p: 0 | 40 | 70 | 100 }) {
  const hole = hero.hole[p === 0 ? 0 : 1]!;
  return (
    <div className="hero-plate relative aspect-square w-full [container-type:inline-size]">
      {THEMES.map((t) => (
        <picture key={t} data-poster={t}>
          <source media={PHONE} type="image/avif" srcSet={file(p, t, "avif", true)} />
          <source type="image/avif" srcSet={file(p, t, "avif", false)} />
          <source media={PHONE} type="image/webp" srcSet={file(p, t, "webp", true)} />
          <img
            src={file(p, t, "webp", false)}
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
          className="max-w-[55%] font-display text-regime text-[length:min(var(--text-regime),7.6cqi)] font-bold text-balance data-[tone=geru]:text-geru data-[tone=monsoon]:text-monsoon"
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

// Preload the resolved theme's 0% poster (the LCP) at high priority, home page only. Same file and media
// split as the <source>s, so the browser picks the same file and never fetches twice.
export const posterPreloadScript = `if(location.pathname==="/"){var t=document.documentElement.dataset.theme,p=matchMedia(${JSON.stringify(PHONE)}).matches,l=document.createElement("link");l.rel="preload";l.as="image";l.type="image/avif";l.fetchPriority="high";l.href="/hero/poster-0-"+t+(p?"-720":"")+".avif";document.head.appendChild(l)}`;
