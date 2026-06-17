import { v } from "convex/values";
import { mutation, query } from "../_generated/server";
import { requireOrgRole } from "./helpers";
import { loggedAction } from "../_middleware";

export const list = query({
  args: { project: v.optional(v.string()) },
  handler: async (ctx, args) => {
    if (args.project !== undefined) {
      return await ctx.db
        .query("convexFunctions")
        .withIndex("by_project_file", (q) => q.eq("project", args.project!))
        .collect();
    }
    return await ctx.db.query("convexFunctions").collect();
  },
});

export const getByProject = query({
  args: { project: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("convexFunctions")
      .withIndex("by_project_file", (q) => q.eq("project", args.project))
      .collect();
  },
});

export const getByName = query({
  args: { project: v.string(), name: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("convexFunctions")
      .withIndex("by_project_name", (q) =>
        q.eq("project", args.project).eq("name", args.name),
      )
      .first();
  },
});

export const ingest = mutation({
  args: {
    project: v.string(),
    rows: v.array(
      v.object({
        file: v.string(),
        name: v.string(),
        kind: v.union(
          v.literal("query"),
          v.literal("mutation"),
          v.literal("action"),
          v.literal("internalQuery"),
          v.literal("internalMutation"),
          v.literal("internalAction"),
        ),
        args: v.optional(v.string()),
        returns: v.optional(v.string()),
        lines: v.number(),
        lastCommit: v.string(),
      }),
    ),
  },
  handler: async (ctx, args) => {
    await requireOrgRole(ctx, "croilar-admin", ["owner", "admin"]);
    const existing = await ctx.db
      .query("convexFunctions")
      .withIndex("by_project_file", (q) => q.eq("project", args.project))
      .collect();
    for (const row of existing) {
      await ctx.db.delete(row._id);
    }
    for (const row of args.rows) {
      await ctx.db.insert("convexFunctions", { project: args.project, ...row });
    }
    return { deleted: existing.length, inserted: args.rows.length };
  },
});

export const refreshAll = loggedAction(
  async (_ctx, _args: { project?: string } | undefined) => {
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
      body: JSON.stringify({ kind: "convex_functions" }),
    });
    if (!resp.ok) {
      throw new Error(`analyzer failed: ${resp.status} ${await resp.text()}`);
    }
    return (await resp.json()) as { rows: number };
  },
  { function: "convex_functions.refreshAll", project: "croilar" },
);
