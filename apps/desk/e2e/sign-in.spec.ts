import { expect, test, type Page } from "@playwright/test";
import { signInErrors } from "../src/landing/content";

// The test provider picks its user from login_hint, which a browser never sends. Routing cannot add it:
// the authorize request is a redirect, and route overrides do not reach redirected requests. So the
// browser lands on the provider's refusal, and the test re-opens the same authorize URL with the hint.
async function atProvider(page: Page, hint: string) {
  await page.waitForURL(/^http:\/\/127\.0\.0\.1:9411\/authorize\?/);
  await page.goto(`${page.url()}&login_hint=${hint}`);
}

async function signIn(page: Page, hint = "mfa") {
  await page.goto("/sign-in");
  await page.getByRole("link", { name: "Sign in" }).click();
  await atProvider(page, hint);
}

// Next's route announcer is also role=alert; the sign-in message lives in main.
const alert = (page: Page) => page.getByRole("main").getByRole("alert");

// The codes the API redirects with, and the copy the design spec gives each.
const expected = {
  mfa_required: { label: "SECOND FACTOR NEEDED", message: "Your sign-in did not use multi-factor authentication." },
  unknown_user: { label: "NOT ON THIS DESK", message: "Your account signed in, but it is not set up on this desk." },
  expired: { label: "SIGN-IN EXPIRED", message: "That sign-in expired or was already used." },
  cancelled: { label: "SIGN-IN CANCELLED", message: "You cancelled sign-in at your provider." },
  provider_unavailable: { label: "PROVIDER UNREACHABLE", message: "We could not reach your sign-in provider." },
  failed: { label: "SIGN-IN FAILED", message: "Sign-in did not complete." },
} satisfies Record<string, { label: string; message: string }>;

test("signed out, /desk sends you to /sign-in", async ({ page }) => {
  await page.goto("/desk");
  await expect(page).toHaveURL(/\/sign-in$/);
  await expect(page.getByRole("heading", { level: 1, name: "Sign in" })).toBeVisible();
  await expect(alert(page)).toHaveCount(0);
  await expect(page).toHaveTitle("Sign in | Axiom Desk");
});

test("the MFA user signs in, lands on /desk named with their tenant, and stays signed in on reload", async ({ page }) => {
  await signIn(page);
  await expect(page).toHaveURL(/\/desk$/);
  await expect(page.getByRole("heading", { level: 1, name: "Maya Desk" })).toBeVisible();
  await expect(page.getByText("axiom-desk", { exact: true })).toBeVisible();
  await expect(page).toHaveTitle("Desk | Axiom");
  await page.reload();
  await expect(page).toHaveURL(/\/desk$/);
  await expect(page.getByRole("heading", { level: 1, name: "Maya Desk" })).toBeVisible();
});

test("signed in, /sign-in sends you to /desk", async ({ page }) => {
  await signIn(page);
  await expect(page).toHaveURL(/\/desk$/);
  await page.goto("/sign-in");
  await expect(page).toHaveURL(/\/desk$/);
});

test("sign out lands on /sign-in, and Back to /desk sends you to /sign-in", async ({ page }) => {
  await signIn(page);
  await expect(page).toHaveURL(/\/desk$/);
  await page.getByRole("button", { name: "Sign out" }).click();
  await expect(page).toHaveURL(/\/sign-in$/);
  await page.goBack();
  await expect(page).toHaveURL(/\/sign-in$/);
  await expect(page.getByRole("heading", { level: 1, name: "Sign in" })).toBeVisible();
});

test("the content module covers exactly the API's error codes", () => {
  expect(Object.keys(signInErrors).sort()).toEqual(Object.keys(expected).sort());
});

for (const [code, copy] of Object.entries(expected)) {
  test(`?error=${code} shows its own message`, async ({ page }) => {
    await page.goto(`/sign-in?error=${code}`);
    await expect(alert(page)).toContainText(copy.label);
    await expect(alert(page)).toContainText(copy.message);
    await expect(page).toHaveTitle("Sign-in problem | Axiom Desk");
    await expect(page.getByRole("link", { name: "Sign in" })).toBeVisible();
  });
}

test("an unknown error code shows the generic message and never echoes the value", async ({ page }) => {
  await page.goto("/sign-in?error=%3Cmarquee%3Eowned");
  await expect(alert(page)).toContainText(expected.failed.label);
  await expect(alert(page)).toContainText(expected.failed.message);
  await expect(page.locator("body")).not.toContainText("owned");
});

test("the user without MFA ends on /sign-in with the MFA message", async ({ page }) => {
  await signIn(page, "nomfa");
  await expect(page).toHaveURL(/\/sign-in\?error=mfa_required$/);
  await expect(alert(page)).toContainText(expected.mfa_required.message);
});

async function tabTo(page: Page, name: string) {
  for (let i = 0; i < 10; i++) {
    await page.keyboard.press("Tab");
    if ((await page.evaluate(() => document.activeElement?.textContent?.trim())) === name) return;
  }
  throw new Error(`Tab never reached ${name}`);
}

test("keyboard only: Sign in and Sign out are reachable and show the focus ring", async ({ page }) => {
  await page.goto("/sign-in");
  await tabTo(page, "Sign in");
  const signInLink = page.getByRole("link", { name: "Sign in" });
  await expect(signInLink).toBeFocused();
  await expect(signInLink).toHaveCSS("outline-style", "solid");
  await expect(signInLink).toHaveCSS("outline-width", "2px");
  await page.keyboard.press("Enter");
  await atProvider(page, "mfa");
  await expect(page).toHaveURL(/\/desk$/);

  await tabTo(page, "Sign out");
  const signOut = page.getByRole("button", { name: "Sign out" });
  await expect(signOut).toBeFocused();
  await expect(signOut).toHaveCSS("outline-style", "solid");
  await expect(signOut).toHaveCSS("outline-width", "2px");
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/\/sign-in$/);
});
