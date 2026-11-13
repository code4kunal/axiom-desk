import { test } from "node:test";
import assert from "node:assert/strict";
import { bannedHit, leaves } from "./copy-rules.ts";

test("no string in the content module uses a banned phrase", () => {
  const hits = leaves()
    .map((l) => ({ path: l.path, hit: bannedHit(l.value) }))
    .filter((h) => h.hit);
  assert.deepEqual(hits, []);
});

test("a banned word planted in any field is caught", () => {
  for (const l of leaves())
    for (const word of ["Buy", "profits", "guaranteed"])
      assert.notEqual(bannedHit(`${l.value} ${word}`), null, `${l.path} + ${word}`);
});

test("matching is whole-word, case-insensitive, with listed inflections", () => {
  assert.equal(bannedHit("ask any buyer"), null);
  assert.equal(bannedHit("a sellout"), null);
  assert.equal(bannedHit("Buying power"), "Buying");
  assert.equal(bannedHit("past returns"), "returns");
  assert.equal(bannedHit("SELL"), "SELL");
  assert.equal(bannedHit("tools that beat  the market"), "beat  the market");
});

test("sharing metadata exists and is in the walked content", () => {
  const paths = leaves().map((l) => l.path);
  for (const p of ["meta.title", "meta.description", "meta.ogTitle", "meta.ogDescription"])
    assert.ok(paths.includes(p), `missing ${p}`);
});
