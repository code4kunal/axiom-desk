"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Dialog } from "radix-ui";
import { useRef, useState } from "react";
import { sections, shell } from "./content";
import { Wordmark } from "./Wordmark";

const ordinal = (i: number) => String(i + 1).padStart(2, "0");

// Below 1024 (R13, R19): INDEX unfolds a full-screen sheet of the eight sections. The trigger stays a real
// link to the footer index, so it works before hydration or without JS.
export function NavSheet() {
  const [open, setOpen] = useState(false);
  const [current, setCurrent] = useState<string | null>(null);
  const target = useRef<string | null>(null);
  const router = useRouter();

  function onOpenChange(next: boolean) {
    // The rail's links carry the observer's aria-current even while hidden below 1024.
    if (next) setCurrent(document.querySelector("nav ol a[aria-current]")?.getAttribute("href")?.slice(2) ?? null);
    setOpen(next);
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Trigger asChild>
        <Link
          href="/#footer"
          onClick={(e) => {
            // Stops the footer jump; Radix then skips its own toggle, so open here.
            e.preventDefault();
            onOpenChange(true);
          }}
          className="-mx-2 flex h-12 min-w-12 items-center justify-end px-2 font-mono text-label font-medium uppercase text-ink focus-visible:outline-offset-[-2px] lg:hidden"
        >
          {shell.indexTrigger}
        </Link>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Content
          aria-describedby={undefined}
          className="overlay fixed inset-0 z-50 overflow-y-auto bg-ground"
          onCloseAutoFocus={(e) => {
            const id = target.current;
            target.current = null;
            if (!id) return; // closed without a choice: focus returns to INDEX
            e.preventDefault();
            const el = document.getElementById(id);
            // Legal pages and the 404 share this header but not the sections: go to the home page.
            if (!el) return router.push(`/#${id}`);
            history.pushState(null, "", `/#${id}`);
            el.scrollIntoView();
            el.setAttribute("tabindex", "-1");
            el.focus({ preventScroll: true });
          }}
        >
          <div className="sticky top-0 border-b border-hairline bg-ground">
            <div className="frame flex h-12 items-center justify-between">
              <Wordmark className="text-[20px]" />
              <Dialog.Close className="-mx-2 flex h-12 min-w-12 items-center justify-end px-2 font-mono text-label font-medium uppercase text-ink focus-visible:outline-offset-[-2px]">
                {shell.close}
              </Dialog.Close>
            </div>
          </div>
          <Dialog.Title className="sr-only">{shell.navLabel}</Dialog.Title>
          <nav aria-label={shell.navLabel} className="frame pt-4 pb-12">
            <ol>
              {sections.map((s, i) => (
                <li key={s.id} className="border-b border-hairline">
                  <Link
                    href={`/#${s.id}`}
                    aria-current={current === s.id ? "location" : undefined}
                    onClick={(e) => {
                      e.preventDefault();
                      target.current = s.id;
                      setOpen(false);
                    }}
                    className="relative flex h-14 items-center gap-4 pl-3 font-body text-[20px] font-medium text-ink focus-visible:outline-offset-[-2px] aria-[current=location]:before:absolute aria-[current=location]:before:inset-y-3 aria-[current=location]:before:left-0 aria-[current=location]:before:w-0.5 aria-[current=location]:before:bg-ink aria-[current=location]:before:content-['']"
                  >
                    <span className="w-6 font-mono text-label font-normal text-ink-dim">{ordinal(i)}</span>
                    {s.label}
                  </Link>
                </li>
              ))}
            </ol>
          </nav>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
