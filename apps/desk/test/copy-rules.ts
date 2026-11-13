// Shared by the copy, numbers and launch tests: every string the page can show comes from content.ts.
import * as content from "../src/landing/content.ts";

export type Leaf = { path: string; value: string; ancestors: unknown[] };

export function* walk(node: unknown, path = "", ancestors: unknown[] = []): Generator<Leaf> {
  if (typeof node === "string") yield { path, value: node, ancestors };
  else if (node && typeof node === "object")
    for (const [k, v] of Object.entries(node)) yield* walk(v, path ? `${path}.${k}` : k, [...ancestors, node]);
}

export const leaves = () => [...walk(content)];

// Whole words, case-insensitive; inflections listed explicitly so "buyer" stays legal.
const BANNED = [
  "returns",
  "guarantee",
  "guarantees",
  "guaranteed",
  "profit",
  "profits",
  "profitable",
  "buy",
  "buys",
  "buying",
  "sell",
  "sells",
  "selling",
  "tips",
  "beat the market",
  "beats the market",
  "beating the market",
];
const bannedRe = new RegExp(`\\b(${BANNED.join("|").replace(/ /g, "\\s+")})\\b`, "i");

export const bannedHit = (s: string) => s.match(bannedRe)?.[0] ?? null;

// A data figure: a date, or a number. Ordinals are not in content.ts (they're computed), and the
// capability count and the HTTP status are not data.
const EXEMPT = [/UP TO \d+ SYNCED CHARTS/i, /STATUS 404/];
const FIGURE = /\d{4}-\d{2}-\d{2}|\d+(?:\.\d+)?/g;

export function figures(s: string): string[] {
  const cleaned = EXEMPT.reduce((acc, re) => acc.replace(re, ""), s);
  return cleaned.match(FIGURE) ?? [];
}

// A figure is covered when its own string, or a sibling string of any enclosing object, says ILLUSTRATIVE.
export function covered(leaf: Leaf): boolean {
  if (/\bILLUSTRATIVE\b/.test(leaf.value)) return true;
  return leaf.ancestors.some((a) =>
    Object.values(a as object).some((v) => typeof v === "string" && /\bILLUSTRATIVE\b/.test(v)),
  );
}
