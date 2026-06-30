// bonnegar/iac/sources/discover-stacks.ts — Walks bonnegar/stacks/*/compose.yaml
// Produces typed Stack[] with the 6-file GOLD_STANDARD check.

import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

export interface DiscoveredStack {
  name: string;
  path: string;
  composePath: string;
  hasGOLD_STANDARD: {
    compose: boolean;
    sidecar: boolean;
    secrets: boolean;
    pangolin: boolean;
    blueprint: boolean;
    envExample: boolean;
  };
  hasPangolin: boolean; // for the resource discoverer
  hasSecrets: boolean;  // for the secrets discoverer
  services: string[];  // from compose.yaml (top-level keys)
  imageTags: string[];  // for the image tag validation
}

export function discoverStacks(rootDir: string = "../../bonnegar/stacks"): DiscoveredStack[] {
  const stacks: DiscoveredStack[] = [];
  const absRoot = join(import.meta.dir, rootDir);

  // Bun.file is preferred but we use Node fs for portability
  const fs = require("node:fs");
  if (!fs.existsSync(absRoot)) return stacks;

  const entries = fs.readdirSync(absRoot, { withFileTypes: true });
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    if (entry.name.startsWith(".")) continue;

    const stackPath = join(absRoot, entry.name);
    const composePath = join(stackPath, "compose.yaml");
    if (!fs.existsSync(composePath)) continue; // Not a stack (e.g. .DS_Store, README.md, GOLD_STANDARD.md)

    const hasCompose = true;
    const hasSidecar = fs.existsSync(join(stackPath, "sidecar.yaml"));
    const hasSecrets = fs.existsSync(join(stackPath, "secrets.env"));
    const hasPangolin = fs.existsSync(join(stackPath, "pangolin.yaml"));
    const hasBlueprint = fs.existsSync(join(stackPath, "blueprint.yaml"));
    const hasEnvExample = fs.existsSync(join(stackPath, ".env.example"));

    // Parse compose.yaml to extract service names + image tags
    const composeText = fs.readFileSync(composePath, "utf8");
    const services = parseServiceNames(composeText);
    const imageTags = parseImageTags(composeText);

    stacks.push({
      name: entry.name,
      path: stackPath,
      composePath,
      hasGOLD_STANDARD: {
        compose: hasCompose,
        sidecar: hasSidecar,
        secrets: hasSecrets,
        pangolin: hasPangolin,
        blueprint: hasBlueprint,
        envExample: hasEnvExample,
      },
      hasPangolin,
      hasSecrets,
      services,
      imageTags,
    });
  }

  return stacks.sort((a, b) => a.name.localeCompare(b.name));
}

function parseServiceNames(composeText: string): string[] {
  // Top-level `services:` keys (YAML)
  const lines = composeText.split("\n");
  const services: string[] = [];
  let inServices = false;
  for (const line of lines) {
    if (/^services:\s*$/.test(line)) {
      inServices = true;
      continue;
    }
    if (inServices && /^[a-z]/.test(line) && !line.startsWith(" ")) {
      inServices = false;
      continue;
    }
    if (inServices) {
      const m = line.match(/^\s{2}([a-z][a-z0-9_-]*):\s*$/);
      if (m) services.push(m[1]);
    }
  }
  return services;
}

function parseImageTags(composeText: string): string[] {
  const tags: string[] = [];
  const re = /image:\s*["']?([a-z0-9._/-]+:[a-z0-9._-]+)["']?/gi;
  let m;
  while ((m = re.exec(composeText)) !== null) tags.push(m[1]);
  return tags;
}
