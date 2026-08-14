import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const byTask = query({
  args: { taskId: v.id("tasks") },
  handler: async (ctx, { taskId }) => {
    return await ctx.db
      .query("comparisons")
      .withIndex("by_task", (q) => q.eq("taskId", taskId))
      .collect();
  },
});

export const get = query({
  args: { id: v.id("comparisons") },
  handler: async (ctx, { id }) => {
    return await ctx.db.get(id);
  },
});

export const updateStatus = mutation({
  args: {
    comparisonId: v.id("comparisons"),
    status: v.union(
      v.literal("pending"),
      v.literal("running"),
      v.literal("success"),
      v.literal("failed"),
      v.literal("timeout")
    ),
    durationMs: v.optional(v.number()),
    outputStorageId: v.optional(v.id("_storage")),
    outputSizeBytes: v.optional(v.number()),
    errorMessage: v.optional(v.string()),
    metrics: v.optional(
      v.object({
        tokenCount: v.optional(v.number()),
        characterCount: v.optional(v.number()),
        wordCount: v.optional(v.number()),
        confidence: v.optional(v.number()),
      })
    ),
  },
  handler: async (ctx, args) => {
    const { comparisonId, status, ...updates } = args;

    const patchData: Record<string, unknown> = { status, ...updates };

    if (status === "running") {
      patchData.startedAt = Date.now();
    }
    if (
      status === "success" ||
      status === "failed" ||
      status === "timeout"
    ) {
      patchData.completedAt = Date.now();
    }

    await ctx.db.patch(comparisonId, patchData);
  },
});

export const saveResult = mutation({
  args: {
    comparisonId: v.id("comparisons"),
    content: v.string(),
    fullContentStorageId: v.optional(v.id("_storage")),
    isTruncated: v.boolean(),
    previewLength: v.number(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("results", args);
  },
});

export const getResult = query({
  args: { comparisonId: v.id("comparisons") },
  handler: async (ctx, { comparisonId }) => {
    return await ctx.db
      .query("results")
      .withIndex("by_comparison", (q) => q.eq("comparisonId", comparisonId))
      .first();
  },
});
