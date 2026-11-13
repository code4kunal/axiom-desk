import { test } from "node:test";
import assert from "node:assert/strict";
import { keyframe, pose } from "../src/landing/hero/ring.ts";

const deg = (r: number) => Math.round((r * 180) / Math.PI);

test("the four states: needle sweeps 38°, ring tilts 12° then settles flat", () => {
  assert.deepEqual([0, 0.4, 0.7, 1].map((p) => deg(pose(p).needle)), [30, -8, -8, -8]);
  assert.deepEqual([0, 0.4, 0.7, 1].map((p) => deg(pose(p).tilt)), [0, 12, 12, 0]);
});

test("ticks turn geru by 40%, and the basket reweights between 40% and 70%", () => {
  assert.equal(pose(0.1).geru, 0);
  assert.equal(pose(0.4).geru, 1);
  assert.deepEqual([0.4, 0.55, 0.7].map((p) => +pose(p).reweight.toFixed(6)), [0, 0.5, 1]);
});

test("keyframe maps scroll px to ring progress through the dock points", () => {
  const docks = [0, 400, 700, 1000];
  const at = (y: number) => Number(keyframe(y, docks).toFixed(3));
  assert.deepEqual([-50, 0, 200, 400, 550, 700, 850, 1000, 1200].map(at), [0, 0, 0.2, 0.4, 0.55, 0.7, 0.85, 1, 1]);
  // Uneven docks (375: the text passes first): 40% lands exactly on its dock.
  assert.equal(keyframe(600, [0, 600, 800, 900]), 0.4);
});
