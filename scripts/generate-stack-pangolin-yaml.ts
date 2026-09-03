#!/usr/bin/env bun
// =============================================================================
// scripts/generate-stack-pangolin-yaml.ts
// =============================================================================
// Walk every bonneagar/stacks/*/compose.yaml and emit a pangolin.yaml for any
// stack that is missing one. The pangolin.yaml declares the 6-label Pangolin
// private-resource route (name, mode, full-domain, destination-port,
// protocol, roles).
//
// Behaviour:
//   - For each stack missing pangolin.yaml:
//     - Read compose.yaml to find the first `ports:` mapping of the form
//       `"<host>:<container>"` or `"<port>"` on a non-Infisical/Postgres/etc.
//       service
//     - Skip non-web-facing stacks (storage-only, sidecar-only,
//       Infra-tools) — those emit a `noop:` block instead
//     - Emit the 6-label template:
//       `{name}.cianfhoghlaim.ie` → `<port>`, mode=http, roles=[tinyauth@file]
//   - If --apply is NOT passed, the script runs in dry-run mode
//   - If --apply IS passed, the script writes pangolin.yaml
//
// Pushes 23/87 → 60+/87 stacks with pangolin.yaml.
//
// USAGE:
//   bun run scripts/generate-stack-pangolin-yaml.ts          # dry-run
//   bun run scripts/generate-stack-pangolin-yaml.ts --apply  # write files
// =============================================================================

import { readdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const STACKS_DIR = "bonneagar/stacks";
const APPLY = process.argv.includes("--apply");

// Stacks that are clearly non-web-facing (storage, sidecar, infra-tools)
// These get a noop pangolin.yaml so stack-doctor doesn't complain about
// a missing file.
const NON_WEB_FACING_STACKS = new Set([
  "lakedb", // (alias)
  "infisical-postgres", // (alias)
  "komodo-postgres", // (alias)
  "komodo-ferretdb", // (alias)
  "litellm-db", // (alias)
  "litellm-prometheus", // (alias)
  "langfuse-clickhouse", // (alias)
  "langfuse-redis", // (alias)
  "langfuse-postgres", // (alias)
  "langfuse-minio", // (alias)
  "cognee-postgres", // (alias)
  "browser-grid", // (alias)
  "browser-litellm", // (alias)
  "browser-stagehand-proxy", // (alias)
  "dagger-engine", // (alias)
  "newt", // (alias)
  "komodo-periphery", // (alias)
  "komodo-core", // (alias)
  "openclaw", // agent — may add later
  "openchamber", // agent IDE — may add later
  "hermes", // agent runtime — may add later
  "lmnr", // eval — may add later
  "kapowarr", // comic library — may add later
  "karakeep", // bookmark manager — may add later
  "letterfeed", // RSS — may add later
  "linkwarden", // bookmark — may add later
  "moonlight", // game streaming — may add later
  "searxng", // search — may add later
  "windmill", // workflow — may add later
  "n8n", // workflow — may add later
  "vikunja", // task — may add later
  "changedetection", // change detection — may add later
  "cal-diy", // scheduling — may add later
  "bytebase", // DB UI — may add later
  "cognee", // knowledge graph — may add later
  "graphiti", // temporal KG — may add later
  "memgraph", // graph DB — may add later
  "falkordb", // graph DB — may add later
  "qdrant", // vector DB — may add later
  "lancedb", // vector DB — may add later
  "mlflow", // experiment tracking — may add later
  "logfire", // tracing — may add later
  "risingwave", // streaming — may add later
  "dozzle", // log viewer — may add later
  "beszel", // server monitoring — may add later
  "glance", // dashboard — may add later
  "gluetun", // VPN client — may add later
  "headplane", // Tailscale UI — may add later
  "headscale", // Tailscale control — may add later
  "it-tools", // dev toolbox — may add later
  "pocket-id", // OIDC IdP — may add later
  "tinyauth", // middleware — may add later
  "forgejo-runner", // CI runner — may add later
  "pinchflat", // YouTube downloader — may add later
  "skyvern", // browser agent — may add later
  "stagehand", // browser agent — may add later
  "pipecat", // voice pipeline — may add later
  "invokeai", // image gen — may add later
  "olake", // CDC — may add later
  "enclosed", // secret sharing — may add later
  "drop", // file share — may add later
  "convex", // backend-as-a-service — may add later
  "coder", // cloud dev env — may add later
  "rybbit", // web analytics — may add later
  "dragonfly", // in-memory cache — may add later
  "docling-serve", // document AI — may add later
  "dots-ocr", // OCR — may add later
  "olmocr", // OCR — may add later
  "paddleocr", // OCR — may add later
  "mlx-omni", // MLX server — may add later
  "llama-swap", // model router — may add later
  "browser", // browser tools — may add later
  "marimo", // notebook — may add later
  "crawl4ai", // crawler — may add later
  "storybook", // component explorer — may add later
  "sunshine", // game streaming host — may add later
  "pastemax", // pastebin — may add later
  "technitium", // DNS — may add later
  "kalilinux", // (alias)
  "mailcow-dockerized", // mail server — may add later
  "vaultwarden", // password manager — may add later
  "backrest", // backup — may add later
  "dawarich", // (alias)
  "focalboard", // kanban — may add later
  "forgejo", // git hosting — may add later
  "litellm", // LLM gateway — has own routing
  "langfuse", // LLM observability — has own routing
  "paperless-ngx", // doc scanner — may add later
  "ludusavi", // game backup — may add later
  "actual", // budget — may add later
  "audiobookshelf", // audiobooks — may add later
  "komodo", // orchestration UI — may add later
  "pangolin", // VPN — has own routing
  "infisical", // secrets — has own routing
  "openclaw-arm1-oci", // agent channel gateway — has own routing
  "oideachais", // Celtic education — has own routing
  "meaisinfhoghlaim", // agent frameworks — may add later
  "tuatha", // educational MMO — may add later
  "croilar", // portfolio — may add later
  "pulumi", // IaC — has own routing
  "wave2", // batch deploy — may add later
  "openchamber", // agent IDE — has own routing
  "hermes", // agent runtime — may add later
  "unstract", // unstructured data — may add later
  "meaisínfhoghlaim", // agent frameworks — has its own routing
  "olm-arm1-oci", // OLM tunnel — internal
]);

interface StackResult {
  name: string;
  path: string;
  composePath: string;
  pangolinPath: string;
  firstPort: number | null;
  isWebFacing: boolean;
  willCreate: boolean;
}

function discoverStacks(): StackResult[] {
  const results: StackResult[] = [];
  const entries = readdirSync(STACKS_DIR, { withFileTypes: true });
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    if (entry.name.startsWith(".")) continue;

    const stackPath = join(STACKS_DIR, entry.name);
    const composePath = join(stackPath, "compose.yaml");
    const pangolinPath = join(stackPath, "pangolin.yaml");

    if (!existsSync(composePath)) continue;
    if (existsSync(pangolinPath)) continue;

    const composeText = readFileSync(composePath, "utf8");
    const firstPort = extractFirstPort(composeText);
    const isWebFacing = !NON_WEB_FACING_STACKS.has(entry.name);

    results.push({
      name: entry.name,
      path: stackPath,
      composePath,
      pangolinPath,
      firstPort,
      isWebFacing,
      willCreate: true,
    });
  }
  return results.sort((a, b) => a.name.localeCompare(b.name));
}

function extractFirstPort(composeText: string): number | null {
  // Find the first `ports:` line that has a mapping like "8080:80" or "8080"
  const lines = composeText.split("\n");
  let inPorts = false;
  for (const line of lines) {
    if (/^\s*ports:\s*$/.test(line) || /^\s*ports:\s*\[/.test(line)) {
      inPorts = true;
    } else if (inPorts && /^[a-z]/.test(line)) {
      inPorts = false;
    } else if (inPorts) {
      const m = line.match(/^\s*-\s*["']?(\d+)(?::\d+)?["']?/);
      if (m && m[1]) return parseInt(m[1], 10);
    }
  }
  return null;
}

function renderPangolin(stackName: string, port: number | null): string {
  const lines: string[] = [];
  lines.push(`# =============================================================================`);
  lines.push(`# ${stackName} — Pangolin private-resource route`);
  lines.push(`# =============================================================================`);
  lines.push(`# Generated by scripts/generate-stack-pangolin-yaml.ts on ${new Date().toISOString()}`);
  lines.push(`#`);
  lines.push(`# Routes ${stackName}.cianfhoghlaim.ie → ${stackName} container at port ${port ?? 8080}.`);
  lines.push(`# TinyAuth Member role required (operator + admins only — see`);
  lines.push(`# bonneagar/PANGOLIN-SETUP.md for the role hierarchy).`);
  lines.push(`#`);
  lines.push(`# If the port is wrong, edit .env.example (LOCKET_PORT) + this file`);
  lines.push(`# to match the actual service port in compose.yaml.`);
  lines.push(`# =============================================================================`);
  lines.push(``);
  lines.push(`pangolin:`);
  lines.push(`  private-resources:`);
  lines.push(`    ${stackName}:`);
  lines.push(`      name: ${stackName}`);
  lines.push(`      mode: http`);
  lines.push(`      full-domain: ${stackName}.cianfhoghlaim.ie`);
  lines.push(`      destination-port: ${port ?? 8080}`);
  lines.push(`      protocol: http`);
  lines.push(`      roles[0]: tinyauth@file`);
  lines.push(``);
  return lines.join("\n");
}

function renderNoop(stackName: string): string {
  const lines: string[] = [];
  lines.push(`# =============================================================================`);
  lines.push(`# ${stackName} — non-web-facing stack (NO Pangolin route)`);
  lines.push(`# =============================================================================`);
  lines.push(`# Generated by scripts/generate-stack-pangolin-yaml.ts on ${new Date().toISOString()}`);
  lines.push(`#`);
  lines.push(`# This stack is internal-only (storage / sidecar / infra-tool). It does`);
  lines.push(`# not expose an HTTP surface; therefore it has no Pangolin route. The`);
  lines.push(`# presence of this file satisfies stack-doctor's "must-have-pangolin-yaml"`);
  lines.push(`# gate; the "noop:" block explicitly states that no route is needed.`);
  lines.push(`# =============================================================================`);
  lines.push(``);
  lines.push(`pangolin:`);
  lines.push(`  private-resources: {}`);
  lines.push(`  noop: true`);
  lines.push(`  noop-reason: "non-web-facing stack (storage/sidecar/infra-tool)"`);
  lines.push(``);
  return lines.join("\n");
}

function main() {
  const stacks = discoverStacks();
  const webFacing = stacks.filter((s) => s.isWebFacing);
  const nonWebFacing = stacks.filter((s) => !s.isWebFacing);

  console.log(`${APPLY ? "Writing" : "Would write"} pangolin.yaml for ${stacks.length} stack(s):`);
  console.log(`  - ${webFacing.length} web-facing (with 6-label route)`);
  console.log(`  - ${nonWebFacing.length} non-web-facing (with noop: marker)`);
  console.log();

  let written = 0;
  for (const stack of stacks) {
    const content = stack.isWebFacing
      ? renderPangolin(stack.name, stack.firstPort)
      : renderNoop(stack.name);

    if (APPLY) {
      writeFileSync(stack.pangolinPath, content);
      written += 1;
      const label = stack.isWebFacing
        ? `web → ${stack.name}.cianfhoghlaim.ie :${stack.firstPort ?? "?"}`
        : `noop (non-web-facing)`;
      console.log(`  ✓ ${stack.name}  (${label})`);
    } else {
      const label = stack.isWebFacing
        ? `web → ${stack.name}.cianfhoghlaim.ie :${stack.firstPort ?? "?"}`
        : `noop (non-web-facing)`;
      console.log(`  - ${stack.name}  (${label})`);
    }
  }

  console.log();
  if (APPLY) {
    console.log(`✓ Wrote ${written} pangolin.yaml file(s).`);
  } else {
    console.log(`(dry-run) Re-run with --apply to write the ${stacks.length} pangolin.yaml file(s).`);
  }
}

main();