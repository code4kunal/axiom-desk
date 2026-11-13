// Shared by the copy, numbers and launch tests: every string the page can show comes from content.ts.
import * as content from "../src/landing/content.ts";

export type Leaf = { path: string; value: string };

export function* walk(node: unknown, path = ""): Generator<Leaf> {
  if (typeof node === "string") yield { path, value: node };
  else if (node && typeof node === "object")
    for (const [k, v] of Object.entries(node)) yield* walk(v, path ? `${path}.${k}` : k);
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
const EXEMPT = [/UP TO \d+ SYNCED CHARTS/i, /STATUS 404/, /^STEP \d OF \d$/]; // counts and codes, not data
const FIGURE = /\d{4}-\d{2}-\d{2}|\d+(?:\.\d+)?/g;

export function figures(s: string): string[] {
  const cleaned = EXEMPT.reduce((acc, re) => acc.replace(re, ""), s);
  return cleaned.match(FIGURE) ?? [];
}

// Figures without their own label, and the caption the page renders right beside them. Listed by hand:
// sharing an object with some ILLUSTRATIVE string says nothing about what the visitor sees next to it.
export const COVERED_BY: Record<string, string> = {
  "hero.hole": "hero.plates", // the ring's hole reading sits beside the rail captions
  "hero.legend": "hero.plates", // the legend under the ring, same captions
  "charts.scene": "charts.clip", // the clip's ILLUSTRATIVE tag sits in the same frame
  "agent.scene": "agent.clip", // the clip's ILLUSTRATIVE tag sits in the same frame
};

const marked = (s: string) => /\bILLUSTRATIVE\b/.test(s);
const under = (path: string, prefix: string) => path === prefix || path.startsWith(`${prefix}.`);

// A figure is covered when its own string says ILLUSTRATIVE, or it is listed in COVERED_BY and that
// caption group says ILLUSTRATIVE.
export function covered(leaf: Leaf, all: Leaf[] = leaves()): boolean {
  if (marked(leaf.value)) return true;
  const by = Object.entries(COVERED_BY).find(([prefix]) => under(leaf.path, prefix))?.[1];
  return by !== undefined && all.some((l) => under(l.path, by) && marked(l.value));
}
