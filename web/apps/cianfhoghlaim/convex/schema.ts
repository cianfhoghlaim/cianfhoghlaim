/** Convex schema for the central Cianfhoghlaim homepage.
 *
 * Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
 * (Phase 10 - the central Cianfhoghlaim homepage).
 *
 * This is the canonical Convex schema for:
 * - Chat messages (the per-subject agent conversation history)
 * - User annotations (per-subject notes on LC topics)
 * - User progress tracking (per-subject completion %)
 * - Pipeline health cache (the 4-stage BIEP status)
 * - Knowledge graph cache (the 7-cluster Cognee summary)
 */

import { defineSchema, defineTable, v } from "convex/schema";

/**
 * The canonical Cianfhoghlaim Convex schema.
 */
export default defineSchema({
  // Per-subject chat conversation history
  chat_messages: defineTable({
    thread_id: v.string(),
    subject: v.string(), // the subject slug
    stage: v.string(), // "lc" | "jc" | "gcse" | "a_level"
    role: v.string(), // "user" | "assistant" | "system"
    content: v.string(),
    ragas_score: v.optional(v.number()), // 0.0-1.0 (assistant messages only)
    agent: v.optional(v.string()), // the per-subject agent that generated the response
    created_at: v.number(),
  })
    .index("by_thread", ["thread_id", "created_at"])
    .index("by_subject", ["subject", "stage", "created_at"]),

  // Per-subject user annotations
  annotations: defineTable({
    user_id: v.string(),
    subject: v.string(),
    stage: v.string(),
    topic_code: v.string(),
    note: v.string(),
    ncca_code: v.optional(v.string()),
    lo_code: v.optional(v.string()),
    created_at: v.number(),
    updated_at: v.number(),
  })
    .index("by_user", ["user_id", "created_at"])
    .index("by_subject_topic", ["subject", "topic_code", "created_at"]),

  // Per-user per-subject progress tracking
  progress: defineTable({
    user_id: v.string(),
    subject: v.string(),
    stage: v.string(),
    topic_code: v.string(),
    score: v.number(), // 0-100
    completed: v.boolean(),
    notes: v.optional(v.string()),
    last_attempted: v.number(),
    created_at: v.number(),
  })
    .index("by_user", ["user_id", "last_attempted"])
    .index("by_subject", ["subject", "score"]),

  // Pipeline health cache (Phase 5 - the 4-stage BIEP)
  pipeline_health: defineTable({
    pipeline: v.string(), // "lc_dlt" | "lc_baml" | "lc_cocoindex" | "lc_ragas" | ...
    stage: v.string(), // "lc" | "jc" | "gcse" | "a_level"
    status: v.string(), // "healthy" | "running" | "stalled" | "error"
    subjects_processed: v.number(),
    subjects_total: v.number(),
    pdfs_processed: v.number(),
    pdfs_total: v.number(),
    ragas_score: v.optional(v.number()),
    last_update: v.number(),
  })
    .index("by_pipeline", ["pipeline", "last_update"])
    .index("by_stage", ["stage", "last_update"]),

  // Knowledge graph cache (the 7 Cognee clusters)
  knowledge_graph: defineTable({
    cluster: v.string(), // "aistear" | "primary" | "jc" | "lc" | "uni" | "memory" | "activity"
    name: v.string(),
    description: v.string(),
    entity_count: v.number(),
    relationship_count: v.number(),
    centroid_embedding: v.optional(v.string()),
    updated_at: v.number(),
  })
    .index("by_cluster", ["cluster", "updated_at"]),

  // Activity feed cache (Phase 5-9 - the per-subject pipeline events)
  activity_events: defineTable({
    kind: v.string(),
    subject: v.string(),
    agent: v.string(),
    message: v.string(),
    ragas_score: v.optional(v.number()),
    created_at: v.number(),
  })
    .index("by_kind", ["kind", "created_at"])
    .index("by_subject", ["subject", "created_at"])
    .index("by_agent", ["agent", "created_at"]),
});
