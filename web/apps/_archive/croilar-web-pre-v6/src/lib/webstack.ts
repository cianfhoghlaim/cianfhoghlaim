/**
 * STUB for `lib/webstack` (expanded).
 *
 * Per the 2026-08-26 build subagent report: the webstack helper module was
 * planned but never created. Stubbed here to unblock the typecheck. The
 * routes/admin/web/$project.tsx + pipelines.tsx + notebooks/{$slug,index}.tsx
 * pages consume 17 exports (fetchSnapshot, Project, ConvexFunction, etc).
 */
export type WebStackSnapshot = {
  pipelines: ReadonlyArray<unknown>;
  convexFunctions: ReadonlyArray<unknown>;
  bamlSchemas: ReadonlyArray<unknown>;
  notebooks: ReadonlyArray<unknown>;
  routes: ReadonlyArray<unknown>;
  projects: ReadonlyArray<unknown>;
};

export type MarimoNotebook = {
  slug: string;
  title: string;
  description?: string;
  url?: string;
};

export type Project = {
  slug: string;
  name: string;
  description?: string;
  status?: "active" | "archived";
};

export type ConvexFunction = {
  path: string;
  args?: Record<string, unknown>;
  returns?: string;
};

export type BamlSchema = {
  name: string;
  client?: string;
  fields?: ReadonlyArray<string>;
};

export type TanstackRoute = {
  path: string;
  file?: string;
};

export async function fetchSnapshot(): Promise<WebStackSnapshot> {
  return { pipelines: [], convexFunctions: [], bamlSchemas: [], notebooks: [], routes: [], projects: [] };
}

export function formatRelative(_timestamp: number | string): string {
  return "—";
}

export const PROJECTS: ReadonlyArray<Project> = [];

export function troubleshoot(_opts: Record<string, unknown> = {}): {
  recommendations: ReadonlyArray<string>;
} {
  return { recommendations: [] };
}
