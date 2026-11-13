import Link from "next/link";
import { sections, shell } from "./content";
import { Wordmark } from "./Wordmark";

const ordinal = (i: number) => String(i + 1).padStart(2, "0");

export function Nav() {
  return (
    <div className="sticky top-0 z-20 h-12 border-b border-hairline bg-ground">
      <div className="frame flex h-full items-center justify-between gap-6">
        <header>
          <Link href="/" className="flex h-12 items-center focus-visible:outline-offset-[-2px] text-[20px] lg:text-[24px]">
            <Wordmark />
          </Link>
        </header>
        <nav aria-label={shell.navLabel} className="h-full">
          <ol className="hidden h-full items-stretch gap-4 lg:flex xl:gap-6">
            {sections.map((s, i) => (
              <li key={s.id} className="flex">
                <Link
                  href={`/#${s.id}`}
                  className="-mx-2 flex items-center gap-2 px-2 font-mono text-label focus-visible:outline-offset-[-2px] font-medium uppercase text-ink-dim hover:text-ink"
                >
                  <span className="hidden font-normal xl:inline">{ordinal(i)}</span>
                  {s.label}
                </Link>
              </li>
            ))}
          </ol>
          {/* shortcut: links to the footer index until the mobile nav sheet exists. */}
          <Link
            href="/#footer"
            className="-mx-2 flex h-12 min-w-12 items-center justify-end px-2 font-mono focus-visible:outline-offset-[-2px] text-label font-medium uppercase text-ink lg:hidden"
          >
            {shell.indexTrigger}
          </Link>
        </nav>
      </div>
    </div>
  );
}
