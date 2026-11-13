import type { CSSProperties } from "react";
import { BrokerDialog } from "@/landing/BrokerDialog";
import { ClipSlot } from "@/landing/ClipSlot";
import { agent, brokers, charts, evidence, hedge, options, problem } from "@/landing/content";
import { HedgeCard } from "@/landing/HedgeCard";
import { Hero } from "@/landing/hero/Hero";
import { Observers } from "@/landing/Observers";
import { Sheet } from "@/landing/sections/Sheet";
import { Specimen } from "@/landing/Specimen";

const i = (n: number) => ({ "--i": n }) as CSSProperties;

export default function Home() {
  return (
    <>
      <Hero />
      <Sheet id="problem" layout="text" heading={problem.heading} lede={problem.lede} />
      <Sheet id="charts" layout="clip" heading={charts.heading} caption={charts.caption} media={<ClipSlot clip={charts.clip} />} />
      <Sheet id="options" layout="portrait" heading={options.heading} caption={options.caption} media={<ClipSlot clip={options.clip} />} />
      <Sheet id="hedge" layout="card" heading={hedge.heading} lede={hedge.lede} media={<HedgeCard text={hedge.card} grid={hedge.grid} />} />
      <Sheet id="agent" layout="portrait" heading={agent.heading} lede={agent.lede} caption={agent.caption} media={<ClipSlot clip={agent.clip} />} />
      <Sheet id="evidence" layout="card" heading={evidence.heading} lede={evidence.lede} media={<Specimen />} />
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
