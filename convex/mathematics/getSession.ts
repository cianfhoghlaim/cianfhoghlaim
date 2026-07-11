// convex/mathematics/getSession — per-subject Convex real-time backend.
//
// Per openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/
// The per-subject Convex schema + functions for the 6 BIEP v1 LC subjects.
// Pairs with the per-subject TanStack route tree at
// apps/cianfhoghlaim-leaving-cert/apps/web/src/routes/en/subjects/mathematics/.

// getSession — fetch a per-subject Mathematics interactive study session
// by id (or by the most-recent session for a user).
//
// Convex query called from /en/subjects/mathematics/syllabus and the
// /en/subjects/mathematics/study-plan page on load.

import { query } from "./_generated/server";
import { v } from "convex/values";

export const getSession = query({
  args: {
    sessionId: v.optional(v.id("study_sessions")),
    userId: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    if (args.sessionId) {
      return await ctx.db.get(args.sessionId);
    }
    if (args.userId) {
      const sessions = await ctx.db
        .query("study_sessions")
        .withIndex("by_user", (q) => q.eq("user_id", args.userId!))
        .filter((q) => q.eq(q.field("subject"), "mathematics"))
        .order("desc")
        .take(1);
      return sessions[0] ?? null;
    }
    return null;
  },
});

export const listSessions = query({
  args: { userId: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("study_sessions")
      .withIndex("by_user", (q) => q.eq("user_id", args.userId))
      .filter((q) => q.eq(q.field("subject"), "mathematics"))
      .order("desc")
      .take(20);
  },
});
