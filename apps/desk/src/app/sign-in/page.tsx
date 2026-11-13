import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Alert, Rail, me, primary } from "@/desk/shell";
import { signIn, signInErrors } from "@/landing/content";

type Props = { searchParams: Promise<{ error?: string | string[] }> };

// The code is never shown: an unknown one gets the generic copy, a missing one gets no message.
async function problem({ searchParams }: Props) {
  const { error } = await searchParams;
  if (error === undefined) return null;
  return typeof error === "string" && Object.hasOwn(signInErrors, error)
    ? signInErrors[error as keyof typeof signInErrors]
    : signInErrors.failed;
}

export async function generateMetadata(props: Props): Promise<Metadata> {
  return { title: { absolute: (await problem(props)) ? signIn.errorTitle : signIn.title }, robots: { index: false } };
}

export default async function SignIn(props: Props) {
  if (typeof (await me()) === "object") redirect("/desk");
  const error = await problem(props);
  return (
    <>
      <Rail />
      <main id="main" className="frame xl:grid xl:min-h-[calc(100dvh-3rem)] xl:grid-cols-12 xl:gap-x-6">
        <div className="max-w-[48ch] pt-16 pb-24 md:pt-24 xl:col-span-5">
          <p className="font-mono text-caption uppercase text-ink-dim">{signIn.caption}</p>
          <h1 className="mt-4 font-display text-legal-h1 font-bold text-balance">{signIn.heading}</h1>
          {error && (
            <Alert label={error.label}>
              {error.message} {error.next}
            </Alert>
          )}
          <p className="mt-6 text-body text-ink-dim">{signIn.body}</p>
          {/* A plain anchor: sign-in is a full-page GET to the API, never a client-side route. */}
          <a href="/auth/login" className={`mt-8 w-full md:w-auto ${primary}`}>
            {signIn.action}
          </a>
          <p className="mt-6 text-small text-ink-dim">{signIn.hint}</p>
        </div>
        <div aria-hidden className="hidden border-l border-hairline xl:col-start-6 xl:block" />
      </main>
    </>
  );
}
