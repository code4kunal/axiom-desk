import assert from "node:assert/strict";
import { test } from "node:test";
import { BAR_SECONDS, Replay } from "./replay.ts";

test("same seed gives the identical session, so both renderers draw the same bars", () => {
  const a = new Replay(3, 500, 30);
  const b = new Replay(3, 500, 30);
  assert.deepEqual(a.history, b.history);
  for (let i = 0; i < 200; i++) assert.deepEqual(a.next(), b.next());
});

test("ticks keep OHLC valid and open a new bar every ticksPerBar ticks", () => {
  const r = new Replay(1, 10, 5);
  let lastTime = r.history[r.history.length - 1]!.time;
  for (let i = 1; i <= 50; i++) {
    const { bar, isNew } = r.next();
    assert.equal(isNew, i % 5 === 0);
    if (isNew) {
      assert.equal(bar.time, lastTime + BAR_SECONDS);
      lastTime = bar.time;
    }
    assert.ok(bar.low <= Math.min(bar.open, bar.close) && bar.high >= Math.max(bar.open, bar.close));
  }
  for (const b of r.history) assert.ok(b.low <= Math.min(b.open, b.close) && b.high >= Math.max(b.open, b.close));
});
