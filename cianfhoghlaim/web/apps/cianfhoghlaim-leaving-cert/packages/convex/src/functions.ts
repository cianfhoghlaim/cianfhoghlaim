// Convex mutations + queries for the conic-leaving-cert deployment.
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R6.
//
// These functions consume the 8 tables defined in schema.ts:
//   - subject_sessions, practice_attempts, annotations,
//     classmate_shares, extraction_budget (5 carried-over)
//   - skill_assets, diagram_cache, badge_ledger (3 new)

import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// ── subject_sessions ──────────────────────────────────────────────────

export const startSession = mutation({
  args: {
    stage: v.string(),
    subject: v.string(),
    userId: v.string(),
    agnoSessionId: v.string(),
    language: v.union(v.literal("en"), v.literal("ga")),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("subject_sessions", {
      ...args,
      message_count: 0,
      last_active_at: Date.now(),
    });
  },
});

export const recordMessage = mutation({
  args: {
    sessionId: v.id("subject_sessions"),
  },
  handler: async (ctx, args) => {
    const session = await ctx.db.get(args.sessionId);
    if (!session) return null;
    await ctx.db.patch(args.sessionId, {
      message_count: session.message_count + 1,
      last_active_at: Date.now(),
    });
    return args.sessionId;
  },
});

// ── practice_attempts ─────────────────────────────────────────────────

export const recordAttempt = mutation({
  args: {
    stage: v.string(),
    subject: v.string(),
    userId: v.string(),
    questionId: v.string(),
    essay: v.string(),
    score: v.number(),
    rubricFingerprint: v.string(),
    traceId: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("practice_attempts", {
      ...args,
      submitted_at: Date.now(),
    });
  },
});

export const getAttemptsByUserSubject = query({
  args: {
    userId: v.string(),
    subject: v.string(),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("practice_attempts")
      .withIndex("by_user_subject", (q) =>
        q.eq("user_id", args.userId).eq("subject", args.subject),
      )
      .order("desc")
      .take(args.limit ?? 50);
  },
});

// ── badge_ledger ──────────────────────────────────────────────────────

export const issueBadge = mutation({
  args: {
    studentId: v.string(),
    framework: v.string(),
    level: v.string(),
    subject: v.string(),
    competencyCode: v.string(),
    competencyTextEn: v.string(),
    competencyTextGa: v.optional(v.string()),
    eiraicTier: v.number(),
    agentIssuer: v.string(),
    evidenceHash: v.string(),
    signature: v.string(),
    onChainAnchor: v.optional(v.string()),
    anchorDate: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("badge_ledger", {
      ...args,
      date_earned: Date.now(),
    });
  },
});

export const getBadgesByStudent = query({
  args: {
    studentId: v.string(),
    eiraicTier: v.optional(v.number()),
    subject: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    let q = ctx.db
      .query("badge_ledger")
      .withIndex("by_student", (q) => q.eq("student_id", args.studentId));
    const badges = await q.order("desc").collect();
    return badges.filter((b) => {
      if (args.eiraicTier !== undefined && b.eiraic_tier !== args.eiraicTier) return false;
      if (args.subject !== undefined && b.subject !== args.subject) return false;
      return true;
    });
  },
});

// ── diagram_cache ─────────────────────────────────────────────────────

export const getDiagramFromCache = query({
  args: {
    mode: v.string(),
    subject: v.string(),
    language: v.union(v.literal("en"), v.literal("ga")),
    level: v.optional(v.union(v.literal("hl"), v.literal("ol"), v.literal("fl"), v.literal("jc"))),
  },
  handler: async (ctx, args) => {
    const cached = await ctx.db
      .query("diagram_cache")
      .withIndex("by_mode_subject", (q) =>
        q
          .eq("mode", args.mode)
          .eq("subject", args.subject)
          .eq("language", args.language),
      )
      .first();
    if (!cached) return null;
    if (cached.stale_at < Date.now()) return null;
    return cached;
  },
});

export const storeDiagram = mutation({
  args: {
    mode: v.string(),
    subject: v.string(),
    language: v.union(v.literal("en"), v.literal("ga")),
    level: v.optional(v.union(v.literal("hl"), v.literal("ol"), v.literal("fl"), v.literal("jc"))),
    payload: v.any(),
    staleAfterHours: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const staleAfter = (args.staleAfterHours ?? 24) * 60 * 60 * 1000;
    return await ctx.db.insert("diagram_cache", {
      ...args,
      rendered_at: Date.now(),
      stale_at: Date.now() + staleAfter,
    });
  },
});

// ── skill_assets ─────────────────────────────────────────────────────

export const listSkillAssets = query({
  args: {
    subject: v.string(),
    mode: v.optional(v.string()),
    language: v.optional(v.union(v.literal("en"), v.literal("ga"))),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("skill_assets")
      .withIndex("by_subject_mode", (q) =>
        q.eq("subject", args.subject),
      )
      .collect()
      .then((assets) =>
        assets.filter((a) => {
          if (args.mode && a.mode !== args.mode) return false;
          if (args.language && a.language !== args.language) return false;
          return true;
        }),
      );
  },
});