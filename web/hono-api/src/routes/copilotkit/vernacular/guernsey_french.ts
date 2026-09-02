/**
 * Hono route for Guernsey French (Guernésiais) vernacular CopilotKit actions.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
 * change (Phase 14 of the cianfhoghlaim-nua v6 era plan).
 *
 * Mounted at /api/copilotkit/vernacular/guernsey_french/* in
 * web/hono-api/src/index.ts.
 */

import { buildVernacularApp } from "./_vernacular_factory";

const guernseyFrenchApp = buildVernacularApp({
  vernacular: "guernsey_french",
  display_name: "Guernsey French (Guernésiais)",
  jurisdiction: "GG",
  baml_function: "ExtractGuernseyFrenchSubjectSpec",
  language_code: "fr-gg",
});

export default guernseyFrenchApp;
