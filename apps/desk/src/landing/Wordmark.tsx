// "Axiom" with the i's dot replaced by a drawn geru tick (clipped i plus a drawn mark).
export function Wordmark({ className = "" }: { className?: string }) {
  return (
    <span
      role="img"
      aria-label="Axiom"
      className={`whitespace-nowrap font-display font-extrabold tracking-[-0.03em] leading-none text-ink ${className}`}
    >
      Ax
      <span className="relative inline-block">
        {/* A plain i clipped below its dot: a dotless ı pulls Eczar's 28 KB latin-ext file onto the LCP path. */}
        <span className="inline-block [clip-path:inset(0.29em_0_0_0)]">i</span>
        <span className="absolute left-1/2 bottom-[0.81em] h-[0.34em] w-[2px] -translate-x-[calc(50%_-_0.04em)] bg-geru-mark" />
      </span>
      om
    </span>
  );
}
