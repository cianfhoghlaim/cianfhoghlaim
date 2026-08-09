// bonneagar/iac/load-env.ts — Load the repo-root .env into process.env (the IaC runs from bonneagar/iac/, but bun's auto-load looks for .env in cwd)
//
// WHY: The IaC scripts are invoked via `cd iac && bun run cli.ts <command>` (per
// bonneagar/iac/package.json). Bun's built-in `--env-file` flag is NOT used
// (would require changing every script invocation). The repo-root .env file
// is hydrated by mise directory hooks when the operator `cd`s into the
// repo root, but when bun is invoked from `bonneagar/iac/`, the working
// directory is `bonneagar/iac/` and bun doesn't auto-load the parent
// directory's .env file.
//
// This loader uses the conventional `dotenv` parsing approach: reads the
// file, parses KEY=VALUE pairs (respecting quotes + escape characters),
// and ONLY sets process.env entries that are NOT already set (so the
// existing shell env takes precedence — this prevents stale shell vars
// from being overwritten by an outdated .env).
//
// ADDED 2026-08-15 (per the 2026-08-15-bonneagar-infra-remediation-v2 openspec change).

import { readFileSync, statSync } from "node:fs";
import { join, dirname } from "node:path";

/**
 * Find the closest .env file to the current working directory by walking
 * up the parent chain (max 8 levels to avoid filesystem root runaway).
 *
 * Returns the path of the FIRST .env file we find (closest to cwd).
 * Returns null if no .env file is found.
 */
function findEnvPath(): string | null {
  // 1. process.cwd()/.env (operator runs bun from the repo root)
  let candidate = join(process.cwd(), ".env");
  if (isRegularFile(candidate)) return candidate;
  // 2. Walk up from process.cwd() looking for a .env in parent dirs
  let dir = process.cwd();
  for (let i = 0; i < 8; i++) {
    const parent = dirname(dir);
    if (parent === dir) break; // reached filesystem root
    candidate = join(parent, ".env");
    if (isRegularFile(candidate)) return candidate;
    dir = parent;
  }
  return null;
}

function isRegularFile(path: string): boolean {
  try {
    return statSync(path).isFile();
  } catch {
    return false;
  }
}

export function loadEnv(): { loaded: string[]; skipped: string[]; envPath: string } {
  const loaded: string[] = [];
  const skipped: string[] = [];
  const envPath = findEnvPath() ?? "(none)";

  if (envPath === "(none)") {
    return { loaded, skipped, envPath };
  }

  const text = readFileSync(envPath, "utf8");
  for (const rawLine of text.split("\n")) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const eqIdx = line.indexOf("=");
    if (eqIdx === -1) continue;
    const key = line.slice(0, eqIdx).trim();
    let value = line.slice(eqIdx + 1).trim();
    // Strip inline comments (after `#` not inside quotes)
    const hashIdx = value.search(/\s#/);
    if (hashIdx !== -1) value = value.slice(0, hashIdx).trim();
    // Strip surrounding quotes
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    // Expand \n + \\ + \" escape sequences
    value = value.replace(/\\n/g, "\n").replace(/\\\\/g, "\\").replace(/\\"/g, '"');
    if (process.env[key] === undefined || process.env[key] === "") {
      process.env[key] = value;
      loaded.push(key);
    } else {
      skipped.push(key);
    }
  }
  return { loaded, skipped, envPath };
}

// Auto-load on import (side-effect import)
loadEnv();
