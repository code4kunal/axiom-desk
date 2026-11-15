// Every string a chart pane, rail or ticket head shows, except order-side words (order-labels.ts, KTD15).
// Tags are the non-colour cue (DESIGN.md §8.3): they shorten under 380px pane width and never drop.

export type Tag = { full: string; short: string; definition: string };

const tag = (full: string, definition: string, short = full): Tag => ({ full, short, definition });

export const tags = {
  callWall: tag("CALL WALL", "Call wall: strike with the most call open interest", "CW"),
  putWall: tag("PUT WALL", "Put wall: strike with the most put open interest", "PW"),
  maxPain: tag("MAX PAIN", "Max pain: strike where option holders lose the most at expiry", "MP"),
  poc: tag("POC", "Point of control: price traded most in the session"),
  nakedPoc: tag("nPOC", "Naked POC: an earlier session's point of control, not yet revisited"),
  vah: tag("VAH", "Value area high: top of the 70% of trade"),
  val: tag("VAL", "Value area low: bottom of the 70% of trade"),
  ib: tag("IB", "Initial balance: range of the first hour"),
  hvn: tag("HVN", "High-volume node: a price the market accepted"),
  lvn: tag("LVN", "Low-volume node: a price the market rejected"),
  singlePrints: tag("SP", "Single prints: prices traded in one period only"),
  stack: tag("STACK", "Stacked imbalance: adjacent prices where one side traded 3 to 1"),
  vwap: tag("VWAP", "Volume-weighted average price"),
  cone1: tag("1σ 68%", "Implied range: one standard deviation, about 68% of outcomes"),
  cone2: tag("2σ 95%", "Implied range: two standard deviations, about 95% of outcomes"),
  breakeven: tag("BE", "Breakeven: the price where the strategy neither gains nor loses at expiry"),
};

export const lanes = { call: "C", put: "P", bid: "BID", ask: "ASK" };

export const payoff = { maxGain: "max gain", maxLoss: "max loss" };

export const evidence = { forward: "forward return", samples: "Samples", grades: { cnf: "CNF", rac: "RAC", wl: "WL" } };

export const railTypes = {
  positioning: "POSITIONING",
  structure: "STRUCTURE",
  flow: "FLOW",
  regime: "REGIME",
  magnet: "MAGNET",
};

export const order = { staged: "STAGED", confirm: "Confirm order", clear: "Clear" };

export const replay = { banner: "REPLAY", backToLive: "Back to live" };
