// bonnegar/iac/sources/discover-resources.ts — Walks bonnegar/stacks/*/pangolin.yaml
// Produces typed PangolinResource[] (filtered to non-empty).

import { join } from "node:path";
import type { PangolinResource } from "../models/pangolin.ts";
import { discoverStacks } from "./discover-stacks.ts";

export function discoverResources(rootDir?: string): PangolinResource[] {
  const stacks = discoverStacks(rootDir);
  const resources: PangolinResource[] = [];

  for (const stack of stacks) {
    if (!stack.hasPangolin) continue;
    const pangolinPath = join(stack.path, "pangolin.yaml");
    const fs = require("node:fs");
    const text = fs.readFileSync(pangolinPath, "utf8");

    // Parse the 6-label shape: name, mode, full-domain, destination-port, protocol, roles
    const resource = parsePangolinYaml(text, stack.name);
    if (resource) resources.push(resource);
  }

  return resources;
}

function parsePangolinYaml(text: string, stackName: string): PangolinResource | null {
  // If the file is empty or all-comments, skip
  const stripped = text.replace(/^#.*$/gm, "").trim();
  if (!stripped) return null;

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
      siteId: niceId === "komodo" || niceId === "openclaw" || niceId === "langfuse" || niceId === "litellm" ? 1 : 1, // default to bunchloch=1; user can override later
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
  const privateBlockMatch = text.match(/private-resources:\s*\n\s+([a-z][a-z0-9_-]+):\s*\n([\s\S]*?)(?=\n  [a-z]|\nprivate-resources:|\Z)/m);
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
        siteId: 1,
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
