// bonneagar/iac/sources/discover-sites.ts — Walks stacks/*/site.yaml
// Produces typed SiteSpec[] for the iac:sync:sites command.

import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { discoverStacks } from "./discover-stacks.ts";

export interface SiteSpec {
  niceId: string;
  name: string;
  description?: string;
  address?: string;
  type?: "local" | "remote";
  stackName: string;
  stackPath: string;
  infisicalSecretPrefix?: string;
  infisicalSecretPath?: string;
}

export function discoverSites(rootDir?: string): SiteSpec[] {
  const stacks = discoverStacks(rootDir);
  const sites: SiteSpec[] = [];

  for (const stack of stacks) {
    const sitePath = join(stack.path, "site.yaml");
    if (!existsSync(sitePath)) continue;
    const text = readFileSync(sitePath, "utf8");
    const site = parseSiteYaml(text, stack.name, stack.path);
    if (site) sites.push(site);
  }

  return sites;
}

function parseSiteYaml(text: string, stackName: string, stackPath: string): SiteSpec | null {
  // Parse: pangolin.sites: [ { niceId, name, description, address, type, ... }, ... ]
  const sitesBlock = text.match(/sites:\s*\n([\s\S]*?)(?=\npangolin:|\n[a-z][a-z-]*:|\Z)/m);
  if (!sitesBlock) return null;

  const block = sitesBlock[1];

  // Naive multi-entry parser — finds each `- niceId:` block
  const entries: SiteSpec[] = [];
  const lines = block.split("\n");
  let current: Partial<SiteSpec> | null = null;
  for (const raw of lines) {
    const line = raw.replace(/\r$/, "");
    const itemMatch = line.match(/^\s*-\s*([a-zA-Z_]+):\s*(.*?)\s*$/);
    if (itemMatch) {
      if (current && current.niceId) {
        entries.push({ stackName, stackPath, ...current } as SiteSpec);
      }
      current = { [itemMatch[1]]: unquote(itemMatch[2]) };
    } else {
      const kv = line.match(/^\s{4,}([a-zA-Z_]+):\s*(.*?)\s*$/);
      if (kv && current) {
        current[kv[1] as keyof SiteSpec] = unquote(kv[2]) as never;
      }
    }
  }
  if (current && current.niceId) {
    entries.push({ stackName, stackPath, ...current } as SiteSpec);
  }
  return entries[0] ?? null;
}

function unquote(s: string): string {
  if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) {
    return s.slice(1, -1);
  }
  return s;
}
