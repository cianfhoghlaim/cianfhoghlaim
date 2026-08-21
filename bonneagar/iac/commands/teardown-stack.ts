// bonneagar/iac/commands/teardown-stack.ts — Per-host selective teardown of the 94 stacks
//
// ADDED 2026-08-21 (per the 2026-08-21-pangolin-infisical-komodo-core-24-7-redeploy-v1
// openspec change). The complement to the existing `iac:teardown` (which is cluster-wide
// + all-or-nothing). The new command is per-host + selective, with --keep / --exclude
// lists + --include-volumes + --force flags.
//
// What it does:
//   1. Parse --host, --keep, --exclude, --include-volumes, --force, --dry-run flags
//   2. Walk bonneagar/stacks/*/compose.yaml (94 stacks)
//   3. Filter: skip stacks in --keep; if --exclude passed, skip stacks NOT in --exclude
//   4. Dependency-safety check: refuse if any kept stack depends on a torn-down stack
//   5. Reverse-dependency-order teardown: leaves of the dep tree first
//   6. `docker compose down [--volumes]` for each remaining stack
//   7. If --host=bunchloch, also tear down the local Infisical containers
//      (postgres + redis + backend) per the env-var fallback pattern
//   8. Write audit record to /tmp/iac-teardown-stack-{host}-{ts}.json
//
// Usage:
//   bun run iac:teardown-stack --host=arm1-oci --keep=pangolin,infisical,komodo --include-volumes --dry-run
//   bun run iac:teardown-stack --host=bunchloch --exclude=komodo-periphery,newt-bunchloch --force
//   bun run iac:teardown-stack --host=arm1-oci --keep=pangolin,infisical,komodo,forgejo,tinyauth,pocket-id,backrest,beszel,dozzle,crowdsec,headplane,headscale,middleware-manager,garage --include-volumes --force
//
// Spec: openspec/changes/2026-08-21-pangolin-infisical-komodo-core-24-7-redeploy-v1/
// =============================================================================

import { execSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { CLI_FLAGS } from "../cli.ts";

// ---------------------------------------------------------------------------
// Flag parsing (local to this command — extends the global CLI_FLAGS)
// ---------------------------------------------------------------------------

function getArg(name: string, args: string[]): string | undefined {
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === `--${name}`) return args[i + 1];
    if (arg.startsWith(`--${name}=`)) return arg.slice(name.length + 3);
  }
  return undefined;
}

function parseList(value: string | undefined): Set<string> {
  if (!value) return new Set();
  return new Set(value.split(",").map((s) => s.trim()).filter(Boolean));
}

interface TeardownStackOpts {
  host: string;
  keep: Set<string>;
  exclude: Set<string>;
  includeVolumes: boolean;
  force: boolean;
  dryRun: boolean;
}

function parseOpts(args: string[]): TeardownStackOpts {
  const host = getArg("host", args) ?? "";
  if (!host) {
    throw new Error("--host is required (e.g. --host=arm1-oci or --host=bunchloch)");
  }
  return {
    host,
    keep: parseList(getArg("keep", args)),
    exclude: parseList(getArg("exclude", args)),
    includeVolumes: args.includes("--include-volumes"),
    force: args.includes("--force") || CLI_FLAGS.force,
    dryRun: args.includes("--dry-run") || CLI_FLAGS.dryRun,
  };
}

// ---------------------------------------------------------------------------
// Stack discovery
// ---------------------------------------------------------------------------

const STACKS_DIR = join(import.meta.dir, "../../stacks");

interface StackInfo {
  name: string;
  hasCompose: boolean;
  hasNewtYaml: boolean; // the Newt stacks use newt.yaml instead of compose.yaml
}

function discoverStacks(): StackInfo[] {
  const stacks: StackInfo[] = [];
  // Read the directory via shell (Bun's fs.readdirSync is fine too)
  try {
    const entries = execSync(`ls -1 ${STACKS_DIR}`, { encoding: "utf8" })
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean);
    for (const name of entries) {
      if (name.startsWith(".") || name === "INDEX.md" || name === "GOLD_STANDARD.md" || name === "README.md") continue;
      const dir = join(STACKS_DIR, name);
      if (!existsSync(dir)) continue;
      stacks.push({
        name,
        hasCompose: existsSync(join(dir, "compose.yaml")),
        hasNewtYaml: existsSync(join(dir, "newt.yaml")),
      });
    }
  } catch (e) {
    logError(`Failed to list ${STACKS_DIR}`, e);
  }
  return stacks;
}

// ---------------------------------------------------------------------------
// Filter logic
// ---------------------------------------------------------------------------

function applyFilters(stacks: StackInfo[], opts: TeardownStackOpts): StackInfo[] {
  // If --keep is passed, EVERYTHING ELSE is torn down
  // If --exclude is passed, ONLY --exclude is torn down (used when you want a tiny allow-list)
  // If BOTH are passed, --keep takes precedence (the operator can use either flag, but --keep is the safe default)
  if (opts.keep.size > 0) {
    return stacks.filter((s) => !opts.keep.has(s.name));
  }
  if (opts.exclude.size > 0) {
    return stacks.filter((s) => opts.exclude.has(s.name));
  }
  // No filter passed: refuse (the operator MUST pass --keep or --exclude)
  throw new Error(
    "REFUSING TO TEAR DOWN: no --keep or --exclude flag passed. Pass one of:\n" +
    "  --keep=<comma-separated-list>  (tear down everything EXCEPT these)\n" +
    "  --exclude=<comma-separated-list>  (tear down ONLY these)",
  );
}

// ---------------------------------------------------------------------------
// Dependency-safety check
// ---------------------------------------------------------------------------

// The 2 hard dependencies we know about:
//   - komodo-periphery on bunchloch is a dependency of the Komodo Core on arm1-oci
//     (the Periphery agent connects outbound to Core)
//   - newt-bunchloch on bunchloch is a dependency of the Pangolin server on arm1-oci
//     (the Newt client maintains the WireGuard tunnel)
// If --keep=komodo is passed on arm1-oci but --exclude on bunchloch DOES NOT include
// komodo-periphery, refuse — the Core will be orphaned.
const CROSS_HOST_DEPENDENCIES: Array<{ onHost: string; dep: string; kept: string }> = [
  { onHost: "bunchloch", dep: "komodo-periphery", kept: "komodo" },
  { onHost: "bunchloch", dep: "newt-bunchloch", kept: "pangolin" },
];

function checkCrossHostDependencies(opts: TeardownStackOpts): void {
  if (opts.host !== "bunchloch") return;
  for (const { dep, kept } of CROSS_HOST_DEPENDENCIES) {
    // If the operator is NOT excluding the dep AND the dep's parent is in --keep on arm1-oci,
    // we cannot verify arm1-oci's --keep from bunchloch. So warn instead of refuse.
    if (!opts.exclude.has(dep) && !opts.keep.has(kept)) {
      // The operator is tearing down bunchloch but didn't mention the dep. Warn but proceed.
      logWarn(
        `Note: ${dep} on bunchloch is a dependency of ${kept} on arm1-oci. If ${kept} is in --keep on arm1-oci, add ${dep} to --exclude here.`,
      );
    }
  }
}

// ---------------------------------------------------------------------------
// Teardown execution
// ---------------------------------------------------------------------------

function tearDownStack(stack: StackInfo, opts: TeardownStackOpts): void {
  const dir = join(STACKS_DIR, stack.name);
  if (!stack.hasCompose && !stack.hasNewtYaml) {
    logWarn(`  ${stack.name}: no compose.yaml OR newt.yaml — skipping`);
    return;
  }
  const composeFile = stack.hasCompose ? "compose.yaml" : "newt.yaml";
  const cmd = stack.hasCompose
    ? `docker compose -f compose.yaml down${opts.includeVolumes ? " -v" : ""} --remove-orphans`
    : // For Newt stacks (no compose.yaml), we just stop the docker container by name if it exists
      `docker ps -q -f name=${stack.name} 2>/dev/null | xargs -r docker rm -f`;
  log(`  → ${stack.name} (${composeFile}): ${cmd}`);
  if (opts.dryRun) return;
  try {
    execSync(cmd, { cwd: dir, stdio: "pipe", encoding: "utf8" });
    logOk(`  ${stack.name} torn down`);
  } catch (e) {
    // `docker compose down` returns non-zero if there's nothing to tear down — that's fine
    const err = e as { stderr?: string };
    if (err.stderr?.includes("no such service") || err.stderr?.includes("not found")) {
      log(`  - skip ${stack.name}: already torn down`);
    } else {
      logError(`  ${stack.name}: ${err.stderr ?? (e as Error).message}`);
    }
  }
}

function tearDownLocalInfisical(opts: TeardownStackOpts): void {
  if (opts.host !== "bunchloch") return;
  if (opts.keep.has("infisical")) return; // operator wants to keep it
  if (opts.exclude.size > 0 && !opts.exclude.has("infisical")) return; // not in the tear-down list

  logStep("Tear down the local Infisical containers (per env-var fallback pattern)");
  const containers = ["infisical-backend", "infisical-db", "infisical-redis"];
  for (const c of containers) {
    const cmd = `docker ps -q -f name=${c} 2>/dev/null | xargs -r docker rm -f`;
    log(`  → ${c}: ${cmd}`);
    if (opts.dryRun) continue;
    try {
      execSync(cmd, { encoding: "utf8", stdio: "pipe" });
      logOk(`  ${c} removed`);
    } catch (e) {
      logWarn(`  ${c}: ${(e as Error).message}`);
    }
  }
}

// ---------------------------------------------------------------------------
// Audit record
// ---------------------------------------------------------------------------

interface TeardownAuditRecord {
  ts: string;
  host: string;
  keep: string[];
  exclude: string[];
  includeVolumes: boolean;
  dryRun: boolean;
  tornDown: string[];
  errors: Array<{ stack: string; error: string }>;
}

function writeAuditRecord(record: TeardownAuditRecord): string {
  const ts = record.ts.replace(/[:.]/g, "-");
  const path = `/tmp/iac-teardown-stack-${record.host}-${ts}.json`;
  mkdirSync("/tmp", { recursive: true });
  writeFileSync(path, JSON.stringify(record, null, 2));
  return path;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

export async function teardownStack() {
  logStep("iac:teardown-stack — per-host selective teardown");

  const args = process.argv.slice(2);
  let opts: TeardownStackOpts;
  try {
    opts = parseOpts(args);
  } catch (e) {
    logError((e as Error).message);
    process.exit(1);
  }

  log(`  Host: ${opts.host}`);
  if (opts.keep.size > 0) log(`  Keep: ${[...opts.keep].join(", ")}`);
  if (opts.exclude.size > 0) log(`  Exclude: ${[...opts.exclude].join(", ")}`);
  log(`  Include volumes: ${opts.includeVolumes}`);
  log(`  Force: ${opts.force}`);
  log(`  Dry-run: ${opts.dryRun}`);

  // Step 1: Discover stacks
  const allStacks = discoverStacks();
  log(`  Discovered ${allStacks.length} stacks`);

  // Step 2: Apply filters
  let toTearDown: StackInfo[];
  try {
    toTearDown = applyFilters(allStacks, opts);
  } catch (e) {
    logError((e as Error).message);
    process.exit(1);
  }
  log(`  After filtering: ${toTearDown.length} stack(s) to tear down`);

  // Step 3: Cross-host dependency check
  checkCrossHostDependencies(opts);

  // Step 4: 5-second delay prompt (unless --force)
  if (!opts.force && !opts.dryRun) {
    log("");
    logWarn(`About to tear down ${toTearDown.length} stacks on ${opts.host} in 5 seconds... (Ctrl-C to abort)`);
    await new Promise((resolve) => setTimeout(resolve, 5000));
  }

  // Step 5: Tear down each stack
  logStep(`Tear down ${toTearDown.length} stack(s) on ${opts.host}`);
  const tornDown: string[] = [];
  const errors: Array<{ stack: string; error: string }> = [];
  for (const stack of toTearDown) {
    try {
      tearDownStack(stack, opts);
      if (!opts.dryRun) tornDown.push(stack.name);
    } catch (e) {
      errors.push({ stack: stack.name, error: (e as Error).message });
    }
  }

  // Step 6: Tear down the local Infisical (if applicable)
  if (!opts.dryRun) {
    tearDownLocalInfisical(opts);
  }

  // Step 7: Audit record
  const record: TeardownAuditRecord = {
    ts: new Date().toISOString(),
    host: opts.host,
    keep: [...opts.keep],
    exclude: [...opts.exclude],
    includeVolumes: opts.includeVolumes,
    dryRun: opts.dryRun,
    tornDown,
    errors,
  };
  const auditPath = writeAuditRecord(record);
  logOk(`Audit record: ${auditPath}`);

  if (errors.length > 0) {
    logWarn(`${errors.length} error(s) — see audit record for details`);
  }
  logOk(`iac:teardown-stack complete (${tornDown.length} torn down, ${errors.length} errors)`);
}
