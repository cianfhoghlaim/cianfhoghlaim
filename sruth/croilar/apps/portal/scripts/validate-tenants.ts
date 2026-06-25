#!/usr/bin/env bun
/**
 * Tenant config validator
 *
 * Validates every *.yaml file in config/tenants/ against tenant-schema.json.
 * Exits 0 on success, 1 on first failure.
 *
 * Usage:  bun run croilar/apps/portal/scripts/validate-tenants.ts
 */
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { parse as parseYaml } from "yaml";
import Ajv from "ajv";

const TENANTS_DIR = join(import.meta.dir, "..", "config", "tenants");
const SCHEMA_PATH = join(TENANTS_DIR, "tenant-schema.json");

const ajv = new Ajv.default({ allErrors: true, strict: false });
const schema = JSON.parse(readFileSync(SCHEMA_PATH, "utf-8"));
const validate = ajv.compile(schema);

const yamlFiles = readdirSync(TENANTS_DIR).filter(
  (f) => f.endsWith(".yaml") || f.endsWith(".yml"),
);

let failed = 0;
console.log(`[validate-tenants] Found ${yamlFiles.length} YAML tenant configs`);

for (const file of yamlFiles) {
  const path = join(TENANTS_DIR, file);
  const content = readFileSync(path, "utf-8");
  let data: unknown;
  try {
    data = parseYaml(content);
  } catch (err) {
    console.error(`  ✗ ${file}: YAML parse error: ${err}`);
    failed++;
    continue;
  }

  if (validate(data)) {
    console.log(`  ✓ ${file}`);
  } else {
    console.error(`  ✗ ${file}:`);
    for (const err of validate.errors ?? []) {
      console.error(`     - ${err.instancePath || "/"} ${err.message}`);
    }
    failed++;
  }
}

if (failed > 0) {
  console.error(`[validate-tenants] ${failed} tenant config(s) failed validation`);
  process.exit(1);
}

console.log(`[validate-tenants] All ${yamlFiles.length} tenant configs valid.`);
