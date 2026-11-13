import type { ReactNode } from "react";

// Fixed box from the clip's render size, so the placeholder, the still and the real clip share it.
const RATIO = { landscape: "1200 / 760", portrait: "720 / 900" } as const;

// The scene is a CSS-animated sample screen (no JS); its static styles are the last frame, which is
// what reduced motion shows. The label (ILLUSTRATIVE) stays in the corner of every frame.
export function ClipSlot({ clip, children }: { clip: { label: string; shape: string }; children?: ReactNode }) {
  const shape = clip.shape as keyof typeof RATIO;
  return (
    <div
      className={`clip relative w-full overflow-hidden rounded-2 border border-hairline bg-raised ${shape === "portrait" ? "md:max-w-[432px] lg:max-w-none" : ""}`}
      style={{ aspectRatio: RATIO[shape] }}
    >
      {children ?? <div aria-hidden className="absolute inset-4 rounded-1 border border-hairline" />}
      <p className="absolute top-[3.5cqw] right-[3.5cqw] font-mono text-label font-medium uppercase text-ink">{clip.label}</p>
    </div>
  );
}
