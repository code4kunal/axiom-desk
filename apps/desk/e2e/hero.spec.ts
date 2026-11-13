import { expect, test, type Page } from "@playwright/test";
import { hero } from "../src/landing/content";

// WebGL2 in headless Chromium comes from SwiftShader.
test.use({ launchOptions: { args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] } });

type Win = Window & { cls: number };

// Every script body the page downloads, so a test can tell whether three or GSAP was fetched.
function scripts(page: Page) {
  const bodies: Promise<string>[] = [];
  page.on("response", (r) => {
    if (r.request().resourceType() === "script") bodies.push(r.text().catch(() => ""));
  });
  return async () => {
    const all = await Promise.all(bodies);
    return { three: all.some((b) => b.includes("WebGLRenderer")), gsap: all.some((b) => b.includes("ScrollTrigger")) };
  };
}

async function trackCls(page: Page) {
  await page.addInitScript(() => {
    (window as unknown as Win).cls = 0;
    new PerformanceObserver((l) => {
      for (const e of l.getEntries() as (PerformanceEntry & { value: number; hadRecentInput: boolean })[])
        if (!e.hadRecentInput) (window as unknown as Win).cls += e.value;
    }).observe({ type: "layout-shift", buffered: true });
  });
}
const cls = (page: Page) => page.evaluate(() => (window as unknown as Win).cls);

const ringLive = (page: Page) =>
  page.waitForFunction(() => document.querySelector<HTMLElement>("#season canvas")?.style.opacity === "1");

// Scroll px where each caption (0, 40, 70, card) docks under the ring.
const docks = (page: Page) =>
  page.evaluate(() =>
    [...document.querySelectorAll<HTMLElement>("#season .hero-rail, #season .hero-track")].map((el) => {
      const railTop = parseFloat(getComputedStyle(el).top);
      el.style.position = "static";
      const top = el.getBoundingClientRect().top + scrollY;
      el.style.position = "";
      return Math.round(top - railTop);
    }),
  );

// Lets load + idle pass so the island would have fetched its chunks if it were going to.
const settle = (page: Page) => page.waitForLoadState("load").then(() => page.waitForTimeout(2500));

test("AE1: data saver never pins and never downloads the ring or GSAP", async ({ page }) => {
  await page.addInitScript(() =>
    Object.defineProperty(navigator, "connection", { value: { saveData: true, effectiveType: "4g" } }),
  );
  const loaded = scripts(page);
  await page.goto("/");
  await settle(page);
  expect(await page.evaluate(() => document.documentElement.dataset.hero)).toBeUndefined();
  expect(await loaded()).toEqual({ three: false, gsap: false });
});

test("the pinned path downloads both chunks and draws the ring (control for AE1/AE5)", async ({ page }) => {
  const loaded = scripts(page);
  await page.goto("/");
  await ringLive(page);
  expect(await page.evaluate(() => document.documentElement.dataset.hero)).toBe("pin");
  expect(await loaded()).toEqual({ three: true, gsap: true });
});

test.describe("AE5: reduced motion", () => {
  test.use({ reducedMotion: "reduce" });
  test("stacks the four posters, no pin, no chunks", async ({ page }) => {
    const loaded = scripts(page);
    await page.goto("/");
    await settle(page);
    expect(await page.evaluate(() => document.documentElement.dataset.hero)).toBeUndefined();
    await expect(page.locator("#season .hero-plate")).toHaveCount(4);
    for (const plate of await page.locator("#season .hero-plate").all()) await expect(plate).toBeVisible();
    expect(await loaded()).toEqual({ three: false, gsap: false });
  });
});

test.describe("1280×800", () => {
  test.use({ viewport: { width: 1280, height: 800 } });

  test("AE2: /#baskets lands on section 07 with CLS under 0.05", async ({ page }) => {
    await trackCls(page);
    await page.goto("/#baskets");
    // The ring is off screen here, so it may never draw a frame; wait for the island to attach it.
    await page.locator("#season canvas").waitFor({ state: "attached" });
    await page.waitForTimeout(1000);
    // Lands where the browser puts any section: under the 48px nav plus the section's own scroll margin.
    const [top, want] = await page
      .locator("#baskets")
      .evaluate((el) => [el.getBoundingClientRect().top, 48 + parseFloat(getComputedStyle(el).scrollMarginTop)]);
    expect(Math.abs(top! - want!)).toBeLessThan(2);
    expect(await cls(page)).toBeLessThan(0.05);
  });

  test("captions dock at 0.4, 0.7 and 1 of the pin", async ({ page }) => {
    await page.goto("/");
    const d = await page.evaluate(() => document.getElementById("season")!.offsetHeight - innerHeight);
    expect((await docks(page)).map((y) => +(y / d).toFixed(2))).toEqual([0, 0.4, 0.7, 1]);
  });

  test("forced context loss: the canvas fades out, the poster stays, no console errors", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto("/");
    await ringLive(page);
    await page.evaluate(() =>
      document.querySelector("canvas")!.getContext("webgl2")!.getExtension("WEBGL_lose_context")!.loseContext(),
    );
    await expect(page.locator("#season canvas")).toHaveCount(0);
    await expect(page.locator("#season .hero-poster img:visible")).toHaveCount(1);
    expect(errors).toEqual([]);
  });

  test("no WebGL2: the 0% poster pins and the captions dock over it, CLS under 0.05", async ({ page }) => {
    await page.addInitScript(() => {
      const get = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function (this: HTMLCanvasElement, id: string, ...rest: unknown[]) {
        return id === "webgl2" ? null : (get as (...a: unknown[]) => unknown).call(this, id, ...rest);
      } as typeof get;
    });
    await trackCls(page);
    const loaded = scripts(page);
    await page.goto("/");
    await settle(page);
    expect(await page.evaluate(() => document.documentElement.dataset.hero)).toBe("pin");
    await expect(page.locator("#season canvas")).toHaveCount(0);
    const [, d40] = await docks(page);
    await page.evaluate((y) => scrollTo(0, y! + 2), d40);
    const poster = await page.locator("#season .hero-poster").boundingBox();
    expect(poster!.y).toBeCloseTo(48, 0);
    // Palette v2: the legend band (--legend-h) docks between the poster and the rail.
    const rail = await page.locator("#reading").boundingBox();
    const legend = await page.locator("#season .hero-legend").boundingBox();
    const legendH = await page.evaluate(() => parseFloat(getComputedStyle(document.getElementById("season")!).getPropertyValue("--legend-h")));
    expect(legendH).toBeGreaterThan(0);
    expect(rail!.y).toBeCloseTo(poster!.y + poster!.height + legendH, 0);
    expect(legend!.y + legend!.height).toBeCloseTo(rail!.y, 0);
    expect(await cls(page)).toBeLessThan(0.05);
    expect(await loaded()).toEqual({ three: false, gsap: false });
  });

  test("back navigation restores the scroll position inside the pin", async ({ page }) => {
    await page.goto("/");
    const [, , d70] = await docks(page);
    await page.evaluate((y) => scrollTo(0, y!), d70);
    await page.waitForTimeout(300);
    await page.goto("/privacy");
    await page.goBack();
    await page.waitForFunction((y) => Math.abs(scrollY - y!) < 2, d70);
  });

  test("Tab passes through the hero: primary, brokers, then section 02", async ({ page }) => {
    await page.goto("/");
    const seen: string[] = [];
    for (let i = 0; i < 40 && seen.length < 3; i++) {
      await page.keyboard.press("Tab");
      const where = await page.evaluate(() => {
        const a = document.activeElement!;
        const hero = document.getElementById("season")!;
        if (hero.contains(a)) return a.getAttribute("href");
        return hero.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_FOLLOWING ? "after" : null;
      });
      if (where) seen.push(where);
    }
    expect(seen).toEqual(["#reading", "#brokers", "after"]);
  });
});

test.describe("AE3: dark system, stored Light", () => {
  test.use({ colorScheme: "dark", viewport: { width: 1280, height: 800 } });
  // R6/AE3 as amended 2026-11-13: the LCP is the statement or the poster, whichever is larger.
  test("fetches only the light 0% poster; the LCP is the statement or that poster, under 2.5 s", async ({ page }) => {
    await page.addInitScript(() => localStorage.setItem("axiom-theme", "light"));
    const posters: string[] = [];
    page.on("request", (r) => r.url().includes("/hero/") && posters.push(r.url().split("/").pop()!));
    await page.goto("/");
    await settle(page);
    // One request, the light 0% poster, in whichever srcset width the viewport picks (720w or 960w).
    expect(posters).toHaveLength(1);
    expect(posters[0]).toMatch(/^poster-0-light(-720)?\.avif$/);
    const lcp = await page.evaluate(
      () =>
        new Promise<{ ms: number; statement: boolean; url: string }>((res) =>
          new PerformanceObserver((l) => {
            const e = l.getEntries().at(-1) as PerformanceEntry & { url: string; element: Element | null };
            res({ ms: e.startTime, statement: e.element?.id === "season-h", url: e.url });
          }).observe({ type: "largest-contentful-paint", buffered: true }),
        ),
    );
    expect(lcp.statement || /\/hero\/poster-0-light(-720)?\.avif$/.test(lcp.url), JSON.stringify(lcp)).toBe(true);
    expect(lcp.ms).toBeLessThan(2500);
  });
});

test.describe("375×844", () => {
  test.use({ viewport: { width: 375, height: 844 }, hasTouch: true, isMobile: true });
  test("the INDEX trigger stays visible and on top at 0, 40, 70 and 100", async ({ page }) => {
    await page.goto("/");
    for (const y of await docks(page)) {
      await page.evaluate((v) => scrollTo(0, v + 2), y);
      const index = page.getByRole("link", { name: /index/i });
      await expect(index).toBeVisible();
      const onTop = await index.evaluate((el) => {
        const r = el.getBoundingClientRect();
        return el.contains(document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2));
      });
      expect(onTop, `INDEX covered at ${y}`).toBe(true);
    }
  });

  test("captions dock one at a time: the next one is still below the fold when one docks", async ({ page }) => {
    await page.goto("/");
    await settle(page);
    const d = await docks(page);
    for (let k = 1; k < d.length - 1; k++) {
      await page.evaluate((y) => scrollTo(0, y), d[k]!);
      const nextTop = await page.locator("#season .hero-track").nth(k).evaluate((el) => el.getBoundingClientRect().top);
      expect(nextTop, `caption ${k + 1} visible while caption ${k} docks`).toBeGreaterThanOrEqual(page.viewportSize()!.height - 2);
    }
  });
});

test("rotating a pinned phone to landscape drops the pin and the live ring", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await ringLive(page);
  await page.setViewportSize({ width: 844, height: 390 });
  await expect.poll(() => page.evaluate(() => document.documentElement.dataset.hero ?? null)).toBeNull();
  await expect(page.locator("#season canvas")).toHaveCount(0);
  for (const plate of await page.locator("#season .hero-plate").all()) await expect(plate).toBeVisible();
});

// The live ring draws phone density below 768 and desktop density from 768; the poster it fades over must match.
for (const [width, height, phone] of [[375, 844, true], [800, 1000, false]] as const) {
  test(`at ${width} wide the 0% poster is the ${phone ? "phone" : "desktop"}-density file`, async ({ browser }) => {
    const ctx = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 1, colorScheme: "light" });
    const page = await ctx.newPage();
    const posters: string[] = [];
    page.on("request", (r) => r.url().includes("/hero/poster-0-light") && posters.push(new URL(r.url()).pathname));
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    expect(posters).toEqual([`/hero/poster-0-light${phone ? "-720" : ""}.avif`]);
    await ctx.close();
  });
}

// Common short desktop viewports: 1366×768 minus browser chrome, and the 600px gate floor.
for (const [width, height] of [[1366, 650], [1024, 600]] as const) {
  test(`the caption rail stays on screen at ${width}×${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.goto("/");
    expect(await page.evaluate(() => document.documentElement.dataset.hero)).toBe("pin");
    const d = await docks(page);
    for (const y of d.slice(0, 2)) {
      await page.evaluate((v) => scrollTo(0, v + 2), y);
      const bottom = await page.locator("#season .hero-rail").evaluate((el) => el.getBoundingClientRect().bottom);
      expect(bottom, `rail bottom at scroll ${y}`).toBeLessThanOrEqual(height);
    }
  });
}

test.describe("JavaScript disabled", () => {
  test.use({ javaScriptEnabled: false, viewport: { width: 1280, height: 800 } });
  test("stacked layout with no reserved empty space", async ({ page }) => {
    await page.goto("/");
    expect(await page.evaluate(() => document.documentElement.dataset.hero)).toBeUndefined();
    await expect(page.locator("#season .hero-plate")).toHaveCount(4);
    // The stacked hero is its content: no box reserved past the grid beyond its bottom padding.
    expect(
      await page.locator("#season").evaluate((el: HTMLElement) => el.offsetHeight - el.querySelector<HTMLElement>(".grid")!.offsetHeight),
    ).toBeLessThan(200);
  });
});

test("og:image is a 1200×630 JPEG under 300 KB", async ({ page, request }) => {
  await page.goto("/");
  const url = new URL((await page.locator('meta[property="og:image"]').getAttribute("content"))!).pathname;
  const body = await (await request.get(url)).body();
  expect(body.length).toBeLessThan(300 * 1024);
  // Dimensions from the JPEG's first SOFn marker.
  let i = 2;
  while (body[i + 1]! < 0xc0 || body[i + 1]! > 0xc3) i += 2 + body.readUInt16BE(i + 2);
  expect([body.readUInt16BE(i + 7), body.readUInt16BE(i + 5)]).toEqual([1200, 630]);
});

test("each pin step says where the reader is and what just happened", async ({ page }) => {
  await page.goto("/");
  const docks = page.locator("#season .hero-rail, #season .hero-track");
  await expect(docks).toHaveCount(hero.steps.length);
  for (const [i, step] of hero.steps.entries()) {
    await expect(docks.nth(i).getByText(step.label, { exact: true })).toHaveCount(1);
    await expect(docks.nth(i).getByText(step.say, { exact: true })).toHaveCount(1);
  }
});
