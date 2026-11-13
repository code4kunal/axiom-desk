import Link from "next/link";
import { sections, shell } from "./content";
import { NavSheet } from "./NavSheet";
import { ThemeMenu } from "./ThemeMenu";
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
        <div className="flex h-full items-center gap-4 xl:gap-6">
        <nav aria-label={shell.navLabel} className="h-full max-lg:hidden">
          <ol className="flex h-full items-stretch gap-4 xl:gap-6">
            {sections.map((s, i) => (
              <li key={s.id} className="flex">
                <Link
                  href={`/#${s.id}`}
                  className="-mx-2 flex items-center gap-2 border-y-2 border-transparent px-2 font-mono text-label font-medium uppercase text-ink-dim hover:text-ink focus-visible:outline-offset-[-2px] aria-[current=location]:border-b-brass-mark aria-[current=location]:text-brass"
                >
                  <span className="hidden font-normal xl:inline">{ordinal(i)}</span>
                  {s.label}
                </Link>
              </li>
            ))}
          </ol>
        </nav>
        <ThemeMenu />
        <NavSheet />
        </div>
      </div>
    </div>
  );
}
