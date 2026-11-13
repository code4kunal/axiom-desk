// The ring rendered offline at one state (scripts/render-posters.ts), one picture per theme. CSS shows
// the theme's picture; the other is display:none and lazy, so it is never fetched (KTD8).
const THEMES = ["dark", "light"] as const;

export function Poster({ p }: { p: 0 | 40 | 70 | 100 }) {
  return (
    <div aria-hidden className="hero-plate relative aspect-square w-full overflow-hidden rounded-2 border border-hairline bg-raised">
      {THEMES.map((t) => (
        <picture key={t} data-poster={t}>
          <source type="image/avif" srcSet={`/hero/poster-${p}-${t}.avif`} />
          <img
            src={`/hero/poster-${p}-${t}.webp`}
            alt=""
            width={1200}
            height={1200}
            loading="lazy"
            decoding="async"
            className="block size-full"
          />
        </picture>
      ))}
    </div>
  );
}

// Head script: preload the resolved theme's 0% poster (the LCP) at high priority, home page only.
export const posterPreloadScript = `if(location.pathname==="/"){var l=document.createElement("link");l.rel="preload";l.as="image";l.type="image/avif";l.fetchPriority="high";l.href="/hero/poster-0-"+document.documentElement.dataset.theme+".avif";document.head.appendChild(l)}`;
