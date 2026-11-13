// "Axiom" with the i's dot replaced by a 2 x 10 px brass tick (dotless i plus a drawn mark).
export function Wordmark({ className = "" }: { className?: string }) {
  return (
    <span
      role="img"
      aria-label="Axiom"
      className={`font-display font-extrabold tracking-[-0.03em] leading-none text-ink ${className}`}
    >
      Ax
      <span className="relative inline-block">
        ı
        <span className="absolute left-1/2 bottom-[0.81em] h-[0.34em] w-[2px] -translate-x-[calc(50%_-_0.04em)] bg-brass-mark" />
      </span>
      om
    </span>
  );
}
