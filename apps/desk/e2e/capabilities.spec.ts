import { expect, test, type Page } from "@playwright/test";

// Same sign-in path as sign-in.spec.ts: the test provider needs login_hint, which a browser never sends.
async function signIn(page: Page) {
  await page.goto("/sign-in");
  await page.getByRole("link", { name: "Sign in" }).click();
  await page.waitForURL(/^http:\/\/127\.0\.0\.1:9411\/authorize\?/);
  await page.goto(`${page.url()}&login_hint=mfa`);
  await expect(page).toHaveURL(/\/desk$/);
}

// A real browser fetch from the desk page: same origin, httpOnly session cookie attached by the browser.
function callFromPage(page: Page, name: string, input: unknown) {
  return page.evaluate(
    async ([n, body]) => {
      const res = await fetch(`/api/capabilities/${n}`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      });
      return { status: res.status, body: (await res.json()) as { error?: unknown } };
    },
    [name, input] as const,
  );
}

test("signed in, runs_latest returns the seeded run's envelope", async ({ page }) => {
  await signIn(page);
  const res = await callFromPage(page, "runs_latest", { kind: "regime" });
  expect(res.status).toBe(200);
  expect(res.body).toMatchObject({ value: { kind: "regime", payload: { state: "risk-on" } } });
});

test("signed out, a capability call is 401", async ({ page }) => {
  await page.goto("/sign-in");
  const res = await callFromPage(page, "runs_latest", { kind: "regime" });
  expect(res.status).toBe(401);
});

test("signed in, a cross-origin POST is 403", async ({ page }) => {
  await signIn(page);
  // page.request shares the signed-in browser's cookies, so only the Origin differs.
  const res = await page.request.post("/api/capabilities/runs_latest", {
    headers: { origin: "https://evil.example", "content-type": "application/json" },
    data: { kind: "regime" },
  });
  expect(res.status()).toBe(403);
});

test("signed in, an unknown capability is 404", async ({ page }) => {
  await signIn(page);
  const res = await callFromPage(page, "no_such_capability", {});
  expect(res.status).toBe(404);
});
