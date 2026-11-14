import type {
  CapabilityInputs,
  CapabilityName,
  CapabilityOutputs,
  Envelope,
} from "../../../../packages/registry-ts/src/index.ts";

export class CapabilityCallError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }

  // The API answers a licence refusal with 403 "licence scope <scope> is not entitled"; a pane
  // shows "not entitled" for it, and "unavailable" for everything else.
  // shortcut: matches the registry's message text, move to a structured error code once the API sends one.
  get notEntitled(): boolean {
    return /^licence scope \S+ is not entitled$/.test(this.message);
  }
}

/** Call a capability from the browser through the desk's same-origin route; the session cookie rides along. */
export async function callCapability<N extends CapabilityName>(
  name: N,
  input: CapabilityInputs[N],
  fetchImpl: typeof fetch = fetch,
): Promise<Envelope<CapabilityOutputs[N]>> {
  const response = await fetchImpl(`/api/capabilities/${encodeURIComponent(name)}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(input),
  });
  const body: unknown = await response.json();
  if (!response.ok) {
    const error = (body as { error?: unknown }).error;
    throw new CapabilityCallError(response.status, typeof error === "string" ? error : JSON.stringify(error));
  }
  return body as Envelope<CapabilityOutputs[N]>;
}
