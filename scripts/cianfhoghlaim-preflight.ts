#!/usr/bin/env bun
/**
 * scripts/cianfhoghlaim-preflight.ts
 *
 * Topology + auth + secrets preflight checks before deploy.
 *
 * Currently checks:
 *   1. The two-host topology is honored (arm1-oci + bunchloch only).
 *   2. Brand linter is clean (no bons, kcg, KCGu, cax41, security.hetzner).
 *   3. Stack linter passes (errors == 0).
 *
 * Future checks (Phase 6):
 *   - Pangolin API reachable (PANGOLIN_URL)
 *   - Komodo API reachable (KOMODO_URL)
 *   - Infisical API reachable (INFISICAL_URL)
 *   - Machine identity resolvable (INFISICAL_CLIENT_ID + secret)
 */

import { spawn } from "node:child_process";
import { resolve } from "node:path";

const ROOT = resolve(import.meta.dir, "..");

interface Check {
  name: string;
  ok: boolean;
  message: string;
}

function run(script: string): Promise<number> {
  return new Promise((resolveRun) => {
    const child = spawn("bun", ["run", script], { cwd: ROOT, stdio: "inherit", env: process.env });
    child.on("exit", (code) => resolveRun(code ?? 1));
  });
}

async function main(): Promise<number> {
  const checks: Check[] = [];

  const brandCode = await run("scripts/cianfhoghlaim-brand-lint.ts");
  checks.push({
    name: "brand-lint",
    ok: brandCode === 0,
    message:
      brandCode === 0
        ? "OK (no legacy brand tokens or retired-host references)"
        : "FAIL (see brand-lint output above)",
  });

  const stackCode = await run("scripts/cianfhoghlaim-stack-lint.ts");
  checks.push({
    name: "stack-lint",
    ok: stackCode === 0,
    message: stackCode === 0 ? "OK (no errors across all stacks)" : "FAIL (see stack-lint output above)",
  });

  let ok = true;
  console.log("");
  console.log("preflight summary:");
  for (const c of checks) {
    console.log(`  ${c.ok ? "OK" : "FAIL"}  ${c.name} — ${c.message}`);
    if (!c.ok) ok = false;
  }
  console.log("");
  return ok ? 0 : 1;
}

process.exit(await main());