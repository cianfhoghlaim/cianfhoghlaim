// convex/gaeilge/discussExamPaper — per-subject Convex real-time backend.
//
// Per openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/
// The per-subject Convex schema + functions for the 6 BIEP v1 LC subjects.
// Pairs with the per-subject TanStack route tree at
// apps/cianfhoghlaim-leaving-cert/apps/web/src/routes/en/subjects/gaeilge/.

// discussExamPaper — per-subject Gaeilge exam paper discussion.
//
// Convex action that calls into the per-subject BAML backend
// baml/education/web/gaeilge_web.baml (function WebExamPaperDiscussion)
// to walk the student through a past exam question.
//
// Called from /en/subjects/gaeilge/exam-papers.

import { action, internalMutation } from "./_generated/server";
import { v } from "convex/values";
import { b } from "cianfhoghlaim.baml_client";

export const discussExamPaper = action({
  args: {
    sessionId: v.id("study_sessions"),
    paperYear: v.number(),
    paperLevel: v.union(v.literal("hl"), v.literal("ol"), v.literal("fl")),
    paperLanguage: v.union(v.literal("en"), v.literal("ga")),
    questionText: v.string(),
  },
  handler: async (ctx, args): Promise<string> => {
    const discussion = await b.WebExamPaperDiscussion({
      subject: "gaeilge",
      paper_year: args.paperYear,
      paper_level: args.paperLevel,
      paper_language: args.paperLanguage,
      question_text: args.questionText,
    });
    return await ctx.runMutation("exam_paper_discussions:insert", {
      sessionId: args.sessionId,
      subject: "gaeilge",
      paperYear: args.paperYear,
      paperLevel: args.paperLevel,
      paperLanguage: args.paperLanguage,
      questionText: args.questionText,
      discussionJson: JSON.stringify(discussion),
      createdAt: Date.now(),
      traceId: discussion.trace_id ?? null,
    });
  },
});

export const insertExamPaperDiscussion = internalMutation({
  args: {
    sessionId: v.id("study_sessions"),
    subject: v.literal("gaeilge"),
    paperYear: v.number(),
    paperLevel: v.union(v.literal("hl"), v.literal("ol"), v.literal("fl")),
    paperLanguage: v.union(v.literal("en"), v.literal("ga")),
    questionText: v.string(),
    discussionJson: v.string(),
    createdAt: v.number(),
    traceId: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("exam_paper_discussions", args);
  },
});
