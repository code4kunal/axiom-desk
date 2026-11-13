// Fixed box from the clip's render size, so the placeholder, the still and the real clip share it.
const RATIO = { landscape: "1200 / 760", portrait: "720 / 900" } as const;

export function ClipSlot({ clip }: { clip: { label: string; shape: string } }) {
  const shape = clip.shape as keyof typeof RATIO;
  return (
    <div
      className={`relative w-full rounded-2 border border-hairline bg-raised ${shape === "portrait" ? "md:max-w-[432px] lg:max-w-none" : ""}`}
      style={{ aspectRatio: RATIO[shape] }}
    >
      <div aria-hidden className="absolute inset-4 rounded-1 border border-hairline" />
      <p className="absolute top-6 left-6 font-mono text-label font-medium uppercase text-ink-dim">{clip.label}</p>
    </div>
  );
}
