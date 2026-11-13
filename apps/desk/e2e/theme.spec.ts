import { expect, test } from "@playwright/test";

const LIGHT_GROUND = "rgb(245, 230, 220)";
const DARK_GROUND = "rgb(20, 16, 13)";

test.describe("theme before first paint", () => {
  test.use({ colorScheme: "dark" });

  test("a stored Light choice beats a dark system before the body is parsed", async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem("axiom-theme", "light");
      // Record data-theme the moment <body> is inserted: after the head script, before any paint.
      new MutationObserver((_, obs) => {
        if (document.body) {
          (window as unknown as { themeAtBody: string | undefined }).themeAtBody =
            document.documentElement.dataset.theme;
          obs.disconnect();
        }
      }).observe(document, { childList: true, subtree: true });
    });
    await page.goto("/");
    expect(await page.evaluate(() => (window as unknown as { themeAtBody?: string }).themeAtBody)).toBe("light");
    await expect(page.locator("body")).toHaveCSS("background-color", LIGHT_GROUND);
  });

  test("no stored choice follows the dark system", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
    await expect(page.locator("body")).toHaveCSS("background-color", DARK_GROUND);
  });
});

test("unknown routes render the 404 with noindex and a link home", async ({ page }) => {
  const res = await page.goto("/does-not-exist");
  expect(res?.status()).toBe(404);
  await expect(page.locator('meta[name="robots"]')).toHaveAttribute("content", /noindex/);
  await expect(page.locator('main a[href="/"]')).toBeVisible();
});

for (const path of ["/privacy", "/terms"]) {
  test(`${path} shows the pending-legal-review notice`, async ({ page }) => {
    await page.goto(path);
    await expect(page.getByText("Text pending legal review")).toBeVisible();
  });
}
