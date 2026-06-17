import { query } from "../_generated/server";
import { requireOrgRole } from "./helpers";

export const getSummary = query({
  args: {},
  handler: async (ctx) => {
    await requireOrgRole(ctx, "croilar-admin", ["owner", "admin"]);
    const [
      routes,
      functions,
      cf,
      baml,
      notebooks,
      pipelines,
      stacks,
      latestGlance,
    ] = await Promise.all([
      ctx.db.query("tanstackRoutes").collect(),
      ctx.db.query("convexFunctions").collect(),
      ctx.db.query("cloudflareResources").collect(),
      ctx.db.query("bamlSchemas").collect(),
      ctx.db.query("marimoNotebooks").collect(),
      ctx.db.query("pipelines").collect(),
      ctx.db.query("stacks").collect(),
      ctx.db
        .query("glanceConfig")
        .withIndex("by_version")
        .order("desc")
        .first(),
    ]);
    const byProject = (rows: { project: string }[]): Record<string, number> => {
      const out: Record<string, number> = {};
      for (const r of rows) {
        out[r.project] = (out[r.project] ?? 0) + 1;
      }
      return out;
    };
    return {
      tanstackRoutes: byProject(routes),
      convexFunctions: byProject(functions),
      cloudflareResources: byProject(cf),
      bamlSchemas: byProject(baml),
      marimoNotebooks: byProject(notebooks),
      pipelineCount: pipelines.length,
      stackCount: stacks.length,
      glanceConfigVersion: latestGlance?.version ?? null,
      glanceConfigGeneratedAt: latestGlance?.generatedAt ?? null,
      generatedAt: Date.now(),
    };
  },
});
