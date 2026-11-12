// Generated from the capability registry by `uv run python -m axiom_api.codegen`.
// Do not edit by hand.

export interface Source {
  name: string;
  licence_scope: string;
}

export interface Envelope<T = unknown> {
  result_id: string;
  capability: string;
  version: string;
  inputs_hash: string;
  value: T;
  as_of: string;
  method: string;
  sources: Source[];
  limitations: string[];
  evidence_ref: string | null;
  calibration_status: string | null;
}

/** Latest published run of a kind (for example the current regime) */
export interface RunsLatestInput {
  kind: string;
}

export interface CapabilityInputs {
  runs_latest: RunsLatestInput;
}

export type CapabilityName = keyof CapabilityInputs;

export const capabilityNames: CapabilityName[] = ["runs_latest"];
