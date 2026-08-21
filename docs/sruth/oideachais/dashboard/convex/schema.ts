import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // Tasks table - main comparison jobs
  tasks: defineTable({
    filename: v.string(),
    fileSize: v.number(),
    fileStorageId: v.optional(v.id("_storage")),
    outputFormat: v.union(
      v.literal("markdown"),
      v.literal("json"),
      v.literal("text")
    ),
    status: v.union(
      v.literal("pending"),
      v.literal("running"),
      v.literal("completed"),
      v.literal("failed"),
      v.literal("cancelled")
    ),
    selectedModels: v.array(v.string()),
    totalDurationMs: v.optional(v.number()),
    createdAt: v.number(),
    completedAt: v.optional(v.number()),
    createdBy: v.optional(v.string()),
    metadata: v.optional(
      v.object({
        pageCount: v.optional(v.number()),
        hasImages: v.optional(v.boolean()),
        language: v.optional(v.string()),
      })
    ),
  })
    .index("by_status", ["status"])
    .index("by_created", ["createdAt"]),

  // Comparisons table - individual model runs within a task
  comparisons: defineTable({
    taskId: v.id("tasks"),
    modelName: v.string(),
    modelProvider: v.string(),
    status: v.union(
      v.literal("pending"),
      v.literal("running"),
      v.literal("success"),
      v.literal("failed"),
      v.literal("timeout")
    ),
    startedAt: v.optional(v.number()),
    completedAt: v.optional(v.number()),
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
  })
    .index("by_task", ["taskId"])
    .index("by_model", ["modelName"])
    .index("by_status", ["status"]),

  // Model registry - available models and their status
  models: defineTable({
    name: v.string(),
    displayName: v.string(),
    provider: v.string(),
    endpoint: v.string(),
    isAvailable: v.boolean(),
    capabilities: v.array(v.string()),
    vramRequirement: v.optional(v.string()),
    avgLatencyMs: v.optional(v.number()),
    successRate: v.optional(v.number()),
    lastChecked: v.optional(v.number()),
    metadata: v.optional(
      v.object({
        contextLength: v.optional(v.number()),
        supportsIrish: v.optional(v.boolean()),
        specialization: v.optional(v.string()),
      })
    ),
  })
    .index("by_name", ["name"])
    .index("by_provider", ["provider"])
    .index("by_availability", ["isAvailable"]),

  // Results cache - stores processed outputs for quick retrieval
  results: defineTable({
    comparisonId: v.id("comparisons"),
    content: v.string(),
    fullContentStorageId: v.optional(v.id("_storage")),
    isTruncated: v.boolean(),
    previewLength: v.number(),
  }).index("by_comparison", ["comparisonId"]),
});
