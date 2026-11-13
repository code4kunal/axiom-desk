import { expect, test } from "@playwright/test";
import { hero, meta, sections } from "../src/landing/content";

test.describe("with JavaScript disabled", () => {
  test.use({ javaScriptEnabled: false });

  test("the hedge line is in the page before any script runs", async ({ page }) => {
    await page.goto("/");
    const confirm = hero.hedgeCard.slice(hero.hedgeCard.lastIndexOf(" · ") + 3);
    await expect(page.getByText(confirm).first()).toBeVisible();
  });

  test("every nav anchor has a section to land on", async ({ page }) => {
    await page.goto("/");
    for (const s of sections) await expect(page.locator(`#${s.id}`)).toHaveCount(1);
  });
});

test("sharing metadata comes from the content module", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator('meta[property="og:title"]')).toHaveAttribute("content", meta.ogTitle);
  await expect(page.locator('meta[property="og:description"]')).toHaveAttribute("content", meta.ogDescription);
  await expect(page.locator('meta[name="twitter:card"]')).toHaveAttribute("content", "summary_large_image");
});

test("with working scripts a section below the fold stays hidden past 3s and reveals on scroll", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/");
  const below = page.locator("footer [data-reveal], #brokers [data-reveal]").last();
  await page.waitForFunction(() => "observing" in document.documentElement.dataset);
  await page.waitForTimeout(3500); // past the CSS failsafe
  expect(await below.evaluate((el) => getComputedStyle(el).opacity)).toBe("0");
  await below.scrollIntoViewIfNeeded();
  await expect.poll(() => below.evaluate((el) => +getComputedStyle(el).opacity)).toBe(1);
});

test.describe("scripts that never load", () => {
  test("section text still appears after a short wait", async ({ page }) => {
    // The head script still marks html[data-js], but no app chunk ever runs (stale deploy, dead network).
    await page.route("**/_next/static/chunks/**/*.js", (r) => r.abort());
    await page.goto("/#brokers");
    const heading = page.locator("#brokers [data-reveal]").first();
    await expect(heading).toBeAttached();
    await expect.poll(() => heading.evaluate((el) => +getComputedStyle(el).opacity), { timeout: 6000 }).toBe(1);
  });

  test("scripts that arrive after the 3s failsafe leave every shown section visible", async ({ page }) => {
    // Slow phone: the failsafe shows everything at 3s, then the observer starts at ~4.5s.
    await page.route("**/_next/static/chunks/**/*.js", async (r) => {
      await new Promise((done) => setTimeout(done, 4500));
      await r.continue();
    });
    await page.goto("/#brokers");
    await page.waitForFunction(() => "observing" in document.documentElement.dataset, null, { timeout: 15_000 });
    await page.waitForTimeout(800); // longer than the 480ms reveal transition
    // Sections above #brokers were shown by the failsafe and are off screen now: none may go blank again.
    const hidden = await page.$$eval("[data-reveal]", (els) => els.filter((el) => getComputedStyle(el).opacity !== "1").length);
    expect(hidden).toBe(0);
  });

  test("printing shows every section", async ({ page }) => {
    await page.route("**/_next/static/chunks/**/*.js", (r) => r.abort());
    await page.goto("/");
    await page.emulateMedia({ media: "print" });
    const hidden = await page.$$eval("[data-reveal]", (els) => els.filter((el) => getComputedStyle(el).opacity !== "1").length);
    expect(hidden).toBe(0);
  });
});
