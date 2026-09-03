import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const create = mutation({
  args: {
    filename: v.string(),
    fileSize: v.number(),
    fileStorageId: v.optional(v.id("_storage")),
    outputFormat: v.union(
      v.literal("markdown"),
      v.literal("json"),
      v.literal("text")
    ),
    selectedModels: v.array(v.string()),
  },
  handler: async (ctx, args) => {
    const taskId = await ctx.db.insert("tasks", {
      ...args,
      status: "pending",
      createdAt: Date.now(),
    });

    // Create comparison records for each model
    for (const model of args.selectedModels) {
      await ctx.db.insert("comparisons", {
        taskId,
        modelName: model,
        modelProvider: getProviderForModel(model),
        status: "pending",
      });
    }

    return taskId;
  },
});

export const updateStatus = mutation({
  args: {
    taskId: v.id("tasks"),
    status: v.union(
      v.literal("pending"),
      v.literal("running"),
      v.literal("completed"),
      v.literal("failed"),
      v.literal("cancelled")
    ),
    totalDurationMs: v.optional(v.number()),
  },
  handler: async (ctx, { taskId, status, totalDurationMs }) => {
    const updates: Record<string, unknown> = { status };
    if (status === "completed" || status === "failed") {
      updates.completedAt = Date.now();
    }
    if (totalDurationMs !== undefined) {
      updates.totalDurationMs = totalDurationMs;
    }
    await ctx.db.patch(taskId, updates);
  },
});

export const get = query({
  args: { id: v.id("tasks") },
  handler: async (ctx, { id }) => {
    return await ctx.db.get(id);
  },
});

export const getWithComparisons = query({
  args: { id: v.id("tasks") },
  handler: async (ctx, { id }) => {
    const task = await ctx.db.get(id);
    if (!task) return null;

    const comparisons = await ctx.db
      .query("comparisons")
      .withIndex("by_task", (q) => q.eq("taskId", id))
      .collect();

    return { task, comparisons };
  },
});

export const recent = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, { limit = 20 }) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_created")
      .order("desc")
      .take(limit);
  },
});

export const deleteTask = mutation({
  args: { taskId: v.id("tasks") },
  handler: async (ctx, { taskId }) => {
    // Delete all comparisons for this task
    const comparisons = await ctx.db
      .query("comparisons")
      .withIndex("by_task", (q) => q.eq("taskId", taskId))
      .collect();

    for (const comparison of comparisons) {
      // Delete results first
      const results = await ctx.db
        .query("results")
        .withIndex("by_comparison", (q) => q.eq("comparisonId", comparison._id))
        .collect();
      for (const result of results) {
        await ctx.db.delete(result._id);
      }
      await ctx.db.delete(comparison._id);
    }

    await ctx.db.delete(taskId);
  },
});

// Helper function to get provider for a model
function getProviderForModel(modelName: string): string {
  const providerMap: Record<string, string> = {
    "qwen3-vl-30b": "llama-swap",
    "glm-4.6v-flash": "llama-swap",
    "gemma-3-27b": "llama-swap",
    "olmocr-7b": "mlx-omni-server",
    "granite-docling": "mlx-omni-server",
    "dots-ocr": "vllm",
    paddleocr: "paddle",
    docling: "docling",
    unstract: "unstract",
    pymupdf4llm: "library",
    markitdown: "library",
    marker: "library",
    tesseract: "library",
  };
  return providerMap[modelName] || "unknown";
}
