#!/usr/bin/env -S bun run
/**
 * croilar/scripts/migrate-personas-to-streams.ts
 *
 * One-shot migration that finishes the persona → stream refactor:
 *
 *   1. Renames remaining `notebooks/aleyum|cianfhoghlaim` and
 *      `packages/i18n/src/resources/aleyum|cianfhoghlaim` directories
 *      (in case the manual steps were skipped).
 *   2. Rewrites Python and TypeScript files that still reference the
 *      legacy `flowId` / `flow_id` / `carlcashman` strings.
 *   3. Emits a CSV diff of every changed path for review.
 *
 * Idempotent: re-running on an already-migrated repo is a no-op
 * (a small "no changes needed" CSV is emitted and the process exits 0).
 *
 * Usage:
 *   bun run croilar/scripts/migrate-personas-to-streams.ts
 *
 * After running, commit the changes and delete this script.
 */

import { execSync } from "node:child_process";
import { readFileSync, writeFileSync, existsSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const REPO_ROOT = execSync("git rev-parse --show-toplevel", { encoding: "utf8" }).trim();
const CROILAR = join(REPO_ROOT, "croilar");

interface Change {
  path: string;
  kind: "rename" | "rewrite" | "delete";
  detail: string;
}

const changes: Change[] = [];

// --------------------------------------------------------------------------
// 1. Directory renames (idempotent: only rename if source still exists)
// --------------------------------------------------------------------------

const renames: Array<[string, string]> = [
  // notebooks
  [join(CROILAR, "notebooks/aleyum"), join(CROILAR, "notebooks/streams/music")],
  [join(CROILAR, "notebooks/cianfhoghlaim"), join(CROILAR, "notebooks/streams/teaching")],
  // i18n resources
  [join(CROILAR, "packages/i18n/src/resources/aleyum"), join(CROILAR, "packages/i18n/src/resources/streams/music")],
  [join(CROILAR, "packages/i18n/src/resources/cianfhoghlaim"), join(CROILAR, "packages/i18n/src/resources/streams/teaching")],
];

for (const [src, dst] of renames) {
  if (existsSync(src) && !existsSync(dst)) {
    execSync(`git mv "${src}" "${dst}"`, { cwd: REPO_ROOT, stdio: "inherit" });
    changes.push({ path: relative(REPO_ROOT, dst), kind: "rename", detail: `moved from ${relative(REPO_ROOT, src)}` });
  }
}

// --------------------------------------------------------------------------
// 2. Text rewrites — only files that still contain the legacy strings
// --------------------------------------------------------------------------

const rewriteRules: Array<{ pattern: RegExp; replacement: string; note: string }> = [
  { pattern: /\bflow_id\b/g, replacement: "stream_id", note: "Python flow_id → stream_id" },
  { pattern: /\bflowId\b/g, replacement: "streamId", note: "TS flowId → streamId" },
  { pattern: /"carlcashman"/g, replacement: '"teaching"', note: "carlcashman default → teaching stream" },
  { pattern: /'carlcashman'/g, replacement: "'teaching'", note: "carlcashman default → teaching stream" },
  { pattern: /aleyum_dagster_secrets/g, replacement: "croilar_dagster_secrets", note: "compose secret rename" },
  { pattern: /aleyum-postgres\b/g, replacement: "croilar-postgres", note: "compose postgres rename" },
  { pattern: /aleyum-data\b/g, replacement: "croilar-data", note: "volume rename" },
  { pattern: /aleyum-assets\b/g, replacement: "croilar-assets", note: "R2 bucket legacy alias" },
];

function walk(dir: string, out: string[] = []): string[] {
  if (!existsSync(dir)) return out;
  for (const entry of execSync(`git ls-files "${dir}"`, { cwd: REPO_ROOT, encoding: "utf8" }).split("\n").filter(Boolean)) {
    out.push(entry);
  }
  return out;
}

const tracked = [
  ...walk(join(CROILAR, "pipelines")),
  ...walk(join(CROILAR, "baml")),
  ...walk(join(CROILAR, "baml_src")),
  ...walk(join(CROILAR, "dagster_assets")),
  ...walk(join(CROILAR, "_shared")),
  ...walk(join(CROILAR, "tests")),
  ...walk(join(CROILAR, "agent_os")),
  ...walk(join(CROILAR, "apps")),
  ...walk(join(CROILAR, "packages")),
  ...walk(join(CROILAR, "notebooks")),
];

for (const absPath of tracked) {
  const rel = relative(REPO_ROOT, absPath);
  if (!existsSync(absPath)) continue;
  const stat = statSync(absPath);
  if (!stat.isFile()) continue;
  if (absPath.endsWith(".csv") || absPath.endsWith(".duckdb") || absPath.endsWith(".lancedb")) continue;

  let text: string;
  try {
    text = readFileSync(absPath, "utf8");
  } catch {
    continue;
  }

  let mutated = text;
  const applied: string[] = [];
  for (const rule of rewriteRules) {
    if (rule.pattern.test(mutated)) {
      mutated = mutated.replace(rule.pattern, rule.replacement);
      applied.push(rule.note);
    }
  }

  if (mutated !== text) {
    writeFileSync(absPath, mutated);
    changes.push({ path: rel, kind: "rewrite", detail: applied.join("; ") });
  }
}

// --------------------------------------------------------------------------
// 3. Emit CSV diff
// --------------------------------------------------------------------------

const csvPath = join(REPO_ROOT, "croilar-personas-to-streams-migration.csv");
const csv = [
  "kind,path,detail",
  ...changes.map((c) => `${c.kind},${JSON.stringify(c.path)},${JSON.stringify(c.detail)}`),
].join("\n");
writeFileSync(csvPath, csv + "\n");

console.log(`Migration complete: ${changes.length} change(s) recorded.`);
console.log(`CSV diff: ${relative(REPO_ROOT, csvPath)}`);
if (changes.length === 0) {
  console.log("No changes needed — repo is already migrated.");
}
