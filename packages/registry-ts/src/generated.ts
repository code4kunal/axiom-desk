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

/** F&O contract rules, expiry cycle weekdays, lot value and ban status */
export interface FnoContractRulesInput {
  exchange: string;
  underlying: string;
  on: string;
}

/** Point-in-time instrument resolution, asset-class role and eligibility */
export interface InstrumentLookupInput {
  on: string;
  symbol?: string | null;
  instrument_id?: string | null;
  purpose?: "basket_member" | "order_draft_leg" | "basket_tracking_member" | null;
}

/** Latest published run of a kind (for example the current regime) */
export interface RunsLatestInput {
  kind: string;
}

/** Trading session status, holidays and adjacent sessions per segment */
export interface TradingCalendarInput {
  segment: string;
  on?: string | null;
  timestamp?: string | null;
}

export interface CapabilityInputs {
  fno_contract_rules: FnoContractRulesInput;
  instrument_lookup: InstrumentLookupInput;
  runs_latest: RunsLatestInput;
  trading_calendar: TradingCalendarInput;
}

export interface CapabilityOutputs {
  fno_contract_rules: unknown;
  instrument_lookup: unknown;
  runs_latest: unknown;
  trading_calendar: unknown;
}

export type CapabilityName = keyof CapabilityInputs;

export const capabilityNames: CapabilityName[] = ["fno_contract_rules", "instrument_lookup", "runs_latest", "trading_calendar"];
