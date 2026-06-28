#!/usr/bin/env bun
// regenerate-glance-config.ts — Glance config auto-generator.
//
// Reads the webstack snapshot (produced by analyze-web-stack.ts) and emits
// a Glance config with one page per project (tuatha, oideachais, croilar,
// meaisinfhoghlaim) + the existing Home page.
//
// SAFETY: refuses to clobber a manually-edited glance.yml unless the env var
// CROILAR_GLANCE_REGEN_FORCE=true is set.
//
// Usage:
//   bun run regenerate-glance-config.ts
//   bun run regenerate-glance-config.ts --out /tmp/glance.yml
//   CROILAR_GLANCE_REGEN_FORCE=true bun run regenerate-glance-config.ts

import { readFile, writeFile, stat } from "node:fs/promises";
import { existsSync } from "node:fs";
import { resolve } from "node:path";

const REPO_ROOT = process.env.CROILAR_REPO_ROOT ?? resolve(import.meta.dir, "../..");
const SNAPSHOT_PATH = resolve(REPO_ROOT, "croilar/.cache/webstack-snapshot.json");
const GLANCE_PATH = resolve(
  REPO_ROOT,
  "infrastructure/stacks/glance/config/glance.yml",
);

const FORCE = process.env.CROILAR_GLANCE_REGEN_FORCE === "true";

interface Route { project: string; route: string; file: string; }
interface ConvexFunction { project: string; name: string; kind: string; file: string; }
interface CloudflareResource { project: string; kind: string; name: string; }
interface BamlSchema { project: string; file: string; classCount: number; functionCount: number; enumCount: number; }
interface MarimoNotebook { project: string; slug: string; file: string; cellCount: number; }
interface Snapshot {
  generatedAt: number;
  tanstackRoutes: Route[];
  convexFunctions: ConvexFunction[];
  cloudflareResources: CloudflareResource[];
  bamlSchemas: BamlSchema[];
  marimoNotebooks: MarimoNotebook[];
}

const PROJECTS = ["tuatha", "oideachais", "croilar", "meaisinfhoghlaim"] as const;
type Project = (typeof PROJECTS)[number];

const PORTAL_BASE_URL =
  process.env.CROILAR_PORTAL_BASE_URL ?? "https://portal.cianfhoghlaim.ie";

const RSS_BY_PROJECT: Record<Project, { title: string; url: string }[]> = {
  tuatha: [
    { title: "HuggingFace Releases", url: "https://huggingface.co/blog/feed.xml" },
  ],
  oideachais: [
    { title: "RisingWave Blog", url: "https://risingwave.com/blog/rss.xml" },
  ],
  croilar: [
    { title: "Dagster Blog", url: "https://dagster.io/blog/rss.xml" },
  ],
  meaisinfhoghlaim: [
    { title: "Langfuse Blog", url: "https://langfuse.com/blog/rss.xml" },
  ],
};

const MONITOR_ENDPOINTS: Record<Project, { title: string; url: string }[]> = {
  tuatha: [
    { title: "Dagster (tuath)", url: "http://dagster:3000/health" },
    { title: "Dagster (crypteolas)", url: "http://dagster:3000/health" },
  ],
  oideachais: [
    { title: "Oideachais API", url: "http://oideachais-web:3000/health" },
    { title: "LanceDB", url: "http://lancedb:8080/health" },
  ],
  croilar: [
    { title: "Cianfhoghlaim Portal", url: "http://portal:3000/api/health" },
    { title: "Komodo", url: "http://komodo-core:9120/health" },
  ],
  meaisinfhoghlaim: [
    { title: "MLflow", url: "http://mlflow:5000/health" },
    { title: "Cognee", url: "http://cognee:8000/health" },
  ],
};

function projectRoutes(s: Snapshot, p: Project): Route[] {
  return s.tanstackRoutes.filter((r) => r.project === p);
}
function projectFunctions(s: Snapshot, p: Project): ConvexFunction[] {
  return s.convexFunctions.filter((f) => f.project === p);
}
function projectBaml(s: Snapshot, p: Project): BamlSchema[] {
  return s.bamlSchemas.filter((b) => b.project === p);
}
function projectCf(s: Snapshot, p: Project): CloudflareResource[] {
  return s.cloudflareResources.filter((c) => c.project === p);
}
function projectNotebooks(s: Snapshot, p: Project): MarimoNotebook[] {
  return s.marimoNotebooks.filter((n) => n.project === p);
}

function renderProjectPage(p: Project, s: Snapshot): string {
  const routes = projectRoutes(s, p);
  const fns = projectFunctions(s, p);
  const baml = projectBaml(s, p);
  const cf = projectCf(s, p);
  const nb = projectNotebooks(s, p);
  const rss = RSS_BY_PROJECT[p] ?? [];
  const monitors = MONITOR_ENDPOINTS[p] ?? [];

  const routeList = routes
    .slice(0, 25)
    .map((r) => `              - text: "${r.route} — ${r.file}"`)
    .join("\n");
  const fnList = fns
    .slice(0, 25)
    .map((f) => `              - text: "${f.kind} ${f.name} — ${f.file}"`)
    .join("\n");
  const bamlList = baml
    .slice(0, 10)
    .map((b) => `              - text: "${b.file} (${b.classCount}c ${b.functionCount}f ${b.enumCount}e)"`)
    .join("\n");
  const cfList = cf
    .map((c) => `              - text: "${c.kind}: ${c.name}"`)
    .join("\n");
  const nbList = nb
    .map((n) => `              - text: "${n.slug} (${n.cellCount} cells)"`)
    .join("\n");

  const monitorWidget = monitors.length > 0
    ? `          - type: monitor
            title: "${p} services"
            cache: 1m
            sites:
${monitors.map((m) => `              - title: "${m.title}"
                url: ${m.url}`).join("\n")}`
    : "";

  const rssWidget = rss.length > 0
    ? `          - type: rss
            title: "${p} feeds"
            feeds:
${rss.map((r) => `              - url: ${r.url}
                limit: 5`).join("\n")}
            style: vertical-list`
    : "";

  return `  - name: "${p}"
    columns:
      - size: small
        widgets:
          - type: search
            autofocus: true
            search-engine: https://search.cianfhoghlaim.ie/search?q={QUERY}
          - type: custom-api
            title: "Open in Portal"
            url: ${PORTAL_BASE_URL}/web/${p}
            cache: 5m
            body: |
              <div style="padding:0.5rem 0">
                <a href="${PORTAL_BASE_URL}/web/${p}" target="_blank" rel="noopener">View ${p} in the croilar devtools hub &rarr;</a>
              </div>
${monitorWidget ? `      - size: full
        widgets:
${monitorWidget}` : ""}
${rssWidget ? `      - size: full
        widgets:
${rssWidget}` : ""}
      - size: full
        widgets:
          - type: group
            widgets:
${routeList ? `              - type: list
                title: "TanStack routes (${routes.length})"
                items:
${routeList}` : ""}
${fnList ? `              - type: list
                title: "Convex functions (${fns.length})"
                items:
${fnList}` : ""}
${bamlList ? `              - type: list
                title: "BAML schemas (${baml.length})"
                items:
${bamlList}` : ""}
${cfList ? `              - type: list
                title: "Cloudflare (${cf.length})"
                items:
${cfList}` : ""}
${nbList ? `              - type: list
                title: "Marimo notebooks (${nb.length})"
                items:
${nbList}` : ""}
`;
}

function buildYaml(s: Snapshot): string {
  const pages = PROJECTS.map((p) => renderProjectPage(p, s)).join("\n");
  const widgetCount = s.tanstackRoutes.length
    + s.convexFunctions.length
    + s.bamlSchemas.length
    + s.cloudflareResources.length
    + s.marimoNotebooks.length
    + 5;
  return `# Generated by croilar/scripts/regenerate-glance-config.ts
# Generated at: ${new Date(s.generatedAt).toISOString()}
# DO NOT EDIT — run the regenerator instead.
# (Set CROILAR_GLANCE_REGEN_FORCE=true to override the safety check.)

server:
  host: 0.0.0.0
  port: 8080
  base-url: ""

theme:
  background-color: "#0a0a0a"
  primary-color: "#6c5ce7"
  text-color: "#e0e0e0"

pages:
${pages}
# ${widgetCount} widgets total across ${PROJECTS.length} project pages.
`;
}

async function main() {
  const args = process.argv.slice(2);
  let outFile: string | null = null;
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === "--out") outFile = args[++i] ?? null;
  }

  if (!existsSync(SNAPSHOT_PATH)) {
    throw new Error(
      `Snapshot not found at ${SNAPSHOT_PATH}. Run 'bun run croilar/scripts/analyze-web-stack.ts' first.`,
    );
  }

  const targetPath = outFile ?? GLANCE_PATH;

  if (existsSync(targetPath)) {
    const text = await readFile(targetPath, "utf-8");
    if (!text.startsWith("# Generated by") && !FORCE) {
      throw new Error(
        `${targetPath} appears to be manually edited. Set CROILAR_GLANCE_REGEN_FORCE=true to clobber.`,
      );
    }
  }

  const payload = await buildPayload();
  const yaml = buildYaml(payload.snapshot);
  await writeFile(targetPath, yaml, "utf-8");
  const st = await stat(targetPath);
  console.error(
    `wrote ${st.size} bytes to ${targetPath} (${payload.snapshot.tanstackRoutes.length} routes, ${payload.snapshot.convexFunctions.length} functions, ${payload.snapshot.bamlSchemas.length} baml, ${payload.snapshot.cloudflareResources.length} cf, ${payload.snapshot.marimoNotebooks.length} notebooks)`,
  );
  process.stdout.write(
    JSON.stringify({
      yaml,
      pageCount: PROJECTS.length,
      widgetCount: payload.widgetCount,
    }),
  );
}

interface BuildPayload {
  snapshot: Snapshot;
  widgetCount: number;
}

async function buildPayload(): Promise<BuildPayload> {
  const text = await readFile(SNAPSHOT_PATH, "utf-8");
  const snapshot = JSON.parse(text) as Snapshot;
  const widgetCount = snapshot.tanstackRoutes.length
    + snapshot.convexFunctions.length
    + snapshot.bamlSchemas.length
    + snapshot.cloudflareResources.length
    + snapshot.marimoNotebooks.length
    + 5;
  return { snapshot, widgetCount };
}

main().catch((e) => {
  console.error(e instanceof Error ? e.message : String(e));
  process.exit(1);
});
