import assert from "node:assert/strict";
import { test } from "node:test";

import { CapabilityError, callCapability } from "./index.ts";
import type { CapabilityOutputs, Envelope } from "./index.ts";

type Equal<A, B> = (<T>() => T extends A ? 1 : 2) extends <T>() => T extends B ? 1 : 2 ? true : false;

test("sends the token, surface and input to the capability route", async () => {
  let seen: { url: string; init: RequestInit } | undefined;
  const fakeFetch = (async (url: string, init: RequestInit) => {
    seen = { url, init };
    return new Response(JSON.stringify({ result_id: "res_1" }), { status: 200 });
  }) as typeof fetch;

  const envelope = await callCapability("http://api", "tok", "runs_latest", { kind: "regime" }, "command", fakeFetch);

  assert.equal(envelope.result_id, "res_1");
  assert.equal(seen?.url, "http://api/capabilities/runs_latest");
  const headers = seen?.init.headers as Record<string, string>;
  assert.equal(headers.Authorization, "Bearer tok");
  assert.equal(headers["X-Axiom-Surface"], "command");
  assert.deepEqual(JSON.parse(String(seen?.init.body)), { kind: "regime" });
});

test("raises with the status and server message on refusal", async () => {
  const fakeFetch = (async () =>
    new Response(JSON.stringify({ error: "licence scope internal-only is not entitled" }), {
      status: 403,
    })) as typeof fetch;

  await assert.rejects(
    callCapability("http://api", "tok", "runs_latest", { kind: "regime" }, "screen", fakeFetch),
    (err: unknown) => err instanceof CapabilityError && err.status === 403 && /licence/.test(err.message),
  );
});

// A probe capability with a concrete output: every real output is still `unknown`, which would make the check
// below pass even if callCapability dropped the output type. The check itself runs under `pnpm typecheck`.
declare module "./generated.ts" {
  interface CapabilityInputs {
    typing_probe: { id: string };
  }
  interface CapabilityOutputs {
    typing_probe: { score: number };
  }
}

test("types the envelope value with the capability's output", () => {
  type Returned = Awaited<ReturnType<typeof callCapability<"typing_probe">>>;
  const typed: Equal<Returned, Envelope<CapabilityOutputs["typing_probe"]>> = true;
  const value: Equal<Returned["value"], { score: number }> = true;
  assert.ok(typed && value);
});
