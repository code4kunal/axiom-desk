// Composes the 1200×630 sharing image (ring at 0% + the statement) on a running build, so it uses the
// self-hosted fonts and tokens. Run: node scripts/render-og.ts http://localhost:3101  (from apps/desk)
import { writeFileSync, mkdirSync } from "node:fs";
import { createRequire } from "node:module";
import { join } from "node:path";
import { chromium } from "@playwright/test";
import { hero } from "../src/landing/content.ts";

const require = createRequire(import.meta.url);
// Only the encoder calls used here; sharp has no types resolvable from this package.
type Encoder = { avif(o: object): Encoder; webp(o: object): Encoder; jpeg(o: object): Encoder; toBuffer(): Promise<Buffer> };
const sharp = createRequire(require.resolve("next/package.json"))("sharp") as (input: Buffer) => Encoder;

const base = process.argv[2];
if (!base) throw new Error("usage: node scripts/render-og.ts <base-url>");
const out = join(import.meta.dirname, "../public/og");
mkdirSync(out, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, colorScheme: "dark" });
await page.goto(base);
await page.evaluate(
  ({ statement, rail }) => {
    document.body.innerHTML = `
    <div style="position:fixed;inset:0;display:grid;grid-template-columns:630px 1fr;background:var(--color-ground);color:var(--color-ink)">
      <img src="/hero/poster-0-dark.webp" style="width:630px;height:630px;display:block" alt="">
      <div style="display:flex;flex-direction:column;justify-content:space-between;padding:56px 56px 48px 40px">
        <p style="font:800 30px/1 var(--font-display);letter-spacing:-0.03em">Axiom</p>
        <p style="font:800 44px/1.02 var(--font-display);letter-spacing:-0.02em;text-wrap:balance">${statement}</p>
        <p style="font:400 13px/1.5 var(--font-mono);letter-spacing:0.06em;color:var(--color-ink-dim);border-top:1px solid var(--color-hairline);padding-top:12px">${rail}</p>
      </div>
    </div>`;
    window.scrollTo(0, 0);
  },
  { statement: hero.statement, rail: hero.plates[0]!.caption },
);
await page.evaluate(() => Promise.all([document.fonts.ready, ...[...document.images].map((i) => i.decode())]));
const png = await page.screenshot({ type: "png" });
const jpg = await sharp(png).jpeg({ quality: 82, mozjpeg: true }).toBuffer();
writeFileSync(join(out, "og-1200x630.jpg"), jpg);
await browser.close();
console.log(`og image ${jpg.length} bytes`);
