import type { CSSProperties } from "react";
import { BrokerDialog } from "@/landing/BrokerDialog";
import { ClipSlot } from "@/landing/ClipSlot";
import { AgentClip } from "@/landing/clips/AgentClip";
import { ChartsClip } from "@/landing/clips/ChartsClip";
import { OptionsClip } from "@/landing/clips/OptionsClip";
import { SectorsClip } from "@/landing/clips/SectorsClip";
import { StrategyClip } from "@/landing/clips/StrategyClip";
import { agent, baskets, brokers, charts, oneDesk, options, sectors, strategies } from "@/landing/content";
import { Hero } from "@/landing/hero/Hero";
import { Observers } from "@/landing/Observers";
import { BasketMix } from "@/landing/sections/BasketMix";
import { Cycle } from "@/landing/sections/Cycle";
import { OneDesk } from "@/landing/sections/OneDesk";
import { Sheet } from "@/landing/sections/Sheet";

const i = (n: number) => ({ "--i": n }) as CSSProperties;

export default function Home() {
  return (
    <>
      <Hero />
      <Sheet id="one-desk" layout="wide" heading={oneDesk.heading} lede={oneDesk.lede}>
        <OneDesk />
      </Sheet>
      <Sheet id="sectors" layout="clip" heading={sectors.heading} lede={sectors.lede} caption={sectors.caption} media={<ClipSlot clip={sectors.clip}><SectorsClip /></ClipSlot>}>
        <Cycle />
      </Sheet>
      <Sheet id="charts" layout="clip" heading={charts.heading} lede={charts.lede} caption={charts.caption} media={<ClipSlot clip={charts.clip}><ChartsClip /></ClipSlot>} />
      <Sheet id="options" layout="portrait" heading={options.heading} lede={options.lede} caption={options.caption} media={<ClipSlot clip={options.clip}><OptionsClip /></ClipSlot>} />
      <Sheet id="strategies" layout="portrait" heading={strategies.heading} lede={strategies.lede} caption={strategies.caption} media={<ClipSlot clip={strategies.clip}><StrategyClip /></ClipSlot>} />
      <Sheet
        id="baskets"
        layout="card"
        heading={baskets.heading}
        lede={baskets.lede}
        caption={baskets.caption}
        media={<BasketMix before={baskets.before} after={baskets.after} />}
      />
      <Sheet id="agent" layout="portrait" heading={agent.heading} lede={agent.lede} caption={agent.caption} media={<ClipSlot clip={agent.clip}><AgentClip /></ClipSlot>} />
      <Sheet id="brokers" layout="text" heading={brokers.heading} lede={brokers.lede}>
        <BrokerDialog
          style={i(2)}
          className="mt-8 flex h-12 items-center justify-center rounded-2 bg-brass-mark px-6 font-body text-ui font-medium text-on-brass md:inline-flex"
        />
        <p data-reveal style={i(3)} className="mt-4 text-body text-ink">
          {brokers.publicLine}
        </p>
      </Sheet>
      <Observers />
    </>
  );
}
