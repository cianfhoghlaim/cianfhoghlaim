#!/usr/bin/env bun
// validate-frontmatter.ts — fail CI if any canonical doc in
// `docs/00-core/`, `docs/01-...` through `docs/06-...` is missing the
// `truth:` frontmatter field. The `truth` field is one of:
//
//   sole         — the only authoritative source for this topic
//   partial      — coexists with other sources; flagged
//   superseded   — historical, replaced by another doc; scripts skip
//
// This script is intentionally lightweight: it does NOT enforce a
// specific value, only that the field is present.
//
// Exit code 0 = all canonical docs have `truth:`. Exit 1 = missing.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const ROOT = new URL("..", import.meta.url).pathname;

const TRUTH_FIELDS = new Set(["sole", "partial", "superseded"]);

// Only check the numbered canonical domains (not audit/archive/skills).
const CANONICAL_PREFIXES = [
  "docs/00-core",
  "docs/01-platform-architecture",
  "docs/02-architecture",
  "docs/02-data-platform",
  "docs/03-agents",
  "docs/04-ai-ml",
  "docs/05-web",
  "docs/06-infrastructure",
];

const EXCLUDE_DIRS = new Set(["archive", "node_modules", ".git"]);

function isCanonical(rel: string): boolean {
  return CANONICAL_PREFIXES.some((p) => rel.startsWith(p));
}

function* walk(dir: string): Generator<string> {
  for (const entry of readdirSync(dir)) {
    if (EXCLUDE_DIRS.has(entry)) continue;
    const full = join(dir, entry);
    const s = statSync(full);
    if (s.isDirectory()) yield* walk(full);
    else if (entry.endsWith(".md") || entry.endsWith(".mdx")) yield full;
  }
}

function hasTruthField(src: string): boolean {
  // Frontmatter is delimited by `---` lines at the top of the file.
  if (!src.startsWith("---")) return false;
  const end = src.indexOf("\n---", 3);
  if (end < 0) return false;
  const fm = src.slice(0, end);
  for (const line of fm.split("\n")) {
    const m = /^truth\s*:\s*(\S+)/.exec(line);
    if (m && TRUTH_FIELDS.has(m[1])) return true;
  }
  return false;
}

let missing = 0;
const missingList: string[] = [];

for (const path of walk(join(ROOT, "docs"))) {
  const rel = relative(ROOT, path);
  if (!isCanonical(rel)) continue;
  const src = readFileSync(path, "utf8");
  if (!hasTruthField(src)) {
    missing++;
    missingList.push(rel);
  }
}

if (missing === 0) {
  console.log(`validate-frontmatter: OK (all canonical docs have truth: field)`);
  process.exit(0);
} else {
  console.error(
    `validate-frontmatter: ${missing} canonical doc(s) missing truth: frontmatter`
  );
  for (const m of missingList.slice(0, 20)) {
    console.error(`  - ${m}`);
  }
  if (missingList.length > 20) {
    console.error(`  ... and ${missingList.length - 20} more`);
  }
  process.exit(1);
}
