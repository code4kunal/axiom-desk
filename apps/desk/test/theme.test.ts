import { test } from "node:test";
import assert from "node:assert/strict";
import { resolveTheme, themeScript } from "../src/landing/theme.ts";

const stored = (v: string | null) => () => v;
const throwing = () => {
  throw new Error("SecurityError: storage blocked");
};

test("stored choice wins over the system preference", () => {
  assert.equal(resolveTheme(stored("light"), true), "light");
  assert.equal(resolveTheme(stored("dark"), false), "dark");
});

test("no stored choice follows the system", () => {
  assert.equal(resolveTheme(stored(null), true), "dark");
  assert.equal(resolveTheme(stored(null), false), "light");
});

test("storage that throws falls back to the system", () => {
  assert.equal(resolveTheme(throwing, true), "dark");
  assert.equal(resolveTheme(throwing, false), "light");
});

test("a tampered stored value is ignored", () => {
  assert.equal(resolveTheme(stored("purple"), true), "dark");
  assert.equal(resolveTheme(stored(""), false), "light");
});

test("the head script sets data-theme from storage before paint", () => {
  const el = { dataset: {} as Record<string, string> };
  const ctx = {
    document: { documentElement: el },
    localStorage: { getItem: () => "light" },
    matchMedia: () => ({ matches: true }),
  };
  new Function("document", "localStorage", "matchMedia", themeScript)(
    ctx.document,
    ctx.localStorage,
    ctx.matchMedia,
  );
  assert.equal(el.dataset.theme, "light");
});
