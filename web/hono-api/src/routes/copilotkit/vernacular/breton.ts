/**
 * Hono route for Breton (Brezhoneg) vernacular CopilotKit actions.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
 * change (Phase 14 of the cianfhoghlaim-nua v6 era plan).
 *
 * Mounted at /api/copilotkit/vernacular/breton/* in
 * web/hono-api/src/index.ts. Sister-repo lift target.
 */

import { buildVernacularApp } from "./_vernacular_factory";

const bretonApp = buildVernacularApp({
  vernacular: "breton",
  display_name: "Breton (Brezhoneg)",
  jurisdiction: "BR",
  baml_function: "ExtractBretonSubjectSpec",
  language_code: "br",
});

export default bretonApp;
