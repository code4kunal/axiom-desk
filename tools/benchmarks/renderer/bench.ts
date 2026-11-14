// Runs each renderer in headed Google Chrome (real GPU) against the vite dev server and prints the results.
// Usage: pnpm dev (in another shell), then:
//   pnpm bench [custom scichart] [--session=budget|footprint] [--seconds=20] [--tps=20] [--charts=8]
//              [--repeats=3] [--replay=60] [--profile=<hardware name>] [--out=file.jsonl] [--port=5199]
// --session=budget is the 16-chart, 600 s, 3-repeat, 60x run; --session=footprint is the 4-footprint-chart run.
// Without --session the run is the quick 8-chart check, one repeat, and reports "incomplete".
import { appendFileSync } from "node:fs";
import os from "node:os";
import { chromium } from "playwright";
import { SESSIONS, type Session } from "./src/load.ts";
import { frameStats, summarise } from "./src/metrics.ts";
import { ticksPerSecond } from "./src/replay.ts";

const args = process.argv.slice(2);
const flags = Object.fromEntries(
  args.filter((a) => a.startsWith("--")).map((a) => a.slice(2).split("=") as [string, string]),
);
const renderers = args.filter((a) => !a.startsWith("--"));

const quick: Session = { charts: 8, seconds: 20, repeats: 1, speed: 0, load: "none" };
const preset: Session = SESSIONS[flags.session as keyof typeof SESSIONS] ?? quick;
const charts = Number(flags.charts ?? preset.charts);
const seconds = Number(flags.seconds ?? preset.seconds);
const repeats = Number(flags.repeats ?? preset.repeats);
const speed = Number(flags.replay ?? preset.speed);
// Replay speed sets the tick rate (30 ticks per bar); the quick run keeps its fixed 20 ticks/s.
const tps = Number(flags.tps ?? (speed ? ticksPerSecond(30, speed) : 20));
const qs = new URLSearchParams({ seconds: String(seconds), tps: String(tps), charts: String(charts), history: flags.history ?? "20000" });

// Installed Chrome: the browser the desk runs, and no Playwright browser download.
const browser = await chromium.launch({ channel: "chrome", headless: false });
try {
  const cpus = os.cpus();
  const hardware = {
    profile: flags.profile ?? "unnamed",
    cpu: cpus[0]?.model,
    cores: cpus.length,
    memGB: Math.round(os.totalmem() / 2 ** 30),
    os: `${os.platform()}-${os.arch()} ${os.release()}`,
    node: process.version,
    chrome: browser.version(),
    gpu: "",
    devicePixelRatio: 0,
  };
  for (const r of renderers.length ? renderers : ["custom", "scichart"]) {
    const runs = [];
    for (let i = 0; i < repeats; i++) {
      const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
      const errors: string[] = [];
      page.on("pageerror", (e) => errors.push(e.message));
      await page.goto(`http://localhost:${flags.port ?? "5199"}/?renderer=${r}&${qs}`);
      // Setup (history for every chart) is not bounded by the run length.
      await page.waitForFunction((n) => document.querySelectorAll(".cell").length === n, charts, { timeout: 120_000 });
      // Loaded through the dev server so vite compiles it; main.ts is not touched.
      await page.evaluate(
        ([kind, rate]) => import(/* @vite-ignore */ "/src/load.ts" as string).then((m) => m.mountLoad(kind, rate)),
        [preset.load, tps] as const,
      );
      // One wait on either outcome: racing two waits leaves the loser to reject unhandled later.
      const done = await page.waitForFunction(
        () => window.__bench ?? (document.getElementById("out")?.textContent?.startsWith("ERROR") && "error"),
        null,
        { timeout: (seconds + 60) * 1000 },
      );
      if ((await done.jsonValue()) === "error") {
        runs.push({ error: await page.textContent("#out"), pageErrors: errors });
      } else {
        const bench = await page.evaluate(() => window.__bench!);
        const log = await page.evaluate(() => window.__frames!);
        if (!hardware.gpu) {
          Object.assign(hardware, await page.evaluate(() => {
            const gl = document.createElement("canvas").getContext("webgl2");
            const ext = gl?.getExtension("WEBGL_debug_renderer_info");
            return { gpu: ext ? String(gl!.getParameter(ext.UNMASKED_RENDERER_WEBGL)) : "unavailable", devicePixelRatio: devicePixelRatio };
          }));
        }
        runs.push({
          ...frameStats(log),
          fps: Math.round((log.length / seconds) * 100) / 100,
          ticksPerSecDelivered: bench.ticksPerSecDelivered,
          longTasks: bench.longTasks,
          longTaskMs: bench.longTaskMs,
          pageErrors: errors,
        });
      }
      await page.close();
    }
    const ok = runs.filter((x): x is Exclude<typeof x, { error: string | null }> => !("error" in x));
    const line = JSON.stringify({
      renderer: r, load: preset.load, charts, seconds, replaySpeed: speed, tps, repeats: runs.length,
      status: ok.length < runs.length ? "error" : summarise(ok).status, hardware, runs,
    });
    console.log(line);
    if (flags.out) appendFileSync(flags.out, `${line}\n`);
  }
} finally {
  await browser.close();
}
