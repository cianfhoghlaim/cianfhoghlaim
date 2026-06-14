#!/usr/bin/env bun
// validate-openspec-stale.ts — fail CI if any `openspec/changes/*/`
// has been idle for more than 14 days OR if any
// `openspec/specs/*/spec.md` has zero `### Requirement:` blocks.
//
// Exit code 0 = fresh & well-formed. Exit code 1 = violations printed.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const ROOT = new URL("..", import.meta.url).pathname;
const CHANGES_DIR = join(ROOT, "openspec", "changes");
const SPECS_DIR = join(ROOT, "openspec", "specs");

const IDLE_DAYS = 14;
const IDLE_MS = IDLE_DAYS * 24 * 60 * 60 * 1000;

function* walk(dir: string): Generator<string> {
  if (!statSafe(dir)) return;
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    const s = statSafe(full);
    if (!s) continue;
    if (s.isDirectory()) yield* walk(full);
    else if (entry.endsWith(".md")) yield full;
  }
}

function statSafe(p: string) {
  try {
    return statSync(p);
  } catch {
    return null;
  }
}

let violations = 0;
const now = Date.now();

// 1. Stale changes (no proposal.md modified in the last 14d).
for (const changeDir of readdirSafe(CHANGES_DIR)) {
  const proposal = join(CHANGES_DIR, changeDir, "proposal.md");
  if (!statSafe(proposal)) continue;
  const s = statSync(proposal);
  const ageDays = (now - s.mtimeMs) / (24 * 60 * 60 * 1000);
  if (ageDays > IDLE_DAYS) {
    console.error(
      `STALE: openspec/changes/${changeDir}/proposal.md is ${ageDays.toFixed(1)}d old (>${IDLE_DAYS}d)`
    );
    violations++;
  }
}

// 2. Specs with 0 requirements.
for (const specPath of walk(SPECS_DIR)) {
  if (!specPath.endsWith("/spec.md")) continue;
  const rel = relative(ROOT, specPath);
  const src = readFileSync(specPath, "utf8");
  const reqCount = (src.match(/^###\s+Requirement\s*:/gm) || []).length;
  if (reqCount === 0) {
    console.error(`EMPTY SPEC: ${rel} has 0 ### Requirement: blocks`);
    violations++;
  }
}

if (violations === 0) {
  console.log(
    `validate-openspec-stale: OK (no changes idle >${IDLE_DAYS}d, all specs have requirements)`
  );
  process.exit(0);
} else {
  console.error(`\nvalidate-openspec-stale: ${violations} violation(s)`);
  process.exit(1);
}

function readdirSafe(p: string): string[] {
  try {
    return readdirSync(p);
  } catch {
    return [];
  }
}
