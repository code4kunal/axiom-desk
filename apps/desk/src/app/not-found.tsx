import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "@/landing/content";

// Next adds the noindex robots tag to not-found responses itself.
export const metadata: Metadata = { title: notFound.title };

export default function NotFound() {
  return (
    <div className="frame pt-32 pb-24">
      <div className="max-w-[48ch] lg:max-w-[60%]">
        <p className="font-mono text-caption uppercase text-ink-dim">{notFound.caption}</p>
        <h1 className="mt-4 font-display text-legal-h1 font-bold text-balance">{notFound.heading}</h1>
        <p className="mt-6 max-w-[48ch] text-body text-ink-dim">{notFound.body}</p>
        <Link
          href="/"
          className="mt-8 inline-flex h-12 items-center rounded-2 bg-brass-mark px-6 font-body text-ui font-medium text-on-brass"
        >
          {notFound.home}
        </Link>
        <p className="mt-6 text-small text-ink-dim">{notFound.hint}</p>
      </div>
    </div>
  );
}
