// convex/english/generateStudyPlan — per-subject Convex real-time backend.
//
// Per openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/
// The per-subject Convex schema + functions for the 6 BIEP v1 LC subjects.
// Pairs with the per-subject TanStack route tree at
// apps/cianfhoghlaim-leaving-cert/apps/web/src/routes/en/subjects/english/.

// generateStudyPlan — per-subject English study plan generator.
//
// Convex action that calls into the per-subject BAML backend
// baml/education/web/english_web.baml (function WebStudyPlan), which
// itself delegates to baml/education/subjects/Béarla for the
// per-subject syllabus + past-paper grounding.
//
// Called from /en/subjects/english/study-plan.

import { action } from "./_generated/server";
import { v } from "convex/values";
import { b } from "cianfhoghlaim.baml_client";

export const generateStudyPlan = action({
  args: {
    sessionId: v.id("study_sessions"),
    weeksUntilExam: v.number(),
    targetLevel: v.union(v.literal("hl"), v.literal("ol"), v.literal("fl")),
    language: v.union(v.literal("en"), v.literal("ga")),
    focusTopics: v.optional(v.array(v.string())),
  },
  handler: async (ctx, args): Promise<string> => {
    const plan = await b.WebStudyPlan({
      subject: "english",
      weeks_until_exam: args.weeksUntilExam,
      target_level: args.targetLevel,
      language: args.language,
      focus_topics: args.focusTopics ?? [],
    });
    const planId = await ctx.runMutation("study_plans:insert", {
      sessionId: args.sessionId,
      subject: "english",
      planJson: JSON.stringify(plan),
      language: args.language,
      generatedAt: Date.now(),
      traceId: plan.trace_id ?? null,
    });
    await ctx.runMutation("study_sessions:setPlan", {
      sessionId: args.sessionId,
      planId,
    });
    return planId;
  },
});

// Internal mutations registered below for ctx.runMutation access.

import { internalMutation } from "./_generated/server";

export const insertStudyPlan = internalMutation({
  args: {
    sessionId: v.id("study_sessions"),
    subject: v.literal("english"),
    planJson: v.string(),
    language: v.union(v.literal("en"), v.literal("ga")),
    generatedAt: v.number(),
    traceId: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("study_plans", args);
  },
});

export const setSessionPlan = internalMutation({
  args: {
    sessionId: v.id("study_sessions"),
    planId: v.id("study_plans"),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.sessionId, { plan_id: args.planId, last_active_at: Date.now() });
  },
});
