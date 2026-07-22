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

import { readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join, basename } from "node:path";

const STACKS_DIR = "./stacks";

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
      const result = normalizeSecretsEnv(full, parentStack);
      if (result.changed) {
        totalReplacements += result.count;
        totalFiles += 1;
        console.log(`  ${full}: ${result.count} replacements`);
      }
    }
  }
}

console.log("=== Infisical URI Normalization ===");
walkSecretsEnv(STACKS_DIR);
console.log(`\nTotal: ${totalReplacements} replacements across ${totalFiles} files`);
