import assert from "node:assert/strict";
import { test } from "node:test";
import { frameStats, runStatus, summarise, TICK_FLOOR } from "./metrics.ts";
import { SESSIONS } from "./load.ts";
import { BAR_SECONDS, ticksPerSecond } from "./replay.ts";

// 1000 frames sorted: 995 x 8.3, 3 x 20, one 40, one 60. Expected values counted by hand:
// nearest rank p99.9 is rank 999 -> 40; p95 is rank 950 -> 8.3; one frame is over 50 ms.
const log = [...Array(995).fill(8.3), 20, 20, 20, 40, 60].reverse();

test("frameStats reports p99.9 and the count of frames over 50 ms on a fixed frame log", () => {
  const s = frameStats(log);
  assert.equal(s.p999, 40);
  assert.equal(s.over50ms, 1);
  assert.equal(s.p95, 8.3);
  assert.equal(s.max, 60);
  assert.equal(s.frames, 1000);
});

test("a frame of exactly 50 ms is not over 50 ms", () => {
  assert.equal(frameStats([8, 50, 51]).over50ms, 1);
});

const good = { p95: 8.3, p999: 20, over50ms: 0 };

test("fewer than 3 repeats is incomplete, even when every run is within limits", () => {
  assert.equal(summarise([good, good]).status, "incomplete");
  assert.equal(summarise([]).status, "incomplete");
});

test("3 repeats are judged against the frame limits: p95 16.7, p99.9 33, at most 3 frames over 50 ms", () => {
  assert.equal(summarise([good, good, good]).status, "pass");
  assert.equal(summarise([good, good, { ...good, p999: 34 }]).status, "fail");
  assert.equal(summarise([good, good, { ...good, p95: 17 }]).status, "fail");
  assert.equal(summarise([good, good, { ...good, over50ms: 4 }]).status, "fail");
  assert.equal(summarise([good, good, { ...good, over50ms: 3 }]).status, "pass");
});

const run = { ...good, pageErrors: [] as string[], ticksPerSecDelivered: 30 };

test("only an unmodified preset session can pass; a shortened or quick run within limits is incomplete", () => {
  assert.equal(runStatus([run, run, run], 30, true), "pass");
  assert.equal(runStatus([run, run, run], 30, false), "incomplete");
  assert.equal(runStatus([run, run, { ...run, p95: 17 }], 30, false), "fail");
});

test("a page error, a tick shortfall or an errored run voids the verdict", () => {
  assert.equal(runStatus([run, run, { ...run, pageErrors: ["draw threw"] }], 30, true), "error");
  assert.equal(runStatus([run, run, { ...run, ticksPerSecDelivered: 30 * TICK_FLOOR - 0.01 }], 30, true), "error");
  assert.equal(runStatus([run, run, { ...run, ticksPerSecDelivered: 30 * TICK_FLOOR }], 30, true), "pass");
  assert.equal(runStatus([run, run, { error: "ERROR: boom" }], 30, true), "error");
});

test("sessions: the budget session is 16 charts for 600 s x 3 at 60x, the footprint session is 4 charts", () => {
  assert.deepEqual(
    { c: SESSIONS.budget.charts, s: SESSIONS.budget.seconds, r: SESSIONS.budget.repeats, x: SESSIONS.budget.speed },
    { c: 16, s: 600, r: 3, x: 60 },
  );
  assert.equal(SESSIONS.footprint.charts, 4);
  assert.equal(SESSIONS.footprint.load, "footprint");
});

test("replay at 60x plays one bar-minute per wall second, so 30 ticks per bar is 30 ticks/s", () => {
  assert.equal(BAR_SECONDS, 60);
  assert.equal(ticksPerSecond(30, 60), 30);
  assert.equal(ticksPerSecond(30, 1), 0.5);
});
