/**
 * croilar/apps/portal/src/lib/webstack.ts
 *
 * Web stack observability data layer (croilar-devtools-hub).
 *
 * The portal pages bind to the analyzer output (static JSON written by
 * scripts/analyze-web-stack.ts). When a Convex deployment is available,
 * the same shapes are available via the Convex `devtools.getSummary` /
 * `tanstack_routes.list` / etc. queries.
 *
 * All exports in this file are typed against the analyzer row shapes so
 * the portal pages work today and swap to Convex hooks later without
 * changing the consuming components.
 */

export interface TanstackRoute {
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

export interface ConvexFunction {
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

export interface CloudflareResource {
  project: string;
  kind: "worker" | "pages" | "r2" | "kv" | "d1" | "durable_object";
  name: string;
  account?: string;
  wranglerConfig?: string;
  lastDeployed?: number;
  version?: string;
}

export interface BamlSchema {
  project: string;
  file: string;
  classCount: number;
  functionCount: number;
  enumCount: number;
}

export interface MarimoNotebook {
  project: string;
  slug: string;
  file: string;
  title: string;
  cellCount: number;
}

export interface ConvexCall {
  function: string;
  kind: "query" | "mutation" | "action";
  project: string;
  args?: string;
  durationMs: number;
  ok: boolean;
  error?: string;
  calledAt: number;
}

export interface TestRun {
  project: string;
  suite: string;
  branch: string;
  commit: string;
  passed: number;
  failed: number;
  skipped: number;
  durationMs: number;
  startedAt: number;
  finishedAt: number;
  failureDetails?: string;
}

export interface WebStackSnapshot {
  generatedAt: number;
  tanstackRoutes: TanstackRoute[];
  convexFunctions: ConvexFunction[];
  cloudflareResources: CloudflareResource[];
  bamlSchemas: BamlSchema[];
  marimoNotebooks: MarimoNotebook[];
}

export const PROJECTS = ["tuatha", "oideachais", "croilar", "meaisinfhoghlaim"] as const;
export type Project = (typeof PROJECTS)[number];

const SNAPSHOT_URL = "/api/webstack/snapshot.json";

/**
 * Fetch the latest web stack snapshot. Returns an empty snapshot if the
 * analyzer has not been run yet.
 */
export async function fetchSnapshot(signal?: AbortSignal): Promise<WebStackSnapshot> {
  try {
    const res = await fetch(SNAPSHOT_URL, { signal });
    if (!res.ok) {
      return emptySnapshot();
    }
    return (await res.json()) as WebStackSnapshot;
  } catch {
    return emptySnapshot();
  }
}

export function emptySnapshot(): WebStackSnapshot {
  return {
    generatedAt: 0,
    tanstackRoutes: [],
    convexFunctions: [],
    cloudflareResources: [],
    bamlSchemas: [],
    marimoNotebooks: [],
  };
}

export function projectCounts(snapshot: WebStackSnapshot): Record<Project, number> {
  const out: Record<Project, number> = {
    tuatha: 0,
    oideachais: 0,
    croilar: 0,
    meaisinfhoghlaim: 0,
  };
  for (const r of snapshot.tanstackRoutes) {
    if (PROJECTS.includes(r.project as Project)) {
      out[r.project as Project] += 1;
    }
  }
  return out;
}

export function routesForProject(
  snapshot: WebStackSnapshot,
  project: Project,
): TanstackRoute[] {
  return snapshot.tanstackRoutes.filter((r) => r.project === project);
}

export function functionsForProject(
  snapshot: WebStackSnapshot,
  project: Project,
): ConvexFunction[] {
  return snapshot.convexFunctions.filter((f) => f.project === project);
}

export function bamlForProject(
  snapshot: WebStackSnapshot,
  project: Project,
): BamlSchema[] {
  return snapshot.bamlSchemas.filter((b) => b.project === project);
}

export function cloudflareForProject(
  snapshot: WebStackSnapshot,
  project: Project,
): CloudflareResource[] {
  return snapshot.cloudflareResources.filter((c) => c.project === project);
}

export function notebooksForProject(
  snapshot: WebStackSnapshot,
  project: Project,
): MarimoNotebook[] {
  return snapshot.marimoNotebooks.filter((n) => n.project === project);
}

export function troubleshoot(
  snapshot: WebStackSnapshot,
  project: Project,
  route: TanstackRoute,
): {
  functions: ConvexFunction[];
  baml: BamlSchema[];
  notebooks: MarimoNotebook[];
} {
  const dir = route.file.split("/").slice(0, -1).join("/");
  return {
    functions: functionsForProject(snapshot, project).filter(
      (f) => f.file.startsWith(dir) || f.file.includes(route.route),
    ),
    baml: bamlForProject(snapshot, project).filter((b) => b.file.startsWith(dir)),
    notebooks: notebooksForProject(snapshot, project).filter((n) =>
      n.file.startsWith(dir),
    ),
  };
}

export function formatTimestamp(ms: number): string {
  if (!ms) return "—";
  return new Date(ms).toISOString().replace("T", " ").slice(0, 19);
}

export function formatRelative(ms: number, now: number = Date.now()): string {
  if (!ms) return "—";
  const diff = now - ms;
  if (diff < 60_000) return `${Math.floor(diff / 1000)}s ago`;
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}
