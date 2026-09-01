// Convex function: practice_attempts
import { v } from "convex/values";
import { mutation, query } from "../_generated/server";

export const recordPracticeAttempt = mutation({
  args: {
    stage: v.string(),
    subject: v.string(),
    user_id: v.string(),
    question_id: v.string(),
    essay: v.string(),
    score: v.number(),
    rubric_fingerprint: v.string(),
    trace_id: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("practice_attempts", {
      ...args,
      submitted_at: Date.now(),
    });
  },
});

export const listPracticeAttempts = query({
  args: { subject: v.string(), user_id: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("practice_attempts")
      .withIndex("by_user_subject", (q) =>
        q.eq("user_id", args.user_id).eq("subject", args.subject)
      )
      .order("desc")
      .collect();
  },
});
