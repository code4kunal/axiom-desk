import { Caption } from "../Caption";
import { hero } from "../content";
import { HedgeCard } from "../HedgeCard";
import { Poster } from "./Poster";

// Needle angle per plate: expansion, then the 38° sweep that holds through 70 and 100.
const NEEDLE = [-30, 8, 8, 8];

const caption = "mt-3 font-mono text-caption uppercase text-ink-dim";

// Stacked default (no JS, reduced motion, or gate fails): four plates as ordinary content.
export function Hero() {
  const [p0, p40, p70] = hero.plates;
  return (
    <section id="season" aria-labelledby="season-h" className="frame scroll-mt-16 pt-6 pb-24 md:pt-10 lg:pt-16 lg:pb-32">
      <div className="grid grid-cols-4 gap-x-4 gap-y-6 md:grid-cols-8 md:gap-y-8 md:gap-x-6 lg:grid-cols-12">
        <h1
          id="season-h"
          className="col-span-4 font-display text-statement font-extrabold text-balance md:col-span-8 lg:col-span-7"
        >
          {hero.statement}
        </h1>

        <div className="col-span-4 md:row-start-2 lg:col-span-7">
          <p className="max-w-[46ch] text-subline text-ink">{hero.subline}</p>
          <div className="mt-8 flex flex-col gap-2 md:flex-row md:items-center md:gap-6">
            <a
              href="#reading"
              className="flex h-[52px] items-center justify-center rounded-2 bg-brass-mark px-6 font-body text-ui font-medium text-on-brass md:h-12"
            >
              {hero.primary}
            </a>
            <a href="#brokers" className="link flex h-12 items-center justify-center text-ui md:justify-start">
              {hero.brokers}
            </a>
          </div>
        </div>

        {/* Below 768 the figure dissolves into the grid so the buttons fit the first screen and caption 0 follows them. */}
        <figure className="contents md:col-span-4 md:col-start-5 md:row-start-2 md:block lg:col-span-5 lg:col-start-8 lg:row-span-2 lg:row-start-1">
          <div className="order-first col-span-4 mx-auto w-full max-w-[300px] md:max-w-none">
            <Poster needle={NEEDLE[0]!} />
          </div>
          <figcaption className={`col-span-4 ${caption} max-md:mt-2 max-md:border-t max-md:border-hairline max-md:pt-3`}>
            <Caption text={p0!.caption} state={p0!.state} tone={p0!.tone} />
          </figcaption>
        </figure>

        <div className="col-span-4 grid gap-y-10 max-md:mt-10 md:col-span-8 md:grid-cols-3 md:gap-x-6 lg:col-span-12 lg:mt-8">
          <figure id="reading" className="scroll-mt-16">
            <Poster needle={NEEDLE[1]!} />
            <figcaption className={caption}>
              <Caption text={p40!.caption} state={p40!.state} tone={p40!.tone} />
            </figcaption>
          </figure>
          <figure>
            <Poster needle={NEEDLE[2]!} />
            <figcaption className={caption}>
              <Caption text={p70!.caption} />
            </figcaption>
          </figure>
          <figure>
            <Poster needle={NEEDLE[3]!} />
            <figcaption className="mt-3">
              <HedgeCard text={hero.hedgeCard} />
            </figcaption>
          </figure>
        </div>
      </div>
    </section>
  );
}
