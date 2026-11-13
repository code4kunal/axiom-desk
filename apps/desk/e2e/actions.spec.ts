import { expect, test, type Page } from "@playwright/test";
import { agent, brokers, charts, options, sections, shell } from "../src/landing/content";

// U5: theme menu, broker dialog, nav sheet, clip slots (R10, R12, R13, R14, R19).

const themeTrigger = (page: Page) => page.locator("header ~ div").getByRole("button", { name: new RegExp(shell.theme) });

for (const width of [375, 768, 1280]) {
  test(`theme control is in the header at ${width} and switches the theme`, async ({ page }) => {
    await page.setViewportSize({ width, height: 800 });
    await page.emulateMedia({ colorScheme: "light" });
    await page.goto("/");
    const trigger = themeTrigger(page);
    await expect(trigger).toBeVisible();
    const box = (await trigger.boundingBox())!;
    expect(box.y + box.height).toBeLessThanOrEqual(48);
    await trigger.click();
    await page.getByRole("menuitemradio", { name: shell.themeChoices.dark }).click();
    await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  });
}

test("no nav lists a Footer item: the rail and the sheet list exactly the sections", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto("/");
  const rail = page.getByRole("navigation", { name: shell.navLabel }).getByRole("link");
  await expect(rail).toHaveCount(sections.length);
  await expect(rail.filter({ hasText: /footer/i })).toHaveCount(0);
});

for (const where of ["rail", "footer"] as const) {
  test(`a keyboard jump from the ${where} index moves the Tab start into that section`, async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto("/");
    const target = sections.find((s) => s.id === "brokers")!; // has its own Tab stop: Talk to the desk
    const list = where === "rail" ? page.getByRole("navigation", { name: shell.navLabel }) : page.locator("footer");
    const link = list.locator(`a[href="/#${target.id}"]`);
    await link.focus();
    await page.keyboard.press("Enter");
    await expect(page).toHaveURL(new RegExp(`#${target.id}$`));
    await page.keyboard.press("Tab");
    // The next Tab stop is inside the section, not the next link in the list.
    expect(await page.evaluate((id) => document.getElementById(id)!.contains(document.activeElement), target.id)).toBe(true);
  });
}

test("the theme menu offers System, Dark and Light; Light persists across a reload", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "dark" });
  await page.goto("/");
  await themeTrigger(page).click();
  const items = page.getByRole("menuitemradio");
  await expect(items).toHaveText(Object.values(shell.themeChoices));
  await expect(page.getByRole("menuitemradio", { name: shell.themeChoices.system })).toHaveAttribute("aria-checked", "true");
  await page.getByRole("menuitemradio", { name: shell.themeChoices.light }).click();
  await expect(page.getByRole("menu")).toHaveCount(0);
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await expect(themeTrigger(page)).toContainText(shell.themeChoices.light);
});

test("the keyboard-highlighted theme item draws a visible ring", async ({ page }) => {
  await page.goto("/");
  // Keys pressed before hydration are lost (slow CI runner); data-observing is set once the client islands run.
  await page.waitForFunction(() => "observing" in document.documentElement.dataset);
  await themeTrigger(page).focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("menu")).toBeVisible();
  await page.keyboard.press("ArrowDown");
  const item = page.locator("[role=menuitemradio][data-highlighted]");
  await expect(item).toHaveCount(1);
  await expect(item).toHaveCSS("outline-style", "solid");
});

test("the theme trigger's hit area is at least 48px tall", async ({ page }) => {
  await page.goto("/");
  const t = themeTrigger(page);
  const hit = await t.evaluate((el) => {
    const r = el.getBoundingClientRect();
    return [r.top - 3.5, r.bottom + 3.5].map((py) => el.contains(document.elementFromPoint(r.left + r.width / 2, py)));
  });
  expect(hit).toEqual([true, true]);
});

test.describe("broker dialog", () => {
  const talk = (page: Page) => page.getByRole("link", { name: brokers.action });

  test("AE4: address as text, Copy writes it to the clipboard, the mailto carries the subject", async ({ page, context }) => {
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);
    await page.goto("/");
    await talk(page).click();
    const dialog = page.getByRole("dialog", { name: brokers.action });
    await expect(dialog).toBeVisible();
    await expect(dialog.getByText(brokers.contact, { exact: true })).toBeVisible();
    await expect(dialog.locator("input, textarea, select, form")).toHaveCount(0);
    await dialog.getByRole("button", { name: brokers.copy }).click();
    await expect(dialog.getByRole("button", { name: brokers.copied })).toBeVisible();
    expect(await page.evaluate(() => navigator.clipboard.readText())).toBe(brokers.contact);
    const mail = dialog.getByRole("link", { name: brokers.mail });
    await expect(mail).toHaveAttribute("href", `mailto:${brokers.contact}?subject=${encodeURIComponent(brokers.subject)}`);
  });

  test("traps focus, closes on Escape and returns focus to Talk to the desk", async ({ page }) => {
    await page.goto("/");
    await talk(page).click();
    const dialog = page.getByRole("dialog", { name: brokers.action });
    await expect(dialog).toBeVisible();
    await expect(dialog.getByRole("button", { name: brokers.copy })).toBeFocused();
    for (let i = 0; i < 8; i++) {
      await page.keyboard.press("Tab");
      expect(await dialog.evaluate((d) => d.contains(document.activeElement))).toBe(true);
    }
    await page.keyboard.press("Escape");
    await expect(dialog).toHaveCount(0);
    await expect(talk(page)).toBeFocused();
  });

  test("a denied clipboard selects the address and says how to copy it", async ({ page }) => {
    await page.addInitScript(() => {
      navigator.clipboard.writeText = () => Promise.reject(new DOMException("denied", "NotAllowedError"));
    });
    await page.goto("/");
    await talk(page).click();
    const dialog = page.getByRole("dialog", { name: brokers.action });
    await dialog.getByRole("button", { name: brokers.copy }).click();
    await expect(dialog.getByText(brokers.copyFailed, { exact: true }).first()).toBeVisible();
    await expect(dialog.locator("[aria-live=polite]")).toHaveText(brokers.copyFailed);
    expect(await page.evaluate(() => getSelection()?.toString())).toBe(brokers.contact);
  });

  test("without JavaScript the trigger is a working mailto link", async ({ browser, baseURL }) => {
    const ctx = await browser.newContext({ javaScriptEnabled: false, baseURL });
    const page = await ctx.newPage();
    await page.goto("/");
    await expect(page.getByRole("link", { name: brokers.action })).toHaveAttribute("href", /^mailto:/);
    await ctx.close();
  });
});

test.describe("nav sheet at 375", () => {
  test.use({ viewport: { width: 375, height: 844 } });

  test("opens from Index, lists the sections, and closes on a choice with focus on that section", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: shell.indexTrigger }).click();
    const sheet = page.getByRole("dialog", { name: shell.navLabel });
    await expect(sheet).toBeVisible();
    const links = sheet.getByRole("link");
    await expect(links).toHaveCount(sections.length);
    await expect(links).toContainText(sections.map((s) => s.label));
    const target = sections[4]!;
    await links.filter({ hasText: target.label }).click();
    await expect(sheet).toHaveCount(0);
    await expect(page).toHaveURL(new RegExp(`#${target.id}$`));
    await expect(page.locator(`#${target.id}`)).toBeFocused();
  });

  test("on a page without the sections, a choice goes to that section on the home page", async ({ page }) => {
    await page.goto("/privacy");
    await page.getByRole("link", { name: shell.indexTrigger }).click();
    const target = sections[2]!;
    await page.getByRole("dialog", { name: shell.navLabel }).getByRole("link", { name: new RegExp(target.label) }).click();
    await expect(page).toHaveURL(new RegExp(`/#${target.id}$`));
    await expect(page.locator(`#${target.id}`)).toBeInViewport();
  });

  test("Escape closes the sheet and returns focus to Index", async ({ page }) => {
    await page.goto("/");
    const index = page.getByRole("link", { name: shell.indexTrigger });
    await index.click();
    await expect(page.getByRole("dialog", { name: shell.navLabel })).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await expect(index).toBeFocused();
  });
});

test("each clip slot shows CLIP PLACEHOLDER and no video is requested on load", async ({ page }) => {
  const media: string[] = [];
  page.on("request", (r) => r.resourceType() === "media" && media.push(r.url()));
  await page.goto("/");
  const clips = [charts.clip, options.clip, agent.clip];
  for (const c of new Set(clips.map((c) => c.label))) await expect(page.getByText(c, { exact: true })).toHaveCount(clips.length);
  await expect(page.locator("video")).toHaveCount(0);
  await page.waitForLoadState("networkidle");
  expect(media).toEqual([]);
});
