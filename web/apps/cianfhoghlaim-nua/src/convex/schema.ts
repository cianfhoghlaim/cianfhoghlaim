/**
 * Convex schema for the consolidated cianfhoghlaim-nua app.
 *
 * Re-exports the canonical schema from `@cianfhoghlaim/db` (the
 * shared Convex schema package at web/packages/db/convex/schema.ts).
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 change
 * (Phase 3 §B.5).
 */

export {
  default,
  users,
  agents,
  threads,
  runs,
  messages,
  knowledge_graph_nodes,
  subject_caches,
  ncce_learning_graphs,
  study_plans,
  quest_packs,
  oral_study_plans,
  formative_attempts,
  audio_segments,
} from "@cianfhoghlaim/db/convex/schema";
