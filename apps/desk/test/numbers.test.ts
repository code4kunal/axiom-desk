import { test } from "node:test";
import assert from "node:assert/strict";
import { covered, figures, leaves } from "./copy-rules.ts";

test("the page shows fewer than 20 data figures", () => {
  const all = leaves().flatMap((l) => figures(l.value).map((f) => `${l.path}: ${f}`));
  assert.ok(all.length < 20, `${all.length} figures:\n${all.join("\n")}`);
});

test("every data figure sits in a caption group marked ILLUSTRATIVE", () => {
  const bare = leaves()
    .filter((l) => figures(l.value).length > 0 && !covered(l))
    .map((l) => l.path);
  assert.deepEqual(bare, []);
});

test("the figure rules have bite", () => {
  assert.deepEqual(figures("BASE RATE 0.58 · N 212 · AS OF 2026-11-13"), ["0.58", "212", "2026-11-13"]);
  assert.deepEqual(figures("UP TO 8 SYNCED CHARTS"), []);
  const leaf = { path: "x", value: "CONF 0.74", ancestors: [{ caption: "CONF 0.74" }] };
  assert.equal(covered(leaf), false);
  assert.equal(covered({ ...leaf, ancestors: [{ rail: "N 212 · ILLUSTRATIVE", s: "CONF 0.74" }] }), true);
});
