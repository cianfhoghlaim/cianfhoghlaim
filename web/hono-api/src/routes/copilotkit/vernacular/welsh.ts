/**
 * Hono route for Welsh (Cymraeg) vernacular CopilotKit actions.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
 * change (Phase 14 of the cianfhoghlaim-nua v6 era plan).
 *
 * Mounted at /api/copilotkit/vernacular/welsh/* in
 * web/hono-api/src/index.ts. Delegates to ``_vernacular_factory.ts``
 * which carries the 4-endpoint surface for all 8 vernaculars.
 */

import { buildVernacularApp } from "./_vernacular_factory";

const welshApp = buildVernacularApp({
  vernacular: "welsh",
  display_name: "Welsh (Cymraeg)",
  jurisdiction: "WL",
  baml_function: "ExtractWelshSubjectSpec",
  language_code: "cy",
});

export default welshApp;
