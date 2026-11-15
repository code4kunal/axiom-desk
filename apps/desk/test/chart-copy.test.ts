// KTD15: on the desk, "buy" and "sell" are allowed only in order-labels.ts; every other chart string keeps
// the landing ban list, unchanged (R157, R171, R179).
import { test } from "node:test";
import assert from "node:assert/strict";
import { bannedHit, chartLeaves, orderLeaves } from "./copy-rules.ts";

test("no chart string uses a banned phrase", () => {
  const hits = chartLeaves()
    .map((l) => ({ path: l.path, hit: bannedHit(l.value) }))
    .filter((h) => h.hit);
  assert.deepEqual(hits, []);
});

test("buy or sell planted in any chart string outside order-labels is caught", () => {
  assert.ok(chartLeaves().length > 0);
  for (const l of chartLeaves())
    for (const word of ["buy", "SELL"]) assert.notEqual(bannedHit(`${l.value} ${word}`), null, `${l.path} + ${word}`);
});

test("order labels may say buy and sell, and nothing else from the ban list", () => {
  const leaves = orderLeaves();
  assert.ok(leaves.some((l) => /\bbuy\b/i.test(l.value)) && leaves.some((l) => /\bsell\b/i.test(l.value)));
  for (const l of leaves) {
    assert.equal(bannedHit(l.value, "order"), null, l.path);
    for (const word of ["profit", "returns", "guaranteed"])
      assert.notEqual(bannedHit(`${l.value} ${word}`, "order"), null, `${l.path} + ${word}`);
  }
});

test("payoff and evidence wording uses max gain, max loss and forward return", () => {
  const values = chartLeaves().map((l) => l.value);
  for (const phrase of ["max gain", "max loss", "forward return"])
    assert.ok(values.some((v) => v.toLowerCase().includes(phrase)), phrase);
});
