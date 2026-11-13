import { test } from "node:test";
import assert from "node:assert/strict";
import { hero } from "../src/landing/content.ts";
import { keyframe, pose, WEIGHTS_A, WEIGHTS_B } from "../src/landing/hero/ring.ts";

const deg = (r: number) => Math.round((r * 180) / Math.PI) || 0; // no -0
const at = (key: keyof ReturnType<typeof pose>) => [0, 0.4, 0.7, 1].map((p) => Number(pose(p)[key].toFixed(2)));

test("needle sweeps 38° by the 40% state and holds", () => {
  assert.deepEqual([0, 0.2, 0.4, 0.7, 1].map((p) => deg(pose(p).needle)), [0, -19, -38, -38, -38]);
});

test("rim turns geru by 40%, frays there and calms by 100%", () => {
  assert.deepEqual(at("sweep"), [0, 1, 1, 1]);
  assert.deepEqual(at("fray"), [0, 1, 0.99, 0]);
});

test("money moves between 44% and 74%, and the tilt flattens by 100%", () => {
  assert.equal(pose(0.44).mix, 0);
  assert.equal(pose(0.74).mix, 1);
  assert.deepEqual(at("tilt"), [1, 1.6, 1.6, 0]);
});

// The legend says the move in words (no figures on screen); the words must match what the ring draws.
test("the legend words match the weights the ring draws", () => {
  const top = Math.max(...WEIGHTS_A);
  assert.deepEqual(WEIGHTS_A.map((w) => (w === top ? "Most" : w >= 9 ? "Some" : "Low")), hero.legend.before);
  assert.deepEqual(WEIGHTS_A.map((a, k) => (WEIGHTS_B[k]! < a ? "Less" : WEIGHTS_B[k]! > a ? "More" : "Same")), hero.legend.after);
});

test("keyframe maps scroll px to ring progress through the dock points", () => {
  const docks = [0, 400, 700, 1000];
  const kf = (y: number) => Number(keyframe(y, docks).toFixed(3));
  assert.deepEqual([-50, 0, 200, 400, 550, 700, 850, 1000, 1200].map(kf), [0, 0, 0.2, 0.4, 0.55, 0.7, 0.85, 1, 1]);
  // Uneven docks (375: the text passes first): 40% lands exactly on its dock.
  assert.equal(keyframe(600, [0, 600, 800, 900]), 0.4);
});
