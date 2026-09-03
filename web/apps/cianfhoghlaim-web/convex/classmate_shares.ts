// Convex function: classmate_shares
import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const shareClassmateSession = mutation({
  args: {
    stage: v.string(),
    session_id: v.id("subject_sessions"),
    owner_id: v.string(),
    visibility: v.union(v.literal("public"), v.literal("link-only")),
  },
  handler: async (ctx, args) => {
    const share_token = crypto.randomUUID().replace(/-/g, "").slice(0, 16);
    const id = await ctx.db.insert("classmate_shares", {
      ...args,
      share_token,
      created_at: Date.now(),
    });
    return { id, share_token };
  },
});

export const getClassmateShare = query({
  args: { share_token: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("classmate_shares")
      .withIndex("by_token", (q) => q.eq("share_token", args.share_token))
      .first();
  },
});
