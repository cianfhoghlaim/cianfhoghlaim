// Convex function: annotations
import { v } from "convex/values";
import { mutation, query } from "../_generated/server";

export const addAnnotation = mutation({
  args: {
    stage: v.string(),
    document_url: v.string(),
    range_start: v.number(),
    range_end: v.number(),
    note: v.string(),
    author_id: v.string(),
    visibility: v.union(v.literal("private"), v.literal("public")),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("annotations", {
      ...args,
      created_at: Date.now(),
    });
  },
});

export const listAnnotations = query({
  args: { document_url: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("annotations")
      .withIndex("by_document", (q) => q.eq("document_url", args.document_url))
      .order("asc")
      .collect();
  },
});
