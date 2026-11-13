// Runs each renderer in headed Google Chrome (real GPU) against the vite dev server and prints the results.
// Usage: pnpm dev (in another shell), then: pnpm bench [custom scichart] [--seconds=20] [--tps=20] [--charts=8] [--port=5199]
import { chromium } from "playwright";

const args = process.argv.slice(2);
const flags = Object.fromEntries(
  args.filter((a) => a.startsWith("--")).map((a) => a.slice(2).split("=") as [string, string]),
);
const renderers = args.filter((a) => !a.startsWith("--"));
const qs = new URLSearchParams({
  seconds: flags.seconds ?? "20",
  tps: flags.tps ?? "20",
  charts: flags.charts ?? "8",
  history: flags.history ?? "20000",
});

// Installed Chrome: the browser the desk runs, and no Playwright browser download.
const browser = await chromium.launch({ channel: "chrome", headless: false });
try {
  for (const r of renderers.length ? renderers : ["custom", "scichart"]) {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto(`http://localhost:${flags.port ?? "5199"}/?renderer=${r}&${qs}`);
    const timeoutMs = (Number(qs.get("seconds")) + 60) * 1000;
    const result = await Promise.race([
      page.waitForFunction(() => window.__bench, null, { timeout: timeoutMs }).then((h) => h.jsonValue()),
      page.waitForFunction(() => document.getElementById("out")?.textContent?.startsWith("ERROR"), null, { timeout: timeoutMs }).then(
        async () => ({ renderer: r, error: await page.textContent("#out") }),
      ),
    ]);
    console.log(JSON.stringify({ ...result, pageErrors: errors }));
    await page.close();
  }
} finally {
  await browser.close();
}
