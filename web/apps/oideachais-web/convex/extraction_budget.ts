// Convex function: extraction_budget
// Tracks per-session BAML extraction budget (5 papers/day/session by default).
import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const incrementExtractionBudget = mutation({
  args: {
    session_id: v.string(),
    tokens_consumed: v.number(),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("extraction_budget")
      .withIndex("by_session", (q) => q.eq("session_id", args.session_id))
      .first();

    if (!existing) {
      const reset_at = Date.now() + 24 * 60 * 60 * 1000;
      return await ctx.db.insert("extraction_budget", {
        session_id: args.session_id,
        papers_extracted: 1,
        tokens_consumed: args.tokens_consumed,
        reset_at,
        last_extraction_at: Date.now(),
      });
    }

    await ctx.db.patch(existing._id, {
      papers_extracted: existing.papers_extracted + 1,
      tokens_consumed: existing.tokens_consumed + args.tokens_consumed,
      last_extraction_at: Date.now(),
    });
    return existing._id;
  },
});

export const getExtractionBudget = query({
  args: { session_id: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("extraction_budget")
      .withIndex("by_session", (q) => q.eq("session_id", args.session_id))
      .first();
  },
});
