import { v } from "convex/values";
import { mutation, query } from "../_generated/server";
import { requireOrgRole } from "./helpers";

export const list = query({
  args: {
    project: v.optional(v.string()),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const lim = args.limit ?? 50;
    if (args.project !== undefined) {
      return await ctx.db
        .query("testRuns")
        .withIndex("by_project_started", (q) => q.eq("project", args.project!))
        .order("desc")
        .take(lim);
    }
    return await ctx.db.query("testRuns").order("desc").take(lim);
  },
});

export const getLatest = query({
  args: { project: v.string(), branch: v.optional(v.string()) },
  handler: async (ctx, args) => {
    if (args.branch) {
      return await ctx.db
        .query("testRuns")
        .withIndex("by_project_branch", (q) =>
          q.eq("project", args.project).eq("branch", args.branch!),
        )
        .order("desc")
        .first();
    }
    return await ctx.db
      .query("testRuns")
      .withIndex("by_project_started", (q) => q.eq("project", args.project))
      .order("desc")
      .first();
  },
});

export const getByProject = query({
  args: { project: v.string(), limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("testRuns")
      .withIndex("by_project_started", (q) => q.eq("project", args.project))
      .order("desc")
      .take(args.limit ?? 10);
  },
});

export const ingest = mutation({
  args: {
    project: v.string(),
    suite: v.string(),
    branch: v.string(),
    commit: v.string(),
    passed: v.number(),
    failed: v.number(),
    skipped: v.number(),
    durationMs: v.number(),
    startedAt: v.number(),
    finishedAt: v.number(),
    failureDetails: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    await requireOrgRole(ctx, "croilar-admin", ["owner", "admin"]);
    const id = await ctx.db.insert("testRuns", args);
    return id;
  },
});
