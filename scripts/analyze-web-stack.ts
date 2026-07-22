#!/usr/bin/env bun
// analyze-web-stack.ts — Monorepo walker for the croilar-devtools-hub.
//
// Walks every project in the monorepo, extracts:
//   - tanstack routes
//   - convex functions
//   - cloudflare resources (wrangler.toml)
//   - baml schemas (baml_src/*.baml)
//   - marimo notebooks (notebooks/*.py)
//
// Writes aggregate JSON to stdout (or a file with --out).
// Designed to be called from a Convex action via HTTP or run locally.
//
// Usage:
//   bun run analyze-web-stack.ts                          # all projects
//   bun run analyze-web-stack.ts --project tuatha         # one project
//   bun run analyze-web-stack.ts --kind tanstack_routes   # one kind
//   bun run analyze-web-stack.ts --kind all --out /tmp/x.json
//
// Env:
//   CROILAR_REPO_ROOT  — repo root (default: derived from this script's location)

import { readdir, readFile, stat } from "node:fs/promises";
import { join, relative, resolve } from "node:path";
import { spawnSync } from "node:child_process";

interface AnalyzerOptions {
  repoRoot: string;
  project?: string;
  kind: AnalyzerKind | "all";
  out?: string;
}

type AnalyzerKind =
  | "tanstack_routes"
  | "convex_functions"
  | "cloudflare"
  | "baml"
  | "marimo";

const ALL_PROJECTS = ["tuatha", "oideachais", "croilar", "meaisinfhoghlaim"] as const;
type Project = (typeof ALL_PROJECTS)[number];

const ROOTS: Record<Project, string[]> = {
  tuatha: ["tuatha/ui/src/routes"],
  oideachais: [
    "oideachais/apps/web/src/routes",
    "oideachais/dashboard/src/routes",
  ],
  croilar: [
    "croilar/apps/web/src/routes",
    "croilar/apps/portal/src/routes",
  ],
  meaisinfhoghlaim: ["meaisinfhoghlaim/.../src/routes"],
};

const CONVEX_ROOTS: Record<Project, string[]> = {
  tuatha: ["tuatha/crypteolas/convex", "infrastructure/browser/sruth_browser/frontend/convex"],
  oideachais: ["oideachais/dashboard/convex", "oideachais/web/convex"],
  croilar: ["croilar/convex"],
  meaisinfhoghlaim: ["meaisinfhoghlaim/convex"],
};

const WRANGLER_CONFIGS: Record<Project, string[]> = {
  tuatha: ["tuatha/crypteolas/wrangler.toml"],
  oideachais: ["oideachais/web/wrangler.toml"],
  croilar: ["croilar/wrangler.toml", "croilar/apps/web/wrangler.toml"],
  meaisinfhoghlaim: [],
};

const BAML_ROOTS: Record<Project, string[]> = {
  tuatha: ["tuatha/crypteolas/baml_src"],
  oideachais: ["oideachais/baml_src"],
  croilar: [
    "croilar/baml_src",
    "croilar/pipelines/spotify/baml_src",
    "croilar/pipelines/linkedin/baml_src",
    "croilar/pipelines/researchgate/baml_src",
  ],
  meaisinfhoghlaim: ["meaisinfhoghlaim/baml_src"],
};

const NOTEBOOK_ROOTS: Record<Project, string[]> = {
  tuatha: ["tuatha/crypteolas/marimo"],
  oideachais: ["oideachais/marimo", "oideachais/notebooks"],
  croilar: ["croilar/notebooks"],
  meaisinfhoghlaim: ["meaisinfhoghlaim/notebooks"],
};

function parseArgs(argv: string[]): AnalyzerOptions {
  const envRoot = process.env.CROILAR_REPO_ROOT;
  const scriptDir = import.meta.dir;
  const defaultRoot = resolve(scriptDir, "../..");
  const opts: AnalyzerOptions = {
    repoRoot: envRoot && envRoot.length > 0 ? envRoot : defaultRoot,
    kind: "all",
  };
  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (a === "--project") {
      const v = argv[++i];
      if (!v) throw new Error("--project requires a value");
      opts.project = v;
    } else if (a === "--kind") {
      const v = argv[++i];
      if (!v) throw new Error("--kind requires a value");
      opts.kind = v as AnalyzerKind | "all";
    } else if (a === "--out") {
      const v = argv[++i];
      if (!v) throw new Error("--out requires a value");
      opts.out = v;
    } else if (a === "--repo-root") {
      const v = argv[++i];
      if (!v) throw new Error("--repo-root requires a value");
      opts.repoRoot = v;
    } else {
      throw new Error(`unknown arg: ${a}`);
    }
  }
  return opts;
}

async function pathExists(p: string): Promise<boolean> {
  try {
    await stat(p);
    return true;
  } catch {
    return false;
  }
}

async function listFiles(
  root: string,
  match: (path: string) => boolean,
): Promise<string[]> {
  const out: string[] = [];
  async function walk(dir: string) {
    let entries;
    try {
      entries = await readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      const p = join(dir, entry.name);
      if (entry.isDirectory()) {
        if (entry.name === "node_modules" || entry.name === ".git" || entry.name === "dist" || entry.name === "build") continue;
        await walk(p);
      } else if (entry.isFile()) {
        if (match(p)) out.push(p);
      }
    }
  }
  await walk(root);
  return out;
}

function lastCommitFor(file: string, repoRoot: string): { sha: string; at: number } {
  const r = spawnSync(
    "git",
    ["log", "-1", "--format=%H|%ct", "--", file],
    { cwd: repoRoot, encoding: "utf-8" },
  );
  if (r.status !== 0 || !r.stdout.trim()) return { sha: "", at: 0 };
  const [sha, ts] = r.stdout.trim().split("|");
  return { sha: sha ?? "", at: ts ? Number(ts) * 1000 : 0 };
}

// ── tanstack routes ────────────────────────────────────────────────────
interface TanstackRoute {
  project: string;
  route: string;
  file: string;
  isPublic: boolean;
  isServer: boolean;
  hasLoader: boolean;
  hasAuth: boolean;
  lines: number;
  lastCommit: string;
  lastCommitAt: number;
}

async function analyzeTanstackRoutes(
  project: Project,
  repoRoot: string,
): Promise<TanstackRoute[]> {
  const out: TanstackRoute[] = [];
  for (const root of ROOTS[project]) {
    const abs = resolve(repoRoot, root);
    if (!(await pathExists(abs))) continue;
    const files = await listFiles(abs, (p) => p.endsWith(".tsx") || p.endsWith(".ts"));
    for (const f of files) {
      if (f.endsWith("routeTree.gen.ts")) continue;
      if (f.includes("/__root")) continue;
      if (f.includes("/_layout/") && !f.includes("/_layout/index")) continue;
      const text = await readFile(f, "utf-8");
      const lines = text.split("\n").length;
      const hasLoader = /export\s+const\s+loader\s*=/.test(text) || /loader\s*\(/.test(text);
      const hasAuth = /\brequireAuth\b|requireOrgRole|@convex-dev\/auth|getIdentity\(/.test(text);
      const isServer = /server\s*:\s*\{|createServerFileRoute|server\s*\./.test(text);
      const isPublic = !hasAuth;
      const route = routeFromFile(f, abs);
      const { sha, at } = lastCommitFor(relative(repoRoot, f), repoRoot);
      out.push({
        project,
        route,
        file: relative(repoRoot, f),
        isPublic,
        isServer,
        hasLoader,
        hasAuth,
        lines,
        lastCommit: sha,
        lastCommitAt: at,
      });
    }
  }
  return out;
}

function routeFromFile(file: string, root: string): string {
  const rel = relative(root, file).replace(/\\/g, "/");
  const noext = rel.replace(/\.(tsx|ts)$/, "");
  const parts = noext.split("/").map((p) => {
    if (p.startsWith("$")) return `:${p.slice(1)}`;
    if (p === "index") return "";
    if (p.startsWith("(") && p.endsWith(")")) return "";
    return p;
  });
  const path = "/" + parts.filter(Boolean).join("/");
  return path === "/" ? "/" : path.replace(/\/$/, "");
}

// ── convex functions ───────────────────────────────────────────────────
interface ConvexFunction {
  project: string;
  file: string;
  name: string;
  kind:
    | "query"
    | "mutation"
    | "action"
    | "internalQuery"
    | "internalMutation"
    | "internalAction";
  args?: string;
  returns?: string;
  lines: number;
  lastCommit: string;
}

async function analyzeConvexFunctions(
  project: Project,
  repoRoot: string,
): Promise<ConvexFunction[]> {
  const out: ConvexFunction[] = [];
  for (const root of CONVEX_ROOTS[project]) {
    const abs = resolve(repoRoot, root);
    if (!(await pathExists(abs))) continue;
    const files = await listFiles(
      abs,
      (p) => p.endsWith(".ts") && !p.endsWith(".d.ts") && !p.endsWith("_generated.ts"),
    );
    for (const f of files) {
      const text = await readFile(f, "utf-8");
      const lines = text.split("\n").length;
      const re = /export\s+const\s+(\w+)\s*=\s*(query|mutation|action|internalQuery|internalMutation|internalAction)\s*\(/g;
      let m;
      while ((m = re.exec(text)) !== null) {
        const [, name, kind] = m;
        const { sha } = lastCommitFor(relative(repoRoot, f), repoRoot);
        out.push({
          project,
          file: relative(repoRoot, f),
          name: name!,
          kind: kind as ConvexFunction["kind"],
          lines,
          lastCommit: sha,
        });
      }
    }
  }
  return out;
}

// ── cloudflare resources ───────────────────────────────────────────────
interface CloudflareResource {
  project: string;
  kind: "worker" | "pages" | "r2" | "kv" | "d1" | "durable_object";
  name: string;
  account?: string;
  wranglerConfig?: string;
}

async function analyzeCloudflare(
  project: Project,
  repoRoot: string,
): Promise<CloudflareResource[]> {
  const out: CloudflareResource[] = [];
  for (const cfg of WRANGLER_CONFIGS[project]) {
    const abs = resolve(repoRoot, cfg);
    if (!(await pathExists(abs))) continue;
    const text = await readFile(abs, "utf-8");
    const account = /account_id\s*=\s*"([^"]+)"/.exec(text)?.[1];
    const seen = new Set<string>();
    const add = (kind: CloudflareResource["kind"], name: string) => {
      const key = `${kind}:${name}`;
      if (seen.has(key)) return;
      seen.add(key);
      out.push({ project, kind, name, account, wranglerConfig: cfg });
    };
    if (text.includes("pages_build_output_dir") || text.includes("[[pages_build_output_dir]]") || text.match(/name\s*=\s*"[\w-]+"\s*\n[\s\S]*?output_directory/)) {
      const name = /^name\s*=\s*"([^"]+)"/m.exec(text)?.[1];
      if (name) add("pages", name);
    } else {
      const name = /^name\s*=\s*"([^"]+)"/m.exec(text)?.[1];
      if (name) add("worker", name);
    }
    for (const m of text.matchAll(/\[\[r2_buckets\]\][\s\S]*?binding\s*=\s*"([^"]+)"[\s\S]*?bucket_name\s*=\s*"([^"]+)"/g)) {
      add("r2", m[2]!);
    }
    for (const m of text.matchAll(/\[\[kv_namespaces\]\][\s\S]*?binding\s*=\s*"([^"]+)"[\s\S]*?id\s*=\s*"([^"]+)"/g)) {
      add("kv", m[2]!);
    }
    for (const m of text.matchAll(/\[\[d1_databases\]\][\s\S]*?binding\s*=\s*"([^"]+)"[\s\S]*?database_name\s*=\s*"([^"]+)"/g)) {
      add("d1", m[2]!);
    }
    for (const m of text.matchAll(/\[\[durable_objects\.(bindings)\]\][\s\S]*?name\s*=\s*"([^"]+)"/g)) {
      add("durable_object", m[2]!);
    }
  }
  return out;
}

// ── baml schemas ───────────────────────────────────────────────────────
interface BamlSchema {
  project: string;
  file: string;
  classCount: number;
  functionCount: number;
  enumCount: number;
}

async function analyzeBaml(
  project: Project,
  repoRoot: string,
): Promise<BamlSchema[]> {
  const out: BamlSchema[] = [];
  for (const root of BAML_ROOTS[project]) {
    const abs = resolve(repoRoot, root);
    if (!(await pathExists(abs))) continue;
    const files = await listFiles(abs, (p) => p.endsWith(".baml"));
    for (const f of files) {
      const text = await readFile(f, "utf-8");
      const classCount = (text.match(/^\s*class\s+/gm) ?? []).length;
      const functionCount = (text.match(/^\s*function\s+/gm) ?? []).length;
      const enumCount = (text.match(/^\s*enum\s+/gm) ?? []).length;
      out.push({
        project,
        file: relative(repoRoot, f),
        classCount,
        functionCount,
        enumCount,
      });
    }
  }
  return out;
}

// ── marimo notebooks ──────────────────────────────────────────────────
interface MarimoNotebook {
  project: string;
  slug: string;
  file: string;
  title: string;
  cellCount: number;
}

async function analyzeMarimo(
  project: Project,
  repoRoot: string,
): Promise<MarimoNotebook[]> {
  const out: MarimoNotebook[] = [];
  for (const root of NOTEBOOK_ROOTS[project]) {
    const abs = resolve(repoRoot, root);
    if (!(await pathExists(abs))) continue;
    const files = await listFiles(abs, (p) => p.endsWith(".py") && !p.includes("__"));
    for (const f of files) {
      const text = await readFile(f, "utf-8");
      const cellCount = (text.match(/@app\.cell/g) ?? []).length;
      const rel = relative(repoRoot, f);
      const slug = rel
        .replace(/\.py$/, "")
        .replace(/^[^/]+\/[^/]+\//, "")
        .replace(/\//g, "/");
      const title = rel.split("/").pop()?.replace(/\.py$/, "") ?? slug;
      out.push({ project, slug, file: rel, title, cellCount });
    }
  }
  return out;
}

// ── orchestrator ──────────────────────────────────────────────────────
async function run(opts: AnalyzerOptions) {
  const projects: Project[] = opts.project
    ? [opts.project as Project]
    : ([...ALL_PROJECTS] as Project[]);

  const summary: Record<string, unknown> = {
    generatedAt: Date.now(),
    schemaVersion: 1,
  };
  if (opts.kind === "all" || opts.kind === "tanstack_routes") {
    const rows: TanstackRoute[] = [];
    for (const p of projects) {
      rows.push(...(await analyzeTanstackRoutes(p, opts.repoRoot)));
    }
    summary.tanstackRoutes = rows;
  }
  if (opts.kind === "all" || opts.kind === "convex_functions") {
    const rows: ConvexFunction[] = [];
    for (const p of projects) {
      rows.push(...(await analyzeConvexFunctions(p, opts.repoRoot)));
    }
    summary.convexFunctions = rows;
  }
  if (opts.kind === "all" || opts.kind === "cloudflare") {
    const rows: CloudflareResource[] = [];
    for (const p of projects) {
      rows.push(...(await analyzeCloudflare(p, opts.repoRoot)));
    }
    summary.cloudflareResources = rows;
  }
  if (opts.kind === "all" || opts.kind === "baml") {
    const rows: BamlSchema[] = [];
    for (const p of projects) {
      rows.push(...(await analyzeBaml(p, opts.repoRoot)));
    }
    summary.bamlSchemas = rows;
  }
  if (opts.kind === "all" || opts.kind === "marimo") {
    const rows: MarimoNotebook[] = [];
    for (const p of projects) {
      rows.push(...(await analyzeMarimo(p, opts.repoRoot)));
    }
    summary.marimoNotebooks = rows;
  }

  const output = JSON.stringify(summary, null, 2);
  if (opts.out) {
    await Bun.write(opts.out, output);
    console.error(`wrote ${output.length} bytes to ${opts.out}`);
  } else {
    console.log(output);
  }
  return summary;
}

const opts = parseArgs(process.argv.slice(2));
await run(opts);
