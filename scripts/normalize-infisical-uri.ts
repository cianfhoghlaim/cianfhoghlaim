#!/usr/bin/env bun
// scripts/normalize-infisical-uri.ts
// Sweep all stacks/*/secrets.env files and convert the broken
//   {{ infisical:///<key> }}  Jinja syntax
//   {{ infisical:///<svc>/<key> }}  Jinja syntax
//   {{ infisical:///<key>?path=/<folder> }}  Jinja syntax (use folder as svc)
//   infisical://dev-baile/<key>?path=/<folder>  bare syntax (use folder as svc)
// to the canonical 2-segment Infisical URI form
//   infisical://dev-baile/<svc>/<key>
// where <svc> is the parent stack directory name (or the ?path= folder).
//
// Usage:
//   bun run scripts/normalize-infisical-uri.ts              (default: normalize, write files)
//   bun run scripts/normalize-infisical-uri.ts --check-grammar  (CI gate: scan + exit 1 if MIXED)
//
// --check-grammar mirrors the detection logic in scripts/stack-doctor.sh
// (lines 158-166): a stack's secrets.env is MIXED if it contains both at
// least one `KEY=infisical://dev-baile/...` line AND at least one
// `KEY={{ infisical:///... }}` line. Empty files (zero URI lines) are
// also reported so the CI operator can see them, but they are NOT
// mixed — they pass.

import { readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join, basename } from "node:path";

const STACKS_DIR = "./stacks";

// --------------------------------------------------------------------------
// CLI parsing (--check-grammar | default = normalize)
// --------------------------------------------------------------------------
const args = process.argv.slice(2);
const CHECK_GRAMMAR = args.includes("--check-grammar");

// Bare: `KEY=infisical://dev-baile/...` outside of comments or Jinja braces.
// Mirrors the stack-doctor.sh bash regex `^[[:space:]]*[^#[:space:]][^=]*=infisical://dev-baile/`.
// JavaScript regex does NOT support POSIX classes (e.g. `[:space:]`) inside
// `[]`, so we approximate with `\s` (whitespace) and a leading optional group.
//   - `^\s*` = optional leading whitespace (tabs / spaces)
//   - `[^#\s]` = first non-comment, non-blank char (the start of KEY)
//   - `[^=]*` = rest of KEY (no `=` allowed — KEY is single token)
//   - `=infisical:\/\/dev-baile\/` = the URI itself
// The `\s` style matches space, tab, newline, but we anchored to `^` so
// only the leading whitespace matters here.
const BARE_DETECT_RE = /^\s*[^#\s][^=]*=infisical:\/\/dev-baile\//;
// Jinja: `KEY={{ infisical:... }}` (note the inner whitespace inside `{{`)
const JINJA_DETECT_RE = /^\s*[^#\s][^=]*=\{\{\s*infisical:/;

function countGrammar(text: string): { bare: number; jinja: number } {
  let bare = 0;
  let jinja = 0;
  for (const line of text.split("\n")) {
    if (BARE_DETECT_RE.test(line)) bare++;
    else if (JINJA_DETECT_RE.test(line)) jinja++;
  }
  return { bare, jinja };
}

function auditGrammarSecretsEnv(filePath: string): { bare: number; jinja: number; mixed: boolean; zero: boolean } {
  const text = readFileSync(filePath, "utf8");
  const { bare, jinja } = countGrammar(text);
  return {
    bare,
    jinja,
    mixed: bare > 0 && jinja > 0,
    zero: bare === 0 && jinja === 0,
  };
}

let mixedCount = 0;
let zeroUriCount = 0;
let totalGrammarFiles = 0;
let totalReplacements = 0;
let totalFiles = 0;

// Match either:
//   {{ infisical:///<key>[?query] }}            (stack-name is implied from file dir)
//   {{ infisical:///<svc>/<key>[?query] }}       (svc is explicit)
const JINJA_URI_RE = /\{\{\s*infisical:\/\/\/([^}]+)\s*\}\}/g;

// Also handle the malformed bare form that resulted from a prior pass:
//   infisical://dev-baile/<key>?path=/<folder>
const BARE_URI_RE = /infisical:\/\/dev-baile\/([A-Za-z0-9_-]+)\?path=\/([A-Za-z0-9_-]+)/g;

function parseInner(inner: string, stackName: string): { svc: string; key: string } {
  // inner is the part after `infisical:///`, e.g. "croilar/db_url" or "postgres_user?path=/pangolin"
  const [pathPart, queryPart] = inner.split("?");
  const parts = pathPart.split("/").filter(Boolean);
  // Look for ?path=/<folder> in the query
  let folderSvc: string | null = null;
  if (queryPart) {
    const pathMatch = queryPart.match(/(?:^|&)path=\/([A-Za-z0-9_-]+)/);
    if (pathMatch) folderSvc = pathMatch[1];
  }
  let svc: string;
  let key: string;
  if (parts.length === 1) {
    // infisical:///<key>  →  use ?path folder if present, else stack dir
    svc = folderSvc ?? stackName;
    key = parts[0];
  } else if (parts.length === 2) {
    // infisical:///<svc>/<key>  →  use the explicit svc (folder override is unusual here)
    svc = parts[0];
    key = parts[1];
  } else {
    svc = parts[0];
    key = parts.slice(1).join("/");
  }
  return { svc, key };
}

function normalizeSecretsEnv(filePath: string, stackName: string): { changed: boolean; count: number } {
  let text = readFileSync(filePath, "utf8");
  let count = 0;

  // Pass 1: handle Jinja form
  text = text.replace(JINJA_URI_RE, (_, inner: string) => {
    count++;
    const { svc, key } = parseInner(inner, stackName);
    return `infisical://dev-baile/${svc}/${key}`;
  });

  // Pass 2: handle malformed bare form (from prior partial conversions)
  text = text.replace(BARE_URI_RE, (_, key: string, folder: string) => {
    count++;
    return `infisical://dev-baile/${folder}/${key}`;
  });

  if (count > 0) {
    writeFileSync(filePath, text, "utf8");
    return { changed: true, count };
  }
  return { changed: false, count: 0 };
}

function walkSecretsEnv(dir: string, parentStack: string = ""): void {
  let entries: string[];
  try {
    entries = readdirSync(dir);
  } catch (e) {
    console.warn(`  (skipping unreadable dir: ${dir})`);
    return;
  }
  for (const entry of entries) {
    const full = join(dir, entry);
    let st;
    try {
      st = statSync(full);
    } catch (e) {
      // dangling symlink or perms — skip
      continue;
    }
    if (st.isSymbolicLink()) {
      // skip symlinks (e.g. skills-curated → ../../.agents/skills)
      continue;
    }
    if (st.isDirectory()) {
      const stackName = parentStack || basename(full);
      walkSecretsEnv(full, stackName);
    } else if (entry === "secrets.env") {
      totalGrammarFiles++;
      if (CHECK_GRAMMAR) {
        const result = auditGrammarSecretsEnv(full);
        const stackName = parentStack || basename(dir);
        const tag = result.mixed ? "✗ MIXED" : result.zero ? "○ empty" : "✓ clean";
        console.log(
          `  [${stackName.padEnd(24)}] ${tag}  (bare=${result.bare} jinja=${result.jinja})`,
        );
        if (result.mixed) mixedCount++;
        else if (result.zero) zeroUriCount++;
      } else {
        const result = normalizeSecretsEnv(full, parentStack);
        if (result.changed) {
          totalReplacements += result.count;
          totalFiles += 1;
          console.log(`  ${full}: ${result.count} replacements`);
        }
      }
    }
  }
}

if (CHECK_GRAMMAR) {
  console.log("=== Infisical URI Grammar Check (--check-grammar) ===");
  walkSecretsEnv(STACKS_DIR);
  console.log("");
  console.log(`Scanned ${totalGrammarFiles} secrets.env files`);
  console.log(`  mixed (grammar violation): ${mixedCount}`);
  console.log(`  empty (no infisical URI):  ${zeroUriCount}`);
  if (mixedCount > 0) {
    console.error("");
    console.error(`CI GATE FAILURE: ${mixedCount} secrets.env files mix bare + Jinja grammar.`);
    console.error(
      "Mixed grammar is a silent-integration-break risk: init-vault.ts reads the bare form,",
    );
    console.error(
      "bons-locket-shim reads the Jinja form, and the two systems never see the same secret.",
    );
    console.error(
      "Fix: re-run `bun run scripts/normalize-infisical-uri.ts` (no flag) to sweep to the",
    );
    console.error("canonical bare form, then re-run this check.");
    process.exit(1);
  }
  // Empty-zero files are a soft warning, not a hard failure.
  if (zeroUriCount > 0) {
    console.warn(
      `(note: ${zeroUriCount} secrets.env files have no infisical:// URIs — review manually)`,
    );
  }
  process.exit(0);
}

console.log("=== Infisical URI Normalization ===");
walkSecretsEnv(STACKS_DIR);
console.log(`\nTotal: ${totalReplacements} replacements across ${totalFiles} files`);
