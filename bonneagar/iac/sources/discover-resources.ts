// bonnegar/iac/sources/discover-resources.ts — Walks bonnegar/stacks/*/pangolin.yaml
// Produces typed PangolinResource[] (filtered to non-empty).

import { join } from "node:path";
import type { PangolinResource } from "../models/pangolin.ts";
import { discoverStacks } from "./discover-stacks.ts";

// Site name -> Pangolin numeric siteId. Populated live via listSites() by
// the caller (see sync-resources.ts) rather than hardcoded here, since
// siteIds are assigned by Pangolin at site-creation time and can't be
// known statically. Falls back to this hardcoded map only when no live
// map is supplied (e.g. --dry-run without API access), so `mise run
// iac:plan` can still show *something* useful offline.
//
// NOTE (2026-08-07): verified live against the running Pangolin DB — the
// site backing this exact arm1-oci box is named "oracle" (siteId 7), NOT
// "oci.arm1" (siteId 5, a stale/orphaned registration from a past newt
// session with no currently-connected process). "bunchloch" (siteId 8)
// is the MacBook's site.
const FALLBACK_SITE_IDS: Record<string, number> = {
  oracle: 7,
  bunchloch: 8,
};

const DEFAULT_SITE_NAME = "bunchloch";

export interface DiscoverResourcesOptions {
  /** Live site name -> numeric siteId map, from PangolinClient.listSites(). */
  siteIdsByName?: Record<string, number>;
}

export function discoverResources(rootDir?: string, options: DiscoverResourcesOptions = {}): PangolinResource[] {
  const stacks = discoverStacks(rootDir);
  const resources: PangolinResource[] = [];
  const siteIdsByName = options.siteIdsByName ?? FALLBACK_SITE_IDS;

  for (const stack of stacks) {
    if (!stack.hasPangolin) continue;
    const pangolinPath = join(stack.path, "pangolin.yaml");
    const fs = require("node:fs");
    const text = fs.readFileSync(pangolinPath, "utf8");

    // Parse the 6-label shape: name, mode, full-domain, destination-port, protocol, roles
    const resource = parsePangolinYaml(text, stack.name, siteIdsByName);
    if (resource) resources.push(resource);
  }

  return resources;
}

function resolveSiteId(siteName: string | undefined, siteIdsByName: Record<string, number>, stackName: string): number {
  const name = siteName ?? DEFAULT_SITE_NAME;
  const id = siteIdsByName[name];
  if (id === undefined) {
    // FAIL LOUDLY. The previous behavior silently defaulted every
    // resource to siteId 1 regardless of what `site:` (if any) was
    // declared — that's exactly how infisical/openchamber/komodo ended up
    // bound to offline sites with no error anywhere. An unresolvable site
    // name is a real authoring mistake and must stop the sync, not
    // silently land on the wrong site.
    throw new Error(
      `discoverResources: stack "${stackName}" declares site "${name}" which is not in the known site map ` +
        `(${Object.keys(siteIdsByName).join(", ")}). Add a "site:" field matching a real Pangolin site name, ` +
        `or pass a fresh siteIdsByName from PangolinClient.listSites().`,
    );
  }
  return id;
}

function parsePangolinYaml(text: string, stackName: string, siteIdsByName: Record<string, number>): PangolinResource | null {
  // If the file is empty or all-comments, skip
  const stripped = text.replace(/^#.*$/gm, "").trim();
  if (!stripped) return null;

  // Optional `site: <name>` field, either shape. Falls back to
  // DEFAULT_SITE_NAME (bunchloch) when absent — see resolveSiteId().
  const siteMatch = text.match(/^\s*site:\s*"?([a-z0-9_.-]+)"?/m);
  const siteName = siteMatch?.[1];

  // Look for `private-resources:` block (the v0 shape)
  // OR `http:` block (the v4 shape)
  // The v4 shape is the most common in bonnegar/stacks/<name>/pangolin.yaml
  const httpRuleMatch = text.match(/rule:\s*"Host\(`([^`]+)`\)"/);
  const httpServiceMatch = text.match(/^  services:\s*\n\s+([a-z][a-z0-9_-]*):/m);
  const httpURLMatch = text.match(/url:\s*"http:\/\/([^:]+):(\d+)"/);

  if (httpRuleMatch && httpServiceMatch && httpURLMatch) {
    const fullDomain = httpRuleMatch[1];
    const destination = httpURLMatch[1];
    const destinationPort = parseInt(httpURLMatch[2], 10);
    const niceId = fullDomain.split(".")[0];
    return {
      name: niceId,
      niceId,
      subdomain: niceId,
      destination,
      destinationPort,
      siteId: resolveSiteId(siteName, siteIdsByName, stackName),
      mode: "http",
      scheme: "https",
      enabled: true,
      userIds: [],
      roleIds: [],
      clientIds: [],
      domainId: "cianfhoghlaim",
    };
  }

  // The v0 shape: `private-resources: <niceId>: { name, mode, destination, full-domain, destination-port, protocol, roles }`
  // NOTE (2026-08-07): `\Z` is a Perl/Python "end of string" escape, not a
  // JavaScript one — JS parses it as a literal "Z" character. That silently
  // broke this whole branch for any file whose private-resources block runs
  // to end-of-file without a trailing `  [a-z]` line or a second
  // `private-resources:` block after it (i.e. every real-world v0 file,
  // confirmed against bonneagar/stacks/infisical/pangolin.yaml — the only
  // current v0-grammar consumer — which never matched, before or after this
  // fix's other changes). `$(?![\s\S])` is the correct JS idiom for "true
  // end of string" that still works under the `/m` flag (which makes bare
  // `$` match end-of-line, not end-of-string).
  const privateBlockMatch = text.match(/private-resources:\s*\n\s+([a-z][a-z0-9_-]+):\s*\n([\s\S]*?)(?=\n  [a-z]|\nprivate-resources:|$(?![\s\S]))/m);
  if (privateBlockMatch) {
    const niceId = privateBlockMatch[1];
    const body = privateBlockMatch[2];
    const nameMatch = body.match(/^\s*name:\s*"?([^"\n]+)"?/m);
    const modeMatch = body.match(/^\s*mode:\s*"?([^"\n]+)"?/m);
    const destMatch = body.match(/^\s*destination:\s*"?([^"\n]+)"?/m);
    const destPortMatch = body.match(/^\s*destination-port:\s*(\d+)/m);
    const domainMatch = body.match(/^\s*full-domain:\s*"?([^"\n]+)"?/m);
    const protocolMatch = body.match(/^\s*protocol:\s*"?([^"\n]+)"?/m);
    if (nameMatch && destMatch && destPortMatch && domainMatch) {
      const fullDomain = domainMatch[1].trim();
      return {
        name: nameMatch[1].trim().replace(/^["']|["']$/g, ""),
        niceId,
        subdomain: fullDomain.split(".")[0],
        destination: destMatch[1].trim().replace(/^["']|["']$/g, ""),
        destinationPort: parseInt(destPortMatch[1], 10),
        siteId: resolveSiteId(siteName, siteIdsByName, stackName),
        mode: (modeMatch?.[1].trim().replace(/^["']|["']$/g, "") as PangolinResource["mode"]) ?? "http",
        scheme: (protocolMatch?.[1].trim().replace(/^["']|["']$/g, "") as PangolinResource["scheme"]) ?? "https",
        enabled: true,
        userIds: [],
        roleIds: [],
        clientIds: [],
        domainId: "cianfhoghlaim",
      };
    }
  }

  // If we can't parse it, return null (the caller skips it)
  return null;
}
