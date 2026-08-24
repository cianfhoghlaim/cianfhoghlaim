/**
 * Convex schema — the canonical reactive schema for the Cianfhoghlaim
 * platform.
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change. This is a STUB — the real schema lands in a Wave 6 follow-up
 * PR. The 5 consolidated web apps consume this schema via
 * `import { api } from "@cianfhoghlaim/db"` which re-exports
 * the auto-generated Convex client.
 *
 * Reference:
 *   - Convex docs: https://docs.convex.dev/database/schemas
 *   - Convex + TanStack Start: https://docs.convex.dev/client/tanstack/tanstack-start
 *   - Convex + Better Auth: https://www.better-auth.com/docs/integrations/convex
 */

import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

/**
 * The Cianfhoghlaim Convex schema (Wave 6 stub).
 *
 * Real implementation lands in the Wave 6 follow-up PR — at minimum:
 *   - users (Better Auth + Convex integration)
 *   - agents (the 12-agent Cianfhoghlaim fleet)
 *   - threads (CopilotKit thread storage)
 *   - runs (CocoIndex App execution history)
 *   - messages (AG-UI TEXT_MESSAGE_* events)
 *   - knowledge_graph_nodes (Cognee cognify outputs)
 *   - per-subject caches (chemistry_syllabus, etc.)
 */
export default defineSchema({
  // Placeholder table so `npx convex dev` can start.
  // The real tables land in the Wave 6 follow-up PR.
  _wave6_placeholder: defineTable({
    created_at: v.string(),
    note: v.string(),
  }),
});
