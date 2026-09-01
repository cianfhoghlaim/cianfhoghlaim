/**
 * Convex schema — the canonical reactive schema for the Cianfhoghlaim
 * platform.
 *
 * Per the **2026-08-25-post-cascade-followups** openspec change. This
 * supersedes the Wave 6 stub with the real 7-table schema:
 *
 *   - users                — Better Auth + Convex integration
 *   - agents               — the 12-agent Cianfhoghlaim fleet
 *   - threads              — CopilotKit thread storage
 *   - runs                 — CocoIndex App execution history
 *   - messages             — AG-UI TEXT_MESSAGE_* events
 *   - knowledge_graph_nodes — Cognee cognify outputs
 *   - subject_caches       — per-subject BIEP caches
 *
 * The 5 consolidated web apps consume this schema via
 * `import { api } from "@cianfhoghlaim/db"` which re-exports the
 * auto-generated Convex client.
 *
 * Reference:
 *   - Convex docs:                 https://docs.convex.dev/database/schemas
 *   - Convex + TanStack Start:     https://docs.convex.dev/client/tanstack/tanstack-start
 *   - Convex + Better Auth:        https://www.better-auth.com/docs/integrations/convex
 *   - Convex + AG-UI (this PR):    https://docs.copilotkit.ai/direct-to-llm
 *   - AG-UI protocol:              https://docs.ag-ui.com/
 */

import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

// ─── 1. users (Better Auth + Convex integration) ──────────────────────────────
//
// Mirrors the Better Auth users table. The Convex trigger
// (web/packages/db/convex/auth.ts) syncs Better Auth → Convex.

export const users = defineTable({
  better_auth_id: v.string(),
  email: v.string(),
  name: v.optional(v.string()),
  image: v.optional(v.string()),
  role: v.union(
    v.literal("admin"),
    v.literal("user"),
    v.literal("guest"),
  ),
  // The 3 OIDC audiences per Wave 6 (better-auth setup)
  aud: v.union(
    v.literal("convex_backend"),
    v.literal("croilar_web"),
    v.literal("croilar_portal"),
  ),
  created_at: v.number(),  // epoch ms
  updated_at: v.number(),
})
  .index("by_better_auth_id", ["better_auth_id"])
  .index("by_email", ["email"]);

// ─── 2. agents (the 12-agent Cianfhoghlaim fleet) ─────────────────────────────
//
// The Cianfhoghlaim platform uses 12 agents (per Wave 2 + Wave 3).
// Each agent row describes one agent in the fleet.

export const agents = defineTable({
  name: v.string(),  // e.g. "uog_exam_papers_agent"
  display_name: v.string(),  // e.g. "UoG Exam Papers Agent"
  framework: v.union(
    v.literal("ag-ui"),
    v.literal("adk"),
    v.literal("crewai"),
    v.literal("langgraph"),
    v.literal("pydantic-ai"),
    v.literal("mastra"),
    v.literal("claude-sdk"),
  ),
  // The 8 pipeline kinds from Wave 2 (the per-source-kind handler that
  // generated this agent's underlying DAG).
  pipeline_kind: v.union(
    v.literal("syllabus"),
    v.literal("exam_papers"),
    v.literal("personal_archive"),
    v.literal("official_docs"),
    v.literal("comics"),
    v.literal("crypto"),
    v.literal("pdf"),
    v.literal("media"),
  ),
  dlt_source: v.string(),  // e.g. "dlt_sources.education.tertiary.uog.exam_papers"
  status: v.union(
    v.literal("active"),
    v.literal("paused"),
    v.literal("error"),
  ),
  config: v.optional(v.record(v.string(), v.any())),  // free-form config
  created_at: v.number(),
  updated_at: v.number(),
})
  .index("by_name", ["name"])
  .index("by_pipeline_kind", ["pipeline_kind"])
  .index("by_status", ["status"]);

// ─── 3. threads (CopilotKit thread storage) ────────────────────────────────
//
// Each row is one CopilotKit thread — a conversation between the user
// and one (or more) agents.

export const threads = defineTable({
  user_id: v.id("users"),
  agent_id: v.optional(v.id("agents")),
  title: v.string(),
  status: v.union(
    v.literal("active"),
    v.literal("completed"),
    v.literal("interrupted"),
  ),
  // The 3-thread_metadata fields CopilotKit expects
  metadata: v.optional(v.record(v.string(), v.any())),
  created_at: v.number(),
  updated_at: v.number(),
})
  .index("by_user", ["user_id"])
  .index("by_agent", ["agent_id"])
  .index("by_status", ["status"]);

// ─── 4. runs (CocoIndex App execution history) ─────────────────────────────
//
// Each row is one execution of one CocoIndex App. Created by the
// orchestration DAG (Wave 2).

export const runs = defineTable({
  agent_id: v.optional(v.id("agents")),
  thread_id: v.optional(v.id("threads")),
  pipeline_kind: v.union(
    v.literal("syllabus"),
    v.literal("exam_papers"),
    v.literal("personal_archive"),
    v.literal("official_docs"),
    v.literal("comics"),
    v.literal("crypto"),
    v.literal("pdf"),
    v.literal("media"),
  ),
  status: v.union(
    v.literal("running"),
    v.literal("completed"),
    v.literal("failed"),
    v.literal("interrupted"),
  ),
  // The OpenSpec change that triggered this run (e.g. "2026-08-24-wave-2-orchestration-vertical-pipelines-v1")
  openspec_change: v.optional(v.string()),
  // OTel semantic conventions per Wave 7
  db_system: v.optional(v.string()),  // "duckdb"
  gen_ai_system: v.optional(v.string()),  // "baml"
  object_store_system: v.optional(v.string()),  // "s3"
  started_at: v.number(),
  completed_at: v.optional(v.number()),
  // Wave 4 DuckLake 1.0 snapshot reference (for time-travel queries)
  ducklake_snapshot: v.optional(v.string()),
})
  .index("by_agent", ["agent_id"])
  .index("by_status", ["status"])
  .index("by_pipeline_kind", ["pipeline_kind"]);

// ─── 5. messages (AG-UI TEXT_MESSAGE_* events) ─────────────────────────────
//
// Each row is one AG-UI chat message event. Consumed by the AG-UI
// SSE handler at web/hono-api/src/routes/agui/index.ts (the Wave 6
// stub replaced by this real implementation).

export const messages = defineTable({
  thread_id: v.id("threads"),
  run_id: v.optional(v.id("runs")),
  // The 12 AG-UI event types from @cianfhoghlaim/contracts
  event_type: v.union(
    v.literal("RUN_STARTED"),
    v.literal("RUN_FINISHED"),
    v.literal("STEP_STARTED"),
    v.literal("STEP_FINISHED"),
    v.literal("TEXT_MESSAGE_START"),
    v.literal("TEXT_MESSAGE_CONTENT"),
    v.literal("TEXT_MESSAGE_END"),
    v.literal("TOOL_CALL_START"),
    v.literal("TOOL_CALL_ARGS"),
    v.literal("TOOL_CALL_END"),
    v.literal("TOOL_CALL_RESULT"),
    v.literal("STATE_DELTA"),
    v.literal("MESSAGES_SNAPSHOT"),
  ),
  content: v.string(),  // The text content (or JSON for non-text events)
  // The AG-UI shared state snapshot (for STATE_DELTA / MESSAGES_SNAPSHOT)
  state_snapshot: v.optional(v.record(v.string(), v.any())),
  // Per Wave 7 OTel semantic conventions
  db_system: v.optional(v.string()),
  gen_ai_system: v.optional(v.string()),
  object_store_system: v.optional(v.string()),
  timestamp: v.number(),
})
  .index("by_thread", ["thread_id"])
  .index("by_run", ["run_id"])
  .index("by_event_type", ["event_type"]);

// ─── 6. knowledge_graph_nodes (Cognee cognify outputs) ────────────────────
//
// Each row is one node in the Cognee knowledge graph. Populated by the
// `dlt_sources/knowledge_graph/*.py` files (the cognify pipeline).

export const knowledge_graph_nodes = defineTable({
  // The cognify node type (entity, concept, relationship, etc.)
  node_type: v.union(
    v.literal("entity"),
    v.literal("concept"),
    v.literal("relationship"),
    v.literal("chunk"),
  ),
  name: v.string(),  // The node's display name
  // The cognify dataset this node belongs to (e.g. "british_isles.mathematics")
  dataset: v.string(),
  // The cognify properties (free-form JSON)
  properties: v.record(v.string(), v.any()),
  // Optional reference to a message or run that produced this node
  source_run_id: v.optional(v.id("runs")),
  source_message_id: v.optional(v.id("messages")),
  created_at: v.number(),
})
  .index("by_dataset", ["dataset"])
  .index("by_node_type", ["node_type"])
  .index("by_name", ["name"]);

// ─── 7. subject_caches (per-subject BIEP caches) ──────────────────────────
//
// The Wave 4 DuckLake SORTED BY (subject, board, year, language) materialised
// into Convex for fast BIEP-axis reads. One row per (subject, board, year, language).

export const subject_caches = defineTable({
  // The BIEP axis (per Wave 6 contracts)
  subject: v.string(),  // "mathematics", "chemistry", etc.
  board: v.union(
    v.literal("ncca"),     // Ireland
    v.literal("sec"),      // Ireland (older)
    v.literal("ccea"),     // Northern Ireland
    v.literal("sqa"),      // Scotland
    v.literal("wjec"),     // Wales
    v.literal("aqa"),      // England
    v.literal("edexcel"),  // England
    v.literal("ocr"),      // England
    v.literal("cambridge"),  // International
  ),
  year: v.number(),
  language: v.union(
    v.literal("en"),
    v.literal("ga"),  // Irish
  ),
  // The cached JSON payload
  payload: v.record(v.string(), v.any()),
  // Wave 4 DuckLake time-travel reference
  ducklake_at_timestamp: v.optional(v.string()),
  ducklake_at_version: v.optional(v.number()),
  refreshed_at: v.number(),
  expires_at: v.optional(v.number()),
})
  .index("by_subject", ["subject"])
  .index("by_board_year", ["board", "year"])
  .index("by_language", ["language"]);

// ─── The canonical Cianfhoghlaim schema ────────────────────────────────────

// ─── 8. study_plans (chat-with-syllabus → study-plan surface) ─────────────
//
// Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
// (Phase 1, §3.1 of tasks.md). One row per generated study plan,
// hydrated from the canonical Phase 1 planner at
// `agents.adk.subjects.lc.planner.generate_study_plan(...)`.
// Phase 1 scope: chemistry + mathematics + gaeilge + computer_science.
// Phase 5 broadens to the 14 NCCA LC subjects.

export const study_plans = defineTable({
  // The user who requested the plan (foreign key to users)
  user_id: v.id("users"),
  // The NCCA subject slug (e.g. "chemistry", "gaeilge")
  subject: v.string(),
  // The LO codes the student selected (array of NCCA LO codes)
  lo_codes: v.array(v.string()),
  // Total weeks in the plan (1-52)
  duration_weeks: v.number(),
  // Irish dialect for the Gaeilge subject; null otherwise
  dialect: v.union(
    v.literal("connacht"),
    v.literal("munster"),
    v.literal("ulster"),
    v.literal("standard"),
  ),
  // Serialised StudyPlanWeeks[] (canonical Phase 1 schema)
  weeks_plan_json: v.array(v.record(v.string(), v.any())),
  // Serialised StudyPlanMilestone[]
  milestones_json: v.array(v.record(v.string(), v.any())),
  // Serialised KC weights (map of competency → weight 0.0-1.0)
  kc_weights_json: v.record(v.string(), v.number()),
  // Serialised PastPaperRef[] (with NCCA page citations)
  recommended_past_papers_json: v.array(v.record(v.string(), v.any())),
  // The Convex id of the matching oral_study_plan row (Phase 1: null
  // — populated in Phase 6 when the oral-plan companion call ships)
  oral_study_plan_id: v.optional(v.id("oral_study_plans")),
  // Langfuse trace id for cross-service correlation
  langfuse_trace_id: v.optional(v.string()),
  // The optional stub_reason from the planner (populated when BAML
  // is unavailable or the call fails — used for observability)
  stub_reason: v.optional(v.string()),
  created_at: v.number(),
})
  .index("by_user", ["user_id"])
  .index("by_subject", ["subject"])
  .index("by_created_at", ["created_at"]);

// ─── 9. quest_packs (the formative-assessment quest packs) ────────────────
//
// Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
// (Phase 1, §3.1). One row per quest-pack materialisation from the
// fixed `orchestration/defs/2_materials/lc_extraction/quest_pack_assets.py`
// Dagster asset (which now calls the consolidated
// `b.GenerateSubjectQuestPack(...)` per Phase 1 §2.1).

export const quest_packs = defineTable({
  subject: v.string(),
  // Stage (LC_HL | LC_OL | LC_FDN | JC | GCSE | A_LEVEL)
  stage: v.string(),
  language: v.union(v.literal("en"), v.literal("ga"), v.literal("en_and_ga")),
  // The NCCA LO codes covered by this pack
  lo_codes: v.array(v.string()),
  // Serialised SubjectQuestPack (the qpack_template.baml response shape)
  items_json: v.array(v.record(v.string(), v.any())),
  // Total marks across all items
  total_marks: v.number(),
  // Estimated completion time in minutes
  estimated_duration_minutes: v.number(),
  created_at: v.number(),
})
  .index("by_subject", ["subject"])
  .index("by_stage_language", ["stage", "language"]);

// ─── 10. oral_study_plans (the oral-delivery companion to study_plans) ────
//
// Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
// (Phase 1, §3.1). One row per oral study plan; Phase 1 ships the
// schema + an empty audio_segments[] stub from
// `baml_src/british_isles/_shared/oral_study_plan.baml`; Phase 6
// fills the audio_segments[] via the wired Pipecat + Chatterbox
// dispatch.

export const oral_study_plans = defineTable({
  // The parent study_plans row (foreign key)
  study_plan_id: v.id("study_plans"),
  dialect: v.union(
    v.literal("connacht"),
    v.literal("munster"),
    v.literal("ulster"),
    v.literal("standard"),
  ),
  // Total estimated oral duration in minutes
  duration_min: v.number(),
  // Provider-specific voice id (empty in Phase 1)
  voice_id: v.string(),
  // Serialised OralStudySegment[] (empty in Phase 1; filled in Phase 6)
  audio_segments_json: v.array(v.record(v.string(), v.any())),
  // The implementation phase marker
  phase: v.union(
    v.literal("phase1_stub"),
    v.literal("phase6_wired"),
  ),
  created_at: v.number(),
})
  .index("by_study_plan", ["study_plan_id"])
  .index("by_dialect", ["dialect"]);

// ─── 11. formative_attempts (student responses to quest-pack items) ───────
//
// Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
// (Phase 1, §3.1). Phase 1 ships the schema; Phase 5 (BAML/CocoIndex
// hardening) wires the population.

export const formative_attempts = defineTable({
  user_id: v.id("users"),
  quest_pack_id: v.id("quest_packs"),
  item_id: v.string(),
  student_response: v.string(),
  // Serialised QuestPackScore (overall_score + per_criterion_scores +
  // feedback_text + next_steps)
  score_json: v.record(v.string(), v.any()),
  created_at: v.number(),
})
  .index("by_user", ["user_id"])
  .index("by_quest_pack", ["quest_pack_id"]);

// ─── 12. audio_segments (per-segment audio bytes for oral study plans) ────
//
// Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
// (Phase 1, §3.1). Phase 1 ships the schema; Phase 6 (oral delivery)
// wires the population from the wired Pipecat + Chatterbox dispatch.

export const audio_segments = defineTable({
  oral_study_plan_id: v.id("oral_study_plans"),
  week_number: v.number(),
  text_en: v.string(),
  text_ga: v.optional(v.string()),
  estimated_duration_sec: v.number(),
  tts_provider: v.union(
    v.literal("chatterbox"),
    v.literal("orpheus-tts-3b-ft"),
    v.literal("facebook-mms-tts-gle"),
  ),
  voice_id: v.string(),
  // The audio bytes (stored as a base64 string; a real production
  // system would offload to R2 + signed URLs per the existing
  // `web/hono-api/src/routes/pdf/[...r2-key].ts` pattern).
  audio_b64: v.string(),
  created_at: v.number(),
})
  .index("by_oral_study_plan", ["oral_study_plan_id"])
  .index("by_tts_provider", ["tts_provider"]);

export default defineSchema({
  users,
  agents,
  threads,
  runs,
  messages,
  knowledge_graph_nodes,
  subject_caches,
  study_plans,
  quest_packs,
  oral_study_plans,
  formative_attempts,
  audio_segments,
});
