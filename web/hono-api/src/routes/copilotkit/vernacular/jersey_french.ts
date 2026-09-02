/**
 * Hono route for Jersey French (Jèrriais) vernacular CopilotKit actions.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
 * change (Phase 14 of the cianfhoghlaim-nua v6 era plan).
 *
 * Mounted at /api/copilotkit/vernacular/jersey_french/* in
 * web/hono-api/src/index.ts.
 */

import { buildVernacularApp } from "./_vernacular_factory";

const jerseyFrenchApp = buildVernacularApp({
  vernacular: "jersey_french",
  display_name: "Jersey French (Jèrriais)",
  jurisdiction: "JE",
  baml_function: "ExtractJerseyFrenchSubjectSpec",
  language_code: "fr-je",
});

export default jerseyFrenchApp;
