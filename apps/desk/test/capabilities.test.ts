import { after, before, beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import { createServer, type IncomingHttpHeaders, type Server } from "node:http";
import type { AddressInfo } from "node:net";
import { POST } from "../src/app/api/capabilities/[name]/route.ts";
import { callCapability, CapabilityCallError } from "../src/desk/capabilities.ts";

// The API is a separate process; this stub stands in for it and records what the route sent.
type Seen = { url: string; headers: IncomingHttpHeaders; body: string };
let seen: Seen[] = [];
let reply: { status: number; body: unknown } = { status: 200, body: {} };
let api: Server;

before(async () => {
  api = createServer((req, res) => {
    let body = "";
    req.on("data", (chunk: Buffer) => (body += chunk.toString()));
    req.on("end", () => {
      seen.push({ url: req.url ?? "", headers: req.headers, body });
      res.writeHead(reply.status, { "content-type": "application/json" });
      res.end(JSON.stringify(reply.body));
    });
  });
  await new Promise<void>((resolve) => api.listen(0, "127.0.0.1", resolve));
  process.env.AXIOM_API_ORIGIN = `http://127.0.0.1:${(api.address() as AddressInfo).port}`;
});

after(() => api.close());

beforeEach(() => {
  seen = [];
  reply = { status: 200, body: {} };
});

const desk = "http://localhost:3100";
const signedIn = "__Host-axiom_session=tok-123; theme=dark";

function call(name: string, headers: Record<string, string>, body: unknown = { kind: "regime" }) {
  const request = new Request(`${desk}/api/capabilities/${encodeURIComponent(name)}`, {
    method: "POST",
    headers: { "content-type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
  return POST(request, { params: Promise.resolve({ name }) });
}

// What a browser on the desk does: relative URL, same-origin Origin, session cookie attached.
const browserFetch = ((url: string, init: RequestInit) => {
  const name = decodeURIComponent(url.split("/").pop() ?? "");
  const request = new Request(new URL(url, desk), {
    ...init,
    headers: { ...(init.headers as Record<string, string>), origin: desk, cookie: signedIn },
  });
  return POST(request, { params: Promise.resolve({ name }) });
}) as typeof fetch;

const envelope = {
  result_id: "r-1",
  capability: "runs_latest",
  version: "1",
  inputs_hash: "h",
  value: { run_id: "run-9", kind: "regime", payload: { state: "trend" } },
  as_of: "2026-11-14T09:15:00+05:30",
  method: "latest published run",
  sources: [{ name: "nse_bhavcopy", licence_scope: "public" }],
  limitations: [],
  evidence_ref: null,
  calibration_status: null,
};

test("a signed-in same-origin call reaches the API as Bearer on the screen surface and returns its envelope", async () => {
  reply = { status: 200, body: envelope };
  const res = await call("runs_latest", { origin: desk, cookie: signedIn });
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), envelope);
  assert.equal(seen.length, 1);
  const [sent] = seen;
  assert.equal(sent?.url, "/capabilities/runs_latest");
  assert.equal(sent?.headers.authorization, "Bearer tok-123");
  assert.equal(sent?.headers["x-axiom-surface"], "screen");
  assert.equal(sent?.headers.cookie, undefined);
  assert.deepEqual(JSON.parse(sent?.body ?? ""), { kind: "regime" });
});

test("the browser caller returns the typed envelope", async () => {
  reply = { status: 200, body: envelope };
  const got = await callCapability("runs_latest", { kind: "regime" }, browserFetch);
  assert.deepEqual(got, envelope);
});

test("no session cookie is 401 and never reaches the API", async () => {
  const res = await call("runs_latest", { origin: desk, cookie: "theme=dark" });
  assert.equal(res.status, 401);
  assert.equal(seen.length, 0);
});

test("a cross-origin POST is 403 and never reaches the API", async () => {
  const res = await call("runs_latest", { origin: "https://evil.example", cookie: signedIn });
  assert.equal(res.status, 403);
  assert.equal(seen.length, 0);
});

test("a POST with no Origin header is 403", async () => {
  const res = await call("runs_latest", { cookie: signedIn });
  assert.equal(res.status, 403);
  assert.equal(seen.length, 0);
});

test("the capability name cannot walk to another API path", async () => {
  reply = { status: 404, body: { error: "capability not found" } };
  await call("../auth/me", { origin: desk, cookie: signedIn });
  assert.equal(seen[0]?.url, "/capabilities/..%2Fauth%2Fme");
});

for (const status of [401, 403, 404, 422]) {
  test(`an API ${status} passes through with its body`, async () => {
    reply = { status, body: { error: `api said ${status}` } };
    const res = await call("runs_latest", { origin: desk, cookie: signedIn });
    assert.equal(res.status, status);
    assert.deepEqual(await res.json(), { error: `api said ${status}` });
  });
}

// The registry's refusal text: Forbidden(f"licence scope {scope} is not entitled").
test("a licence refusal reaches the browser as not entitled, distinct from 404", async () => {
  reply = { status: 403, body: { error: "licence scope nse_fo_realtime is not entitled" } };
  const refused = await callCapability("runs_latest", { kind: "regime" }, browserFetch).catch((e: unknown) => e);
  assert.ok(refused instanceof CapabilityCallError);
  assert.equal(refused.status, 403);
  assert.equal(refused.notEntitled, true);

  reply = { status: 404, body: { error: "run regime not found" } };
  const missing = await callCapability("runs_latest", { kind: "regime" }, browserFetch).catch((e: unknown) => e);
  assert.ok(missing instanceof CapabilityCallError);
  assert.equal(missing.status, 404);
  assert.equal(missing.notEntitled, false);
});

test("any other 403 is not reported as not entitled", async () => {
  reply = { status: 403, body: { error: "runs_latest is not available on the screen surface" } };
  const refused = await callCapability("runs_latest", { kind: "regime" }, browserFetch).catch((e: unknown) => e);
  assert.ok(refused instanceof CapabilityCallError);
  assert.equal(refused.notEntitled, false);
});

test("an unreachable API is 502", async () => {
  const live = process.env.AXIOM_API_ORIGIN;
  process.env.AXIOM_API_ORIGIN = "http://127.0.0.1:1"; // nothing listens on port 1
  try {
    const res = await call("runs_latest", { origin: desk, cookie: signedIn });
    assert.equal(res.status, 502);
  } finally {
    process.env.AXIOM_API_ORIGIN = live;
  }
});
