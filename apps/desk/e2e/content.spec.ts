import { expect, test } from "@playwright/test";
import { meta, sections } from "../src/landing/content";

test.describe("with JavaScript disabled", () => {
  test.use({ javaScriptEnabled: false });

  test("the hedge line is in the page before any script runs", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("a human confirms every order").first()).toBeVisible();
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

test.describe("scripts that never load", () => {
  test("section text still appears after a short wait", async ({ page }) => {
    // The head script still marks html[data-js], but no app chunk ever runs (stale deploy, dead network).
    await page.route("**/_next/static/chunks/**/*.js", (r) => r.abort());
    await page.goto("/#brokers");
    const heading = page.locator("#brokers [data-reveal]").first();
    await expect(heading).toBeAttached();
    await expect.poll(() => heading.evaluate((el) => +getComputedStyle(el).opacity), { timeout: 6000 }).toBe(1);
  });

  test("printing shows every section", async ({ page }) => {
    await page.route("**/_next/static/chunks/**/*.js", (r) => r.abort());
    await page.goto("/");
    await page.emulateMedia({ media: "print" });
    const hidden = await page.$$eval("[data-reveal]", (els) => els.filter((el) => getComputedStyle(el).opacity !== "1").length);
    expect(hidden).toBe(0);
  });
});
