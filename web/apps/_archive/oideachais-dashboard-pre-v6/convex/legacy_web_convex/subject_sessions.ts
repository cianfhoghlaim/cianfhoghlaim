// Convex function: subject_sessions
// Persists Agno team chat sessions so they survive container restarts and
// can be shared across devices.
import { v } from "convex/values";
import { mutation, query } from "../_generated/server";

export const createSubjectSession = mutation({
  args: {
    stage: v.string(),
    subject: v.string(),
    user_id: v.string(),
    agno_session_id: v.string(),
    language: v.union(v.literal("en"), v.literal("ga")),
  },
  handler: async (ctx, args) => {
    const id = await ctx.db.insert("subject_sessions", {
      ...args,
      message_count: 0,
      last_active_at: Date.now(),
    });
    return id;
  },
});

export const updateSubjectSession = mutation({
  args: {
    id: v.id("subject_sessions"),
    message_count: v.number(),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      message_count: args.message_count,
      last_active_at: Date.now(),
    });
  },
});

export const getSubjectSession = query({
  args: {
    stage: v.string(),
    subject: v.string(),
    user_id: v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("subject_sessions")
      .withIndex("by_user_stage", (q) =>
        q.eq("user_id", args.user_id).eq("stage", args.stage)
      )
      .filter((q) => q.eq(q.field("subject"), args.subject))
      .order("desc")
      .first();
  },
});
