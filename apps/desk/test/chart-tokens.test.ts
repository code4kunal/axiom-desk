// R217: every chart colour role in DESIGN.md §8.2 ships in globals.css with its light and dark value,
// and §8.3 pairs it with a non-colour cue (R197). Roles are read from DESIGN.md, not listed here.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const design = readFileSync(new URL("../../../DESIGN.md", import.meta.url), "utf8");
const css = readFileSync(new URL("../src/app/globals.css", import.meta.url), "utf8");

const section = (from: string, to: string) => design.slice(design.indexOf(from), design.indexOf(to));
const s82 = section("### 8.2", "### 8.3");
const s83 = section("### 8.3", "### 8.4");

const roles = [...s82.matchAll(/^\|[^|]+\| `--c-([a-z]+)` \| `(#\w{6})` \| `(#\w{6})` \| `(#\w{6})` \|/gm)].map(
  ([, name, text, mark, dark]) => ({ name: name!, text: text!, mark: mark!, dark: dark! }),
);
const heat = [...s82.matchAll(/^\| (\d) \| `(#\w{6})` \| [\d.]+ \| `(#\w{6})` \|/gm)].map(([, step, light, dark]) => ({
  step: step!,
  light: light!,
  dark: dark!,
}));

// Declarations of the first block whose selector starts with `head`.
function block(head: string): Map<string, string> {
  const start = css.indexOf(head);
  assert.notEqual(start, -1, `globals.css has no ${head}`);
  const open = css.indexOf("{", start);
  let depth = 0;
  let end = open;
  for (; end < css.length; end++) {
    if (css[end] === "{") depth++;
    else if (css[end] === "}" && --depth === 0) break;
  }
  const body = css.slice(open + 1, end);
  return new Map([...body.matchAll(/(--[\w-]+):\s*([^;]+);/g)].map(([, k, v]) => [k!, v!.trim()]));
}

const light = block("@theme static");
const darkSets = [':root[data-theme="dark"]', "@media (prefers-color-scheme: dark)"].map(
  (head) => new Map([...light, ...block(head)]),
);

function resolve(vars: Map<string, string>, name: string, seen = 0): string | undefined {
  const v = vars.get(name);
  const alias = v?.match(/^var\((--[\w-]+)\)$/);
  return alias && seen < 8 ? resolve(vars, alias[1]!, seen + 1) : v?.toLowerCase();
}

test("DESIGN.md §8.2 lists the chart roles and the six heat steps", () => {
  assert.ok(roles.length >= 7, `parsed ${roles.length} roles`);
  assert.equal(heat.length, 6);
});

test("every chart role has its light text, light mark and dark token", () => {
  for (const r of roles) {
    const t = `--color-c-${r.name}`;
    assert.equal(resolve(light, t), r.text.toLowerCase(), `${t} light`);
    assert.equal(resolve(light, `${t}-mark`), r.mark.toLowerCase(), `${t}-mark light`);
    for (const dark of darkSets) {
      assert.equal(resolve(dark, t), r.dark.toLowerCase(), `${t} dark`);
      assert.equal(resolve(dark, `${t}-mark`), r.dark.toLowerCase(), `${t}-mark dark`);
    }
  }
});

test("every heat step has its light and dark token", () => {
  for (const h of heat) {
    const t = `--color-heat-${h.step}`;
    assert.equal(resolve(light, t), h.light.toLowerCase(), `${t} light`);
    for (const dark of darkSets) assert.equal(resolve(dark, t), h.dark.toLowerCase(), `${t} dark`);
  }
});

test("every chart role is paired with a non-colour cue in §8.3", () => {
  const rows = s83.split("\n").filter((l) => /^\| (?!Element|---)/.test(l));
  for (const r of roles) {
    const row = rows.find((l) => l.includes(`--c-${r.name}`));
    assert.ok(row, `--c-${r.name} has no row in §8.3`);
    const cue = row.split("|")[3]?.trim();
    assert.ok(cue, `--c-${r.name} row has an empty cue`);
  }
});
