// Launch check only (pnpm launch): fails while any clip slot still shows its placeholder still.
import { test } from "node:test";
import assert from "node:assert/strict";
import { leaves } from "../copy-rules.ts";

test("no clip slot still shows CLIP PLACEHOLDER", () => {
  const slots = leaves().filter((l) => /(^|\.)clip\./.test(l.path));
  assert.ok(slots.length > 0, "no clip slots found in content.ts");
  const placeholders = slots.filter((l) => l.value === "CLIP PLACEHOLDER").map((l) => l.path);
  assert.deepEqual(placeholders, []);
});
