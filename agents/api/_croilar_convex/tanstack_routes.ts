import { v } from "convex/values";
import { mutation, query } from "../_generated/server";
import { DEVTOOLS_READ_ROLES, DEVTOOLS_WRITE_ROLES, requireDevtoolsRead, requireOrgRole } from "./helpers";
import { loggedAction } from "../_middleware";

export const list = query({
  args: {
    project: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    await requireDevtoolsRead(ctx);
    if (args.project !== undefined) {
      return await ctx.db
        .query("tanstackRoutes")
        .withIndex("by_project", (q) => q.eq("project", args.project!))
        .collect();
    }
    return await ctx.db.query("tanstackRoutes").collect();
  },
});

export const getByProject = query({
  args: { project: v.string() },
  handler: async (ctx, args) => {
    await requireDevtoolsRead(ctx);
    return await ctx.db
      .query("tanstackRoutes")
      .withIndex("by_project", (q) => q.eq("project", args.project))
      .collect();
  },
});

export const getSummary = query({
  args: {},
  handler: async (ctx) => {
    await requireDevtoolsRead(ctx);
    const routes = await ctx.db.query("tanstackRoutes").collect();
    const summary: Record<string, number> = {};
    for (const r of routes) {
      summary[r.project] = (summary[r.project] ?? 0) + 1;
    }
    return summary;
  },
});

export const ingest = mutation({
  args: {
    project: v.string(),
    rows: v.array(
      v.object({
        route: v.string(),
        file: v.string(),
        isPublic: v.boolean(),
        isServer: v.boolean(),
        hasLoader: v.boolean(),
        hasAuth: v.boolean(),
        lines: v.number(),
        lastCommit: v.string(),
        lastCommitAt: v.number(),
      }),
    ),
  },
  handler: async (ctx, args) => {
    await requireOrgRole(ctx, "croilar-admin", DEVTOOLS_WRITE_ROLES);
    const existing = await ctx.db
      .query("tanstackRoutes")
      .withIndex("by_project", (q) => q.eq("project", args.project))
      .collect();
    for (const row of existing) {
      await ctx.db.delete(row._id);
    }
    for (const row of args.rows) {
      await ctx.db.insert("tanstackRoutes", { project: args.project, ...row });
    }
    return { deleted: existing.length, inserted: args.rows.length };
  },
});

export const refreshAll = loggedAction(
  async (ctx, _args: { project?: string } | undefined) => {
    const httpUrl = process.env.CROILAR_CONVEX_HTTP_URL;
    const deployKey = process.env.CROILAR_CONVEX_DEPLOY_KEY;
    if (!httpUrl || !deployKey) {
      throw new Error(
        "CROILAR_CONVEX_HTTP_URL and CROILAR_CONVEX_DEPLOY_KEY must be set",
      );
    }
    const resp = await fetch(`${httpUrl}/api/run/analyze-web-stack`, {
      method: "POST",
      headers: {
        Authorization: `Convex ${deployKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ kind: "tanstack_routes" }),
    });
    if (!resp.ok) {
      throw new Error(`analyzer failed: ${resp.status} ${await resp.text()}`);
    }
    const data = (await resp.json()) as { rows: unknown[] };
    await ctx.runMutation("tanstack_routes:ingest" as any, {
      project: "all",
      rows: data.rows,
    });
    return { rows: data.rows.length };
  },
  { function: "tanstack_routes.refreshAll", project: "croilar" },
);
