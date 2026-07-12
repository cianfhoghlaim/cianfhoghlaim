#!/usr/bin/env bun
// scripts/test-discover-secrets.ts
// Run discoverSecrets() and print summary — verifies the URI normalization sweep

import { discoverSecrets } from "../iac/sources/discover-secrets.ts";

const secrets = discoverSecrets();
console.log(`Total secrets discovered: ${secrets.length}`);

// Group by stack
const byStack = new Map<string, number>();
for (const s of secrets) {
  byStack.set(s.path, (byStack.get(s.path) ?? 0) + 1);
}
const sortedStacks = Array.from(byStack.entries()).sort();
console.log(`\nPer-stack counts:`);
for (const [path, count] of sortedStacks) {
  console.log(`  ${path}: ${count}`);
}
console.log(`\nUnique stacks: ${byStack.size}`);

// Show any malformed URIs
const malformed = secrets.filter((s) => s.path.includes("?") || !s.path.startsWith("/"));
if (malformed.length > 0) {
  console.log(`\nMalformed (${malformed.length}):`);
  for (const m of malformed.slice(0, 5)) {
    console.log(`  ${m.path}/${m.key}`);
  }
} else {
  console.log(`\nAll URIs are well-formed.`);
}
