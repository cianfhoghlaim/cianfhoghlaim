#!/usr/bin/env bun
// scripts/strip-trailing-whitespace.ts
// Strip trailing whitespace from all secrets.env files (post-URI normalization cleanup)

import { readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const STACKS_DIR = "./stacks";

let totalFiles = 0;

function stripWhitespace(filePath: string): void {
  const text = readFileSync(filePath, "utf8");
  const stripped = text.split("\n").map((line) => line.replace(/[ \t]+$/, "")).join("\n");
  if (stripped !== text) {
    writeFileSync(filePath, stripped, "utf8");
    totalFiles++;
    console.log(`  ${filePath}`);
  }
}

function walk(dir: string): void {
  let entries: string[];
  try {
    entries = readdirSync(dir);
  } catch {
    return;
  }
  for (const entry of entries) {
    const full = join(dir, entry);
    let st;
    try {
      st = statSync(full);
    } catch {
      continue;
    }
    if (st.isSymbolicLink()) continue;
    if (st.isDirectory()) walk(full);
    else if (entry === "secrets.env") stripWhitespace(full);
  }
}

console.log("=== Stripping trailing whitespace ===");
walk(STACKS_DIR);
console.log(`\nTotal: ${totalFiles} files cleaned`);
