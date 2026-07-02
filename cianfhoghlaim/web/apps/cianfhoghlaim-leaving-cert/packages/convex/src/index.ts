// Convex schema + functions for Cianfhoghlaim Leaving Cert
// Fresh standalone deployment: `conic-leaving-cert` (NOT cross-workspace with croilar-portal).
// 5 carried-over tables (byte-for-byte identical to oideachais-web/convex/schema.ts)
// + 3 new tables (skill_assets, diagram_cache, badge_ledger).

import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";
export { } from "./functions";

export default defineSchema({
  // ── 5 carried-over tables ──
  subject_sessions: defineTable({
    stage: v.string(),
    subject: v.string(),
    user_id: v.string(),
    agno_session_id: v.string(),
    message_count: v.number(),
    last_active_at: v.number(),
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
    budget_limit: v.number(),
    reset_at: v.number(),
  })
    .index("by_session", ["session_id"]),

  // ── 3 new tables ──
  skill_assets: defineTable({
    subject: v.string(),
    mode: v.string(),
    language: v.union(v.literal("en"), v.literal("ga")),
    level: v.union(v.literal("hl"), v.literal("ol"), v.literal("fl"), v.literal("jc")),
    storage_id: v.string(),
    storage_format: v.union(v.literal("svg"), v.literal("png"), v.literal("glb"), v.literal("usdz")),
    eiraic_tier: v.optional(v.number()),
    meta: v.object({
      width: v.optional(v.number()),
      height: v.optional(v.number()),
      byte_size: v.optional(v.number()),
      sha256: v.optional(v.string()),
    }),
    created_at: v.number(),
  })
    .index("by_subject_mode", ["subject", "mode", "language"]),

  diagram_cache: defineTable({
    mode: v.string(),
    subject: v.string(),
    language: v.union(v.literal("en"), v.literal("ga")),
    level: v.optional(v.union(v.literal("hl"), v.literal("ol"), v.literal("fl"), v.literal("jc"))),
    payload: v.any(),
    rendered_at: v.number(),
    stale_at: v.number(),
  })
    .index("by_mode_subject", ["mode", "subject", "language"]),

  badge_ledger: defineTable({
    student_id: v.string(),
    framework: v.string(),
    level: v.string(),
    subject: v.string(),
    competency_code: v.string(),
    competency_text_en: v.string(),
    competency_text_ga: v.optional(v.string()),
    eiraic_tier: v.number(),
    agent_issuer: v.string(),
    evidence_hash: v.string(),
    signature: v.string(),
    on_chain_anchor: v.optional(v.string()),
    anchor_date: v.optional(v.string()),
    date_earned: v.number(),
  })
    .index("by_student", ["student_id"])
    .index("by_student_subject", ["student_id", "subject"])
    .index("by_eiraic_tier", ["eiraic_tier"])
    .index("by_anchor_date", ["anchor_date"]),
});