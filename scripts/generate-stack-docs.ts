#!/usr/bin/env bun
// =============================================================================
// scripts/generate-stack-docs.ts
// =============================================================================
// Walk every bonneagar/stacks/<name>/ and emit a docs/stacks/<name>.md for
// any stack that is missing one. The doc follows the 4-section template
// established by the hand-written baseline (`docs/stacks/cal-diy.md`,
// `docs/stacks/infisical.md`, etc.):
//
//   1. Purpose for the Cianfhoghlaim project (1-2 paragraphs)
//   2. Why it stays in komodo/pangolin/infisical GitOps (1-2 paragraphs)
//   3. Cross-references (bullet list of ops + code + IaC + Pangolin)
//   4. Tags (host / tier / project label triplets)
//
// Behaviour:
//   - For each stack missing docs/stacks/<name>.md:
//     - Read compose.yaml + README.md (optional) + blueprint.yaml (optional)
//       + pangolin.yaml (optional)
//     - Extract the service list, the primary image, the port, and the
//       declared domain
//     - Render a 4-section doc that mirrors the hand-written baseline
//       (between 22-50 lines; terse)
//   - If --apply is NOT passed, the script runs in dry-run mode (prints the
//     intended writes without touching disk)
//   - If --apply IS passed, the script writes the missing docs
//   - --stack=<name> limits to a single stack (debugging)
//
// Closes the `2026-07-14-t1-docs-stacks-and-secrets-env-v1` follow-up
// (issue #107: 94 docs + 18 secrets.env refactor + new generator).
//
// USAGE:
//   bun run scripts/generate-stack-docs.ts               # dry-run
//   bun run scripts/generate-stack-docs.ts --apply      # write files
//   bun run scripts/generate-stack-docs.ts --stack=drop # single stack (dry)
//   bun run scripts/generate-stack-docs.ts --apply --stack=hermes
// =============================================================================

import {
  readdirSync,
  readFileSync,
  writeFileSync,
  existsSync,
} from "node:fs";
import { join } from "node:path";

const STACKS_DIR = "bonneagar/stacks";
const DOCS_DIR = "docs/stacks";
const APPLY = process.argv.includes("--apply");
const STACK_FILTER = (() => {
  const flag = process.argv.find((a) => a.startsWith("--stack="));
  return flag ? flag.split("=")[1] : null;
})();

interface ParsedCompose {
  name: string | null;
  services: string[];
  images: { service: string; image: string }[];
  ports: { service: string; ports: string[] }[];
  descriptionComment: string | null;
}

interface ParsedBlueprint {
  raw: string;
  isPublic: boolean;
  isPrivate: boolean;
  domain: string | null;
  destinationPort: number | null;
  protocol: string | null;
}

interface StackResult {
  name: string;
  path: string;
  stackDir: string;
  composePath: string;
  composeFileName: string;
  readmePath: string;
  blueprintPath: string;
  pangolinPath: string;
  docPath: string;
  compose: ParsedCompose | null;
  hasReadme: boolean;
  hasBlueprint: boolean;
  blueprint: ParsedBlueprint | null;
  docExists: boolean;
  willCreate: boolean;
  isStagingArea: boolean;
}

function discoverStacks(): StackResult[] {
  const results: StackResult[] = [];
  const entries = readdirSync(STACKS_DIR, { withFileTypes: true });
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    if (entry.name.startsWith(".")) continue;
    if (STACK_FILTER && entry.name !== STACK_FILTER) continue;

    const stackDir = join(STACKS_DIR, entry.name);
    const readmePath = join(stackDir, "README.md");
    const blueprintPath = join(stackDir, "blueprint.yaml");
    const pangolinPath = join(stackDir, "pangolin.yaml");
    const docPath = join(DOCS_DIR, `${entry.name}.md`);

    // Prefer `compose.yaml`; fall back to `docker-compose.yaml` (newt-style)
    const composePath = existsSync(join(stackDir, "compose.yaml"))
      ? join(stackDir, "compose.yaml")
      : existsSync(join(stackDir, "docker-compose.yaml"))
        ? join(stackDir, "docker-compose.yaml")
        : null;
    if (!composePath) continue; // not a real compose stack
    const composeFileName = composePath.split("/").pop() ?? "compose.yaml";

    const compose = parseCompose(readFileSync(composePath, "utf8"));
    const hasReadme = existsSync(readmePath);
    const hasBlueprint = existsSync(blueprintPath);
    const blueprint = hasBlueprint
      ? parseBlueprint(readFileSync(blueprintPath, "utf8"))
      : null;
    const docExists = existsSync(docPath);
    const isStagingArea =
      compose.name?.includes("multistack") ||
      compose.name?.includes("staging") ||
      compose.services.length === 0;

    results.push({
      name: entry.name,
      path: stackDir,
      stackDir,
      composePath,
      composeFileName,
      readmePath,
      blueprintPath,
      pangolinPath,
      docPath,
      compose,
      hasReadme,
      hasBlueprint,
      blueprint,
      docExists,
      willCreate: !docExists,
      isStagingArea,
    });
  }
  return results.sort((a, b) => a.name.localeCompare(b.name));
}

// -----------------------------------------------------------------------------
// Compose parsing — best-effort line-based scan. Avoids pulling in a YAML lib.
// -----------------------------------------------------------------------------

function parseCompose(text: string): ParsedCompose {
  const lines = text.split("\n");
  let name: string | null = null;
  const services: string[] = [];
  const images: { service: string; image: string }[] = [];
  const ports: { service: string; ports: string[] }[] = [];
  let currentService: string | null = null;
  // Track which top-level section we're in: "", "services", "volumes",
  // "networks", "configs", "secrets", etc.
  let topSection = "";
  let inPorts = false;
  const descriptionComments: string[] = [];

  for (const rawLine of lines) {
    const line = rawLine.replace(/#.*$/, "").trimEnd();
    const trimmed = line.trim();
    if (!trimmed) continue;

    // Top-level `name:` directive (before any section header)
    if (
      /^name:\s+/.test(trimmed) &&
      !currentService &&
      topSection === ""
    ) {
      const m = trimmed.match(/^name:\s+(.+?)\s*$/);
      if (m) name = m[1] ?? null;
      continue;
    }

    // Top-level section header (no indent)
    const sectionMatch = trimmed.match(/^([a-z_]+):\s*$/);
    if (sectionMatch && sectionMatch[1] && rawLine.startsWith(sectionMatch[1] + ":")) {
      const section = sectionMatch[1];
      if (
        section === "services" ||
        section === "volumes" ||
        section === "networks" ||
        section === "configs" ||
        section === "secrets" ||
        section === "x-*" // ignore extensions
      ) {
        topSection = section;
        currentService = null;
        inPorts = false;
        continue;
      }
    }

    // Capture file-level comments for the description
    if (topSection === "" && trimmed.startsWith("#")) {
      descriptionComments.push(trimmed.slice(1).trim());
      continue;
    }

    // Only collect service names inside `services:`
    if (topSection !== "services") continue;

    // First-level (2-space indent) service name
    if (
      /^[a-z][a-z0-9_-]*:\s*$/.test(trimmed) &&
      rawLine.startsWith("  ") &&
      !rawLine.startsWith("    ")
    ) {
      currentService = trimmed.replace(/:\s*$/, "");
      services.push(currentService);
      inPorts = false;
      continue;
    }

    if (!currentService) continue;

    // `image:` line within a service
    const imageMatch = trimmed.match(/^image:\s+(.+?)\s*$/);
    if (imageMatch && imageMatch[1]) {
      images.push({ service: currentService, image: imageMatch[1] });
      continue;
    }

    // `ports:` block — collect until next non-indented key
    if (/^ports:\s*$/.test(trimmed)) {
      inPorts = true;
      ports.push({ service: currentService, ports: [] });
      continue;
    }
    if (inPorts) {
      // Skip IP-prefixed bindings like `127.0.0.1:9119:9119` (services
      // bound to loopback — the IP-prefix means "private interface only"
      // and the container port is the second number). The actual
      // public-port info lives in the blueprint.yaml.
      const ipBound = /^-\s+["']?\d+\.\d+\.\d+\.\d+:/.test(trimmed);
      if (ipBound) {
        continue;
      }
      const portMatch = trimmed.match(
        /^-\s+["']?(\$\{[^}]+\}:)?(\d+)(?::\d+)?["']?/
      );
      if (portMatch && portMatch[2]) {
        ports[ports.length - 1]?.ports.push(portMatch[2]);
      } else if (/^[a-z]/.test(trimmed) && !trimmed.startsWith("-")) {
        inPorts = false;
      }
    }
  }

  // Pick the first descriptive comment line as the purpose lead
  const descriptionComment = descriptionComments
    .filter((c) => c && !c.startsWith("=====") && !c.startsWith("Phase"))
    .slice(0, 3)
    .join(" ")
    .trim() || null;

  return {
    name,
    services,
    images,
    ports,
    descriptionComment,
  };
}

// -----------------------------------------------------------------------------
// Blueprint parsing — extract domain + port for cross-references
// -----------------------------------------------------------------------------

function parseBlueprint(text: string): ParsedBlueprint {
  const isPublic = text.includes("public-resources:");
  const isPrivate = text.includes("private-resources:");
  let domain: string | null = null;
  let destinationPort: number | null = null;
  let protocol: string | null = null;

  const fullDomainMatch = text.match(/full-domain:\s*["']?([^\s"']+)["']?/);
  if (fullDomainMatch && fullDomainMatch[1]) {
    domain = fullDomainMatch[1];
  }
  const portMatch = text.match(/destination-port:\s*(\d+)/);
  if (portMatch && portMatch[1]) {
    destinationPort = parseInt(portMatch[1], 10);
  }
  const protoMatch = text.match(/protocol:\s*["']?([^\s"']+)["']?/);
  if (protoMatch && protoMatch[1]) {
    protocol = protoMatch[1];
  }

  return {
    raw: text,
    isPublic,
    isPrivate,
    domain,
    destinationPort,
    protocol,
  };
}

// -----------------------------------------------------------------------------
// README extraction — first heading + the body of the first section
// (before the next `## ` heading or the 10th non-empty line, whichever comes
// first)
// -----------------------------------------------------------------------------

function extractReadmeLead(readme: string): string | null {
  if (!readme.trim()) return null;
  const lines = readme.split("\n");
  const out: string[] = [];
  let foundTopHeading = false;
  let inBody = false;
  let nonEmpty = 0;
  let lastWasBlank = false;
  for (const line of lines) {
    const trimmed = line.trim();
    if (!foundTopHeading) {
      const headingMatch = trimmed.match(/^#\s+(.+?)$/);
      if (headingMatch && headingMatch[1]) {
        out.push(`# ${headingMatch[1]}`);
        foundTopHeading = true;
      }
      continue;
    }
    if (!inBody) {
      // Skip until first non-blank line AFTER the top heading
      if (!trimmed) continue;
      // Skip the first level-2 heading body (e.g. "## Overview")
      // and start collecting after it
      if (/^##\s+/.test(trimmed)) {
        inBody = true;
        continue;
      }
      // Plain content directly under the top heading
      inBody = true;
    }
    // In body — stop at the next `## ` heading or 10 non-empty lines
    if (/^##\s+/.test(trimmed)) {
      break;
    }
    if (trimmed) {
      out.push(trimmed);
      nonEmpty += 1;
      lastWasBlank = false;
    } else if (!lastWasBlank && out.length > foundTopHeading ? 1 : 0) {
      out.push("");
      lastWasBlank = true;
    }
    if (nonEmpty >= 10) break;
  }
  // Strip trailing blank lines
  while (out.length > 0 && out[out.length - 1] === "") {
    out.pop();
  }
  return out.length > 1 ? out.join("\n") : null;
}

// -----------------------------------------------------------------------------
// Doc rendering — mirrors the 4-section hand-written baseline
// -----------------------------------------------------------------------------

function renderStackDoc(stack: StackResult): string {
  const lines: string[] = [];
  const name = stack.name;
  const compose = stack.compose;
  const blueprint = stack.blueprint;
  const services = compose?.services ?? [];
  const primaryImage = compose?.images[0]?.image ?? "(no image declared)";
  const primaryPort =
    compose?.ports[0]?.ports[0] ?? blueprint?.destinationPort ?? null;
  const domain = blueprint?.domain ?? null;
  const isStaging = stack.isStagingArea;

  lines.push(`# ${name}`);
  lines.push("");
  lines.push(`## Purpose for the Cianfhoghlaim project`);
  lines.push("");

  if (isStaging) {
    lines.push(
      `\`${name}\` is a **staging / multi-stack area** for the Wave 2 personal-utility stacks. It is NOT a single stack itself; the subdirectories of \`bonneagar/stacks/${name}/\` are the real 6-file GOLD_STANDARD stacks (one per sub-service).`
    );
    lines.push("");
    lines.push(
      `Satisfies the \`bun run validate-stacks\` GOLD_STANDARD gate (every subdir of \`bonneagar/stacks/\` must contain at least one \`.yaml\` file). The omnibus deploy procedure is at \`bonneagar/komodo/procedures/deploy-${name}-bunchloch.toml\`.`
    );
    lines.push("");
  } else if (stack.hasReadme) {
    const readme = readFileSync(stack.readmePath, "utf8");
    const lead = extractReadmeLead(readme);
    if (lead) {
      lines.push(lead);
      lines.push("");
    } else {
      lines.push(
        `Runs ${services.length} service(s) at \`bonneagar/stacks/${name}/\`: ${services.join(", ")}.`
      );
      lines.push("");
    }
  } else if (compose?.descriptionComment) {
    lines.push(compose.descriptionComment);
    lines.push("");
  } else {
    const summary =
      services.length > 0
        ? `Runs ${services.join(", ")} as part of the ${name} stack (image: \`${primaryImage}\`).`
        : `${name} stack (image: \`${primaryImage}\`).`;
    lines.push(summary);
    lines.push("");
  }

  lines.push(`## Why it stays in komodo/pangolin/infisical GitOps`);
  lines.push("");
  lines.push(
    `Managed via the 6-file GOLD_STANDARD contract: \`compose.yaml\` + \`sidecar.yaml\` + \`secrets.env\` + \`pangolin.yaml\` + \`blueprint.yaml\` + \`.env.example\`. The Locket sidecar injects Infisical-resolved secrets at container runtime; Pangolin provides private-resource routing; Komodo orchestrates deploy + health checks.`
  );
  lines.push("");
  if (primaryPort && !isStaging) {
    lines.push(
      `Primary port: \`${primaryPort}\`. Backed by Komodo deploy procedure + Pangolin ${blueprint?.isPrivate ? "private" : blueprint?.isPublic ? "public" : ""} resource registration.`
    );
    lines.push("");
  } else if (isStaging) {
    lines.push(
      `The stack omits a single primary port because each sub-stack exposes its own. Consult the per-sub-stack docs once generated.`
    );
    lines.push("");
  }

  lines.push(`## Cross-references`);
  lines.push("");
  lines.push(
    `- **Ops**: \`bonneagar/stacks/${name}/\` (the 6-file GOLD_STANDARD)`
  );
  lines.push(
    `- **Code**: \`cianfhoghlaim/<code-path>\` (if any — see the linked Dagster assets / BAML schemas / DLT sources)`
  );
  lines.push(
    `- **IaC**: registered in \`bonneagar/iac/komodo/deploy-stacks.ts\` with tags \`host:<host>\` + \`tier:<tier>\``
  );
  if (domain && !isStaging) {
    lines.push(
      `- **Pangolin**: \`${domain}\` (${blueprint?.isPrivate ? "private" : blueprint?.isPublic ? "public" : ""} resource, port ${primaryPort ?? "?"})`
    );
  } else if (!isStaging) {
    lines.push(
      `- **Pangolin**: no public domain (internal/storage sidecar — see stack-doctor)`
    );
  }
  lines.push("");

  lines.push(`## Tags`);
  lines.push("");
  lines.push(
    `- \`host:<bunchloch | arm1-oci | ca-x41>\` (per \`deploy-stacks.ts\` registration)`
  );
  lines.push(
    `- \`tier:<foundation | data-engineering | agent-platform | language-model | user-facing-web | personal-utility>\``
  );
  lines.push(`- \`project:cianfhoghlaim\` (if cianfhoghlaim-relevant)`);
  lines.push("");
  lines.push(`---`);
  lines.push(
    `_Generated by \`scripts/generate-stack-docs.ts\` at ${new Date().toISOString()}_`
  );
  lines.push("");

  return lines.join("\n");
}

// -----------------------------------------------------------------------------
// Main
// -----------------------------------------------------------------------------

function main() {
  const stacks = discoverStacks();
  if (stacks.length === 0) {
    console.log(
      `No stacks discovered${STACK_FILTER ? ` (filter: ${STACK_FILTER})` : ""}.`
    );
    return;
  }

  const missing = stacks.filter((s) => !s.docExists);
  if (missing.length === 0) {
    console.log(
      `✓ All ${stacks.length} discovered stack(s) already have docs.`
    );
    return;
  }

  console.log(
    `${APPLY ? "Writing" : "Would write"} docs for ${missing.length} stack(s)${STACK_FILTER ? ` (filter: ${STACK_FILTER})` : ""}:`
  );
  console.log();

  let written = 0;
  for (const stack of missing) {
    if (!APPLY) {
      const port = stack.compose?.ports[0]?.ports[0] ?? "?";
      const img = stack.compose?.images[0]?.image ?? "?";
      console.log(
        `  - ${stack.name.padEnd(20)} (port=${port}, image=${img})`
      );
      continue;
    }
    const content = renderStackDoc(stack);
    writeFileSync(stack.docPath, content);
    written += 1;
    console.log(`  ✓ ${stack.name}.md`);
  }

  console.log();
  if (APPLY) {
    console.log(`✓ Wrote ${written} docs/stacks/*.md file(s).`);
  } else {
    console.log(
      `(dry-run) Re-run with --apply to write the ${missing.length} docs file(s).`
    );
  }
}

main();
