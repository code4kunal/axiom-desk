import type { CapabilityInputs, CapabilityName, Envelope } from "./generated.ts";

export type { CapabilityInputs, CapabilityName, Envelope, Source } from "./generated.ts";
export { capabilityNames } from "./generated.ts";

export type Surface = "screen" | "command";

export class CapabilityError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

/** Call a registry capability over HTTP. The session token decides tenant and user. */
export async function callCapability<N extends CapabilityName>(
  baseUrl: string,
  token: string,
  name: N,
  input: CapabilityInputs[N],
  surface: Surface = "screen",
  fetchImpl: typeof fetch = fetch,
): Promise<Envelope> {
  const response = await fetchImpl(`${baseUrl}/capabilities/${name}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      "X-Axiom-Surface": surface,
    },
    body: JSON.stringify(input),
  });
  const body: unknown = await response.json();
  if (!response.ok) {
    const error = (body as { error?: unknown }).error;
    throw new CapabilityError(response.status, typeof error === "string" ? error : JSON.stringify(error));
  }
  return body as Envelope;
}
