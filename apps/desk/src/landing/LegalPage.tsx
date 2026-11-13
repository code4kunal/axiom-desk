import Link from "next/link";

type Legal = { caption: string; title: string; stamp: string; notice: string; body: readonly string[]; back: string };

export function LegalPage({ copy }: { copy: Legal }) {
  return (
    <div className="frame pt-24 pb-24">
      <div className="max-w-[64ch]">
        <p className="font-mono text-caption uppercase text-ink-dim">{copy.caption}</p>
        <h1 className="mt-4 font-display text-legal-h1 font-bold text-balance">{copy.title}</h1>
        <p
          role="note"
          className="mt-8 flex items-center gap-4 rounded-2 border border-hairline bg-raised p-4 text-small text-ink"
        >
          <span className="stamp text-stamp-rac">{copy.stamp}</span>
          {copy.notice}
        </p>
        {copy.body.map((p) => (
          <p key={p} className="mt-6 text-legal-body text-ink">
            {p}
          </p>
        ))}
        <p className="mt-8">
          <Link href="/" className="link inline-flex h-12 items-center text-body">
            {copy.back}
          </Link>
        </p>
      </div>
    </div>
  );
}
