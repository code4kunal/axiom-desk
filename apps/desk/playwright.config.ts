import { defineConfig, devices } from "@playwright/test";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const port = 3100;
const repo = resolve(import.meta.dirname, "../..");
const issuer = "http://127.0.0.1:9411";
const api = "http://127.0.0.1:8765";
// A fresh records database each run, with the MFA test user on the axiom-desk directory and one published regime run.
const db = join(mkdtempSync(join(tmpdir(), "axiom-e2e-")), "desk.db");
const seed = [
  "import sqlite3, sys, time",
  "from datetime import datetime, timezone",
  "from axiom_core.db import migrate",
  "from axiom_core.envelope import Source",
  "from axiom_core.runs import RunStore",
  "from axiom_core.audit import AuditLog",
  "from axiom_core.tenancy import Directory",
  "c = sqlite3.connect(sys.argv[1])",
  "migrate(c)",
  "Directory(c, AuditLog(c, time.time)).bootstrap_admin('axiom-desk', 'user-mfa')",
  "RunStore(c, time.time).publish('regime', datetime(2026, 11, 13, tzinfo=timezone.utc), {'state': 'risk-on'}, (Source('nse-eod', 'public'),))",
].join("; ");

export default defineConfig({
  testDir: "e2e",
  fullyParallel: true,
  reporter: "list",
  use: { baseURL: `http://localhost:${port}` },
  webServer: [
    {
      command: "uv run --no-sync python tools/test_idp/idp.py --port 9411 --client-id desk --client-secret e2e-only --tenant-claim tenant",
      cwd: repo,
      url: `${issuer}/.well-known/openid-configuration`,
      reuseExistingServer: false,
    },
    {
      command: `uv run --no-sync python -c "${seed}" ${db} && uv run --no-sync uvicorn --factory axiom_api.app:default_app --host 127.0.0.1 --port 8765 --workers 1`,
      cwd: repo,
      url: `${api}/auth/me`,
      reuseExistingServer: false,
      env: {
        AXIOM_DB: db,
        AXIOM_OIDC_ISSUER: issuer,
        AXIOM_OIDC_CLIENT_ID: "desk",
        AXIOM_OIDC_CLIENT_SECRET: "e2e-only",
        AXIOM_PUBLIC_ORIGIN: `http://localhost:${port}`,
      },
    },
    {
      command: `next build && next start --port ${port}`,
      port,
      reuseExistingServer: !process.env.CI,
      timeout: 180_000,
      env: { AXIOM_API_ORIGIN: api },
    },
  ],
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
