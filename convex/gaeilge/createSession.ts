// convex/gaeilge/createSession — per-subject Convex real-time backend.
//
// Per openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/
// The per-subject Convex schema + functions for the 6 BIEP v1 LC subjects.
// Pairs with the per-subject TanStack route tree at
// apps/cianfhoghlaim-leaving-cert/apps/web/src/routes/en/subjects/gaeilge/.

// createSession — start a per-subject Gaeilge interactive study session.
//
// Convex mutation called from /en/subjects/gaeilge/study-plan when the
// student presses "Start studying". Creates a study_sessions row and
// returns its id. The session_id is then passed to generateStudyPlan.

import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const createSession = mutation({
  args: {
    userId: v.string(),
    agnoSessionId: v.string(),
    language: v.union(v.literal("en"), v.literal("ga")),
    level: v.union(v.literal("hl"), v.literal("ol"), v.literal("fl"), v.literal("jc")),
  },
  handler: async (ctx, args) => {
    const now = Date.now();
    return await ctx.db.insert("study_sessions", {
      subject: "gaeilge",
      user_id: args.userId,
      agno_session_id: args.agnoSessionId,
      language: args.language,
      level: args.level,
      started_at: now,
      last_active_at: now,
      message_count: 0,
    });
  },
});
