import { test } from "node:test";
import assert from "node:assert/strict";
import { gate, pinGate, type GateInputs } from "../src/landing/hero/gate.ts";

// Desktop 1280×800, WebGL2, motion allowed, device memory unknown, no data saver.
const desktop: GateInputs = {
  webgl2: true,
  reducedMotion: false,
  deviceMemory: undefined,
  saveData: undefined,
  effectiveType: undefined,
  viewportHeight: 800,
};

test("a capable desktop with unknown device memory passes", () => {
  assert.equal(gate(desktop), true);
  assert.equal(pinGate(desktop), true);
});

const failing: [string, Partial<GateInputs>][] = [
  ["no WebGL2", { webgl2: false }],
  ["reduced motion", { reducedMotion: true }],
  ["deviceMemory 2", { deviceMemory: 2 }],
  ["saveData on", { saveData: true }],
  ["3g", { effectiveType: "3g" }],
  ["2g", { effectiveType: "2g" }],
  ["slow-2g", { effectiveType: "slow-2g" }],
  ["landscape phone 844×390", { viewportHeight: 390 }],
];

for (const [name, change] of failing)
  test(`fails on its own: ${name}`, () => assert.equal(gate({ ...desktop, ...change }), false));

// User ruling 2026-11-13: a "3g" estimate still pins the poster; only the 3D ring stays off.
const pinsAnyway = ["no WebGL2", "3g"];

test("the pin gate ignores WebGL (checked after load) and a 3g estimate, but nothing else", () => {
  const noWebgl: GateInputs = { ...desktop, webgl2: false };
  assert.equal(pinGate(noWebgl), true);
  assert.equal(pinGate({ ...desktop, effectiveType: "3g" }), true);
  for (const [name, change] of failing.filter(([n]) => !pinsAnyway.includes(n)))
    assert.equal(pinGate({ ...desktop, ...change }), false, name);
});

test("boundaries: 4 GB and a 600px-tall viewport pass, 4g passes", () => {
  assert.equal(gate({ ...desktop, deviceMemory: 4, viewportHeight: 600, effectiveType: "4g" }), true);
  assert.equal(gate({ ...desktop, viewportHeight: 599 }), false);
});
