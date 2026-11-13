import { cookies } from "next/headers";
import type { ReactNode } from "react";
import { cache } from "react";
import { Wordmark } from "@/landing/Wordmark";

export type Me = { name: string; tenant: string } | "signed-out" | "unreachable";

// One /auth/me read per request, shared by generateMetadata and the page.
export const me = cache(async (): Promise<Me> => {
  // Outside the try: during prerender cookies() throws Next's own bail-out, which must not be swallowed.
  const cookie = (await cookies()).toString();
  try {
    const res = await fetch(`${process.env.AXIOM_API_ORIGIN}/auth/me`, { headers: { cookie }, cache: "no-store" });
    if (res.status === 401) return "signed-out";
    if (!res.ok) return "unreachable";
    return (await res.json()) as { name: string; tenant: string };
  } catch {
    return "unreachable"; // API down, refused connection, or no API origin configured
  }
});

export const primary =
  "inline-flex h-12 items-center justify-center rounded-2 bg-brass-mark px-6 font-body text-ui font-medium text-on-brass hover:bg-ink-dim";

export function Rail({ children }: { children?: ReactNode }) {
  return (
    <header className="sticky top-0 z-20 h-12 border-b border-hairline bg-ground">
      <div className="frame flex h-full items-center justify-between gap-6">
        <span className="flex h-12 items-center text-[20px] lg:text-[24px]">
          <Wordmark />
        </span>
        {children}
      </div>
    </header>
  );
}

// The 48ch working column every desk screen uses; at xl a hairline rule closes it off.
export function Column({ children }: { children: ReactNode }) {
  return (
    <main id="main" className="frame xl:grid xl:min-h-[calc(100dvh-3rem)] xl:grid-cols-12 xl:gap-x-6">
      <div className="max-w-[48ch] pt-16 pb-24 md:pt-24 xl:col-span-5">{children}</div>
      <div aria-hidden className="hidden border-l border-hairline xl:col-start-6 xl:block" />
    </main>
  );
}

export const alertId = "problem";

export function Alert({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div id={alertId} role="alert" className="mt-6 border-t-2 border-geru-mark pt-4">
      <p className="font-mono text-label font-medium uppercase text-geru">{label}</p>
      <p className="mt-2 text-body font-medium text-ink">{children}</p>
    </div>
  );
}
