// convex/gaeilge/updateSession — per-subject Convex real-time backend.
//
// Per openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/
// The per-subject Convex schema + functions for the 6 BIEP v1 LC subjects.
// Pairs with the per-subject TanStack route tree at
// apps/cianfhoghlaim-leaving-cert/apps/web/src/routes/en/subjects/gaeilge/.

// updateSession — update a per-subject Gaeilge study session with
// progress (lesson completed, topic mastered, message count).
//
// Convex mutation called from the per-subject interactive pages whenever
// the student completes an action (e.g. finished a syllabus topic,
// answered a practice question).

import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const updateSession = mutation({
  args: {
    sessionId: v.id("study_sessions"),
    messageCountDelta: v.optional(v.number()),
    planId: v.optional(v.id("study_plans")),
  },
  handler: async (ctx, args) => {
    const session = await ctx.db.get(args.sessionId);
    if (!session) return null;
    const patch: Record<string, unknown> = {
      last_active_at: Date.now(),
    };
    if (args.messageCountDelta !== undefined) {
      patch.message_count = session.message_count + args.messageCountDelta;
    }
    if (args.planId !== undefined) {
      patch.plan_id = args.planId;
    }
    await ctx.db.patch(args.sessionId, patch);
    return args.sessionId;
  },
});
