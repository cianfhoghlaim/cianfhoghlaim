// bonneagar/iac/commands/wire-pocketid-as-oidc.ts — Thin TypeScript wrapper
// around scripts/wire-pocketid-pangolin-komodo.sh
//
// The bash script is the source of truth. This TS file just shells out to it
// (preserves the `bun run iac:wire-pocketid-as-oidc` UX from the package.json
// script `wire-pocketid-as-oidc: "bun run cli.ts wire-pocketid-as-oidc"`).
//
// Why split:
//   - The bash script is portable, testable, and easy for non-TS users
//     (operators, system admins, less-technical users of the repo).
//   - The TS wrapper is a thin adapter that loads the .env, passes flags,
//     and prints the same UX as the rest of the bons IaC CLI.
//
// v2.9.0 implementation. Wires Pocket ID as OIDC IdP for both Komodo +
// Pangolin in a single, idempotent call. See scripts/wire-pocketid-pangolin-komodo.sh
// for the full implementation + prerequisites.

import { spawnSync } from "node:child_process";
import { resolve, join } from "node:path";
import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { readFileSync, readdirSync, statSync } from "node:fs";

const SCRIPT_PATH = resolve(
  import.meta.dir,
  "../../scripts/wire-pocketid-pangolin-komodo.sh",
);

export async function wirePocketIdAsOidc(opts: {
  domain: string;
  force: boolean;
  dryRun: boolean;
}) {
  logStep("wire-pocketid-as-oidc");
  log(`  bash script: ${SCRIPT_PATH}`);

  const args: string[] = [];
  if (opts.dryRun) args.push("--dry-run");
  if (opts.force) args.push("--force");
  args.push(`--domain=${opts.domain}`);

  const result = spawnSync("bash", [SCRIPT_PATH, ...args], {
    stdio: "inherit",
    env: process.env,
  });

  if (result.status !== 0) {
    logError(`wire-pocketid-pangolin-komodo.sh exited with code ${result.status}`);
    throw new Error(`Pocket ID + Komodo + Pangolin wiring failed`);
  }

  // Read the audit record (the bash script writes it)
  const auditFile = findLatestAudit();
  if (auditFile) {
    logOk(`audit record: ${auditFile}`);
    try {
      return JSON.parse(readFileSync(auditFile, "utf8"));
    } catch (e) {
      logWarn(`audit record parse failed: ${(e as Error).message}`);
    }
  }
  return null;
}

function findLatestAudit(): string | null {
  const dir = "/tmp";
  let best: { file: string; mtime: number } | null = null;
  for (const f of readdirSync(dir)) {
    if (!f.startsWith("wire-pocketid-pangolin-komodo-")) continue;
    const stat = statSync(join(dir, f));
    if (!best || stat.mtimeMs > best.mtime) best = { file: join(dir, f), mtime: stat.mtimeMs };
  }
  return best?.file ?? null;
}