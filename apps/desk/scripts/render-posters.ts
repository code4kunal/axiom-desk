// Renders the hero ring at 0/40/70/100 in both themes with the real ring module, then encodes the
// posters (AVIF + WebP, 960×960). Run: node scripts/render-posters.ts  (from apps/desk)
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { chromium } from "@playwright/test";
import ts from "typescript";

const require = createRequire(import.meta.url);
// Only the encoder calls used here (resize included); sharp has no types resolvable from this package.
type Encoder = { resize(w: number): Encoder; avif(o: object): Encoder; webp(o: object): Encoder; jpeg(o: object): Encoder; toBuffer(): Promise<Buffer> };
// sharp ships with Next; borrow it rather than adding a dependency for a build-time script.
const sharp = createRequire(require.resolve("next/package.json"))("sharp") as (input: Buffer) => Encoder;

const root = join(import.meta.dirname, "..");
const threeBuild = dirname(require.resolve("three")); // three/build/three.cjs
const out = join(root, "public/hero");
mkdirSync(out, { recursive: true });

// Token values straight from globals.css: light (primary) in @theme, dark under [data-theme="dark"].
const css = readFileSync(join(root, "src/app/globals.css"), "utf8");
function tokens(block: string, dark: boolean) {
  const get = (name: string) => {
    const m = block.match(new RegExp(`--color-${name}:\\s*(#[0-9a-f]{6})`, "i"));
    if (!m) throw new Error(`token ${name} not found`);
    return m[1]!;
  };
  return {
    ground: get("ground"),
    ink: get("ink"),
    inkFaint: get("ink-faint"),
    geruMark: get("geru-mark"),
    marks: ["equity", "gilts", "gold", "cash", "intl"].map((k) => get(`${k}-mark`)),
    dark,
  };
}
const palettes = {
  light: tokens(css.slice(css.indexOf("@theme"), css.indexOf(":root {")), false),
  dark: tokens(css.slice(css.indexOf(':root[data-theme="dark"]')), true),
};

const ringJs = ts.transpileModule(readFileSync(join(root, "src/landing/hero/ring.ts"), "utf8"), {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
}).outputText;

const html = `<!doctype html><script type="importmap">{"imports":{"three":"/three/three.module.js"}}</script>
<canvas id="c" width="1200" height="1200"></canvas>
<script type="module">
import { createRing } from "/ring.js";
window.render = (palette, p) => {
  const c = document.getElementById("c");
  // 480 CSS px at DPR 2.5 = 1200 device px: dots and needle match the live canvas at display size.
  const ring = window.ring ??= createRing(c, palette, { dpr: 2.5, narrow: false, preserveDrawingBuffer: true });
  ring.resize(480, 480);
  ring.setPalette(palette);
  ring.setProgress(p);
  ring.frame(10, 0); // a long dt settles the tilt; t 0 freezes the breath
  return c.toDataURL("image/png");
};
window.ready = true;
</script>`;

const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const page = await browser.newPage({ viewport: { width: 1200, height: 1200 } });
await page.route("http://render.local/**", (route) => {
  const path = new URL(route.request().url()).pathname;
  if (path === "/") return route.fulfill({ contentType: "text/html", body: html });
  if (path === "/ring.js") return route.fulfill({ contentType: "text/javascript", body: ringJs });
  if (path.startsWith("/three/"))
    return route.fulfill({ contentType: "text/javascript", body: readFileSync(join(threeBuild, path.slice(7))) });
  return route.fulfill({ status: 404 });
});
page.on("pageerror", (e) => console.error("page error:", e.message));
await page.goto("http://render.local/");
await page.waitForFunction(() => (window as unknown as { ready?: boolean }).ready);

for (const theme of ["dark", "light"] as const)
  for (const p of [0, 40, 70, 100]) {
    const url = await page.evaluate(
      ([pal, prog]) => (window as unknown as { render: (a: unknown, b: number) => string }).render(pal, prog),
      [palettes[theme], p / 100] as const,
    );
    const png = Buffer.from(url.split(",")[1]!, "base64");
    const base = join(out, `poster-${p}-${theme}`);
    // 960px covers the largest display (479 CSS px) at DPR 2; the dot field makes AVIF q40 the size knee.
    writeFileSync(`${base}.avif`, await sharp(png).resize(960).avif({ quality: 40, effort: 6 }).toBuffer());
    writeFileSync(`${base}.webp`, await sharp(png).resize(960).webp({ quality: 75 }).toBuffer());
    if (process.argv.includes("--png")) writeFileSync(`${base}.png`, png);
  }

await browser.close();
console.log("posters written to", out);
