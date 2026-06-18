// croilar/mcp/devtools/index.ts
//
// croilar-mcp-devtools — exposes the web stack snapshot (produced by
// `croilar/scripts/analyze-web-stack.ts`) to Claude and other MCP clients.
//
// Tools:
//   - list_tanstack_routes   — list all routes, filter by project
//   - list_convex_functions  — list all Convex functions, filter by project
//   - list_cloudflare        — list all Cloudflare resources, filter by project
//   - list_baml              — list BAML schemas, filter by project
//   - list_marimo            — list Marimo notebooks, filter by project
//   - get_project_summary    — composite per-project rollup
//   - get_snapshot           — full raw snapshot
//
// Env:
//   CROILAR_REPO_ROOT — repo root (defaults to the parent of this script's grandparent)
//
// Transport: stdio (per the MCP spec).

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { resolve } from "node:path";
import { readFile } from "node:fs/promises";
import { existsSync } from "node:fs";

const REPO_ROOT = process.env.CROILAR_REPO_ROOT ?? resolve(import.meta.dir, "../..", "..");
const SNAPSHOT_PATH = resolve(REPO_ROOT, "croilar/.cache/webstack-snapshot.json");
const ANALYZER = resolve(REPO_ROOT, "croilar/scripts/analyze-web-stack.ts");

const PROJECTS = ["tuatha", "oideachais", "croilar", "meaisinfhoghlaim"] as const;
type Project = (typeof PROJECTS)[number];

interface Snapshot {
  generatedAt: number;
  schemaVersion?: number;
  tanstackRoutes: any[];
  convexFunctions: any[];
  cloudflareResources: any[];
  bamlSchemas: any[];
  marimoNotebooks: any[];
}

async function loadSnapshot(): Promise<Snapshot> {
  if (!existsSync(SNAPSHOT_PATH)) {
    await regenerate();
  }
  return JSON.parse(await readFile(SNAPSHOT_PATH, "utf-8")) as Snapshot;
}

async function regenerate(): Promise<void> {
  const proc = Bun.spawn(["bun", "run", ANALYZER, "--out", SNAPSHOT_PATH], {
    cwd: REPO_ROOT,
    stdout: "pipe",
    stderr: "pipe",
  });
  await proc.exited;
}

function byProject<T extends { project: string }>(rows: T[], project?: string): T[] {
  if (!project) return rows;
  return rows.filter((r) => r.project === project);
}

const server = new Server(
  {
    name: "croilar-mcp-devtools",
    version: "0.1.0",
  },
  {
    capabilities: { tools: {} },
  },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "list_tanstack_routes",
      description: "List all TanStack routes discovered by the analyzer. Filter by project.",
      inputSchema: {
        type: "object",
        properties: {
          project: { type: "string", enum: [...PROJECTS] },
        },
      },
    },
    {
      name: "list_convex_functions",
      description: "List all Convex functions discovered by the analyzer.",
      inputSchema: {
        type: "object",
        properties: {
          project: { type: "string", enum: [...PROJECTS] },
        },
      },
    },
    {
      name: "list_cloudflare",
      description: "List all Cloudflare resources (workers, pages, R2, KV, D1) discovered from wrangler configs.",
      inputSchema: {
        type: "object",
        properties: {
          project: { type: "string", enum: [...PROJECTS] },
        },
      },
    },
    {
      name: "list_baml",
      description: "List all BAML schemas discovered by the analyzer.",
      inputSchema: {
        type: "object",
        properties: {
          project: { type: "string", enum: [...PROJECTS] },
        },
      },
    },
    {
      name: "list_marimo",
      description: "List all Marimo notebooks discovered by the analyzer.",
      inputSchema: {
        type: "object",
        properties: {
          project: { type: "string", enum: [...PROJECTS] },
        },
      },
    },
    {
      name: "get_project_summary",
      description: "Per-project rollup: counts of routes, functions, BAML schemas, Cloudflare, and notebooks.",
      inputSchema: {
        type: "object",
        properties: {
          project: { type: "string", enum: [...PROJECTS] },
        },
        required: ["project"],
      },
    },
    {
      name: "get_snapshot",
      description: "Return the full web stack snapshot as JSON.",
      inputSchema: { type: "object", properties: {} },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  const a = (args ?? {}) as { project?: string };
  const snap = await loadSnapshot();
  switch (name) {
    case "list_tanstack_routes":
      return { content: [{ type: "text", text: JSON.stringify(byProject(snap.tanstackRoutes, a.project), null, 2) }] };
    case "list_convex_functions":
      return { content: [{ type: "text", text: JSON.stringify(byProject(snap.convexFunctions, a.project), null, 2) }] };
    case "list_cloudflare":
      return { content: [{ type: "text", text: JSON.stringify(byProject(snap.cloudflareResources, a.project), null, 2) }] };
    case "list_baml":
      return { content: [{ type: "text", text: JSON.stringify(byProject(snap.bamlSchemas, a.project), null, 2) }] };
    case "list_marimo":
      return { content: [{ type: "text", text: JSON.stringify(byProject(snap.marimoNotebooks, a.project), null, 2) }] };
    case "get_project_summary": {
      if (!a.project) {
        return { isError: true, content: [{ type: "text", text: "project is required" }] };
      }
      const p = a.project;
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                project: p,
                routes: snap.tanstackRoutes.filter((r) => r.project === p).length,
                functions: snap.convexFunctions.filter((f) => f.project === p).length,
                bamlSchemas: snap.bamlSchemas.filter((b) => b.project === p).length,
                cloudflare: snap.cloudflareResources.filter((c) => c.project === p).length,
                notebooks: snap.marimoNotebooks.filter((n) => n.project === p).length,
                generatedAt: snap.generatedAt,
              },
              null,
              2,
            ),
          },
        ],
      };
    }
    case "get_snapshot":
      return { content: [{ type: "text", text: JSON.stringify(snap, null, 2) }] };
    default:
      return { isError: true, content: [{ type: "text", text: `unknown tool: ${name}` }] };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("croilar-mcp-devtools ready on stdio");
}

main().catch((e) => {
  console.error("croilar-mcp-devtools failed to start:", e);
  process.exit(1);
});
