// Launch check only (pnpm launch): fails until the real desk contact replaces the placeholder.
import { test } from "node:test";
import assert from "node:assert/strict";
import { leaves } from "../copy-rules.ts";

test("the desk contact is a real address, not the reserved placeholder", () => {
  const placeholders = leaves()
    .filter((l) => l.value.includes("@axiom.invalid"))
    .map((l) => l.path);
  assert.deepEqual(placeholders, []);
});
