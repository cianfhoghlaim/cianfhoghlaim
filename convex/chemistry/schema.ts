// convex/chemistry/schema — per-subject Convex real-time backend.
//
// Per openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/
// The per-subject Convex schema + functions for the 6 BIEP v1 LC subjects.
// Pairs with the per-subject TanStack route tree at
// apps/cianfhoghlaim-leaving-cert/apps/web/src/routes/en/subjects/chemistry/.

// Convex schema for the per-subject Chemistry (Ceimic) interactive study
// surface. Defines 3 tables: study_sessions, syllabus_progress, and
// exam_paper_discussions.
//
// Per-subject BAML backend (functions: WebStudyPlan,
// WebExamPaperDiscussion, WebMarkingSchemeExplanation) lives at
// baml/education/web/chemistry_web.baml. The foundation extraction is in
// baml/education/subjects/qpack_chemistry.baml.
//
// These tables are consumed by the per-subject TanStack routes:
//   - convex/chemistry/createSession.ts   → POST /en/subjects/chemistry/study-plan
//   - convex/chemistry/getSession.ts      → GET  /en/subjects/chemistry/syllabus
//   - convex/chemistry/updateSession.ts   → POST /en/subjects/chemistry/syllabus
//   - convex/chemistry/generateStudyPlan.ts → POST /en/subjects/chemistry/study-plan
//   - convex/chemistry/discussExamPaper.ts → POST /en/subjects/chemistry/exam-papers

import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // One row per per-subject interactive study session.
  study_sessions: defineTable({
    subject: v.literal("chemistry"),
    user_id: v.string(),
    agno_session_id: v.string(),
    language: v.union(v.literal("en"), v.literal("ga")),
    level: v.union(v.literal("hl"), v.literal("ol"), v.literal("fl"), v.literal("jc")),
    started_at: v.number(),
    last_active_at: v.number(),
    message_count: v.number(),
    plan_id: v.optional(v.id("study_plans")),
  })
    .index("by_user", ["user_id"])
    .index("by_agno_session", ["agno_session_id"]),

  // Per-session generated study plan (output of WebStudyPlan BAML action).
  study_plans: defineTable({
    session_id: v.id("study_sessions"),
    subject: v.literal("chemistry"),
    plan_json: v.string(),         // serialised WebStudyPlanResponse
    language: v.union(v.literal("en"), v.literal("ga")),
    generated_at: v.number(),
    trace_id: v.optional(v.string()),
  })
    .index("by_session", ["session_id"]),

  // Per-exam-paper discussion thread (output of WebExamPaperDiscussion).
  exam_paper_discussions: defineTable({
    session_id: v.id("study_sessions"),
    subject: v.literal("chemistry"),
    paper_year: v.number(),
    paper_level: v.union(v.literal("hl"), v.literal("ol"), v.literal("fl")),
    paper_language: v.union(v.literal("en"), v.literal("ga")),
    question_text: v.string(),
    discussion_json: v.string(),   // serialised WebExamPaperDiscussionResponse
    created_at: v.number(),
    trace_id: v.optional(v.string()),
  })
    .index("by_session", ["session_id"])
    .index("by_paper", ["subject", "paper_year", "paper_level"]),
});
