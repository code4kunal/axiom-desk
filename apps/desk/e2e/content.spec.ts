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
