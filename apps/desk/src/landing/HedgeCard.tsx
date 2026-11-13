import { Caption } from "./Caption";

// One content string: mono segments, then the human-confirms line (split at the last " · ").
export function HedgeCard({ text }: { text: string }) {
  const cut = text.lastIndexOf(" · ");
  return (
    <div className="rounded-2 border border-hairline bg-raised">
      <p className="px-3 py-3 font-mono text-caption uppercase text-ink-dim lg:px-4">
        <Caption text={text.slice(0, cut)} />
      </p>
      <p className="border-t border-hairline px-3 py-3 font-body text-ui font-medium text-ink lg:px-4">
        {text.slice(cut + 3)}
      </p>
    </div>
  );
}
