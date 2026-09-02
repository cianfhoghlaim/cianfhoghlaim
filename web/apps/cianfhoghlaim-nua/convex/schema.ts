/**
 * Convex schema for the consolidated cianfhoghlaim-nua app.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-ireland-lc-completion-v1 change
 * (Step 2 of the cianfhoghlaim-nua v6 era plan). Includes the 14
 * NCCA LC subject tables (8 priority + 6 NCCA-adjacent).
 *
 * Phase 11 (the 2026-09-XX-orchestration-integration-v1 change) adds
 * the 5 per-jurisdiction subject_spec tables:
 * - england_subject_specs
 * - wales_subject_specs
 * - scotland_subject_specs
 * - northern_ireland_subject_specs
 * - isle_of_man_subject_specs
 *
 * Combined surface (18 tables):
 * 1-4. Root tables: users, study_plans, oral_study_plans, ncce_learning_graphs
 * 5-12. 8 per-subject tables: accounting, business, french, history, art,
 *      music, applied_mathematics, physics
 * 13-17. 5 jurisdiction subject_spec tables (Phase 11)
 * 18. Total Phase 11 schema (the canonical 18-table BIEP v3 schema)
 */

import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

// Re-export the per-subject tables
export {
  accounting,
  business,
  french,
  history,
  art,
  music,
  applied_mathematics,
  physics,
} from "./lc";

// Re-export the 5 Phase 11 jurisdiction subject_spec tables
export {
  england_subject_specs,
  wales_subject_specs,
  scotland_subject_specs,
  northern_ireland_subject_specs,
  isle_of_man_subject_specs,
} from "./jurisdictions";

// The 4 root tables (from web/packages/db/convex/schema.ts)
const users = defineTable({
  better_auth_id: v.string(),
  email: v.string(),
  name: v.optional(v.string()),
  image: v.optional(v.string()),
  role: v.union(v.literal("admin"), v.literal("user"), v.literal("guest")),
  aud: v.union(
    v.literal("convex_backend"),
    v.literal("croilar_web"),
    v.literal("croilar_portal"),
  ),
  created_at: v.number(),
  updated_at: v.number(),
});

const study_plans = defineTable({
  user_id: v.id("users"),
  subject: v.string(),
  lo_codes: v.array(v.string()),
  duration_weeks: v.number(),
  dialect: v.union(
    v.literal("connacht"),
    v.literal("munster"),
    v.literal("ulster"),
    v.literal("standard"),
  ),
  weeks_plan_json: v.array(v.record(v.string(), v.any())),
  milestones_json: v.array(v.record(v.string(), v.any())),
  kc_weights_json: v.record(v.string(), v.number()),
  recommended_past_papers_json: v.array(v.record(v.string(), v.any())),
  oral_study_plan_id: v.optional(v.id("oral_study_plans")),
  langfuse_trace_id: v.optional(v.string()),
  stub_reason: v.optional(v.string()),
  created_at: v.number(),
})
  .index("by_user", ["user_id"])
  .index("by_subject", ["subject"])
  .index("by_created_at", ["created_at"]);

const oral_study_plans = defineTable({
  study_plan_id: v.id("study_plans"),
  dialect: v.union(
    v.literal("connacht"),
    v.literal("munster"),
    v.literal("ulster"),
    v.literal("standard"),
  ),
  duration_min: v.number(),
  voice_id: v.string(),
  audio_segments_json: v.array(v.record(v.string(), v.any())),
  phase: v.union(v.literal("phase1_stub"), v.literal("phase6_wired")),
  created_at: v.number(),
})
  .index("by_study_plan", ["study_plan_id"])
  .index("by_dialect", ["dialect"]);

const ncce_learning_graphs = defineTable({
  subject: v.string(),
  year_level: v.string(),
  title: v.string(),
  source_pdf: v.string(),
  rows_json: v.array(v.record(v.string(), v.any())),
  columns_json: v.array(v.record(v.string(), v.any())),
  cells_json: v.array(v.record(v.string(), v.any())),
  prerequisites_json: v.array(v.record(v.string(), v.any())),
  total_lessons: v.number(),
  total_skills: v.number(),
  pedagogy_principles_json: v.array(v.record(v.string(), v.any())),
  pedagogy_overlay_json: v.optional(v.record(v.string(), v.any())),
  equivalencies_json: v.optional(v.array(v.record(v.string(), v.any()))),
  created_at: v.number(),
})
  .index("by_subject", ["subject"])
  .index("by_year_level", ["year_level"])
  .index("by_subject_year", ["subject", "year_level"]);

export default defineSchema({
  users,
  ncce_learning_graphs,
  study_plans,
  oral_study_plans,
  accounting,
  business,
  french,
  history,
  art,
  music,
  applied_mathematics,
  physics,
  // Phase 11 — the 5 jurisdiction subject_spec tables
  england_subject_specs,
  wales_subject_specs,
  scotland_subject_specs,
  northern_ireland_subject_specs,
  isle_of_man_subject_specs,
});
