import type { CSSProperties } from "react";
import { agent } from "../content";

// One exchange with the agent: the question, three cited lines, then the sources they point to.
// Sized in container units so the type scales with the slot.
const at = (i: number): CSSProperties => ({ animationName: `clip-step-${i}` });

function Cite({ n }: { n: string }) {
  return (
    <span className="ml-[0.8cqw] inline-block rounded-1 border border-hairline px-[0.9cqw] align-[0.3cqw] font-mono text-[2.6cqw] leading-[3.6cqw] text-ink-dim">
      {n}
    </span>
  );
}

export function AgentClip() {
  const s = agent.scene;
  return (
    <div data-scene aria-hidden className="absolute inset-0 flex flex-col p-[5.5cqw] pt-[11cqw]">
      <p className="clip-step ml-auto max-w-[80%] rounded-2 border border-hairline bg-ground px-[3.5cqw] py-[2.6cqw] text-[max(14px,3.8cqw)] leading-[1.35] font-medium text-ink" style={at(0)}>
        {s.question}
      </p>
      <div className="mt-[4cqw] space-y-[2.4cqw] border-l-2 border-ink pl-[3.5cqw]">
        {s.answer.map((a, i) => (
          <p key={a.cite} className="clip-step text-[max(14px,3.6cqw)] leading-[1.4] text-ink" style={at(i + 1)}>
            {a.text}
            <Cite n={a.cite} />
          </p>
        ))}
      </div>
      <ol className="clip-step mt-[4cqw] border-t border-hairline font-mono text-[max(12px,2.8cqw)] uppercase text-ink-dim" style={at(4)}>
        {s.sources.map((src, i) => (
          <li key={src} className="flex gap-[2.5cqw] border-b border-hairline py-[1.8cqw]">
            <span className="text-ink">{i + 1}</span>
            {src}
          </li>
        ))}
      </ol>
      <p className="clip-step mt-[2.5cqw] text-[max(13px,3.4cqw)] text-ink-dim" style={at(5)}>
        {s.footnote}
      </p>
    </div>
  );
}
