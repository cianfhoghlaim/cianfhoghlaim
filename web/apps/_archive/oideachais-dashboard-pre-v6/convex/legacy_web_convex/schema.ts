// Convex schema for Cianfhoghlaim Oideachais.
// 5 tables: subject_sessions, practice_attempts, annotations, classmate_shares, extraction_budget.
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  subject_sessions: defineTable({
    stage: v.string(),                       // aistear | primary | junior_cycle | senior_cycle | tertiary
    subject: v.string(),                     // subject slug (e.g., "mathematics")
    user_id: v.string(),
    agno_session_id: v.string(),
    message_count: v.number(),
    last_active_at: v.number(),               // ms since epoch
    language: v.union(v.literal("en"), v.literal("ga")),
  })
    .index("by_user_stage", ["user_id", "stage"])
    .index("by_agno_session", ["agno_session_id"]),

  practice_attempts: defineTable({
    stage: v.string(),
    subject: v.string(),
    user_id: v.string(),
    question_id: v.string(),
    essay: v.string(),
    score: v.number(),
    rubric_fingerprint: v.string(),
    trace_id: v.optional(v.string()),
    submitted_at: v.number(),
  })
    .index("by_user_subject", ["user_id", "subject"])
    .index("by_trace", ["trace_id"]),

  annotations: defineTable({
    stage: v.string(),
    document_url: v.string(),
    range_start: v.number(),
    range_end: v.number(),
    note: v.string(),
    author_id: v.string(),
    visibility: v.union(v.literal("private"), v.literal("public")),
    created_at: v.number(),
  })
    .index("by_document", ["document_url"])
    .index("by_author", ["author_id"]),

  classmate_shares: defineTable({
    stage: v.string(),
    session_id: v.id("subject_sessions"),
    owner_id: v.string(),
    share_token: v.string(),
    visibility: v.union(v.literal("public"), v.literal("link-only")),
    created_at: v.number(),
  })
    .index("by_token", ["share_token"])
    .index("by_owner", ["owner_id"]),

  extraction_budget: defineTable({
    session_id: v.string(),
    papers_extracted: v.number(),
    tokens_consumed: v.number(),
    reset_at: v.number(),
    last_extraction_at: v.optional(v.number()),
  })
    .index("by_session", ["session_id"]),
});
