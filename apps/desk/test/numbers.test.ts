import { test } from "node:test";
import assert from "node:assert/strict";
import { covered, figures, leaves } from "./copy-rules.ts";

// R3 (amended 2026-11-13): the hero repeats one reading in the hole, rail and legend, so the cap counts distinct values.
test("the page shows fewer than 20 distinct data figures", () => {
  const all = leaves().flatMap((l) => figures(l.value).map((f) => ({ f, at: `${l.path}: ${f}` })));
  const distinct = new Set(all.map((x) => x.f));
  assert.ok(distinct.size < 20, `${distinct.size} distinct figures:\n${all.map((x) => x.at).join("\n")}`);
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
  const captions = [{ path: "hero.plates.0.caption", value: "N 212 · ILLUSTRATIVE" }];
  assert.equal(covered({ path: "x", value: "N 212 · ILLUSTRATIVE" }, captions), true);
  // A headline figure next to a labelled sibling is not covered: only listed caption groups count.
  assert.equal(covered({ path: "hero.statement", value: "Up 23% this year" }, [...captions, { path: "hero.hedgeCard", value: "ILLUSTRATIVE" }]), false);
  assert.equal(covered({ path: "hero.hole.0.conf", value: "CONF 0.74" }, captions), true);
  assert.equal(covered({ path: "hero.hole.0.conf", value: "CONF 0.74" }, []), false);
});
