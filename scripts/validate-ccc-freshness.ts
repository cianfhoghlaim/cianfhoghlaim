#!/usr/bin/env bun
// validate-ccc-freshness.ts — fail CI if the CCC (CocoIndex Code) index
// is older than the policy threshold. Two thresholds:
//   - main branch: 7 days (CI gate)
//   - feature branch: 24 hours (developer nudge)
//
// The index metadata lives in two SQLite files under `.cocoindex_code/`:
//   - `cocoindex.db` — CocoIndex flow state (mtime = last incremental update)
//   - `target_sqlite.db` — semantic search target (always mtime-equivalent)
//
// We use the mtime of the more recently updated of the two as the
// "last index run" timestamp.
//
// Exit code 0 = fresh. Exit code 1 = stale. Exit code 2 = missing index
// (treat as a hard failure on main, a soft warning on feature branches).
import { existsSync, statSync } from "node:fs";
import { join } from "node:path";

const ROOT = new URL("..", import.meta.url).pathname;
const CCC_DIR = join(ROOT, ".cocoindex_code");
const COCOINDEX_DB = join(CCC_DIR, "cocoindex.db");
const TARGET_DB = join(CCC_DIR, "target_sqlite.db");

// --- Policy ----------------------------------------------------------------
const MAX_AGE_DAYS_MAIN = 7;
const MAX_AGE_DAYS_FEATURE = 1; // 24h
const MAX_AGE_MS_MAIN = MAX_AGE_DAYS_MAIN * 24 * 60 * 60 * 1000;
const MAX_AGE_MS_FEATURE = MAX_AGE_DAYS_FEATURE * 24 * 60 * 60 * 1000;

// --- Branch detection ------------------------------------------------------
function detectBranch(): "main" | "feature" {
  try {
    const head = Bun.spawnSync({
      cmd: ["git", "rev-parse", "--abbrev-ref", "HEAD"],
      cwd: ROOT,
    });
    const branch = head.stdout.toString().trim();
    return branch === "main" || branch === "master"
      ? "main"
      : "feature";
  } catch {
    return "feature"; // default to the looser threshold
  }
}

// --- Index timestamp detection --------------------------------------------
function lastIndexTimeMs(): number | null {
  const times: number[] = [];
  for (const path of [COCOINDEX_DB, TARGET_DB]) {
    if (existsSync(path)) {
      try {
        times.push(statSync(path).mtimeMs);
      } catch {
        // ignore unreadable file
      }
    }
  }
  if (times.length === 0) return null;
  return Math.max(...times);
}

// --- Main ------------------------------------------------------------------
const branch = detectBranch();
const maxAgeMs = branch === "main" ? MAX_AGE_MS_MAIN : MAX_AGE_MS_FEATURE;
const maxAgeDays = branch === "main" ? MAX_AGE_DAYS_MAIN : MAX_AGE_DAYS_FEATURE;

const lastMs = lastIndexTimeMs();

if (lastMs === null) {
  // Missing index: soft warning on feature, hard failure on main.
  if (branch === "main") {
    console.error(
      `validate-ccc-freshness: STALE — no .cocoindex_code/ index found.\n` +
        `  Run \`bun run ccc:init && bun run ccc:index\` to (re)build.`
    );
    process.exit(1);
  } else {
    console.warn(
      `validate-ccc-freshness: WARN — no .cocoindex_code/ index found.\n` +
        `  Run \`bun run ccc:init && bun run ccc:index\` to (re)build.`
    );
    process.exit(0);
  }
}

const ageMs = Date.now() - lastMs;
const ageDays = ageMs / (24 * 60 * 60 * 1000);
const isoTime = new Date(lastMs).toISOString();
const status = ageMs > maxAgeMs ? "STALE" : "OK";
const branchLabel = branch === "main" ? "main" : "feature";

if (status === "STALE") {
  console.error(
    `validate-ccc-freshness: ${status} — last index update was ` +
      `${ageDays.toFixed(1)}d ago (threshold: ${maxAgeDays}d on ${branchLabel})\n` +
      `  Last updated: ${isoTime}\n` +
      `  Run \`bun run ccc:index\` to refresh.`
  );
  process.exit(1);
} else {
  console.log(
    `validate-ccc-freshness: ${status} (last update: ${ageDays.toFixed(1)}d ago, ` +
      `threshold: ${maxAgeDays}d on ${branchLabel})`
  );
  process.exit(0);
}
