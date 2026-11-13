import Link from "next/link";
import { sections, shell } from "../content";
import { Wordmark } from "../Wordmark";

export function Footer() {
  return (
    <footer id="footer" className="border-t border-hairline pt-16 pb-12 lg:pt-24 lg:pb-16">
      <div className="frame grid grid-cols-4 gap-x-4 gap-y-8 md:grid-cols-8 md:gap-x-6 lg:grid-cols-12">
        <div className="col-span-4 md:col-span-4 lg:col-span-5">
          <Wordmark className="text-[24px]" />
          <p className="mt-6 max-w-[40ch] text-small text-ink">{shell.disclaimer}</p>
        </div>

        <div className="col-span-4 md:col-span-2 lg:col-span-3 lg:col-start-7">
          <h2 className="sr-only">{shell.footerIndexLabel}</h2>
          <ol className="border-t border-hairline">
            {sections.map((s, i) => (
              <li key={s.id} className="border-b border-hairline">
                <Link
                  href={`/#${s.id}`}
                  className="flex h-12 items-center gap-3 font-mono text-label font-medium uppercase text-ink-dim hover:text-ink"
                >
                  <span className="font-normal">{String(i + 1).padStart(2, "0")}</span>
                  {s.label}
                </Link>
              </li>
            ))}
          </ol>
        </div>

        <div className="col-span-4 flex flex-col gap-4 md:col-span-2 lg:col-span-3 lg:col-start-10">
          <ul className="flex gap-6">
            <li>
              <Link href="/privacy" className="link flex h-12 min-w-12 items-center text-small">
                {shell.privacy}
              </Link>
            </li>
            <li>
              <Link href="/terms" className="link flex h-12 min-w-12 items-center text-small">
                {shell.terms}
              </Link>
            </li>
          </ul>
        </div>
      </div>
      <div className="frame mt-12">
        <p className="border-t border-hairline pt-4 font-mono text-caption uppercase text-balance text-ink-dim">
          {shell.footerCaption}
        </p>
      </div>
    </footer>
  );
}
