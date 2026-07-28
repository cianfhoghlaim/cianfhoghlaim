#!/usr/bin/env bun
/**
 * scripts/brand-rename.ts
 *
 * One-shot brand rename: bons → cianfhoghlaim.
 *
 * This script is idempotent. It rewrites only the tokens that the
 * Cianfhoghlaim brand-rename linter flags:
 *   ghcr.io/cianfhoghlaim/locket-shim, cianfhoghlaim-locket-shim, bons:
 *
 * Scope:
 *   - bonneagar/stacks/**         (active stack files)
 *   - bonneagar/scripts/**        (active IaC scripts)
 *   - mise.toml, .infisical.env  (active IaC root files)
 *   - openspec/changes/2026-07-28-reconcile-stack-contract-and-rename-bons-kcg-to-cianfhoghlaim-v1/**
 *                                 (active change; the OpenSpec change itself
 *                                  may mention the old tokens for context)
 *
 * Exclusions:
 *   - .agents/skills_backup/      (retired skills)
 *   - stedding/                   (non-canonical archive)
 *   - bonneagar/_archive/         (already deprecated with a banner)
 *   - .research/                  (transient research artifacts)
 *
 * Run with: bun run scripts/brand-rename.ts
 */

import { readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join, relative, resolve } from "node:path";

const ROOT = resolve(import.meta.dir, "..");

// Allow-list of file extensions to rewrite
const TARGET_EXTS = new Set([".md", ".yaml", ".yml", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".toml", ".env", ".sh", ".py"]);

// Replacement rules (order matters — longer first)
const REPLACEMENTS: Array<[RegExp, string]> = [
  // Image references
  [/bons-locker-shim:infisical-0\.2\.0/g, "ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0"],
  [/bons-locker-shim:0\.2\.0/g, "ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0"],
  [/\bbons-locker-shim\b/g, "ghcr.io/cianfhoghlaim/locket-shim"],
  [/\bbons-locket-shim\b/g, "cianfhoghlaim-locket-shim"],
  // Domain references
  [/bons\.ai\/docs\/locket/g, "docs.cianfhoghlaim.ie/locket"],
];

// Directories excluded from the rename
const EXCLUDED_DIRS = new Set([
  ".agents/skills_backup",
  "stedding",
  "bonneagar/_archive",
  "bonneagar/iac/pulumi/hetzner",
  "bonneagar/stacks/openclaw/skills-curated",
  "bonneagar/stacks/GOLD_STANDARD.md",
  "scripts/cianfhoghlaim-brand-rename.ts",
  ".research",
  ".git",
  "node_modules",
  "spaces/data-engineering",
]);

function isExcluded(path: string): boolean {
  for (const dir of EXCLUDED_DIRS) {
    if (path.startsWith(dir + "/") || path === dir) {
      return true;
    }
  }
  return false;
}

function* walk(dir: string): Generator<string> {
  let entries: string[];
  try {
    entries = readdirSync(dir);
  } catch {
    return;
  }
  for (const entry of entries) {
    if (entry === ".git" || entry === "node_modules") continue;
    const full = join(dir, entry);
    const rel = relative(ROOT, full);
    if (isExcluded(rel)) continue;
    let st;
    try {
      st = statSync(full);
    } catch {
      continue;
    }
    if (st.isDirectory()) {
      yield* walk(full);
    } else if (st.isFile()) {
      const dotIdx = entry.lastIndexOf(".");
      if (dotIdx >= 0) {
        const ext = entry.slice(dotIdx);
        if (TARGET_EXTS.has(ext)) yield full;
      }
    }
  }
}

let totalFiles = 0;
let totalReplacements = 0;
const summary: Array<{ file: string; changes: number }> = [];

for (const file of walk(ROOT)) {
  const rel = relative(ROOT, file);
  const original = readFileSync(file, "utf8");
  let updated = original;
  let fileChanges = 0;

  for (const [pattern, replacement] of REPLACEMENTS) {
    updated = updated.replace(pattern, () => {
      fileChanges++;
      return replacement;
    });
  }

  if (fileChanges > 0) {
    writeFileSync(file, updated);
    totalFiles++;
    totalReplacements += fileChanges;
    summary.push({ file: rel, changes: fileChanges });
  }
}

summary.sort((a, b) => b.changes - a.changes);

console.log(`brand-rename: ${totalFiles} files, ${totalReplacements} replacements`);
for (const { file, changes } of summary) {
  console.log(`  ${changes.toString().padStart(4)}  ${file}`);
}