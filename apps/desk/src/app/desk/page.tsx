import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Alert, Rail, me, primary } from "@/desk/shell";
import { desk } from "@/landing/content";

export async function generateMetadata(): Promise<Metadata> {
  return { title: { absolute: typeof (await me()) === "object" ? desk.title : desk.unreachable.title }, robots: { index: false } };
}

export default async function Desk() {
  const user = await me();
  if (user === "signed-out") redirect("/sign-in");
  if (user === "unreachable") {
    // Session state is unknown, so no Sign out; Reload is a plain full-page GET.
    const u = desk.unreachable;
    return (
      <>
        <Rail />
        <main id="main" className="frame pt-16 pb-24 md:pt-24">
          <div className="max-w-[48ch]">
            <p className="font-mono text-caption uppercase text-ink-dim">{u.caption}</p>
            <h1 className="mt-4 font-display text-legal-h1 font-bold text-balance">{u.heading}</h1>
            <Alert label={u.label}>{u.message}</Alert>
            <p className="mt-6 text-body text-ink-dim">{u.next}</p>
            <a href="/desk" className={`mt-8 w-full md:w-auto ${primary}`}>
              {u.reload}
            </a>
          </div>
        </main>
      </>
    );
  }
  return (
    <>
      <Rail>
        <form method="post" action="/auth/logout" className="flex h-full">
          <button
            type="submit"
            className="px-4 font-body text-ui font-medium text-ink hover:text-ink-dim focus-visible:outline-offset-[-2px]"
          >
            {desk.signOut}
          </button>
        </form>
      </Rail>
      <main id="main" className="frame pt-16 pb-24 md:pt-24">
        <p className="font-mono text-caption uppercase text-ink-dim">{desk.caption}</p>
        <h1 className="mt-4 font-display text-legal-h1 font-bold text-balance break-words">{user.name}</h1>
        <dl className="mt-6 border-b border-hairline">
          <div className="flex flex-col gap-2 border-t border-hairline py-4 md:flex-row md:items-baseline md:justify-between">
            <dt className="font-mono text-label uppercase text-ink-dim">{desk.tenantLabel}</dt>
            <dd className="font-mono text-ui font-medium break-words text-ink">{user.tenant}</dd>
          </div>
        </dl>
        <p className="mt-6 max-w-[48ch] text-body text-ink-dim">{desk.body}</p>
      </main>
    </>
  );
}
