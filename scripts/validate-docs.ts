#!/usr/bin/env bun
// validate-docs.ts — fail CI if any `docs/**/*.md` file references
// the legacy namespaces that were removed in Phase 3.6.
//
//   - `oideachais.data_platform.*`     (old data_platform subdir)
//   - `oideachais.middleware.*`        (old middleware subdir)
//   - `sruth/` (the old sruth browser layout, replaced by
//     `infrastructure/browser/`)
//   - `bonneagar/` (old Irish-translated layout, replaced by
//     `infrastructure/`)
//   - `taighde_` prefix (old research prefix, replaced by `meaisinfhoghlaim/`)
//
// Exit code 0 = clean. Exit code 1 = violations printed.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const ROOT = new URL("..", import.meta.url).pathname;
const DOCS_DIR = join(ROOT, "docs");

const FORBIDDEN: Array<{ pattern: RegExp; hint: string }> = [
  { pattern: /\boideachais\.data_platform\b/, hint: "use `oideachais.<X>` top-level packages (dlt_sources, dlt_utils, dagster_defs, ocr, ...)" },
  { pattern: /\boideachais\.middleware\b/, hint: "use `oideachais.<X>` top-level packages" },
  { pattern: /\bsruth\//, hint: "use `infrastructure/browser/` (sruth-browser is now a workspace member at infrastructure/browser/)" },
  { pattern: /\bbonneagar\//, hint: "use `infrastructure/` (Irish-translated paths were consolidated in Phase 1.1)" },
  { pattern: /\btaighde_/, hint: "use `meaisinfhoghlaim/` (research/AI/ML was renamed in Phase 1.1)" },
];

const EXCLUDE_DIRS = new Set(["archive", "node_modules", ".git", ".cocoindex_code"]);

function isSuperseded(src: string): boolean {
  // Frontmatter delimited by `---` at top; look for either:
  //   truth: superseded   (Phase 4.3 convention)
  //   status: superseded  (Phase 1.1 convention used in this repo)
  if (!src.startsWith("---")) return false;
  const end = src.indexOf("\n---", 3);
  if (end < 0) return false;
  const fm = src.slice(0, end);
  return (
    /^truth\s*:\s*superseded\s*$/m.test(fm) ||
    /^status\s*:\s*['"]?superseded['"]?\s*$/m.test(fm)
  );
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

let violations = 0;
let skipped = 0;
for (const path of walk(DOCS_DIR)) {
  const src = readFileSync(path, "utf8");
  if (isSuperseded(src)) {
    skipped++;
    continue;
  }
  // Strip frontmatter (only check the body, so `supersedes:` provenance
  // entries that reference old source paths don't trigger false positives).
  let body = src;
  if (body.startsWith("---")) {
    const end = body.indexOf("\n---", 3);
    if (end > 0) {
      body = body.slice(end + 4);
    }
  }
  const lines = body.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    for (const { pattern, hint } of FORBIDDEN) {
      if (pattern.test(line)) {
        const rel = relative(ROOT, path);
        console.error(`${rel}:${i + 1}: ${pattern}`);
        console.error(`  | ${line.trim()}`);
        console.error(`  hint: ${hint}`);
        violations++;
      }
    }
  }
}

if (violations === 0) {
  console.log(
    `validate-docs: OK (${skipped} superseded doc(s) skipped, no legacy namespace references in the rest)`
  );
  process.exit(0);
} else {
  console.error(`\nvalidate-docs: ${violations} violation(s) found`);
  process.exit(1);
}
