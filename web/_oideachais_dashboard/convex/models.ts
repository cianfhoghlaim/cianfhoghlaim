import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("models").collect();
  },
});

export const available = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db
      .query("models")
      .withIndex("by_availability", (q) => q.eq("isAvailable", true))
      .collect();
  },
});

export const get = query({
  args: { name: v.string() },
  handler: async (ctx, { name }) => {
    return await ctx.db
      .query("models")
      .withIndex("by_name", (q) => q.eq("name", name))
      .first();
  },
});

export const upsert = mutation({
  args: {
    name: v.string(),
    displayName: v.string(),
    provider: v.string(),
    endpoint: v.string(),
    isAvailable: v.boolean(),
    capabilities: v.array(v.string()),
    vramRequirement: v.optional(v.string()),
    metadata: v.optional(
      v.object({
        contextLength: v.optional(v.number()),
        supportsIrish: v.optional(v.boolean()),
        specialization: v.optional(v.string()),
      })
    ),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("models")
      .withIndex("by_name", (q) => q.eq("name", args.name))
      .first();

    if (existing) {
      await ctx.db.patch(existing._id, {
        ...args,
        lastChecked: Date.now(),
      });
      return existing._id;
    } else {
      return await ctx.db.insert("models", {
        ...args,
        lastChecked: Date.now(),
      });
    }
  },
});

export const updateAvailability = mutation({
  args: {
    name: v.string(),
    isAvailable: v.boolean(),
    avgLatencyMs: v.optional(v.number()),
    successRate: v.optional(v.number()),
  },
  handler: async (ctx, { name, isAvailable, avgLatencyMs, successRate }) => {
    const model = await ctx.db
      .query("models")
      .withIndex("by_name", (q) => q.eq("name", name))
      .first();

    if (model) {
      const updates: Record<string, unknown> = {
        isAvailable,
        lastChecked: Date.now(),
      };
      if (avgLatencyMs !== undefined) updates.avgLatencyMs = avgLatencyMs;
      if (successRate !== undefined) updates.successRate = successRate;

      await ctx.db.patch(model._id, updates);
    }
  },
});

// Seed the default models
export const seed = mutation({
  args: {},
  handler: async (ctx) => {
    const defaultModels = [
      // VLM Models (llama-swap)
      {
        name: "qwen3-vl-30b",
        displayName: "Qwen3-VL-30B",
        provider: "llama-swap",
        endpoint: "http://localhost:8080",
        isAvailable: true,
        capabilities: ["vision", "document", "table", "irish"],
        vramRequirement: "18GB",
        metadata: { supportsIrish: true, contextLength: 32768 },
      },
      {
        name: "glm-4.6v-flash",
        displayName: "GLM-4.6V Flash",
        provider: "llama-swap",
        endpoint: "http://localhost:8080",
        isAvailable: true,
        capabilities: ["vision", "document"],
        vramRequirement: "6GB",
        metadata: { contextLength: 131072 },
      },
      {
        name: "gemma-3-27b",
        displayName: "Gemma-3-27B",
        provider: "llama-swap",
        endpoint: "http://localhost:8080",
        isAvailable: true,
        capabilities: ["vision", "multilingual"],
        vramRequirement: "16GB",
      },
      // MLX Models
      {
        name: "olmocr-7b",
        displayName: "OlmOCR-7B",
        provider: "mlx-omni-server",
        endpoint: "http://localhost:10240",
        isAvailable: true,
        capabilities: ["ocr", "table", "dense-text"],
        vramRequirement: "4GB",
      },
      {
        name: "granite-docling",
        displayName: "Granite-Docling",
        provider: "mlx-omni-server",
        endpoint: "http://localhost:10240",
        isAvailable: true,
        capabilities: ["document", "structure"],
        vramRequirement: "0.5GB",
      },
      // vLLM
      {
        name: "dots-ocr",
        displayName: "dots.ocr",
        provider: "vllm",
        endpoint: "http://localhost:8001",
        isAvailable: true,
        capabilities: ["ocr", "layout", "table", "formula", "multilingual"],
        vramRequirement: "4GB",
        metadata: { specialization: "SOTA layout detection, 100+ languages" },
      },
      // Platform Services
      {
        name: "paddleocr",
        displayName: "PaddleOCR",
        provider: "paddle",
        endpoint: "http://localhost:8000",
        isAvailable: true,
        capabilities: ["ocr", "fast"],
      },
      {
        name: "docling",
        displayName: "Docling",
        provider: "docling",
        endpoint: "http://localhost:5001",
        isAvailable: true,
        capabilities: ["document", "layout"],
        metadata: { specialization: "IBM Document Intelligence" },
      },
      {
        name: "unstract",
        displayName: "Unstract",
        provider: "unstract",
        endpoint: "http://localhost:8002",
        isAvailable: true,
        capabilities: ["workflow", "multi-tool"],
        metadata: { specialization: "Document workflow orchestration" },
      },
      // Python Libraries
      {
        name: "pymupdf4llm",
        displayName: "PyMuPDF4LLM",
        provider: "library",
        endpoint: "local",
        isAvailable: true,
        capabilities: ["fast", "text-extraction"],
        metadata: { specialization: "Fast PDF text extraction" },
      },
      {
        name: "markitdown",
        displayName: "MarkItDown",
        provider: "library",
        endpoint: "local",
        isAvailable: true,
        capabilities: ["markdown", "document"],
        metadata: { specialization: "Microsoft markdown converter" },
      },
      {
        name: "marker",
        displayName: "Marker",
        provider: "library",
        endpoint: "local",
        isAvailable: true,
        capabilities: ["ml", "layout", "high-quality"],
        metadata: { specialization: "ML-based layout analysis, highest quality" },
      },
      {
        name: "tesseract",
        displayName: "Tesseract",
        provider: "library",
        endpoint: "local",
        isAvailable: true,
        capabilities: ["ocr", "legacy"],
        metadata: { specialization: "Classic OCR, legacy/fallback" },
      },
    ];

    for (const model of defaultModels) {
      const existing = await ctx.db
        .query("models")
        .withIndex("by_name", (q) => q.eq("name", model.name))
        .first();

      if (!existing) {
        await ctx.db.insert("models", {
          ...model,
          lastChecked: Date.now(),
        });
      }
    }
  },
});
